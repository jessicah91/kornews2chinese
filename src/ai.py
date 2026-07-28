from __future__ import annotations
import random, re
from collections import Counter
import jieba, requests
from pypinyin import Style, lazy_pinyin
from .models import GrammarItem, QuizItem, SentencePair, StudyArticle, VocabularyItem

DEEPL_FREE_URL="https://api-free.deepl.com/v2/translate"
DEEPL_PRO_URL="https://api.deepl.com/v2/translate"
STOPWORDS=set("的 了 在 是 和 与 及 为 对 将 也 有 被 这 那 一个 一种 进行 表示 认为 可以 已经 目前 记者 据 其中 以及 相关 通过 今年 近日 方面 工作 问题 情况 中国 韩国".split())
GRAMMAR_PATTERNS=[
("不仅…而且…","‘~뿐만 아니라 …도’라는 뜻으로 두 사실을 함께 강조합니다."),
("由于","원인이나 이유를 나타내는 ‘~로 인해, ~때문에’입니다."),
("因此","앞 문장의 결과를 잇는 ‘따라서, 그러므로’입니다."),
("尽管","양보를 나타내는 ‘비록 ~이지만’입니다."),
("随着","변화가 함께 진행됨을 나타내는 ‘~함에 따라’입니다."),
("对于","주제나 대상을 제시하는 ‘~에 대해서’입니다."),
("根据","근거나 출처를 제시하는 ‘~에 따르면’입니다."),
("为了","목적을 나타내는 ‘~하기 위해’입니다."),
("通过","수단을 나타내는 ‘~을 통해’입니다."),
("正在","진행 중인 동작을 나타내는 ‘~하고 있다’입니다."),
("已经","완료나 상태 변화를 강조하는 ‘이미, 벌써’입니다."),
("仍然","상태가 계속됨을 나타내는 ‘여전히’입니다."),
("可能","가능성이나 추측을 나타내는 ‘~일 수 있다’입니다."),
]

def _sentences(text:str)->list[str]:
    text=re.sub(r"\s+"," ",text).strip()
    if not text:return []
    parts=re.split(r"(?<=[.!?。！？])\s+|(?<=다\.)\s+|(?<=요\.)\s+",text)
    return [p.strip() for p in parts if len(p.strip())>=12]

def _pinyin(text:str)->str:return " ".join(lazy_pinyin(text,style=Style.TONE,neutral_tone_with_five=False))

def _translate(api_key:str,texts:list[str],source_lang:str,target_lang:str)->list[str]:
    if not texts:return []
    endpoint=DEEPL_FREE_URL if api_key.endswith(":fx") else DEEPL_PRO_URL
    out=[]
    for start in range(0,len(texts),25):
        chunk=texts[start:start+25]
        r=requests.post(endpoint,headers={"Authorization":f"DeepL-Auth-Key {api_key}","Content-Type":"application/json"},json={"text":chunk,"source_lang":source_lang,"target_lang":target_lang,"preserve_formatting":True},timeout=120)
        r.raise_for_status()
        vals=[x["text"].strip() for x in r.json().get("translations",[])]
        if len(vals)!=len(chunk):raise RuntimeError("DeepL returned an unexpected number of translations")
        out.extend(vals)
    return out

def _difficulty(sentences:list[str])->int:
    if not sentences:return 1
    avg=sum(len(s) for s in sentences)/len(sentences)
    return 1 if avg<25 else 2 if avg<40 else 3 if avg<60 else 4 if avg<85 else 5

def _vocabulary(api_key:str,pairs:list[SentencePair],limit:int=15)->list[VocabularyItem]:
    corpus=" ".join(p.chinese for p in pairs)
    words=[w.strip() for w in jieba.lcut(corpus) if 2<=len(w.strip())<=6 and re.fullmatch(r"[一-鿿]+",w.strip()) and w.strip() not in STOPWORDS]
    ranked=[w for w,_ in Counter(words).most_common(limit*3)]
    selected=[]
    for w in ranked:
        if any(w in old or old in w for old in selected):continue
        selected.append(w)
        if len(selected)>=limit:break
    meanings=_translate(api_key,selected,"ZH","KO") if selected else []
    result=[]
    for word,meaning in zip(selected,meanings):
        pair=next((p for p in pairs if word in p.chinese),None)
        result.append(VocabularyItem(word=word,pinyin=_pinyin(word),meaning_ko=meaning,example_zh=pair.chinese if pair else "",example_ko=pair.korean if pair else ""))
    return result

def _grammar(pairs:list[SentencePair],limit:int=6)->list[GrammarItem]:
    out=[]
    for pattern,explanation in GRAMMAR_PATTERNS:
        needle=pattern.replace("…","")
        pair=next((p for p in pairs if needle in p.chinese or (pattern.startswith("不仅") and "不仅" in p.chinese and "而且" in p.chinese)),None)
        if pair:
            out.append(GrammarItem(expression=pattern,explanation_ko=explanation,example_zh=pair.chinese,example_ko=pair.korean))
        if len(out)>=limit:break
    return out

def _quizzes(pairs:list[SentencePair],vocab:list[VocabularyItem],limit:int=5)->list[QuizItem]:
    rng=random.Random(42)
    quizzes=[]
    usable=pairs[:min(len(pairs),12)]
    for i,p in enumerate(usable[:3]):
        distract=[x.chinese for x in usable if x.chinese!=p.chinese]
        if len(distract)<2:break
        choices=[p.chinese]+rng.sample(distract,2); rng.shuffle(choices)
        quizzes.append(QuizItem(question_ko=f"다음 한국어 문장의 올바른 중국어 번역은?\n\n{p.korean}",choices=choices,answer_index=choices.index(p.chinese),explanation_ko="기사에 나온 문장과 일치하는 번역입니다."))
    for item in vocab[:max(0,limit-len(quizzes))]:
        others=[v.meaning_ko for v in vocab if v.word!=item.word and v.meaning_ko!=item.meaning_ko]
        if len(others)<2:break
        choices=[item.meaning_ko]+rng.sample(others,2); rng.shuffle(choices)
        quizzes.append(QuizItem(question_ko=f"‘{item.word} ({item.pinyin})’의 뜻은?",choices=choices,answer_index=choices.index(item.meaning_ko),explanation_ko=f"{item.word}는 기사 문맥에서 ‘{item.meaning_ko}’로 쓰였습니다."))
    return quizzes[:limit]

def translate_article(api_key:str,*,title:str,body:str,source_url:str,max_sentences:int=60)->StudyArticle:
    del source_url
    korean=_sentences(body)[:max_sentences]
    if not korean:raise RuntimeError("No sentences were extracted from the article")
    chinese=_translate(api_key,korean,"KO","ZH")
    title_zh=_translate(api_key,[title],"KO","ZH")[0]
    pairs=[SentencePair(korean=ko,chinese=zh,pinyin=_pinyin(zh)) for ko,zh in zip(korean,chinese,strict=True)]
    vocab=_vocabulary(api_key,pairs)
    grammar=_grammar(pairs)
    quizzes=_quizzes(pairs,vocab)
    return StudyArticle(title_ko=title,title_zh=title_zh,title_pinyin=_pinyin(title_zh),summary_ko=" ".join(korean[:3]),summary_zh=" ".join(chinese[:3]),difficulty=_difficulty(chinese),sentence_pairs=pairs,vocabulary=vocab,grammar=grammar,quizzes=quizzes)
