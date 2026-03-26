"""
B2B Sales Intelligence Dashboard
==================================
Interactive Streamlit App — Part C (KPIs + Charts) & Part D (Business Insights)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from itertools import combinations
from collections import Counter

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Global font */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

    /* Main background */
    .main { background-color: #f0f4f8; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #2563EB 100%);
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stMultiSelect span { color: #1e293b !important; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-top: 4px solid;
        transition: transform .2s;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
    .kpi-value { font-size: 2rem; font-weight: 800; margin: 6px 0 4px; }
    .kpi-label { font-size: 0.82rem; color: #64748b; font-weight: 500; letter-spacing: .4px; text-transform: uppercase; }

    /* Section headers */
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #0f172a;
        margin: 32px 0 16px; padding-left: 12px;
        border-left: 5px solid #2563EB;
    }

    /* Insight cards */
    .insight-card {
        background: white; border-radius: 12px; padding: 20px 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 16px;
    }
    .insight-title { font-size: 1rem; font-weight: 700; margin-bottom: 10px; }
    .strategy-item {
        background: #f8fafc; border-left: 4px solid #2563EB;
        padding: 10px 14px; border-radius: 0 8px 8px 0;
        margin: 8px 0; font-size: 0.9rem; color: #334155;
    }

    /* Chart containers */
    .chart-box {
        background: white; border-radius: 14px; padding: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }

    /* Dashboard title */
    .dash-title {
        font-size: 2rem; font-weight: 900; color: #0f172a;
        letter-spacing: -0.5px;
    }
    .dash-subtitle { font-size: 0.95rem; color: #64748b; margin-top: 2px; }

    /* Streamlit element tweaks */
    div[data-testid="stMetric"] { background: white; border-radius: 10px; padding: 12px; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    div.stButton > button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Last_Purchase_Date"] = pd.to_datetime(df["Last_Purchase_Date"])
    df["Month"] = df["Last_Purchase_Date"].dt.to_period("M")
    df["Month_str"] = df["Last_Purchase_Date"].dt.strftime("%b %Y")
    df["Year"] = df["Last_Purchase_Date"].dt.year
    return df


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔧 Dashboard Filters")
    st.markdown("---")

    uploaded = st.file_uploader("📂 Upload Dataset (.xlsx)", type=["xlsx"])
    if uploaded:
        df_raw = load_data(uploaded)
    else:
        try:
            df_raw = load_data("data/B2B_Dataset_1000_Rows.xlsx")
        except Exception:
            st.error("⚠️ Place your dataset at `data/B2B_Dataset_1000_Rows.xlsx` or upload it above.")
            st.stop()

    st.markdown("### 🌍 Region")
    all_regions = sorted(df_raw["Region"].unique())
    sel_regions = st.multiselect("Select Region(s)", all_regions, default=all_regions)

    st.markdown("### 📦 Product Category")
    all_cats = sorted(df_raw["Product_Category"].unique())
    sel_cats = st.multiselect("Select Category(ies)", all_cats, default=all_cats)

    st.markdown("### 📅 Purchase Frequency")
    freq_min, freq_max = int(df_raw["Purchase_Frequency"].min()), int(df_raw["Purchase_Frequency"].max())
    sel_freq = st.slider("Frequency Range", freq_min, freq_max, (freq_min, freq_max))

    st.markdown("### 💰 Revenue Range")
    rev_min, rev_max = int(df_raw["Revenue"].min()), int(df_raw["Revenue"].max())
    sel_rev = st.slider("Revenue ($)", rev_min, rev_max, (rev_min, rev_max))

    st.markdown("---")
    st.markdown("### 📊 Part D Insights")
    show_pairs    = st.checkbox("Products Bought Together", value=True)
    show_repeat   = st.checkbox("Repeat Purchases by Region", value=True)
    show_rec      = st.checkbox("Recommendations vs Revenue", value=True)
    show_strategy = st.checkbox("Suggested Strategies", value=True)

    st.markdown("---")
    st.caption("B2B Sales Dashboard · Part C & D")

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
df = df_raw.copy()
if sel_regions:
    df = df[df["Region"].isin(sel_regions)]
if sel_cats:
    df = df[df["Product_Category"].isin(sel_cats)]
df = df[(df["Purchase_Frequency"] >= sel_freq[0]) & (df["Purchase_Frequency"] <= sel_freq[1])]
df = df[(df["Revenue"] >= sel_rev[0]) & (df["Revenue"] <= sel_rev[1])]

if df.empty:
    st.warning("⚠️ No data matches your filters. Please adjust the sidebar selections.")
    st.stop()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_title, col_rows = st.columns([5, 1])
with col_title:
    st.markdown('<div class="dash-title">📊 B2B Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Product Recommendation & Sales Analytics · Part C + Part D</div>', unsafe_allow_html=True)
with col_rows:
    st.metric("Records", f"{len(df):,}")

st.markdown("---")

# ─────────────────────────────────────────────
# PART C — KPI METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Part C · KPI Metrics</div>', unsafe_allow_html=True)

total_sales       = len(df)
repeat_customers  = int((df["Purchase_Frequency"] > 1).sum())
rec_success_rate  = round(repeat_customers / total_sales * 100, 1) if total_sales else 0
total_revenue     = int(df["Revenue"].sum())
avg_order_value   = int(df["Revenue"].mean()) if total_sales else 0

kpi_colors = ["#2563EB", "#7C3AED", "#059669", "#DC2626"]
kpi_data = [
    ("📦", "Total Sales",                str(total_sales),           kpi_colors[0]),
    ("🔁", "Repeat Customers",           str(repeat_customers),       kpi_colors[1]),
    ("✅", "Recommendation Success Rate", f"{rec_success_rate}%",     kpi_colors[2]),
    ("💰", "Total Revenue",              f"${total_revenue:,}",       kpi_colors[3]),
]

k1, k2, k3, k4 = st.columns(4)
for col, (icon, label, value, color) in zip([k1, k2, k3, k4], kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div style="font-size:1.8rem">{icon}</div>
            <div class="kpi-value" style="color:{color}">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Avg order + top region mini row
m1, m2, m3 = st.columns(3)
top_region   = df.groupby("Region")["Revenue"].sum().idxmax()
top_category = df.groupby("Product_Category")["Revenue"].sum().idxmax()
m1.metric("💵 Avg Order Value",  f"${avg_order_value:,}")
m2.metric("🏆 Top Region",       top_region)
m3.metric("🥇 Top Category",     top_category)

# ─────────────────────────────────────────────
# PART C — CHARTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Part C · Charts</div>', unsafe_allow_html=True)

PALETTE = ["#2563EB", "#7C3AED", "#059669", "#DC2626", "#D97706", "#0891B2"]

# --- Chart 1: Purchase Trends (full width) ---
trend = (df.groupby(df["Last_Purchase_Date"].dt.to_period("M"))["Revenue"]
           .sum()
           .reset_index())
trend["Month_str"] = trend["Last_Purchase_Date"].astype(str)
trend = trend.sort_values("Last_Purchase_Date")

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["Month_str"], y=trend["Revenue"],
    mode="lines+markers",
    line=dict(color="#2563EB", width=3),
    marker=dict(size=7, color="white", line=dict(color="#2563EB", width=2.5)),
    fill="tozeroy", fillcolor="rgba(37,99,235,0.10)",
    name="Monthly Revenue",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"
))
fig_trend.update_layout(
    title="📈 Customer Purchase Trends (Monthly Revenue)",
    title_font=dict(size=15, color="#0f172a"),
    plot_bgcolor="white", paper_bgcolor="white",
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=10)),
    yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9"),
    margin=dict(l=10, r=10, t=50, b=10),
    height=320,
)
st.markdown('<div class="chart-box">', unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts 2 & 3 side by side ---
col_left, col_right = st.columns(2)

with col_left:
    cat_perf = df.groupby("Product_Category")["Revenue"].sum().reset_index().sort_values("Revenue")
    fig_cat = px.bar(
        cat_perf, x="Revenue", y="Product_Category", orientation="h",
        color="Product_Category", color_discrete_sequence=PALETTE,
        text=cat_perf["Revenue"].apply(lambda v: f"${v/1e6:.2f}M"),
        title="📦 Product Category Performance",
    )
    fig_cat.update_traces(textposition="outside", marker_line_width=0)
    fig_cat.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=False),
        title_font=dict(size=14, color="#0f172a"),
        margin=dict(l=10, r=60, t=50, b=10), height=340,
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    region_data = df.groupby("Region").agg(
        Revenue=("Revenue", "sum"),
        Sales=("Client_ID", "count")
    ).reset_index()

    fig_region = make_subplots(specs=[[{"secondary_y": True}]])
    fig_region.add_trace(go.Bar(
        x=region_data["Region"], y=region_data["Revenue"],
        name="Revenue", marker_color="#2563EB", opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"
    ), secondary_y=False)
    fig_region.add_trace(go.Bar(
        x=region_data["Region"], y=region_data["Sales"],
        name="Sales Count", marker_color="#7C3AED", opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Sales: %{y}<extra></extra>"
    ), secondary_y=True)
    fig_region.update_layout(
        title="🌍 Region-wise Sales",
        title_font=dict(size=14, color="#0f172a"),
        plot_bgcolor="white", paper_bgcolor="white",
        barmode="group", legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=10, r=10, t=60, b=10), height=340,
        xaxis=dict(showgrid=False),
    )
    fig_region.update_yaxes(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9", secondary_y=False)
    fig_region.update_yaxes(showgrid=False, secondary_y=True)
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_region, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Bonus: Revenue distribution
st.markdown("<br>", unsafe_allow_html=True)
col_hist, col_pie = st.columns(2)

with col_hist:
    fig_hist = px.histogram(
        df, x="Revenue", nbins=30, color_discrete_sequence=["#2563EB"],
        title="💵 Revenue Distribution",
        marginal="box",
    )
    fig_hist.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        title_font=dict(size=14, color="#0f172a"),
        xaxis=dict(tickprefix="$", gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        showlegend=False,
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_pie:
    pie_data = df.groupby("Product_Category")["Revenue"].sum().reset_index()
    fig_pie = px.pie(
        pie_data, names="Product_Category", values="Revenue",
        color_discrete_sequence=PALETTE,
        title="🥧 Revenue Share by Category",
        hole=0.42,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
    )
    fig_pie.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        title_font=dict(size=14, color="#0f172a"),
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PART D — BUSINESS INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Part D · Business Insights</div>', unsafe_allow_html=True)

# ── Q1: Frequently purchased together ──────────────
if show_pairs:
    st.markdown("#### ① Products Frequently Purchased Together")
    client_products = df.groupby("Client_ID")["Product_Category"].apply(list)
    pair_counts = Counter()
    for products in client_products:
        unique = list(set(products))
        for pair in combinations(sorted(unique), 2):
            pair_counts[pair] += 1

    if pair_counts:
        pairs_df = pd.DataFrame(
            [(f"{a}  +  {b}", cnt) for (a, b), cnt in pair_counts.most_common(10)],
            columns=["Product Pair", "Clients Who Bought Both"]
        )
        col_pairs_chart, col_pairs_table = st.columns([3, 2])
        with col_pairs_chart:
            fig_pairs = px.bar(
                pairs_df.head(5), x="Clients Who Bought Both", y="Product Pair",
                orientation="h", color_discrete_sequence=["#7C3AED"],
                text="Clients Who Bought Both",
                title="Top Product Pairs",
            )
            fig_pairs.update_traces(textposition="outside")
            fig_pairs.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                title_font=dict(size=13, color="#0f172a"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                margin=dict(l=10, r=40, t=50, b=10), height=260,
                showlegend=False,
            )
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.plotly_chart(fig_pairs, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_pairs_table:
            st.dataframe(pairs_df, use_container_width=True, hide_index=True, height=270)
    else:
        st.info("Not enough data to find product pairs with current filters.")

    st.markdown("<br>", unsafe_allow_html=True)

# ── Q2: Repeat purchases by region ─────────────────
if show_repeat:
    st.markdown("#### ② Repeat Purchases by Region")
    region_repeat = df.groupby("Region").agg(
        Total=("Client_ID", "count"),
        Repeat=("Purchase_Frequency", lambda x: (x > 1).sum()),
    ).reset_index()
    region_repeat["Repeat Rate (%)"] = (region_repeat["Repeat"] / region_repeat["Total"] * 100).round(1)
    region_repeat = region_repeat.sort_values("Repeat Rate (%)", ascending=False)

    col_rep_chart, col_rep_table = st.columns([3, 2])
    with col_rep_chart:
        fig_rep = px.bar(
            region_repeat, x="Region", y="Repeat Rate (%)",
            color="Repeat Rate (%)", color_continuous_scale="Blues",
            text=region_repeat["Repeat Rate (%)"].apply(lambda v: f"{v}%"),
            title="Repeat Purchase Rate by Region",
        )
        fig_rep.update_traces(textposition="outside")
        fig_rep.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            title_font=dict(size=13, color="#0f172a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 110]),
            margin=dict(l=10, r=10, t=50, b=10), height=280,
            showlegend=False, coloraxis_showscale=False,
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_rep, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_rep_table:
        display_rr = region_repeat[["Region", "Total", "Repeat", "Repeat Rate (%)"]].copy()
        display_rr.columns = ["Region", "Total Sales", "Repeat Buyers", "Repeat Rate (%)"]
        st.dataframe(display_rr, use_container_width=True, hide_index=True, height=290)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Q3: Are recommendations improving sales? ───────
if show_rec:
    st.markdown("#### ③ Are Recommendations Improving Sales?")
    df_rec = df.copy()
    bins   = [0, 2, 5, 10]
    labels = ["Low (1–2)", "Med (3–5)", "High (6–10)"]
    df_rec["Freq_Bucket"] = pd.cut(df_rec["Purchase_Frequency"], bins=bins, labels=labels)
    rec_agg = df_rec.groupby("Freq_Bucket", observed=True).agg(
        Avg_Revenue=("Revenue", "mean"),
        Count=("Client_ID", "count"),
    ).reset_index()
    rec_agg["Avg_Revenue"] = rec_agg["Avg_Revenue"].round(0).astype(int)

    col_rec_chart, col_rec_insight = st.columns([3, 2])
    with col_rec_chart:
        fig_rec = px.bar(
            rec_agg, x="Freq_Bucket", y="Avg_Revenue",
            color="Freq_Bucket",
            color_discrete_sequence=["#059669", "#2563EB", "#7C3AED"],
            text=rec_agg["Avg_Revenue"].apply(lambda v: f"${v:,}"),
            title="Avg Revenue by Purchase Frequency",
            labels={"Freq_Bucket": "Frequency Group", "Avg_Revenue": "Avg Revenue ($)"},
        )
        fig_rec.update_traces(textposition="outside")
        fig_rec.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            title_font=dict(size=13, color="#0f172a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(tickprefix="$", tickformat=",", gridcolor="#f1f5f9"),
            margin=dict(l=10, r=10, t=50, b=10), height=280,
            showlegend=False,
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_rec, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_rec_insight:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<div class="insight-title" style="color:#059669">📊 Key Finding</div>', unsafe_allow_html=True)
        for _, row in rec_agg.iterrows():
            st.markdown(f"**{row['Freq_Bucket']}** &nbsp;→&nbsp; Avg Revenue: **${row['Avg_Revenue']:,}** &nbsp;(n={row['Count']})")
        st.markdown("""
        <div style="margin-top:14px; padding:10px 14px; background:#f0fdf4;
             border-left:4px solid #059669; border-radius:0 8px 8px 0;
             font-size:0.88rem; color:#166534;">
        ✅ Higher purchase frequency correlates with higher average revenue.
        Product recommendations are <strong>driving growth</strong>.
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Q4: Suggested Strategies ───────────────────────
if show_strategy:
    st.markdown("#### ④ Recommended Business Strategies")

    top_region_s   = df.groupby("Region")["Revenue"].sum().idxmax()
    top_category_s = df.groupby("Product_Category")["Revenue"].sum().idxmax()
    region_rep2 = df.groupby("Region").agg(
        Total=("Client_ID", "count"),
        Repeat=("Purchase_Frequency", lambda x: (x > 1).sum()),
    )
    region_rep2["rate"] = region_rep2["Repeat"] / region_rep2["Total"]
    best_repeat_region = region_rep2["rate"].idxmax()

    strategies = [
        {
            "icon": "🚀",
            "title": f"Expand in '{top_region_s}' Region",
            "desc": f"'{top_region_s}' is the highest revenue-generating region. "
                    f"Increase sales headcount, run targeted campaigns, and invest "
                    f"in localized marketing to maximise growth potential.",
            "color": "#2563EB",
        },
        {
            "icon": "📦",
            "title": f"Bundle '{top_category_s}' with Lower-Performing Categories",
            "desc": f"'{top_category_s}' is the top revenue category. "
                    f"Create cross-sell bundles pairing it with slower categories "
                    f"to lift average order value and drive volume.",
            "color": "#7C3AED",
        },
        {
            "icon": "🔁",
            "title": f"Replicate '{best_repeat_region}' Retention Playbook",
            "desc": f"'{best_repeat_region}' has the highest repeat-purchase rate. "
                    f"Document what's working there — loyalty programs, follow-up cadence, "
                    f"account management — and roll it out across all regions.",
            "color": "#059669",
        },
    ]

    s1, s2, s3 = st.columns(3)
    for col, s in zip([s1, s2, s3], strategies):
        with col:
            st.markdown(f"""
            <div class="insight-card" style="border-top: 4px solid {s['color']}; min-height:200px;">
                <div class="insight-title" style="color:{s['color']}; font-size:1.05rem;">
                    {s['icon']} {s['title']}
                </div>
                <div style="font-size:0.88rem; color:#475569; line-height:1.6;">
                    {s['desc']}
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RAW DATA EXPLORER (collapsible)
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗂️ Raw Data Explorer", expanded=False):
    search = st.text_input("🔍 Search Client ID or Region", "")
    display_df = df.copy()
    if search:
        mask = (
            display_df["Client_ID"].astype(str).str.contains(search, case=False) |
            display_df["Region"].str.contains(search, case=False)
        )
        display_df = display_df[mask]

    st.dataframe(
        display_df[["Client_ID", "Product_ID", "Product_Category",
                     "Region", "Purchase_Frequency", "Revenue", "Last_Purchase_Date"]]
          .sort_values("Revenue", ascending=False)
          .reset_index(drop=True),
        use_container_width=True,
        height=380,
    )
    col_dl1, col_dl2 = st.columns([1, 5])
    with col_dl1:
        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.82rem;'>"
    "B2B Sales Intelligence Dashboard · Part C & D · Built with Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True
)
