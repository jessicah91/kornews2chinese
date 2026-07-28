# K-News Chinese Reader

매일 한국 뉴스를 수집해 중국어 전문 번역, 병음, 핵심 단어, 문법, 독해 문제로 변환하고 이메일로 알려 주는 개인 학습 사이트입니다.

## 구성

- 뉴스 검색: Naver Search API
- 기사 본문 추출: Trafilatura
- 번역·학습자료 생성: OpenAI API
- 저장: Supabase
- 사이트: Streamlit
- 이메일: Resend
- 자동 실행: GitHub Actions

## 1. Supabase 만들기

1. Supabase 프로젝트를 생성합니다.
2. SQL Editor에서 `supabase/schema.sql`을 실행합니다.
3. Project Settings → API에서 아래 값을 확인합니다.
   - Project URL
   - anon public key
   - service_role key

`service_role` 키는 GitHub Secrets에만 넣고 사이트에는 절대 노출하지 마세요.

## 2. 네이버 뉴스 API

네이버 개발자 센터에서 애플리케이션을 만들고 검색 API 사용을 등록합니다.

필요한 값:
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

## 3. OpenAI API

OpenAI API 키를 발급합니다. 기본 모델은 `.env.example`과 GitHub Variables에서 변경할 수 있습니다.

## 4. Resend 이메일

Resend에서 API 키를 발급하고 발신 도메인을 인증합니다.

필요한 값:
- `RESEND_API_KEY`
- `EMAIL_FROM` 예: `K-News Chinese <news@your-domain.com>`
- `EMAIL_TO` 받을 이메일 주소

개발 중에는 Resend 계정에서 허용된 수신 주소와 발신 주소를 사용하세요.

## 5. 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# .env 값 입력
python collect.py
streamlit run app.py
```

## 6. GitHub 설정

저장소 Settings → Secrets and variables → Actions에서 설정합니다.

### Secrets

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `EMAIL_TO`

### Variables

- `APP_URL`: 배포한 Streamlit 주소
- `NEWS_QUERIES`: `경제,사회,국제`
- `ARTICLES_PER_QUERY`: `1`
- `OPENAI_MODEL`: `gpt-5-mini`
- `MAX_ARTICLE_CHARS`: `12000`

GitHub Actions의 `Daily Chinese News` 워크플로는 매일 한국시간 오전 6시에 실행되도록 설정되어 있습니다. 메일은 자료 생성이 끝난 직후 발송됩니다.

## 7. Streamlit 배포

1. Streamlit Community Cloud에서 이 GitHub 저장소를 선택합니다.
2. Main file을 `app.py`로 지정합니다.
3. Secrets에 아래를 입력합니다.

```toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_ANON_KEY = "..."
```

4. 배포된 주소를 GitHub Variable `APP_URL`에 넣습니다.

## 저작권·수집 주의

이 프로젝트는 개인 학습용을 전제로 합니다. 기사 원문과 번역문을 공개·재배포하거나 상업적으로 이용하기 전에는 해당 언론사의 이용약관과 권리 관계를 확인하세요. 일부 언론사는 자동 본문 수집을 차단하므로 해당 기사는 건너뛸 수 있습니다.

## 동작 확인

GitHub Actions → Daily Chinese News → Run workflow로 수동 실행하여 먼저 확인하세요.
