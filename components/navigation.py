from __future__ import annotations

import streamlit as st


PAGES = ["홈", "기사 찾기", "단어장", "즐겨찾기", "마이페이지"]


def _go(page: str) -> None:
    st.session_state["page"] = page
    st.session_state["selected_article_id"] = None


def render_navigation() -> None:
    brand, *menu_cols = st.columns([3.6, .72, .95, .78, .88, .92], vertical_alignment="center")

    with brand:
        st.markdown(
            """
            <div class="brand-row">
                <div class="brand-mark">中</div>
                <div>
                    <div class="brand-name">Chinese Daily</div>
                    <div class="brand-sub">뉴스로 배우는 중국어</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    current = st.session_state.get("page", "홈")
    for col, page in zip(menu_cols, PAGES):
        with col:
            if st.button(
                page,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if current == page and not st.session_state.get("selected_article_id") else "secondary",
            ):
                _go(page)
                st.rerun()

