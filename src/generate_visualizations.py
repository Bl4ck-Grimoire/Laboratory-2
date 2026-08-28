import os
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "retail_dw.db")
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def viz1_monthly_net_sales_trend(conn):
    """R1  temporal requirement -> line chart (best for a trend over time)."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT d.year, d.month, d.month_name, SUM(f.net_sales) AS net_sales
        FROM FactSales f
        JOIN DimDate d ON f.date_key = d.date_key
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month;
        """
    )
    rows = cur.fetchall()
    labels = [f"{r[2][:3]} {r[0]}" for r in rows]
    values = [r[3] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(labels, values, marker="o", linewidth=2, color="#2563eb")
    ax.fill_between(labels, values, alpha=0.08, color="#2563eb")
    ax.set_title("R1  Monthly Net Sales Trend (Jan–Jun 2026)", fontsize=13, weight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Net Sales (COP)")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x/1e6:.0f}M")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    out_path = os.path.join(DOCS_DIR, "viz1_monthly_net_sales_trend.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def viz2_top_categories_brands(conn):
    """R3  comparative requirement -> horizontal bar chart (best for ranking)."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.category, SUM(f.net_sales) AS net_sales
        FROM FactSales f
        JOIN DimProduct p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY net_sales ASC;
        """
    )
    rows = cur.fetchall()
    categories = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(categories, values, color="#0ea5a4")
    ax.set_title("R3  Net Sales by Product Category", fontsize=13, weight="bold")
    ax.set_xlabel("Net Sales (COP)")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x/1e6:.0f}M")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value/1e6:.0f}M",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()

    out_path = os.path.join(DOCS_DIR, "viz2_top_categories_brands.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    path1 = viz1_monthly_net_sales_trend(conn)
    print(f"[VIZ] Saved: {path1}")

    path2 = viz2_top_categories_brands(conn)
    print(f"[VIZ] Saved: {path2}")

    conn.close()


if __name__ == "__main__":
    main()
