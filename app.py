"""
B2B Sales Intelligence Dashboard
==================================
Interactive Streamlit App — Part C (KPIs + Charts) & Part D (Business Insights)
FIXED: Dark mode compatible — all headings, cards, and charts now visible in both themes
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from itertools import combinations
from collections import Counter
import io

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark mode compatible
# Uses Streamlit's built-in CSS variables so colors adapt automatically
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Import a distinctive font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%) !important;
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stMultiSelect span { color: #1e293b !important; }
    section[data-testid="stSidebar"] label { color: #cbd5e1 !important; }

    /* ── KPI Cards — use currentColor trick so text is always visible ── */
    .kpi-card {
        border-radius: 16px;
        padding: 24px 18px;
        text-align: center;
        border-top: 5px solid;
        transition: transform .2s, box-shadow .2s;
        /* Light-mode default */
        background: #ffffff;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08);
    }
    /* Dark mode override via Streamlit's data-theme attribute */
    [data-theme="dark"] .kpi-card,
    .stApp[data-theme="dark"] .kpi-card {
        background: #1e293b !important;
        box-shadow: 0 2px 16px rgba(0,0,0,0.35) !important;
    }
    .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
    .kpi-value  { font-size: 2.1rem; font-weight: 900; margin: 8px 0 5px; }
    .kpi-label  {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        /* Adapts to theme via Streamlit's own text color */
        color: #64748b;
    }
    [data-theme="dark"] .kpi-label { color: #94a3b8 !important; }

    /* ── Section Headers — visible in both themes ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        margin: 36px 0 18px;
        padding: 10px 16px;
        border-left: 5px solid #2563EB;
        border-radius: 0 8px 8px 0;
        letter-spacing: -0.3px;
        /* Light */
        color: #0f172a;
        background: linear-gradient(90deg, rgba(37,99,235,0.08) 0%, transparent 100%);
    }
    [data-theme="dark"] .section-header {
        color: #e2e8f0 !important;
        background: linear-gradient(90deg, rgba(37,99,235,0.18) 0%, transparent 100%) !important;
    }

    /* ── Chart wrapper boxes ── */
    .chart-box {
        border-radius: 16px;
        padding: 6px;
        /* Light */
        background: #ffffff;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    [data-theme="dark"] .chart-box {
        background: #1e293b !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
    }

    /* ── Insight cards ── */
    .insight-card {
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 16px;
        border-top: 4px solid transparent;
        /* Light */
        background: #ffffff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    [data-theme="dark"] .insight-card {
        background: #1e293b !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
    }
    .insight-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

   /* ── Dashboard title ── */
.dash-title {
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.8px;
    color: #ffffff;  /* white */
}
[data-theme="dark"] .dash-title { color: #ffffff !important; }
    }
    [data-theme="dark"] .dash-title { color: #f1f5f9 !important; }

    .dash-subtitle {
        font-size: 0.92rem;
        margin-top: 4px;
        color: #64748b;
    }
    [data-theme="dark"] .dash-subtitle { color: #94a3b8 !important; }

    /* ── Insight body text ── */
    .insight-body {
        font-size: 0.88rem;
        line-height: 1.65;
        color: #475569;
    }
    [data-theme="dark"] .insight-body { color: #94a3b8 !important; }

    /* ── Section sub-headings (#### tags) ── */
    h4 {
        color: #0f172a !important;
    }
    [data-theme="dark"] h4 { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#2563EB", "#7C3AED", "#059669", "#DC2626", "#D97706", "#0891B2"]

# Helper: detect dark mode for Plotly chart theming
# We'll use transparent backgrounds so Plotly charts adapt naturally
PLOT_BG    = "rgba(0,0,0,0)"   # transparent — inherits from container
PAPER_BG   = "rgba(0,0,0,0)"
FONT_COLOR = None               # let Plotly use its default (theme-aware)

def base_layout(title="", height=320):
    return dict(
        title=title,
        title_font=dict(size=14, color=None),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
    )

# ─────────────────────────────────────────────
# SIDEBAR — file uploader always shown first
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 B2B Dashboard")
    st.markdown("---")
    st.markdown("### 📂 Upload Dataset")
    uploaded = st.file_uploader(
        "Upload your Excel file (.xlsx)",
        type=["xlsx"],
        label_visibility="collapsed",
    )

# ── Welcome screen ────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown('<div class="dash-title">📊 B2B Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Part C · KPI Metrics &amp; Charts &nbsp;|&nbsp; Part D · Business Insights</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈  **Upload your Excel dataset in the sidebar** to launch the dashboard.")
    st.markdown("""
**Required columns in your `.xlsx` file:**

| Column | Type |
|---|---|
| Client_ID | text |
| Product_ID | text |
| Product_Category | text |
| Region | text |
| Purchase_Frequency | number |
| Revenue | number |
| Last_Purchase_Date | date |
    """)
    st.stop()

# ─────────────────────────────────────────────
# LOAD & VALIDATE DATA
# ─────────────────────────────────────────────
try:
    file_bytes = uploaded.read()
    df_raw = pd.read_excel(io.BytesIO(file_bytes))
    df_raw["Last_Purchase_Date"] = pd.to_datetime(df_raw["Last_Purchase_Date"])
except Exception as e:
    st.error(f"❌ Could not read the file: {e}")
    st.stop()

required_cols = {"Client_ID", "Product_Category", "Region",
                 "Purchase_Frequency", "Revenue", "Last_Purchase_Date"}
missing = required_cols - set(df_raw.columns)
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🌍 Region")
    all_regions = sorted(df_raw["Region"].unique())
    sel_regions = st.multiselect("Regions", all_regions, default=all_regions, label_visibility="collapsed")

    st.markdown("### 📦 Product Category")
    all_cats = sorted(df_raw["Product_Category"].unique())
    sel_cats = st.multiselect("Categories", all_cats, default=all_cats, label_visibility="collapsed")

    st.markdown("### 📅 Purchase Frequency")
    fmin, fmax = int(df_raw["Purchase_Frequency"].min()), int(df_raw["Purchase_Frequency"].max())
    sel_freq = st.slider("Frequency", fmin, fmax, (fmin, fmax), label_visibility="collapsed")

    st.markdown("### 💰 Revenue Range ($)")
    rmin, rmax = int(df_raw["Revenue"].min()), int(df_raw["Revenue"].max())
    sel_rev = st.slider("Revenue", rmin, rmax, (rmin, rmax), label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 📌 Part D Toggles")
    show_pairs    = st.checkbox("① Products Bought Together",   value=True)
    show_repeat   = st.checkbox("② Repeat Purchases by Region", value=True)
    show_rec      = st.checkbox("③ Recommendations vs Revenue", value=True)
    show_strategy = st.checkbox("④ Suggested Strategies",       value=True)
    st.markdown("---")
    st.caption("B2B Sales Dashboard · Part C & D")

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()
if sel_regions:
    df = df[df["Region"].isin(sel_regions)]
if sel_cats:
    df = df[df["Product_Category"].isin(sel_cats)]
df = df[
    (df["Purchase_Frequency"] >= sel_freq[0]) & (df["Purchase_Frequency"] <= sel_freq[1]) &
    (df["Revenue"] >= sel_rev[0])             & (df["Revenue"] <= sel_rev[1])
]

if df.empty:
    st.warning("⚠️ No data matches your filters. Please adjust the sidebar selections.")
    st.stop()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
c1, c2 = st.columns([5, 1])
with c1:
    st.markdown('<div class="dash-title">📊 B2B Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Part C · KPI Metrics &amp; Charts &nbsp;|&nbsp; Part D · Business Insights</div>', unsafe_allow_html=True)
with c2:
    st.metric("Records", f"{len(df):,}")
st.markdown("---")

# ─────────────────────────────────────────────
# PART C — KPI METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Part C · KPI Metrics</div>', unsafe_allow_html=True)

total_sales      = len(df)
repeat_customers = int((df["Purchase_Frequency"] > 1).sum())
rec_success_rate = round(repeat_customers / total_sales * 100, 1)
total_revenue    = int(df["Revenue"].sum())
avg_order_value  = int(df["Revenue"].mean())
top_region       = df.groupby("Region")["Revenue"].sum().idxmax()
top_category     = df.groupby("Product_Category")["Revenue"].sum().idxmax()

kpi_list = [
    ("📦", "Total Sales",                 str(total_sales),       "#2563EB"),
    ("🔁", "Repeat Customers",            str(repeat_customers),   "#7C3AED"),
    ("✅", "Recommendation Success Rate", f"{rec_success_rate}%", "#059669"),
    ("💰", "Total Revenue",               f"${total_revenue:,}",  "#DC2626"),
]
for col, (icon, label, value, color) in zip(st.columns(4), kpi_list):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div style="font-size:1.9rem">{icon}</div>
            <div class="kpi-value" style="color:{color}">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
m1.metric("💵 Avg Order Value", f"${avg_order_value:,}")
m2.metric("🏆 Top Region",      top_region)
m3.metric("🥇 Top Category",    top_category)

# ─────────────────────────────────────────────
# PART C — CHARTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Part C · Charts</div>', unsafe_allow_html=True)

# Chart 1 — Monthly Revenue Trend
trend = (df.groupby(df["Last_Purchase_Date"].dt.to_period("M"))["Revenue"]
           .sum().reset_index())
trend["Month_str"] = trend["Last_Purchase_Date"].astype(str)
trend = trend.sort_values("Last_Purchase_Date")

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["Month_str"], y=trend["Revenue"],
    mode="lines+markers",
    line=dict(color="#2563EB", width=3),
    marker=dict(size=8, color="white", line=dict(color="#2563EB", width=2.5)),
    fill="tozeroy", fillcolor="rgba(37,99,235,0.12)",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
))
fig_trend.update_layout(
    **base_layout("📈 Customer Purchase Trends (Monthly Revenue)", 320),
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=10)),
    yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="rgba(148,163,184,0.2)"),
)
st.markdown('<div class="chart-box">', unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts 2 & 3 — Category + Region
cl, cr = st.columns(2)

with cl:
    cat_data = df.groupby("Product_Category")["Revenue"].sum().reset_index().sort_values("Revenue")
    fig_cat = px.bar(
        cat_data, x="Revenue", y="Product_Category", orientation="h",
        color="Product_Category", color_discrete_sequence=PALETTE,
        text=cat_data["Revenue"].apply(lambda v: f"${v/1e6:.2f}M"),
        title="📦 Product Category Performance",
    )
    fig_cat.update_traces(textposition="outside", marker_line_width=0)
    fig_cat.update_layout(
        **base_layout("📦 Product Category Performance", 340),
        showlegend=False,
        xaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="rgba(148,163,184,0.2)"),
        yaxis=dict(showgrid=False),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with cr:
    reg_data = df.groupby("Region").agg(Revenue=("Revenue","sum"), Sales=("Client_ID","count")).reset_index()
    fig_reg = make_subplots(specs=[[{"secondary_y": True}]])
    fig_reg.add_trace(go.Bar(
        x=reg_data["Region"], y=reg_data["Revenue"], name="Revenue",
        marker_color="#2563EB", opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig_reg.add_trace(go.Bar(
        x=reg_data["Region"], y=reg_data["Sales"], name="Sales Count",
        marker_color="#7C3AED", opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Sales: %{y}<extra></extra>",
    ), secondary_y=True)
    fig_reg.update_layout(
        **base_layout("🌍 Region-wise Sales", 340),
        barmode="group",
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(showgrid=False),
    )
    fig_reg.update_yaxes(tickprefix="$", tickformat=".2s", gridcolor="rgba(148,163,184,0.2)", secondary_y=False)
    fig_reg.update_yaxes(showgrid=False, secondary_y=True)
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_reg, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Bonus Charts
st.markdown("<br>", unsafe_allow_html=True)
bh, bp = st.columns(2)

with bh:
    fig_hist = px.histogram(
        df, x="Revenue", nbins=30, color_discrete_sequence=["#2563EB"],
        title="💵 Revenue Distribution", marginal="box",
    )
    fig_hist.update_layout(
        **base_layout("💵 Revenue Distribution", 320),
        xaxis=dict(tickprefix="$", gridcolor="rgba(148,163,184,0.2)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.2)"),
        showlegend=False,
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with bp:
    pie_data = df.groupby("Product_Category")["Revenue"].sum().reset_index()
    fig_pie = px.pie(
        pie_data, names="Product_Category", values="Revenue",
        color_discrete_sequence=PALETTE, title="🥧 Revenue Share by Category", hole=0.42,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig_pie.update_layout(
        **base_layout("🥧 Revenue Share by Category", 320),
        legend=dict(orientation="h", y=-0.1),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PART D — BUSINESS INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Part D · Business Insights</div>', unsafe_allow_html=True)

# ① Frequently bought together
if show_pairs:
    st.markdown("#### ① Products Frequently Purchased Together")
    client_prods = df.groupby("Client_ID")["Product_Category"].apply(list)
    pair_counts  = Counter()
    for prods in client_prods:
        for pair in combinations(sorted(set(prods)), 2):
            pair_counts[pair] += 1

    if pair_counts:
        pairs_df = pd.DataFrame(
            [(f"{a}  +  {b}", cnt) for (a, b), cnt in pair_counts.most_common(10)],
            columns=["Product Pair", "Clients Who Bought Both"],
        )
        pc, pt = st.columns([3, 2])
        with pc:
            fig_pairs = px.bar(
                pairs_df.head(6), x="Clients Who Bought Both", y="Product Pair",
                orientation="h", color_discrete_sequence=["#7C3AED"],
                text="Clients Who Bought Both", title="Top Co-Purchased Product Pairs",
            )
            fig_pairs.update_traces(textposition="outside")
            fig_pairs.update_layout(
                **base_layout("Top Co-Purchased Product Pairs", 270),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                showlegend=False,
                margin=dict(l=10, r=50, t=50, b=10),
            )
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.plotly_chart(fig_pairs, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with pt:
            st.dataframe(pairs_df, use_container_width=True, hide_index=True, height=280)
    else:
        st.info("Not enough product variety in current filters to compute pairs.")
    st.markdown("<br>", unsafe_allow_html=True)

# ② Repeat by region
if show_repeat:
    st.markdown("#### ② Repeat Purchases by Region")
    rr = df.groupby("Region").agg(
        Total=("Client_ID", "count"),
        Repeat=("Purchase_Frequency", lambda x: (x > 1).sum()),
    ).reset_index()
    rr["Repeat Rate (%)"] = (rr["Repeat"] / rr["Total"] * 100).round(1)
    rr = rr.sort_values("Repeat Rate (%)", ascending=False)

    rc, rt = st.columns([3, 2])
    with rc:
        fig_rr = px.bar(
            rr, x="Region", y="Repeat Rate (%)",
            color="Repeat Rate (%)", color_continuous_scale="Blues",
            text=rr["Repeat Rate (%)"].apply(lambda v: f"{v}%"),
            title="Repeat Purchase Rate by Region",
        )
        fig_rr.update_traces(textposition="outside")
        fig_rr.update_layout(
            **base_layout("Repeat Purchase Rate by Region", 290),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(148,163,184,0.2)", range=[0, 115]),
            showlegend=False,
            coloraxis_showscale=False,
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_rr, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with rt:
        disp = rr[["Region", "Total", "Repeat", "Repeat Rate (%)"]].copy()
        disp.columns = ["Region", "Total Sales", "Repeat Buyers", "Repeat Rate (%)"]
        st.dataframe(disp, use_container_width=True, hide_index=True, height=300)
    st.markdown("<br>", unsafe_allow_html=True)

# ③ Recommendations vs Revenue
if show_rec:
    st.markdown("#### ③ Are Recommendations Improving Sales?")
    df_r = df.copy()
    df_r["Freq_Bucket"] = pd.cut(
        df_r["Purchase_Frequency"], bins=[0, 2, 5, 10],
        labels=["Low (1–2)", "Med (3–5)", "High (6–10)"],
    )
    rec_agg = df_r.groupby("Freq_Bucket", observed=True).agg(
        Avg_Revenue=("Revenue", "mean"),
        Count=("Client_ID", "count"),
    ).reset_index()
    rec_agg["Avg_Revenue"] = rec_agg["Avg_Revenue"].round(0).astype(int)

    rcc, rci = st.columns([3, 2])
    with rcc:
        fig_rc = px.bar(
            rec_agg, x="Freq_Bucket", y="Avg_Revenue",
            color="Freq_Bucket",
            color_discrete_sequence=["#059669", "#2563EB", "#7C3AED"],
            text=rec_agg["Avg_Revenue"].apply(lambda v: f"${v:,}"),
            title="Avg Revenue by Purchase Frequency Bucket",
            labels={"Freq_Bucket": "Frequency Group", "Avg_Revenue": "Avg Revenue ($)"},
        )
        fig_rc.update_traces(textposition="outside")
        fig_rc.update_layout(
            **base_layout("Avg Revenue by Purchase Frequency Bucket", 290),
            xaxis=dict(showgrid=False),
            yaxis=dict(tickprefix="$", tickformat=",", gridcolor="rgba(148,163,184,0.2)"),
            showlegend=False,
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_rc, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with rci:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<div class="insight-title" style="color:#059669">📊 Key Finding</div>', unsafe_allow_html=True)
        for _, row in rec_agg.iterrows():
            st.markdown(f"**{row['Freq_Bucket']}** → Avg Revenue: **${row['Avg_Revenue']:,}** (n={row['Count']})")
        st.markdown("""
        <div style="margin-top:14px; padding:10px 14px; background:rgba(5,150,105,0.12);
             border-left:4px solid #059669; border-radius:0 8px 8px 0;
             font-size:0.88rem; color:#059669;">
        ✅ Higher purchase frequency = higher average revenue.
        Recommendations are <strong>driving measurable growth</strong>.
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ④ Strategies
if show_strategy:
    st.markdown("#### ④ Recommended Business Strategies")
    rr2 = df.groupby("Region").agg(
        Total=("Client_ID", "count"),
        Repeat=("Purchase_Frequency", lambda x: (x > 1).sum()),
    )
    rr2["rate"] = rr2["Repeat"] / rr2["Total"]
    best_repeat = rr2["rate"].idxmax()

    strategies = [
        {
            "icon": "🚀", "color": "#2563EB",
            "title": f"Expand in '{top_region}' Region",
            "desc": (f"'{top_region}' generates the highest revenue. Increase sales headcount, "
                     "run targeted campaigns, and invest in localized marketing to maximise growth."),
        },
        {
            "icon": "📦", "color": "#7C3AED",
            "title": f"Bundle '{top_category}' with Other Categories",
            "desc": (f"'{top_category}' is the top revenue category. Create cross-sell bundles "
                     "pairing it with slower-moving categories to lift average order value."),
        },
        {
            "icon": "🔁", "color": "#059669",
            "title": f"Scale '{best_repeat}' Retention Playbook",
            "desc": (f"'{best_repeat}' has the highest repeat-purchase rate. Document what's "
                     "working — loyalty programs, follow-up cadence, account management — and replicate it."),
        },
    ]
    s1, s2, s3 = st.columns(3)
    for col, s in zip([s1, s2, s3], strategies):
        with col:
            st.markdown(f"""
            <div class="insight-card" style="border-top:4px solid {s['color']}; min-height:200px;">
                <div class="insight-title" style="color:{s['color']}; font-size:1.05rem;">
                    {s['icon']} {s['title']}
                </div>
                <div class="insight-body">
                    {s['desc']}
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RAW DATA EXPLORER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗂️ Raw Data Explorer", expanded=False):
    search = st.text_input("🔍 Search by Client ID or Region", "")
    view_df = df.copy()
    if search:
        mask = (
            view_df["Client_ID"].astype(str).str.contains(search, case=False) |
            view_df["Region"].str.contains(search, case=False)
        )
        view_df = view_df[mask]
    st.dataframe(
        view_df[["Client_ID", "Product_ID", "Product_Category",
                 "Region", "Purchase_Frequency", "Revenue", "Last_Purchase_Date"]]
          .sort_values("Revenue", ascending=False)
          .reset_index(drop=True),
        use_container_width=True, height=380,
    )
    st.download_button(
        "⬇️ Download Filtered CSV",
        view_df.to_csv(index=False).encode("utf-8"),
        "filtered_data.csv", "text/csv",
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.82rem; color:#64748b;'>"
    "B2B Sales Intelligence Dashboard · Part C &amp; D · Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True,
)
