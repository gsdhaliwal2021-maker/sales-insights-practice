import sqlite3

import pytest

from pipeline.__main__ import main
from pipeline.clean import clean, read_raw
from pipeline.load import load


@pytest.fixture
def db(raw_csv, tmp_path):
    path = tmp_path / "test.db"
    df, _ = clean(read_raw(raw_csv))
    load(df, path)
    return path


def query(db, sql):
    with sqlite3.connect(db) as conn:
        return conn.execute(sql).fetchall()


def test_rows_loaded(db):
    assert query(db, "SELECT COUNT(*) FROM transactions") == [(3,)]


def test_column_types_in_sqlite(db):
    row = query(db, """
        SELECT typeof(quantity), typeof(unit_price), typeof(customer_id),
               typeof(invoice_date), typeof(revenue)
        FROM transactions LIMIT 1
    """)
    assert row == [("integer", "real", "text", "text", "real")]


def test_dates_are_iso_text(db):
    # ISO text lets SQLite's strftime() group by month.
    months = query(db, "SELECT DISTINCT strftime('%Y-%m', invoice_date) FROM transactions ORDER BY 1")
    assert months == [("2026-04",), ("2026-05",)]


def test_load_is_idempotent(raw_csv, db):
    df, _ = clean(read_raw(raw_csv))
    load(df, db)  # second run on the same database
    assert query(db, "SELECT COUNT(*) FROM transactions") == [(3,)]


def test_cli_end_to_end(raw_csv, tmp_path, capsys):
    db_path = tmp_path / "cli.db"
    main(["--csv", str(raw_csv), "--db", str(db_path)])
    assert "wrote 3 rows" in capsys.readouterr().out
    assert query(db_path, "SELECT COUNT(*) FROM transactions") == [(3,)]
