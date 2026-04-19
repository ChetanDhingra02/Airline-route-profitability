import os
import joblib
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

st.set_page_config(
    page_title="Airline Route Profitability Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

:root {
    --lavender:     #EAE6F8;
    --lavender-mid: #C9BFEF;
    --lavender-dk:  #7B68C8;
    --lavender-floor: #4D3EA0;
    --mint:         #E2F4ED;
    --mint-mid:     #7AC9A8;
    --mint-dk:      #3D9E74;
    --mint-floor:   #27735A;
    --peach:        #FDEAE4;
    --peach-mid:    #F6BBA8;
    --peach-dk:     #D85A30;
    --peach-floor:  #A03A18;
    --sky:          #E3F1FB;
    --lemon:        #FEF7DF;
    --lemon-mid:    #F5D97A;
    --lemon-floor:  #D4B040;
    --blush:        #FCE9F0;
    --blush-mid:    #F2B5CF;
    --blush-floor:  #D490B0;
    --ink:          #1E1B2E;
    --ink-soft:     #4A4663;
    --ink-muted:    #7A758F;
    --surface:      #FAFAF8;
    --border:       rgba(160,150,200,0.20);
    --border-md:    rgba(160,150,200,0.32);
    --top-shine:    rgba(255,255,255,0.90);
    --inner-shine:  inset 0 1px 0 rgba(255,255,255,0.85);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, sans-serif !important;
}

/* ── PAGE BACKGROUND ── */
.stApp {
    background: linear-gradient(135deg, #F0EDFC 0%, #EAF6F2 38%, #FDE8E2 72%, #F0EDFC 100%);
    min-height: 100vh;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.78) !important;
    border-right: 1.5px solid var(--border-md) !important;
    backdrop-filter: blur(14px);
    box-shadow: 4px 0 24px rgba(100,80,160,0.07) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small { color: var(--ink-soft) !important; }

/* ── 3D METRIC CARDS ── */
[data-testid="metric-container"] {
    background: #fff;
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.75);
    border-right: 1.5px solid var(--border);
    border-bottom: 5px solid rgba(180,165,220,0.42);
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow:
        var(--inner-shine),
        0 8px 24px rgba(100,80,160,0.10),
        0 2px 6px rgba(100,80,160,0.06);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow:
        var(--inner-shine),
        0 14px 34px rgba(100,80,160,0.14),
        0 4px 10px rgba(100,80,160,0.08);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--ink-muted) !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {
    font-family: 'DM Serif Display', Georgia, serif !important;
    font-size: 2rem !important;
    color: var(--ink) !important;
}

/* ── 3D TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.65);
    border-radius: 16px;
    padding: 5px;
    gap: 4px;
    border: 1.5px solid var(--border);
    box-shadow: inset 0 2px 8px rgba(100,80,160,0.07);
    backdrop-filter: blur(8px);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 11px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.83rem;
    color: var(--ink-muted) !important;
    padding: 8px 16px;
    background: transparent;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(234,230,248,0.55) !important;
    color: var(--ink-soft) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--lavender-dk) !important;
    color: #fff !important;
    box-shadow:
        0 4px 0 var(--lavender-floor),
        0 6px 16px rgba(123,104,200,0.30),
        inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transform: translateY(-1px);
}
.stTabs [data-baseweb="tab-panel"] { background: transparent; }

/* ── HEADINGS ── */
h1, h2, h3, h4 {
    font-family: 'DM Serif Display', Georgia, serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.02em;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
.stMarkdown p, .stMarkdown li {
    color: var(--ink-soft);
    line-height: 1.7;
}

/* ── WIDGET LABELS ── */
.stSelectbox label, .stNumberInput label,
.stSlider label, .stRadio label,
.stCheckbox label, .stTextInput label {
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
}

/* ── INPUTS (3D inset feel) ── */
.stSelectbox [data-baseweb="select"] div,
.stTextInput input, .stNumberInput input {
    color: var(--ink) !important;
    background: rgba(255,255,255,0.92) !important;
    border-color: var(--border-md) !important;
    border-radius: 10px !important;
    box-shadow: inset 0 2px 6px rgba(100,80,160,0.06) !important;
}

/* ── 3D DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.75);
    border-right: 1.5px solid var(--border);
    border-bottom: 4px solid rgba(180,165,220,0.35);
    box-shadow: var(--inner-shine), 0 6px 18px rgba(100,80,160,0.08);
    background: rgba(255,255,255,0.85);
}

/* ── 3D EXPANDER ── */
[data-testid="stExpander"] {
    border-top: 1.5px solid var(--top-shine) !important;
    border-left: 1.5px solid rgba(255,255,255,0.75) !important;
    border-right: 1.5px solid var(--border) !important;
    border-bottom: 4px solid rgba(180,165,220,0.35) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.75) !important;
    box-shadow: var(--inner-shine), 0 6px 16px rgba(100,80,160,0.07) !important;
}
[data-testid="stExpander"] summary p { color: var(--ink) !important; }

/* ── 3D FORM ── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.60);
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.70);
    border-right: 1.5px solid var(--border);
    border-bottom: 5px solid rgba(180,165,220,0.38);
    border-radius: 20px;
    padding: 12px 20px 22px;
    box-shadow: var(--inner-shine), 0 10px 28px rgba(100,80,160,0.09);
    backdrop-filter: blur(10px);
}

/* ── 3D SUBMIT BUTTON ── */
[data-testid="stFormSubmitButton"] > button {
    background: var(--lavender-dk) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    padding: 13px 32px !important;
    width: 100% !important;
    transition: all 0.12s ease !important;
    box-shadow:
        0 6px 0 var(--lavender-floor),
        0 9px 20px rgba(123,104,200,0.30),
        inset 0 1px 0 rgba(255,255,255,0.22) !important;
    position: relative !important;
    top: 0 !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow:
        0 8px 0 var(--lavender-floor),
        0 14px 28px rgba(123,104,200,0.36),
        inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stFormSubmitButton"] > button:active {
    box-shadow:
        0 2px 0 var(--lavender-floor),
        0 4px 10px rgba(123,104,200,0.20),
        inset 0 1px 0 rgba(255,255,255,0.22) !important;
    transform: translateY(4px) !important;
}

/* ── 3D REGULAR BUTTONS ── */
.stButton > button {
    background: rgba(255,255,255,0.88) !important;
    border-top: 1.5px solid rgba(255,255,255,0.95) !important;
    border-left: 1.5px solid rgba(255,255,255,0.80) !important;
    border-right: 1.5px solid var(--border-md) !important;
    border-bottom: none !important;
    border-radius: 11px !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 10px 26px !important;
    transition: all 0.12s ease !important;
    box-shadow:
        0 5px 0 rgba(160,150,200,0.38),
        0 8px 16px rgba(100,80,160,0.10),
        inset 0 1px 0 rgba(255,255,255,0.90) !important;
    position: relative !important;
    top: 0 !important;
}
.stButton > button:hover {
    background: var(--lavender) !important;
    box-shadow:
        0 7px 0 rgba(160,150,200,0.42),
        0 12px 22px rgba(100,80,160,0.14),
        inset 0 1px 0 rgba(255,255,255,0.90) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    box-shadow:
        0 1px 0 rgba(160,150,200,0.30),
        0 2px 6px rgba(100,80,160,0.07),
        inset 0 1px 0 rgba(255,255,255,0.90) !important;
    transform: translateY(4px) !important;
}

[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stAlert"] p { color: inherit !important; }
hr { border-color: var(--border-md) !important; }

/* ── 3D HERO ── */
.hero {
    background: rgba(255,255,255,0.70);
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.75);
    border-right: 1.5px solid var(--border);
    border-bottom: 6px solid rgba(180,165,220,0.38);
    border-radius: 26px;
    padding: 42px 50px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(14px);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.85),
        0 18px 48px rgba(100,80,160,0.10),
        0 4px 12px rgba(100,80,160,0.06);
}
.hero::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.95), transparent);
}
.hero::after {
    content: "✈";
    position: absolute;
    right: 50px; top: 50%;
    transform: translateY(-50%);
    font-size: 7rem;
    opacity: 0.06;
    color: var(--lavender-dk);
}
.hero h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem !important;
    color: var(--ink) !important;
    margin: 0 0 10px 0 !important;
    letter-spacing: -0.03em !important;
}
.hero p {
    color: var(--ink-soft) !important;
    font-size: 1rem;
    margin: 0;
    max-width: 580px;
    line-height: 1.7;
}

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 1.55rem;
    color: var(--ink);
    padding: 4px 0 18px 0;
    border-bottom: 1.5px solid var(--border-md);
    margin-bottom: 18px;
}
.sidebar-brand span { color: var(--lavender-dk); }

/* ── 3D INFO BOX ── */
.info-box {
    background: rgba(255,255,255,0.72);
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.70);
    border-right: 1.5px solid rgba(160,150,200,0.18);
    border-bottom: 4px solid rgba(180,165,220,0.32);
    border-radius: 14px;
    padding: 16px 20px;
    font-size: 0.88rem;
    color: var(--ink-soft);
    margin-bottom: 14px;
    line-height: 1.80;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 6px 16px rgba(100,80,160,0.07);
}

/* ── PILLS ── */
.pill {
    display: inline-block;
    padding: 3px 13px;
    border-radius: 99px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    border-top: 1px solid rgba(255,255,255,0.80);
    box-shadow: 0 2px 0 rgba(0,0,0,0.10);
}
.pill-expand   { background: #A8DCC5; color: #1A5C40; box-shadow: 0 2px 0 #7AC9A8; }
.pill-maintain { background: #F5D97A; color: #6B4800; box-shadow: 0 2px 0 #D4B040; }
.pill-optimize { background: #F6BBA8; color: #7A2A10; box-shadow: 0 2px 0 #E0907A; }
.pill-drop     { background: #F2B5CF; color: #7A1840; box-shadow: 0 2px 0 #D490B0; }

/* ── RESULT CARD colours ── */
.result-expand  { background:#E2F4ED; border-bottom-color:#7AC9A8 !important; }
.result-maintain{ background:#FEF7DF; border-bottom-color:#D4B040 !important; }
.result-optimize{ background:#FDEAE4; border-bottom-color:#E0907A !important; }
.result-drop    { background:#FCE9F0; border-bottom-color:#D490B0 !important; }
.result-card {
    border-top: 1.5px solid var(--top-shine);
    border-left: 1.5px solid rgba(255,255,255,0.75);
    border-right: 1.5px solid rgba(160,150,200,0.18);
    border-bottom: 5px solid;
    border-radius: 22px;
    padding: 28px 34px;
    margin: 24px 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.80), 0 12px 30px rgba(100,80,160,0.09);
}
</style>
""", unsafe_allow_html=True)

DECISION_COLORS = {
    "Expand":   "#3D9E74",
    "Maintain": "#B07C0A",
    "Optimize": "#D85A30",
    "Drop":     "#B8365C",
}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

def pastel_fig(figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("none"); fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#C9BFEF")
    ax.spines["bottom"].set_color("#C9BFEF")
    ax.tick_params(colors="#4A4663", labelsize=9)
    ax.xaxis.label.set_color("#4A4663"); ax.yaxis.label.set_color("#4A4663")
    ax.title.set_color("#1E1B2E"); ax.title.set_fontsize(12); ax.title.set_fontweight("bold")
    ax.grid(axis="y", color="#EAE6F8", linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)
    return fig, ax

def col_seq(labels):
    return [DECISION_COLORS.get(l, "#C9BFEF") for l in labels]

BASE_DIR     = os.path.dirname(__file__)
DATA_PATH    = os.path.join(BASE_DIR, "airline_route_profitability.csv")
MODEL1_PATH  = os.path.join(BASE_DIR, "model_with_revenue.pkl")
MODEL2_PATH  = os.path.join(BASE_DIR, "model_without_revenue.pkl")
MODEL3_PATH  = os.path.join(BASE_DIR, "model_preoperational.pkl")
X1_COLS_PATH = os.path.join(BASE_DIR, "x1_columns.pkl")
X2_COLS_PATH = os.path.join(BASE_DIR, "x2_columns.pkl")
X3_COLS_PATH = os.path.join(BASE_DIR, "x3_columns.pkl")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Flight_Date"] = pd.to_datetime(df["Flight_Date"])
    for col in ["Ancillary_Revenue", "Catering_Cost", "Handling_Cost"]:
        if col in df.columns: df[col] = df[col].fillna(0)
    ph = df["Profit"].quantile(0.75); mh = df["Profit_Margin"].quantile(0.75)
    lh = df["Load_Factor"].quantile(0.75); mm = df["Profit_Margin"].median(); lm = df["Load_Factor"].median()
    def classify(row):
        if row["Profit"]>=ph and row["Profit_Margin"]>=mh and row["Load_Factor"]>=lh: return "Expand"
        elif row["Profit"]<=0: return "Drop"
        elif row["Profit_Margin"]<mm or row["Load_Factor"]<lm: return "Optimize"
        else: return "Maintain"
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

df = load_data()
model1, model2, model3, X1_columns, X2_columns, X3_columns = load_artifacts()

comparison = pd.DataFrame({
    "Model":    ["With revenue variables", "Without revenue variables", "Only pre-operational features"],
    "Accuracy": [0.879624, 0.837618, 0.721003],
    "Macro F1": [0.879616, 0.838726, 0.729150],
})

df_sorted = df.sort_values(["Route","Flight_Date"]).copy()
df_sorted["Prev_Decision"] = df_sorted.groupby("Route")["Route_Decision"].shift(1)
df_sorted["Changed"] = df_sorted["Route_Decision"] != df_sorted["Prev_Decision"]
route_switches = df_sorted.groupby("Route")["Changed"].sum().sort_values(ascending=False).reset_index().rename(columns={"Changed":"Decision Switches"})
route_variability = df.groupby("Route")["Route_Decision"].nunique().sort_values(ascending=False).reset_index().rename(columns={"Route_Decision":"Unique States"})

if "pred_result" not in st.session_state: st.session_state.pred_result = None

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Sky<span>Lens</span> ✈</div>', unsafe_allow_html=True)
    st.markdown("**Filter the view**")
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
    <small style='color:#7A758F;line-height:2.2'>
    <b>Decision labels</b><br>
    <span class='pill pill-expand'>Expand</span>&nbsp; High profit &amp; demand<br><br>
    <span class='pill pill-maintain'>Maintain</span>&nbsp; Stable performer<br><br>
    <span class='pill pill-optimize'>Optimize</span>&nbsp; Room to improve<br><br>
    <span class='pill pill-drop'>Drop</span>&nbsp; Losing money
    </small>""", unsafe_allow_html=True)

fdf = df.copy()
if sel_route    != "All": fdf = fdf[fdf["Route"]          == sel_route]
if sel_aircraft != "All": fdf = fdf[fdf["Aircraft_Type"]  == sel_aircraft]
if sel_season   != "All": fdf = fdf[fdf["Season"]         == sel_season]
if sel_decision != "All": fdf = fdf[fdf["Route_Decision"] == sel_decision]

st.markdown("""
<div class="hero">
  <h1>Route Intelligence Dashboard</h1>
  <p>
    This dashboard is built on a sample airline dataset for analysis and demonstration purposes only. 
    It does not reflect real-time airline operations or current flight decisions.
  </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Overview","🔍  Performance Drivers","🗺  Route Actions","📈  Route Stability","🤖  Prediction Tool",
])

with tab1:
    n = len(fdf); avg_profit = fdf["Profit"].mean(); avg_load = fdf["Load_Factor"].mean(); n_routes = fdf["Route"].nunique()
    expand_pct   = (fdf["Route_Decision"]=="Expand").mean()*100   if n else 0
    maintain_pct = (fdf["Route_Decision"]=="Maintain").mean()*100 if n else 0
    optimize_pct = (fdf["Route_Decision"]=="Optimize").mean()*100 if n else 0
    drop_pct     = (fdf["Route_Decision"]=="Drop").mean()*100     if n else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Flights",   f"{n:,}")
    c2.metric("Unique Routes",   f"{n_routes}")
    c3.metric("Average Profit",  f"${avg_profit:,.0f}")
    c4.metric("Avg Load Factor", f"{avg_load:.0%}")
    st.markdown("&nbsp;")
    d1,d2,d3,d4 = st.columns(4)
    d1.metric("Expand",   f"{expand_pct:.1f}%")
    d2.metric("Maintain", f"{maintain_pct:.1f}%")
    d3.metric("Optimize", f"{optimize_pct:.1f}%")
    d4.metric("Drop",     f"{drop_pct:.1f}%")
    st.markdown("&nbsp;")
    left, right = st.columns([1,1])
    with left:
        st.markdown("### Decision mix")
        dc = fdf["Route_Decision"].value_counts()
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {"Expand":"#A8DCC5","Maintain":"#F5D97A","Optimize":"#F6BBA8","Drop":"#F2B5CF"}
        fig, ax = pastel_fig((5,5))
        wedges,texts,autotexts = ax.pie(dc.values, labels=dc.index, autopct="%1.1f%%",
            colors=[wc[l] for l in dc.index], startangle=90,
            wedgeprops={"linewidth":3,"edgecolor":"#FAFAF8"},
            textprops={"color":"#1E1B2E","fontsize":10,"fontfamily":"DM Sans"})
        for at in autotexts: at.set_fontsize(9); at.set_color("#1E1B2E"); at.set_fontweight("bold")
        ax.set_title("Share of Flights by Decision", pad=16)
        st.pyplot(fig)
    with right:
        st.markdown("### Average metrics by decision")
        summary = (fdf.groupby("Route_Decision")[["Profit","Profit_Margin","Load_Factor"]].mean()
            .reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).round(3).reset_index()
            .rename(columns={"Route_Decision":"Decision","Profit":"Avg Profit ($)","Profit_Margin":"Avg Margin","Load_Factor":"Avg Load Factor"}))
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""<div class="info-box"><b>How to read this</b><br>
        Each row shows average profitability and seat occupancy for flights in that category.
        <b>Expand</b> routes should have the highest values across all three columns.</div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("### What separates strong routes from weak ones?")
    st.markdown("<p style='color:#7A758F'>These charts reveal the metrics most associated with route profitability.</p>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        apd = fdf.groupby("Route_Decision")["Profit"].mean().reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna()
        fig, ax = pastel_fig((6,4))
        bars = ax.bar(apd.index, apd.values, color=col_seq(apd.index.tolist()), width=0.55, edgecolor="#FAFAF8", linewidth=2.5)
        for b in bars:
            h=b.get_height(); ax.text(b.get_x()+b.get_width()/2, h+abs(apd.values).max()*0.02, f"${h:,.0f}", ha="center", va="bottom", fontsize=8, color="#4A4663", fontweight="700")
        ax.set_ylabel("Average Profit ($)"); ax.set_title("Average Profit by Decision")
        st.pyplot(fig)
    with right:
        ald = fdf.groupby("Route_Decision")["Load_Factor"].mean().reindex([x for x in ORDER if x in fdf["Route_Decision"].unique()]).dropna()
        fig, ax = pastel_fig((6,4))
        bars = ax.bar(ald.index, ald.values, color=col_seq(ald.index.tolist()), width=0.55, edgecolor="#FAFAF8", linewidth=2.5)
        for b in bars:
            h=b.get_height(); ax.text(b.get_x()+b.get_width()/2, h+0.005, f"{h:.0%}", ha="center", va="bottom", fontsize=8, color="#4A4663", fontweight="700")
        ax.set_ylabel("Average Seat Occupancy"); ax.set_title("Seat Occupancy by Decision")
        st.pyplot(fig)
    st.markdown("---")
    st.markdown("### Where is the money going?")
    st.markdown("<p style='color:#7A758F'>The biggest cost components across all filtered flights.</p>", unsafe_allow_html=True)
    cost_cols = ["Fuel_Cost","Maintenance_Cost","Crew_Cost","Depreciation_Cost","Insurance_Cost","Airport_Fees","Catering_Cost","Handling_Cost","Navigation_Fees","Sales_Distribution_Cost","Passenger_Service_Cost","Overhead_Cost","Marketing_Cost","IT_Systems_Cost"]
    avail_costs = [c for c in cost_cols if c in fdf.columns]
    cost_means = fdf[avail_costs].mean().sort_values(ascending=True).tail(8)
    label_map = {"Fuel_Cost":"Fuel","Maintenance_Cost":"Maintenance","Crew_Cost":"Crew","Depreciation_Cost":"Depreciation","Insurance_Cost":"Insurance","Airport_Fees":"Airport Fees","Catering_Cost":"Catering","Handling_Cost":"Handling","Navigation_Fees":"Navigation","Sales_Distribution_Cost":"Sales & Distribution","Passenger_Service_Cost":"Passenger Service","Overhead_Cost":"Overhead","Marketing_Cost":"Marketing","IT_Systems_Cost":"IT Systems"}
    cost_means.index = [label_map.get(i,i) for i in cost_means.index]
    pastel8 = ["#C9BFEF","#A8D0EF","#A8DCC5","#F5D97A","#F6BBA8","#F2B5CF","#EAE6F8","#E2F4ED"]
    fig, ax = pastel_fig((9,4))
    bars = ax.barh(cost_means.index, cost_means.values, color=pastel8[:len(cost_means)], edgecolor="#FAFAF8", linewidth=2.5, height=0.6)
    mx = cost_means.max()
    for b in bars:
        w=b.get_width(); ax.text(w+mx*0.01, b.get_y()+b.get_height()/2, f"${w:,.0f}", va="center", fontsize=8, color="#4A4663", fontweight="700")
    ax.set_xlabel("Average Cost per Flight ($)"); ax.set_title("Top Cost Drivers")
    st.pyplot(fig)

with tab3:
    st.markdown("### Which routes need attention?")
    st.markdown("<p style='color:#7A758F'>A quick view of your best and worst performing routes.</p>", unsafe_allow_html=True)
    st.markdown("#### Top routes currently classified as Expand")
    expand_routes = (fdf[fdf["Route_Decision"]=="Expand"].sort_values("Profit",ascending=False)[["Route","Profit","Profit_Margin","Load_Factor"]].head(10).rename(columns={"Profit":"Avg Profit ($)","Profit_Margin":"Profit Margin","Load_Factor":"Load Factor"}))
    st.dataframe(expand_routes, use_container_width=True, hide_index=True)
    st.markdown("&nbsp;")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Top 10 routes by total profit")
        top = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).tail(10)
        fig, ax = pastel_fig((7,5))
        ax.barh(top.index, top.values, color="#A8DCC5", edgecolor="#FAFAF8", linewidth=2.5, height=0.6)
        ax.set_xlabel("Total Profit ($)"); ax.set_title("Top 10 Routes")
        st.pyplot(fig)
    with right:
        st.markdown("#### Bottom 10 routes by total profit")
        worst = fdf.groupby("Route")["Profit"].sum().sort_values(ascending=True).head(10)
        fig, ax = pastel_fig((7,5))
        ax.barh(worst.index, worst.values, color="#F2B5CF", edgecolor="#FAFAF8", linewidth=2.5, height=0.6)
        ax.set_xlabel("Total Profit ($)"); ax.set_title("Bottom 10 Routes")
        st.pyplot(fig)

with tab4:
    st.markdown("### How consistent are route decisions over time?")
    st.markdown("<p style='color:#7A758F'>A route that frequently flips between categories may need structural attention.</p>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Routes with most decision changes")
        st.dataframe(route_switches.head(10), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Routes seen in the most decision states")
        st.dataframe(route_variability.head(10), use_container_width=True, hide_index=True)
    st.markdown("---")
    urbd = df.groupby("Route_Decision")["Route"].nunique().reset_index().rename(columns={"Route":"Unique Routes"}).set_index("Route_Decision").reindex(ORDER).dropna()
    st.markdown("#### How many unique routes appear in each category?")
    bc_map = {"Expand":"#A8DCC5","Maintain":"#F5D97A","Optimize":"#F6BBA8","Drop":"#F2B5CF"}
    bc = [bc_map.get(i,"#C9BFEF") for i in urbd.index]
    fig, ax = pastel_fig((8,4))
    bars = ax.bar(urbd.index, urbd["Unique Routes"], color=bc, width=0.55, edgecolor="#FAFAF8", linewidth=2.5)
    for b in bars:
        h=b.get_height(); ax.text(b.get_x()+b.get_width()/2, h+0.25, f"{int(h)}", ha="center", fontsize=9, color="#4A4663", fontweight="700")
    ax.set_ylabel("Number of Unique Routes"); ax.set_title("Unique Routes per Decision Category")
    st.pyplot(fig)
    patches = [mpatches.Patch(color=bc_map.get(d,"#C9BFEF"), label=d) for d in ORDER]
    fig2, ax2 = plt.subplots(figsize=(5,0.5)); fig2.patch.set_alpha(0); ax2.axis("off")
    ax2.legend(handles=patches, loc="center", frameon=False, ncol=4, prop={"size":9}, labelcolor="#1E1B2E")
    st.pyplot(fig2)

with tab5:
    st.markdown("### Simulate a route scenario")
    st.markdown("<p style='color:#7A758F'>Enter route characteristics and our model will suggest the best decision.</p>", unsafe_allow_html=True)
    st.markdown("#### How accurate are the models?")
    fig, ax = pastel_fig((8,3.5))
    x = np.arange(len(comparison)); w = 0.32
    b1 = ax.bar(x-w/2, comparison["Accuracy"], w, label="Accuracy", color="#C9BFEF", edgecolor="#FAFAF8", linewidth=2.5)
    b2 = ax.bar(x+w/2, comparison["Macro F1"], w, label="Macro F1", color="#A8DCC5", edgecolor="#FAFAF8", linewidth=2.5)
    for b in list(b1)+list(b2):
        h=b.get_height(); ax.text(b.get_x()+b.get_width()/2, h+0.005, f"{h:.0%}", ha="center", fontsize=7.5, color="#4A4663", fontweight="700")
    ax.set_xticks(x); ax.set_xticklabels(comparison["Model"], fontsize=8.5)
    ax.set_ylim(0,1.12); ax.set_ylabel("Score"); ax.set_title("Model Accuracy & F1 Comparison")
    ax.legend(frameon=False, fontsize=9); plt.xticks(rotation=10)
    st.pyplot(fig)
    st.markdown("---")
    st.markdown("#### Choose a prediction mode")
    st.markdown("""<div class="info-box">
    <span class='pill pill-maintain'>With Revenue</span>&nbsp; Most accurate — use when you have ticket &amp; ancillary revenue data.<br><br>
    <span class='pill pill-optimize'>Cost-only</span>&nbsp; Good accuracy using cost data only, no revenue figures needed.<br><br>
    <span class='pill pill-expand'>Pre-launch</span>&nbsp; Use before a route launches, when only capacity/demand signals are known.
    </div>""", unsafe_allow_html=True)
    model_choice = st.selectbox("Prediction mode", ["With Revenue Variables","Without Revenue Variables","Only Pre-Operational Features"], key="model_choice_select")

    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**✈ Flight basics**")
            aircraft_type     = st.selectbox("Aircraft Type",    sorted(df["Aircraft_Type"].dropna().unique()))
            aircraft_capacity = st.number_input("Aircraft Capacity", min_value=50,  max_value=600, value=250)
            passengers        = st.number_input("Passengers",        min_value=0,   max_value=600, value=200)
            load_factor       = st.slider("Load Factor (seat occupancy)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
        with col2:
            st.markdown("**🌍 Route context**")
            flight_hours   = st.number_input("Flight Hours",   min_value=0.5, max_value=20.0, value=6.0, step=0.1)
            season_val     = st.selectbox("Season",            sorted(df["Season"].dropna().unique()))
            route_category = st.selectbox("Route Category",    sorted(df["Route_Category"].dropna().unique()))
            demand_level   = st.selectbox("Demand Level",      sorted(df["Demand_Level"].dropna().unique()))
        if model_choice == "With Revenue Variables":
            with col3:
                st.markdown("**💰 Revenue**")
                ticket_revenue    = st.number_input("Ticket Revenue ($)",    min_value=0.0, value=120000.0, step=1000.0)
                ancillary_revenue = st.number_input("Ancillary Revenue ($)", min_value=0.0, value=10000.0,  step=500.0)
        elif model_choice == "Without Revenue Variables":
            with col3:
                st.markdown("**💸 Cost breakdown**")
                fuel_cost               = st.number_input("Fuel Cost ($)",                 min_value=0.0, value=40000.0,  step=1000.0)
                maintenance_cost        = st.number_input("Maintenance Cost ($)",          min_value=0.0, value=15000.0,  step=500.0)
                crew_cost               = st.number_input("Crew Cost ($)",                 min_value=0.0, value=8000.0,   step=500.0)
                depreciation_cost       = st.number_input("Depreciation Cost ($)",         min_value=0.0, value=20000.0,  step=500.0)
                insurance_cost          = st.number_input("Insurance Cost ($)",            min_value=0.0, value=4000.0,   step=250.0)
                airport_fees            = st.number_input("Airport Fees ($)",              min_value=0.0, value=5000.0,   step=250.0)
                catering_cost           = st.number_input("Catering Cost ($)",             min_value=0.0, value=5000.0,   step=250.0)
                handling_cost           = st.number_input("Handling Cost ($)",             min_value=0.0, value=4000.0,   step=250.0)
                navigation_fees         = st.number_input("Navigation Fees ($)",           min_value=0.0, value=3500.0,   step=250.0)
                sales_distribution_cost = st.number_input("Sales & Distribution Cost ($)", min_value=0.0, value=35000.0, step=500.0)
                passenger_service_cost  = st.number_input("Passenger Service Cost ($)",    min_value=0.0, value=5000.0,   step=250.0)
                overhead_cost           = st.number_input("Overhead Cost ($)",             min_value=0.0, value=25000.0,  step=500.0)
                marketing_cost          = st.number_input("Marketing Cost ($)",            min_value=0.0, value=12000.0,  step=500.0)
                it_systems_cost         = st.number_input("IT Systems Cost ($)",           min_value=0.0, value=3000.0,   step=250.0)
        submitted = st.form_submit_button("✈  Get Route Decision")

    if submitted:
        if model_choice == "With Revenue Variables":
            row = {"Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,"Passengers":passengers,"Load_Factor":load_factor,"Flight_Hours":flight_hours,"Season":season_val,"Route_Category":route_category,"Demand_Level":demand_level,"Ticket_Revenue":ticket_revenue,"Ancillary_Revenue":ancillary_revenue}
            inp=prepare_input(pd.DataFrame([row]),X1_columns); pred=model1.predict(inp)[0]; prob=model1.predict_proba(inp)[0]; cls=model1.classes_
        elif model_choice == "Without Revenue Variables":
            row = {"Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,"Passengers":passengers,"Load_Factor":load_factor,"Flight_Hours":flight_hours,"Season":season_val,"Route_Category":route_category,"Demand_Level":demand_level,"Fuel_Cost":fuel_cost,"Maintenance_Cost":maintenance_cost,"Crew_Cost":crew_cost,"Depreciation_Cost":depreciation_cost,"Insurance_Cost":insurance_cost,"Airport_Fees":airport_fees,"Catering_Cost":catering_cost,"Handling_Cost":handling_cost,"Navigation_Fees":navigation_fees,"Sales_Distribution_Cost":sales_distribution_cost,"Passenger_Service_Cost":passenger_service_cost,"Overhead_Cost":overhead_cost,"Marketing_Cost":marketing_cost,"IT_Systems_Cost":it_systems_cost}
            inp=prepare_input(pd.DataFrame([row]),X2_columns); pred=model2.predict(inp)[0]; prob=model2.predict_proba(inp)[0]; cls=model2.classes_
        else:
            row = {"Aircraft_Type":aircraft_type,"Aircraft_Capacity":aircraft_capacity,"Passengers":passengers,"Load_Factor":load_factor,"Flight_Hours":flight_hours,"Season":season_val,"Route_Category":route_category,"Demand_Level":demand_level}
            inp=prepare_input(pd.DataFrame([row]),X3_columns); pred=model3.predict(inp)[0]; prob=model3.predict_proba(inp)[0]; cls=model3.classes_
        st.session_state.pred_result = {"prediction":pred,"probabilities":prob,"classes":cls}

    if st.session_state.pred_result is not None:
        res=st.session_state.pred_result; pred=res["prediction"]; prob=res["probabilities"]; cls=res["classes"]
        pill_cls = {"Expand":"pill-expand","Maintain":"pill-maintain","Optimize":"pill-optimize","Drop":"pill-drop"}
        result_cls = {"Expand":"result-expand","Maintain":"result-maintain","Optimize":"result-optimize","Drop":"result-drop"}
        text_col = {"Expand":"#1A5C40","Maintain":"#6B4800","Optimize":"#7A2A10","Drop":"#7A1840"}
        explanations = {
            "Expand":   "This route shows strong performance signals — high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed — keep monitoring.",
            "Optimize": "This route has potential but something is holding it back — efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }
        st.markdown(f"""
        <div class='result-card {result_cls.get(pred,"result-expand")}'>
          <div style='margin-bottom:10px'><span class='pill {pill_cls.get(pred,"")}' style='font-size:0.8rem;padding:4px 16px'>{pred}</span></div>
          <div style='font-family:"DM Serif Display",serif;font-size:1.85rem;color:{text_col.get(pred,"#1E1B2E")};margin-bottom:10px'>Suggested Decision: <b>{pred}</b></div>
          <p style='color:#4A4663;margin:0;font-size:0.95rem;line-height:1.75'>{explanations.get(pred,"")}</p>
        </div>""", unsafe_allow_html=True)

        prob_df = pd.DataFrame({"Decision":cls,"Probability":prob}).sort_values("Probability",ascending=False)
        st.markdown("#### Confidence by decision option")
        bar_cp = {"Expand":"#A8DCC5","Maintain":"#F5D97A","Optimize":"#F6BBA8","Drop":"#F2B5CF"}
        fig, ax = pastel_fig((6,3.5))
        bars = ax.bar(prob_df["Decision"], prob_df["Probability"], color=[bar_cp.get(d,"#C9BFEF") for d in prob_df["Decision"]], width=0.5, edgecolor="#FAFAF8", linewidth=2.5)
        for b in bars:
            h=b.get_height(); ax.text(b.get_x()+b.get_width()/2, h+0.012, f"{h:.0%}", ha="center", fontsize=9, color="#4A4663", fontweight="700")
        ax.set_ylim(0,1.18); ax.set_ylabel("Probability"); ax.set_title("Model Confidence per Decision")
        st.pyplot(fig)
        st.dataframe(prob_df.assign(Probability=prob_df["Probability"].map("{:.1%}".format)).reset_index(drop=True), use_container_width=True, hide_index=True)

with st.expander("🗂  Show filtered data"):
    st.dataframe(fdf, use_container_width=True)

st.markdown("""
<div style='text-align:center;color:#7A758F;font-size:0.78rem;padding:36px 0 16px;font-family:"DM Sans",sans-serif'>
  SkyLens Route Intelligence &nbsp;·&nbsp; Built with Streamlit
</div>""", unsafe_allow_html=True)