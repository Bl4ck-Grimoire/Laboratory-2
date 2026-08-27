QUERIES = {
    "R1": {
        "title": "R1 - Monthly Net Sales Trend",
        "sql": """
            SELECT d.year, d.month, d.month_name,
                   ROUND(SUM(f.net_sales), 2) AS net_sales
            FROM FactSales f
            JOIN DimDate d ON f.date_key = d.date_key
            GROUP BY d.year, d.month
            ORDER BY d.year, d.month;
        """,
    },
    "R2": {
        "title": "R2 - Net Sales & Quantity by Store and Channel",
        "sql": """
            SELECT s.store_name, c.channel_name,
                   SUM(f.quantity) AS units_sold,
                   ROUND(SUM(f.net_sales), 2) AS net_sales
            FROM FactSales f
            JOIN DimStore s ON f.store_key = s.store_key
            JOIN DimChannel c ON f.channel_key = c.channel_key
            GROUP BY s.store_name, c.channel_name
            ORDER BY net_sales DESC;
        """,
    },
    "R3": {
        "title": "R3 - Top Categories and Brands by Revenue and Units",
        "sql": """
            SELECT p.category, p.brand,
                   SUM(f.quantity) AS units_sold,
                   ROUND(SUM(f.net_sales), 2) AS net_sales
            FROM FactSales f
            JOIN DimProduct p ON f.product_key = p.product_key
            GROUP BY p.category, p.brand
            ORDER BY net_sales DESC;
        """,
    },
    "R4": {
        "title": "R4 - Promotion Performance (Sales, Units, Discount)",
        "sql": """
            SELECT pr.promotion_name,
                   SUM(f.quantity) AS units_sold,
                   ROUND(SUM(f.net_sales), 2) AS net_sales,
                   ROUND(SUM(f.discount_amount), 2) AS discount_amount
            FROM FactSales f
            JOIN DimPromotion pr ON f.promotion_key = pr.promotion_key
            GROUP BY pr.promotion_name
            ORDER BY net_sales DESC;
        """,
    },
    "R5": {
        "title": "R5 - Gross Profit and Gross Margin % by Category, Store, Month",
        "sql": """
            SELECT p.category, s.store_name, d.year, d.month,
                   ROUND(SUM(f.gross_profit), 2) AS gross_profit,
                   ROUND(SUM(f.gross_profit) * 100.0 / SUM(f.net_sales), 2) AS gross_margin_pct
            FROM FactSales f
            JOIN DimProduct p ON f.product_key = p.product_key
            JOIN DimStore s ON f.store_key = s.store_key
            JOIN DimDate d ON f.date_key = d.date_key
            GROUP BY p.category, s.store_name, d.year, d.month
            ORDER BY gross_profit DESC
            LIMIT 15;
        """,
    },
}


def run_query(conn, key):
    cur = conn.cursor()
    cur.execute(QUERIES[key]["sql"])
    columns = [c[0] for c in cur.description]
    return columns, cur.fetchall()


def run_all(conn):
    results = {}
    for key, spec in QUERIES.items():
        columns, rows = run_query(conn, key)
        results[key] = (spec["title"], columns, rows)
    return results


def print_results(results):
    for key, (title, columns, rows) in results.items():
        print(f"\n=== {title} ===")
        print(" | ".join(columns))
        for row in rows:
            print(" | ".join(str(v) for v in row))
