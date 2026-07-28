from __future__ import annotations

import json

from openai import OpenAI

from .models import StudyArticle


SYSTEM_PROMPT = """당신은 한국 뉴스를 중국어로 가르치는 전문 교사이자 번역가다.
반드시 중국 대륙의 간체자를 사용한다. 기사 내용을 사실대로 유지하고, 원문에 없는 사실을 추가하지 않는다.
인명·기관명·수치·날짜를 보존한다. 문단을 학습하기 좋은 문장 단위로 나누되 지나치게 축약하지 않는다.
중국어 번역은 자연스러운 현대 표준중국어 뉴스 문체로 작성한다.
병음은 성조 부호를 포함한다. 결과는 지정된 JSON 형식만 출력한다.
"""


def translate_article(api_key: str, model: str, *, title: str, body: str, source_url: str) -> StudyArticle:
    client = OpenAI(api_key=api_key)
    schema = StudyArticle.model_json_schema()
    prompt = f"""아래 한국어 뉴스 기사를 중국어 학습자료로 변환하라.

요구사항:
- 제목과 본문 전체의 핵심 정보를 빠뜨리지 말고 번역
- sentence_pairs에는 원문의 흐름대로 한국어 문장과 중국어 번역을 8~30개 수록
- 원문이 짧으면 가능한 범위에서 모두 수록
- summary_ko와 summary_zh는 각각 3~5문장
- vocabulary는 중요한 뉴스 단어 8~15개
- grammar는 유용한 표현 3~6개
- quizzes는 객관식 3개
- difficulty는 중국어 독해 난이도 1~5
- 출처 URL은 번역문에 넣지 말 것

제목: {title}
출처: {source_url}
본문:
{body}
"""
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "study_article",
                "schema": schema,
                "strict": True,
            }
        },
    )
    raw = response.output_text
    return StudyArticle.model_validate(json.loads(raw))
