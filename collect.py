from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import replace
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
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

LOGGER = logging.getLogger(__name__)


# 화면과 DB에 저장되는 최종 카테고리
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


# 실제 네이버 뉴스 API에서 검색할 표현
#
# "연예", "스포츠", "문화 생활"처럼 넓은 단어 하나만 검색하면
# 허용 언론사 기사가 거의 잡히지 않을 수 있으므로
# 카테고리별로 여러 구체적인 검색어를 사용한다.
TOPIC_SEARCH_QUERIES: dict[str, tuple[str, ...]] = {
    "국제": (
        "미국 국제",
        "중국 국제",
        "일본 국제",
        "유럽 국제",
        "해외 주요 뉴스",
    ),
    "정치": (
        "대통령",
        "정부 정책",
        "국회",
        "여야",
        "정치 주요 뉴스",
    ),
    "경제": (
        "경제",
        "물가",
        "금리 환율",
        "부동산",
        "기업 수출",
    ),
    "사회": (
        "사회",
        "교육",
        "의료",
        "환경",
        "직장 생활",
    ),
    "IT·과학": (
        "인공지능 AI",
        "반도체",
        "스마트폰 기술",
        "과학 연구",
        "우주",
    ),
    "문화·생활": (
        "여행",
        "건강 생활",
        "음식",
        "전시 공연",
        "축제",
    ),
    "연예": (
        "드라마 배우",
        "영화",
        "가수 음악",
        "예능",
        "콘서트",
    ),
    "스포츠": (
        "축구",
        "야구",
        "KBO",
        "해외 스포츠",
        "국가대표 경기",
    ),
}


def collect_candidates_by_topic(
    settings: Settings,
    seen_urls: set[str],
) -> dict[str, list[NewsCandidate]]:
    """
    카테고리별 검색어를 모두 실행한 뒤 허용 언론사 후보를 모은다.

    검색어가 무엇이든 candidate.query를 최종 카테고리명으로 바꿔
    news.py의 주제 적합도 점수와 DB category가 정확히 작동하게 한다.
    """
    candidates_by_topic: dict[str, list[NewsCandidate]] = defaultdict(list)

    # 같은 실행 안에서 동일 URL이 여러 검색어에 중복 포함되지 않도록 한다.
    local_seen: set[str] = set()

    for topic in TARGET_TOPICS:
        queries = TOPIC_SEARCH_QUERIES.get(topic, (topic,))

        LOGGER.info(
            "Collecting topic %s with %d search queries.",
            topic,
            len(queries),
        )

        for query in queries:
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

                # 실제 검색어 대신 최종 주제를 넣어
                # choose_candidate의 주제 점수와 DB category를 맞춘다.
                normalized_candidate = replace(
                    candidate,
                    query=topic,
                )

                candidates_by_topic[topic].append(
                    normalized_candidate
                )
                local_seen.add(url)
                added_count += 1

            LOGGER.info(
                "Added %d allowed candidates "
                "for topic=%s query=%s",
                added_count,
                topic,
                query,
            )

        LOGGER.info(
            "Topic %s collected %d unique candidates in total.",
            topic,
            len(candidates_by_topic.get(topic, [])),
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
    특정 주제에서 학습에 적합한 기사를 최대 limit개 저장한다.

    본문 추출·번역·DB 저장에 실패하면 다음 후보를 계속 시도한다.
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

        # 추출 실패한 URL도 같은 실행에서 반복 선택되지 않도록 등록한다.
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
                "[topic=%s, publisher=%s, chars=%d]: %s",
                topic,
                publisher,
                len(body),
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
        candidates = candidates_by_topic.get(topic, [])

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

    saved_topics = sorted(
        {
            row.get("category", "")
            for row in saved
            if isinstance(row, dict)
        }
    )

    LOGGER.info(
        "Done. Saved %d articles across %d target topics. "
        "Saved topics: %s",
        len(saved),
        len(TARGET_TOPICS),
        ", ".join(saved_topics) or "none",
    )


if __name__ == "__main__":
    main()
