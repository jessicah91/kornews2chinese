from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import requests
import trafilatura


LOGGER = logging.getLogger(__name__)

NAVER_NEWS_URL = (
    "https://openapi.naver.com/v1/search/news.json"
)


ALLOWED_PUBLISHERS = {
    "news.sbs.co.kr": "SBS",
    "imnews.imbc.com": "MBC",
    "news.kbs.co.kr": "KBS",
    "kbs.co.kr": "KBS",
    "chosun.com": "조선일보",
    "www.chosun.com": "조선일보",
    "joongang.co.kr": "중앙일보",
    "www.joongang.co.kr": "중앙일보",
    "donga.com": "동아일보",
    "www.donga.com": "동아일보",
    "mk.co.kr": "매일경제",
    "www.mk.co.kr": "매일경제",
}


QUERY_TOPIC_MAP = {
    "국제": "국제",
    "세계": "국제",
    "해외": "국제",
    "정치": "정치",
    "정부": "정치",
    "국회": "정치",
    "경제": "경제",
    "금융": "경제",
    "기업": "경제",
    "사회": "사회",
    "교육": "사회",
    "사건": "사회",
    "IT": "IT·과학",
    "과학": "IT·과학",
    "기술": "IT·과학",
    "인공지능": "IT·과학",
    "문화": "문화·생활",
    "생활": "문화·생활",
    "여행": "문화·생활",
    "건강": "문화·생활",
    "연예": "연예",
    "드라마": "연예",
    "영화": "연예",
    "음악": "연예",
    "스포츠": "스포츠",
    "축구": "스포츠",
    "야구": "스포츠",
}


BLOCKED_TITLE_WORDS = (
    "[인사]",
    "[부고]",
    "[알림]",
    "[포토]",
    "[사진]",
    "[영상]",
    "[속보]",
    "[사설]",
    "[칼럼]",
    "[기고]",
    "[전문]",
    "[전문가 칼럼]",
    "오늘의 운세",
    "별자리 운세",
    "띠별 운세",
    "주요 인사",
    "인사 이동",
    "인사발령",
    "채용 공고",
    "모집 공고",
    "입찰 공고",
    "당첨 번호",
    "로또 번호",
    "날씨 예보",
    "주간 운세",
    "포토뉴스",
    "영상뉴스",
    "기자수첩",
    "취재파일",
    "오피니언",
)


VERY_DIFFICULT_TERMS = (
    "파생상품",
    "신용부도스와프",
    "총부채원리금상환비율",
    "양적긴축",
    "통화승수",
    "재정승수",
    "수익률곡선",
    "금리스와프",
    "채권 듀레이션",
    "상고심",
    "헌법소원",
    "행정소송",
    "위헌법률심판",
    "손해배상청구",
    "법률적 쟁점",
    "양자역학",
    "분자생물학",
    "유전체 분석",
    "임상 3상",
    "반도체 미세공정",
    "고대역폭메모리 공정",
    "열역학",
    "핵융합 반응",
)


IMPORTANT_NEWS_TERMS = (
    "정부",
    "대통령",
    "국회",
    "경제",
    "물가",
    "금리",
    "환율",
    "고용",
    "부동산",
    "반도체",
    "인공지능",
    "AI",
    "수출",
    "무역",
    "미국",
    "중국",
    "일본",
    "유럽",
    "외교",
    "안보",
    "교육",
    "의료",
    "환경",
    "기후",
    "삼성",
    "SK",
    "현대",
    "LG",
    "영화",
    "드라마",
    "배우",
    "가수",
    "콘서트",
    "예능",
    "넷플릭스",
    "디즈니",
    "음악",
    "공연",
    "축구",
    "야구",
    "농구",
    "배구",
    "골프",
    "대표팀",
    "리그",
    "월드컵",
    "올림픽",
    "KBO",
    "메이저리그",
    "여행",
    "음식",
    "건강",
    "운동",
    "전시",
    "축제",
)


EASY_TOPIC_BONUS = {
    "국제": 1,
    "정치": 0,
    "경제": 0,
    "사회": 1,
    "IT·과학": 1,
    "문화·생활": 4,
    "연예": 5,
    "스포츠": 5,
}


TRAILING_PATTERNS = (
    r"무단\s*전재.*$",
    r"무단전재.*$",
    r"재배포\s*금지.*$",
    r"저작권자.*$",
    r"Copyright.*$",
    r"기사\s*제보.*$",
    r"제보는.*$",
    r"독자\s*제보.*$",
    r"SNS\s*기사보내기.*$",
    r"기사보내기.*$",
    r"관련기사.*$",
    r"추천기사.*$",
    r"기자의\s*다른\s*기사.*$",
    r"댓글\s*\d+.*$",
)


@dataclass(frozen=True)
class NewsCandidate:
    query: str
    title: str
    description: str
    link: str
    original_link: str
    published_at: str

    @property
    def topic(self) -> str:
        return topic_from_query(self.query)


def _clean(value: str | None) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def topic_from_query(query: str) -> str:
    normalized = re.sub(
        r"\s+",
        " ",
        query or "",
    ).strip()

    for keyword, topic in QUERY_TOPIC_MAP.items():
        if keyword.lower() in normalized.lower():
            return topic

    return "사회"


def search_naver_news(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 100,
) -> list[NewsCandidate]:
    response = requests.get(
        NAVER_NEWS_URL,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        },
        params={
            "query": query,
            "display": min(max(display, 1), 100),
            "sort": "date",
        },
        timeout=20,
    )
    response.raise_for_status()

    items = response.json().get("items", [])

    return [
        NewsCandidate(
            query=query,
            title=_clean(item.get("title")),
            description=_clean(
                item.get("description")
            ),
            link=item.get("link", "") or "",
            original_link=(
                item.get("originallink", "")
                or item.get("link", "")
                or ""
            ),
            published_at=item.get(
                "pubDate",
                "",
            ) or "",
        )
        for item in items
    ]


def _hostname(url: str) -> str:
    try:
        return (
            urlparse(url)
            .netloc
            .lower()
            .split(":")[0]
        )
    except Exception:
        return ""


def publisher_name(url: str) -> str | None:
    hostname = _hostname(url)

    for domain, name in ALLOWED_PUBLISHERS.items():
        if (
            hostname == domain
            or hostname.endswith("." + domain)
        ):
            return name

    return None


def _is_allowed_publisher(url: str) -> bool:
    return publisher_name(url) is not None


def _is_blocked_title(title: str) -> bool:
    normalized = re.sub(
        r"\s+",
        " ",
        title,
    ).strip().lower()

    return any(
        blocked.lower() in normalized
        for blocked in BLOCKED_TITLE_WORDS
    )


def _difficulty_penalty(
    title: str,
    description: str,
) -> int:
    combined = f"{title} {description}"
    hits = sum(
        1
        for term in VERY_DIFFICULT_TERMS
        if term in combined
    )

    penalty = hits * 4

    if len(title) > 75:
        penalty += 2

    uppercase_tokens = re.findall(
        r"\b[A-Z]{3,}\b",
        title,
    )

    if len(uppercase_tokens) >= 3:
        penalty += 2

    special_count = len(
        re.findall(
            r"[%·:/()〈〉《》\[\]]",
            title,
        )
    )

    if special_count >= 6:
        penalty += 2

    return penalty


def _topic_relevance_score(
    candidate: NewsCandidate,
) -> int:
    combined = (
        f"{candidate.title} "
        f"{candidate.description}"
    ).lower()

    topic_keywords = {
        "국제": (
            "미국",
            "중국",
            "일본",
            "유럽",
            "해외",
            "외교",
            "정상회담",
            "관세",
        ),
        "정치": (
            "대통령",
            "국회",
            "정부",
            "여당",
            "야당",
            "선거",
            "의원",
            "장관",
        ),
        "경제": (
            "경제",
            "금리",
            "환율",
            "증시",
            "기업",
            "부동산",
            "수출",
            "금융",
        ),
        "사회": (
            "사회",
            "교육",
            "학교",
            "경찰",
            "법원",
            "병원",
            "노동",
            "환경",
        ),
        "IT·과학": (
            "ai",
            "인공지능",
            "it",
            "과학",
            "기술",
            "로봇",
            "우주",
            "연구",
        ),
        "문화·생활": (
            "문화",
            "생활",
            "여행",
            "건강",
            "음식",
            "전시",
            "축제",
            "공연",
        ),
        "연예": (
            "연예",
            "배우",
            "가수",
            "드라마",
            "영화",
            "예능",
            "콘서트",
            "앨범",
        ),
        "스포츠": (
            "스포츠",
            "축구",
            "야구",
            "농구",
            "배구",
            "선수",
            "경기",
            "대표팀",
        ),
    }

    return sum(
        2
        for keyword in topic_keywords.get(
            candidate.topic,
            (),
        )
        if keyword.lower() in combined
    )


def _importance_score(
    candidate: NewsCandidate,
) -> int:
    combined = (
        f"{candidate.title} "
        f"{candidate.description}"
    )

    score = 10

    for term in IMPORTANT_NEWS_TERMS:
        if term.lower() in combined.lower():
            score += 2

    score += EASY_TOPIC_BONUS.get(
        candidate.topic,
        0,
    )

    score += _topic_relevance_score(candidate)

    score -= _difficulty_penalty(
        candidate.title,
        candidate.description,
    )

    if len(candidate.description) < 35:
        score -= 2

    if len(candidate.title) < 12:
        score -= 3

    if len(candidate.title) > 90:
        score -= 2

    return score


def choose_candidate(
    candidates: list[NewsCandidate],
    seen_urls: set[str],
) -> NewsCandidate | None:
    valid_candidates: list[NewsCandidate] = []

    for candidate in candidates:
        canonical_url = (
            candidate.original_link
            or candidate.link
        )

        if not canonical_url:
            continue

        if canonical_url in seen_urls:
            continue

        if not _is_allowed_publisher(
            canonical_url
        ):
            continue

        if _is_blocked_title(
            candidate.title
        ):
            LOGGER.info(
                "Skipping blocked article title: %s",
                candidate.title,
            )
            continue

        score = _importance_score(candidate)

        if score < 5:
            LOGGER.info(
                "Skipping low-value/difficult article "
                "(%s): %s",
                score,
                candidate.title,
            )
            continue

        valid_candidates.append(candidate)

    if not valid_candidates:
        return None

    valid_candidates.sort(
        key=_importance_score,
        reverse=True,
    )

    selected = valid_candidates[0]
    selected_url = (
        selected.original_link
        or selected.link
    )

    LOGGER.info(
        "Selected article "
        "[topic=%s, publisher=%s, score=%s]: %s",
        selected.topic,
        publisher_name(selected_url),
        _importance_score(selected),
        selected.title,
    )

    return selected


def _remove_trailing_noise(
    text: str,
) -> str:
    cleaned = text

    cleaned = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "",
        cleaned,
    )

    for pattern in TRAILING_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )

    cleaned = re.sub(
        r"ⓒ\s*[^\n]{0,100}",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"©\s*[^\n]{0,100}",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"[ \t]+",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    return cleaned.strip()


def extract_article_text(
    url: str,
    max_chars: int,
) -> str:
    if not url:
        return ""

    try:
        downloaded = trafilatura.fetch_url(
            url
        )

        if not downloaded:
            LOGGER.warning(
                "Could not download article: %s",
                url,
            )
            return ""

        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            include_images=False,
            include_links=False,
            favor_precision=True,
            deduplicate=True,
            output_format="txt",
        )

        if not extracted:
            LOGGER.warning(
                "Could not extract article body: %s",
                url,
            )
            return ""

        cleaned = _remove_trailing_noise(
            extracted
        )

        lines: list[str] = []

        for raw_line in cleaned.splitlines():
            line = re.sub(
                r"\s+",
                " ",
                raw_line,
            ).strip()

            if not line:
                continue

            if line in {
                "기사입력",
                "수정",
                "댓글",
                "공유",
                "인쇄",
                "가나다라마바사",
                "관련 뉴스",
                "많이 본 뉴스",
            }:
                continue

            if re.fullmatch(
                r"댓글\s*\d*",
                line,
            ):
                continue

            lines.append(line)

        final_text = "\n\n".join(lines)
        final_text = _remove_trailing_noise(
            final_text
        )

        return final_text[
            :max_chars
        ].strip()

    except Exception:
        LOGGER.exception(
            "Article extraction failed: %s",
            url,
        )
        return ""


def published_iso(
    value: str,
) -> str | None:
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(
            value
        )
        return parsed.isoformat()
    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        LOGGER.warning(
            "Could not parse published date: %s",
            value,
        )
        return None


def today_iso() -> str:
    return datetime.now().date().isoformat()
