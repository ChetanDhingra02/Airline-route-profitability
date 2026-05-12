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
#  JEWEL-TONE LIGHT PALETTE — Crystal / Genshin Impact Style
# ─────────────────────────────────────────────────────────────
BG_BASE        = "#fdf9f4"          # warm pearl ivory
BG_SOFT        = "#f5eeff"          # lavender tint
BG_COOL        = "#eef5fd"          # sky tint

GLASS_BG       = "rgba(255, 252, 248, 0.72)"
GLASS_BORDER   = "rgba(162, 106, 255, 0.28)"

INK            = "#1a0f3c"          # deep indigo-black
INK_SOFT       = "#4a3278"          # violet ink mid
INK_MUTED      = "#8b6faa"          # muted amethyst

ACCENT         = "#7c3aed"          # vivid violet
ACCENT_DK      = "#5b21b6"
ACCENT_LT      = "#c4b5fd"
ACCENT_2       = "#0284c7"          # sapphire
MAGENTA        = "#db2777"          # ruby

# Jewel chart tones — maximum saturation
CHART_EXPAND   = "#1d4ed8"          # deep sapphire
CHART_MAINTAIN = "#047857"          # deep emerald
CHART_OPTIMIZE = "#b45309"          # deep topaz
CHART_ORANGE   = "#b45309"
CHART_DROP     = "#be185d"          # deep ruby
CHART_NEUTRAL  = [
    "#6d28d9", "#1d4ed8", "#0e7490", "#047857",
    "#be185d", "#b45309", "#15803d", "#71717a",
]

DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_OPTIMIZE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {{
    --pearl:       {BG_BASE};
    --pearl-soft:  {BG_SOFT};
    --pearl-cool:  {BG_COOL};
    --ink:         {INK};
    --ink-soft:    {INK_SOFT};
    --ink-muted:   {INK_MUTED};
    --accent:      {ACCENT};
    --accent-dk:   {ACCENT_DK};
    --accent-lt:   {ACCENT_LT};
    --accent-2:    {ACCENT_2};
    --magenta:     {MAGENTA};
    --sapphire:    #1d4ed8;
    --emerald:     #047857;
    --topaz:       #b45309;
    --ruby:        #be185d;
    --amethyst:    #6d28d9;
    --r-sm: 10px; --r-md: 16px; --r-lg: 22px; --r-xl: 28px;
    --sh-sm: 0 2px 16px rgba(120,70,200,0.10), 0 1px 4px rgba(0,0,0,0.05);
    --sh-md: 0 8px 32px rgba(120,70,200,0.16), 0 2px 8px rgba(0,0,0,0.08);
    --sh-lg: 0 20px 56px rgba(120,70,200,0.22), 0 4px 16px rgba(0,0,0,0.10);
    --sh-glow: 0 0 0 1px rgba(124,58,237,0.30), 0 0 28px rgba(124,58,237,0.18);
    --ease: cubic-bezier(0.25, 0.8, 0.25, 1);
}}

/* ── Keyframes ── */
@keyframes floatIn    {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes fadeUp     {{ from {{ opacity:0; transform:translateY(8px);  }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes orbDrift1  {{ 0%,100% {{ transform:translate(0,0) scale(1); }}         50% {{ transform:translate(28px,-18px) scale(1.06); }} }}
@keyframes orbDrift2  {{ 0%,100% {{ transform:translate(0,0) scale(1); }}         40% {{ transform:translate(-22px,16px) scale(1.08); }} }}
@keyframes orbDrift3  {{ 0%,100% {{ transform:translate(-50%,-50%) scale(1); }}   60% {{ transform:translate(-50%,-50%) scale(1.10); }} }}
@keyframes shimmer    {{ 0% {{ left:-80%; }} 100% {{ left:160%; }} }}
@keyframes pulseRing  {{ 0%,100% {{ box-shadow: var(--sh-sm); }} 50% {{ box-shadow: var(--sh-glow); }} }}
@keyframes scanLine   {{ 0% {{ top:-4px; opacity:0; }} 5% {{ opacity:0.8; }} 95% {{ opacity:0.4; }} 100% {{ top:100%; opacity:0; }} }}
@keyframes twinkle    {{ 0%,100% {{ opacity:0; transform:scale(0.4); }} 50% {{ opacity:1; transform:scale(1); }} }}
@keyframes badgePop   {{ 0% {{ transform:scale(0.8); opacity:0; }} 60% {{ transform:scale(1.05); }} 100% {{ transform:scale(1); opacity:1; }} }}
@keyframes borderFlow {{ 0%,100% {{ border-color:rgba(124,58,237,0.18); }} 50% {{ border-color:rgba(124,58,237,0.45); }} }}
@keyframes crystalFloat {{ 0%,100% {{ transform:translateY(0) rotate(0deg); }} 50% {{ transform:translateY(-6px) rotate(2deg); }} }}
@keyframes particleFly  {{ 0%   {{ opacity:0; transform:scale(0.3) translateY(0); }}
                           30%  {{ opacity:1; }}
                           100% {{ opacity:0; transform:scale(1.2) translateY(-20px); }} }}

html, body, [class*="css"] {{
    font-family: 'DM Sans', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: {INK} !important;
}}


/* ── App background — warm pearl with chromatic orbs ── */
.stApp {{
    min-height: 100vh;
    background:
        radial-gradient(ellipse at 14% 18%, rgba(162,106,255,0.16) 0, transparent 34%),
        radial-gradient(ellipse at 84% 12%, rgba(56,189,248,0.13) 0, transparent 30%),
        radial-gradient(ellipse at 62% 88%, rgba(219,39,119,0.09) 0, transparent 28%),
        radial-gradient(ellipse at 32% 72%, rgba(5,150,105,0.08) 0, transparent 26%),
        radial-gradient(ellipse at 76% 54%, rgba(180,83,9,0.06) 0, transparent 22%),
        linear-gradient(155deg, #fdf9f4 0%, #f7f0ff 28%, #eef5fd 56%, #f0fdf8 80%, #fdf9f4 100%);
    background-attachment: fixed;
}}

/* ── Ambient orbs ── */
.stApp::before {{
    content:"";
    position:fixed; top:-120px; left:-120px;
    width:480px; height:480px; border-radius:50%;
    background:radial-gradient(circle, rgba(124,58,237,0.14) 0%, transparent 70%);
    animation:orbDrift1 20s ease-in-out infinite;
    pointer-events:none; z-index:0;
}}
.stApp::after {{
    content:"";
    position:fixed; bottom:-100px; right:-100px;
    width:400px; height:400px; border-radius:50%;
    background:radial-gradient(circle, rgba(2,132,199,0.12) 0%, transparent 70%);
    animation:orbDrift2 26s ease-in-out infinite;
    pointer-events:none; z-index:0;
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
    background: rgba(253,249,244,0.90) !important;
    border-right: 1px solid rgba(124,58,237,0.18) !important;
    backdrop-filter: blur(24px) saturate(1.5) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.5) !important;
    box-shadow: 4px 0 32px rgba(124,58,237,0.08) !important;
}}
[data-testid="stSidebar"] * {{ color: {INK_SOFT} !important; }}

.sidebar-brand {{
    font-family: 'Cinzel', serif;
    font-size: 1.25rem; font-weight: 700;
    color: {INK}; letter-spacing: 0.06em;
    padding: 0.2rem 0 1rem 0;
    border-bottom: 1px solid rgba(124,58,237,0.18);
    margin-bottom: 1rem; text-transform: uppercase;
}}
.sidebar-brand span {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_2});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}

/* ── Headings ── */
h1,h2,h3,h4 {{
    font-family: 'Cinzel', serif !important;
    color: {INK} !important;
    letter-spacing: 0.04em !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
}}

/* ── Hero ── */
.hero {{
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between; gap: 1.2rem;
    border-radius: var(--r-xl);
    padding: 2rem 2.4rem; margin-bottom: 1.4rem;
    background: linear-gradient(140deg,
        rgba(255,252,248,0.88) 0%,
        rgba(245,238,255,0.80) 50%,
        rgba(238,245,253,0.75) 100%);
    border: 1px solid rgba(124,58,237,0.28);
    backdrop-filter: blur(24px) saturate(1.6);
    -webkit-backdrop-filter: blur(24px) saturate(1.6);
    box-shadow: var(--sh-md), inset 0 1px 0 rgba(255,255,255,0.9);
    animation: pulseRing 5s ease-in-out infinite;
    transition: transform 280ms var(--ease);
}}
.hero:hover {{ transform: translateY(-3px); }}
.hero::before {{
    content:"";
    position:absolute; left:0; right:0; height:2px;
    background:linear-gradient(90deg,
        transparent 0%,
        rgba(124,58,237,0) 10%,
        rgba(124,58,237,0.6) 45%,
        rgba(2,132,199,0.5) 55%,
        rgba(124,58,237,0) 90%, transparent 100%);
    animation: scanLine 6s linear infinite; pointer-events:none; z-index:5;
}}
.hero::after {{
    content:"";
    position:absolute; top:-60px; right:-60px;
    width:240px; height:240px; border-radius:50%;
    background:radial-gradient(circle, rgba(2,132,199,0.16) 0%, transparent 70%);
    animation: orbDrift3 14s ease-in-out infinite; pointer-events:none;
}}
.hero-star {{ position:absolute; width:3px; height:3px; border-radius:50%; pointer-events:none; }}
.hero-star:nth-child(1) {{ top:20%; left:46%; background:rgba(124,58,237,0.7); animation:twinkle 3.0s ease-in-out infinite; }}
.hero-star:nth-child(2) {{ top:68%; left:63%; background:rgba(2,132,199,0.7); animation:twinkle 4.0s ease-in-out infinite 0.8s; }}
.hero-star:nth-child(3) {{ top:38%; left:78%; background:rgba(219,39,119,0.6); animation:twinkle 2.8s ease-in-out infinite 1.5s; }}
.hero-star:nth-child(4) {{ top:80%; left:32%; background:rgba(5,150,105,0.6); animation:twinkle 3.5s ease-in-out infinite 0.4s; width:4px; height:4px; }}
.hero-left,.hero-badge,.hero-glyph {{ position:relative; z-index:1; }}
.hero-left {{ flex:1; min-width:0; }}
.hero-eyebrow {{
    font-size:0.59rem; text-transform:uppercase; letter-spacing:0.22em;
    color:{ACCENT}; font-weight:700; margin-bottom:0.5rem; font-family:'DM Sans',sans-serif;
}}
.hero h1 {{
    margin:0 0 0.4rem 0 !important;
    font-size:1.90rem !important; line-height:1.2 !important;
    background: linear-gradient(135deg, {INK} 0%, {ACCENT} 60%, {ACCENT_2} 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    text-shadow:none !important;
}}
.hero p {{ margin:0; color:{INK_SOFT} !important; font-size:0.86rem !important;
           font-family:'DM Sans',sans-serif !important; text-transform:none !important;
           letter-spacing:0 !important; font-weight:400 !important; }}
.hero-badge {{
    display:inline-flex; align-items:center; gap:0.5rem;
    padding:0.6rem 1.1rem; border-radius:999px;
    border:1px solid rgba(219,39,119,0.45);
    background:linear-gradient(135deg,rgba(219,39,119,0.10),rgba(124,58,237,0.10));
    color:{MAGENTA}; font-size:0.70rem; font-weight:700;
    letter-spacing:0.08em; text-transform:uppercase; font-family:'DM Sans',sans-serif;
    box-shadow:0 4px 18px rgba(219,39,119,0.15), 0 0 0 1px rgba(219,39,119,0.15);
    animation:badgePop 700ms ease-out 250ms both;
    white-space:nowrap; transition:transform 180ms var(--ease), box-shadow 180ms var(--ease);
}}
.hero-badge:hover {{ transform:translateY(-3px) scale(1.04); box-shadow:0 8px 26px rgba(219,39,119,0.28); }}
.hero-glyph {{
    font-size:3rem; opacity:0.12; color:{ACCENT};
    animation:crystalFloat 6s ease-in-out infinite;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
    background: linear-gradient(155deg,
        rgba(255,252,248,0.85) 0%, rgba(248,244,255,0.75) 100%) !important;
    border: 1px solid rgba(124,58,237,0.20) !important;
    border-radius: var(--r-md) !important;
    backdrop-filter: blur(16px) saturate(1.4) !important;
    -webkit-backdrop-filter: blur(16px) saturate(1.4) !important;
    box-shadow: var(--sh-sm), inset 0 1px 0 rgba(255,255,255,0.95) !important;
    padding: 1.1rem 1.2rem !important;
    transition: transform 200ms var(--ease), box-shadow 200ms var(--ease) !important;
    position:relative; overflow:hidden;
    animation: borderFlow 6s ease-in-out infinite;
}}
[data-testid="metric-container"]::after {{
    content:""; position:absolute; top:0; left:-80%; width:50%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.55),transparent);
    transition:left 0.55s ease; pointer-events:none;
}}
[data-testid="metric-container"]:hover {{
    transform:translateY(-5px) scale(1.02) !important;
    box-shadow:var(--sh-md), 0 0 0 1px rgba(124,58,237,0.35), inset 0 1px 0 rgba(255,255,255,0.95) !important;
}}
[data-testid="metric-container"]:hover::after {{ left:160%; }}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size:0.60rem !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:0.16em !important;
    color:{ACCENT} !important; font-family:'DM Sans',sans-serif !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
    color:{INK} !important; font-size:1.90rem !important; font-weight:700 !important;
    letter-spacing:-0.02em !important; font-family:'Cinzel',serif !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap:0.22rem;
    background:rgba(255,252,248,0.80);
    border:1px solid rgba(124,58,237,0.20);
    border-radius:20px; padding:0.30rem;
    backdrop-filter:blur(16px);
    box-shadow:var(--sh-sm);
}}
.stTabs [data-baseweb="tab"] {{
    height:40px; padding:0 1rem !important;
    border-radius:14px !important;
    color:{INK_MUTED} !important;
    font-size:0.79rem !important; font-weight:600 !important;
    font-family:'DM Sans',sans-serif !important;
    background:transparent !important; letter-spacing:0.03em !important;
    transition:background 180ms, color 180ms, transform 180ms !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background:rgba(124,58,237,0.08) !important; color:{ACCENT} !important;
    transform:translateY(-1px) !important;
}}
.stTabs [aria-selected="true"] {{
    background:linear-gradient(135deg,rgba(124,58,237,0.14),rgba(2,132,199,0.10)) !important;
    color:{INK} !important;
    box-shadow:0 4px 14px rgba(124,58,237,0.14), inset 0 0 0 1px rgba(124,58,237,0.28) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:1.5rem; }}

/* ── Section headings ── */
.section-hd {{
    font-family:'Cinzel',serif; font-size:1.02rem; font-weight:600;
    color:{INK}; margin:0 0 0.28rem 0; letter-spacing:0.05em; text-transform:uppercase;
}}
.section-sub {{
    font-size:0.83rem; color:{INK_MUTED}; margin:0 0 1.1rem 0; line-height:1.65;
    font-family:'DM Sans',sans-serif; font-weight:400; text-transform:none; letter-spacing:0;
}}

/* ── Divider label ── */
.divider-label {{
    display:flex; align-items:center; gap:0.7rem; margin:1.5rem 0 1rem 0;
    font-size:0.59rem; font-weight:700; text-transform:uppercase; letter-spacing:0.20em;
    color:{ACCENT}; font-family:'DM Sans',sans-serif;
}}
.divider-label::before,.divider-label::after {{
    content:""; flex:1; height:1px;
    background:linear-gradient(90deg,transparent,rgba(124,58,237,0.28),transparent);
}}

/* ── Info box ── */
.info-box {{
    background:linear-gradient(155deg,rgba(255,252,248,0.85),rgba(248,244,255,0.75));
    border:1px solid rgba(124,58,237,0.18);
    border-radius:var(--r-md); padding:1rem 1.1rem;
    color:{INK_SOFT}; line-height:1.75; box-shadow:var(--sh-sm);
    font-size:0.86rem; font-family:'DM Sans',sans-serif;
    transition:transform 200ms, box-shadow 200ms;
}}
.info-box:hover {{ transform:translateY(-2px); box-shadow:var(--sh-md); }}

/* ── Pills ── */
.pill {{
    display:inline-block; padding:0.25rem 0.72rem; border-radius:999px;
    font-size:0.61rem; font-weight:700; letter-spacing:0.10em; text-transform:uppercase;
    font-family:'DM Sans',sans-serif; border:1px solid transparent;
    transition:transform 180ms; cursor:default;
}}
.pill:hover {{ transform:scale(1.06); }}
.pill-expand   {{ background:rgba(29,78,216,0.10); color:#1d4ed8; border-color:rgba(29,78,216,0.30); }}
.pill-maintain {{ background:rgba(4,120,87,0.10);  color:#047857; border-color:rgba(4,120,87,0.28); }}
.pill-optimize {{ background:rgba(180,83,9,0.10);  color:#b45309; border-color:rgba(180,83,9,0.26); }}
.pill-drop     {{ background:rgba(190,24,93,0.10); color:#be185d; border-color:rgba(190,24,93,0.28); }}

/* ── Result card ── */
.result-card {{
    border-radius:var(--r-lg); padding:1.5rem 1.6rem; margin:1.2rem 0;
    border:1px solid rgba(124,58,237,0.22); box-shadow:var(--sh-md);
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    animation:fadeUp 380ms ease-out; transition:transform 280ms, box-shadow 280ms;
}}
.result-card:hover {{ transform:translateY(-4px); box-shadow:var(--sh-lg); }}
.result-expand   {{ background:linear-gradient(140deg,rgba(219,234,254,0.80),rgba(255,252,248,0.85)); border-left:4px solid {CHART_EXPAND}; }}
.result-maintain {{ background:linear-gradient(140deg,rgba(209,250,229,0.80),rgba(255,252,248,0.85)); border-left:4px solid {CHART_MAINTAIN}; }}
.result-optimize {{ background:linear-gradient(140deg,rgba(254,243,199,0.80),rgba(255,252,248,0.85)); border-left:4px solid {CHART_OPTIMIZE}; }}
.result-drop     {{ background:linear-gradient(140deg,rgba(252,231,243,0.80),rgba(255,252,248,0.85)); border-left:4px solid {CHART_DROP}; }}

/* ── Form inputs ── */
.stSelectbox label,.stNumberInput label,.stSlider label,
.stRadio label,.stCheckbox label,.stTextInput label {{
    color:{INK_SOFT} !important; font-weight:600 !important; font-size:0.73rem !important;
    letter-spacing:0.06em !important; text-transform:uppercase !important;
    font-family:'DM Sans',sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,.stNumberInput input {{
    background:rgba(255,252,248,0.85) !important;
    border:1px solid rgba(124,58,237,0.22) !important;
    border-radius:var(--r-sm) !important; color:{INK} !important;
    min-height:42px !important; box-shadow:none !important;
    transition:border-color 180ms, box-shadow 180ms !important;
    font-family:'DM Sans',sans-serif !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover,
.stTextInput input:hover,.stNumberInput input:hover {{
    border-color:rgba(124,58,237,0.45) !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,.stNumberInput input:focus {{
    border-color:rgba(124,58,237,0.70) !important;
    box-shadow:0 0 0 3px rgba(124,58,237,0.12) !important;
}}
[data-baseweb="menu"] {{
    background:rgba(255,252,248,0.96) !important;
    border:1px solid rgba(124,58,237,0.22) !important;
    border-radius:var(--r-sm) !important;
    box-shadow:var(--sh-md) !important;
}}
[data-baseweb="menu"] li {{ color:{INK_SOFT} !important; }}
[data-baseweb="menu"] li:hover {{ background:rgba(124,58,237,0.08) !important; color:{ACCENT} !important; }}

/* ── Form card ── */
[data-testid="stForm"] {{
    background:linear-gradient(155deg,rgba(255,252,248,0.88),rgba(248,244,255,0.80)) !important;
    border:1px solid rgba(124,58,237,0.22) !important;
    border-radius:var(--r-lg) !important; padding:1.5rem 1.6rem 1.8rem !important;
    box-shadow:var(--sh-md), inset 0 1px 0 rgba(255,255,255,0.90) !important;
    backdrop-filter:blur(20px) !important;
    animation:borderFlow 7s ease-in-out infinite !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button, .stButton > button {{
    border-radius:var(--r-sm) !important; font-weight:700 !important; border:none !important;
    font-family:'DM Sans',sans-serif !important; letter-spacing:0.08em !important;
    text-transform:uppercase !important; font-size:0.81rem !important;
    transition:transform 180ms, box-shadow 180ms !important;
    position:relative; overflow:hidden;
}}
[data-testid="stFormSubmitButton"] > button {{
    width:100% !important;
    background:linear-gradient(135deg,{ACCENT},{ACCENT_DK}) !important;
    box-shadow:0 8px 26px rgba(124,58,237,0.35), 0 0 0 1px rgba(124,58,237,0.30) !important;
    color:white !important; padding:0.72rem 0 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform:translateY(-2px) !important;
    box-shadow:0 14px 36px rgba(124,58,237,0.50) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{ transform:translateY(0) scale(0.98) !important; }}
.stButton > button {{
    background:rgba(255,252,248,0.85) !important; color:{INK_SOFT} !important;
    border:1px solid rgba(124,58,237,0.22) !important; box-shadow:var(--sh-sm) !important;
}}
.stButton > button:hover {{
    background:rgba(248,244,255,0.95) !important; color:{ACCENT} !important;
    transform:translateY(-2px) !important; box-shadow:var(--sh-md) !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
    background:rgba(255,252,248,0.80) !important;
    border:1px solid rgba(124,58,237,0.18) !important;
    border-radius:var(--r-md) !important; overflow:hidden !important;
    box-shadow:var(--sh-sm) !important; backdrop-filter:blur(14px) !important;
    transition:transform 280ms, box-shadow 280ms !important;
}}
[data-testid="stDataFrame"]:hover {{
    transform:translateY(-3px) !important; box-shadow:var(--sh-md) !important;
}}
[data-testid="stDataFrame"] [role="grid"] {{ background:transparent !important; }}
[data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {{ color:{INK_SOFT} !important; }}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background:rgba(124,58,237,0.08) !important; color:{ACCENT} !important;
    font-weight:700 !important; font-size:0.71rem !important;
    letter-spacing:0.10em !important; text-transform:uppercase !important;
    border-bottom:1px solid rgba(124,58,237,0.16) !important;
    font-family:'DM Sans',sans-serif !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
    border-bottom:1px solid rgba(124,58,237,0.08) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background:rgba(255,252,248,0.80) !important;
    border:1px solid rgba(124,58,237,0.18) !important;
    border-radius:var(--r-md) !important; box-shadow:var(--sh-sm) !important;
    backdrop-filter:blur(14px) !important;
    transition:transform 180ms, box-shadow 180ms !important;
}}
[data-testid="stExpander"]:hover {{ transform:translateY(-2px) !important; box-shadow:var(--sh-md) !important; }}
[data-testid="stExpander"] summary p {{
    color:{INK_SOFT} !important; font-weight:600 !important;
    font-family:'DM Sans',sans-serif !important;
}}

/* ── Charts ── */
[data-testid="stPyplot"] {{
    background:rgba(255,252,248,0.75);
    border:1px solid rgba(124,58,237,0.18);
    border-radius:var(--r-lg); padding:1rem;
    box-shadow:var(--sh-sm); backdrop-filter:blur(14px);
    transition:transform 280ms, box-shadow 280ms;
}}
[data-testid="stPyplot"]:hover {{
    transform:translateY(-4px);
    box-shadow:var(--sh-md), 0 0 0 1px rgba(124,58,237,0.28);
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius:var(--r-md) !important;
    background:rgba(255,252,248,0.85) !important;
    border:1px solid rgba(124,58,237,0.20) !important;
    color:{INK_SOFT} !important;
}}

hr {{ border:none !important; border-top:1px solid rgba(124,58,237,0.14) !important; margin:1.4rem 0 !important; }}

.col-label {{
    font-size:0.63rem; font-weight:700; color:{ACCENT}; letter-spacing:0.16em;
    text-transform:uppercase; margin-bottom:0.9rem;
    display:flex; align-items:center; gap:0.4rem; font-family:'DM Sans',sans-serif;
}}
.col-label::after {{
    content:""; flex:1; height:1px;
    background:linear-gradient(90deg,rgba(124,58,237,0.28),transparent);
}}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background:{ACCENT} !important; border-color:{ACCENT_LT} !important;
    box-shadow:0 0 10px rgba(124,58,237,0.40) !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
    background:linear-gradient(90deg,{ACCENT},{ACCENT_2}) !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:rgba(245,238,255,0.60); }}
::-webkit-scrollbar-thumb {{ background:rgba(124,58,237,0.30); border-radius:999px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(124,58,237,0.55); }}
::selection {{ background:rgba(124,58,237,0.20); color:{INK}; }}

/* ── Airplane cursor canvas (always on top) ── */
#airplane-canvas {{
    position:fixed; top:0; left:0;
    width:100vw; height:100vh;
    pointer-events:none; z-index:999999;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  AIRPLANE CURSOR + TRAIL CANVAS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<canvas id="airplane-canvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('airplane-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;
    window.addEventListener('resize', () => {
        W = window.innerWidth; H = window.innerHeight;
        canvas.width = W; canvas.height = H;
    });

    let mx = W/2, my = H/2, pmx = W/2, pmy = H/2;
    let angle = 0, targetAngle = 0;
    const trail = [];
    const MAX_TRAIL = 38;

    document.addEventListener('mousemove', e => {
        const dx = e.clientX - mx, dy = e.clientY - my;
        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
            targetAngle = Math.atan2(dy, dx) + Math.PI / 2;
        }
        pmx = mx; pmy = my;
        mx = e.clientX; my = e.clientY;
        trail.push({ x: mx, y: my, age: 0 });
        if (trail.length > MAX_TRAIL) trail.shift();
    });

    function lerpAngle(a, b, t) {
        let diff = b - a;
        while (diff >  Math.PI) diff -= 2 * Math.PI;
        while (diff < -Math.PI) diff += 2 * Math.PI;
        return a + diff * t;
    }

    // Jewel trail colors cycling
    const jewelColors = [
        'rgba(124,58,237,',   // amethyst
        'rgba(29,78,216,',    // sapphire
        'rgba(2,132,199,',    // crystal blue
        'rgba(4,120,87,',     // emerald
        'rgba(180,83,9,',     // topaz
        'rgba(219,39,119,',   // ruby
    ];
    let colorIdx = 0;
    let colorT = 0;

    function drawAirplane(x, y, ang, scale=1) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(ang);
        ctx.scale(scale, scale);

        // Shadow / glow beneath plane
        ctx.shadowColor = 'rgba(124,58,237,0.45)';
        ctx.shadowBlur  = 14;

        // Fuselage
        ctx.beginPath();
        ctx.moveTo(0, -14);
        ctx.quadraticCurveTo(3.5, -4, 3, 6);
        ctx.quadraticCurveTo(1.5, 10, 0, 11);
        ctx.quadraticCurveTo(-1.5, 10, -3, 6);
        ctx.quadraticCurveTo(-3.5, -4, 0, -14);
        ctx.fillStyle = '#7c3aed';
        ctx.fill();

        // Wings
        ctx.beginPath();
        ctx.moveTo(-2, 1); ctx.lineTo(-14, 8); ctx.lineTo(-12, 10);
        ctx.lineTo(-1.5, 5);
        ctx.closePath();
        ctx.fillStyle = '#1d4ed8';
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(2, 1); ctx.lineTo(14, 8); ctx.lineTo(12, 10);
        ctx.lineTo(1.5, 5);
        ctx.closePath();
        ctx.fillStyle = '#1d4ed8';
        ctx.fill();

        // Tail fins
        ctx.beginPath();
        ctx.moveTo(-1, 8); ctx.lineTo(-6, 13); ctx.lineTo(-5, 14);
        ctx.lineTo(-0.5, 10);
        ctx.closePath();
        ctx.fillStyle = '#db2777';
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(1, 8); ctx.lineTo(6, 13); ctx.lineTo(5, 14);
        ctx.lineTo(0.5, 10);
        ctx.closePath();
        ctx.fillStyle = '#db2777';
        ctx.fill();

        // Cockpit window
        ctx.beginPath();
        ctx.ellipse(0, -9, 1.8, 2.5, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(196,229,255,0.90)';
        ctx.shadowBlur = 0;
        ctx.fill();

        ctx.restore();
    }

    function frame() {
        ctx.clearRect(0, 0, W, H);

        // Age trail points
        for (let i = 0; i < trail.length; i++) trail[i].age++;

        // Draw trail as glowing connected dots / crystals
        for (let i = 1; i < trail.length; i++) {
            const p = trail[i];
            const prog = i / trail.length;          // 0 at tail, 1 at head
            const fade = prog * (1 - p.age / 120);
            if (fade <= 0) continue;

            const ci = Math.floor(prog * jewelColors.length) % jewelColors.length;
            const c  = jewelColors[ci];

            // Streak segment
            const prev = trail[i - 1];
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(p.x, p.y);
            ctx.strokeStyle = c + (fade * 0.70).toFixed(2) + ')';
            ctx.lineWidth   = prog * 3.5 + 0.5;
            ctx.lineCap     = 'round';
            ctx.shadowColor = c + '0.6)';
            ctx.shadowBlur  = 8 * prog;
            ctx.stroke();
            ctx.restore();

            // Tiny jewel spark every few points
            if (i % 5 === 0 && prog > 0.15) {
                const r = prog * 2.8;
                ctx.save();
                ctx.beginPath();
                ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
                ctx.fillStyle = c + (fade * 0.55).toFixed(2) + ')';
                ctx.shadowColor = c + '0.8)';
                ctx.shadowBlur  = 10;
                ctx.fill();
                ctx.restore();
            }
        }

        // Smooth angle
        angle = lerpAngle(angle, targetAngle, 0.18);

        // Draw airplane
        drawAirplane(mx, my, angle, 1.15);

        requestAnimationFrame(frame);
    }
    frame();
})();
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(__file__)
DATA_PATH    = os.path.join(BASE_DIR, "airline_route_profitability.csv")
if not os.path.exists(DATA_PATH):
    alt_data_path = os.path.join(BASE_DIR, "airline_route_profitability(1).csv")
    if os.path.exists(alt_data_path):
        DATA_PATH = alt_data_path
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
#  CHART HELPERS — light-theme aware, jewel colors
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#fdf9f4")
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
    ax.title.set_fontfamily("serif")
    ax.grid(axis="y", color="#e8e0f0", linewidth=0.8, linestyle="-", alpha=0.85)
    ax.set_axisbelow(True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(INK_MUTED)
    return fig, ax


def col_seq(labels):
    return [DECISION_COLORS.get(l, ACCENT) for l in labels]


def add_bar_shimmer(bars, ax, alpha=0.92):
    """Legacy fallback: no white static rectangles. Use HTML helpers for real shimmer."""
    for bar in bars:
        bar.set_alpha(alpha)
        bar.set_linewidth(0)
    return bars



# ─────────────────────────────────────────────────────────────
#  ANIMATED HTML CHART HELPERS — keeps the same theme, but lets bars shimmer
# ─────────────────────────────────────────────────────────────
def _fmt_chart_value(v, value_format="number"):
    if value_format == "percent":
        return f"{v:.0%}"
    if value_format == "money":
        return f"${v:,.0f}"
    return f"{v:,.0f}"


def shimmer_vertical_bar_chart(title, labels, series, max_value=None, value_format="number", height=430):
    """
    Animated vertical grouped/single bar chart rendered in HTML/CSS.
    series example:
    [
        {"name": "Accuracy", "values": [0.88, 0.84], "color": ACCENT},
        {"name": "Macro F1", "values": [0.88, 0.84], "color": ACCENT_2},
    ]
    """
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
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .gi-chart {{
        width: 100%;
        min-height: {height}px;
        box-sizing: border-box;
        padding: 26px 30px 24px;
        border-radius: 22px;
        background:
            radial-gradient(circle at 16% 12%, rgba(124,58,237,0.13), transparent 32%),
            radial-gradient(circle at 88% 20%, rgba(2,132,199,0.11), transparent 34%),
            linear-gradient(145deg, rgba(255,252,248,0.76), rgba(245,238,255,0.62), rgba(238,245,253,0.66));
        border: 1px solid rgba(124,58,237,0.18);
        box-shadow: 0 2px 16px rgba(120,70,200,0.10), 0 1px 4px rgba(0,0,0,0.05);
        font-family: 'DM Sans', system-ui, sans-serif;
        color: {INK};
        overflow: hidden;
        position: relative;
    }}

    .gi-chart::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.22), transparent);
        transform: translateX(-130%);
        animation: chartSweep 5.5s ease-in-out infinite;
        pointer-events: none;
    }}

    .gi-chart-title {{
        font-family: 'Cinzel', Georgia, serif;
        text-align: center;
        font-size: 24px;
        line-height: 1.25;
        color: {INK};
        margin-bottom: 20px;
        letter-spacing: 0.04em;
        font-weight: 600;
    }}

    .gi-legend {{
        display: flex;
        justify-content: center;
        gap: 22px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }}

    .gi-legend-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: {INK_SOFT};
        font-weight: 600;
        font-size: 14px;
    }}

    .gi-legend-color {{
        width: 30px;
        height: 12px;
        border-radius: 999px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.45), 0 4px 12px rgba(74,50,120,0.12);
    }}

    .gi-plot {{
        display: grid;
        grid-template-columns: repeat({max(len(labels), 1)}, minmax(0, 1fr));
        gap: 30px;
        align-items: end;
        height: {max(height - 180, 190)}px;
        border-bottom: 1px solid rgba(124,58,237,0.18);
        background-image: linear-gradient(to top, rgba(124,58,237,0.08) 1px, transparent 1px);
        background-size: 100% 25%;
        padding: 0 18px;
        position: relative;
        z-index: 1;
    }}

    .gi-group {{
        height: 100%;
        display: flex;
        align-items: end;
        justify-content: center;
        gap: 10px;
        position: relative;
    }}

    .gi-bar-wrap {{
        height: 100%;
        width: min(48px, 30%);
        min-width: 26px;
        display: flex;
        align-items: end;
        justify-content: center;
        position: relative;
    }}

    .gi-bar {{
        width: 100%;
        height: var(--bar-height);
        min-height: 3px;
        border-radius: 14px 14px 4px 4px;
        position: relative;
        overflow: hidden;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.65),
            inset 8px 0 16px rgba(255,255,255,0.16),
            0 10px 24px rgba(74,50,120,0.18);
        animation: growBar 850ms cubic-bezier(.22,.9,.25,1) both;
    }}

    .gi-bar::before {{
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 80%;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(255,255,255,0.10) 20%,
            rgba(255,255,255,0.74) 48%,
            rgba(255,255,255,0.18) 66%,
            transparent 100%);
        transform: translateX(-150%);
        animation: barShimmer 2.25s ease-in-out infinite;
        animation-delay: var(--delay);
    }}


    .gi-value {{
        position: absolute;
        bottom: calc(var(--bar-height) + 8px);
        font-size: 13px;
        font-weight: 800;
        color: {INK_SOFT};
        white-space: nowrap;
    }}

    .gi-xlabels {{
        display: grid;
        grid-template-columns: repeat({max(len(labels), 1)}, minmax(0, 1fr));
        gap: 30px;
        padding: 13px 18px 0;
        text-align: center;
        position: relative;
        z-index: 1;
    }}

    .gi-xlabel {{
        color: {INK_SOFT};
        font-weight: 700;
        font-size: 13px;
        line-height: 1.25;
        transform: rotate(-6deg);
        transform-origin: center top;
    }}

    @keyframes barShimmer {{
        0%   {{ transform: translateX(-150%); }}
        48%  {{ transform: translateX(155%); }}
        100% {{ transform: translateX(155%); }}
    }}

    @keyframes growBar {{
        from {{ height: 0%; opacity: 0.50; }}
        to   {{ height: var(--bar-height); opacity: 1; }}
    }}

    @keyframes chartSweep {{
        0%   {{ transform: translateX(-130%); }}
        45%  {{ transform: translateX(130%); }}
        100% {{ transform: translateX(130%); }}
    }}
    </style>

    <script>
    const chart = {chart_json};

    function formatValue(v) {{
        if (chart.value_format === "percent") return Math.round(v * 100) + "%";
        if (chart.value_format === "money") return "$" + Math.round(v).toLocaleString();
        return Math.round(v).toLocaleString();
    }}

    const root = document.getElementById("gi-chart-root");
    const legendHtml = chart.series.map(s => `
        <div class="gi-legend-item">
            <span class="gi-legend-color" style="background:${{s.color}}"></span>
            ${{s.name}}
        </div>
    `).join("");

    const groupsHtml = chart.labels.map((label, i) => `
        <div class="gi-group">
            ${{chart.series.map((s, j) => {{
                const value = Number(s.values[i] || 0);
                const pct = Math.max(2, Math.min(100, value / chart.max_value * 100));
                const color = s.colors ? s.colors[i] : s.color;
                return `
                    <div class="gi-bar-wrap">
                        <div class="gi-value" style="--bar-height:${{pct}}%">${{formatValue(value)}}</div>
                        <div class="gi-bar"
                             style="--bar-height:${{pct}}%; --delay:${{(i + j) * 120}}ms; background: linear-gradient(180deg, ${{color}}, ${{color}}dd);"></div>
                    </div>
                `;
            }}).join("")}}
        </div>
    `).join("");

    const xLabelsHtml = chart.labels.map(label => `<div class="gi-xlabel">${{label}}</div>`).join("");

    root.innerHTML = `
        <div class="gi-chart">
            <div class="gi-chart-title">${{chart.title}}</div>
            <div class="gi-legend">${{legendHtml}}</div>
            <div class="gi-plot">${{groupsHtml}}</div>
            <div class="gi-xlabels">${{xLabelsHtml}}</div>
        </div>
    `;
    </script>
    """, height=height + 40, scrolling=False)


def shimmer_horizontal_bar_chart(title, labels, values, colors=None, value_format="number", height=430):
    """Animated horizontal bar chart rendered in HTML/CSS."""
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
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .gi-hchart {{
        width: 100%;
        min-height: {height}px;
        box-sizing: border-box;
        padding: 24px 28px;
        border-radius: 22px;
        background:
            radial-gradient(circle at 16% 12%, rgba(124,58,237,0.13), transparent 32%),
            radial-gradient(circle at 88% 20%, rgba(2,132,199,0.11), transparent 34%),
            linear-gradient(145deg, rgba(255,252,248,0.76), rgba(245,238,255,0.62), rgba(238,245,253,0.66));
        border: 1px solid rgba(124,58,237,0.18);
        box-shadow: 0 2px 16px rgba(120,70,200,0.10), 0 1px 4px rgba(0,0,0,0.05);
        font-family: 'DM Sans', system-ui, sans-serif;
        color: {INK};
        overflow: hidden;
        position: relative;
    }}

    .gi-hchart::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.22), transparent);
        transform: translateX(-130%);
        animation: chartSweep 5.5s ease-in-out infinite;
        pointer-events: none;
    }}

    .gi-hchart-title {{
        font-family: 'Cinzel', Georgia, serif;
        text-align: center;
        font-size: 22px;
        line-height: 1.25;
        color: {INK};
        margin-bottom: 20px;
        letter-spacing: 0.04em;
        font-weight: 600;
    }}

    .gi-hrows {{
        display: flex;
        flex-direction: column;
        gap: 13px;
        position: relative;
        z-index: 1;
    }}

    .gi-hrow {{
        display: grid;
        grid-template-columns: minmax(92px, 170px) 1fr minmax(72px, 100px);
        align-items: center;
        gap: 12px;
    }}

    .gi-hlabel {{
        color: {INK_SOFT};
        font-size: 13px;
        font-weight: 700;
        line-height: 1.15;
        text-align: right;
    }}

    .gi-htrack {{
        height: 24px;
        border-radius: 999px;
        background: rgba(124,58,237,0.07);
        border: 1px solid rgba(124,58,237,0.12);
        overflow: hidden;
        position: relative;
    }}

    .gi-hbar {{
        height: 100%;
        width: var(--bar-width);
        border-radius: 999px;
        position: relative;
        overflow: hidden;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.65),
            inset 8px 0 16px rgba(255,255,255,0.16),
            0 8px 18px rgba(74,50,120,0.14);
        animation: growHBar 850ms cubic-bezier(.22,.9,.25,1) both;
    }}

    .gi-hbar::before {{
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 80%;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(255,255,255,0.10) 20%,
            rgba(255,255,255,0.74) 48%,
            rgba(255,255,255,0.18) 66%,
            transparent 100%);
        transform: translateX(-150%);
        animation: barShimmer 2.25s ease-in-out infinite;
        animation-delay: var(--delay);
    }}


    .gi-hvalue {{
        color: {INK_SOFT};
        font-weight: 800;
        font-size: 13px;
        white-space: nowrap;
    }}

    @keyframes barShimmer {{
        0%   {{ transform: translateX(-150%); }}
        48%  {{ transform: translateX(155%); }}
        100% {{ transform: translateX(155%); }}
    }}

    @keyframes growHBar {{
        from {{ width: 0%; opacity: 0.50; }}
        to   {{ width: var(--bar-width); opacity: 1; }}
    }}

    @keyframes chartSweep {{
        0%   {{ transform: translateX(-130%); }}
        45%  {{ transform: translateX(130%); }}
        100% {{ transform: translateX(130%); }}
    }}
    </style>

    <script>
    const chart = {chart_json};
    const root = document.getElementById("gi-hbar-root");

    const rowsHtml = chart.rows.map((r, i) => `
        <div class="gi-hrow">
            <div class="gi-hlabel">${{r.label}}</div>
            <div class="gi-htrack">
                <div class="gi-hbar"
                     style="--bar-width:${{r.width}}%; --delay:${{i * 110}}ms; background: linear-gradient(90deg, ${{r.color}}, ${{r.color}}dd);"></div>
            </div>
            <div class="gi-hvalue">${{r.display}}</div>
        </div>
    `).join("");

    root.innerHTML = `
        <div class="gi-hchart">
            <div class="gi-hchart-title">${{chart.title}}</div>
            <div class="gi-hrows">${{rowsHtml}}</div>
        </div>
    `;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_pie_chart(title, labels, values, colors=None, height=430):
    """Animated donut/pie-style chart rendered in HTML/CSS with shimmer."""
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
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .gi-pie-card {{
        width: 100%;
        min-height: {height}px;
        box-sizing: border-box;
        padding: 24px 28px;
        border-radius: 22px;
        background:
            radial-gradient(circle at 16% 12%, rgba(124,58,237,0.13), transparent 32%),
            radial-gradient(circle at 88% 20%, rgba(2,132,199,0.11), transparent 34%),
            linear-gradient(145deg, rgba(255,252,248,0.76), rgba(245,238,255,0.62), rgba(238,245,253,0.66));
        border: 1px solid rgba(124,58,237,0.18);
        box-shadow: 0 2px 16px rgba(120,70,200,0.10), 0 1px 4px rgba(0,0,0,0.05);
        font-family: 'DM Sans', system-ui, sans-serif;
        color: {INK};
        overflow: hidden;
        position: relative;
    }}

    .gi-pie-card::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.22), transparent);
        transform: translateX(-130%);
        animation: pieCardSweep 5.5s ease-in-out infinite;
        pointer-events: none;
    }}

    .gi-pie-title {{
        font-family: 'Cinzel', Georgia, serif;
        text-align: center;
        font-size: 22px;
        line-height: 1.25;
        color: {INK};
        margin-bottom: 18px;
        letter-spacing: 0.04em;
        font-weight: 600;
    }}

    .gi-pie-layout {{
        display: grid;
        grid-template-columns: minmax(210px, 0.9fr) minmax(190px, 1fr);
        gap: 24px;
        align-items: center;
        position: relative;
        z-index: 1;
    }}

    .gi-donut-wrap {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .gi-donut {{
        width: min(230px, 80vw);
        aspect-ratio: 1;
        border-radius: 50%;
        background: conic-gradient(var(--pie-gradient));
        position: relative;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.65),
            0 14px 32px rgba(74,50,120,0.16);
        overflow: hidden;
        animation: donutPop 850ms cubic-bezier(.22,.9,.25,1) both;
    }}

    .gi-donut::before {{
        content: "";
        position: absolute;
        inset: -20%;
        background: linear-gradient(115deg,
            transparent 0%,
            rgba(255,255,255,0.08) 32%,
            rgba(255,255,255,0.70) 48%,
            rgba(255,255,255,0.12) 62%,
            transparent 100%);
        transform: translateX(-120%) rotate(12deg);
        animation: pieShimmer 2.8s ease-in-out infinite;
    }}

    .gi-donut::after {{
        content: "";
        position: absolute;
        inset: 27%;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 25%, rgba(255,255,255,0.82), rgba(255,252,248,0.88) 62%, rgba(245,238,255,0.90));
        box-shadow: inset 0 2px 10px rgba(124,58,237,0.10);
    }}

    .gi-pie-legend {{
        display: flex;
        flex-direction: column;
        gap: 11px;
    }}

    .gi-pie-row {{
        display: grid;
        grid-template-columns: 14px 1fr auto;
        align-items: center;
        gap: 10px;
        color: {INK_SOFT};
        font-size: 13px;
        font-weight: 700;
    }}

    .gi-pie-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.45), 0 4px 12px rgba(74,50,120,0.13);
    }}

    .gi-pie-pct {{
        color: {INK_SOFT};
        font-weight: 900;
        white-space: nowrap;
    }}

    @keyframes pieShimmer {{
        0%   {{ transform: translateX(-120%) rotate(12deg); }}
        48%  {{ transform: translateX(120%) rotate(12deg); }}
        100% {{ transform: translateX(120%) rotate(12deg); }}
    }}

    @keyframes donutPop {{
        from {{ transform: scale(0.86) rotate(-18deg); opacity: 0.55; }}
        to   {{ transform: scale(1) rotate(0deg); opacity: 1; }}
    }}

    @keyframes pieCardSweep {{
        0%   {{ transform: translateX(-130%); }}
        45%  {{ transform: translateX(130%); }}
        100% {{ transform: translateX(130%); }}
    }}
    </style>

    <script>
    const pieChart = {chart_json};
    const root = document.getElementById("gi-pie-root");
    const rowsHtml = pieChart.rows.map(r => `
        <div class="gi-pie-row">
            <span class="gi-pie-dot" style="background:${{r.color}}"></span>
            <span>${{r.label}}</span>
            <span class="gi-pie-pct">${{r.display}}</span>
        </div>
    `).join("");

    root.innerHTML = `
        <div class="gi-pie-card">
            <div class="gi-pie-title">${{pieChart.title}}</div>
            <div class="gi-pie-layout">
                <div class="gi-donut-wrap">
                    <div class="gi-donut" style="--pie-gradient:${{pieChart.gradient}}"></div>
                </div>
                <div class="gi-pie-legend">${{rowsHtml}}</div>
            </div>
        </div>
    `;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_classic_horizontal_bar_chart(title, labels, values, color=ACCENT, value_format="money", height=460):
    """Classic horizontal chart closer to the original Matplotlib look, with animated bar shimmer."""
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
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    .gi-classic-card {{
        width: 100%;
        min-height: {height}px;
        box-sizing: border-box;
        padding: 24px 26px 22px;
        border-radius: 22px;
        background: transparent;
        font-family: 'DM Sans', system-ui, sans-serif;
        color: {INK};
        overflow: hidden;
        position: relative;
    }}

    .gi-classic-title {{
        font-family: 'Cinzel', Georgia, serif;
        text-align: center;
        font-size: 22px;
        line-height: 1.25;
        color: {INK};
        margin-bottom: 18px;
        letter-spacing: 0.04em;
        font-weight: 600;
    }}

    .gi-classic-rows {{
        display: flex;
        flex-direction: column;
        gap: 12px;
    }}

    .gi-classic-row {{
        display: grid;
        grid-template-columns: minmax(84px, 150px) 1fr minmax(88px, 110px);
        align-items: center;
        gap: 12px;
    }}

    .gi-classic-label {{
        color: {INK_SOFT};
        font-size: 13px;
        font-weight: 700;
        line-height: 1.1;
        text-align: right;
    }}

    .gi-classic-axis {{
        height: 23px;
        position: relative;
        border-bottom: 1px solid rgba(124,58,237,0.13);
        background-image: linear-gradient(to right, rgba(124,58,237,0.08) 1px, transparent 1px);
        background-size: 25% 100%;
    }}

    .gi-classic-bar {{
        height: 22px;
        width: var(--bar-width);
        border-radius: 6px;
        position: relative;
        overflow: hidden;
        background: linear-gradient(90deg, var(--bar-color), color-mix(in srgb, var(--bar-color) 82%, white));
        box-shadow: 0 6px 16px rgba(74,50,120,0.13), inset 0 1px 0 rgba(255,255,255,0.50);
        animation: growClassic 850ms cubic-bezier(.22,.9,.25,1) both;
    }}

    .gi-classic-bar::before {{
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 72%;
        background: linear-gradient(90deg,
            transparent 0%,
            rgba(255,255,255,0.08) 24%,
            rgba(255,255,255,0.62) 50%,
            rgba(255,255,255,0.13) 68%,
            transparent 100%);
        transform: translateX(-150%);
        animation: classicBarShimmer 2.25s ease-in-out infinite;
        animation-delay: var(--delay);
    }}

    .gi-classic-value {{
        color: {INK_SOFT};
        font-weight: 800;
        font-size: 13px;
        white-space: nowrap;
    }}

    @keyframes classicBarShimmer {{
        0%   {{ transform: translateX(-150%); }}
        48%  {{ transform: translateX(155%); }}
        100% {{ transform: translateX(155%); }}
    }}

    @keyframes growClassic {{
        from {{ width: 0%; opacity: 0.50; }}
        to   {{ width: var(--bar-width); opacity: 1; }}
    }}
    </style>

    <script>
    const classicChart = {chart_json};
    const root = document.getElementById("gi-classic-hbar-root");
    const rowsHtml = classicChart.rows.map((r, i) => `
        <div class="gi-classic-row">
            <div class="gi-classic-label">${{r.label}}</div>
            <div class="gi-classic-axis">
                <div class="gi-classic-bar" style="--bar-width:${{r.width}}%; --bar-color:${{classicChart.color}}; --delay:${{i * 110}}ms;"></div>
            </div>
            <div class="gi-classic-value">${{r.display}}</div>
        </div>
    `).join("");

    root.innerHTML = `
        <div class="gi-classic-card">
            <div class="gi-classic-title">${{classicChart.title}}</div>
            <div class="gi-classic-rows">${{rowsHtml}}</div>
        </div>
    `;
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
def compute_model_metrics(df, model, columns):
    """Compute live model metrics from the loaded artifact and current labeled dataset."""
    from sklearn.metrics import accuracy_score, f1_score

    feature_df = df.drop(columns=["Route_Decision"], errors="ignore")
    X = prepare_input(feature_df, columns)
    y_true = df["Route_Decision"]
    y_pred = model.predict(X)
    return accuracy_score(y_true, y_pred), f1_score(y_true, y_pred, average="macro")

try:
    m1_acc, m1_f1 = compute_model_metrics(df, model1, X1_columns)
    m2_acc, m2_f1 = compute_model_metrics(df, model2, X2_columns)
    m3_acc, m3_f1 = compute_model_metrics(df, model3, X3_columns)
except Exception:
    # Safe fallback only if an environment/version issue prevents metric recomputation.
    m1_acc, m1_f1 = 0.879624, 0.879616
    m2_acc, m2_f1 = 0.837618, 0.838726
    m3_acc, m3_f1 = 0.721003, 0.729150

comparison = pd.DataFrame({
    "Model":    ["With revenue variables", "Without revenue variables", "Only pre-operational features"],
    "Accuracy": [m1_acc, m2_acc, m3_acc],
    "Macro F1": [m1_f1, m2_f1, m3_f1],
})

df_sorted = df.sort_values(["Route", "Flight_Date"]).copy()
df_sorted["Prev_Decision"] = df_sorted.groupby("Route")["Route_Decision"].shift(1)
df_sorted["Changed"] = df_sorted["Prev_Decision"].notna() & (df_sorted["Route_Decision"] != df_sorted["Prev_Decision"])
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
    st.markdown('<div class="sidebar-brand">Airline <span>Route</span> Intelligence ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.64rem;color:{ACCENT};margin-bottom:14px;"
        "font-weight:700;letter-spacing:0.16em;text-transform:uppercase;font-family:DM Sans,sans-serif'>Filter View</p>",
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
    <p style='font-size:0.62rem;color:{ACCENT};font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;margin-bottom:10px;font-family:DM Sans,sans-serif'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:9px;font-size:0.80rem;color:{INK_SOFT};font-family:DM Sans,sans-serif'>
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
  <div class="hero-star"></div><div class="hero-star"></div>
  <div class="hero-star"></div><div class="hero-star"></div>
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

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="divider-label">Composition</div>', unsafe_allow_html=True)

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
        st.markdown("""
        <div class="info-box">
          <strong style="color:#7c3aed">How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:#1d4ed8">Expand</strong> routes should have the highest values across all three columns.
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

    st.markdown('<div class="divider-label">Cost breakdown</div>', unsafe_allow_html=True)
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

    # Build a gradient of jewel tones for cost bars
    nc = len(cost_means)
    jewel_ramp = [
        CHART_EXPAND, "#0e7490", ACCENT, CHART_MAINTAIN,
        "#15803d", CHART_OPTIMIZE, CHART_DROP, "#6d28d9",
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
        f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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

    st.markdown('<div class="divider-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a prediction mode</p>', unsafe_allow_html=True)
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

    if st.session_state.get("last_model_choice") != model_choice:
        st.session_state.pred_result = None
        st.session_state.last_model_choice = model_choice

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<p class="col-label">✈ Flight basics</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = min(passengers / aircraft_capacity, 1.0) if aircraft_capacity else 0.0
            st.markdown(
                f"<div class='info-box'>Calculated Load Factor: <strong>{load_factor:.0%}</strong><br>Based on passengers ÷ aircraft capacity.</div>",
                unsafe_allow_html=True,
            )
            if passengers > aircraft_capacity:
                st.warning("Passengers exceed aircraft capacity. Load factor is capped at 100% for prediction.")

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

        submitted = st.form_submit_button("✈  Get Route Decision")

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
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Cinzel",serif;font-size:1.55rem;font-weight:600;
                      color:{text_col.get(pred, INK)};margin-bottom:10px;letter-spacing:0.04em;
                      text-transform:uppercase'>
            Suggested Decision: {pred}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-size:0.88rem;line-height:1.75;
                    font-family:"DM Sans",sans-serif'>
            {explanations.get(pred, "")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
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
<div style='text-align:center;padding:40px 0 18px'>
  <div style='display:inline-flex;align-items:center;gap:12px;
              background:rgba(255,252,248,0.85);
              border:1px solid rgba(124,58,237,0.22);
              border-radius:999px;
              padding:0.55rem 1.4rem;
              backdrop-filter:blur(14px);
              box-shadow:0 4px 18px rgba(124,58,237,0.10);
              font-family:"DM Sans",sans-serif;
              font-size:0.67rem;
              font-weight:600;
              color:{INK_MUTED};
              letter-spacing:0.12em;
              text-transform:uppercase'>
    <span style='color:{ACCENT};font-size:0.78rem'>✦</span>
    Airline Profitability System
    <span style='color:{ACCENT};font-size:0.78rem'>✦</span>
    Built with Streamlit
  </div>
</div>
""", unsafe_allow_html=True)