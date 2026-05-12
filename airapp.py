import os
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

st.set_page_config(
    page_title="SkyLens · Route Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  THEME SYSTEM  (change these variables to restyle the whole app)
# ─────────────────────────────────────────────────────────────
# Palette – updated for a dark glassmorphic theme
# These colours mirror the provided inspiration HTML with purple primaries and warm accent hues.
COLOR_BG          = "#131315"             # base canvas (very dark charcoal)
COLOR_SURFACE     = "rgba(32,31,33,0.60)" # glass panel surface (semi‑transparent)
COLOR_BORDER      = "rgba(255,255,255,0.08)"   # subtle white border for panels
COLOR_BORDER_MD   = "rgba(255,255,255,0.16)"

COLOR_INK         = "#e5e1e4"             # primary text (off‑white)
COLOR_INK_SOFT    = "#c4c0c5"             # secondary text
COLOR_INK_MUTED   = "#9b8c9e"             # tertiary text

COLOR_ACCENT      = "#e9b3ff"             # primary accent (lavender)
COLOR_ACCENT_DARK = "#9026c3"             # accent dark variant

COLOR_GREEN       = "#4ade80"             # Expand
COLOR_YELLOW      = "#facc15"             # Maintain
COLOR_ORANGE      = "#fb923c"             # Optimize
COLOR_PINK        = "#fb7185"             # Drop

# Chart palette tuned for dark backgrounds
CHART_EXPAND   = COLOR_GREEN
CHART_MAINTAIN = COLOR_YELLOW
CHART_OPTIMIZE = COLOR_ORANGE
CHART_DROP     = COLOR_PINK
CHART_NEUTRAL  = [
    "#6e40c9", "#9150d8", "#b480e7", "#d2a4f5",
    "#efc5d5", "#f3b5c6", "#fcb9b2", "#ffcc99"
]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&family=Manrope:wght@300;400;500;600;700&display=swap');

/* ── CSS VARIABLES ─────────────────────────────────────────── */
:root {{
    --bg:          {COLOR_BG};
    --surface:     {COLOR_SURFACE};
    --border:      {COLOR_BORDER};
    --border-md:   {COLOR_BORDER_MD};
    --ink:         {COLOR_INK};
    --ink-soft:    {COLOR_INK_SOFT};
    --ink-muted:   {COLOR_INK_MUTED};
    --accent:      {COLOR_ACCENT};
    --accent-dk:   {COLOR_ACCENT_DARK};
    --green:       {COLOR_GREEN};
    --yellow:      {COLOR_YELLOW};
    --orange:      {COLOR_ORANGE};
    --pink:        {COLOR_PINK};
    --radius-sm:   8px;
    --radius-md:   14px;
    --radius-lg:   20px;
    --shadow-sm:   0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 16px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
    --shadow-lg:   0 8px 32px rgba(0,0,0,0.09), 0 2px 8px rgba(0,0,0,0.05);
}}

/* ── BASE ───────────────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Syne', system-ui, sans-serif !important;
    color: var(--ink) !important;
}}

.stApp {{
    background: var(--bg) !important;
    min-height: 100vh;
}}

/* Remove Streamlit default header padding */
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}}

/* ── SIDEBAR ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border-md) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {{
    color: var(--ink-soft) !important;
    font-family: 'Syne', sans-serif !important;
}}

/* ── METRIC CARDS ───────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: var(--surface);
    border: 1px solid var(--border-md);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.18s ease, transform 0.18s ease;
}}
[data-testid="metric-container"]:hover {{
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    color: var(--ink-muted) !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {{
    font-family: 'DM Mono', monospace !important;
    font-size: 1.75rem !important;
    font-weight: 500 !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em !important;
}}

/* ── TABS ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: 4px;
    gap: 2px;
    border: 1px solid var(--border-md);
    box-shadow: var(--shadow-sm);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: var(--radius-sm);
    font-family: 'Syne', sans-serif !important;
    font-weight: 600;
    font-size: 0.80rem;
    color: var(--ink-muted) !important;
    padding: 7px 16px;
    background: transparent;
    border: none !important;
    transition: all 0.14s ease;
    letter-spacing: 0.01em;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: var(--bg) !important;
    color: var(--ink-soft) !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--ink) !important;
    color: #fff !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent;
    padding-top: 1.5rem;
}}

/* ── HEADINGS ───────────────────────────────────────────────── */
h1, h2, h3, h4 {{
    font-family: 'Syne', sans-serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
    font-weight: 700 !important;
}}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {{
    color: var(--ink-soft);
    line-height: 1.65;
    font-size: 0.90rem;
}}

/* ── WIDGET LABELS ──────────────────────────────────────────── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}}

/* ── INPUTS ─────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] div,
.stTextInput input,
.stNumberInput input {{
    color: var(--ink) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem !important;
    box-shadow: none !important;
    transition: border-color 0.14s ease !important;
}}
.stSelectbox [data-baseweb="select"] div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(10,110,250,0.12) !important;
}}

/* ── DATAFRAME ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 1px solid var(--border-md);
    box-shadow: var(--shadow-sm);
    background: var(--surface);
}}

/* ── EXPANDER ───────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-md) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden;
}}
[data-testid="stExpander"] summary p {{
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}}

/* ── FORM ───────────────────────────────────────────────────── */
[data-testid="stForm"] {{
    background: var(--surface);
    border: 1px solid var(--border-md);
    border-radius: var(--radius-lg);
    padding: 24px 28px 28px;
    box-shadow: var(--shadow-md);
}}

/* ── SUBMIT BUTTON ──────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {{
    background: var(--ink) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 12px 32px !important;
    width: 100% !important;
    transition: all 0.14s ease !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    background: var(--accent) !important;
    box-shadow: 0 4px 16px rgba(10,110,250,0.28) !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform: translateY(0) !important;
    box-shadow: none !important;
}}

/* ── REGULAR BUTTONS ────────────────────────────────────────── */
.stButton > button {{
    background: var(--surface) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--ink) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 9px 22px !important;
    transition: all 0.14s ease !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stButton > button:hover {{
    background: var(--bg) !important;
    border-color: var(--ink-muted) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}}

/* ── ALERT ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-md) !important;
}}
[data-testid="stAlert"] p {{ color: inherit !important; }}

hr {{
    border: none !important;
    border-top: 1px solid var(--border-md) !important;
    margin: 1.5rem 0 !important;
}}

/* ── CUSTOM COMPONENTS ──────────────────────────────────────── */

/* Hero banner */
.hero {{
    background: var(--ink);
    border-radius: var(--radius-lg);
    padding: 40px 48px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 80% 50%, rgba(10,110,250,0.20) 0%, transparent 60%);
    pointer-events: none;
}}
.hero-eyebrow {{
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 10px;
}}
.hero h1 {{
    font-family: 'Syne', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin: 0 0 12px 0 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.15 !important;
}}
.hero p {{
    color: rgba(255,255,255,0.55) !important;
    font-size: 0.92rem;
    margin: 0;
    max-width: 540px;
    line-height: 1.65;
    font-weight: 400;
}}
.hero-glyph {{
    position: absolute;
    right: 48px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    opacity: 0.07;
    color: #fff;
    line-height: 1;
    pointer-events: none;
    user-select: none;
}}

/* Sidebar brand */
.sidebar-brand {{
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--ink);
    padding: 4px 0 16px 0;
    border-bottom: 1px solid var(--border-md);
    margin-bottom: 16px;
    letter-spacing: -0.02em;
}}
.sidebar-brand span {{ color: var(--accent); }}

/* Section header */
.section-hd {{
    margin: 0 0 4px 0;
    font-size: 1.0rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.01em;
}}
.section-sub {{
    font-size: 0.82rem;
    color: var(--ink-muted);
    margin: 0 0 20px 0;
    font-weight: 400;
}}

/* Info box */
.info-box {{
    background: var(--bg);
    border: 1px solid var(--border-md);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    font-size: 0.84rem;
    color: var(--ink-soft);
    margin-bottom: 14px;
    line-height: 1.75;
}}

/* Decision pills */
.pill {{
    display: inline-block;
    padding: 2px 11px;
    border-radius: 99px;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: 1px solid transparent;
}}
.pill-expand   {{ background: #E6F9EF; color: #1A6B3C; border-color: #B2EACB; }}
.pill-maintain {{ background: #FEF9E6; color: #7A5400; border-color: #F0D98A; }}
.pill-optimize {{ background: #FFF0E8; color: #8A3300; border-color: #FFBF9A; }}
.pill-drop     {{ background: #FFF0F4; color: #80103C; border-color: #FFB8CC; }}

/* Result card */
.result-card {{
    border: 1px solid var(--border-md);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    margin: 20px 0;
    box-shadow: var(--shadow-md);
}}
.result-expand   {{ background: #F0FBF5; border-left: 4px solid {CHART_EXPAND}; }}
.result-maintain {{ background: #FEFCF0; border-left: 4px solid {CHART_MAINTAIN}; }}
.result-optimize {{ background: #FFF5F0; border-left: 4px solid {CHART_OPTIMIZE}; }}
.result-drop     {{ background: #FFF0F4; border-left: 4px solid {CHART_DROP}; }}

/* Divider with label */
.divider-label {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0 16px;
    color: var(--ink-muted);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}}
.divider-label::before, .divider-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border-md);
}}
/*
    ────────────────────────────────────────────────────────────
    DARK THEME OVERRIDES & GLASSMORPHISM
    These styles are appended at the end of the style block to override
    the default light theme and introduce a modern, glassy look inspired
    by the provided HTML examples. They redefine variables, apply
    backdrop blurs, radial backgrounds, and adjust spacing to give
    components depth and separation.
*/
:root {{
    --bg:                #131315;
    --surface:           rgba(32,31,33,0.60);
    --border:            rgba(255,255,255,0.08);
    --border-md:         rgba(255,255,255,0.16);
    --ink:               #e5e1e4;
    --ink-soft:          #c4c0c5;
    --ink-muted:         #9b8c9e;
    --accent:            #e9b3ff;
    --accent-dk:         #9026c3;
    --green:             #4ade80;
    --yellow:            #facc15;
    --orange:            #fb923c;
    --pink:              #fb7185;
    --radius-sm:         10px;
    --radius-md:         18px;
    --radius-lg:         24px;
    --radius-xl:         28px;
    --shadow-sm:         0 2px 4px rgba(0,0,0,0.40), 0 1px 2px rgba(0,0,0,0.30);
    --shadow-md:         0 4px 12px rgba(0,0,0,0.45), 0 2px 6px rgba(0,0,0,0.35);
    --shadow-lg:         0 8px 24px rgba(0,0,0,0.50), 0 4px 12px rgba(0,0,0,0.40);
    --glass-bg:          rgba(32,31,33,0.60);
    --glass-border:      rgba(255,255,255,0.10);
    --glass-blur:        blur(20px);
}}
html, body, [class*="css"] {{
    font-family: 'Manrope', sans-serif !important;
    color: var(--ink) !important;
    background: radial-gradient(circle at 0% 0%, #1c1b1d 0%, #131315 50%, #0e0e10 100%) !important;
    scroll-behavior: smooth;
}}
.stApp {{
    background: var(--bg) !important;
    background: radial-gradient(circle at 0% 0%, #1c1b1d 0%, #131315 50%, #0e0e10 100%) !important;
    position: relative;
    min-height: 100vh;
}}
.stApp::before,
.stApp::after {{
    content: "";
    position: absolute;
    border-radius: 50%;
    width: 650px;
    height: 650px;
    background: radial-gradient(circle, rgba(233,179,255,0.12) 0%, rgba(233,179,255,0) 70%);
    pointer-events: none;
    z-index: -1;
    filter: blur(80px);
}}
.stApp::before {{
    top: -250px;
    left: -250px;
}}
.stApp::after {{
    bottom: -250px;
    right: -250px;
    transform: scale(1.4);
    opacity: 0.6;
}}
/* Sidebar glass effect */
[data-testid="stSidebar"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border-right: 1px solid var(--glass-border) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.50) !important;
}}
/* Sidebar text override */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {{
    color: var(--ink-soft) !important;
    font-family: 'Manrope', sans-serif !important;
}}
/* Metric cards glass style */
[data-testid="metric-container"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 26px 30px !important;
    box-shadow: var(--shadow-md) !important;
    margin-bottom: 32px !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-5px) !important;
    box-shadow: var(--shadow-lg) !important;
}}
/* Metric labels and values */
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    color: var(--ink-muted) !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {{
    font-family: 'DM Mono', monospace !important;
    font-size: 2.1rem !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
}}
/* Hero glass style */
.hero {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 56px 64px !important;
    margin-bottom: 36px !important;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-md) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}
.hero:hover {{
    transform: translateY(-4px) !important;
    box-shadow: var(--shadow-lg) !important;
}}
.hero-eyebrow {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: var(--ink-muted);
    margin-bottom: 12px;
}}
.hero h1 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    letter-spacing: -0.03em !important;
}}
.hero p {{
    color: var(--ink-soft) !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 1.0rem !important;
    line-height: 1.70 !important;
}}
.hero-glyph {{
    font-size: 8rem;
    opacity: 0.10;
    color: var(--ink);
    line-height: 1;
    position: absolute;
    right: 64px;
    top: 50%;
    transform: translateY(-50%);
    user-select: none;
    pointer-events: none;
}}
/* Section headers */
.section-hd {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em !important;
    margin-bottom: 4px !important;
}}
.section-sub {{
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.90rem !important;
    color: var(--ink-soft) !important;
    margin-bottom: 20px !important;
}}
/* Decision pills updated colours */
.pill-expand   {{ background: rgba(34,197,94,0.20) !important; color: #4ade80 !important; border-color: rgba(34,197,94,0.40) !important; }}
.pill-maintain {{ background: rgba(250,204,21,0.20) !important; color: #facc15 !important; border-color: rgba(250,204,21,0.40) !important; }}
.pill-optimize {{ background: rgba(251,146,60,0.20) !important; color: #fb923c !important; border-color: rgba(251,146,60,0.40) !important; }}
.pill-drop     {{ background: rgba(251,113,133,0.20) !important; color: #fb7185 !important; border-color: rgba(251,113,133,0.40) !important; }}
/* Result cards glass style overrides */
.result-card {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 36px 40px !important;
    margin: 32px 0 !important;
    box-shadow: var(--shadow-md) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}
.result-card:hover {{
    transform: translateY(-4px) !important;
    box-shadow: var(--shadow-lg) !important;
}}
/* Info box glass style */
.info-box {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px !important;
    color: var(--ink-soft) !important;
    box-shadow: var(--shadow-md) !important;
}}
.info-box strong {{
    color: var(--ink) !important;
}}
/* DataFrame glass style */
[data-testid="stDataFrame"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-md) !important;
    overflow: hidden !important;
}}
/* Expander glass style */
[data-testid="stExpander"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-md) !important;
}}
/* Form glass style */
[data-testid="stForm"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 32px 36px !important;
    box-shadow: var(--shadow-md) !important;
}}
/* Tabs style overrides */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.80rem !important;
    color: var(--ink-muted) !important;
    padding: 8px 18px !important;
    border-radius: var(--radius-sm) !important;
    transition: background 0.2s ease, color 0.2s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(255,255,255,0.05) !important;
    color: var(--ink-soft) !important;
}}
.stTabs [aria-selected="true"] {{
    background: var(--accent) !important;
    color: #310048 !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding-top: 1.5rem !important;
}}
/* Buttons gradient style */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-dk) 100%) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: #310048 !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 10px 24px !important;
    box-shadow: 0 6px 16px rgba(233,179,255,0.30) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
    background: linear-gradient(90deg, var(--accent-dk) 0%, var(--accent) 100%) !important;
    box-shadow: 0 8px 20px rgba(233,179,255,0.45) !important;
    transform: translateY(-2px) !important;
}}
/* Divider label override */
.divider-label {{
    color: var(--ink-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}}
.divider-label::before, .divider-label::after {{
    background: var(--border-md) !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  DECISION CONFIG  (unchanged from original)
# ─────────────────────────────────────────────────────────────
DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_ORANGE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

# ─────────────────────────────────────────────────────────────
#  CHART HELPER  (restyled, same data logic)
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    """
    Return a matplotlib figure/axes pair styled for a dark, glassmorphic theme.

    The charts produced by this helper adopt transparent backgrounds so they
    integrate nicely with the glass panels defined in the CSS. Axis lines,
    ticks and gridlines use muted tints pulled from the defined colour palette
    to enhance legibility on a dark canvas. Titles and labels employ
    contrasting colours and modern fonts.
    """
    fig, ax = plt.subplots(figsize=figsize)
    # Make the figure and axes backgrounds fully transparent so the
    # underlying glass panel shows through.
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    # Hide spines on the top and right to declutter the plot.
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # Colour remaining spines with a soft grey for dark mode.
    ax.spines["left"].set_color("#4f4352")
    ax.spines["bottom"].set_color("#4f4352")
    # Style ticks and tick labels with muted colours and slightly larger font.
    ax.tick_params(colors=COLOR_INK_MUTED, labelsize=9)
    # Axis labels use the same muted tint as ticks.
    ax.xaxis.label.set_color(COLOR_INK_MUTED)
    ax.yaxis.label.set_color(COLOR_INK_MUTED)
    # Title styling: brighter ink, larger size, bold weight and modern font.
    ax.title.set_color(COLOR_INK)
    ax.title.set_fontsize(12)
    ax.title.set_fontweight("bold")
    ax.title.set_fontfamily("Manrope")
    # Use a dashed grid with low opacity for the horizontal lines only.
    # Note: matplotlib requires RGBA values as a tuple when specifying
    # transparency. We supply an almost-white colour with low opacity (8%).
    ax.grid(axis="y", color=(1, 1, 1, 0.08), linewidth=1.0, linestyle="--")
    ax.set_axisbelow(True)
    return fig, ax

def col_seq(labels):
    return [DECISION_COLORS.get(l, "#CCCCCC") for l in labels]

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
    st.markdown('<div class="sidebar-brand">Sky<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.75rem;color:#9b8c9e;margin-bottom:18px;font-weight:500;"
        "letter-spacing:0.05em;text-transform:uppercase'>Filter view</p>",
        unsafe_allow_html=True
    )
    route_opts    = ["All"] + sorted(df["Route"].dropna().unique().tolist())
    aircraft_opts = ["All"] + sorted(df["Aircraft_Type"].dropna().unique().tolist())
    season_opts   = ["All"] + sorted(df["Season"].dropna().unique().tolist())
    decision_opts = ["All"] + sorted(df["Route_Decision"].dropna().unique().tolist())

    sel_route    = st.selectbox("Route",         route_opts)
    sel_aircraft = st.selectbox("Aircraft Type", aircraft_opts)
    sel_season   = st.selectbox("Season",        season_opts)
    sel_decision = st.selectbox("Decision",      decision_opts)

    st.markdown("---")
    st.markdown("""
    <p style='font-size:0.72rem;color:#9b8c9e;font-weight:700;letter-spacing:0.10em;
    text-transform:uppercase;margin-bottom:10px'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:8px;font-size:0.82rem;color:#c4c0c5'>
      <div><span class='pill pill-expand'>Expand</span>&nbsp;&nbsp;High profit &amp; demand</div>
      <div><span class='pill pill-maintain'>Maintain</span>&nbsp;&nbsp;Stable performer</div>
      <div><span class='pill pill-optimize'>Optimize</span>&nbsp;&nbsp;Room to improve</div>
      <div><span class='pill pill-drop'>Drop</span>&nbsp;&nbsp;Losing money</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FILTERING  (logic unchanged)
# ─────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_route    != "All": fdf = fdf[fdf["Route"]          == sel_route]
if sel_aircraft != "All": fdf = fdf[fdf["Aircraft_Type"]  == sel_aircraft]
if sel_season   != "All": fdf = fdf[fdf["Season"]         == sel_season]
if sel_decision != "All": fdf = fdf[fdf["Route_Decision"] == sel_decision]

# ─────────────────────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">Route Intelligence Platform</div>
  <h1>SkyLens Dashboard</h1>
  <p>
    Built on a sample airline dataset for analysis and demonstration purposes only.
    Does not reflect real-time airline operations or current flight decisions.
  </p>
  <div class="hero-glyph">✈</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Performance Drivers",
    "Route Actions",
    "Route Stability",
    "Prediction Tool",
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

    # Primary KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Flights",   f"{n:,}")
    c2.metric("Unique Routes",   f"{n_routes}")
    c3.metric("Average Profit",  f"${avg_profit:,.0f}")
    c4.metric("Avg Load Factor", f"{avg_load:.0%}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Decision split KPIs
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
        wc = {
            "Expand":   CHART_EXPAND,
            "Maintain": CHART_MAINTAIN,
            "Optimize": CHART_ORANGE,
            "Drop":     CHART_DROP,
        }
        fig, ax = clean_fig((5, 4.6))
        wedges, texts, autotexts = ax.pie(
            dc.values,
            labels=dc.index,
            autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index],
            startangle=90,
            wedgeprops={"linewidth": 3, "edgecolor": COLOR_BORDER_MD},
            textprops={"color": COLOR_INK, "fontsize": 9.5, "fontfamily": "Syne"},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8.5)
            at.set_color(COLOR_INK)
            at.set_fontweight("bold")
        ax.set_title("Share of Flights by Decision", pad=14)
        st.pyplot(fig)

    with right:
        st.markdown('<p class="section-hd">Average metrics by decision</p>', unsafe_allow_html=True)
        summary = (
            fdf.groupby("Route_Decision")[["Profit", "Profit_Margin", "Load_Factor"]]
            .mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .round(3)
            .reset_index()
            .rename(columns={
                "Route_Decision": "Decision",
                "Profit":         "Avg Profit ($)",
                "Profit_Margin":  "Avg Margin",
                "Load_Factor":    "Avg Load Factor",
            })
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="info-box">
          <strong>How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong>Expand</strong> routes should have the highest values across all three columns.
        </div>
        """, unsafe_allow_html=True)

# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown('<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        apd = (
            fdf.groupby("Route_Decision")["Profit"].mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .dropna()
        )
        fig, ax = clean_fig((6, 4))
        bars = ax.bar(
            apd.index, apd.values,
            color=col_seq(apd.index.tolist()),
            width=0.5,
            edgecolor=COLOR_BORDER_MD,
            linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + abs(apd.values).max() * 0.025,
                f"${h:,.0f}",
                ha="center", va="bottom",
                fontsize=8, color=COLOR_INK_SOFT, fontweight="700",
            )
        ax.set_ylabel("Average Profit ($)")
        ax.set_title("Average Profit by Decision")
        st.pyplot(fig)

    with right:
        ald = (
            fdf.groupby("Route_Decision")["Load_Factor"].mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .dropna()
        )
        fig, ax = clean_fig((6, 4))
        bars = ax.bar(
            ald.index, ald.values,
            color=col_seq(ald.index.tolist()),
            width=0.5,
            edgecolor=COLOR_BORDER_MD,
            linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.006,
                f"{h:.0%}",
                ha="center", va="bottom",
                fontsize=8, color=COLOR_INK_SOFT, fontweight="700",
            )
        ax.set_ylabel("Average Seat Occupancy")
        ax.set_title("Seat Occupancy by Decision")
        st.pyplot(fig)

    st.markdown('<div class="divider-label">Cost breakdown</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Where is the money going?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">The biggest cost components across all filtered flights.</p>', unsafe_allow_html=True)

    cost_cols = [
        "Fuel_Cost", "Maintenance_Cost", "Crew_Cost", "Depreciation_Cost",
        "Insurance_Cost", "Airport_Fees", "Catering_Cost", "Handling_Cost",
        "Navigation_Fees", "Sales_Distribution_Cost", "Passenger_Service_Cost",
        "Overhead_Cost", "Marketing_Cost", "IT_Systems_Cost",
    ]
    avail_costs = [c for c in cost_cols if c in fdf.columns]
    cost_means  = fdf[avail_costs].mean().sort_values(ascending=True).tail(8)
    label_map   = {
        "Fuel_Cost":               "Fuel",
        "Maintenance_Cost":        "Maintenance",
        "Crew_Cost":               "Crew",
        "Depreciation_Cost":       "Depreciation",
        "Insurance_Cost":          "Insurance",
        "Airport_Fees":            "Airport Fees",
        "Catering_Cost":           "Catering",
        "Handling_Cost":           "Handling",
        "Navigation_Fees":         "Navigation",
        "Sales_Distribution_Cost": "Sales & Dist.",
        "Passenger_Service_Cost":  "Pax Service",
        "Overhead_Cost":           "Overhead",
        "Marketing_Cost":          "Marketing",
        "IT_Systems_Cost":         "IT Systems",
    }
    cost_means.index = [label_map.get(i, i) for i in cost_means.index]
    fig, ax = clean_fig((9, 4))
    bars = ax.barh(
        cost_means.index, cost_means.values,
        color=CHART_NEUTRAL[:len(cost_means)],
        edgecolor=COLOR_BORDER_MD,
        linewidth=2,
        height=0.55,
    )
    mx = cost_means.max()
    for b in bars:
        w = b.get_width()
        ax.text(
            w + mx * 0.012,
            b.get_y() + b.get_height() / 2,
            f"${w:,.0f}",
            va="center", fontsize=8, color=COLOR_INK_SOFT, fontweight="700",
        )
    ax.set_xlabel("Average Cost per Flight ($)")
    ax.set_title("Top Cost Drivers")
    st.pyplot(fig)

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
        "Top routes currently classified as Expand</p>",
        unsafe_allow_html=True,
    )
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route", "Profit", "Profit_Margin", "Load_Factor"]]
        .head(10)
        .rename(columns={
            "Profit":        "Avg Profit ($)",
            "Profit_Margin": "Profit Margin",
            "Load_Factor":   "Load Factor",
        })
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
            "Top 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(top.index, top.values, color=CHART_EXPAND, edgecolor=COLOR_BORDER_MD, linewidth=2, height=0.55)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Top 10 Routes")
        st.pyplot(fig)

    with right:
        st.markdown(
            "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
            "Bottom 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(worst.index, worst.values, color=CHART_DROP, edgecolor=COLOR_BORDER_MD, linewidth=2, height=0.55)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Bottom 10 Routes")
        st.pyplot(fig)

# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
            "Routes with most decision changes</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
            "Routes seen in the most decision states</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
        "How many unique routes appear in each category?</p>",
        unsafe_allow_html=True,
    )

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route": "Unique Routes"})
        .set_index("Route_Decision")
        .reindex(ORDER)
        .dropna()
    )
    bc_map = {
        "Expand":   CHART_EXPAND,
        "Maintain": CHART_MAINTAIN,
        "Optimize": CHART_ORANGE,
        "Drop":     CHART_DROP,
    }
    bc = [bc_map.get(i, "#CCCCCC") for i in urbd.index]
    fig, ax = clean_fig((8, 4))
    bars = ax.bar(
        urbd.index, urbd["Unique Routes"],
        color=bc, width=0.5,
        edgecolor=COLOR_BORDER_MD, linewidth=2,
    )
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + 0.3,
            f"{int(h)}",
            ha="center", fontsize=9, color=COLOR_INK_SOFT, fontweight="700",
        )
    ax.set_ylabel("Number of Unique Routes")
    ax.set_title("Unique Routes per Decision Category")
    st.pyplot(fig)

    patches = [mpatches.Patch(color=bc_map.get(d, "#CCCCCC"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5, 0.5))
    fig2.patch.set_alpha(0)
    ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size": 9}, labelcolor=COLOR_INK)
    st.pyplot(fig2)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    # Model accuracy chart
    st.markdown(
        "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
        "How accurate are the models?</p>",
        unsafe_allow_html=True,
    )
    fig, ax = clean_fig((8, 3.5))
    x = np.arange(len(comparison))
    w = 0.30
    b1 = ax.bar(x - w / 2, comparison["Accuracy"], w, label="Accuracy",
                color=CHART_NEUTRAL[0], edgecolor=COLOR_BORDER_MD, linewidth=2)
    b2 = ax.bar(x + w / 2, comparison["Macro F1"], w, label="Macro F1",
                color=CHART_NEUTRAL[2], edgecolor=COLOR_BORDER_MD, linewidth=2)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.006, f"{h:.0%}",
                ha="center", fontsize=7.5, color=COLOR_INK_SOFT, fontweight="700")
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["Model"], fontsize=8.5)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Model Accuracy & F1 Comparison")
    ax.legend(frameon=False, fontsize=9, labelcolor=COLOR_INK)
    plt.xticks(rotation=10)
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
        ["With Revenue Variables", "Without Revenue Variables", "Only Pre-Operational Features"],
        key="model_choice_select",
    )

    # ── FORM (logic unchanged) ────────────────────────────────
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                "<p style='font-size:0.75rem;font-weight:700;color:#9b8c9e;letter-spacing:0.08em;"
                "text-transform:uppercase;margin-bottom:12px'>Flight basics</p>",
                unsafe_allow_html=True,
            )
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown(
                "<p style='font-size:0.75rem;font-weight:700;color:#9b8c9e;letter-spacing:0.08em;"
                "text-transform:uppercase;margin-bottom:12px'>Route context</p>",
                unsafe_allow_html=True,
            )
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.75rem;font-weight:700;color:#9b8c9e;letter-spacing:0.08em;"
                    "text-transform:uppercase;margin-bottom:12px'>Revenue</p>",
                    unsafe_allow_html=True,
                )
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.75rem;font-weight:700;color:#9b8c9e;letter-spacing:0.08em;"
                    "text-transform:uppercase;margin-bottom:12px'>Cost breakdown</p>",
                    unsafe_allow_html=True,
                )
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

        submitted = st.form_submit_button("Get Route Decision →")

    # ── PREDICTION LOGIC (unchanged) ─────────────────────────
    if submitted:
        if model_choice == "With Revenue Variables":
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
                "Ticket_Revenue": ticket_revenue, "Ancillary_Revenue": ancillary_revenue,
            }
            inp  = prepare_input(pd.DataFrame([row]), X1_columns)
            pred = model1.predict(inp)[0]
            prob = model1.predict_proba(inp)[0]
            cls  = model1.classes_
        elif model_choice == "Without Revenue Variables":
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
                "Fuel_Cost": fuel_cost, "Maintenance_Cost": maintenance_cost,
                "Crew_Cost": crew_cost, "Depreciation_Cost": depreciation_cost,
                "Insurance_Cost": insurance_cost, "Airport_Fees": airport_fees,
                "Catering_Cost": catering_cost, "Handling_Cost": handling_cost,
                "Navigation_Fees": navigation_fees, "Sales_Distribution_Cost": sales_distribution_cost,
                "Passenger_Service_Cost": passenger_service_cost, "Overhead_Cost": overhead_cost,
                "Marketing_Cost": marketing_cost, "IT_Systems_Cost": it_systems_cost,
            }
            inp  = prepare_input(pd.DataFrame([row]), X2_columns)
            pred = model2.predict(inp)[0]
            prob = model2.predict_proba(inp)[0]
            cls  = model2.classes_
        else:
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
            }
            inp  = prepare_input(pd.DataFrame([row]), X3_columns)
            pred = model3.predict(inp)[0]
            prob = model3.predict_proba(inp)[0]
            cls  = model3.classes_

        st.session_state.pred_result = {"prediction": pred, "probabilities": prob, "classes": cls}

    # ── RESULT DISPLAY (unchanged logic, restyled) ────────────
    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]
        prob = res["probabilities"]
        cls  = res["classes"]

        pill_cls = {
            "Expand":   "pill-expand",
            "Maintain": "pill-maintain",
            "Optimize": "pill-optimize",
            "Drop":     "pill-drop",
        }
        result_cls = {
            "Expand":   "result-expand",
            "Maintain": "result-maintain",
            "Optimize": "result-optimize",
            "Drop":     "result-drop",
        }
        text_col = {
            "Expand":   COLOR_GREEN,
            "Maintain": COLOR_YELLOW,
            "Optimize": COLOR_ORANGE,
            "Drop":     COLOR_PINK,
        }
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred, "result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred, "")}' style='font-size:0.68rem'>{pred}</span>
          </div>
          <div style='font-family:"Syne",sans-serif;font-size:1.65rem;font-weight:800;
                      color:{text_col.get(pred, "#e5e1e4")};margin-bottom:10px;letter-spacing:-0.02em'>
            Suggested Decision: {pred}
          </div>
          <p style='color:#c4c0c5;margin:0;font-size:0.90rem;line-height:1.70'>
            {explanations.get(pred, "")}
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:0.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
            "Confidence by decision option</p>",
            unsafe_allow_html=True,
        )

        prob_df = (
            pd.DataFrame({"Decision": cls, "Probability": prob})
            .sort_values("Probability", ascending=False)
        )
        bar_cp = {
            "Expand":   CHART_EXPAND,
            "Maintain": CHART_MAINTAIN,
            "Optimize": CHART_ORANGE,
            "Drop":     CHART_DROP,
        }
        fig, ax = clean_fig((6, 3.5))
        bars = ax.bar(
            prob_df["Decision"], prob_df["Probability"],
            color=[bar_cp.get(d, "#CCCCCC") for d in prob_df["Decision"]],
            width=0.45, edgecolor=COLOR_BORDER_MD, linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.013,
                f"{h:.0%}",
                ha="center", fontsize=9, color=COLOR_INK_SOFT, fontweight="700",
            )
        ax.set_ylim(0, 1.18)
        ax.set_ylabel("Probability")
        ax.set_title("Model Confidence per Decision")
        st.pyplot(fig)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

# ─────────────────────────────────────────────────────────────
#  FILTERED DATA EXPANDER  (unchanged)
# ─────────────────────────────────────────────────────────────
with st.expander("Show filtered data"):
    st.dataframe(fdf, use_container_width=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#AAAAAA;font-size:0.75rem;
            padding:36px 0 16px;font-family:"Syne",sans-serif;
            letter-spacing:0.04em'>
  SKYLENS ROUTE INTELLIGENCE &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  HOW TO TWEAK THE THEME
# ─────────────────────────────────────────────────────────────
# All visual tokens live at the top of this file under "THEME SYSTEM".
# To switch to a dark mode: change COLOR_BG to #0E0E0E, COLOR_SURFACE to
# #1A1A1A, COLOR_INK to #FFFFFF, COLOR_INK_SOFT to #CCCCCC, and update
# --bg / --surface / --ink in the CSS :root block accordingly.
#
# To change the accent color (buttons, focus rings): update COLOR_ACCENT
# and --accent in :root.
#
# Chart colors are controlled by CHART_EXPAND / CHART_MAINTAIN /
# CHART_ORANGE / CHART_DROP and CHART_NEUTRAL at the top of the file.