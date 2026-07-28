from __future__ import annotations

from typing import Any

import streamlit as st

from components.article_card import render_article_card


def render_favorites(articles: list[dict[str, Any]]) -> None:
    ids = st.session_state.get("saved_article_ids", [])
    saved = [article for article in articles if article.get("id") in ids]

    st.markdown(
        """
        <section class="page-head">
            <div class="page-eyebrow">SAVED ARTICLES</div>
            <h1 class="page-title">즐겨찾기</h1>
            <div class="page-copy">나중에 다시 읽고 싶은 기사와 학습 콘텐츠를 한곳에 모아보세요.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not saved:
        st.markdown(
            '<div class="empty">저장한 기사가 아직 없습니다.<br>관심 있는 기사를 즐겨찾기에 추가해보세요.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="section-heading-row"><div class="section-heading">저장한 기사 {len(saved)}개</div><div class="section-caption">다시 학습하기</div></div>',
        unsafe_allow_html=True,
    )
    for article in saved:
        render_article_card(article, "favorite")
