from datetime import datetime


def _new_report():
    return {
        "input_rows": 0,
        "dropped_bad_date": 0,
        "dropped_bad_numeric": 0,
        "dropped_non_positive_qty_or_price": 0,
        "dropped_duplicate_sale_line_id": 0,
        "dropped_orphan_reference": 0,
        "filled_missing_promotion": 0,
        "output_rows": 0,
    }


def clean_sales_rows(raw_rows, reference, default_promotion_id="PR00"):
    report = _new_report()
    report["input_rows"] = len(raw_rows)

    valid_products = {p["product_id"] for p in reference["products"]}
    valid_stores = {s["store_id"] for s in reference["stores"]}
    valid_channels = {c["channel_id"] for c in reference["channels"]}
    valid_promotions = {p["promotion_id"] for p in reference["promotions"]}

    seen_line_ids = set()
    clean_rows = []

    for row in raw_rows:
        # 1. Trim whitespace defensively on every string field
        row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

        # 2. Deduplicate by sale_line_id (grain key) keeps first occurrence
        sale_line_id = row["sale_line_id"]
        if sale_line_id in seen_line_ids:
            report["dropped_duplicate_sale_line_id"] += 1
            continue
        seen_line_ids.add(sale_line_id)

        # 3. Parse and validate the date
        try:
            sale_date = datetime.strptime(row["sale_date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            report["dropped_bad_date"] += 1
            continue

        # 4. Cast and validate numeric fields
        try:
            quantity = int(row["quantity"])
            unit_price_sale = float(row["unit_price_sale"])
        except (ValueError, KeyError):
            report["dropped_bad_numeric"] += 1
            continue

        if quantity <= 0 or unit_price_sale <= 0:
            report["dropped_non_positive_qty_or_price"] += 1
            continue

        # 5. Fill missing promotion_id with the "No Promotion" member
        promotion_id = row.get("promotion_id") or ""
        if promotion_id == "":
            promotion_id = default_promotion_id
            report["filled_missing_promotion"] += 1

        # 6. Referential integrity, every business key must resolve to a
        #    known dimension member, otherwise the row cannot be attributed
        #    and is quarantined rather than loaded with a broken FK.
        if (
            row["product_id"] not in valid_products
            or row["store_id"] not in valid_stores
            or row["channel_id"] not in valid_channels
            or promotion_id not in valid_promotions
        ):
            report["dropped_orphan_reference"] += 1
            continue

        clean_rows.append(
            {
                "sale_line_id": sale_line_id,
                "transaction_id": row["transaction_id"],
                "sale_date": sale_date,
                "store_id": row["store_id"],
                "product_id": row["product_id"],
                "channel_id": row["channel_id"],
                "promotion_id": promotion_id,
                "quantity": quantity,
                "unit_price_sale": unit_price_sale,
            }
        )

    report["output_rows"] = len(clean_rows)
    return clean_rows, report


def clean_reference(reference):
    cleaned = {}
    for collection_name, records in reference.items():
        seen_keys = set()
        cleaned_records = []
        key_field = {
            "products": "product_id",
            "stores": "store_id",
            "channels": "channel_id",
            "promotions": "promotion_id",
        }[collection_name]

        for record in records:
            record = {
                k: (v.strip() if isinstance(v, str) else v) for k, v in record.items()
            }
            key = record[key_field]
            if key in seen_keys:
                continue
            seen_keys.add(key)
            cleaned_records.append(record)

        cleaned[collection_name] = cleaned_records
    return cleaned
