
import os
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Airline Profitability System",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────────────────────
#  PIXEL / SUPER MARIO PALETTE
# ─────────────────────────────────────────────────────────────
BG_BASE        = "#e8f4f8"          # sky blue (Mario sky)
BG_SOFT        = "#d4ecd4"          # grass green tint
BG_COOL        = "#fff9e6"          # coin yellow tint

GLASS_BG       = "rgba(255, 255, 255, 0.82)"
GLASS_BORDER   = "rgba(44, 117, 44, 0.40)"

INK            = "#1a1a2e"          # dark navy pixel ink
INK_SOFT       = "#2c3e50"          # medium dark
INK_MUTED      = "#5a6c7d"          # muted slate

ACCENT         = "#e63946"          # Mario red
ACCENT_DK      = "#c1121f"          # dark red
ACCENT_LT      = "#ff8fa3"          # light red
ACCENT_2       = "#1d6a96"          # Mario blue (overalls)
MAGENTA        = "#f4a261"          # coin orange

# Pixel chart tones
CHART_EXPAND   = "#2d6a4f"          # forest green (go!)
CHART_MAINTAIN = "#1d6a96"          # Mario blue
CHART_OPTIMIZE = "#e9c46a"          # coin yellow
CHART_ORANGE   = "#f4a261"
CHART_DROP     = "#e63946"          # Mario red (stop)
CHART_NEUTRAL  = [
    "#e63946", "#1d6a96", "#2d6a4f", "#e9c46a",
    "#f4a261", "#7f768b", "#2ec4b6", "#264653",
]

DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_OPTIMIZE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — PIXEL / 8-BIT GAME THEME
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&family=Nunito:wght@400;600;700;800&display=swap');

:root {{
    --sky:         {BG_BASE};
    --grass:       {BG_SOFT};
    --coin:        {BG_COOL};
    --ink:         {INK};
    --ink-soft:    {INK_SOFT};
    --ink-muted:   {INK_MUTED};
    --red:         {ACCENT};
    --red-dk:      {ACCENT_DK};
    --red-lt:      {ACCENT_LT};
    --blue:        {ACCENT_2};
    --orange:      {MAGENTA};
    --green:       {CHART_EXPAND};
    --coin-y:      {CHART_OPTIMIZE};
    --px-border:   4px;
    --px-shadow:   4px 4px 0px rgba(0,0,0,0.35);
    --px-shadow-lg: 6px 6px 0px rgba(0,0,0,0.35);
    --px-inset:    inset -3px -3px 0px rgba(0,0,0,0.25), inset 2px 2px 0px rgba(255,255,255,0.35);
}}

/* Pixel checkerboard keyframes */
@keyframes floatIn    {{ from {{ opacity:0; transform:translateY(16px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes coinSpin   {{ 0%,100% {{ transform:scaleX(1); }} 40% {{ transform:scaleX(0.1); }} 60% {{ transform:scaleX(1); }} }}
@keyframes bobUp      {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-6px); }} }}
@keyframes blinkCursor {{ 0%,49% {{ opacity:1; }} 50%,100% {{ opacity:0; }} }}
@keyframes pixelSlide {{ from {{ transform:translateX(-100%); }} to {{ transform:translateX(120vw); }} }}
@keyframes starPop    {{ 0% {{ transform:scale(0) rotate(0deg); opacity:0; }}
                         60% {{ transform:scale(1.3) rotate(20deg); opacity:1; }}
                         100% {{ transform:scale(1) rotate(15deg); opacity:0.85; }} }}
@keyframes groundScroll {{ from {{ background-position:0 0; }} to {{ background-position:-64px 0; }} }}
@keyframes coinFloat  {{ 0%,100% {{ transform:translateY(0) rotate(0deg); }}
                         50% {{ transform:translateY(-8px) rotate(10deg); }} }}
@keyframes pixelPulse {{ 0%,100% {{ box-shadow: 4px 4px 0px rgba(0,0,0,0.35); }}
                         50% {{ box-shadow: 4px 4px 0px rgba(0,0,0,0.35), 0 0 0 3px {ACCENT}55; }} }}

html, body, [class*="css"] {{
    font-family: 'Nunito', system-ui, sans-serif !important;
    -webkit-font-smoothing: auto !important;
    color: {INK} !important;
    image-rendering: pixelated;
}}

/* ── App background: checkered sky pattern ── */
.stApp {{
    min-height: 100vh;
    background-color: #87CEEB;
    background-image:
        /* Pixel cloud shapes using box gradients */
        radial-gradient(ellipse at 15% 22%, rgba(255,255,255,0.75) 0, rgba(255,255,255,0.75) 6%, transparent 7%),
        radial-gradient(ellipse at 18% 20%, rgba(255,255,255,0.75) 0, rgba(255,255,255,0.75) 5%, transparent 6%),
        radial-gradient(ellipse at 21% 22%, rgba(255,255,255,0.75) 0, rgba(255,255,255,0.75) 5%, transparent 6%),
        radial-gradient(ellipse at 60% 12%, rgba(255,255,255,0.72) 0, rgba(255,255,255,0.72) 5%, transparent 6%),
        radial-gradient(ellipse at 63% 10%, rgba(255,255,255,0.72) 0, rgba(255,255,255,0.72) 4%, transparent 5%),
        radial-gradient(ellipse at 80% 30%, rgba(255,255,255,0.60) 0, rgba(255,255,255,0.60) 4%, transparent 5%),
        radial-gradient(ellipse at 83% 28%, rgba(255,255,255,0.60) 0, rgba(255,255,255,0.60) 3%, transparent 4%),
        /* Checkerboard tile overlay */
        repeating-conic-gradient(rgba(255,255,255,0.06) 0% 25%, transparent 0% 50%) 0 0 / 32px 32px,
        /* Main sky gradient */
        linear-gradient(180deg, #5bb8e8 0%, #87CEEB 40%, #a8dff5 70%, #c8f0d0 85%, #5a9e50 100%);
    background-attachment: fixed;
}}

/* Ground strip at the very bottom */
.stApp::after {{
    content: "";
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 24px;
    background: repeating-linear-gradient(
        90deg,
        #5a9e50 0px, #5a9e50 16px,
        #4a8a40 16px, #4a8a40 32px
    );
    z-index: 0;
    pointer-events: none;
}}

.main .block-container {{
    max-width: 1320px;
    padding-top: 1.8rem;
    padding-bottom: 5rem;
    animation: floatIn 400ms ease-out;
    position: relative; z-index: 1;
}}
section.main > div {{ background: transparent; }}

/* ── Sidebar: brick wall style ── */
[data-testid="stSidebar"] {{
    background:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 15px,
            rgba(0,0,0,0.12) 15px,
            rgba(0,0,0,0.12) 16px
        ),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 31px,
            rgba(0,0,0,0.10) 31px,
            rgba(0,0,0,0.10) 32px
        ),
        linear-gradient(180deg, #d9534f 0%, #c0392b 100%) !important;
    border-right: 4px solid #8B0000 !important;
    box-shadow: 4px 0 0 #8B0000 !important;
}}
[data-testid="stSidebar"] * {{ color: #"#7f768b" !important; }}
[data-testid="stSidebar"] label {{ color: #ffe066 !important; }}

.sidebar-brand {{
    font-family: 'Inter', sans-serif;
    font-size: 0.60rem; font-weight: 400;
    color: #ffe066;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 3px solid rgba(255,255,255,0.25);
    margin-bottom: 1rem;
    line-height: 1.8;
    text-shadow: 2px 2px 0px rgba(0,0,0,0.5);
    letter-spacing: 0.05em;
}}
.sidebar-brand span {{ color: #fff8e7; }}

/* ── Headings: pixel font ── */
h1,h2,h3,h4 {{
    font-family: 'Inter', sans-serif !important;
    color: {INK} !important;
    font-weight: 400 !important;
    text-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
    text-transform: none !important;
    letter-spacing: 0.03em !important;
}}

/* ── Hero: pixel game card ── */
.hero {{
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    border-radius: 0 !important;
    padding: 1.6rem 2rem; margin-bottom: 1.4rem;
    background: #fff9e6;
    border: 4px solid {INK};
    box-shadow: var(--px-shadow-lg);
    image-rendering: pixelated;
}}

/* Pixel border decoration top */
.hero::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 8px;
    background: repeating-linear-gradient(
        90deg,
        {ACCENT} 0px, {ACCENT} 16px,
        {CHART_EXPAND} 16px, {CHART_EXPAND} 32px,
        {ACCENT_2} 32px, {ACCENT_2} 48px,
        {CHART_OPTIMIZE} 48px, {CHART_OPTIMIZE} 64px
    );
}}
/* Pixel border bottom */
.hero::after {{
    content: "";
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 8px;
    background: repeating-linear-gradient(
        90deg,
        {CHART_OPTIMIZE} 0px, {CHART_OPTIMIZE} 16px,
        {ACCENT_2} 16px, {ACCENT_2} 32px,
        {CHART_EXPAND} 32px, {CHART_EXPAND} 48px,
        {ACCENT} 48px, {ACCENT} 64px
    );
}}

.hero-star {{ display: none; }}
.hero-left,.hero-badge,.hero-glyph {{ position:relative; z-index:1; }}
.hero-left {{ flex:1; min-width:0; padding-top: 8px; }}
.hero-eyebrow {{
    font-family: 'Inter', sans-serif;
    font-size: 0.48rem; letter-spacing: 0.18em;
    color: {ACCENT};
    margin-bottom: 0.7rem;
    text-shadow: 1px 1px 0px rgba(0,0,0,0.2);
}}
.hero h1 {{
    margin: 0 0 0.5rem 0 !important;
    font-size: 1.1rem !important;
    line-height: 1.5 !important;
    color: {INK} !important;
    text-shadow: 3px 3px 0px rgba(0,0,0,0.18) !important;
    -webkit-text-fill-color: {INK} !important;
}}
.hero p {{
    margin: 0; color: {INK_SOFT} !important;
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-weight: 400 !important;
}}

.hero-badge {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.55rem 1rem;
    border: 3px solid {INK};
    background: {CHART_OPTIMIZE};
    color: {INK};
    font-family: 'Inter', sans-serif;
    font-size: 0.45rem;
    letter-spacing: 0.06em;
    box-shadow: 3px 3px 0px rgba(0,0,0,0.35);
    white-space: nowrap;
    animation: bobUp 2s ease-in-out infinite;
    border-radius: 0 !important;
    text-transform: none;
}}

.hero-glyph {{
    font-size: 2.8rem; opacity: 0.13; color: {INK};
    animation: coinFloat 4s ease-in-out infinite;
}}

/* ── Pixel airplane in hero (canvas) ── */
#pixel-plane-canvas {{
    position: absolute;
    top: 50%; left: 0;
    transform: translateY(-50%);
    width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
    image-rendering: pixelated;
}}

/* ── Metric cards: pixel block style ── */
[data-testid="metric-container"] {{
    background: #ffffff !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0px {INK} !important;
    padding: 1rem 1.1rem !important;
    transition: transform 150ms ease, box-shadow 150ms ease !important;
    position: relative; overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: "";
    position: absolute; top: 0; left: 0; right: 0;
    height: 5px;
    background: repeating-linear-gradient(
        90deg,
        {ACCENT} 0px, {ACCENT} 8px,
        {ACCENT_2} 8px, {ACCENT_2} 16px
    );
}}
[data-testid="metric-container"]:hover {{
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px {INK} !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.45rem !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0.08em !important;
    color: {INK_SOFT} !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
    color: {INK} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em !important;
    text-shadow: 2px 2px 0px rgba(0,0,0,0.12) !important;
}}

/* ── Tabs: pixel style ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.18rem;
    background: rgba(255,255,255,0.85);
    border: 3px solid {INK};
    border-radius: 0 !important;
    padding: 0.25rem;
    box-shadow: 3px 3px 0px {INK};
}}
.stTabs [data-baseweb="tab"] {{
    height: 38px; padding: 0 0.9rem !important;
    border-radius: 0 !important;
    color: {INK_MUTED} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.42rem !important;
    font-weight: 400 !important;
    background: transparent !important;
    letter-spacing: 0.03em !important;
    transition: background 120ms, color 120ms !important;
    border: 2px solid transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: {CHART_OPTIMIZE}44 !important;
    color: {INK} !important;
    border: 2px solid {INK} !important;
}}
.stTabs [aria-selected="true"] {{
    background: {ACCENT} !important;
    color: #fff8e7 !important;
    border: 2px solid {INK} !important;
    box-shadow: 2px 2px 0px rgba(0,0,0,0.3) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.4rem; }}

/* ── Section headings ── */
.section-hd {{
    font-family: 'Inter', sans-serif;
    font-size: 0.60rem;
    font-weight: 400;
    color: {INK};
    margin: 0 0 0.3rem 0;
    letter-spacing: 0.04em;
    text-shadow: 1px 1px 0px rgba(0,0,0,0.12);
}}
.section-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: {INK_MUTED};
    margin: 0 0 1rem 0;
    line-height: 1.55;
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
}}

/* ── Divider label: coin style ── */
.divider-label {{
    display: flex; align-items: center; gap: 0.7rem;
    margin: 1.5rem 0 1rem 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.42rem;
    font-weight: 400;
    letter-spacing: 0.16em;
    color: {INK};
}}
.divider-label::before, .divider-label::after {{
    content: ""; flex: 1; height: 3px;
    background: repeating-linear-gradient(
        90deg,
        {INK} 0px, {INK} 8px,
        transparent 8px, transparent 12px
    );
}}

/* ── Info box: speech bubble pixel style ── */
.info-box {{
    background: #fff9e6;
    border: 3px solid {INK};
    border-radius: 0 !important;
    padding: 1rem 1.1rem;
    color: {INK_SOFT};
    line-height: 1.75;
    box-shadow: 4px 4px 0px {INK};
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    transition: transform 150ms, box-shadow 150ms;
    position: relative;
}}
.info-box:hover {{
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px {INK};
}}

/* ── Pills: pixel badge style ── */
.pill {{
    display: inline-block;
    padding: 0.22rem 0.60rem;
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.40rem;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: none;
    border: 2px solid {INK};
    transition: transform 120ms;
    cursor: default;
    box-shadow: 2px 2px 0px rgba(0,0,0,0.3);
}}
.pill:hover {{ transform: translate(-1px, -1px); box-shadow: 3px 3px 0px rgba(0,0,0,0.3); }}
.pill-expand   {{ background: #b7e4c7; color: #1b4332; border-color: #1b4332; }}
.pill-maintain {{ background: #bde0fe; color: #023e8a; border-color: #023e8a; }}
.pill-optimize {{ background: #ffe066; color: #7c4b00; border-color: #7c4b00; }}
.pill-drop     {{ background: #ffb3ba; color: #7d0000; border-color: #7d0000; }}

/* ── Result card ── */
.result-card {{
    border-radius: 0 !important;
    padding: 1.4rem 1.5rem; margin: 1.1rem 0;
    border: 4px solid {INK};
    box-shadow: 6px 6px 0px {INK};
    animation: floatIn 300ms ease-out;
    transition: transform 200ms, box-shadow 200ms;
}}
.result-card:hover {{
    transform: translate(-3px, -3px);
    box-shadow: 9px 9px 0px {INK};
}}
.result-expand   {{ background: #b7e4c7; border-left: 8px solid {CHART_EXPAND}; }}
.result-maintain {{ background: #bde0fe; border-left: 8px solid {CHART_MAINTAIN}; }}
.result-optimize {{ background: #ffe066; border-left: 8px solid {CHART_OPTIMIZE}; }}
.result-drop     {{ background: #ffb3ba; border-left: 8px solid {CHART_DROP}; }}

/* ── Form inputs: pixel style ── */
.stSelectbox label,.stNumberInput label,.stSlider label,
.stRadio label,.stCheckbox label,.stTextInput label {{
    font-family: 'Inter', sans-serif !important;
    color: {INK_SOFT} !important;
    font-weight: 400 !important;
    font-size: 0.44rem !important;
    letter-spacing: 0.05em !important;
    text-transform: none !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input {{
    background: #ffffff !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    color: {INK} !important;
    min-height: 42px !important;
    box-shadow: 3px 3px 0px {INK} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    transition: box-shadow 120ms !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:hover, .stNumberInput input:hover {{
    box-shadow: 4px 4px 0px {INK} !important;
}}
[data-baseweb="menu"] {{
    background: #fff9e6 !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0px {INK} !important;
}}
[data-baseweb="menu"] li {{ color: {INK} !important; font-family: 'Inter', sans-serif !important; font-size: 1.1rem !important; }}
[data-baseweb="menu"] li:hover {{ background: {CHART_OPTIMIZE}88 !important; }}

/* ── Form card ── */
[data-testid="stForm"] {{
    background: rgba(255, 255, 255, 0.92) !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    padding: 1.4rem 1.5rem 1.7rem !important;
    box-shadow: 6px 6px 0px {INK} !important;
}}

/* ── Buttons: pixel press style ── */
[data-testid="stFormSubmitButton"] > button, .stButton > button {{
    border-radius: 0 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.50rem !important;
    letter-spacing: 0.06em !important;
    text-transform: none !important;
    transition: transform 80ms, box-shadow 80ms !important;
    position: relative; overflow: hidden;
    border: 3px solid {INK} !important;
}}
[data-testid="stFormSubmitButton"] > button {{
    width: 100% !important;
    background: {ACCENT} !important;
    box-shadow: 4px 4px 0px {INK} !important;
    color: white !important;
    padding: 0.7rem 0 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px {INK} !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform: translate(2px, 2px) !important;
    box-shadow: 1px 1px 0px {INK} !important;
}}
.stButton > button {{
    background: #ffffff !important;
    color: {INK} !important;
    box-shadow: 3px 3px 0px {INK} !important;
}}
.stButton > button:hover {{
    background: {CHART_OPTIMIZE} !important;
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0px {INK} !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background: rgba(255, 255, 255, 0.90) !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    overflow: hidden !important;
    box-shadow: 4px 4px 0px {INK} !important;
    transition: transform 200ms, box-shadow 200ms !important;
}}
[data-testid="stDataFrame"]:hover {{
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px {INK} !important;
}}
[data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {{ color: {INK_SOFT} !important; }}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background: {INK} !important;
    color: #ffe066 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.44rem !important;
    letter-spacing: 0.08em !important;
    text-transform: none !important;
    border-bottom: 2px solid {INK} !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
    border-bottom: 1px solid rgba(26, 26, 46, 0.12) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: rgba(255, 255, 255, 0.88) !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    box-shadow: 3px 3px 0px {INK} !important;
    transition: transform 150ms, box-shadow 150ms !important;
}}
[data-testid="stExpander"]:hover {{
    transform: translate(-1px, -1px) !important;
    box-shadow: 4px 4px 0px {INK} !important;
}}
[data-testid="stExpander"] summary p {{
    color: {INK} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.50rem !important;
    font-weight: 400 !important;
}}

/* ── Charts ── */
[data-testid="stPyplot"] {{
    background: rgba(255, 255, 255, 0.88);
    border: 3px solid {INK};
    border-radius: 0;
    padding: 0.8rem;
    box-shadow: 4px 4px 0px {INK};
    transition: transform 200ms, box-shadow 200ms;
}}
[data-testid="stPyplot"]:hover {{
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px {INK};
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 0 !important;
    background: rgba(255, 255, 255, 0.90) !important;
    border: 3px solid {INK} !important;
    box-shadow: 3px 3px 0px {INK} !important;
    color: {INK} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
}}

hr {{ border: none !important; height: 3px !important;
      background: repeating-linear-gradient(
        90deg, {INK} 0px, {INK} 8px, transparent 8px, transparent 12px
      ) !important; margin: 1.2rem 0 !important; }}

.col-label {{
    font-family: 'Inter', sans-serif;
    font-size: 0.44rem;
    font-weight: 400;
    color: {ACCENT};
    letter-spacing: 0.10em;
    text-transform: none;
    margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
}}
.col-label::after {{
    content: ""; flex: 1; height: 3px;
    background: repeating-linear-gradient(
        90deg, {ACCENT} 0px, {ACCENT} 6px, transparent 6px, transparent 9px
    );
}}

/* Slider: pixel thumb */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background: {ACCENT} !important;
    border: 3px solid {INK} !important;
    border-radius: 0 !important;
    box-shadow: 2px 2px 0px {INK} !important;
    width: 20px !important; height: 20px !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
    background: {ACCENT} !important;
    height: 6px !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child {{
    height: 6px !important;
    background: rgba(26,26,46,0.2) !important;
    border-radius: 0 !important;
}}

/* Scrollbar: chunky pixel */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: #c8f0d0; border: 2px solid {INK}; }}
::-webkit-scrollbar-thumb {{ background: {ACCENT}; border: 2px solid {INK}; border-radius: 0; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT_DK}; }}
::selection {{ background: {CHART_OPTIMIZE}; color: {INK}; }}

/* ── Airplane cursor canvas ── */
#airplane-canvas {{
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none; z-index: 999999;
    image-rendering: pixelated;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  GLASSMORPHISM + MOTION WEBSITE OVERRIDE
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {{
    --bg-0: #07111f;
    --bg-1: #0b1730;
    --glass: rgba(255,255,255,0.105);
    --glass-strong: rgba(255,255,255,0.16);
    --glass-border: rgba(255,255,255,0.26);
    --text: #f7fbff;
    --muted: rgba(226,236,255,0.72);
    --cyan: #67e8f9;
    --blue: #60a5fa;
    --violet: #a78bfa;
    --pink: #f0abfc;
    --green: #86efac;
    --warning: #fde68a;
    --danger: #fca5a5;
    --radius-xl: 28px;
    --radius-lg: 22px;
    --shadow-soft: 0 24px 80px rgba(0,0,0,.38);
}}

html {{
    scroll-behavior: smooth;
}}

body, .stApp {{
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--text) !important;
    background:
        radial-gradient(circle at 12% 16%, rgba(103,232,249,.30), transparent 28%),
        radial-gradient(circle at 84% 4%, rgba(167,139,250,.32), transparent 30%),
        radial-gradient(circle at 74% 86%, rgba(240,171,252,.22), transparent 30%),
        linear-gradient(135deg, var(--bg-0) 0%, var(--bg-1) 52%, #111827 100%) !important;
    background-attachment: fixed !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
        linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px);
    background-size: 52px 52px;
    mask-image: radial-gradient(circle at 50% 15%, black, transparent 72%);
}}

.stApp::after {{
    content: "";
    position: fixed;
    width: 42rem;
    height: 42rem;
    right: -16rem;
    top: 12rem;
    border-radius: 999px;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(circle, rgba(96,165,250,.20), transparent 63%);
    filter: blur(12px);
    animation: orbDrift 14s ease-in-out infinite alternate;
}}

@keyframes orbDrift {{
    from {{ transform: translate3d(0,0,0) scale(1); }}
    to {{ transform: translate3d(-8vw,7vh,0) scale(1.12); }}
}}
@keyframes floatUp {{
    from {{ opacity: 0; transform: translateY(24px) scale(.98); filter: blur(8px); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
}}
@keyframes softGlow {{
    0%,100% {{ box-shadow: 0 24px 80px rgba(0,0,0,.34), 0 0 0 1px rgba(255,255,255,.20) inset; }}
    50% {{ box-shadow: 0 28px 100px rgba(96,165,250,.25), 0 0 0 1px rgba(255,255,255,.30) inset; }}
}}
@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
@keyframes shimmerLine {{
    from {{ transform: translateX(-130%); }}
    to {{ transform: translateX(130%); }}
}}

.block-container {{
    max-width: 1320px !important;
    padding-top: 2.2rem !important;
    position: relative;
    z-index: 1;
}}

h1,h2,h3,h4,p,span,div,label {{
    font-family: 'Inter', system-ui, sans-serif !important;
    text-shadow: none !important;
}}

h1,h2,h3,h4, .section-hd {{
    color: #ffffff !important;
    letter-spacing: -0.035em !important;
    font-weight: 800 !important;
}}

p, .section-sub, .stMarkdown, [data-testid="stMetricDelta"], [data-testid="stMetricValue"] {{
    color: var(--muted) !important;
}}

.hero {{
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.4rem;
    margin-bottom: 1.6rem;
    padding: clamp(1.7rem, 4vw, 3.2rem) !important;
    border-radius: 34px !important;
    border: 1px solid rgba(255,255,255,.24) !important;
    background:
        linear-gradient(135deg, rgba(255,255,255,.18), rgba(255,255,255,.07)),
        radial-gradient(circle at 20% 10%, rgba(103,232,249,.30), transparent 34%),
        radial-gradient(circle at 84% 18%, rgba(240,171,252,.22), transparent 38%) !important;
    backdrop-filter: blur(24px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(170%) !important;
    box-shadow: var(--shadow-soft) !important;
    animation: floatUp .9s ease both, softGlow 6s ease-in-out infinite !important;
}}
.hero canvas {{ display: none !important; }}
.hero::before {{
    content: "";
    position: absolute;
    inset: -2px;
    background: linear-gradient(115deg, transparent 18%, rgba(255,255,255,.34), transparent 42%);
    transform: translateX(-130%);
    animation: shimmerLine 5.8s ease-in-out infinite;
}}
.hero::after {{
    content: "";
    position: absolute;
    right: -8rem;
    top: -8rem;
    width: 22rem;
    height: 22rem;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(103,232,249,.30), transparent 60%);
    filter: blur(4px);
}}
.hero h1 {{
    font-size: clamp(2.4rem, 6vw, 5.9rem) !important;
    line-height: .9 !important;
    margin: 0 0 1rem !important;
    background: linear-gradient(90deg, #fff, #c7f9ff, #d8b4fe, #fff);
    background-size: 240% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent !important;
    animation: gradientShift 8s ease infinite;
}}
.hero p {{
    font-size: 1rem !important;
    color: rgba(240,247,255,.76) !important;
    max-width: 680px;
}}
.hero-eyebrow, .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    width: fit-content;
    border-radius: 999px !important;
    padding: .55rem .85rem !important;
    font-size: .72rem !important;
    font-weight: 800 !important;
    letter-spacing: .11em !important;
    color: #e0faff !important;
    border: 1px solid rgba(255,255,255,.28) !important;
    background: rgba(255,255,255,.11) !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: none !important;
}}
.hero-glyph {{
    font-size: clamp(3.2rem, 10vw, 8rem) !important;
    color: rgba(255,255,255,.52) !important;
    animation: orbDrift 7s ease-in-out infinite alternate;
}}

[data-testid="stSidebar"] {{
    background: rgba(5,12,24,.58) !important;
    border-right: 1px solid rgba(255,255,255,.16) !important;
    backdrop-filter: blur(24px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(170%) !important;
    box-shadow: 20px 0 60px rgba(0,0,0,.22) !important;
}}
[data-testid="stSidebar"] * {{
    color: rgba(245,250,255,.88) !important;
}}
.sidebar-brand {{
    color: #fff !important;
    border-bottom: 1px solid rgba(255,255,255,.14) !important;
    font-weight: 900 !important;
    letter-spacing: -.01em !important;
}}

div[data-testid="stVerticalBlock"] > div,
.info-box, .result-card,
.gi-chart, .gi-hchart, .gi-pie-card, .gi-classic-card {{
    border-radius: var(--radius-lg) !important;
}}

.info-box, .result-card,
[data-testid="stMetric"],
.gi-chart, .gi-hchart, .gi-pie-card, .gi-classic-card,
.stDataFrame, div[data-testid="stExpander"] {{
    background: linear-gradient(135deg, rgba(255,255,255,.15), rgba(255,255,255,.065)) !important;
    border: 1px solid rgba(255,255,255,.20) !important;
    box-shadow: 0 18px 60px rgba(0,0,0,.22) !important;
    backdrop-filter: blur(20px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(160%) !important;
    animation: floatUp .75s ease both;
}}

.section-hd {{
    font-size: clamp(1.2rem, 2.2vw, 2rem) !important;
    margin-top: .4rem !important;
}}
.section-sub {{
    font-size: .98rem !important;
    line-height: 1.7 !important;
}}

.divider-label {{
    color: rgba(255,255,255,.85) !important;
    letter-spacing: .14em !important;
    font-size: .72rem !important;
    margin: 1.8rem 0 1rem !important;
}}
.divider-label::before, .divider-label::after {{
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.38), transparent) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: .65rem !important;
    padding: .45rem !important;
    border-radius: 999px !important;
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.16) !important;
    backdrop-filter: blur(18px) !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 999px !important;
    border: 1px solid transparent !important;
    color: rgba(245,250,255,.72) !important;
    font-weight: 800 !important;
    transition: transform .25s ease, background .25s ease, color .25s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    transform: translateY(-2px);
    background: rgba(255,255,255,.12) !important;
    color: #fff !important;
}}
.stTabs [aria-selected="true"] {{
    color: #07111f !important;
    background: linear-gradient(135deg, #67e8f9, #c084fc) !important;
    border: 1px solid rgba(255,255,255,.45) !important;
}}

.stButton > button, .stDownloadButton > button {{
    border: 0 !important;
    border-radius: 999px !important;
    color: #07111f !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #67e8f9, #a78bfa, #f0abfc) !important;
    background-size: 220% 220% !important;
    box-shadow: 0 18px 40px rgba(103,232,249,.18) !important;
    transition: transform .25s ease, box-shadow .25s ease !important;
    animation: gradientShift 7s ease infinite;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 24px 60px rgba(167,139,250,.28) !important;
}}

.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input, .stTextInput input, .stSlider, textarea {{
    border-radius: 16px !important;
    background: rgba(255,255,255,.10) !important;
    border-color: rgba(255,255,255,.20) !important;
    color: #fff !important;
}}

.pill {{
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,.24) !important;
    box-shadow: none !important;
    color: #07111f !important;
    font-weight: 900 !important;
}}
.pill-expand {{ background: linear-gradient(135deg, #86efac, #67e8f9) !important; }}
.pill-maintain {{ background: linear-gradient(135deg, #93c5fd, #a78bfa) !important; }}
.pill-optimize {{ background: linear-gradient(135deg, #fde68a, #f0abfc) !important; }}
.pill-drop {{ background: linear-gradient(135deg, #fca5a5, #f0abfc) !important; }}

.result-card {{
    border-left: 1px solid rgba(255,255,255,.20) !important;
}}
.result-expand, .result-maintain, .result-optimize, .result-drop {{
    background: linear-gradient(135deg, rgba(255,255,255,.17), rgba(255,255,255,.07)) !important;
}}

.gi-chart-title, .gi-hchart-title, .gi-pie-title, .gi-classic-title,
.gi-value, .gi-hvalue, .gi-classic-value, .gi-xlabel, .gi-hlabel, .gi-pie-pct {{
    color: rgba(255,255,255,.88) !important;
}}
.gi-bar, .gi-hbar, .gi-classic-bar {{
    border-radius: 999px !important;
    box-shadow: 0 0 34px rgba(103,232,249,.18) !important;
}}

[data-testid="stDataFrame"] {{
    border-radius: 20px !important;
    overflow: hidden !important;
}}

footer, header {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}

@media (max-width: 760px) {{
    .hero {{
        flex-direction: column;
        align-items: flex-start;
    }}
    .hero-glyph {{
        position: absolute;
        right: 1rem;
        bottom: 1rem;
        opacity: .28;
    }}
}}
</style>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────
#  MOTION BACKDROP NOTE
#  Cursor canvas removed for a cleaner motion-site experience.
#  The glassmorphism / animation layer below handles visual motion.
# ─────────────────────────────────────────────────────────────

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
#  CHART HELPERS
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#ffffff")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=INK_MUTED, labelsize=8.5, length=0)
    ax.xaxis.label.set_color(INK_SOFT)
    ax.yaxis.label.set_color(INK_SOFT)
    ax.title.set_color(INK)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    ax.grid(axis="y", color="#cccccc", linewidth=1.0, linestyle="--", alpha=0.70)
    ax.set_axisbelow(True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(INK_MUTED)
    return fig, ax


def col_seq(labels):
    return [DECISION_COLORS.get(l, ACCENT) for l in labels]


def add_bar_shimmer(bars, ax, alpha=0.92):
    for bar in bars:
        bar.set_alpha(alpha)
        bar.set_linewidth(0)
    return bars


# ─────────────────────────────────────────────────────────────
#  PIXEL HTML CHART HELPERS
# ─────────────────────────────────────────────────────────────
def _fmt_chart_value(v, value_format="number"):
    if value_format == "percent":
        return f"{v:.0%}"
    if value_format == "money":
        return f"${v:,.0f}"
    return f"{v:,.0f}"


def shimmer_vertical_bar_chart(title, labels, series, max_value=None, value_format="number", height=430):
    labels = [str(x) for x in labels]
    clean_series = []
    all_values = []

    for s in series:
        vals = [float(x) if pd.notna(x) else 0.0 for x in s.get("values", [])]
        all_values.extend(vals)
        clean_series.append({
            "name": str(s.get("name", "Value")),
            "values": vals,
            "color": s.get("color", ACCENT),
            "colors": s.get("colors", None),
        })

    if not all_values:
        st.info("No chart data available for the current filter.")
        return

    if max_value is None:
        max_value = max(all_values) if max(all_values) != 0 else 1
    max_value = float(max_value) if max_value else 1.0

    chart = {
        "title": title,
        "labels": labels,
        "series": clean_series,
        "max_value": max_value,
        "value_format": value_format,
    }
    chart_json = json.dumps(chart)

    components.html(f"""
    <div id="gi-chart-root"></div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
    .gi-chart {{
        width:100%; min-height:{height}px; box-sizing:border-box;
        padding:22px 24px 20px;
        background:#fff9e6;
        border:3px solid #1a1a2e;
        box-shadow:5px 5px 0px #1a1a2e;
        font-family:'VT323',monospace; color:#1a1a2e; overflow:hidden; position:relative;
    }}
    .gi-chart::before {{
        content:""; position:absolute; top:0; left:0; right:0; height:7px;
        background:repeating-linear-gradient(90deg,{ACCENT} 0px,{ACCENT} 14px,{CHART_EXPAND} 14px,{CHART_EXPAND} 28px,{ACCENT_2} 28px,{ACCENT_2} 42px,{CHART_OPTIMIZE} 42px,{CHART_OPTIMIZE} 56px);
    }}
    .gi-chart-title {{
        font-family:'Press Start 2P',monospace;
        text-align:center; font-size:12px; line-height:1.4; color:#1a1a2e;
        margin-bottom:16px; margin-top:10px; letter-spacing:0.03em;
    }}
    .gi-legend {{ display:flex; justify-content:center; gap:18px; margin-bottom:18px; flex-wrap:wrap; }}
    .gi-legend-item {{ display:flex; align-items:center; gap:7px; color:#2c3e50; font-size:16px; }}
    .gi-legend-color {{ width:18px; height:12px; border:2px solid #1a1a2e; image-rendering:pixelated; }}
    .gi-plot {{
        display:grid;
        grid-template-columns:repeat({max(len(labels),1)}, minmax(0,1fr));
        gap:24px; align-items:end;
        height:{max(height-175,190)}px;
        border-bottom:3px solid #1a1a2e;
        background-image:repeating-linear-gradient(to top, rgba(26,26,46,0.10) 1px, transparent 1px);
        background-size:100% 25%;
        padding:0 14px; position:relative; z-index:1;
    }}
    .gi-group {{ height:100%; display:flex; align-items:end; justify-content:center; gap:8px; position:relative; }}
    .gi-bar-wrap {{ height:100%; width:min(44px,28%); min-width:22px; display:flex; align-items:end; justify-content:center; position:relative; }}
    .gi-bar {{
        width:100%; height:var(--bar-height); min-height:3px;
        border:2px solid #1a1a2e;
        position:relative; overflow:hidden;
        box-shadow:3px 3px 0px #1a1a2e;
        animation:pixGrow 700ms steps(14,end) both;
        image-rendering:pixelated;
    }}
    .gi-bar::after {{
        content:""; position:absolute; top:0; left:0; right:0;
        height:6px; background:rgba(255,255,255,0.45);
    }}
    .gi-value {{
        position:absolute; bottom:calc(var(--bar-height) + 8px);
        font-size:15px; font-weight:bold; color:#1a1a2e; white-space:nowrap;
    }}
    .gi-xlabels {{
        display:grid;
        grid-template-columns:repeat({max(len(labels),1)}, minmax(0,1fr));
        gap:24px; padding:10px 14px 0; text-align:center; position:relative; z-index:1;
    }}
    .gi-xlabel {{ color:#2c3e50; font-family:'Press Start 2P',monospace; font-size:8px; line-height:1.4; }}
    @keyframes pixGrow {{
        from {{ height:0%; }} to {{ height:var(--bar-height); }}
    }}
    </style>
    <script>
    const chart = {chart_json};
    function formatValue(v) {{
        if (chart.value_format==="percent") return Math.round(v*100)+"%";
        if (chart.value_format==="money") return "$"+Math.round(v).toLocaleString();
        return Math.round(v).toLocaleString();
    }}
    const root = document.getElementById("gi-chart-root");
    const legendHtml = chart.series.map(s=>`
        <div class="gi-legend-item">
            <span class="gi-legend-color" style="background:${{s.color}}"></span>
            ${{s.name}}
        </div>`).join("");
    const groupsHtml = chart.labels.map((label,i)=>`
        <div class="gi-group">
            ${{chart.series.map((s,j)=>{{
                const value=Number(s.values[i]||0);
                const pct=Math.max(2,Math.min(100,value/chart.max_value*100));
                const color=s.colors?s.colors[i]:s.color;
                return `<div class="gi-bar-wrap">
                    <div class="gi-value" style="--bar-height:${{pct}}%">${{formatValue(value)}}</div>
                    <div class="gi-bar" style="--bar-height:${{pct}}%;background:${{color}};animation-delay:${{(i+j)*80}}ms;"></div>
                </div>`;
            }}).join("")}}
        </div>`).join("");
    const xLabelsHtml = chart.labels.map(label=>`<div class="gi-xlabel">${{label}}</div>`).join("");
    root.innerHTML=`<div class="gi-chart">
        <div class="gi-chart-title">${{chart.title}}</div>
        <div class="gi-legend">${{legendHtml}}</div>
        <div class="gi-plot">${{groupsHtml}}</div>
        <div class="gi-xlabels">${{xLabelsHtml}}</div>
    </div>`;
    </script>
    """, height=height + 40, scrolling=False)


def shimmer_horizontal_bar_chart(title, labels, values, colors=None, value_format="number", height=430):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    if not values:
        st.info("No chart data available for the current filter.")
        return

    if colors is None:
        colors = [ACCENT for _ in values]
    elif isinstance(colors, str):
        colors = [colors for _ in values]
    else:
        colors = list(colors)

    max_abs = max(abs(v) for v in values) or 1.0
    rows = []
    for label, value, color in zip(labels, values, colors):
        rows.append({
            "label": label,
            "value": value,
            "display": _fmt_chart_value(value, value_format),
            "width": max(2, min(100, abs(value) / max_abs * 100)),
            "color": color,
        })

    chart = {"title": title, "rows": rows}
    chart_json = json.dumps(chart)

    components.html(f"""
    <div id="gi-hbar-root"></div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
    .gi-hchart {{
        width:100%; min-height:{height}px; box-sizing:border-box;
        padding:22px 24px;
        background:#fff9e6;
        border:3px solid #1a1a2e;
        box-shadow:5px 5px 0px #1a1a2e;
        font-family:'VT323',monospace; color:#1a1a2e; overflow:hidden; position:relative;
    }}
    .gi-hchart::before {{
        content:""; position:absolute; top:0; left:0; right:0; height:7px;
        background:repeating-linear-gradient(90deg,{CHART_OPTIMIZE} 0px,{CHART_OPTIMIZE} 14px,{ACCENT_2} 14px,{ACCENT_2} 28px,{CHART_EXPAND} 28px,{CHART_EXPAND} 42px,{ACCENT} 42px,{ACCENT} 56px);
    }}
    .gi-hchart-title {{
        font-family:'Press Start 2P',monospace;
        text-align:center; font-size:12px; line-height:1.4; color:#1a1a2e;
        margin-bottom:18px; margin-top:10px;
    }}
    .gi-hrows {{ display:flex; flex-direction:column; gap:11px; position:relative; z-index:1; }}
    .gi-hrow {{ display:grid; grid-template-columns:minmax(80px,155px) 1fr minmax(65px,95px); align-items:center; gap:10px; }}
    .gi-hlabel {{ color:#2c3e50; font-size:15px; font-weight:bold; line-height:1.1; text-align:right; }}
    .gi-htrack {{ height:20px; background:rgba(26,26,46,0.09); border:2px solid #1a1a2e; overflow:hidden; position:relative; }}
    .gi-hbar {{
        height:100%; width:var(--bar-width);
        position:relative; overflow:hidden;
        border-right:2px solid #1a1a2e;
        box-shadow:inset 0 4px 0 rgba(255,255,255,0.40);
        animation:pixHGrow 700ms steps(14,end) both;
        animation-delay:var(--delay);
        image-rendering:pixelated;
    }}
    .gi-hvalue {{ color:#1a1a2e; font-weight:bold; font-size:15px; white-space:nowrap; }}
    @keyframes pixHGrow {{ from {{ width:0%; }} to {{ width:var(--bar-width); }} }}
    </style>
    <script>
    const chart = {chart_json};
    const root = document.getElementById("gi-hbar-root");
    const rowsHtml = chart.rows.map((r,i)=>`
        <div class="gi-hrow">
            <div class="gi-hlabel">${{r.label}}</div>
            <div class="gi-htrack">
                <div class="gi-hbar" style="--bar-width:${{r.width}}%;--delay:${{i*90}}ms;background:${{r.color}};"></div>
            </div>
            <div class="gi-hvalue">${{r.display}}</div>
        </div>`).join("");
    root.innerHTML=`<div class="gi-hchart">
        <div class="gi-hchart-title">${{chart.title}}</div>
        <div class="gi-hrows">${{rowsHtml}}</div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_pie_chart(title, labels, values, colors=None, height=430):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    total = sum(values)
    if not values or total <= 0:
        st.info("No chart data available for the current filter.")
        return

    if colors is None:
        colors = [ACCENT for _ in values]
    else:
        colors = list(colors)

    rows = []
    start = 0.0
    stops = []
    for label, value, color in zip(labels, values, colors):
        pct = value / total * 100
        end = start + pct
        stops.append(f"{color} {start:.4f}% {end:.4f}%")
        rows.append({
            "label": label,
            "value": value,
            "pct": pct,
            "display": f"{pct:.1f}%",
            "color": color,
        })
        start = end

    chart = {
        "title": title,
        "gradient": ", ".join(stops),
        "rows": rows,
        "total": total,
    }
    chart_json = json.dumps(chart)

    components.html(f"""
    <div id="gi-pie-root"></div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
    .gi-pie-card {{
        width:100%; min-height:{height}px; box-sizing:border-box;
        padding:22px 24px;
        background:#fff9e6;
        border:3px solid #1a1a2e;
        box-shadow:5px 5px 0px #1a1a2e;
        font-family:'VT323',monospace; color:#1a1a2e; overflow:hidden; position:relative;
    }}
    .gi-pie-card::before {{
        content:""; position:absolute; top:0; left:0; right:0; height:7px;
        background:repeating-linear-gradient(90deg,{ACCENT} 0px,{ACCENT} 14px,{CHART_EXPAND} 14px,{CHART_EXPAND} 28px,{ACCENT_2} 28px,{ACCENT_2} 42px,{CHART_OPTIMIZE} 42px,{CHART_OPTIMIZE} 56px);
    }}
    .gi-pie-title {{
        font-family:'Press Start 2P',monospace;
        text-align:center; font-size:12px; line-height:1.4; color:#1a1a2e;
        margin-bottom:16px; margin-top:10px;
    }}
    .gi-pie-layout {{
        display:grid; grid-template-columns:minmax(200px,0.9fr) minmax(180px,1fr);
        gap:22px; align-items:center; position:relative; z-index:1;
    }}
    .gi-donut-wrap {{ display:flex; align-items:center; justify-content:center; }}
    .gi-donut {{
        width:min(210px,75vw); aspect-ratio:1; border-radius:0 !important;
        background:conic-gradient(var(--pie-gradient));
        position:relative;
        border:4px solid #1a1a2e;
        box-shadow:5px 5px 0px #1a1a2e;
        image-rendering:pixelated;
        animation:pixDonut 800ms steps(16,end) both;
    }}
    .gi-donut::after {{
        content:""; position:relative; inset:25%;
        background:#fff9e6;
        border:3px solid #1a1a2e;
    }}
    .gi-pie-legend {{ display:flex; flex-direction:column; gap:10px; }}
    .gi-pie-row {{
        display:grid; grid-template-columns:16px 1fr auto;
        align-items:center; gap:9px; color:#2c3e50; font-size:16px;
    }}
    .gi-pie-dot {{ width:14px; height:14px; border:2px solid #1a1a2e; image-rendering:pixelated; }}
    .gi-pie-pct {{ color:#1a1a2e; font-weight:bold; white-space:nowrap; }}
    @keyframes pixDonut {{ from {{ transform:scale(0.5); opacity:0; }} to {{ transform:scale(1); opacity:1; }} }}
    </style>
    <script>
    const pieChart = {chart_json};
    const root = document.getElementById("gi-pie-root");
    const rowsHtml = pieChart.rows.map(r=>`
        <div class="gi-pie-row">
            <span class="gi-pie-dot" style="background:${{r.color}}"></span>
            <span>${{r.label}}</span>
            <span class="gi-pie-pct">${{r.display}}</span>
        </div>`).join("");
    root.innerHTML=`<div class="gi-pie-card">
        <div class="gi-pie-title">${{pieChart.title}}</div>
        <div class="gi-pie-layout">
            <div class="gi-donut-wrap">
                <div class="gi-donut" style="--pie-gradient:${{pieChart.gradient}}"></div>
            </div>
            <div class="gi-pie-legend">${{rowsHtml}}</div>
        </div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_classic_horizontal_bar_chart(title, labels, values, color=ACCENT, value_format="money", height=460):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    if not values:
        st.info("No chart data available for the current filter.")
        return

    max_abs = max(abs(v) for v in values) or 1.0
    rows = [{
        "label": lab,
        "value": val,
        "display": _fmt_chart_value(val, value_format),
        "width": max(2, min(100, abs(val) / max_abs * 100)),
    } for lab, val in zip(labels, values)]

    chart_json = json.dumps({"title": title, "rows": rows, "color": color})

    components.html(f"""
    <div id="gi-classic-hbar-root"></div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
    .gi-classic-card {{
        width:100%; min-height:{height}px; box-sizing:border-box;
        padding:22px 24px 20px;
        background:transparent;
        font-family:'VT323',monospace; color:#1a1a2e; overflow:hidden; position:relative;
    }}
    .gi-classic-title {{
        font-family:'Press Start 2P',monospace;
        text-align:center; font-size:12px; line-height:1.4; color:#1a1a2e;
        margin-bottom:16px;
    }}
    .gi-classic-rows {{ display:flex; flex-direction:column; gap:10px; }}
    .gi-classic-row {{ display:grid; grid-template-columns:minmax(80px,145px) 1fr minmax(80px,105px); align-items:center; gap:10px; }}
    .gi-classic-label {{ color:#2c3e50; font-size:15px; font-weight:bold; line-height:1.1; text-align:right; }}
    .gi-classic-axis {{
        height:20px; position:relative;
        border-bottom:2px solid #1a1a2e;
        background-image:repeating-linear-gradient(to right,rgba(26,26,46,0.10) 1px,transparent 1px);
        background-size:25% 100%;
    }}
    .gi-classic-bar {{
        height:20px; width:var(--bar-width);
        border:2px solid #1a1a2e;
        position:relative; overflow:hidden;
        background:var(--bar-color);
        box-shadow:2px 2px 0px #1a1a2e, inset 0 3px 0 rgba(255,255,255,0.40);
        animation:pixClassicGrow 700ms steps(14,end) both;
        animation-delay:var(--delay);
        image-rendering:pixelated;
    }}
    .gi-classic-value {{ color:#1a1a2e; font-weight:bold; font-size:15px; white-space:nowrap; }}
    @keyframes pixClassicGrow {{ from {{ width:0%; }} to {{ width:var(--bar-width); }} }}
    </style>
    <script>
    const classicChart = {chart_json};
    const root = document.getElementById("gi-classic-hbar-root");
    const rowsHtml = classicChart.rows.map((r,i)=>`
        <div class="gi-classic-row">
            <div class="gi-classic-label">${{r.label}}</div>
            <div class="gi-classic-axis">
                <div class="gi-classic-bar" style="--bar-width:${{r.width}}%;--bar-color:${{classicChart.color}};--delay:${{i*90}}ms;"></div>
            </div>
            <div class="gi-classic-value">${{r.display}}</div>
        </div>`).join("");
    root.innerHTML=`<div class="gi-classic-card">
        <div class="gi-classic-title">${{classicChart.title}}</div>
        <div class="gi-classic-rows">${{rowsHtml}}</div>
    </div>`;
    </script>
    """, height=height + 30, scrolling=False)


# ─────────────────────────────────────────────────────────────
#  LOAD
# ─────────────────────────────────────────────────────────────
df = load_data()
model1, model2, model3, X1_columns, X2_columns, X3_columns = load_artifacts()


# ─────────────────────────────────────────────────────────────
#  PRE-COMPUTED
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
    st.markdown('<div class="sidebar-brand">✈ AIRLINE<br>ROUTE<br>INTEL</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-family:Inter, sans-serif;font-size:0.44rem;color:#ffe066;"
        "margin-bottom:14px;letter-spacing:0.12em;'>FILTER</p>",
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
    <p style='font-family:Inter, sans-serif;font-size:0.42rem;color:#ffe066;
    margin-bottom:10px;letter-spacing:0.12em;'>LEGEND</p>
    <div style='display:flex;flex-direction:column;gap:8px;font-family:Inter, sans-serif;font-size:1rem;color:#fff8e7;'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-expand'>EXPAND</span>High profit &amp; demand
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-maintain'>MAINTAIN</span>Stable performer
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-optimize'>OPTIMIZE</span>Room to improve
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-drop'>DROP</span>Losing money
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
#  HERO — pixel airplane animates across
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <canvas id="pixel-plane-canvas" width="900" height="90" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;image-rendering:pixelated;"></canvas>
  <div class="hero-left" style="position:relative;z-index:2;">
    <div class="hero-eyebrow">★ ROUTE INTELLIGENCE PLATFORM ★</div>
    <h1>AIRLINE<br>PROFITABILITY<br>SYSTEM</h1>
    <p>Sample airline dataset · for analysis &amp; demonstration only</p>
  </div>
  <div class="hero-badge" style="position:relative;z-index:2;">⚡ ML-POWERED</div>
  <div class="hero-glyph" style="position:relative;z-index:2;">✈</div>
</div>

<script>
(function() {
    const canvas = document.getElementById('pixel-plane-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    let planeX = -60;
    const planeY = canvas.height / 2;

    // Coin-yellow color trail blocks
    const trailColors = ['#e9c46a','#f4a261','#e63946','#2d6a4f','#1d6a96'];
    const trail = [];

    function drawPixelPlane(x, y) {
        const S = 4;
        const pixels = [
            [0,-5,'#ffffff'],[0,-4,'#ffffff'],[0,-3,'#a8d8f0'],[0,-2,'#ffffff'],
            [0,-1,'#ffffff'],[0,0,'#ffffff'],[0,1,'#ffffff'],
            [-1,-4,'#1a1a2e'],[-1,-3,'#1a1a2e'],[-1,-2,'#1a1a2e'],[-1,-1,'#1a1a2e'],[-1,0,'#1a1a2e'],
            [1,-4,'#1a1a2e'],[1,-3,'#1a1a2e'],[1,-2,'#1a1a2e'],[1,-1,'#1a1a2e'],[1,0,'#1a1a2e'],
            [0,-6,'#e0e0e0'],
            [-4,0,'#1d6a96'],[-3,0,'#1d6a96'],[-2,0,'#1d6a96'],
            [2,0,'#1d6a96'],[3,0,'#1d6a96'],[4,0,'#1d6a96'],
            [-4,-1,'#1d6a96'],[-3,-1,'#1d6a96'],
            [3,-1,'#1d6a96'],[4,-1,'#1d6a96'],
            [-5,0,'#1a1a2e'],[5,0,'#1a1a2e'],
            [-4,1,'#1a1a2e'],[-3,1,'#1a1a2e'],[3,1,'#1a1a2e'],[4,1,'#1a1a2e'],
            [-1,2,'#e63946'],[1,2,'#e63946'],
            [-1,3,'#1a1a2e'],[1,3,'#1a1a2e'],
        ];
        pixels.forEach(([col, row, color]) => {
            ctx.fillStyle = color;
            ctx.fillRect(Math.round(x + col*S - S/2), Math.round(y + row*S - S/2), S, S);
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Trail blocks
        trail.push({x: planeX, y: planeY + (Math.sin(planeX * 0.04) * 8), color: trailColors[Math.floor(planeX/12) % trailColors.length]});
        if (trail.length > 18) trail.shift();

        trail.forEach((t, i) => {
            const alpha = i / trail.length;
            ctx.globalAlpha = alpha * 0.7;
            ctx.fillStyle = t.color;
            const sz = Math.round(3 + alpha * 5);
            ctx.fillRect(Math.round(t.x) - sz/2, Math.round(t.y) - sz/2, sz, sz);
        });
        ctx.globalAlpha = 1;

        // Subtle sine wave path for the plane
        const bobY = planeY + Math.sin(planeX * 0.04) * 8;
        drawPixelPlane(Math.round(planeX), Math.round(bobY));

        planeX += 1.8;
        if (planeX > canvas.width + 80) planeX = -80;

        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
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

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="divider-label">★ COMPOSITION ★</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<p class="section-hd">Decision mix</p>', unsafe_allow_html=True)
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {
            "Expand":   CHART_EXPAND,
            "Maintain": CHART_MAINTAIN,
            "Optimize": CHART_OPTIMIZE,
            "Drop":     CHART_DROP,
        }
        wedge_colors = [wc[l] for l in dc.index]
        shimmer_pie_chart(
            title="Share of Flights by Decision",
            labels=dc.index.tolist(),
            values=dc.values.tolist(),
            colors=wedge_colors,
            height=390,
        )

    with right:
        st.markdown('<p class="section-hd">Average metrics by decision</p>', unsafe_allow_html=True)
        summary = (
            fdf.groupby("Route_Decision")[["Profit", "Profit_Margin", "Load_Factor"]]
            .mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .round(3).reset_index()
            .rename(columns={
                "Route_Decision": "Decision",
                "Profit": "Avg Profit ($)",
                "Profit_Margin": "Avg Margin",
                "Load_Factor": "Avg Load Factor",
            })
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown(f"""
        <div class="info-box">
          <strong style="color:{ACCENT}">HOW TO READ THIS</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:{CHART_EXPAND}">EXPAND</strong> routes should have the highest values across all three columns.
        </div>""", unsafe_allow_html=True)


# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown('<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        apd = (fdf.groupby("Route_Decision")["Profit"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        shimmer_horizontal_bar_chart(
            title="Average Profit by Decision",
            labels=apd.index.tolist(),
            values=apd.values.tolist(),
            colors=col_seq(apd.index.tolist()),
            value_format="money",
            height=350,
        )

    with right:
        ald = (fdf.groupby("Route_Decision")["Load_Factor"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        shimmer_vertical_bar_chart(
            title="Seat Occupancy by Decision",
            labels=ald.index.tolist(),
            series=[{
                "name": "Average Seat Occupancy",
                "values": ald.values.tolist(),
                "color": ACCENT,
                "colors": col_seq(ald.index.tolist()),
            }],
            max_value=1.0,
            value_format="percent",
            height=350,
        )

    st.markdown('<div class="divider-label">★ COST BREAKDOWN ★</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Where is the money going?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">The biggest cost components across all filtered flights.</p>', unsafe_allow_html=True)

    cost_cols = [
        "Fuel_Cost", "Maintenance_Cost", "Crew_Cost", "Depreciation_Cost", "Insurance_Cost",
        "Airport_Fees", "Catering_Cost", "Handling_Cost", "Navigation_Fees",
        "Sales_Distribution_Cost", "Passenger_Service_Cost", "Overhead_Cost",
        "Marketing_Cost", "IT_Systems_Cost",
    ]
    avail_costs = [c for c in cost_cols if c in fdf.columns]
    cost_means  = fdf[avail_costs].mean().sort_values(ascending=True).tail(8)
    label_map = {
        "Fuel_Cost": "Fuel", "Maintenance_Cost": "Maintenance", "Crew_Cost": "Crew",
        "Depreciation_Cost": "Depreciation", "Insurance_Cost": "Insurance",
        "Airport_Fees": "Airport Fees", "Catering_Cost": "Catering", "Handling_Cost": "Handling",
        "Navigation_Fees": "Navigation", "Sales_Distribution_Cost": "Sales & Dist.",
        "Passenger_Service_Cost": "Pax Service", "Overhead_Cost": "Overhead",
        "Marketing_Cost": "Marketing", "IT_Systems_Cost": "IT Systems",
    }
    cost_means.index = [label_map.get(i, i) for i in cost_means.index]

    nc = len(cost_means)
    jewel_ramp = [
        CHART_EXPAND, ACCENT_2, ACCENT, CHART_MAINTAIN,
        "#15803d", CHART_OPTIMIZE, CHART_DROP, "#6a4c93",
    ]
    neutral_cols = jewel_ramp[:nc]

    shimmer_horizontal_bar_chart(
        title="Top Cost Drivers",
        labels=cost_means.index.tolist(),
        values=cost_means.values.tolist(),
        colors=neutral_cols,
        value_format="money",
        height=430,
    )


# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
        "Top routes: EXPAND</p>", unsafe_allow_html=True)
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route", "Profit", "Profit_Margin", "Load_Factor"]].head(10)
        .rename(columns={"Profit": "Avg Profit ($)", "Profit_Margin": "Profit Margin", "Load_Factor": "Load Factor"})
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
            "Top 10 routes · total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        shimmer_classic_horizontal_bar_chart(
            title="Top 10 Routes",
            labels=top.index.tolist(),
            values=top.values.tolist(),
            color=CHART_EXPAND,
            value_format="money",
            height=430,
        )

    with right:
        st.markdown(
            f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
            "Bottom 10 routes · total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        shimmer_classic_horizontal_bar_chart(
            title="Bottom 10 Routes",
            labels=worst.index.tolist(),
            values=worst.values.tolist(),
            color=CHART_DROP,
            value_format="money",
            height=430,
        )


# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
            "Most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
            "Most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">★ DISTRIBUTION ★</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
        "Unique routes per category</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route": "Unique Routes"})
        .set_index("Route_Decision").reindex(ORDER).dropna()
    )
    bc_map = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN,
              "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
    bc = [bc_map.get(i, ACCENT) for i in urbd.index]

    vals4 = urbd["Unique Routes"].values.tolist()
    shimmer_vertical_bar_chart(
        title="Unique Routes per Decision Category",
        labels=urbd.index.tolist(),
        series=[{
            "name": "Unique Routes",
            "values": vals4,
            "color": ACCENT,
            "colors": bc,
        }],
        max_value=max(vals4) if vals4 else 1,
        value_format="number",
        height=390,
    )


# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)

    shimmer_vertical_bar_chart(
        title="Model Accuracy & F1 Comparison",
        labels=comparison["Model"].tolist(),
        series=[
            {
                "name": "Accuracy",
                "values": comparison["Accuracy"].tolist(),
                "color": ACCENT,
            },
            {
                "name": "Macro F1",
                "values": comparison["Macro F1"].tolist(),
                "color": ACCENT_2,
            },
        ],
        max_value=1.0,
        value_format="percent",
        height=430,
    )

    st.markdown('<div class="divider-label">★ CONFIGURATION ★</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a prediction mode</p>', unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
    <span class='pill pill-maintain'>WITH REVENUE</span>&nbsp; Most accurate — use when you have ticket &amp; ancillary revenue data.<br><br>
    <span class='pill pill-optimize'>COST-ONLY</span>&nbsp; Good accuracy using cost data only, no revenue figures needed.<br><br>
    <span class='pill pill-expand'>PRE-LAUNCH</span>&nbsp; Use before a route launches, when only capacity/demand signals are known.
    </div>""", unsafe_allow_html=True)

    model_choice = st.selectbox(
        "Prediction mode",
        ["With Revenue Variables", "Without Revenue Variables", "Only Pre-Operational Features"],
        key="model_choice_select",
    )

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<p class="col-label">✈ FLIGHT BASICS</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown('<p class="col-label">🌍 ROUTE CONTEXT</p>', unsafe_allow_html=True)
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown('<p class="col-label">💰 REVENUE</p>', unsafe_allow_html=True)
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown('<p class="col-label">💸 COST BREAKDOWN</p>', unsafe_allow_html=True)
                fuel_cost               = st.number_input("Fuel Cost ($)",                  min_value=0.0, value=40000.0,  step=1000.0)
                maintenance_cost        = st.number_input("Maintenance Cost ($)",           min_value=0.0, value=15000.0,  step=500.0)
                crew_cost               = st.number_input("Crew Cost ($)",                  min_value=0.0, value=8000.0,   step=500.0)
                depreciation_cost       = st.number_input("Depreciation Cost ($)",          min_value=0.0, value=20000.0,  step=500.0)
                insurance_cost          = st.number_input("Insurance Cost ($)",             min_value=0.0, value=4000.0,   step=250.0)
                airport_fees            = st.number_input("Airport Fees ($)",               min_value=0.0, value=5000.0,   step=250.0)
                catering_cost           = st.number_input("Catering Cost ($)",              min_value=0.0, value=5000.0,   step=250.0)
                handling_cost           = st.number_input("Handling Cost ($)",              min_value=0.0, value=4000.0,   step=250.0)
                navigation_fees         = st.number_input("Navigation Fees ($)",            min_value=0.0, value=3500.0,   step=250.0)
                sales_distribution_cost = st.number_input("Sales & Distribution Cost ($)",  min_value=0.0, value=35000.0,  step=500.0)
                passenger_service_cost  = st.number_input("Passenger Service Cost ($)",     min_value=0.0, value=5000.0,   step=250.0)
                overhead_cost           = st.number_input("Overhead Cost ($)",              min_value=0.0, value=25000.0,  step=500.0)
                marketing_cost          = st.number_input("Marketing Cost ($)",             min_value=0.0, value=12000.0,  step=500.0)
                it_systems_cost         = st.number_input("IT Systems Cost ($)",            min_value=0.0, value=3000.0,   step=250.0)

        submitted = st.form_submit_button("✈  GET ROUTE DECISION")

    # ── PREDICTION LOGIC ────────────────────────────────────
    if submitted:
        if model_choice == "With Revenue Variables":
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
                "Ticket_Revenue": ticket_revenue, "Ancillary_Revenue": ancillary_revenue,
            }
            inp = prepare_input(pd.DataFrame([row]), X1_columns)
            pred = model1.predict(inp)[0]; prob = model1.predict_proba(inp)[0]; cls = model1.classes_
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
            inp = prepare_input(pd.DataFrame([row]), X2_columns)
            pred = model2.predict(inp)[0]; prob = model2.predict_proba(inp)[0]; cls = model2.classes_
        else:
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
            }
            inp = prepare_input(pd.DataFrame([row]), X3_columns)
            pred = model3.predict(inp)[0]; prob = model3.predict_proba(inp)[0]; cls = model3.classes_

        st.session_state.pred_result = {"prediction": pred, "probabilities": prob, "classes": cls}

    # ── RESULT ──────────────────────────────────────────────
    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]; prob = res["probabilities"]; cls = res["classes"]

        pill_cls   = {"Expand": "pill-expand", "Maintain": "pill-maintain",
                      "Optimize": "pill-optimize", "Drop": "pill-drop"}
        result_cls = {"Expand": "result-expand", "Maintain": "result-maintain",
                      "Optimize": "result-optimize", "Drop": "result-drop"}
        text_col   = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN,
                      "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred, "result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred, "")}'>{pred.upper()}</span>
          </div>
          <div style='font-family:Inter, sans-serif;font-size:0.85rem;font-weight:400;
                      color:{text_col.get(pred, INK)};margin-bottom:12px;letter-spacing:0.03em;
                      text-shadow:2px 2px 0px rgba(0,0,0,0.15);line-height:1.5'>
            DECISION: {pred.upper()}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-family:Inter, sans-serif;font-size:1.15rem;line-height:1.75;'>
            {explanations.get(pred, "")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-family:Inter, sans-serif;font-size:0.50rem;color:{INK};margin-bottom:7px;'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision": cls, "Probability": prob})
                   .sort_values("Probability", ascending=False))
        bar_cp  = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN,
                   "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}

        bar_colors = [bar_cp.get(d, ACCENT) for d in prob_df["Decision"]]
        probs = prob_df["Probability"].tolist()
        shimmer_vertical_bar_chart(
            title="Model Confidence per Decision",
            labels=prob_df["Decision"].tolist(),
            series=[{
                "name": "Probability",
                "values": probs,
                "color": ACCENT,
                "colors": bar_colors,
            }],
            max_value=1.0,
            value_format="percent",
            height=390,
        )

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
<div style='text-align:center;padding:40px 0 28px'>
  <div style='display:inline-block;
              background:#fff9e6;
              border:3px solid {INK};
              box-shadow:4px 4px 0px {INK};
              padding:0.6rem 1.6rem;
              font-family:Inter, sans-serif;
              font-size:0.42rem;
              color:{INK_MUTED};
              letter-spacing:0.10em;'>
    ★ AIRLINE PROFITABILITY SYSTEM ★ BUILT WITH STREAMLIT ★
  </div>
</div>
""", unsafe_allow_html=True)
