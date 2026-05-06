import os
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
#   IMPACT JEWEL-TONE PALETTE  (warm parchment light base)
# ─────────────────────────────────────────────────────────────
PARCHMENT     = "#fdf6e8"
PARCHMENT_2   = "#f5ead0"
PARCHMENT_3   = "#ede0c0"
SCROLL_EDGE   = "#d4b896"

JADE_GEM      = "#2d8b5e"
JADE_BRIGHT   = "#3db87a"
JADE_PALE     = "#c5e8d5"

AMBER_GEM     = "#c87d1a"
AMBER_BRIGHT  = "#e8971f"
AMBER_PALE    = "#faecd0"

CERULEAN      = "#1a6b9e"
CERULEAN_B    = "#2288c8"
CERULEAN_PALE = "#c8e4f5"

ROSE          = "#c0424e"
ROSE_BRIGHT   = "#e05060"
ROSE_PALE     = "#f5d0d4"

VIOLET        = "#7b4fa0"

INK           = "#2c1f0e"
INK_2         = "#4a3520"
INK_MUTED     = "#7a6040"
INK_DIM       = "#b09070"

BORDER_WARM   = "rgba(196,160,100,0.40)"
BORDER_JADE   = "rgba(45,139,94,0.35)"
BORDER_AMBER  = "rgba(200,125,26,0.45)"

SHADOW        = "rgba(44,31,14,0.12)"
SHADOW_MED    = "rgba(44,31,14,0.20)"

EXPAND_C      = "#2d8b5e"
MAINTAIN_C    = "#c87d1a"
OPTIMIZE_C    = "#1a6b9e"
DROP_C        = "#c0424e"

DECISION_COLORS = {
    "Expand":   EXPAND_C,
    "Maintain": MAINTAIN_C,
    "Optimize": OPTIMIZE_C,
    "Drop":     DROP_C,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  Impact Light / Jewel-Tone
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;900&family=Crimson+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&display=swap');

:root {{
  --parch:  {PARCHMENT};
  --parch2: {PARCHMENT_2};
  --parch3: {PARCHMENT_3};
  --edge:   {SCROLL_EDGE};
  --jade:   {JADE_GEM};
  --jade-b: {JADE_BRIGHT};
  --amber:  {AMBER_GEM};
  --amber-b:{AMBER_BRIGHT};
  --cerulean:{CERULEAN};
  --rose:   {ROSE};
  --ink:    {INK};
  --ink2:   {INK_2};
  --muted:  {INK_MUTED};
  --dim:    {INK_DIM};
  --bw:     {BORDER_WARM};
  --bj:     {BORDER_JADE};
  --ba:     {BORDER_AMBER};
  --sh:     {SHADOW};
  --shm:    {SHADOW_MED};
}}

/* ── Keyframes ── */
@keyframes floatIn    {{ from{{ opacity:0; transform:translateY(18px); }} to{{ opacity:1; transform:translateY(0); }} }}
@keyframes fadeUp     {{ from{{ opacity:0; transform:translateY(10px); }} to{{ opacity:1; transform:translateY(0); }} }}
@keyframes gemPulse   {{ 0%,100%{{ box-shadow:0 0 0 0 rgba(45,139,94,0); }} 60%{{ box-shadow:0 0 16px 3px rgba(45,139,94,0.13); }} }}
@keyframes amberGlow  {{ 0%,100%{{ box-shadow:0 0 0 2px rgba(200,125,26,0); }} 60%{{ box-shadow:0 0 0 2px rgba(200,125,26,0.22), 0 0 20px rgba(200,125,26,0.10); }} }}
@keyframes borderFlow {{ 0%{{ background-position:0% 50%; }} 100%{{ background-position:200% 50%; }} }}
@keyframes popIn      {{ from{{ transform:scale(.82); opacity:0; }} to{{ transform:scale(1); opacity:1; }} }}
@keyframes planeTrail {{ 0%{{ left:-160px; opacity:0; }} 6%{{ opacity:1; }} 94%{{ opacity:1; }} 100%{{ left:calc(100% + 160px); opacity:0; }} }}
@keyframes runeFloat  {{ 0%,100%{{ opacity:0.06; transform:translateY(0) rotate(0deg); }} 50%{{ opacity:0.11; transform:translateY(-8px) rotate(3deg); }} }}
@keyframes inkFadeIn  {{ from{{ opacity:0; transform:translateY(8px); }} to{{ opacity:1; transform:translateY(0); }} }}
@keyframes growV      {{ from{{ height:0; opacity:.3; }} to{{ height:var(--bh); opacity:1; }} }}
@keyframes growH      {{ from{{ width:0; opacity:.3; }}  to{{ width:var(--bw,0); opacity:1; }} }}
@keyframes kiSweep    {{ 0%{{left:-80%}} 50%{{left:180%}} 100%{{left:180%}} }}
@keyframes kiShimmer  {{ 0%{{transform:translateX(-150%)}} 48%{{transform:translateX(155%)}} 100%{{transform:translateX(155%)}} }}
@keyframes kiPopIn    {{ from{{transform:scale(.85);opacity:.3}} to{{transform:scale(1);opacity:1}} }}
@keyframes kiFloat    {{ 0%,100%{{transform:rotate(-1deg) scale(1)}} 50%{{transform:rotate(1deg) scale(1.02)}} }}

/* ── Base ── */
html, body, [class*="css"] {{
  font-family: 'Crimson Pro', Georgia, serif !important;
  color: {INK_2} !important;
  background: {PARCHMENT} !important;
  -webkit-font-smoothing: antialiased;
}}

/* ── Parchment background with illustrated warmth ── */
.stApp {{
  min-height: 100vh;
  background:
    radial-gradient(ellipse at 18% 12%, rgba(200,125,26,0.09) 0, transparent 35%),
    radial-gradient(ellipse at 82% 8%,  rgba(45,139,94,0.07) 0, transparent 30%),
    radial-gradient(ellipse at 50% 92%, rgba(26,107,158,0.06) 0, transparent 38%),
    radial-gradient(ellipse at 8%  75%, rgba(192,66,78,0.05) 0, transparent 28%),
    radial-gradient(ellipse at 90% 70%, rgba(200,125,26,0.06) 0, transparent 30%),
    linear-gradient(160deg, {PARCHMENT} 0%, #fbf0d8 35%, #f8ead0 65%, {PARCHMENT} 100%) !important;
  background-attachment: fixed;
}}

/* Parchment texture lines */
.stApp::before {{
  content:"";
  position:fixed; inset:0;
  background-image:
    repeating-linear-gradient(0deg,  rgba(180,140,80,0.022) 0px, rgba(180,140,80,0.022) 1px, transparent 1px, transparent 46px),
    repeating-linear-gradient(90deg, rgba(180,140,80,0.012) 0px, rgba(180,140,80,0.012) 1px, transparent 1px, transparent 46px);
  pointer-events:none; z-index:0;
}}

/* Decorative corner rune */
.stApp::after {{
  content:"❧";
  position:fixed; bottom:60px; right:48px;
  font-size:3rem; color:{AMBER_GEM}; opacity:0.07;
  animation: runeFloat 9s ease-in-out infinite;
  pointer-events:none; z-index:0;
  font-family: Georgia, serif;
}}

.main .block-container {{
  max-width: 1360px;
  padding-top: 1.5rem;
  padding-bottom: 5rem;
  animation: floatIn 500ms ease-out;
  position: relative; z-index: 1;
}}
section.main > div {{ background: transparent; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #f7e9cc 0%, #f0ddb0 100%) !important;
  border-right: 1.5px solid {SCROLL_EDGE} !important;
  box-shadow: 3px 0 24px {SHADOW} !important;
}}
[data-testid="stSidebar"] * {{ color: {INK_MUTED} !important; }}

.sidebar-brand {{
  font-family: 'Cinzel', serif;
  font-size: 0.72rem; font-weight: 700;
  color: {INK}; letter-spacing: 0.14em;
  padding: 0.4rem 0 1.2rem 0;
  border-bottom: 1px solid {BORDER_AMBER};
  margin-bottom: 1.2rem;
  line-height: 1.8;
}}
.sidebar-brand .brand-accent {{
  color: {AMBER_GEM};
  display: block; font-size: 0.54rem;
  letter-spacing: 0.22em; margin-top: 0.15rem; font-weight: 500;
}}

/* ── Headings ── */
h1,h2,h3,h4 {{
  font-family: 'Cinzel', serif !important;
  color: {INK} !important;
  letter-spacing: 0.06em !important;
  font-weight: 700 !important;
}}

/* ── HERO ── */
.hero {{
  position: relative; overflow: hidden;
  border-radius: 14px;
  padding: 2.4rem 2.8rem; margin-bottom: 2rem;
  background: linear-gradient(135deg,
    rgba(253,246,232,0.97) 0%, rgba(245,234,208,0.98) 60%, rgba(237,224,192,0.96) 100%);
  border: 1.5px solid {SCROLL_EDGE};
  box-shadow:
    0 2px 0 rgba(255,255,255,0.85) inset,
    0 -1px 0 rgba(180,140,80,0.25) inset,
    0 16px 48px {SHADOW};
  animation: amberGlow 6s ease-in-out infinite;
}}
/* Inner double-border ornament */
.hero::before {{
  content:""; position:absolute; inset:6px;
  border-radius:10px;
  border:1px solid rgba(196,160,100,0.26);
  pointer-events:none; z-index:0;
}}
/* Animated gem-tone top border */
.hero::after {{
  content:"";
  position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg,
    transparent 0%, {JADE_GEM} 12%, {AMBER_BRIGHT} 30%, {CERULEAN} 52%, {ROSE} 72%, {VIOLET} 88%, transparent 100%);
  background-size:200% 100%;
  animation:borderFlow 4s linear infinite;
  border-radius:14px 14px 0 0;
}}

/* Pixel airplane track */
.hero-plane-track {{
  position:absolute; top:50%; left:0; right:0;
  transform:translateY(-50%); height:56px;
  pointer-events:none; overflow:hidden; z-index:2;
}}
.hero-plane {{
  position:absolute; top:50%; transform:translateY(-50%);
  animation:planeTrail 9s cubic-bezier(.45,0,.55,1) infinite 1.2s;
  display:flex; align-items:center;
  image-rendering:pixelated;
}}

.hero-content {{
  position:relative; z-index:3;
  display:flex; align-items:center; justify-content:space-between; gap:2rem;
}}
.hero-left {{ flex:1; min-width:0; }}
.hero-eyebrow {{
  font-family:'Cinzel',serif;
  font-size:0.60rem; letter-spacing:0.38em;
  color:{AMBER_GEM}; font-weight:600; margin-bottom:0.6rem;
  text-transform:uppercase;
}}
.hero h1 {{
  margin:0 0 0.5rem 0 !important;
  font-size:2.1rem !important; line-height:1.18 !important;
  background:linear-gradient(135deg, {INK} 0%, {JADE_GEM} 55%, {AMBER_GEM} 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text;
  text-shadow:none !important; letter-spacing:0.06em !important;
}}
.hero p {{
  margin:0; color:{INK_MUTED} !important;
  font-size:0.95rem !important; font-family:'Crimson Pro',serif !important;
  text-transform:none !important; letter-spacing:0.01em !important;
  font-weight:400 !important; font-style:italic;
}}
.hero-badge {{
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:0.55rem 1.1rem; border-radius:6px;
  border:1.5px solid {BORDER_JADE};
  background:linear-gradient(135deg,rgba(45,139,94,0.12),rgba(197,232,213,0.22));
  color:{JADE_GEM}; font-size:0.64rem; font-weight:700;
  letter-spacing:0.12em; text-transform:uppercase;
  font-family:'Cinzel',serif;
  box-shadow:0 4px 16px rgba(45,139,94,0.15), inset 0 1px 0 rgba(255,255,255,0.65);
  animation:popIn 600ms ease-out 300ms both; white-space:nowrap;
}}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
  background:linear-gradient(135deg, #fffdf5 0%, {PARCHMENT_3} 100%) !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:12px !important;
  box-shadow:0 1px 0 rgba(255,255,255,0.90) inset, 0 6px 24px {SHADOW} !important;
  padding:1.2rem 1.3rem !important;
  transition:transform 200ms ease, box-shadow 200ms ease !important;
  position:relative; overflow:hidden;
  animation:gemPulse 7s ease-in-out infinite;
}}
[data-testid="metric-container"]:hover {{
  transform:translateY(-3px) !important;
  box-shadow:0 12px 36px {SHADOW_MED}, 0 0 16px rgba(200,125,26,0.12) !important;
  border-color:{AMBER_GEM} !important;
}}
[data-testid="metric-container"]::before {{
  content:""; position:absolute; top:0; left:0; right:0; height:2.5px;
  background:linear-gradient(90deg, {JADE_GEM}, {AMBER_BRIGHT}, {CERULEAN});
  opacity:0.65;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
  font-size:0.58rem !important; font-weight:600 !important;
  text-transform:uppercase !important; letter-spacing:0.18em !important;
  color:{INK_MUTED} !important; font-family:'Cinzel',serif !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {{
  color:{INK} !important; font-size:1.85rem !important; font-weight:700 !important;
  font-family:'Cinzel',serif !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap:0.10rem;
  background:rgba(245,234,208,0.90);
  border:1.5px solid {SCROLL_EDGE};
  border-radius:10px; padding:0.3rem;
  box-shadow:0 4px 16px {SHADOW};
}}
.stTabs [data-baseweb="tab"] {{
  height:40px; padding:0 1.2rem !important;
  border-radius:7px !important;
  color:{INK_MUTED} !important;
  font-size:0.68rem !important; font-weight:600 !important;
  font-family:'Cinzel',serif !important;
  background:transparent !important; letter-spacing:0.06em !important;
  text-transform:uppercase !important;
  transition:background 200ms, color 200ms !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
  background:rgba(200,125,26,0.10) !important; color:{AMBER_GEM} !important;
}}
.stTabs [aria-selected="true"] {{
  background:linear-gradient(135deg,rgba(200,125,26,0.14),rgba(253,246,232,0.92)) !important;
  color:{INK} !important;
  box-shadow:0 0 0 1.5px rgba(200,125,26,0.45), 0 4px 12px {SHADOW} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:1.8rem; }}

/* ── Section headings ── */
.section-hd {{
  font-family:'Cinzel',serif; font-size:0.95rem; font-weight:700;
  color:{INK}; margin:0 0 0.3rem 0;
  letter-spacing:0.10em; text-transform:uppercase;
}}
.section-sub {{
  font-size:0.95rem; color:{INK_MUTED}; margin:0 0 1.2rem 0; line-height:1.75;
  font-family:'Crimson Pro',serif; font-weight:400; font-style:italic;
}}

/* ── Divider label ── */
.divider-label {{
  display:flex; align-items:center; gap:0.8rem; margin:2rem 0 1.2rem 0;
  font-size:0.58rem; font-weight:700; text-transform:uppercase; letter-spacing:0.24em;
  color:{AMBER_GEM}; font-family:'Cinzel',serif;
}}
.divider-label::before, .divider-label::after {{
  content:""; flex:1; height:1px;
  background:linear-gradient(90deg,transparent,{BORDER_AMBER},transparent);
}}

/* ── Info box ── */
.info-box {{
  background:linear-gradient(135deg,rgba(253,246,232,0.95),rgba(245,234,208,0.85));
  border:1.5px solid {SCROLL_EDGE};
  border-left:3px solid {JADE_GEM};
  border-radius:10px; padding:1.1rem 1.2rem;
  color:{INK_MUTED}; line-height:1.85;
  box-shadow:0 4px 16px {SHADOW};
  font-size:0.95rem; font-family:'Crimson Pro',serif;
}}

/* ── Pills ── */
.pill {{
  display:inline-block; padding:0.22rem 0.72rem; border-radius:20px;
  font-size:0.58rem; font-weight:700; letter-spacing:0.10em; text-transform:uppercase;
  font-family:'Cinzel',serif; border:1px solid transparent;
}}
.pill-expand   {{ background:rgba(45,139,94,0.12);  color:{JADE_GEM};   border-color:rgba(45,139,94,0.38); }}
.pill-maintain {{ background:rgba(200,125,26,0.12); color:{AMBER_GEM};  border-color:rgba(200,125,26,0.42); }}
.pill-optimize {{ background:rgba(26,107,158,0.10); color:{CERULEAN};   border-color:rgba(26,107,158,0.38); }}
.pill-drop     {{ background:rgba(192,66,78,0.10);  color:{ROSE};       border-color:rgba(192,66,78,0.38); }}

/* ── Result card ── */
.result-card {{
  border-radius:14px; padding:1.8rem 2rem; margin:1.4rem 0;
  border:1.5px solid {SCROLL_EDGE};
  box-shadow:0 12px 40px {SHADOW_MED};
  animation:inkFadeIn 400ms ease-out;
  position:relative; overflow:hidden;
}}
.result-card::before {{
  content:""; position:absolute; top:0; left:0; right:0; height:3px;
  background:var(--card-glow);
}}
.result-expand   {{ background:linear-gradient(135deg,rgba(45,139,94,0.07),rgba(253,246,232,0.98)); border-color:rgba(45,139,94,0.30);  --card-glow:linear-gradient(90deg,{JADE_GEM},{JADE_BRIGHT}); }}
.result-maintain {{ background:linear-gradient(135deg,rgba(200,125,26,0.07),rgba(253,246,232,0.98)); border-color:rgba(200,125,26,0.35); --card-glow:linear-gradient(90deg,{AMBER_GEM},{AMBER_BRIGHT}); }}
.result-optimize {{ background:linear-gradient(135deg,rgba(26,107,158,0.07),rgba(253,246,232,0.98)); border-color:rgba(26,107,158,0.30); --card-glow:linear-gradient(90deg,{CERULEAN},{CERULEAN_B}); }}
.result-drop     {{ background:linear-gradient(135deg,rgba(192,66,78,0.07),rgba(253,246,232,0.98));  border-color:rgba(192,66,78,0.30);  --card-glow:linear-gradient(90deg,{ROSE},{ROSE_BRIGHT}); }}

/* ── Form inputs ── */
.stSelectbox label, .stNumberInput label, .stSlider label,
.stRadio label, .stCheckbox label, .stTextInput label {{
  color:{INK_MUTED} !important; font-weight:600 !important; font-size:0.60rem !important;
  letter-spacing:0.16em !important; text-transform:uppercase !important;
  font-family:'Cinzel',serif !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input {{
  background:#fffdf5 !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:8px !important; color:{INK_2} !important;
  min-height:44px !important;
  box-shadow:0 2px 8px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.80) !important;
  transition:border-color 200ms !important;
  font-family:'Crimson Pro',serif !important; font-size:0.97rem !important;
}}
.stSelectbox [data-baseweb="select"] > div:hover {{ border-color:{AMBER_GEM} !important; }}
.stSelectbox [data-baseweb="select"] > div:focus-within {{ border-color:{JADE_GEM} !important; box-shadow:0 0 0 3px rgba(45,139,94,0.14) !important; }}
[data-baseweb="menu"] {{
  background:#fffdf5 !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:8px !important; box-shadow:0 12px 36px {SHADOW_MED} !important;
}}
[data-baseweb="menu"] li {{ color:{INK_MUTED} !important; }}
[data-baseweb="menu"] li:hover {{ background:rgba(200,125,26,0.08) !important; color:{AMBER_GEM} !important; }}

/* ── Form card ── */
[data-testid="stForm"] {{
  background:linear-gradient(135deg,#fffdf5,{PARCHMENT_3}) !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:14px !important; padding:1.8rem 2rem 2rem !important;
  box-shadow:0 12px 40px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.80) !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button, .stButton > button {{
  border-radius:8px !important; font-weight:700 !important;
  font-family:'Cinzel',serif !important; letter-spacing:0.10em !important;
  text-transform:uppercase !important; font-size:0.76rem !important;
  transition:transform 200ms, box-shadow 200ms, background 200ms !important;
  border:1.5px solid transparent !important;
}}
[data-testid="stFormSubmitButton"] > button {{
  width:100% !important; padding:0.9rem 0 !important;
  background:linear-gradient(135deg, {JADE_GEM}, #1e7a50) !important;
  border-color:{JADE_BRIGHT} !important;
  box-shadow:0 6px 20px rgba(45,139,94,0.28) !important;
  color:#fdf6e8 !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
  transform:translateY(-2px) !important;
  box-shadow:0 10px 28px rgba(45,139,94,0.40) !important;
  background:linear-gradient(135deg,{JADE_BRIGHT},{JADE_GEM}) !important;
}}
.stButton > button {{
  background:{PARCHMENT_2} !important; color:{INK_MUTED} !important;
  border-color:{SCROLL_EDGE} !important; box-shadow:0 3px 10px {SHADOW} !important;
}}
.stButton > button:hover {{
  color:{AMBER_GEM} !important; transform:translateY(-1px) !important;
  border-color:{AMBER_GEM} !important;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
  background:#fffdf5 !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:10px !important; overflow:hidden !important;
  box-shadow:0 4px 18px {SHADOW} !important;
}}
[data-testid="stDataFrame"] [role="columnheader"] {{
  background:{AMBER_PALE} !important; color:{AMBER_GEM} !important;
  font-weight:700 !important; font-size:0.68rem !important;
  letter-spacing:0.14em !important; text-transform:uppercase !important;
  border-bottom:1.5px solid {SCROLL_EDGE} !important;
  font-family:'Cinzel',serif !important;
}}
[data-testid="stDataFrame"] [role="gridcell"] {{
  color:{INK_2} !important; border-bottom:1px solid rgba(196,160,100,0.18) !important;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
  background:#fffdf5 !important;
  border:1.5px solid {SCROLL_EDGE} !important;
  border-radius:10px !important; box-shadow:0 3px 12px {SHADOW} !important;
}}
[data-testid="stExpander"] summary {{ color:{INK_MUTED} !important; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{
  border-radius:10px !important; background:{AMBER_PALE} !important;
  border:1.5px solid {SCROLL_EDGE} !important; color:{INK_MUTED} !important;
}}

hr {{ border:none !important; height:1px !important;
     background:linear-gradient(90deg,transparent,{BORDER_AMBER},transparent) !important;
     margin:1.5rem 0 !important; }}

.col-label {{
  font-size:0.58rem; font-weight:700; color:{AMBER_GEM}; letter-spacing:0.18em;
  text-transform:uppercase; margin-bottom:1rem;
  display:flex; align-items:center; gap:0.6rem; font-family:'Cinzel',serif;
}}
.col-label::after {{
  content:""; flex:1; height:1px;
  background:linear-gradient(90deg,rgba(200,125,26,0.40),transparent);
}}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
  background:{AMBER_GEM} !important; border-color:{AMBER_BRIGHT} !important;
  box-shadow:0 0 10px rgba(200,125,26,0.40) !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {{
  background:linear-gradient(90deg,{JADE_GEM},{AMBER_GEM}) !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:{PARCHMENT_2}; }}
::-webkit-scrollbar-thumb {{ background:rgba(196,160,100,0.45); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:{AMBER_GEM}; }}
::selection {{ background:rgba(200,125,26,0.22); color:{INK}; }}

p, span, div, label {{ color:{INK_2}; }}
.stMarkdown p {{ color:{INK_MUTED} !important; }}
</style>

<!-- ✦  pixel cursor ripple on click ✦ -->
<script>
(function(){{
  var PIXELS=[
    {{dx:-5,dy:-5,c:"#2d8b5e",s:5}},{{dx:5,dy:-5,c:"#c87d1a",s:5}},
    {{dx:-5,dy:5,c:"#c87d1a",s:5}},{{dx:5,dy:5,c:"#2d8b5e",s:5}},
    {{dx:0,dy:-9,c:"#ffffff",s:3}},{{dx:0,dy:9,c:"#ffffff",s:3}},
    {{dx:-9,dy:0,c:"#3db87a",s:3}},{{dx:9,dy:0,c:"#e8971f",s:3}},
    {{dx:-3,dy:-3,c:"#fdf6e8",s:4}},{{dx:3,dy:3,c:"#fdf6e8",s:4}},
    {{dx:7,dy:-4,c:"#1a6b9e",s:3}},{{dx:-7,dy:4,c:"#c0424e",s:3}},
  ];
  document.addEventListener('click',function(e){{
    PIXELS.forEach(function(p,i){{
      var el=document.createElement('div');
      el.style.cssText=[
        'position:fixed','pointer-events:none','z-index:99999',
        'width:'+p.s+'px','height:'+p.s+'px',
        'left:'+(e.clientX+p.dx-p.s/2)+'px',
        'top:'+(e.clientY+p.dy-p.s/2)+'px',
        'background:'+p.c,
        'image-rendering:pixelated',
        'box-shadow:0 0 '+p.s+'px '+p.c+'99',
        'opacity:0.90','border-radius:1px',
        'transform:scale(1)',
        'transition:transform 500ms ease-out,opacity 500ms ease-out',
      ].join(';');
      document.body.appendChild(el);
      requestAnimationFrame(function(){{
        requestAnimationFrame(function(){{
          var a=(i/PIXELS.length)*2*Math.PI;
          var d=14+Math.random()*14;
          el.style.transform='translate('+(Math.cos(a)*d)+'px,'+(Math.sin(a)*d)+'px) scale(0.08)';
          el.style.opacity='0';
        }});
      }});
      setTimeout(function(){{if(el.parentNode)el.parentNode.removeChild(el);}},540);
    }});
  }});
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
#  CHART HELPERS
# ─────────────────────────────────────────────────────────────
def col_seq(labels):
    return [DECISION_COLORS.get(l, JADE_GEM) for l in labels]

def _fmt_chart_value(v, value_format="number"):
    if value_format == "percent": return f"{v:.0%}"
    if value_format == "money":   return f"${v:,.0f}"
    return f"{v:,.0f}"


# ─────────────────────────────────────────────────────────────
#  ANIMATED HTML CHART HELPERS —  Light / Jewel-Tone
# ─────────────────────────────────────────────────────────────
_CHART_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Crimson+Pro:wght@400;500;600&display=swap');

.ki-card {{
    width:100%; box-sizing:border-box;
    padding:24px 28px 22px; border-radius:14px;
    background:linear-gradient(135deg, #fffdf5 0%, {PARCHMENT_3} 100%);
    border:1.5px solid {SCROLL_EDGE};
    box-shadow:0 6px 24px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.90);
    font-family:'Crimson Pro',Georgia,serif;
    color:{INK_2}; overflow:hidden; position:relative;
}}
.ki-card::before {{
    content:""; position:absolute; top:0; left:0; right:0; height:2.5px;
    background:linear-gradient(90deg,transparent,{JADE_GEM} 30%,{AMBER_BRIGHT} 70%,transparent);
    opacity:0.60;
}}
.ki-card::after {{
    content:""; position:absolute; top:0; left:-80%; bottom:0; width:40%;
    background:linear-gradient(90deg,transparent,rgba(200,125,26,0.05),transparent);
    animation:kiSweep 7s ease-in-out infinite; pointer-events:none;
}}
.ki-title {{
    font-family:'Cinzel',serif;
    text-align:center; font-size:0.90rem; line-height:1.4;
    color:{INK}; margin-bottom:20px; font-weight:700;
    letter-spacing:0.12em; text-transform:uppercase;
}}
.ki-legend {{ display:flex; justify-content:center; gap:20px; margin-bottom:20px; flex-wrap:wrap; }}
.ki-legend-item {{ display:flex; align-items:center; gap:8px; color:{INK_MUTED}; font-weight:600; font-size:0.88rem; }}
.ki-legend-swatch {{ width:14px; height:6px; border-radius:10px; }}

@keyframes kiSweep   {{ 0%{{left:-80%}} 50%{{left:180%}} 100%{{left:180%}} }}
@keyframes kiGrowV   {{ from{{height:0;opacity:.3}} to{{height:var(--bh);opacity:1}} }}
@keyframes kiGrowH   {{ from{{width:0;opacity:.3}}  to{{width:var(--bw,0);opacity:1}} }}
@keyframes kiShimmer {{ 0%{{transform:translateX(-150%)}} 48%{{transform:translateX(155%)}} 100%{{transform:translateX(155%)}} }}
@keyframes kiPopIn   {{ from{{transform:scale(.85);opacity:.3}} to{{transform:scale(1);opacity:1}} }}
@keyframes kiFloat   {{ 0%,100%{{transform:rotate(-1deg) scale(1)}} 50%{{transform:rotate(1deg) scale(1.02)}} }}
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
            "color": s.get("color", JADE_GEM),
            "colors": s.get("colors", None),
        })
    if not all_values: st.info("No chart data available."); return
    if max_value is None: max_value = max(all_values) if max(all_values) != 0 else 1
    max_value = float(max_value)
    chart = {"title": title, "labels": labels, "series": clean_series,
             "max_value": max_value, "value_format": value_format}
    cj = json.dumps(chart)
    plot_h = max(height - 200, 180)

    components.html(f"""
    <div id="ki-vbar-root"></div>
    <style>
    {_CHART_CSS}
    .ki-vplot {{
        display:grid;
        grid-template-columns:repeat({max(len(labels),1)},minmax(0,1fr));
        gap:16px; align-items:end; height:{plot_h}px;
        border-bottom:1px solid {SCROLL_EDGE};
        background-image:repeating-linear-gradient(to top,rgba(196,160,100,0.10) 0px,rgba(196,160,100,0.10) 1px,transparent 1px,transparent 25%);
        padding:0 8px; position:relative; z-index:1;
    }}
    .ki-vgroup {{ height:100%; display:flex; align-items:end; justify-content:center; gap:6px; }}
    .ki-vbar-wrap {{ height:100%; width:min(48px,30%); min-width:20px; display:flex; align-items:end; justify-content:center; position:relative; }}
    .ki-vbar {{
        width:100%; height:var(--bh); min-height:3px;
        border-radius:6px 6px 2px 2px; position:relative; overflow:hidden;
        box-shadow:0 4px 12px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.35);
        animation:kiGrowV 700ms cubic-bezier(.22,.9,.25,1) both;
    }}
    .ki-vbar::before {{
        content:""; position:absolute; inset:0; width:60%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),rgba(255,255,255,0.55),rgba(255,255,255,0.12),transparent);
        transform:translateX(-150%);
        animation:kiShimmer 2.8s ease-in-out infinite; animation-delay:var(--delay);
    }}
    .ki-vvalue {{
        position:absolute; bottom:calc(var(--bh) + 8px);
        font-size:11px; font-weight:700; color:{INK_MUTED}; white-space:nowrap;
        font-family:'Crimson Pro',serif;
    }}
    .ki-xlabels {{
        display:grid; grid-template-columns:repeat({max(len(labels),1)},minmax(0,1fr));
        gap:16px; padding:12px 8px 0; text-align:center; position:relative; z-index:1;
    }}
    .ki-xlabel {{ color:{INK_MUTED}; font-weight:600; font-size:12px; line-height:1.3; font-family:'Crimson Pro',serif; }}
    </style>
    <script>
    const chart={cj};
    function fmtV(v){{
      if(chart.value_format==="percent") return Math.round(v*100)+"%";
      if(chart.value_format==="money") return "$"+Math.round(v).toLocaleString();
      return Math.round(v).toLocaleString();
    }}
    const root=document.getElementById("ki-vbar-root");
    const legendHtml=chart.series.map(s=>`
        <div class="ki-legend-item">
          <span class="ki-legend-swatch" style="background:${{s.color}}"></span>
          ${{s.name}}
        </div>`).join("");
    const groupsHtml=chart.labels.map((label,i)=>`
        <div class="ki-vgroup">
          ${{chart.series.map((s,j)=>{{
              const val=Number(s.values[i]||0);
              const pct=Math.max(2,Math.min(100,val/chart.max_value*100));
              const color=s.colors?s.colors[i]:s.color;
              return `<div class="ki-vbar-wrap">
                <div class="ki-vvalue" style="--bh:${{pct}}%">${{fmtV(val)}}</div>
                <div class="ki-vbar" style="--bh:${{pct}}%;--delay:${{(i+j)*80}}ms;background:linear-gradient(180deg,${{color}}ee,${{color}}99);"></div>
              </div>`;
          }}).join("")}}
        </div>`).join("");
    const xlabels=chart.labels.map(l=>`<div class="ki-xlabel">${{l}}</div>`).join("");
    root.innerHTML=`<div class="ki-card">
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
    if not values: st.info("No chart data available."); return
    if colors is None: colors = [JADE_GEM] * len(values)
    elif isinstance(colors, str): colors = [colors] * len(values)
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
    {_CHART_CSS}
    .ki-hrows {{ display:flex; flex-direction:column; gap:12px; position:relative; z-index:1; }}
    .ki-hrow  {{ display:grid; grid-template-columns:minmax(90px,150px) 1fr minmax(70px,96px); align-items:center; gap:12px; }}
    .ki-hlabel {{ color:{INK_MUTED}; font-size:13px; font-weight:600; text-align:right; font-family:'Crimson Pro',serif; }}
    .ki-htrack {{ height:24px; border-radius:6px; background:rgba(196,160,100,0.14); border:1px solid {SCROLL_EDGE}; overflow:hidden; position:relative; }}
    .ki-hbar {{
        height:100%; width:var(--bw); border-radius:6px; position:relative; overflow:hidden;
        box-shadow:0 0 10px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.30);
        animation:kiGrowH 700ms cubic-bezier(.22,.9,.25,1) both;
    }}
    .ki-hbar::before {{
        content:""; position:absolute; inset:0; width:60%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.10),rgba(255,255,255,0.55),rgba(255,255,255,0.10),transparent);
        transform:translateX(-150%); animation:kiShimmer 2.8s ease-in-out infinite; animation-delay:var(--delay);
    }}
    .ki-hvalue {{ color:{INK}; font-weight:700; font-size:13px; white-space:nowrap; font-family:'Crimson Pro',serif; }}
    </style>
    <script>
    const chart={cj};
    const root=document.getElementById("ki-hbar-root");
    const rows=chart.rows.map((r,i)=>`
        <div class="ki-hrow">
          <div class="ki-hlabel">${{r.label}}</div>
          <div class="ki-htrack"><div class="ki-hbar" style="--bw:${{r.width}}%;--delay:${{i*80}}ms;background:linear-gradient(90deg,${{r.color}}bb,${{r.color}});"></div></div>
          <div class="ki-hvalue">${{r.display}}</div>
        </div>`).join("");
    root.innerHTML=`<div class="ki-card" style="min-height:{height}px">
      <div class="ki-title">${{chart.title}}</div>
      <div class="ki-hrows">${{rows}}</div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_pie_chart(title, labels, values, colors=None, height=430):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    total = sum(values)
    if not values or total <= 0: st.info("No chart data available."); return
    if colors is None: colors = [JADE_GEM] * len(values)
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
    {_CHART_CSS}
    .ki-pie-layout {{ display:grid; grid-template-columns:220px 1fr; gap:28px; align-items:center; position:relative; z-index:1; }}
    .ki-donut-wrap {{ display:flex; align-items:center; justify-content:center; }}
    .ki-donut-outer {{
        width:200px; height:200px; border-radius:50%;
        background:conic-gradient(var(--pg));
        position:relative;
        box-shadow:0 0 32px rgba(200,125,26,0.18), 0 8px 28px {SHADOW_MED};
        animation:kiPopIn 800ms cubic-bezier(.22,.9,.25,1) both, kiFloat 7s ease-in-out 1s infinite;
        flex-shrink:0;
    }}
    .ki-donut-outer::after {{
        content:""; position:absolute; inset:28%; border-radius:50%;
        background:#fffdf5;
        box-shadow:inset 0 2px 10px {SHADOW};
    }}
    .ki-donut-outer::before {{
        content:""; position:absolute; inset:0; border-radius:50%;
        background:linear-gradient(115deg,transparent 30%,rgba(255,255,255,0.18) 48%,transparent 66%);
        transform:translateX(-120%) rotate(12deg);
        animation:kiShimmer 3.5s ease-in-out infinite; z-index:1;
    }}
    .ki-pie-legend {{ display:flex; flex-direction:column; gap:12px; }}
    .ki-pie-row {{ display:grid; grid-template-columns:12px 1fr auto; align-items:center; gap:10px; color:{INK_MUTED}; font-size:13px; font-weight:600; font-family:'Crimson Pro',serif; }}
    .ki-pie-dot {{ width:10px; height:10px; border-radius:3px; flex-shrink:0; }}
    .ki-pie-pct {{ font-weight:700; white-space:nowrap; color:{INK}; font-size:14px; }}
    @media(max-width:500px){{ .ki-pie-layout{{grid-template-columns:1fr;}} .ki-donut-outer{{width:160px;height:160px;}} }}
    </style>
    <script>
    const pc={cj};
    const root=document.getElementById("ki-pie-root");
    const rows=pc.rows.map(r=>`<div class="ki-pie-row">
        <span class="ki-pie-dot" style="background:${{r.color}}"></span>
        <span>${{r.label}}</span>
        <span class="ki-pie-pct">${{r.display}}</span>
    </div>`).join("");
    root.innerHTML=`<div class="ki-card" style="min-height:{height}px;display:flex;flex-direction:column;justify-content:space-between;">
      <div class="ki-title">${{pc.title}}</div>
      <div class="ki-pie-layout">
        <div class="ki-donut-wrap">
          <div class="ki-donut-outer" style="--pg:conic-gradient(${{pc.gradient}})"></div>
        </div>
        <div class="ki-pie-legend">${{rows}}</div>
      </div>
    </div>`;
    </script>
    """, height=height + 35, scrolling=False)


def shimmer_classic_horizontal_bar_chart(title, labels, values, color=JADE_GEM, value_format="money", height=460):
    labels = [str(x) for x in labels]
    values = [float(x) if pd.notna(x) else 0.0 for x in values]
    if not values: st.info("No chart data available."); return
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
    {_CHART_CSS}
    .ki-crows {{ display:flex; flex-direction:column; gap:12px; }}
    .ki-crow  {{ display:grid; grid-template-columns:minmax(82px,140px) 1fr minmax(86px,108px); align-items:center; gap:12px; }}
    .ki-clabel {{ color:{INK_MUTED}; font-size:13px; font-weight:600; text-align:right; font-family:'Crimson Pro',serif; }}
    .ki-caxis  {{ height:24px; position:relative; border-bottom:1px solid {SCROLL_EDGE};
                  background-image:repeating-linear-gradient(to right,rgba(196,160,100,0.15) 1px,transparent 1px);
                  background-size:25% 100%; }}
    .ki-cbar {{
        height:24px; width:var(--bw); border-radius:0 6px 6px 0; position:relative; overflow:hidden;
        background:linear-gradient(90deg,var(--bc)88,var(--bc));
        box-shadow:0 0 12px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.30);
        animation:kiGrowH 700ms cubic-bezier(.22,.9,.25,1) both;
    }}
    .ki-cbar::before {{
        content:""; position:absolute; inset:0; width:60%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08),rgba(255,255,255,0.50),rgba(255,255,255,0.08),transparent);
        transform:translateX(-150%); animation:kiShimmer 2.8s ease-in-out infinite; animation-delay:var(--delay);
    }}
    .ki-cvalue {{ color:{INK}; font-weight:700; font-size:13px; white-space:nowrap; font-family:'Crimson Pro',serif; }}
    </style>
    <script>
    const cc={cj};
    const root=document.getElementById("ki-cbar-root");
    const rows=cc.rows.map((r,i)=>`<div class="ki-crow">
        <div class="ki-clabel">${{r.label}}</div>
        <div class="ki-caxis"><div class="ki-cbar" style="--bw:${{r.width}}%;--bc:${{cc.color}};--delay:${{i*80}}ms;"></div></div>
        <div class="ki-cvalue">${{r.display}}</div>
    </div>`).join("");
    root.innerHTML=`<div class="ki-card" style="min-height:{height}px">
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
    st.markdown(f"""
    <div class="sidebar-brand">
        AIRLINE ROUTE
        <span class="brand-accent">✦ INTEL PLATFORM</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.60rem;color:{AMBER_GEM};margin-bottom:12px;"
        f"font-weight:700;letter-spacing:0.20em;text-transform:uppercase;"
        f"font-family:Cinzel,serif;'>▸ Filter View</p>",
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
    <p style='font-size:0.60rem;color:{JADE_GEM};font-weight:700;letter-spacing:0.20em;
    text-transform:uppercase;margin-bottom:14px;font-family:Cinzel,serif;'>
    ▸ Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:12px;font-size:0.92rem;color:{INK_MUTED};font-family:"Crimson Pro",serif;font-style:italic;'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-expand'>Expand</span>
        <span style='color:{INK_MUTED}'>High profit &amp; demand</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-maintain'>Maintain</span>
        <span style='color:{INK_MUTED}'>Stable performer</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-optimize'>Optimize</span>
        <span style='color:{INK_MUTED}'>Room to improve</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span class='pill pill-drop'>Drop</span>
        <span style='color:{INK_MUTED}'>Losing money</span>
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
#  HERO — Pixel airplane + gem-tone border
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <!-- Pixel airplane track -->
  <div class="hero-plane-track">
    <div class="hero-plane">
      <div style="position:relative;width:80px;height:48px;image-rendering:pixelated;">
        <!-- Pixel trail -->
        <div style="position:absolute;right:78px;top:50%;transform:translateY(-50%);
                    width:110px;height:2px;
                    background:linear-gradient(to left,{AMBER_GEM} 0%,{JADE_GEM} 35%,transparent 100%);
                    opacity:0.55;"></div>
        <div style="position:absolute;right:82px;top:calc(50% - 3px);width:5px;height:5px;background:{AMBER_GEM};opacity:0.80;"></div>
        <div style="position:absolute;right:94px;top:calc(50% + 1px);width:4px;height:4px;background:{JADE_GEM};opacity:0.60;"></div>
        <div style="position:absolute;right:106px;top:calc(50%);width:3px;height:3px;background:{CERULEAN};opacity:0.50;"></div>
        <div style="position:absolute;right:118px;top:calc(50% - 1px);width:3px;height:3px;background:{ROSE};opacity:0.35;"></div>
        <!-- Body -->
        <div style="position:absolute;left:17px;top:6px;width:6px;height:12px;background:{JADE_GEM};"></div>
        <!-- Nose -->
        <div style="position:absolute;left:18px;top:2px;width:4px;height:4px;background:{JADE_BRIGHT};"></div>
        <div style="position:absolute;left:19px;top:0;width:2px;height:2px;background:{AMBER_GEM};"></div>
        <!-- Wings -->
        <div style="position:absolute;left:2px;top:9px;width:36px;height:3px;background:{JADE_GEM};"></div>
        <div style="position:absolute;left:0;top:10px;width:4px;height:2px;background:{CERULEAN};"></div>
        <div style="position:absolute;left:36px;top:10px;width:4px;height:2px;background:{CERULEAN};"></div>
        <!-- Tail -->
        <div style="position:absolute;left:9px;top:16px;width:6px;height:2px;background:{AMBER_BRIGHT};"></div>
        <div style="position:absolute;left:25px;top:16px;width:6px;height:2px;background:{AMBER_BRIGHT};"></div>
        <!-- Cockpit -->
        <div style="position:absolute;left:18px;top:3px;width:4px;height:3px;background:{AMBER_GEM};opacity:0.90;"></div>
        <!-- Engines -->
        <div style="position:absolute;left:10px;top:10px;width:5px;height:2px;background:{ROSE};"></div>
        <div style="position:absolute;left:25px;top:10px;width:5px;height:2px;background:{ROSE};"></div>
      </div>
    </div>
  </div>

  <div class="hero-content">
    <div class="hero-left">
      <div class="hero-eyebrow">✦ Route Intelligence Platform ✦</div>
      <h1>Airline Profitability<br>System</h1>
      <p style="margin-top:0.4rem;">Sample airline dataset · for analysis &amp; demonstration only</p>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.8rem;position:relative;z-index:4;">
      <div class="hero-badge">⚗ ML-Powered Analytics</div>
      <div style="
        display:flex;gap:6px;align-items:center;
        font-family:'Cinzel',serif;
        font-size:0.58rem;font-weight:600;
        letter-spacing:0.16em;color:{INK_DIM};text-transform:uppercase;
      ">
        <span style="width:7px;height:7px;border-radius:50%;background:{JADE_GEM};
                     box-shadow:0 0 6px {JADE_GEM};display:inline-block;"></span>
        Live System
      </div>
    </div>
  </div>
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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="divider-label">✦ Composition ✦</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown(f'<p class="section-hd">Decision Mix</p>', unsafe_allow_html=True)
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {"Expand": EXPAND_C, "Maintain": MAINTAIN_C, "Optimize": OPTIMIZE_C, "Drop": DROP_C}
        wedge_colors = [wc[l] for l in dc.index]
        shimmer_pie_chart(
            title="Share of Flights by Decision",
            labels=dc.index.tolist(),
            values=dc.values.tolist(),
            colors=wedge_colors,
            height=390,
        )

    with right:
        st.markdown(f'<p class="section-hd">Average Metrics by Decision</p>', unsafe_allow_html=True)
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
          <strong style="color:{JADE_GEM}">✦ How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:{EXPAND_C}">Expand</strong> routes have the highest values across all three columns.
        </div>""", unsafe_allow_html=True)


# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown(f'<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        apd = (fdf.groupby("Route_Decision")["Profit"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        shimmer_horizontal_bar_chart(
            title="Average Profit by Decision",
            labels=apd.index.tolist(),
            values=apd.values.tolist(),
            colors=col_seq(apd.index.tolist()),
            value_format="money", height=350,
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
                "color": JADE_GEM,
                "colors": col_seq(ald.index.tolist()),
            }],
            max_value=1.0, value_format="percent", height=350,
        )

    st.markdown('<div class="divider-label">✦ Cost Breakdown ✦</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-hd">Where is the money going?</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">The biggest cost components across all filtered flights.</p>', unsafe_allow_html=True)

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
    nc = len(cost_means)
    color_ramp = [JADE_GEM, CERULEAN, AMBER_GEM, ROSE, JADE_BRIGHT, CERULEAN_B, AMBER_BRIGHT, VIOLET]
    neutral_cols = (color_ramp * 4)[:nc]
    shimmer_horizontal_bar_chart(
        title="Top Cost Drivers",
        labels=cost_means.index.tolist(),
        values=cost_means.values.tolist(),
        colors=neutral_cols, value_format="money", height=430,
    )


# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown(f'<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
        f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
        "Top routes currently classified as Expand</p>", unsafe_allow_html=True)
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route","Profit","Profit_Margin","Load_Factor"]].head(10)
        .rename(columns={"Profit":"Avg Profit ($)","Profit_Margin":"Profit Margin","Load_Factor":"Load Factor"})
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
            f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        shimmer_classic_horizontal_bar_chart(
            title="Top 10 Routes",
            labels=top.index.tolist(), values=top.values.tolist(),
            color=EXPAND_C, value_format="money", height=430,
        )

    with right:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
            f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
            "Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        shimmer_classic_horizontal_bar_chart(
            title="Bottom 10 Routes",
            labels=worst.index.tolist(), values=worst.values.tolist(),
            color=DROP_C, value_format="money", height=430,
        )


# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown(f'<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
            f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
            f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">✦ Distribution ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
        f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
        "How many unique routes appear in each category?</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route":"Unique Routes"})
        .set_index("Route_Decision").reindex(ORDER).dropna()
    )
    bc = [DECISION_COLORS.get(i, JADE_GEM) for i in urbd.index]
    vals4 = urbd["Unique Routes"].values.tolist()
    shimmer_vertical_bar_chart(
        title="Unique Routes per Decision Category",
        labels=urbd.index.tolist(),
        series=[{"name":"Unique Routes","values":vals4,"color":JADE_GEM,"colors":bc}],
        max_value=max(vals4) if vals4 else 1,
        value_format="number", height=390,
    )


# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown(f'<p class="section-hd">Simulate a Route Scenario</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
        f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)

    shimmer_vertical_bar_chart(
        title="Model Accuracy & F1 Comparison",
        labels=comparison["Model"].tolist(),
        series=[
            {"name":"Accuracy","values":comparison["Accuracy"].tolist(),"color":JADE_GEM},
            {"name":"Macro F1","values":comparison["Macro F1"].tolist(), "color":AMBER_GEM},
        ],
        max_value=1.0, value_format="percent", height=430,
    )

    st.markdown('<div class="divider-label">✦ Configuration ✦</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-hd">Choose a Prediction Mode</p>', unsafe_allow_html=True)
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
            st.markdown(f'<p class="col-label">✈ Flight Basics</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown(f'<p class="col-label">🌍 Route Context</p>', unsafe_allow_html=True)
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown(f'<p class="col-label">💰 Revenue</p>', unsafe_allow_html=True)
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown(f'<p class="col-label">💸 Cost Breakdown</p>', unsafe_allow_html=True)
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

        submitted = st.form_submit_button("✦ Get Route Decision")

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
            inp  = prepare_input(pd.DataFrame([row]), X2_columns)
            pred = model2.predict(inp)[0]; prob = model2.predict_proba(inp)[0]; cls = model2.classes_
        else:
            row = {
                "Aircraft_Type": aircraft_type, "Aircraft_Capacity": aircraft_capacity,
                "Passengers": passengers, "Load_Factor": load_factor,
                "Flight_Hours": flight_hours, "Season": season_val,
                "Route_Category": route_category, "Demand_Level": demand_level,
            }
            inp  = prepare_input(pd.DataFrame([row]), X3_columns)
            pred = model3.predict(inp)[0]; prob = model3.predict_proba(inp)[0]; cls = model3.classes_

        st.session_state.pred_result = {"prediction": pred, "probabilities": prob, "classes": cls}

    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]; prob = res["probabilities"]; cls = res["classes"]

        pill_cls   = {"Expand":"pill-expand","Maintain":"pill-maintain","Optimize":"pill-optimize","Drop":"pill-drop"}
        result_cls = {"Expand":"result-expand","Maintain":"result-maintain","Optimize":"result-optimize","Drop":"result-drop"}
        text_col   = {"Expand":EXPAND_C,"Maintain":MAINTAIN_C,"Optimize":OPTIMIZE_C,"Drop":DROP_C}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred,"result-expand")}'>
          <div style='margin-bottom:12px'>
            <span class='pill {pill_cls.get(pred,"")}'>{pred}</span>
          </div>
          <div style='font-family:"Cinzel",serif;font-size:1.30rem;font-weight:700;
                      color:{text_col.get(pred,INK)};margin-bottom:12px;letter-spacing:0.06em;
                      text-transform:uppercase'>
            ✦ Suggested Decision: {pred}
          </div>
          <p style='color:{INK_MUTED};margin:0;font-size:0.97rem;line-height:1.85;
                    font-family:"Crimson Pro",serif;font-style:italic;'>
            {explanations.get(pred,"")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.78rem;font-weight:700;color:{INK};margin-bottom:8px;"
            f"font-family:Cinzel,serif;letter-spacing:0.08em;text-transform:uppercase'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision": cls, "Probability": prob})
                   .sort_values("Probability", ascending=False))
        bar_colors = [DECISION_COLORS.get(d, JADE_GEM) for d in prob_df["Decision"]]
        shimmer_vertical_bar_chart(
            title="Model Confidence per Decision",
            labels=prob_df["Decision"].tolist(),
            series=[{
                "name":"Probability","values":prob_df["Probability"].tolist(),
                "color":JADE_GEM,"colors":bar_colors,
            }],
            max_value=1.0, value_format="percent", height=390,
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
<div style='text-align:center;padding:48px 0 20px'>
  <div style='display:inline-flex;align-items:center;gap:16px;
              background:linear-gradient(135deg,#fffdf5,{PARCHMENT_3});
              border:1.5px solid {SCROLL_EDGE};
              padding:0.65rem 1.8rem; border-radius:8px;
              box-shadow:0 4px 16px {SHADOW}, inset 0 1px 0 rgba(255,255,255,0.80);
              font-family:"Cinzel",serif;
              font-size:0.66rem; font-weight:700;
              color:{INK_DIM}; letter-spacing:0.16em; text-transform:uppercase'>
    <span style='color:{JADE_GEM};font-size:0.85rem'>✦</span>
    Airline Profitability System
    <span style='color:{AMBER_GEM};font-size:0.85rem'>✦</span>
    Built with Streamlit
    <span style='color:{CERULEAN};font-size:0.85rem'>✦</span>
  </div>
</div>
""", unsafe_allow_html=True)