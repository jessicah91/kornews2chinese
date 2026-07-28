from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --green: #2E7D5A;
            --green-hover: #27694C;
            --green-light: #EEF8F2;
            --green-bg: #F7FBF8;
            --green-border: #DCEEDF;
            --text: #18211C;
            --muted: #68736C;
            --white: #FFFFFF;
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                         "SF Pro Text", "Apple SD Gothic Neo", "Noto Sans KR",
                         "Segoe UI", sans-serif;
        }

        .stApp {
            background: var(--green-bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 5.5rem;
            padding-bottom: 5rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(247, 251, 248, 0.82);
            backdrop-filter: blur(18px);
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        h1, h2, h3 {
            letter-spacing: -0.035em;
            color: var(--text);
        }

        h1 {
            font-weight: 650 !important;
        }

        h2, h3 {
            font-weight: 620 !important;
        }

        p, li, label {
            letter-spacing: -0.01em;
        }

        .brand {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--green);
            letter-spacing: -0.03em;
            padding: .5rem 0 .85rem;
        }

        .hero {
            padding: 4.4rem 2rem 3.9rem;
            text-align: center;
            border: 1px solid var(--green-border);
            border-radius: 30px;
            background:
                radial-gradient(circle at 50% -10%, #DDF3E6 0%, transparent 44%),
                linear-gradient(180deg, #FFFFFF 0%, #F5FBF7 100%);
            margin: 1.5rem 0 2.5rem;
        }

        .eyebrow {
            display: inline-block;
            margin-bottom: 1.1rem;
            color: var(--green);
            font-size: .92rem;
            font-weight: 650;
        }

        .hero-title {
            max-width: 780px;
            margin: 0 auto;
            font-size: clamp(2.15rem, 5.2vw, 4.45rem);
            line-height: 1.12;
            font-weight: 560;
            letter-spacing: -0.055em;
            color: var(--text);
        }

        .hero-copy {
            max-width: 620px;
            margin: 1.25rem auto 0;
            color: var(--muted);
            font-size: 1.08rem;
            line-height: 1.7;
        }

        .section-heading {
            margin: 2.8rem 0 1rem;
            font-size: 1.55rem;
            font-weight: 650;
            letter-spacing: -0.04em;
        }

        .surface {
            padding: 1.45rem 1.5rem;
            border: 1px solid var(--green-border);
            border-radius: 22px;
            background: var(--white);
            box-shadow: 0 8px 30px rgba(35, 77, 56, .045);
        }

        .article-card {
            padding: 1.35rem 1.4rem;
            border: 1px solid var(--green-border);
            border-radius: 20px;
            background: var(--white);
            margin-bottom: .75rem;
            transition: transform .15s ease, box-shadow .15s ease;
        }

        .article-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 34px rgba(35, 77, 56, .07);
        }

        .meta {
            color: var(--muted);
            font-size: .86rem;
            line-height: 1.5;
        }

        .article-title {
            margin: .55rem 0 .35rem;
            font-size: 1.22rem;
            line-height: 1.42;
            font-weight: 640;
            letter-spacing: -0.03em;
        }

        .article-zh {
            color: var(--green);
            font-size: 1rem;
            line-height: 1.55;
        }

        .badge {
            display: inline-block;
            padding: .28rem .62rem;
            border-radius: 999px;
            margin: 0 .25rem .3rem 0;
            background: var(--green-light);
            color: var(--green);
            font-size: .78rem;
            font-weight: 650;
        }

        .sentence-box {
            padding: 1.15rem 1.2rem;
            border: 1px solid var(--green-border);
            border-radius: 18px;
            background: #FFFFFF;
            margin-bottom: .8rem;
        }

        .sentence-zh {
            font-size: 1.16rem;
            line-height: 1.85;
            font-weight: 600;
        }

        .sentence-pinyin {
            color: var(--green);
            line-height: 1.7;
            margin-top: .18rem;
        }

        .sentence-ko {
            color: var(--muted);
            line-height: 1.7;
            margin-top: .2rem;
        }

        .empty {
            padding: 3rem 1.5rem;
            text-align: center;
            border: 1px dashed var(--green-border);
            border-radius: 22px;
            color: var(--muted);
            background: rgba(255,255,255,.7);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 650;
            color: var(--green);
            letter-spacing: -0.04em;
        }

        div.stButton > button,
        div.stDownloadButton > button,
        a[data-testid="stLinkButton"] {
            border-radius: 999px !important;
            border: 1px solid var(--green-border) !important;
            font-weight: 600 !important;
            min-height: 2.65rem;
        }

        div.stButton > button[kind="primary"],
        div.stDownloadButton > button[kind="primary"] {
            background: var(--green) !important;
            border-color: var(--green) !important;
            color: #fff !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: var(--green-hover) !important;
            border-color: var(--green-hover) !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border-color: var(--green-border) !important;
            background: #fff !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--green) !important;
        }


        .expression-card {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.1rem;
            border: 1px solid var(--green-border);
            border-radius: 26px;
            background:
                radial-gradient(circle at 92% 12%, rgba(196, 232, 210, .52), transparent 34%),
                linear-gradient(145deg, #FFFFFF 0%, #F0F9F4 100%);
            box-shadow: 0 12px 38px rgba(35, 77, 56, .055);
        }

        .expression-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.1rem;
        }

        .expression-label {
            display: inline-flex;
            align-items: center;
            min-height: 1.9rem;
            padding: .3rem .72rem;
            border-radius: 999px;
            background: rgba(46, 125, 90, .1);
            color: var(--green);
            font-size: .8rem;
            font-weight: 680;
        }

        .expression-date {
            color: var(--muted);
            font-size: .82rem;
        }

        .expression-main {
            font-size: clamp(2rem, 4.3vw, 3.45rem);
            line-height: 1.15;
            font-weight: 570;
            letter-spacing: -.045em;
            color: var(--text);
        }

        .expression-pinyin {
            margin-top: .58rem;
            color: var(--green);
            font-size: 1.05rem;
            line-height: 1.6;
        }

        .expression-meaning {
            margin-top: .82rem;
            color: var(--text);
            font-size: 1.08rem;
            font-weight: 590;
            line-height: 1.65;
        }

        .expression-example {
            margin-top: 1.45rem;
            padding: 1.15rem 1.2rem;
            border: 1px solid rgba(46, 125, 90, .12);
            border-radius: 17px;
            background: rgba(255, 255, 255, .76);
        }

        .expression-example-title {
            margin-bottom: .42rem;
            color: var(--muted);
            font-size: .78rem;
            font-weight: 650;
        }

        .expression-example-zh {
            font-size: 1.07rem;
            font-weight: 600;
            line-height: 1.7;
        }

        .expression-example-ko {
            margin-top: .25rem;
            color: var(--muted);
            line-height: 1.65;
        }

        .expression-note {
            margin-top: 1.1rem;
            color: var(--muted);
            font-size: .91rem;
            line-height: 1.7;
        }

        @media (max-width: 760px) {
            .block-container {
                padding: .65rem 1rem 4rem;
            }

            .hero {
                padding: 3.2rem 1.15rem 2.9rem;
                border-radius: 24px;
            }

            .hero-copy {
                font-size: .98rem;
            }

            .article-card {
                padding: 1.15rem;
            }

            .expression-card {
                padding: 1.45rem 1.25rem;
                border-radius: 22px;
            }

            .expression-date {
                display: none;
            }

            div[data-testid="column"] {
                min-width: 100% !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
