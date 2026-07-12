#!/usr/bin/env python3
"""Run the SQL analysis layer over the AI water-tracker site data (DuckDB).

The shaping half of the BI project; a Power BI dashboard is the presentation
half. Reads queries.sql, runs each statement against ai_water_sites.csv and
prints the result, so the analysis is reproducible with one command.

Requires DuckDB:  python3 -m pip install --user duckdb
Usage:            python3 run_queries.py
"""
import os
import re
import sys

try:
    import duckdb
except ImportError:
    sys.exit("DuckDB not installed. Run: python3 -m pip install --user duckdb")

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)  # so read_csv_auto('ai_water_sites.csv') resolves


def blocks(path):
    """Split queries.sql into (label, sql) on each numbered '-- N.' comment."""
    raw = open(path, encoding="utf-8").read()
    for chunk in re.split(r"\n(?=-- \d+\.)", raw):
        lines = chunk.strip().splitlines()
        if not lines:
            continue
        label = lines[0].lstrip("- ").strip() if lines[0].startswith("--") else ""
        sql = "\n".join(l for l in lines if not l.lstrip().startswith("--")).strip()
        if sql:
            yield label, sql


def main():
    for label, sql in blocks("queries.sql"):
        print(f"\n===== {label} =====")
        print(duckdb.sql(sql).df().to_string(index=False))


if __name__ == "__main__":
    main()
