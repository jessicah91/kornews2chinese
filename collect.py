from __future__ import annotations

import logging
from collections import defaultdict

from src.ai import translate_article
from src.config import Settings
from src.db import existing_urls, get_admin_client, save_article
from src.emailer import send_digest
from src.news import (
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


TARGET_PUBLISHERS = (
    "SBS",
    "MBC",
    "KBS",
    "조선일보",
    "중앙일보",
    "동아일보",
    "매일경제",
)


def collect_candidates_by_publisher(
    settings: Settings,
    seen_urls: set[str],
) -> dict[str, list]:
    """
    모든 검색어의 네이버 뉴스 결과를 모아서
    허용 언론사별 후보 목록으로 분류한다.
    """
    candidates_by_publisher: dict[str, list] = defaultdict(list)
    local_seen: set[str] = set()

    for query in settings.news_queries:
        LOGGER.info("Searching news query: %s", query)

        try:
            candidates = search_naver_news(
                settings.naver_client_id,
                settings.naver_client_secret,
                query,
                display=100,
            )
        except Exception:
            LOGGER.exception("News search failed for query: %s", query)
            continue

        for candidate in candidates:
            url = candidate.original_link or candidate.link

            if not url:
                continue

            if url in seen_urls or url in local_seen:
                continue

            publisher = publisher_name(url)

            if publisher not in TARGET_PUBLISHERS:
                continue

            candidates_by_publisher[publisher].append(candidate)
            local_seen.add(url)

    return candidates_by_publisher


def collect_one_article_for_publisher(
    publisher: str,
    candidates: list,
    settings: Settings,
    db,
    seen_urls: set[str],
):
    """
    특정 언론사 후보 중에서 가장 적절한 기사 1개를 저장한다.
    본문 추출에 실패하면 다음 후보를 시도한다.
    """
    remaining_candidates = list(candidates)

    while remaining_candidates:
        candidate = choose_candidate(
            remaining_candidates,
            seen_urls,
        )

        if not candidate:
            LOGGER.info(
                "No suitable candidate found for publisher: %s",
                publisher,
            )
            return None

        remaining_candidates.remove(candidate)

        url = candidate.original_link or candidate.link

        if not url:
            continue

        seen_urls.add(url)

        LOGGER.info(
            "Trying article [%s]: %s",
            publisher,
            candidate.title,
        )

        body = extract_article_text(
            url,
            settings.max_article_chars,
        )

        if len(body) < 500:
            LOGGER.warning(
                "Skipping short/unavailable article [%s]: %s",
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
                "Translation failed [%s]: %s",
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
                    "category": candidate.query,
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
                "Database save failed [%s]: %s",
                publisher,
                url,
            )
            continue

        LOGGER.info(
            "Saved article [%s]: %s",
            publisher,
            candidate.title,
        )

        return row

    LOGGER.info(
        "All candidates failed for publisher: %s",
        publisher,
    )

    return None


def main() -> None:
    settings = Settings.from_env()

    db = get_admin_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )

    seen_urls = set(existing_urls(db))
    saved = []

    candidates_by_publisher = collect_candidates_by_publisher(
        settings,
        seen_urls,
    )

    for publisher in TARGET_PUBLISHERS:
        candidates = candidates_by_publisher.get(
            publisher,
            [],
        )

        LOGGER.info(
            "Publisher %s has %d candidates.",
            publisher,
            len(candidates),
        )

        if not candidates:
            LOGGER.warning(
                "No search results found for publisher: %s",
                publisher,
            )
            continue

        row = collect_one_article_for_publisher(
            publisher,
            candidates,
            settings,
            db,
            seen_urls,
        )

        if row:
            saved.append(row)

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
            LOGGER.exception("Digest email failed.")

    LOGGER.info(
        "Done. Saved %d of %d target publishers.",
        len(saved),
        len(TARGET_PUBLISHERS),
    )


if __name__ == "__main__":
    main()
