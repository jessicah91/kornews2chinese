from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import streamlit as st
from supabase import Client, create_client


st.set_page_config(
    page_title="오늘의 중국어 뉴스",
    page_icon="📰",
    layout="wide",
)


TOPIC_OPTIONS = [
    "전체",
    "국제",
    "정치",
    "경제",
    "사회",
    "IT·과학",
    "문화·생활",
    "스포츠",
]

TOPIC_KEYWORDS = {
    "국제": (
        "국제", "세계", "외교", "미국", "중국", "일본", "러시아", "유럽",
        "우크라이나", "전쟁", "정상회담", "관세", "해외", "글로벌",
    ),
    "정치": (
        "정치", "대통령", "국회", "정부", "여당", "야당", "선거", "의원",
        "장관", "총리", "정당", "청와대", "외교부", "법안",
    ),
    "경제": (
        "경제", "금리", "환율", "증시", "주식", "부동산", "기업", "산업",
        "수출", "수입", "물가", "은행", "금융", "투자", "반도체",
    ),
    "사회": (
        "사회", "사건", "사고", "법원", "경찰", "검찰", "교육", "학교",
        "의료", "병원", "노동", "취업", "복지", "환경", "재난",
    ),
    "IT·과학": (
        "IT", "과학", "기술", "AI", "인공지능", "로봇", "우주", "연구",
        "스마트폰", "플랫폼", "소프트웨어", "데이터", "인터넷", "게임",
    ),
    "문화·생활": (
        "문화", "생활", "건강", "여행", "음식", "패션", "영화", "드라마",
        "음악", "공연", "도서", "전시", "방송", "연예", "날씨",
    ),
    "스포츠": (
        "스포츠", "축구", "야구", "농구", "배구", "골프", "선수", "감독",
        "경기", "리그", "대표팀", "올림픽", "월드컵",
    ),
}


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 850;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        color: #6b7280;
        margin-bottom: 1.6rem;
    }

    .hero-card {
        padding: 1.6rem 1.7rem;
        border: 1px solid #dbeafe;
        border-radius: 20px;
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 70%);
        margin-bottom: 1.4rem;
    }

    .article-card {
        padding: 1.2rem 1.35rem;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        margin-bottom: 1rem;
        background: white;
    }

    .meta-badge {
        display: inline-block;
        padding: 0.27rem 0.65rem;
        border-radius: 999px;
        background: #f3f4f6;
        margin-right: 0.35rem;
        margin-bottom: 0.4rem;
        font-size: 0.84rem;
    }

    .topic-badge {
        display: inline-block;
        padding: 0.27rem 0.65rem;
        border-radius: 999px;
        background: #dbeafe;
        color: #1d4ed8;
        margin-right: 0.35rem;
        margin-bottom: 0.4rem;
        font-size: 0.84rem;
        font-weight: 700;
    }

    .chinese-sentence {
        font-size: 1.2rem;
        line-height: 1.9;
        font-weight: 650;
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
        font-weight: 750;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .summary-box {
        padding: 1.2rem 1.3rem;
        border-radius: 16px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin: 0.75rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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


def study_data(article: dict[str, Any]) -> dict[str, Any]:
    data = article.get("study_data")
    return data if isinstance(data, dict) else {}


def first_value(
    data: dict[str, Any],
    *keys: str,
    default: str = "",
) -> str:
    for key in keys:
        value = data.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return default


def article_title_ko(article: dict[str, Any]) -> str:
    return first_value(
        study_data(article),
        "title_ko",
        default=article.get("publisher_title") or "제목 없음",
    )


def article_title_zh(article: dict[str, Any]) -> str:
    return first_value(
        study_data(article),
        "title_zh",
        "translated_title",
    )


def article_pinyin(article: dict[str, Any]) -> str:
    return first_value(
        study_data(article),
        "title_pinyin",
        "pinyin_title",
    )


def publisher_of(article: dict[str, Any]) -> str:
    value = article.get("publisher_name")

    if isinstance(value, str) and value.strip():
        return value.strip()

    return "언론사 미상"


def normalize_difficulty(value: Any) -> int:
    if isinstance(value, bool):
        return 3

    if isinstance(value, (int, float)):
        return max(1, min(round(value), 5))

    if isinstance(value, str):
        digits = "".join(char for char in value if char.isdigit())

        if digits:
            number = int(digits[0])
            if number >= 6:
                return 5
            return max(1, min(number, 5))

        lowered = value.lower()

        if "매우 쉬" in value:
            return 1
        if "쉬움" in value or "easy" in lowered:
            return 2
        if "매우 어려" in value or "advanced" in lowered:
            return 5
        if "어려움" in value or "hard" in lowered:
            return 4

    return 3


def difficulty_of(article: dict[str, Any]) -> int:
    data = study_data(article)

    for key in ("difficulty", "difficulty_level", "level", "hsk_level"):
        if key in data:
            return normalize_difficulty(data.get(key))

    return 3


def difficulty_label(level: int) -> str:
    return {
        1: "매우 쉬움",
        2: "쉬움",
        3: "적당함",
        4: "도전",
        5: "매우 어려움",
    }.get(level, "적당함")


def hsk_label(article: dict[str, Any]) -> str:
    data = study_data(article)
    raw = data.get("hsk_level")

    if isinstance(raw, str) and raw.strip():
        text = raw.strip().upper()
        return text if text.startswith("HSK") else f"HSK{text}"

    if isinstance(raw, (int, float)):
        return f"HSK{max(1, min(round(raw), 6))}"

    mapping = {1: "HSK3", 2: "HSK4", 3: "HSK5", 4: "HSK5", 5: "HSK6"}
    return mapping[difficulty_of(article)]


def estimated_minutes(article: dict[str, Any]) -> int:
    data = study_data(article)

    for key in ("reading_time", "reading_minutes", "estimated_minutes"):
        value = data.get(key)

        if isinstance(value, (int, float)):
            return max(1, round(value))

        if isinstance(value, str):
            digits = "".join(char for char in value if char.isdigit())
            if digits:
                return max(1, int(digits))

    sentence_pairs = data.get("sentence_pairs") or []

    if isinstance(sentence_pairs, list) and sentence_pairs:
        return max(3, round(len(sentence_pairs) * 1.2))

    return max(3, round(len(article.get("source_text") or "") / 500))


def format_date(value: Any) -> str:
    if not value:
        return ""

    text = str(value)

    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.strftime("%Y.%m.%d")
    except ValueError:
        return text[:10]


def text_for_topic(article: dict[str, Any]) -> str:
    data = study_data(article)
    vocabulary = data.get("vocabulary") or []

    vocab_text = " ".join(
        str(item.get("meaning_ko") or item.get("meaning") or "")
        for item in vocabulary
        if isinstance(item, dict)
    )

    return " ".join(
        [
            article_title_ko(article),
            article_title_zh(article),
            str(article.get("category") or ""),
            str(article.get("source_text") or "")[:2500],
            first_value(data, "summary_ko", "summary_short", "summary_long"),
            vocab_text,
        ]
    ).lower()


def topic_of(article: dict[str, Any]) -> str:
    raw_category = str(article.get("category") or "").strip()
    normalized = raw_category.replace(" ", "")

    direct_mapping = {
        "국제": "국제",
        "세계": "국제",
        "정치": "정치",
        "경제": "경제",
        "사회": "사회",
        "it": "IT·과학",
        "it·과학": "IT·과학",
        "과학": "IT·과학",
        "문화": "문화·생활",
        "생활": "문화·생활",
        "문화·생활": "문화·생활",
        "스포츠": "스포츠",
    }

    lowered = normalized.lower()

    if lowered in direct_mapping:
        return direct_mapping[lowered]

    text = text_for_topic(article)
    scores: dict[str, int] = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for keyword in keywords if keyword.lower() in text)

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return "사회"

    return best_topic


def recommendation_score(article: dict[str, Any]) -> int:
    data = study_data(article)

    for key in ("recommendation_score", "recommend_score"):
        value = data.get(key)

        if isinstance(value, (int, float)):
            return max(0, min(round(value), 100))

        if isinstance(value, str):
            digits = "".join(char for char in value if char.isdigit())
            if digits:
                return max(0, min(int(digits), 100))

    level = difficulty_of(article)
    score = 75 - abs(level - 3) * 12

    if data.get("sentence_pairs"):
        score += 8
    if data.get("vocabulary"):
        score += 6
    if data.get("grammar"):
        score += 4
    if data.get("quizzes"):
        score += 4
    if first_value(data, "summary_ko", "summary_short"):
        score += 3

    return max(0, min(score, 100))


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

    return [{"zh": chinese, "pinyin": pinyin, "ko": korean}]


def value_from_item(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def safe(value: Any) -> str:
    return escape(str(value or ""))


def summary_values(article: dict[str, Any]) -> tuple[str, str, list[str]]:
    data = study_data(article)

    short_summary = first_value(
        data,
        "summary_short",
        "summary_one_line",
        "summary_ko",
    )

    long_summary = first_value(
        data,
        "summary_long",
        "summary_three_lines",
    )

    reading_points_raw = (
        data.get("reading_points")
        or data.get("reading_point")
        or data.get("study_points")
        or data.get("study_tip")
        or []
    )

    if isinstance(reading_points_raw, str):
        reading_points = [
            line.strip("•- ").strip()
            for line in reading_points_raw.splitlines()
            if line.strip()
        ]
    elif isinstance(reading_points_raw, list):
        reading_points = [
            str(item).strip()
            for item in reading_points_raw
            if str(item).strip()
        ]
    else:
        reading_points = []

    return short_summary, long_summary, reading_points


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


with st.sidebar:
    st.header("학습 설정")

    selected_topic = st.radio(
        "주제",
        options=TOPIC_OPTIONS,
        index=0,
    )

    selected_levels = st.multiselect(
        "난이도",
        options=[1, 2, 3, 4, 5],
        default=[2, 3, 4],
        format_func=lambda value: (
            f"{hsk_label({'study_data': {'difficulty': value}})} "
            f"· {difficulty_label(value)}"
        ),
    )

    search_word = st.text_input(
        "기사 검색",
        placeholder="AI, 중국, 경제 등",
    )

    st.divider()

    show_korean = st.toggle("한국어 해석 보기", value=True)
    show_pinyin = st.toggle("병음 보기", value=True)

    if st.button("새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


filtered_articles: list[dict[str, Any]] = []

for article in articles:
    if selected_topic != "전체" and topic_of(article) != selected_topic:
        continue

    if difficulty_of(article) not in selected_levels:
        continue

    if search_word:
        searchable = " ".join(
            [
                article_title_ko(article),
                article_title_zh(article),
                str(article.get("category") or ""),
                publisher_of(article),
                topic_of(article),
            ]
        ).lower()

        if search_word.lower().strip() not in searchable:
            continue

    filtered_articles.append(article)


if not filtered_articles:
    st.info("선택한 조건에 맞는 기사가 없습니다.")
    st.stop()


recommended = max(filtered_articles, key=recommendation_score)
recommended_data = study_data(recommended)
recommended_short, _, _ = summary_values(recommended)

st.subheader("🔥 오늘의 추천 기사")

st.markdown(
    f"""
    <div class="hero-card">
        <span class="topic-badge">{safe(topic_of(recommended))}</span>
        <span class="meta-badge">{safe(publisher_of(recommended))}</span>
        <span class="meta-badge">{safe(hsk_label(recommended))}</span>
        <span class="meta-badge">추천도 {recommendation_score(recommended)}점</span>
        <span class="meta-badge">예상 {estimated_minutes(recommended)}분</span>
        <span class="meta-badge">
            단어 {len(recommended_data.get("vocabulary") or [])}개
        </span>
        <h2 style="margin-top:0.7rem; margin-bottom:0.45rem;">
            {safe(article_title_ko(recommended))}
        </h2>
        <div class="small-muted">{safe(article_title_zh(recommended))}</div>
        {
            f'<p style="margin-top:0.9rem;">{safe(recommended_short)}</p>'
            if recommended_short
            else ''
        }
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("추천 기사 공부하기", type="primary"):
    st.session_state["selected_article_id"] = recommended.get("id")


st.subheader("📚 기사 선택")

default_index = 0
selected_id = st.session_state.get("selected_article_id")

for index, article in enumerate(filtered_articles):
    if article.get("id") == selected_id:
        default_index = index
        break

selected_article = st.selectbox(
    "공부할 기사를 골라주세요",
    options=filtered_articles,
    index=default_index,
    format_func=lambda article: (
        f"[{topic_of(article)} · {publisher_of(article)}] "
        f"{article_title_ko(article)} "
        f"· {hsk_label(article)}"
    ),
)

st.session_state["selected_article_id"] = selected_article.get("id")

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
                    topic_of(selected_article),
                    publisher_of(selected_article),
                    format_date(selected_article.get("published_at")),
                ],
            )
        )
    )

    st.title(article_title_ko(selected_article))

    title_zh = article_title_zh(selected_article)

    if title_zh:
        st.markdown(
            f'<div class="chinese-sentence">{safe(title_zh)}</div>',
            unsafe_allow_html=True,
        )

    title_pinyin = article_pinyin(selected_article)

    if show_pinyin and title_pinyin:
        st.markdown(
            f'<div class="pinyin-sentence">{safe(title_pinyin)}</div>',
            unsafe_allow_html=True,
        )

with right:
    st.metric("난이도", hsk_label(selected_article))
    st.caption(difficulty_label(level))
    st.metric("추천도", f"{recommendation_score(selected_article)}점")
    st.metric("예상 시간", f"{estimated_minutes(selected_article)}분")

    source_url = selected_article.get("source_url")

    if source_url:
        st.link_button(
            "원문 기사 열기",
            source_url,
            use_container_width=True,
        )


summary_short, summary_long, reading_points = summary_values(selected_article)
summary_zh = first_value(data, "summary_zh")

if summary_short or summary_long or summary_zh or reading_points:
    st.subheader("📌 기사 요약")

    if summary_short:
        with st.container(border=True):
            st.markdown("**한 줄 요약**")
            st.write(summary_short)

    if summary_long:
        with st.container(border=True):
            st.markdown("**3줄 요약**")
            st.write(summary_long)

    if summary_zh:
        with st.container(border=True):
            st.markdown("**중국어 요약**")
            st.markdown(
                f'<div class="chinese-sentence">{safe(summary_zh)}</div>',
                unsafe_allow_html=True,
            )

    if reading_points:
        with st.container(border=True):
            st.markdown("**읽기 포인트**")
            for point in reading_points:
                st.markdown(f"- {point}")


reading_tab, vocab_tab, grammar_tab, quiz_tab = st.tabs(
    [
        "📖 문장별 읽기",
        "🗂 핵심 단어",
        "🧩 문법",
        "✅ 퀴즈",
    ]
)


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
                    <div class="chinese-sentence">{safe(zh)}</div>
                    {
                        f'<div class="pinyin-sentence">{safe(pinyin)}</div>'
                        if show_pinyin and pinyin
                        else ''
                    }
                    {
                        f'<div class="korean-sentence">{safe(ko)}</div>'
                        if show_korean and ko
                        else ''
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )


with vocab_tab:
    vocabulary = data.get("vocabulary") or []

    if not vocabulary:
        st.info("추출된 핵심 단어가 없습니다.")
    else:
        cols = st.columns(2)

        for index, item in enumerate(vocabulary):
            if not isinstance(item, dict):
                continue

            word = value_from_item(item, "word", "zh", "chinese")
            pinyin = value_from_item(item, "pinyin")
            meaning = value_from_item(
                item,
                "meaning_ko",
                "meaning",
                "ko",
            )
            example = value_from_item(item, "example", "sentence")

            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="vocab-word">{safe(word)}</div>',
                        unsafe_allow_html=True,
                    )

                    if pinyin:
                        st.caption(pinyin)

                    if meaning:
                        st.write(meaning)

                    if example:
                        st.markdown(f"예문: {example}")

                    st.button(
                        "☆ 단어 저장",
                        key=(
                            f"save_word_{selected_article.get('id')}_"
                            f"{index}_{word}"
                        ),
                        disabled=True,
                        help=(
                            "다음 단계에서 saved_words 테이블과 "
                            "연결하면 실제 저장됩니다."
                        ),
                        use_container_width=True,
                    )


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
            example = value_from_item(item, "example", "sentence")

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
                            st.error(
                                f"아쉬워요. 정답은 `{correct_text}`입니다."
                            )

                        if explanation:
                            st.info(explanation)
                else:
                    st.write("정답:", answer or "정답 정보 없음")


st.divider()
st.caption(
    "기사와 번역은 자동 수집된 자료입니다. "
    "번역 및 병음은 문맥에 따라 일부 부정확할 수 있습니다."
)
