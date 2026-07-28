from __future__ import annotations

from pydantic import BaseModel, Field


class SentencePair(BaseModel):
    korean: str
    chinese: str
    pinyin: str


class VocabularyItem(BaseModel):
    word: str
    pinyin: str
    meaning_ko: str
    example_zh: str = ""
    example_ko: str = ""


class GrammarItem(BaseModel):
    expression: str
    explanation_ko: str
    example_zh: str
    example_ko: str


class QuizItem(BaseModel):
    question_ko: str
    choices: list[str] = Field(min_length=3, max_length=5)
    answer_index: int = Field(ge=0, le=4)
    explanation_ko: str


class StudyArticle(BaseModel):
    title_ko: str
    title_zh: str
    title_pinyin: str
    summary_ko: str
    summary_zh: str
    difficulty: int = Field(ge=1, le=5)
    sentence_pairs: list[SentencePair]
    vocabulary: list[VocabularyItem]
    grammar: list[GrammarItem]
    quizzes: list[QuizItem]
