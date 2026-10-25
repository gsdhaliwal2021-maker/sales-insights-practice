"""Load the cleaned DataFrame into SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

# We write the schema by hand instead of letting pandas invent one, so the
# column types are explicit and the indexes we query on actually exist.
SCHEMA = """
DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id           INTEGER PRIMARY KEY,
    invoice_no   TEXT    NOT NULL,
    stock_code   TEXT    NOT NULL,
    description  TEXT    NOT NULL,
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    invoice_date TEXT    NOT NULL,  -- ISO 8601 'YYYY-MM-DD HH:MM:SS'
    unit_price   REAL    NOT NULL CHECK (unit_price > 0),
    customer_id  TEXT    NOT NULL,
    country      TEXT    NOT NULL,
    revenue      REAL    NOT NULL
);

CREATE INDEX idx_transactions_date     ON transactions (invoice_date);
CREATE INDEX idx_transactions_customer ON transactions (customer_id);
"""

COLUMNS = [
    "invoice_no", "stock_code", "description", "quantity", "invoice_date",
    "unit_price", "customer_id", "country", "revenue",
]


def load(df: pd.DataFrame, db_path: str | Path) -> int:
    """Replace the `transactions` table with `df`. Returns rows written.

    Rebuilding from scratch every run keeps the load idempotent: running the
    pipeline twice gives the same database, never double-counted rows.
    """
    rows = df[COLUMNS].copy()
    # SQLite has no date type; ISO text sorts correctly and works with
    # SQLite's strftime(), so it's the conventional choice.
    rows["invoice_date"] = rows["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    records = [
        tuple(None if pd.isna(v) else (v.item() if hasattr(v, "item") else v) for v in row)
        for row in rows.itertuples(index=False)
    ]
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            f"INSERT INTO transactions ({', '.join(COLUMNS)}) "
            f"VALUES ({', '.join('?' * len(COLUMNS))})",
            records,
        )
    return len(records)
