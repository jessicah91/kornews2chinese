from __future__ import annotations

from typing import Any

import streamlit as st

from utils.articles import (
    difficulty, difficulty_label, estimated_minutes, format_date, hsk,
    item_value, publisher, safe, sentence_pairs, study_data, summary,
    title_ko, title_pinyin, title_zh, topic,
)


def render_article_detail(article: dict[str, Any]) -> None:
    if st.button("← 목록으로"):
        st.session_state["selected_article_id"] = None
        st.rerun()

    article_id = article.get("id")
    data = study_data(article)

    st.markdown(
        f"""
        <div style="margin-top:1.1rem;">
            <span class="badge">{safe(topic(article))}</span>
            <span class="badge">{safe(hsk(article))}</span>
            <span class="badge">약 {estimated_minutes(article)}분</span>
            <div class="meta" style="margin-top:.6rem;">
                {safe(publisher(article))} · {safe(format_date(article.get("published_at")))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title(title_ko(article))
    if title_zh(article):
        st.markdown(f'<div class="article-zh" style="font-size:1.3rem;">{safe(title_zh(article))}</div>', unsafe_allow_html=True)
    if st.session_state.get("show_pinyin") and title_pinyin(article):
        st.markdown(f'<div class="sentence-pinyin">{safe(title_pinyin(article))}</div>', unsafe_allow_html=True)

    actions = st.columns([1, 1, 2])
    saved = article_id in st.session_state.get("saved_article_ids", [])
    with actions[0]:
        if st.button("♥ 저장됨" if saved else "♡ 즐겨찾기", use_container_width=True):
            ids = st.session_state.setdefault("saved_article_ids", [])
            ids.remove(article_id) if saved else ids.append(article_id)
            st.rerun()
    with actions[1]:
        source_url = article.get("source_url")
        if source_url:
            st.link_button("원문 보기", source_url, use_container_width=True)

    if summary(article):
        st.markdown('<div class="section-heading">기사 요약</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="surface">{safe(summary(article))}</div>', unsafe_allow_html=True)

    reading_tab, vocab_tab, grammar_tab, quiz_tab = st.tabs(["문장별 읽기", "핵심 단어", "문법", "퀴즈"])

    with reading_tab:
        toggle_cols = st.columns(2)
        with toggle_cols[0]:
            st.session_state["show_pinyin"] = st.toggle("병음 보기", value=st.session_state.get("show_pinyin", True))
        with toggle_cols[1]:
            st.session_state["show_korean"] = st.toggle("한국어 보기", value=st.session_state.get("show_korean", True))

        pairs = sentence_pairs(article)
        if not pairs:
            st.info("문장별 학습 데이터가 없습니다.")
        for index, pair in enumerate(pairs, start=1):
            zh = item_value(pair, "zh", "chinese", "translated", "sentence_zh")
            py = item_value(pair, "pinyin", "sentence_pinyin")
            ko = item_value(pair, "ko", "korean", "original", "sentence_ko")
            st.markdown(
                f"""
                <div class="sentence-box">
                    <div class="meta">문장 {index}</div>
                    <div class="sentence-zh">{safe(zh)}</div>
                    {f'<div class="sentence-pinyin">{safe(py)}</div>' if st.session_state["show_pinyin"] and py else ''}
                    {f'<div class="sentence-ko">{safe(ko)}</div>' if st.session_state["show_korean"] and ko else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with vocab_tab:
        vocabulary = data.get("vocabulary") or []
        if not vocabulary:
            st.info("추출된 핵심 단어가 없습니다.")
        for index, item in enumerate(vocabulary):
            if not isinstance(item, dict):
                continue
            word = item_value(item, "word", "zh", "chinese")
            py = item_value(item, "pinyin")
            meaning = item_value(item, "meaning_ko", "meaning", "ko")
            example = item_value(item, "example", "sentence")
            with st.container(border=True):
                st.markdown(f"### {word}")
                if py:
                    st.caption(py)
                if meaning:
                    st.write(meaning)
                if example:
                    st.markdown(f"**예문**  \n{example}")

                saved_words = st.session_state.setdefault("saved_words", [])
                signature = f"{article_id}:{word}:{meaning}"
                exists = any(item.get("signature") == signature for item in saved_words)
                if st.button("✓ 저장됨" if exists else "＋ 단어 저장", key=f"save_word_{article_id}_{index}", disabled=exists):
                    saved_words.append({
                        "signature": signature,
                        "article_id": article_id,
                        "word": word,
                        "pinyin": py,
                        "meaning": meaning,
                        "example": example,
                        "article_title": title_ko(article),
                    })
                    st.rerun()

    with grammar_tab:
        grammar = data.get("grammar") or []
        if not grammar:
            st.info("추출된 문법 표현이 없습니다.")
        for index, item in enumerate(grammar, start=1):
            if isinstance(item, str):
                st.markdown(f"**{index}. {item}**")
            elif isinstance(item, dict):
                pattern = item_value(item, "pattern", "grammar", "expression")
                explanation = item_value(item, "explanation_ko", "explanation", "meaning")
                example = item_value(item, "example", "sentence")
                with st.container(border=True):
                    st.markdown(f"### {index}. {pattern}")
                    if explanation:
                        st.write(explanation)
                    if example:
                        st.markdown(f"**기사 속 예문**  \n{example}")

    with quiz_tab:
        quizzes = data.get("quizzes") or []
        if not quizzes:
            st.info("생성된 퀴즈가 없습니다.")
        for index, quiz in enumerate(quizzes, start=1):
            if not isinstance(quiz, dict):
                continue
            question = item_value(quiz, "question", "question_ko")
            options = quiz.get("options") or quiz.get("choices") or []
            answer = quiz.get("answer")
            explanation = item_value(quiz, "explanation", "explanation_ko")
            with st.container(border=True):
                st.markdown(f"### {index}. {question}")
                if isinstance(options, list) and options:
                    selected = st.radio("정답 선택", options, index=None, key=f"quiz_{article_id}_{index}")
                    if st.button("정답 확인", key=f"check_{article_id}_{index}"):
                        correct = str(options[answer]) if isinstance(answer, int) and 0 <= answer < len(options) else str(answer or "")
                        if selected is None:
                            st.warning("답을 먼저 선택해주세요.")
                        elif str(selected) == correct:
                            st.success("정답이에요! 🎉")
                        else:
                            st.error(f"정답은 {correct}입니다.")
                        if explanation:
                            st.info(explanation)
