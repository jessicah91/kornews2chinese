from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    naver_client_id: str
    naver_client_secret: str
    deepl_api_key: str
    supabase_url: str
    supabase_service_role_key: str
    news_queries: tuple[str, ...]
    articles_per_query: int
    max_article_chars: int

    @classmethod
    def from_env(cls) -> "Settings":
        queries = tuple(
            q.strip() for q in os.getenv("NEWS_QUERIES", "경제,사회,국제").split(",") if q.strip()
        )
        return cls(
            naver_client_id=_required("NAVER_CLIENT_ID"),
            naver_client_secret=_required("NAVER_CLIENT_SECRET"),
            deepl_api_key=_required("DEEPL_API_KEY"),
            supabase_url=_required("SUPABASE_URL"),
            supabase_service_role_key=_required("SUPABASE_SERVICE_ROLE_KEY"),
            news_queries=queries,
            articles_per_query=max(1, int(os.getenv("ARTICLES_PER_QUERY", "1"))),
            max_article_chars=max(2000, int(os.getenv("MAX_ARTICLE_CHARS", "8000"))),
        )
