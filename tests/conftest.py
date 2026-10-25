"""Shared test fixtures.

`raw_csv` is a tiny hand-made CSV where every row exists to exercise one
cleaning rule. Small, explicit fixtures make a failing test easy to read:
you can see exactly which row should have survived.
"""

from pathlib import Path

import pytest

HEADER = "InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country"

ROWS = [
    # --- rows that should survive ---------------------------------------
    "500001,A1,GOOD MUG,2,2026-04-03 09:00,1.50,10001,France",
    "500002,A2,GOOD BAG,1,2026-05-10 14:30,4.00,10002.0,Spain",   # float-style ID
    "500003,A3, PADDED NAME ,3,2026-05-11 08:00,2.00, 10003 ,Germany",  # whitespace
    # --- rows that should be dropped ------------------------------------
    "C500004,A1,GOOD MUG,-2,2026-04-04 09:00,1.50,10001,France",  # cancellation
    "500005,A4,NO CUSTOMER,1,2026-04-05 09:00,3.00,,France",      # null CustomerID
    "500006,A5,BAD QTY,abc,2026-04-06 09:00,3.00,10004,France",   # non-numeric qty
    "500007,A6,BAD DATE,1,not-a-date,3.00,10004,France",          # bad date
    "500008,A7,FREE SAMPLE,1,2026-04-07 09:00,0.00,10004,France", # zero price
    "500001,A1,GOOD MUG,2,2026-04-03 09:00,1.50,10001,France",    # exact duplicate
]


@pytest.fixture
def raw_csv(tmp_path: Path) -> Path:
    path = tmp_path / "raw.csv"
    path.write_text("\n".join([HEADER, *ROWS]) + "\n")
    return path


@pytest.fixture
def repo_csv() -> Path:
    """The real dataset, for integration tests."""
    return Path(__file__).resolve().parents[1] / "data" / "online_retail.csv"
