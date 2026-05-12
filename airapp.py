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
#  COLOUR TOKENS  (chart palette — unchanged logic)
# ─────────────────────────────────────────────────────────────
CHART_EXPAND   = "#34C759"
CHART_MAINTAIN = "#FFD60A"
CHART_OPTIMIZE = "#FF6B35"
CHART_DROP     = "#FF375F"
CHART_ORANGE   = "#FF6B35"
CHART_NEUTRAL  = ["#6E9FDC","#9AC8CD","#B5CDA3","#E8C47A","#E8A97A","#E88A9A","#C4B8E8","#A8D8CF"]

COLOR_GREEN    = "#34C759"
COLOR_YELLOW   = "#FFD60A"
COLOR_ORANGE   = "#FF6B35"
COLOR_PINK     = "#FF375F"

# ─────────────────────────────────────────────────────────────
#  AURORA GLASSMORPHISM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── KEYFRAMES ──────────────────────────────────────────────── */
@keyframes aurora1 {
  0%   { transform: translate(0%, 0%)    scale(1);    opacity: 0.55; }
  33%  { transform: translate(8%, -12%)  scale(1.08); opacity: 0.65; }
  66%  { transform: translate(-6%, 10%)  scale(0.95); opacity: 0.50; }
  100% { transform: translate(0%, 0%)    scale(1);    opacity: 0.55; }
}
@keyframes aurora2 {
  0%   { transform: translate(0%, 0%)    scale(1);    opacity: 0.45; }
  40%  { transform: translate(-10%, 8%)  scale(1.12); opacity: 0.60; }
  70%  { transform: translate(7%, -6%)   scale(0.92); opacity: 0.40; }
  100% { transform: translate(0%, 0%)    scale(1);    opacity: 0.45; }
}
@keyframes aurora3 {
  0%   { transform: translate(0%, 0%)    scale(1);    opacity: 0.35; }
  50%  { transform: translate(5%, 14%)   scale(1.06); opacity: 0.50; }
  80%  { transform: translate(-8%, -4%)  scale(0.98); opacity: 0.30; }
  100% { transform: translate(0%, 0%)    scale(1);    opacity: 0.35; }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(99,179,237,0.18), 0 8px 32px rgba(0,0,0,0.45); }
  50%       { box-shadow: 0 0 40px rgba(99,179,237,0.32), 0 8px 32px rgba(0,0,0,0.45); }
}
@keyframes planeFloat {
  0%, 100% { transform: translateY(0px) rotate(-2deg); }
  50%       { transform: translateY(-8px) rotate(2deg); }
}
@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* ── ROOT ───────────────────────────────────────────────────── */
:root {
  --sky-deep:     #050d1a;
  --sky-mid:      #091628;
  --glass-bg:     rgba(12, 28, 52, 0.55);
  --glass-border: rgba(120, 180, 255, 0.18);
  --glass-hover:  rgba(12, 28, 52, 0.75);
  --aurora-teal:  #00c9a7;
  --aurora-blue:  #4fc3f7;
  --aurora-violet:#a78bfa;
  --aurora-green: #34d399;
  --ink:          rgba(255,255,255,0.92);
  --ink-soft:     rgba(255,255,255,0.65);
  --ink-muted:    rgba(255,255,255,0.38);
  --accent:       #63b3ed;
  --green:        #34C759;
  --yellow:       #FFD60A;
  --orange:       #FF6B35;
  --pink:         #FF375F;
  --radius-sm:    10px;
  --radius-md:    16px;
  --radius-lg:    24px;
  --radius-xl:    32px;
  --blur:         blur(18px) saturate(180%);
  --shadow-glass: 0 8px 32px rgba(0,0,0,0.50), inset 0 1px 0 rgba(255,255,255,0.08);
}

/* ── DEEP SKY BACKGROUND ────────────────────────────────────── */
html, body, .stApp {
  background: var(--sky-deep) !important;
  font-family: 'Outfit', system-ui, sans-serif !important;
  color: var(--ink) !important;
}

/* Aurora blob divs injected via st.markdown */
.aurora-blob {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  mix-blend-mode: screen;
}
.aurora-blob-1 {
  width: 70vw; height: 55vw;
  top: -15%; left: -20%;
  background: radial-gradient(ellipse,
    rgba(0,180,160,0.42) 0%,
    rgba(78,166,255,0.28) 40%,
    transparent 70%);
  filter: blur(90px);
  animation: aurora1 22s ease-in-out infinite;
}
.aurora-blob-2 {
  width: 60vw; height: 50vw;
  bottom: -10%; right: -15%;
  background: radial-gradient(ellipse,
    rgba(139,92,246,0.38) 0%,
    rgba(52,211,153,0.22) 40%,
    transparent 70%);
  filter: blur(90px);
  animation: aurora2 28s ease-in-out infinite;
}
.aurora-blob-3 {
  width: 40vw; height: 40vw;
  top: 40%; left: 35%;
  background: radial-gradient(ellipse,
    rgba(78,166,255,0.22) 0%,
    rgba(0,200,180,0.15) 50%,
    transparent 70%);
  filter: blur(100px);
  animation: aurora3 34s ease-in-out infinite;
}

/* ── CONTENT LAYERING ───────────────────────────────────────── */
.main .block-container {
  position: relative;
  z-index: 1;
  padding-top: 2rem;
  padding-bottom: 4rem;
  max-width: 1320px;
}

/* ── SIDEBAR ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(5, 15, 32, 0.82) !important;
  border-right: 1px solid var(--glass-border) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {
  color: var(--ink-soft) !important;
  font-family: 'Outfit', sans-serif !important;
}

/* ── GLASS CARD BASE ────────────────────────────────────────── */
.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-glass);
  padding: 24px 28px;
  margin-bottom: 16px;
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  animation: fadeUp 0.5s ease both;
}
.glass-card:hover {
  transform: translateY(-3px);
  background: var(--glass-hover);
  box-shadow: 0 16px 48px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.12);
}

/* ── METRIC CARDS ───────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
  box-shadow: var(--shadow-glass) !important;
  padding: 20px 24px !important;
  transition: transform 0.22s ease, box-shadow 0.22s ease !important;
  animation: fadeUp 0.45s ease both;
}
[data-testid="metric-container"]:hover {
  transform: translateY(-3px) !important;
  animation: pulseGlow 2.5s ease infinite !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
  font-size: 0.62rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--ink-muted) !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.70rem !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em !important;
}

/* ── TABS ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(5,15,32,0.70);
  border-radius: var(--radius-md);
  padding: 4px;
  gap: 2px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-glass);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--radius-sm);
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600;
  font-size: 0.80rem;
  color: var(--ink-muted) !important;
  padding: 8px 18px;
  background: transparent;
  border: none !important;
  transition: all 0.18s ease;
  letter-spacing: 0.02em;
}
.stTabs [data-baseweb="tab"]:hover {
  background: rgba(255,255,255,0.06) !important;
  color: var(--ink-soft) !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(99,179,237,0.25), rgba(0,201,167,0.20)) !important;
  color: var(--ink) !important;
  border: 1px solid rgba(99,179,237,0.35) !important;
  box-shadow: 0 2px 12px rgba(99,179,237,0.20) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent;
  padding-top: 1.5rem;
}

/* ── HEADINGS ───────────────────────────────────────────────── */
h1, h2, h3, h4 {
  font-family: 'Outfit', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
  font-weight: 700 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {
  color: var(--ink-soft);
  line-height: 1.65;
  font-size: 0.90rem;
}

/* ── WIDGET LABELS ──────────────────────────────────────────── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {
  color: var(--ink-soft) !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
}

/* ── INPUTS ─────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] div,
.stTextInput input,
.stNumberInput input {
  color: var(--ink) !important;
  background: rgba(10,24,48,0.80) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.88rem !important;
  box-shadow: none !important;
  transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stSelectbox [data-baseweb="select"] div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(99,179,237,0.18) !important;
}

/* ── SLIDER ─────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] [role="slider"] {
  background: var(--aurora-blue) !important;
  box-shadow: 0 0 10px rgba(79,195,247,0.60) !important;
}

/* ── DATAFRAME ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: var(--radius-md) !important;
  overflow: hidden;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-glass) !important;
  background: rgba(5,15,32,0.65) !important;
}

/* ── EXPANDER ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--glass-bg) !important;
  box-shadow: var(--shadow-glass) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary p {
  color: var(--ink-soft) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
}

/* ── FORM ───────────────────────────────────────────────────── */
[data-testid="stForm"] {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 28px 32px 32px;
  box-shadow: var(--shadow-glass);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

/* ── SUBMIT BUTTON ──────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, rgba(99,179,237,0.25) 0%, rgba(0,201,167,0.22) 100%) !important;
  border: 1px solid rgba(99,179,237,0.45) !important;
  border-radius: var(--radius-md) !important;
  color: var(--ink) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  padding: 13px 32px !important;
  width: 100% !important;
  transition: all 0.22s ease !important;
  box-shadow: 0 4px 20px rgba(99,179,237,0.18), inset 0 1px 0 rgba(255,255,255,0.10) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: linear-gradient(135deg, rgba(99,179,237,0.40) 0%, rgba(0,201,167,0.35) 100%) !important;
  border-color: rgba(99,179,237,0.70) !important;
  box-shadow: 0 6px 30px rgba(99,179,237,0.38), inset 0 1px 0 rgba(255,255,255,0.18) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
  transform: translateY(0) !important;
}

/* ── REGULAR BUTTONS ────────────────────────────────────────── */
.stButton > button {
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--ink-soft) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 9px 22px !important;
  transition: all 0.18s ease !important;
  box-shadow: var(--shadow-glass) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}
.stButton > button:hover {
  background: rgba(99,179,237,0.12) !important;
  border-color: rgba(99,179,237,0.40) !important;
  color: var(--ink) !important;
  box-shadow: 0 4px 20px rgba(99,179,237,0.20) !important;
  transform: translateY(-2px) !important;
}

/* ── ALERT ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--glass-border) !important;
  background: var(--glass-bg) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
}
[data-testid="stAlert"] p { color: var(--ink-soft) !important; }

hr {
  border: none !important;
  border-top: 1px solid var(--glass-border) !important;
  margin: 1.5rem 0 !important;
}

/* ── HERO ───────────────────────────────────────────────────── */
.hero {
  position: relative;
  border-radius: var(--radius-xl);
  padding: 48px 56px;
  margin-bottom: 32px;
  overflow: hidden;
  background: linear-gradient(135deg,
    rgba(5,20,45,0.85) 0%,
    rgba(8,28,58,0.75) 50%,
    rgba(3,15,35,0.90) 100%);
  border: 1px solid var(--glass-border);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow:
    0 24px 64px rgba(0,0,0,0.60),
    inset 0 1px 0 rgba(255,255,255,0.10),
    inset 0 -1px 0 rgba(0,0,0,0.20);
  animation: fadeUp 0.6s ease both;
}

/* Aurora shimmer band inside hero */
.hero::before {
  content: "";
  position: absolute;
  top: -40%; left: -10%;
  width: 120%; height: 180%;
  background: conic-gradient(
    from 200deg at 60% 40%,
    rgba(0,201,167,0.18) 0deg,
    rgba(99,179,237,0.22) 90deg,
    rgba(167,139,250,0.14) 180deg,
    rgba(52,211,153,0.10) 270deg,
    rgba(0,201,167,0.18) 360deg
  );
  filter: blur(50px);
  pointer-events: none;
  animation: aurora1 18s ease-in-out infinite;
}

/* Subtle light streak */
.hero::after {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(99,179,237,0.50) 40%,
    rgba(0,201,167,0.40) 60%,
    transparent 100%
  );
  background-size: 200% auto;
  animation: shimmer 4s linear infinite;
}

.hero-eyebrow {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: var(--aurora-teal);
  margin-bottom: 14px;
  opacity: 0.85;
}
.hero h1 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 2.80rem !important;
  font-weight: 800 !important;
  color: var(--ink) !important;
  margin: 0 0 14px 0 !important;
  letter-spacing: -0.03em !important;
  line-height: 1.12 !important;
  background: linear-gradient(135deg, #ffffff 30%, rgba(99,179,237,0.90) 70%, rgba(0,201,167,0.80) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero p {
  color: var(--ink-muted) !important;
  font-size: 0.90rem;
  margin: 0;
  max-width: 520px;
  line-height: 1.70;
  font-weight: 400;
  position: relative;
  z-index: 1;
}
.hero-glyph {
  position: absolute;
  right: 56px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 7rem;
  opacity: 0.08;
  color: #fff;
  line-height: 1;
  pointer-events: none;
  user-select: none;
  animation: planeFloat 6s ease-in-out infinite;
}

/* ── SIDEBAR BRAND ──────────────────────────────────────────── */
.sidebar-brand {
  font-family: 'Outfit', sans-serif;
  font-size: 1.40rem;
  font-weight: 800;
  color: var(--ink);
  padding: 4px 0 18px 0;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 18px;
  letter-spacing: -0.02em;
}
.sidebar-brand span {
  background: linear-gradient(135deg, var(--aurora-blue), var(--aurora-teal));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── SECTION HEADERS ────────────────────────────────────────── */
.section-hd {
  margin: 0 0 4px 0;
  font-size: 1.0rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.section-sub {
  font-size: 0.82rem;
  color: var(--ink-muted);
  margin: 0 0 20px 0;
  font-weight: 400;
}

/* ── INFO BOX ───────────────────────────────────────────────── */
.info-box {
  background: rgba(99,179,237,0.06);
  border: 1px solid rgba(99,179,237,0.20);
  border-radius: var(--radius-sm);
  padding: 16px 20px;
  font-size: 0.84rem;
  color: var(--ink-soft);
  margin-bottom: 16px;
  line-height: 1.80;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* ── DECISION PILLS ─────────────────────────────────────────── */
.pill {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 99px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border: 1px solid transparent;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.pill-expand   { background: rgba(52,199,89,0.15);  color: #5de887; border-color: rgba(52,199,89,0.35);  }
.pill-maintain { background: rgba(255,214,10,0.12);  color: #ffd600; border-color: rgba(255,214,10,0.30);  }
.pill-optimize { background: rgba(255,107,53,0.12);  color: #ff8a60; border-color: rgba(255,107,53,0.30);  }
.pill-drop     { background: rgba(255,55,95,0.12);   color: #ff6b8a; border-color: rgba(255,55,95,0.28);   }

/* ── RESULT CARD ────────────────────────────────────────────── */
.result-card {
  border-radius: var(--radius-lg);
  padding: 30px 36px;
  margin: 20px 0;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-glass);
  animation: fadeUp 0.4s ease both;
  position: relative;
  overflow: hidden;
}
.result-card::after {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
}
.result-expand   {
  background: rgba(52,199,89,0.10);
  border: 1px solid rgba(52,199,89,0.30);
  border-left: 4px solid #34C759;
}
.result-maintain {
  background: rgba(255,214,10,0.08);
  border: 1px solid rgba(255,214,10,0.28);
  border-left: 4px solid #FFD60A;
}
.result-optimize {
  background: rgba(255,107,53,0.10);
  border: 1px solid rgba(255,107,53,0.28);
  border-left: 4px solid #FF6B35;
}
.result-drop {
  background: rgba(255,55,95,0.10);
  border: 1px solid rgba(255,55,95,0.28);
  border-left: 4px solid #FF375F;
}

/* ── DIVIDER LABEL ──────────────────────────────────────────── */
.divider-label {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 28px 0 18px;
  color: var(--ink-muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.divider-label::before,
.divider-label::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--glass-border);
}

/* ── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(99,179,237,0.25);
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(99,179,237,0.45);
}
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
#  CHART HELPER  (restyled for dark theme, same data logic)
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    """Return a figure/ax pair styled for the aurora dark theme."""
    # All colours are matplotlib-compatible (R,G,B,A) tuples with values 0-1
    SPINE_COLOR  = (0.47, 0.71, 1.00, 0.18)   # soft blue, very translucent
    TICK_COLOR   = (1.00, 1.00, 1.00, 0.45)   # white 45% opacity
    LABEL_COLOR  = (1.00, 1.00, 1.00, 0.45)
    TITLE_COLOR  = (1.00, 1.00, 1.00, 0.85)
    GRID_COLOR   = (0.47, 0.71, 1.00, 0.08)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("none")
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.tick_params(colors=TICK_COLOR, labelsize=8.5)
    ax.xaxis.label.set_color(LABEL_COLOR)
    ax.yaxis.label.set_color(LABEL_COLOR)
    ax.title.set_color(TITLE_COLOR)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, linestyle="--")
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
        "<p style='font-size:0.68rem;color:rgba(255,255,255,0.35);margin-bottom:18px;"
        "font-weight:600;letter-spacing:0.12em;text-transform:uppercase'>Filter view</p>",
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
    <p style='font-size:0.66rem;color:rgba(255,255,255,0.35);font-weight:700;
    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:0.82rem;
    color:rgba(255,255,255,0.60)'>
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
#  AURORA BLOBS  (real DOM elements — CSS ::before won't work in Streamlit)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="aurora-blob aurora-blob-1"></div>
<div class="aurora-blob aurora-blob-2"></div>
<div class="aurora-blob aurora-blob-3"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">✦ Route Intelligence Platform</div>
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
    "✦  Overview",
    "◈  Performance Drivers",
    "◉  Route Actions",
    "◐  Route Stability",
    "⬡  Prediction Tool",
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
            wedgeprops={"linewidth": 3, "edgecolor": "#050d1a"},
            textprops={"color": (1,1,1,0.75), "fontsize": 9.5},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8.5)
            at.set_color((1,1,1,0.90))
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
          <strong style="color:rgba(255,255,255,0.85)">How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:rgba(255,255,255,0.75)">Expand</strong> routes should have
          the highest values across all three columns.
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
            edgecolor="#050d1a",
            linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + abs(apd.values).max() * 0.025,
                f"${h:,.0f}",
                ha="center", va="bottom",
                fontsize=8, color=(1,1,1,0.65), fontweight="700",
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
            edgecolor="#050d1a",
            linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.006,
                f"{h:.0%}",
                ha="center", va="bottom",
                fontsize=8, color=(1,1,1,0.65), fontweight="700",
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
        edgecolor="#050d1a",
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
            va="center", fontsize=8, color=(1,1,1,0.65), fontweight="700",
        )
    ax.set_xlabel("Average Cost per Flight ($)")
    ax.set_title("Top Cost Drivers")
    st.pyplot(fig)

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
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
            "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
            "Top 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(top.index, top.values, color=CHART_EXPAND, edgecolor="#050d1a", linewidth=2, height=0.55)
        ax.set_xlabel("Total Profit ($)")
        ax.set_title("Top 10 Routes")
        st.pyplot(fig)

    with right:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
            "Bottom 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(worst.index, worst.values, color=CHART_DROP, edgecolor="#050d1a", linewidth=2, height=0.55)
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
            "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
            "Routes with most decision changes</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
            "Routes seen in the most decision states</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
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
        edgecolor="#050d1a", linewidth=2,
    )
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + 0.3,
            f"{int(h)}",
            ha="center", fontsize=9, color=(1,1,1,0.65), fontweight="700",
        )
    ax.set_ylabel("Number of Unique Routes")
    ax.set_title("Unique Routes per Decision Category")
    st.pyplot(fig)

    patches = [mpatches.Patch(color=bc_map.get(d, "#CCCCCC"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5, 0.5))
    fig2.patch.set_alpha(0)
    ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size": 9}, labelcolor=(1,1,1,0.65))
    st.pyplot(fig2)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    # Model accuracy chart
    st.markdown(
        "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
        "How accurate are the models?</p>",
        unsafe_allow_html=True,
    )
    fig, ax = clean_fig((8, 3.5))
    x = np.arange(len(comparison))
    w = 0.30
    b1 = ax.bar(x - w / 2, comparison["Accuracy"], w, label="Accuracy",
                color="#4fc3f7", edgecolor="#050d1a", linewidth=2)
    b2 = ax.bar(x + w / 2, comparison["Macro F1"], w, label="Macro F1",
                color="#34d399", edgecolor="#050d1a", linewidth=2)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.006, f"{h:.0%}",
                ha="center", fontsize=7.5, color=(1,1,1,0.65), fontweight="700")
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["Model"], fontsize=8.5)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Score")
    ax.set_title("Model Accuracy & F1 Comparison")
    ax.legend(frameon=False, fontsize=9, labelcolor=(1,1,1,0.65))
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
                "<p style='font-size:0.68rem;font-weight:700;color:rgba(99,179,237,0.70);"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Flight basics</p>",
                unsafe_allow_html=True,
            )
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown(
                "<p style='font-size:0.68rem;font-weight:700;color:rgba(99,179,237,0.70);"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Route context</p>",
                unsafe_allow_html=True,
            )
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.68rem;font-weight:700;color:rgba(99,179,237,0.70);"
                    "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Revenue</p>",
                    unsafe_allow_html=True,
                )
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.68rem;font-weight:700;color:rgba(99,179,237,0.70);"
                    "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Cost breakdown</p>",
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

        submitted = st.form_submit_button("⬡  Get Route Decision")

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
          <div style='font-family:"Outfit",sans-serif;font-size:1.65rem;font-weight:800;
                      color:{text_col.get(pred, "rgba(255,255,255,0.90)")};margin-bottom:10px;
                      letter-spacing:-0.02em'>
            Suggested Decision: {pred}
          </div>
          <p style='color:rgba(255,255,255,0.60);margin:0;font-size:0.90rem;line-height:1.70'>
            {explanations.get(pred, "")}
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.70);margin-bottom:8px'>"
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
            width=0.45, edgecolor="#050d1a", linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.013,
                f"{h:.0%}",
                ha="center", fontsize=9, color=(1,1,1,0.65), fontweight="700",
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
<div style='text-align:center;color:rgba(255,255,255,0.20);font-size:0.70rem;
            padding:40px 0 16px;font-family:"Outfit",sans-serif;
            letter-spacing:0.10em'>
  SKYLENS ROUTE INTELLIGENCE &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)