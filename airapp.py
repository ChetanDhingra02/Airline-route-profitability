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
#  THEME TOKENS
# ─────────────────────────────────────────────────────────────
COLOR_BG           = "#05010a"
COLOR_GREEN        = "#0bda87"
COLOR_YELLOW       = "#E4D00A"
COLOR_ORANGE       = "#ec5b13"
COLOR_PINK         = "#E0115F"
COLOR_ACCENT       = "#0074D9"
COLOR_ACCENT_DARK  = "#005bb5"
COLOR_AMETHYST     = "#9966CC"

CHART_EXPAND   = "#0bda87"
CHART_MAINTAIN = "#E4D00A"
CHART_OPTIMIZE = "#ec5b13"
CHART_DROP     = "#E0115F"
CHART_NEUTRAL  = ["#0074D9","#9966CC","#0bda87","#E4D00A","#ec5b13","#E0115F","#7ecfff","#b388ff"]

# ─────────────────────────────────────────────────────────────
#  AURORA CANVAS + ANIMATED STARS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
#aurora-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -10;
    pointer-events: none;
}
</style>
<canvas id="aurora-canvas"></canvas>
<script>
(function() {
  const canvas = document.getElementById('aurora-canvas');
  const ctx    = canvas.getContext('2d');
  let W, H, t = 0;

  /* ── stars ── */
  const stars = Array.from({length: 280}, () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 1.5 + 0.2,
    speed: Math.random() * 0.003 + 0.0005,
    phase: Math.random() * Math.PI * 2,
    twinkleSpeed: Math.random() * 0.04 + 0.01
  }));

  /* ── aurora blobs ── */
  const blobs = [
    { cx:0.18, cy:0.28, rx:0.42, rgb:'11,218,135',  a:0.13, ox:0.08, oy:0.06, os:0.18, ot:0.22 },
    { cx:0.78, cy:0.20, rx:0.40, rgb:'153,102,204', a:0.14, ox:0.06, oy:0.08, os:0.14, ot:0.25 },
    { cx:0.50, cy:0.55, rx:0.50, rgb:'224,17,95',   a:0.08, ox:0.10, oy:0.06, os:0.11, ot:0.30 },
    { cx:0.10, cy:0.78, rx:0.38, rgb:'0,116,217',   a:0.11, ox:0.05, oy:0.07, os:0.12, ot:0.18 },
    { cx:0.88, cy:0.68, rx:0.28, rgb:'228,208,10',  a:0.07, ox:0.04, oy:0.05, os:0.22, ot:0.26 },
    { cx:0.35, cy:0.10, rx:0.32, rgb:'0,116,217',   a:0.09, ox:0.07, oy:0.04, os:0.16, ot:0.20 },
  ];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  function frame() {
    t += 0.012;
    ctx.clearRect(0, 0, W, H);

    /* deep space background */
    const bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, '#05010a');
    bg.addColorStop(1, '#0d041a');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    /* aurora blobs */
    blobs.forEach(b => {
      const cx = (b.cx + Math.sin(t * b.os) * b.ox) * W;
      const cy = (b.cy + Math.cos(t * b.os * 0.7) * b.oy) * H;
      const a  = b.a + Math.sin(t * b.ot) * (b.a * 0.5);
      const r  = b.rx * W;
      const g  = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0,    `rgba(${b.rgb},${Math.min(a, 0.22).toFixed(3)})`);
      g.addColorStop(0.45, `rgba(${b.rgb},${(a * 0.4).toFixed(3)})`);
      g.addColorStop(1,    `rgba(${b.rgb},0)`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    });

    /* subtle shimmer scan-line */
    const scan = ctx.createLinearGradient(0, 0, W, H);
    scan.addColorStop(0,   'rgba(255,255,255,0)');
    scan.addColorStop(0.5, `rgba(255,255,255,${(0.012 + 0.006 * Math.sin(t * 0.4)).toFixed(4)})`);
    scan.addColorStop(1,   'rgba(255,255,255,0)');
    ctx.fillStyle = scan;
    ctx.fillRect(0, 0, W, H);

    /* twinkling stars */
    stars.forEach(s => {
      const twinkle = 0.25 + 0.75 * Math.abs(Math.sin(t * s.twinkleSpeed / s.speed + s.phase));
      const size    = s.r * (0.7 + 0.3 * twinkle);
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${(twinkle * 0.9).toFixed(3)})`;
      ctx.fill();

      /* occasional star cross-glow */
      if (s.r > 1.2 && twinkle > 0.85) {
        ctx.strokeStyle = `rgba(255,255,255,${(twinkle * 0.25).toFixed(3)})`;
        ctx.lineWidth   = 0.5;
        const g = 5 * s.r;
        ctx.beginPath();
        ctx.moveTo(s.x * W - g, s.y * H);
        ctx.lineTo(s.x * W + g, s.y * H);
        ctx.moveTo(s.x * W, s.y * H - g);
        ctx.lineTo(s.x * W, s.y * H + g);
        ctx.stroke();
      }
    });

    requestAnimationFrame(frame);
  }
  frame();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,900;1,400&family=DM+Mono:wght@300;400;500&display=swap');

/* ── VARIABLES ─────────────────────────────────────────────── */
:root {{
  --bg:           {COLOR_BG};
  --green:        {COLOR_GREEN};
  --yellow:       {COLOR_YELLOW};
  --orange:       {COLOR_ORANGE};
  --pink:         {COLOR_PINK};
  --accent:       {COLOR_ACCENT};
  --amethyst:     {COLOR_AMETHYST};

  --glass-bg:     rgba(255,255,255,0.05);
  --glass-bg-hov: rgba(255,255,255,0.08);
  --glass-border: rgba(255,255,255,0.10);
  --glass-border-bright: rgba(255,255,255,0.18);
  --glass-shine:  rgba(255,255,255,0.06);

  --ink:          #ffffff;
  --ink-soft:     rgba(255,255,255,0.75);
  --ink-muted:    rgba(255,255,255,0.45);
  --ink-faint:    rgba(255,255,255,0.22);

  --radius-sm:    10px;
  --radius-md:    16px;
  --radius-lg:    22px;

  --shadow-sm:    0 2px 12px rgba(0,0,0,0.45);
  --shadow-md:    0 8px 32px rgba(0,0,0,0.55);
  --shadow-lg:    0 20px 60px rgba(0,0,0,0.65);

  --glow-green:   0 0 24px rgba(11,218,135,0.30), 0 0 60px rgba(11,218,135,0.12);
  --glow-blue:    0 0 24px rgba(0,116,217,0.35),  0 0 60px rgba(0,116,217,0.14);
  --glow-purple:  0 0 24px rgba(153,102,204,0.30),0 0 60px rgba(153,102,204,0.12);
  --glow-ruby:    0 0 24px rgba(224,17,95,0.30),  0 0 60px rgba(224,17,95,0.12);
  --glow-citrine: 0 0 24px rgba(228,208,10,0.30), 0 0 60px rgba(228,208,10,0.12);
}}

/* ── BASE ───────────────────────────────────────────────────── */
html, body, [class*="css"] {{
  font-family: 'Public Sans', system-ui, sans-serif !important;
  color: var(--ink) !important;
}}

.stApp {{
  background: transparent !important;
  min-height: 100vh;
}}

.main .block-container {{
  padding-top: 2rem;
  padding-bottom: 4rem;
  max-width: 1300px;
  background: transparent !important;
}}

/* Force every Streamlit inner wrapper to be see-through */
section[data-testid="stMain"] > div,
.stMainBlockContainer,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: transparent !important;
}}

/* ── SIDEBAR ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background: rgba(5,1,10,0.82) !important;
  backdrop-filter: blur(28px) !important;
  -webkit-backdrop-filter: blur(28px) !important;
  border-right: 1px solid var(--glass-border) !important;
  box-shadow: 4px 0 40px rgba(0,0,0,0.65) !important;
}}
[data-testid="stSidebar"]::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg,
    rgba(11,218,135,0.04) 0%,
    rgba(153,102,204,0.04) 50%,
    rgba(0,116,217,0.04) 100%);
  pointer-events: none;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {{
  color: var(--ink-soft) !important;
  font-family: 'Public Sans', sans-serif !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] {{
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] * {{
  color: var(--ink) !important;
  background: transparent !important;
}}

/* ── METRIC CARDS ─────────────────────────────────────────────── */
[data-testid="metric-container"] {{
  background: var(--glass-bg) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border: 1px solid var(--glass-border) !important;
  border-left: 3px solid var(--green) !important;
  border-radius: var(--radius-md) !important;
  padding: 22px 26px !important;
  box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.07) !important;
  transition: all 0.28s cubic-bezier(0.34,1.56,0.64,1) !important;
  position: relative;
  overflow: hidden;
}}
[data-testid="metric-container"]::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--glass-shine) 0%, transparent 55%);
  pointer-events: none;
  border-radius: inherit;
}}
[data-testid="metric-container"]:hover {{
  background: var(--glass-bg-hov) !important;
  border-left-color: var(--accent) !important;
  box-shadow: var(--shadow-md), var(--glow-blue) !important;
  transform: translateY(-4px) scale(1.01) !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
  font-size: 0.60rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  color: var(--ink-muted) !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {{
  font-family: 'DM Mono', monospace !important;
  font-size: 1.85rem !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
  letter-spacing: -0.03em !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none !important; }}

/* ── TABS ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  background: rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border-radius: var(--radius-md) !important;
  padding: 5px !important;
  gap: 3px !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-sm) !important;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: var(--radius-sm) !important;
  font-family: 'Public Sans', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.68rem !important;
  color: var(--ink-muted) !important;
  padding: 8px 20px !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: all 0.22s ease !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
  background: rgba(11,218,135,0.09) !important;
  color: var(--green) !important;
  border-color: rgba(11,218,135,0.20) !important;
}}
.stTabs [aria-selected="true"] {{
  background: rgba(11,218,135,0.14) !important;
  color: var(--green) !important;
  box-shadow: var(--glow-green), inset 0 0 10px rgba(11,218,135,0.06) !important;
  border-color: rgba(11,218,135,0.35) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
  background: transparent !important;
  padding-top: 1.8rem !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

/* ── HEADINGS ─────────────────────────────────────────────────── */
h1, h2, h3, h4 {{
  font-family: 'Public Sans', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.025em;
  font-weight: 900 !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {{
  color: var(--ink-soft);
  line-height: 1.70;
  font-size: 0.88rem;
}}

/* ── WIDGET LABELS ────────────────────────────────────────────── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
  color: var(--ink-muted) !important;
  font-weight: 800 !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
}}

/* ── INPUTS ───────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {{
  color: var(--ink) !important;
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Public Sans', sans-serif !important;
  font-size: 0.87rem !important;
  box-shadow: none !important;
  transition: border-color 0.22s ease, box-shadow 0.22s ease !important;
  backdrop-filter: blur(10px) !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {{
  border-color: rgba(0,116,217,0.60) !important;
  box-shadow: 0 0 0 3px rgba(0,116,217,0.14), var(--glow-blue) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  background: rgba(8,2,18,0.96) !important;
  backdrop-filter: blur(24px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
}}
[data-baseweb="popover"] [role="option"] {{ color: var(--ink-soft) !important; }}
[data-baseweb="popover"] [role="option"]:hover {{
  background: rgba(11,218,135,0.12) !important;
  color: var(--green) !important;
}}
[data-testid="stSlider"] [role="slider"] {{
  background: var(--green) !important;
  box-shadow: 0 0 12px rgba(11,218,135,0.70) !important;
}}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{
  color: var(--green) !important;
  font-family: 'DM Mono', monospace !important;
}}

/* ── DATAFRAME ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-sm) !important;
  background: rgba(255,255,255,0.03) !important;
  backdrop-filter: blur(16px) !important;
}}
[data-testid="stDataFrame"] th {{
  background: rgba(11,218,135,0.09) !important;
  color: var(--green) !important;
  font-weight: 800 !important;
  letter-spacing: 0.10em !important;
  font-size: 0.68rem !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid rgba(11,218,135,0.20) !important;
}}
[data-testid="stDataFrame"] td {{
  color: var(--ink-soft) !important;
  border-color: rgba(255,255,255,0.05) !important;
  font-size: 0.85rem !important;
}}
[data-testid="stDataFrame"] tr:hover td {{
  background: rgba(255,255,255,0.03) !important;
}}

/* ── EXPANDER ─────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  box-shadow: var(--shadow-sm) !important;
  overflow: hidden !important;
  transition: all 0.25s ease !important;
}}
[data-testid="stExpander"]:hover {{
  box-shadow: var(--shadow-md), var(--glow-blue) !important;
  border-color: rgba(0,116,217,0.30) !important;
  background: var(--glass-bg-hov) !important;
}}
[data-testid="stExpander"] summary p {{
  color: var(--ink) !important;
  font-weight: 800 !important;
  font-size: 0.86rem !important;
  letter-spacing: 0.04em !important;
}}

/* ── FORM ─────────────────────────────────────────────────────── */
[data-testid="stForm"] {{
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 30px 36px 36px !important;
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}}

/* ── SUBMIT BUTTON ────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(135deg, rgba(0,116,217,0.90) 0%, rgba(153,102,204,0.80) 100%) !important;
  border: 1px solid rgba(0,116,217,0.55) !important;
  border-radius: var(--radius-sm) !important;
  color: #fff !important;
  font-family: 'Public Sans', sans-serif !important;
  font-weight: 900 !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  padding: 14px 36px !important;
  width: 100% !important;
  transition: all 0.24s cubic-bezier(0.34,1.56,0.64,1) !important;
  box-shadow: 0 4px 24px rgba(0,116,217,0.35) !important;
  backdrop-filter: blur(10px) !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
  background: linear-gradient(135deg, #0074D9 0%, {COLOR_AMETHYST} 100%) !important;
  box-shadow: 0 0 40px rgba(0,116,217,0.60), 0 0 80px rgba(153,102,204,0.30) !important;
  transform: translateY(-3px) scale(1.02) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
  transform: translateY(0) scale(0.99) !important;
}}

/* ── REGULAR BUTTONS ──────────────────────────────────────────── */
.stButton > button {{
  background: rgba(255,255,255,0.06) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--ink) !important;
  font-family: 'Public Sans', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.78rem !important;
  padding: 10px 24px !important;
  transition: all 0.24s cubic-bezier(0.34,1.56,0.64,1) !important;
  letter-spacing: 0.06em !important;
}}
.stButton > button:hover {{
  background: rgba(11,218,135,0.12) !important;
  border-color: rgba(11,218,135,0.45) !important;
  box-shadow: var(--glow-green) !important;
  transform: translateY(-3px) scale(1.02) !important;
  color: var(--green) !important;
}}

/* ── ALERT ────────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--glass-border) !important;
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(10px) !important;
}}
[data-testid="stAlert"] p {{ color: var(--ink-soft) !important; }}

hr {{
  border: none !important;
  border-top: 1px solid var(--glass-border) !important;
  margin: 1.8rem 0 !important;
}}

/* ── CHROME ───────────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
  background: rgba(5,1,10,0.75) !important;
  backdrop-filter: blur(20px) !important;
  border-bottom: 1px solid var(--glass-border) !important;
}}

/* ── SCROLLBAR ────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.02); }}
::-webkit-scrollbar-thumb {{
  background: rgba(11,218,135,0.28);
  border-radius: 99px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(11,218,135,0.50); }}

/* ══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* HERO ─────────────────────────────────────────────────────── */
.hero {{
  background: var(--glass-bg);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 48px 56px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.08);
}}
.hero::before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 90% 50%, rgba(11,218,135,0.13) 0%, transparent 55%),
    radial-gradient(ellipse at 10% 50%, rgba(153,102,204,0.11) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 100%, rgba(0,116,217,0.08) 0%, transparent 50%);
  pointer-events: none;
  animation: heroShimmer 9s ease-in-out infinite alternate;
}}
.hero::after {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(11,218,135,0.50) 30%,
    rgba(153,102,204,0.50) 70%,
    transparent 100%);
  animation: shimmerLine 4s ease-in-out infinite;
}}
@keyframes heroShimmer {{
  0%   {{ opacity: 0.55; }}
  100% {{ opacity: 1.00; }}
}}
@keyframes shimmerLine {{
  0%,100% {{ opacity: 0.4; }}
  50%     {{ opacity: 1.0; }}
}}

.hero-eyebrow {{
  font-size: 0.60rem;
  font-weight: 900;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: 12px;
  text-shadow: 0 0 16px rgba(11,218,135,0.70);
  display: flex;
  align-items: center;
  gap: 8px;
}}
.hero-eyebrow::before {{
  content: "";
  display: inline-block;
  width: 6px; height: 6px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(11,218,135,0.90);
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%,100% {{ opacity: 1; transform: scale(1); }}
  50%     {{ opacity: 0.5; transform: scale(0.6); }}
}}

.hero h1 {{
  font-family: 'Public Sans', sans-serif !important;
  font-size: 3.0rem !important;
  font-weight: 900 !important;
  color: #fff !important;
  margin: 0 0 16px 0 !important;
  letter-spacing: -0.035em !important;
  line-height: 1.06 !important;
}}
.hero p {{
  color: var(--ink-muted) !important;
  font-size: 0.90rem;
  margin: 0;
  max-width: 520px;
  line-height: 1.75;
  font-weight: 400;
}}
.hero-glyph {{
  position: absolute;
  right: 56px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 10rem;
  opacity: 0.04;
  color: var(--green);
  line-height: 1;
  pointer-events: none;
  user-select: none;
  filter: blur(1px);
  animation: glyphDrift 14s ease-in-out infinite alternate;
}}
@keyframes glyphDrift {{
  0%   {{ transform: translateY(-54%) rotate(-5deg); opacity: 0.03; }}
  100% {{ transform: translateY(-46%) rotate(5deg);  opacity: 0.07; }}
}}

/* SIDEBAR BRAND ─────────────────────────────────────────────── */
.sidebar-brand {{
  font-family: 'Public Sans', sans-serif;
  font-size: 1.35rem;
  font-weight: 900;
  color: #fff;
  padding: 4px 0 18px 0;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 20px;
  letter-spacing: -0.015em;
  text-shadow: 0 0 24px rgba(11,218,135,0.35);
}}
.sidebar-brand span {{ color: var(--amethyst); }}

/* SECTION HEADERS ───────────────────────────────────────────── */
.section-hd {{
  margin: 0 0 4px 0;
  font-size: 1.05rem;
  font-weight: 900;
  color: var(--ink);
  letter-spacing: -0.015em;
}}
.section-sub {{
  font-size: 0.82rem;
  color: var(--ink-muted);
  margin: 0 0 22px 0;
  font-weight: 400;
}}

/* INFO BOX ──────────────────────────────────────────────────── */
.info-box {{
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-left: 3px solid rgba(0,116,217,0.65);
  border-radius: var(--radius-sm);
  padding: 14px 20px;
  font-size: 0.84rem;
  color: var(--ink-soft);
  margin-bottom: 16px;
  line-height: 1.80;
  box-shadow: 0 0 20px rgba(0,116,217,0.07);
}}

/* PILLS ─────────────────────────────────────────────────────── */
.pill {{
  display: inline-block;
  padding: 3px 13px;
  border-radius: 99px;
  font-size: 0.65rem;
  font-weight: 900;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  border: 1px solid transparent;
  backdrop-filter: blur(6px);
}}
.pill-expand   {{ background:rgba(11,218,135,0.15);  color:#0bda87; border-color:rgba(11,218,135,0.40);  box-shadow:0 0 12px rgba(11,218,135,0.25); }}
.pill-maintain {{ background:rgba(228,208,10,0.15);  color:#E4D00A; border-color:rgba(228,208,10,0.40);  box-shadow:0 0 12px rgba(228,208,10,0.25); }}
.pill-optimize {{ background:rgba(236,91,19,0.15);   color:#ec5b13; border-color:rgba(236,91,19,0.40);   box-shadow:0 0 12px rgba(236,91,19,0.25); }}
.pill-drop     {{ background:rgba(224,17,95,0.15);   color:#E0115F; border-color:rgba(224,17,95,0.40);   box-shadow:0 0 12px rgba(224,17,95,0.25); }}

/* RESULT CARDS ──────────────────────────────────────────────── */
.result-card {{
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 32px 38px;
  margin: 22px 0;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}}
.result-card::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, transparent 55%);
  pointer-events: none;
  border-radius: inherit;
}}
.result-card::after {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.20), transparent);
}}
.result-expand   {{ background:rgba(11,218,135,0.07);  border-left:4px solid {CHART_EXPAND};   box-shadow:var(--shadow-md),0 0 50px rgba(11,218,135,0.14); }}
.result-maintain {{ background:rgba(228,208,10,0.07);  border-left:4px solid {CHART_MAINTAIN}; box-shadow:var(--shadow-md),0 0 50px rgba(228,208,10,0.14); }}
.result-optimize {{ background:rgba(236,91,19,0.07);   border-left:4px solid {CHART_OPTIMIZE}; box-shadow:var(--shadow-md),0 0 50px rgba(236,91,19,0.14); }}
.result-drop     {{ background:rgba(224,17,95,0.07);   border-left:4px solid {CHART_DROP};     box-shadow:var(--shadow-md),0 0 50px rgba(224,17,95,0.14); }}

/* DIVIDER LABEL ─────────────────────────────────────────────── */
.divider-label {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 30px 0 20px;
  color: var(--ink-faint);
  font-size: 0.65rem;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}}
.divider-label::before, .divider-label::after {{
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
}}

/* GLASS CHART WRAPPER ───────────────────────────────────────── */
.chart-glass {{
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  DECISION CONFIG
# ─────────────────────────────────────────────────────────────
DECISION_COLORS = {
    "Expand":   CHART_EXPAND,
    "Maintain": CHART_MAINTAIN,
    "Optimize": CHART_OPTIMIZE,
    "Drop":     CHART_DROP,
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

# ─────────────────────────────────────────────────────────────
#  CHART HELPER — jewel-dark aesthetic
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#0d0520")
    fig.patch.set_alpha(0.92)
    ax.set_facecolor("#0a0118")

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color((1, 1, 1, 0.10))
    ax.spines["bottom"].set_color((1, 1, 1, 0.10))

    ax.tick_params(colors=(1, 1, 1, 0.40), labelsize=8.5, length=0)
    ax.xaxis.label.set_color((1, 1, 1, 0.50))
    ax.yaxis.label.set_color((1, 1, 1, 0.50))
    ax.title.set_color("#ffffff")
    ax.title.set_fontsize(11.5)
    ax.title.set_fontweight("bold")
    ax.title.set_fontfamily("sans-serif")

    ax.grid(axis="y", color=(1, 1, 1, 0.05), linewidth=0.8, linestyle="--")
    ax.grid(axis="x", color=(1, 1, 1, 0.03), linewidth=0.5, linestyle=":")
    ax.set_axisbelow(True)

    # subtle inner glow border
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(0.8)
    return fig, ax


def add_bar_glow(ax, bars, colors):
    """Draw a soft glow beneath each bar by layering a wider, translucent copy."""
    for bar, color in zip(bars, colors):
        import matplotlib.patches as mp
        import matplotlib.colors as mc
        r, g, b, _ = mc.to_rgba(color)
        glow = mp.FancyBboxPatch(
            (bar.get_x() - bar.get_width() * 0.15, min(bar.get_y(), 0)),
            bar.get_width() * 1.30,
            abs(bar.get_height()),
            boxstyle="round,pad=0",
            facecolor=(r, g, b, 0.08),
            edgecolor="none",
            zorder=bar.get_zorder() - 1,
        )
        ax.add_patch(glow)


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
#  LOAD
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
        "<p style='font-size:0.68rem;color:rgba(255,255,255,0.40);margin-bottom:20px;"
        "font-weight:800;letter-spacing:0.12em;text-transform:uppercase'>Filter view</p>",
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
    <p style='font-size:0.65rem;color:rgba(255,255,255,0.40);font-weight:900;
    letter-spacing:0.14em;text-transform:uppercase;margin-bottom:12px'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:10px;font-size:0.82rem;color:rgba(255,255,255,0.70)'>
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
#  FILTERING  (logic unchanged)
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
    "✦  Overview",
    "📈  Performance Drivers",
    "🛫  Route Actions",
    "⚡  Route Stability",
    "🔮  Prediction Tool",
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

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
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
        fig, ax = clean_fig((5.5, 5.0))

        # glowing wedges
        wedges, texts, autotexts = ax.pie(
            dc.values,
            labels=dc.index,
            autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index],
            startangle=90,
            wedgeprops={"linewidth": 3, "edgecolor": "#0d0520"},
            textprops={"color": "#ffffff", "fontsize": 9.5, "fontfamily": "sans-serif"},
            pctdistance=0.78,
            radius=0.90,
        )
        for at in autotexts:
            at.set_fontsize(8.5)
            at.set_color("#ffffff")
            at.set_fontweight("bold")
        for txt in texts:
            txt.set_color("rgba(255,255,255,0.75)")

        # draw glow ring
        theta = np.linspace(0, 2 * np.pi, 300)
        ax.plot(0.95 * np.cos(theta), 0.95 * np.sin(theta),
                color=(1, 1, 1, 0.04), linewidth=8, zorder=0)

        ax.set_title("Share of Flights by Decision", pad=16, color="#ffffff")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

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
          <strong style="color:#0bda87">Expand</strong> routes should have the highest values across all three columns.
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
        fig, ax = clean_fig((6, 4.2))
        colors = col_seq(apd.index.tolist())
        bars = ax.bar(
            apd.index, apd.values,
            color=colors,
            width=0.48,
            edgecolor="#0d0520",
            linewidth=1.5,
            zorder=3,
        )
        add_bar_glow(ax, bars, colors)
        mx = abs(apd.values).max() if len(apd) else 1
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + mx * 0.028,
                f"${h:,.0f}",
                ha="center", va="bottom",
                fontsize=8, color=(1, 1, 1, 0.65), fontweight="bold",
            )
        ax.set_ylabel("Average Profit ($)", fontsize=8.5)
        ax.set_title("Average Profit by Decision", pad=14)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        ald = (
            fdf.groupby("Route_Decision")["Load_Factor"].mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .dropna()
        )
        fig, ax = clean_fig((6, 4.2))
        colors = col_seq(ald.index.tolist())
        bars = ax.bar(
            ald.index, ald.values,
            color=colors,
            width=0.48,
            edgecolor="#0d0520",
            linewidth=1.5,
            zorder=3,
        )
        add_bar_glow(ax, bars, colors)
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.007,
                f"{h:.0%}",
                ha="center", va="bottom",
                fontsize=8, color=(1, 1, 1, 0.65), fontweight="bold",
            )
        ax.set_ylabel("Average Seat Occupancy", fontsize=8.5)
        ax.set_title("Seat Occupancy by Decision", pad=14)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

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

    fig, ax = clean_fig((9, 4.2))
    bar_colors = CHART_NEUTRAL[:len(cost_means)]
    bars = ax.barh(
        cost_means.index, cost_means.values,
        color=bar_colors,
        edgecolor="#0d0520",
        linewidth=1.5,
        height=0.52,
        zorder=3,
    )
    mx = cost_means.max() if len(cost_means) else 1
    for b in bars:
        w = b.get_width()
        ax.text(
            w + mx * 0.015,
            b.get_y() + b.get_height() / 2,
            f"${w:,.0f}",
            va="center", fontsize=8, color=(1, 1, 1, 0.60), fontweight="bold",
        )
    ax.set_xlabel("Average Cost per Flight ($)", fontsize=8.5)
    ax.set_title("Top Cost Drivers", pad=14)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px;"
        "letter-spacing:0.04em'>Top routes currently classified as Expand</p>",
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

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
            "Top 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5.2))
        bars = ax.barh(top.index, top.values,
                       color=CHART_EXPAND, edgecolor="#0d0520", linewidth=1.5, height=0.52, zorder=3)
        add_bar_glow(ax, bars, [CHART_EXPAND] * len(bars))
        ax.set_xlabel("Total Profit ($)", fontsize=8.5)
        ax.set_title("Top 10 Routes", pad=14)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
            "Bottom 10 routes by total profit</p>",
            unsafe_allow_html=True,
        )
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5.2))
        bars = ax.barh(worst.index, worst.values,
                       color=CHART_DROP, edgecolor="#0d0520", linewidth=1.5, height=0.52, zorder=3)
        add_bar_glow(ax, bars, [CHART_DROP] * len(bars))
        ax.set_xlabel("Total Profit ($)", fontsize=8.5)
        ax.set_title("Bottom 10 Routes", pad=14)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
            "Routes with most decision changes</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
            "Routes seen in the most decision states</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
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
        "Optimize": CHART_OPTIMIZE,
        "Drop":     CHART_DROP,
    }
    bc = [bc_map.get(i, "#CCCCCC") for i in urbd.index]
    fig, ax = clean_fig((8, 4.2))
    bars = ax.bar(
        urbd.index, urbd["Unique Routes"],
        color=bc, width=0.48,
        edgecolor="#0d0520", linewidth=1.5, zorder=3,
    )
    add_bar_glow(ax, bars, bc)
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + 0.4,
            f"{int(h)}",
            ha="center", fontsize=9, color=(1, 1, 1, 0.65), fontweight="bold",
        )
    ax.set_ylabel("Number of Unique Routes", fontsize=8.5)
    ax.set_title("Unique Routes per Decision Category", pad=14)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    patches = [mpatches.Patch(color=bc_map.get(d, "#CCCCCC"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5, 0.5))
    fig2.patch.set_alpha(0)
    ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size": 9}, labelcolor="#ffffff")
    st.pyplot(fig2)
    plt.close(fig2)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
        "How accurate are the models?</p>",
        unsafe_allow_html=True,
    )
    fig, ax = clean_fig((8, 3.8))
    x = np.arange(len(comparison))
    w = 0.30
    b1 = ax.bar(x - w / 2, comparison["Accuracy"], w, label="Accuracy",
                color=COLOR_ACCENT, edgecolor="#0d0520", linewidth=1.5, zorder=3)
    b2 = ax.bar(x + w / 2, comparison["Macro F1"], w, label="Macro F1",
                color=COLOR_AMETHYST, edgecolor="#0d0520", linewidth=1.5, zorder=3)
    add_bar_glow(ax, list(b1), [COLOR_ACCENT] * len(b1))
    add_bar_glow(ax, list(b2), [COLOR_AMETHYST] * len(b2))
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.007, f"{h:.0%}",
                ha="center", fontsize=7.5, color=(1, 1, 1, 0.60), fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(comparison["Model"], fontsize=8.5)
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Score", fontsize=8.5)
    ax.set_title("Model Accuracy & F1 Comparison", pad=14)
    leg = ax.legend(frameon=False, fontsize=9)
    for text in leg.get_texts():
        text.set_color("rgba(255,255,255,0.65)")
    plt.xticks(rotation=10)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

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

    # ── FORM ──────────────────────────────────────────────────
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                "<p style='font-size:0.68rem;font-weight:900;color:rgba(255,255,255,0.40);"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:14px'>Flight basics</p>",
                unsafe_allow_html=True,
            )
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown(
                "<p style='font-size:0.68rem;font-weight:900;color:rgba(255,255,255,0.40);"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:14px'>Route context</p>",
                unsafe_allow_html=True,
            )
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.68rem;font-weight:900;color:rgba(255,255,255,0.40);"
                    "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:14px'>Revenue</p>",
                    unsafe_allow_html=True,
                )
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.68rem;font-weight:900;color:rgba(255,255,255,0.40);"
                    "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:14px'>Cost breakdown</p>",
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

        submitted = st.form_submit_button("✦  Get Route Decision")

    # ── PREDICTION LOGIC (unchanged) ──────────────────────────
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

    # ── RESULT DISPLAY ─────────────────────────────────────────
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
          <div style='margin-bottom:12px'>
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Public Sans",sans-serif;font-size:1.70rem;font-weight:900;
                      color:{text_col.get(pred, "#111")};margin-bottom:12px;letter-spacing:-0.025em;
                      text-shadow:0 0 30px {text_col.get(pred, "#111")}55'>
            Suggested Decision: {pred}
          </div>
          <p style='color:rgba(255,255,255,0.60);margin:0;font-size:0.90rem;line-height:1.75'>
            {explanations.get(pred, "")}
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='font-size:0.78rem;font-weight:800;color:#ffffff;margin-bottom:10px'>"
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
            "Optimize": CHART_OPTIMIZE,
            "Drop":     CHART_DROP,
        }
        colors_prob = [bar_cp.get(d, "#CCCCCC") for d in prob_df["Decision"]]
        fig, ax = clean_fig((6, 3.8))
        bars = ax.bar(
            prob_df["Decision"], prob_df["Probability"],
            color=colors_prob,
            width=0.44, edgecolor="#0d0520", linewidth=1.5, zorder=3,
        )
        add_bar_glow(ax, bars, colors_prob)
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.014,
                f"{h:.0%}",
                ha="center", fontsize=9, color=(1, 1, 1, 0.70), fontweight="bold",
            )
        ax.set_ylim(0, 1.20)
        ax.set_ylabel("Probability", fontsize=8.5)
        ax.set_title("Model Confidence per Decision", pad=14)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
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
<div style='text-align:center;color:rgba(255,255,255,0.30);font-size:0.72rem;
            padding:40px 0 20px;font-family:"Public Sans",sans-serif;
            letter-spacing:0.06em'>
  ✦ &nbsp;SKYLENS ROUTE INTELLIGENCE&nbsp; · &nbsp;Built with Streamlit&nbsp; ✦
</div>
""", unsafe_allow_html=True)