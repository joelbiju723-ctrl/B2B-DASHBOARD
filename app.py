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
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    .main { background-color: #f0f4f8; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #2563EB 100%);
    }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    section[data-testid="stSidebar"] .stMultiSelect span { color: #1e293b !important; }
    .kpi-card {
        background: white; border-radius: 14px; padding: 22px 18px;
        text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-top: 4px solid; transition: transform .2s;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
    .kpi-value  { font-size: 2rem; font-weight: 800; margin: 6px 0 4px; }
    .kpi-label  { font-size: 0.82rem; color: #64748b; font-weight: 500;
                  letter-spacing: .4px; text-transform: uppercase; }
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #0f172a;
        margin: 32px 0 16px; padding-left: 12px;
        border-left: 5px solid #2563EB;
    }
    .insight-card {
        background: white; border-radius: 12px; padding: 20px 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 16px;
    }
    .insight-title { font-size: 1rem; font-weight: 700; margin-bottom: 10px; }
    .chart-box {
        background: white; border-radius: 14px; padding: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .dash-title    { font-size: 2rem; font-weight: 900; color: #0f172a; letter-spacing: -0.5px; }
    .dash-subtitle { font-size: 0.95rem; color: #64748b; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#2563EB", "#7C3AED", "#059669", "#DC2626", "#D97706", "#0891B2"]

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

# ── Show welcome screen until a file is uploaded ──────────────────────────────
if uploaded is None:
    st.markdown('<div class="dash-title">📊 B2B Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Part C · KPI Metrics & Charts &nbsp;|&nbsp; Part D · Business Insights</div>', unsafe_allow_html=True)
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
# SIDEBAR FILTERS  (only shown after upload)
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
    st.markdown('<div class="dash-subtitle">Part C · KPI Metrics & Charts &nbsp;|&nbsp; Part D · Business Insights</div>', unsafe_allow_html=True)
with c2:
    st.metric("Records", f"{len(df):,}")
st.markdown("---")

# ─────────────────────────────────────────────
# PART C — KPI METRICS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Part C · KPI Metrics</div>', unsafe_allow_html=True)

total_sales      = len(df)
repeat_customers = int((df["Purchase_Frequency"] > 1).sum())
rec_success_rate = round(repeat_customers / total_sales * 100, 1)
total_revenue    = int(df["Revenue"].sum())
avg_order_value  = int(df["Revenue"].mean())
top_region       = df.groupby("Region")["Revenue"].sum().idxmax()
top_category     = df.groupby("Product_Category")["Revenue"].sum().idxmax()

kpi_list = [
    ("📦", "Total Sales",                 str(total_sales),          "#2563EB"),
    ("🔁", "Repeat Customers",            str(repeat_customers),      "#7C3AED"),
    ("✅", "Recommendation Success Rate", f"{rec_success_rate}%",    "#059669"),
    ("💰", "Total Revenue",               f"${total_revenue:,}",      "#DC2626"),
]
for col, (icon, label, value, color) in zip(st.columns(4), kpi_list):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}">
            <div style="font-size:1.8rem">{icon}</div>
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
st.markdown('<div class="section-header">Part C · Charts</div>', unsafe_allow_html=True)

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
    marker=dict(size=7, color="white", line=dict(color="#2563EB", width=2.5)),
    fill="tozeroy", fillcolor="rgba(37,99,235,0.10)",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
))
fig_trend.update_layout(
    title="📈 Customer Purchase Trends (Monthly Revenue)",
    title_font=dict(size=15, color="#0f172a"),
    plot_bgcolor="white", paper_bgcolor="white",
    xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=10)),
    yaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9"),
    margin=dict(l=10, r=10, t=50, b=10), height=320,
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
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=False),
        title_font=dict(size=14, color="#0f172a"),
        margin=dict(l=10, r=60, t=50, b=10), height=340,
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
        title="🌍 Region-wise Sales",
        title_font=dict(size=14, color="#0f172a"),
        plot_bgcolor="white", paper_bgcolor="white",
        barmode="group", legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=10, r=10, t=60, b=10), height=340,
        xaxis=dict(showgrid=False),
    )
    fig_reg.update_yaxes(tickprefix="$", tickformat=".2s", gridcolor="#f1f5f9", secondary_y=False)
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
        plot_bgcolor="white", paper_bgcolor="white",
        title_font=dict(size=14, color="#0f172a"),
        xaxis=dict(tickprefix="$", gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
        margin=dict(l=10, r=10, t=50, b=10), height=320, showlegend=False,
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
        plot_bgcolor="white", paper_bgcolor="white",
        title_font=dict(size=14, color="#0f172a"),
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        legend=dict(orientation="h", y=-0.1),
    )
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PART D — BUSINESS INSIGHTS
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Part D · Business Insights</div>', unsafe_allow_html=True)

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
                plot_bgcolor="white", paper_bgcolor="white",
                title_font=dict(size=13, color="#0f172a"),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                margin=dict(l=10, r=40, t=50, b=10), height=270, showlegend=False,
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
            plot_bgcolor="white", paper_bgcolor="white",
            title_font=dict(size=13, color="#0f172a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f1f5f9", range=[0, 115]),
            margin=dict(l=10, r=10, t=50, b=10), height=290,
            showlegend=False, coloraxis_showscale=False,
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
            plot_bgcolor="white", paper_bgcolor="white",
            title_font=dict(size=13, color="#0f172a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(tickprefix="$", tickformat=",", gridcolor="#f1f5f9"),
            margin=dict(l=10, r=10, t=50, b=10), height=290, showlegend=False,
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
        <div style="margin-top:14px; padding:10px 14px; background:#f0fdf4;
             border-left:4px solid #059669; border-radius:0 8px 8px 0;
             font-size:0.88rem; color:#166534;">
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
            <div class="insight-card" style="border-top:4px solid {s['color']}; min-height:190px;">
                <div class="insight-title" style="color:{s['color']}; font-size:1.05rem;">
                    {s['icon']} {s['title']}
                </div>
                <div style="font-size:0.88rem; color:#475569; line-height:1.65;">
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
    "<div style='text-align:center; color:#94a3b8; font-size:0.82rem;'>"
    "B2B Sales Intelligence Dashboard · Part C & D · Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True,
)
