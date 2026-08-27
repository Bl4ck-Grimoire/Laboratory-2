"""
Run with:  python3 src/main.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from extract import extract_sales, extract_reference
from transform import clean_sales_rows, clean_reference
from create_schema import create_schema
from load_dimensions import load_all_dimensions
from load_fact import load_fact_sales
from queries import run_all, print_results

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "sales_transactions.csv")
JSON_PATH = os.path.join(BASE_DIR, "data", "reference_data.json")
DB_PATH = os.path.join(BASE_DIR, "database", "retail_dw.db")


def main():
    # 1. EXTRACT
    raw_sales = extract_sales(CSV_PATH)
    raw_reference = extract_reference(JSON_PATH)
    print(f"[EXTRACT] {len(raw_sales)} raw sales rows read from CSV.")

    # 2. TRANSFORM (cleaning + validation)
    reference = clean_reference(raw_reference)
    sales_rows, report = clean_sales_rows(raw_sales, reference)

    print("\n[TRANSFORM] Data quality report:")
    for k, v in report.items():
        print(f"    {k}: {v}")

    # 3. CREATE SCHEMA
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = create_schema(DB_PATH)
    print(f"\n[SCHEMA] Star Schema created at {DB_PATH}")

    # 4. LOAD DIMENSIONS
    dim_lookups = load_all_dimensions(conn, reference, sales_rows)
    print("\n[LOAD] Dimensions loaded:")
    print(f"    DimDate:      {len(dim_lookups['date'])} rows")
    print(f"    DimProduct:   {len(dim_lookups['product'])} rows")
    print(f"    DimStore:     {len(dim_lookups['store'])} rows")
    print(f"    DimChannel:   {len(dim_lookups['channel'])} rows")
    print(f"    DimPromotion: {len(dim_lookups['promotion'])} rows")

    # 5. LOAD FACT
    products_by_id = {p["product_id"]: p for p in reference["products"]}
    fact_rows_loaded = load_fact_sales(conn, sales_rows, dim_lookups, products_by_id)
    print(f"\n[LOAD] FactSales loaded: {fact_rows_loaded} rows")

    # 6. VALIDATE
    results = run_all(conn)
    print("\n[VALIDATE] Part F — requirement-based queries:")
    print_results(results)

    conn.close()
    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()
