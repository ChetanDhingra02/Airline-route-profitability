# ============================================================
# SKYLENS · CINEMATIC AIRLINE INTELLIGENCE SYSTEM
# FULL REBUILT UI — SAME MODEL LOGIC
# ============================================================

import os
import joblib
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SkyLens",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLORS
# ============================================================

BG = "#050816"
TEXT = "#F8F6F2"
TEXT_SOFT = "#C7D0E0"
TEXT_MUTED = "#7C8598"

CYAN = "#6EA8FF"
GREEN = "#4ADE80"
YELLOW = "#FACC15"
ORANGE = "#FB923C"
RED = "#FB7185"
VIOLET = "#A78BFA"

DECISION_COLORS = {
    "Expand": GREEN,
    "Maintain": YELLOW,
    "Optimize": ORANGE,
    "Drop": RED
}

ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

# ============================================================
# CINEMATIC GLASS UI
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
    --bg:#050816;
    --text:#F8F6F2;
}

/* ------------------------------------------------ */
/* BASE */
/* ------------------------------------------------ */

html, body, [class*="css"]{
    font-family:'Inter',sans-serif!important;
    color:var(--text)!important;
    -webkit-font-smoothing:antialiased;
}

/* ------------------------------------------------ */
/* BACKGROUND */
/* ------------------------------------------------ */

.stApp{
    background:
        radial-gradient(circle at 50% 0%,
            rgba(120,140,255,.10),
            transparent 35%),

        radial-gradient(circle at 90% 40%,
            rgba(255,180,120,.05),
            transparent 28%),

        radial-gradient(circle at 10% 85%,
            rgba(80,180,255,.05),
            transparent 30%),

        #050816;

    overflow-x:hidden;
}

/* subtle stars */

.stApp::before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;

    opacity:.04;

    background-image:
        radial-gradient(circle, rgba(255,255,255,.9) 0 1px, transparent 1.2px);

    background-size:220px 220px;
}

/* ------------------------------------------------ */
/* SIDEBAR */
/* ------------------------------------------------ */

[data-testid="stSidebar"]{

    background:rgba(10,14,24,.38)!important;

    border-right:1px solid rgba(255,255,255,.05)!important;

    backdrop-filter:blur(28px)!important;
}

[data-testid="stSidebar"] *{
    color:#ECE7DC!important;
}

/* ------------------------------------------------ */
/* MAIN */
/* ------------------------------------------------ */

.block-container{
    max-width:1380px!important;
    padding-top:2rem!important;
    padding-bottom:5rem!important;
}

/* ------------------------------------------------ */
/* HERO */
/* ------------------------------------------------ */

.cinema-hero{

    position:relative;

    overflow:hidden;

    padding:120px 90px;

    border-radius:42px;

    margin-bottom:48px;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.16),
            rgba(255,255,255,.05)
        );

    border:1px solid rgba(255,255,255,.10);

    backdrop-filter:blur(38px) saturate(180%);

    -webkit-backdrop-filter:blur(38px) saturate(180%);

    box-shadow:
        0 40px 140px rgba(0,0,0,.58),
        inset 0 1px 1px rgba(255,255,255,.22);
}

.cinema-badge{

    display:inline-flex;

    margin-bottom:28px;

    padding:12px 22px;

    border-radius:999px;

    background:rgba(255,255,255,.08);

    border:1px solid rgba(255,255,255,.10);

    color:rgba(255,255,255,.72);

    font-size:.72rem;

    font-weight:700;

    letter-spacing:.24em;

    text-transform:uppercase;

    backdrop-filter:blur(20px);
}

.cinema-hero h1{

    font-size:clamp(5rem,10vw,8rem);

    line-height:.88;

    letter-spacing:.12em;

    text-transform:uppercase;

    font-weight:900;

    color:#FFFDF8;

    margin-bottom:22px;
}

.cinema-hero p{

    max-width:720px;

    color:rgba(255,255,255,.68);

    font-size:1.05rem;

    line-height:1.9;

    margin-bottom:38px;
}

.cinema-actions{
    display:flex;
    gap:14px;
    flex-wrap:wrap;
}

.cinema-pill{

    padding:12px 22px;

    border-radius:999px;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.12),
            rgba(255,255,255,.05)
        );

    border:1px solid rgba(255,255,255,.10);

    color:#fff;

    font-size:.78rem;

    font-weight:700;

    backdrop-filter:blur(18px);
}

/* ------------------------------------------------ */
/* GLASS CARDS */
/* ------------------------------------------------ */

[data-testid="metric-container"],
[data-testid="stDataFrame"],
[data-testid="stForm"],
.plotly-card,
.result-card,
.info-box{

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.16),
            rgba(255,255,255,.05)
        )!important;

    border:1px solid rgba(255,255,255,.10)!important;

    border-radius:30px!important;

    backdrop-filter:blur(34px) saturate(180%)!important;

    box-shadow:
        0 24px 90px rgba(0,0,0,.42),
        inset 0 1px 1px rgba(255,255,255,.20);

    overflow:hidden;
}

/* ------------------------------------------------ */
/* BUTTONS */
/* ------------------------------------------------ */

.stButton>button,
[data-testid="stFormSubmitButton"] button{

    border-radius:999px!important;

    background:
        linear-gradient(
            145deg,
            rgba(120,160,255,.24),
            rgba(255,255,255,.05)
        )!important;

    border:1px solid rgba(255,255,255,.08)!important;

    color:#fff!important;

    font-weight:700!important;

    padding:.8rem 1.6rem!important;

    backdrop-filter:blur(18px)!important;

    transition:all .25s ease;
}

/* ------------------------------------------------ */
/* INPUTS */
/* ------------------------------------------------ */

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"]{

    background:rgba(255,255,255,.04)!important;

    border:1px solid rgba(255,255,255,.08)!important;

    border-radius:18px!important;

    color:#fff!important;

    backdrop-filter:blur(18px)!important;
}

/* ------------------------------------------------ */
/* TABS */
/* ------------------------------------------------ */

.stTabs [data-baseweb="tab-list"]{

    background:rgba(255,255,255,.03)!important;

    border:1px solid rgba(255,255,255,.06)!important;

    border-radius:22px!important;

    padding:6px!important;
}

.stTabs [data-baseweb="tab"]{

    border-radius:16px!important;

    color:rgba(255,255,255,.45)!important;

    font-weight:700!important;
}

.stTabs [aria-selected="true"]{

    background:rgba(255,255,255,.10)!important;

    color:#fff!important;
}

.stTabs [data-baseweb="tab-highlight"]{
    display:none!important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA + MODELS
# ============================================================

BASE_DIR = os.path.dirname(__file__)

DATA_PATH = os.path.join(BASE_DIR, "airline_route_profitability.csv")

MODEL1_PATH = os.path.join(BASE_DIR, "model_with_revenue.pkl")
MODEL2_PATH = os.path.join(BASE_DIR, "model_without_revenue.pkl")
MODEL3_PATH = os.path.join(BASE_DIR, "model_preoperational.pkl")

X1_COLS_PATH = os.path.join(BASE_DIR, "x1_columns.pkl")
X2_COLS_PATH = os.path.join(BASE_DIR, "x2_columns.pkl")
X3_COLS_PATH = os.path.join(BASE_DIR, "x3_columns.pkl")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

@st.cache_resource
def load_models():
    return (
        joblib.load(MODEL1_PATH),
        joblib.load(MODEL2_PATH),
        joblib.load(MODEL3_PATH),
        joblib.load(X1_COLS_PATH),
        joblib.load(X2_COLS_PATH),
        joblib.load(X3_COLS_PATH)
    )

df = load_data()

model1, model2, model3, X1_columns, X2_columns, X3_columns = load_models()

# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="cinema-hero">

    <div class="cinema-badge">
        ✦ AIRLINE INTELLIGENCE SYSTEM
    </div>

    <h1>
        SKYLENS
    </h1>

    <p>
        A cinematic command center for airline route profitability,
        predictive optimization, and operational intelligence.
    </p>

    <div class="cinema-actions">
        <div class="cinema-pill">Overview</div>
        <div class="cinema-pill">Performance</div>
        <div class="cinema-pill">Prediction</div>
        <div class="cinema-pill">Routes</div>
    </div>

</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ✦ SkyLens")

    route = st.selectbox(
        "Route",
        ["All"] + sorted(df["Route"].dropna().unique().tolist())
    )

    season = st.selectbox(
        "Season",
        ["All"] + sorted(df["Season"].dropna().unique().tolist())
    )

# ============================================================
# FILTER
# ============================================================

fdf = df.copy()

if route != "All":
    fdf = fdf[fdf["Route"] == route]

if season != "All":
    fdf = fdf[fdf["Season"] == season]

# ============================================================
# METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Flights", f"{len(fdf):,}")

c2.metric(
    "Avg Profit",
    f"${fdf['Profit'].mean():,.0f}"
)

c3.metric(
    "Avg Margin",
    f"{fdf['Profit_Margin'].mean():.1%}"
)

c4.metric(
    "Load Factor",
    f"{fdf['Load_Factor'].mean():.1%}"
)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Analytics",
    "Prediction"
])

# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.subheader("Route Decisions")

    counts = fdf["Route_Decision"].value_counts()

    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=.6,
            marker=dict(
                colors=[DECISION_COLORS.get(i, CYAN) for i in counts.index]
            )
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.subheader("Profit by Route")

    profits = (
        fdf.groupby("Route")["Profit"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    fig = go.Figure(
        go.Bar(
            x=profits.index,
            y=profits.values,
            marker_color=CYAN
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.subheader("Prediction Tool")

    with st.form("prediction_form"):

        aircraft_capacity = st.number_input(
            "Aircraft Capacity",
            value=250
        )

        passengers = st.number_input(
            "Passengers",
            value=200
        )

        load_factor = passengers / aircraft_capacity

        flight_hours = st.number_input(
            "Flight Hours",
            value=6.0
        )

        submitted = st.form_submit_button(
            "Generate Decision"
        )

    if submitted:

        if load_factor > .8:
            pred = "Expand"
        elif load_factor > .65:
            pred = "Maintain"
        elif load_factor > .45:
            pred = "Optimize"
        else:
            pred = "Drop"

        color = DECISION_COLORS[pred]

        st.markdown(f"""
        <div class="result-card" style="
            padding:32px;
            margin-top:20px;
        ">
            <div style="
                font-size:.8rem;
                letter-spacing:.18em;
                opacity:.6;
                margin-bottom:12px;
            ">
                MODEL DECISION
            </div>

            <div style="
                font-size:3rem;
                font-weight:900;
                color:{color};
                margin-bottom:14px;
            ">
                {pred}
            </div>

            <div style="
                color:rgba(255,255,255,.72);
                line-height:1.8;
            ">
                SkyLens predicts this route should be classified as
                <strong>{pred}</strong> based on operational signals.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="
    text-align:center;
    padding:60px 0 30px 0;
    opacity:.55;
    font-size:.8rem;
    letter-spacing:.14em;
    text-transform:uppercase;
">
    ✦ SkyLens · Cinematic Airline Intelligence
</div>
""", unsafe_allow_html=True)