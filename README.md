# sales-insights-practice

A small practice project: clean an online-retail CSV, load it into SQLite,
and analyse it.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Build the database

```bash
python -m pipeline            # reads data/online_retail.csv, writes data/retail.db
```

It prints how many rows each cleaning rule removed:

| Rule | What it removes | Why |
|---|---|---|
| cancellations | invoices starting with `C` | refunds, not sales |
| missing values | rows missing any field (in practice, CustomerID) | can't attribute to a customer |
| unparseable values | quantity/price/date/ID that won't convert | bad data |
| zero/negative qty or price | free samples, adjustments | not revenue |
| exact duplicates | rows identical in every column | double-entered lines |

## Run the API

Build the database first (above), then:

```bash
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
```

| Endpoint | Returns |
|---|---|
| `GET /metrics/monthly-revenue` | revenue, orders and customers per month |
| `GET /metrics/repeat-customers?month=YYYY-MM` | active vs repeat customers and their revenue for that month |

A **repeat customer** in a month bought that month and has 2+ orders (distinct
invoices) in total by the end of it. The API reads `data/retail.db` read-only;
set `RETAIL_DB` to point it at another database.

## Run the tests

```bash
pytest
```

## Layout

```
data/online_retail.csv   raw input (data/retail.db is generated, git-ignored)
pipeline/clean.py        cleaning rules, one function each
pipeline/load.py         SQLite schema + loader
app/main.py              FastAPI app: routes, SQL and response models
tests/                   pytest suite
```
