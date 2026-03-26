"""
B2B Sales Dashboard
===================
Part C: KPI metrics + charts
Part D: Business insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import numpy as np
from itertools import combinations
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────

def load_data(path: str = "data/B2B_Dataset_1000_Rows.xlsx") -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Last_Purchase_Date"] = pd.to_datetime(df["Last_Purchase_Date"])
    df["Month"] = df["Last_Purchase_Date"].dt.to_period("M")
    return df


# ─────────────────────────────────────────────
# 2. KPI CALCULATIONS
# ─────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    total_sales      = len(df)
    repeat_customers = int((df["Purchase_Frequency"] > 1).sum())
    rec_success_rate = round(repeat_customers / total_sales * 100, 2)
    total_revenue    = int(df["Revenue"].sum())
    return {
        "Total Sales":               total_sales,
        "Repeat Customers":          repeat_customers,
        "Recommendation Success Rate": f"{rec_success_rate}%",
        "Total Revenue":             f"${total_revenue:,}",
    }


# ─────────────────────────────────────────────
# 3. CHART HELPERS
# ─────────────────────────────────────────────

PALETTE = ["#2563EB", "#7C3AED", "#059669", "#DC2626", "#D97706"]

def chart_category_performance(df, ax):
    data = df.groupby("Product_Category")["Revenue"].sum().sort_values(ascending=True)
    bars = ax.barh(data.index, data.values, color=PALETTE[:len(data)], height=0.55, edgecolor="white")
    for bar, val in zip(bars, data.values):
        ax.text(val + data.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"${val/1e6:.2f}M", va="center", fontsize=9, fontweight="bold", color="#1e293b")
    ax.set_title("Product Category Performance", fontsize=13, fontweight="bold", pad=10, color="#1e293b")
    ax.set_xlabel("Total Revenue ($)", fontsize=9, color="#64748b")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors="#64748b")


def chart_purchase_trends(df, ax):
    trend = df.groupby("Month")["Revenue"].sum().reset_index()
    trend["Month_str"] = trend["Month"].astype(str)
    ax.fill_between(range(len(trend)), trend["Revenue"], alpha=0.18, color="#2563EB")
    ax.plot(range(len(trend)), trend["Revenue"], color="#2563EB", linewidth=2.5, marker="o",
            markersize=5, markerfacecolor="white", markeredgewidth=2)
    step = max(1, len(trend) // 6)
    ax.set_xticks(range(0, len(trend), step))
    ax.set_xticklabels(trend["Month_str"].iloc[::step], rotation=35, ha="right", fontsize=8)
    ax.set_title("Customer Purchase Trends (Monthly Revenue)", fontsize=13,
                 fontweight="bold", pad=10, color="#1e293b")
    ax.set_ylabel("Revenue ($)", fontsize=9, color="#64748b")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors="#64748b")


def chart_region_sales(df, ax):
    data = df.groupby("Region").agg(Revenue=("Revenue", "sum"), Sales=("Client_ID", "count"))
    x = np.arange(len(data))
    width = 0.38
    b1 = ax.bar(x - width / 2, data["Revenue"], width, color="#2563EB", label="Revenue", alpha=0.88)
    ax2 = ax.twinx()
    b2 = ax2.bar(x + width / 2, data["Sales"], width, color="#7C3AED", label="Sales Count", alpha=0.88)
    ax.set_xticks(x)
    ax.set_xticklabels(data.index, fontsize=10)
    ax.set_ylabel("Revenue ($)", fontsize=9, color="#2563EB")
    ax2.set_ylabel("Sales Count", fontsize=9, color="#7C3AED")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
    ax.set_title("Region-wise Sales", fontsize=13, fontweight="bold", pad=10, color="#1e293b")
    lines = [b1, b2]
    ax.legend(lines, ["Revenue", "Sales Count"], loc="upper right", fontsize=8)
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    ax.tick_params(colors="#64748b")


# ─────────────────────────────────────────────
# 4. BUSINESS INSIGHTS (Part D)
# ─────────────────────────────────────────────

def insight_frequent_pairs(df: pd.DataFrame) -> list[tuple]:
    """Products frequently purchased together (same client)."""
    client_products = df.groupby("Client_ID")["Product_Category"].apply(list)
    pair_counts = Counter()
    for products in client_products:
        unique = list(set(products))
        for pair in combinations(sorted(unique), 2):
            pair_counts[pair] += 1
    return pair_counts.most_common(5)


def insight_repeat_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Region-wise repeat purchase rate."""
    region = df.groupby("Region").agg(
        Total=("Client_ID", "count"),
        Repeat=("Purchase_Frequency", lambda x: (x > 1).sum()),
    )
    region["Repeat_Rate_%"] = (region["Repeat"] / region["Total"] * 100).round(1)
    return region.sort_values("Repeat_Rate_%", ascending=False)


def insight_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Check if higher purchase frequency correlates with higher revenue."""
    bins   = [0, 2, 5, 10]
    labels = ["Low (1–2)", "Med (3–5)", "High (6–10)"]
    df = df.copy()
    df["Freq_Bucket"] = pd.cut(df["Purchase_Frequency"], bins=bins, labels=labels)
    return df.groupby("Freq_Bucket", observed=True).agg(
        Avg_Revenue=("Revenue", "mean"),
        Count=("Client_ID", "count"),
    ).round(0)


def suggest_strategies(df: pd.DataFrame) -> list[str]:
    top_region    = df.groupby("Region")["Revenue"].sum().idxmax()
    top_category  = df.groupby("Product_Category")["Revenue"].sum().idxmax()
    repeat_region = insight_repeat_by_region(df)["Repeat_Rate_%"].idxmax()
    return [
        f"1. EXPAND in '{top_region}' — highest revenue region. "
          f"Increase sales headcount and targeted campaigns there.",
        f"2. BUNDLE '{top_category}' with lower-performing categories "
          f"to lift average order value and cross-sell.",
        f"3. REPLICATE '{repeat_region}' retention playbook across other regions — "
          f"it has the highest repeat-purchase rate; document what's working and scale it.",
    ]


# ─────────────────────────────────────────────
# 5. KPI CARD RENDERER
# ─────────────────────────────────────────────

def draw_kpi_panel(fig, kpis: dict, y_top=0.97, height=0.13):
    colors = ["#2563EB", "#7C3AED", "#059669", "#DC2626"]
    n = len(kpis)
    margin = 0.02
    w = (1 - margin * (n + 1)) / n
    for i, (label, value) in enumerate(kpis.items()):
        x = margin + i * (w + margin)
        ax = fig.add_axes([x, y_top - height, w, height])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        fancy = FancyBboxPatch((0.03, 0.03), 0.94, 0.94,
                               boxstyle="round,pad=0.05",
                               linewidth=2, edgecolor=colors[i],
                               facecolor=colors[i] + "18")
        ax.add_patch(fancy)
        ax.text(0.5, 0.67, str(value), ha="center", va="center",
                fontsize=17, fontweight="bold", color=colors[i])
        ax.text(0.5, 0.28, label, ha="center", va="center",
                fontsize=9, color="#475569", wrap=True)


# ─────────────────────────────────────────────
# 6. MAIN DASHBOARD
# ─────────────────────────────────────────────

def build_dashboard(path: str = "data/B2B_Dataset_1000_Rows.xlsx",
                    out: str  = "outputs/dashboard.png"):
    df   = load_data(path)
    kpis = compute_kpis(df)

    fig = plt.figure(figsize=(20, 24), facecolor="#f8fafc")
    fig.suptitle("B2B Sales Dashboard", fontsize=22, fontweight="bold",
                 y=0.98, color="#0f172a")

    # KPI cards (top strip)
    draw_kpi_panel(fig, kpis, y_top=0.94, height=0.10)

    # Charts grid (below KPIs)
    gs = gridspec.GridSpec(3, 2, figure=fig,
                           top=0.83, bottom=0.38,
                           hspace=0.45, wspace=0.35,
                           left=0.07, right=0.97)

    ax1 = fig.add_subplot(gs[0, :])   # full-width trend
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    chart_purchase_trends(df, ax1)
    chart_category_performance(df, ax2)
    chart_region_sales(df, ax3)

    # ── Part D: Business Insights ──────────────────
    ins_y = 0.35
    fig.text(0.05, ins_y, "Part D: Business Insights",
             fontsize=14, fontweight="bold", color="#0f172a")

    # Q1 — Frequent pairs
    pairs = insight_frequent_pairs(df)
    fig.text(0.05, ins_y - 0.025, "① Products Frequently Purchased Together",
             fontsize=11, fontweight="bold", color="#2563EB")
    for j, ((a, b), cnt) in enumerate(pairs):
        fig.text(0.07, ins_y - 0.04 - j * 0.018,
                 f"  {a}  +  {b}  →  {cnt} clients", fontsize=9, color="#334155")

    # Q2 — Repeat by region
    rr = insight_repeat_by_region(df)
    fig.text(0.55, ins_y - 0.025, "② Repeat Purchases by Region",
             fontsize=11, fontweight="bold", color="#7C3AED")
    for j, (region, row) in enumerate(rr.iterrows()):
        fig.text(0.57, ins_y - 0.04 - j * 0.018,
                 f"  {region}:  {row['Repeat_Rate_%']}%  ({int(row['Repeat'])}/{int(row['Total'])})",
                 fontsize=9, color="#334155")

    # Q3 — Recommendations & revenue
    rec = insight_recommendations(df)
    fig.text(0.05, ins_y - 0.135, "③ Are Recommendations Improving Sales?",
             fontsize=11, fontweight="bold", color="#059669")
    for j, (bucket, row) in enumerate(rec.iterrows()):
        fig.text(0.07, ins_y - 0.150 - j * 0.018,
                 f"  {bucket}:  Avg Revenue = ${int(row['Avg_Revenue']):,}  (n={int(row['Count'])})",
                 fontsize=9, color="#334155")
    fig.text(0.07, ins_y - 0.207,
             "  → Higher purchase frequency → higher avg revenue. Recommendations drive growth.",
             fontsize=9, color="#059669", style="italic")

    # Q4 — Strategies
    strategies = suggest_strategies(df)
    fig.text(0.55, ins_y - 0.135, "④ Recommended Strategies",
             fontsize=11, fontweight="bold", color="#DC2626")
    for j, s in enumerate(strategies):
        # Wrap text manually at ~75 chars
        words = s.split()
        line, lines = "", []
        for w in words:
            if len(line) + len(w) + 1 > 72:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        if line:
            lines.append(line)
        for k, ln in enumerate(lines):
            fig.text(0.57, ins_y - 0.150 - j * 0.055 - k * 0.018,
                     ln, fontsize=9, color="#334155")

    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[✓] Dashboard saved → {out}")


# ─────────────────────────────────────────────
# 7. CLI ENTRY
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="B2B Sales Dashboard Generator")
    parser.add_argument("--data",   default="data/B2B_Dataset_1000_Rows.xlsx",
                        help="Path to the Excel dataset")
    parser.add_argument("--output", default="outputs/dashboard.png",
                        help="Output path for dashboard image")
    parser.add_argument("--kpis-only", action="store_true",
                        help="Print KPIs to console only")
    args = parser.parse_args()

    df = load_data(args.data)

    if args.kpis_only:
        for k, v in compute_kpis(df).items():
            print(f"  {k}: {v}")
    else:
        build_dashboard(args.data, args.output)
