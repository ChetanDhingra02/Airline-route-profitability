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
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────────────────────
#  KINICH PALETTE — Light background, pixel-art inspired
#  Colors pulled directly from Kinich's character art:
#  • Forest/jade green  #1a5c3a / #2d7a4f
#  • Electric lime      #a8e63d / #c8f03a
#  • Warm gold          #d4a017 / #f0c040
#  • Deep teal          #0f6b6b / #1d9a9a
#  • Pixel chartreuse   #7ecb20
#  • Parchment ivory    #f8f4e8  (main BG)
# ─────────────────────────────────────────────────────────────
BG_BASE      = "#f8f4e8"   # warm parchment — like Natlan stone
BG_SOFT      = "#eef7ec"   # faint jade tint
BG_COOL      = "#e8f5f0"   # teal whisper

GLASS_BG     = "rgba(248,244,232,0.78)"
GLASS_BORDER = "rgba(45,122,79,0.30)"

INK          = "#0f2d1a"   # deep forest black
INK_SOFT     = "#2d5a3d"   # forest green mid
INK_MUTED    = "#5a8a6a"   # muted jade

ACCENT       = "#1d7a4a"   # Kinich jade
ACCENT_DK    = "#0f4a2a"   # deep forest
ACCENT_LT    = "#a8e63d"   # electric lime highlight
ACCENT_2     = "#d4a017"   # Natlan gold
PIXEL_GREEN  = "#7ecb20"   # pixel art lime
PIXEL_TEAL   = "#1d9a9a"   # teal
MAGENTA_ACT  = "#c85a1a"   # warm amber-orange accent (Kinich arm cuffs)

# Chart jewel tones — Kinich palette
CHART_EXPAND   = "#1a7a3a"   # jade
CHART_MAINTAIN = "#d4a017"   # gold
CHART_OPTIMIZE = "#1d9a9a"   # teal
CHART_DROP     = "#c85a1a"   # amber-warning

DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_OPTIMIZE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — Kinich / Natlan aesthetic
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@300;400;500;600;700;800&family=Oxanium:wght@400;500;600;700;800&display=swap');

:root {{
    --parchment:   {BG_BASE};
    --jade-soft:   {BG_SOFT};
    --teal-soft:   {BG_COOL};
    --ink:         {INK};
    --ink-soft:    {INK_SOFT};
    --ink-muted:   {INK_MUTED};
    --accent:      {ACCENT};
    --accent-dk:   {ACCENT_DK};
    --accent-lt:   {ACCENT_LT};
    --gold:        {ACCENT_2};
    --pixel-green: {PIXEL_GREEN};
    --teal:        {PIXEL_TEAL};
    --r-sm: 4px; --r-md: 8px; --r-lg: 12px; --r-xl: 16px;
    --sh-sm: 0 2px 12px rgba(29,122,74,0.12), 0 1px 4px rgba(0,0,0,0.06);
    --sh-md: 0 6px 24px rgba(29,122,74,0.18), 0 2px 8px rgba(0,0,0,0.08);
    --sh-lg: 0 16px 48px rgba(29,122,74,0.22), 0 4px 16px rgba(0,0,0,0.10);
    --pixel-border: 2px solid rgba(29,122,74,0.35);
    --gold-border:  2px solid rgba(212,160,23,0.45);
    --ease: cubic-bezier(0.25, 0.8, 0.25, 1);
    --pixel-size: 6px;
}}

/* ── Keyframes ── */
@keyframes floatIn    {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes fadeUp     {{ from {{ opacity:0; transform:translateY(8px);  }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes pixelDrift {{ 0%,100% {{ transform:translate(0,0); }} 33% {{ transform:translate(4px,-3px); }} 66% {{ transform:translate(-3px,4px); }} }}
@keyframes goldPulse  {{ 0%,100% {{ box-shadow:0 0 0 2px rgba(212,160,23,0.20); }} 50% {{ box-shadow:0 0 0 4px rgba(212,160,23,0.45), 0 0 18px rgba(168,230,61,0.20); }} }}
@keyframes scanPx     {{ 0% {{ left:-120%; }} 100% {{ left:220%; }} }}
@keyframes checkFlash {{ 0%,100% {{ opacity:0.22; }} 50% {{ opacity:0.45; }} }}
@keyframes pixelFloat {{ 0%,100% {{ transform:translateY(0) rotate(0deg); }} 50% {{ transform:translateY(-8px) rotate(3deg); }} }}
@keyframes pixelPop   {{ 0% {{ transform:scale(0.7); opacity:0; }} 60% {{ transform:scale(1.08); }} 100% {{ transform:scale(1); opacity:1; }} }}
@keyframes limeGlow   {{ 0%,100% {{ border-color:rgba(29,122,74,0.25); box-shadow:var(--sh-sm); }} 50% {{ border-color:rgba(168,230,61,0.50); box-shadow:var(--sh-sm), 0 0 14px rgba(168,230,61,0.22); }} }}
@keyframes tileScroll {{ 0% {{ background-position:0 0; }} 100% {{ background-position:48px 48px; }} }}
@keyframes shimmer    {{ 0% {{ left:-80%; }} 100% {{ left:180%; }} }}

/* ── Pixel cursor ── */
*, *::before, *::after {{ cursor: none !important; }}
#kinich-cursor {{ position:fixed; top:0; left:0; pointer-events:none; z-index:999999; image-rendering:pixelated; }}

html, body, [class*="css"] {{
    font-family: 'Nunito', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: {INK} !important;
}}

/* ── App background — warm parchment with pixel tile texture ── */
.stApp {{
    min-height: 100vh;
    background:
        radial-gradient(ellipse at 8% 15%,  rgba(126,203,32,0.12) 0, transparent 32%),
        radial-gradient(ellipse at 88% 10%,  rgba(29,154,154,0.10) 0, transparent 28%),
        radial-gradient(ellipse at 55% 90%,  rgba(212,160,23,0.10) 0, transparent 30%),
        radial-gradient(ellipse at 20% 78%,  rgba(29,122,74,0.08) 0, transparent 26%),
        linear-gradient(160deg, #f8f4e8 0%, #f0f7ea 35%, #e8f5f0 65%, #f8f4e8 100%);
    background-attachment: fixed;
}}

/* Subtle pixel checkerboard overlay (very faint) */
.stApp::before {{
    content:"";
    position:fixed; inset:0;
    background-image:
        linear-gradient(45deg, rgba(29,122,74,0.025) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(29,122,74,0.025) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(29,122,74,0.025) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(29,122,74,0.025) 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    pointer-events:none; z-index:0;
    animation: tileScroll 8s linear infinite;
}}

.main .block-container {{
    max-width: 1320px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    animation: floatIn 500ms ease-out;
    position: relative; z-index: 1;
}}
section.main > div {{ background: transparent; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: rgba(240,247,234,0.95) !important;
    border-right: 3px solid rgba(29,122,74,0.30) !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 4px 0 24px rgba(29,122,74,0.10) !important;
}}
[data-testid="stSidebar"] * {{ color: {INK_SOFT} !important; }}

.sidebar-brand {{
    font-family: 'Press Start 2P', monospace;
    font-size: 0.72rem; font-weight: 400;
    color: {INK}; letter-spacing: 0.04em;
    padding: 0.2rem 0 1rem 0;
    border-bottom: 2px solid rgba(212,160,23,0.40);
    margin-bottom: 1rem;
    line-height: 1.8;
}}
.sidebar-brand span {{
    color: {ACCENT_2};
}}

/* ── Headings ── */
h1,h2,h3,h4 {{
    font-family: 'Oxanium', sans-serif !important;
    color: {INK} !important;
    letter-spacing: 0.06em !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
}}

/* ── Hero ── */
.hero {{
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between; gap: 1.2rem;
    border-radius: var(--r-md);
    padding: 2rem 2.4rem; margin-bottom: 1.4rem;
    background: linear-gradient(140deg,
        rgba(240,247,234,0.95) 0%,
        rgba(232,245,240,0.90) 50%,
        rgba(248,244,232,0.95) 100%);
    border: 2px solid rgba(212,160,23,0.40);
    box-shadow: var(--sh-md), inset 0 1px 0 rgba(255,255,255,0.90);
    animation: goldPulse 4s ease-in-out infinite;
}}

/* Pixel checkerboard border corners */
.hero::before {{
    content:"";
    position:absolute; top:0; left:0; right:0; height:4px;
    background: repeating-linear-gradient(
        90deg,
        {ACCENT}   0px,  {ACCENT}   8px,
        {ACCENT_2} 8px,  {ACCENT_2} 16px,
        {PIXEL_GREEN} 16px, {PIXEL_GREEN} 24px,
        {PIXEL_TEAL}  24px, {PIXEL_TEAL}  32px
    );
    opacity: 0.85;
}}
.hero::after {{
    content:"";
    position:absolute; bottom:0; left:0; right:0; height:3px;
    background: repeating-linear-gradient(
        90deg,
        {ACCENT_2} 0px,  {ACCENT_2} 8px,
        {ACCENT}   8px,  {ACCENT}   16px,
        {PIXEL_TEAL}  16px, {PIXEL_TEAL}  24px,
        {PIXEL_GREEN} 24px, {PIXEL_GREEN} 32px
    );
    opacity: 0.60;
}}

.hero-left,.hero-badge,.hero-glyph {{ position:relative; z-index:1; }}
.hero-left {{ flex:1; min-width:0; }}
.hero-eyebrow {{
    font-family:'Press Start 2P',monospace;
    font-size:0.46rem; letter-spacing:0.14em;
    color:{ACCENT}; font-weight:400; margin-bottom:0.6rem;
}}
.hero h1 {{
    margin:0 0 0.4rem 0 !important;
    font-size:1.80rem !important; line-height:1.2 !important;
    background: linear-gradient(135deg, {INK} 0%, {ACCENT} 45%, {ACCENT_2} 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    text-shadow:none !important;
}}
.hero p {{
    margin:0; color:{INK_SOFT} !important; font-size:0.86rem !important;
    font-family:'Nunito',sans-serif !important; text-transform:none !important;
    letter-spacing:0 !important; font-weight:500 !important;
}}
.hero-badge {{
    display:inline-flex; align-items:center; gap:0.5rem;
    padding:0.5rem 1rem; border-radius:2px;
    border:2px solid rgba(212,160,23,0.55);
    background:linear-gradient(135deg,rgba(212,160,23,0.14),rgba(29,122,74,0.10));
    color:{ACCENT_2}; font-size:0.50rem; font-weight:400;
    letter-spacing:0.08em; text-transform:uppercase; font-family:'Press Start 2P',monospace;
    box-shadow:0 4px 14px rgba(212,160,23,0.18);
    animation: pixelPop 600ms ease-out 200ms both;
    white-space:nowrap;
    image-rendering:pixelated;
}}
.hero-glyph {{
    font-size:3.5rem; opacity:0.10; color:{ACCENT};
    animation:pixelFloat 5s ease-in-out infinite;
    font-family:'Press Start 2P',monospace;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(155deg,
        rgba(240,247,234,0.90) 0%, rgba(232,245,240,0.82) 100%) !important;
    border: 2px solid rgba(29,122,74,0.22) !important;
    border-radius: var(--r-sm) !important;
    box-shadow: var(--sh-sm) !important;
    padding: 1.1rem 1.2rem !important;
    transition: transform 200ms var(--ease), box-shadow 200ms var(--ease) !important;
    position:relative; overflow:hidden;
    animation: limeGlow 5s ease-in-out infinite;
    image-rendering:pixelated;
}}
/* Pixel corner accent */
[data-testid="metric-container"]::before {{
    content:""; position:absolute; top:0; left:0;
    width:8px; height:8px;
    background:{ACCENT_2}; opacity:0.75;
}}
[data-testid="metric-container"]::after {{
    content:""; position:absolute; bottom:0; right:0;
    width:8px; height:8px;
    background:{ACCENT}; opacity:0.50;
}}
[data-testid="metric-container"]:hover {{
    transform:translateY(-4px) scale(1.02) !important;
    box-shadow:var(--sh-md), 0 0 0 2px rgba(168,230,61,0.45) !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size:0.56rem !important; font-weight:400 !important;
    text-transform:uppercase !important; letter-spacing:0.14em !important;
    color:{ACCENT} !important; font-family:'Press Start 2P',monospace !important;
    line-height:1.6 !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
    color:{INK} !important; font-size:1.80rem !important; font-weight:700 !important;
    font-family:'Oxanium',sans-serif !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap:0.22rem;
    background:rgba(240,247,234,0.85);
    border:2px solid rgba(29,122,74,0.22);
    border-radius:4px; padding:0.28rem;
    box-shadow:var(--sh-sm);
}}
.stTabs [data-baseweb="tab"] {{
    height:40px; padding:0 1rem !important;
    border-radius:2px !important;
    color:{INK_MUTED} !important;
    font-size:0.66rem !important; font-weight:400 !important;
    font-family:'Press Start 2P',monospace !important;
    background:transparent !important; letter-spacing:0.02em !important;
    transition:background 180ms, color 180ms !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background:rgba(29,122,74,0.10) !important; color:{ACCENT} !important;
}}
.stTabs [aria-selected="true"] {{
    background:linear-gradient(135deg,rgba(29,122,74,0.16),rgba(212,160,23,0.12)) !important;
    color:{INK} !important;
    box-shadow:0 4px 12px rgba(29,122,74,0.16), inset 0 0 0 2px rgba(212,160,23,0.35) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:1.5rem; }}

/* ── Section headings ── */
.section-hd {{
    font-family:'Oxanium',sans-serif; font-size:0.95rem; font-weight:700;
    color:{INK}; margin:0 0 0.28rem 0; letter-spacing:0.06em; text-transform:uppercase;
}}
.section-sub {{
    font-size:0.84rem; color:{INK_MUTED}; margin:0 0 1.1rem 0; line-height:1.65;
    font-family:'Nunito',sans-serif; font-weight:500;
}}

/* ── Divider label ── */
.divider-label {{
    display:flex; align-items:center; gap:0.7rem; margin:1.5rem 0 1rem 0;
    font-size:0.50rem; font-weight:400; text-transform:uppercase; letter-spacing:0.20em;
    color:{ACCENT_2}; font-family:'Press Start 2P',monospace;
}}
.divider-label::before,.divider-label::after {{
    content:""; flex:1; height:2px;
    background: repeating-linear-gradient(
        90deg, {ACCENT} 0, {ACCENT} 4px, transparent 4px, transparent 8px
    );
    opacity: 0.40;
}}

/* ── Info box ── */
.info-box {{
    background:linear-gradient(155deg,rgba(240,247,234,0.90),rgba(232,245,240,0.80));
    border:2px solid rgba(29,122,74,0.22);
    border-left:4px solid {ACCENT_2};
    border-radius:var(--r-sm); padding:1rem 1.1rem;
    color:{INK_SOFT}; line-height:1.80; box-shadow:var(--sh-sm);
    font-size:0.86rem; font-family:'Nunito',sans-serif;
}}

/* ── Pills ── */
.pill {{
    display:inline-block; padding:0.22rem 0.65rem; border-radius:2px;
    font-size:0.48rem; font-weight:400; letter-spacing:0.08em; text-transform:uppercase;
    font-family:'Press Start 2P',monospace; border:2px solid transparent;
    image-rendering:pixelated;
}}
.pill-expand   {{ background:rgba(26,122,58,0.12);  color:{CHART_EXPAND};   border-color:rgba(26,122,58,0.35); }}
.pill-maintain {{ background:rgba(212,160,23,0.12); color:{CHART_MAINTAIN}; border-color:rgba(212,160,23,0.38); }}
.pill-optimize {{ background:rgba(29,154,154,0.12); color:{CHART_OPTIMIZE}; border-color:rgba(29,154,154,0.35); }}
.pill-drop     {{ background:rgba(200,90,26,0.12);  color:{CHART_DROP};    border-color:rgba(200,90,26,0.35); }}

/* ── Result card ── */
.result-card {{
    border-radius:var(--r-md); padding:1.5rem 1.6rem; margin:1.2rem 0;
    border:2px solid rgba(29,122,74,0.25);
    box-shadow:var(--sh-md);
    animation:fadeUp 380ms ease-out;
    position:relative; overflow:hidden;
}}
.result-card::before {{
    content:""; position:absolute; top:0; left:0; right:0; height:4px;
    background: repeating-linear-gradient(
        90deg, var(--card-accent) 0, var(--card-accent) 6px,
        transparent 6px, transparent 12px
    );
}}
.result-expand   {{ background:linear-gradient(140deg,rgba(220,245,225,0.90),rgba(248,244,232,0.92)); border-left:5px solid {CHART_EXPAND};   --card-accent:{CHART_EXPAND}; }}
.result-maintain {{ background:linear-gradient(140deg,rgba(255,245,200,0.90),rgba(248,244,232,0.92)); border-left:5px solid {CHART_MAINTAIN}; --card-accent:{CHART_MAINTAIN}; }}
.result-optimize {{ background:linear-gradient(140deg,rgba(200,240,240,0.90),rgba(248,244,232,0.92)); border-left:5px solid {CHART_OPTIMIZE}; --card-accent:{CHART_OPTIMIZE}; }}
.result-drop     {{ background:linear-gradient(140deg,rgba(255,225,200,0.90),rgba(248,244,232,0.92)); border-left:5px solid {CHART_DROP};     --card-accent:{CHART_DROP}; }}

/* ── Form inputs ── */
.stSelectbox label,.stNumberInput label,.stSlider label,
.stRadio label,.stCheckbox label,.stTextInput label {{
    color:{INK_SOFT} !important; font-weight:400 !important; font-size:0.55rem !important;
    letter-spacing:0.08em !important; text-transform:uppercase !important;
    font-family:'Press Start 2P',monospace !important; line-height:1.8 !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,.stNumberInput input {{
    background:rgba(248,252,245,0.92) !important;
    border:2px solid rgba(29,122,74,0.28) !important;
    border-radius:2px !important; color:{INK} !important;
    min-height:42px !important; box-shadow:none !important;
    transition:border-color 180ms !important;
    font-family:'Nunito',sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover {{ border-color:rgba(212,160,23,0.55) !important; }}
.stSelectbox [data-baseweb="select"] > div:focus-within {{ border-color:{ACCENT} !important; box-shadow:0 0 0 3px rgba(29,122,74,0.14) !important; }}
[data-baseweb="menu"] {{
    background:rgba(248,252,245,0.98) !important;
    border:2px solid rgba(29,122,74,0.28) !important;
    border-radius:2px !important; box-shadow:var(--sh-md) !important;
}}
[data-baseweb="menu"] li {{ color:{INK_SOFT} !important; }}
[data-baseweb="menu"] li:hover {{ background:rgba(29,122,74,0.10) !important; color:{ACCENT} !important; }}

/* ── Form card ── */
[data-testid="stForm"] {{
    background:linear-gradient(155deg,rgba(240,247,234,0.92),rgba(248,252,245,0.88)) !important;
    border:2px solid rgba(29,122,74,0.28) !important;
    border-radius:var(--r-md) !important; padding:1.5rem 1.6rem 1.8rem !important;
    box-shadow:var(--sh-md) !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button, .stButton > button {{
    border-radius:2px !important; font-weight:400 !important; border:2px solid transparent !important;
    font-family:'Press Start 2P',monospace !important; letter-spacing:0.06em !important;
    text-transform:uppercase !important; font-size:0.52rem !important;
    transition:transform 180ms, box-shadow 180ms !important;
    image-rendering:pixelated;
}}
[data-testid="stFormSubmitButton"] > button {{
    width:100% !important; padding:0.85rem 0 !important;
    background:linear-gradient(135deg,{ACCENT},{ACCENT_DK}) !important;
    border-color:{ACCENT_LT} !important;
    box-shadow:0 6px 20px rgba(29,122,74,0.35), 4px 4px 0 rgba(15,74,42,0.55) !important;
    color:white !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform:translate(-2px,-2px) !important;
    box-shadow:0 10px 28px rgba(29,122,74,0.45), 6px 6px 0 rgba(15,74,42,0.55) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform:translate(2px,2px) !important;
    box-shadow:2px 2px 0 rgba(15,74,42,0.55) !important;
}}
.stButton > button {{
    background:rgba(248,252,245,0.90) !important; color:{INK_SOFT} !important;
    border-color:rgba(29,122,74,0.30) !important;
    box-shadow:var(--sh-sm), 3px 3px 0 rgba(29,122,74,0.20) !important;
}}
.stButton > button:hover {{
    color:{ACCENT} !important;
    transform:translate(-2px,-2px) !important;
    box-shadow:var(--sh-md), 5px 5px 0 rgba(29,122,74,0.28) !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background:rgba(240,247,234,0.85) !important;
    border:2px solid rgba(29,122,74,0.22) !important;
    border-radius:var(--r-sm) !important; overflow:hidden !important;
    box-shadow:var(--sh-sm) !important;
}}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background:rgba(29,122,74,0.10) !important; color:{ACCENT} !important;
    font-weight:700 !important; font-size:0.72rem !important;
    letter-spacing:0.08em !important; text-transform:uppercase !important;
    border-bottom:2px solid rgba(212,160,23,0.35) !important;
    font-family:'Oxanium',sans-serif !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
    border-bottom:1px solid rgba(29,122,74,0.08) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background:rgba(240,247,234,0.85) !important;
    border:2px solid rgba(29,122,74,0.20) !important;
    border-radius:var(--r-sm) !important; box-shadow:var(--sh-sm) !important;
}}

/* ── Charts ── */
[data-testid="stPyplot"] {{
    background:rgba(240,247,234,0.80);
    border:2px solid rgba(29,122,74,0.20);
    border-radius:var(--r-md); padding:1rem;
    box-shadow:var(--sh-sm);
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius:var(--r-sm) !important;
    background:rgba(240,247,234,0.90) !important;
    border:2px solid rgba(29,122,74,0.22) !important;
    color:{INK_SOFT} !important;
}}

hr {{ border:none !important; height:2px !important;
     background: repeating-linear-gradient(90deg, {ACCENT} 0, {ACCENT} 4px, transparent 4px, transparent 10px) !important;
     opacity:0.25 !important; margin:1.4rem 0 !important; }}

.col-label {{
    font-size:0.50rem; font-weight:400; color:{ACCENT_2}; letter-spacing:0.12em;
    text-transform:uppercase; margin-bottom:0.9rem;
    display:flex; align-items:center; gap:0.5rem; font-family:'Press Start 2P',monospace;
    line-height:1.8;
}}
.col-label::after {{
    content:""; flex:1; height:2px;
    background: repeating-linear-gradient(90deg, {ACCENT_2} 0, {ACCENT_2} 4px, transparent 4px, transparent 8px);
    opacity: 0.40;
}}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background:{ACCENT_2} !important; border-color:{ACCENT_LT} !important;
    box-shadow:0 0 8px rgba(212,160,23,0.50), 2px 2px 0 rgba(15,74,42,0.35) !important;
    border-radius:0 !important; width:16px !important; height:16px !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
    background:linear-gradient(90deg,{ACCENT},{ACCENT_LT}) !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:rgba(232,245,240,0.60); }}
::-webkit-scrollbar-thumb {{ background:rgba(29,122,74,0.35); border-radius:0; }}
::-webkit-scrollbar-thumb:hover {{ background:{ACCENT}; }}
::selection {{ background:rgba(168,230,61,0.30); color:{INK}; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  KINICH PIXEL CURSOR + PIXEL AIRPLANE TRAIL
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<canvas id="kinich-cursor"></canvas>
<script>
(function() {{
    const canvas = document.getElementById('kinich-cursor');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    let W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;
    window.addEventListener('resize', () => {{
        W = window.innerWidth; H = window.innerHeight;
        canvas.width = W; canvas.height = H;
        ctx.imageSmoothingEnabled = false;
    }});

    let mx = W/2, my = H/2;
    let angle = 0, targetAngle = 0;
    const trail = [];
    const MAX_TRAIL = 28;

    document.addEventListener('mousemove', e => {{
        const dx = e.clientX - mx, dy = e.clientY - my;
        if (Math.abs(dx) + Math.abs(dy) > 1) {{
            targetAngle = Math.atan2(dy, dx) + Math.PI / 2;
        }}
        mx = e.clientX; my = e.clientY;
        trail.push({{ x: mx, y: my, age: 0 }});
        if (trail.length > MAX_TRAIL) trail.shift();
    }});

    function lerpAngle(a, b, t) {{
        let d = b - a;
        while (d >  Math.PI) d -= 2*Math.PI;
        while (d < -Math.PI) d += 2*Math.PI;
        return a + d * t;
    }}

    // Kinich pixel cursor — checkerboard headband style, 16×16 pixel art
    // Colors: jade, lime, gold, teal
    const C_JADE  = '#1a7a3a';
    const C_LIME  = '#a8e63d';
    const C_GOLD  = '#d4a017';
    const C_TEAL  = '#1d9a9a';
    const C_INK   = '#0f2d1a';
    const C_WHITE = '#f8f4e8';

    // Each row: array of [color|null] for a 14×14 pixel cursor
    // Shaped like a stylized sword/arrow pointing up — Kinich's weapon style
    const CURSOR_PX = 3; // scale each pixel by 3px

    function drawPixelCursor(x, y, ang) {{
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(ang);

        const p = CURSOR_PX;

        // Pixel art airplane/arrow cursor
        // Map: each cell is one pixel
        const grid = [
            // col:  0  1  2  3  4
            [0,0,1,0,0],   // row 0   — nose tip
            [0,0,1,0,0],   // row 1
            [0,1,1,1,0],   // row 2   — head
            [0,1,2,1,0],   // row 3   — gold cockpit
            [1,1,2,1,1],   // row 4   — wings
            [1,3,1,3,1],   // row 5   — teal wing stripe
            [0,1,1,1,0],   // row 6
            [0,0,1,0,0],   // row 7   — body
            [0,0,1,0,0],   // row 8
            [0,1,1,1,0],   // row 9   — tail
            [1,0,1,0,1],   // row 10  — tail fins
        ];
        const colorMap = {{ 0:null, 1:C_JADE, 2:C_GOLD, 3:C_TEAL, 4:C_LIME }};

        const offsetX = -(grid[0].length * p) / 2;
        const offsetY = -(grid.length * p) / 2;

        // Pixel shadow (pixel-offset style)
        ctx.globalAlpha = 0.22;
        for (let r = 0; r < grid.length; r++) {{
            for (let c = 0; c < grid[r].length; c++) {{
                const v = grid[r][c];
                if (!v) continue;
                ctx.fillStyle = C_INK;
                ctx.fillRect(offsetX + c*p + 2, offsetY + r*p + 2, p, p);
            }}
        }}
        ctx.globalAlpha = 1.0;

        for (let r = 0; r < grid.length; r++) {{
            for (let c = 0; c < grid[r].length; c++) {{
                const v = grid[r][c];
                const col = colorMap[v];
                if (!col) continue;
                ctx.fillStyle = col;
                ctx.fillRect(offsetX + c*p, offsetY + r*p, p, p);
            }}
        }}

        ctx.restore();
    }}

    // Pixel airplane body for trail
    function drawPixelAirplane(x, y, ang, scale, alpha) {{
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(ang);
        ctx.globalAlpha = alpha;
        ctx.imageSmoothingEnabled = false;

        const p = Math.max(1, Math.floor(scale * 2.5));

        // Mini pixel plane: 5×7
        const plane = [
            [0,1,0],
            [0,2,0],
            [1,1,1],
            [3,1,3],
            [0,1,0],
            [0,1,0],
            [1,0,1],
        ];
        const cmap = {{ 0:null, 1:C_JADE, 2:C_GOLD, 3:C_TEAL }};
        const ox = -(3*p)/2, oy = -(7*p)/2;
        for (let r = 0; r < plane.length; r++) {{
            for (let c = 0; c < plane[r].length; c++) {{
                const col = cmap[plane[r][c]];
                if (!col) continue;
                ctx.fillStyle = col;
                ctx.fillRect(ox + c*p, oy + r*p, p, p);
            }}
        }}
        ctx.restore();
    }}

    // Pixel spark colors — Kinich palette
    const sparkColors = [C_LIME, C_GOLD, C_TEAL, C_JADE, '#7ecb20', '#f0c040'];

    let tick = 0;

    function frame() {{
        ctx.clearRect(0, 0, W, H);
        ctx.imageSmoothingEnabled = false;
        tick++;

        // Age trail
        for (let i=0; i<trail.length; i++) trail[i].age++;

        // Draw pixel airplane trail
        for (let i=1; i<trail.length; i++) {{
            const p = trail[i];
            const prog = i / trail.length;
            const fade = prog * Math.max(0, 1 - p.age / 60);
            if (fade < 0.05) continue;

            if (i > 1 && i % 3 === 0) {{
                const prev = trail[i-1];
                const dx = p.x - prev.x, dy = p.y - prev.y;
                const a = Math.atan2(dy, dx) + Math.PI/2;
                drawPixelAirplane(p.x, p.y, a, prog * 0.8 + 0.2, fade * 0.7);
            }}

            // Pixel square sparks — checkerboard style
            if (i % 4 === 0 && prog > 0.3) {{
                const sz = Math.max(2, Math.floor(prog * 5));
                const col = sparkColors[Math.floor(prog * sparkColors.length)];
                ctx.fillStyle = col;
                ctx.globalAlpha = fade * 0.65;
                // Pixel-snap position
                const sx = Math.floor(p.x / 4) * 4;
                const sy = Math.floor(p.y / 4) * 4;
                ctx.fillRect(sx, sy, sz, sz);
                // Checkerboard offset spark
                if (i % 8 === 0) {{
                    ctx.fillStyle = C_GOLD;
                    ctx.fillRect(sx + sz, sy + sz, sz, sz);
                }}
                ctx.globalAlpha = 1.0;
            }}
        }}

        angle = lerpAngle(angle, targetAngle, 0.20);

        // Draw main pixel cursor at mouse
        drawPixelCursor(mx, my, angle);

        requestAnimationFrame(frame);
    }}
    frame();
}})();
</script>
""", unsafe_allow_html=True)


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
#  CHART HELPERS — Kinich palette
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#f0f7ea")
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
    ax.grid(axis="y", color="#c8e8c8", linewidth=0.8, linestyle="-", alpha=0.85)
    ax.set_axisbelow(True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(INK_MUTED)
    return fig, ax


def col_seq(labels):
    return [DECISION_COLORS.get(l, ACCENT) for l in labels]


def _fmt_chart_value(v, value_format="number"):
    if value_format == "percent":
        return f"{v:.0%}"
    if value_format == "money":
        return f"${v:,.0f}"
    return f"{v:,.0f}"


# ─────────────────────────────────────────────────────────────
#  ANIMATED HTML CHART HELPERS — Kinich pixel-art style
# ─────────────────────────────────────────────────────────────

# Shared chart CSS injected once inline
_KINICH_CHART_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Oxanium:wght@400;500;600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap');

.ki-card {{
    width:100%; box-sizing:border-box;
    padding:22px 26px 20px;
    border-radius:8px;
    background:
        linear-gradient(145deg, rgba(240,247,234,0.80), rgba(232,245,240,0.72), rgba(248,244,232,0.78));
    border:2px solid rgba(29,122,74,0.22);
    box-shadow:0 2px 14px rgba(29,122,74,0.12);
    font-family:'Nunito',system-ui,sans-serif;
    color:{INK};
    overflow:hidden; position:relative;
    image-rendering:pixelated;
}}

/* Pixel checkerboard corner decorations */
.ki-card::before {{
    content:"";
    position:absolute; top:0; left:0; right:0; height:4px;
    background: repeating-linear-gradient(
        90deg,
        {ACCENT}    0px,  {ACCENT}    8px,
        {ACCENT_2}  8px,  {ACCENT_2}  16px,
        {PIXEL_GREEN} 16px, {PIXEL_GREEN} 24px,
        {PIXEL_TEAL}  24px, {PIXEL_TEAL}  32px
    );
    opacity:0.70;
}}

/* Shimmer sweep */
.ki-card::after {{
    content:"";
    position:absolute; top:0; left:-80%; bottom:0; width:50%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.28),transparent);
    animation:kiSweep 5s ease-in-out infinite;
    pointer-events:none;
}}

.ki-title {{
    font-family:'Oxanium',sans-serif;
    text-align:center; font-size:18px; line-height:1.3;
    color:{INK}; margin-bottom:18px; font-weight:700;
    letter-spacing:0.06em; text-transform:uppercase;
}}

.ki-legend {{
    display:flex; justify-content:center; gap:18px; margin-bottom:18px; flex-wrap:wrap;
}}
.ki-legend-item {{
    display:flex; align-items:center; gap:7px;
    color:{INK_SOFT}; font-weight:700; font-size:13px;
}}
.ki-legend-swatch {{
    width:16px; height:8px; border-radius:0;
    image-rendering:pixelated;
    box-shadow:2px 2px 0 rgba(15,45,26,0.25);
}}

@keyframes kiSweep   {{ 0%{{left:-80%}} 50%{{left:180%}} 100%{{left:180%}} }}
@keyframes kiGrowV   {{ from{{height:0%;opacity:.4}} to{{height:var(--bh);opacity:1}} }}
@keyframes kiGrowH   {{ from{{width:0%;opacity:.4}}  to{{width:var(--bw);opacity:1}} }}
@keyframes kiShimmer {{ 0%{{transform:translateX(-150%)}} 48%{{transform:translateX(155%)}} 100%{{transform:translateX(155%)}} }}
@keyframes kiPopIn   {{ from{{transform:scale(.8) rotate(-8deg);opacity:.4}} to{{transform:scale(1) rotate(0deg);opacity:1}} }}
"""


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
        st.info("No chart data available.")
        return
    if max_value is None:
        max_value = max(all_values) if max(all_values) != 0 else 1
    max_value = float(max_value)

    chart = {"title": title, "labels": labels, "series": clean_series,
             "max_value": max_value, "value_format": value_format}
    cj = json.dumps(chart)
    plot_h = max(height - 190, 180)

    components.html(f"""
    <div id="ki-vbar-root"></div>
    <style>
    {_KINICH_CHART_CSS}
    .ki-vplot {{
        display:grid;
        grid-template-columns:repeat({max(len(labels),1)}, minmax(0,1fr));
        gap:24px; align-items:end; height:{plot_h}px;
        border-bottom:2px solid rgba(29,122,74,0.20);
        background-image:repeating-linear-gradient(
            to top,
            rgba(29,122,74,0.07) 0px, rgba(29,122,74,0.07) 1px,
            transparent 1px, transparent 25%
        );
        padding:0 14px; position:relative; z-index:1;
    }}
    .ki-vgroup {{ height:100%; display:flex; align-items:end; justify-content:center; gap:8px; }}
    .ki-vbar-wrap {{ height:100%; width:min(44px,28%); min-width:24px; display:flex; align-items:end; justify-content:center; position:relative; }}
    .ki-vbar {{
        width:100%; height:var(--bh); min-height:3px;
        border-radius:0; position:relative; overflow:hidden;
        box-shadow:3px 3px 0 rgba(15,45,26,0.30), inset 0 1px 0 rgba(255,255,255,0.55);
        animation:kiGrowV 800ms cubic-bezier(.22,.9,.25,1) both;
        image-rendering:pixelated;
    }}
    .ki-vbar::before {{
        content:""; position:absolute; inset:0; width:75%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),rgba(255,255,255,0.65),rgba(255,255,255,0.12),transparent);
        transform:translateX(-150%);
        animation:kiShimmer 2.2s ease-in-out infinite; animation-delay:var(--delay);
    }}
    /* Pixel checkerboard stripe on bar */
    .ki-vbar::after {{
        content:""; position:absolute; top:0; left:0; right:0; height:6px;
        background:repeating-linear-gradient(
            90deg, rgba(255,255,255,0.28) 0, rgba(255,255,255,0.28) 4px,
            transparent 4px, transparent 8px
        );
    }}
    .ki-vvalue {{
        position:absolute; bottom:calc(var(--bh) + 7px);
        font-size:12px; font-weight:800; color:{INK_SOFT}; white-space:nowrap;
    }}
    .ki-xlabels {{
        display:grid; grid-template-columns:repeat({max(len(labels),1)}, minmax(0,1fr));
        gap:24px; padding:12px 14px 0; text-align:center; position:relative; z-index:1;
    }}
    .ki-xlabel {{ color:{INK_SOFT}; font-weight:700; font-size:12px; line-height:1.25; }}
    </style>
    <script>
    const chart = {cj};
    function fmtV(v) {{
        if (chart.value_format==="percent") return Math.round(v*100)+"%";
        if (chart.value_format==="money") return "$"+Math.round(v).toLocaleString();
        return Math.round(v).toLocaleString();
    }}
    const root = document.getElementById("ki-vbar-root");
    const legendHtml = chart.series.map(s=>`
        <div class="ki-legend-item">
          <span class="ki-legend-swatch" style="background:${{s.color}}"></span>
          ${{s.name}}
        </div>`).join("");
    const groupsHtml = chart.labels.map((label,i)=>`
        <div class="ki-vgroup">
          ${{chart.series.map((s,j)=>{{
              const val = Number(s.values[i]||0);
              const pct = Math.max(2,Math.min(100,val/chart.max_value*100));
              const color = s.colors ? s.colors[i] : s.color;
              return `<div class="ki-vbar-wrap">
                <div class="ki-vvalue" style="--bh:${{pct}}%">${{fmtV(val)}}</div>
                <div class="ki-vbar" style="--bh:${{pct}}%;--delay:${{(i+j)*100}}ms;background:linear-gradient(180deg,${{color}},${{color}}cc);"></div>
              </div>`;
          }}).join("")}}
        </div>`).join("");
    const xlabels = chart.labels.map(l=>`<div class="ki-xlabel">${{l}}</div>`).join("");
    root.innerHTML = `<div class="ki-card">
      <div class="ki-title">${{chart.title}}</div>
      <div class="ki-legend">${{legendHtml}}</div>
      <div class="ki-vplot">${{groupsHtml}}</div>
      <div class="ki-xlabels">${{xlabels}}</div>
    </div>`;
    </script>
    """, height=height + 40, scrolling=False)


def shimmer_horizontal_bar_chart(title, labels, values, colors=None, value_format="number", height=430):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    if not values:
        st.info("No chart data available.")
        return
    if colors is None:
        colors = [ACCENT] * len(values)
    elif isinstance(colors, str):
        colors = [colors] * len(values)
    max_abs = max(abs(v) for v in values) or 1.0
    rows = [{
        "label": lab, "value": val,
        "display": _fmt_chart_value(val, value_format),
        "width": max(2, min(100, abs(val)/max_abs*100)),
        "color": col
    } for lab, val, col in zip(labels, values, colors)]
    cj = json.dumps({"title": title, "rows": rows})

    components.html(f"""
    <div id="ki-hbar-root"></div>
    <style>
    {_KINICH_CHART_CSS}
    .ki-hrows {{ display:flex; flex-direction:column; gap:11px; position:relative; z-index:1; }}
    .ki-hrow  {{ display:grid; grid-template-columns:minmax(90px,160px) 1fr minmax(70px,96px); align-items:center; gap:10px; }}
    .ki-hlabel {{ color:{INK_SOFT}; font-size:13px; font-weight:700; text-align:right; }}
    .ki-htrack {{ height:22px; border-radius:0; background:rgba(29,122,74,0.08); border:1px solid rgba(29,122,74,0.15); overflow:hidden; position:relative; }}
    .ki-hbar {{
        height:100%; width:var(--bw); border-radius:0; position:relative; overflow:hidden;
        box-shadow:2px 2px 0 rgba(15,45,26,0.25), inset 0 1px 0 rgba(255,255,255,0.50);
        animation:kiGrowH 800ms cubic-bezier(.22,.9,.25,1) both;
    }}
    .ki-hbar::before {{
        content:""; position:absolute; inset:0; width:75%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),rgba(255,255,255,0.60),rgba(255,255,255,0.12),transparent);
        transform:translateX(-150%); animation:kiShimmer 2.2s ease-in-out infinite; animation-delay:var(--delay);
    }}
    .ki-hvalue {{ color:{INK_SOFT}; font-weight:800; font-size:13px; white-space:nowrap; }}
    </style>
    <script>
    const chart = {cj};
    const root = document.getElementById("ki-hbar-root");
    const rows = chart.rows.map((r,i)=>`
        <div class="ki-hrow">
          <div class="ki-hlabel">${{r.label}}</div>
          <div class="ki-htrack"><div class="ki-hbar" style="--bw:${{r.width}}%;--delay:${{i*100}}ms;background:linear-gradient(90deg,${{r.color}},${{r.color}}cc);"></div></div>
          <div class="ki-hvalue">${{r.display}}</div>
        </div>`).join("");
    root.innerHTML = `<div class="ki-card" style="min-height:{height}px">
      <div class="ki-title">${{chart.title}}</div>
      <div class="ki-hrows">${{rows}}</div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_pie_chart(title, labels, values, colors=None, height=430):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    total = sum(values)
    if not values or total <= 0:
        st.info("No chart data available.")
        return
    if colors is None:
        colors = [ACCENT] * len(values)
    rows, start, stops = [], 0.0, []
    for label, value, color in zip(labels, values, colors):
        pct = value / total * 100
        end = start + pct
        stops.append(f"{color} {start:.4f}% {end:.4f}%")
        rows.append({"label": label, "value": value, "pct": pct, "display": f"{pct:.1f}%", "color": color})
        start = end
    cj = json.dumps({"title": title, "gradient": ", ".join(stops), "rows": rows, "total": total})

    components.html(f"""
    <div id="ki-pie-root"></div>
    <style>
    {_KINICH_CHART_CSS}
    .ki-pie-layout {{ display:grid; grid-template-columns:minmax(200px,.9fr) minmax(180px,1fr); gap:22px; align-items:center; position:relative; z-index:1; }}
    .ki-donut-wrap {{ display:flex; align-items:center; justify-content:center; }}
    .ki-donut {{
        width:min(220px,78vw); aspect-ratio:1; border-radius:0;
        background:conic-gradient(var(--pg));
        position:relative; overflow:hidden;
        box-shadow:4px 4px 0 rgba(15,45,26,0.28), 0 12px 28px rgba(29,122,74,0.16);
        animation:kiPopIn 800ms cubic-bezier(.22,.9,.25,1) both;
        image-rendering:pixelated;
    }}
    .ki-donut::before {{
        content:""; position:absolute; inset:-20%;
        background:linear-gradient(115deg,transparent,rgba(255,255,255,0.60) 48%,transparent);
        transform:translateX(-120%) rotate(12deg);
        animation:kiShimmer 2.8s ease-in-out infinite;
    }}
    .ki-donut::after {{
        content:""; position:absolute; inset:28%; border-radius:0;
        background:linear-gradient(145deg,rgba(240,247,234,0.90),rgba(248,244,232,0.95));
        box-shadow:inset 0 2px 8px rgba(29,122,74,0.12), inset -1px -1px 0 rgba(212,160,23,0.30);
    }}
    .ki-pie-legend {{ display:flex; flex-direction:column; gap:10px; }}
    .ki-pie-row {{ display:grid; grid-template-columns:10px 1fr auto; align-items:center; gap:9px; color:{INK_SOFT}; font-size:13px; font-weight:700; }}
    .ki-pie-dot {{ width:10px; height:10px; border-radius:0; box-shadow:2px 2px 0 rgba(15,45,26,0.22); image-rendering:pixelated; }}
    .ki-pie-pct {{ font-weight:900; white-space:nowrap; color:{INK_SOFT}; }}
    </style>
    <script>
    const pc = {cj};
    const root = document.getElementById("ki-pie-root");
    const rows = pc.rows.map(r=>`<div class="ki-pie-row">
        <span class="ki-pie-dot" style="background:${{r.color}}"></span>
        <span>${{r.label}}</span>
        <span class="ki-pie-pct">${{r.display}}</span>
    </div>`).join("");
    root.innerHTML = `<div class="ki-card" style="min-height:{height}px">
      <div class="ki-title">${{pc.title}}</div>
      <div class="ki-pie-layout">
        <div class="ki-donut-wrap"><div class="ki-donut" style="--pg:${{pc.gradient}}"></div></div>
        <div class="ki-pie-legend">${{rows}}</div>
      </div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_classic_horizontal_bar_chart(title, labels, values, color=ACCENT, value_format="money", height=460):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    if not values:
        st.info("No chart data available.")
        return
    max_abs = max(abs(v) for v in values) or 1.0
    rows = [{
        "label": lab, "value": val,
        "display": _fmt_chart_value(val, value_format),
        "width": max(2, min(100, abs(val)/max_abs*100))
    } for lab, val in zip(labels, values)]
    cj = json.dumps({"title": title, "rows": rows, "color": color})

    components.html(f"""
    <div id="ki-cbar-root"></div>
    <style>
    {_KINICH_CHART_CSS}
    .ki-crows {{ display:flex; flex-direction:column; gap:11px; }}
    .ki-crow  {{ display:grid; grid-template-columns:minmax(82px,148px) 1fr minmax(86px,108px); align-items:center; gap:10px; }}
    .ki-clabel {{ color:{INK_SOFT}; font-size:13px; font-weight:700; text-align:right; }}
    .ki-caxis {{ height:22px; position:relative; border-bottom:1px solid rgba(29,122,74,0.15);
                 background-image:repeating-linear-gradient(to right,rgba(29,122,74,0.08) 1px,transparent 1px); background-size:25% 100%; }}
    .ki-cbar {{
        height:22px; width:var(--bw); border-radius:0; position:relative; overflow:hidden;
        background:linear-gradient(90deg,var(--bc),color-mix(in srgb,var(--bc) 80%,#fff));
        box-shadow:2px 2px 0 rgba(15,45,26,0.22), inset 0 1px 0 rgba(255,255,255,0.45);
        animation:kiGrowH 800ms cubic-bezier(.22,.9,.25,1) both;
    }}
    .ki-cbar::before {{
        content:""; position:absolute; inset:0; width:70%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),rgba(255,255,255,0.55),rgba(255,255,255,0.12),transparent);
        transform:translateX(-150%); animation:kiShimmer 2.2s ease-in-out infinite; animation-delay:var(--delay);
    }}
    .ki-cvalue {{ color:{INK_SOFT}; font-weight:800; font-size:13px; white-space:nowrap; }}
    </style>
    <script>
    const cc = {cj};
    const root = document.getElementById("ki-cbar-root");
    const rows = cc.rows.map((r,i)=>`<div class="ki-crow">
        <div class="ki-clabel">${{r.label}}</div>
        <div class="ki-caxis"><div class="ki-cbar" style="--bw:${{r.width}}%;--bc:${{cc.color}};--delay:${{i*100}}ms;"></div></div>
        <div class="ki-cvalue">${{r.display}}</div>
    </div>`).join("");
    root.innerHTML = `<div class="ki-card" style="min-height:{height}px">
      <div class="ki-title">${{cc.title}}</div>
      <div class="ki-crows">${{rows}}</div>
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
    st.markdown(
        '<div class="sidebar-brand">AIRLINE<br><span>ROUTE</span><br>INTEL ✦</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='font-size:0.50rem;color:{ACCENT};margin-bottom:14px;"
        f"font-weight:400;letter-spacing:0.14em;text-transform:uppercase;"
        f"font-family:Press Start 2P,monospace;line-height:1.8'>◆ Filter View</p>",
        unsafe_allow_html=True,
    )
    route_opts    = ["All"] + sorted(df["Route"].dropna().unique().tolist())
    aircraft_opts = ["All"] + sorted(df["Aircraft_Type"].dropna().unique().tolist())
    season_opts   = ["All"] + sorted(df["Season"].dropna().unique().tolist())
    decision_opts = ["All"] + sorted(df["Route_Decision"].dropna().unique().tolist())

    sel_route    = st.selectbox("✈  Route",         route_opts)
    sel_aircraft = st.selectbox("🛩  Aircraft Type", aircraft_opts)
    sel_season   = st.selectbox("🌿  Season",        season_opts)
    sel_decision = st.selectbox("🏷  Decision",      decision_opts)

    st.markdown("---")
    st.markdown(f"""
    <p style='font-size:0.48rem;color:{ACCENT_2};font-weight:400;letter-spacing:0.14em;
    text-transform:uppercase;margin-bottom:10px;font-family:Press Start 2P,monospace;line-height:1.8'>
    ◆ Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:0.82rem;color:{INK_SOFT};font-family:Nunito,sans-serif'>
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
#  HERO — Kinich pixel art style
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-left">
    <div class="hero-eyebrow">◆ Route Intelligence Platform ◆</div>
    <h1>Airline Profitability System</h1>
    <p>Sample airline dataset · for analysis &amp; demonstration only</p>
  </div>
  <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.7rem;position:relative;z-index:1">
    <div class="hero-badge">⚡ ML-Powered</div>
    <!-- Pixel art Kinich-style companion sprite (CSS-drawn) -->
    <div style="
      width:48px;height:48px;
      image-rendering:pixelated;
      background:
        /* body */
        radial-gradient(circle at 50% 45%, {ACCENT} 40%, transparent 41%),
        /* gold eyes */
        radial-gradient(circle at 38% 42%, {ACCENT_2} 6%, transparent 7%),
        radial-gradient(circle at 62% 42%, {ACCENT_2} 6%, transparent 7%),
        /* lime outline */
        radial-gradient(circle at 50% 45%, transparent 38%, {PIXEL_GREEN} 39%, {PIXEL_GREEN} 44%, transparent 45%);
      border:2px solid {ACCENT_2};
      border-radius:0;
      box-shadow:3px 3px 0 rgba(15,45,26,0.35);
      animation:pixelFloat 3s ease-in-out infinite;
    " title="Kinich's Companion"></div>
  </div>
  <div class="hero-glyph">✈</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Overview",
    "🔍  Drivers",
    "🗺  Routes",
    "📈  Stability",
    "🤖  Predict",
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
    st.markdown('<div class="divider-label">◆ Composition ◆</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<p class="section-hd">Decision Mix</p>', unsafe_allow_html=True)
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN,
              "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
        wedge_colors = [wc[l] for l in dc.index]
        shimmer_pie_chart(
            title="Share of Flights by Decision",
            labels=dc.index.tolist(),
            values=dc.values.tolist(),
            colors=wedge_colors,
            height=390,
        )

    with right:
        st.markdown('<p class="section-hd">Average Metrics by Decision</p>', unsafe_allow_html=True)
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
          <strong style="color:{ACCENT}">◆ How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:{CHART_EXPAND}">Expand</strong> routes should have the highest values across all three columns.
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

    st.markdown('<div class="divider-label">◆ Cost Breakdown ◆</div>', unsafe_allow_html=True)
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
    kinich_ramp = [CHART_EXPAND, PIXEL_TEAL, ACCENT, CHART_MAINTAIN,
                   PIXEL_GREEN, CHART_OPTIMIZE, CHART_DROP, "#5a8a6a"]
    neutral_cols = kinich_ramp[:nc]

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
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
        "Top routes currently classified as Expand</p>", unsafe_allow_html=True)
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
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
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
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
            "Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
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
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">◆ Distribution ◆</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
        "How many unique routes appear in each category?</p>", unsafe_allow_html=True)

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
    st.markdown('<p class="section-hd">Simulate a Route Scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)

    shimmer_vertical_bar_chart(
        title="Model Accuracy & F1 Comparison",
        labels=comparison["Model"].tolist(),
        series=[
            {"name": "Accuracy", "values": comparison["Accuracy"].tolist(), "color": ACCENT},
            {"name": "Macro F1", "values": comparison["Macro F1"].tolist(),  "color": ACCENT_2},
        ],
        max_value=1.0,
        value_format="percent",
        height=430,
    )

    st.markdown('<div class="divider-label">◆ Configuration ◆</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a Prediction Mode</p>', unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
    <span class='pill pill-maintain'>With Revenue</span>&nbsp; Most accurate — use when you have ticket &amp; ancillary revenue data.<br><br>
    <span class='pill pill-optimize'>Cost-only</span>&nbsp; Good accuracy using cost data only, no revenue figures needed.<br><br>
    <span class='pill pill-expand'>Pre-launch</span>&nbsp; Use before a route launches, when only capacity/demand signals are known.
    </div>""", unsafe_allow_html=True)

    model_choice = st.selectbox(
        "Prediction mode",
        ["With Revenue Variables", "Without Revenue Variables", "Only Pre-Operational Features"],
        key="model_choice_select",
    )

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<p class="col-label">✈ Flight Basics</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown('<p class="col-label">🌍 Route Context</p>', unsafe_allow_html=True)
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
                st.markdown('<p class="col-label">💸 Cost Breakdown</p>', unsafe_allow_html=True)
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

        submitted = st.form_submit_button("◆ Get Route Decision")

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
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Oxanium",sans-serif;font-size:1.45rem;font-weight:700;
                      color:{text_col.get(pred, INK)};margin-bottom:10px;letter-spacing:0.06em;
                      text-transform:uppercase'>
            ◆ Suggested Decision: {pred}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-size:0.88rem;line-height:1.80;
                    font-family:"Nunito",sans-serif'>
            {explanations.get(pred, "")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.76rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:Nunito,sans-serif'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision": cls, "Probability": prob})
                   .sort_values("Probability", ascending=False))
        bar_cp  = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN,
                   "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
        bar_colors = [bar_cp.get(d, ACCENT) for d in prob_df["Decision"]]

        shimmer_vertical_bar_chart(
            title="Model Confidence per Decision",
            labels=prob_df["Decision"].tolist(),
            series=[{
                "name": "Probability",
                "values": prob_df["Probability"].tolist(),
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
<div style='text-align:center;padding:40px 0 18px'>
  <div style='display:inline-flex;align-items:center;gap:14px;
              background:rgba(240,247,234,0.90);
              border:2px solid rgba(212,160,23,0.40);
              padding:0.55rem 1.6rem;
              box-shadow:3px 3px 0 rgba(15,45,26,0.20);
              font-family:"Press Start 2P",monospace;
              font-size:0.44rem; line-height:1.8;
              font-weight:400;
              color:{INK_MUTED};
              letter-spacing:0.10em;
              text-transform:uppercase;
              image-rendering:pixelated'>
    <span style='color:{ACCENT};font-size:0.60rem'>◆</span>
    Airline Profitability System
    <span style='color:{ACCENT_2};font-size:0.60rem'>◆</span>
    Built with Streamlit
    <span style='color:{ACCENT};font-size:0.60rem'>◆</span>
  </div>
</div>
""", unsafe_allow_html=True)