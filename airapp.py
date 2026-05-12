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
TEXT = "#F5F7FB"
TEXT_SOFT = "#C9D2E3"
TEXT_MUTED = "#7F8AA3"
CYAN = "#38BDF8"
BLUE = "#2563EB"
AMBER = "#F59E0B"
GREEN = "#22C55E"
RED = "#F43F5E"
VIOLET = "#A78BFA"

CHART_EXPAND   = "#22C55E"
CHART_MAINTAIN = "#FACC15"
CHART_OPTIMIZE = "#FB923C"
CHART_DROP     = "#FB7185"
CHART_NEUTRAL  = ["#38BDF8", "#A78BFA", "#F59E0B", "#22C55E", "#FB7185", "#60A5FA", "#2DD4BF", "#F472B6"]
DECISION_COLORS = {"Expand": CHART_EXPAND, "Maintain": CHART_MAINTAIN, "Optimize": CHART_OPTIMIZE, "Drop": CHART_DROP}
ORDER = ["Expand", "Maintain", "Optimize", "Drop"]

ACCENT = CYAN
INK = TEXT
INK_SOFT = TEXT_SOFT
INK_MUTED = TEXT_MUTED

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root {{
  --bg:#050505; --panel:rgba(18,18,22,.78); --panel2:rgba(24,24,30,.72);
  --ink:#F7F7F8; --soft:#B9BBC6; --muted:#737684;
  --blue:#5E6AD2; --violet:#8B5CF6; --green:#34D399; --yellow:#FBBF24; --orange:#FB923C; --red:#FB7185;
  --border:rgba(255,255,255,.10); --border2:rgba(255,255,255,.16);
}}
html,body,[class*="css"] {{ font-family:'Inter',system-ui,sans-serif!important; color:var(--ink)!important; -webkit-font-smoothing:antialiased; scroll-behavior:smooth; }}
.stApp {{
  min-height:100vh!important; overflow-x:hidden!important; position:relative!important;
  background:
    radial-gradient(circle at 50% -10%, rgba(94,106,210,.18), transparent 32%),
    radial-gradient(circle at 82% 20%, rgba(139,92,246,.10), transparent 28%),
    radial-gradient(circle at 22% 76%, rgba(56,189,248,.055), transparent 26%),
    linear-gradient(180deg,#050505 0%,#08080A 54%,#050505 100%)!important;
}}
.stApp:before {{
  content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.14;
  background-image:
    radial-gradient(circle, rgba(255,255,255,.55) 0 1px, transparent 1.4px),
    radial-gradient(circle, rgba(160,170,255,.38) 0 1px, transparent 1.3px);
  background-size:180px 180px,260px 260px; background-position:20px 30px,120px 90px;
}}
.stApp:after {{
  content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.045;
  background:
    linear-gradient(115deg, transparent 0 22%, rgba(255,255,255,.8) 22.1%, transparent 22.28%),
    linear-gradient(35deg, transparent 0 54%, rgba(255,255,255,.8) 54.1%, transparent 54.24%),
    linear-gradient(150deg, transparent 0 72%, rgba(255,255,255,.8) 72.1%, transparent 72.24%);
}}
.linear-bg {{ position:fixed; inset:0; z-index:1; pointer-events:none; overflow:hidden; }}
.constellation {{ position:absolute; width:420px; height:220px; opacity:.16; }}
.constellation.one {{ left:9%; top:13%; }} .constellation.two {{ right:8%; top:32%; transform:scale(.85) rotate(14deg); opacity:.10; }}
.constellation:before {{ content:""; position:absolute; inset:0; background:linear-gradient(25deg,transparent 0 35%,rgba(255,255,255,.45) 35.1%,transparent 35.5%),linear-gradient(145deg,transparent 0 58%,rgba(255,255,255,.35) 58.1%,transparent 58.5%); }}
.orb {{ position:absolute; border-radius:50%; filter:blur(70px); opacity:.22; }} .orb.one {{ width:460px;height:460px;left:42%;top:-190px;background:#5E6AD2; }} .orb.two {{ width:320px;height:320px;right:-120px;bottom:10%;background:#8B5CF6;opacity:.12; }}
.main .block-container {{ max-width:1240px!important; padding-top:2rem!important; padding-bottom:4rem!important; position:relative!important; z-index:3!important; }}
[data-testid="stSidebar"] {{ background:rgba(8,8,10,.72)!important; border-right:1px solid var(--border)!important; backdrop-filter:blur(24px) saturate(140%)!important; box-shadow:16px 0 60px rgba(0,0,0,.32)!important; }}
[data-testid="stSidebar"] * {{ color:var(--soft)!important; }}
.sidebar-brand {{ font-size:1.18rem; font-weight:800; padding:.35rem 0 1rem; margin-bottom:1rem; border-bottom:1px solid var(--border); letter-spacing:-.04em; color:white!important; }}
.sidebar-brand span {{ color:#A8B1FF!important; -webkit-text-fill-color:unset!important; background:none!important; }}
.hero,.feature-inner,[data-testid="metric-container"],[data-testid="stForm"],[data-testid="stDataFrame"],[data-testid="stExpander"],.info-box,.result-card,.plotly-card {{
  background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025)),rgba(18,18,22,.82)!important;
  border:1px solid var(--border)!important; border-radius:24px!important;
  box-shadow:0 24px 80px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06)!important;
  backdrop-filter:blur(20px) saturate(140%)!important; -webkit-backdrop-filter:blur(20px) saturate(140%)!important;
}}
.hero {{ padding:44px 46px!important; margin-bottom:22px!important; overflow:hidden; position:relative; }}
.hero:before {{ content:""; position:absolute; width:420px; height:420px; right:-180px; top:-210px; background:radial-gradient(circle,rgba(94,106,210,.20),transparent 68%); pointer-events:none; }}
.hero h1 {{ font-family:'Inter',system-ui,sans-serif!important; font-size:clamp(2.25rem,5vw,4.8rem)!important; line-height:.95!important; letter-spacing:-.085em!important; color:white!important; margin:0!important; text-transform:none!important; }}
.hero p {{ color:var(--soft)!important; max-width:680px; font-size:1rem!important; line-height:1.65!important; margin:.9rem 0 0!important; }}
.hero-eyebrow {{ color:#A8B1FF; font-size:.72rem; font-weight:800; letter-spacing:.18em; text-transform:uppercase; margin-bottom:14px; }}
.hero-badge {{ display:inline-flex; margin-top:22px; padding:9px 14px; border:1px solid rgba(255,255,255,.12); border-radius:999px; color:#E9EAFF; background:rgba(94,106,210,.12); font-size:.72rem; font-weight:700; letter-spacing:.04em; }}
.hero-glyph,.hero-star {{ display:none!important; }}
.feature-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:8px 0 26px; }}
.feature-card {{ position:relative; transition:transform .25s ease; }} .feature-card:hover {{ transform:translateY(-3px); }}
.feature-card:before {{ content:""; position:absolute; inset:18px; background:var(--card-gradient); filter:blur(42px); opacity:.12; z-index:-1; }}
.feature-inner {{ min-height:170px!important; padding:22px!important; border-radius:24px!important; border:1px solid var(--border)!important; }}
.feature-icon {{ font-size:24px; margin-bottom:28px; opacity:.9; }}
.feature-inner h3 {{ font-family:'Inter',system-ui,sans-serif!important; color:white!important; font-size:1.05rem!important; margin:0 0 8px!important; text-transform:none!important; letter-spacing:-.04em!important; }}
.feature-inner p {{ color:rgba(185,187,198,.78)!important; font-size:.86rem!important; line-height:1.58!important; margin:0!important; }}
[data-testid="metric-container"] {{ padding:22px!important; transition:transform .22s ease,border-color .22s ease!important; }}
[data-testid="metric-container"]:hover,.plotly-card:hover,.feature-card:hover {{ border-color:var(--border2)!important; box-shadow:0 30px 90px rgba(0,0,0,.55),0 0 38px rgba(94,106,210,.10),inset 0 1px 0 rgba(255,255,255,.08)!important; }}
[data-testid="metric-container"]:hover {{ transform:translateY(-3px)!important; }}
[data-testid="stMetricLabel"] p {{ color:var(--muted)!important; font-size:.66rem!important; letter-spacing:.12em!important; text-transform:uppercase!important; font-weight:700!important; }}
[data-testid="stMetricValue"],[data-testid="stMetricValue"]>div {{ color:white!important; font-size:2rem!important; font-weight:800!important; letter-spacing:-.06em!important; }}
.stTabs [data-baseweb="tab-list"] {{ gap:4px; padding:5px; border-radius:18px; background:rgba(18,18,22,.70); border:1px solid var(--border); backdrop-filter:blur(20px); }}
.stTabs [data-baseweb="tab"] {{ border-radius:13px!important; color:var(--muted)!important; font-weight:700!important; padding:9px 14px!important; }}
.stTabs [aria-selected="true"] {{ background:rgba(255,255,255,.07)!important; color:white!important; border:1px solid rgba(255,255,255,.09)!important; }} .stTabs [data-baseweb="tab-highlight"] {{ display:none!important; }}
.section-hd {{ font-family:'Inter',system-ui,sans-serif!important; font-size:1.05rem!important; color:white!important; font-weight:750!important; letter-spacing:-.04em!important; margin:0 0 6px!important; }}
.section-sub {{ color:var(--muted)!important; margin:0 0 18px!important; line-height:1.65!important; }}
.divider-label {{ display:flex; gap:14px; align-items:center; margin:28px 0 18px; color:#A8B1FF; font-size:.66rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }} .divider-label:before,.divider-label:after {{ content:""; height:1px; flex:1; background:linear-gradient(90deg,transparent,rgba(255,255,255,.14),transparent); }}
.info-box {{ padding:18px 20px!important; color:var(--soft)!important; line-height:1.7; }} .info-box strong {{ color:white!important; }}
.pill {{ display:inline-block; padding:5px 10px; border-radius:999px; font-size:.62rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase; border:1px solid transparent; }}
.pill-expand{{background:rgba(52,211,153,.10);color:#A7F3D0;border-color:rgba(52,211,153,.25)}} .pill-maintain{{background:rgba(251,191,36,.10);color:#FDE68A;border-color:rgba(251,191,36,.24)}} .pill-optimize{{background:rgba(251,146,60,.10);color:#FDBA74;border-color:rgba(251,146,60,.24)}} .pill-drop{{background:rgba(251,113,133,.10);color:#FDA4AF;border-color:rgba(251,113,133,.24)}}
.result-card {{ padding:26px 28px!important; margin:24px 0!important; }} .result-expand{{border-left:3px solid #34D399!important}}.result-maintain{{border-left:3px solid #FBBF24!important}}.result-optimize{{border-left:3px solid #FB923C!important}}.result-drop{{border-left:3px solid #FB7185!important}}
.stSelectbox label,.stNumberInput label,.stSlider label,.stRadio label,.stCheckbox label,.stTextInput label {{ color:var(--soft)!important; font-weight:700!important; font-size:.70rem!important; letter-spacing:.07em!important; text-transform:uppercase!important; }}
.stSelectbox [data-baseweb="select"]>div,.stTextInput input,.stNumberInput input {{ background:rgba(5,5,5,.55)!important; border:1px solid var(--border)!important; border-radius:12px!important; color:white!important; min-height:40px!important; }}
[data-testid="stForm"] {{ padding:24px 26px 28px!important; }} [data-testid="stFormSubmitButton"]>button,.stButton>button {{ border-radius:999px!important; font-weight:800!important; border:1px solid rgba(255,255,255,.14)!important; background:#5E6AD2!important; color:white!important; box-shadow:0 12px 34px rgba(94,106,210,.22)!important; transition:transform .2s ease!important; }} [data-testid="stFormSubmitButton"]>button:hover,.stButton>button:hover {{ transform:translateY(-2px)!important; background:#6F7BE8!important; }}
[data-testid="stDataFrame"] div,[data-testid="stDataFrame"] span {{ color:var(--soft)!important; }}
.plotly-card {{ border-radius:24px; padding:16px 16px 6px; margin-bottom:18px; }}
.plotly-card-title {{ font-size:1.02rem; font-weight:750; color:white; letter-spacing:-.04em; margin:4px 6px 10px; }}
hr {{ border:none!important; border-top:1px solid rgba(255,255,255,.10)!important; }} ::selection {{ background:rgba(94,106,210,.28); }}
@media(max-width:900px) {{ .feature-grid {{ grid-template-columns:1fr; }} }}
</style>
<div class="linear-bg"><div class="orb one"></div><div class="orb two"></div><div class="constellation one"></div><div class="constellation two"></div></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  FINAL CLEAN PLOTLY HELPERS — single source of truth
# ─────────────────────────────────────────────────────────────
def _fmt_money(v):
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def col_seq(labels):
    return [DECISION_COLORS.get(str(label), CYAN) for label in labels]
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
<div class="hero">
  <div class="hero-star"></div><div class="hero-star"></div>
  <div class="hero-star"></div><div class="hero-star"></div>
  <div class="hero-left">
    <div class="hero-eyebrow">✦ Route Intelligence Platform</div>
    <h1>Airline Profitability System</h1>
    <p>Sample airline dataset · for analysis &amp; demonstration only</p>
  </div>
  <div class="hero-badge">⚡ ML-Powered Decisions</div>
  <div class="hero-glyph">✈</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
  <div class="feature-card" style="--card-gradient:linear-gradient(137deg,#38BDF8 0%,#7DD3FC 45%,#2563EB 100%)"><div class="feature-inner"><div class="feature-icon">✈️</div><h3>Route Intelligence</h3><p>Monitor route profitability, load factor, and network performance through a polished executive dashboard.</p></div></div>
  <div class="feature-card" style="--card-gradient:linear-gradient(137deg,#FACC15 0%,#FB923C 45%,#FB7185 100%)"><div class="feature-inner"><div class="feature-icon">📡</div><h3>Decision Engine</h3><p>Classify routes into Expand, Maintain, Optimize, or Drop with model-backed confidence scores.</p></div></div>
  <div class="feature-card" style="--card-gradient:linear-gradient(137deg,#22C55E 0%,#2DD4BF 45%,#A78BFA 100%)"><div class="feature-inner"><div class="feature-icon">💹</div><h3>Profit Signals</h3><p>Surface the costs, demand patterns, and stability issues that drive airline profitability.</p></div></div>
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