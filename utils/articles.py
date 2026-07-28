from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any


TOPICS = ["전체", "국제", "정치", "경제", "사회", "IT·과학", "문화·생활", "연예", "스포츠"]

TOPIC_KEYWORDS = {
    "국제": ("국제", "세계", "외교", "미국", "중국", "일본", "러시아", "유럽", "해외", "글로벌"),
    "정치": ("정치", "대통령", "국회", "정부", "여당", "야당", "선거", "의원", "장관", "법안"),
    "경제": ("경제", "금리", "환율", "증시", "주식", "부동산", "기업", "산업", "수출", "은행", "반도체"),
    "사회": ("사회", "사건", "사고", "법원", "경찰", "검찰", "교육", "학교", "의료", "노동", "복지"),
    "IT·과학": ("IT", "과학", "기술", "AI", "인공지능", "로봇", "우주", "연구", "스마트폰", "플랫폼"),
    "문화·생활": ("문화", "생활", "건강", "여행", "음식", "패션", "도서", "전시", "날씨"),
    "연예": ("연예", "배우", "가수", "아이돌", "드라마", "영화", "방송", "콘서트", "앨범"),
    "스포츠": ("스포츠", "축구", "야구", "농구", "배구", "골프", "선수", "감독", "경기", "리그"),
}


def safe(value: Any) -> str:
    return escape(str(value or ""))


def study_data(article: dict[str, Any]) -> dict[str, Any]:
    data = article.get("study_data")
    return data if isinstance(data, dict) else {}


def first_value(data: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def title_ko(article: dict[str, Any]) -> str:
    return first_value(study_data(article), "title_ko", default=article.get("publisher_title") or "제목 없음")


def title_zh(article: dict[str, Any]) -> str:
    return first_value(study_data(article), "title_zh", "translated_title")


def title_pinyin(article: dict[str, Any]) -> str:
    return first_value(study_data(article), "title_pinyin", "pinyin_title")


def publisher(article: dict[str, Any]) -> str:
    value = article.get("publisher_name")
    return value.strip() if isinstance(value, str) and value.strip() else "언론사 미상"


def normalize_level(value: Any) -> int:
    if isinstance(value, bool):
        return 3
    if isinstance(value, (int, float)):
        return max(1, min(round(value), 5))
    if isinstance(value, str):
        digits = "".join(ch for ch in value if ch.isdigit())
        if digits:
            return max(1, min(int(digits[0]), 5))
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


def difficulty(article: dict[str, Any]) -> int:
    data = study_data(article)
    for key in ("difficulty", "difficulty_level", "level", "hsk_level"):
        if key in data:
            return normalize_level(data.get(key))
    return 3


def difficulty_label(level: int) -> str:
    return {1: "매우 쉬움", 2: "쉬움", 3: "적당함", 4: "도전", 5: "매우 어려움"}.get(level, "적당함")


def hsk(article: dict[str, Any]) -> str:
    raw = study_data(article).get("hsk_level")
    if isinstance(raw, str) and raw.strip():
        text = raw.strip().upper()
        return text if text.startswith("HSK") else f"HSK{text}"
    if isinstance(raw, (int, float)):
        return f"HSK{max(1, min(round(raw), 6))}"
    return {1: "HSK3", 2: "HSK4", 3: "HSK5", 4: "HSK5", 5: "HSK6"}[difficulty(article)]


def estimated_minutes(article: dict[str, Any]) -> int:
    data = study_data(article)
    for key in ("reading_time", "reading_minutes", "estimated_minutes"):
        value = data.get(key)
        if isinstance(value, (int, float)):
            return max(1, round(value))
        if isinstance(value, str):
            digits = "".join(ch for ch in value if ch.isdigit())
            if digits:
                return max(1, int(digits))
    pairs = data.get("sentence_pairs")
    if isinstance(pairs, list) and pairs:
        return max(3, round(len(pairs) * 1.2))
    return max(3, round(len(article.get("source_text") or "") / 500))


def format_date(value: Any) -> str:
    if not value:
        return ""
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).strftime("%Y.%m.%d")
    except ValueError:
        return text[:10]


def searchable_text(article: dict[str, Any]) -> str:
    data = study_data(article)
    vocab = data.get("vocabulary") or []
    vocab_text = " ".join(
        " ".join(str(item.get(k) or "") for k in ("word", "zh", "meaning_ko", "meaning"))
        for item in vocab if isinstance(item, dict)
    )
    return " ".join([
        title_ko(article), title_zh(article), publisher(article),
        str(article.get("category") or ""), str(article.get("source_text") or ""),
        first_value(data, "summary_ko", "summary_short", "summary_long"), vocab_text,
    ]).lower()


def topic(article: dict[str, Any]) -> str:
    raw = str(article.get("category") or "").strip().replace(" ", "")
    direct = {
        "국제": "국제", "세계": "국제", "정치": "정치", "경제": "경제", "사회": "사회",
        "it": "IT·과학", "it·과학": "IT·과학", "과학": "IT·과학",
        "문화": "문화·생활", "생활": "문화·생활", "문화·생활": "문화·생활",
        "연예": "연예", "스포츠": "스포츠",
    }
    if raw.lower() in direct:
        return direct[raw.lower()]
    text = searchable_text(article)
    scores = {name: sum(1 for word in words if word.lower() in text) for name, words in TOPIC_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "사회"


def recommendation_score(article: dict[str, Any]) -> int:
    data = study_data(article)
    value = data.get("recommendation_score") or data.get("recommend_score")
    if isinstance(value, (int, float)):
        return max(0, min(round(value), 100))
    score = 75 - abs(difficulty(article) - 3) * 12
    score += 8 if data.get("sentence_pairs") else 0
    score += 6 if data.get("vocabulary") else 0
    score += 4 if data.get("grammar") else 0
    score += 4 if data.get("quizzes") else 0
    return max(0, min(score, 100))


def summary(article: dict[str, Any]) -> str:
    return first_value(study_data(article), "summary_short", "summary_one_line", "summary_ko", "summary_long")


def sentence_pairs(article: dict[str, Any]) -> list[dict[str, Any]]:
    data = study_data(article)
    pairs = data.get("sentence_pairs")
    if isinstance(pairs, list) and pairs:
        return [item for item in pairs if isinstance(item, dict)]
    zh = first_value(data, "content_zh", "translated_text", "summary_zh")
    ko = first_value(data, "content_ko", "summary_ko", default=article.get("source_text") or "")
    py = first_value(data, "pinyin", "content_pinyin")
    return [{"zh": zh, "pinyin": py, "ko": ko}] if zh or ko else []


def item_value(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""
