# SQL analysis layer — AI Data-Centre Water Tracker

The shaping half of a small BI project over the tracker's site data: filter, group,
rank and split the sites in SQL, then present the same splits in a dashboard. This
folder holds the SQL layer; it runs locally with no server. A Power BI presentation
layer is built on the same table separately.

## Data

`ai_water_sites.csv` — 10 data-centre sites derived from the tracker's [`sites.csv`](../sites.csv),
with the Water Consumption Impact index (`WCI`), cooling type, grid region, a
measured-vs-planning `Status` flag, and the hydropower-coupling fields. Figures come
from operator environmental reports and public reservoir data; see [`SOURCES.md`](../SOURCES.md).

## Run it

```
python3 -m pip install --user duckdb
python3 run_queries.py
```

Or open the queries directly in the DuckDB CLI:

```
duckdb
.read queries.sql
```

Each query reads the CSV in place, so there is no import step.

## What the queries show (`queries.sql`)

1. Average WCI per operator, for operators with two or more sites (`GROUP BY` / `HAVING`).
2. Primary-verified sites ranked by WCI (filtering + sort).
3. Each site ranked within its operator, top two per operator (`RANK() OVER (PARTITION BY ...)`).
4. Water demand that counts vs planning-only figures that are excluded (`CASE` bucketing).
5. Hydro-coupled sites: water use that also draws on a dammed reservoir.

## Method note

For ten rows a single flat table is correct; a growing dataset would split operator and
site into dimension tables (a star schema). The `Status` flag keeps non-operational
planning figures out of the measured totals, which is the same discipline the tracker
applies to its published Water Consumption Impact numbers.

Licensed CC BY 4.0, consistent with the rest of the tracker.
