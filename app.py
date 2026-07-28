from __future__ import annotations

import streamlit as st

from components.navigation import render_navigation
from components.theme import apply_theme
from services.data import load_articles
from views.article_detail import render_article_detail
from views.favorites import render_favorites
from views.home import render_home
from views.mypage import render_mypage
from views.search import render_search
from views.vocabulary import render_vocabulary


st.set_page_config(
    page_title="오늘의 중국어",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

DEFAULTS = {
    "page": "홈",
    "selected_article_id": None,
    "saved_article_ids": [],
    "saved_words": [],
    "studied_article_ids": [],
    "show_pinyin": True,
    "show_korean": True,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value

articles = load_articles()

render_navigation()

selected_id = st.session_state.get("selected_article_id")
if selected_id:
    selected = next((a for a in articles if a.get("id") == selected_id), None)
    if selected:
        render_article_detail(selected)
    else:
        st.session_state["selected_article_id"] = None
        st.rerun()
else:
    page = st.session_state.get("page", "홈")

    if page == "홈":
        render_home(articles)
    elif page == "기사 찾기":
        render_search(articles)
    elif page == "단어장":
        render_vocabulary()
    elif page == "즐겨찾기":
        render_favorites(articles)
    elif page == "마이페이지":
        render_mypage(articles)
    else:
        st.session_state["page"] = "홈"
        st.rerun()
