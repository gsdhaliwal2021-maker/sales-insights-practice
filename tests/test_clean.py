import pandas as pd
import pytest

from pipeline.clean import clean, read_raw


@pytest.fixture
def cleaned(raw_csv):
    return clean(read_raw(raw_csv))


def test_only_valid_rows_survive(cleaned):
    df, _ = cleaned
    assert sorted(df["invoice_no"]) == ["500001", "500002", "500003"]


def test_report_counts_each_rule(cleaned):
    _, report = cleaned
    assert report.rows_in == 9
    assert report.dropped == {
        "cancellations": 1,
        "missing values": 1,
        "unparseable values": 2,
        "zero/negative qty or price": 1,
        "exact duplicates": 1,
    }
    assert report.rows_out == 3
    # Nothing silently disappears: every input row is accounted for.
    assert report.rows_in - sum(report.dropped.values()) == report.rows_out


def test_types_are_fixed(cleaned):
    df, _ = cleaned
    assert pd.api.types.is_integer_dtype(df["quantity"])
    assert pd.api.types.is_float_dtype(df["unit_price"])
    assert pd.api.types.is_datetime64_any_dtype(df["invoice_date"])
    assert pd.api.types.is_string_dtype(df["customer_id"])


def test_customer_id_normalised(cleaned):
    df, _ = cleaned
    # '10002.0' and ' 10003 ' both become clean whole-number strings.
    assert set(df["customer_id"]) == {"10001", "10002", "10003"}


def test_text_is_stripped(cleaned):
    df, _ = cleaned
    assert "PADDED NAME" in set(df["description"])


def test_revenue_is_quantity_times_price(cleaned):
    df, _ = cleaned
    by_invoice = dict(zip(df["invoice_no"], df["revenue"]))
    assert by_invoice == {"500001": 3.0, "500002": 4.0, "500003": 6.0}


def test_missing_column_raises(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("InvoiceNo,Quantity\n1,2\n")
    with pytest.raises(ValueError, match="missing expected columns"):
        read_raw(bad)


# --- integration test on the real file ------------------------------------

def test_real_dataset_invariants(repo_csv):
    df, report = clean(read_raw(repo_csv))
    assert report.rows_out > 0
    assert not df["invoice_no"].str.startswith("C").any()
    assert df.isna().sum().sum() == 0
    assert (df["quantity"] > 0).all() and (df["unit_price"] > 0).all()
    assert not df.duplicated().any()
