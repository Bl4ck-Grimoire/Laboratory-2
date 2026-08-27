MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def load_dim_date(conn, clean_sales_rows):
    distinct_dates = sorted({row["sale_date"] for row in clean_sales_rows})

    cur = conn.cursor()
    lookup = {}
    for i, d in enumerate(distinct_dates, start=1):
        quarter = (d.month - 1) // 3 + 1
        cur.execute(
            """INSERT INTO DimDate
               (date_key, full_date, day, month, month_name, quarter, year)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (i, d.isoformat(), d.day, d.month, MONTH_NAMES[d.month - 1], quarter, d.year),
        )
        lookup[d] = i
    conn.commit()
    return lookup


def load_dim_product(conn, products):
    cur = conn.cursor()
    lookup = {}
    for i, p in enumerate(products, start=1):
        cur.execute(
            """INSERT INTO DimProduct
               (product_key, product_id, product_name, category, brand)
               VALUES (?, ?, ?, ?, ?)""",
            (i, p["product_id"], p["product_name"], p["category"], p["brand"]),
        )
        lookup[p["product_id"]] = i
    conn.commit()
    return lookup


def load_dim_store(conn, stores):
    cur = conn.cursor()
    lookup = {}
    for i, s in enumerate(stores, start=1):
        cur.execute(
            """INSERT INTO DimStore
               (store_key, store_id, store_name, city, region)
               VALUES (?, ?, ?, ?, ?)""",
            (i, s["store_id"], s["store_name"], s["city"], s["region"]),
        )
        lookup[s["store_id"]] = i
    conn.commit()
    return lookup


def load_dim_channel(conn, channels):
    cur = conn.cursor()
    lookup = {}
    for i, c in enumerate(channels, start=1):
        cur.execute(
            """INSERT INTO DimChannel (channel_key, channel_id, channel_name)
               VALUES (?, ?, ?)""",
            (i, c["channel_id"], c["channel_name"]),
        )
        lookup[c["channel_id"]] = i
    conn.commit()
    return lookup


def load_dim_promotion(conn, promotions):
    cur = conn.cursor()
    lookup = {}
    for i, p in enumerate(promotions, start=1):
        cur.execute(
            """INSERT INTO DimPromotion
               (promotion_key, promotion_id, promotion_name, discount_pct)
               VALUES (?, ?, ?, ?)""",
            (i, p["promotion_id"], p["promotion_name"], p["discount_pct"]),
        )
        lookup[p["promotion_id"]] = i
    conn.commit()
    return lookup


def load_all_dimensions(conn, clean_reference, clean_sales_rows):
    return {
        "date": load_dim_date(conn, clean_sales_rows),
        "product": load_dim_product(conn, clean_reference["products"]),
        "store": load_dim_store(conn, clean_reference["stores"]),
        "channel": load_dim_channel(conn, clean_reference["channels"]),
        "promotion": load_dim_promotion(conn, clean_reference["promotions"]),
    }
