from __future__ import annotations

import streamlit as st


def render_vocabulary() -> None:
    words = st.session_state.get("saved_words", [])
    st.markdown(
        f"""
        <section class="page-head">
            <div class="page-eyebrow">MY VOCABULARY</div>
            <h1 class="page-title">단어장</h1>
            <div class="page-copy">기사에서 저장한 단어를 다시 보고, 중국어·병음·뜻으로 빠르게 검색하세요.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not words:
        st.markdown(
            '<div class="empty">저장한 단어가 아직 없습니다.<br>기사의 핵심 단어에서 단어를 저장해보세요.</div>',
            unsafe_allow_html=True,
        )
        return

    query = st.text_input("단어 검색", placeholder="중국어, 병음 또는 뜻")
    filtered = [
        word for word in words
        if not query.strip() or query.lower() in " ".join(
            str(word.get(k) or "") for k in ("word", "pinyin", "meaning", "article_title")
        ).lower()
    ]

    st.markdown(
        f'<div class="section-heading-row"><div class="section-heading">저장한 단어 {len(filtered)}개</div><div class="section-caption">전체 {len(words)}개</div></div>',
        unsafe_allow_html=True,
    )

    for index, word in enumerate(filtered):
        with st.container(border=True):
            cols = st.columns([4.5, 1], vertical_alignment="center")
            with cols[0]:
                st.markdown(f"### {word.get('word', '')}")
                if word.get("pinyin"):
                    st.markdown(f'<div class="sentence-pinyin">{word["pinyin"]}</div>', unsafe_allow_html=True)
                st.write(word.get("meaning", ""))
                if word.get("example"):
                    st.markdown(f"**예문**  \n{word['example']}")
                st.caption(f"출처: {word.get('article_title', '')}")
            with cols[1]:
                if st.button("삭제", key=f"delete_word_{index}", use_container_width=True):
                    st.session_state["saved_words"].remove(word)
                    st.rerun()
