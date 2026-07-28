from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --green: #34C759;
            --green-strong: #2AA84A;
            --green-dark: #1F7A35;
            --green-soft: #EAF9EE;
            --green-soft-2: #F3FBF5;
            --text: #1C1C1E;
            --muted: #6E6E73;
            --line: #E5E5EA;
            --surface: #FFFFFF;
            --surface-soft: #F5F5F7;
            --shadow-sm: 0 10px 30px rgba(0, 0, 0, .055);
            --shadow-md: 0 24px 65px rgba(0, 0, 0, .09);
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "SF Pro Text", "Apple SD Gothic Neo", "Noto Sans KR",
                         "Segoe UI", sans-serif;
        }

        html { scroll-behavior: smooth; }

        .stApp {
            background: #F5F5F7;
            color: var(--text);
        }

        header[data-testid="stHeader"] {
            background: rgba(245, 245, 247, .84);
            backdrop-filter: blur(18px);
            border-bottom: 1px solid rgba(229, 229, 234, .82);
        }

        #MainMenu, footer { visibility: hidden; }

        .block-container {
            max-width: 1180px;
            padding-top: 5.15rem !important;
            padding-bottom: 5rem !important;
        }

        h1, h2, h3, h4 {
            color: var(--text);
            letter-spacing: -.045em;
        }

        p, label, li { letter-spacing: -.01em; }

        /* ---------- Navigation ---------- */
        .nav-shell {
            position: relative;
            z-index: 2;
            padding: .7rem .85rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(229, 229, 234, .96);
            border-radius: 1.35rem;
            background: rgba(255, 255, 255, .92);
            box-shadow: var(--shadow-sm);
        }

        .brand-row {
            display: flex;
            align-items: center;
            min-height: 2.8rem;
            gap: .72rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 2.25rem;
            height: 2.25rem;
            border-radius: .78rem;
            color: #fff;
            background: linear-gradient(145deg, #34C759, #2DB84D);
            box-shadow: 0 8px 22px rgba(52, 199, 89, .25);
            font-size: .98rem;
            font-weight: 780;
        }

        .brand-name {
            font-size: 1.03rem;
            line-height: 1.15;
            font-weight: 760;
            color: var(--text);
            letter-spacing: -.035em;
        }

        .brand-sub {
            margin-top: .15rem;
            color: #8E8E93;
            font-size: .69rem;
            font-weight: 560;
        }

        /* nav buttons are text-like, not giant pills */
        .nav-shell div.stButton > button {
            min-height: 2.5rem !important;
            padding: 0 .62rem !important;
            border: 0 !important;
            border-radius: .82rem !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #515154 !important;
            font-size: .87rem !important;
            font-weight: 650 !important;
        }

        .nav-shell div.stButton > button:hover {
            color: var(--green-dark) !important;
            background: var(--green-soft-2) !important;
            transform: none !important;
        }

        .nav-shell div.stButton > button[kind="primary"] {
            color: var(--green-dark) !important;
            background: var(--green-soft) !important;
        }

        /* ---------- Page heading ---------- */
        .page-head {
            margin: .5rem 0 1.7rem;
        }

        .page-eyebrow {
            color: var(--green-strong);
            font-size: .78rem;
            font-weight: 760;
            letter-spacing: .01em;
            margin-bottom: .65rem;
        }

        .page-title {
            margin: 0;
            color: var(--text);
            font-size: clamp(2.35rem, 4.5vw, 3.55rem);
            line-height: 1.08;
            font-weight: 760;
            letter-spacing: -.065em;
        }

        .page-copy {
            max-width: 650px;
            margin-top: .8rem;
            color: var(--muted);
            font-size: .98rem;
            line-height: 1.72;
        }

        /* ---------- Hero ---------- */
        .hero-copy-wrap {
            padding: 4rem 0 3.35rem;
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            margin-bottom: 1.35rem;
            padding: .42rem .78rem;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: .8rem;
            font-weight: 740;
        }

        .hero-title {
            max-width: 610px;
            margin: 0;
            color: var(--text);
            font-size: clamp(3rem, 5.55vw, 4.8rem);
            line-height: 1.04;
            font-weight: 760;
            letter-spacing: -.072em;
        }

        .hero-title .accent { color: var(--green-strong); }

        .hero-copy {
            max-width: 565px;
            margin-top: 1.45rem;
            color: var(--muted);
            font-size: 1.04rem;
            line-height: 1.78;
        }

        .hero-proof {
            display: flex;
            flex-wrap: wrap;
            gap: .75rem 1.1rem;
            margin-top: 1.55rem;
            color: #5F5F63;
            font-size: .84rem;
            font-weight: 630;
        }

        .hero-proof span::before {
            content: "✓";
            margin-right: .38rem;
            color: var(--green-strong);
            font-weight: 850;
        }

        .hero-expression {
            position: relative;
            overflow: hidden;
            min-height: 470px;
            padding: 2.15rem;
            border: 1px solid #E5E5EA;
            border-radius: 2.1rem;
            background:
                radial-gradient(circle at 100% 0%, rgba(52, 199, 89, .20), transparent 40%),
                linear-gradient(155deg, #FFFFFF 0%, #F4FBF6 100%);
            box-shadow: var(--shadow-md);
        }

        .hero-expression::after {
            content: "";
            position: absolute;
            right: -5rem;
            bottom: -5rem;
            width: 13rem;
            height: 13rem;
            border-radius: 50%;
            background: rgba(52, 199, 89, .07);
        }

        .expression-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.75rem;
        }

        .expression-label {
            color: var(--green-dark);
            font-size: .82rem;
            font-weight: 780;
        }

        .expression-type {
            padding: .28rem .58rem;
            border-radius: 999px;
            color: var(--green-dark);
            background: rgba(52, 199, 89, .11);
            font-size: .7rem;
            font-weight: 730;
        }

        .expression-main {
            color: var(--text);
            font-size: clamp(2.25rem, 4vw, 3.25rem);
            line-height: 1.17;
            font-weight: 780;
            letter-spacing: -.04em;
        }

        .expression-pinyin {
            margin-top: .68rem;
            color: var(--green-dark);
            font-size: .98rem;
            font-weight: 640;
        }

        .expression-meaning {
            margin-top: 1.3rem;
            color: var(--text);
            font-size: 1.28rem;
            line-height: 1.55;
            font-weight: 690;
            letter-spacing: -.025em;
        }

        .expression-example {
            position: relative;
            z-index: 1;
            margin-top: 1.5rem;
            padding: 1.1rem 1.15rem;
            border: 1px solid #E5E5EA;
            border-radius: 1.15rem;
            background: rgba(255,255,255,.78);
        }

        .expression-example-title {
            margin-bottom: .5rem;
            color: var(--muted);
            font-size: .72rem;
            font-weight: 740;
        }

        .expression-example-zh {
            color: var(--text);
            font-size: 1rem;
            line-height: 1.65;
            font-weight: 650;
        }

        .expression-example-ko {
            margin-top: .25rem;
            color: var(--muted);
            font-size: .87rem;
            line-height: 1.6;
        }

        /* ---------- Sections/cards ---------- */
        .section-heading-row {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 3.6rem 0 1.15rem;
        }

        .section-heading {
            margin: 2.7rem 0 1rem;
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 750;
            letter-spacing: -.045em;
        }

        .section-heading-row .section-heading { margin: 0; }
        .section-caption { color: var(--muted); font-size: .86rem; }

        .featured-card,
        .article-card,
        .surface,
        .filter-panel,
        .word-card,
        .detail-hero,
        .stat-card {
            border: 1px solid var(--line);
            background: rgba(255,255,255,.94);
            box-shadow: var(--shadow-sm);
        }

        .featured-card {
            padding: 1.9rem;
            border-radius: 1.75rem;
        }

        .featured-kicker {
            margin-bottom: .85rem;
            color: var(--green-dark);
            font-size: .76rem;
            font-weight: 780;
        }

        .featured-title {
            color: var(--text);
            font-size: 1.7rem;
            line-height: 1.38;
            font-weight: 750;
            letter-spacing: -.04em;
        }

        .featured-zh {
            margin-top: .6rem;
            color: var(--green-dark);
            font-size: 1.02rem;
            line-height: 1.62;
        }

        .featured-summary {
            margin-top: .9rem;
            color: var(--muted);
            font-size: .93rem;
            line-height: 1.72;
        }

        .featured-metrics {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .72rem;
            margin-top: 1.2rem;
        }

        .metric-box {
            padding: .9rem;
            border-radius: 1rem;
            background: var(--surface-soft);
        }

        .metric-label { color: var(--muted); font-size: .7rem; font-weight: 650; }
        .metric-value { margin-top: .2rem; color: var(--text); font-size: .95rem; font-weight: 740; }

        .topic-card {
            min-height: 8.4rem;
            padding: 1.2rem 1.1rem;
            border: 1px solid var(--line);
            border-radius: 1.35rem;
            background: rgba(255,255,255,.92);
            box-shadow: 0 8px 25px rgba(0,0,0,.035);
            transition: .16s ease;
        }

        .topic-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
        .topic-icon { font-size: 1.42rem; }
        .topic-name { margin-top: .8rem; font-size: 1rem; font-weight: 730; }
        .topic-count { margin-top: .22rem; color: var(--muted); font-size: .76rem; }

        .article-card {
            padding: 1.45rem 1.5rem;
            margin-bottom: .55rem;
            border-radius: 1.45rem;
            transition: .16s ease;
        }

        .article-card:hover { transform: translateY(-2px); box-shadow: 0 16px 38px rgba(0,0,0,.075); }
        .article-title { margin: .62rem 0 .38rem; color: var(--text); font-size: 1.18rem; line-height: 1.43; font-weight: 710; letter-spacing: -.03em; }
        .article-zh { color: var(--green-dark); font-size: .96rem; line-height: 1.6; }
        .meta { color: var(--muted); font-size: .82rem; line-height: 1.55; }

        .badge {
            display: inline-block;
            margin: 0 .25rem .3rem 0;
            padding: .28rem .62rem;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: .72rem;
            font-weight: 720;
        }

        .filter-panel {
            padding: 1.35rem 1.4rem .9rem;
            margin-bottom: 2rem;
            border-radius: 1.45rem;
        }

        .surface {
            padding: 1.45rem 1.5rem;
            border-radius: 1.4rem;
        }

        .detail-hero {
            padding: 1.65rem 1.7rem;
            border-radius: 1.55rem;
            margin: 1rem 0 1.4rem;
        }

        .sentence-box {
            padding: 1.2rem 1.25rem;
            margin-bottom: .8rem;
            border: 1px solid var(--line);
            border-radius: 1.15rem;
            background: #fff;
        }
        .sentence-zh { color: var(--text); font-size: 1.15rem; line-height: 1.9; font-weight: 620; }
        .sentence-pinyin { margin-top: .18rem; color: var(--green-dark); line-height: 1.7; }
        .sentence-ko { margin-top: .2rem; color: var(--muted); line-height: 1.72; }

        .empty {
            padding: 3.2rem 1.5rem;
            text-align: center;
            border: 1px dashed #D1D1D6;
            border-radius: 1.45rem;
            color: var(--muted);
            background: rgba(255,255,255,.72);
        }

        .stat-card { padding: 1.3rem 1.35rem; border-radius: 1.35rem; }
        .stat-number { margin-top: .28rem; color: var(--green-dark); font-size: 2rem; font-weight: 760; letter-spacing: -.045em; }

        /* ---------- Buttons ---------- */
        div.stButton > button,
        div.stDownloadButton > button,
        a[data-testid="stLinkButton"] {
            min-height: 2.8rem;
            border: 1px solid var(--line) !important;
            border-radius: .95rem !important;
            background: #fff !important;
            color: #3A3A3C !important;
            box-shadow: none !important;
            font-weight: 660 !important;
            transition: .15s ease !important;
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover,
        a[data-testid="stLinkButton"]:hover {
            border-color: #A7DDB5 !important;
            color: var(--green-dark) !important;
            transform: translateY(-1px);
        }

        div.stButton > button[kind="primary"],
        div.stDownloadButton > button[kind="primary"] {
            border-color: transparent !important;
            background: linear-gradient(145deg, #34C759, #2DB84D) !important;
            color: #fff !important;
            box-shadow: 0 10px 24px rgba(52,199,89,.22) !important;
        }

        div.stButton > button[kind="primary"]:hover,
        div.stDownloadButton > button[kind="primary"]:hover {
            color: #fff !important;
            box-shadow: 0 13px 30px rgba(52,199,89,.29) !important;
        }

        /* ---------- Inputs / Selects / tags ---------- */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea {
            min-height: 3rem !important;
            border-color: #D1D1D6 !important;
            border-radius: .9rem !important;
            background: #fff !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: #72D28C !important;
            box-shadow: 0 0 0 3px rgba(52,199,89,.12) !important;
        }

        /* Fix the red multiselect chips in the screenshot */
        span[data-baseweb="tag"],
        div[data-baseweb="tag"] {
            background: var(--green-soft) !important;
            color: var(--green-dark) !important;
            border-radius: .55rem !important;
        }
        span[data-baseweb="tag"] svg,
        div[data-baseweb="tag"] svg {
            fill: var(--green-dark) !important;
            color: var(--green-dark) !important;
        }

        /* 라디오 버튼 · 체크박스 · 토글 초록색 */
input[type="radio"],
input[type="checkbox"] {
    accent-color: #34C759 !important;
}

/* 선택된 라디오 버튼 */
[data-testid="stRadio"] [role="radio"][aria-checked="true"] {
    background-color: #34C759 !important;
    border-color: #34C759 !important;
}

/* Streamlit 버전별 라디오 버튼 대응 */
[data-testid="stRadio"] label:has(input:checked) > div:first-child {
    background-color: #34C759 !important;
    border-color: #34C759 !important;
}

/* 선택된 원 안쪽 흰 점 */
[data-testid="stRadio"] label:has(input:checked) > div:first-child > div {
    background-color: #FFFFFF !important;
}

[data-testid="stRadio"] [role="radiogroup"] label {
    color: #48484A !important;
}

[data-testid="stToggle"] button[aria-checked="true"] {
    background-color: #34C759 !important;
}
        [data-testid="stRadio"] [role="radiogroup"] label { color: #48484A !important; }
        [data-testid="stToggle"] button[aria-checked="true"] { background-color: var(--green) !important; }

        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: .35rem;
            border-bottom: 1px solid var(--line);
        }
        div[data-testid="stTabs"] button {
            padding-left: .85rem;
            padding-right: .85rem;
            color: var(--muted);
        }
        div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--green-dark) !important; }
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--green) !important; }

        /* bordered Streamlit containers */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line) !important;
            border-radius: 1.3rem !important;
            background: rgba(255,255,255,.92) !important;
            box-shadow: 0 8px 26px rgba(0,0,0,.035) !important;
        }

        @media (max-width: 900px) {
            .block-container { padding-top: 4.8rem !important; }
            .nav-shell { border-radius: 1.1rem; }
            .hero-copy-wrap { padding: 2.4rem 0 1.4rem; }
            .hero-expression { min-height: auto; margin-top: .7rem; }
            .featured-metrics { grid-template-columns: 1fr; }
            .section-heading-row { align-items: start; flex-direction: column; gap: .25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
