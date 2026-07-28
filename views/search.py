from __future__ import annotations

from typing import Any

import streamlit as st

from components.article_card import render_article_card
from utils.articles import TOPICS, difficulty, searchable_text, topic


def render_search(articles: list[dict[str, Any]]) -> None:
    st.markdown(
        """
        <section class="page-head">
            <div class="page-eyebrow">ARTICLE LIBRARY</div>
            <h1 class="page-title">기사 찾기</h1>
            <div class="page-copy">관심 있는 주제와 난이도를 골라 오늘 공부할 중국어 기사를 찾아보세요.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        left, middle, right = st.columns([2.2, 1.15, 1.35], gap="medium")
        with left:
            query = st.text_input("검색어", placeholder="예: 반도체, 중국, 금리")
        with middle:
            default_topic = st.session_state.pop("search_topic", "전체")
            topic_index = TOPICS.index(default_topic) if default_topic in TOPICS else 0
            selected_topic = st.selectbox("카테고리", TOPICS, index=topic_index)
        with right:
            levels = st.multiselect("난이도", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])

        sort = st.radio("정렬", ["추천순", "최신순", "쉬운 순"], horizontal=True)

    filtered = []
    for article in articles:
        if selected_topic != "전체" and topic(article) != selected_topic:
            continue
        if difficulty(article) not in levels:
            continue
        if query.strip() and query.strip().lower() not in searchable_text(article):
            continue
        filtered.append(article)

    if sort == "추천순":
        from utils.articles import recommendation_score
        filtered.sort(key=recommendation_score, reverse=True)
    elif sort == "쉬운 순":
        filtered.sort(key=difficulty)

    st.markdown(
        f'<div class="section-heading-row"><div class="section-heading">검색 결과 {len(filtered)}개</div><div class="section-caption">조건에 맞는 학습 콘텐츠</div></div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown('<div class="empty">조건에 맞는 기사가 없습니다.<br>검색어나 필터를 조금 넓혀보세요.</div>', unsafe_allow_html=True)
        return

    for article in filtered:
        render_article_card(article, "search")
