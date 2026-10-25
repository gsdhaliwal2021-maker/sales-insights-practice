"""API tests against a tiny database with hand-checkable answers.

Customers in the fixture:
  C1  one order in April (10.00), one in May (5.00)  -> repeat in May only
  C2  two orders in April (2.00 + 3.00)              -> repeat in April
  C3  one order in May (7.00)                        -> never repeat
  C4  one April order with two lines (4.00 + 1.00)   -> one order, not repeat

Expected:
  April revenue 20.00 | active C1,C2,C4 | repeat C2      | repeat revenue 5.00
  May   revenue 12.00 | active C1,C3    | repeat C1      | repeat revenue 5.00
"""

import pytest
from fastapi.testclient import TestClient

from app import main as api_main
from pipeline.clean import clean, read_raw
from pipeline.load import load

HEADER = "InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country"
ROWS = [
    "A1,X1,ITEM,1,2026-04-02 10:00,10.00,1,France",   # C1 April
    "A2,X1,ITEM,1,2026-05-02 10:00,5.00,1,France",    # C1 May
    "B1,X1,ITEM,1,2026-04-03 10:00,2.00,2,Spain",     # C2 April order 1
    "B2,X1,ITEM,1,2026-04-20 10:00,3.00,2,Spain",     # C2 April order 2
    "E1,X1,ITEM,1,2026-05-15 10:00,7.00,3,Germany",   # C3 May
    "F1,X1,ITEM,1,2026-04-10 10:00,4.00,4,Ireland",   # C4 line 1
    "F1,X2,OTHER,1,2026-04-10 10:00,1.00,4,Ireland",  # C4 line 2, same invoice
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    csv = tmp_path / "api.csv"
    csv.write_text("\n".join([HEADER, *ROWS]) + "\n")
    db = tmp_path / "api.db"
    df, _ = clean(read_raw(csv))
    load(df, db)
    # Point the app at the test database instead of data/retail.db.
    monkeypatch.setenv("RETAIL_DB", str(db))
    return TestClient(api_main.app)


# --- monthly revenue ------------------------------------------------------

def test_monthly_revenue(client):
    resp = client.get("/metrics/monthly-revenue")
    assert resp.status_code == 200
    assert resp.json() == [
        {"month": "2026-04", "revenue": 20.0, "orders": 4, "customers": 3},
        {"month": "2026-05", "revenue": 12.0, "orders": 2, "customers": 2},
    ]


# --- repeat customers -----------------------------------------------------

def test_repeat_customers_april(client):
    body = client.get("/metrics/repeat-customers", params={"month": "2026-04"}).json()
    assert body == {
        "month": "2026-04",
        "active_customers": 3,
        "repeat_customers": 1,   # C2 (two orders); C4's two lines are one order
        "repeat_rate": 0.3333,
        "repeat_revenue": 5.0,
        "total_revenue": 20.0,
    }


def test_repeat_customers_may_counts_returning_customer(client):
    body = client.get("/metrics/repeat-customers", params={"month": "2026-05"}).json()
    assert body["active_customers"] == 2
    assert body["repeat_customers"] == 1      # C1 came back from April
    assert body["repeat_revenue"] == 5.0
    assert body["repeat_rate"] == 0.5


def test_later_orders_do_not_leak_into_earlier_month(client):
    # C1's May order must not make C1 a repeat customer in April.
    body = client.get("/metrics/repeat-customers", params={"month": "2026-04"}).json()
    assert body["repeat_revenue"] == 5.0      # only C2's 2.00 + 3.00, not C1's 10.00


@pytest.mark.parametrize("bad", ["2026-13", "2026-4", "26-04", "april", "2026-04-01", ""])
def test_bad_month_format_is_422(client, bad):
    resp = client.get("/metrics/repeat-customers", params={"month": bad})
    assert resp.status_code == 422


def test_missing_month_is_422(client):
    assert client.get("/metrics/repeat-customers").status_code == 422


def test_month_without_data_is_404(client):
    resp = client.get("/metrics/repeat-customers", params={"month": "2030-01"})
    assert resp.status_code == 404
    assert "No transactions" in resp.json()["detail"]


def test_missing_database_is_503(tmp_path, monkeypatch):
    monkeypatch.setenv("RETAIL_DB", str(tmp_path / "nope.db"))
    resp = TestClient(api_main.app).get("/metrics/monthly-revenue")
    assert resp.status_code == 503
    assert "python -m pipeline" in resp.json()["detail"]


def test_api_cannot_write(client):
    # The connection is read-only, so a write attempt must fail.
    import sqlite3
    gen = api_main.get_db()   # keep a reference, or the generator's cleanup closes it
    conn = next(gen)
    try:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("DELETE FROM transactions")
    finally:
        gen.close()
