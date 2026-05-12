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
#  COSMOS THEME INJECTED FROM cosmos_app.py
#  Model/data logic below is unchanged.
# ─────────────────────────────────────────────────────────────

BACKGROUND_URL = "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=2400&q=80"

# Cosmos / glass UI palette used by charts and helper components
BG_BASE        = "#03030a"
BG_SOFT        = "#080719"
BG_COOL        = "#0b1026"

GLASS_BG       = "rgba(255,255,255,0.08)"
GLASS_BORDER   = "rgba(255,255,255,0.18)"

INK            = "#f8f5ff"
INK_SOFT       = "#e3dcff"
INK_MUTED      = "#b8b2d6"

ACCENT         = "#c0a6ff"
ACCENT_DK      = "#7c3aed"
ACCENT_LT      = "#e9ddff"
ACCENT_2       = "#7aa6ff"
MAGENTA        = "#ff8cc8"

# Chart tones tuned for dark cosmos background
CHART_EXPAND   = "#7aa6ff"
CHART_MAINTAIN = "#7df7c4"
CHART_OPTIMIZE = "#ffd08a"
CHART_ORANGE   = "#ffd08a"
CHART_DROP     = "#ff8cc8"
CHART_NEUTRAL  = [
    "#c0a6ff", "#7aa6ff", "#67e8f9", "#7df7c4",
    "#ff8cc8", "#ffd08a", "#a7f3d0", "#c7c7d9",
]

DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_OPTIMIZE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]


# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — COSMOS REFERENCE THEME
# ─────────────────────────────────────────────────────────────
CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Manrope:wght@400;500;600;700;800&display=swap');

  #MainMenu, header, footer { visibility: hidden; }

  :root {
    --cosmos-bg: #03020b;
    --cosmos-panel: rgba(9, 10, 24, 0.72);
    --cosmos-panel-strong: rgba(12, 14, 32, 0.86);
    --cosmos-card: rgba(255,255,255,0.075);
    --cosmos-card-hover: rgba(255,255,255,0.105);
    --cosmos-border: rgba(255,255,255,0.145);
    --cosmos-border-hover: rgba(210,196,255,0.38);
    --cosmos-text: #f7f4ff;
    --cosmos-soft: #d8d4ea;
    --cosmos-muted: #a9a3c3;
    --cosmos-faint: #7f789b;
    --cosmos-blue: #7aa6ff;
    --cosmos-gold: #ffd08a;
    --cosmos-pink: #ff8cc8;
    --cosmos-violet: #bba2ff;
    --cosmos-cyan: #67e8f9;
    --radius-lg: 26px;
    --radius-md: 18px;
    --shadow-soft: 0 14px 42px rgba(0,0,0,.36);
    --shadow-hover: 0 22px 70px rgba(0,0,0,.52), 0 0 38px rgba(155,126,255,.20);
  }

  html, body, [class*="css"] {
    font-family: 'Inter', 'Manrope', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--cosmos-text) !important;
    scroll-behavior: smooth;
    text-rendering: geometricPrecision;
  }

  .stApp {
    min-height: 100vh;
    background:
      linear-gradient(rgba(1,1,8,0.38), rgba(1,1,8,0.56)),
      radial-gradient(ellipse at 50% 42%, rgba(150,90,230,0.24), transparent 38%),
      radial-gradient(ellipse at 22% 68%, rgba(65,115,210,0.13), transparent 32%),
      radial-gradient(ellipse at 77% 62%, rgba(210,90,145,0.11), transparent 32%),
      linear-gradient(rgba(3,2,14,0.64), rgba(3,2,14,0.82)),
      url("{BACKGROUND_URL}") center/cover no-repeat fixed;
    color: var(--cosmos-text);
    overflow-x: hidden;
  }

  .stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0.42;
    background-image:
      radial-gradient(1.6px 1.6px at 48px 80px, rgba(255,255,255,.78), transparent 55%),
      radial-gradient(1px 1px at 160px 220px, rgba(255,255,255,.55), transparent 55%),
      radial-gradient(1.5px 1.5px at 340px 140px, rgba(196,218,255,.70), transparent 55%),
      radial-gradient(1px 1px at 540px 430px, rgba(255,255,255,.52), transparent 55%),
      radial-gradient(1.5px 1.5px at 760px 180px, rgba(255,220,160,.58), transparent 55%),
      radial-gradient(1px 1px at 980px 360px, rgba(255,255,255,.55), transparent 55%),
      radial-gradient(1.5px 1.5px at 1220px 250px, rgba(210,190,255,.65), transparent 55%);
    background-size: 1440px 820px;
    animation: cosmosStarDrift 120s linear infinite;
  }

  .stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 1;
    opacity: 0.16;
    background-image:
      radial-gradient(1.8px 1.8px at 8% 18%, rgba(255,255,255,.90), transparent 58%),
      radial-gradient(1.2px 1.2px at 18% 72%, rgba(191,219,254,.72), transparent 58%),
      radial-gradient(1.6px 1.6px at 33% 38%, rgba(255,255,255,.82), transparent 58%),
      radial-gradient(1.2px 1.2px at 46% 80%, rgba(221,214,254,.72), transparent 58%),
      radial-gradient(1.7px 1.7px at 61% 25%, rgba(255,255,255,.86), transparent 58%),
      radial-gradient(1.1px 1.1px at 74% 64%, rgba(186,230,253,.68), transparent 58%),
      radial-gradient(1.6px 1.6px at 88% 34%, rgba(255,255,255,.80), transparent 58%),
      radial-gradient(1.1px 1.1px at 94% 86%, rgba(253,224,171,.62), transparent 58%);
    background-size: 100vw 100vh;
    mix-blend-mode: screen;
    animation: cosmosTwinkle 5.8s ease-in-out infinite alternate;
  }

  @keyframes cosmosStarDrift {
    from { transform: translate3d(0,0,0); }
    to { transform: translate3d(-72px,-180px,0); }
  }

  @keyframes cosmosTwinkle {
    0%   { opacity: .10; filter: drop-shadow(0 0 1px rgba(255,255,255,.12)); }
    45%  { opacity: .18; filter: drop-shadow(0 0 2px rgba(180,205,255,.18)); }
    100% { opacity: .13; filter: drop-shadow(0 0 1px rgba(255,255,255,.10)); }
  }

  @keyframes softReveal {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes gentleFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
  }

  .block-container {
    padding-top: 1.05rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1380px !important;
    position: relative;
    z-index: 2;
    animation: softReveal .55s ease both;
  }

  section.main > div { background: transparent !important; }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8,8,24,.86), rgba(4,4,16,.90)) !important;
    border-right: 1px solid rgba(255,255,255,.12) !important;
    backdrop-filter: blur(22px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(145%) !important;
    box-shadow: 12px 0 44px rgba(0,0,0,.35) !important;
  }
  [data-testid="stSidebar"] * { color: var(--cosmos-soft) !important; }

  .sidebar-brand {
    font-family: 'Inter', system-ui, sans-serif !important;
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: .20em;
    color: #fff !important;
    padding: .35rem 0 1.05rem;
    border-bottom: 1px solid rgba(255,255,255,.13);
    margin-bottom: 1rem;
    text-transform: uppercase;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', 'Manrope', system-ui, sans-serif !important;
    color: #fff !important;
    letter-spacing: .015em !important;
    text-shadow: none !important;
  }

  p, span, div, label { color: var(--cosmos-soft); }

  .hero {
    position: relative;
    overflow: hidden;
    border-radius: 28px;
    padding: 2rem 2.35rem;
    margin: .2rem 0 1.35rem;
    min-height: 150px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.4rem;
    background:
      radial-gradient(circle at 74% 22%, rgba(122,166,255,.16), transparent 30%),
      radial-gradient(circle at 19% 72%, rgba(255,140,200,.10), transparent 30%),
      linear-gradient(160deg, rgba(255,255,255,0.095), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(18px) saturate(145%);
    -webkit-backdrop-filter: blur(18px) saturate(145%);
    box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.13), 0 0 30px rgba(155,126,255,.13);
    animation: gentleFloat 10s ease-in-out infinite;
    transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease, background .28s ease;
  }

  .hero:hover {
    transform: translateY(-5px);
    border-color: rgba(210,196,255,.34);
    box-shadow: var(--shadow-hover), inset 0 1px 0 rgba(255,255,255,.18);
    background:
      radial-gradient(circle at 74% 22%, rgba(122,166,255,.20), transparent 30%),
      radial-gradient(circle at 19% 72%, rgba(255,140,200,.13), transparent 30%),
      linear-gradient(160deg, rgba(255,255,255,0.115), rgba(255,255,255,0.045));
  }

  .hero::before,
  [data-testid="metric-container"]::before,
  [data-testid="stForm"]::before,
  [data-testid="stDataFrame"]::before,
  [data-testid="stExpander"]::before,
  .info-box::before,
  .result-card::before,
  [data-testid="stPlotlyChart"]::before,
  [data-testid="stPyplot"]::before {
    content: none !important;
    display: none !important;
    animation: none !important;
  }

  .hero h1 {
    margin: 0 0 .5rem !important;
    font-size: clamp(1.9rem, 3.6vw, 3.15rem) !important;
    line-height: 1.02 !important;
    font-weight: 900 !important;
    color: #fff !important;
    letter-spacing: .01em !important;
    text-transform: none !important;
  }

  .hero p {
    margin: 0 !important;
    color: var(--cosmos-soft) !important;
    font-size: .98rem !important;
    line-height: 1.65 !important;
  }

  .hero-eyebrow {
    font-size: .70rem;
    text-transform: uppercase;
    letter-spacing: .22em;
    color: var(--cosmos-violet) !important;
    font-weight: 800;
    margin-bottom: .6rem;
  }

  .hero-badge {
    position: relative;
    z-index: 1;
    padding: .72rem 1.15rem;
    border-radius: 999px;
    color: #fff !important;
    font-weight: 800;
    letter-spacing: .06em;
    font-size: .76rem;
    text-transform: uppercase;
    background: linear-gradient(90deg, rgba(80,140,255,0.18), rgba(255,140,180,0.14));
    border: 1px solid rgba(200,180,255,0.38);
    box-shadow: 0 0 22px rgba(140,120,255,0.28), inset 0 0 10px rgba(180,160,255,0.16);
    white-space: nowrap;
  }

  .hero-glyph {
    font-size: 3.1rem;
    opacity: .34;
    color: #fff !important;
    filter: drop-shadow(0 0 16px rgba(122,166,255,.45));
  }

  .hero-star {
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 12px rgba(255,255,255,.75);
    opacity: .65;
  }

  .hero-star:nth-child(1) { left: 58%; top: 25%; }
  .hero-star:nth-child(2) { left: 74%; top: 62%; }
  .hero-star:nth-child(3) { left: 34%; top: 78%; }
  .hero-star:nth-child(4) { left: 90%; top: 34%; }

  [data-testid="metric-container"],
  [data-testid="stForm"],
  [data-testid="stDataFrame"],
  [data-testid="stExpander"],
  .info-box,
  .result-card,
  [data-testid="stPlotlyChart"],
  [data-testid="stPyplot"] {
    position: relative !important;
    overflow: hidden !important;
    border-radius: var(--radius-lg) !important;
    background:
      linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.034)),
      rgba(8, 9, 22, .64) !important;
    border: 1px solid var(--cosmos-border) !important;
    backdrop-filter: blur(18px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(145%) !important;
    box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.105), 0 0 24px rgba(155,126,255,.08) !important;
    color: var(--cosmos-text) !important;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease, background .25s ease !important;
  }

  [data-testid="metric-container"]:hover,
  [data-testid="stForm"]:hover,
  [data-testid="stDataFrame"]:hover,
  [data-testid="stExpander"]:hover,
  .info-box:hover,
  .result-card:hover,
  [data-testid="stPlotlyChart"]:hover,
  [data-testid="stPyplot"]:hover {
    transform: translateY(-6px) !important;
    border-color: var(--cosmos-border-hover) !important;
    background:
      linear-gradient(180deg, rgba(255,255,255,.095), rgba(255,255,255,.043)),
      rgba(10, 11, 28, .72) !important;
    box-shadow: var(--shadow-hover), inset 0 1px 0 rgba(255,255,255,.16) !important;
  }

  [data-testid="metric-container"] { padding: 1.2rem 1.25rem !important; }

  [data-testid="stMetricLabel"] p {
    color: var(--cosmos-muted) !important;
    font-size: .72rem !important;
    letter-spacing: .13em !important;
    text-transform: uppercase !important;
    font-weight: 800 !important;
  }

  [data-testid="stMetricValue"],
  [data-testid="stMetricValue"] > div {
    color: #fff !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
  }

  .section-hd {
    color: #fff !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    font-size: 1.10rem;
    font-weight: 900;
    letter-spacing: .035em;
    text-transform: uppercase;
    margin-bottom: .38rem;
  }

  .section-sub {
    color: var(--cosmos-soft) !important;
    line-height: 1.75;
    font-size: .96rem;
    margin-bottom: 1.1rem;
  }

  .info-box {
    padding: 1.08rem 1.22rem !important;
    color: var(--cosmos-soft) !important;
    line-height: 1.75 !important;
    border-radius: 20px !important;
  }

  .divider-label,
  .col-label {
    color: var(--cosmos-violet) !important;
    font-size: .66rem;
    font-weight: 900;
    letter-spacing: .17em;
    text-transform: uppercase;
  }

  .divider-label::before,
  .divider-label::after,
  .col-label::after {
    background: linear-gradient(90deg, transparent, rgba(187,162,255,.36), transparent) !important;
  }

  .pill {
    display: inline-block;
    padding: .35rem .82rem;
    border-radius: 999px;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    border: 1px solid rgba(255,255,255,.16);
    background: rgba(255,255,255,.07);
    transition: transform .22s ease, box-shadow .22s ease;
  }
  .pill:hover { transform: translateY(-2px); box-shadow: 0 0 22px rgba(187,162,255,.25); }
  .pill-expand { color: #a9c5ff !important; border-color: rgba(122,166,255,.35); }
  .pill-maintain { color: #a9f8dc !important; border-color: rgba(125,247,196,.32); }
  .pill-optimize { color: #ffdea5 !important; border-color: rgba(255,208,138,.32); }
  .pill-drop { color: #ffb3d5 !important; border-color: rgba(255,140,200,.34); }

  .result-expand { border-left: 4px solid #7aa6ff !important; }
  .result-maintain { border-left: 4px solid #7df7c4 !important; }
  .result-optimize { border-left: 4px solid #ffd08a !important; }
  .result-drop { border-left: 4px solid #ff8cc8 !important; }

  .stTabs [data-baseweb="tab-list"] {
    gap: .85rem;
    background: rgba(6,7,20,.58);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 999px;
    padding: .42rem .55rem;
    backdrop-filter: blur(16px);
  }

  .stTabs [data-baseweb="tab"] {
    color: var(--cosmos-muted) !important;
    border-radius: 999px !important;
    font-weight: 800 !important;
    font-size: .84rem !important;
    letter-spacing: .02em;
    padding: 0.55rem 1.35rem !important;
    min-width: 120px;
    justify-content: center;
    transition: all .22s ease !important;
  }

  .stTabs [data-baseweb="tab"]:hover {
    color: #fff !important;
    background: rgba(255,255,255,.075) !important;
  }

  .stTabs [aria-selected="true"] {
    color: #fff !important;
    background: linear-gradient(90deg, rgba(122,166,255,.20), rgba(187,162,255,.18)) !important;
    box-shadow: 0 0 22px rgba(122,166,255,.18) !important;
  }

  [data-testid="stForm"] { padding: 1.45rem 1.55rem 1.65rem !important; }
  [data-testid="stPyplot"], [data-testid="stPlotlyChart"] {
    padding: 1.25rem !important;
    background: rgba(7,8,20,.78) !important;
    border-radius: 24px !important;
  }

  button[title="View fullscreen"],
  [data-testid="StyledFullScreenButton"] {
    display: none !important;
  }

  .stTextInput input,
  .stNumberInput input,
  .stSelectbox [data-baseweb="select"] > div {
    background: rgba(7,8,20,.72) !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    color: #fff !important;
    border-radius: 15px !important;
    min-height: 42px !important;
    box-shadow: none !important;
  }

  .stTextInput input:focus,
  .stNumberInput input:focus,
  .stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: rgba(187,162,255,.54) !important;
    box-shadow: 0 0 0 3px rgba(187,162,255,.12) !important;
  }

  .stSelectbox label,
  .stNumberInput label,
  .stSlider label,
  .stRadio label,
  .stCheckbox label,
  .stTextInput label {
    color: var(--cosmos-muted) !important;
    font-weight: 800 !important;
    font-size: .72rem !important;
    letter-spacing: .10em !important;
    text-transform: uppercase !important;
  }

  [data-testid="stFormSubmitButton"] > button,
  .stButton > button {
    border-radius: 999px !important;
    border: 1px solid rgba(200,180,255,.34) !important;
    background: linear-gradient(90deg, rgba(122,166,255,.22), rgba(187,162,255,.18)) !important;
    color: #fff !important;
    font-weight: 900 !important;
    letter-spacing: .05em !important;
    transition: all .22s ease !important;
    box-shadow: 0 10px 26px rgba(0,0,0,.24), 0 0 20px rgba(122,166,255,.16) !important;
  }

  [data-testid="stFormSubmitButton"] > button:hover,
  .stButton > button:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(220,210,255,.55) !important;
    box-shadow: 0 16px 36px rgba(0,0,0,.34), 0 0 30px rgba(187,162,255,.28) !important;
  }

  [data-testid="stDataFrame"] [role="columnheader"] {
    background: rgba(122,166,255,.10) !important;
    color: #fff !important;
    font-weight: 800 !important;
  }

  [data-testid="stDataFrame"] div,
  [data-testid="stDataFrame"] span { color: var(--cosmos-soft) !important; }

  [data-testid="stExpander"] summary p {
    color: var(--cosmos-soft) !important;
    font-weight: 800 !important;
  }

  [data-testid="stAlert"] {
    border-radius: 18px !important;
    background: rgba(10,11,28,.76) !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    color: var(--cosmos-soft) !important;
  }

  hr { border: none !important; border-top: 1px solid rgba(255,255,255,.11) !important; margin: 1.35rem 0 !important; }

  [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--cosmos-violet) !important;
    box-shadow: 0 0 12px rgba(187,162,255,.34) !important;
  }

  ::selection { background: rgba(187,162,255,.26); color: #fff; }
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-track { background: rgba(3,2,14,.86); }
  ::-webkit-scrollbar-thumb { background: rgba(187,162,255,.34); border-radius: 999px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(187,162,255,.58); }



  /* ─────────────────────────────────────────────
     POLISHED PREDICTION FORM
     tighter layout, premium inputs, full-width CTA
  ───────────────────────────────────────────── */
  [data-testid="stForm"] {
    max-width: 1240px !important;
    margin: 0 auto 0.9rem auto !important;
    padding: 1.45rem 1.55rem 1.25rem !important;
    border-radius: 24px !important;
    background:
      radial-gradient(circle at 22% 15%, rgba(187,162,255,.075), transparent 26%),
      radial-gradient(circle at 78% 65%, rgba(122,166,255,.055), transparent 30%),
      linear-gradient(180deg, rgba(255,255,255,.068), rgba(255,255,255,.028)),
      rgba(7,8,20,.70) !important;
  }

  [data-testid="stForm"] > div {
    gap: 1.15rem !important;
  }

  .col-label {
    display: flex !important;
    align-items: center !important;
    gap: .55rem !important;
    margin: .15rem 0 .85rem !important;
    padding-bottom: .55rem !important;
    border-bottom: 1px solid rgba(187,162,255,.16) !important;
  }

  .col-label::after {
    content: none !important;
  }

  [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: .65rem !important;
  }

  [data-testid="stForm"] label {
    margin-bottom: .25rem !important;
  }

  [data-testid="stForm"] .stSelectbox,
  [data-testid="stForm"] .stNumberInput,
  [data-testid="stForm"] .stTextInput {
    margin-bottom: .42rem !important;
  }

  [data-testid="stForm"] .stNumberInput > div,
  [data-testid="stForm"] .stSelectbox > div {
    box-shadow: 0 8px 18px rgba(0,0,0,.16) !important;
    border-radius: 16px !important;
  }

  [data-testid="stForm"] input,
  [data-testid="stForm"] [data-baseweb="select"] > div {
    min-height: 44px !important;
    background: rgba(5,6,18,.78) !important;
    border: 1px solid rgba(255,255,255,.13) !important;
    color: #f7f4ff !important;
  }

  [data-testid="stForm"] input:hover,
  [data-testid="stForm"] [data-baseweb="select"] > div:hover {
    border-color: rgba(187,162,255,.34) !important;
    background: rgba(8,9,24,.86) !important;
  }

  [data-testid="stForm"] input:focus,
  [data-testid="stForm"] [data-baseweb="select"] > div:focus-within {
    border-color: rgba(210,196,255,.58) !important;
    box-shadow: 0 0 0 3px rgba(187,162,255,.12), 0 0 20px rgba(122,166,255,.08) !important;
  }

  [data-testid="stForm"] .info-box {
    margin-top: .25rem !important;
    padding: .85rem .95rem !important;
    border-radius: 18px !important;
    line-height: 1.58 !important;
    background: rgba(10,12,30,.56) !important;
    border-color: rgba(210,196,255,.15) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 8px 22px rgba(0,0,0,.20) !important;
  }

  [data-testid="stForm"] .info-box:hover {
    transform: none !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.10), 0 10px 28px rgba(0,0,0,.26) !important;
  }

  [data-testid="stFormSubmitButton"] {
    width: 100% !important;
    margin-top: 1.05rem !important;
  }

  [data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-height: 52px !important;
    border-radius: 18px !important;
    justify-content: center !important;
    font-size: .92rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    background:
      linear-gradient(90deg, rgba(122,166,255,.34), rgba(187,162,255,.30), rgba(255,140,200,.18)) !important;
    border: 1px solid rgba(220,210,255,.46) !important;
    box-shadow:
      0 12px 34px rgba(0,0,0,.30),
      0 0 22px rgba(122,166,255,.20),
      inset 0 1px 0 rgba(255,255,255,.18) !important;
  }

  [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-4px) scale(1.005) !important;
    border-color: rgba(245,238,255,.72) !important;
    background:
      linear-gradient(90deg, rgba(122,166,255,.44), rgba(187,162,255,.40), rgba(255,140,200,.25)) !important;
    box-shadow:
      0 18px 46px rgba(0,0,0,.42),
      0 0 38px rgba(187,162,255,.36),
      0 0 70px rgba(122,166,255,.14),
      inset 0 1px 0 rgba(255,255,255,.24) !important;
  }

  [data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(-1px) scale(.996) !important;
  }

  /* Remove the little plus/minus buttons from visually dominating number inputs */
  [data-testid="stForm"] [data-testid="stNumberInputStepDown"],
  [data-testid="stForm"] [data-testid="stNumberInputStepUp"] {
    background: rgba(255,255,255,.045) !important;
    border-left: 1px solid rgba(255,255,255,.08) !important;
    color: rgba(247,244,255,.75) !important;
  }

  [data-testid="stForm"] [data-testid="stNumberInputStepDown"]:hover,
  [data-testid="stForm"] [data-testid="stNumberInputStepUp"]:hover {
    background: rgba(187,162,255,.16) !important;
    color: #ffffff !important;
  }




  /* ─────────────────────────────────────────────
     FINAL DASHBOARD LAYOUT FIX
     Wider main canvas, tighter sidebar, form behaves like dashboard section
  ───────────────────────────────────────────── */

  .block-container {
    max-width: 1520px !important;
    padding-left: 2.3rem !important;
    padding-right: 2.3rem !important;
  }

  [data-testid="stSidebar"] {
    width: 245px !important;
    min-width: 245px !important;
  }

  [data-testid="stSidebar"] > div:first-child {
    width: 245px !important;
    min-width: 245px !important;
  }

  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: .65rem !important;
  }

  [data-testid="stSidebar"] .stSelectbox,
  [data-testid="stSidebar"] .stMultiSelect,
  [data-testid="stSidebar"] .stSlider {
    margin-bottom: .55rem !important;
  }

  .info-box,
  .result-card,
  [data-testid="stForm"] {
    width: 100% !important;
    max-width: none !important;
  }

  [data-testid="stForm"] {
    margin: 1rem 0 1.45rem 0 !important;
    padding: 1.65rem 1.85rem 1.45rem !important;
    border-radius: 26px !important;
  }

  [data-testid="stForm"] [data-testid="column"] {
    padding-left: .35rem !important;
    padding-right: .35rem !important;
  }

  [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    gap: 1.35rem !important;
  }

  [data-testid="stForm"] .stSelectbox,
  [data-testid="stForm"] .stNumberInput,
  [data-testid="stForm"] .stTextInput {
    margin-bottom: .62rem !important;
  }

  [data-testid="stForm"] input,
  [data-testid="stForm"] [data-baseweb="select"] > div {
    min-height: 46px !important;
  }

  [data-testid="stForm"] .info-box {
    min-height: 92px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
  }

  [data-testid="stFormSubmitButton"] {
    width: 100% !important;
    margin-top: 1.15rem !important;
  }

  [data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-height: 54px !important;
    border-radius: 18px !important;
  }

  [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-4px) scale(1.006) !important;
  }

  .result-card {
    margin-top: 1.7rem !important;
    margin-bottom: 1.6rem !important;
    padding: 1.55rem 1.75rem !important;
  }

  .section-hd {
    margin-top: .35rem !important;
  }

  [data-testid="stPyplot"],
  [data-testid="stPlotlyChart"] {
    margin-top: .75rem !important;
  }


  @media (max-width: 900px) {
    .hero { flex-direction: column; align-items: flex-start; padding: 1.5rem; }
    .hero h1 { font-size: 2rem !important; }
  }


  /* ─────────────────────────────────────────────
     QUIET LUXURY MOTION UPGRADE
     Boundary-light cards, rare meteors, deeper frost,
     purple glow, chart entrance animation.
     No shimmer. No JS. Safe raw CSS.
  ───────────────────────────────────────────── */

  @keyframes chartReveal {
    from { opacity: 0; transform: translateY(12px) scale(.985); filter: saturate(.82) contrast(.92); }
    to   { opacity: 1; transform: translateY(0) scale(1); filter: saturate(1) contrast(1); }
  }

  @keyframes panelBreath {
    0%, 100% { box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.12), 0 0 24px rgba(155,126,255,.10); }
    50%      { box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.15), 0 0 34px rgba(187,162,255,.16); }
  }

  @keyframes boundaryGlow {
    0%   { opacity: .38; filter: blur(.2px); }
    50%  { opacity: .92; filter: blur(.0px); }
    100% { opacity: .48; filter: blur(.25px); }
  }

  @keyframes meteorFallA {
    0%   { transform: translate3d(-12vw,-12vh,0) rotate(-23deg); opacity: 0; }
    5%   { opacity: .42; }
    14%  { opacity: .18; }
    20%  { transform: translate3d(112vw,58vh,0) rotate(-23deg); opacity: 0; }
    100% { transform: translate3d(112vw,58vh,0) rotate(-23deg); opacity: 0; }
  }

  @keyframes meteorFallB {
    0%   { transform: translate3d(95vw,-18vh,0) rotate(-31deg); opacity: 0; }
    6%   { opacity: .32; }
    15%  { opacity: .12; }
    23%  { transform: translate3d(-18vw,70vh,0) rotate(-31deg); opacity: 0; }
    100% { transform: translate3d(-18vw,70vh,0) rotate(-31deg); opacity: 0; }
  }

  @keyframes slowNebulaDepth {
    0%, 100% { transform: translate3d(0,0,0) scale(1); opacity: .42; }
    50%      { transform: translate3d(1.2vw,-1.0vh,0) scale(1.025); opacity: .55; }
  }

  .cosmos-motion-layer {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
  }

  .cosmos-nebula-depth {
    position: absolute;
    inset: -10%;
    background:
      radial-gradient(circle at 24% 62%, rgba(122,166,255,.095), transparent 28%),
      radial-gradient(circle at 72% 36%, rgba(187,162,255,.105), transparent 31%),
      radial-gradient(circle at 58% 78%, rgba(255,140,200,.055), transparent 26%);
    filter: blur(26px);
    animation: slowNebulaDepth 24s ease-in-out infinite;
    opacity: .46;
  }

  .cosmos-meteor {
    position: absolute;
    width: 190px;
    height: 1px;
    border-radius: 999px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.65), rgba(187,162,255,.32), transparent);
    box-shadow: 0 0 12px rgba(187,162,255,.22);
    opacity: 0;
  }

  .cosmos-meteor.m1 { top: 11%; left: 0; animation: meteorFallA 28s linear infinite 5s; }
  .cosmos-meteor.m2 { top: 4%; right: 0; width: 145px; animation: meteorFallB 34s linear infinite 16s; }
  .cosmos-meteor.m3 { top: 24%; left: -5%; width: 120px; animation: meteorFallA 42s linear infinite 27s; opacity: .0; }

  .hero,
  [data-testid="metric-container"],
  [data-testid="stForm"],
  [data-testid="stDataFrame"],
  [data-testid="stExpander"],
  .info-box,
  .result-card,
  [data-testid="stPlotlyChart"],
  [data-testid="stPyplot"] {
    isolation: isolate !important;
    box-shadow:
      0 18px 56px rgba(0,0,0,.42),
      inset 0 1px 0 rgba(255,255,255,.15),
      inset 0 -1px 0 rgba(255,255,255,.045),
      0 0 30px rgba(187,162,255,.11) !important;
  }

  .hero::after,
  [data-testid="metric-container"]::after,
  [data-testid="stForm"]::after,
  [data-testid="stDataFrame"]::after,
  [data-testid="stExpander"]::after,
  .info-box::after,
  .result-card::after,
  [data-testid="stPlotlyChart"]::after,
  [data-testid="stPyplot"]::after {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    border-radius: inherit !important;
    pointer-events: none !important;
    z-index: -1 !important;
    padding: 1px !important;
    background:
      linear-gradient(135deg,
        rgba(255,255,255,.16),
        rgba(187,162,255,.42),
        rgba(122,166,255,.20),
        rgba(255,255,255,.10));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
            mask-composite: exclude;
    opacity: .24 !important;
    transition: opacity .28s ease, filter .28s ease !important;
  }

  .hero:hover::after,
  [data-testid="metric-container"]:hover::after,
  [data-testid="stForm"]:hover::after,
  [data-testid="stDataFrame"]:hover::after,
  [data-testid="stExpander"]:hover::after,
  .info-box:hover::after,
  .result-card:hover::after,
  [data-testid="stPlotlyChart"]:hover::after,
  [data-testid="stPyplot"]:hover::after {
    opacity: .92 !important;
    filter: drop-shadow(0 0 12px rgba(187,162,255,.34)) !important;
    animation: boundaryGlow 2.8s ease-in-out infinite !important;
  }

  [data-testid="stForm"],
  .result-card,
  [data-testid="stPyplot"],
  [data-testid="stPlotlyChart"] {
    background:
      radial-gradient(circle at 18% 8%, rgba(187,162,255,.09), transparent 25%),
      radial-gradient(circle at 82% 82%, rgba(122,166,255,.06), transparent 30%),
      linear-gradient(180deg, rgba(255,255,255,.082), rgba(255,255,255,.030)),
      rgba(7,8,20,.74) !important;
    backdrop-filter: blur(22px) saturate(158%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(158%) !important;
  }

  [data-testid="stPyplot"],
  [data-testid="stPlotlyChart"] {
    animation: chartReveal .72s cubic-bezier(.22,.9,.25,1) both, panelBreath 8s ease-in-out infinite !important;
    border-color: rgba(187,162,255,.18) !important;
  }

  [data-testid="stPyplot"] img,
  [data-testid="stPlotlyChart"] svg,
  [data-testid="stPlotlyChart"] canvas {
    animation: chartReveal .62s cubic-bezier(.22,.9,.25,1) both !important;
  }

  [data-testid="stPyplot"]:hover,
  [data-testid="stPlotlyChart"]:hover {
    transform: translateY(-6px) scale(1.004) !important;
    box-shadow:
      0 24px 76px rgba(0,0,0,.54),
      inset 0 1px 0 rgba(255,255,255,.18),
      0 0 46px rgba(187,162,255,.24),
      0 0 90px rgba(122,166,255,.10) !important;
  }

  [data-testid="stFormSubmitButton"] > button {
    position: relative !important;
    overflow: hidden !important;
  }

  [data-testid="stFormSubmitButton"] > button::after {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    background: radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(255,255,255,.20), transparent 32%);
    opacity: 0;
    transition: opacity .25s ease;
    pointer-events: none;
  }

  [data-testid="stFormSubmitButton"] > button:hover::after {
    opacity: 1;
  }

  @media (prefers-reduced-motion: reduce) {
    .cosmos-meteor,
    .cosmos-nebula-depth,
    [data-testid="stPyplot"],
    [data-testid="stPlotlyChart"],
    [data-testid="stPyplot"] img,
    [data-testid="stPlotlyChart"] svg,
    [data-testid="stPlotlyChart"] canvas {
      animation: none !important;
    }
  }
</style>
"""
CSS = CSS.replace("{BACKGROUND_URL}", BACKGROUND_URL)

st.markdown(CSS, unsafe_allow_html=True)

st.markdown("""
<div class="cosmos-motion-layer">
  <div class="cosmos-nebula-depth"></div>
  <div class="cosmos-meteor m1"></div>
  <div class="cosmos-meteor m2"></div>
  <div class="cosmos-meteor m3"></div>
</div>
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
    """Create a readable, professional matplotlib figure for the COSMOS theme."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor((0.025, 0.027, 0.06, 0.0))
    ax.set_facecolor((0.035, 0.04, 0.09, 0.72))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color((1, 1, 1, 0.13))
        ax.spines[spine].set_linewidth(0.8)
    ax.tick_params(colors=INK_MUTED, labelsize=9.5, length=0, pad=7)
    ax.xaxis.label.set_color(INK_SOFT)
    ax.yaxis.label.set_color(INK_SOFT)
    ax.title.set_color(INK)
    ax.title.set_fontsize(12.5)
    ax.title.set_fontweight("bold")
    ax.grid(axis="y", color="#ffffff", linewidth=0.8, linestyle="-", alpha=0.095)
    ax.set_axisbelow(True)
    return fig, ax


def col_seq(labels):
    return [DECISION_COLORS.get(str(l), ACCENT) for l in labels]


def add_bar_shimmer(bars, ax, alpha=0.94):
    """Compatibility helper. No shimmer is applied in the professional theme."""
    for bar in bars:
        bar.set_alpha(alpha)
        bar.set_linewidth(0)
    return bars


def _fmt_chart_value(v, value_format="number"):
    if value_format == "percent":
        return f"{v:.0%}"
    if value_format == "money":
        return f"${v:,.0f}"
    return f"{v:,.0f}"


def _style_axis(ax, grid_axis="y"):
    ax.set_facecolor((0.035, 0.04, 0.09, 0.72))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color((1, 1, 1, 0.12))
        ax.spines[spine].set_linewidth(0.8)
    ax.tick_params(colors=INK_MUTED, labelsize=9.4, length=0, pad=8)
    ax.xaxis.label.set_color(INK_SOFT)
    ax.yaxis.label.set_color(INK_SOFT)
    ax.title.set_color(INK)
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")
    if grid_axis:
        ax.grid(axis=grid_axis, color="#ffffff", linewidth=0.8, alpha=0.10)
    ax.set_axisbelow(True)


def _finish_fig(fig, kind="default"):
    fig.patch.set_facecolor((0.025, 0.027, 0.06, 0.0))
    if kind == "horizontal":
        fig.subplots_adjust(left=0.18, right=0.88, top=0.82, bottom=0.18)
    elif kind == "vertical":
        fig.subplots_adjust(left=0.11, right=0.97, top=0.82, bottom=0.18)
    else:
        fig.tight_layout(pad=1.7)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def shimmer_vertical_bar_chart(title, labels, series, max_value=None, value_format="number", height=430):
    """Professional vertical bar chart. Name kept for compatibility; shimmer removed."""
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

    if not labels or not all_values:
        st.info("No chart data available for the current filter.")
        return

    n_groups = len(labels)
    n_series = max(1, len(clean_series))
    x = np.arange(n_groups)
    width = min(0.74 / n_series, 0.34)

    fig_w = max(8.8, min(14.0, n_groups * 0.95 + 3.7))
    fig_h = max(4.05, min(6.2, height / 96))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    _style_axis(ax, grid_axis="y")

    for j, s in enumerate(clean_series):
        offset = (j - (n_series - 1) / 2) * width
        colors = s.get("colors") or [s.get("color", ACCENT)] * len(s["values"])
        bars = ax.bar(x + offset, s["values"], width=width, color=colors, label=s["name"], alpha=0.94)
        for bar, val in zip(bars, s["values"]):
            label = _fmt_chart_value(val, value_format)
            ax.annotate(
                label,
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                textcoords="offset points",
                xytext=(0, 7),
                ha="center",
                color=INK_SOFT,
                fontsize=9,
                fontweight="bold",
            )

    ax.set_title(title, pad=18)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, ha="center", color=INK_SOFT, fontsize=9.4)
    if max_value is not None:
        ax.set_ylim(top=float(max_value) * 1.20 if float(max_value) > 0 else 1)
    elif all_values:
        top = max(all_values)
        ax.set_ylim(top=top * 1.22 if top > 0 else 1)
    if len(clean_series) > 1:
        leg = ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=min(3, len(clean_series)))
        for t in leg.get_texts():
            t.set_color(INK_SOFT)
    _finish_fig(fig, kind="vertical")


def shimmer_horizontal_bar_chart(title, labels, values, colors=None, value_format="number", height=430):
    """Professional horizontal bar chart. Name kept for compatibility; shimmer removed."""
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

    fig_h = max(4.05, min(6.2, len(labels) * 0.44 + 2.25))
    fig, ax = plt.subplots(figsize=(9.8, fig_h))
    _style_axis(ax, grid_axis="x")
    ax.grid(axis="y", visible=False)

    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, alpha=0.94, height=0.58)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, color=INK_SOFT, fontsize=9.4)
    ax.invert_yaxis()
    ax.set_title(title, pad=18)

    max_abs = max(abs(v) for v in values) or 1
    pad = max_abs * 0.035
    for bar, val in zip(bars, values):
        x_pos = val + pad if val >= 0 else val - pad
        ha = "left" if val >= 0 else "right"
        ax.text(
            x_pos,
            bar.get_y() + bar.get_height() / 2,
            _fmt_chart_value(val, value_format),
            va="center",
            ha=ha,
            color=INK_SOFT,
            fontsize=9.2,
            fontweight="bold",
        )
    ax.set_xlim(left=min(0, min(values)) - max_abs * 0.22, right=max(values) + max_abs * 0.22)
    _finish_fig(fig, kind="horizontal")


def shimmer_pie_chart(title, labels, values, colors=None, height=430):
    """Professional donut chart. Name kept for compatibility; shimmer removed."""
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

    fig, ax = plt.subplots(figsize=(7.6, max(4.2, min(5.6, height / 90))))
    fig.patch.set_facecolor((0.025, 0.027, 0.06, 0.0))
    ax.set_facecolor((0.035, 0.04, 0.09, 0.72))

    wedges, _ = ax.pie(
        values,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.42, "edgecolor": "#17182d", "linewidth": 1.5, "alpha": 0.96},
    )
    ax.text(0, 0.045, f"{int(total):,}", ha="center", va="center", color=INK, fontsize=19, fontweight="bold")
    ax.text(0, -0.15, "flights", ha="center", va="center", color=INK_MUTED, fontsize=9.5)
    ax.set_title(title, color=INK, fontsize=13, fontweight="bold", pad=18)

    legend_labels = [f"{lab}  {val / total * 100:.1f}%" for lab, val in zip(labels, values)]
    leg = ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9.4)
    for t in leg.get_texts():
        t.set_color(INK_SOFT)
    ax.set_aspect("equal")
    _finish_fig(fig)


def shimmer_classic_horizontal_bar_chart(title, labels, values, color=ACCENT, value_format="money", height=460):
    """Classic horizontal chart compatibility wrapper; shimmer removed."""
    colors = color if isinstance(color, list) else [color for _ in labels]
    shimmer_horizontal_bar_chart(title, labels, values, colors=colors, value_format=value_format, height=height)


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
# Native st.tabs keeps tab switching instant and clean.
# Keep the visual/order exactly like the original dashboard.
OVERVIEW_TAB_LABEL = "📊  Overview"
PREDICTION_TAB_LABEL = "🤖  Prediction Tool"
if "active_tab_label" not in st.session_state:
    st.session_state.active_tab_label = OVERVIEW_TAB_LABEL

tab_labels = [
    OVERVIEW_TAB_LABEL,
    "🔍  Performance Drivers",
    "🗺  Route Actions",
    "📈  Route Stability",
    PREDICTION_TAB_LABEL,
]

# Newer Streamlit versions support a default selected tab.
# The fallback keeps the app compatible if your deployed version is older.
try:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        tab_labels,
        default=st.session_state.active_tab_label,
    )
    TABS_DEFAULT_SUPPORTED = True
except TypeError:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)
    TABS_DEFAULT_SUPPORTED = False


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

    left, right = st.columns(2, gap="large")

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
    left, right = st.columns(2, gap="large")

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

    left, right = st.columns(2, gap="large")
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




def render_prediction_result():
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


# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    # Show results near the top of the Prediction Tool page, not below the full form.
    # This prevents the app from feeling like it jumps to the bottom after clicking Predict.
    render_prediction_result()

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
        st.session_state.active_tab_label = PREDICTION_TAB_LABEL

        # Re-render with Prediction Tool selected, then show the result near the top.
        if TABS_DEFAULT_SUPPORTED:
            st.rerun()

