from __future__ import annotations

from supabase import Client, create_client


def get_admin_client(url: str, service_role_key: str) -> Client:
    return create_client(url, service_role_key)


def existing_urls(client: Client) -> set[str]:
    response = client.table("articles").select("source_url").execute()
    return {row["source_url"] for row in (response.data or []) if row.get("source_url")}


def save_article(client: Client, payload: dict) -> dict:
    response = client.table("articles").upsert(payload, on_conflict="source_url").execute()
    if not response.data:
        raise RuntimeError("Supabase returned no saved row")
    return response.data[0]
