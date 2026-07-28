from __future__ import annotations

from typing import Any

import streamlit as st

from components.article_card import open_article, render_article_card
from components.daily_expression import get_daily_expression
from utils.articles import (
    TOPICS,
    estimated_minutes,
    hsk,
    publisher,
    recommendation_score,
    safe,
    summary,
    title_ko,
    title_zh,
    topic,
)


TOPIC_ICONS = {
    "전체": "📰",
    "국제": "🌏",
    "정치": "🏛️",
    "경제": "📈",
    "사회": "👥",
    "IT·과학": "💻",
    "문화·생활": "🎨",
    "연예": "🎬",
    "스포츠": "⚽",
}


def _render_expression_card(articles: list[dict[str, Any]]) -> dict[str, Any]:
    expression = get_daily_expression(articles)

    example_html = ""
    if expression.get("example"):
        translation = (
            f'<div class="expression-example-ko">{safe(expression.get("translation"))}</div>'
            if expression.get("translation")
            else ""
        )
        example_html = f"""
        <div class="expression-example">
            <div class="expression-example-title">기사처럼 써보기</div>
            <div class="expression-example-zh">{safe(expression.get('example'))}</div>
            {translation}
        </div>
        """

    pinyin_html = (
        f'<div class="expression-pinyin">{safe(expression.get("pinyin"))}</div>'
        if expression.get("pinyin")
        else ""
    )
    meaning_html = (
        f'<div class="expression-meaning">{safe(expression.get("meaning"))}</div>'
        if expression.get("meaning")
        else ""
    )

    st.markdown(
        f"""
        <section class="hero-expression">
            <div class="expression-head">
                <div class="expression-label">🌱 오늘의 표현</div>
                <div class="expression-type">{safe(expression.get('type', '문법'))}</div>
            </div>
            <div class="expression-main">{safe(expression.get('expression'))}</div>
            {pinyin_html}
            {meaning_html}
            {example_html}
        </section>
        """,
        unsafe_allow_html=True,
    )
    return expression


def _render_featured_article(article: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <section class="featured-card">
            <div class="featured-kicker">EDITOR'S PICK · 오늘 가장 먼저 읽을 기사</div>
            <div class="featured-title">{safe(title_ko(article))}</div>
            <div class="featured-zh">{safe(title_zh(article))}</div>
            <div class="featured-summary">{safe(summary(article) or '핵심 내용을 읽고 문장, 단어, 표현, 퀴즈까지 한 번에 학습해보세요.')}</div>
            <div class="featured-metrics">
                <div class="metric-box">
                    <div class="metric-label">난이도</div>
                    <div class="metric-value">{safe(hsk(article))}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">예상 학습 시간</div>
                    <div class="metric-value">약 {estimated_minutes(article)}분</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">카테고리</div>
                    <div class="metric-value">{safe(topic(article))}</div>
                </div>
            </div>
            <div class="meta" style="margin-top:1rem;">{safe(publisher(article))}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_home(articles: list[dict[str, Any]]) -> None:
    left, right = st.columns([1.12, .88], gap="large", vertical_alignment="center")

    with left:
        st.markdown(
            """
            <section class="hero-copy-wrap">
                <div class="hero-kicker">🌿 하루 10분 중국어 루틴</div>
                <h1 class="hero-title">뉴스로 배우는<br><span class="accent">진짜 중국어</span></h1>
                <div class="hero-copy">
                    매일 한국 뉴스를 중국어 학습 콘텐츠로 바꿔드립니다.
                    기사 한 편으로 문장, 병음, 핵심 단어, 문법 표현과 퀴즈까지 이어서 공부하세요.
                </div>
                <div class="hero-proof">
                    <span>한국 뉴스 기반</span>
                    <span>문장별 병음</span>
                    <span>AI 학습 콘텐츠</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if articles:
            recommended = max(articles, key=recommendation_score)
            if st.button("오늘의 뉴스로 공부하기 →", type="primary", key="hero_start", use_container_width=False):
                open_article(recommended)
                st.rerun()
        else:
            st.button("기사가 준비되면 시작할 수 있어요", disabled=True, use_container_width=False)

    with right:
        expression = _render_expression_card(articles)
        related_article = expression.get("article")
        if related_article and st.button(
            "이 표현이 나온 기사 보기 →",
            key=f"hero_expression_{related_article.get('id')}",
            use_container_width=True,
        ):
            open_article(related_article)
            st.rerun()

    if not articles:
        st.markdown('<div class="empty">아직 저장된 기사가 없습니다.</div>', unsafe_allow_html=True)
        return

    recommended = max(articles, key=recommendation_score)

    st.markdown(
        '<div class="section-heading-row"><div class="section-heading">오늘의 추천</div><div class="section-caption">가볍게 시작하기 좋은 기사 한 편</div></div>',
        unsafe_allow_html=True,
    )
    feature, action = st.columns([3.2, 1], gap="large", vertical_alignment="center")
    with feature:
        _render_featured_article(recommended)
    with action:
        if st.button("추천 기사 학습하기", type="primary", key="featured_start", use_container_width=True):
            open_article(recommended)
            st.rerun()
        if st.button("다른 기사 찾아보기", key="featured_search", use_container_width=True):
            st.session_state["page"] = "기사 찾기"
            st.rerun()

    st.markdown(
        '<div class="section-heading-row"><div class="section-heading">관심 분야부터 골라보기</div><div class="section-caption">카테고리별 최신 기사</div></div>',
        unsafe_allow_html=True,
    )

    visible_topics = ["국제", "경제", "사회", "IT·과학", "문화·생활", "스포츠"]
    cols = st.columns(3, gap="medium")
    for index, name in enumerate(visible_topics):
        count = sum(1 for article in articles if topic(article) == name)
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="topic-card">
                    <div class="topic-icon">{TOPIC_ICONS[name]}</div>
                    <div class="topic-name">{name}</div>
                    <div class="topic-count">학습 기사 {count}개</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("둘러보기", key=f"home_topic_{name}", use_container_width=True):
                st.session_state["search_topic"] = name
                st.session_state["page"] = "기사 찾기"
                st.rerun()

    st.markdown(
        '<div class="section-heading-row"><div class="section-heading">최신 기사</div><div class="section-caption">새로 올라온 학습 콘텐츠</div></div>',
        unsafe_allow_html=True,
    )
    for article in articles[:6]:
        render_article_card(article, "latest")
