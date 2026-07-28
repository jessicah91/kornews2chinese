from __future__ import annotations
import os
from datetime import date
import streamlit as st
from supabase import create_client
st.set_page_config(page_title="K-News Chinese Reader",page_icon="📰",layout="wide")

def secret(name:str)->str:
    try:return str(st.secrets[name])
    except Exception:return os.getenv(name,"")
@st.cache_resource
def db():
    url=secret("SUPABASE_URL").rstrip('/'); key=secret("SUPABASE_ANON_KEY")
    if not url or not key:st.error("Streamlit Secrets에 SUPABASE_URL과 SUPABASE_ANON_KEY를 설정해 주세요.");st.stop()
    return create_client(url,key)
@st.cache_data(ttl=300)
def load_articles():
    return db().table("articles").select("id,source_url,category,collected_date,study_data,created_at").eq("is_published",True).order("created_at",desc=True).limit(200).execute().data or []

def safe(data,key,default=""):return data.get(key,default) if isinstance(data,dict) else default
articles=load_articles();st.title("📰 한국 뉴스로 배우는 중국어");st.caption("한국어 전문 · 중국어 번역 · 병음 · 단어 · 문법 · 퀴즈")
if not articles:st.info("아직 등록된 기사가 없습니다.");st.stop()
valid=[a for a in articles if isinstance(a.get("study_data"),dict) and safe(a["study_data"],"title_ko")]
if not valid:st.warning("학습 데이터가 없습니다. GitHub Actions에서 reprocess를 실행해 주세요.");st.stop()
categories=["전체"]+sorted({a.get("category") or "기타" for a in valid});selected_category=st.sidebar.selectbox("분야",categories);show_pinyin=st.sidebar.toggle("병음 보기",True);show_korean=st.sidebar.toggle("한국어 보기",True)
dates=sorted({a["collected_date"] for a in valid if a.get("collected_date")},reverse=True);selected_date=st.sidebar.selectbox("날짜",dates,index=0)
filtered=[a for a in valid if a.get("collected_date")==selected_date and (selected_category=="전체" or (a.get("category") or "기타")==selected_category)]
if not filtered:st.warning("선택 조건에 해당하는 기사가 없습니다.");st.stop()
query_id=st.query_params.get("article");index=next((i for i,a in enumerate(filtered) if str(a["id"])==str(query_id)),0) if query_id else 0
labels=[f"[{a.get('category','기타')}] {safe(a['study_data'],'title_ko')}" for a in filtered];selected=st.selectbox("기사 선택",labels,index=index);article=filtered[labels.index(selected)];data=article["study_data"]
st.header(safe(data,"title_ko"));st.subheader(safe(data,"title_zh"));
if show_pinyin:st.caption(safe(data,"title_pinyin"))
st.link_button("언론사 원문 열기",article["source_url"]);difficulty=int(safe(data,"difficulty",3) or 3);st.progress(min(max(difficulty,1),5)/5,text=f"난이도 {difficulty}/5")
with st.expander("기사 요약",expanded=True):
    if show_korean:st.write(safe(data,"summary_ko"))
    st.write(safe(data,"summary_zh"))
st.divider();st.subheader("문장별 전문 번역")
for idx,pair in enumerate(safe(data,"sentence_pairs",[]),1):
    with st.container(border=True):
        st.markdown(f"**{idx}. {pair.get('chinese','')}**")
        if show_pinyin:st.caption(pair.get("pinyin",""))
        if show_korean:st.write(pair.get("korean",""))
left,right=st.columns(2)
with left:
    st.subheader("핵심 단어")
    vocab=safe(data,"vocabulary",[])
    if not vocab:st.info("추출된 단어가 없습니다.")
    for item in vocab:
        with st.expander(f"{item.get('word','')} · {item.get('pinyin','')}"):
            st.write(item.get("meaning_ko",""));st.write(item.get("example_zh",""));st.caption(item.get("example_ko",""))
with right:
    st.subheader("뉴스 표현과 문법")
    grammar=safe(data,"grammar",[])
    if not grammar:st.info("본문에서 지정 문법 패턴이 발견되지 않았습니다.")
    for item in grammar:
        with st.expander(item.get("expression","표현")):
            st.write(item.get("explanation_ko",""));st.write(item.get("example_zh",""));st.caption(item.get("example_ko",""))
st.divider();st.subheader("독해 퀴즈")
quizzes=safe(data,"quizzes",[])
if not quizzes:st.info("생성된 퀴즈가 없습니다.")
for qi,q in enumerate(quizzes):
    choice=st.radio(q.get("question_ko","문제"),q.get("choices",[]),index=None,key=f"{article['id']}-{qi}")
    if choice is not None:
        chosen=q.get("choices",[]).index(choice)
        (st.success if chosen==q.get("answer_index") else st.error)("정답이에요" if chosen==q.get("answer_index") else "다시 생각해 보세요")
        st.caption(q.get("explanation_ko",""))
