from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from src.ai import translate_article
from src.config import Settings
from src.db import existing_urls, get_admin_client, save_article
from src.emailer import send_digest
from src.news import (
    NewsCandidate,
    choose_candidate,
    extract_article_text,
    published_iso,
    publisher_name,
    search_naver_news,
    today_iso,
    topic_from_query,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

LOGGER = logging.getLogger(__name__)


TARGET_TOPICS = (
    "국제",
    "정치",
    "경제",
    "사회",
    "IT·과학",
    "문화·생활",
    "연예",
    "스포츠",
)


def collect_candidates_by_topic(
    settings: Settings,
    seen_urls: set[str],
) -> dict[str, list[NewsCandidate]]:
    """
    설정된 검색어별로 네이버 뉴스 후보를 수집한 뒤,
    검색어에 대응하는 주제별 후보 목록으로 분류한다.

    같은 URL은 한 번만 포함하며,
    이미 DB에 저장된 URL도 제외한다.
    """
    candidates_by_topic: dict[str, list[NewsCandidate]] = defaultdict(list)
    local_seen: set[str] = set()

    for query in settings.news_queries:
        topic = topic_from_query(query)

        LOGGER.info(
            "Searching news query: %s (topic=%s)",
            query,
            topic,
        )

        try:
            candidates = search_naver_news(
                settings.naver_client_id,
                settings.naver_client_secret,
                query,
                display=100,
            )
        except Exception:
            LOGGER.exception(
                "News search failed for query: %s",
                query,
            )
            continue

        added_count = 0

        for candidate in candidates:
            url = candidate.original_link or candidate.link

            if not url:
                continue

            if url in seen_urls or url in local_seen:
                continue

            publisher = publisher_name(url)

            if not publisher:
                continue

            candidates_by_topic[topic].append(candidate)
            local_seen.add(url)
            added_count += 1

        LOGGER.info(
            "Collected %d allowed candidates for topic: %s",
            added_count,
            topic,
        )

    return candidates_by_topic


def collect_articles_for_topic(
    topic: str,
    candidates: list[NewsCandidate],
    limit: int,
    settings: Settings,
    db: Any,
    seen_urls: set[str],
) -> list[dict[str, Any]]:
    """
    특정 주제 후보 중 학습에 적합한 기사를 최대 limit개 저장한다.

    후보 선택 후 본문 추출, 번역, DB 저장 중 하나라도 실패하면
    같은 주제의 다음 후보를 계속 시도한다.
    """
    saved_rows: list[dict[str, Any]] = []
    remaining_candidates = list(candidates)

    while remaining_candidates and len(saved_rows) < limit:
        candidate = choose_candidate(
            remaining_candidates,
            seen_urls,
        )

        if not candidate:
            LOGGER.info(
                "No suitable candidate found for topic: %s",
                topic,
            )
            break

        remaining_candidates.remove(candidate)

        url = candidate.original_link or candidate.link

        if not url:
            continue

        # 같은 실행 안에서 다시 선택되지 않도록 먼저 등록한다.
        seen_urls.add(url)

        publisher = publisher_name(url) or "언론사 미상"

        LOGGER.info(
            "Trying article [topic=%s, publisher=%s]: %s",
            topic,
            publisher,
            candidate.title,
        )

        body = extract_article_text(
            url,
            settings.max_article_chars,
        )

        if len(body) < 500:
            LOGGER.warning(
                "Skipping short/unavailable article "
                "[topic=%s, publisher=%s]: %s",
                topic,
                publisher,
                url,
            )
            continue

        try:
            study = translate_article(
                settings.deepl_api_key,
                title=candidate.title,
                body=body,
                source_url=url,
                max_sentences=settings.max_sentences,
            )
        except Exception:
            LOGGER.exception(
                "Translation failed "
                "[topic=%s, publisher=%s]: %s",
                topic,
                publisher,
                url,
            )
            continue

        try:
            row = save_article(
                db,
                {
                    "source_url": url,
                    "naver_url": candidate.link,
                    "publisher_name": publisher,
                    "publisher_title": candidate.title,
                    "category": topic,
                    "author_name": None,
                    "published_at": published_iso(
                        candidate.published_at
                    ),
                    "published_at_text": candidate.published_at,
                    "collected_date": today_iso(),
                    "source_text": body,
                    "study_data": study.model_dump(),
                    "processing_status": "completed",
                    "processing_error": None,
                    "ai_model": (
                        "DeepL + deterministic study tools"
                    ),
                    "is_published": True,
                },
            )
        except Exception:
            LOGGER.exception(
                "Database save failed "
                "[topic=%s, publisher=%s]: %s",
                topic,
                publisher,
                url,
            )
            continue

        LOGGER.info(
            "Saved article "
            "[topic=%s, publisher=%s]: %s",
            topic,
            publisher,
            candidate.title,
        )

        saved_rows.append(row)

    if not saved_rows:
        LOGGER.info(
            "All candidates failed for topic: %s",
            topic,
        )

    return saved_rows


def main() -> None:
    settings = Settings.from_env()

    db = get_admin_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )

    seen_urls = set(existing_urls(db))
    saved: list[dict[str, Any]] = []

    candidates_by_topic = collect_candidates_by_topic(
        settings,
        seen_urls,
    )

    for topic in TARGET_TOPICS:
        candidates = candidates_by_topic.get(
            topic,
            [],
        )

        LOGGER.info(
            "Topic %s has %d candidates.",
            topic,
            len(candidates),
        )

        if not candidates:
            LOGGER.warning(
                "No search results found for topic: %s",
                topic,
            )
            continue

        topic_rows = collect_articles_for_topic(
            topic=topic,
            candidates=candidates,
            limit=settings.articles_per_query,
            settings=settings,
            db=db,
            seen_urls=seen_urls,
        )

        saved.extend(topic_rows)

    if (
        settings.resend_api_key
        and settings.email_from
        and settings.email_to
        and saved
    ):
        try:
            send_digest(
                settings.resend_api_key,
                settings.email_from,
                settings.email_to,
                settings.app_url,
                saved,
            )
        except Exception:
            LOGGER.exception(
                "Digest email failed."
            )

    LOGGER.info(
        "Done. Saved %d articles across %d target topics.",
        len(saved),
        len(TARGET_TOPICS),
    )


if __name__ == "__main__":
    main()
