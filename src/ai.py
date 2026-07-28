from __future__ import annotations

import re

import requests
from pypinyin import Style, lazy_pinyin

from .models import StudyArticle, SentencePair

DEEPL_FREE_URL = "https://api-free.deepl.com/v2/translate"
DEEPL_PRO_URL = "https://api.deepl.com/v2/translate"


def _sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+|(?<=[다요죠임함됨됨])\.\s*", text)
    return [part.strip() for part in parts if len(part.strip()) >= 8]


def _pinyin(text: str) -> str:
    return " ".join(lazy_pinyin(text, style=Style.TONE, neutral_tone_with_five=False))


def _translate(api_key: str, texts: list[str]) -> list[str]:
    if not texts:
        return []
    endpoint = DEEPL_FREE_URL if api_key.endswith(":fx") else DEEPL_PRO_URL
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"DeepL-Auth-Key {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "text": texts,
            "source_lang": "KO",
            "target_lang": "ZH-HANS",
            "preserve_formatting": True,
        },
        timeout=90,
    )
    response.raise_for_status()
    translated = response.json().get("translations", [])
    if len(translated) != len(texts):
        raise RuntimeError("DeepL returned an unexpected number of translations")
    return [item["text"].strip() for item in translated]


def translate_article(api_key: str, *, title: str, body: str, source_url: str) -> StudyArticle:
    del source_url  # reserved for later learning features
    korean_sentences = _sentences(body)[:40]
    if not korean_sentences:
        raise RuntimeError("No sentences were extracted from the article")

    # DeepL request limits are easier to manage in chunks.
    translated_sentences: list[str] = []
    for start in range(0, len(korean_sentences), 20):
        translated_sentences.extend(_translate(api_key, korean_sentences[start:start + 20]))

    title_zh = _translate(api_key, [title])[0]
    summary_ko = " ".join(korean_sentences[:3])
    summary_zh = " ".join(translated_sentences[:3])

    pairs = [
        SentencePair(korean=ko, chinese=zh, pinyin=_pinyin(zh))
        for ko, zh in zip(korean_sentences, translated_sentences, strict=True)
    ]

    return StudyArticle(
        title_ko=title,
        title_zh=title_zh,
        title_pinyin=_pinyin(title_zh),
        summary_ko=summary_ko,
        summary_zh=summary_zh,
        difficulty=3,
        sentence_pairs=pairs,
        vocabulary=[],
        grammar=[],
        quizzes=[],
    )
