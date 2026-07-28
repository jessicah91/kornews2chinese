from __future__ import annotations

import streamlit as st


PAGES = ["홈", "기사 찾기", "단어장", "즐겨찾기", "마이페이지"]


def _go(page: str) -> None:
    st.session_state["page"] = page
    st.session_state["selected_article_id"] = None


def render_navigation() -> None:
    st.markdown('<div class="brand">🌿 오늘의 중국어</div>', unsafe_allow_html=True)

    cols = st.columns([1, 1.15, 1, 1, 1.05])
    current = st.session_state.get("page", "홈")

    for col, page in zip(cols, PAGES):
        with col:
            if st.button(
                page,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if current == page and not st.session_state.get("selected_article_id") else "secondary",
            ):
                _go(page)
                st.rerun()
