"""Run the whole pipeline:  python -m pipeline [--csv PATH] [--db PATH]"""

import argparse

from pipeline.clean import clean, read_raw
from pipeline.load import load

DEFAULT_CSV = "data/online_retail.csv"
DEFAULT_DB = "data/retail.db"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Clean the retail CSV and load it into SQLite.")
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args(argv)

    df, report = clean(read_raw(args.csv))
    print(report)
    written = load(df, args.db)
    print(f"wrote {written} rows to {args.db}")


if __name__ == "__main__":
    main()
