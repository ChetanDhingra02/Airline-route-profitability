import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# SKYLENS - Airline Route Profitability Analytics
# Streamlit Edition with Custom CSS Theming
# ============================================================

# ---- CUSTOM CSS THEME ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Root Theme Variables */
:root {
    --background: 232 45% 5%;
    --foreground: 40 30% 96%;
    --card: 232 35% 9%;
    --primary: 210 85% 70%;
    --primary-foreground: 232 50% 6%;
    --primary-glow: 220 90% 78%;
    --secondary: 232 28% 14%;
    --muted: 232 22% 12%;
    --muted-foreground: 225 15% 72%;
    --accent: 280 55% 70%;
    --success: 152 70% 48%;
    --warning: 38 95% 58%;
    --danger: 0 78% 62%;
    --border: 215 30% 22%;
    --glass: rgba(28, 32, 52, 0.55);
    --glass-strong: rgba(34, 38, 58, 0.72);
    --glass-border: rgba(200, 180, 220, 0.14);
}

/* Global Background - Muted Nebula Theme */
.stApp {
    background: 
        radial-gradient(900px 600px at 50% 0%, hsl(265 55% 35% / 0.32), transparent 60%),
        radial-gradient(700px 500px at 85% 30%, hsl(210 70% 45% / 0.18), transparent 60%),
        radial-gradient(800px 600px at 10% 80%, hsl(290 50% 35% / 0.18), transparent 60%),
        radial-gradient(600px 450px at 70% 90%, hsl(20 60% 45% / 0.10), transparent 60%),
        linear-gradient(180deg, hsl(232 50% 4%), hsl(232 45% 6%)) !important;
    background-attachment: fixed !important;
    color: hsl(40 30% 96%) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: hsl(40 30% 96%) !important;
    letter-spacing: -0.01em !important;
}

p, div, span, label {
    color: hsl(225 15% 72%) !important;
}

/* Glass Cards */
.glass-card {
    background: linear-gradient(160deg, hsl(220 40% 14% / 0.85), hsl(220 38% 10% / 0.6)) !important;
    backdrop-filter: blur(20px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(140%) !important;
    border: 1px solid hsl(280 60% 85% / 0.14) !important;
    border-radius: 0.9rem !important;
    box-shadow: 0 10px 40px -10px hsl(220 60% 2% / 0.6), inset 0 1px 0 0 hsl(210 100% 90% / 0.05) !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    transition: all 400ms cubic-bezier(0.22, 1, 0.36, 1) !important;
}

.glass-card:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 30px 80px -20px hsl(198 95% 58% / 0.25), 0 10px 30px -10px hsl(220 60% 2% / 0.7) !important;
    border-color: hsl(210 85% 70% / 0.45) !important;
}

.glass-strong {
    background: linear-gradient(160deg, hsl(220 40% 16% / 0.92), hsl(220 38% 11% / 0.78)) !important;
    backdrop-filter: blur(24px) saturate(150%) !important;
    border: 1px solid hsl(210 60% 80% / 0.12) !important;
}

/* KPI Card Styling */
.kpi-card {
    background: linear-gradient(160deg, hsl(220 40% 14% / 0.85), hsl(220 38% 10% / 0.6)) !important;
    backdrop-filter: blur(20px) saturate(140%) !important;
    border: 1px solid hsl(280 60% 85% / 0.14) !important;
    border-radius: 0.9rem !important;
    padding: 1.5rem !important;
    text-align: center !important;
}

.kpi-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.2em !important;
    color: hsl(225 15% 72%) !important;
    margin-bottom: 0.5rem !important;
}

.kpi-value {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 600 !important;
    color: hsl(40 30% 96%) !important;
}

.kpi-delta {
    font-size: 0.85rem !important;
    margin-top: 0.3rem !important;
}

.kpi-delta.positive {
    color: hsl(152 70% 48%) !important;
}

.kpi-delta.negative {
    color: hsl(0 78% 62%) !important;
}

/* Section Headers */
.section-eyebrow {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.25em !important;
    color: hsl(220 90% 78%) !important;
    margin-bottom: 0.5rem !important;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 600 !important;
    color: hsl(40 30% 96%) !important;
    margin-bottom: 0.5rem !important;
    line-height: 1.2 !important;
}

.section-subtitle {
    font-size: 1rem !important;
    color: hsl(225 15% 72%) !important;
    margin-bottom: 1.5rem !important;
}

/* Text Gradient */
.text-gradient {
    background: linear-gradient(135deg, hsl(198 95% 58%), hsl(195 100% 70%)) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
}

/* Divider Glow */
.divider-glow {
    height: 1px !important;
    background: linear-gradient(90deg, transparent, hsl(210 85% 70% / 0.5), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* Chips / Badges */
.chip {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    border-radius: 9999px !important;
    padding: 0.3rem 0.8rem !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    background: hsl(210 85% 70% / 0.12) !important;
    color: hsl(220 90% 78%) !important;
    border: 1px solid hsl(210 85% 70% / 0.25) !important;
}

.chip-success {
    background: hsl(152 70% 48% / 0.12) !important;
    color: hsl(152 70% 48%) !important;
    border: 1px solid hsl(152 70% 48% / 0.30) !important;
}

.chip-warning {
    background: hsl(38 95% 58% / 0.12) !important;
    color: hsl(38 95% 58%) !important;
    border: 1px solid hsl(38 95% 58% / 0.30) !important;
}

.chip-danger {
    background: hsl(0 78% 62% / 0.12) !important;
    color: hsl(0 78% 62%) !important;
    border: 1px solid hsl(0 78% 62% / 0.30) !important;
}

/* Tables */
.data-table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 0.9rem !important;
}

.data-table th {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    color: hsl(225 15% 72%) !important;
    padding: 0.75rem !important;
    text-align: left !important;
    border-bottom: 1px solid hsl(215 30% 22%) !important;
}

.data-table td {
    padding: 0.75rem !important;
    color: hsl(40 30% 96%) !important;
    border-bottom: 1px solid hsl(215 30% 22% / 0.4) !important;
}

.data-table tr:hover td {
    background: hsl(232 28% 14% / 0.5) !important;
}

/* Decision Dot */
.decision-dot {
    display: inline-block !important;
    width: 10px !important;
    height: 10px !important;
    border-radius: 50% !important;
    margin-right: 0.5rem !important;
}

/* Progress Bar */
.progress-bar-bg {
    width: 100% !important;
    height: 8px !important;
    background: hsl(232 28% 14% / 0.6) !important;
    border-radius: 9999px !important;
    overflow: hidden !important;
}

.progress-bar-fill {
    height: 100% !important;
    border-radius: 9999px !important;
    transition: width 0.7s ease !important;
}

/* Hero Styling */
.hero-title {
    font-size: 3rem !important;
    font-weight: 600 !important;
    line-height: 1.05 !important;
    color: hsl(40 30% 96%) !important;
    margin-bottom: 1rem !important;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, hsl(198 95% 58%), hsl(195 100% 70%)) !important;
    color: hsl(232 50% 6%) !important;
    border: none !important;
    border-radius: 0.75rem !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    box-shadow: 0 10px 40px -10px hsl(198 95% 58% / 0.5) !important;
}

button[kind="primary"]:hover {
    opacity: 0.95 !important;
    transform: scale(1.02) !important;
}

/* Streamlit Specific Overrides */
.stSelectbox > div > div {
    background: hsl(232 28% 14% / 0.6) !important;
    border: 1px solid hsl(215 30% 22%) !important;
    color: hsl(40 30% 96%) !important;
    border-radius: 0.5rem !important;
}

.stNumberInput > div > div > input {
    background: hsl(232 28% 14% / 0.6) !important;
    border: 1px solid hsl(215 30% 22%) !important;
    color: hsl(40 30% 96%) !important;
    border-radius: 0.5rem !important;
}

.stSlider > div > div > div {
    background: hsl(210 85% 70% / 0.3) !important;
}

.stSlider > div > div > div > div {
    background: hsl(198 95% 58%) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Map Container */
.map-container {
    background: linear-gradient(160deg, hsl(220 40% 14% / 0.85), hsl(220 38% 10% / 0.6)) !important;
    border: 1px solid hsl(280 60% 85% / 0.14) !important;
    border-radius: 0.9rem !important;
    padding: 1rem !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Runway Grid Background */
.runway-grid {
    background-image:
        linear-gradient(hsl(210 60% 80% / 0.05) 1px, transparent 1px),
        linear-gradient(90deg, hsl(210 60% 80% / 0.05) 1px, transparent 1px) !important;
    background-size: 56px 56px !important;
    mask-image: radial-gradient(ellipse at center, black 35%, transparent 80%) !important;
}

/* Font Mono Class */
.font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Animated Elements */
@keyframes pulse-ring {
    0% { transform: scale(0.6); opacity: 0.7; }
    100% { transform: scale(2.2); opacity: 0; }
}

.pulse-ring {
    animation: pulse-ring 2.4s cubic-bezier(0.22, 1, 0.36, 1) infinite;
}

@keyframes float-soft {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

.float-soft {
    animation: float-soft 5s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

# ---- DATASETS ----

DECISION_COLORS = {
    "Expand": "#3ddc84",
    "Maintain": "#38bdf8",
    "Optimize": "#fbbf24",
    "Drop": "#f87171",
}

DECISION_DESC = {
    "Expand": {
        "title": "Expand",
        "tagline": "Scale capacity & frequency",
        "body": "Route shows strong unit economics, healthy load factors, and durable demand. Add frequencies, upgauge aircraft, or open codeshare partners.",
    },
    "Maintain": {
        "title": "Maintain",
        "tagline": "Hold schedule, monitor",
        "body": "Profit and demand are stable within target bands. Preserve current schedule and pricing while monitoring fuel and competitive dynamics.",
    },
    "Optimize": {
        "title": "Optimize",
        "tagline": "Reprice, re-time, retrofit",
        "body": "Margins are pressured but recoverable. Tune fare mix, slot timing, ancillary attach, and seat configuration before changing the network.",
    },
    "Drop": {
        "title": "Drop",
        "tagline": "Exit or seasonalize",
        "body": "Persistent losses with weak structural demand. Withdraw the route, seasonalize, or substitute with a regional partner aircraft.",
    },
}

decisionMix = [
    {"name": "Expand", "value": 412},
    {"name": "Maintain", "value": 1086},
    {"name": "Optimize", "value": 538},
    {"name": "Drop", "value": 174},
]

summaryKPIs = [
    {"label": "Routes Analyzed", "value": "2,210", "delta": "+128 QoQ", "positive": True},
    {"label": "Avg Route Profit", "value": "$1.42M", "delta": "+6.4%", "positive": True},
    {"label": "Network Load Factor", "value": "82.7%", "delta": "+1.9 pts", "positive": True},
    {"label": "Routes At Risk", "value": "174", "delta": "−12 QoQ", "positive": True},
]

avgProfitByDecision = [
    {"decision": "Expand", "profit": 4.82},
    {"decision": "Maintain", "profit": 1.71},
    {"decision": "Optimize", "profit": 0.34},
    {"decision": "Drop", "profit": -1.26},
]

loadFactorByDecision = [
    {"decision": "Expand", "lf": 88.6},
    {"decision": "Maintain", "lf": 83.1},
    {"decision": "Optimize", "lf": 74.8},
    {"decision": "Drop", "lf": 61.2},
]

topCostDrivers = [
    {"driver": "Fuel", "impact": 34},
    {"driver": "Crew & Labor", "impact": 19},
    {"driver": "Airport Fees", "impact": 12},
    {"driver": "Maintenance", "impact": 11},
    {"driver": "Distribution", "impact": 9},
    {"driver": "Ground Ops", "impact": 8},
    {"driver": "Other", "impact": 7},
]

topRoutes = [
    {"route": "JFK → LHR", "profit": 28.4, "decision": "Expand"},
    {"route": "LAX → NRT", "profit": 24.1, "decision": "Expand"},
    {"route": "SFO → SIN", "profit": 21.7, "decision": "Expand"},
    {"route": "ORD → FRA", "profit": 19.6, "decision": "Maintain"},
    {"route": "ATL → CDG", "profit": 18.2, "decision": "Maintain"},
    {"route": "MIA → GRU", "profit": 16.9, "decision": "Expand"},
    {"route": "DFW → ICN", "profit": 15.4, "decision": "Maintain"},
    {"route": "BOS → DUB", "profit": 14.1, "decision": "Expand"},
]

bottomRoutes = [
    {"route": "CLE → AUS", "profit": -6.8, "decision": "Drop"},
    {"route": "MEM → BOI", "profit": -5.9, "decision": "Drop"},
    {"route": "PIT → JAX", "profit": -4.7, "decision": "Drop"},
    {"route": "OMA → ABQ", "profit": -3.6, "decision": "Optimize"},
    {"route": "BUF → MSY", "profit": -3.2, "decision": "Optimize"},
    {"route": "RIC → OKC", "profit": -2.9, "decision": "Optimize"},
    {"route": "TUL → BHM", "profit": -2.4, "decision": "Optimize"},
    {"route": "SAT → ROC", "profit": -1.9, "decision": "Optimize"},
]

stableRoutes = [
    {"route": "JFK → LHR", "stability": 0.96, "variance": "Low", "years": 7},
    {"route": "LAX → NRT", "stability": 0.94, "variance": "Low", "years": 9},
    {"route": "ORD → FRA", "stability": 0.93, "variance": "Low", "years": 11},
    {"route": "SFO → SIN", "stability": 0.91, "variance": "Low", "years": 6},
    {"route": "ATL → CDG", "stability": 0.90, "variance": "Low", "years": 8},
]

volatileRoutes = [
    {"route": "MIA → CCS", "stability": 0.34, "variance": "High", "years": 4},
    {"route": "LAX → PVG", "stability": 0.41, "variance": "High", "years": 5},
    {"route": "JFK → TLV", "stability": 0.46, "variance": "High", "years": 6},
    {"route": "SEA → ANC", "stability": 0.49, "variance": "High", "years": 3},
    {"route": "IAH → EZE", "stability": 0.52, "variance": "Medium", "years": 5},
]

uniqueRoutesByDecision = [
    {"decision": "Expand", "routes": 312},
    {"decision": "Maintain", "routes": 884},
    {"decision": "Optimize", "routes": 421},
    {"decision": "Drop", "routes": 138},
]

modelMetrics = [
    {"model": "With Revenue Vars", "accuracy": 0.927, "f1": 0.918},
    {"model": "Without Revenue", "accuracy": 0.871, "f1": 0.854},
    {"model": "Pre-Operational", "accuracy": 0.802, "f1": 0.781},
]

confidenceByDecision = [
    {"decision": "Expand", "confidence": 0.91},
    {"decision": "Maintain", "confidence": 0.88},
    {"decision": "Optimize", "confidence": 0.79},
    {"decision": "Drop", "confidence": 0.84},
]

summaryTable = [
    {"decision": "Expand", "routes": 412, "share": "18.6%", "avgProfit": "$4.82M", "avgLF": "88.6%"},
    {"decision": "Maintain", "routes": 1086, "share": "49.1%", "avgProfit": "$1.71M", "avgLF": "83.1%"},
    {"decision": "Optimize", "routes": 538, "share": "24.3%", "avgProfit": "$0.34M", "avgLF": "74.8%"},
    {"decision": "Drop", "routes": 174, "share": "7.9%", "avgProfit": "−$1.26M", "avgLF": "61.2%"},
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section_header(eyebrow, title, subtitle=""):
    st.markdown(f'<p class="section-eyebrow">{eyebrow}</p>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="section-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider-glow"></div>', unsafe_allow_html=True)

def glass_card(title="", subtitle="", action_html="", content_html=""):
    subtitle_html = f'<p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">{subtitle}</p>' if subtitle else ""
    action = f'<div style="float: right;">{action_html}</div>' if action_html else ""
    header = f'<h3 style="margin: 0; font-size: 1.1rem; font-weight: 600;">{title}</h3>' if title else ""
    st.markdown(f"""
    <div class="glass-card">
        {action}{header}
        {subtitle_html}
        {content_html}
    </div>
    """, unsafe_allow_html=True)

def progress_bar_html(value, color, label="", percent_label=""):
    return f"""
    <div style="margin-bottom: 0.8rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem; font-size: 0.85rem;">
            <span>{label}</span>
            <span class="font-mono" style="color: hsl(225 15% 72%);">{percent_label}</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {value}%; background: {color};"></div>
        </div>
    </div>
    """

def decision_badge(decision):
    color = DECISION_COLORS[decision]
    return f'<span class="decision-dot" style="background: {color};"></span>{decision}'

# ============================================================
# PAGE LAYOUT
# ============================================================

st.set_page_config(page_title="SkyLens · Route Intelligence", page_icon="✈️", layout="wide")

# ---- TOP NAV ----
nav_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; 
     background: linear-gradient(160deg, hsl(220 40% 16% / 0.92), hsl(220 38% 11% / 0.78));
     backdrop-filter: blur(24px) saturate(150%);
     border: 1px solid hsl(210 60% 80% / 0.12);
     border-radius: 0.9rem; margin-bottom: 2rem;
     box-shadow: 0 10px 40px -10px hsl(220 60% 2% / 0.6), inset 0 1px 0 0 hsl(210 100% 90% / 0.05);">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="width: 36px; height: 36px; border-radius: 0.6rem; background: linear-gradient(135deg, hsl(198 95% 58%), hsl(280 55% 70%)); display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 1.2rem;">✈️</span>
        </div>
        <div>
            <div style="font-weight: 600; font-size: 1.1rem; color: hsl(40 30% 96%);">SkyLens</div>
            <div class="font-mono" style="font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.2em; color: hsl(225 15% 72%);">Route Intelligence</div>
        </div>
    </div>
    <div style="display: flex; gap: 1.5rem; font-size: 0.9rem;">
        <a href="#overview" style="color: hsl(225 15% 72%); text-decoration: none; transition: color 0.3s;">Overview</a>
        <a href="#drivers" style="color: hsl(225 15% 72%); text-decoration: none; transition: color 0.3s;">Drivers</a>
        <a href="#actions" style="color: hsl(225 15% 72%); text-decoration: none; transition: color 0.3s;">Actions</a>
        <a href="#stability" style="color: hsl(225 15% 72%); text-decoration: none; transition: color 0.3s;">Stability</a>
        <a href="#predict" style="color: hsl(225 15% 72%); text-decoration: none; transition: color 0.3s;">Predict</a>
    </div>
    <div>
        <span class="chip" style="font-size: 0.75rem;">🚀 Launch Console</span>
    </div>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# ---- HERO SECTION ----
hero_html = """
<div style="padding: 3rem 0 2rem 0;">
    <div class="chip" style="margin-bottom: 1rem;">📡 Live · Network telemetry</div>
    <h1 class="hero-title">The command center for <span class="text-gradient">airline route profitability</span>.</h1>
    <p style="font-size: 1.1rem; max-width: 600px; margin-bottom: 1.5rem; color: hsl(225 15% 72%);">
        SkyLens translates network economics into clear executive decisions — Expand, Maintain, Optimize, Drop — 
        backed by transparent models built for revenue management and operations leaders.
    </p>
    <div style="display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;">
        <a href="#overview" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem; 
            background: linear-gradient(135deg, hsl(198 95% 58%), hsl(195 100% 70%)); color: hsl(232 50% 6%);
            border-radius: 0.75rem; text-decoration: none; font-weight: 600; box-shadow: 0 15px 50px -15px hsl(198 95% 58% / 0.7);">
            Open Dashboard →
        </a>
        <a href="#predict" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem;
            background: hsl(232 28% 14% / 0.4); border: 1px solid hsl(215 30% 22% / 0.6); color: hsl(40 30% 96%);
            border-radius: 0.75rem; text-decoration: none; font-weight: 500; backdrop-filter: blur(12px);">
            ✈️ Run Decision Model
        </a>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; max-width: 500px;">
        <div class="kpi-card">
            <div class="kpi-value">2,210</div>
            <div class="kpi-label">Routes</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">92.7%</div>
            <div class="kpi-label">Model Accuracy</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">47</div>
            <div class="kpi-label">Carriers</div>
        </div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# ---- OVERVIEW SECTION ----
st.markdown('<div id="overview" style="scroll-margin-top: 80px;"></div>', unsafe_allow_html=True)
section_header("01 · Overview", "Network profitability at a glance", 
    "A consolidated view of the route portfolio, its decision mix, and the KPIs revenue management leaders track every morning.")

# KPI Cards
kpi_cols = st.columns(4)
for i, kpi in enumerate(summaryKPIs):
    with kpi_cols[i]:
        delta_class = "positive" if kpi["positive"] else "negative"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{kpi['label']}</div>
            <div class="kpi-value">{kpi['value']}</div>
            <div class="kpi-delta {delta_class}">{'📈' if kpi['positive'] else '📉'} {kpi['delta']}</div>
        </div>
        """, unsafe_allow_html=True)

# Decision Mix & Portfolio Summary
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

with col1:
    total = sum(d["value"] for d in decisionMix)
    legend_html = ""
    for d in decisionMix:
        pct = (d["value"] / total) * 100
        legend_html += f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; 
            background: hsl(232 28% 14% / 0.4); border-radius: 0.4rem; margin-bottom: 0.3rem;">
            <span style="font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                <span class="decision-dot" style="background: {DECISION_COLORS[d['name']};"></span>
                {d['name']}
            </span>
            <span class="font-mono" style="font-size: 0.75rem; color: hsl(225 15% 72%);">{pct:.1f}%</span>
        </div>
        """
    
    chart_data = pd.DataFrame(decisionMix)
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Decision Mix</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Share of routes by recommended action</p>
        <div style="height: 220px;">
            {st.bar_chart(chart_data.set_index("name")["value"], use_container_width=True, height=220)}
        </div>
        {legend_html}
    </div>
    """, unsafe_allow_html=True)

with col2:
    table_rows = ""
    for row in summaryTable:
        table_rows += f"""
        <tr>
            <td><span class="decision-dot" style="background: {DECISION_COLORS[row['decision']};"></span>{row['decision']}</td>
            <td class="font-mono">{row['routes']:,}</td>
            <td class="font-mono" style="color: hsl(225 15% 72%);">{row['share']}</td>
            <td class="font-mono">{row['avgProfit']}</td>
            <td class="font-mono">{row['avgLF']}</td>
        </tr>
        """
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Portfolio Summary</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Decision-level KPIs across the network</p>
        <div style="overflow-x: auto;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Decision</th>
                        <th>Routes</th>
                        <th>Share</th>
                        <th>Avg Profit</th>
                        <th>Avg Load Factor</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Live Network Map
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card map-container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
            <h3 style="margin: 0;">Live Network Map</h3>
            <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin: 0.3rem 0 0 0;">Animated route arcs across primary hubs</p>
        </div>
        <span class="chip">📡 Live · Realtime</span>
    </div>
    <div style="position: relative; height: 350px; display: flex; align-items: center; justify-content: center;">
        <svg viewBox="0 0 900 480" style="width: 100%; height: 100%;">
            <defs>
                <linearGradient id="arcGrad" x1="0" x2="1">
                    <stop offset="0%" stop-color="hsl(280 55% 70%)" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="hsl(210 85% 70%)" stop-opacity="0.9" />
                </linearGradient>
                <radialGradient id="hubGlow">
                    <stop offset="0%" stop-color="hsl(220 90% 78%)" stop-opacity="0.7" />
                    <stop offset="100%" stop-color="hsl(210 85% 70%)" stop-opacity="0" />
                </radialGradient>
            </defs>
            
            <!-- Route Arcs -->
            <path d="M 270 180 Q 370 90 470 150" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 270 180 Q 370 90 470 150" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <path d="M 200 220 Q 480 80 760 210" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 200 220 Q 480 80 760 210" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <path d="M 470 150 Q 595 150 720 320" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 470 150 Q 595 150 720 320" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <path d="M 270 180 Q 315 270 360 360" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 270 180 Q 315 270 360 360" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <path d="M 480 165 Q 535 207 590 250" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 480 165 Q 535 207 590 250" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <path d="M 590 250 Q 655 285 720 320" fill="none" stroke="hsl(210 85% 70% / 0.25)" stroke-width="1.5"/>
            <path d="M 590 250 Q 655 285 720 320" fill="none" stroke="url(#arcGrad)" stroke-width="1.8" stroke-dasharray="6 8"/>
            
            <!-- Hubs -->
            <circle cx="270" cy="180" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 270px 180px;"/>
            <circle cx="270" cy="180" r="4" fill="hsl(220 90% 78%)"/>
            <text x="285" y="170" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">JFK</text>
            
            <circle cx="470" cy="150" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 470px 150px;"/>
            <circle cx="470" cy="150" r="4" fill="hsl(220 90% 78%)"/>
            <text x="485" y="140" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">LHR</text>
            
            <circle cx="760" cy="210" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 760px 210px;"/>
            <circle cx="760" cy="210" r="4" fill="hsl(220 90% 78%)"/>
            <text x="775" y="200" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">NRT</text>
            
            <circle cx="720" cy="320" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 720px 320px;"/>
            <circle cx="720" cy="320" r="4" fill="hsl(220 90% 78%)"/>
            <text x="735" y="310" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">SIN</text>
            
            <circle cx="200" cy="220" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 200px 220px;"/>
            <circle cx="200" cy="220" r="4" fill="hsl(220 90% 78%)"/>
            <text x="215" y="210" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">LAX</text>
            
            <circle cx="360" cy="360" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 360px 360px;"/>
            <circle cx="360" cy="360" r="4" fill="hsl(220 90% 78%)"/>
            <text x="375" y="350" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">GRU</text>
            
            <circle cx="480" cy="165" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 480px 165px;"/>
            <circle cx="480" cy="165" r="4" fill="hsl(220 90% 78%)"/>
            <text x="495" y="155" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">CDG</text>
            
            <circle cx="590" cy="250" r="22" fill="url(#hubGlow)" class="pulse-ring" style="transform-origin: 590px 250px;"/>
            <circle cx="590" cy="250" r="4" fill="hsl(220 90% 78%)"/>
            <text x="605" y="240" fill="hsl(40 30% 96% / 0.85)" font-size="11" font-family="JetBrains Mono, monospace">DXB</text>
        </svg>
        
        <!-- Radar Overlay -->
        <div style="position: absolute; right: 20px; top: 20px; width: 120px; height: 120px;">
            <div style="width: 100%; height: 100%; border-radius: 50%; border: 1px solid hsl(280 55% 70% / 0.3); position: relative;">
                <div style="position: absolute; inset: 15px; border-radius: 50%; border: 1px solid hsl(280 55% 70% / 0.2);"></div>
                <div style="position: absolute; inset: 30px; border-radius: 50%; border: 1px solid hsl(280 55% 70% / 0.15);"></div>
                <div style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background: hsl(280 55% 70%); box-shadow: 0 0 20px hsl(280 55% 70%);"></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- DRIVERS SECTION ----
st.markdown('<div id="drivers" style="scroll-margin-top: 80px;"></div>', unsafe_allow_html=True)
section_header("02 · Performance Drivers", "What moves the margin",
    "The economic levers behind each route classification — profit, load factor, and cost composition.")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    df_profit = pd.DataFrame(avgProfitByDecision)
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Average Profit by Decision</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Annualized, USD millions per route</p>
    """, unsafe_allow_html=True)
    chart = st.bar_chart(df_profit.set_index("decision")["profit"], use_container_width=True, height=280)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    df_lf = pd.DataFrame(loadFactorByDecision)
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Load Factor by Decision</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Percent of seats sold, weighted across the cohort</p>
    """, unsafe_allow_html=True)
    st.bar_chart(df_lf.set_index("decision")["lf"], use_container_width=True, height=280)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card">
    <h3 style="margin-top: 0;">Top Cost Drivers</h3>
    <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Share of operating cost across the network (%)</p>
""", unsafe_allow_html=True)

# Horizontal bar chart for cost drivers using HTML/CSS
cost_html = ""
for item in topCostDrivers:
    cost_html += progress_bar_html(item["impact"], "hsl(210 85% 70%)", item["driver"], f"{item['impact']}%")

st.markdown(f"""{cost_html}</div>""", unsafe_allow_html=True)

# ---- ACTIONS SECTION ----
st.markdown('<div id="actions" style="scroll-margin-top: 80px;"></div>', unsafe_allow_html=True)
section_header("03 · Route Actions", "Where to lean in. Where to retreat.",
    "Ranked profit contribution across the network with action-level distribution.")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0;">Top Routes — Total Profit</h3>
                <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin: 0.3rem 0 0 0;">USD millions, last 12 months</p>
            </div>
            <span class="chip chip-success">📈 Winners</span>
        </div>
    """, unsafe_allow_html=True)
    
    top_html = ""
    for route in topRoutes:
        color = DECISION_COLORS[route["decision"]]
        top_html += progress_bar_html(
            (route["profit"] / 30) * 100, color, 
            f'<span class="decision-dot" style="background: {color};"></span>{route["route"]}',
            f"${route['profit']}M"
        )
    st.markdown(f"{top_html}</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0;">Bottom Routes — Total Profit</h3>
                <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin: 0.3rem 0 0 0;">USD millions, last 12 months</p>
            </div>
            <span class="chip chip-danger">📉 Watchlist</span>
        </div>
    """, unsafe_allow_html=True)
    
    bottom_html = ""
    for route in bottomRoutes:
        color = DECISION_COLORS[route["decision"]]
        bottom_html += progress_bar_html(
            (abs(route["profit"]) / 8) * 100, color,
            f'<span class="decision-dot" style="background: {color};"></span>{route["route"]}',
            f"${route['profit']}M"
        )
    st.markdown(f"{bottom_html}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card">
    <h3 style="margin-top: 0;">Unique Routes per Decision</h3>
    <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Count of distinct city-pairs by recommended action</p>
""", unsafe_allow_html=True)

routes_html = ""
for d in uniqueRoutesByDecision:
    max_routes = max(r["routes"] for r in uniqueRoutesByDecision)
    pct = (d["routes"] / max_routes) * 100
    routes_html += progress_bar_html(
        pct, DECISION_COLORS[d["decision"]],
        f'<span class="decision-dot" style="background: {DECISION_COLORS[d["decision"]]};"></span>{d["decision"]}',
        f"{d['routes']:,}"
    )
st.markdown(f"{routes_html}</div>", unsafe_allow_html=True)

# ---- STABILITY SECTION ----
st.markdown('<div id="stability" style="scroll-margin-top: 80px;"></div>', unsafe_allow_html=True)
section_header("04 · Route Stability", "Confidence over time",
    "Stability score blends profit variance, demand volatility, and competitive pressure across rolling windows.")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

def stability_table(rows, title, subtitle, chip_class, chip_text):
    rows_html = ""
    for r in rows:
        variance_chip = ""
        if r["variance"] == "Low":
            variance_chip = f'<span class="chip">{r["variance"]}</span>'
        elif r["variance"] == "Medium":
            variance_chip = f'<span class="chip chip-warning">{r["variance"]}</span>'
        else:
            variance_chip = f'<span class="chip chip-danger">{r["variance"]}</span>'
        
        color = "linear-gradient(90deg, hsl(152 70% 48%), hsl(280 55% 70%))" if r["stability"] > 0.7 else \
                "linear-gradient(90deg, hsl(38 95% 58%), hsl(210 85% 70%))" if r["stability"] > 0.5 else \
                "linear-gradient(90deg, hsl(0 78% 62%), hsl(38 95% 58%))"
        
        rows_html += f"""
        <tr>
            <td class="font-mono">{r['route']}</td>
            <td class="font-mono">{r['stability']*100:.0f}</td>
            <td style="width: 35%;">
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {r['stability']*100}%; background: {color};"></div>
                </div>
            </td>
            <td>{variance_chip}</td>
            <td class="font-mono" style="color: hsl(225 15% 72%);">{r['years']}</td>
        </tr>
        """
    
    return f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0;">{title}</h3>
                <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin: 0.3rem 0 0 0;">{subtitle}</p>
            </div>
            <span class="chip {chip_class}">{chip_text}</span>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Route</th>
                    <th>Stability</th>
                    <th>Score</th>
                    <th>Variance</th>
                    <th>Years</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

with col1:
    st.markdown(stability_table(stableRoutes, "Most Stable Routes", 
        "Lowest variance, highest predictability", "", "🛡️ Anchors"), unsafe_allow_html=True)

with col2:
    st.markdown(stability_table(volatileRoutes, "Most Volatile Routes", 
        "High variance — review monthly", "chip-warning", "⚡ Monitor"), unsafe_allow_html=True)

# ---- PREDICTION SECTION ----
st.markdown('<div id="predict" style="scroll-margin-top: 80px;"></div>', unsafe_allow_html=True)
section_header("05 · Prediction Tool", "Decision intelligence for any city-pair",
    "Three model surfaces — same inputs, different signal availability — calibrated for planning, ops, and live revenue management.")

st.markdown("<br>", unsafe_allow_html=True)

# Mode Selector
mode_cols = st.columns(3)
modes = [
    ("with", "With Revenue Variables", "Full-signal model — revenue, fares, ancillaries", "✨"),
    ("without", "Without Revenue Variables", "Operational signals only — no revenue leakage", "⚙️"),
    ("preop", "Only Pre-Operational Features", "Pre-launch network planning model", "📋"),
]

selected_mode = "with"  # default

# We need to handle state for mode selection
if "prediction_mode" not in st.session_state:
    st.session_state.prediction_mode = "with"

mode_html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">'
for m_id, m_label, m_tagline, m_icon in modes:
    active = "border: 1px solid hsl(210 85% 70% / 0.6); box-shadow: 0 0 0 2px hsl(210 85% 70% / 0.3);" if st.session_state.prediction_mode == m_id else ""
    bg = "background: hsl(210 85% 70% / 0.12);" if st.session_state.prediction_mode == m_id else ""
    icon_bg = "background: hsl(210 85% 70% / 0.2); color: hsl(220 90% 78%);" if st.session_state.prediction_mode == m_id else "background: hsl(232 28% 14% / 0.5); color: hsl(225 15% 72%);"
    
    mode_html += f"""
    <div class="glass-card" style="cursor: pointer; {active}">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="width: 36px; height: 36px; border-radius: 0.5rem; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; {icon_bg}">
                {m_icon}
            </div>
            <div>
                <div style="font-weight: 600; color: hsl(40 30% 96%);">{m_label}</div>
                <div style="font-size: 0.75rem; color: hsl(225 15% 72%);">{m_tagline}</div>
            </div>
        </div>
    </div>
    """
mode_html += '</div>'
st.markdown(mode_html, unsafe_allow_html=True)

# Use radio buttons hidden but functional for mode selection
mode_choice = st.radio("Select Model Mode", 
    options=["with", "without", "preop"], 
    format_func=lambda x: dict(with="With Revenue Variables", without="Without Revenue Variables", preop="Pre-Operational Only")[x],
    horizontal=True, label_visibility="collapsed")
st.session_state.prediction_mode = mode_choice

# Form & Results
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Route Inputs</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Configure the city-pair and operating profile</p>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        origin = st.text_input("Origin (IATA)", value="JFK", max_chars=3)
    with c2:
        destination = st.text_input("Destination (IATA)", value="LHR", max_chars=3)
    
    c3, c4 = st.columns(2)
    with c3:
        aircraft = st.selectbox("Aircraft", 
            options=["A320", "A321", "B738", "B789", "A359", "B77W"],
            index=3)
    with c4:
        distance = st.number_input("Stage Length (km)", value=5540, min_value=100, max_value=15000)
    
    show_ops = mode_choice != "preop"
    show_revenue = mode_choice == "with"
    
    if show_ops:
        freq = st.slider("Frequency / week", min_value=1, max_value=28, value=14)
        lf = st.slider("Load Factor", min_value=40, max_value=100, value=84)
        fuel = st.slider("Fuel Cost Index", min_value=20, max_value=100, value=62)
        comp = st.slider("Competitive Pressure", min_value=0, max_value=100, value=55)
        season = st.slider("Seasonality (Δ%)", min_value=-50, max_value=50, value=5)
    else:
        freq, lf, fuel, comp, season = 14, 84, 62, 55, 5
    
    if show_revenue:
        fare = st.slider("Avg Fare (USD)", min_value=80, max_value=2000, value=720, step=10)
        anc = st.slider("Ancillary / Pax", min_value=0, max_value=200, value=48)
        yield_idx = st.slider("Yield Index", min_value=20, max_value=100, value=71)
    else:
        fare, anc, yield_idx = 720, 48, 71
    
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
        <div class="font-mono" style="font-size: 0.75rem; color: hsl(225 15% 72%);">
            Model: <span style="color: hsl(220 90% 78%);">{}</span>
        </div>
    </div>
    """.format(dict(with="With Revenue Variables", without="Without Revenue Variables", preop="Pre-Operational Only")[mode_choice]), unsafe_allow_html=True)
    
    predict_btn = st.button("✈️ Run Decision Model", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Prediction Logic
def predict(mode, form):
    op_score = (
        (form["lf"] - 60) * 1.4 +
        (form["freq"] - 7) * 1.2 -
        (form["fuel"] - 50) * 1.1 -
        (form["comp"] - 40) * 0.5 +
        form["season"] * 0.4 -
        max(0, form["dist"] - 6000) * 0.002
    )
    
    rev_score = (form["fare"] - 400) * 0.06 + form["anc"] * 0.25 + (form["yield"] - 50) * 0.9
    
    score = op_score
    conf_boost = 0
    if mode == "with":
        score += rev_score
        conf_boost = 0.07
    if mode == "preop":
        score = score * 0.6 - 4
        conf_boost = -0.08
    
    logits = {
        "Expand": score - 22,
        "Maintain": -abs(score - 6) + 14,
        "Optimize": -abs(score + 6) + 12,
        "Drop": -score - 12,
    }
    
    exps = {k: np.exp(v / 8) for k, v in logits.items()}
    total_exp = sum(exps.values())
    probs = {k: v / total_exp for k, v in exps.items()}
    
    decision = max(probs, key=probs.get)
    confidence = min(0.99, max(0.45, probs[decision] + conf_boost))
    
    return {"decision": decision, "probs": probs, "confidence": confidence}

# Default prediction
form_state = {
    "origin": origin, "dest": destination, "aircraft": aircraft,
    "dist": distance, "freq": freq, "lf": lf, "fuel": fuel,
    "comp": comp, "season": season, "fare": fare, "anc": anc, "yield": yield_idx
}

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = predict("with", form_state)

if predict_btn:
    st.session_state.prediction_result = predict(mode_choice, form_state)

result = st.session_state.prediction_result

with col2:
    color = DECISION_COLORS[result["decision"]]
    desc = DECISION_DESC[result["decision"]]
    
    prob_bars = ""
    for d, p in sorted(result["probs"].items(), key=lambda x: x[1], reverse=True):
        prob_bars += progress_bar_html(p * 100, DECISION_COLORS[d], 
            f'<span class="decision-dot" style="background: {DECISION_COLORS[d]};"></span>{d}',
            f"{p*100:.1f}%")
    
    st.markdown(f"""
    <div class="glass-card glass-strong" style="height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <p class="font-mono" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; color: hsl(225 15% 72%);">Recommended Action</p>
                <h2 style="margin: 0.25rem 0; font-size: 2.5rem; color: {color};">{desc['title']}</h2>
                <p style="font-size: 0.9rem; color: hsl(225 15% 72%);">{desc['tagline']}</p>
            </div>
            <div style="text-align: right;">
                <p class="font-mono" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; color: hsl(225 15% 72%);">Confidence</p>
                <p class="font-mono" style="font-size: 1.8rem; color: hsl(220 90% 78%); margin: 0;">{result['confidence']*100:.1f}%</p>
            </div>
        </div>
        
        <div style="background: hsl(232 28% 14% / 0.3); border: 1px solid hsl(215 30% 22% / 0.5); border-radius: 0.5rem; padding: 1rem; margin-bottom: 1.5rem;">
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.6; color: hsl(40 30% 96% / 0.9);">{desc['body']}</p>
        </div>
        
        <p class="font-mono" style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; color: hsl(225 15% 72%); margin-bottom: 0.75rem;">Class Probabilities</p>
        {prob_bars}
        
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 1.5rem; font-size: 0.8rem; color: hsl(225 15% 72%);">
            <span style="font-size: 1rem;">✈️</span>
            {origin} → {destination} · {aircraft} · {distance:,} km
        </div>
    </div>
    """, unsafe_allow_html=True)

# Model Performance
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Model Accuracy & F1</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Hold-out evaluation across the three model surfaces</p>
    """, unsafe_allow_html=True)
    
    df_metrics = pd.DataFrame(modelMetrics)
    chart_data = df_metrics.set_index("model")[["accuracy", "f1"]]
    st.bar_chart(chart_data, use_container_width=True, height=280)
    
    st.markdown("""
        <div style="display: flex; gap: 1rem; font-size: 0.8rem; margin-top: 0.5rem;">
            <span style="display: flex; align-items: center; gap: 0.4rem;">
                <span class="decision-dot" style="background: hsl(210 85% 70%);"></span> Accuracy
            </span>
            <span style="display: flex; align-items: center; gap: 0.4rem;">
                <span class="decision-dot" style="background: hsl(280 55% 70%);"></span> F1
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">Prediction Confidence by Decision</h3>
        <p style="font-size: 0.85rem; color: hsl(225 15% 72%); margin-bottom: 1rem;">Mean predicted probability of the chosen class</p>
    """, unsafe_allow_html=True)
    
    conf_html = ""
    for c in confidenceByDecision:
        conf_html += progress_bar_html(
            c["confidence"] * 100, DECISION_COLORS[c["decision"]],
            f'<span class="decision-dot" style="background: {DECISION_COLORS[c["decision"]]};"></span>{c["decision"]}',
            f"{c['confidence']*100:.1f}%"
        )
    st.markdown(f"{conf_html}</div>", unsafe_allow_html=True)

# ---- FOOTER ----
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid hsl(215 30% 22% / 0.5); padding: 2rem 0; margin-top: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="width: 32px; height: 32px; border-radius: 0.5rem; background: linear-gradient(135deg, hsl(198 95% 58%), hsl(280 55% 70%)); display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1rem;">✈️</span>
            </div>
            <div>
                <div style="font-weight: 600; color: hsl(40 30% 96%);">SkyLens</div>
                <div class="font-mono" style="font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.2em; color: hsl(225 15% 72%);">Route Intelligence Platform</div>
            </div>
        </div>
        <p style="font-size: 0.75rem; color: hsl(225 15% 72%);">© 2026 SkyLens Analytics · Built for revenue management & network planning leaders</p>
    </div>
</div>
""", unsafe_allow_html=True)
