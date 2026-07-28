from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from components.article_card import open_article
from utils.articles import study_data, title_ko


FALLBACK_EXPRESSIONS = [
    {
        "type": "문법",
        "expression": "既然～就～",
        "pinyin": "jìrán... jiù...",
        "meaning": "이미 ~한 이상, 그러면 ~하다",
        "example": "既然决定了，就不要后悔",
        "translation": "이미 결정한 이상 후회하지 마",
        "note": "앞절의 사실이나 상황을 받아들인 뒤, 그에 따른 판단이나 행동을 말할 때 사용해요.",
    },
    {
        "type": "문법",
        "expression": "一边～一边～",
        "pinyin": "yìbiān... yìbiān...",
        "meaning": "~하면서 동시에 ~하다",
        "example": "她一边看新闻，一边记生词",
        "translation": "그녀는 뉴스를 보면서 새 단어를 적는다",
        "note": "두 행동이 동시에 진행될 때 사용하는 대표적인 병렬 표현이에요.",
    },
    {
        "type": "자주 쓰는 패턴",
        "expression": "越来越～",
        "pinyin": "yuèláiyuè...",
        "meaning": "점점 더 ~해지다",
        "example": "学习中文的人越来越多",
        "translation": "중국어를 공부하는 사람이 점점 많아지고 있다",
        "note": "시간이 흐르면서 상태나 정도가 계속 변할 때 사용해요.",
    },
    {
        "type": "문법",
        "expression": "不但～而且～",
        "pinyin": "búdàn... érqiě...",
        "meaning": "~할 뿐만 아니라 ~하기도 하다",
        "example": "这篇新闻不但有意思，而且很实用",
        "translation": "이 뉴스는 재미있을 뿐만 아니라 매우 실용적이다",
        "note": "두 가지 장점이나 사실을 강조하여 이어 말할 때 사용해요.",
    },
    {
        "type": "자주 쓰는 패턴",
        "expression": "除了～以外～",
        "pinyin": "chúle... yǐwài...",
        "meaning": "~을 제외하고 / ~뿐만 아니라",
        "example": "除了新闻以外，我也喜欢看纪录片",
        "translation": "뉴스 외에도 나는 다큐멘터리 보는 것을 좋아한다",
        "note": "뒤에 还·也·都가 오면 ‘~뿐만 아니라’라는 추가 의미로 자주 사용돼요.",
    },
    {
        "type": "관용표현",
        "expression": "不知不觉",
        "pinyin": "bù zhī bù jué",
        "meaning": "자기도 모르는 사이에",
        "example": "不知不觉，我已经学了一个小时",
        "translation": "나도 모르는 사이에 벌써 한 시간 동안 공부했다",
        "note": "시간이 흐르거나 변화가 일어났음을 뒤늦게 깨달을 때 자연스럽게 사용해요.",
    },
    {
        "type": "문법",
        "expression": "只要～就～",
        "pinyin": "zhǐyào... jiù...",
        "meaning": "~하기만 하면 ~하다",
        "example": "只要每天练习，就会慢慢进步",
        "translation": "매일 연습하기만 하면 조금씩 발전할 것이다",
        "note": "충분조건을 나타내는 표현으로, 앞의 조건만 충족되면 뒤의 결과가 생긴다는 뜻이에요.",
    },
    {
        "type": "문법",
        "expression": "虽然～但是～",
        "pinyin": "suīrán... dànshì...",
        "meaning": "비록 ~하지만",
        "example": "虽然这篇文章有点难，但是很值得读",
        "translation": "이 글은 조금 어렵지만 읽을 가치가 있다",
        "note": "앞뒤 내용이 서로 대비될 때 사용하는 가장 기본적인 양보 표현이에요.",
    },
    {
        "type": "자주 쓰는 패턴",
        "expression": "对～来说",
        "pinyin": "duì... láishuō",
        "meaning": "~에게 있어서 / ~의 입장에서 보면",
        "example": "对初学者来说，这个表达很重要",
        "translation": "초보자에게 이 표현은 매우 중요하다",
        "note": "특정 사람이나 집단의 관점에서 평가하거나 설명할 때 사용해요.",
    },
    {
        "type": "관용표현",
        "expression": "说到做到",
        "pinyin": "shuō dào zuò dào",
        "meaning": "말한 것은 반드시 실천하다",
        "example": "他是一个说到做到的人",
        "translation": "그는 말한 것을 반드시 실천하는 사람이다",
        "note": "약속이나 결심을 행동으로 옮기는 사람을 긍정적으로 평가할 때 자주 써요.",
    },
]


def _first_nonempty(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_article_grammar(article: dict[str, Any]) -> list[dict[str, Any]]:
    grammar = study_data(article).get("grammar") or []
    normalized: list[dict[str, Any]] = []

    if not isinstance(grammar, list):
        return normalized

    for item in grammar:
        if isinstance(item, str) and item.strip():
            normalized.append({
                "type": "기사 속 문법",
                "expression": item.strip(),
                "pinyin": "",
                "meaning": "",
                "example": "",
                "translation": "",
                "note": "오늘의 기사에서 추출한 핵심 표현이에요.",
                "article": article,
            })
            continue

        if not isinstance(item, dict):
            continue

        expression = _first_nonempty(item, "pattern", "grammar", "expression", "title")
        if not expression:
            continue

        normalized.append({
            "type": _first_nonempty(item, "type", "category") or "기사 속 문법",
            "expression": expression,
            "pinyin": _first_nonempty(item, "pinyin"),
            "meaning": _first_nonempty(item, "meaning_ko", "meaning", "explanation_ko", "explanation"),
            "example": _first_nonempty(item, "example", "sentence", "example_zh"),
            "translation": _first_nonempty(item, "translation", "example_ko", "sentence_ko"),
            "note": _first_nonempty(item, "note", "tip", "explanation_ko", "explanation")
                    or "오늘의 기사에서 추출한 핵심 표현이에요.",
            "article": article,
        })

    return normalized


def get_daily_expression(articles: list[dict[str, Any]]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []

    for article in articles[:30]:
        candidates.extend(_normalize_article_grammar(article))

    day_number = date.today().toordinal()

    if candidates:
        return candidates[day_number % len(candidates)]

    fallback = FALLBACK_EXPRESSIONS[day_number % len(FALLBACK_EXPRESSIONS)].copy()
    fallback["article"] = None
    return fallback


def render_daily_expression(articles: list[dict[str, Any]]) -> None:
    expression = get_daily_expression(articles)
    article = expression.get("article")

    st.markdown('<div class="section-heading">오늘의 표현</div>', unsafe_allow_html=True)

    html = [
        '<section class="expression-card">',
        '<div class="expression-topline">',
        f'<span class="expression-label">{expression.get("type", "오늘의 표현")}</span>',
        '<span class="expression-date">매일 한 표현씩</span>',
        '</div>',
        f'<div class="expression-main">{expression.get("expression", "")}</div>',
    ]

    if expression.get("pinyin"):
        html.append(f'<div class="expression-pinyin">{expression["pinyin"]}</div>')

    if expression.get("meaning"):
        html.append(f'<div class="expression-meaning">{expression["meaning"]}</div>')

    if expression.get("example"):
        html.extend([
            '<div class="expression-example">',
            '<div class="expression-example-title">예문</div>',
            f'<div class="expression-example-zh">{expression["example"]}</div>',
        ])
        if expression.get("translation"):
            html.append(f'<div class="expression-example-ko">{expression["translation"]}</div>')
        html.append('</div>')

    if expression.get("note"):
        html.append(f'<div class="expression-note">{expression["note"]}</div>')

    html.append('</section>')
    st.markdown("".join(html), unsafe_allow_html=True)

    if article:
        left, right = st.columns([3, 1])
        with left:
            st.caption(f"이 표현은 「{title_ko(article)}」 기사에서 가져왔어요.")
        with right:
            if st.button(
                "관련 기사 보기",
                key=f"daily_expression_article_{article.get('id')}",
                use_container_width=True,
            ):
                open_article(article)
                st.rerun()
