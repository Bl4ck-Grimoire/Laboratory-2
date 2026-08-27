def load_fact_sales(conn, clean_sales_rows, dim_lookups, products_by_id):
    """
    products_by_id: {product_id: {..., "list_price": ..., "unit_cost": ...}}
    
    """
    cur = conn.cursor()
    rows_loaded = 0

    for row in clean_sales_rows:
        product = products_by_id[row["product_id"]]
        list_price = product["list_price"]
        unit_cost = product["unit_cost"]
        quantity = row["quantity"]

        gross_sales = quantity * list_price
        net_sales = quantity * row["unit_price_sale"]
        discount_amount = gross_sales - net_sales
        cost_amount = quantity * unit_cost
        gross_profit = net_sales - cost_amount

        cur.execute(
            """INSERT INTO FactSales (
                   sale_line_id, transaction_id,
                   date_key, product_key, store_key, channel_key, promotion_key,
                   quantity, gross_sales, discount_amount, net_sales,
                   cost_amount, gross_profit
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row["sale_line_id"],
                row["transaction_id"],
                dim_lookups["date"][row["sale_date"]],
                dim_lookups["product"][row["product_id"]],
                dim_lookups["store"][row["store_id"]],
                dim_lookups["channel"][row["channel_id"]],
                dim_lookups["promotion"][row["promotion_id"]],
                quantity,
                gross_sales,
                discount_amount,
                net_sales,
                cost_amount,
                gross_profit,
            ),
        )
        rows_loaded += 1

    conn.commit()
    return rows_loaded
