from __future__ import annotations

from typing import Any

import streamlit as st

from utils.articles import (
    estimated_minutes, format_date, hsk, publisher, safe, summary,
    title_ko, title_zh, topic,
)


def open_article(article: dict[str, Any]) -> None:
    st.session_state["selected_article_id"] = article.get("id")
    studied = st.session_state.setdefault("studied_article_ids", [])
    if article.get("id") not in studied:
        studied.append(article.get("id"))


def render_article_card(article: dict[str, Any], key_prefix: str = "card") -> None:
    article_id = article.get("id")
    saved = article_id in st.session_state.get("saved_article_ids", [])

    st.markdown(
        f"""
        <article class="article-card">
            <span class="badge">{safe(topic(article))}</span>
            <span class="badge">{safe(hsk(article))}</span>
            <span class="badge">약 {estimated_minutes(article)}분</span>
            <div class="article-title">{safe(title_ko(article))}</div>
            <div class="article-zh">{safe(title_zh(article))}</div>
            <div class="meta" style="margin-top:.72rem;">
                {safe(publisher(article))} · {safe(format_date(article.get("published_at")))}
            </div>
            {
                f'<div class="meta" style="margin-top:.6rem;">{safe(summary(article))}</div>'
                if summary(article) else ''
            }
        </article>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([3.3, 1])
    with left:
        if st.button("이 기사로 공부하기 →", key=f"{key_prefix}_open_{article_id}", type="primary", use_container_width=True):
            open_article(article)
            st.rerun()
    with right:
        if st.button("♥ 저장됨" if saved else "♡ 저장", key=f"{key_prefix}_save_{article_id}", use_container_width=True):
            ids = st.session_state.setdefault("saved_article_ids", [])
            if saved:
                ids.remove(article_id)
            else:
                ids.append(article_id)
            st.rerun()
