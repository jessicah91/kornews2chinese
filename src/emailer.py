from __future__ import annotations
import html
from collections.abc import Sequence
import resend

def send_digest(api_key:str,sender:str,recipient:str,app_url:str,articles:Sequence[dict])->None:
    if not articles:return
    resend.api_key=api_key
    cards=[]
    for item in articles:
        data=item["study_data"]
        words=", ".join(v["word"] for v in data.get("vocabulary",[])[:5]) or "오늘의 기사에서 확인"
        article_url=f"{app_url}?article={item.get('id','')}" if app_url else item["source_url"]
        card=("<div style='border:1px solid #e5e7eb;border-radius:12px;padding:18px;margin:14px 0'>"
              f"<div>{html.escape(item.get('category',''))}</div>"
              f"<h2>{html.escape(data['title_ko'])}</h2>"
              f"<div>{html.escape(data['title_zh'])}</div>"
              f"<p>{html.escape(data['summary_ko'])}</p>"
              f"<p><b>오늘의 단어</b> {html.escape(words)}</p>"
              f"<a href='{html.escape(article_url)}'>공부하러 가기</a></div>")
        cards.append(card)
    body="<div style='font-family:Arial,sans-serif;max-width:680px;margin:auto;padding:24px'><h1>오늘의 중국어 뉴스</h1>"+"".join(cards)+"</div>"
    resend.Emails.send({"from":sender,"to":[recipient],"subject":f"오늘의 중국어 뉴스 {len(articles)}개","html":body})
