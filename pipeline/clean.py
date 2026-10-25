"""Clean the raw Online Retail CSV into a tidy, typed DataFrame.

Each cleaning rule is its own small function so it can be read, tested and
changed in isolation. `clean()` runs them in order and records how many rows
each rule removed, so you can always explain where rows went.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Raw CSV header -> snake_case name used everywhere downstream (SQL, API).
COLUMN_MAP = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}

# A row missing any of these can't be used for revenue or customer analysis.
REQUIRED_COLUMNS = list(COLUMN_MAP.values())


@dataclass
class CleanReport:
    """How many rows each step removed. Handy for logging and for tests."""

    rows_in: int = 0
    dropped: dict[str, int] = field(default_factory=dict)
    rows_out: int = 0

    def __str__(self) -> str:
        lines = [f"rows in:  {self.rows_in}"]
        lines += [f"  - {step}: {n}" for step, n in self.dropped.items()]
        lines.append(f"rows out: {self.rows_out}")
        return "\n".join(lines)


def read_raw(path: str | Path) -> pd.DataFrame:
    """Read every column as text first.

    Letting pandas guess types on read is how IDs like '012345' lose their
    leading zero or CustomerID turns into 12420.0. We read as strings and
    convert deliberately in `fix_types`.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=True)
    missing = set(COLUMN_MAP) - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing expected columns: {sorted(missing)}")
    return df.rename(columns=COLUMN_MAP)[REQUIRED_COLUMNS]


def strip_text(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace and turn empty strings into real nulls."""
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].str.strip().replace("", pd.NA)
    return out


def drop_cancellations(df: pd.DataFrame) -> pd.DataFrame:
    """Cancelled invoices start with 'C' and carry negative quantities.

    We drop them so revenue reflects completed sales only. (A refunds
    analysis would keep them in a separate table instead.)
    """
    is_cancel = df["invoice_no"].str.upper().str.startswith("C", na=False)
    return df[~is_cancel]


def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows missing any required field (in practice: CustomerID)."""
    return df.dropna(subset=REQUIRED_COLUMNS)


def fix_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert text columns to their real types.

    `errors="coerce"` turns unparseable values into nulls instead of
    crashing; `drop_unparseable` removes those rows afterwards.
    """
    out = df.copy()
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce").astype("Int64")
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce").astype("Float64")
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="coerce")
    # Some exports write CustomerID as '17850.0'. Go via float, then to a
    # whole-number string ID. It's an identifier, not a quantity, so we keep
    # it as text: you never add or average customer IDs.
    cid = pd.to_numeric(out["customer_id"], errors="coerce")
    whole = cid.notna() & (cid % 1 == 0)
    out["customer_id"] = cid.where(whole).astype("Int64").astype("string")
    return out


def drop_unparseable(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where a type conversion failed (value became null)."""
    return df.dropna(subset=["quantity", "unit_price", "invoice_date", "customer_id"])


def drop_non_positive(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only real sales: quantity > 0 and price > 0.

    Zero-price lines are free samples or manual adjustments, not revenue.
    Negative quantity outside a 'C' invoice would also be a correction.
    """
    return df[(df["quantity"] > 0) & (df["unit_price"] > 0)]


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows identical in every column (likely double-entered lines)."""
    return df.drop_duplicates()


def add_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Line revenue = quantity x unit price, rounded to cents."""
    out = df.copy()
    out["revenue"] = (out["quantity"] * out["unit_price"]).round(2)
    return out


# Order matters: drop cancellations and nulls before converting types, then
# validate values, then de-duplicate once everything is in its final form.
STEPS = [
    ("cancellations", drop_cancellations),
    ("missing values", drop_nulls),
    ("unparseable values", lambda d: drop_unparseable(fix_types(d))),
    ("zero/negative qty or price", drop_non_positive),
    ("exact duplicates", drop_duplicates),
]


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    """Run every cleaning step and return (clean_df, report)."""
    report = CleanReport(rows_in=len(raw))
    df = strip_text(raw)
    for name, step in STEPS:
        before = len(df)
        df = step(df)
        report.dropped[name] = before - len(df)
    df = add_revenue(df).reset_index(drop=True)
    report.rows_out = len(df)
    return df, report
