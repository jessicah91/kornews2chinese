from __future__ import annotations

from typing import Any

import streamlit as st

from components.article_card import open_article, render_article_card
from components.daily_expression import render_daily_expression
from utils.articles import TOPICS, recommendation_score, topic


TOPIC_ICONS = {
    "전체": "📰", "국제": "🌏", "정치": "🏛️", "경제": "📈", "사회": "👥",
    "IT·과학": "💻", "문화·생활": "🎨", "연예": "🎬", "스포츠": "⚽",
}


def render_home(articles: list[dict[str, Any]]) -> None:
    st.markdown(
        '''
        <section class="hero">
            <div class="eyebrow">오늘의 중국어 뉴스 학습</div>
            <div class="hero-title">매일 한국 뉴스를<br>중국어로 공부하세요</div>
            <div class="hero-copy">
                관심 있는 기사를 골라 중국어 문장, 병음, 핵심 단어와 퀴즈까지
                한 흐름으로 학습해보세요.
            </div>
        </section>
        ''',
        unsafe_allow_html=True,
    )

    if not articles:
        render_daily_expression([])
        st.markdown('<div class="empty">아직 저장된 기사가 없습니다.</div>', unsafe_allow_html=True)
        return

    recommended = max(articles, key=recommendation_score)
    if st.button("오늘의 추천 기사 시작하기", type="primary", use_container_width=True):
        open_article(recommended)
        st.rerun()

    render_daily_expression(articles)

    st.markdown('<div class="section-heading">오늘의 추천</div>', unsafe_allow_html=True)
    render_article_card(recommended, "recommended")

    st.markdown('<div class="section-heading">카테고리 둘러보기</div>', unsafe_allow_html=True)
    rows = [TOPICS[1:6], TOPICS[6:]]
    for row_index, row in enumerate(rows):
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            count = sum(1 for article in articles if topic(article) == name)
            with col:
                if st.button(
                    f"{TOPIC_ICONS[name]} {name}\n{count}개",
                    key=f"home_topic_{row_index}_{name}",
                    use_container_width=True,
                ):
                    st.session_state["search_topic"] = name
                    st.session_state["page"] = "기사 찾기"
                    st.rerun()

    st.markdown('<div class="section-heading">최신 기사</div>', unsafe_allow_html=True)
    for article in articles[:6]:
        render_article_card(article, "latest")
