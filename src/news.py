from __future__ import annotations
import html, logging, re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
import requests, trafilatura

LOGGER=logging.getLogger(__name__)
NAVER_NEWS_URL="https://openapi.naver.com/v1/search/news.json"

@dataclass(frozen=True)
class NewsCandidate:
    query:str; title:str; description:str; link:str; original_link:str; published_at:str

def _clean(value:str)->str:
    value=html.unescape(re.sub(r"<[^>]+>","",value or ""))
    return re.sub(r"\s+"," ",value).strip()

def search_naver_news(client_id:str,client_secret:str,query:str,display:int=10)->list[NewsCandidate]:
    r=requests.get(NAVER_NEWS_URL,headers={"X-Naver-Client-Id":client_id,"X-Naver-Client-Secret":client_secret},params={"query":query,"display":min(display,100),"sort":"date"},timeout=30)
    r.raise_for_status()
    return [NewsCandidate(query,_clean(i.get("title","")),_clean(i.get("description","")),i.get("link","") or "",i.get("originallink","") or i.get("link","") or "",i.get("pubDate","") or "") for i in r.json().get("items",[])]

def extract_article_text(url:str,max_chars:int)->str:
    if not url:return ""
    try:
        downloaded=trafilatura.fetch_url(url)
        if not downloaded:return ""
        text=trafilatura.extract(downloaded,include_comments=False,include_tables=False,favor_recall=True,deduplicate=True,output_format="txt") or ""
        text=re.sub(r"\n{3,}","\n\n",text).strip()
        return text[:max_chars]
    except Exception as exc:
        LOGGER.warning("Article extraction failed for %s: %s",urlparse(url).netloc,exc)
        return ""

def choose_candidate(candidates:list[NewsCandidate],seen_urls:set[str])->NewsCandidate|None:
    return next((c for c in candidates if (c.original_link or c.link) and (c.original_link or c.link) not in seen_urls),None)

def today_iso()->str:return datetime.now().astimezone().date().isoformat()

def published_iso(value:str)->str|None:
    try:return parsedate_to_datetime(value).isoformat()
    except Exception:return None

def publisher_name(url:str)->str:
    host=urlparse(url).netloc.lower().removeprefix('www.')
    return host.split('.')[0].upper() if host else ""
