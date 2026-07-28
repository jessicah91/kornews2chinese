from __future__ import annotations

from typing import Any

import streamlit as st

from components.article_card import render_article_card


def render_favorites(articles: list[dict[str, Any]]) -> None:
    st.title("즐겨찾기")
    ids = st.session_state.get("saved_article_ids", [])
    saved = [article for article in articles if article.get("id") in ids]

    if not saved:
        st.markdown(
            '<div class="empty">저장한 기사가 아직 없습니다.<br>관심 있는 기사를 즐겨찾기에 추가해보세요.</div>',
            unsafe_allow_html=True,
        )
        return

    st.caption(f"저장한 기사 {len(saved)}개")
    for article in saved:
        render_article_card(article, "favorite")
