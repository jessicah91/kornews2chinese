# K-News Chinese Reader — DeepL MVP

현재 1단계 버전은 매일 한국 뉴스 3건을 수집하고, 본문을 DeepL로 중국어 간체 번역한 뒤 병음과 함께 Supabase에 저장합니다.

## 필요한 GitHub Actions Secrets

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `DEEPL_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## 첫 실행

GitHub 저장소의 **Actions → Daily Chinese News → Run workflow**를 누릅니다.
성공하면 Supabase의 `articles` 테이블에 경제·사회·국제 기사 각 1건이 저장됩니다.

## 다음 단계

첫 실행 성공 후 Streamlit 사이트 배포와 이메일 발송을 연결합니다.
