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

## Run the tests

```bash
pytest
```

## Layout

```
data/online_retail.csv   raw input (data/retail.db is generated, git-ignored)
pipeline/clean.py        cleaning rules, one function each
pipeline/load.py         SQLite schema + loader
tests/                   pytest suite
```
