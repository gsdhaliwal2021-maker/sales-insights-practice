"""Metrics API over the SQLite database built by `python -m pipeline`.

Run it:  uvicorn app.main:app --reload   then open http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

DEFAULT_DB = "data/retail.db"

app = FastAPI(title="Sales Insights API", version="0.1.0")


# --- SQL ---------------------------------------------------------------------
# Plain strings, so any query can be pasted straight into a SQLite shell.
# Months are filtered with a date range (>= start AND < stop) rather than
# strftime(...) = :month, so SQLite can use the index on invoice_date.

MONTHLY_REVENUE_SQL = """
SELECT
    strftime('%Y-%m', invoice_date) AS month,
    ROUND(SUM(revenue), 2)          AS revenue,
    COUNT(DISTINCT invoice_no)      AS orders,
    COUNT(DISTINCT customer_id)     AS customers
FROM transactions
GROUP BY month
ORDER BY month
"""

# A *repeat customer* in month M bought in M and has placed at least 2 orders
# (distinct invoices) in total by the end of M. That covers customers returning
# from an earlier month and customers who ordered twice within M. Two lines on
# one invoice are one order. Orders after M never count, so a month's answer
# doesn't change as new data arrives.
REPEAT_CUSTOMERS_SQL = """
WITH bounds AS (
    SELECT :month || '-01'                   AS start,
           date(:month || '-01', '+1 month') AS stop
),
orders_to_date AS (           -- lifetime order count per customer up to end of M
    SELECT customer_id, COUNT(DISTINCT invoice_no) AS n_orders
    FROM transactions, bounds
    WHERE invoice_date < bounds.stop
    GROUP BY customer_id
),
active AS (                   -- customers who bought in M, with their M revenue
    SELECT customer_id, SUM(revenue) AS revenue
    FROM transactions, bounds
    WHERE invoice_date >= bounds.start AND invoice_date < bounds.stop
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                                         AS active_customers,
    COALESCE(SUM(o.n_orders >= 2), 0)                                AS repeat_customers,
    ROUND(COALESCE(SUM(CASE WHEN o.n_orders >= 2 THEN a.revenue END), 0), 2)
                                                                     AS repeat_revenue,
    ROUND(COALESCE(SUM(a.revenue), 0), 2)                            AS total_revenue
FROM active a
JOIN orders_to_date o USING (customer_id)
"""


# --- database dependency -----------------------------------------------------

def db_path() -> Path:
    """Where the database lives. Override with the RETAIL_DB env var."""
    return Path(os.environ.get("RETAIL_DB", DEFAULT_DB))


def get_db() -> Iterator[sqlite3.Connection]:
    """Open a read-only connection for one request, then close it.

    A FastAPI dependency: routes receive it via `Depends(get_db)`, and tests
    can point it elsewhere by setting RETAIL_DB.
    """
    path = db_path()
    if not path.exists():
        raise HTTPException(503, f"Database not found at {path}. Run `python -m pipeline` first.")
    # mode=ro: the API only reads, so it should be unable to write.
    # check_same_thread=False: FastAPI may run the dependency and the route on
    # different threads; each request still gets its own connection.
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


# --- response models ---------------------------------------------------------

class MonthlyRevenue(BaseModel):
    month: str
    revenue: float
    orders: int
    customers: int


class RepeatCustomers(BaseModel):
    month: str
    active_customers: int
    repeat_customers: int
    repeat_rate: float      # repeat_customers / active_customers
    repeat_revenue: float   # revenue in the month from repeat customers
    total_revenue: float


# --- routes ------------------------------------------------------------------

@app.get("/metrics/monthly-revenue", response_model=list[MonthlyRevenue])
def monthly_revenue(db: DB) -> list[dict]:
    """Revenue, order count and customer count for every month in the data."""
    return [dict(row) for row in db.execute(MONTHLY_REVENUE_SQL)]


@app.get("/metrics/repeat-customers", response_model=RepeatCustomers)
def repeat_customers(
    db: DB,
    month: Annotated[
        str,
        Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Month as YYYY-MM", examples=["2026-05"]),
    ],
) -> dict:
    """How many of the month's customers are repeat customers.

    A repeat customer bought in `month` and has placed 2+ orders in total
    by the end of `month`.
    """
    row = db.execute(REPEAT_CUSTOMERS_SQL, {"month": month}).fetchone()
    if row["active_customers"] == 0:
        raise HTTPException(404, f"No transactions in {month}.")
    return {
        "month": month,
        **dict(row),
        "repeat_rate": round(row["repeat_customers"] / row["active_customers"], 4),
    }
