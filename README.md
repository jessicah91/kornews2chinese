# Chinese Daily V4 — Home Redesign

Streamlit + Supabase 기반 한국 뉴스 중국어 학습 서비스입니다.

## 이번 버전에서 바뀐 점

- 홈 화면을 Apple 계열의 여백 중심 레이아웃으로 전면 개편
- 왼쪽 학습 소개 + 오른쪽 `오늘의 표현` 카드로 Hero 재구성
- 추천 기사 영역을 핵심 지표가 보이는 Featured 카드로 변경
- 카테고리를 서비스형 카드 UI로 변경
- 상단 네비게이션과 브랜드 영역 재설계
- Streamlit 상단 헤더와 겹치지 않도록 상단 여백을 `5.6rem`으로 고정
- 데스크톱과 좁은 화면에서 자연스럽게 재배치되는 반응형 CSS 적용

## 적용 방법

기존 GitHub 저장소 루트에 압축을 풀어 덮어쓰세요.

```text
app.py
components/
services/
utils/
views/
```

기존 `collect.py`, `news.py`, `config.py`, `.github/workflows/`는 삭제하지 않습니다.

## 필요한 Streamlit Secrets

```toml
SUPABASE_URL="..."
SUPABASE_ANON_KEY="..."
```
