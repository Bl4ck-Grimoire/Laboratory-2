import csv
import json


def extract_sales(csv_path):
    """Read sales_transactions.csv into a list of raw dict rows (all strings)."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def extract_reference(json_path):
    """Read reference_data.json into a dict with the four collections."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)
