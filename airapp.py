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
#  THEME TOKENS — jewel-tone palette
# ─────────────────────────────────────────────────────────────
COLOR_BG           = "#04010d"
COLOR_GREEN        = "#00ffb3"
COLOR_YELLOW       = "#f5e642"
COLOR_ORANGE       = "#ff6b35"
COLOR_PINK         = "#ff2d78"
COLOR_ACCENT       = "#4d9fff"
COLOR_ACCENT_DARK  = "#1a6fd4"
COLOR_AMETHYST     = "#b366ff"
COLOR_MAGENTA      = "#e040fb"
COLOR_TEAL         = "#00e5cc"

CHART_EXPAND   = "#00ffb3"
CHART_MAINTAIN = "#f5e642"
CHART_OPTIMIZE = "#ff6b35"
CHART_DROP     = "#ff2d78"
CHART_NEUTRAL  = ["#4d9fff","#b366ff","#00ffb3","#f5e642","#ff6b35","#ff2d78","#7ecfff","#e040fb"]

# ─────────────────────────────────────────────────────────────
#  AURORA CANVAS — multi-layer animated aurora + stars
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
#aurora-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: -10;
    pointer-events: none;
    display: block;
}
</style>
<canvas id="aurora-canvas"></canvas>
<script>
(function() {
  const canvas = document.getElementById('aurora-canvas');
  const ctx    = canvas.getContext('2d');
  let W, H, t = 0;

  /* ── stars ── */
  const STAR_COUNT = 340;
  const stars = Array.from({length: STAR_COUNT}, () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 1.8 + 0.15,
    speed: Math.random() * 0.002 + 0.0004,
    phase: Math.random() * Math.PI * 2,
    twinkleSpeed: Math.random() * 0.05 + 0.008,
    colorIndex: Math.floor(Math.random() * 4),
  }));
  const STAR_TINTS = [
    [255,255,255],
    [180,220,255],
    [200,180,255],
    [180,255,230],
  ];

  /* ── aurora wave bands ── */
  const bands = [
    { y: 0.18, amp: 0.08,  freq: 1.3, speed: 0.18, rgb: '0,255,179',   alpha: 0.22, thickness: 0.14 },
    { y: 0.28, amp: 0.07,  freq: 1.7, speed: 0.14, rgb: '179,102,255', alpha: 0.18, thickness: 0.12 },
    { y: 0.12, amp: 0.06,  freq: 2.1, speed: 0.22, rgb: '224,64,251',  alpha: 0.13, thickness: 0.10 },
    { y: 0.35, amp: 0.05,  freq: 1.1, speed: 0.10, rgb: '77,159,255',  alpha: 0.14, thickness: 0.11 },
    { y: 0.08, amp: 0.04,  freq: 2.8, speed: 0.26, rgb: '0,229,204',   alpha: 0.10, thickness: 0.08 },
  ];

  /* ── aurora blobs (radial) ── */
  const blobs = [
    { cx:0.15, cy:0.22, rx:0.55, rgb:'0,255,179',   a:0.18, ox:0.09, oy:0.07, os:0.15, ot:0.22 },
    { cx:0.82, cy:0.18, rx:0.50, rgb:'179,102,255', a:0.20, ox:0.07, oy:0.09, os:0.13, ot:0.25 },
    { cx:0.50, cy:0.45, rx:0.60, rgb:'224,64,251',  a:0.10, ox:0.11, oy:0.06, os:0.10, ot:0.30 },
    { cx:0.08, cy:0.72, rx:0.45, rgb:'77,159,255',  a:0.14, ox:0.06, oy:0.08, os:0.12, ot:0.18 },
    { cx:0.90, cy:0.65, rx:0.35, rgb:'0,229,204',   a:0.12, ox:0.05, oy:0.06, os:0.20, ot:0.26 },
    { cx:0.40, cy:0.08, rx:0.42, rgb:'255,45,120',  a:0.09, ox:0.08, oy:0.04, os:0.16, ot:0.20 },
    { cx:0.70, cy:0.38, rx:0.38, rgb:'245,230,66',  a:0.07, ox:0.06, oy:0.07, os:0.18, ot:0.24 },
  ];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  /* draw a single aurora wave band as a smooth horizontal ribbon */
  function drawBand(b) {
    const baseY = b.y * H;
    const thick = b.thickness * H;
    const pts   = 120;
    ctx.beginPath();
    for (let i = 0; i <= pts; i++) {
      const x = (i / pts) * W;
      const phase2 = t * b.speed + i * 0.08;
      const y = baseY
        + Math.sin(phase2 * b.freq)              * b.amp * H
        + Math.sin(phase2 * b.freq * 1.618 + 1.2) * b.amp * H * 0.4
        + Math.sin(phase2 * b.freq * 0.618 + 2.5) * b.amp * H * 0.2;
      if (i === 0) ctx.moveTo(x, y);
      else         ctx.lineTo(x, y);
    }
    for (let i = pts; i >= 0; i--) {
      const x = (i / pts) * W;
      const phase2 = t * b.speed + i * 0.08;
      const y = baseY + thick
        + Math.sin(phase2 * b.freq + 0.5)          * b.amp * H * 0.6
        + Math.sin(phase2 * b.freq * 1.618 + 2.0)  * b.amp * H * 0.25;
      ctx.lineTo(x, y);
    }
    ctx.closePath();

    /* vertical gradient through the ribbon */
    const grad = ctx.createLinearGradient(0, baseY - thick * 0.5, 0, baseY + thick * 1.5);
    grad.addColorStop(0,    `rgba(${b.rgb},0)`);
    grad.addColorStop(0.3,  `rgba(${b.rgb},${(b.alpha * 0.6).toFixed(3)})`);
    grad.addColorStop(0.55, `rgba(${b.rgb},${b.alpha.toFixed(3)})`);
    grad.addColorStop(0.75, `rgba(${b.rgb},${(b.alpha * 0.5).toFixed(3)})`);
    grad.addColorStop(1,    `rgba(${b.rgb},0)`);
    ctx.fillStyle = grad;
    ctx.fill();
  }

  function frame() {
    t += 0.008;
    ctx.clearRect(0, 0, W, H);

    /* deep space background */
    const bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0,   '#04010d');
    bg.addColorStop(0.5, '#080118');
    bg.addColorStop(1,   '#0a0220');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    /* aurora blob layer (soft radial pools of colour) */
    blobs.forEach(b => {
      const cx = (b.cx + Math.sin(t * b.os + 0.3)  * b.ox) * W;
      const cy = (b.cy + Math.cos(t * b.os * 0.65) * b.oy) * H;
      const a  = b.a + Math.sin(t * b.ot) * (b.a * 0.45);
      const r  = b.rx * W;
      const g  = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0,    `rgba(${b.rgb},${Math.min(a, 0.26).toFixed(3)})`);
      g.addColorStop(0.40, `rgba(${b.rgb},${(a * 0.38).toFixed(3)})`);
      g.addColorStop(1,    `rgba(${b.rgb},0)`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    });

    /* aurora wave bands — the signature curtain effect */
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    bands.forEach(drawBand);
    ctx.restore();

    /* subtle shimmer overlay */
    const scan = ctx.createLinearGradient(0, 0, W * 0.5, H);
    scan.addColorStop(0,   'rgba(255,255,255,0)');
    scan.addColorStop(0.5, `rgba(255,255,255,${(0.018 + 0.008 * Math.sin(t * 0.35)).toFixed(4)})`);
    scan.addColorStop(1,   'rgba(255,255,255,0)');
    ctx.fillStyle = scan;
    ctx.fillRect(0, 0, W, H);

    /* twinkling stars */
    stars.forEach(s => {
      const twinkle = 0.20 + 0.80 * Math.abs(Math.sin(t * s.twinkleSpeed / s.speed + s.phase));
      const size    = s.r * (0.65 + 0.35 * twinkle);
      const tint    = STAR_TINTS[s.colorIndex];
      ctx.beginPath();
      ctx.arc(s.x * W, s.y * H, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${tint[0]},${tint[1]},${tint[2]},${(twinkle * 0.92).toFixed(3)})`;
      ctx.fill();

      /* cross-glow on brighter stars */
      if (s.r > 1.1 && twinkle > 0.82) {
        ctx.save();
        ctx.strokeStyle = `rgba(${tint[0]},${tint[1]},${tint[2]},${(twinkle * 0.28).toFixed(3)})`;
        ctx.lineWidth   = 0.6;
        const g = 6 * s.r * twinkle;
        ctx.beginPath();
        ctx.moveTo(s.x * W - g, s.y * H);
        ctx.lineTo(s.x * W + g, s.y * H);
        ctx.moveTo(s.x * W, s.y * H - g);
        ctx.lineTo(s.x * W, s.y * H + g);
        ctx.stroke();
        /* diagonal softcross */
        ctx.globalAlpha = 0.12 * twinkle;
        const dg = g * 0.55;
        ctx.beginPath();
        ctx.moveTo(s.x * W - dg, s.y * H - dg);
        ctx.lineTo(s.x * W + dg, s.y * H + dg);
        ctx.moveTo(s.x * W + dg, s.y * H - dg);
        ctx.lineTo(s.x * W - dg, s.y * H + dg);
        ctx.stroke();
        ctx.restore();
      }
    });

    requestAnimationFrame(frame);
  }
  frame();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — jewel glassmorphism system
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── CSS VARIABLES ─────────────────────────────────────────── */
:root {{
  --bg:           {COLOR_BG};
  --green:        {COLOR_GREEN};
  --yellow:       {COLOR_YELLOW};
  --orange:       {COLOR_ORANGE};
  --pink:         {COLOR_PINK};
  --accent:       {COLOR_ACCENT};
  --amethyst:     {COLOR_AMETHYST};
  --magenta:      {COLOR_MAGENTA};
  --teal:         {COLOR_TEAL};

  --glass-1:      rgba(255,255,255,0.042);
  --glass-2:      rgba(255,255,255,0.075);
  --glass-3:      rgba(255,255,255,0.11);
  --glass-border: rgba(255,255,255,0.10);
  --glass-bright: rgba(255,255,255,0.20);
  --glass-shine:  linear-gradient(135deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.02) 50%, transparent 100%);

  --ink:          #ffffff;
  --ink-soft:     rgba(255,255,255,0.78);
  --ink-muted:    rgba(255,255,255,0.48);
  --ink-faint:    rgba(255,255,255,0.22);

  --r-sm:   10px;
  --r-md:   16px;
  --r-lg:   22px;
  --r-xl:   30px;

  --sh-sm:  0 2px 16px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.04);
  --sh-md:  0 8px 40px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.06);
  --sh-lg:  0 24px 72px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.08);

  --glow-green:   0 0 32px rgba(0,255,179,0.40),   0 0 80px rgba(0,255,179,0.15);
  --glow-blue:    0 0 32px rgba(77,159,255,0.40),   0 0 80px rgba(77,159,255,0.15);
  --glow-purple:  0 0 32px rgba(179,102,255,0.40),  0 0 80px rgba(179,102,255,0.15);
  --glow-magenta: 0 0 32px rgba(224,64,251,0.40),   0 0 80px rgba(224,64,251,0.15);
  --glow-pink:    0 0 32px rgba(255,45,120,0.40),   0 0 80px rgba(255,45,120,0.15);
  --glow-citrine: 0 0 32px rgba(245,230,66,0.40),   0 0 80px rgba(245,230,66,0.15);
  --glow-teal:    0 0 32px rgba(0,229,204,0.40),    0 0 80px rgba(0,229,204,0.15);
}}

/* ── BASE ───────────────────────────────────────────────────── */
html, body, [class*="css"] {{
  font-family: 'Outfit', system-ui, sans-serif !important;
  color: var(--ink) !important;
  -webkit-font-smoothing: antialiased;
}}
.stApp {{
  background: transparent !important;
  min-height: 100vh;
}}
.main .block-container {{
  padding-top: 2.2rem;
  padding-bottom: 5rem;
  max-width: 1340px;
  background: transparent !important;
}}
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
  background: rgba(4,1,13,0.88) !important;
  backdrop-filter: blur(36px) saturate(1.4) !important;
  -webkit-backdrop-filter: blur(36px) saturate(1.4) !important;
  border-right: 1px solid rgba(179,102,255,0.18) !important;
  box-shadow: 4px 0 60px rgba(0,0,0,0.75), inset -1px 0 0 rgba(255,255,255,0.06) !important;
}}
[data-testid="stSidebar"]::before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%,   rgba(0,255,179,0.07)   0%, transparent 60%),
    radial-gradient(ellipse at 0%  60%,  rgba(179,102,255,0.07) 0%, transparent 55%),
    radial-gradient(ellipse at 100% 90%, rgba(77,159,255,0.05)  0%, transparent 55%);
  pointer-events: none;
  animation: sidebarPulse 10s ease-in-out infinite alternate;
}}
@keyframes sidebarPulse {{
  0%   {{ opacity: 0.6; }}
  100% {{ opacity: 1.0; }}
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {{
  color: var(--ink-soft) !important;
  font-family: 'Outfit', sans-serif !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] {{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(179,102,255,0.25) !important;
  border-radius: var(--r-sm) !important;
  transition: border-color 0.22s, box-shadow 0.22s !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"]:hover {{
  border-color: rgba(0,255,179,0.40) !important;
  box-shadow: var(--glow-green) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] * {{
  color: var(--ink) !important;
  background: transparent !important;
}}

/* ── METRIC CARDS — jewel glassmorphism ──────────────────────── */
[data-testid="metric-container"] {{
  background: var(--glass-1) !important;
  backdrop-filter: blur(28px) saturate(1.6) !important;
  -webkit-backdrop-filter: blur(28px) saturate(1.6) !important;
  border: 1px solid var(--glass-border) !important;
  border-top: 1px solid var(--glass-bright) !important;
  border-left: 3px solid var(--green) !important;
  border-radius: var(--r-md) !important;
  padding: 24px 28px !important;
  box-shadow: var(--sh-sm), inset 0 1px 0 rgba(255,255,255,0.10) !important;
  transition: all 0.32s cubic-bezier(0.34,1.56,0.64,1) !important;
  position: relative;
  overflow: hidden;
  animation: cardFadeIn 0.6s ease both;
}}
[data-testid="metric-container"]::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: var(--glass-shine);
  pointer-events: none;
  border-radius: inherit;
}}
[data-testid="metric-container"]::after {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(0,255,179,0.55) 40%, rgba(179,102,255,0.55) 70%, transparent 100%);
  animation: shimmerLine 4s ease-in-out infinite;
}}
[data-testid="metric-container"]:hover {{
  background: var(--glass-2) !important;
  border-left-color: var(--accent) !important;
  box-shadow: var(--sh-md), var(--glow-blue) !important;
  transform: translateY(-6px) scale(1.015) !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
  font-size: 0.58rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  color: var(--ink-muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {{
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 2.0rem !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
  letter-spacing: -0.04em !important;
  text-shadow: 0 0 40px rgba(255,255,255,0.15) !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none !important; }}

@keyframes cardFadeIn {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes shimmerLine {{
  0%,100% {{ opacity: 0.3; transform: scaleX(0.8); }}
  50%     {{ opacity: 1.0; transform: scaleX(1.0); }}
}}

/* ── TABS ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  background: rgba(255,255,255,0.038) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;
  border-radius: var(--r-lg) !important;
  padding: 6px !important;
  gap: 4px !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--sh-sm), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}}
.stTabs [data-baseweb="tab"] {{
  border-radius: var(--r-md) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.67rem !important;
  color: var(--ink-muted) !important;
  padding: 9px 22px !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: all 0.24s cubic-bezier(0.4,0,0.2,1) !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
  background: rgba(0,255,179,0.08) !important;
  color: var(--green) !important;
  border-color: rgba(0,255,179,0.22) !important;
}}
.stTabs [aria-selected="true"] {{
  background: rgba(0,255,179,0.12) !important;
  color: var(--green) !important;
  box-shadow: var(--glow-green), inset 0 0 14px rgba(0,255,179,0.06) !important;
  border-color: rgba(0,255,179,0.40) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
  background: transparent !important;
  padding-top: 2rem !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

/* ── HEADINGS ─────────────────────────────────────────────────── */
h1, h2, h3, h4 {{
  font-family: 'Outfit', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.03em;
  font-weight: 800 !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {{
  color: var(--ink-soft);
  line-height: 1.72;
  font-size: 0.88rem;
  font-family: 'Outfit', sans-serif;
}}

/* ── WIDGET LABELS ────────────────────────────────────────────── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
  color: var(--ink-muted) !important;
  font-weight: 800 !important;
  font-size: 0.66rem !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  font-family: 'JetBrains Mono', monospace !important;
}}

/* ── INPUTS ───────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {{
  color: var(--ink) !important;
  background: rgba(255,255,255,0.055) !important;
  border: 1px solid rgba(179,102,255,0.22) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.87rem !important;
  box-shadow: none !important;
  transition: border-color 0.22s ease, box-shadow 0.22s ease !important;
  backdrop-filter: blur(12px) !important;
}}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus {{
  border-color: rgba(77,159,255,0.65) !important;
  box-shadow: 0 0 0 3px rgba(77,159,255,0.14), var(--glow-blue) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  background: rgba(6,1,18,0.96) !important;
  backdrop-filter: blur(28px) !important;
  border: 1px solid rgba(179,102,255,0.22) !important;
  border-radius: var(--r-md) !important;
}}
[data-baseweb="popover"] [role="option"] {{ color: var(--ink-soft) !important; }}
[data-baseweb="popover"] [role="option"]:hover {{
  background: rgba(0,255,179,0.10) !important;
  color: var(--green) !important;
}}
[data-testid="stSlider"] [role="slider"] {{
  background: var(--green) !important;
  box-shadow: 0 0 16px rgba(0,255,179,0.80) !important;
}}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{
  color: var(--green) !important;
  font-family: 'JetBrains Mono', monospace !important;
}}

/* ── DATAFRAME ────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
  border-radius: var(--r-md) !important;
  overflow: hidden !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--sh-sm) !important;
  background: rgba(255,255,255,0.028) !important;
  backdrop-filter: blur(20px) !important;
  transition: box-shadow 0.28s !important;
}}
[data-testid="stDataFrame"]:hover {{
  box-shadow: var(--sh-md), var(--glow-purple) !important;
}}
[data-testid="stDataFrame"] th {{
  background: rgba(0,255,179,0.08) !important;
  color: var(--green) !important;
  font-weight: 800 !important;
  letter-spacing: 0.10em !important;
  font-size: 0.66rem !important;
  text-transform: uppercase !important;
  border-bottom: 1px solid rgba(0,255,179,0.18) !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stDataFrame"] td {{
  color: var(--ink-soft) !important;
  border-color: rgba(255,255,255,0.04) !important;
  font-size: 0.85rem !important;
}}
[data-testid="stDataFrame"] tr:hover td {{
  background: rgba(0,255,179,0.04) !important;
}}

/* ── EXPANDER ─────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--r-md) !important;
  background: var(--glass-1) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  box-shadow: var(--sh-sm) !important;
  overflow: hidden !important;
  transition: all 0.28s cubic-bezier(0.4,0,0.2,1) !important;
  position: relative;
}}
[data-testid="stExpander"]::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(179,102,255,0.55), transparent);
}}
[data-testid="stExpander"]:hover {{
  box-shadow: var(--sh-md), var(--glow-purple) !important;
  border-color: rgba(179,102,255,0.32) !important;
  background: var(--glass-2) !important;
}}
[data-testid="stExpander"] summary p {{
  color: var(--ink) !important;
  font-weight: 800 !important;
  font-size: 0.86rem !important;
  letter-spacing: 0.04em !important;
}}

/* ── FORM ─────────────────────────────────────────────────────── */
[data-testid="stForm"] {{
  background: rgba(255,255,255,0.045) !important;
  backdrop-filter: blur(32px) saturate(1.5) !important;
  -webkit-backdrop-filter: blur(32px) saturate(1.5) !important;
  border: 1px solid var(--glass-border) !important;
  border-top: 1px solid rgba(255,255,255,0.18) !important;
  border-radius: var(--r-xl) !important;
  padding: 32px 40px 40px !important;
  box-shadow: var(--sh-md), inset 0 1px 0 rgba(255,255,255,0.10) !important;
  position: relative;
}}
[data-testid="stForm"]::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: var(--glass-shine);
  border-radius: inherit;
  pointer-events: none;
}}

/* ── SUBMIT BUTTON ────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(135deg,
    rgba(77,159,255,0.90)  0%,
    rgba(179,102,255,0.80) 50%,
    rgba(224,64,251,0.75)  100%) !important;
  border: 1px solid rgba(77,159,255,0.55) !important;
  border-radius: var(--r-md) !important;
  color: #fff !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 900 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  padding: 15px 40px !important;
  width: 100% !important;
  transition: all 0.26s cubic-bezier(0.34,1.56,0.64,1) !important;
  box-shadow: 0 4px 30px rgba(77,159,255,0.40), 0 0 0 1px rgba(255,255,255,0.08) !important;
  backdrop-filter: blur(12px) !important;
  position: relative;
  overflow: hidden;
}}
[data-testid="stFormSubmitButton"] > button::after {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.14) 0%, transparent 60%);
  border-radius: inherit;
  pointer-events: none;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
  background: linear-gradient(135deg, #4d9fff 0%, #b366ff 50%, #e040fb 100%) !important;
  box-shadow: 0 0 50px rgba(77,159,255,0.70), 0 0 100px rgba(179,102,255,0.35) !important;
  transform: translateY(-4px) scale(1.025) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
  transform: translateY(0) scale(0.985) !important;
}}

/* ── REGULAR BUTTONS ──────────────────────────────────────────── */
.stButton > button {{
  background: rgba(255,255,255,0.055) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(179,102,255,0.22) !important;
  border-radius: var(--r-sm) !important;
  color: var(--ink) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.78rem !important;
  padding: 11px 26px !important;
  transition: all 0.26s cubic-bezier(0.34,1.56,0.64,1) !important;
  letter-spacing: 0.07em !important;
}}
.stButton > button:hover {{
  background: rgba(0,255,179,0.10) !important;
  border-color: rgba(0,255,179,0.50) !important;
  box-shadow: var(--glow-green) !important;
  transform: translateY(-4px) scale(1.025) !important;
  color: var(--green) !important;
}}

/* ── ALERT ────────────────────────────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: var(--r-md) !important;
  border: 1px solid rgba(77,159,255,0.22) !important;
  background: rgba(77,159,255,0.06) !important;
  backdrop-filter: blur(12px) !important;
}}
[data-testid="stAlert"] p {{ color: var(--ink-soft) !important; }}

hr {{
  border: none !important;
  border-top: 1px solid var(--glass-border) !important;
  margin: 2rem 0 !important;
}}

/* ── CHROME ───────────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
  background: rgba(4,1,13,0.78) !important;
  backdrop-filter: blur(24px) saturate(1.5) !important;
  border-bottom: 1px solid rgba(179,102,255,0.16) !important;
}}

/* ── SCROLLBAR ────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.02); }}
::-webkit-scrollbar-thumb {{
  background: linear-gradient(180deg, rgba(0,255,179,0.35), rgba(179,102,255,0.35));
  border-radius: 99px;
}}
::-webkit-scrollbar-thumb:hover {{
  background: linear-gradient(180deg, rgba(0,255,179,0.60), rgba(179,102,255,0.60));
}}

/* ══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* HERO ─────────────────────────────────────────────────────── */
.hero {{
  background: rgba(255,255,255,0.040);
  backdrop-filter: blur(36px) saturate(1.6);
  -webkit-backdrop-filter: blur(36px) saturate(1.6);
  border: 1px solid var(--glass-border);
  border-top: 1px solid rgba(255,255,255,0.20);
  border-radius: var(--r-xl);
  padding: 52px 60px;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--sh-lg), inset 0 1px 0 rgba(255,255,255,0.10);
  animation: heroEntrance 0.8s cubic-bezier(0.22,1,0.36,1) both;
}}
@keyframes heroEntrance {{
  from {{ opacity: 0; transform: translateY(24px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.hero::before {{
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 88% 50%, rgba(0,255,179,0.16) 0%, transparent 50%),
    radial-gradient(ellipse at 12% 50%, rgba(179,102,255,0.14) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 100%, rgba(77,159,255,0.10) 0%, transparent 45%),
    linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 55%);
  pointer-events: none;
  animation: heroShimmer 11s ease-in-out infinite alternate;
}}
.hero::after {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(0,255,179,0.70)  25%,
    rgba(179,102,255,0.70) 55%,
    rgba(224,64,251,0.60) 80%,
    transparent 100%);
  animation: shimmerLine 5s ease-in-out infinite;
}}
@keyframes heroShimmer {{
  0%   {{ opacity: 0.50; }}
  100% {{ opacity: 1.00; }}
}}

.hero-eyebrow {{
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: 14px;
  text-shadow: 0 0 20px rgba(0,255,179,0.80);
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
}}
.hero-eyebrow::before {{
  content: "";
  display: inline-block;
  width: 7px; height: 7px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 12px rgba(0,255,179,1.0), 0 0 24px rgba(0,255,179,0.60);
  animation: pulse 1.8s ease-in-out infinite;
}}
@keyframes pulse {{
  0%,100% {{ opacity: 1; transform: scale(1);   box-shadow: 0 0 12px rgba(0,255,179,1), 0 0 24px rgba(0,255,179,0.6); }}
  50%     {{ opacity: 0.45; transform: scale(0.55); box-shadow: 0 0 6px rgba(0,255,179,0.5); }}
}}

.hero h1 {{
  font-family: 'Outfit', sans-serif !important;
  font-size: 3.2rem !important;
  font-weight: 900 !important;
  color: #fff !important;
  margin: 0 0 18px 0 !important;
  letter-spacing: -0.04em !important;
  line-height: 1.04 !important;
  text-shadow: 0 0 60px rgba(255,255,255,0.12) !important;
}}
.hero p {{
  color: var(--ink-muted) !important;
  font-size: 0.92rem;
  margin: 0;
  max-width: 540px;
  line-height: 1.78;
  font-weight: 400;
}}
.hero-glyph {{
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11rem;
  opacity: 0.045;
  background: linear-gradient(135deg, var(--green), var(--amethyst));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  pointer-events: none;
  user-select: none;
  animation: glyphDrift 16s ease-in-out infinite alternate;
}}
@keyframes glyphDrift {{
  0%   {{ transform: translateY(-56%) rotate(-6deg) scale(0.96); opacity: 0.032; }}
  100% {{ transform: translateY(-44%) rotate(6deg)  scale(1.04); opacity: 0.065; }}
}}

/* SIDEBAR BRAND ─────────────────────────────────────────────── */
.sidebar-brand {{
  font-family: 'Outfit', sans-serif;
  font-size: 1.40rem;
  font-weight: 900;
  color: #fff;
  padding: 4px 0 20px 0;
  border-bottom: 1px solid rgba(179,102,255,0.20);
  margin-bottom: 22px;
  letter-spacing: -0.02em;
  text-shadow: 0 0 28px rgba(0,255,179,0.35);
}}
.sidebar-brand span {{ color: var(--amethyst); }}

/* SECTION HEADERS ───────────────────────────────────────────── */
.section-hd {{
  margin: 0 0 4px 0;
  font-size: 1.08rem;
  font-weight: 800;
  color: var(--ink);
  letter-spacing: -0.018em;
  font-family: 'Outfit', sans-serif;
}}
.section-sub {{
  font-size: 0.82rem;
  color: var(--ink-muted);
  margin: 0 0 24px 0;
  font-weight: 400;
}}

/* INFO BOX ──────────────────────────────────────────────────── */
.info-box {{
  background: rgba(77,159,255,0.07);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(77,159,255,0.20);
  border-left: 3px solid rgba(77,159,255,0.75);
  border-radius: var(--r-sm);
  padding: 16px 22px;
  font-size: 0.84rem;
  color: var(--ink-soft);
  margin-bottom: 18px;
  line-height: 1.82;
  box-shadow: 0 0 24px rgba(77,159,255,0.08);
  position: relative;
  overflow: hidden;
}}
.info-box::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 60%);
}}

/* PILLS ─────────────────────────────────────────────────────── */
.pill {{
  display: inline-block;
  padding: 4px 14px;
  border-radius: 99px;
  font-size: 0.63rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border: 1px solid transparent;
  backdrop-filter: blur(8px);
  font-family: 'JetBrains Mono', monospace;
  transition: box-shadow 0.22s;
}}
.pill:hover {{ filter: brightness(1.15); }}
.pill-expand   {{ background:rgba(0,255,179,0.14);  color:{COLOR_GREEN}; border-color:rgba(0,255,179,0.45);  box-shadow:0 0 16px rgba(0,255,179,0.30); }}
.pill-maintain {{ background:rgba(245,230,66,0.14); color:{COLOR_YELLOW}; border-color:rgba(245,230,66,0.45);  box-shadow:0 0 16px rgba(245,230,66,0.30); }}
.pill-optimize {{ background:rgba(255,107,53,0.14); color:{COLOR_ORANGE}; border-color:rgba(255,107,53,0.45);  box-shadow:0 0 16px rgba(255,107,53,0.30); }}
.pill-drop     {{ background:rgba(255,45,120,0.14); color:{COLOR_PINK};   border-color:rgba(255,45,120,0.45);  box-shadow:0 0 16px rgba(255,45,120,0.30); }}

/* RESULT CARDS ──────────────────────────────────────────────── */
.result-card {{
  border: 1px solid var(--glass-border);
  border-radius: var(--r-xl);
  padding: 36px 44px;
  margin: 24px 0;
  backdrop-filter: blur(32px) saturate(1.5);
  -webkit-backdrop-filter: blur(32px) saturate(1.5);
  box-shadow: var(--sh-lg);
  position: relative;
  overflow: hidden;
  animation: resultReveal 0.5s cubic-bezier(0.22,1,0.36,1) both;
}}
@keyframes resultReveal {{
  from {{ opacity: 0; transform: translateY(20px) scale(0.98); }}
  to   {{ opacity: 1; transform: translateY(0)    scale(1); }}
}}
.result-card::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 55%);
  pointer-events: none;
  border-radius: inherit;
}}
.result-card::after {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
}}
.result-expand   {{ background:rgba(0,255,179,0.07);  border-left:4px solid {CHART_EXPAND};   box-shadow:var(--sh-lg), 0 0 60px rgba(0,255,179,0.16); }}
.result-maintain {{ background:rgba(245,230,66,0.07); border-left:4px solid {CHART_MAINTAIN}; box-shadow:var(--sh-lg), 0 0 60px rgba(245,230,66,0.16); }}
.result-optimize {{ background:rgba(255,107,53,0.07); border-left:4px solid {CHART_OPTIMIZE}; box-shadow:var(--sh-lg), 0 0 60px rgba(255,107,53,0.16); }}
.result-drop     {{ background:rgba(255,45,120,0.07); border-left:4px solid {CHART_DROP};     box-shadow:var(--sh-lg), 0 0 60px rgba(255,45,120,0.16); }}

/* DIVIDER LABEL ─────────────────────────────────────────────── */
.divider-label {{
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 34px 0 22px;
  color: var(--ink-faint);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}}
.divider-label::before, .divider-label::after {{
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(179,102,255,0.28), transparent);
}}

/* GLASS CHART WRAPPER ───────────────────────────────────────── */
.chart-glass {{
  background: rgba(255,255,255,0.035);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--r-md);
  padding: 22px;
  box-shadow: var(--sh-sm);
  transition: box-shadow 0.28s;
}}
.chart-glass:hover {{
  box-shadow: var(--sh-md), var(--glow-purple);
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
    fig.patch.set_facecolor("#07021a")
    fig.patch.set_alpha(0.94)
    ax.set_facecolor("#05010f")

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color((1, 1, 1, 0.08))
    ax.spines["bottom"].set_color((1, 1, 1, 0.08))

    ax.tick_params(colors=(1, 1, 1, 0.38), labelsize=8.5, length=0)
    ax.xaxis.label.set_color((1, 1, 1, 0.45))
    ax.yaxis.label.set_color((1, 1, 1, 0.45))
    ax.title.set_color("#ffffff")
    ax.title.set_fontsize(11.5)
    ax.title.set_fontweight("bold")
    ax.title.set_fontfamily("sans-serif")

    ax.grid(axis="y", color=(1, 1, 1, 0.045), linewidth=0.8, linestyle="--")
    ax.grid(axis="x", color=(1, 1, 1, 0.025), linewidth=0.5, linestyle=":")
    ax.set_axisbelow(True)

    for spine in ["left", "bottom"]:
        ax.spines[spine].set_linewidth(0.7)
    return fig, ax


def add_bar_glow(ax, bars, colors):
    import matplotlib.patches as mp
    import matplotlib.colors as mc
    for bar, color in zip(bars, colors):
        r, g, b, _ = mc.to_rgba(color)
        glow = mp.FancyBboxPatch(
            (bar.get_x() - bar.get_width() * 0.18, min(bar.get_y(), 0)),
            bar.get_width() * 1.36,
            abs(bar.get_height()),
            boxstyle="round,pad=0",
            facecolor=(r, g, b, 0.10),
            edgecolor="none",
            zorder=bar.get_zorder() - 1,
        )
        ax.add_patch(glow)


def col_seq(labels):
    return [DECISION_COLORS.get(l, "#CCCCCC") for l in labels]

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
        "<p style='font-size:0.65rem;color:rgba(255,255,255,0.38);margin-bottom:20px;"
        "font-weight:800;letter-spacing:0.14em;text-transform:uppercase;"
        "font-family:\"JetBrains Mono\",monospace'>Filter view</p>",
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
    <p style='font-size:0.62rem;color:rgba(255,255,255,0.38);font-weight:900;
    letter-spacing:0.16em;text-transform:uppercase;margin-bottom:14px;
    font-family:"JetBrains Mono",monospace'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:12px;font-size:0.82rem;color:rgba(255,255,255,0.68)'>
      <div style='display:flex;align-items:center;gap:12px'>
        <span class='pill pill-expand'>Expand</span>High profit &amp; demand
      </div>
      <div style='display:flex;align-items:center;gap:12px'>
        <span class='pill pill-maintain'>Maintain</span>Stable performer
      </div>
      <div style='display:flex;align-items:center;gap:12px'>
        <span class='pill pill-optimize'>Optimize</span>Room to improve
      </div>
      <div style='display:flex;align-items:center;gap:12px'>
        <span class='pill pill-drop'>Drop</span>Losing money
      </div>
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

    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
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

        wedges, texts, autotexts = ax.pie(
            dc.values,
            labels=dc.index,
            autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index],
            startangle=90,
            wedgeprops={"linewidth": 3, "edgecolor": "#07021a"},
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
        st.markdown(f"""
        <div class="info-box">
          <strong>How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:{COLOR_GREEN}">Expand</strong> routes should have the highest values across all three columns.
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
            edgecolor="#07021a",
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
            edgecolor="#07021a",
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
        edgecolor="#07021a",
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
                       color=CHART_EXPAND, edgecolor="#07021a", linewidth=1.5, height=0.52, zorder=3)
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
                       color=CHART_DROP, edgecolor="#07021a", linewidth=1.5, height=0.52, zorder=3)
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
        edgecolor="#07021a", linewidth=1.5, zorder=3,
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
                color=COLOR_ACCENT, edgecolor="#07021a", linewidth=1.5, zorder=3)
    b2 = ax.bar(x + w / 2, comparison["Macro F1"], w, label="Macro F1",
                color=COLOR_AMETHYST, edgecolor="#07021a", linewidth=1.5, zorder=3)
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

    # ── FORM ──────────────────────────────────────────────────
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                "<p style='font-size:0.65rem;font-weight:900;color:rgba(255,255,255,0.38);"
                "letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;"
                "font-family:\"JetBrains Mono\",monospace'>Flight basics</p>",
                unsafe_allow_html=True,
            )
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

        with col2:
            st.markdown(
                "<p style='font-size:0.65rem;font-weight:900;color:rgba(255,255,255,0.38);"
                "letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;"
                "font-family:\"JetBrains Mono\",monospace'>Route context</p>",
                unsafe_allow_html=True,
            )
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))

        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.65rem;font-weight:900;color:rgba(255,255,255,0.38);"
                    "letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;"
                    "font-family:\"JetBrains Mono\",monospace'>Revenue</p>",
                    unsafe_allow_html=True,
                )
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)

        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown(
                    "<p style='font-size:0.65rem;font-weight:900;color:rgba(255,255,255,0.38);"
                    "letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;"
                    "font-family:\"JetBrains Mono\",monospace'>Cost breakdown</p>",
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
          <div style='margin-bottom:14px'>
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Outfit",sans-serif;font-size:1.80rem;font-weight:900;
                      color:{text_col.get(pred, "#111")};margin-bottom:14px;letter-spacing:-0.03em;
                      text-shadow:0 0 40px {text_col.get(pred, "#111")}66'>
            Suggested Decision: {pred}
          </div>
          <p style='color:rgba(255,255,255,0.62);margin:0;font-size:0.92rem;line-height:1.78'>
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
            width=0.44, edgecolor="#07021a", linewidth=1.5, zorder=3,
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
<div style='text-align:center;color:rgba(255,255,255,0.28);font-size:0.70rem;
            padding:44px 0 22px;font-family:"JetBrains Mono",monospace;
            letter-spacing:0.10em'>
  ✦ &nbsp;SKYLENS ROUTE INTELLIGENCE&nbsp; · &nbsp;Built with Streamlit&nbsp; ✦
</div>
""", unsafe_allow_html=True)