from __future__ import annotations

import logging

from src.ai import translate_article
from src.config import Settings
from src.db import existing_urls, get_admin_client, save_article
from src.emailer import send_digest
from src.news import choose_candidate, extract_article_text, search_naver_news, today_iso

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def main() -> None:
    settings = Settings.from_env()
    db = get_admin_client(settings.supabase_url, settings.supabase_service_role_key)
    seen = existing_urls(db)
    saved: list[dict] = []

    for query in settings.news_queries:
        candidates = search_naver_news(
            settings.naver_client_id,
            settings.naver_client_secret,
            query,
            display=max(10, settings.articles_per_query * 5),
        )
        used_for_query = 0
        while used_for_query < settings.articles_per_query:
            candidate = choose_candidate(candidates, seen)
            if not candidate:
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
                settings.openai_api_key,
                settings.openai_model,
                title=candidate.title,
                body=body,
                source_url=source_url,
            )
            row = save_article(db, {
                "source_url": source_url,
                "naver_url": candidate.link,
                "publisher_title": candidate.title,
                "category": query,
                "published_at_text": candidate.published_at,
                "collected_date": today_iso(),
                "source_text": body,
                "study_data": study.model_dump(),
            })
            saved.append(row)
            used_for_query += 1

    send_digest(
        settings.resend_api_key,
        settings.email_from,
        settings.email_to,
        settings.app_url,
        saved,
    )
    LOGGER.info("Done. Saved %d articles.", len(saved))


if __name__ == "__main__":
    main()
