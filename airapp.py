import os
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

st.set_page_config(
    page_title="Airline Profitability System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────────────────────
BG_BASE   = "#f0f4ff"
BG_MESH_A = "rgba(167, 139, 250, 0.13)"
BG_MESH_B = "rgba(125, 211, 252, 0.11)"

GLASS_BG     = "rgba(255,255,255,0.62)"
GLASS_BORDER = "rgba(255,255,255,0.90)"
GLASS_BLUR   = "blur(22px)"

INK       = "#1e293b"
INK_SOFT  = "#334155"
INK_MUTED = "#64748b"

ACCENT    = "#818cf8"
ACCENT_DK = "#6366f1"
ACCENT_LT = "#eef2ff"
ACCENT_2  = "#a78bfa"

COLOR_GREEN  = "#059669"
COLOR_YELLOW = "#d97706"
COLOR_ORANGE = "#ea580c"
COLOR_PINK   = "#e11d48"

CHART_EXPAND   = "#93c5fd"
CHART_MAINTAIN = "#6ee7b7"
CHART_OPTIMIZE = "#fcd34d"
CHART_ORANGE   = "#fcd34d"
CHART_DROP     = "#fca5a5"
CHART_NEUTRAL  = [
    "#c4b5fd", "#bfdbfe", "#bae6fd", "#ddd6fe",
    "#fecdd3", "#fde68a", "#bbf7d0", "#cbd5e1",
]

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — Liquid Glass Pastel · Professional Edition
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,300;1,9..144,400&display=swap');

:root {{
    --bg-base: {BG_BASE};
    --glass-bg: {GLASS_BG};
    --glass-border: {GLASS_BORDER};
    --glass-blur: {GLASS_BLUR};
    --ink: {INK};
    --ink-soft: {INK_SOFT};
    --ink-muted: {INK_MUTED};
    --accent: {ACCENT};
    --accent-dk: {ACCENT_DK};
    --accent-lt: {ACCENT_LT};
    --accent-2: {ACCENT_2};
    --radius-sm: 12px;
    --radius-md: 18px;
    --radius-lg: 24px;
    --radius-xl: 32px;
    --shadow-sm: 0 4px 16px rgba(99,102,241,0.06), 0 1px 4px rgba(15,23,42,0.04);
    --shadow-md: 0 12px 36px rgba(99,102,241,0.10), 0 4px 12px rgba(15,23,42,0.06);
    --shadow-lg: 0 24px 56px rgba(99,102,241,0.14), 0 8px 24px rgba(15,23,42,0.08);
    --shadow-glow: 0 0 0 1px rgba(129,140,248,0.14), 0 16px 40px rgba(129,140,248,0.18);
    --motion-fast: 200ms cubic-bezier(.25,.8,.25,1);
    --motion-med: 320ms cubic-bezier(.25,.8,.25,1);
    --motion-slow: 480ms cubic-bezier(.25,.8,.25,1);
}}

/* ── Keyframes ── */
@keyframes floatIn {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0);    }}
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0);   }}
}}
@keyframes driftGlow {{
    0%,100% {{ transform: translate3d(0,0,0) rotate(-8deg); }}
    50%     {{ transform: translate3d(0,-6px,0) rotate(-6deg); }}
}}
@keyframes orbFloat1 {{
    0%,100% {{ transform: translate(0,0) scale(1); }}
    33%     {{ transform: translate(18px,-12px) scale(1.04); }}
    66%     {{ transform: translate(-10px,8px) scale(0.97); }}
}}
@keyframes orbFloat2 {{
    0%,100% {{ transform: translate(0,0) scale(1); }}
    40%     {{ transform: translate(-16px,14px) scale(1.06); }}
    70%     {{ transform: translate(12px,-8px) scale(0.96); }}
}}
@keyframes orbFloat3 {{
    0%,100% {{ transform: translate(0,0) scale(1); }}
    30%     {{ transform: translate(10px,16px) scale(1.03); }}
    60%     {{ transform: translate(-14px,-10px) scale(0.98); }}
}}
@keyframes badgePop {{
    0%   {{ transform: scale(0.85); opacity:0; }}
    60%  {{ transform: scale(1.05); }}
    100% {{ transform: scale(1);   opacity:1; }}
}}
@keyframes shimmerSlide {{
    0%   {{ left: -100%; }}
    100% {{ left: 150%;  }}
}}

/* ── Global fonts ── */
html, body, [class*="css"] {{
    font-family: 'Sora', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

/* ── App background ── */
.stApp {{
    min-height: 100vh;
    background:
        radial-gradient(circle at 12% 15%, rgba(167,139,250,0.16) 0, transparent 28%),
        radial-gradient(circle at 88% 12%, rgba(125,211,252,0.13) 0, transparent 26%),
        radial-gradient(circle at 55% 88%, rgba(253,186,116,0.10) 0, transparent 30%),
        radial-gradient(circle at 78% 55%, rgba(196,181,253,0.11) 0, transparent 24%),
        linear-gradient(160deg, #f5f7ff 0%, #eef2ff 40%, #f0fafe 75%, #f5f7ff 100%);
    background-attachment: fixed;
}}

/* ── Floating orb 1 ── */
.stApp::before {{
    content: "";
    position: fixed;
    top: -100px; left: -100px;
    width: 450px; height: 450px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%);
    animation: orbFloat1 18s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}}

/* ── Floating orb 2 ── */
.stApp::after {{
    content: "";
    position: fixed;
    bottom: -80px; right: -80px;
    width: 380px; height: 380px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(125,211,252,0.12) 0%, transparent 70%);
    animation: orbFloat2 22s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}}

.main .block-container {{
    max-width: 1300px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    animation: floatIn 500ms ease-out;
    position: relative;
    z-index: 1;
}}

section.main > div {{ background: transparent; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: rgba(255,255,255,0.56) !important;
    border-right: 1px solid rgba(196,181,253,0.22) !important;
    backdrop-filter: blur(26px) saturate(1.8) !important;
    -webkit-backdrop-filter: blur(26px) saturate(1.8) !important;
    box-shadow: 4px 0 32px rgba(99,102,241,0.07) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--ink-soft) !important; }}

/* ── Sidebar brand ── */
.sidebar-brand {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.55rem;
    color: var(--ink);
    letter-spacing: -0.03em;
    padding: 0.25rem 0 1.1rem 0;
    border-bottom: 1px solid rgba(196,181,253,0.25);
    margin-bottom: 1.1rem;
}}
.sidebar-brand span {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_2});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
    font-family: 'Fraunces', Georgia, serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.025em !important;
    font-weight: 400 !important;
}}

[data-testid="stMarkdownContainer"] p,
.stMarkdown p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown li {{
    color: var(--ink-soft);
    line-height: 1.76;
    font-size: 0.91rem;
}}

/* ── Hero ── */
.hero {{
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.4rem;
    border-radius: var(--radius-xl);
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.2rem;
    background: linear-gradient(140deg,
        rgba(255,255,255,0.72) 0%,
        rgba(238,242,255,0.60) 50%,
        rgba(255,255,255,0.52) 100%);
    border: 1px solid rgba(255,255,255,0.92);
    backdrop-filter: blur(28px) saturate(1.6);
    -webkit-backdrop-filter: blur(28px) saturate(1.6);
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.80);
    transition: box-shadow var(--motion-med), transform var(--motion-med);
}}
.hero:hover {{
    box-shadow: var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.85);
    transform: translateY(-2px);
}}
.hero::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.90) 50%, transparent 100%);
}}
.hero::after {{
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(196,181,253,0.22) 0%, transparent 70%);
    animation: orbFloat3 12s ease-in-out infinite;
    pointer-events: none;
}}
.hero-left, .hero-badge, .hero-glyph {{ position: relative; z-index: 1; }}
.hero-left {{ flex: 1; min-width: 0; }}
.hero-eyebrow {{
    font-size: 0.63rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 0.5rem;
}}
.hero h1 {{
    margin: 0 0 0.4rem 0 !important;
    font-size: 2.2rem !important;
    line-height: 1.15 !important;
}}
.hero p {{
    margin: 0;
    color: var(--ink-muted) !important;
    font-size: 0.88rem;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.62rem 1.1rem;
    border-radius: 999px;
    border: 1px solid rgba(129,140,248,0.22);
    background: linear-gradient(135deg, rgba(255,255,255,0.72), rgba(238,242,255,0.60));
    color: var(--accent-dk);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    box-shadow: 0 4px 16px rgba(129,140,248,0.12);
    transition: transform var(--motion-fast), box-shadow var(--motion-fast);
    animation: badgePop 600ms ease-out 200ms both;
    white-space: nowrap;
}}
.hero-badge:hover {{
    transform: translateY(-3px) scale(1.03);
    box-shadow: 0 12px 28px rgba(129,140,248,0.22);
}}
.hero-glyph {{
    font-size: 3.2rem;
    opacity: 0.22;
    animation: driftGlow 5s ease-in-out infinite;
    filter: drop-shadow(0 4px 12px rgba(129,140,248,0.18));
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(160deg,
        rgba(255,255,255,0.78) 0%,
        rgba(238,242,255,0.55) 100%) !important;
    border: 1px solid rgba(255,255,255,0.92) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(20px) saturate(1.5) !important;
    -webkit-backdrop-filter: blur(20px) saturate(1.5) !important;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.80) !important;
    padding: 1.1rem 1.2rem !important;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast) !important;
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::after {{
    content: "";
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.32), transparent);
    transition: left var(--motion-slow);
    pointer-events: none;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: var(--shadow-md), 0 0 0 1px rgba(129,140,248,0.12), inset 0 1px 0 rgba(255,255,255,0.88) !important;
}}
[data-testid="metric-container"]:hover::after {{
    left: 150%;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.13em !important;
    color: var(--accent) !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
    color: var(--ink) !important;
    font-size: 2.0rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    font-family: 'Sora', sans-serif !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.3rem;
    background: rgba(255,255,255,0.52);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 20px;
    padding: 0.38rem;
    backdrop-filter: blur(18px) saturate(1.4);
    box-shadow: var(--shadow-sm);
}}
.stTabs [data-baseweb="tab"] {{
    height: 44px;
    padding: 0 1.1rem !important;
    border-radius: 14px !important;
    color: var(--ink-soft) !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    background: transparent !important;
    transition: background var(--motion-fast), color var(--motion-fast), transform var(--motion-fast) !important;
    letter-spacing: 0.01em;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(255,255,255,0.78) !important;
    color: var(--accent-dk) !important;
    transform: translateY(-1px) !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(238,242,255,0.70)) !important;
    color: var(--accent-dk) !important;
    box-shadow: 0 6px 18px rgba(99,102,241,0.12), inset 0 0 0 1px rgba(129,140,248,0.18) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem; }}

/* ── Section headings ── */
.section-hd {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}}
.section-sub {{
    font-size: 0.83rem;
    color: var(--ink-muted);
    margin: 0 0 1.2rem 0;
    line-height: 1.6;
}}

/* ── Divider label ── */
.divider-label {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.6rem 0 1.1rem 0;
    font-size: 0.63rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--accent);
}}
.divider-label::before, .divider-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(129,140,248,0.22), transparent);
}}

/* ── Info box ── */
.info-box {{
    background: linear-gradient(160deg,
        rgba(255,255,255,0.82) 0%,
        rgba(238,242,255,0.65) 100%);
    border: 1px solid rgba(196,181,253,0.22);
    border-radius: var(--radius-md);
    padding: 1rem 1.15rem;
    color: var(--ink-soft);
    line-height: 1.78;
    box-shadow: var(--shadow-sm);
    font-size: 0.88rem;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast);
}}
.info-box:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}}

/* ── Pills ── */
.pill {{
    display: inline-block;
    padding: 0.26rem 0.75rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border: 1px solid transparent;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast);
    cursor: default;
}}
.pill:hover {{ transform: scale(1.06); }}
.pill-expand   {{ background: rgba(59,130,246,0.12); color: #1d4ed8; border-color: rgba(59,130,246,0.22); }}
.pill-maintain {{ background: rgba(16,185,129,0.12); color: #047857; border-color: rgba(16,185,129,0.22); }}
.pill-optimize {{ background: rgba(245,158,11,0.12); color: #b45309; border-color: rgba(245,158,11,0.22); }}
.pill-drop     {{ background: rgba(239,68,68,0.12);  color: #b91c1c; border-color: rgba(239,68,68,0.20);  }}

/* ── Result card ── */
.result-card {{
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.6rem;
    margin: 1.2rem 0;
    border: 1px solid rgba(255,255,255,0.94);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(18px) saturate(1.4);
    -webkit-backdrop-filter: blur(18px) saturate(1.4);
    animation: fadeUp 400ms ease-out;
    transition: transform var(--motion-med), box-shadow var(--motion-med);
}}
.result-card:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}}
.result-expand   {{ background: linear-gradient(140deg, rgba(219,234,254,0.70), rgba(255,255,255,0.72)); border-left: 4px solid {CHART_EXPAND};   }}
.result-maintain {{ background: linear-gradient(140deg, rgba(209,250,229,0.70), rgba(255,255,255,0.72)); border-left: 4px solid {CHART_MAINTAIN}; }}
.result-optimize {{ background: linear-gradient(140deg, rgba(254,243,199,0.70), rgba(255,255,255,0.72)); border-left: 4px solid {CHART_OPTIMIZE}; }}
.result-drop     {{ background: linear-gradient(140deg, rgba(254,226,226,0.70), rgba(255,255,255,0.72)); border-left: 4px solid {CHART_DROP};     }}

/* ── Form inputs ── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.03em !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {{
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(196,181,253,0.28) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--ink) !important;
    min-height: 44px !important;
    box-shadow: none !important;
    transition: border-color var(--motion-fast), box-shadow var(--motion-fast), transform var(--motion-fast) !important;
    font-family: 'Sora', sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:hover,
.stNumberInput input:hover {{
    border-color: rgba(129,140,248,0.42) !important;
    transform: translateY(-1px) !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {{
    border-color: rgba(99,102,241,0.55) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    transform: translateY(-1px) !important;
}}

/* ── Form card ── */
[data-testid="stForm"] {{
    background: linear-gradient(160deg,
        rgba(255,255,255,0.68) 0%,
        rgba(238,242,255,0.52) 100%) !important;
    border: 1px solid rgba(255,255,255,0.90) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.5rem 1.6rem 1.8rem !important;
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.94) !important;
    backdrop-filter: blur(20px) saturate(1.5) !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button,
.stButton > button {{
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    border: none !important;
    font-family: 'Sora', sans-serif !important;
    letter-spacing: 0.03em !important;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast) !important;
    position: relative;
    overflow: hidden;
}}
[data-testid="stFormSubmitButton"] > button {{
    width: 100% !important;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_DK}) !important;
    box-shadow: 0 10px 28px rgba(99,102,241,0.28), 0 4px 10px rgba(99,102,241,0.18) !important;
    color: white !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 0 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 38px rgba(99,102,241,0.34), 0 6px 16px rgba(99,102,241,0.22) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform: translateY(0) scale(0.98) !important;
}}
.stButton > button {{
    background: rgba(255,255,255,0.82) !important;
    color: var(--ink) !important;
    border: 1px solid rgba(196,181,253,0.22) !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stButton > button:hover {{
    background: rgba(255,255,255,0.96) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background: rgba(255,255,255,0.62) !important;
    border: 1px solid rgba(255,255,255,0.88) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
    backdrop-filter: blur(18px) !important;
    transition: transform var(--motion-med), box-shadow var(--motion-med) !important;
}}
[data-testid="stDataFrame"]:hover {{
    transform: translateY(-4px) !important;
    box-shadow: var(--shadow-md) !important;
}}
[data-testid="stDataFrame"] [role="grid"] {{ background: transparent !important; }}
[data-testid="stDataFrame"] div,
[data-testid="stDataFrame"] span {{ color: var(--ink) !important; }}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background: rgba(238,242,255,0.60) !important;
    color: var(--accent-dk) !important;
    font-weight: 700 !important;
    font-size: 0.74rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(196,181,253,0.18) !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
    border-bottom: 1px solid rgba(226,232,240,0.45) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: linear-gradient(160deg,
        rgba(255,255,255,0.65) 0%,
        rgba(238,242,255,0.50) 100%) !important;
    border: 1px solid rgba(255,255,255,0.92) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-sm) !important;
    backdrop-filter: blur(16px) !important;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast) !important;
}}
[data-testid="stExpander"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}}
[data-testid="stExpander"] summary p {{
    color: var(--ink) !important;
    font-weight: 600 !important;
}}

/* ── Charts ── */
[data-testid="stPyplot"] {{
    background: linear-gradient(160deg,
        rgba(255,255,255,0.64) 0%,
        rgba(238,242,255,0.50) 100%);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: var(--radius-lg);
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(16px);
    transition: transform var(--motion-med), box-shadow var(--motion-med);
}}
[data-testid="stPyplot"]:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{ border-radius: var(--radius-md) !important; }}

/* ── HR ── */
hr {{
    border: none !important;
    border-top: 1px solid rgba(196,181,253,0.22) !important;
    margin: 1.4rem 0 !important;
}}

/* ── Column label ── */
.col-label {{
    font-size: 0.67rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}
.col-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(129,140,248,0.22), transparent);
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: rgba(129,140,248,0.22);
    border-radius: 999px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(129,140,248,0.42); }}

/* ── Selection ── */
::selection {{
    background: rgba(129,140,248,0.20);
    color: var(--ink);
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  DECISION CONFIG  (unchanged)
# ─────────────────────────────────────────────────────────────
DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_ORANGE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

# ─────────────────────────────────────────────────────────────
#  CHART HELPERS
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("none")
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=INK_MUTED, labelsize=8.5, length=0)
    ax.xaxis.label.set_color(INK_MUTED)
    ax.yaxis.label.set_color(INK_MUTED)
    ax.title.set_color(INK)
    ax.title.set_fontsize(11.5)
    ax.title.set_fontweight("bold")
    ax.grid(axis="y", color="#e2e8f8", linewidth=0.7, linestyle="-", alpha=0.85)
    ax.set_axisbelow(True)
    return fig, ax

def col_seq(labels):
    return [DECISION_COLORS.get(l, "#94a3b8") for l in labels]

def soften_bars(bars, alpha=0.88):
    for bar in bars:
        bar.set_alpha(alpha)
        bar.set_linewidth(0)
    return bars

# ─────────────────────────────────────────────────────────────
#  PATHS  (unchanged)
# ─────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(__file__)
DATA_PATH    = os.path.join(BASE_DIR, "airline_route_profitability.csv")
MODEL1_PATH  = os.path.join(BASE_DIR, "model_with_revenue.pkl")
MODEL2_PATH  = os.path.join(BASE_DIR, "model_without_revenue.pkl")
MODEL3_PATH  = os.path.join(BASE_DIR, "model_preoperational.pkl")
X1_COLS_PATH = os.path.join(BASE_DIR, "x1_columns.pkl")
X2_COLS_PATH = os.path.join(BASE_DIR, "x2_columns.pkl")
X3_COLS_PATH = os.path.join(BASE_DIR, "x3_columns.pkl")

# ─────────────────────────────────────────────────────────────
#  DATA & MODEL LOADING  (logic unchanged)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Flight_Date"] = pd.to_datetime(df["Flight_Date"])
    for col in ["Ancillary_Revenue", "Catering_Cost", "Handling_Cost"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    ph = df["Profit"].quantile(0.75)
    mh = df["Profit_Margin"].quantile(0.75)
    lh = df["Load_Factor"].quantile(0.75)
    mm = df["Profit_Margin"].median()
    lm = df["Load_Factor"].median()

    def classify(row):
        if row["Profit"] >= ph and row["Profit_Margin"] >= mh and row["Load_Factor"] >= lh:
            return "Expand"
        elif row["Profit"] <= 0:
            return "Drop"
        elif row["Profit_Margin"] < mm or row["Load_Factor"] < lm:
            return "Optimize"
        else:
            return "Maintain"

    df["Route_Decision"] = df.apply(classify, axis=1)
    return df

@st.cache_resource
def load_artifacts():
    return (
        joblib.load(MODEL1_PATH), joblib.load(MODEL2_PATH), joblib.load(MODEL3_PATH),
        joblib.load(X1_COLS_PATH), joblib.load(X2_COLS_PATH), joblib.load(X3_COLS_PATH)
    )

def prepare_input(input_df, training_columns):
    enc = pd.get_dummies(input_df, drop_first=True)
    return enc.reindex(columns=training_columns, fill_value=0)

# ─────────────────────────────────────────────────────────────
#  LOAD  (unchanged)
# ─────────────────────────────────────────────────────────────
df = load_data()
model1, model2, model3, X1_columns, X2_columns, X3_columns = load_artifacts()

# ─────────────────────────────────────────────────────────────
#  PRE-COMPUTED DATA  (unchanged)
# ─────────────────────────────────────────────────────────────
comparison = pd.DataFrame({
    "Model":    ["With revenue variables", "Without revenue variables", "Only pre-operational features"],
    "Accuracy": [0.879624, 0.837618, 0.721003],
    "Macro F1": [0.879616, 0.838726, 0.729150],
})

df_sorted = df.sort_values(["Route", "Flight_Date"]).copy()
df_sorted["Prev_Decision"] = df_sorted.groupby("Route")["Route_Decision"].shift(1)
df_sorted["Changed"] = df_sorted["Route_Decision"] != df_sorted["Prev_Decision"]
route_switches = (
    df_sorted.groupby("Route")["Changed"].sum()
    .sort_values(ascending=False).reset_index()
    .rename(columns={"Changed": "Decision Switches"})
)
route_variability = (
    df.groupby("Route")["Route_Decision"].nunique()
    .sort_values(ascending=False).reset_index()
    .rename(columns={"Route_Decision": "Unique States"})
)

if "pred_result" not in st.session_state:
    st.session_state.pred_result = None

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Airline<span> Route Intelligence</span> ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.68rem;color:{ACCENT};margin-bottom:16px;"
        "font-weight:700;letter-spacing:0.13em;text-transform:uppercase'>Filter View</p>",
        unsafe_allow_html=True,
    )
    route_opts    = ["All"] + sorted(df["Route"].dropna().unique().tolist())
    aircraft_opts = ["All"] + sorted(df["Aircraft_Type"].dropna().unique().tolist())
    season_opts   = ["All"] + sorted(df["Season"].dropna().unique().tolist())
    decision_opts = ["All"] + sorted(df["Route_Decision"].dropna().unique().tolist())

    sel_route    = st.selectbox("✈  Route",         route_opts)
    sel_aircraft = st.selectbox("🛩  Aircraft Type", aircraft_opts)
    sel_season   = st.selectbox("🌤  Season",        season_opts)
    sel_decision = st.selectbox("🏷  Decision",      decision_opts)

    st.markdown("---")
    st.markdown(f"""
    <p style='font-size:0.66rem;color:{ACCENT};font-weight:700;letter-spacing:0.13em;
    text-transform:uppercase;margin-bottom:12px'>Decision labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:0.82rem;color:{INK_SOFT}'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-expand'>Expand</span>High profit &amp; demand
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-maintain'>Maintain</span>Stable performer
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-optimize'>Optimize</span>Room to improve
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-drop'>Drop</span>Losing money
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FILTER  (logic unchanged)
# ─────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_route    != "All": fdf = fdf[fdf["Route"]          == sel_route]
if sel_aircraft != "All": fdf = fdf[fdf["Aircraft_Type"]  == sel_aircraft]
if sel_season   != "All": fdf = fdf[fdf["Season"]         == sel_season]
if sel_decision != "All": fdf = fdf[fdf["Route_Decision"] == sel_decision]

# ─────────────────────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-left">
    <div class="hero-eyebrow">✦ Route Intelligence Platform</div>
    <h1>Airline Profitability System Dashboard</h1>
    <p>Sample airline dataset · for analysis &amp; demonstration only</p>
  </div>
  <div class="hero-badge">⚡ ML-Powered Decisions</div>
  <div class="hero-glyph">✈</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Overview",
    "🔍  Performance Drivers",
    "🗺  Route Actions",
    "📈  Route Stability",
    "🤖  Prediction Tool",
])

# ── TAB 1 · OVERVIEW ─────────────────────────────────────────
with tab1:
    n          = len(fdf)
    avg_profit = fdf["Profit"].mean()
    avg_load   = fdf["Load_Factor"].mean()
    n_routes   = fdf["Route"].nunique()

    expand_pct   = (fdf["Route_Decision"] == "Expand").mean()   * 100 if n else 0
    maintain_pct = (fdf["Route_Decision"] == "Maintain").mean() * 100 if n else 0
    optimize_pct = (fdf["Route_Decision"] == "Optimize").mean() * 100 if n else 0
    drop_pct     = (fdf["Route_Decision"] == "Drop").mean()     * 100 if n else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Flights",   f"{n:,}")
    c2.metric("Unique Routes",   f"{n_routes}")
    c3.metric("Average Profit",  f"${avg_profit:,.0f}")
    c4.metric("Avg Load Factor", f"{avg_load:.0%}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="divider-label">Composition</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<p class="section-hd">Decision mix</p>', unsafe_allow_html=True)
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
              "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
        fig, ax = clean_fig((5, 4.8))
        wedges, texts, autotexts = ax.pie(
            dc.values, labels=dc.index, autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index], startangle=90,
            wedgeprops={"linewidth":3,"edgecolor":"white"},
            textprops={"color":INK,"fontsize":9.5},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8.5); at.set_color(INK_SOFT); at.set_fontweight("bold")
        ax.set_title("Share of Flights by Decision", pad=14)
        st.pyplot(fig)

    with right:
        st.markdown('<p class="section-hd">Average metrics by decision</p>', unsafe_allow_html=True)
        summary = (
            fdf.groupby("Route_Decision")[["Profit","Profit_Margin","Load_Factor"]]
            .mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .round(3).reset_index()
            .rename(columns={
                "Route_Decision":"Decision","Profit":"Avg Profit ($)",
                "Profit_Margin":"Avg Margin","Load_Factor":"Avg Load Factor",
            })
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="info-box">
          <strong>How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong>Expand</strong> routes should have the highest values across all three columns.
        </div>""", unsafe_allow_html=True)

# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown('<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        apd = (fdf.groupby("Route_Decision")["Profit"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        fig, ax = clean_fig((6, 4))
        colors = col_seq(apd.index.tolist())
        bars = ax.bar(apd.index, apd.values, color=colors, width=0.55)
        soften_bars(bars)
        mn, mx = min(apd.values.min(), 0), apd.values.max()
        pad = (mx - mn) * 0.10 if mx != mn else 1
        for bar, h in zip(bars, apd.values):
            x_pos = bar.get_x() + bar.get_width()/2
            if h >= 0:
                ty = h + pad; va = "bottom"; txt_color = INK_MUTED
            else:
                ty = h * 0.5; va = "center"; txt_color = "white"
            ax.text(x_pos, ty, f"${h:,.0f}",
                    ha="center", va=va, fontsize=8, color=txt_color, fontweight="700")
        ax.set_ylabel("Average Profit ($)")
        ax.set_title("Average Profit by Decision")
        st.pyplot(fig)

    with right:
        ald = (fdf.groupby("Route_Decision")["Load_Factor"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        fig, ax = clean_fig((6, 4))
        colors = col_seq(ald.index.tolist())
        bars = ax.bar(ald.index, ald.values, color=colors, width=0.55)
        soften_bars(bars)
        for bar, h in zip(bars, ald.values):
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.02, f"{h:.0%}",
                    ha="center", va="bottom", fontsize=8, color=INK_MUTED, fontweight="700")
        ax.set_ylabel("Average Seat Occupancy")
        ax.set_title("Seat Occupancy by Decision")
        st.pyplot(fig)

    st.markdown('<div class="divider-label">Cost breakdown</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Where is the money going?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">The biggest cost components across all filtered flights.</p>', unsafe_allow_html=True)

    cost_cols = [
        "Fuel_Cost","Maintenance_Cost","Crew_Cost","Depreciation_Cost","Insurance_Cost",
        "Airport_Fees","Catering_Cost","Handling_Cost","Navigation_Fees",
        "Sales_Distribution_Cost","Passenger_Service_Cost","Overhead_Cost",
        "Marketing_Cost","IT_Systems_Cost",
    ]
    avail_costs = [c for c in cost_cols if c in fdf.columns]
    cost_means  = fdf[avail_costs].mean().sort_values(ascending=True).tail(8)
    label_map = {
        "Fuel_Cost":"Fuel","Maintenance_Cost":"Maintenance","Crew_Cost":"Crew",
        "Depreciation_Cost":"Depreciation","Insurance_Cost":"Insurance",
        "Airport_Fees":"Airport Fees","Catering_Cost":"Catering","Handling_Cost":"Handling",
        "Navigation_Fees":"Navigation","Sales_Distribution_Cost":"Sales & Dist.",
        "Passenger_Service_Cost":"Pax Service","Overhead_Cost":"Overhead",
        "Marketing_Cost":"Marketing","IT_Systems_Cost":"IT Systems",
    }
    cost_means.index = [label_map.get(i, i) for i in cost_means.index]
    fig, ax = clean_fig((9, 4))
    nc = len(cost_means)
    neutral_cols = CHART_NEUTRAL[:nc]
    bars = ax.barh(cost_means.index, cost_means.values, color=neutral_cols, height=0.55)
    soften_bars(bars)
    mx_c = cost_means.max()
    for bar, w in zip(bars, cost_means.values):
        ax.text(w + mx_c*0.015, bar.get_y() + bar.get_height()/2, f"${w:,.0f}",
                va="center", fontsize=8, color=INK_MUTED, fontweight="700")
    ax.set_xlabel("Average Cost per Flight ($)")
    ax.set_title("Top Cost Drivers")
    ax.grid(axis="x", color="#e2e8f8", linewidth=0.7, linestyle="-", alpha=0.85)
    ax.grid(axis="y", visible=False)
    st.pyplot(fig)

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "Top routes currently classified as Expand</p>", unsafe_allow_html=True)
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route","Profit","Profit_Margin","Load_Factor"]].head(10)
        .rename(columns={"Profit":"Avg Profit ($)","Profit_Margin":"Profit Margin","Load_Factor":"Load Factor"})
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5))
        bars = ax.barh(top.index, top.values, color=CHART_EXPAND, height=0.55)
        soften_bars(bars)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Top 10 Routes")
        ax.grid(axis="x", color="#e2e8f8", linewidth=0.7, linestyle="-", alpha=0.85)
        ax.grid(axis="y", visible=False)
        st.pyplot(fig)

    with right:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5))
        bars = ax.barh(worst.index, worst.values, color=CHART_DROP, height=0.55)
        soften_bars(bars)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Bottom 10 Routes")
        ax.grid(axis="x", color="#e2e8f8", linewidth=0.7, linestyle="-", alpha=0.85)
        ax.grid(axis="y", visible=False)
        st.pyplot(fig)

# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "How many unique routes appear in each category?</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route":"Unique Routes"})
        .set_index("Route_Decision").reindex(ORDER).dropna()
    )
    bc_map = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
              "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
    bc = [bc_map.get(i,"#c4b5fd") for i in urbd.index]
    fig, ax = clean_fig((8, 4))
    vals4 = urbd["Unique Routes"].values.tolist()
    bars = ax.bar(urbd.index, vals4, color=bc, width=0.55)
    soften_bars(bars)
    for bar, h in zip(bars, vals4):
        ax.text(bar.get_x() + bar.get_width()/2, h + max(vals4)*0.05, f"{int(h)}",
                ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
    ax.set_ylabel("Number of Unique Routes")
    ax.set_title("Unique Routes per Decision Category")
    st.pyplot(fig)

    patches = [mpatches.Patch(color=bc_map.get(d,"#c4b5fd"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5,0.5)); fig2.patch.set_alpha(0); ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size":9}, labelcolor=INK)
    st.pyplot(fig2)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)
    fig, ax = clean_fig((8, 3.5))
    x = np.arange(len(comparison)); w = 0.33
    acc_col = "#c4b5fd"
    f1_col  = "#bfdbfe"
    bars1 = ax.bar(x - w/2, comparison["Accuracy"], width=w, color=acc_col, label="Accuracy")
    bars2 = ax.bar(x + w/2, comparison["Macro F1"], width=w, color=f1_col,  label="Macro F1")
    soften_bars(bars1); soften_bars(bars2)
    for bar, acc in zip(bars1, comparison["Accuracy"]):
        ax.text(bar.get_x()+bar.get_width()/2, acc+0.02, f"{acc:.0%}",
                ha="center", fontsize=7.5, color=INK_MUTED, fontweight="700")
    for bar, f1 in zip(bars2, comparison["Macro F1"]):
        ax.text(bar.get_x()+bar.get_width()/2, f1+0.02, f"{f1:.0%}",
                ha="center", fontsize=7.5, color=INK_MUTED, fontweight="700")
    ax.legend(frameon=False, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["Model"], fontsize=8.5, rotation=10)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Model Accuracy & F1 Comparison")
    st.pyplot(fig)

    st.markdown('<div class="divider-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a prediction mode</p>', unsafe_allow_html=True)
    st.markdown("""<div class="info-box">
    <span class='pill pill-maintain'>With Revenue</span>&nbsp; Most accurate — use when you have ticket &amp; ancillary revenue data.<br><br>
    <span class='pill pill-optimize'>Cost-only</span>&nbsp; Good accuracy using cost data only, no revenue figures needed.<br><br>
    <span class='pill pill-expand'>Pre-launch</span>&nbsp; Use before a route launches, when only capacity/demand signals are known.
    </div>""", unsafe_allow_html=True)

    model_choice = st.selectbox(
        "Prediction mode",
        ["With Revenue Variables","Without Revenue Variables","Only Pre-Operational Features"],
        key="model_choice_select",
    )

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<p class="col-label">✈ Flight basics</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown('<p class="col-label">🌍 Route context</p>', unsafe_allow_html=True)
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown('<p class="col-label">💰 Revenue</p>', unsafe_allow_html=True)
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown('<p class="col-label">💸 Cost breakdown</p>', unsafe_allow_html=True)
                fuel_cost               = st.number_input("Fuel Cost ($)",                 min_value=0.0, value=40000.0,  step=1000.0)
                maintenance_cost        = st.number_input("Maintenance Cost ($)",          min_value=0.0, value=15000.0,  step=500.0)
                crew_cost               = st.number_input("Crew Cost ($)",                 min_value=0.0, value=8000.0,   step=500.0)
                depreciation_cost       = st.number_input("Depreciation Cost ($)",         min_value=0.0, value=20000.0,  step=500.0)
                insurance_cost          = st.number_input("Insurance Cost ($)",            min_value=0.0, value=4000.0,   step=250.0)
                airport_fees            = st.number_input("Airport Fees ($)",              min_value=0.0, value=5000.0,   step=250.0)
                catering_cost           = st.number_input("Catering Cost ($)",             min_value=0.0, value=5000.0,   step=250.0)
                handling_cost           = st.number_input("Handling Cost ($)",             min_value=0.0, value=4000.0,   step=250.0)
                navigation_fees         = st.number_input("Navigation Fees ($)",           min_value=0.0, value=3500.0,   step=250.0)
                sales_distribution_cost = st.number_input("Sales & Distribution Cost ($)", min_value=0.0, value=35000.0,  step=500.0)
                passenger_service_cost  = st.number_input("Passenger Service Cost ($)",    min_value=0.0, value=5000.0,   step=250.0)
                overhead_cost           = st.number_input("Overhead Cost ($)",             min_value=0.0, value=25000.0,  step=500.0)
                marketing_cost          = st.number_input("Marketing Cost ($)",            min_value=0.0, value=12000.0,  step=500.0)
                it_systems_cost         = st.number_input("IT Systems Cost ($)",           min_value=0.0, value=3000.0,   step=250.0)

        submitted = st.form_submit_button("✈  Get Route Decision")

    # ── PREDICTION LOGIC  (unchanged) ────────────────────────
    if submitted:
        if model_choice == "With Revenue Variables":
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
                "Ticket_Revenue":ticket_revenue,"Ancillary_Revenue":ancillary_revenue,
            }
            inp=prepare_input(pd.DataFrame([row]),X1_columns)
            pred=model1.predict(inp)[0]; prob=model1.predict_proba(inp)[0]; cls=model1.classes_
        elif model_choice == "Without Revenue Variables":
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
                "Fuel_Cost":fuel_cost,"Maintenance_Cost":maintenance_cost,
                "Crew_Cost":crew_cost,"Depreciation_Cost":depreciation_cost,
                "Insurance_Cost":insurance_cost,"Airport_Fees":airport_fees,
                "Catering_Cost":catering_cost,"Handling_Cost":handling_cost,
                "Navigation_Fees":navigation_fees,"Sales_Distribution_Cost":sales_distribution_cost,
                "Passenger_Service_Cost":passenger_service_cost,"Overhead_Cost":overhead_cost,
                "Marketing_Cost":marketing_cost,"IT_Systems_Cost":it_systems_cost,
            }
            inp=prepare_input(pd.DataFrame([row]),X2_columns)
            pred=model2.predict(inp)[0]; prob=model2.predict_proba(inp)[0]; cls=model2.classes_
        else:
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
            }
            inp=prepare_input(pd.DataFrame([row]),X3_columns)
            pred=model3.predict(inp)[0]; prob=model3.predict_proba(inp)[0]; cls=model3.classes_

        st.session_state.pred_result = {"prediction":pred,"probabilities":prob,"classes":cls}

    # ── RESULT DISPLAY ──
    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]; prob = res["probabilities"]; cls = res["classes"]

        pill_cls   = {"Expand":"pill-expand","Maintain":"pill-maintain",
                      "Optimize":"pill-optimize","Drop":"pill-drop"}
        result_cls = {"Expand":"result-expand","Maintain":"result-maintain",
                      "Optimize":"result-optimize","Drop":"result-drop"}
        text_col   = {"Expand":"#1d4ed8","Maintain":"#047857",
                      "Optimize":"#b45309","Drop":"#b91c1c"}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred,"result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred,"")}' style='font-size:0.68rem'>{pred}</span>
          </div>
          <div style='font-family:"Fraunces",Georgia,serif;font-size:1.75rem;font-weight:600;
                      color:{text_col.get(pred,INK)};margin-bottom:10px;letter-spacing:-0.025em'>
            Suggested Decision: {pred}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-size:0.90rem;line-height:1.76;
                    font-family:"Sora",sans-serif'>
            {explanations.get(pred,"")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision":cls,"Probability":prob})
                   .sort_values("Probability", ascending=False))
        bar_cp = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
                  "Optimize":CHART_OPTIMIZE,"Drop":CHART_DROP}
        fig, ax = clean_fig((6, 3.5))
        bar_colors = [bar_cp.get(d, "#94a3b8") for d in prob_df["Decision"]]
        probs = prob_df["Probability"].tolist()
        bars = ax.bar(prob_df["Decision"], probs, color=bar_colors, width=0.5)
        soften_bars(bars)
        for bar, h in zip(bars, probs):
            ax.text(bar.get_x()+bar.get_width()/2, h + 0.03, f"{h:.0%}",
                    ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("Probability")
        ax.set_title("Model Confidence per Decision")
        st.pyplot(fig)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────
#  FILTERED DATA EXPANDER  (unchanged)
# ─────────────────────────────────────────────────────────────
with st.expander("🗂  Show filtered data"):
    st.dataframe(fdf, use_container_width=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:44px 0 20px;'>
  <div style='display:inline-flex;align-items:center;gap:12px;
              background:rgba(255,255,255,0.60);
              border:1px solid rgba(196,181,253,0.20);
              border-radius:999px;
              padding:0.58rem 1.5rem;
              backdrop-filter:blur(12px);
              box-shadow:0 4px 16px rgba(99,102,241,0.08);
              font-family:"Sora",sans-serif;
              font-size:0.70rem;
              font-weight:600;
              color:{INK_MUTED};
              letter-spacing:0.10em;
              text-transform:uppercase'>
    <span style='color:{ACCENT};font-size:0.85rem'>✦</span>
    Airline Profitability System
    <span style='color:{ACCENT};font-size:0.85rem'>✦</span>
    Built with Streamlit
  </div>
</div>
""", unsafe_allow_html=True)