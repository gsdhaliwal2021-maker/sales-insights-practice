"""Metrics API over the SQLite database built by `python -m pipeline`.

Run it:  uvicorn api.main:app --reload   then open http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

from api import queries

DEFAULT_DB = "data/retail.db"

app = FastAPI(title="Sales Insights API", version="0.1.0")


# --- database dependency ----------------------------------------------------

def db_path() -> Path:
    """Where the database lives. Override with the RETAIL_DB env var."""
    return Path(os.environ.get("RETAIL_DB", DEFAULT_DB))


def get_db() -> Iterator[sqlite3.Connection]:
    """Open a read-only connection for one request, then close it.

    A FastAPI *dependency*: routes ask for it with `Depends(get_db)`, and
    tests swap it for a test database via `app.dependency_overrides`.
    """
    path = db_path()
    if not path.exists():
        raise HTTPException(503, f"Database not found at {path}. Run `python -m pipeline` first.")
    # mode=ro: the API only reads, so it should be unable to write.
    # check_same_thread=False: FastAPI may run the dependency and the route in
    # different worker threads; each request still gets its own connection.
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


# --- response models ---------------------------------------------------------
# Pydantic models document the response shape in /docs and validate that the
# API returns what it promises.

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
    return [dict(row) for row in db.execute(queries.MONTHLY_REVENUE)]


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
    row = db.execute(queries.REPEAT_CUSTOMERS, {"month": month}).fetchone()
    if row["active_customers"] == 0:
        raise HTTPException(404, f"No transactions in {month}.")
    return {
        "month": month,
        **dict(row),
        "repeat_rate": round(row["repeat_customers"] / row["active_customers"], 4),
    }
