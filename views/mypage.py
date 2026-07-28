from __future__ import annotations

from typing import Any

import streamlit as st

from utils.articles import title_ko


def render_mypage(articles: list[dict[str, Any]]) -> None:
    studied_ids = st.session_state.get("studied_article_ids", [])
    saved_ids = st.session_state.get("saved_article_ids", [])
    words = st.session_state.get("saved_words", [])

    st.markdown(
        """
        <section class="page-head">
            <div class="page-eyebrow">LEARNING PROGRESS</div>
            <h1 class="page-title">마이페이지</h1>
            <div class="page-copy">현재 브라우저에 저장된 학습 기록과 기본 표시 설정을 확인하세요.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="medium")
    stats = [
        ("학습한 기사", len(studied_ids), "개"),
        ("저장한 단어", len(words), "개"),
        ("즐겨찾기", len(saved_ids), "개"),
    ]
    for col, (label, number, unit) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="meta">{label}</div>
                    <div class="stat-number">{number}{unit}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-heading">최근 학습한 기사</div>', unsafe_allow_html=True)
    recent = [article for article_id in reversed(studied_ids) for article in articles if article.get("id") == article_id][:5]

    if not recent:
        st.markdown('<div class="empty">아직 학습 기록이 없습니다.</div>', unsafe_allow_html=True)
    else:
        with st.container(border=True):
            for article in recent:
                if st.button(title_ko(article), key=f"recent_{article.get('id')}", use_container_width=True):
                    st.session_state["selected_article_id"] = article.get("id")
                    st.rerun()

    st.markdown('<div class="section-heading">학습 설정</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.session_state["show_pinyin"] = st.toggle("병음 기본 표시", value=st.session_state.get("show_pinyin", True))
        st.session_state["show_korean"] = st.toggle("한국어 기본 표시", value=st.session_state.get("show_korean", True))
