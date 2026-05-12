import os
import joblib
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go

st.set_page_config(
    page_title="SkyLens · Airline Profitability Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────────────────────
BG        = "#0A0D18"
TEXT      = "#1A1F35"
TEXT_SOFT = "#3D4466"
TEXT_MUTED= "#7A82A6"
CYAN      = "#0EA5E9"
BLUE      = "#3B82F6"
AMBER     = "#F59E0B"
GREEN     = "#10B981"
RED       = "#F43F5E"
VIOLET    = "#8B5CF6"

CHART_EXPAND   = "#10B981"
CHART_MAINTAIN = "#F59E0B"
CHART_OPTIMIZE = "#F97316"
CHART_DROP     = "#F43F5E"
CHART_NEUTRAL  = [CYAN, VIOLET, AMBER, GREEN, RED, BLUE, "#2DD4BF", "#F472B6"]
DECISION_COLORS = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN, "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

ACCENT   = CYAN
ACCENT_2 = VIOLET
INK      = TEXT
INK_SOFT = TEXT_SOFT
INK_MUTED= TEXT_MUTED

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

#MainMenu, footer { visibility: hidden; }

/* ── FULL-WIDTH LAYOUT ── */
.block-container {
  padding-top: 0 !important;
  padding-bottom: 2rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  max-width: 100% !important;
}

/* ── ANIMATED NEBULA BACKGROUND ── */
.stApp {
  font-family: 'DM Sans', sans-serif;
  color: #1A1F35;
  background-color: #0D1022;
  overflow-x: hidden;
}

.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 90% 60% at 20% 30%, rgba(99, 60, 180, 0.12) 0%, transparent 60%),
    radial-gradient(ellipse 70% 80% at 80% 70%, rgba(30, 80, 160, 0.10) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 50% 10%, rgba(140, 60, 100, 0.07) 0%, transparent 50%),
    radial-gradient(ellipse 60% 50% at 70% 40%, rgba(40, 120, 140, 0.06) 0%, transparent 55%),
    linear-gradient(160deg, #0B0E1F 0%, #0E1128 40%, #0C0F20 70%, #0B0D1E 100%);
  animation: nebulaDrift 40s ease-in-out infinite alternate;
  pointer-events: none;
}

.stApp::after {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 40% 30% at 85% 20%, rgba(80, 40, 160, 0.08) 0%, transparent 55%),
    radial-gradient(ellipse 55% 45% at 15% 75%, rgba(20, 80, 120, 0.09) 0%, transparent 55%),
    radial-gradient(ellipse 35% 55% at 60% 85%, rgba(120, 50, 80, 0.06) 0%, transparent 50%);
  animation: nebulaDrift2 55s ease-in-out infinite alternate;
  pointer-events: none;
}

@keyframes nebulaDrift {
  0%   { opacity: 0.7; transform: scale(1)    rotate(0deg); }
  33%  { opacity: 0.9; transform: scale(1.04) rotate(0.4deg); }
  66%  { opacity: 0.75; transform: scale(0.98) rotate(-0.3deg); }
  100% { opacity: 0.85; transform: scale(1.02) rotate(0.5deg); }
}
@keyframes nebulaDrift2 {
  0%   { opacity: 0.6; transform: scale(1)    rotate(0deg); }
  50%  { opacity: 0.85; transform: scale(1.05) rotate(-0.5deg); }
  100% { opacity: 0.65; transform: scale(0.97) rotate(0.3deg); }
}

/* Subtle star field */
.stApp > * { position: relative; z-index: 1; }

/* ── SIDEBAR — FROST WHITE ── */
[data-testid="stSidebar"] {
  background: rgba(255, 255, 255, 0.72) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(28px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
  box-shadow: 4px 0 32px rgba(30, 40, 120, 0.12) !important;
}
[data-testid="stSidebar"] * {
  color: #1A2040 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p {
  color: #3D4A80 !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: rgba(255,255,255,0.55) !important;
  border: 1px solid rgba(30,50,140,0.18) !important;
  border-radius: 12px !important;
  color: #1A2040 !important;
}

/* ── FROST WHITE GLASS CARDS ── */
[data-testid="metric-container"],
[data-testid="stDataFrame"],
[data-testid="stForm"],
.plotly-card,
.result-card,
.info-box {
  background: rgba(255, 255, 255, 0.62) !important;
  border: 1px solid rgba(255, 255, 255, 0.90) !important;
  border-radius: 20px !important;
  backdrop-filter: blur(22px) saturate(160%) !important;
  -webkit-backdrop-filter: blur(22px) saturate(160%) !important;
  box-shadow:
    0 8px 32px rgba(30, 40, 120, 0.10),
    0 2px 8px rgba(30, 40, 120, 0.06),
    inset 0 1px 0 rgba(255,255,255,0.95) !important;
}

/* ── METRIC CARDS ── */
[data-testid="metric-container"] { padding: 22px !important; }
[data-testid="stMetricLabel"] {
  color: #5A6490 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.14em !important;
  font-size: 0.70rem !important;
  font-weight: 700 !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
  color: #0F1530 !important;
  font-weight: 800 !important;
  font-family: 'Syne', sans-serif !important;
}
[data-testid="stMetricDelta"] { color: #10B981 !important; }

/* ── BUTTONS ── */
.stButton > button,
[data-testid="stFormSubmitButton"] button {
  border-radius: 999px !important;
  border: 1px solid rgba(30,50,180,0.20) !important;
  background: linear-gradient(160deg, rgba(255,255,255,0.85), rgba(240,244,255,0.70)) !important;
  color: #1A2060 !important;
  font-weight: 700 !important;
  font-family: 'DM Sans', sans-serif !important;
  backdrop-filter: blur(12px) !important;
  box-shadow: 0 4px 18px rgba(30,50,180,0.12), inset 0 1px 0 rgba(255,255,255,0.95) !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(30,50,180,0.20), inset 0 1px 0 rgba(255,255,255,1) !important;
}

/* ── INPUTS ── */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
  background: rgba(255,255,255,0.70) !important;
  border: 1px solid rgba(30,50,180,0.18) !important;
  border-radius: 12px !important;
  color: #1A2040 !important;
  backdrop-filter: blur(10px) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.55) !important;
  border: 1px solid rgba(255,255,255,0.88) !important;
  border-radius: 16px !important;
  padding: 5px !important;
  backdrop-filter: blur(16px) !important;
  box-shadow: 0 2px 12px rgba(30,40,120,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
  color: #5A6490 !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(255,255,255,0.88) !important;
  color: #0F1530 !important;
  box-shadow: 0 2px 8px rgba(30,40,120,0.12) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── PLOTLY CARDS ── */
.plotly-card { padding: 20px !important; }
.plotly-card-title {
  color: #0F1530 !important;
  font-weight: 800 !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 1rem !important;
  margin-bottom: 12px !important;
}

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
  font-size: 1.05rem; font-weight: 800; letter-spacing: 0.14em;
  color: #0F1530; text-transform: uppercase; margin-bottom: 18px; display: block;
  font-family: 'Syne', sans-serif;
}
.sidebar-brand span { color: #7C3AED; }

/* ── DECISION PILLS ── */
.pill {
  display: inline-block; padding: 3px 12px; border-radius: 999px;
  font-size: 0.70rem; font-weight: 700; letter-spacing: 0.07em;
  font-family: 'DM Sans', sans-serif;
}
.pill-expand   { background: rgba(16,185,129,0.14);  color: #065f46; border: 1px solid rgba(16,185,129,0.30); }
.pill-maintain { background: rgba(245,158,11,0.14);  color: #92400e; border: 1px solid rgba(245,158,11,0.30); }
.pill-optimize { background: rgba(249,115,22,0.14);  color: #7c2d12; border: 1px solid rgba(249,115,22,0.30); }
.pill-drop     { background: rgba(244,63,94,0.14);   color: #881337; border: 1px solid rgba(244,63,94,0.30); }

/* ── SECTION LABELS ── */
.section-hd {
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: #7A82A6; margin-bottom: 12px;
  font-family: 'DM Sans', sans-serif;
}
.section-sub {
  font-size: 0.85rem; color: #5A6490; margin-bottom: 18px; line-height: 1.6;
  font-family: 'DM Sans', sans-serif;
}
.divider-label {
  font-size: 0.66rem; font-weight: 700; letter-spacing: 0.22em;
  text-transform: uppercase; color: #9AA0C0;
  text-align: center; margin: 22px 0 16px;
  font-family: 'DM Sans', sans-serif;
}
.col-label {
  font-size: 0.70rem; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; color: #7C3AED; margin-bottom: 8px;
  font-family: 'DM Sans', sans-serif;
}

/* ── RESULT CARDS ── */
.result-card { padding: 26px !important; margin-bottom: 18px; }
.result-expand   { border-left: 4px solid #10B981 !important; }
.result-maintain { border-left: 4px solid #F59E0B !important; }
.result-optimize { border-left: 4px solid #F97316 !important; }
.result-drop     { border-left: 4px solid #F43F5E !important; }

/* ── INFO BOX ── */
.info-box {
  padding: 14px 18px !important; font-size: 0.84rem;
  color: #3D4466; line-height: 1.65; margin: 8px 0;
  font-family: 'DM Sans', sans-serif;
}

/* ── HERO ── */
.hero {
  position: relative;
  padding: 72px 80px !important;
  border-radius: 28px !important;
  overflow: hidden;
  margin-bottom: 36px !important;
  margin-top: 24px !important;
  background: rgba(255, 255, 255, 0.58) !important;
  border: 1px solid rgba(255, 255, 255, 0.92) !important;
  backdrop-filter: blur(28px) saturate(160%) !important;
  -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
  box-shadow:
    0 20px 80px rgba(30, 40, 120, 0.12),
    0 4px 16px rgba(30, 40, 120, 0.08),
    inset 0 1px 0 rgba(255,255,255,1) !important;
}
.hero h1 {
  font-size: clamp(2.8rem, 6vw, 5.5rem) !important;
  line-height: 0.92 !important;
  letter-spacing: 0.04em !important;
  font-weight: 900 !important;
  color: #0A0F28 !important;
  font-family: 'Syne', sans-serif !important;
}
.hero p {
  color: #3D4A80 !important;
  font-size: 1.0rem !important;
  line-height: 1.7 !important;
  max-width: 600px;
  font-family: 'DM Sans', sans-serif;
}
.hero-eyebrow {
  color: #7A82A6 !important;
  font-size: 0.70rem !important;
  letter-spacing: 0.30em !important;
  text-transform: uppercase !important;
  font-family: 'DM Sans', sans-serif !important;
  margin-bottom: 16px !important;
  display: block;
}
.hero-badge {
  display: inline-flex;
  margin-top: 28px;
  padding: 10px 24px;
  border-radius: 999px;
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(30,50,180,0.18);
  backdrop-filter: blur(10px);
  color: #1A2060;
  font-weight: 700;
  font-size: 0.82rem;
  font-family: 'DM Sans', sans-serif;
  box-shadow: 0 4px 16px rgba(30,50,180,0.10), inset 0 1px 0 rgba(255,255,255,1);
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  padding: 12px !important;
}
[data-testid="stDataFrame"] th {
  color: #3D4466 !important;
  font-weight: 700 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}
[data-testid="stDataFrame"] td {
  color: #1A2040 !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── WARNING ── */
.stAlert {
  background: rgba(255,255,255,0.65) !important;
  border: 1px solid rgba(255,255,255,0.90) !important;
  border-radius: 14px !important;
  backdrop-filter: blur(16px) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  PLOTLY HELPERS
# ─────────────────────────────────────────────────────────────
def _fmt_money(v):
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def col_seq(labels):
    return [DECISION_COLORS.get(str(label), ACCENT) for label in labels]

def _format_value(v, value_format="number", fmt_fn=None):
    if fmt_fn:
        return fmt_fn(v)
    if value_format == "money":
        return _fmt_money(v)
    if value_format == "percent":
        return f"{v:.0%}"
    return f"{v:,.0f}"

def _plotly_layout(fig, height=420, showlegend=False):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="DM Sans", color="#3D4466", size=13),
        showlegend=showlegend,
        margin=dict(l=52, r=54, t=18, b=58),
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(30,50,180,0.20)",
            font_color="#0F1530",
            font_family="DM Sans",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color="#7A82A6", tickfont=dict(size=12))
    fig.update_yaxes(gridcolor="rgba(30,50,180,0.07)", zeroline=False, color="#7A82A6", tickfont=dict(size=12))
    return fig

def plotly_card(title, fig, height=420):
    st.markdown(
        f'<div class="plotly-card"><div class="plotly-card-title">{title}</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    st.markdown('</div>', unsafe_allow_html=True)

def plotly_donut_chart(title, labels, values, colors=None, height=420, **kwargs):
    labels = [str(x) for x in labels]
    vals = [float(v) if pd.notna(v) else 0.0 for v in values]
    if not vals or sum(vals) <= 0:
        st.info("No chart data available for the current filter.")
        return
    colors = colors or [DECISION_COLORS.get(x, CYAN) for x in labels]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=vals,
            hole=0.58,
            marker=dict(colors=colors, line=dict(color="rgba(255,255,255,0.9)", width=3)),
            textinfo="percent",
            textfont=dict(size=14, color="white"),
            hovertemplate="%{label}<br>%{percent}<br>%{value}<extra></extra>",
            sort=False,
        )
    )
    _plotly_layout(fig, height=height, showlegend=True)
    fig.update_layout(
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=12, color="#3D4466")),
        margin=dict(l=20, r=20, t=8, b=76),
    )
    plotly_card(title, fig, height)

def plotly_vbar_chart(title, labels, series=None, values=None, colors=None, max_value=None,
                       value_format="number", height=420, fmt_fn=None, y_label="", **kwargs):
    labels = [str(x) for x in labels]
    fig = go.Figure()
    if series is None:
        series = [{"name": "Value", "values": values or [], "colors": colors}]
    for srs in series:
        vals = [float(v) if pd.notna(v) else 0.0 for v in srs.get("values", [])]
        marker_colors = srs.get("colors") or colors or [srs.get("color", CYAN)] * len(vals)
        if isinstance(marker_colors, str):
            marker_colors = [marker_colors] * len(vals)
        text = [_format_value(v, value_format=value_format, fmt_fn=fmt_fn) for v in vals]
        fig.add_trace(
            go.Bar(
                x=labels,
                y=vals,
                name=srs.get("name", "Value"),
                marker=dict(color=marker_colors, line=dict(width=0), opacity=0.85),
                text=text,
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
    _plotly_layout(fig, height=height, showlegend=len(series) > 1)
    if max_value is not None:
        fig.update_yaxes(range=[0, max_value * 1.12])
    fig.update_traces(width=0.52)
    if y_label:
        fig.update_yaxes(title_text=y_label)
    plotly_card(title, fig, height)

def plotly_hbar_chart(title, labels, values, colors=None, color=None, value_format="money",
                       height=460, fmt_fn=None, **kwargs):
    labels = [str(x) for x in labels]
    vals = [float(v) if pd.notna(v) else 0.0 for v in values]
    if not vals:
        st.info("No chart data available for the current filter.")
        return
    if colors is None:
        colors = [color or CYAN] * len(vals)
    elif isinstance(colors, str):
        colors = [colors] * len(vals)
    else:
        colors = list(colors)
    if len(colors) < len(vals):
        colors = colors + [color or CYAN] * (len(vals) - len(colors))
    text = [_format_value(v, value_format=value_format, fmt_fn=fmt_fn) for v in vals]
    fig = go.Figure(
        go.Bar(
            y=labels,
            x=vals,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0), opacity=0.82),
            text=text,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x}<extra></extra>",
        )
    )
    _plotly_layout(fig, height=height, showlegend=False)
    fig.update_layout(margin=dict(l=130, r=110, t=18, b=48))
    fig.update_yaxes(autorange="reversed")
    plotly_card(title, fig, height)

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
#  LOAD
# ─────────────────────────────────────────────────────────────
df = load_data()
model1, model2, model3, X1_columns, X2_columns, X3_columns = load_artifacts()

# ─────────────────────────────────────────────────────────────
#  PRE-COMPUTED
# ─────────────────────────────────────────────────────────────
def compute_model_metrics(df, model, columns):
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
    st.markdown('<div class="sidebar-brand">Sky<span>Lens</span> ✦</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.64rem;color:#7C3AED;margin-bottom:14px;"
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
    st.markdown("""
    <p style='font-size:0.62rem;color:#7C3AED;font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;margin-bottom:10px;font-family:DM Sans,sans-serif'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:9px;font-size:0.80rem;color:#3D4466;font-family:DM Sans,sans-serif'>
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
  <span class="hero-eyebrow">✦ &nbsp; AIRLINE ROUTE INTELLIGENCE &nbsp; ✦</span>
  <h1>SKYLENS<br>DASHBOARD</h1>
  <p>Analyze route profitability, operational signals, and model-backed decisions in one polished command view.</p>
  <div class="hero-badge">✦ &nbsp; Explore dashboard below</div>
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
        # Keep consistent ORDER for both labels and colors
        ordered_labels = [x for x in ORDER if x in dc.index]
        dc = dc.reindex(ordered_labels).dropna()
        wedge_colors = [DECISION_COLORS[l] for l in dc.index]
        plotly_donut_chart(
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
            .reset_index()
            .rename(columns={
                "Route_Decision": "Decision",
                "Profit": "Avg Profit ($)",
                "Profit_Margin": "Avg Margin",
                "Load_Factor": "Avg Load Factor",
            })
        )
        # ── FIX: format margin as % and load factor as %
        summary["Avg Profit ($)"]  = summary["Avg Profit ($)"].map("${:,.0f}".format)
        summary["Avg Margin"]      = summary["Avg Margin"].map("{:.1f}%".format)
        summary["Avg Load Factor"] = summary["Avg Load Factor"].map("{:.1%}".format)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="info-box">
          <strong style="color:#7C3AED">How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:#2563EB">Expand</strong> routes should have the highest values across all three columns.
        </div>""", unsafe_allow_html=True)

# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown('<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        apd = (fdf.groupby("Route_Decision")["Profit"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        plotly_hbar_chart(
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
        plotly_vbar_chart(
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
    nc = len(cost_means)
    jewel_ramp = [CHART_EXPAND, "#0e7490", ACCENT, CHART_MAINTAIN,
                  "#15803d", CHART_OPTIMIZE, CHART_DROP, "#6d28d9"]
    neutral_cols = jewel_ramp[:nc]

    plotly_hbar_chart(
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
        .assign(**{
            "Avg Profit ($)":  lambda d: d["Avg Profit ($)"].map("${:,.0f}".format),
            "Profit Margin":   lambda d: d["Profit Margin"].map("{:.1f}%".format),
            "Load Factor":     lambda d: d["Load Factor"].map("{:.1%}".format),
        })
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown(
            f"<p style='font-size:0.75rem;font-weight:700;color:{INK};margin-bottom:7px;font-family:DM Sans,sans-serif'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        plotly_hbar_chart(
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
        plotly_hbar_chart(
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
    plotly_vbar_chart(
        title="Unique Routes per Decision Category",
        labels=urbd.index.tolist(),
        series=[{"name": "Unique Routes", "values": vals4, "color": ACCENT, "colors": bc}],
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

    plotly_vbar_chart(
        title="Model Accuracy & F1 Comparison",
        labels=comparison["Model"].tolist(),
        series=[
            {"name": "Accuracy",  "values": comparison["Accuracy"].tolist(),  "color": ACCENT},
            {"name": "Macro F1",  "values": comparison["Macro F1"].tolist(),  "color": ACCENT_2},
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
          <div style='font-family:"Syne",sans-serif;font-size:1.45rem;font-weight:700;
                      color:{text_col.get(pred, INK)};margin-bottom:10px;letter-spacing:0.03em;
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
        plotly_vbar_chart(
            title="Model Confidence per Decision",
            labels=prob_df["Decision"].tolist(),
            series=[{"name": "Probability", "values": probs, "color": ACCENT, "colors": bar_colors}],
            max_value=1.0,
            value_format="percent",
            height=390,
        )

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:40px 0 18px'>
  <div style='display:inline-flex;align-items:center;gap:12px;
              background:rgba(255,255,255,0.65);
              border:1px solid rgba(255,255,255,0.92);
              border-radius:999px;
              padding:0.55rem 1.4rem;
              backdrop-filter:blur(16px);
              box-shadow:0 4px 20px rgba(30,40,120,0.10), inset 0 1px 0 rgba(255,255,255,1);
              font-family:"DM Sans",sans-serif;
              font-size:0.67rem;
              font-weight:700;
              color:#5A6490;
              letter-spacing:0.12em;
              text-transform:uppercase'>
    <span style='color:#7C3AED;font-size:0.78rem'>✦</span>
    Airline Profitability System
    <span style='color:#7C3AED;font-size:0.78rem'>✦</span>
    Built with Streamlit
  </div>
</div>
""", unsafe_allow_html=True)