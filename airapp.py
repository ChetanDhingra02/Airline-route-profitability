import os
import json
import joblib
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="SkyLens · Route Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  PALETTE TOKENS
# ─────────────────────────────────────────────────────────────
C_EXPAND   = "#4ade80"
C_MAINTAIN = "#facc15"
C_OPTIMIZE = "#fb923c"
C_DROP     = "#fb7185"
C_NEUTRAL  = ["#6e40c9","#9150d8","#b480e7","#d2a4f5","#efc5d5","#f3b5c6","#fcb9b2","#ffcc99"]
DECISION_COLORS = {"Expand": C_EXPAND, "Maintain": C_MAINTAIN, "Optimize": C_OPTIMIZE, "Drop": C_DROP}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  — injected once into the Streamlit host page
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500&display=swap');

/* ── TOKENS ─────────────────────────────────────────────────── */
:root {
  --bg:           #0b0b0d;
  --surface:      rgba(20,19,22,0.72);
  --surface-hi:   rgba(32,30,36,0.85);
  --border:       rgba(255,255,255,0.06);
  --border-md:    rgba(255,255,255,0.13);
  --border-hi:    rgba(255,255,255,0.22);
  --border-glow:  rgba(233,179,255,0.30);
  --ink:          #e5e1e4;
  --ink-soft:     #c4bfc6;
  --ink-muted:    #9b8c9e;
  --ink-ghost:    #3e3444;
  --accent:       #e9b3ff;
  --accent-mid:   #c863fb;
  --accent-dk:    #9026c3;
  --pink:         #ffb2b7;
  --green:        #4ade80;
  --yellow:       #facc15;
  --orange:       #fb923c;
  --red:          #fb7185;
  --blur-sm:      blur(16px);
  --blur-md:      blur(28px);
  --blur-lg:      blur(48px);
  --blur-xl:      blur(72px);
  --sh-sm:        0 4px 16px rgba(0,0,0,.60),0 1px 3px rgba(0,0,0,.40);
  --sh-md:        0 8px 32px rgba(0,0,0,.65),0 2px 8px rgba(0,0,0,.50),0 0 0 1px rgba(255,255,255,.04);
  --sh-lg:        0 16px 48px rgba(0,0,0,.70),0 4px 16px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.06);
  --sh-xl:        0 24px 64px rgba(0,0,0,.75),0 8px 24px rgba(233,179,255,.08),0 0 0 1px rgba(255,255,255,.07);
  --glow:         0 0 40px rgba(233,179,255,.18),0 0 80px rgba(233,179,255,.08);
  --r-sm:  10px; --r-md: 16px; --r-lg: 22px; --r-xl: 28px; --r-2xl: 36px;
}

/* ── FULL-APP DEEP BG ───────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Manrope', system-ui, sans-serif !important;
  color: var(--ink) !important;
  -webkit-font-smoothing: antialiased;
}
.stApp {
  background:
    radial-gradient(ellipse 80% 60% at 15% -10%,  rgba(144,38,195,.24) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 85% 110%,  rgba(208,2,66,.18) 0%, transparent 55%),
    linear-gradient(160deg, #0f0c12 0%, #0b0b0d 40%, #0a0810 100%) !important;
  min-height: 100vh !important;
}
.main .block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 5rem !important;
  max-width: 1360px !important;
}

/* ── AMBIENT ORB LAYER ──────────────────────────────────────── */
.stApp::before {
  content: "";
  position: fixed;
  top: -200px; left: -200px;
  width: 700px; height: 700px;
  background: radial-gradient(circle, rgba(233,179,255,.09) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  animation: orbA 20s ease-in-out infinite;
}
.stApp::after {
  content: "";
  position: fixed;
  bottom: -200px; right: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(208,2,66,.09) 0%, transparent 70%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  animation: orbB 25s ease-in-out infinite;
}
@keyframes orbA { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(50px,-40px) scale(1.06)} 66%{transform:translate(-30px,25px) scale(.96)} }
@keyframes orbB { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(-40px,30px) scale(1.04)} 66%{transform:translate(25px,-20px) scale(.97)} }

/* ── SIDEBAR ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(12,11,16,.88) !important;
  backdrop-filter: var(--blur-lg) !important;
  -webkit-backdrop-filter: var(--blur-lg) !important;
  border-right: 1px solid var(--border-md) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,.75), inset -1px 0 0 rgba(255,255,255,.03) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {
  color: var(--ink-soft) !important;
  font-family: 'Manrope', sans-serif !important;
}
[data-testid="stSidebar"]::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"]::-webkit-scrollbar-track { background: transparent; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: var(--ink-ghost); border-radius: 3px; }

/* ── METRIC CARDS — TRUE GLASS BUOYANCY ────────────────────── */
[data-testid="metric-container"] {
  background: linear-gradient(145deg, rgba(44,40,58,.92) 0%, rgba(22,20,30,.88) 100%) !important;
  backdrop-filter: var(--blur-md) !important;
  -webkit-backdrop-filter: var(--blur-md) !important;
  border: 1px solid var(--border-md) !important;
  border-top: 1px solid rgba(255,255,255,.20) !important;
  border-radius: var(--r-xl) !important;
  padding: 30px 32px !important;
  box-shadow: var(--sh-lg), 0 -1px 0 rgba(255,255,255,.06) inset !important;
  margin-bottom: 24px !important;
  position: relative !important;
  overflow: hidden !important;
  transition: transform .40s cubic-bezier(.22,1,.36,1), box-shadow .40s ease !important;
  /* Buoyancy: cards appear to float above the deep bg */
  transform: translateY(0) !important;
}
[data-testid="metric-container"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.28), transparent);
  pointer-events: none;
}
[data-testid="metric-container"]::after {
  content: "";
  position: absolute;
  top: -60px; right: -40px;
  width: 150px; height: 150px;
  background: radial-gradient(circle, rgba(233,179,255,.07) 0%, transparent 70%);
  pointer-events: none;
}
[data-testid="metric-container"]:hover {
  transform: translateY(-8px) !important;
  box-shadow: var(--sh-xl), var(--glow) !important;
  border-color: var(--border-glow) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
  font-family: 'Manrope', sans-serif !important;
  font-size: .66rem !important;
  font-weight: 700 !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  color: var(--ink-muted) !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {
  font-family: 'DM Mono', monospace !important;
  font-size: 2.1rem !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
  letter-spacing: -.035em !important;
  line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] {
  font-family: 'Manrope', sans-serif !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
}

/* ── TABS ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(12,11,16,.85) !important;
  backdrop-filter: var(--blur-sm) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--r-lg) !important;
  padding: 5px !important;
  gap: 3px !important;
  box-shadow: var(--sh-sm) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--r-md) !important;
  font-family: 'Manrope', sans-serif !important;
  font-weight: 600 !important;
  font-size: .80rem !important;
  color: var(--ink-muted) !important;
  padding: 9px 22px !important;
  background: transparent !important;
  border: none !important;
  letter-spacing: .01em !important;
  transition: all .20s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
  background: rgba(255,255,255,.06) !important;
  color: var(--ink-soft) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(233,179,255,.22) 0%, rgba(200,99,251,.18) 100%) !important;
  color: var(--accent) !important;
  border: 1px solid rgba(233,179,255,.28) !important;
  box-shadow: 0 2px 12px rgba(233,179,255,.22), inset 0 1px 0 rgba(255,255,255,.16) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding-top: 2rem !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── HEADINGS ───────────────────────────────────────────────── */
h1,h2,h3,h4 {
  font-family: 'Space Grotesk', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -.02em !important;
  font-weight: 600 !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--ink-soft) !important;
  line-height: 1.70 !important;
  font-size: .90rem !important;
}

/* ── INPUTS ─────────────────────────────────────────────────── */
.stSelectbox label,.stNumberInput label,
.stSlider label,.stRadio label,.stCheckbox label,.stTextInput label {
  color: var(--ink-soft) !important; font-weight: 600 !important;
  font-size: .78rem !important; letter-spacing: .06em !important;
  text-transform: uppercase !important; font-family: 'Manrope', sans-serif !important;
}
.stSelectbox [data-baseweb="select"] div,
.stTextInput input, .stNumberInput input {
  color: var(--ink) !important;
  background: rgba(18,16,24,.85) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'Manrope', sans-serif !important;
  font-size: .88rem !important;
  transition: border-color .18s ease, box-shadow .18s ease !important;
}
.stSelectbox [data-baseweb="select"] div:focus-within,
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--accent-mid) !important;
  box-shadow: 0 0 0 3px rgba(200,99,251,.20), 0 0 18px rgba(200,99,251,.14) !important;
}

/* ── DATAFRAME ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--border-md) !important;
  box-shadow: var(--sh-md) !important;
  background: rgba(14,12,20,.85) !important;
  backdrop-filter: var(--blur-md) !important;
}

/* ── EXPANDER ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--border-md) !important;
  border-radius: var(--r-lg) !important;
  background: rgba(16,14,22,.85) !important;
  backdrop-filter: var(--blur-sm) !important;
  box-shadow: var(--sh-sm) !important;
  overflow: hidden !important;
  margin-top: 16px !important;
  transition: box-shadow .30s ease !important;
}
[data-testid="stExpander"]:hover {
  box-shadow: var(--sh-md) !important;
}
[data-testid="stExpander"] summary p {
  color: var(--ink) !important;
  font-weight: 600 !important;
  font-size: .88rem !important;
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ── FORM ───────────────────────────────────────────────────── */
[data-testid="stForm"] {
  background: linear-gradient(145deg, rgba(38,34,52,.92) 0%, rgba(18,16,26,.90) 100%) !important;
  backdrop-filter: var(--blur-lg) !important;
  -webkit-backdrop-filter: var(--blur-lg) !important;
  border: 1px solid var(--border-md) !important;
  border-top: 1px solid rgba(255,255,255,.18) !important;
  border-radius: var(--r-2xl) !important;
  padding: 40px 44px !important;
  box-shadow: var(--sh-xl) !important;
  position: relative !important;
  overflow: hidden !important;
  margin-top: 8px !important;
}
[data-testid="stForm"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(233,179,255,.45) 40%, rgba(208,2,66,.32) 70%, transparent 100%);
}

/* ── SUBMIT BUTTON ──────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, var(--accent-mid) 0%, var(--accent-dk) 100%) !important;
  border: none !important;
  border-radius: var(--r-md) !important;
  color: #1a0028 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  font-size: .88rem !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
  padding: 14px 36px !important;
  width: 100% !important;
  transition: all .25s cubic-bezier(.22,1,.36,1) !important;
  box-shadow: 0 6px 24px rgba(200,99,251,.42), 0 2px 8px rgba(200,99,251,.32) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-mid) 100%) !important;
  box-shadow: 0 10px 36px rgba(233,179,255,.58), 0 4px 16px rgba(233,179,255,.38) !important;
  transform: translateY(-3px) !important;
}

/* ── BUTTONS ────────────────────────────────────────────────── */
.stButton > button {
  background: rgba(30,26,40,.85) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--r-md) !important;
  color: var(--ink) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  transition: all .25s cubic-bezier(.22,1,.36,1) !important;
  box-shadow: var(--sh-sm) !important;
}
.stButton > button:hover {
  background: rgba(48,42,66,.90) !important;
  border-color: var(--border-glow) !important;
  box-shadow: var(--sh-md), 0 0 24px rgba(233,179,255,.14) !important;
  transform: translateY(-3px) !important;
}

/* ── ALERTS ─────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r-lg) !important;
  border: 1px solid var(--border-md) !important;
  backdrop-filter: var(--blur-sm) !important;
  background: rgba(16,14,22,.85) !important;
}

/* ── HR ─────────────────────────────────────────────────────── */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, var(--border-hi), transparent) !important;
  margin: 2rem 0 !important;
}

/* ── SCROLL ANIMATION ENGINE ────────────────────────────────── */
@keyframes fadeUp {
  from { opacity:0; transform:translateY(32px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes scaleUp {
  from { opacity:0; transform:scale(.96) translateY(20px); }
  to   { opacity:1; transform:scale(1) translateY(0); }
}

/* ── CUSTOM COMPONENTS ──────────────────────────────────────── */
.hero {
  background: linear-gradient(145deg, rgba(52,42,72,.94) 0%, rgba(22,18,34,.92) 60%, rgba(14,10,24,.96) 100%);
  backdrop-filter: var(--blur-xl);
  -webkit-backdrop-filter: var(--blur-xl);
  border: 1px solid var(--border-md);
  border-top: 1px solid rgba(255,255,255,.22);
  border-radius: var(--r-2xl);
  padding: 64px 80px;
  margin-bottom: 56px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--sh-xl), var(--glow);
  animation: scaleUp .75s cubic-bezier(.22,1,.36,1) both;
}
.hero::before {
  content:"";
  position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent 0%,rgba(233,179,255,.65) 35%,rgba(208,2,66,.44) 65%,transparent 100%);
}
.hero::after {
  content:"";
  position:absolute; top:-130px; right:-90px;
  width:520px; height:520px;
  background:radial-gradient(circle,rgba(233,179,255,.13) 0%,transparent 65%);
  pointer-events:none;
}
.hero-eyebrow {
  font-family:'Manrope',sans-serif;
  font-size:.66rem; font-weight:700; letter-spacing:.24em;
  text-transform:uppercase; color:var(--ink-muted);
  margin-bottom:16px; display:flex; align-items:center; gap:12px;
}
.hero-eyebrow::before {
  content:""; width:28px; height:1px;
  background:var(--accent); opacity:.7;
}
.hero h1 {
  font-family:'Space Grotesk',sans-serif !important;
  font-size:3.4rem !important; font-weight:700 !important;
  margin:0 0 18px 0 !important; letter-spacing:-.035em !important;
  line-height:1.08 !important;
  background:linear-gradient(135deg,#f2eaff 0%,var(--accent) 50%,var(--pink) 100%);
  -webkit-background-clip:text !important;
  -webkit-text-fill-color:transparent !important;
  background-clip:text !important;
}
.hero p {
  color:var(--ink-soft) !important;
  font-family:'Manrope',sans-serif !important;
  font-size:1.02rem !important; line-height:1.75 !important;
  margin:0 !important; max-width:580px;
}
.hero-glyph {
  position:absolute; right:80px; top:50%;
  transform:translateY(-50%);
  font-size:10rem; opacity:.055;
  color:var(--accent); line-height:1;
  pointer-events:none; user-select:none; filter:blur(3px);
}

.sidebar-brand {
  font-family:'Space Grotesk',sans-serif;
  font-size:1.45rem; font-weight:700; color:var(--ink);
  padding:6px 0 22px; border-bottom:1px solid var(--border-md);
  margin-bottom:22px; letter-spacing:-.025em;
}
.sidebar-brand span {
  background:linear-gradient(135deg,var(--accent),var(--pink));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}

.section-hd {
  font-family:'Space Grotesk',sans-serif !important;
  font-size:1.10rem !important; font-weight:600 !important;
  color:var(--ink) !important; letter-spacing:-.015em !important;
  margin:0 0 6px 0 !important;
}
.section-sub {
  font-family:'Manrope',sans-serif !important;
  font-size:.88rem !important; color:var(--ink-muted) !important;
  margin:0 0 24px 0 !important; line-height:1.65 !important;
}

.info-box {
  background:linear-gradient(145deg,rgba(32,28,44,.92) 0%,rgba(18,16,26,.88) 100%) !important;
  backdrop-filter:var(--blur-md) !important;
  border:1px solid var(--border-md) !important;
  border-top:1px solid rgba(255,255,255,.15) !important;
  border-radius:var(--r-lg) !important;
  padding:22px 28px !important;
  font-size:.875rem !important; color:var(--ink-soft) !important;
  margin-bottom:20px !important; line-height:1.80 !important;
  box-shadow:var(--sh-md) !important;
  position:relative; overflow:hidden;
  transition:box-shadow .30s ease, transform .30s ease !important;
}
.info-box:hover {
  box-shadow:var(--sh-lg) !important;
  transform:translateY(-2px) !important;
}
.info-box::before {
  content:""; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent,rgba(233,179,255,.32),transparent);
}
.info-box strong { color:var(--ink) !important; font-weight:700 !important; }

.pill {
  display:inline-block; padding:3px 12px; border-radius:99px;
  font-size:.66rem; font-weight:700; letter-spacing:.08em;
  text-transform:uppercase; border:1px solid transparent;
  font-family:'Manrope',sans-serif;
}
.pill-expand   {background:rgba(74,222,128,.15);color:#4ade80;border-color:rgba(74,222,128,.38);}
.pill-maintain {background:rgba(250,204,21,.15);color:#facc15;border-color:rgba(250,204,21,.38);}
.pill-optimize {background:rgba(251,146,60,.15);color:#fb923c;border-color:rgba(251,146,60,.38);}
.pill-drop     {background:rgba(251,113,133,.15);color:#fb7185;border-color:rgba(251,113,133,.38);}

.result-card {
  background:linear-gradient(145deg,rgba(38,34,52,.94) 0%,rgba(18,16,28,.92) 100%) !important;
  backdrop-filter:var(--blur-lg) !important;
  border:1px solid var(--border-md) !important;
  border-radius:var(--r-2xl) !important;
  padding:44px 48px !important;
  margin:36px 0 !important;
  box-shadow:var(--sh-xl) !important;
  position:relative; overflow:hidden;
  animation:scaleUp .55s cubic-bezier(.22,1,.36,1) both;
  transition:transform .35s cubic-bezier(.22,1,.36,1),box-shadow .35s ease !important;
}
.result-card::before {
  content:""; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent);
}
.result-card:hover {
  transform:translateY(-6px) !important;
  box-shadow:var(--sh-xl),0 0 70px rgba(233,179,255,.12) !important;
}
.result-expand   {border-left:3px solid #4ade80 !important;}
.result-maintain {border-left:3px solid #facc15 !important;}
.result-optimize {border-left:3px solid #fb923c !important;}
.result-drop     {border-left:3px solid #fb7185 !important;}
.result-expand::after   {content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:radial-gradient(circle,rgba(74,222,128,.12) 0%,transparent 70%);pointer-events:none;}
.result-maintain::after {content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:radial-gradient(circle,rgba(250,204,21,.12) 0%,transparent 70%);pointer-events:none;}
.result-optimize::after {content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:radial-gradient(circle,rgba(251,146,60,.12) 0%,transparent 70%);pointer-events:none;}
.result-drop::after     {content:"";position:absolute;top:-60px;right:-60px;width:220px;height:220px;background:radial-gradient(circle,rgba(251,113,133,.12) 0%,transparent 70%);pointer-events:none;}

.divider-label {
  display:flex; align-items:center; gap:16px;
  margin:44px 0 24px; color:var(--ink-muted);
  font-size:.68rem; font-weight:700; letter-spacing:.16em;
  text-transform:uppercase; font-family:'Manrope',sans-serif;
}
.divider-label::before { content:""; flex:1; height:1px; background:linear-gradient(90deg,transparent,var(--border-hi)); }
.divider-label::after  { content:""; flex:1; height:1px; background:linear-gradient(90deg,var(--border-hi),transparent); }

/* ── iframes (SVG charts) — glass wrapper ───────────────────── */
iframe {
  border-radius: var(--r-xl) !important;
  border: none !important;
  display: block !important;
}

/* ── scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--ink-ghost); border-radius:5px; }
::-webkit-scrollbar-thumb:hover { background:var(--ink-muted); }

/* ── vertical rhythm ────────────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap:20px !important; }

/* ─────────────────────────────────────────────────────────────
   PROFESSIONAL 3D MOTION UPGRADE — CSS ONLY, LOGIC UNCHANGED
   Adds depth, glass, glow, scroll motion, hover lift, and SVG polish.
   ───────────────────────────────────────────────────────────── */
:root {
  --glass-bg: linear-gradient(145deg, rgba(255,255,255,.105), rgba(255,255,255,.035) 42%, rgba(255,255,255,.055));
  --glass-stroke: rgba(255,255,255,.16);
  --glass-stroke-strong: rgba(255,255,255,.28);
  --violet-glow: rgba(184,92,255,.28);
  --rose-glow: rgba(255,124,182,.20);
  --cyan-glow: rgba(100,210,255,.16);
  --card-depth: 0 22px 65px rgba(0,0,0,.48), 0 8px 24px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.16);
  --card-depth-hover: 0 34px 90px rgba(0,0,0,.56), 0 14px 36px rgba(184,92,255,.16), inset 0 1px 0 rgba(255,255,255,.22);
  --motion-ease: cubic-bezier(.19,1,.22,1);
}

html { scroll-behavior: smooth; }
.stApp {
  isolation: isolate;
  background:
    radial-gradient(circle at 18% 12%, rgba(154,92,255,.24), transparent 34%),
    radial-gradient(circle at 80% 18%, rgba(255,104,180,.13), transparent 30%),
    radial-gradient(circle at 50% 90%, rgba(67,200,255,.10), transparent 38%),
    linear-gradient(135deg, #07070b 0%, #0c0a14 45%, #070810 100%) !important;
}
.stApp::before {
  background:
    radial-gradient(circle at 32% 30%, rgba(233,179,255,.14), transparent 48%),
    radial-gradient(circle at 70% 70%, rgba(100,210,255,.08), transparent 42%) !important;
  mix-blend-mode: screen;
}
.stApp::after {
  background:
    linear-gradient(rgba(255,255,255,.026) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.022) 1px, transparent 1px),
    radial-gradient(circle, rgba(255,255,255,.09) 1px, transparent 1.5px) !important;
  background-size: 48px 48px, 48px 48px, 120px 120px !important;
  background-position: center !important;
  inset: 0 !important;
  width: auto !important;
  height: auto !important;
  opacity: .42;
  filter: none !important;
  animation: gridDrift 28s linear infinite !important;
  z-index: 0;
}
@keyframes gridDrift {
  from { transform: translate3d(0,0,0); }
  to { transform: translate3d(-48px,-48px,0); }
}

.main .block-container {
  position: relative;
  z-index: 1;
  perspective: 1400px;
}

/* hero/title treatment */
h1, h2, h3 {
  font-family: 'Space Grotesk', 'Manrope', system-ui, sans-serif !important;
  letter-spacing: -.04em !important;
}
h1 {
  font-size: clamp(2.7rem, 6vw, 6.25rem) !important;
  line-height: .92 !important;
  background: linear-gradient(110deg, #ffffff 0%, #f1d7ff 34%, #b85cff 62%, #7dd7ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
  text-shadow: 0 0 48px rgba(184,92,255,.18);
  animation: heroFloat 7s var(--motion-ease) infinite alternate;
}
@keyframes heroFloat {
  from { transform: translate3d(0,0,0) rotateX(0deg); filter: drop-shadow(0 0 0 rgba(184,92,255,0)); }
  to { transform: translate3d(0,-8px,0) rotateX(2deg); filter: drop-shadow(0 18px 32px rgba(184,92,255,.12)); }
}

[data-testid="stMarkdownContainer"] p {
  text-wrap: pretty;
}

/* universal premium glass surfaces */
[data-testid="metric-container"],
[data-testid="stExpander"],
[data-testid="stDataFrame"],
[data-testid="stTable"],
.stAlert,
.info-box,
.result-card,
div[data-testid="stForm"],
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-stroke) !important;
  border-top-color: var(--glass-stroke-strong) !important;
  box-shadow: var(--card-depth) !important;
  backdrop-filter: blur(28px) saturate(150%) !important;
  -webkit-backdrop-filter: blur(28px) saturate(150%) !important;
  transform-style: preserve-3d;
}

[data-testid="metric-container"],
[data-testid="stExpander"],
[data-testid="stDataFrame"],
.info-box,
.result-card {
  transition:
    transform .55s var(--motion-ease),
    box-shadow .55s var(--motion-ease),
    border-color .55s var(--motion-ease),
    filter .55s var(--motion-ease) !important;
  will-change: transform, box-shadow;
}
[data-testid="metric-container"]:hover,
[data-testid="stExpander"]:hover,
[data-testid="stDataFrame"]:hover,
.info-box:hover,
.result-card:hover {
  transform: translate3d(0,-10px,42px) rotateX(2deg) rotateY(-1deg) !important;
  border-color: rgba(233,179,255,.36) !important;
  box-shadow: var(--card-depth-hover), 0 0 64px rgba(184,92,255,.13) !important;
  filter: saturate(1.08);
}

/* animated border sheen */
[data-testid="metric-container"]::before,
.info-box::before,
.result-card::before {
  height: 2px !important;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.55), rgba(184,92,255,.55), transparent) !important;
  transform: translateX(-120%);
  animation: borderSheen 5.5s ease-in-out infinite;
}
@keyframes borderSheen {
  0%, 42% { transform: translateX(-120%); opacity: 0; }
  52% { opacity: 1; }
  72%,100% { transform: translateX(120%); opacity: 0; }
}

/* buttons feel like buoyant 3D controls */
.stButton > button,
.stDownloadButton > button,
button[kind="primary"],
button[data-testid="baseButton-primary"] {
  position: relative !important;
  overflow: hidden !important;
  border-radius: 999px !important;
  border: 1px solid rgba(255,255,255,.20) !important;
  background:
    radial-gradient(circle at 30% 0%, rgba(255,255,255,.30), transparent 30%),
    linear-gradient(135deg, rgba(184,92,255,.95), rgba(255,124,182,.74)) !important;
  box-shadow: 0 16px 36px rgba(184,92,255,.26), inset 0 1px 0 rgba(255,255,255,.30) !important;
  transition: transform .32s var(--motion-ease), box-shadow .32s var(--motion-ease), filter .32s var(--motion-ease) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
  transform: translateY(-4px) scale(1.015) !important;
  box-shadow: 0 26px 55px rgba(184,92,255,.36), 0 0 48px rgba(255,124,182,.16), inset 0 1px 0 rgba(255,255,255,.34) !important;
  filter: brightness(1.08);
}
.stButton > button::after,
.stDownloadButton > button::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,.35) 45%, transparent 70%);
  transform: translateX(-120%);
  transition: transform .7s var(--motion-ease);
}
.stButton > button:hover::after,
.stDownloadButton > button:hover::after { transform: translateX(120%); }

/* tabs as pill navigation */
.stTabs [data-baseweb="tab-list"] {
  position: sticky;
  top: .75rem;
  z-index: 6;
  background: rgba(10,9,15,.58) !important;
  border-color: rgba(255,255,255,.14) !important;
  box-shadow: 0 18px 50px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.12) !important;
}
.stTabs [aria-selected="true"] {
  background:
    linear-gradient(135deg, rgba(255,255,255,.17), rgba(184,92,255,.20)) !important;
  color: #fff !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.24), 0 8px 24px rgba(184,92,255,.16) !important;
}

/* sidebar depth */
[data-testid="stSidebar"] {
  background:
    radial-gradient(circle at 20% 0%, rgba(184,92,255,.20), transparent 34%),
    rgba(7,7,12,.72) !important;
}
.sidebar-brand {
  filter: drop-shadow(0 12px 24px rgba(184,92,255,.18));
}

/* dataframes/table polish */
[data-testid="stDataFrame"] {
  border-radius: 24px !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] div {
  scrollbar-width: thin;
}

/* scroll-driven reveal, CSS-only with graceful fallback */
@supports (animation-timeline: view()) {
  [data-testid="metric-container"],
  [data-testid="stExpander"],
  [data-testid="stDataFrame"],
  .info-box,
  .result-card,
  iframe,
  h1, h2, h3 {
    animation: reveal3d both;
    animation-timeline: view();
    animation-range: entry 0% cover 28%;
  }
  @keyframes reveal3d {
    from {
      opacity: 0;
      transform: translate3d(0, 36px, -80px) rotateX(8deg);
      filter: blur(10px);
    }
    to {
      opacity: 1;
      transform: translate3d(0, 0, 0) rotateX(0);
      filter: blur(0);
    }
  }
}

/* accessibility: reduce motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .001ms !important;
    scroll-behavior: auto !important;
  }
}

</style>

<script>
/* ── SCROLL-REVEAL ENGINE ──────────────────────────────────── */
(function() {
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        e.target.style.opacity = "1";
        e.target.style.transform = "translateY(0)";
        io.unobserve(e.target);
      }
    });
  },{ threshold:0.06, rootMargin:"0px 0px -30px 0px" });

  function attach(){
    var els = document.querySelectorAll(
      "[data-testid='metric-container'], [data-testid='stDataFrame'], " +
      "[data-testid='stExpander'], .element-container"
    );
    els.forEach(function(el, i){
      if(!el.dataset.sr){
        el.dataset.sr = "1";
        el.style.opacity = "0";
        el.style.transform = "translateY(28px)";
        el.style.transition = "opacity .6s cubic-bezier(.22,1,.36,1) " + (i%5)*0.06 + "s, transform .6s cubic-bezier(.22,1,.36,1) " + (i%5)*0.06 + "s";
        io.observe(el);
      }
    });
  }
  setTimeout(attach, 200);
  new MutationObserver(function(){ setTimeout(attach, 100); })
    .observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SVG CHART RENDERER HELPERS
#  Each function receives already-computed Python data and
#  returns an st.components.v1.html call with a self-contained
#  glass-panel SVG chart.  No matplotlib anywhere.
# ─────────────────────────────────────────────────────────────

CHART_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Mono:wght@400;500&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: transparent;
    font-family: 'Space Grotesk', sans-serif;
    overflow: hidden;
  }
  .card {
    background: linear-gradient(145deg, rgba(34,30,48,.96) 0%, rgba(16,14,24,.94) 100%);
    border: 1px solid rgba(255,255,255,.12);
    border-top: 1px solid rgba(255,255,255,.20);
    border-radius: 20px;
    padding: 22px 24px 18px;
    box-shadow: 0 16px 48px rgba(0,0,0,.70), 0 4px 16px rgba(0,0,0,.55),
                0 0 0 1px rgba(255,255,255,.06),
                0 -1px 0 rgba(255,255,255,.06) inset;
    position: relative;
    overflow: hidden;
    transition: transform .4s cubic-bezier(.22,1,.36,1), box-shadow .4s ease;
    cursor: default;
  }
  .card:hover {
    transform: translateY(-6px);
    box-shadow: 0 24px 64px rgba(0,0,0,.75), 0 8px 24px rgba(233,179,255,.10),
                0 0 0 1px rgba(255,255,255,.09),
                0 0 60px rgba(233,179,255,.08);
  }
  .card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.30), transparent);
    pointer-events: none;
  }
  .card::after {
    content: "";
    position: absolute; top: -60px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(233,179,255,.07) 0%, transparent 70%);
    pointer-events: none;
  }
  .chart-title {
    font-size: 13px; font-weight: 600; color: #e5e1e4;
    letter-spacing: -.01em; margin-bottom: 14px;
  }
  svg { display: block; }
  .axis-label { font-size: 9px; fill: #9b8c9e; font-family: 'Space Grotesk', sans-serif; }
  .value-label { font-size: 9.5px; fill: #c4bfc6; font-weight: 700; font-family: 'DM Mono', monospace; }
  .grid-line { stroke: rgba(255,255,255,.045); stroke-width: .8; stroke-dasharray: 5,4; }
  .bar-rect { transition: opacity .2s; cursor: pointer; }
  .bar-rect:hover { opacity: .82; filter: brightness(1.15); }

  /* bar entrance animation */
  @keyframes barGrow {
    from { transform: scaleY(0); transform-origin: bottom; }
    to   { transform: scaleY(1); transform-origin: bottom; }
  }
  @keyframes barGrowH {
    from { transform: scaleX(0); transform-origin: left; }
    to   { transform: scaleX(1); transform-origin: left; }
  }
  @keyframes fadeIn { from{opacity:0} to{opacity:1} }
  .bar-anim { animation: barGrow .65s cubic-bezier(.22,1,.36,1) both; }
  .bar-anim-h { animation: barGrowH .65s cubic-bezier(.22,1,.36,1) both; }
  .fade-in { animation: fadeIn .50s ease both; }

  /* pie slice pulse on hover */
  .pie-slice { transition: opacity .2s, filter .2s; cursor: pointer; }
  .pie-slice:hover { opacity: .85; filter: brightness(1.18) drop-shadow(0 0 8px currentColor); }

  /* Premium SVG chart depth / motion upgrade */
  body::before {
    content:"";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 22% 10%, rgba(233,179,255,.10), transparent 34%),
      radial-gradient(circle at 88% 82%, rgba(100,210,255,.06), transparent 30%);
    opacity: .9;
  }
  .card {
    transform-style: preserve-3d;
    backdrop-filter: blur(30px) saturate(155%);
    -webkit-backdrop-filter: blur(30px) saturate(155%);
    background:
      radial-gradient(circle at 18% 0%, rgba(255,255,255,.12), transparent 28%),
      linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.035) 48%, rgba(184,92,255,.065)) !important;
    border-color: rgba(255,255,255,.16) !important;
  }
  .card:hover {
    transform: translateY(-8px) rotateX(2deg) rotateY(-1deg);
    border-color: rgba(233,179,255,.34) !important;
  }
  .card::before {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.55), rgba(233,179,255,.62), transparent);
    animation: chartSheen 5s ease-in-out infinite;
  }
  @keyframes chartSheen {
    0%, 42% { transform: translateX(-120%); opacity: 0; }
    55% { opacity: 1; }
    78%, 100% { transform: translateX(120%); opacity: 0; }
  }
  .chart-title {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -.025em;
  }
  .chart-title::before {
    content:"";
    width: 8px; height: 8px; border-radius: 999px;
    background: #e9b3ff;
    box-shadow: 0 0 18px rgba(233,179,255,.75);
  }
  .bar-rect, .pie-slice {
    transition: opacity .24s ease, filter .24s ease, transform .24s cubic-bezier(.19,1,.22,1);
    transform-box: fill-box;
    transform-origin: center;
  }
  .bar-rect:hover {
    opacity: .94;
    filter: brightness(1.22) drop-shadow(0 0 16px currentColor);
    transform: translateY(-2px);
  }
  .pie-slice:hover {
    opacity: .95;
    transform: scale(1.025);
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: .001ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: .001ms !important;
    }
  }
</style>
"""

def _fmt_money(v):
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def _grid_lines(ax_x, ax_y, w, h, n=5):
    """Return SVG horizontal grid line strings."""
    lines = []
    for i in range(1, n + 1):
        y = ax_y + h - (h * i / n)
        lines.append(f'<line class="grid-line" x1="{ax_x}" y1="{y:.1f}" x2="{ax_x+w}" y2="{y:.1f}"/>')
    return "\n".join(lines)

def _grid_lines_v(ax_x, ax_y, w, h, n=4):
    """Return SVG vertical grid line strings (for horizontal bar charts)."""
    lines = []
    for i in range(1, n + 1):
        x = ax_x + (w * i / n)
        lines.append(f'<line class="grid-line" x1="{x:.1f}" y1="{ax_y}" x2="{x:.1f}" y2="{ax_y+h}"/>')
    return "\n".join(lines)


def render_vbar_chart(title, labels, values, colors, height=340,
                      fmt_fn=None, y_label="", uid="chart"):
    """Vertical bar chart — pure SVG inside a glass card."""
    if fmt_fn is None:
        fmt_fn = lambda v: f"{v:,.0f}"
    n = len(labels)
    W, H = 560, height
    pad_l, pad_r, pad_t, pad_b = 54, 20, 28, 44
    ax_w = W - pad_l - pad_r
    ax_h = H - pad_t - pad_b
    bar_w = ax_w / n * 0.52
    bar_gap = ax_w / n

    vmax = max(abs(v) for v in values) if values else 1
    vmin = min(values) if values else 0
    has_neg = vmin < 0

    def to_y(v):
        if has_neg:
            total = vmax - vmin
            return pad_t + ax_h - ((v - vmin) / total) * ax_h
        else:
            return pad_t + ax_h - (v / vmax) * ax_h

    zero_y = to_y(0) if has_neg else pad_t + ax_h

    bars_svg = []
    labels_svg = []
    val_labels = []

    for i, (lbl, v, col) in enumerate(zip(labels, values, colors)):
        cx = pad_l + bar_gap * i + bar_gap / 2
        bx = cx - bar_w / 2
        by = to_y(v)
        bh = abs(zero_y - by)
        delay = i * 0.08

        # gradient def id
        gid = f"{uid}_g{i}"
        bars_svg.append(f"""
<defs>
  <linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{col}" stop-opacity=".95"/>
    <stop offset="100%" stop-color="{col}" stop-opacity=".55"/>
  </linearGradient>
</defs>
<rect class="bar-rect bar-anim" rx="5" ry="5"
  x="{bx:.1f}" y="{min(by, zero_y):.1f}" width="{bar_w:.1f}" height="{bh:.1f}"
  fill="url(#{gid})"
  style="filter:drop-shadow(0 4px 12px {col}44);animation-delay:{delay:.2f}s"/>""")

        # x-axis label
        labels_svg.append(
            f'<text class="axis-label" x="{cx:.1f}" y="{pad_t+ax_h+18}" text-anchor="middle">{lbl}</text>'
        )
        # value label above bar
        label_y = min(by, zero_y) - 6
        if label_y < pad_t + 6:
            label_y = min(by, zero_y) + bh + 14
        val_labels.append(
            f'<text class="value-label fade-in" x="{cx:.1f}" y="{label_y:.1f}" text-anchor="middle"'
            f' style="animation-delay:{delay+0.3:.2f}s">{fmt_fn(v)}</text>'
        )

    # y-axis tick labels
    y_ticks = []
    for i in range(6):
        val = vmin + (vmax - vmin) * i / 5 if has_neg else vmax * i / 5
        y = to_y(val)
        y_ticks.append(
            f'<text class="axis-label" x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end">{fmt_fn(val)}</text>'
        )

    html = f"""<!DOCTYPE html><html><head>{CHART_CSS}</head><body>
<div class="card">
  <div class="chart-title">{title}</div>
  <svg viewBox="0 0 {W} {H}" width="100%" style="max-height:{H}px">
    <!-- grid -->
    {_grid_lines(pad_l, pad_t, ax_w, ax_h)}
    <!-- zero line -->
    <line x1="{pad_l}" y1="{zero_y:.1f}" x2="{pad_l+ax_w}" y2="{zero_y:.1f}"
          stroke="rgba(255,255,255,.18)" stroke-width="1"/>
    <!-- bars -->
    {''.join(bars_svg)}
    <!-- axis labels -->
    {''.join(labels_svg)}
    {''.join(val_labels)}
    {''.join(y_ticks)}
    <!-- y-axis label -->
    <text class="axis-label" x="12" y="{pad_t + ax_h//2}" text-anchor="middle"
          transform="rotate(-90,12,{pad_t + ax_h//2})">{y_label}</text>
  </svg>
</div>
</body></html>"""
    return html


def render_hbar_chart(title, labels, values, colors, height=None, fmt_fn=None, x_label="", uid="hchart"):
    """Horizontal bar chart — pure SVG inside a glass card."""
    if fmt_fn is None:
        fmt_fn = _fmt_money
    n = len(labels)
    W = 560
    H = height or max(260, 42 * n + 80)
    pad_l, pad_r, pad_t, pad_b = 110, 80, 28, 32
    ax_w = W - pad_l - pad_r
    ax_h = H - pad_t - pad_b
    bar_h = ax_h / n * 0.58
    bar_gap = ax_h / n

    vmax = max(values) if values else 1

    bars_svg = []
    for i, (lbl, v, col) in enumerate(zip(labels, values, colors)):
        cy = pad_t + bar_gap * i + bar_gap / 2
        by = cy - bar_h / 2
        bw = (v / vmax) * ax_w
        delay = i * 0.07
        gid = f"{uid}_g{i}"

        bars_svg.append(f"""
<defs>
  <linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{col}" stop-opacity=".90"/>
    <stop offset="100%" stop-color="{col}" stop-opacity=".50"/>
  </linearGradient>
</defs>
<rect class="bar-rect bar-anim-h" rx="4" ry="4"
  x="{pad_l}" y="{by:.1f}" width="{bw:.1f}" height="{bar_h:.1f}"
  fill="url(#{gid})"
  style="filter:drop-shadow(0 3px 10px {col}44);animation-delay:{delay:.2f}s"/>
<text class="axis-label" x="{pad_l-8}" y="{cy+3.5:.1f}" text-anchor="end" font-size="9">{lbl}</text>
<text class="value-label fade-in" x="{pad_l+bw+6:.1f}" y="{cy+3.5:.1f}"
  style="animation-delay:{delay+0.25:.2f}s">{fmt_fn(v)}</text>""")

    html = f"""<!DOCTYPE html><html><head>{CHART_CSS}</head><body>
<div class="card">
  <div class="chart-title">{title}</div>
  <svg viewBox="0 0 {W} {H}" width="100%" style="max-height:{H}px">
    {_grid_lines_v(pad_l, pad_t, ax_w, ax_h)}
    <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+ax_h}"
          stroke="rgba(255,255,255,.18)" stroke-width="1"/>
    {''.join(bars_svg)}
    <text class="axis-label" x="{pad_l + ax_w//2}" y="{H-6}" text-anchor="middle">{x_label}</text>
  </svg>
</div>
</body></html>"""
    return html


def render_pie_chart(title, labels, values, colors, height=320, uid="pie"):
    """Donut / pie chart — pure SVG inside a glass card."""
    total = sum(values)
    if total == 0:
        return ""
    W, H = 480, height
    cx, cy, r_outer, r_inner = W // 2, H // 2 - 10, min(W, H) // 2 - 50, 55

    slices = []
    legend = []
    angle = -90.0  # start at top

    for i, (lbl, v, col) in enumerate(zip(labels, values, colors)):
        frac = v / total
        sweep = frac * 360
        start_rad = angle * 3.14159265 / 180
        end_rad = (angle + sweep) * 3.14159265 / 180

        x1 = cx + r_outer * __import__('math').cos(start_rad)
        y1 = cy + r_outer * __import__('math').sin(start_rad)
        x2 = cx + r_outer * __import__('math').cos(end_rad)
        y2 = cy + r_outer * __import__('math').sin(end_rad)
        xi1 = cx + r_inner * __import__('math').cos(end_rad)
        yi1 = cy + r_inner * __import__('math').sin(end_rad)
        xi2 = cx + r_inner * __import__('math').cos(start_rad)
        yi2 = cy + r_inner * __import__('math').sin(start_rad)
        large = 1 if sweep > 180 else 0

        # label position
        mid_rad = (angle + sweep / 2) * 3.14159265 / 180
        lx = cx + (r_outer * 0.72) * __import__('math').cos(mid_rad)
        ly = cy + (r_outer * 0.72) * __import__('math').sin(mid_rad)

        d = (f"M {x1:.2f} {y1:.2f} "
             f"A {r_outer} {r_outer} 0 {large} 1 {x2:.2f} {y2:.2f} "
             f"L {xi1:.2f} {yi1:.2f} "
             f"A {r_inner} {r_inner} 0 {large} 0 {xi2:.2f} {yi2:.2f} Z")

        delay = i * 0.10
        gid = f"{uid}_pg{i}"
        slices.append(f"""
<defs>
  <radialGradient id="{gid}" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{col}" stop-opacity=".95"/>
    <stop offset="100%" stop-color="{col}" stop-opacity=".65"/>
  </radialGradient>
</defs>
<path class="pie-slice fade-in" d="{d}" fill="url(#{gid})"
  stroke="rgba(11,11,13,1)" stroke-width="2.5"
  style="filter:drop-shadow(0 4px 14px {col}55);animation-delay:{delay:.2f}s">
  <title>{lbl}: {frac:.1%}</title>
</path>
<text class="value-label fade-in" x="{lx:.1f}" y="{ly+4:.1f}"
  text-anchor="middle" font-size="10"
  style="animation-delay:{delay+0.25:.2f}s">{frac:.0%}</text>""")

        # legend row
        lrow_y = H - 60 + i * 0 + 0  # will compute below
        legend.append((col, lbl, frac))
        angle += sweep

    # legend below chart
    legend_svg = []
    lx0 = 20
    ly0 = H - 36
    for i, (col, lbl, frac) in enumerate(legend):
        ox = lx0 + i * (W // len(legend))
        legend_svg.append(
            f'<rect x="{ox}" y="{ly0}" width="10" height="10" rx="3" fill="{col}" opacity=".85"/>'
            f'<text class="axis-label" x="{ox+14}" y="{ly0+9}">{lbl} {frac:.1%}</text>'
        )

    html = f"""<!DOCTYPE html><html><head>{CHART_CSS}</head><body>
<div class="card">
  <div class="chart-title">{title}</div>
  <svg viewBox="0 0 {W} {H}" width="100%" style="max-height:{H}px">
    {''.join(slices)}
    {''.join(legend_svg)}
  </svg>
</div>
</body></html>"""
    return html


def render_grouped_bar_chart(title, group_labels, series, colors, height=300, uid="grp"):
    """Grouped bar chart for model comparison."""
    n_groups = len(group_labels)
    n_series = len(series)
    W, H = 640, height
    pad_l, pad_r, pad_t, pad_b = 50, 20, 36, 56
    ax_w = W - pad_l - pad_r
    ax_h = H - pad_t - pad_b
    group_w = ax_w / n_groups
    bar_w = group_w * 0.35
    bar_offsets = [-(n_series - 1) * bar_w / 2 + i * bar_w for i in range(n_series)]

    all_vals = [v for s in series for v in s["values"]]
    vmax = max(all_vals) * 1.15

    def to_y(v):
        return pad_t + ax_h - (v / vmax) * ax_h

    bars_svg = []
    legend_svg = []

    for si, s in enumerate(series):
        col = colors[si]
        gid_base = f"{uid}_s{si}"
        for gi, (lbl, v) in enumerate(zip(group_labels, s["values"])):
            cx = pad_l + group_w * gi + group_w / 2 + bar_offsets[si]
            by = to_y(v)
            bh = pad_t + ax_h - by
            delay = (gi * n_series + si) * 0.06
            gid = f"{gid_base}g{gi}"
            bars_svg.append(f"""
<defs>
  <linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{col}" stop-opacity=".95"/>
    <stop offset="100%" stop-color="{col}" stop-opacity=".50"/>
  </linearGradient>
</defs>
<rect class="bar-rect bar-anim" rx="4"
  x="{cx - bar_w/2:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}"
  fill="url(#{gid})" style="filter:drop-shadow(0 3px 10px {col}44);animation-delay:{delay:.2f}s"/>
<text class="value-label fade-in" x="{cx:.1f}" y="{by-5:.1f}" text-anchor="middle" font-size="8.5"
  style="animation-delay:{delay+0.25:.2f}s">{v:.0%}</text>""")

        # legend
        lx = pad_l + si * 110
        legend_svg.append(
            f'<rect x="{lx}" y="{H-20}" width="10" height="10" rx="3" fill="{col}" opacity=".85"/>'
            f'<text class="axis-label" x="{lx+14}" y="{H-11}">{s["label"]}</text>'
        )

    # x-axis group labels
    x_labels = []
    for gi, lbl in enumerate(group_labels):
        cx = pad_l + group_w * gi + group_w / 2
        # wrap long labels
        words = lbl.split()
        if len(words) > 2:
            line1 = " ".join(words[:2])
            line2 = " ".join(words[2:])
            x_labels.append(
                f'<text class="axis-label" x="{cx:.1f}" y="{pad_t+ax_h+14}" text-anchor="middle">{line1}</text>'
                f'<text class="axis-label" x="{cx:.1f}" y="{pad_t+ax_h+25}" text-anchor="middle">{line2}</text>'
            )
        else:
            x_labels.append(
                f'<text class="axis-label" x="{cx:.1f}" y="{pad_t+ax_h+14}" text-anchor="middle">{lbl}</text>'
            )

    y_ticks = []
    for i in range(6):
        val = vmax * i / 5
        y = to_y(val)
        y_ticks.append(
            f'<text class="axis-label" x="{pad_l-8}" y="{y+3:.1f}" text-anchor="end">{val:.0%}</text>'
        )

    html = f"""<!DOCTYPE html><html><head>{CHART_CSS}</head><body>
<div class="card">
  <div class="chart-title">{title}</div>
  <svg viewBox="0 0 {W} {H}" width="100%" style="max-height:{H}px">
    {_grid_lines(pad_l, pad_t, ax_w, ax_h)}
    <line x1="{pad_l}" y1="{pad_t+ax_h}" x2="{pad_l+ax_w}" y2="{pad_t+ax_h}"
          stroke="rgba(255,255,255,.18)" stroke-width="1"/>
    {''.join(bars_svg)}
    {''.join(x_labels)}
    {''.join(y_ticks)}
    {''.join(legend_svg)}
  </svg>
</div>
</body></html>"""
    return html


def svg_chart(html_str, height):
    """Render the chart HTML in a transparent iframe."""
    components.html(html_str, height=height, scrolling=False)


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
    st.markdown('<div class="sidebar-brand">Sky<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:.74rem;color:#9b8c9e;margin-bottom:18px;font-weight:600;"
        "letter-spacing:.06em;text-transform:uppercase'>Filter view</p>",
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
    <p style='font-size:.70rem;color:#9b8c9e;font-weight:700;letter-spacing:.12em;
    text-transform:uppercase;margin-bottom:12px'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:.82rem;color:#c4bfc6'>
      <div><span class='pill pill-expand'>Expand</span>&nbsp;&nbsp;High profit &amp; demand</div>
      <div><span class='pill pill-maintain'>Maintain</span>&nbsp;&nbsp;Stable performer</div>
      <div><span class='pill pill-optimize'>Optimize</span>&nbsp;&nbsp;Room to improve</div>
      <div><span class='pill pill-drop'>Drop</span>&nbsp;&nbsp;Losing money</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FILTERING
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
  <p>Built on a sample airline dataset for analysis and demonstration purposes only.
     Does not reflect real-time airline operations or current flight decisions.</p>
  <div class="hero-glyph">&#9992;</div>
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
    avg_profit = fdf["Profit"].mean() if n else 0
    avg_load   = fdf["Load_Factor"].mean() if n else 0
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
    st.markdown('<div class="divider-label">Composition</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<p class="section-hd">Decision mix</p>', unsafe_allow_html=True)
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        pie_labels = dc.index.tolist()
        pie_values = dc.values.tolist()
        pie_colors = [DECISION_COLORS.get(l, "#888") for l in pie_labels]
        svg_chart(render_pie_chart("Share of Flights by Decision",
                                   pie_labels, pie_values, pie_colors, height=300, uid="pie1"), 330)

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
        <div class="info-box" style="margin-top:16px">
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
        svg_chart(render_vbar_chart(
            "Average Profit by Decision",
            apd.index.tolist(), apd.values.tolist(),
            [DECISION_COLORS.get(l, "#888") for l in apd.index],
            height=320, fmt_fn=_fmt_money, y_label="Avg Profit ($)", uid="tab2_profit"
        ), 360)

    with right:
        ald = (
            fdf.groupby("Route_Decision")["Load_Factor"].mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .dropna()
        )
        svg_chart(render_vbar_chart(
            "Seat Occupancy by Decision",
            ald.index.tolist(), ald.values.tolist(),
            [DECISION_COLORS.get(l, "#888") for l in ald.index],
            height=320, fmt_fn=lambda v: f"{v:.0%}", y_label="Avg Load Factor", uid="tab2_load"
        ), 360)

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
        "Fuel_Cost":"Fuel","Maintenance_Cost":"Maintenance","Crew_Cost":"Crew",
        "Depreciation_Cost":"Depreciation","Insurance_Cost":"Insurance",
        "Airport_Fees":"Airport Fees","Catering_Cost":"Catering","Handling_Cost":"Handling",
        "Navigation_Fees":"Navigation","Sales_Distribution_Cost":"Sales & Dist.",
        "Passenger_Service_Cost":"Pax Service","Overhead_Cost":"Overhead",
        "Marketing_Cost":"Marketing","IT_Systems_Cost":"IT Systems",
    }
    cost_labels = [label_map.get(i, i) for i in cost_means.index]
    cost_values = cost_means.values.tolist()
    cost_colors = C_NEUTRAL[:len(cost_labels)]

    svg_chart(render_hbar_chart(
        "Top Cost Drivers",
        cost_labels, cost_values, cost_colors,
        height=max(280, 42 * len(cost_labels) + 80),
        fmt_fn=_fmt_money, x_label="Average Cost per Flight ($)", uid="tab2_costs"
    ), max(320, 42 * len(cost_labels) + 120))

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>"
        "Top routes currently classified as Expand</p>", unsafe_allow_html=True,
    )
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route", "Profit", "Profit_Margin", "Load_Factor"]]
        .head(10)
        .rename(columns={"Profit":"Avg Profit ($)","Profit_Margin":"Profit Margin","Load_Factor":"Load Factor"})
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        svg_chart(render_hbar_chart(
            "Top 10 Routes",
            top.index.tolist(), top.values.tolist(),
            [C_EXPAND] * len(top),
            height=max(260, 42 * len(top) + 80),
            fmt_fn=_fmt_money, x_label="Total Profit ($)", uid="tab3_top"
        ), max(300, 42 * len(top) + 120))

    with right:
        st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        worst_abs = worst.abs()
        svg_chart(render_hbar_chart(
            "Bottom 10 Routes",
            worst.index.tolist(), worst_abs.values.tolist(),
            [C_DROP] * len(worst),
            height=max(260, 42 * len(worst) + 80),
            fmt_fn=lambda v: f"−{_fmt_money(v)}", x_label="Loss Magnitude ($)", uid="tab3_bot"
        ), max(300, 42 * len(worst) + 120))

# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>How many unique routes appear in each category?</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route": "Unique Routes"})
        .set_index("Route_Decision")
        .reindex(ORDER).dropna()
    )
    svg_chart(render_vbar_chart(
        "Unique Routes per Decision Category",
        urbd.index.tolist(),
        urbd["Unique Routes"].tolist(),
        [DECISION_COLORS.get(d, "#888") for d in urbd.index],
        height=300, fmt_fn=lambda v: str(int(v)),
        y_label="Unique Routes", uid="tab4_urbd"
    ), 340)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>How accurate are the models?</p>", unsafe_allow_html=True)

    svg_chart(render_grouped_bar_chart(
        "Model Accuracy & F1 Comparison",
        comparison["Model"].tolist(),
        [
            {"label": "Accuracy", "values": comparison["Accuracy"].tolist()},
            {"label": "Macro F1", "values": comparison["Macro F1"].tolist()},
        ],
        [C_NEUTRAL[0], C_NEUTRAL[2]],
        height=280, uid="tab5_models"
    ), 320)

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

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<p style='font-size:.74rem;font-weight:700;color:#9b8c9e;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px'>Flight basics</p>", unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown("<p style='font-size:.74rem;font-weight:700;color:#9b8c9e;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px'>Route context</p>", unsafe_allow_html=True)
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown("<p style='font-size:.74rem;font-weight:700;color:#9b8c9e;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px'>Revenue</p>", unsafe_allow_html=True)
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown("<p style='font-size:.74rem;font-weight:700;color:#9b8c9e;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px'>Cost breakdown</p>", unsafe_allow_html=True)
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

    # ── PREDICTION LOGIC ─────────────────────────────────────
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

    # ── RESULT DISPLAY ────────────────────────────────────────
    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]
        prob = res["probabilities"]
        cls  = res["classes"]

        pill_cls   = {"Expand":"pill-expand","Maintain":"pill-maintain","Optimize":"pill-optimize","Drop":"pill-drop"}
        result_cls = {"Expand":"result-expand","Maintain":"result-maintain","Optimize":"result-optimize","Drop":"result-drop"}
        text_col   = {"Expand":C_EXPAND,"Maintain":C_MAINTAIN,"Optimize":C_OPTIMIZE,"Drop":C_DROP}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred, "result-expand")}'>
          <div style='margin-bottom:12px'>
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Space Grotesk",sans-serif;font-size:1.80rem;font-weight:700;
                      color:{text_col.get(pred, "#e5e1e4")};margin-bottom:12px;letter-spacing:-.025em'>
            Suggested Decision: {pred}
          </div>
          <p style='color:#c4bfc6;margin:0;font-size:.92rem;line-height:1.75;font-family:"Manrope",sans-serif'>
            {explanations.get(pred, "")}
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size:.80rem;font-weight:700;color:#e5e1e4;margin-bottom:8px'>Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (
            pd.DataFrame({"Decision": cls, "Probability": prob})
            .sort_values("Probability", ascending=False)
        )
        svg_chart(render_vbar_chart(
            "Model Confidence per Decision",
            prob_df["Decision"].tolist(),
            prob_df["Probability"].tolist(),
            [DECISION_COLORS.get(d, "#888") for d in prob_df["Decision"]],
            height=280, fmt_fn=lambda v: f"{v:.0%}", y_label="Probability", uid="tab5_conf"
        ), 320)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True, hide_index=True,
        )

# ─────────────────────────────────────────────────────────────
#  FILTERED DATA EXPANDER
# ─────────────────────────────────────────────────────────────
with st.expander("Show filtered data"):
    st.dataframe(fdf, use_container_width=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#4f4352;font-size:.74rem;
            padding:48px 0 20px;font-family:"Manrope",sans-serif;
            letter-spacing:.08em;text-transform:uppercase'>
  SkyLens Route Intelligence &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)