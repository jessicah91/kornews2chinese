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
    initial_sidebar_state="expanded",
)


TOPIC_OPTIONS = [
    "전체",
    "국제",
    "정치",
    "경제",
    "사회",
    "IT·과학",
    "문화·생활",
    "연예",
    "스포츠",
]

TOPIC_ICONS = {
    "전체": "✦",
    "국제": "🌏",
    "정치": "🏛️",
    "경제": "📈",
    "사회": "👥",
    "IT·과학": "💻",
    "문화·생활": "🎨",
    "연예": "🎬",
    "스포츠": "⚽",
}

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
        "문화", "생활", "건강", "여행", "음식", "패션", "공연", "도서",
        "전시", "축제", "날씨",
    ),
    "연예": (
        "연예", "영화", "드라마", "배우", "가수", "아이돌", "예능",
        "방송", "음악", "콘서트", "앨범", "넷플릭스",
    ),
    "스포츠": (
        "스포츠", "축구", "야구", "농구", "배구", "골프", "선수", "감독",
        "경기", "리그", "대표팀", "올림픽", "월드컵", "KBO",
    ),
}


st.markdown(
    """
    <style>
    :root {
        --surface: #ffffff;
        --surface-soft: #f6f8fb;
        --surface-blue: #eef4ff;
        --text: #162033;
        --muted: #6f7b8f;
        --line: #e5eaf2;
        --primary: #3157d5;
        --primary-deep: #203ba5;
        --primary-soft: #e8eeff;
        --accent: #f36b4a;
        --success: #16856b;
        --shadow: 0 12px 32px rgba(40, 57, 100, 0.08);
    }

    html, body, [class*="css"] {
        font-family:
            Pretendard, "Apple SD Gothic Neo", "Noto Sans KR",
            "Noto Sans CJK KR", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(66, 105, 225, 0.08),
                transparent 25rem
            ),
            #f7f9fc;
        color: var(--text);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.96);
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 5px 18px rgba(40, 57, 100, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--text);
    }

    div[data-testid="stTabs"] button {
        border-radius: 999px;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: var(--primary-soft);
        color: var(--primary-deep);
    }

    div[data-testid="stExpander"],
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }

    .brand-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.35rem 0 1.25rem;
    }

    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .brand-mark {
        width: 46px;
        height: 46px;
        border-radius: 15px;
        display: grid;
        place-items: center;
        color: white;
        font-size: 1.35rem;
        background:
            linear-gradient(145deg, var(--primary), var(--primary-deep));
        box-shadow: 0 9px 22px rgba(49, 87, 213, 0.25);
    }

    .brand-title {
        font-size: 1.22rem;
        font-weight: 850;
        letter-spacing: -0.03em;
    }

    .brand-caption {
        color: var(--muted);
        font-size: 0.83rem;
        margin-top: 0.1rem;
    }

    .top-nav {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        flex-wrap: wrap;
    }

    .nav-item {
        display: inline-flex;
        align-items: center;
        padding: 0.52rem 0.82rem;
        border-radius: 999px;
        color: #536078;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid var(--line);
        font-size: 0.88rem;
        font-weight: 650;
    }

    .nav-item.active {
        color: white;
        border-color: transparent;
        background: var(--primary);
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        border-radius: 28px;
        padding: 2.2rem 2.25rem;
        background:
            linear-gradient(
                135deg,
                #213da8 0%,
                #3157d5 52%,
                #5578e8 100%
            );
        color: white;
        box-shadow: 0 18px 44px rgba(35, 61, 160, 0.22);
        margin-bottom: 1.35rem;
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        width: 320px;
        height: 320px;
        right: -105px;
        top: -145px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.11);
    }

    .hero-eyebrow {
        display: inline-flex;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 0.82rem;
        font-weight: 750;
        margin-bottom: 0.85rem;
    }

    .hero-heading {
        max-width: 720px;
        font-size: clamp(2rem, 4vw, 3.35rem);
        line-height: 1.12;
        font-weight: 900;
        letter-spacing: -0.055em;
        margin-bottom: 0.8rem;
    }

    .hero-copy {
        max-width: 650px;
        font-size: 1rem;
        line-height: 1.72;
        color: rgba(255, 255, 255, 0.83);
    }

    .section-heading {
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 1rem;
        margin: 2rem 0 0.9rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 850;
        letter-spacing: -0.035em;
    }

    .section-desc {
        color: var(--muted);
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }

    .recommend-card {
        min-height: 100%;
        padding: 1.65rem 1.7rem;
        border: 1px solid #dce5ff;
        border-radius: 24px;
        background:
            linear-gradient(140deg, #f2f6ff 0%, #ffffff 68%);
        box-shadow: var(--shadow);
    }

    .dashboard-card {
        min-height: 100%;
        padding: 1.45rem;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--surface);
        box-shadow: var(--shadow);
    }

    .dashboard-label {
        color: var(--muted);
        font-size: 0.84rem;
        margin-bottom: 0.3rem;
    }

    .dashboard-value {
        font-size: 1.65rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin-bottom: 0.32rem;
    }

    .dashboard-copy {
        color: var(--muted);
        font-size: 0.85rem;
        line-height: 1.55;
    }

    .topic-row {
        display: flex;
        gap: 0.55rem;
        overflow-x: auto;
        padding: 0.15rem 0 0.65rem;
        scrollbar-width: none;
    }

    .topic-row::-webkit-scrollbar {
        display: none;
    }

    .topic-chip {
        flex: 0 0 auto;
        display: inline-flex;
        gap: 0.35rem;
        align-items: center;
        padding: 0.58rem 0.82rem;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: white;
        color: #4b5870;
        font-size: 0.87rem;
        font-weight: 700;
    }

    .article-list-card {
        padding: 1.25rem 1.3rem;
        border: 1px solid var(--line);
        border-radius: 20px;
        margin-bottom: 0.85rem;
        background: rgba(255, 255, 255, 0.94);
        box-shadow: 0 5px 18px rgba(40, 57, 100, 0.04);
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }

    .article-list-card:hover {
        transform: translateY(-2px);
        border-color: #cfd9f5;
        box-shadow: 0 12px 28px rgba(40, 57, 100, 0.09);
    }

    .article-title {
        font-size: 1.08rem;
        line-height: 1.48;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: var(--text);
        margin: 0.45rem 0 0.35rem;
    }

    .article-chinese-preview {
        color: #435477;
        line-height: 1.65;
        font-size: 0.92rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.26rem 0.58rem;
        border-radius: 999px;
        background: #f1f4f8;
        color: #59677d;
        margin-right: 0.28rem;
        margin-bottom: 0.25rem;
        font-size: 0.76rem;
        font-weight: 700;
    }

    .badge-topic {
        background: var(--primary-soft);
        color: var(--primary-deep);
    }

    .badge-accent {
        background: #fff0eb;
        color: #bd4d32;
    }

    .reading-header {
        padding: 1.8rem 1.9rem;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: white;
        box-shadow: var(--shadow);
        margin-top: 1rem;
    }

    .chinese-sentence {
        font-size: 1.18rem;
        line-height: 1.9;
        font-weight: 680;
        margin-top: 0.25rem;
    }

    .pinyin-sentence {
        color: var(--primary);
        line-height: 1.75;
        margin-top: 0.15rem;
    }

    .korean-sentence {
        color: #566176;
        line-height: 1.75;
        margin-top: 0.22rem;
    }

    .sentence-box {
        padding: 1.1rem 1.15rem;
        border: 1px solid #edf0f5;
        border-radius: 17px;
        background: #fafbfe;
        margin-bottom: 0.82rem;
    }

    .summary-box {
        padding: 1.15rem 1.2rem;
        border: 1px solid var(--line);
        border-radius: 17px;
        background: white;
        margin-bottom: 0.7rem;
    }

    .vocab-word {
        font-size: 1.18rem;
        font-weight: 850;
        letter-spacing: -0.02em;
    }

    .small-muted {
        color: var(--muted);
        font-size: 0.87rem;
    }

    .footer-note {
        margin-top: 2.8rem;
        padding-top: 1.2rem;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.65;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.85rem;
        }

        .brand-bar {
            align-items: flex-start;
            flex-direction: column;
        }

        .top-nav {
            width: 100%;
            overflow-x: auto;
            flex-wrap: nowrap;
            padding-bottom: 0.25rem;
        }

        .nav-item {
            flex: 0 0 auto;
        }

        .hero-shell {
            border-radius: 22px;
            padding: 1.7rem 1.35rem;
        }

        .hero-heading {
            font-size: 2rem;
        }

        .reading-header {
            padding: 1.35rem 1.15rem;
        }

        .section-heading {
            align-items: flex-start;
            flex-direction: column;
            gap: 0.25rem;
        }
    }

    @media (max-width: 640px) {
        .brand-caption {
            display: none;
        }

        .brand-mark {
            width: 41px;
            height: 41px;
        }

        .hero-shell {
            padding: 1.5rem 1.1rem;
        }

        .hero-heading {
            font-size: 1.72rem;
        }

        .hero-copy {
            font-size: 0.92rem;
        }

        .article-list-card,
        .recommend-card,
        .dashboard-card {
            border-radius: 18px;
        }

        .chinese-sentence {
            font-size: 1.08rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.7rem;
        }
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

    mapping = {
        1: "HSK3",
        2: "HSK4",
        3: "HSK5",
        4: "HSK5",
        5: "HSK6",
    }
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
            first_value(
                data,
                "summary_ko",
                "summary_short",
                "summary_long",
            ),
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
        "연예": "연예",
        "스포츠": "스포츠",
    }

    lowered = normalized.lower()

    if lowered in direct_mapping:
        return direct_mapping[lowered]

    text = text_for_topic(article)
    scores: dict[str, int] = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        scores[topic] = sum(
            1
            for keyword in keywords
            if keyword.lower() in text
        )

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
        return [
            item
            for item in pairs
            if isinstance(item, dict)
        ]

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


def safe(value: Any) -> str:
    return escape(str(value or ""))


def summary_values(
    article: dict[str, Any],
) -> tuple[str, str, list[str]]:
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


def searchable_text(article: dict[str, Any]) -> str:
    data = study_data(article)
    vocabulary = data.get("vocabulary") or []

    vocab_text = " ".join(
        " ".join(
            [
                value_from_item(item, "word", "zh", "chinese"),
                value_from_item(item, "pinyin"),
                value_from_item(
                    item,
                    "meaning_ko",
                    "meaning",
                    "ko",
                ),
            ]
        )
        for item in vocabulary
        if isinstance(item, dict)
    )

    return " ".join(
        [
            article_title_ko(article),
            article_title_zh(article),
            article_pinyin(article),
            publisher_of(article),
            topic_of(article),
            str(article.get("source_text") or ""),
            first_value(
                data,
                "summary_ko",
                "summary_short",
                "summary_long",
                "summary_zh",
            ),
            vocab_text,
        ]
    ).lower()


def render_brand_bar() -> None:
    st.markdown(
        """
        <div class="brand-bar">
            <div class="brand-wrap">
                <div class="brand-mark">中</div>
                <div>
                    <div class="brand-title">오늘의 중국어 뉴스</div>
                    <div class="brand-caption">
                        K-News로 매일 쌓는 실전 중국어
                    </div>
                </div>
            </div>
            <div class="top-nav">
                <span class="nav-item active">홈</span>
                <span class="nav-item">기사 찾기</span>
                <span class="nav-item">단어장</span>
                <span class="nav-item">즐겨찾기</span>
                <span class="nav-item">마이페이지</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-eyebrow">매일 업데이트되는 실전 중국어</div>
            <div class="hero-heading">
                오늘의 한국 뉴스를<br>
                중국어 학습 콘텐츠로 만나보세요
            </div>
            <div class="hero-copy">
                기사 번역부터 병음, 핵심 단어, 문법, 퀴즈까지
                한 화면에서 이어서 공부할 수 있어요.
                노트북과 모바일 어디서든 편하게 학습해보세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topic_row(articles: list[dict[str, Any]]) -> None:
    topic_counts = {
        topic: sum(
            1
            for article in articles
            if topic_of(article) == topic
        )
        for topic in TOPIC_OPTIONS
        if topic != "전체"
    }

    chips = "".join(
        (
            '<span class="topic-chip">'
            f'{TOPIC_ICONS.get(topic, "•")} '
            f'{safe(topic)} {count}'
            "</span>"
        )
        for topic, count in topic_counts.items()
    )

    st.markdown(
        f'<div class="topic-row">{chips}</div>',
        unsafe_allow_html=True,
    )


articles = load_articles()

render_brand_bar()
render_hero()

if not articles:
    st.warning("아직 저장된 기사가 없습니다.")
    st.stop()


with st.sidebar:
    st.markdown("### 기사 찾기")

    search_word = st.text_input(
        "검색",
        placeholder="AI, 축구, 영화, 중국 등",
    )

    selected_topic = st.radio(
        "카테고리",
        options=TOPIC_OPTIONS,
        index=0,
    )

    selected_levels = st.multiselect(
        "난이도",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda value: (
            f"{hsk_label({'study_data': {'difficulty': value}})} "
            f"· {difficulty_label(value)}"
        ),
    )

    sort_option = st.selectbox(
        "정렬",
        options=["추천순", "최신순", "쉬운 순"],
    )

    st.divider()

    st.markdown("### 읽기 설정")
    show_korean = st.toggle(
        "한국어 해석 보기",
        value=True,
    )
    show_pinyin = st.toggle(
        "병음 보기",
        value=True,
    )

    st.divider()

    if st.button(
        "기사 목록 새로고침",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "단어장·즐겨찾기·마이페이지는 "
        "다음 단계에서 실제 저장 기능과 연결됩니다."
    )


filtered_articles: list[dict[str, Any]] = []

for article in articles:
    if (
        selected_topic != "전체"
        and topic_of(article) != selected_topic
    ):
        continue

    if difficulty_of(article) not in selected_levels:
        continue

    if search_word:
        needle = search_word.lower().strip()

        if needle not in searchable_text(article):
            continue

    filtered_articles.append(article)


if sort_option == "추천순":
    filtered_articles.sort(
        key=recommendation_score,
        reverse=True,
    )
elif sort_option == "쉬운 순":
    filtered_articles.sort(
        key=lambda article: (
            difficulty_of(article),
            -recommendation_score(article),
        )
    )


if not filtered_articles:
    st.info("선택한 조건에 맞는 기사가 없습니다.")
    st.stop()


recommended = max(
    filtered_articles,
    key=recommendation_score,
)
recommended_data = study_data(recommended)
recommended_short, _, _ = summary_values(recommended)

st.markdown(
    """
    <div class="section-heading">
        <div>
            <div class="section-title">오늘의 추천과 학습 현황</div>
            <div class="section-desc">
                지금 읽기 좋은 기사와 오늘의 학습 정보를 확인해보세요.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

recommend_col, stat_col = st.columns([2.15, 1])

with recommend_col:
    st.markdown(
        f"""
        <div class="recommend-card">
            <span class="badge badge-topic">
                {safe(TOPIC_ICONS.get(topic_of(recommended), "✦"))}
                {safe(topic_of(recommended))}
            </span>
            <span class="badge">{safe(publisher_of(recommended))}</span>
            <span class="badge">{safe(hsk_label(recommended))}</span>
            <span class="badge badge-accent">
                추천도 {recommendation_score(recommended)}점
            </span>
            <div class="article-title" style="font-size:1.48rem;">
                {safe(article_title_ko(recommended))}
            </div>
            <div class="article-chinese-preview">
                {safe(article_title_zh(recommended))}
            </div>
            {
                (
                    '<p style="margin-top:0.9rem;line-height:1.7;">'
                    f'{safe(recommended_short)}'
                    '</p>'
                )
                if recommended_short
                else ''
            }
            <div class="small-muted" style="margin-top:0.85rem;">
                예상 {estimated_minutes(recommended)}분 ·
                단어 {len(recommended_data.get("vocabulary") or [])}개 ·
                {format_date(recommended.get("published_at"))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "추천 기사 바로 공부하기",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["selected_article_id"] = recommended.get("id")
        st.rerun()

with stat_col:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-label">현재 확인 가능한 기사</div>
            <div class="dashboard-value">{len(filtered_articles)}개</div>
            <div class="dashboard-copy">
                선택한 카테고리와 난이도 조건에 맞는 기사예요.
            </div>
            <hr style="border:none;border-top:1px solid #e8edf5;margin:1rem 0;">
            <div class="dashboard-label">오늘 추천 난이도</div>
            <div class="dashboard-value">{safe(hsk_label(recommended))}</div>
            <div class="dashboard-copy">
                약 {estimated_minutes(recommended)}분이면 학습할 수 있어요.
            </div>
            <hr style="border:none;border-top:1px solid #e8edf5;margin:1rem 0;">
            <div class="dashboard-label">학습 기능</div>
            <div class="dashboard-copy">
                문장별 읽기 · 핵심 단어 · 문법 · 퀴즈
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="section-heading">
        <div>
            <div class="section-title">카테고리 둘러보기</div>
            <div class="section-desc">
                관심 있는 주제의 최신 기사를 골라보세요.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_topic_row(articles)


st.markdown(
    """
    <div class="section-heading">
        <div>
            <div class="section-title">최신 학습 기사</div>
            <div class="section-desc">
                아래 기사 중 하나를 선택하면 학습 화면으로 이어집니다.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


default_index = 0
selected_id = st.session_state.get("selected_article_id")

for index, article in enumerate(filtered_articles):
    if article.get("id") == selected_id:
        default_index = index
        break


preview_count = min(len(filtered_articles), 8)

for index, article in enumerate(filtered_articles[:preview_count]):
    summary_short, _, _ = summary_values(article)

    card_col, button_col = st.columns([5.5, 1])

    with card_col:
        st.markdown(
            f"""
            <div class="article-list-card">
                <span class="badge badge-topic">
                    {safe(TOPIC_ICONS.get(topic_of(article), "✦"))}
                    {safe(topic_of(article))}
                </span>
                <span class="badge">{safe(hsk_label(article))}</span>
                <span class="badge">
                    {estimated_minutes(article)}분
                </span>
                <div class="article-title">
                    {safe(article_title_ko(article))}
                </div>
                <div class="article-chinese-preview">
                    {safe(article_title_zh(article))}
                </div>
                {
                    (
                        '<div class="small-muted" '
                        'style="margin-top:0.65rem;line-height:1.55;">'
                        f'{safe(summary_short[:135])}'
                        '</div>'
                    )
                    if summary_short
                    else ''
                }
                <div class="small-muted" style="margin-top:0.75rem;">
                    {safe(publisher_of(article))} ·
                    {format_date(article.get("published_at"))} ·
                    추천도 {recommendation_score(article)}점
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with button_col:
        st.write("")
        st.write("")

        if st.button(
            "공부하기",
            key=f"open_article_{article.get('id')}_{index}",
            use_container_width=True,
        ):
            st.session_state["selected_article_id"] = article.get("id")
            st.rerun()


selected_article = st.selectbox(
    "선택한 기사",
    options=filtered_articles,
    index=default_index,
    format_func=lambda article: (
        f"[{topic_of(article)} · {publisher_of(article)}] "
        f"{article_title_ko(article)} · {hsk_label(article)}"
    ),
    label_visibility="collapsed",
)

st.session_state["selected_article_id"] = selected_article.get("id")

data = study_data(selected_article)
level = difficulty_of(selected_article)

st.markdown(
    """
    <div class="section-heading">
        <div>
            <div class="section-title">기사로 공부하기</div>
            <div class="section-desc">
                중국어 기사와 학습 자료를 차례대로 살펴보세요.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="reading-header">', unsafe_allow_html=True)

left, right = st.columns([4, 1.15])

with left:
    st.caption(
        " · ".join(
            filter(
                None,
                [
                    topic_of(selected_article),
                    publisher_of(selected_article),
                    format_date(
                        selected_article.get("published_at")
                    ),
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
    st.metric(
        "추천도",
        f"{recommendation_score(selected_article)}점",
    )
    st.metric(
        "예상 시간",
        f"{estimated_minutes(selected_article)}분",
    )

    source_url = selected_article.get("source_url")

    if source_url:
        st.link_button(
            "원문 기사 열기",
            source_url,
            use_container_width=True,
        )

st.markdown("</div>", unsafe_allow_html=True)


summary_short, summary_long, reading_points = summary_values(
    selected_article
)
summary_zh = first_value(data, "summary_zh")

if summary_short or summary_long or summary_zh or reading_points:
    st.markdown(
        """
        <div class="section-heading">
            <div>
                <div class="section-title">기사 핵심 정리</div>
                <div class="section-desc">
                    본문을 읽기 전에 핵심 내용을 먼저 확인해보세요.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_columns = st.columns(2)

    with summary_columns[0]:
        if summary_short:
            st.markdown(
                f"""
                <div class="summary-box">
                    <div class="small-muted">한 줄 요약</div>
                    <div style="margin-top:0.45rem;line-height:1.7;">
                        {safe(summary_short)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if summary_long:
            st.markdown(
                f"""
                <div class="summary-box">
                    <div class="small-muted">상세 요약</div>
                    <div style="margin-top:0.45rem;line-height:1.7;">
                        {safe(summary_long)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with summary_columns[1]:
        if summary_zh:
            st.markdown(
                f"""
                <div class="summary-box">
                    <div class="small-muted">중국어 요약</div>
                    <div class="chinese-sentence">
                        {safe(summary_zh)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if reading_points:
            points_html = "".join(
                f"<li>{safe(point)}</li>"
                for point in reading_points
            )

            st.markdown(
                f"""
                <div class="summary-box">
                    <div class="small-muted">읽기 포인트</div>
                    <ul style="margin:0.55rem 0 0;padding-left:1.2rem;
                               line-height:1.75;">
                        {points_html}
                    </ul>
                </div>
                """,
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
        st.info(
            "이 기사에서 별도로 추출된 문법 표현이 없습니다."
        )
    else:
        for index, item in enumerate(
            grammar_items,
            start=1,
        ):
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
                    st.markdown(
                        f"**기사 속 예문**  \n{example}"
                    )


with quiz_tab:
    quizzes = data.get("quizzes") or []

    if not quizzes:
        st.info("생성된 퀴즈가 없습니다.")
    else:
        for index, quiz in enumerate(
            quizzes,
            start=1,
        ):
            if not isinstance(quiz, dict):
                continue

            question = value_from_item(
                quiz,
                "question",
                "question_ko",
            )
            options = (
                quiz.get("options")
                or quiz.get("choices")
                or []
            )
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
                        key=(
                            f"quiz_"
                            f"{selected_article.get('id')}_"
                            f"{index}"
                        ),
                        index=None,
                    )

                    if st.button(
                        f"{index}번 정답 확인",
                        key=(
                            f"check_"
                            f"{selected_article.get('id')}_"
                            f"{index}"
                        ),
                    ):
                        correct_text = ""

                        if isinstance(answer, int):
                            if 0 <= answer < len(options):
                                correct_text = str(
                                    options[answer]
                                )
                            elif 1 <= answer <= len(options):
                                correct_text = str(
                                    options[answer - 1]
                                )
                        else:
                            correct_text = str(answer or "")

                        if selected_answer is None:
                            st.warning(
                                "답을 먼저 선택해주세요."
                            )
                        elif (
                            str(selected_answer)
                            == correct_text
                        ):
                            st.success("정답이에요! 🎉")
                        else:
                            st.error(
                                "아쉬워요. 정답은 "
                                f"`{correct_text}`입니다."
                            )

                        if explanation:
                            st.info(explanation)
                else:
                    st.write(
                        "정답:",
                        answer or "정답 정보 없음",
                    )


st.markdown(
    """
    <div class="footer-note">
        기사와 번역은 자동 수집된 자료입니다.
        번역 및 병음은 문맥에 따라 일부 부정확할 수 있습니다.
        저장 기능과 개인 학습 통계는 다음 단계에서 연결됩니다.
    </div>
    """,
    unsafe_allow_html=True,
)
