from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

def _required(name: str) -> str:
    value=os.getenv(name,"").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def _int(name: str, default: int, minimum: int) -> int:
    try: return max(minimum, int(os.getenv(name,str(default))))
    except ValueError: return default

@dataclass(frozen=True)
class Settings:
    naver_client_id:str
    naver_client_secret:str
    deepl_api_key:str
    supabase_url:str
    supabase_service_role_key:str
    news_queries:tuple[str,...]
    articles_per_query:int
    max_article_chars:int
    max_sentences:int
    resend_api_key:str=""
    email_from:str=""
    email_to:str=""
    app_url:str=""

    @classmethod
    def from_env(cls)->"Settings":
        queries=tuple(q.strip() for q in os.getenv("NEWS_QUERIES","경제,사회,국제").split(",") if q.strip())
        return cls(
            naver_client_id=_required("NAVER_CLIENT_ID"),
            naver_client_secret=_required("NAVER_CLIENT_SECRET"),
            deepl_api_key=_required("DEEPL_API_KEY"),
            supabase_url=_required("SUPABASE_URL").rstrip('/'),
            supabase_service_role_key=_required("SUPABASE_SERVICE_ROLE_KEY"),
            news_queries=queries,
            articles_per_query=_int("ARTICLES_PER_QUERY",1,1),
            max_article_chars=_int("MAX_ARTICLE_CHARS",12000,2000),
            max_sentences=_int("MAX_SENTENCES",60,10),
            resend_api_key=os.getenv("RESEND_API_KEY","").strip(),
            email_from=os.getenv("EMAIL_FROM","").strip(),
            email_to=os.getenv("EMAIL_TO","").strip(),
            app_url=os.getenv("APP_URL","").strip(),
        )
