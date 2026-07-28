from __future__ import annotations

import html
from collections.abc import Sequence

import resend


def send_digest(api_key: str, sender: str, recipient: str, app_url: str, articles: Sequence[dict]) -> None:
    if not articles:
        return
    resend.api_key = api_key
    cards = []
    for item in articles:
        data = item["study_data"]
        words = ", ".join(v["word"] for v in data.get("vocabulary", [])[:5])
        article_url = f"{app_url}?article={item.get('id', '')}" if app_url else item["source_url"]
        cards.append(f"""
        <div style="border:1px solid #e5e7eb;border-radius:12px;padding:18px;margin:14px 0">
          <div style="font-size:13px;color:#6b7280">{html.escape(item['category'])}</div>
          <h2 style="font-size:19px;margin:6px 0">{html.escape(data['title_ko'])}</h2>
          <div style="font-size:17px;margin-bottom:8px">{html.escape(data['title_zh'])}</div>
          <p style="color:#374151">{html.escape(data['summary_ko'])}</p>
          <p><b>오늘의 단어</b> {html.escape(words)}</p>
          <a href="{html.escape(article_url)}" style="display:inline-block;background:#111827;color:white;text-decoration:none;padding:10px 14px;border-radius:8px">공부하러 가기</a>
        </div>
        """)
    body = f"""
    <div style="font-family:Arial,'Apple SD Gothic Neo',sans-serif;max-width:680px;margin:auto;padding:24px">
      <h1>오늘의 중국어 뉴스</h1>
      <p>새 학습자료 {len(articles)}개가 등록됐어요.</p>
      {''.join(cards)}
      <p style="font-size:12px;color:#9ca3af">기사 원문은 각 언론사 링크에서 확인하세요.</p>
    </div>
    """
    resend.Emails.send({
        "from": sender,
        "to": [recipient],
        "subject": f"오늘의 중국어 뉴스 {len(articles)}개",
        "html": body,
    })
