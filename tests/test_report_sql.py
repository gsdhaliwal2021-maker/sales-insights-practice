"""Run every SQL block in analysis/report.md against a fresh database.

The report's numbers come from its SQL. This test makes sure the SQL still
runs and still produces the headline figures, so the prose and the code
can't silently drift apart when the pipeline changes.
"""

import re
import sqlite3
from pathlib import Path

import pytest

from pipeline.clean import clean, read_raw
from pipeline.load import load

REPORT = Path(__file__).resolve().parents[1] / "analysis" / "report.md"


def sql_blocks() -> dict[str, str]:
    """Return {name: sql} for every ```sql block starting with '-- name: x'."""
    text = REPORT.read_text()
    return dict(re.findall(r"```sql\n-- name: (\w+)\n(.*?)```", text, flags=re.S))


@pytest.fixture(scope="module")
def conn(tmp_path_factory, request):
    csv = Path(request.config.rootpath) / "data" / "online_retail.csv"
    db = tmp_path_factory.mktemp("report") / "retail.db"
    df, _ = clean(read_raw(csv))
    load(df, db)
    connection = sqlite3.connect(db)
    connection.executescript(sql_blocks()["setup"])
    yield connection
    connection.close()


def test_report_has_expected_blocks():
    assert {"setup", "headline", "bridge", "by_country", "by_product", "by_cohort"} <= set(sql_blocks())


@pytest.mark.parametrize("name", [n for n in sql_blocks() if n != "setup"])
def test_every_block_runs_and_returns_rows(conn, name):
    rows = conn.execute(sql_blocks()[name]).fetchall()
    assert rows, f"block '{name}' returned no rows"


def test_headline_matches_report(conn):
    q2, q3, change, pct, *_ = conn.execute(sql_blocks()["headline"]).fetchone()
    assert (q2, q3, change, pct) == (52392.21, 31422.54, -20969.67, -40.0)


def test_bridge_adds_up_to_headline(conn):
    total_change = sum(row[4] for row in conn.execute(sql_blocks()["bridge"]))
    _, _, change, *_ = conn.execute(sql_blocks()["headline"]).fetchone()
    assert total_change == pytest.approx(change, abs=2)  # rounding per bucket


def test_germany_is_the_outlier(conn):
    rows = {r[0]: r for r in conn.execute(sql_blocks()["by_country"])}
    germany_pct = rows["Germany"][4]
    others = [r[4] for name, r in rows.items() if name != "Germany"]
    assert germany_pct < min(others) - 20


def test_prices_did_not_change(conn):
    for row in conn.execute(sql_blocks()["by_product"]):
        price_q2, price_q3 = row[-2], row[-1]
        assert price_q2 == price_q3, row[1]
