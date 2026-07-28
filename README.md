# 오늘의 중국어 V3

Streamlit + Supabase 기반 한국 뉴스 중국어 학습 서비스입니다.

## 적용 방법

기존 GitHub 저장소의 루트에 아래 구조가 되도록 파일을 업로드하세요.

```text
app.py
components/
services/
utils/
views/
```

기존 `collect.py`, `news.py`, `config.py`, `.github/workflows/` 등은 삭제하지 않습니다.

## 필요한 패키지

기존 requirements.txt에 아래 패키지가 포함되어 있어야 합니다.

```text
streamlit
supabase
```

## Streamlit Secrets

```toml
SUPABASE_URL="..."
SUPABASE_ANON_KEY="..."
```

## 이번 버전에서 동작하는 기능

- 상단 메뉴 실제 화면 전환
- 홈 카테고리 버튼 실제 필터 연결
- 기사 검색과 정렬
- 기사 상세 학습
- 단어 저장 및 단어장
- 기사 즐겨찾기
- 마이페이지 기본 학습 통계
- 모바일 반응형
- 초록색 Apple 스타일 UI

## 주의

단어장, 즐겨찾기, 학습 통계는 현재 Streamlit session_state에 저장됩니다.
브라우저 세션이 종료되면 초기화될 수 있습니다.
다음 단계에서 Supabase 사용자 테이블에 영구 저장하도록 연결할 수 있습니다.


## V3.1 추가 기능

- 홈 화면에 `오늘의 표현` 카드 추가
- 단어 대신 문법, 관용표현, 자주 쓰는 중국어 패턴 표시
- 기사 `study_data.grammar`가 있으면 기사 속 표현 우선 사용
- 기사 문법 데이터가 없으면 기본 표현 목록에서 날짜별 자동 순환
- 기사에서 가져온 표현은 `관련 기사 보기`로 바로 이동
