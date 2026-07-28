from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st
from supabase import Client, create_client


st.set_page_config(
    page_title="오늘의 중국어 뉴스",
    page_icon="📰",
    layout="wide",
)


# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 2.15rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .sub-title {
        color: #6b7280;
        margin-bottom: 1.8rem;
    }

    .article-card {
        padding: 1.25rem 1.4rem;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        margin-bottom: 1rem;
        background: white;
    }

    .meta-badge {
        display: inline-block;
        padding: 0.25rem 0.62rem;
        border-radius: 999px;
        background: #f3f4f6;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        font-size: 0.85rem;
    }

    .chinese-sentence {
        font-size: 1.22rem;
        line-height: 1.9;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    .pinyin-sentence {
        color: #2563eb;
        line-height: 1.7;
        margin-top: 0.2rem;
    }

    .korean-sentence {
        color: #4b5563;
        line-height: 1.7;
        margin-top: 0.25rem;
    }

    .sentence-box {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: #f9fafb;
        margin-bottom: 0.85rem;
    }

    .vocab-word {
        font-size: 1.15rem;
        font-weight: 700;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Supabase 연결
# -----------------------------
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
    except KeyError:
        st.error(
            "Streamlit Secrets에 SUPABASE_URL과 "
            "SUPABASE_ANON_KEY를 등록해주세요."
        )
        st.stop()

    return create_client(url, key)


@st.cache_data(ttl=300)
def load_articles() -> list[dict[str, Any]]:
    client = get_supabase_client()

    response = (
        client.table("articles")
        .select("*")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return response.data or []


# -----------------------------
# 데이터 보조 함수
# -----------------------------
def study_data(article: dict[str, Any]) -> dict[str, Any]:
    data = article.get("study_data")
    return data if isinstance(data, dict) else {}


def first_value(data: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = data.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return default


def article_title_ko(article: dict[str, Any]) -> str:
    data = study_data(article)

    return first_value(
        data,
        "title_ko",
        default=article.get("publisher_title") or "제목 없음",
    )


def article_title_zh(article: dict[str, Any]) -> str:
    data = study_data(article)
    return first_value(data, "title_zh", "translated_title")


def article_pinyin(article: dict[str, Any]) -> str:
    data = study_data(article)
    return first_value(data, "title_pinyin", "pinyin_title")


def normalize_difficulty(value: Any) -> int:
    if isinstance(value, int):
        return max(1, min(value, 5))

    if isinstance(value, float):
        return max(1, min(round(value), 5))

    if isinstance(value, str):
        digits = "".join(char for char in value if char.isdigit())

        if digits:
            return max(1, min(int(digits[0]), 5))

        lowered = value.lower()

        if "쉬움" in value or "easy" in lowered:
            return 2

        if "어려움" in value or "hard" in lowered:
            return 4

        if "매우" in value or "advanced" in lowered:
            return 5

    return 3


def difficulty_of(article: dict[str, Any]) -> int:
    return normalize_difficulty(study_data(article).get("difficulty", 3))


def difficulty_label(level: int) -> str:
    labels = {
        1: "매우 쉬움",
        2: "쉬움",
        3: "적당함",
        4: "도전",
        5: "매우 어려움",
    }

    return labels.get(level, "적당함")


def estimated_minutes(article: dict[str, Any]) -> int:
    data = study_data(article)
    sentence_pairs = data.get("sentence_pairs") or []

    if isinstance(sentence_pairs, list) and sentence_pairs:
        return max(3, round(len(sentence_pairs) * 1.2))

    source_text = article.get("source_text") or ""
    return max(3, round(len(source_text) / 500))


def format_date(value: Any) -> str:
    if not value:
        return ""

    text = str(value)

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%Y.%m.%d")
    except ValueError:
        return text[:10]


def publisher_of(article: dict[str, Any]) -> str:
    return article.get("publisher_name") or "언론사 미상"


def recommendation_score(article: dict[str, Any]) -> int:
    level = difficulty_of(article)
    data = study_data(article)

    score = 100

    # 학습 난이도 3을 가장 우선하고 4도 일부 허용
    score -= abs(level - 3) * 20

    if data.get("sentence_pairs"):
        score += 10

    if data.get("vocabulary"):
        score += 8

    if data.get("quizzes"):
        score += 5

    title = article_title_ko(article)

    important_terms = (
        "정부",
        "경제",
        "국제",
        "중국",
        "미국",
        "일본",
        "AI",
        "인공지능",
        "반도체",
        "교육",
        "환경",
        "외교",
        "금리",
        "환율",
    )

    score += sum(3 for term in important_terms if term in title)

    return score


def sentence_pairs_of(article: dict[str, Any]) -> list[dict[str, Any]]:
    data = study_data(article)
    pairs = data.get("sentence_pairs")

    if isinstance(pairs, list) and pairs:
        return [item for item in pairs if isinstance(item, dict)]

    chinese = first_value(
        data,
        "content_zh",
        "translated_text",
        "summary_zh",
    )

    korean = first_value(
        data,
        "content_ko",
        "summary_ko",
        default=article.get("source_text") or "",
    )

    pinyin = first_value(data, "pinyin", "content_pinyin")

    if not chinese and not korean:
        return []

    return [
        {
            "zh": chinese,
            "pinyin": pinyin,
            "ko": korean,
        }
    ]


def value_from_item(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


# -----------------------------
# 데이터 불러오기
# -----------------------------
articles = load_articles()

st.markdown(
    '<div class="main-title">📰 오늘의 중국어 뉴스</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">'
    "한국 주요 뉴스를 중국어로 읽고 단어·문법·퀴즈까지 공부해요"
    "</div>",
    unsafe_allow_html=True,
)

if not articles:
    st.warning("아직 저장된 기사가 없습니다.")
    st.stop()


# -----------------------------
# 사이드바 필터
# -----------------------------
with st.sidebar:
    st.header("학습 설정")

    publishers = sorted(
        {
            publisher_of(article)
            for article in articles
            if publisher_of(article)
        }
    )

    selected_publishers = st.multiselect(
        "언론사",
        options=publishers,
        default=publishers,
    )

    selected_levels = st.multiselect(
        "난이도",
        options=[1, 2, 3, 4, 5],
        default=[2, 3, 4],
        format_func=lambda value: f"{value} · {difficulty_label(value)}",
    )

    search_word = st.text_input(
        "기사 검색",
        placeholder="AI, 중국, 경제 등",
    )

    st.divider()

    show_korean = st.toggle("한국어 해석 보기", value=True)
    show_pinyin = st.toggle("병음 보기", value=True)

    st.caption("난이도 5는 기본 목록에서 제외돼요.")


filtered_articles: list[dict[str, Any]] = []

for article in articles:
    if publisher_of(article) not in selected_publishers:
        continue

    if difficulty_of(article) not in selected_levels:
        continue

    if search_word:
        searchable = " ".join(
            [
                article_title_ko(article),
                article_title_zh(article),
                article.get("category") or "",
                publisher_of(article),
            ]
        ).lower()

        if search_word.lower() not in searchable:
            continue

    filtered_articles.append(article)


if not filtered_articles:
    st.info("선택한 조건에 맞는 기사가 없습니다.")
    st.stop()


# -----------------------------
# 오늘의 추천 기사
# -----------------------------
recommended = max(filtered_articles, key=recommendation_score)
recommended_data = study_data(recommended)
recommended_level = difficulty_of(recommended)

st.subheader("🔥 오늘의 추천 기사")

st.markdown(
    f"""
    <div class="article-card">
        <span class="meta-badge">{publisher_of(recommended)}</span>
        <span class="meta-badge">
            난이도 {recommended_level} · {difficulty_label(recommended_level)}
        </span>
        <span class="meta-badge">
            예상 {estimated_minutes(recommended)}분
        </span>
        <span class="meta-badge">
            단어 {len(recommended_data.get("vocabulary") or [])}개
        </span>
        <h3>{article_title_ko(recommended)}</h3>
        <div class="small-muted">{article_title_zh(recommended)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# 기사 선택
# -----------------------------
st.subheader("📚 기사 선택")

selected_article = st.selectbox(
    "공부할 기사를 골라주세요",
    options=filtered_articles,
    format_func=lambda article: (
        f"[{publisher_of(article)}] "
        f"{article_title_ko(article)} "
        f"· 난이도 {difficulty_of(article)}"
    ),
)

data = study_data(selected_article)
level = difficulty_of(selected_article)

st.divider()

left, right = st.columns([4, 1])

with left:
    st.caption(
        " · ".join(
            filter(
                None,
                [
                    publisher_of(selected_article),
                    format_date(selected_article.get("published_at")),
                    selected_article.get("category"),
                ],
            )
        )
    )

    st.title(article_title_ko(selected_article))

    title_zh = article_title_zh(selected_article)

    if title_zh:
        st.markdown(
            f'<div class="chinese-sentence">{title_zh}</div>',
            unsafe_allow_html=True,
        )

    title_pinyin = article_pinyin(selected_article)

    if show_pinyin and title_pinyin:
        st.markdown(
            f'<div class="pinyin-sentence">{title_pinyin}</div>',
            unsafe_allow_html=True,
        )

with right:
    st.metric("난이도", f"{level} · {difficulty_label(level)}")
    st.metric("예상 시간", f"{estimated_minutes(selected_article)}분")

    source_url = selected_article.get("source_url")

    if source_url:
        st.link_button(
            "원문 기사 열기",
            source_url,
            use_container_width=True,
        )


summary_ko = first_value(data, "summary_ko")
summary_zh = first_value(data, "summary_zh")

if summary_ko or summary_zh:
    with st.container(border=True):
        st.subheader("한눈에 보기")

        if summary_zh:
            st.markdown(
                f'<div class="chinese-sentence">{summary_zh}</div>',
                unsafe_allow_html=True,
            )

        if show_korean and summary_ko:
            st.markdown(
                f'<div class="korean-sentence">{summary_ko}</div>',
                unsafe_allow_html=True,
            )


reading_tab, vocab_tab, grammar_tab, quiz_tab = st.tabs(
    [
        "📖 문장별 읽기",
        "🗂 핵심 단어",
        "🧩 문법",
        "✅ 퀴즈",
    ]
)


# -----------------------------
# 문장별 읽기
# -----------------------------
with reading_tab:
    pairs = sentence_pairs_of(selected_article)

    if not pairs:
        st.info("문장별 학습 데이터가 없습니다.")
    else:
        for index, pair in enumerate(pairs, start=1):
            zh = value_from_item(
                pair,
                "zh",
                "chinese",
                "translated",
                "sentence_zh",
            )
            pinyin = value_from_item(
                pair,
                "pinyin",
                "sentence_pinyin",
            )
            ko = value_from_item(
                pair,
                "ko",
                "korean",
                "original",
                "sentence_ko",
            )

            st.markdown(
                f"""
                <div class="sentence-box">
                    <div class="small-muted">문장 {index}</div>
                    <div class="chinese-sentence">{zh}</div>
                    {
                        f'<div class="pinyin-sentence">{pinyin}</div>'
                        if show_pinyin and pinyin
                        else ''
                    }
                    {
                        f'<div class="korean-sentence">{ko}</div>'
                        if show_korean and ko
                        else ''
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )


# -----------------------------
# 단어
# -----------------------------
with vocab_tab:
    vocabulary = data.get("vocabulary") or []

    if not vocabulary:
        st.info("추출된 핵심 단어가 없습니다.")
    else:
        cols = st.columns(2)

        for index, item in enumerate(vocabulary):
            if not isinstance(item, dict):
                continue

            word = value_from_item(
                item,
                "word",
                "zh",
                "chinese",
            )
            pinyin = value_from_item(item, "pinyin")
            meaning = value_from_item(
                item,
                "meaning_ko",
                "meaning",
                "ko",
            )
            example = value_from_item(
                item,
                "example",
                "sentence",
            )

            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="vocab-word">{word}</div>',
                        unsafe_allow_html=True,
                    )

                    if pinyin:
                        st.caption(pinyin)

                    if meaning:
                        st.write(meaning)

                    if example:
                        st.markdown(f"예문: {example}")


# -----------------------------
# 문법
# -----------------------------
with grammar_tab:
    grammar_items = data.get("grammar") or []

    if not grammar_items:
        st.info("이 기사에서 별도로 추출된 문법 표현이 없습니다.")
    else:
        for index, item in enumerate(grammar_items, start=1):
            if isinstance(item, str):
                with st.container(border=True):
                    st.markdown(f"**{index}. {item}**")
                continue

            if not isinstance(item, dict):
                continue

            pattern = value_from_item(
                item,
                "pattern",
                "grammar",
                "expression",
            )
            explanation = value_from_item(
                item,
                "explanation_ko",
                "explanation",
                "meaning",
            )
            example = value_from_item(
                item,
                "example",
                "sentence",
            )

            with st.container(border=True):
                st.markdown(f"### {index}. {pattern}")

                if explanation:
                    st.write(explanation)

                if example:
                    st.markdown(f"**기사 속 예문**  \n{example}")


# -----------------------------
# 퀴즈
# -----------------------------
with quiz_tab:
    quizzes = data.get("quizzes") or []

    if not quizzes:
        st.info("생성된 퀴즈가 없습니다.")
    else:
        for index, quiz in enumerate(quizzes, start=1):
            if not isinstance(quiz, dict):
                continue

            question = value_from_item(
                quiz,
                "question",
                "question_ko",
            )
            options = quiz.get("options") or quiz.get("choices") or []
            answer = quiz.get("answer")
            explanation = value_from_item(
                quiz,
                "explanation",
                "explanation_ko",
            )

            with st.container(border=True):
                st.markdown(f"### {index}. {question}")

                if isinstance(options, list) and options:
                    selected_answer = st.radio(
                        "정답 선택",
                        options=options,
                        key=f"quiz_{selected_article.get('id')}_{index}",
                        index=None,
                    )

                    if st.button(
                        f"{index}번 정답 확인",
                        key=f"check_{selected_article.get('id')}_{index}",
                    ):
                        correct_text = ""

                        if isinstance(answer, int):
                            if 0 <= answer < len(options):
                                correct_text = str(options[answer])
                            elif 1 <= answer <= len(options):
                                correct_text = str(options[answer - 1])
                        else:
                            correct_text = str(answer or "")

                        if selected_answer is None:
                            st.warning("답을 먼저 선택해주세요.")
                        elif str(selected_answer) == correct_text:
                            st.success("정답이에요! 🎉")
                        else:
                            st.error(f"아쉬워요. 정답은 `{correct_text}`입니다.")

                        if explanation:
                            st.info(explanation)
                else:
                    st.write("정답:", answer or "정답 정보 없음")


st.divider()
st.caption(
    "기사와 번역은 자동 수집된 자료입니다. "
    "번역 및 병음은 문맥에 따라 일부 부정확할 수 있습니다."
)
