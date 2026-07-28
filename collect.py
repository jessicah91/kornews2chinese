from __future__ import annotations
import logging
from src.ai import translate_article
from src.config import Settings
from src.db import existing_urls,get_admin_client,save_article
from src.emailer import send_digest
from src.news import choose_candidate,extract_article_text,published_iso,publisher_name,search_naver_news,today_iso
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
LOGGER=logging.getLogger(__name__)

def main()->None:
    s=Settings.from_env(); db=get_admin_client(s.supabase_url,s.supabase_service_role_key); seen=existing_urls(db); saved=[]
    for query in s.news_queries:
        candidates=search_naver_news(s.naver_client_id,s.naver_client_secret,query,display=max(100)); used=0
        while used<s.articles_per_query:
            c=choose_candidate(candidates,seen)
            if not c:break
            candidates.remove(c); url=c.original_link or c.link; seen.add(url)
            body=extract_article_text(url,s.max_article_chars)
            if len(body)<500:
                LOGGER.warning("Skipping short/unavailable article: %s",url); continue
            study=translate_article(s.deepl_api_key,title=c.title,body=body,source_url=url,max_sentences=s.max_sentences)
            row=save_article(db,{"source_url":url,"naver_url":c.link,"publisher_name":publisher_name(url),"publisher_title":c.title,"category":query,"author_name":None,"published_at":published_iso(c.published_at),"published_at_text":c.published_at,"collected_date":today_iso(),"source_text":body,"study_data":study.model_dump(),"processing_status":"completed","processing_error":None,"ai_model":"DeepL + deterministic study tools","is_published":True})
            saved.append(row); used+=1
    if s.resend_api_key and s.email_from and s.email_to:
        send_digest(s.resend_api_key,s.email_from,s.email_to,s.app_url,saved)
    LOGGER.info("Done. Saved %d articles.",len(saved))
if __name__=="__main__":main()
