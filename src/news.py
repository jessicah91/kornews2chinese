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

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


# 허용할 언론사
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


# 제목에 아래 표현이 있으면 수집하지 않음
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


# 중국어 학습용으로 지나치게 전문적인 기사에 자주 등장하는 표현
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


# 일반 독자가 읽기 좋은 주요 뉴스에 자주 등장하는 표현
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
)


# 기사 본문에서 제거할 꼬리 문구
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


def _clean(value: str | None) -> str:
    """네이버 검색 결과의 HTML 태그와 엔티티를 정리한다."""
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def search_naver_news(
    client_id: str,
    client_secret: str,
    query: str,
    display: int = 100,
) -> list[NewsCandidate]:
    """네이버 뉴스 검색 API에서 최신 기사 후보를 가져온다."""
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
            description=_clean(item.get("description")),
            link=item.get("link", "") or "",
            original_link=item.get("originallink", "")
            or item.get("link", "")
            or "",
            published_at=item.get("pubDate", "") or "",
        )
        for item in items
    ]


def _hostname(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return ""


def publisher_name(url: str) -> str | None:
    """허용 언론사 URL이면 언론사 이름을 반환한다."""
    hostname = _hostname(url)

    for domain, name in ALLOWED_PUBLISHERS.items():
        if hostname == domain or hostname.endswith("." + domain):
            return name

    return None


def _is_allowed_publisher(url: str) -> bool:
    return publisher_name(url) is not None


def _is_blocked_title(title: str) -> bool:
    normalized = re.sub(r"\s+", " ", title).strip().lower()

    return any(
        blocked.lower() in normalized
        for blocked in BLOCKED_TITLE_WORDS
    )


def _difficulty_penalty(title: str, description: str) -> int:
    """제목과 요약만으로 지나치게 전문적인 기사에 감점을 준다."""
    combined = f"{title} {description}"
    hits = sum(1 for term in VERY_DIFFICULT_TERMS if term in combined)

    penalty = hits * 4

    # 제목이 지나치게 길거나 기호·약어가 많은 기사도 감점
    if len(title) > 75:
        penalty += 2

    uppercase_tokens = re.findall(r"\b[A-Z]{3,}\b", title)
    if len(uppercase_tokens) >= 3:
        penalty += 2

    special_count = len(re.findall(r"[%·:/()〈〉《》\[\]]", title))
    if special_count >= 6:
        penalty += 2

    return penalty


def _importance_score(candidate: NewsCandidate) -> int:
    """중국어 학습에 적절한 일반 주요 뉴스가 먼저 선택되도록 점수를 계산한다."""
    combined = f"{candidate.title} {candidate.description}"

    score = 10

    for term in IMPORTANT_NEWS_TERMS:
        if term in combined:
            score += 2

    score -= _difficulty_penalty(candidate.title, candidate.description)

    # 내용이 너무 짧은 검색 결과는 감점
    if len(candidate.description) < 35:
        score -= 2

    # 제목이 지나치게 짧으면 단순 알림 기사일 가능성이 있음
    if len(candidate.title) < 12:
        score -= 3

    return score


def choose_candidate(
    candidates: list[NewsCandidate],
    seen_urls: set[str],
) -> NewsCandidate | None:
    """
    지정 언론사·일반 기사만 남긴 뒤,
    주요 뉴스성과 학습 난이도를 고려해 가장 적절한 기사를 고른다.
    """
    valid_candidates: list[NewsCandidate] = []

    for candidate in candidates:
        canonical_url = candidate.original_link or candidate.link

        if not canonical_url:
            continue

        if canonical_url in seen_urls:
            continue

        if not _is_allowed_publisher(canonical_url):
            continue

        if _is_blocked_title(candidate.title):
            LOGGER.info(
                "Skipping blocked article title: %s",
                candidate.title,
            )
            continue

        score = _importance_score(candidate)

        # 너무 전문적이거나 학습 가치가 낮은 후보는 제외
        if score < 5:
            LOGGER.info(
                "Skipping low-value/difficult article (%s): %s",
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

    LOGGER.info(
        "Selected article [%s, score=%s]: %s",
        publisher_name(selected.original_link or selected.link),
        _importance_score(selected),
        selected.title,
    )

    return selected


def _remove_trailing_noise(text: str) -> str:
    """기자 이메일, 저작권, SNS 공유 등 기사 외 문구를 제거한다."""
    cleaned = text

    # 기자 이메일 제거
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

    # 기사 중간이나 끝에 붙은 매체 저작권 문구 제거
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

    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def extract_article_text(url: str, max_chars: int) -> str:
    """기사 URL에서 본문을 추출하고 불필요한 문구를 정리한다."""
    if not url:
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            LOGGER.warning("Could not download article: %s", url)
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
            LOGGER.warning("Could not extract article body: %s", url)
            return ""

        cleaned = _remove_trailing_noise(extracted)

        # 너무 짧은 줄과 UI성 문구를 제거
        lines: list[str] = []

        for raw_line in cleaned.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()

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

            if re.fullmatch(r"댓글\s*\d*", line):
                continue

            lines.append(line)

        final_text = "\n\n".join(lines)
        final_text = _remove_trailing_noise(final_text)

        return final_text[:max_chars].strip()

    except Exception:
        LOGGER.exception("Article extraction failed: %s", url)
        return ""


def published_iso(value: str) -> str | None:
    """네이버 API 날짜를 ISO 형식으로 변환한다."""
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
        return parsed.isoformat()
    except (TypeError, ValueError, OverflowError):
        LOGGER.warning("Could not parse published date: %s", value)
        return None


def today_iso() -> str:
    return datetime.now().date().isoformat()
