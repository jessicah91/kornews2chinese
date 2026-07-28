from __future__ import annotations

from typing import Any

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
    except KeyError:
        st.error("Streamlit Secrets에 SUPABASE_URL과 SUPABASE_ANON_KEY를 등록해주세요.")
        st.stop()

    return create_client(url, key)


@st.cache_data(ttl=300, show_spinner=False)
def load_articles() -> list[dict[str, Any]]:
    try:
        response = (
            get_supabase_client()
            .table("articles")
            .select("*")
            .eq("is_published", True)
            .order("created_at", desc=True)
            .limit(150)
            .execute()
        )
        return response.data or []
    except Exception as exc:
        st.error(f"기사를 불러오지 못했습니다: {exc}")
        return []
