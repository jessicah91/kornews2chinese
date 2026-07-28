from __future__ import annotations
import logging
from src.ai import translate_article
from src.config import Settings
from src.db import get_admin_client,load_for_reprocess,update_study
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")

def main()->None:
    s=Settings.from_env(); db=get_admin_client(s.supabase_url,s.supabase_service_role_key); rows=load_for_reprocess(db)
    done=0
    for row in rows:
        title=(row.get("study_data") or {}).get("title_ko") or row.get("publisher_title") or "기사"
        body=row.get("source_text") or ""
        if len(body)<100:continue
        study=translate_article(s.deepl_api_key,title=title,body=body,source_url=row.get("source_url","") or "",max_sentences=s.max_sentences)
        update_study(db,row["id"],study.model_dump()); done+=1
    logging.info("Reprocessed %d articles",done)
if __name__=="__main__":main()
