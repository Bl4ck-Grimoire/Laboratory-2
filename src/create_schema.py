import sqlite3

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS FactSales;
DROP TABLE IF EXISTS DimPromotion;
DROP TABLE IF EXISTS DimChannel;
DROP TABLE IF EXISTS DimStore;
DROP TABLE IF EXISTS DimProduct;
DROP TABLE IF EXISTS DimDate;

CREATE TABLE DimDate (
    date_key    INTEGER PRIMARY KEY,
    full_date   TEXT    NOT NULL UNIQUE,   -- ISO format YYYY-MM-DD
    day         INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT    NOT NULL,
    quarter     INTEGER NOT NULL,
    year        INTEGER NOT NULL
);

CREATE TABLE DimProduct (
    product_key   INTEGER PRIMARY KEY,
    product_id    TEXT    NOT NULL UNIQUE,  -- natural key from source
    product_name  TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    brand         TEXT    NOT NULL
);

CREATE TABLE DimStore (
    store_key   INTEGER PRIMARY KEY,
    store_id    TEXT    NOT NULL UNIQUE,    -- natural key from source
    store_name  TEXT    NOT NULL,
    city        TEXT    NOT NULL,
    region      TEXT    NOT NULL
);

CREATE TABLE DimChannel (
    channel_key   INTEGER PRIMARY KEY,
    channel_id    TEXT    NOT NULL UNIQUE,  -- natural key from source
    channel_name  TEXT    NOT NULL
);

CREATE TABLE DimPromotion (
    promotion_key   INTEGER PRIMARY KEY,
    promotion_id    TEXT    NOT NULL UNIQUE, -- natural key from source
    promotion_name  TEXT    NOT NULL,
    discount_pct    REAL    NOT NULL
);

CREATE TABLE FactSales (
    sale_line_id     TEXT    PRIMARY KEY,     -- degenerate dimension, enforces the grain
    transaction_id   TEXT    NOT NULL,        -- degenerate dimension, traceability only
    date_key         INTEGER NOT NULL REFERENCES DimDate(date_key),
    product_key      INTEGER NOT NULL REFERENCES DimProduct(product_key),
    store_key        INTEGER NOT NULL REFERENCES DimStore(store_key),
    channel_key      INTEGER NOT NULL REFERENCES DimChannel(channel_key),
    promotion_key    INTEGER NOT NULL REFERENCES DimPromotion(promotion_key),
    quantity         INTEGER NOT NULL,
    gross_sales      REAL    NOT NULL,
    discount_amount  REAL    NOT NULL,
    net_sales        REAL    NOT NULL,
    cost_amount      REAL    NOT NULL,
    gross_profit     REAL    NOT NULL
);

CREATE INDEX idx_fact_date ON FactSales(date_key);
CREATE INDEX idx_fact_product ON FactSales(product_key);
CREATE INDEX idx_fact_store ON FactSales(store_key);
CREATE INDEX idx_fact_channel ON FactSales(channel_key);
CREATE INDEX idx_fact_promotion ON FactSales(promotion_key);
"""


def create_schema(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn
