from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

import requests
import trafilatura

LOGGER = logging.getLogger(__name__)
NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


@dataclass(frozen=True)
class NewsCandidate:
    query: str
    title: str
    description: str
    link: str
    original_link: str
    published_at: str


def _clean(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", "", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def search_naver_news(client_id: str, client_secret: str, query: str, display: int = 10) -> list[NewsCandidate]:
    response = requests.get(
        NAVER_NEWS_URL,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
        params={"query": query, "display": display, "sort": "date"},
        timeout=20,
    )
    response.raise_for_status()
    items = response.json().get("items", [])
    return [
        NewsCandidate(
            query=query,
            title=_clean(item.get("title", "")),
            description=_clean(item.get("description", "")),
            link=item.get("link", ""),
            original_link=item.get("originallink", "") or item.get("link", ""),
            published_at=item.get("pubDate", ""),
        )
        for item in items
    ]


def extract_article_text(url: str, max_chars: int) -> str:
    if not url:
        return ""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
            deduplicate=True,
        ) or ""
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text[:max_chars]
    except Exception as exc:  # individual publishers fail often
        LOGGER.warning("Article extraction failed for %s: %s", urlparse(url).netloc, exc)
        return ""


def choose_candidate(candidates: list[NewsCandidate], seen_urls: set[str]) -> NewsCandidate | None:
    for candidate in candidates:
        canonical = candidate.original_link or candidate.link
        if canonical and canonical not in seen_urls:
            return candidate
    return None


def today_iso() -> str:
    return datetime.now().astimezone().date().isoformat()
