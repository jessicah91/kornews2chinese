from __future__ import annotations

import os
from datetime import date

import streamlit as st
from supabase import create_client

st.set_page_config(page_title="K-News Chinese Reader", page_icon="📰", layout="wide")


def secret(name: str) -> str:
    try:
        return str(st.secrets[name])
    except Exception:
        return os.getenv(name, "")


@st.cache_resource
def db():
    url = secret("SUPABASE_URL")
    key = secret("SUPABASE_ANON_KEY")
    if not url or not key:
        st.error("SUPABASE_URL과 SUPABASE_ANON_KEY를 설정해 주세요.")
        st.stop()
    return create_client(url, key)


@st.cache_data(ttl=300)
def load_articles():
    result = db().table("articles").select("id,source_url,category,collected_date,study_data").order("created_at", desc=True).limit(100).execute()
    return result.data or []


articles = load_articles()
st.title("📰 한국 뉴스로 배우는 중국어")
st.caption("한국어 전문 · 중국어 번역 · 병음 · 단어 · 문법 · 퀴즈")

if not articles:
    st.info("아직 등록된 기사가 없습니다. collect.py를 먼저 실행해 주세요.")
    st.stop()

categories = ["전체"] + sorted({a["category"] for a in articles})
selected_category = st.sidebar.selectbox("분야", categories)
show_pinyin = st.sidebar.toggle("병음 보기", value=True)
show_korean = st.sidebar.toggle("한국어 보기", value=True)
selected_date = st.sidebar.date_input("날짜", value=date.fromisoformat(articles[0]["collected_date"]))

filtered = [a for a in articles if a["collected_date"] == selected_date.isoformat()]
if selected_category != "전체":
    filtered = [a for a in filtered if a["category"] == selected_category]
if not filtered:
    st.warning("선택한 조건에 해당하는 기사가 없습니다.")
    st.stop()

query_id = st.query_params.get("article")
index = 0
if query_id:
    index = next((i for i, a in enumerate(filtered) if str(a["id"]) == str(query_id)), 0)
labels = [f"[{a['category']}] {a['study_data']['title_ko']}" for a in filtered]
selected_label = st.selectbox("기사 선택", labels, index=index)
article = filtered[labels.index(selected_label)]
data = article["study_data"]

st.header(data["title_ko"])
st.subheader(data["title_zh"])
if show_pinyin:
    st.caption(data.get("title_pinyin", ""))
st.markdown(f"[언론사 원문 열기]({article['source_url']})")
st.progress(data.get("difficulty", 3) / 5, text=f"난이도 {data.get('difficulty', 3)}/5")

with st.expander("기사 요약", expanded=True):
    if show_korean:
        st.write(data["summary_ko"])
    st.write(data["summary_zh"])

st.divider()
st.subheader("문장별 전문 번역")
for idx, pair in enumerate(data["sentence_pairs"], start=1):
    with st.container(border=True):
        st.markdown(f"**{idx}. {pair['chinese']}**")
        if show_pinyin:
            st.caption(pair["pinyin"])
        if show_korean:
            st.write(pair["korean"])

left, right = st.columns(2)
with left:
    st.subheader("핵심 단어")
    for item in data["vocabulary"]:
        with st.expander(f"{item['word']} · {item['pinyin']}"):
            st.write(item["meaning_ko"])
            if item.get("example_zh"):
                st.write(item["example_zh"])
                st.caption(item.get("example_ko", ""))
with right:
    st.subheader("뉴스 표현과 문법")
    for item in data["grammar"]:
        with st.expander(item["expression"]):
            st.write(item["explanation_ko"])
            st.write(item["example_zh"])
            st.caption(item["example_ko"])

st.divider()
st.subheader("독해 퀴즈")
for q_index, quiz in enumerate(data["quizzes"]):
    choice = st.radio(quiz["question_ko"], quiz["choices"], index=None, key=f"{article['id']}-{q_index}")
    if choice is not None:
        chosen = quiz["choices"].index(choice)
        if chosen == quiz["answer_index"]:
            st.success("정답이에요")
        else:
            st.error("다시 생각해 보세요")
        st.caption(quiz["explanation_ko"])
