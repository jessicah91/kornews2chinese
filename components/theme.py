from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --green: #30A46C;
            --green-dark: #217A4E;
            --green-soft: #EAF7EF;
            --green-wash: #F4FAF6;
            --line: #E3ECE6;
            --text: #152019;
            --muted: #667169;
            --white: #FFFFFF;
            --shadow: 0 18px 55px rgba(26, 67, 43, .09);
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "SF Pro Text", "Apple SD Gothic Neo", "Noto Sans KR",
                         "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 78% 2%, rgba(188, 231, 205, .30), transparent 24rem),
                linear-gradient(180deg, #FBFDFC 0%, var(--green-wash) 100%);
            color: var(--text);
        }

        /* Streamlit 상단 헤더와 겹치지 않도록 넉넉하게 확보 */
        .block-container {
            max-width: 1180px;
            padding-top: 5.6rem !important;
            padding-bottom: 5rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(251, 253, 252, .80);
            backdrop-filter: blur(18px);
            border-bottom: 1px solid rgba(227, 236, 230, .72);
        }

        #MainMenu, footer { visibility: hidden; }

        h1, h2, h3 {
            letter-spacing: -.04em;
            color: var(--text);
        }

        p, li, label { letter-spacing: -.01em; }

        /* Navigation */
        .brand-row {
            display: flex;
            align-items: center;
            gap: .68rem;
            min-height: 2.7rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: .8rem;
            background: linear-gradient(145deg, #42C37A, #24915B);
            color: #fff;
            box-shadow: 0 8px 20px rgba(48, 164, 108, .20);
            font-size: 1rem;
        }

        .brand-name {
            color: var(--text);
            font-size: 1.08rem;
            font-weight: 760;
            letter-spacing: -.035em;
        }

        .brand-sub {
            margin-top: .08rem;
            color: var(--muted);
            font-size: .72rem;
            font-weight: 520;
        }

        .nav-shell {
            padding: .72rem .85rem;
            border: 1px solid rgba(227, 236, 230, .92);
            border-radius: 1.35rem;
            background: rgba(255, 255, 255, .84);
            box-shadow: 0 10px 35px rgba(26, 67, 43, .055);
            margin-bottom: 1.4rem;
        }

        /* Hero */
        .hero-copy-wrap {
            padding: 3.1rem 0 2.7rem;
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .42rem .78rem;
            border-radius: 999px;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: .82rem;
            font-weight: 720;
            margin-bottom: 1.3rem;
        }

        .hero-title {
            max-width: 620px;
            color: var(--text);
            font-size: clamp(2.8rem, 5.2vw, 4.65rem);
            line-height: 1.08;
            font-weight: 720;
            letter-spacing: -.065em;
            margin: 0;
        }

        .hero-title .accent { color: var(--green); }

        .hero-copy {
            max-width: 550px;
            margin-top: 1.3rem;
            color: var(--muted);
            font-size: 1.08rem;
            line-height: 1.75;
        }

        .hero-proof {
            display: flex;
            flex-wrap: wrap;
            gap: .75rem 1.1rem;
            margin-top: 1.45rem;
            color: #536059;
            font-size: .86rem;
            font-weight: 600;
        }

        .hero-proof span::before {
            content: "✓";
            color: var(--green);
            font-weight: 800;
            margin-right: .38rem;
        }

        .hero-expression {
            position: relative;
            overflow: hidden;
            min-height: 455px;
            padding: 2rem;
            border: 1px solid rgba(211, 231, 218, .95);
            border-radius: 2rem;
            background:
                radial-gradient(circle at 95% 0%, rgba(173, 226, 195, .52), transparent 42%),
                linear-gradient(150deg, #FFFFFF 0%, #F1FAF4 100%);
            box-shadow: var(--shadow);
        }

        .hero-expression::after {
            content: "";
            position: absolute;
            right: -5rem;
            bottom: -5rem;
            width: 12rem;
            height: 12rem;
            border-radius: 50%;
            background: rgba(48, 164, 108, .08);
        }

        .expression-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.55rem;
        }

        .expression-label {
            display: inline-flex;
            align-items: center;
            gap: .42rem;
            color: var(--green-dark);
            font-size: .83rem;
            font-weight: 760;
        }

        .expression-type {
            padding: .28rem .58rem;
            border-radius: 999px;
            background: rgba(48, 164, 108, .10);
            color: var(--green-dark);
            font-size: .72rem;
            font-weight: 720;
        }

        .expression-main {
            color: var(--text);
            font-size: clamp(2.05rem, 4vw, 3.15rem);
            line-height: 1.18;
            font-weight: 760;
            letter-spacing: -.035em;
        }

        .expression-pinyin {
            margin-top: .65rem;
            color: var(--green-dark);
            font-size: 1rem;
            font-weight: 620;
        }

        .expression-meaning {
            margin-top: 1.25rem;
            color: var(--text);
            font-size: 1.32rem;
            line-height: 1.5;
            font-weight: 680;
            letter-spacing: -.025em;
        }

        .expression-example {
            position: relative;
            z-index: 1;
            margin-top: 1.45rem;
            padding: 1.05rem 1.1rem;
            border: 1px solid rgba(214, 232, 220, .95);
            border-radius: 1.15rem;
            background: rgba(255, 255, 255, .72);
        }

        .expression-example-title {
            color: var(--muted);
            font-size: .72rem;
            font-weight: 740;
            margin-bottom: .45rem;
        }

        .expression-example-zh {
            color: var(--text);
            font-size: 1rem;
            line-height: 1.6;
            font-weight: 650;
        }

        .expression-example-ko {
            margin-top: .3rem;
            color: var(--muted);
            font-size: .88rem;
            line-height: 1.55;
        }

        /* Sections */
        .section-heading-row {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 3.1rem 0 1rem;
        }

        .section-heading {
            margin: 0;
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 740;
            letter-spacing: -.045em;
        }

        .section-caption {
            color: var(--muted);
            font-size: .88rem;
        }

        .featured-card {
            padding: 1.8rem;
            border: 1px solid var(--line);
            border-radius: 1.65rem;
            background: rgba(255, 255, 255, .88);
            box-shadow: 0 12px 38px rgba(26, 67, 43, .055);
        }

        .featured-kicker {
            color: var(--green-dark);
            font-size: .8rem;
            font-weight: 750;
            margin-bottom: .8rem;
        }

        .featured-title {
            color: var(--text);
            font-size: 1.65rem;
            line-height: 1.38;
            font-weight: 740;
            letter-spacing: -.038em;
        }

        .featured-zh {
            margin-top: .55rem;
            color: var(--green-dark);
            font-size: 1.03rem;
            line-height: 1.6;
        }

        .featured-summary {
            margin-top: .9rem;
            color: var(--muted);
            font-size: .95rem;
            line-height: 1.68;
        }

        .featured-metrics {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .7rem;
            margin-top: 1.15rem;
        }

        .metric-box {
            padding: .85rem .85rem;
            border-radius: 1rem;
            background: #F5F9F6;
        }

        .metric-label {
            color: var(--muted);
            font-size: .72rem;
            font-weight: 650;
        }

        .metric-value {
            margin-top: .18rem;
            color: var(--text);
            font-size: .98rem;
            font-weight: 730;
        }

        .topic-card {
            padding: 1.15rem 1.05rem;
            min-height: 8.2rem;
            border: 1px solid var(--line);
            border-radius: 1.3rem;
            background: rgba(255, 255, 255, .82);
            transition: transform .15s ease, box-shadow .15s ease;
        }

        .topic-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(26, 67, 43, .07);
        }

        .topic-icon { font-size: 1.45rem; }
        .topic-name { margin-top: .8rem; font-size: 1rem; font-weight: 720; }
        .topic-count { margin-top: .22rem; color: var(--muted); font-size: .78rem; }

        .article-card {
            padding: 1.35rem 1.4rem;
            border: 1px solid var(--line);
            border-radius: 1.35rem;
            background: rgba(255, 255, 255, .88);
            margin-bottom: .75rem;
            transition: transform .15s ease, box-shadow .15s ease;
        }

        .article-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 34px rgba(26, 67, 43, .07);
        }

        .meta { color: var(--muted); font-size: .84rem; line-height: 1.5; }
        .article-title { margin: .55rem 0 .35rem; font-size: 1.2rem; line-height: 1.42; font-weight: 690; letter-spacing: -.03em; }
        .article-zh { color: var(--green-dark); font-size: .98rem; line-height: 1.55; }

        .badge {
            display: inline-block;
            padding: .28rem .62rem;
            border-radius: 999px;
            margin: 0 .25rem .3rem 0;
            background: var(--green-soft);
            color: var(--green-dark);
            font-size: .75rem;
            font-weight: 690;
        }

        .surface {
            padding: 1.45rem 1.5rem;
            border: 1px solid var(--line);
            border-radius: 1.4rem;
            background: var(--white);
            box-shadow: 0 8px 30px rgba(26, 67, 43, .045);
        }

        .sentence-box {
            padding: 1.15rem 1.2rem;
            border: 1px solid var(--line);
            border-radius: 1.1rem;
            background: #FFFFFF;
            margin-bottom: .8rem;
        }
        .sentence-zh { font-size: 1.16rem; line-height: 1.85; font-weight: 600; }
        .sentence-pinyin { color: var(--green-dark); line-height: 1.7; margin-top: .18rem; }
        .sentence-ko { color: var(--muted); line-height: 1.7; margin-top: .2rem; }

        .empty {
            padding: 3rem 1.5rem;
            text-align: center;
            border: 1px dashed var(--line);
            border-radius: 1.4rem;
            color: var(--muted);
            background: rgba(255,255,255,.72);
        }

        .stat-number { font-size: 2rem; font-weight: 700; color: var(--green-dark); letter-spacing: -.04em; }

        /* Buttons */
        div.stButton > button,
        div.stDownloadButton > button,
        a[data-testid="stLinkButton"] {
            border-radius: 999px !important;
            border: 1px solid var(--line) !important;
            font-weight: 650 !important;
            min-height: 2.75rem;
            transition: all .15s ease !important;
        }

        div.stButton > button:hover {
            border-color: #BBDAC6 !important;
            color: var(--green-dark) !important;
            transform: translateY(-1px);
        }

        div.stButton > button[kind="primary"],
        div.stDownloadButton > button[kind="primary"] {
            background: linear-gradient(145deg, #36B875, #27985F) !important;
            border-color: transparent !important;
            color: #fff !important;
            box-shadow: 0 9px 22px rgba(48, 164, 108, .19) !important;
        }

        div.stButton > button[kind="primary"]:hover {
            color: #fff !important;
            box-shadow: 0 12px 26px rgba(48, 164, 108, .26) !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border-color: var(--line) !important;
            background: #fff !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--green-dark) !important; }

        @media (max-width: 900px) {
            .block-container { padding-top: 5rem !important; }
            .hero-copy-wrap { padding: 2.1rem 0 1.2rem; }
            .hero-expression { min-height: auto; margin-top: .6rem; }
            .featured-metrics { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
