# K-News Chinese Reader

네이버 뉴스 검색 → 기사 본문 추출 → DeepL 중국어 번역 → 병음/단어/문법/퀴즈 생성 → Supabase 저장 → Streamlit 웹사이트 표시 프로젝트입니다.

## 지금 사용자가 해야 할 일

1. ZIP 내부 파일을 GitHub 저장소 루트에 덮어쓰기합니다.
2. 숨김 폴더 `.github`가 업로드되지 않으면 `github-workflow-main.yml` 내용을 기존 `.github/workflows/main.yml`에 붙여넣습니다.
3. Supabase SQL Editor에서 `supabase/schema.sql`을 실행합니다. 기존 테이블이 있어도 필요한 정책을 다시 적용할 수 있습니다.
4. GitHub Actions에서 `Daily K-News to Chinese` → `Run workflow` → mode `reprocess`를 실행해 기존 3개 기사의 단어/문법/퀴즈를 채웁니다.
5. 그 뒤 mode `collect`를 실행해 새 기사도 확인합니다.

## Streamlit 배포

Streamlit Community Cloud에서 이 GitHub 저장소를 연결하고 Main file path를 `app.py`로 지정합니다.
Advanced settings의 Secrets에 아래를 넣습니다.

```toml
SUPABASE_URL = "https://프로젝트주소.supabase.co"
SUPABASE_ANON_KEY = "Supabase anon key"
```

배포 후 생성된 주소를 GitHub Secret `APP_URL`에 넣으면 이메일 버튼이 사이트로 연결됩니다.

## 이메일(선택)

Resend 계정과 발신 도메인/주소 설정 후 GitHub Secrets에 `RESEND_API_KEY`, `EMAIL_FROM`, `EMAIL_TO`, `APP_URL`을 추가합니다. 이 값들이 없으면 수집은 정상 동작하고 이메일만 건너뜁니다.

## 주의

- DeepL만으로 문법 해설은 생성형 AI 수준이 아니며, 코드에 등록된 자주 쓰는 뉴스 문법 패턴을 탐지합니다.
- 단어 뜻은 DeepL로 중국어→한국어 역번역합니다.
- 일부 언론사는 본문 추출을 차단해 건너뛸 수 있습니다.
