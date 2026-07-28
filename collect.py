from __future__ import annotations

import logging

from src.ai import translate_article
from src.config import Settings
from src.db import existing_urls, get_admin_client, save_article
from src.news import choose_candidate, extract_article_text, search_naver_news, today_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def main() -> None:
    settings = Settings.from_env()
    db = get_admin_client(settings.supabase_url, settings.supabase_service_role_key)
    seen = existing_urls(db)
    saved_count = 0

    for query in settings.news_queries:
        LOGGER.info("Searching Naver News: %s", query)
        candidates = search_naver_news(
            settings.naver_client_id,
            settings.naver_client_secret,
            query,
            display=max(10, settings.articles_per_query * 8),
        )
        used_for_query = 0

        while used_for_query < settings.articles_per_query:
            candidate = choose_candidate(candidates, seen)
            if not candidate:
                LOGGER.warning("No usable candidate remained for: %s", query)
                break
            candidates.remove(candidate)
            source_url = candidate.original_link or candidate.link
            seen.add(source_url)

            body = extract_article_text(source_url, settings.max_article_chars)
            if len(body) < 500:
                LOGGER.warning("Skipping short/unavailable article: %s", source_url)
                continue

            LOGGER.info("Translating [%s] %s", query, candidate.title)
            study = translate_article(
                settings.deepl_api_key,
                title=candidate.title,
                body=body,
                source_url=source_url,
            )

            # Matches the minimal articles table already created in Supabase.
            save_article(db, {
                "source_url": source_url,
                "publisher_title": candidate.title,
                "category": query,
                "collected_date": today_iso(),
                "source_text": body,
                "study_data": study.model_dump(),
            })
            used_for_query += 1
            saved_count += 1

    LOGGER.info("Done. Saved %d articles.", saved_count)


if __name__ == "__main__":
    main()
