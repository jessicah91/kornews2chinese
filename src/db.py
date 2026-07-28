from __future__ import annotations
from supabase import Client, create_client

def get_admin_client(url:str,service_role_key:str)->Client:return create_client(url,service_role_key)
def existing_urls(client:Client)->set[str]:
    r=client.table("articles").select("source_url").execute()
    return {x["source_url"] for x in (r.data or []) if x.get("source_url")}
def save_article(client:Client,payload:dict)->dict:
    r=client.table("articles").upsert(payload,on_conflict="source_url").execute()
    if not r.data:raise RuntimeError("Supabase returned no saved row")
    return r.data[0]
def load_for_reprocess(client:Client,limit:int=100)->list[dict]:
    r=client.table("articles").select("id,source_url,publisher_title,source_text,study_data").order("created_at",desc=True).limit(limit).execute()
    return r.data or []
def update_study(client:Client,row_id:str,study_data:dict)->None:
    client.table("articles").update({"study_data":study_data,"processing_status":"completed","processing_error":None}).eq("id",row_id).execute()
