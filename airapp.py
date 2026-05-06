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
#  THEME TOKENS — Cosmic Character Palette
# ─────────────────────────────────────────────────────────────
BG_BASE      = "#0a0d1a"          # deep navy void — her starfield backdrop
VOID_DARK    = "#060810"
VOID_MID     = "#0e1225"

GLASS_BG     = "rgba(20, 25, 50, 0.65)"
GLASS_BORDER = "rgba(124, 92, 252, 0.28)"
GLASS_BLUR   = "blur(24px)"

INK          = "#e8e4ff"          # near-white with cool violet tint
INK_SOFT     = "#c4b5fd"          # lavender — her hair highlights
INK_MUTED    = "#8b7ec8"          # muted lavender

ACCENT       = "#7c5cfc"          # electric violet — her outfit
ACCENT_DK    = "#5b3fd4"
ACCENT_LT    = "#a78bfa"
ACCENT_2     = "#3b82f6"          # cobalt blue — her collar gems
MAGENTA      = "#e11d78"          # hot magenta — her ribbon bow

COLOR_GREEN  = "#10b981"
COLOR_YELLOW = "#f59e0b"
COLOR_ORANGE = "#f97316"
COLOR_PINK   = "#e11d78"

CHART_EXPAND   = "#3b82f6"        # cobalt
CHART_MAINTAIN = "#10b981"        # teal green
CHART_OPTIMIZE = "#f59e0b"        # amber
CHART_ORANGE   = "#f59e0b"
CHART_DROP     = "#e11d78"        # magenta
CHART_NEUTRAL  = [
    "#7c5cfc", "#3b82f6", "#a78bfa", "#c4b5fd",
    "#e11d78", "#f59e0b", "#10b981", "#64748b",
]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — Cosmic Void · Character-Inspired
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {{
    --bg-base: {BG_BASE};
    --void-dark: {VOID_DARK};
    --void-mid: {VOID_MID};
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
    --magenta: {MAGENTA};
    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 22px;
    --radius-xl: 28px;
    --shadow-sm:  0 4px 20px rgba(124,92,252,0.15), 0 1px 4px rgba(0,0,0,0.40);
    --shadow-md:  0 12px 40px rgba(124,92,252,0.22), 0 4px 16px rgba(0,0,0,0.50);
    --shadow-lg:  0 24px 64px rgba(124,92,252,0.30), 0 8px 32px rgba(0,0,0,0.60);
    --shadow-glow: 0 0 0 1px rgba(124,92,252,0.40), 0 0 32px rgba(124,92,252,0.28), 0 0 64px rgba(59,130,246,0.14);
    --shadow-magenta: 0 0 0 1px rgba(225,29,120,0.35), 0 0 28px rgba(225,29,120,0.22);
    --motion-fast: 180ms cubic-bezier(.25,.8,.25,1);
    --motion-med:  300ms cubic-bezier(.25,.8,.25,1);
    --motion-slow: 500ms cubic-bezier(.25,.8,.25,1);
}}

/* ── Keyframes ── */
@keyframes floatIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0);    }}
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0);    }}
}}
@keyframes orbFloat1 {{
    0%,100% {{ transform: translate(0,0) scale(1); opacity: 0.6; }}
    33%     {{ transform: translate(24px,-16px) scale(1.05); opacity: 0.8; }}
    66%     {{ transform: translate(-12px,10px) scale(0.96); opacity: 0.55; }}
}}
@keyframes orbFloat2 {{
    0%,100% {{ transform: translate(0,0) scale(1); opacity: 0.5; }}
    40%     {{ transform: translate(-20px,18px) scale(1.07); opacity: 0.7; }}
    70%     {{ transform: translate(16px,-10px) scale(0.95); opacity: 0.45; }}
}}
@keyframes orbFloat3 {{
    0%,100% {{ transform: translate(0,0) scale(1); }}
    30%     {{ transform: translate(12px,20px) scale(1.04); }}
    60%     {{ transform: translate(-18px,-12px) scale(0.97); }}
}}
@keyframes pulseGlow {{
    0%,100% {{ box-shadow: 0 0 0 1px rgba(124,92,252,0.25), 0 0 20px rgba(124,92,252,0.12); }}
    50%     {{ box-shadow: 0 0 0 1px rgba(124,92,252,0.55), 0 0 40px rgba(124,92,252,0.30), 0 0 80px rgba(59,130,246,0.12); }}
}}
@keyframes scanLine {{
    0%   {{ top: -4px; opacity: 0; }}
    5%   {{ opacity: 1; }}
    95%  {{ opacity: 0.6; }}
    100% {{ top: 100%; opacity: 0; }}
}}
@keyframes twinkle1 {{
    0%,100% {{ opacity: 0; transform: scale(0.5); }}
    50%     {{ opacity: 1; transform: scale(1); }}
}}
@keyframes twinkle2 {{
    0%,100% {{ opacity: 0; transform: scale(0.3); }}
    40%     {{ opacity: 0.9; transform: scale(1); }}
}}
@keyframes twinkle3 {{
    0%,100% {{ opacity: 0.1; transform: scale(0.6); }}
    60%     {{ opacity: 1; transform: scale(1.1); }}
}}
@keyframes twinkle4 {{
    0%,100% {{ opacity: 0; }}
    70%     {{ opacity: 0.8; }}
}}
@keyframes badgePop {{
    0%   {{ transform: scale(0.8); opacity: 0; }}
    60%  {{ transform: scale(1.06); }}
    100% {{ transform: scale(1);   opacity: 1; }}
}}
@keyframes shimmerSlide {{
    0%   {{ left: -80%; }}
    100% {{ left: 150%; }}
}}
@keyframes borderPulse {{
    0%,100% {{ border-color: rgba(124,92,252,0.25); }}
    50%     {{ border-color: rgba(124,92,252,0.65); }}
}}

/* ── Global fonts ── */
html, body, [class*="css"] {{
    font-family: 'Outfit', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: {INK} !important;
}}

/* ── App background — deep cosmic void ── */
.stApp {{
    min-height: 100vh;
    background:
        radial-gradient(circle at 18% 20%, rgba(124,92,252,0.18) 0, transparent 32%),
        radial-gradient(circle at 82% 15%, rgba(59,130,246,0.14) 0, transparent 28%),
        radial-gradient(circle at 60% 85%, rgba(225,29,120,0.10) 0, transparent 26%),
        radial-gradient(circle at 75% 50%, rgba(167,139,250,0.08) 0, transparent 22%),
        radial-gradient(circle at 30% 70%, rgba(59,130,246,0.09) 0, transparent 24%),
        linear-gradient(160deg, #0a0d1a 0%, #080c1e 35%, #060810 70%, #0a0d1a 100%);
    background-attachment: fixed;
}}

/* ── Floating orb 1 — violet top-left ── */
.stApp::before {{
    content: "";
    position: fixed;
    top: -120px; left: -120px;
    width: 520px; height: 520px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,92,252,0.16) 0%, transparent 70%);
    animation: orbFloat1 20s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}}

/* ── Floating orb 2 — cobalt bottom-right ── */
.stApp::after {{
    content: "";
    position: fixed;
    bottom: -100px; right: -100px;
    width: 440px; height: 440px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.14) 0%, transparent 70%);
    animation: orbFloat2 26s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}}

.main .block-container {{
    max-width: 1300px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    animation: floatIn 550ms ease-out;
    position: relative;
    z-index: 1;
}}

section.main > div {{ background: transparent; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: rgba(10,13,26,0.85) !important;
    border-right: 1px solid rgba(124,92,252,0.22) !important;
    backdrop-filter: blur(28px) saturate(1.6) !important;
    -webkit-backdrop-filter: blur(28px) saturate(1.6) !important;
    box-shadow: 4px 0 40px rgba(124,92,252,0.10) !important;
}}
[data-testid="stSidebar"] * {{ color: {INK_SOFT} !important; }}

/* ── Sidebar brand ── */
.sidebar-brand {{
    font-family: 'Cinzel', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: {INK};
    letter-spacing: 0.06em;
    padding: 0.25rem 0 1.1rem 0;
    border-bottom: 1px solid rgba(124,92,252,0.25);
    margin-bottom: 1.1rem;
    text-transform: uppercase;
}}
.sidebar-brand span {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_2});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
    font-family: 'Cinzel', serif !important;
    color: {INK} !important;
    letter-spacing: 0.04em !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
}}

[data-testid="stMarkdownContainer"] p,
.stMarkdown p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown li {{
    color: {INK_SOFT};
    line-height: 1.78;
    font-size: 0.90rem;
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
    padding: 2rem 2.4rem;
    margin-bottom: 1.4rem;
    background: linear-gradient(140deg,
        rgba(20,25,55,0.82) 0%,
        rgba(12,16,35,0.75) 50%,
        rgba(18,22,50,0.68) 100%);
    border: 1px solid rgba(124,92,252,0.35);
    backdrop-filter: blur(28px) saturate(1.5);
    -webkit-backdrop-filter: blur(28px) saturate(1.5);
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(196,181,253,0.08);
    animation: pulseGlow 4s ease-in-out infinite;
    transition: transform var(--motion-med);
}}
.hero:hover {{
    transform: translateY(-2px);
}}

/* Scan-line sweep */
.hero::before {{
    content: "";
    position: absolute;
    left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(124,92,252,0.0) 15%,
        rgba(196,181,253,0.55) 45%,
        rgba(59,130,246,0.40) 55%,
        rgba(124,92,252,0.0) 85%,
        transparent 100%);
    animation: scanLine 6s linear infinite;
    pointer-events: none;
    z-index: 5;
}}

/* Orb inside hero */
.hero::after {{
    content: "";
    position: absolute;
    top: -70px; right: -70px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.20) 0%, transparent 70%);
    animation: orbFloat3 14s ease-in-out infinite;
    pointer-events: none;
}}

/* Star twinkles inside hero */
.hero-stars::before,
.hero-stars::after {{
    content: "✦";
    position: absolute;
    font-size: 0.4rem;
    color: rgba(196,181,253,0.7);
}}
.hero-star {{
    position: absolute;
    width: 3px; height: 3px;
    border-radius: 50%;
    background: rgba(196,181,253,0.8);
    pointer-events: none;
}}
.hero-star:nth-child(1) {{ top: 18%; left: 45%; animation: twinkle1 3.2s ease-in-out infinite; }}
.hero-star:nth-child(2) {{ top: 70%; left: 62%; animation: twinkle2 4.1s ease-in-out infinite 0.8s; }}
.hero-star:nth-child(3) {{ top: 35%; left: 80%; animation: twinkle3 2.8s ease-in-out infinite 1.4s; width:2px; height:2px; background: rgba(59,130,246,0.9); }}
.hero-star:nth-child(4) {{ top: 82%; left: 30%; animation: twinkle4 3.6s ease-in-out infinite 0.3s; width:4px; height:4px; }}

.hero-left, .hero-badge, .hero-glyph {{ position: relative; z-index: 1; }}
.hero-left {{ flex: 1; min-width: 0; }}
.hero-eyebrow {{
    font-size: 0.60rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: {ACCENT_LT};
    font-weight: 600;
    margin-bottom: 0.6rem;
    font-family: 'Outfit', sans-serif;
}}
.hero h1 {{
    margin: 0 0 0.45rem 0 !important;
    font-size: 1.95rem !important;
    line-height: 1.2 !important;
    text-shadow: 0 0 40px rgba(124,92,252,0.50) !important;
}}
.hero p {{
    margin: 0;
    color: {INK_MUTED} !important;
    font-size: 0.87rem !important;
    font-family: 'Outfit', sans-serif !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-weight: 400 !important;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.62rem 1.1rem;
    border-radius: 999px;
    border: 1px solid rgba(225,29,120,0.45);
    background: linear-gradient(135deg, rgba(225,29,120,0.18), rgba(124,92,252,0.15));
    color: #f472b6;
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'Outfit', sans-serif;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(225,29,120,0.20), 0 0 0 1px rgba(225,29,120,0.18);
    animation: badgePop 700ms ease-out 250ms both;
    white-space: nowrap;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast);
}}
.hero-badge:hover {{
    transform: translateY(-3px) scale(1.04);
    box-shadow: 0 8px 28px rgba(225,29,120,0.35), 0 0 0 1px rgba(225,29,120,0.30);
}}
.hero-glyph {{
    font-size: 3rem;
    opacity: 0.18;
    color: {ACCENT_LT};
    filter: drop-shadow(0 0 16px rgba(124,92,252,0.60));
    animation: orbFloat3 6s ease-in-out infinite;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(160deg,
        rgba(20,25,55,0.82) 0%,
        rgba(14,18,38,0.70) 100%) !important;
    border: 1px solid rgba(124,92,252,0.28) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(20px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(20px) saturate(1.4) !important;
    box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(196,181,253,0.06) !important;
    padding: 1.1rem 1.2rem !important;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast) !important;
    position: relative;
    overflow: hidden;
    animation: borderPulse 5s ease-in-out infinite;
}}
[data-testid="metric-container"]::after {{
    content: "";
    position: absolute;
    top: 0; left: -80%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(196,181,253,0.08), transparent);
    transition: left 0.6s ease;
    pointer-events: none;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: var(--shadow-md), 0 0 0 1px rgba(124,92,252,0.45), inset 0 1px 0 rgba(196,181,253,0.10) !important;
}}
[data-testid="metric-container"]:hover::after {{
    left: 150%;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size: 0.60rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.16em !important;
    color: {ACCENT_LT} !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
    color: {INK} !important;
    font-size: 1.95rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    font-family: 'Cinzel', serif !important;
    text-shadow: 0 0 20px rgba(124,92,252,0.40) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.25rem;
    background: rgba(14,18,38,0.70);
    border: 1px solid rgba(124,92,252,0.22);
    border-radius: 20px;
    padding: 0.35rem;
    backdrop-filter: blur(18px);
    box-shadow: var(--shadow-sm);
}}
.stTabs [data-baseweb="tab"] {{
    height: 42px;
    padding: 0 1.05rem !important;
    border-radius: 14px !important;
    color: {INK_MUTED} !important;
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    background: transparent !important;
    letter-spacing: 0.04em !important;
    transition: background var(--motion-fast), color var(--motion-fast), transform var(--motion-fast) !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(124,92,252,0.14) !important;
    color: {ACCENT_LT} !important;
    transform: translateY(-1px) !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(124,92,252,0.28), rgba(59,130,246,0.20)) !important;
    color: {INK} !important;
    box-shadow: 0 4px 16px rgba(124,92,252,0.22), inset 0 0 0 1px rgba(124,92,252,0.35) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem; }}

/* ── Section headings ── */
.section-hd {{
    font-family: 'Cinzel', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: {INK};
    margin: 0 0 0.3rem 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    text-shadow: 0 0 20px rgba(124,92,252,0.35);
}}
.section-sub {{
    font-size: 0.83rem;
    color: {INK_MUTED};
    margin: 0 0 1.2rem 0;
    line-height: 1.65;
    font-family: 'Outfit', sans-serif;
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
}}

/* ── Divider label ── */
.divider-label {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.6rem 0 1.1rem 0;
    font-size: 0.60rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.20em;
    color: {ACCENT_LT};
    font-family: 'Outfit', sans-serif;
}}
.divider-label::before, .divider-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,92,252,0.35), transparent);
}}

/* ── Info box ── */
.info-box {{
    background: linear-gradient(160deg,
        rgba(18,22,50,0.85) 0%,
        rgba(14,18,38,0.75) 100%);
    border: 1px solid rgba(124,92,252,0.22);
    border-radius: var(--radius-md);
    padding: 1rem 1.15rem;
    color: {INK_SOFT};
    line-height: 1.78;
    box-shadow: var(--shadow-sm);
    font-size: 0.87rem;
    font-family: 'Outfit', sans-serif;
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
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    font-family: 'Outfit', sans-serif;
    border: 1px solid transparent;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast);
    cursor: default;
}}
.pill:hover {{ transform: scale(1.06); }}
.pill-expand   {{ background: rgba(59,130,246,0.16);  color: #93c5fd; border-color: rgba(59,130,246,0.35); }}
.pill-maintain {{ background: rgba(16,185,129,0.14);  color: #6ee7b7; border-color: rgba(16,185,129,0.32); }}
.pill-optimize {{ background: rgba(245,158,11,0.14);  color: #fcd34d; border-color: rgba(245,158,11,0.30); }}
.pill-drop     {{ background: rgba(225,29,120,0.14);  color: #f472b6; border-color: rgba(225,29,120,0.32); }}

/* ── Result card ── */
.result-card {{
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.6rem;
    margin: 1.2rem 0;
    border: 1px solid rgba(124,92,252,0.30);
    box-shadow: var(--shadow-md);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    animation: fadeUp 400ms ease-out;
    transition: transform var(--motion-med), box-shadow var(--motion-med);
}}
.result-card:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}}
.result-expand   {{ background: linear-gradient(140deg, rgba(59,130,246,0.18), rgba(14,18,38,0.80)); border-left: 4px solid {CHART_EXPAND}; }}
.result-maintain {{ background: linear-gradient(140deg, rgba(16,185,129,0.16), rgba(14,18,38,0.80)); border-left: 4px solid {CHART_MAINTAIN}; }}
.result-optimize {{ background: linear-gradient(140deg, rgba(245,158,11,0.16), rgba(14,18,38,0.80)); border-left: 4px solid {CHART_OPTIMIZE}; }}
.result-drop     {{ background: linear-gradient(140deg, rgba(225,29,120,0.16), rgba(14,18,38,0.80)); border-left: 4px solid {CHART_DROP}; }}

/* ── Form inputs ── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
    color: {INK_SOFT} !important;
    font-weight: 600 !important;
    font-size: 0.74rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-family: 'Outfit', sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {{
    background: rgba(14,18,38,0.80) !important;
    border: 1px solid rgba(124,92,252,0.28) !important;
    border-radius: var(--radius-sm) !important;
    color: {INK} !important;
    min-height: 44px !important;
    box-shadow: none !important;
    transition: border-color var(--motion-fast), box-shadow var(--motion-fast) !important;
    font-family: 'Outfit', sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:hover,
.stNumberInput input:hover {{
    border-color: rgba(124,92,252,0.55) !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {{
    border-color: rgba(124,92,252,0.75) !important;
    box-shadow: 0 0 0 3px rgba(124,92,252,0.18) !important;
}}

/* Dropdown list items */
[data-baseweb="menu"] {{
    background: #0e1225 !important;
    border: 1px solid rgba(124,92,252,0.28) !important;
    border-radius: var(--radius-sm) !important;
}}
[data-baseweb="menu"] li {{ color: {INK_SOFT} !important; }}
[data-baseweb="menu"] li:hover {{ background: rgba(124,92,252,0.16) !important; }}

/* ── Form card ── */
[data-testid="stForm"] {{
    background: linear-gradient(160deg,
        rgba(18,22,50,0.82) 0%,
        rgba(14,18,38,0.72) 100%) !important;
    border: 1px solid rgba(124,92,252,0.28) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.5rem 1.6rem 1.8rem !important;
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(196,181,253,0.06) !important;
    backdrop-filter: blur(22px) !important;
    animation: borderPulse 6s ease-in-out infinite !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button,
.stButton > button {{
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    border: none !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
    transition: transform var(--motion-fast), box-shadow var(--motion-fast) !important;
    position: relative;
    overflow: hidden;
}}
[data-testid="stFormSubmitButton"] > button {{
    width: 100% !important;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_DK}) !important;
    box-shadow: 0 8px 28px rgba(124,92,252,0.40), 0 0 0 1px rgba(124,92,252,0.35) !important;
    color: white !important;
    padding: 0.75rem 0 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 38px rgba(124,92,252,0.55), 0 0 40px rgba(59,130,246,0.20) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform: translateY(0) scale(0.98) !important;
}}
.stButton > button {{
    background: rgba(20,25,55,0.80) !important;
    color: {INK_SOFT} !important;
    border: 1px solid rgba(124,92,252,0.28) !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stButton > button:hover {{
    background: rgba(30,36,75,0.90) !important;
    color: {INK} !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background: rgba(14,18,38,0.75) !important;
    border: 1px solid rgba(124,92,252,0.22) !important;
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
[data-testid="stDataFrame"] span {{ color: {INK_SOFT} !important; }}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background: rgba(124,92,252,0.14) !important;
    color: {ACCENT_LT} !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(124,92,252,0.22) !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
    border-bottom: 1px solid rgba(124,92,252,0.10) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: linear-gradient(160deg,
        rgba(18,22,50,0.80) 0%,
        rgba(14,18,38,0.70) 100%) !important;
    border: 1px solid rgba(124,92,252,0.22) !important;
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
    color: {INK_SOFT} !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
}}

/* ── Charts ── */
[data-testid="stPyplot"] {{
    background: rgba(14,18,38,0.70);
    border: 1px solid rgba(124,92,252,0.22);
    border-radius: var(--radius-lg);
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(16px);
    transition: transform var(--motion-med), box-shadow var(--motion-med);
}}
[data-testid="stPyplot"]:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-md), 0 0 0 1px rgba(124,92,252,0.35);
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: var(--radius-md) !important;
    background: rgba(14,18,38,0.80) !important;
    border: 1px solid rgba(124,92,252,0.25) !important;
    color: {INK_SOFT} !important;
}}

/* ── HR ── */
hr {{
    border: none !important;
    border-top: 1px solid rgba(124,92,252,0.18) !important;
    margin: 1.4rem 0 !important;
}}

/* ── Column label ── */
.col-label {{
    font-size: 0.64rem;
    font-weight: 700;
    color: {ACCENT_LT};
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Outfit', sans-serif;
}}
.col-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(124,92,252,0.35), transparent);
}}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background: {ACCENT} !important;
    border-color: {ACCENT_LT} !important;
    box-shadow: 0 0 12px rgba(124,92,252,0.50) !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
    background: linear-gradient(90deg, {ACCENT}, {ACCENT_2}) !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: rgba(10,13,26,0.60); }}
::-webkit-scrollbar-thumb {{
    background: rgba(124,92,252,0.35);
    border-radius: 999px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(124,92,252,0.60); }}

/* ── Selection ── */
::selection {{
    background: rgba(124,92,252,0.28);
    color: {INK};
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  DECISION CONFIG
# ─────────────────────────────────────────────────────────────
DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_ORANGE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  CHART HELPERS — dark-mode aware
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#0e1225")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=INK_MUTED, labelsize=8.5, length=0)
    ax.xaxis.label.set_color(INK_MUTED)
    ax.yaxis.label.set_color(INK_MUTED)
    ax.title.set_color(INK)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    ax.title.set_fontfamily("serif")
    ax.grid(axis="y", color="#1e2545", linewidth=0.8, linestyle="-", alpha=0.90)
    ax.set_axisbelow(True)
    # Set tick label colors
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(INK_MUTED)
    return fig, ax


def col_seq(labels):
    return [DECISION_COLORS.get(l, "#7c5cfc") for l in labels]


def soften_bars(bars, alpha=0.88):
    for bar in bars:
        bar.set_alpha(alpha)
        bar.set_linewidth(0)
    return bars


# ─────────────────────────────────────────────────────────────
#  PATHS
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
#  DATA & MODEL LOADING
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
#  LOAD
# ─────────────────────────────────────────────────────────────
df = load_data()
model1, model2, model3, X1_columns, X2_columns, X3_columns = load_artifacts()


# ─────────────────────────────────────────────────────────────
#  PRE-COMPUTED DATA
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
    st.markdown('<div class="sidebar-brand">Airline<span> Route</span> Intelligence ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.65rem;color:{ACCENT_LT};margin-bottom:16px;"
        "font-weight:700;letter-spacing:0.16em;text-transform:uppercase;font-family:Outfit,sans-serif'>Filter View</p>",
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
    <p style='font-size:0.63rem;color:{ACCENT_LT};font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;margin-bottom:12px;font-family:Outfit,sans-serif'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:0.81rem;color:{INK_MUTED};font-family:Outfit,sans-serif'>
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
#  FILTER
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
  <div class="hero-star"></div>
  <div class="hero-star"></div>
  <div class="hero-star"></div>
  <div class="hero-star"></div>
  <div class="hero-left">
    <div class="hero-eyebrow">✦ Route Intelligence Platform</div>
    <h1>Airline Profitability System</h1>
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
            wedgeprops={"linewidth":3,"edgecolor":"#0a0d1a"},
            textprops={"color":INK,"fontsize":9.5,"fontfamily":"Outfit"},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8.5); at.set_color(INK_SOFT); at.set_fontweight("bold")
        for t in texts:
            t.set_color(INK_SOFT)
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
          <strong style="color:#c4b5fd">How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:#c4b5fd">Expand</strong> routes should have the highest values across all three columns.
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
                ty = h * 0.5; va = "center"; txt_color = INK_SOFT
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
    ax.grid(axis="x", color="#1e2545", linewidth=0.8, linestyle="-", alpha=0.90)
    ax.grid(axis="y", visible=False)
    for label in ax.get_yticklabels():
        label.set_color(INK_SOFT)
    st.pyplot(fig)


# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
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
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5))
        bars = ax.barh(top.index, top.values, color=CHART_EXPAND, height=0.55)
        soften_bars(bars)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Top 10 Routes")
        ax.grid(axis="x", color="#1e2545", linewidth=0.8, linestyle="-", alpha=0.90)
        ax.grid(axis="y", visible=False)
        for label in ax.get_yticklabels():
            label.set_color(INK_SOFT)
        st.pyplot(fig)

    with right:
        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
            "Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5))
        bars = ax.barh(worst.index, worst.values, color=CHART_DROP, height=0.55)
        soften_bars(bars)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Bottom 10 Routes")
        ax.grid(axis="x", color="#1e2545", linewidth=0.8, linestyle="-", alpha=0.90)
        ax.grid(axis="y", visible=False)
        for label in ax.get_yticklabels():
            label.set_color(INK_SOFT)
        st.pyplot(fig)


# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
        "How many unique routes appear in each category?</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route":"Unique Routes"})
        .set_index("Route_Decision").reindex(ORDER).dropna()
    )
    bc_map = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
              "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
    bc = [bc_map.get(i,"#7c5cfc") for i in urbd.index]
    fig, ax = clean_fig((8, 4))
    vals4 = urbd["Unique Routes"].values.tolist()
    bars = ax.bar(urbd.index, vals4, color=bc, width=0.55)
    soften_bars(bars)
    for bar, h in zip(bars, vals4):
        ax.text(bar.get_x() + bar.get_width()/2, h + max(vals4)*0.05, f"{int(h)}",
                ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
    ax.set_ylabel("Number of Unique Routes")
    ax.set_title("Unique Routes per Decision Category")
    for label in ax.get_xticklabels():
        label.set_color(INK_SOFT)
    st.pyplot(fig)

    patches = [mpatches.Patch(color=bc_map.get(d,"#7c5cfc"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5,0.5))
    fig2.patch.set_alpha(0); ax2.axis("off")
    legend = ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size":9})
    for text in legend.get_texts():
        text.set_color(INK_MUTED)
    st.pyplot(fig2)


# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)
    fig, ax = clean_fig((8, 3.5))
    x = np.arange(len(comparison)); w = 0.33
    acc_col = ACCENT
    f1_col  = ACCENT_2
    bars1 = ax.bar(x - w/2, comparison["Accuracy"], width=w, color=acc_col, label="Accuracy")
    bars2 = ax.bar(x + w/2, comparison["Macro F1"], width=w, color=f1_col,  label="Macro F1")
    soften_bars(bars1); soften_bars(bars2)
    for bar, acc in zip(bars1, comparison["Accuracy"]):
        ax.text(bar.get_x()+bar.get_width()/2, acc+0.02, f"{acc:.0%}",
                ha="center", fontsize=7.5, color=INK_MUTED, fontweight="700")
    for bar, f1 in zip(bars2, comparison["Macro F1"]):
        ax.text(bar.get_x()+bar.get_width()/2, f1+0.02, f"{f1:.0%}",
                ha="center", fontsize=7.5, color=INK_MUTED, fontweight="700")
    legend = ax.legend(frameon=False, fontsize=9)
    for text in legend.get_texts():
        text.set_color(INK_SOFT)
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["Model"], fontsize=8.5, rotation=10, color=INK_SOFT)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Model Accuracy & F1 Comparison")
    st.pyplot(fig)

    st.markdown('<div class="divider-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a prediction mode</p>', unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
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

    # ── PREDICTION LOGIC ────────────────────────────────────
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
        text_col   = {"Expand":"#93c5fd","Maintain":"#6ee7b7",
                      "Optimize":"#fcd34d","Drop":"#f472b6"}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred,"result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred,"")}' style='font-size:0.66rem'>{pred}</span>
          </div>
          <div style='font-family:"Cinzel",serif;font-size:1.60rem;font-weight:600;
                      color:{text_col.get(pred,INK)};margin-bottom:10px;letter-spacing:0.04em;
                      text-transform:uppercase;text-shadow:0 0 30px rgba(124,92,252,0.40)'>
            Suggested Decision: {pred}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-size:0.89rem;line-height:1.76;
                    font-family:"Outfit",sans-serif'>
            {explanations.get(pred,"")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:8px;font-family:Outfit,sans-serif'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision":cls,"Probability":prob})
                   .sort_values("Probability", ascending=False))
        bar_cp = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
                  "Optimize":CHART_OPTIMIZE,"Drop":CHART_DROP}
        fig, ax = clean_fig((6, 3.5))
        bar_colors = [bar_cp.get(d, "#7c5cfc") for d in prob_df["Decision"]]
        probs = prob_df["Probability"].tolist()
        bars = ax.bar(prob_df["Decision"], probs, color=bar_colors, width=0.5)
        soften_bars(bars)
        for bar, h in zip(bars, probs):
            ax.text(bar.get_x()+bar.get_width()/2, h + 0.03, f"{h:.0%}",
                    ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("Probability")
        ax.set_title("Model Confidence per Decision")
        for label in ax.get_xticklabels():
            label.set_color(INK_SOFT)
        st.pyplot(fig)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
#  FILTERED DATA EXPANDER
# ─────────────────────────────────────────────────────────────
with st.expander("🗂  Show filtered data"):
    st.dataframe(fdf, use_container_width=True)


# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:44px 0 20px;'>
  <div style='display:inline-flex;align-items:center;gap:12px;
              background:rgba(14,18,38,0.80);
              border:1px solid rgba(124,92,252,0.28);
              border-radius:999px;
              padding:0.58rem 1.5rem;
              backdrop-filter:blur(16px);
              box-shadow:0 4px 20px rgba(124,92,252,0.14), 0 0 0 1px rgba(124,92,252,0.14);
              font-family:"Outfit",sans-serif;
              font-size:0.68rem;
              font-weight:600;
              color:{INK_MUTED};
              letter-spacing:0.12em;
              text-transform:uppercase'>
    <span style='color:{ACCENT_LT};font-size:0.80rem;filter:drop-shadow(0 0 8px rgba(124,92,252,0.70))'>✦</span>
    Airline Profitability System
    <span style='color:{ACCENT_LT};font-size:0.80rem;filter:drop-shadow(0 0 8px rgba(124,92,252,0.70))'>✦</span>
    Built with Streamlit
  </div>
</div>
""", unsafe_allow_html=True)