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
#  PROFESSIONAL AVIATION COMMAND CENTER THEME
# ─────────────────────────────────────────────────────────────
BG = "#080B12"
PANEL = "#121722"
PANEL_2 = "#171E2B"
TEXT = "#FFF7E6"
TEXT_SOFT = "#E8DDCB"
TEXT_MUTED = "#B9AFA5"
CYAN = "#8FD9EF"
BLUE = "#6AA8FF"
AMBER = "#F1C879"
GREEN = "#7DDB9A"
RED = "#F29AA7"
VIOLET = "#C8A8FF"

CHART_EXPAND   = "#7DDB9A"
CHART_MAINTAIN = "#F1C879"
CHART_OPTIMIZE = "#E9A28D"
CHART_DROP     = "#F29AA7"
CHART_NEUTRAL  = ["#8FD9EF", "#C8A8FF", "#F1C879", "#7DDB9A", "#F29AA7", "#6AA8FF", "#8BE3D1", "#EFA7D4"]
DECISION_COLORS = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN, "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

ACCENT = CYAN
ACCENT_2 = VIOLET
INK = TEXT
INK_SOFT = TEXT_SOFT
INK_MUTED = TEXT_MUTED

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cinzel:wght@400;600;700;900&family=DM+Sans:wght@400;500;600;700&display=swap');

:root{
    --bg:#070914;
    --cream:#FFF5CF;
    --text:#FFF7E6;
    --soft:#E8DDCB;
    --muted:#B9AFA5;
    --cyan:#8FD9EF;
    --gold:#F1C879;
    --rose:#E9A28D;
    --violet:#C8A8FF;
    --glass:rgba(255,255,255,.115);
    --glass-strong:rgba(255,255,255,.16);
    --border:rgba(255,255,255,.24);
    --shadow:0 24px 70px rgba(0,0,0,.46), inset 0 1px 24px rgba(255,255,255,.10);
}

html, body, [class*="css"]{
    font-family:'Inter',sans-serif!important;
    color:var(--text)!important;
    -webkit-font-smoothing:antialiased;
}

.stApp{
    background:
        radial-gradient(circle at 52% 28%, rgba(241,200,121,.34), transparent 11%),
        radial-gradient(circle at 46% 37%, rgba(80,190,205,.26), transparent 19%),
        radial-gradient(circle at 63% 45%, rgba(194,78,151,.19), transparent 22%),
        radial-gradient(circle at 20% 52%, rgba(89,70,180,.25), transparent 28%),
        radial-gradient(circle at 80% 28%, rgba(48,120,190,.20), transparent 22%),
        linear-gradient(120deg,#070914 0%,#111026 46%,#080813 100%)!important;
    background-attachment:fixed!important;
    overflow-x:hidden;
}

.stApp::before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:0;
    background:
        radial-gradient(ellipse at center, transparent 0 30%, rgba(6,7,18,.20) 58%, rgba(3,4,12,.78) 100%),
        radial-gradient(circle at 12% 24%, rgba(255,248,210,.82) 0 1px, transparent 2px),
        radial-gradient(circle at 88% 15%, rgba(255,248,210,.66) 0 1px, transparent 2px),
        radial-gradient(circle at 73% 76%, rgba(255,248,210,.56) 0 1px, transparent 2px),
        radial-gradient(circle at 32% 17%, rgba(207,238,255,.58) 0 1px, transparent 2px),
        radial-gradient(circle at 51% 62%, rgba(255,216,251,.46) 0 1px, transparent 2px),
        repeating-radial-gradient(circle at 50% 42%, rgba(255,255,255,.13) 0 1px, transparent 1px 8px);
    opacity:.78;
}

.stApp::after{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:0;
    background:
        linear-gradient(105deg, transparent 15%, rgba(119,72,187,.16), transparent 45%),
        linear-gradient(75deg, transparent 40%, rgba(235,168,74,.14), transparent 64%);
    opacity:.75;
}

.stApp > *{position:relative;z-index:1;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"]{display:none!important;}

.block-container{
    padding-top:2rem!important;
    max-width:1280px!important;
}

[data-testid="stSidebar"]{
    background:rgba(8,10,24,.70)!important;
    border-right:1px solid rgba(255,255,255,.14)!important;
    backdrop-filter:blur(18px) saturate(120%)!important;
    -webkit-backdrop-filter:blur(18px) saturate(120%)!important;
}

[data-testid="stSidebar"] *{color:#F3E9D8!important;}

h1,h2,h3{
    color:var(--cream)!important;
    font-weight:900!important;
    letter-spacing:-.045em!important;
    text-shadow:0 4px 18px rgba(0,0,0,.88),0 0 22px rgba(255,231,178,.22)!important;
}

p,label,span,div{color:var(--text);}
.stMarkdown,.stText,.stCaption{color:var(--text)!important;}

[data-testid="metric-container"],
[data-testid="stDataFrame"],
[data-testid="stForm"],
.plotly-card,
.result-card,
.info-box{
    background:
        linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,.075)),
        radial-gradient(circle at 35% 70%,rgba(91,188,246,.15),transparent 32%),
        radial-gradient(circle at 78% 18%,rgba(244,137,92,.13),transparent 36%),
        rgba(18,20,36,.42)!important;
    border:1px solid var(--border)!important;
    border-top:1px solid rgba(255,255,255,.36)!important;
    border-left:1px solid rgba(255,255,255,.30)!important;
    border-radius:22px!important;
    backdrop-filter:blur(16px) saturate(110%)!important;
    -webkit-backdrop-filter:blur(16px) saturate(110%)!important;
    box-shadow:var(--shadow)!important;
}

[data-testid="metric-container"]{padding:22px!important;}
[data-testid="stMetricLabel"]{
    color:rgba(255,247,230,.72)!important;
    text-transform:uppercase!important;
    letter-spacing:.14em!important;
    font-weight:800!important;
}
[data-testid="stMetricValue"]{
    color:#FFF5CF!important;
    font-weight:900!important;
    text-shadow:0 3px 16px rgba(0,0,0,.8)!important;
}

.stButton>button,
[data-testid="stFormSubmitButton"] button{
    border-radius:999px!important;
    border:1px solid rgba(255,255,255,.58)!important;
    background:linear-gradient(90deg,rgba(71,142,211,.72),rgba(236,168,76,.56))!important;
    color:#FFFEFA!important;
    font-weight:800!important;
    backdrop-filter:blur(18px)!important;
    transition:all .22s ease!important;
    box-shadow:0 0 22px rgba(113,178,255,.48), inset 0 0 12px rgba(255,255,255,.25)!important;
    text-shadow:0 2px 10px rgba(0,0,0,.8)!important;
}
.stButton>button:hover,
[data-testid="stFormSubmitButton"] button:hover{
    transform:translateY(-2px);
    box-shadow:0 0 30px rgba(244,194,121,.58), inset 0 0 14px rgba(255,255,255,.34)!important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"]{
    background:rgba(255,255,255,.105)!important;
    border:1px solid rgba(255,255,255,.26)!important;
    border-radius:16px!important;
    color:#FFF8E8!important;
    backdrop-filter:blur(14px)!important;
}

.stTabs [data-baseweb="tab-list"]{
    background:rgba(255,255,255,.06)!important;
    border:1px solid rgba(255,255,255,.18)!important;
    border-radius:20px!important;
    padding:6px!important;
    backdrop-filter:blur(12px)!important;
}
.stTabs [data-baseweb="tab"]{
    color:rgba(232,221,203,.70)!important;
    border-radius:14px!important;
    font-weight:800!important;
}
.stTabs [aria-selected="true"]{
    background:rgba(255,255,255,.14)!important;
    color:#FFF5CF!important;
}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}

.plotly-card{padding:18px!important;}
.plotly-card-title{
    color:#FFF5CF!important;
    font-weight:900!important;
    margin-bottom:12px!important;
    text-shadow:0 3px 14px rgba(0,0,0,.8)!important;
}

.sidebar-brand{
    font-family:'Cinzel',serif;
    font-size:1.05rem;
    font-weight:900;
    letter-spacing:.12em;
    color:#FFF5CF;
    text-transform:uppercase;
    margin-bottom:18px;
    display:block;
    text-shadow:0 3px 16px rgba(0,0,0,.85);
}
.sidebar-brand span{color:#8FD9EF;}

.pill{
    display:inline-block;
    padding:3px 12px;
    border-radius:999px;
    font-size:.70rem;
    font-weight:800;
    letter-spacing:.07em;
    font-family:'DM Sans',sans-serif;
}
.pill-expand{background:rgba(125,219,154,.18);color:#9CF0B7;border:1px solid rgba(125,219,154,.35);}
.pill-maintain{background:rgba(241,200,121,.18);color:#FFE19A;border:1px solid rgba(241,200,121,.35);}
.pill-optimize{background:rgba(233,162,141,.18);color:#FFC0AE;border:1px solid rgba(233,162,141,.35);}
.pill-drop{background:rgba(242,154,167,.18);color:#FFB4C0;border:1px solid rgba(242,154,167,.35);}

.section-hd{
    font-family:'DM Sans',sans-serif;
    font-size:.78rem;
    font-weight:800;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:rgba(255,245,207,.72)!important;
    margin-bottom:14px;
}
.section-sub{
    color:rgba(232,221,203,.78)!important;
    font-family:'DM Sans',sans-serif;
    line-height:1.6;
}
.divider-label{
    font-family:'DM Sans',sans-serif;
    font-size:.68rem;
    font-weight:800;
    letter-spacing:.22em;
    text-transform:uppercase;
    color:rgba(255,245,207,.52)!important;
    text-align:center;
    margin:24px 0 18px 0;
    position:relative;
}
.divider-label::before,.divider-label::after{
    content:"";
    position:absolute;
    top:50%;
    width:38%;
    height:1px;
    background:rgba(255,255,255,.16);
}
.divider-label::before{left:0;}
.divider-label::after{right:0;}
.col-label{
    font-family:'DM Sans',sans-serif;
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:#8FD9EF!important;
    margin-bottom:10px;
}

.result-card{padding:28px!important;margin-bottom:20px;}
.result-expand{border-left:4px solid #7DDB9A!important;}
.result-maintain{border-left:4px solid #F1C879!important;}
.result-optimize{border-left:4px solid #E9A28D!important;}
.result-drop{border-left:4px solid #F29AA7!important;}

.info-box{
    padding:16px 20px!important;
    font-family:'DM Sans',sans-serif;
    font-size:.84rem;
    color:rgba(255,247,230,.82)!important;
    line-height:1.65;
    margin:10px 0;
}

.twinkle-layer,.constellation,.cosmos-bg{display:none!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FINAL CLEAN PLOTLY HELPERS -- single source of truth
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
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_SOFT, size=13),
        showlegend=showlegend,
        margin=dict(l=52, r=54, t=18, b=58),
        hoverlabel=dict(
            bgcolor="#111722",
            bordercolor="rgba(255,255,255,.16)",
            font_color="white",
            font_family="Inter",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=TEXT_MUTED, tickfont=dict(size=12))
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False, color=TEXT_MUTED, tickfont=dict(size=12))
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
            marker=dict(colors=colors, line=dict(color="#080B12", width=3)),
            textinfo="percent",
            textfont=dict(size=15, color="white"),
            hovertemplate="%{label}<br>%{percent}<br>%{value}<extra></extra>",
        )
    )
    _plotly_layout(fig, height=height, showlegend=True)
    fig.update_layout(
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=12, color=TEXT_SOFT)),
        margin=dict(l=20, r=20, t=8, b=76),
    )
    plotly_card(title, fig, height)


def plotly_vbar_chart(title, labels, series=None, values=None, colors=None, max_value=None, value_format="number", height=420, fmt_fn=None, y_label="", **kwargs):
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
                marker=dict(color=marker_colors, line=dict(width=0)),
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


def plotly_hbar_chart(title, labels, values, colors=None, color=None, value_format="money", height=460, fmt_fn=None, **kwargs):
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
            marker=dict(color=colors, line=dict(width=0)),
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
    """Compute live model metrics from the loaded artifact and current labeled dataset."""
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
    # Safe fallback only if an environment/version issue prevents metric recomputation.
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
    st.markdown('<div class="sidebar-brand">Airline <span>Route</span> Intelligence ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.64rem;color:{ACCENT};margin-bottom:14px;"
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
    st.markdown(f"""
    <p style='font-size:0.62rem;color:{ACCENT};font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;margin-bottom:10px;font-family:DM Sans,sans-serif'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:9px;font-size:0.80rem;color:{INK_SOFT};font-family:DM Sans,sans-serif'>
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
<style>
.hero{
    position:relative;
    padding:72px 80px!important;
    border-radius:30px!important;
    overflow:hidden;
    margin-bottom:40px!important;
    background:
        linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,.075)),
        radial-gradient(circle at 28% 75%,rgba(91,188,246,.18),transparent 32%),
        radial-gradient(circle at 82% 18%,rgba(244,137,92,.15),transparent 36%),
        rgba(18,20,36,.42)!important;
    border:1px solid rgba(255,255,255,.26)!important;
    border-top:1px solid rgba(255,255,255,.38)!important;
    border-left:1px solid rgba(255,255,255,.32)!important;
    backdrop-filter:blur(18px) saturate(115%)!important;
    -webkit-backdrop-filter:blur(18px) saturate(115%)!important;
    box-shadow:0 24px 80px rgba(0,0,0,.50), inset 0 1px 24px rgba(255,255,255,.11)!important;
}
.hero::before{
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background:
        radial-gradient(circle at 58% 62%,rgba(255,245,207,.70) 0 1px,transparent 2px),
        radial-gradient(circle at 68% 45%,rgba(255,245,207,.42) 0 1px,transparent 2px),
        radial-gradient(circle at 42% 35%,rgba(202,237,255,.40) 0 1px,transparent 2px),
        radial-gradient(circle at 86% 28%,rgba(255,245,207,.40) 0 1px,transparent 2px),
        linear-gradient(90deg,transparent,rgba(255,255,255,.35) 35%,rgba(255,255,255,.28) 65%,transparent);
    opacity:.75;
}
.hero>*{position:relative;z-index:1;}
.hero-eyebrow{
    font-family:'DM Sans',sans-serif;
    font-size:.72rem!important;
    letter-spacing:.32em!important;
    text-transform:uppercase!important;
    color:rgba(143,217,239,.88)!important;
    margin-bottom:18px;
    text-shadow:0 2px 12px rgba(0,0,0,.95);
}
.hero h1{
    font-family:'Cinzel',serif!important;
    font-size:clamp(3.2rem,7vw,6rem)!important;
    line-height:.9!important;
    letter-spacing:.08em!important;
    text-transform:uppercase!important;
    font-weight:900!important;
    color:#FFF5CF!important;
    margin-bottom:22px;
    text-shadow:0 5px 22px rgba(0,0,0,.90),0 0 28px rgba(255,231,178,.24)!important;
}
.hero p{
    font-family:'DM Sans',sans-serif;
    color:rgba(255,247,230,.86)!important;
    font-size:1.02rem!important;
    line-height:1.75!important;
    max-width:620px;
    margin-bottom:32px;
    text-shadow:0 3px 14px rgba(0,0,0,.88);
}
.hero-badge{
    display:inline-flex;
    align-items:center;
    gap:10px;
    padding:11px 26px;
    border-radius:999px;
    background:linear-gradient(90deg,rgba(71,142,211,.70),rgba(236,168,76,.52));
    border:1px solid rgba(255,255,255,.58);
    backdrop-filter:blur(18px);
    color:#FFFEFA;
    font-family:'DM Sans',sans-serif;
    font-size:.80rem;
    font-weight:800;
    letter-spacing:.10em;
    box-shadow:0 0 22px rgba(113,178,255,.48), inset 0 0 12px rgba(255,255,255,.24);
    text-shadow:0 2px 10px rgba(0,0,0,.8);
}
</style>

<div class="hero">
  <div class="hero-eyebrow">✦ &nbsp; Airline Route Intelligence &nbsp; ✦</div>
  <h1>SKYLENS<br>DASHBOARD</h1>
  <p>Analyze route profitability, operational signals, and model-backed decisions &mdash; all in one polished command view.</p>
  <div class="hero-badge">✦ &nbsp; Explore dashboard below</div>
</div>
""", unsafe_allow_html=True)

# The rest of your original app logic remains unchanged below this point.
# Keep everything from your TABS section through the footer exactly as you already have it.











# ─────────────────────────────────────────────────────────────
#  FINAL CLEAN PLOTLY HELPERS -- single source of truth
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
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_SOFT, size=13),
        showlegend=showlegend,
        margin=dict(l=52, r=54, t=18, b=58),
        hoverlabel=dict(
            bgcolor="#111722",
            bordercolor="rgba(255,255,255,.16)",
            font_color="white",
            font_family="Inter",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=TEXT_MUTED, tickfont=dict(size=12))
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False, color=TEXT_MUTED, tickfont=dict(size=12))
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
            marker=dict(colors=colors, line=dict(color="#080B12", width=3)),
            textinfo="percent",
            textfont=dict(size=15, color="white"),
            hovertemplate="%{label}<br>%{percent}<br>%{value}<extra></extra>",
        )
    )
    _plotly_layout(fig, height=height, showlegend=True)
    fig.update_layout(
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=12, color=TEXT_SOFT)),
        margin=dict(l=20, r=20, t=8, b=76),
    )
    plotly_card(title, fig, height)


def plotly_vbar_chart(title, labels, series=None, values=None, colors=None, max_value=None, value_format="number", height=420, fmt_fn=None, y_label="", **kwargs):
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
                marker=dict(color=marker_colors, line=dict(width=0)),
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


def plotly_hbar_chart(title, labels, values, colors=None, color=None, value_format="money", height=460, fmt_fn=None, **kwargs):
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
            marker=dict(color=colors, line=dict(width=0)),
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
    """Compute live model metrics from the loaded artifact and current labeled dataset."""
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
    # Safe fallback only if an environment/version issue prevents metric recomputation.
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
    st.markdown('<div class="sidebar-brand">Airline <span>Route</span> Intelligence ✦</div>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.64rem;color:{ACCENT};margin-bottom:14px;"
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
    st.markdown(f"""
    <p style='font-size:0.62rem;color:{ACCENT};font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;margin-bottom:10px;font-family:DM Sans,sans-serif'>Decision Labels</p>
    <div style='display:flex;flex-direction:column;gap:9px;font-size:0.80rem;color:{INK_SOFT};font-family:DM Sans,sans-serif'>
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
<style>
/* ── SINGLE HERO ── */
.hero {
    position: relative;
    padding: 72px 80px !important;
    border-radius: 32px !important;
    overflow: hidden;
    margin-bottom: 40px !important;

    /* frosted glass -- same treatment as metric cards */
    background: linear-gradient(
        145deg,
        rgba(255,255,255,.18) 0%,
        rgba(255,255,255,.08) 60%,
        rgba(255,255,255,.03) 100%
    ) !important;

    border: 1px solid rgba(255,255,255,.22) !important;
    border-top: 1px solid rgba(255,255,255,.35) !important;
    border-left: 1px solid rgba(255,255,255,.28) !important;

    backdrop-filter: blur(36px) saturate(200%) brightness(1.05) !important;
    -webkit-backdrop-filter: blur(36px) saturate(200%) brightness(1.05) !important;

    box-shadow:
        0 20px 80px rgba(0,0,0,.55),
        0 2px 0px rgba(255,255,255,.14) inset,
        0 0 0 0.5px rgba(255,255,255,.08) inset;
}

/* subtle highlight sweep across top of hero */
.hero::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(255,255,255,.50) 30%,
        rgba(255,255,255,.50) 70%,
        transparent);
    pointer-events: none;
}

.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: .72rem !important;
    letter-spacing: .32em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,.50) !important;
    margin-bottom: 18px;
}

.hero h1 {
    font-family: 'Cinzel', serif !important;
    font-size: clamp(3.2rem, 7vw, 6rem) !important;
    line-height: .9 !important;
    letter-spacing: .10em !important;
    text-transform: uppercase !important;
    font-weight: 900 !important;
    color: #FFFDF8 !important;
    margin-bottom: 22px;
}

.hero p {
    font-family: 'DM Sans', sans-serif;
    color: rgba(255,255,255,.65) !important;
    font-size: 1.02rem !important;
    line-height: 1.75 !important;
    max-width: 620px;
    margin-bottom: 32px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 11px 26px;
    border-radius: 999px;
    background: linear-gradient(145deg, rgba(255,255,255,.16), rgba(255,255,255,.05));
    border: 1px solid rgba(255,255,255,.20);
    backdrop-filter: blur(20px);
    color: #fff;
    font-family: 'DM Sans', sans-serif;
    font-size: .80rem;
    font-weight: 700;
    letter-spacing: .10em;
}
</style>

<!-- SINGLE HERO -->
<div class="hero">
  <div class="hero-eyebrow">✦ &nbsp; Airline Route Intelligence &nbsp; ✦</div>
  <h1>SKYLENS<br>DASHBOARD</h1>
  <p>Analyze route profitability, operational signals, and model-backed decisions &mdash; all in one polished command view.</p>
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
        dc = dc.reindex([x for x in ORDER if x in dc.index]).dropna()
        wc = {
            "Expand":   CHART_EXPAND,
            "Maintain": CHART_MAINTAIN,
            "Optimize": CHART_OPTIMIZE,
            "Drop":     CHART_DROP,
        }
        wedge_colors = [wc[l] for l in dc.index]
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
            .round(3).reset_index()
            .rename(columns={
                "Route_Decision": "Decision",
                "Profit": "Avg Profit ($)",
                "Profit_Margin": "Avg Margin",
                "Load_Factor": "Avg Load Factor",
            })
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("""
        <div class="info-box">
          <strong style="color:#7c3aed">How to read this</strong><br>
          Each row shows average profitability and seat occupancy for flights in that category.
          <strong style="color:#1d4ed8">Expand</strong> routes should have the highest values across all three columns.
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

    # Build a gradient of jewel tones for cost bars
    nc = len(cost_means)
    jewel_ramp = [
        CHART_EXPAND, "#0e7490", ACCENT, CHART_MAINTAIN,
        "#15803d", CHART_OPTIMIZE, CHART_DROP, "#6d28d9",
    ]
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
        series=[{
            "name": "Unique Routes",
            "values": vals4,
            "color": ACCENT,
            "colors": bc,
        }],
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
            {
                "name": "Accuracy",
                "values": comparison["Accuracy"].tolist(),
                "color": ACCENT,
            },
            {
                "name": "Macro F1",
                "values": comparison["Macro F1"].tolist(),
                "color": ACCENT_2,
            },
        ],
        max_value=1.0,
        value_format="percent",
        height=430,
    )

    st.markdown('<div class="divider-label">Configuration</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-hd">Choose a prediction mode</p>', unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
    <span class='pill pill-maintain'>With Revenue</span>&nbsp; Most accurate &mdash; use when you have ticket &amp; ancillary revenue data.<br><br>
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
            "Expand":   "This route shows strong performance signals &mdash; high profit, solid margins, and healthy seat occupancy. Consider allocating more capacity here.",
            "Maintain": "This route is working well and performing steadily. No urgent changes needed &mdash; keep monitoring.",
            "Optimize": "This route has potential but something is holding it back &mdash; efficiency or demand may need attention before investing more.",
            "Drop":     "This route is losing money. A deeper review is recommended to determine whether it can be restructured or should be discontinued.",
        }

        st.markdown(f"""
        <div class='result-card {result_cls.get(pred, "result-expand")}'>
          <div style='margin-bottom:10px'>
            <span class='pill {pill_cls.get(pred, "")}'>{pred}</span>
          </div>
          <div style='font-family:"Cinzel",serif;font-size:1.55rem;font-weight:600;
                      color:{text_col.get(pred, INK)};margin-bottom:10px;letter-spacing:0.04em;
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
            series=[{
                "name": "Probability",
                "values": probs,
                "color": ACCENT,
                "colors": bar_colors,
            }],
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
              background:rgba(18,18,22,0.82);
              border:1px solid rgba(255,255,255,0.10);
              border-radius:999px;
              padding:0.55rem 1.4rem;
              backdrop-filter:blur(14px);
              box-shadow:0 20px 60px rgba(0,0,0,0.35);
              font-family:"DM Sans",sans-serif;
              font-size:0.67rem;
              font-weight:600;
              color:{INK_MUTED};
              letter-spacing:0.12em;
              text-transform:uppercase'>
    <span style='color:{ACCENT};font-size:0.78rem'>✦</span>
    Airline Profitability System
    <span style='color:{ACCENT};font-size:0.78rem'>✦</span>
    Built with Streamlit
  </div>
</div>
""", unsafe_allow_html=True)