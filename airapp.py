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
#  THEME TOKENS  ← edit only these to restyle the entire app
# ─────────────────────────────────────────────────────────────
BG_BLOB_A = "#ddd6fe"    # violet blob
BG_BLOB_B = "#fbcfe8"    # blush pink blob
BG_BLOB_C = "#bae6fd"    # sky blue blob

GLASS_BG     = "rgba(255,255,255,0.45)"
GLASS_BORDER = "rgba(255,255,255,0.72)"
GLASS_SHADOW = "0 8px 32px rgba(100,80,160,0.13), 0 1.5px 6px rgba(100,80,160,0.07)"
GLASS_BLUR   = "blur(18px)"

INK       = "#1e1b4b"
INK_SOFT  = "#4c1d95"
INK_MUTED = "#7c6ea0"

ACCENT    = "#7c3aed"
ACCENT_DK = "#5b21b6"

COLOR_GREEN  = "#065f46"
COLOR_YELLOW = "#78350f"
COLOR_ORANGE = "#7c2d12"
COLOR_PINK   = "#831843"

CHART_EXPAND   = "#34d399"
CHART_MAINTAIN = "#fbbf24"
CHART_OPTIMIZE = "#fb923c"
CHART_ORANGE   = "#fb923c"
CHART_DROP     = "#f472b6"
CHART_NEUTRAL  = [
    "#a78bfa","#67e8f9","#86efac","#fde68a",
    "#fca5a5","#f9a8d4","#c4b5fd","#7dd3fc",
]

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS — pastel glassmorphism
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700&display=swap');

:root {{
    --ink:       {INK};
    --ink-soft:  {INK_SOFT};
    --ink-muted: {INK_MUTED};
    --accent:    {ACCENT};
    --glass-bg:  {GLASS_BG};
    --glass-bd:  {GLASS_BORDER};
    --blur:      {GLASS_BLUR};
    --r-sm:  10px; --r-md: 18px; --r-lg: 26px; --r-xl: 34px;
}}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
}}

/* PAGE BACKGROUND — soft pastel mesh */
.stApp {{
    min-height: 100vh;
    background:
        radial-gradient(ellipse 70% 60% at 10%  20%, {BG_BLOB_A}cc 0%, transparent 65%),
        radial-gradient(ellipse 55% 50% at 90%  10%, {BG_BLOB_B}bb 0%, transparent 60%),
        radial-gradient(ellipse 60% 70% at 55%  90%, {BG_BLOB_C}aa 0%, transparent 60%),
        linear-gradient(135deg, #f5f3ff 0%, #fdf2f8 50%, #f0f9ff 100%);
    background-attachment: fixed;
}}
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: rgba(245,243,255,0.70) !important;
    border-right: 1.5px solid rgba(167,139,250,0.28) !important;
    backdrop-filter: {GLASS_BLUR} !important;
    -webkit-backdrop-filter: {GLASS_BLUR} !important;
    box-shadow: 4px 0 24px rgba(124,58,237,0.07) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {{ color: {INK_SOFT} !important; }}

/* METRIC CARDS */
[data-testid="metric-container"] {{
    background: rgba(255,255,255,0.52) !important;
    border: 1.5px solid rgba(255,255,255,0.75) !important;
    border-radius: var(--r-md) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.10),
                inset 0 1px 0 rgba(255,255,255,0.85) !important;
    padding: 20px 24px !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.16),
                inset 0 1px 0 rgba(255,255,255,0.85) !important;
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
    font-size: 0.65rem !important; font-weight: 700 !important;
    letter-spacing: 0.12em !important; text-transform: uppercase !important;
    color: {INK_MUTED} !important;
}}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {{
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 2.0rem !important; font-weight: 700 !important;
    color: {INK} !important; letter-spacing: -0.02em !important;
}}

/* TABS */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.40);
    border: 1.5px solid rgba(255,255,255,0.65);
    border-radius: var(--r-md); padding: 5px; gap: 3px;
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(124,58,237,0.08);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: var(--r-sm) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.80rem !important;
    color: {INK_MUTED} !important; padding: 7px 16px !important;
    background: transparent !important; border: none !important;
    transition: all 0.15s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(167,139,250,0.18) !important;
    color: {INK_SOFT} !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {ACCENT} 0%, #a855f7 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.35),
                inset 0 1px 0 rgba(255,255,255,0.20) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ background: transparent; padding-top: 1.5rem; }}

/* HEADINGS */
h1, h2, h3, h4 {{
    font-family: 'Fraunces', Georgia, serif !important;
    color: {INK} !important; letter-spacing: -0.02em !important;
    font-weight: 700 !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {{
    color: {INK_SOFT}; line-height: 1.70; font-size: 0.90rem;
}}

/* WIDGET LABELS */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {{
    color: {INK} !important; font-weight: 600 !important;
    font-size: 0.79rem !important; letter-spacing: 0.03em !important;
}}

/* INPUTS */
.stSelectbox [data-baseweb="select"] div,
.stTextInput input, .stNumberInput input {{
    color: {INK} !important;
    background: rgba(255,255,255,0.62) !important;
    border: 1.5px solid rgba(167,139,250,0.35) !important;
    border-radius: var(--r-sm) !important;
    backdrop-filter: blur(8px) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}}
.stSelectbox [data-baseweb="select"] div:focus-within,
.stTextInput input:focus, .stNumberInput input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}}

/* DATAFRAME */
[data-testid="stDataFrame"] {{
    border-radius: var(--r-md) !important; overflow: hidden !important;
    border: 1.5px solid rgba(255,255,255,0.70) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.09) !important;
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(10px) !important;
}}

/* EXPANDER */
[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.42) !important;
    border: 1.5px solid rgba(255,255,255,0.68) !important;
    border-radius: var(--r-md) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.08) !important;
}}
[data-testid="stExpander"] summary p {{
    color: {INK} !important; font-weight: 600 !important; font-size: 0.88rem !important;
}}

/* FORM */
[data-testid="stForm"] {{
    background: rgba(255,255,255,0.50) !important;
    border: 1.5px solid rgba(255,255,255,0.72) !important;
    border-radius: var(--r-xl) !important;
    backdrop-filter: blur(18px) !important; -webkit-backdrop-filter: blur(18px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.10),
                inset 0 1px 0 rgba(255,255,255,0.80) !important;
    padding: 24px 28px 30px !important;
}}

/* SUBMIT BUTTON */
[data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(135deg, {ACCENT} 0%, #a855f7 100%) !important;
    border: none !important; border-radius: var(--r-md) !important;
    color: #fff !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.88rem !important;
    letter-spacing: 0.03em !important; padding: 12px 32px !important;
    width: 100% !important; transition: all 0.15s ease !important;
    box-shadow: 0 4px 18px rgba(124,58,237,0.35),
                inset 0 1px 0 rgba(255,255,255,0.18) !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.45),
                inset 0 1px 0 rgba(255,255,255,0.18) !important;
}}
[data-testid="stFormSubmitButton"] > button:active {{
    transform: translateY(1px) !important;
    box-shadow: 0 2px 10px rgba(124,58,237,0.25) !important;
}}

/* REGULAR BUTTONS */
.stButton > button {{
    background: rgba(255,255,255,0.55) !important;
    border: 1.5px solid rgba(167,139,250,0.40) !important;
    border-radius: var(--r-sm) !important; color: {INK} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    padding: 9px 22px !important; backdrop-filter: blur(8px) !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.08) !important;
}}
.stButton > button:hover {{
    background: rgba(167,139,250,0.20) !important;
    border-color: rgba(124,58,237,0.50) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(124,58,237,0.16) !important;
}}

/* ALERTS / HR */
[data-testid="stAlert"] {{
    border-radius: var(--r-md) !important;
    backdrop-filter: blur(8px) !important;
    background: rgba(255,255,255,0.50) !important;
    border: 1.5px solid rgba(255,255,255,0.65) !important;
}}
[data-testid="stAlert"] p {{ color: inherit !important; }}
hr {{
    border: none !important;
    border-top: 1.5px solid rgba(167,139,250,0.22) !important;
    margin: 1.5rem 0 !important;
}}

/* ═══════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════ */

/* Hero */
.hero {{
    position: relative; overflow: hidden;
    border-radius: var(--r-xl); padding: 44px 52px; margin-bottom: 28px;
    background: linear-gradient(135deg,
        rgba(167,139,250,0.55) 0%, rgba(251,207,232,0.50) 50%,
        rgba(186,230,253,0.50) 100%);
    border: 1.5px solid rgba(255,255,255,0.75);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(124,58,237,0.14),
                inset 0 1px 0 rgba(255,255,255,0.80);
}}
.hero::before {{
    content:""; position:absolute; inset:0;
    background: radial-gradient(ellipse 60% 80% at 85% 50%,
        rgba(255,255,255,0.30) 0%, transparent 70%);
    pointer-events:none;
}}
.hero-eyebrow {{
    font-size:0.63rem; font-weight:700; letter-spacing:0.18em;
    text-transform:uppercase; color:rgba(109,40,217,0.70);
    margin-bottom:10px; font-family:'Plus Jakarta Sans',sans-serif;
}}
.hero h1 {{
    font-family:'Fraunces',Georgia,serif !important;
    font-size:2.7rem !important; font-weight:700 !important;
    color:{INK} !important; margin:0 0 12px 0 !important;
    letter-spacing:-0.03em !important; line-height:1.12 !important;
}}
.hero p {{
    color:{INK_SOFT} !important; font-size:0.92rem; margin:0;
    max-width:540px; line-height:1.70; font-weight:400;
}}
.hero-glyph {{
    position:absolute; right:52px; top:50%; transform:translateY(-50%);
    font-size:9rem; opacity:0.13; color:{ACCENT};
    pointer-events:none; user-select:none; line-height:1;
}}

/* Sidebar brand */
.sidebar-brand {{
    font-family:'Fraunces',Georgia,serif; font-size:1.50rem;
    font-weight:700; color:{INK}; padding:4px 0 16px 0;
    border-bottom:1.5px solid rgba(167,139,250,0.25);
    margin-bottom:16px; letter-spacing:-0.02em;
}}
.sidebar-brand span {{ color:{ACCENT}; }}

/* Section helpers */
.section-hd {{
    font-family:'Fraunces',Georgia,serif; font-size:1.05rem;
    font-weight:700; color:{INK}; margin:0 0 4px 0; letter-spacing:-0.01em;
}}
.section-sub {{
    font-size:0.82rem; color:{INK_MUTED}; margin:0 0 20px 0; font-weight:400;
}}

/* Glass info box */
.info-box {{
    background:rgba(255,255,255,0.48); border:1.5px solid rgba(255,255,255,0.70);
    border-radius:var(--r-sm); backdrop-filter:blur(10px);
    padding:14px 18px; font-size:0.84rem; color:{INK_SOFT};
    margin-bottom:14px; line-height:1.78;
}}

/* Decision pills */
.pill {{
    display:inline-block; padding:3px 13px; border-radius:99px;
    font-size:0.69rem; font-weight:700; letter-spacing:0.06em;
    text-transform:uppercase; border:1.5px solid transparent;
    backdrop-filter:blur(6px);
}}
.pill-expand   {{ background:rgba(52,211,153,0.18);  color:#065f46; border-color:rgba(52,211,153,0.45); }}
.pill-maintain {{ background:rgba(251,191,36,0.18);  color:#78350f; border-color:rgba(251,191,36,0.45); }}
.pill-optimize {{ background:rgba(251,146,60,0.18);  color:#7c2d12; border-color:rgba(251,146,60,0.45); }}
.pill-drop     {{ background:rgba(244,114,182,0.18); color:#831843; border-color:rgba(244,114,182,0.45); }}

/* Result card */
.result-card {{
    border-radius:var(--r-lg); padding:28px 34px; margin:20px 0;
    backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
    border:1.5px solid rgba(255,255,255,0.72);
    box-shadow:0 8px 32px rgba(124,58,237,0.10),
               inset 0 1px 0 rgba(255,255,255,0.75);
}}
.result-expand  {{
    background:linear-gradient(135deg,rgba(52,211,153,0.18) 0%,rgba(255,255,255,0.50) 100%);
    border-left:4px solid {CHART_EXPAND};
}}
.result-maintain {{
    background:linear-gradient(135deg,rgba(251,191,36,0.16) 0%,rgba(255,255,255,0.50) 100%);
    border-left:4px solid {CHART_MAINTAIN};
}}
.result-optimize {{
    background:linear-gradient(135deg,rgba(251,146,60,0.16) 0%,rgba(255,255,255,0.50) 100%);
    border-left:4px solid {CHART_OPTIMIZE};
}}
.result-drop {{
    background:linear-gradient(135deg,rgba(244,114,182,0.16) 0%,rgba(255,255,255,0.50) 100%);
    border-left:4px solid {CHART_DROP};
}}

/* Divider label */
.divider-label {{
    display:flex; align-items:center; gap:12px; margin:26px 0 16px;
    color:{INK_MUTED}; font-size:0.70rem; font-weight:700;
    letter-spacing:0.12em; text-transform:uppercase;
    font-family:'Plus Jakarta Sans',sans-serif;
}}
.divider-label::before, .divider-label::after {{
    content:""; flex:1; height:1px;
    background:linear-gradient(90deg,transparent,rgba(167,139,250,0.35),transparent);
}}

/* Column section label */
.col-label {{
    font-size:0.72rem; font-weight:700; color:{INK_MUTED};
    letter-spacing:0.10em; text-transform:uppercase; margin-bottom:14px;
    font-family:'Plus Jakarta Sans',sans-serif;
}}
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
#  CHART HELPER  (axes match pastel theme; data logic unchanged)
# ─────────────────────────────────────────────────────────────
def clean_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("none"); fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#c4b5fd")
    ax.spines["bottom"].set_color("#c4b5fd")
    ax.tick_params(colors=INK_MUTED, labelsize=8.5)
    ax.xaxis.label.set_color(INK_MUTED)
    ax.yaxis.label.set_color(INK_MUTED)
    ax.title.set_color(INK)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    ax.grid(axis="y", color="#ede9fe", linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)
    return fig, ax

def col_seq(labels):
    return [DECISION_COLORS.get(l, "#c4b5fd") for l in labels]

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
    st.markdown('<div class="sidebar-brand">Sky<span>Lens</span> ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.72rem;color:{INK_MUTED};margin-bottom:16px;"
        "font-weight:700;letter-spacing:0.10em;text-transform:uppercase'>Filter View</p>",
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
    <p style='font-size:0.70rem;color:{INK_MUTED};font-weight:700;letter-spacing:0.10em;
    text-transform:uppercase;margin-bottom:10px'>Decision labels</p>
    <div style='display:flex;flex-direction:column;gap:9px;font-size:0.82rem;color:{INK_SOFT}'>
      <div><span class='pill pill-expand'>Expand</span>&nbsp;&nbsp;High profit &amp; demand</div>
      <div><span class='pill pill-maintain'>Maintain</span>&nbsp;&nbsp;Stable performer</div>
      <div><span class='pill pill-optimize'>Optimize</span>&nbsp;&nbsp;Room to improve</div>
      <div><span class='pill pill-drop'>Drop</span>&nbsp;&nbsp;Losing money</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FILTER  (logic unchanged)
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

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

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
        wc = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
              "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
        fig, ax = clean_fig((5, 4.8))
        wedges, texts, autotexts = ax.pie(
            dc.values, labels=dc.index, autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index], startangle=90,
            wedgeprops={"linewidth":3,"edgecolor":(1,1,1,0.85)},
            textprops={"color":INK,"fontsize":9.5},
            pctdistance=0.78,
        )
        for at in autotexts:
            at.set_fontsize(8.5); at.set_color(INK); at.set_fontweight("bold")
        ax.set_title("Share of Flights by Decision", pad=14)
        st.pyplot(fig)

    with right:
        st.markdown('<p class="section-hd">Average metrics by decision</p>', unsafe_allow_html=True)
        summary = (
            fdf.groupby("Route_Decision")[["Profit","Profit_Margin","Load_Factor"]]
            .mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()])
            .round(3).reset_index()
            .rename(columns={
                "Route_Decision":"Decision","Profit":"Avg Profit ($)",
                "Profit_Margin":"Avg Margin","Load_Factor":"Avg Load Factor",
            })
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="info-box">
          <strong>How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong>Expand</strong> routes should have the highest values across all three columns.
        </div>""", unsafe_allow_html=True)

# ── TAB 2 · PERFORMANCE DRIVERS ──────────────────────────────
with tab2:
    st.markdown('<p class="section-hd">What separates strong routes from weak ones?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">These charts reveal the metrics most associated with route profitability.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        apd = (fdf.groupby("Route_Decision")["Profit"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        fig, ax = clean_fig((6, 4))
        bars = ax.bar(apd.index, apd.values, color=col_seq(apd.index.tolist()),
                      width=0.52, edgecolor=(1,1,1,0.80), linewidth=2)
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x()+b.get_width()/2, h+abs(apd.values).max()*0.025,
                    f"${h:,.0f}", ha="center", va="bottom",
                    fontsize=8, color=INK_MUTED, fontweight="700")
        ax.set_ylabel("Average Profit ($)"); ax.set_title("Average Profit by Decision")
        st.pyplot(fig)

    with right:
        ald = (fdf.groupby("Route_Decision")["Load_Factor"].mean()
               .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna())
        fig, ax = clean_fig((6, 4))
        bars = ax.bar(ald.index, ald.values, color=col_seq(ald.index.tolist()),
                      width=0.52, edgecolor=(1,1,1,0.80), linewidth=2)
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x()+b.get_width()/2, h+0.006, f"{h:.0%}",
                    ha="center", va="bottom",
                    fontsize=8, color=INK_MUTED, fontweight="700")
        ax.set_ylabel("Average Seat Occupancy"); ax.set_title("Seat Occupancy by Decision")
        st.pyplot(fig)

    st.markdown('<div class="divider-label">Cost breakdown</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Where is the money going?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">The biggest cost components across all filtered flights.</p>', unsafe_allow_html=True)

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
    fig, ax = clean_fig((9, 4))
    bars = ax.barh(cost_means.index, cost_means.values,
                   color=CHART_NEUTRAL[:len(cost_means)],
                   edgecolor=(1,1,1,0.80), linewidth=2, height=0.55)
    mx = cost_means.max()
    for b in bars:
        w = b.get_width()
        ax.text(w+mx*0.012, b.get_y()+b.get_height()/2,
                f"${w:,.0f}", va="center", fontsize=8, color=INK_MUTED, fontweight="700")
    ax.set_xlabel("Average Cost per Flight ($)"); ax.set_title("Top Cost Drivers")
    st.pyplot(fig)

# ── TAB 3 · ROUTE ACTIONS ────────────────────────────────────
with tab3:
    st.markdown('<p class="section-hd">Which routes need attention?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A quick view of your best and worst performing routes.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "Top routes currently classified as Expand</p>", unsafe_allow_html=True)
    expand_routes = (
        fdf[fdf["Route_Decision"] == "Expand"]
        .sort_values("Profit", ascending=False)
        [["Route","Profit","Profit_Margin","Load_Factor"]].head(10)
        .rename(columns={"Profit":"Avg Profit ($)","Profit_Margin":"Profit Margin","Load_Factor":"Load Factor"})
    )
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Top 10 routes by total profit</p>", unsafe_allow_html=True)
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(top.index, top.values, color=CHART_EXPAND,
                edgecolor=(1,1,1,0.80), linewidth=2, height=0.55)
        ax.set_xlabel("Total Profit ($)"); ax.set_title("Top 10 Routes")
        st.pyplot(fig)

    with right:
        st.markdown(
            f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Bottom 10 routes by total profit</p>", unsafe_allow_html=True)
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = clean_fig((7, 5))
        ax.barh(worst.index, worst.values, color=CHART_DROP,
                edgecolor=(1,1,1,0.80), linewidth=2, height=0.55)
        ax.set_xlabel("Total Profit ($)"); ax.set_title("Bottom 10 Routes")
        st.pyplot(fig)

# ── TAB 4 · ROUTE STABILITY ──────────────────────────────────
with tab4:
    st.markdown('<p class="section-hd">How consistent are route decisions over time?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">A route that frequently flips between categories may need structural attention.</p>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Routes with most decision changes</p>", unsafe_allow_html=True)
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown(
            f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Routes seen in the most decision states</p>", unsafe_allow_html=True)
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)

    st.markdown('<div class="divider-label">Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "How many unique routes appear in each category?</p>", unsafe_allow_html=True)

    urbd = (
        df.groupby("Route_Decision")["Route"].nunique().reset_index()
        .rename(columns={"Route":"Unique Routes"})
        .set_index("Route_Decision").reindex(ORDER).dropna()
    )
    bc_map = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
              "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
    bc = [bc_map.get(i,"#c4b5fd") for i in urbd.index]
    fig, ax = clean_fig((8, 4))
    bars = ax.bar(urbd.index, urbd["Unique Routes"], color=bc, width=0.52,
                  edgecolor=(1,1,1,0.80), linewidth=2)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x()+b.get_width()/2, h+0.3, f"{int(h)}",
                ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
    ax.set_ylabel("Number of Unique Routes"); ax.set_title("Unique Routes per Decision Category")
    st.pyplot(fig)

    patches = [mpatches.Patch(color=bc_map.get(d,"#c4b5fd"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5,0.5)); fig2.patch.set_alpha(0); ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4,
               prop={"size":9}, labelcolor=INK)
    st.pyplot(fig2)

# ── TAB 5 · PREDICTION TOOL ──────────────────────────────────
with tab5:
    st.markdown('<p class="section-hd">Simulate a route scenario</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter route characteristics and our model will suggest the best decision.</p>', unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
        "How accurate are the models?</p>", unsafe_allow_html=True)
    fig, ax = clean_fig((8, 3.5))
    x = np.arange(len(comparison)); w = 0.30
    b1 = ax.bar(x-w/2, comparison["Accuracy"], w, label="Accuracy",
                color="#a78bfa", edgecolor=(1,1,1,0.80), linewidth=2)
    b2 = ax.bar(x+w/2, comparison["Macro F1"],  w, label="Macro F1",
                color="#6ee7b7", edgecolor=(1,1,1,0.80), linewidth=2)
    for b in list(b1)+list(b2):
        h = b.get_height()
        ax.text(b.get_x()+b.get_width()/2, h+0.006, f"{h:.0%}",
                ha="center", fontsize=7.5, color=INK_MUTED, fontweight="700")
    ax.set_xticks(x); ax.set_xticklabels(comparison["Model"], fontsize=8.5)
    ax.set_ylim(0, 1.15); ax.set_ylabel("Score")
    ax.set_title("Model Accuracy & F1 Comparison")
    ax.legend(frameon=False, fontsize=9); plt.xticks(rotation=10)
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
        ["With Revenue Variables","Without Revenue Variables","Only Pre-Operational Features"],
        key="model_choice_select",
    )

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<p class="col-label">✈ Flight basics</p>', unsafe_allow_html=True)
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)

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

        submitted = st.form_submit_button("✈  Get Route Decision")

    # ── PREDICTION LOGIC  (unchanged) ────────────────────────
    if submitted:
        if model_choice == "With Revenue Variables":
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
                "Ticket_Revenue":ticket_revenue,"Ancillary_Revenue":ancillary_revenue,
            }
            inp=prepare_input(pd.DataFrame([row]),X1_columns)
            pred=model1.predict(inp)[0]; prob=model1.predict_proba(inp)[0]; cls=model1.classes_
        elif model_choice == "Without Revenue Variables":
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
                "Fuel_Cost":fuel_cost,"Maintenance_Cost":maintenance_cost,
                "Crew_Cost":crew_cost,"Depreciation_Cost":depreciation_cost,
                "Insurance_Cost":insurance_cost,"Airport_Fees":airport_fees,
                "Catering_Cost":catering_cost,"Handling_Cost":handling_cost,
                "Navigation_Fees":navigation_fees,"Sales_Distribution_Cost":sales_distribution_cost,
                "Passenger_Service_Cost":passenger_service_cost,"Overhead_Cost":overhead_cost,
                "Marketing_Cost":marketing_cost,"IT_Systems_Cost":it_systems_cost,
            }
            inp=prepare_input(pd.DataFrame([row]),X2_columns)
            pred=model2.predict(inp)[0]; prob=model2.predict_proba(inp)[0]; cls=model2.classes_
        else:
            row = {
                "Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,
                "Passengers":passengers,"Load_Factor":load_factor,
                "Flight_Hours":flight_hours,"Season":season_val,
                "Route_Category":route_category,"Demand_Level":demand_level,
            }
            inp=prepare_input(pd.DataFrame([row]),X3_columns)
            pred=model3.predict(inp)[0]; prob=model3.predict_proba(inp)[0]; cls=model3.classes_

        st.session_state.pred_result = {"prediction":pred,"probabilities":prob,"classes":cls}

    # ── RESULT DISPLAY  (logic unchanged, glass-styled) ──────
    if st.session_state.pred_result is not None:
        res  = st.session_state.pred_result
        pred = res["prediction"]; prob = res["probabilities"]; cls = res["classes"]

        pill_cls   = {"Expand":"pill-expand","Maintain":"pill-maintain",
                      "Optimize":"pill-optimize","Drop":"pill-drop"}
        result_cls = {"Expand":"result-expand","Maintain":"result-maintain",
                      "Optimize":"result-optimize","Drop":"result-drop"}
        text_col   = {"Expand":COLOR_GREEN,"Maintain":COLOR_YELLOW,
                      "Optimize":COLOR_ORANGE,"Drop":COLOR_PINK}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred,"result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred,"")}' style='font-size:0.68rem'>{pred}</span>
          </div>
          <div style='font-family:"Fraunces",Georgia,serif;font-size:1.70rem;font-weight:700;
                      color:{text_col.get(pred,INK)};margin-bottom:10px;letter-spacing:-0.02em'>
            Suggested Decision: {pred}
          </div>
          <p style='color:{INK_SOFT};margin:0;font-size:0.90rem;line-height:1.72'>
            {explanations.get(pred,"")}
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<p style='font-size:0.80rem;font-weight:700;color:{INK};margin-bottom:8px'>"
            "Confidence by decision option</p>", unsafe_allow_html=True)

        prob_df = (pd.DataFrame({"Decision":cls,"Probability":prob})
                   .sort_values("Probability", ascending=False))
        bar_cp = {"Expand":CHART_EXPAND,"Maintain":CHART_MAINTAIN,
                  "Optimize":CHART_ORANGE,"Drop":CHART_DROP}
        fig, ax = clean_fig((6, 3.5))
        bars = ax.bar(
            prob_df["Decision"], prob_df["Probability"],
            color=[bar_cp.get(d,"#c4b5fd") for d in prob_df["Decision"]],
            width=0.45, edgecolor=(1,1,1,0.80), linewidth=2,
        )
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x()+b.get_width()/2, h+0.013, f"{h:.0%}",
                    ha="center", fontsize=9, color=INK_MUTED, fontweight="700")
        ax.set_ylim(0,1.18); ax.set_ylabel("Probability")
        ax.set_title("Model Confidence per Decision")
        st.pyplot(fig)

        st.dataframe(
            prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True),
            use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────
#  FILTERED DATA EXPANDER  (unchanged)
# ─────────────────────────────────────────────────────────────
with st.expander("🗂  Show filtered data"):
    st.dataframe(fdf, use_container_width=True)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;color:{INK_MUTED};font-size:0.75rem;
            padding:36px 0 16px;font-family:"Plus Jakarta Sans",sans-serif;
            letter-spacing:0.05em'>
  SKYLENS ROUTE INTELLIGENCE &nbsp;✦&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  HOW TO TWEAK THE THEME
# ─────────────────────────────────────────────────────────────
# All tokens live under "THEME TOKENS" at the top of this file.
#
# Background mood: change BG_BLOB_A/B/C to any hex — e.g. sage+sand+gold
#   for an earthy feel, or rose+coral+cream for a warmer look.
#
# Glass opacity: raise the alpha in GLASS_BG (e.g. 0.65) for more opacity,
#   lower for a more ethereal look. Pair with GLASS_BLUR for intensity.
#
# Accent colour: ACCENT / ACCENT_DK controls buttons, active tabs, focus rings.
#
# Chart colours: CHART_EXPAND / MAINTAIN / OPTIMIZE / DROP / NEUTRAL.