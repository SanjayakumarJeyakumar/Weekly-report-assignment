"""Visualization and Executive Reporting Generator (Part D).

Queries live Supabase PostgreSQL tables using verified SQL logic,
generates publication-quality charts in charts/, and outputs executive deliverables.
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from sqlalchemy import text

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_engine

CHARTS_DIR = PROJECT_ROOT / "charts"
REPORT_DIR = PROJECT_ROOT / "report"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Styling configuration
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def generate_chart_1_revenue_trend(conn) -> Path:
    """Generate Chart 1: Monthly GMV trend with phase flags and MoM growth."""
    print("Generating Chart 1: Monthly Revenue Trend...")
    sql_path = PROJECT_ROOT / "sql" / "04_monthly_revenue.sql"
    df = pd.read_sql(text(sql_path.read_text(encoding="utf-8")), conn)

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

    # Color palette based on period flag
    colors = []
    for flag in df["month_period_flag"]:
        if flag == "LAUNCH_PILOT":
            colors.append("#7fb3d5")
        elif flag == "ZERO_REVENUE":
            colors.append("#e74c3c")
        elif flag == "RAMP_UP":
            colors.append("#f39c12")
        elif flag == "PARTIAL_TAIL":
            colors.append("#95a5a6")
        else:
            colors.append("#2980b9")

    # Bar chart for revenue in thousands (R$)
    x = np.arange(len(df))
    rev_k = df["monthly_revenue"] / 1000.0
    bars = ax1.bar(x, rev_k, color=colors, width=0.68, alpha=0.9, edgecolor="none", label="Monthly Revenue (k R$)")

    ax1.set_ylabel("Monthly Revenue (Thousand R$)", fontsize=11, fontweight="bold", color="#2c3e50")
    ax1.set_title("Olist Marketplace: Monthly Revenue (GMV) Trend & Lifecycle Phases (2016-2018)", fontsize=13, fontweight="bold", pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["month_year"], rotation=45, ha="right", fontsize=9)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"R${y:,.0f}k"))
    ax1.set_ylim(0, max(rev_k) * 1.18)

    # Annotate key phases
    # Nov 2016 zero month
    ax1.annotate("Nov 2016:\nZero Revenue", xy=(2, 0), xytext=(2, 180),
                 arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.2),
                 fontsize=8.5, ha="center", color="#c0392b", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#fdedec", ec="#c0392b", lw=0.8))

    # Black Friday Nov 2017 peak
    nov_17_idx = df[df["month_year"] == "2017-11"].index[0]
    ax1.annotate(f"Black Friday 2017\nPeak: R${rev_k[nov_17_idx]:,.0f}k",
                 xy=(nov_17_idx, rev_k[nov_17_idx]), xytext=(nov_17_idx - 1.5, rev_k[nov_17_idx] + 120),
                 arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.2),
                 fontsize=8.5, ha="center", color="#1e8449", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#eafaf1", ec="#27ae60", lw=0.8))

    # Sep 2018 partial cutoff
    ax1.annotate("Sep 2018:\nCutoff Tail", xy=(len(df) - 1, rev_k.iloc[-1]), xytext=(len(df) - 2.2, 220),
                 arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=1.2),
                 fontsize=8.5, ha="center", color="#7f8c8d", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#f2f4f4", ec="#bdc3c7", lw=0.8))

    # Add custom legend for phases
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2980b9", label="Full Operations (2017-2018)"),
        Patch(facecolor="#7fb3d5", label="Pilot Launch (Sep-Oct 2016)"),
        Patch(facecolor="#e74c3c", label="Zero Orders (Nov 2016)"),
        Patch(facecolor="#95a5a6", label="Cutoff Tail (Sep 2018)"),
    ]
    ax1.legend(handles=legend_elements, loc="upper left", frameon=True, fontsize=9)

    plt.tight_layout()
    out_path = CHARTS_DIR / "01_monthly_revenue_trend.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  Saved: {out_path}")
    return out_path


def generate_chart_2_delivery_delay_vs_reviews(conn) -> Path:
    """Generate Chart 2: Delivery delay vs review rating breakdown."""
    print("Generating Chart 2: Delivery Delay vs Review Score...")
    sql_path = PROJECT_ROOT / "sql" / "08_delivery_delay_vs_reviews.sql"
    df = pd.read_sql(text(sql_path.read_text(encoding="utf-8")), conn)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Subplot 1: % of Orders Delivered Late by Review Score
    colors = ["#c0392b", "#e67e22", "#f1c40f", "#27ae60", "#2ecc71"]
    bars = ax1.bar(df["review_score"], df["pct_late_deliveries_order_grain"], color=colors, width=0.6, edgecolor="#555555", lw=0.5)
    ax1.set_xlabel("Customer Review Score", fontsize=11, fontweight="bold")
    ax1.set_ylabel("% of Orders Delivered Late (>0 Days)", fontsize=11, fontweight="bold")
    ax1.set_title("Proportion of Late Deliveries by Review Score", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xticks(df["review_score"])
    ax1.set_xticklabels([f"★ {s}" for s in df["review_score"]], fontsize=10)
    ax1.set_ylim(0, 42)

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, h + 0.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Subplot 2: Average Transit Time & Average Delay When Late
    scores = df["review_score"]
    x = np.arange(len(scores))
    width = 0.35

    ax2.bar(x - width/2, df["avg_actual_delivery_days"], width, label="Avg Total Delivery Days", color="#34495e", alpha=0.85)
    ax2.bar(x + width/2, df["avg_days_late_when_delayed"], width, label="Avg Days Late (Delayed Orders)", color="#e74c3c", alpha=0.85)

    ax2.set_xlabel("Customer Review Score", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Days", fontsize=11, fontweight="bold")
    ax2.set_title("Actual Delivery Duration & Delay Severity", fontsize=12, fontweight="bold", pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"★ {s}" for s in scores], fontsize=10)
    ax2.legend(loc="upper right", fontsize=9.5)
    ax2.set_ylim(0, 26)

    for i in range(len(scores)):
        ax2.text(x[i] - width/2, df["avg_actual_delivery_days"].iloc[i] + 0.5, f"{df['avg_actual_delivery_days'].iloc[i]:.1f}d", ha="center", fontsize=8.5)
        ax2.text(x[i] + width/2, df["avg_days_late_when_delayed"].iloc[i] + 0.5, f"{df['avg_days_late_when_delayed'].iloc[i]:.1f}d", ha="center", fontsize=8.5, color="#c0392b", fontweight="bold")

    fig.suptitle("Impact of Fulfillment Delay on Customer Satisfaction Ratings", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = CHARTS_DIR / "02_delivery_delay_vs_review_score.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")
    return out_path


def generate_chart_3_repeat_purchase_rate(conn) -> Path:
    """Generate Chart 3: Repeat purchase rate and customer loyalty breakdown."""
    print("Generating Chart 3: Repeat Purchase Rate...")
    sql_path = PROJECT_ROOT / "sql" / "07_repeat_purchase_rate.sql"
    df = pd.read_sql(text(sql_path.read_text(encoding="utf-8")), conn)

    one_time = df["one_time_customers"].iloc[0]
    repeat = df["repeat_customers"].iloc[0]
    rate_pct = df["repeat_purchase_rate_pct"].iloc[0]

    # Query frequency distribution of repeat buyers
    dist_sql = text("""
        WITH counts AS (
            SELECT customer_unique_id, COUNT(DISTINCT order_id) AS orders
            FROM public.mart_order_summary
            WHERE order_status NOT IN ('canceled', 'unavailable')
            GROUP BY customer_unique_id
        )
        SELECT 
            CASE 
                WHEN orders = 1 THEN '1 Order (One-Time)'
                WHEN orders = 2 THEN '2 Orders'
                WHEN orders = 3 THEN '3 Orders'
                ELSE '4+ Orders'
            END AS order_tier,
            COUNT(*) AS customer_count
        FROM counts
        GROUP BY 1
        ORDER BY MIN(orders);
    """)
    dist_df = pd.read_sql(dist_sql, conn)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Donut chart: 1-time vs Repeat
    sizes = [one_time, repeat]
    labels = [f"One-Time\n{one_time:,}\n(96.96%)", f"Repeat Buyers\n{repeat:,}\n({rate_pct:.2f}%)"]
    colors = ["#bdc3c7", "#2980b9"]
    explode = (0, 0.1)

    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, autopct="", startangle=30, colors=colors, explode=explode,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    ax1.set_title(f"Eligible Customer Retention\n(Repeat Rate: {rate_pct:.2f}%)", fontsize=12, fontweight="bold")
    ax1.text(0, 0, f"{rate_pct:.2f}%\nRepeat", ha="center", va="center", fontsize=14, fontweight="bold", color="#2980b9")

    # Bar chart: Breakdown among repeat buyers
    repeat_breakdown = dist_df[dist_df["order_tier"] != "1 Order (One-Time)"].copy()
    b_bars = ax2.bar(repeat_breakdown["order_tier"], repeat_breakdown["customer_count"], color="#3498db", width=0.55, edgecolor="#2980b9")
    ax2.set_ylabel("Unique Customers", fontsize=11, fontweight="bold")
    ax2.set_title("Order Frequency Distribution Among Repeat Buyers", fontsize=12, fontweight="bold")
    ax2.set_ylim(0, max(repeat_breakdown["customer_count"]) * 1.2)

    for b in b_bars:
        h = b.get_height()
        pct = (h / repeat) * 100
        ax2.text(b.get_x() + b.get_width() / 2.0, h + 40, f"{h:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    fig.suptitle("Marketplace Retention Challenge: 97% One-and-Done Buyers", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = CHARTS_DIR / "03_repeat_purchase_rate.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")
    return out_path


def generate_chart_4_rolling_orders_and_categories(conn) -> Path:
    """Generate Chart 4: Rolling 7-day order trend and top revenue categories."""
    print("Generating Chart 4: 7-Day Rolling Orders & Category Revenue...")
    
    # 1. Rolling orders
    roll_sql = PROJECT_ROOT / "sql" / "06_rolling_7_day_orders.sql"
    roll_df = pd.read_sql(text(roll_sql.read_text(encoding="utf-8")), conn)
    roll_df["order_date"] = pd.to_datetime(roll_df["order_date"])

    # 2. Top national categories
    cat_sql = text("""
        SELECT 
            COALESCE(t.product_category_name_english, p.product_category_name, 'uncategorized') AS category_name,
            SUM(i.price) / 1000.0 AS revenue_k
        FROM staging.stg_order_items i
        JOIN staging.stg_orders o ON i.order_id = o.order_id
        JOIN public.olist_products_dataset p ON i.product_id = p.product_id
        LEFT JOIN public.product_category_name_translation t ON p.product_category_name = t.product_category_name
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
        GROUP BY 1
        ORDER BY revenue_k DESC
        LIMIT 6;
    """)
    cat_df = pd.read_sql(cat_sql, conn)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Subplot 1: 7-day Rolling Orders
    ax1.plot(roll_df["order_date"], roll_df["daily_orders"], color="#bdc3c7", alpha=0.45, lw=0.8, label="Daily Orders (Actual)")
    ax1.plot(roll_df["order_date"], roll_df["rolling_7_day_avg_orders"], color="#2c3e50", lw=2.0, label="7-Day Rolling Average")
    ax1.set_title("Daily Orders & 7-Day Rolling Trend (2016-2018)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Order Count", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=9.5)
    ax1.set_ylim(0, max(roll_df["rolling_7_day_avg_orders"]) * 1.25)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(8))

    # Black Friday annotation
    bf_date = pd.to_datetime("2017-11-24")
    ax1.annotate("Black Friday 2017 Peak\n(1,141 daily orders)", xy=(bf_date, 1141), xytext=(bf_date, 800),
                 arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.2),
                 fontsize=8.5, ha="center", color="#c0392b", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#fdedec", ec="#c0392b", lw=0.8))

    # Subplot 2: Top National Categories
    cats_sorted = cat_df.sort_values(by="revenue_k", ascending=True)
    bars = ax2.barh(cats_sorted["category_name"], cats_sorted["revenue_k"], color="#16a085", height=0.6, edgecolor="#0e6655")
    ax2.set_xlabel("GMV Revenue (Thousand R$)", fontsize=11, fontweight="bold")
    ax2.set_title("Top 6 Product Categories Nationally (Gross Revenue)", fontsize=12, fontweight="bold")
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"R${x:,.0f}k"))

    for bar in bars:
        w = bar.get_width()
        ax2.text(w + 15, bar.get_y() + bar.get_height() / 2.0, f"R${w:,.0f}k", va="center", fontsize=9, fontweight="bold")
    ax2.set_xlim(0, max(cats_sorted["revenue_k"]) * 1.18)

    fig.suptitle("Marketplace Velocity & Category Revenue Drivers", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = CHARTS_DIR / "04_top_categories_and_rolling_orders.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")
    return out_path


def generate_all_charts():
    engine = get_engine()
    with engine.connect() as conn:
        generate_chart_1_revenue_trend(conn)
        generate_chart_2_delivery_delay_vs_reviews(conn)
        generate_chart_3_repeat_purchase_rate(conn)
        generate_chart_4_rolling_orders_and_categories(conn)
    print("All 4 publication charts successfully created in charts/")


if __name__ == "__main__":
    generate_all_charts()
