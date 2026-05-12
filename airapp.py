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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500;600&display=swap');
:root{--ink:#fbf7ff;--ink-soft:#ded6e8;--ink-muted:#b4a7c3;--glassA:rgba(26,25,42,.82);--glassB:rgba(52,45,76,.58);--edge:rgba(255,255,255,.28);--edge2:rgba(255,255,255,.48);--violet:#d9b5ff;--pink:#ff91cf;--blue:#7dd3fc;--r:30px;}
html,body,[class*="css"]{font-family:'Manrope',system-ui,sans-serif!important;color:var(--ink)!important;-webkit-font-smoothing:antialiased;scroll-behavior:smooth}.stApp{background:#050612!important;min-height:100vh!important;position:relative!important;overflow:hidden!important}.stApp:before{content:"";position:fixed;inset:-10%;z-index:0;pointer-events:none;background:radial-gradient(circle at 18% 16%,rgba(255,182,193,.20),transparent 18%),radial-gradient(circle at 82% 14%,rgba(125,211,252,.18),transparent 20%),radial-gradient(circle at 62% 78%,rgba(217,181,255,.20),transparent 26%),linear-gradient(180deg,#111029 0%,#070818 58%,#04050d 100%);animation:bgBreath 12s ease-in-out infinite}.stApp:after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;background-image:radial-gradient(circle,rgba(255,255,255,.75) 0 1px,transparent 1.5px),radial-gradient(circle,rgba(175,220,255,.45) 0 1px,transparent 1.8px);background-size:150px 150px,250px 250px;background-position:0 0,80px 70px;animation:stars 70s linear infinite}@keyframes stars{to{background-position:320px 180px,-260px 300px}}@keyframes bgBreath{50%{filter:saturate(1.25) hue-rotate(6deg)}}.space-scene{position:fixed;inset:0;z-index:1;pointer-events:none;overflow:hidden}.planet{position:absolute;border-radius:50%;opacity:.24;filter:saturate(1.2)}.planet.one{width:300px;height:300px;right:5%;top:8%;background:radial-gradient(circle at 34% 28%,#fff 0 3%,#ffd6f0 4% 12%,#9b7cff 34%,rgba(77,55,150,.25) 62%,transparent 72%);box-shadow:0 0 80px rgba(217,181,255,.22);animation:float1 18s ease-in-out infinite}.planet.two{width:150px;height:150px;left:5%;bottom:10%;background:radial-gradient(circle at 35% 30%,#cfffff,#6cc8ff 36%,rgba(60,80,200,.24) 65%,transparent 73%);animation:float1 22s ease-in-out infinite reverse}.comet{position:absolute;width:130px;height:3px;border-radius:999px;background:linear-gradient(90deg,transparent,#fff,#ffd6f0,transparent);opacity:0;transform:rotate(-18deg);filter:drop-shadow(0 0 8px white);animation:comet 10s linear infinite}.c1{left:8%;top:18%;animation-delay:2s}.c2{left:52%;top:9%;animation-delay:6s}.ufo{position:absolute;left:72%;top:64%;width:80px;height:30px;opacity:.17;animation:ufo 25s ease-in-out infinite}.ufo:before{content:"";position:absolute;left:18px;top:0;width:44px;height:22px;border-radius:50%;background:radial-gradient(circle at 50% 20%,#fff,rgba(125,211,252,.35) 48%,transparent 72%)}.ufo:after{content:"";position:absolute;left:0;top:13px;width:80px;height:14px;border-radius:50%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.6),rgba(217,181,255,.45),transparent)}@keyframes float1{50%{transform:translate(-12px,18px) scale(1.03)}}@keyframes comet{0%,70%{opacity:0;transform:translate(0,0) rotate(-18deg)}74%{opacity:.48}86%{opacity:0;transform:translate(460px,160px) rotate(-18deg)}}@keyframes ufo{50%{transform:translate(-130px,-30px) rotate(-4deg)}}.main .block-container{max-width:1380px!important;padding-top:1.2rem!important;padding-bottom:4rem!important;position:relative!important;z-index:3!important}[data-testid="stSidebar"]{background:rgba(11,12,28,.78)!important;backdrop-filter:blur(44px) saturate(180%)!important;border-right:1px solid rgba(255,255,255,.18)!important;box-shadow:20px 0 70px rgba(0,0,0,.55)!important}[data-testid="stSidebar"] *{color:var(--ink-soft)!important}
[data-testid="metric-container"],[data-testid="stForm"],[data-testid="stExpander"],[data-testid="stDataFrame"],.info-box,.result-card,.hero{background:linear-gradient(145deg,rgba(255,255,255,.18),rgba(255,255,255,.075) 32%,rgba(22,20,38,.78) 100%)!important;backdrop-filter:blur(34px) saturate(185%)!important;-webkit-backdrop-filter:blur(34px) saturate(185%)!important;border:1px solid var(--edge)!important;border-top:1px solid var(--edge2)!important;border-radius:var(--r)!important;box-shadow:0 28px 74px rgba(0,0,0,.58),0 10px 26px rgba(0,0,0,.36),inset 0 1px 0 rgba(255,255,255,.40),inset 0 -1px 0 rgba(255,255,255,.10)!important;position:relative!important;overflow:hidden!important}.hero:before,[data-testid="metric-container"]:before,[data-testid="stForm"]:before,[data-testid="stExpander"]:before,.info-box:before,.result-card:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 18% 8%,rgba(255,255,255,.24),transparent 26%),radial-gradient(circle at 92% 92%,rgba(125,211,252,.13),transparent 34%),linear-gradient(135deg,rgba(255,255,255,.18),transparent 24%,transparent 70%,rgba(255,255,255,.08));opacity:.72}.hero:after,[data-testid="metric-container"]:after,[data-testid="stForm"]:after,.result-card:after,.info-box:after{content:"";position:absolute;inset:1px;border-radius:inherit;pointer-events:none;background:radial-gradient(ellipse at 30% -10%,rgba(255,255,255,.22),transparent 38%),radial-gradient(ellipse at 70% 110%,rgba(217,181,255,.14),transparent 42%);mix-blend-mode:screen;opacity:.65}
[data-testid="metric-container"]{padding:30px 32px!important;transition:transform .32s cubic-bezier(.2,.9,.2,1),box-shadow .32s ease!important}[data-testid="metric-container"]:hover,.result-card:hover,.info-box:hover{transform:translateY(-7px)!important;box-shadow:0 36px 92px rgba(0,0,0,.66),0 0 40px rgba(217,181,255,.14),inset 0 1px 0 rgba(255,255,255,.48)!important}[data-testid="stMetricLabel"] p{color:var(--ink-muted)!important;font-size:.7rem!important;letter-spacing:.15em!important;text-transform:uppercase!important;font-weight:800!important}[data-testid="stMetricValue"],[data-testid="stMetricValue"]>div{color:var(--ink)!important;font-size:2.05rem!important;font-weight:800!important;letter-spacing:-.04em!important}.hero{padding:34px 44px!important;margin-bottom:34px!important}.hero h1{font-family:'Space Grotesk',sans-serif!important;font-size:2.8rem!important;line-height:1.05!important;margin:0!important;background:linear-gradient(135deg,#fff,#d9b5ff 50%,#ff91cf);-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important}.hero p,.hero-eyebrow,.hero-glyph{display:none!important}.stButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:999px!important;border:1px solid rgba(255,255,255,.28)!important;background:linear-gradient(135deg,rgba(255,255,255,.22),rgba(255,255,255,.08)),linear-gradient(135deg,rgba(217,181,255,.42),rgba(255,145,207,.22))!important;color:#fff!important;backdrop-filter:blur(28px) saturate(180%)!important;box-shadow:0 16px 38px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.38)!important;transition:all .25s cubic-bezier(.2,.9,.2,1)!important;font-family:'Space Grotesk',sans-serif!important;font-weight:800!important}.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{transform:translateY(-3px)!important;box-shadow:0 24px 58px rgba(0,0,0,.52),0 0 34px rgba(217,181,255,.18),inset 0 1px 0 rgba(255,255,255,.48)!important}.sidebar-brand{font-family:'Space Grotesk';font-size:1.45rem;font-weight:800;padding:6px 0 22px;border-bottom:1px solid rgba(255,255,255,.16);margin-bottom:22px}.sidebar-brand span{background:linear-gradient(135deg,var(--violet),var(--pink));-webkit-background-clip:text;-webkit-text-fill-color:transparent}h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;color:var(--ink)!important;font-weight:800!important}.section-hd{font-family:'Space Grotesk'!important;font-size:1.16rem!important;font-weight:800!important;color:var(--ink)!important;margin:0 0 6px!important}.section-sub,[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{color:var(--ink-soft)!important;line-height:1.7!important}.info-box{padding:24px 30px!important}.result-card{padding:36px 40px!important;margin:32px 0!important}.pill{display:inline-block;padding:3px 12px;border-radius:99px;font-size:.66rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;border:1px solid transparent}.pill-expand{background:rgba(74,222,128,.17);color:#4ade80;border-color:rgba(74,222,128,.42)}.pill-maintain{background:rgba(250,204,21,.17);color:#facc15;border-color:rgba(250,204,21,.42)}.pill-optimize{background:rgba(251,146,60,.17);color:#fb923c;border-color:rgba(251,146,60,.42)}.pill-drop{background:rgba(251,113,133,.17);color:#fb7185;border-color:rgba(251,113,133,.42)}.result-expand{border-left:3px solid #4ade80!important}.result-maintain{border-left:3px solid #facc15!important}.result-optimize{border-left:3px solid #fb923c!important}.result-drop{border-left:3px solid #fb7185!important}.divider-label{display:flex;align-items:center;gap:16px;margin:40px 0 24px;color:var(--ink-muted);font-size:.7rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}.divider-label:before,.divider-label:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.32),transparent)}.stTabs [data-baseweb="tab-list"]{background:rgba(26,25,42,.72)!important;backdrop-filter:blur(26px)!important;border:1px solid rgba(255,255,255,.20)!important;border-radius:24px!important;padding:5px!important}.stTabs [data-baseweb="tab"]{border-radius:18px!important;color:var(--ink-muted)!important;font-weight:800!important;padding:10px 22px!important}.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(217,181,255,.32),rgba(255,145,207,.18))!important;color:var(--violet)!important;border:1px solid rgba(255,255,255,.25)!important}.stTabs [data-baseweb="tab-highlight"]{display:none!important}.stTabs [data-baseweb="tab-panel"]{padding-top:2rem!important}.stSelectbox label,.stNumberInput label,.stSlider label,.stRadio label,.stCheckbox label,.stTextInput label{color:var(--ink-soft)!important;font-weight:800!important;font-size:.78rem!important;letter-spacing:.06em!important;text-transform:uppercase!important}.stSelectbox [data-baseweb="select"] div,.stTextInput input,.stNumberInput input{color:var(--ink)!important;background:rgba(255,255,255,.08)!important;border:1px solid rgba(255,255,255,.22)!important;border-radius:15px!important}[data-testid="stExpander"],[data-testid="stDataFrame"],iframe{border-radius:28px!important}hr{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,rgba(255,255,255,.30),transparent)!important;margin:2rem 0!important}[data-testid="stHorizontalBlock"]{gap:22px!important}::-webkit-scrollbar{width:5px;height:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.24);border-radius:5px}
</style>
<div class="space-scene"><div class="planet one"></div><div class="planet two"></div><div class="comet c1"></div><div class="comet c2"></div><div class="ufo"></div></div>
<script>(function(){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.style.opacity='1';e.target.style.transform='translateY(0) scale(1)';io.unobserve(e.target)}})},{threshold:.07,rootMargin:'0px 0px -35px 0px'});function a(){document.querySelectorAll("[data-testid='metric-container'],[data-testid='stDataFrame'],[data-testid='stExpander'],.element-container").forEach(function(el,i){if(!el.dataset.sr){el.dataset.sr='1';el.style.opacity='0';el.style.transform='translateY(30px) scale(.99)';el.style.transition='opacity .65s cubic-bezier(.22,1,.36,1) '+(i%5)*.04+'s, transform .65s cubic-bezier(.22,1,.36,1) '+(i%5)*.04+'s';io.observe(el)}})}setTimeout(a,250);new MutationObserver(function(){setTimeout(a,120)}).observe(document.body,{childList:true,subtree:true})})();</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SVG CHART RENDERER HELPERS
#  Each function receives already-computed Python data and
#  returns an st.components.v1.html call with a self-contained
#  glass-panel SVG chart.  No matplotlib anywhere.
# ─────────────────────────────────────────────────────────────

CHART_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Mono:wght@400;500;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0}html,body{width:100%;height:100%;background:transparent;overflow:hidden;font-family:'Space Grotesk',sans-serif}.card{width:100%;min-height:100%;background:linear-gradient(145deg,rgba(255,255,255,.16),rgba(255,255,255,.07) 38%,rgba(18,16,32,.82));border:1px solid rgba(255,255,255,.26);border-top:1px solid rgba(255,255,255,.46);border-radius:30px;padding:26px 30px 24px;box-shadow:0 28px 76px rgba(0,0,0,.56),0 10px 28px rgba(0,0,0,.34),inset 0 1px 0 rgba(255,255,255,.36);position:relative;overflow:hidden}.card:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 18% 0%,rgba(255,255,255,.22),transparent 26%),radial-gradient(circle at 98% 100%,rgba(125,211,252,.12),transparent 34%),linear-gradient(135deg,rgba(255,255,255,.14),transparent 25%,transparent 72%,rgba(255,255,255,.07));opacity:.76}.chart-title{position:relative;z-index:2;font-size:18px;font-weight:800;color:#fbf7ff;letter-spacing:-.01em;margin-bottom:14px}svg{position:relative;z-index:2;display:block;width:100%;height:auto;overflow:visible}.axis-label{font-size:15px;fill:#d2c8dc;font-family:'Space Grotesk',sans-serif;font-weight:600}.value-label{font-size:15px;fill:#fff;font-weight:800;font-family:'DM Mono',monospace;paint-order:stroke;stroke:rgba(5,6,18,.65);stroke-width:3px;stroke-linejoin:round}.grid-line{stroke:rgba(255,255,255,.075);stroke-width:1;stroke-dasharray:5,5}.bar-rect{transition:opacity .2s,filter .2s;cursor:pointer}.bar-rect:hover{opacity:.94;filter:brightness(1.08)}@keyframes barGrow{from{transform:scaleY(0);transform-origin:bottom;opacity:.55}to{transform:scaleY(1);transform-origin:bottom;opacity:1}}@keyframes barGrowH{from{transform:scaleX(0);transform-origin:left;opacity:.55}to{transform:scaleX(1);transform-origin:left;opacity:1}}@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}.bar-anim{animation:barGrow .72s cubic-bezier(.22,1,.36,1) both}.bar-anim-h{animation:barGrowH .72s cubic-bezier(.22,1,.36,1) both}.fade-in{animation:fadeIn .55s ease both}.pie-slice{transition:opacity .2s,filter .2s;cursor:pointer}.pie-slice:hover{opacity:.94;filter:brightness(1.08)}
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
    W, H = 880, height
    pad_l, pad_r, pad_t, pad_b = 96, 56, 48, 78
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
  style="filter:drop-shadow(0 5px 12px {col}22);animation-delay:{delay:.2f}s"/>""")

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
    W = 960
    H = height or max(320, 50 * n + 110)
    pad_l, pad_r, pad_t, pad_b = 170, 145, 48, 64
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
  style="filter:drop-shadow(0 4px 10px {col}22);animation-delay:{delay:.2f}s"/>
<text class="axis-label" x="{pad_l-8}" y="{cy+3.5:.1f}" text-anchor="end" font-size="9">{lbl}</text>
<text class="value-label fade-in" x="{min(pad_l+bw+12, W-70):.1f}" y="{cy+5:.1f}"
  text-anchor="start" style="animation-delay:{delay+0.25:.2f}s">{fmt_fn(v)}</text>""")

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
    W, H = 760, height
    cx, cy, r_outer, r_inner = W // 2, H // 2 - 10, min(W, H) // 2 - 56, 64

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
  style="filter:drop-shadow(0 5px 12px {col}24);animation-delay:{delay:.2f}s">
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
    W, H = 980, height
    pad_l, pad_r, pad_t, pad_b = 92, 58, 52, 86
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
  fill="url(#{gid})" style="filter:drop-shadow(0 4px 10px {col}22);animation-delay:{delay:.2f}s"/>
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
    """Render the chart HTML in a transparent iframe with extra breathing room."""
    components.html(html_str, height=height + 64, scrolling=False)


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
  <h1>SkyLens Dashboard</h1>
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
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#4f4352;font-size:.74rem;
            padding:48px 0 20px;font-family:"Manrope",sans-serif;
            letter-spacing:.08em;text-transform:uppercase'>
  SkyLens Route Intelligence &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)
