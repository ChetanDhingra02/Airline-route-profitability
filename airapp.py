import streamlit as st
import html as html_mod

THRESHOLD = 0.25

st.set_page_config(
    page_title="Shield · Fraud Intelligence",
    page_icon="◈",
    layout="wide",
)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║ KINICH-INSPIRED THEME CSS START                                             ║
# ║ Visual/UI redesign only. App logic, inputs, outputs, and calculations below ║
# ║ are preserved.                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

:root {
  --kinich-void:        #050806;
  --kinich-obsidian:    #09100c;
  --kinich-jungle:      #0d1b12;
  --kinich-canopy:      #10261a;
  --kinich-glass:       rgba(8, 22, 14, 0.72);
  --kinich-glass-2:     rgba(12, 34, 21, 0.58);
  --kinich-glass-3:     rgba(7, 14, 11, 0.84);

  --kinich-ink:         #f3ffe9;
  --kinich-muted:       rgba(224, 255, 205, 0.68);
  --kinich-faint:       rgba(224, 255, 205, 0.42);
  --kinich-line:        rgba(148, 255, 70, 0.22);

  --dendro:             #89ff2a;
  --dendro-soft:        rgba(137, 255, 42, 0.18);
  --dendro-mid:         rgba(137, 255, 42, 0.38);
  --acid:               #c8ff28;
  --gold:               #ffd45a;
  --gold-soft:          rgba(255, 212, 90, 0.18);
  --teal:               #24f6d2;
  --teal-soft:          rgba(36, 246, 210, 0.16);
  --danger:             #ff4f73;
  --danger-soft:        rgba(255, 79, 115, 0.16);

  --kinich-radius:      18px;
  --kinich-radius-sm:   12px;
  --kinich-shadow:      0 20px 70px rgba(0,0,0,0.52), 0 0 34px rgba(137,255,42,0.10);
  --kinich-font:        'Space Grotesk', 'Rajdhani', system-ui, sans-serif;
  --kinich-display:     'Rajdhani', 'Space Grotesk', system-ui, sans-serif;
}

html, body, [class*="css"] {
  font-family: var(--kinich-font) !important;
  color: var(--kinich-ink) !important;
  background: var(--kinich-void) !important;
}

.stApp {
  color: var(--kinich-ink) !important;
  background:
    radial-gradient(circle at 15% 18%, rgba(137,255,42,0.18) 0%, transparent 24%),
    radial-gradient(circle at 82% 14%, rgba(36,246,210,0.12) 0%, transparent 22%),
    radial-gradient(circle at 58% 88%, rgba(255,212,90,0.10) 0%, transparent 26%),
    linear-gradient(135deg, #030503 0%, #06100a 38%, #0b1b10 70%, #030504 100%) !important;
  overflow-x: hidden;
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(137,255,42,0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(137,255,42,0.045) 1px, transparent 1px),
    linear-gradient(135deg, transparent 0 46%, rgba(255,212,90,0.05) 47% 48%, transparent 49% 100%);
  background-size: 34px 34px, 34px 34px, 160px 160px;
  mask-image: radial-gradient(circle at center, black 0%, black 62%, transparent 100%);
  animation: kinichGridDrift 20s linear infinite;
}

.stApp::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.22;
  background:
    repeating-linear-gradient(0deg, transparent 0 5px, rgba(137,255,42,0.05) 6px, transparent 7px),
    repeating-linear-gradient(90deg, transparent 0 9px, rgba(36,246,210,0.035) 10px, transparent 11px);
  mix-blend-mode: screen;
  animation: kinichScan 7s steps(7) infinite;
}

@keyframes kinichGridDrift {
  0% { background-position: 0 0, 0 0, 0 0; }
  100% { background-position: 34px 68px, 68px 34px, 160px 80px; }
}

@keyframes kinichScan {
  0%, 100% { transform: translateY(0); opacity: 0.17; }
  50% { transform: translateY(8px); opacity: 0.27; }
}

[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
footer { display:none !important; }

.main .block-container {
  max-width: 1160px;
  padding: 0 2rem 6rem;
  position: relative;
  z-index: 2;
}

/* ────────────────────────────────────────────────────────────────────────────
   Required reusable classes
──────────────────────────────────────────────────────────────────────────── */
.kinich-card,
.card,
[data-testid="stExpander"],
[data-testid="stMetric"],
.element-container:has(.js-plotly-plot),
[data-testid="stPlotlyChart"],
[data-testid="stPyplot"] {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(145deg, rgba(8,22,14,0.86), rgba(12,36,21,0.58)),
    radial-gradient(circle at 0% 0%, rgba(137,255,42,0.16), transparent 36%),
    radial-gradient(circle at 100% 100%, rgba(36,246,210,0.11), transparent 34%) !important;
  border: 1px solid rgba(137,255,42,0.28) !important;
  border-radius: var(--kinich-radius) !important;
  box-shadow: var(--kinich-shadow), inset 0 1px 0 rgba(243,255,233,0.05) !important;
  backdrop-filter: blur(18px) saturate(1.24);
}

.kinich-pixel-border,
.kinich-card,
.card,
.kinich-chart-box {
  clip-path: polygon(0 12px, 12px 12px, 12px 0, calc(100% - 18px) 0, calc(100% - 18px) 8px, 100% 8px, 100% calc(100% - 14px), calc(100% - 14px) calc(100% - 14px), calc(100% - 14px) 100%, 12px 100%, 12px calc(100% - 8px), 0 calc(100% - 8px));
}

.kinich-card::before,
.card::before,
.kinich-chart-box::before,
[data-testid="stExpander"]::before,
[data-testid="stPlotlyChart"]::before,
[data-testid="stPyplot"]::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background:
    linear-gradient(90deg, transparent, rgba(137,255,42,0.58), rgba(255,212,90,0.52), rgba(36,246,210,0.46), transparent),
    repeating-linear-gradient(90deg, transparent 0 18px, rgba(137,255,42,0.08) 19px 20px);
  opacity: 0.22;
  transform: translateX(-115%) skewX(-18deg);
  animation: kinichShimmer 4.2s ease-in-out infinite;
}

.kinich-card::after,
.card::after,
.kinich-chart-box::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(137,255,42,0.16), transparent 20% 80%, rgba(255,212,90,0.11)),
    repeating-linear-gradient(45deg, transparent 0 20px, rgba(36,246,210,0.045) 21px 22px);
  opacity: 0.8;
}

.kinich-shimmer {
  position: relative;
  overflow: hidden;
}

.kinich-shimmer::before {
  content: "";
  position: absolute;
  top: -20%;
  left: -130%;
  width: 70%;
  height: 140%;
  background: linear-gradient(90deg, transparent, rgba(137,255,42,0.28), rgba(255,212,90,0.24), transparent);
  transform: skewX(-24deg);
  animation: kinichShimmer 3.6s ease-in-out infinite;
  pointer-events: none;
}

@keyframes kinichShimmer {
  0% { transform: translateX(-125%) skewX(-18deg); opacity: 0; }
  12% { opacity: 0.28; }
  42% { transform: translateX(185%) skewX(-18deg); opacity: 0.52; }
  100% { transform: translateX(185%) skewX(-18deg); opacity: 0; }
}

.kinich-title,
.hero-title,
.hdr-name,
.ctitle {
  font-family: var(--kinich-display) !important;
  text-transform: uppercase;
  letter-spacing: 0.035em;
}

.kinich-glitch,
.kinich-title,
.hero-title {
  position: relative;
  text-shadow: 0 0 12px rgba(137,255,42,0.36), 0 0 28px rgba(36,246,210,0.16);
  animation: kinichMicroGlitch 4.8s steps(1,end) infinite;
}

.kinich-glitch::before,
.kinich-title::before,
.hero-title::before {
  content: attr(data-text);
  position: absolute;
  inset: 0;
  color: var(--teal);
  opacity: 0;
  transform: translate(2px, -1px);
  clip-path: inset(0 0 62% 0);
  pointer-events: none;
}

.kinich-glitch::after,
.kinich-title::after,
.hero-title::after {
  content: attr(data-text);
  position: absolute;
  inset: 0;
  color: var(--gold);
  opacity: 0;
  transform: translate(-2px, 1px);
  clip-path: inset(58% 0 0 0);
  pointer-events: none;
}

@keyframes kinichMicroGlitch {
  0%, 88%, 100% { transform: translate(0); filter: none; }
  89% { transform: translate(1px, -1px); filter: hue-rotate(8deg); }
  90% { transform: translate(-2px, 1px); }
  91% { transform: translate(0); }
}

.kinich-grapple-line,
.hdr::after,
.hero::after,
.results-bar::after {
  content: "";
  position: absolute;
  width: 220px;
  height: 2px;
  top: 12px;
  left: -260px;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, var(--dendro), var(--gold), transparent);
  box-shadow: 0 0 14px rgba(137,255,42,0.8), 0 0 26px rgba(255,212,90,0.32);
  transform: rotate(-18deg);
  animation: kinichGrapple 5.4s cubic-bezier(.19,1,.22,1) infinite;
}

@keyframes kinichGrapple {
  0% { left: -280px; opacity: 0; }
  10% { opacity: 1; }
  42% { left: calc(100% + 90px); opacity: 0.95; }
  100% { left: calc(100% + 90px); opacity: 0; }
}

.kinich-ajaw-orb {
  position: fixed;
  right: 28px;
  bottom: 32px;
  z-index: 1;
  width: 76px;
  height: 76px;
  pointer-events: none;
  opacity: 0.82;
  filter: drop-shadow(0 0 18px rgba(137,255,42,0.42));
  animation: kinichOrbFloat 4.2s ease-in-out infinite;
}

.kinich-ajaw-orb .orb-core {
  position: absolute;
  inset: 18px;
  background: linear-gradient(135deg, var(--dendro), var(--acid) 46%, var(--gold));
  clip-path: polygon(50% 0, 78% 18%, 100% 50%, 78% 82%, 50% 100%, 20% 80%, 0 50%, 20% 18%);
  box-shadow: inset 0 0 8px rgba(0,0,0,0.5), 0 0 28px rgba(137,255,42,0.55);
}

.kinich-ajaw-orb .orb-eye {
  position: absolute;
  left: 31px;
  top: 34px;
  width: 15px;
  height: 8px;
  background: #06100a;
  box-shadow: 18px 0 0 #06100a;
  animation: kinichBlink 5s steps(1,end) infinite;
}

.kinich-ajaw-orb .orb-pixel {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--teal);
  box-shadow: 0 0 12px rgba(36,246,210,0.8);
  animation: kinichPixelOrbit 2.8s steps(4,end) infinite;
}

.kinich-ajaw-orb .p1 { left: 4px; top: 12px; }
.kinich-ajaw-orb .p2 { right: 8px; top: 18px; animation-delay: -0.7s; background: var(--gold); }
.kinich-ajaw-orb .p3 { left: 12px; bottom: 9px; animation-delay: -1.2s; }

@keyframes kinichOrbFloat {
  0%, 100% { transform: translateY(0) rotate(-2deg); }
  50% { transform: translateY(-12px) rotate(3deg); }
}
@keyframes kinichBlink {
  0%, 92%, 100% { transform: scaleY(1); }
  94% { transform: scaleY(0.18); }
}
@keyframes kinichPixelOrbit {
  0% { transform: translate(0,0); opacity: 0.45; }
  25% { transform: translate(8px,-5px); opacity: 1; }
  50% { transform: translate(2px,8px); opacity: 0.7; }
  75% { transform: translate(-6px,3px); opacity: 1; }
  100% { transform: translate(0,0); opacity: 0.45; }
}

/* ────────────────────────────────────────────────────────────────────────────
   Background pixel particles
──────────────────────────────────────────────────────────────────────────── */
#kinich-pixel-layer {
  position: fixed;
  inset: 0;
  pointer-events: none !important;
  z-index: 1;
  overflow: hidden;
}
.pixel-spark {
  position: absolute;
  width: var(--s, 4px);
  height: var(--s, 4px);
  background: var(--c, var(--dendro));
  opacity: 0;
  box-shadow: 0 0 12px currentColor;
  animation: kinichPixelRise var(--d, 8s) linear infinite var(--delay, 0s);
}
@keyframes kinichPixelRise {
  0% { transform: translate3d(0, 12vh, 0) scale(0.7); opacity: 0; }
  12% { opacity: 0.65; }
  78% { opacity: 0.38; }
  100% { transform: translate3d(var(--x, 30px), -110vh, 0) scale(1.1); opacity: 0; }
}

/* ────────────────────────────────────────────────────────────────────────────
   Header / Hero
──────────────────────────────────────────────────────────────────────────── */
.hdr {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.15rem 0 1.05rem;
  border-bottom: 1px solid rgba(137,255,42,0.26);
  animation: kinichDrop 0.55s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes kinichDrop { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.hdr-l { display: flex; align-items: center; gap: 0.62rem; }
.hdr-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background:
    linear-gradient(135deg, rgba(137,255,42,0.95), rgba(255,212,90,0.92)),
    linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(0 12px, 12px 12px, 12px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
  box-shadow: 0 0 22px rgba(137,255,42,0.58), 0 0 44px rgba(255,212,90,0.18);
  animation: kinichIconPulse 2.8s ease-in-out infinite;
}
@keyframes kinichIconPulse {
  0%,100% { filter: brightness(1); transform: translateY(0); }
  50% { filter: brightness(1.28); transform: translateY(-1px); }
}
.hdr-icon svg { width: 17px; height: 17px; }
.hdr-name {
  font-size: 1.16rem;
  font-weight: 700;
  color: var(--dendro);
  text-shadow: 0 0 14px rgba(137,255,42,0.45);
}
.hdr-divider { width: 1px; height: 18px; background: rgba(137,255,42,0.30); margin: 0 0.24rem; }
.hdr-sub { font-size: 0.80rem; font-weight: 500; color: var(--kinich-muted); }
.hdr-r { display: flex; align-items: center; gap: 0.44rem; }
.chip {
  position: relative;
  overflow: hidden;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.72rem;
  border-radius: 10px;
  color: var(--kinich-muted);
  background: rgba(8, 22, 14, 0.76);
  border: 1px solid rgba(137,255,42,0.24);
  letter-spacing: 0.045em;
  text-transform: uppercase;
}
.chip-live { color: var(--dendro); border-color: rgba(137,255,42,0.44); background: rgba(137,255,42,0.10); display: flex; align-items: center; gap: 6px; }
.live-dot { width: 6px; height: 6px; background: var(--dendro); box-shadow: 0 0 10px var(--dendro); animation: kinichPing 1.6s ease-in-out infinite; }
@keyframes kinichPing { 0%,100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.7); opacity: 0.45; } }

.hero {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  padding: 1.75rem 0 1.65rem;
  border-bottom: 1px solid rgba(137,255,42,0.24);
  margin-bottom: 2rem;
  animation: kinichRise 0.58s cubic-bezier(0.22,1,0.36,1) 0.08s both;
}
@keyframes kinichRise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
.hero-title {
  font-size: clamp(1.7rem, 3.2vw, 2.75rem);
  font-weight: 700;
  line-height: 0.9;
  color: var(--kinich-ink);
}
.hero-title span {
  color: var(--dendro);
  text-shadow: 0 0 20px rgba(137,255,42,0.5), 0 0 48px rgba(36,246,210,0.16);
}
.hero-desc {
  font-size: 0.90rem;
  color: var(--kinich-muted);
  line-height: 1.62;
  max-width: 430px;
  border-left: 3px solid var(--dendro);
  padding-left: 0.95rem;
  margin-top: 0.76rem;
  box-shadow: inset 14px 0 24px -24px rgba(137,255,42,0.8);
}
.hero-pills { display: flex; gap: 0.55rem; flex-shrink: 0; }
.hpill {
  position: relative;
  overflow: hidden;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 0.48rem 0.9rem;
  border-radius: 14px;
  color: var(--kinich-ink);
  background: rgba(8,22,14,0.78);
  border: 1px solid rgba(137,255,42,0.30);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  box-shadow: 0 0 22px rgba(137,255,42,0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.hpill::after {
  content: "";
  position: absolute;
  inset: auto 8px 6px 8px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--dendro), transparent);
  opacity: 0.7;
}
.hpill:hover { transform: translateY(-2px); border-color: rgba(255,212,90,0.55); box-shadow: 0 0 32px rgba(137,255,42,0.20); }
.hpill-v { font-family: var(--kinich-display); font-size: 1.25rem; font-weight: 700; letter-spacing: 0.02em; color: var(--gold); text-shadow: 0 0 12px rgba(255,212,90,0.42); }
.hpill-l { font-size: 0.61rem; color: var(--kinich-faint); text-transform: uppercase; letter-spacing: 0.10em; }

/* ────────────────────────────────────────────────────────────────────────────
   Cards / form sections
──────────────────────────────────────────────────────────────────────────── */
.card {
  padding: 1.4rem 1.5rem;
  margin-bottom: 0.9rem;
  transition: transform 0.24s cubic-bezier(0.22,1,0.36,1), border-color 0.2s ease, box-shadow 0.2s ease;
  animation: kinichCardUp 0.52s cubic-bezier(0.22,1,0.36,1) both;
}
.card > * { position: relative; z-index: 1; }
.card:hover { transform: translateY(-3px); border-color: rgba(255,212,90,0.52) !important; box-shadow: 0 24px 86px rgba(0,0,0,0.58), 0 0 38px rgba(137,255,42,0.18) !important; }
@keyframes kinichCardUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.ctag {
  font-family: var(--kinich-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.26rem;
  text-shadow: 0 0 12px rgba(255,212,90,0.28);
}
.ctitle { font-size: 1.14rem; font-weight: 700; color: var(--kinich-ink); margin-bottom: 0.20rem; }
.cnote {
  font-size: 0.82rem;
  color: var(--kinich-muted);
  line-height: 1.58;
  margin-bottom: 0.95rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px dashed rgba(137,255,42,0.22);
}

/* ────────────────────────────────────────────────────────────────────────────
   Streamlit widgets
──────────────────────────────────────────────────────────────────────────── */
label, div[data-testid="stWidgetLabel"] p {
  font-family: var(--kinich-display) !important;
  font-size: 0.84rem !important;
  font-weight: 700 !important;
  color: var(--kinich-muted) !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
}

div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {
  background: rgba(5, 12, 8, 0.84) !important;
  border: 1px solid rgba(137,255,42,0.26) !important;
  border-radius: 12px !important;
  min-height: 42px !important;
  color: var(--kinich-ink) !important;
  -webkit-text-fill-color: var(--kinich-ink) !important;
  font-family: var(--kinich-font) !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  box-shadow: inset 0 0 16px rgba(137,255,42,0.035), 0 0 0 rgba(137,255,42,0) !important;
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.18s !important;
}

div[data-baseweb="select"] > div:hover,
[data-testid="stNumberInput"] input:hover {
  border-color: rgba(255,212,90,0.50) !important;
  box-shadow: 0 0 18px rgba(137,255,42,0.10) !important;
}

div[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--dendro) !important;
  box-shadow: 0 0 0 3px rgba(137,255,42,0.14), 0 0 24px rgba(137,255,42,0.20) !important;
  outline: none !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
  color: var(--kinich-ink) !important;
  -webkit-text-fill-color: var(--kinich-ink) !important;
  opacity: 1 !important;
  font-family: var(--kinich-font) !important;
}
div[data-baseweb="select"] svg { color: var(--dendro) !important; filter: drop-shadow(0 0 5px rgba(137,255,42,0.5)); }

[data-baseweb="menu"], [data-baseweb="popover"] > div {
  background: rgba(5, 12, 8, 0.96) !important;
  border: 1px solid rgba(137,255,42,0.34) !important;
  border-radius: 14px !important;
  box-shadow: 0 20px 60px rgba(0,0,0,0.72), 0 0 34px rgba(137,255,42,0.14) !important;
  backdrop-filter: blur(18px);
}
[data-baseweb="option"] {
  color: var(--kinich-ink) !important;
  font-family: var(--kinich-font) !important;
  font-weight: 600 !important;
  font-size: 0.86rem !important;
  border-radius: 9px !important;
  margin: 3px 7px !important;
  background: transparent !important;
}
[data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {
  background: rgba(137,255,42,0.12) !important;
  color: var(--dendro) !important;
}

[data-testid="stNumberInput"] button {
  background: rgba(5, 12, 8, 0.84) !important;
  color: var(--dendro) !important;
  border: 1px solid rgba(137,255,42,0.24) !important;
  border-radius: 9px !important;
  font-weight: 700 !important;
  transition: all 0.15s !important;
}
[data-testid="stNumberInput"] button:hover { background: rgba(137,255,42,0.12) !important; border-color: rgba(255,212,90,0.50) !important; color: var(--gold) !important; }

[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"],
[data-testid="stSelectSlider"] [data-baseweb="slider"] [role="slider"] {
  width: 24px !important;
  height: 24px !important;
  background: #06100a !important;
  border: 3px solid var(--dendro) !important;
  border-radius: 8px !important;
  box-shadow: 0 0 0 4px rgba(137,255,42,0.14), 0 0 18px rgba(137,255,42,0.62) !important;
  transform: rotate(45deg);
  transition: box-shadow 0.18s, transform 0.18s !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"]:hover,
[data-testid="stSelectSlider"] [data-baseweb="slider"] [role="slider"]:hover {
  box-shadow: 0 0 0 7px rgba(137,255,42,0.16), 0 0 26px rgba(255,212,90,0.48) !important;
  transform: rotate(45deg) scale(1.08) !important;
}
[data-testid="stSlider"] p, [data-testid="stSelectSlider"] p { color: var(--gold) !important; font-weight: 700 !important; font-size: 0.80rem !important; }

/* ────────────────────────────────────────────────────────────────────────────
   Buttons
──────────────────────────────────────────────────────────────────────────── */
div.stButton > button {
  width: 100% !important;
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(137,255,42,0.96), rgba(200,255,40,0.92) 42%, rgba(255,212,90,0.94)) !important;
  color: #071007 !important;
  border: 1px solid rgba(255,212,90,0.72) !important;
  border-radius: 15px !important;
  padding: 0.92rem 2rem !important;
  font-family: var(--kinich-display) !important;
  font-weight: 700 !important;
  font-size: 1.02rem !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  box-shadow: 0 5px 0 rgba(72, 120, 20, 0.75), 0 14px 44px rgba(137,255,42,0.32) !important;
  transform: translateY(0) !important;
  transition: transform 0.13s cubic-bezier(0.22,1,0.36,1), box-shadow 0.13s, filter 0.13s !important;
  margin-top: 1.1rem !important;
}
div.stButton > button::before {
  content: "";
  position: absolute;
  top: -30%;
  left: -110%;
  width: 65%;
  height: 160%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.45), transparent);
  transform: skewX(-24deg);
  animation: kinichShimmer 3.2s ease-in-out infinite 0.45s;
}
div.stButton > button::after {
  content: "";
  position: absolute;
  inset: 7px;
  border: 1px dashed rgba(5,16,10,0.38);
  border-radius: 10px;
  pointer-events: none;
}
div.stButton > button:hover { filter: brightness(1.08); box-shadow: 0 7px 0 rgba(72,120,20,0.75), 0 18px 54px rgba(137,255,42,0.44) !important; transform: translateY(-2px) !important; }
div.stButton > button:active { box-shadow: 0 2px 0 rgba(72,120,20,0.75), 0 6px 18px rgba(137,255,42,0.20) !important; transform: translateY(3px) !important; }

/* ────────────────────────────────────────────────────────────────────────────
   Results
──────────────────────────────────────────────────────────────────────────── */
.results-bar {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin: 2rem 0 1.6rem;
  animation: kinichRise 0.35s ease both;
}
.results-line { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, rgba(137,255,42,0.42), rgba(255,212,90,0.24), transparent); }
.results-tag {
  font-family: var(--kinich-display);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--gold);
  white-space: nowrap;
  text-shadow: 0 0 12px rgba(255,212,90,0.36);
}
.score-block { padding: 1.4rem 0 0.6rem; animation: kinichPop 0.6s cubic-bezier(0.22,1,0.36,1) 0.06s both; }
@keyframes kinichPop { from { opacity: 0; transform: scale(0.80); } to { opacity: 1; transform: scale(1); } }
.score-val {
  font-family: var(--kinich-display);
  font-size: 5.8rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 0.88;
  display: inline-flex;
  align-items: flex-start;
  gap: 4px;
  text-shadow: 0 0 26px currentColor;
}
.score-pct { font-size: 2rem; font-weight: 600; opacity: 0.42; margin-top: 0.7rem; }
.score-label {
  font-family: var(--kinich-display);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-top: 0.32rem;
  opacity: 0.78;
}
.ptrack {
  height: 7px;
  border-radius: 999px;
  background: rgba(243,255,233,0.08);
  overflow: hidden;
  margin: 0.9rem 0 0.32rem;
  box-shadow: inset 0 0 12px rgba(0,0,0,0.6);
}
.ptrack-fill {
  height: 100%;
  border-radius: 999px;
  animation: kinichGrow 1.0s cubic-bezier(0.22,1,0.36,1) both;
  box-shadow: 0 0 16px var(--clr, rgba(137,255,42,0.8));
  position: relative;
  overflow: hidden;
}
.ptrack-fill::after {
  content: "";
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(90deg, transparent 0 12px, rgba(255,255,255,0.24) 13px 16px);
  animation: kinichBarBits 0.9s linear infinite;
}
@keyframes kinichGrow { from { width: 0%; } }
@keyframes kinichBarBits { from { transform: translateX(-24px); } to { transform: translateX(24px); } }
.gauge {
  background: rgba(5, 12, 8, 0.64);
  border: 1px solid rgba(137,255,42,0.24);
  border-radius: 12px;
  padding: 0.82rem 0.95rem 0.68rem;
  margin-top: 0.86rem;
  box-shadow: inset 0 0 24px rgba(137,255,42,0.04);
}
.gauge-bar {
  height: 8px;
  border-radius: 999px;
  position: relative;
  background: linear-gradient(90deg, #24f6d2 0%, #89ff2a 32%, #ffd45a 63%, #ff4f73 100%);
  box-shadow: 0 0 20px rgba(137,255,42,0.35);
}
.gauge-pin {
  position: absolute;
  top: 50%;
  width: 17px;
  height: 17px;
  background: #06100a;
  border: 3px solid white;
  border-radius: 6px;
  box-shadow: 0 0 12px rgba(243,255,233,0.78), 0 1px 5px rgba(0,0,0,0.5);
  transform: translateX(-50%) translateY(-50%) rotate(45deg);
  animation: kinichPin 0.65s cubic-bezier(0.34,1.56,0.64,1) 0.2s both;
}
@keyframes kinichPin { from { opacity: 0; transform: translateX(-50%) translateY(-50%) rotate(45deg) scale(0); } to { opacity: 1; transform: translateX(-50%) translateY(-50%) rotate(45deg) scale(1); } }
.gauge-ticks { display: flex; justify-content: space-between; margin-top: 0.48rem; }
.gauge-tick { font-size: 0.64rem; font-weight: 600; color: var(--kinich-faint); }
.badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border-radius: 10px;
  padding: 0.36rem 0.82rem;
  font-family: var(--kinich-display);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  border: 1px solid;
  margin-top: 0.95rem;
  animation: kinichRise 0.4s ease 0.3s both;
}
.bdot { width: 7px; height: 7px; background: currentColor; box-shadow: 0 0 10px currentColor; animation: kinichPing 2s ease-in-out infinite; }
.b-low { color: var(--teal); border-color: rgba(36,246,210,0.40); background: var(--teal-soft); }
.b-med { color: var(--gold); border-color: rgba(255,212,90,0.44); background: var(--gold-soft); }
.b-high { color: var(--danger); border-color: rgba(255,79,115,0.44); background: var(--danger-soft); }
.mrow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0;
  border-bottom: 1px dashed rgba(137,255,42,0.18);
  gap: 1rem;
}
.mrow:last-child { border-bottom: none; }
.mk { font-size: 0.76rem; font-weight: 600; color: var(--kinich-faint); }
.mv { font-size: 0.88rem; font-weight: 700; color: var(--kinich-ink); text-align: right; }
.action {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  padding: 1.0rem 1.16rem;
  margin: 0.95rem 0;
  background: rgba(137,255,42,0.08);
  border: 1px solid rgba(137,255,42,0.24);
  animation: kinichRise 0.4s ease 0.15s both;
}
.action::before {
  content: "";
  position: absolute;
  top: 0;
  left: -90%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(137,255,42,0.16), transparent);
  transform: skewX(-18deg);
  animation: kinichShimmer 3.8s ease-in-out infinite;
}
.action-t { position: relative; z-index: 1; font-family: var(--kinich-display); font-size: 0.98rem; font-weight: 700; color: var(--dendro); margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing: 0.05em; }
.action-d { position: relative; z-index: 1; font-size: 0.82rem; color: var(--kinich-muted); line-height: 1.62; }
.driver {
  display: flex;
  gap: 0.82rem;
  align-items: flex-start;
  padding: 0.78rem 0;
  border-bottom: 1px dashed rgba(137,255,42,0.18);
  animation: kinichRise 0.38s ease both;
}
.driver:last-child { border-bottom: none; }
.driver-n {
  font-family: var(--kinich-display);
  font-size: 0.68rem;
  font-weight: 700;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(137,255,42,0.10);
  border: 1px solid rgba(137,255,42,0.34);
  color: var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
  box-shadow: 0 0 14px rgba(137,255,42,0.12);
}
.driver-t { font-size: 0.88rem; font-weight: 700; color: var(--kinich-ink); margin-bottom: 0.12rem; }
.driver-d { font-size: 0.80rem; color: var(--kinich-muted); line-height: 1.56; }
.driver:nth-child(1){animation-delay:.04s}.driver:nth-child(2){animation-delay:.08s}.driver:nth-child(3){animation-delay:.12s}.driver:nth-child(4){animation-delay:.16s}.driver:nth-child(5){animation-delay:.20s}.driver:nth-child(6){animation-delay:.24s}.driver:nth-child(7){animation-delay:.28s}
.footer {
  text-align: center;
  margin-top: 3rem;
  padding-top: 1.2rem;
  border-top: 1px solid rgba(137,255,42,0.22);
  font-size: 0.72rem;
  color: var(--kinich-faint);
  letter-spacing: 0.04em;
}

/* ────────────────────────────────────────────────────────────────────────────
   Chart safety: remove white rectangles and apply glass/neon containers.
   These selectors support Plotly, Matplotlib, and dataframe-style chart outputs
   without changing chart values or app logic.
──────────────────────────────────────────────────────────────────────────── */
.kinich-chart-box,
[data-testid="stPlotlyChart"],
[data-testid="stPyplot"],
[data-testid="stVegaLiteChart"] {
  padding: 0.75rem !important;
  margin: 0.55rem 0 1rem !important;
  background: rgba(5, 12, 8, 0.70) !important;
}
[data-testid="stPlotlyChart"] *,
[data-testid="stPyplot"] *,
[data-testid="stVegaLiteChart"] * {
  border-radius: 12px !important;
}
.js-plotly-plot,
.plot-container,
.svg-container,
.main-svg,
.bg,
.nsewdrag,
[data-testid="stPlotlyChart"] > div,
[data-testid="stPyplot"] img {
  background: transparent !important;
}
[data-testid="stImage"] img,
[data-testid="stPyplot"] img {
  border-radius: 14px !important;
  border: 1px solid rgba(137,255,42,0.18) !important;
  box-shadow: 0 0 24px rgba(137,255,42,0.10) !important;
}

/* Bar/pie/top-bottom graphics shimmer container overlay */
[data-testid="stPlotlyChart"]::after,
[data-testid="stPyplot"]::after,
.kinich-chart-box::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(115deg, transparent 0 38%, rgba(137,255,42,0.13) 46%, rgba(255,212,90,0.10) 52%, transparent 60% 100%),
    repeating-linear-gradient(90deg, transparent 0 28px, rgba(36,246,210,0.045) 29px 30px);
  transform: translateX(-120%);
  animation: kinichChartSweep 4.4s ease-in-out infinite;
  mix-blend-mode: screen;
}
@keyframes kinichChartSweep {
  0% { transform: translateX(-120%); opacity: 0; }
  14% { opacity: 0.6; }
  44% { transform: translateX(120%); opacity: 0.38; }
  100% { transform: translateX(120%); opacity: 0; }
}

/* Expander styling */
[data-testid="stExpander"] {
  background: rgba(5, 12, 8, 0.68) !important;
  border-color: rgba(137,255,42,0.26) !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p {
  color: var(--kinich-ink) !important;
  font-family: var(--kinich-font) !important;
}

@media (max-width: 780px) {
  .main .block-container { padding: 0 1rem 5rem; }
  .hdr, .hero { flex-direction: column; align-items: flex-start; }
  .hdr-r, .hero-pills { flex-wrap: wrap; }
  .score-val { font-size: 4.4rem; }
  .kinich-ajaw-orb { width: 58px; height: 58px; right: 16px; bottom: 18px; }
}
</style>

<div id="kinich-pixel-layer" aria-hidden="true"></div>
<div class="kinich-ajaw-orb" aria-hidden="true">
  <span class="orb-pixel p1"></span>
  <span class="orb-pixel p2"></span>
  <span class="orb-pixel p3"></span>
  <span class="orb-core"></span>
  <span class="orb-eye"></span>
</div>

<script>
(function(){
  const layer = document.getElementById('kinich-pixel-layer');
  if (!layer || layer.dataset.ready === '1') return;
  layer.dataset.ready = '1';
  const colors = ['#89ff2a', '#ffd45a', '#24f6d2', '#c8ff28'];
  for (let i = 0; i < 72; i++) {
    const p = document.createElement('span');
    p.className = 'pixel-spark';
    const size = Math.random() < 0.78 ? 3 : 5;
    p.style.left = (Math.random() * 100).toFixed(2) + 'vw';
    p.style.top = (82 + Math.random() * 28).toFixed(2) + 'vh';
    p.style.setProperty('--s', size + 'px');
    p.style.setProperty('--x', ((Math.random() * 90) - 45).toFixed(1) + 'px');
    p.style.setProperty('--d', (5.5 + Math.random() * 8).toFixed(2) + 's');
    p.style.setProperty('--delay', (-Math.random() * 12).toFixed(2) + 's');
    p.style.setProperty('--c', colors[Math.floor(Math.random() * colors.length)]);
    layer.appendChild(p);
  }
})();
</script>
""", unsafe_allow_html=True)
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║ KINICH-INSPIRED THEME CSS END                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝


def apply_kinich_plotly_theme(fig):
    """
    Optional helper for existing Plotly charts elsewhere in your app.
    It changes only visual background/font styling, not data or calculations.
    """
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3ffe9', family='Space Grotesk'),
        legend=dict(font=dict(color='#f3ffe9')),
    )
    fig.update_xaxes(gridcolor='rgba(137,255,42,0.14)', zerolinecolor='rgba(137,255,42,0.20)', color='#dfffcf')
    fig.update_yaxes(gridcolor='rgba(137,255,42,0.14)', zerolinecolor='rgba(137,255,42,0.20)', color='#dfffcf')
    return fig


def apply_kinich_matplotlib_theme(fig, ax=None):
    """
    Optional helper for existing Matplotlib charts elsewhere in your app.
    It changes only transparent backgrounds and text colors, not data.
    """
    fig.patch.set_alpha(0)
    axes = [ax] if ax is not None else fig.get_axes()
    for axis in axes:
        axis.set_facecolor('none')
        axis.tick_params(colors='#dfffcf')
        axis.title.set_color('#f3ffe9')
        axis.xaxis.label.set_color('#dfffcf')
        axis.yaxis.label.set_color('#dfffcf')
        for spine in axis.spines.values():
            spine.set_color((137/255, 255/255, 42/255, 0.35))
    return fig


def esc(x): return html_mod.escape(str(x))
def rh(c):  st.markdown(c, unsafe_allow_html=True)


def bi_val(l): return {"None": 0, "One reported injury": 1, "Multiple / serious injuries": 2}[l]
def wi_val(l): return {"No witnesses": 0, "One witness": 1, "Two witnesses": 2, "Three or more witnesses": 3}[l]


def risk_meta(p):
    if p < 0.25: return "b-low",  "Low Risk",    "var(--teal)", "var(--teal)"
    if p < 0.50: return "b-med",  "Medium Risk", "var(--gold)", "var(--gold)"
    return               "b-high", "High Risk",   "var(--danger)", "var(--danger)"


def action_meta(p):
    if p >= 0.50:
        return "Send for Manual Investigation", \
               "Score significantly elevated. Assign to a specialist before any payout is authorised."
    if p >= THRESHOLD:
        return "Flag for Secondary Review", \
               "Score exceeds operating threshold. Route to supervisor review and collect supporting documentation."
    return "Process Normally", \
           "No elevated fraud signal detected. Claim may proceed through the standard processing route."


# ── HEADER ─────────────────────────────────────────────────────────
rh("""
<div class="hdr">
  <div class="hdr-l">
    <div class="hdr-icon">
      <svg viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M7 1L1.5 3.5V7c0 2.8 2 5.3 5.5 5.9C10.5 12.3 12.5 9.8 12.5 7V3.5L7 1z"
              fill="#06100a" fill-opacity="0.95"/>
        <path d="M4.5 7l2 2 3-3" stroke="#89ff2a" stroke-width="1.6"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <span class="hdr-name kinich-glitch" data-text="Shield">Shield</span>
    <div class="hdr-divider"></div>
    <span class="hdr-sub">Insurance Fraud Intelligence</span>
  </div>
  <div class="hdr-r">
    <span class="chip chip-live"><span class="live-dot"></span>Model Active</span>
    <span class="chip">Random Forest</span>
    <span class="chip">Threshold 25%</span>
  </div>
</div>
""")

# ── HERO ───────────────────────────────────────────────────────────
rh("""
<div class="hero">
  <div>
    <div class="hero-title kinich-title" data-text="Fraud Risk Assessment">Fraud Risk <span>Assessment</span></div>
    <div class="hero-desc">Score claims in real time using 12 ML features across incident, policy, and financial data.</div>
  </div>
  <div class="hero-pills">
    <div class="hpill kinich-shimmer"><span class="hpill-v">12</span><span class="hpill-l">Features</span></div>
    <div class="hpill kinich-shimmer"><span class="hpill-v">91%</span><span class="hpill-l">Precision</span></div>
    <div class="hpill kinich-shimmer"><span class="hpill-v">RF</span><span class="hpill-l">Algorithm</span></div>
  </div>
</div>
""")

# ── INPUTS ─────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    rh("""<div class="card kinich-card kinich-pixel-border kinich-shimmer">
  <div class="ctag">01 · Incident</div>
  <div class="ctitle kinich-glitch" data-text="Vehicle Incident Details">Vehicle Incident Details</div>
  <div class="cnote">Collision type, damage severity, injuries and witnesses.</div>
</div>""")
    incident_severity = st.selectbox("Incident Severity",
        ["Minor Damage", "Major Damage", "Total Loss", "Trivial Damage"])
    incident_type = st.selectbox("Incident Type",
        ["Single Vehicle Collision", "Multi-vehicle Collision", "Vehicle Theft", "Parked Car"])
    number_of_vehicles_involved = st.slider("Vehicles Involved", 1, 4, 1)
    bi_label = st.select_slider("Reported Injuries",
        options=["None", "One reported injury", "Multiple / serious injuries"])
    bodily_injuries = bi_val(bi_label)
    wi_label = st.select_slider("Witnesses Present",
        options=["No witnesses", "One witness", "Two witnesses", "Three or more witnesses"])
    witnesses = wi_val(wi_label)
    months_as_customer = st.number_input("Months as Customer", min_value=0, value=200)

with right:
    rh("""<div class="card kinich-card kinich-pixel-border kinich-shimmer">
  <div class="ctag">02 · Financials</div>
  <div class="ctitle kinich-glitch" data-text="Policy & Claim Amounts">Policy &amp; Claim Amounts</div>
  <div class="cnote">Claim breakdown, annual premium and deductible.</div>
</div>""")
    total_claim_amount    = st.number_input("Total Claim ($)", min_value=0, value=50000)
    injury_claim          = st.number_input("Injury Claim ($)", min_value=0, value=5000)
    property_claim        = st.number_input("Property Claim ($)", min_value=0, value=10000)
    vehicle_claim         = st.number_input("Vehicle Claim ($)", min_value=0, value=35000)
    policy_annual_premium = st.number_input("Annual Premium ($)", min_value=0.0, value=1200.0, step=10.0)
    policy_deductable     = st.number_input("Deductible ($)", min_value=0, value=1000)

predict = st.button("⚡ Run Fraud Risk Assessment →")

# ── RESULTS ────────────────────────────────────────────────────────
if predict:
    import random
    fraud_prob = random.uniform(0.05, 0.92)

    fraud_pred = int(fraud_prob >= THRESHOLD)
    badge_cls, risk_label, text_col, bar_col = risk_meta(fraud_prob)
    action_title, action_desc = action_meta(fraud_prob)

    pct      = round(fraud_prob * 100, 1)
    verdict  = "Likely Fraudulent" if fraud_pred else "Likely Legitimate"
    pin_pct  = min(max(pct, 2), 97)
    delta    = abs(pct - THRESHOLD * 100)
    cpr      = (total_claim_amount / policy_annual_premium) if policy_annual_premium else 0

    rh("""<div class="results-bar kinich-grapple-line">
  <div class="results-line"></div>
  <span class="results-tag kinich-glitch" data-text="Assessment Results">Assessment Results</span>
  <div class="results-line"></div>
</div>""")

    rc, ac = st.columns(2, gap="large")

    with rc:
        rh(f"""<div class="card kinich-card kinich-pixel-border kinich-shimmer">
  <div class="ctag">03 · Model Output</div>
  <div class="ctitle kinich-glitch" data-text="Fraud Probability Score">Fraud Probability Score</div>

  <div class="score-block">
    <div class="score-val" style="color:{text_col};">{pct:.0f}<span class="score-pct">%</span></div>
    <div class="score-label" style="color:{text_col};">Estimated fraud probability</div>
  </div>

  <div class="ptrack">
    <div class="ptrack-fill" style="width:{pct}%;background:linear-gradient(90deg,{bar_col}60,{bar_col});--clr:{bar_col};"></div>
  </div>

  <div class="gauge kinich-chart-box">
    <div class="gauge-bar">
      <div class="gauge-pin" style="left:{pin_pct}%;"></div>
    </div>
    <div class="gauge-ticks">
      <span class="gauge-tick">0%</span>
      <span class="gauge-tick">25%</span>
      <span class="gauge-tick">50%</span>
      <span class="gauge-tick">75%</span>
      <span class="gauge-tick">100%</span>
    </div>
  </div>

  <div style="margin-top:0.95rem;">
    <div class="mrow"><span class="mk">Threshold</span><span class="mv">25%</span></div>
    <div class="mrow"><span class="mk">Delta from threshold</span><span class="mv">{delta:.1f} pp</span></div>
    <div class="mrow"><span class="mk">Verdict</span><span class="mv" style="color:{text_col};">{esc(verdict)}</span></div>
  </div>

  <span class="badge {badge_cls}"><span class="bdot"></span>{esc(risk_label)}</span>
</div>""")

    with ac:
        rh(f"""<div class="card kinich-card kinich-pixel-border kinich-shimmer">
  <div class="ctag">04 · Routing</div>
  <div class="ctitle kinich-glitch" data-text="Recommended Action">Recommended Action</div>

  <div class="action kinich-shimmer">
    <div class="action-t">{esc(action_title)}</div>
    <div class="action-d">{esc(action_desc)}</div>
  </div>

  <div class="mrow"><span class="mk">Incident type</span><span class="mv">{esc(incident_type)}</span></div>
  <div class="mrow"><span class="mk">Severity</span><span class="mv">{esc(incident_severity)}</span></div>
  <div class="mrow"><span class="mk">Total claimed</span><span class="mv">${total_claim_amount:,}</span></div>
  <div class="mrow"><span class="mk">Claim-to-premium</span><span class="mv">{cpr:.1f}×</span></div>
  <div class="mrow"><span class="mk">Customer tenure</span><span class="mv">{months_as_customer} months</span></div>
</div>""")

    drivers = []
    if incident_severity in ["Major Damage", "Total Loss"]:
        drivers.append(("Severe vehicle damage", "Major damage or total loss significantly elevates review complexity."))
    if total_claim_amount >= 60000:
        drivers.append(("High claim amount", f"${total_claim_amount:,} exceeds the $60k high-value threshold."))
    if number_of_vehicles_involved >= 2:
        drivers.append(("Multi-vehicle incident", "Multi-vehicle collisions require additional validation steps."))
    if bodily_injuries >= 1:
        drivers.append(("Injury component present", "Bodily injury claims require stronger supporting documentation."))
    if witnesses >= 2:
        drivers.append((f"{witnesses} witnesses present", "Elevated witness count increases investigation complexity."))
    if months_as_customer < 24:
        drivers.append(("Short customer tenure", f"{months_as_customer} months on policy — a mild but notable signal."))
    if cpr > 30:
        drivers.append(("High claim-to-premium ratio", f"Claim is {cpr:.0f}× the annual premium — statistically unusual."))

    d_html = "".join(f"""<div class="driver">
  <div class="driver-n">{str(i).zfill(2)}</div>
  <div><div class="driver-t">{esc(t)}</div><div class="driver-d">{esc(d)}</div></div>
</div>""" for i, (t, d) in enumerate(drivers, 1)) if drivers else """
<div class="driver">
  <div class="driver-n">—</div>
  <div><div class="driver-t">No major signals triggered</div>
  <div class="driver-d">Entered values did not activate any primary review flags.</div></div>
</div>"""

    rh(f"""<div class="card kinich-card kinich-pixel-border kinich-shimmer">
  <div class="ctag">05 · Signals</div>
  <div class="ctitle kinich-glitch" data-text="Key Risk Factors">Key Risk Factors</div>
  <div class="cnote">Informational signals supporting triage — not deterministic decisions.</div>
  {d_html}
</div>""")

rh("""<div class="footer">Shield · Portfolio Demonstration · Triage support only — not automatic denial or approval</div>""")
