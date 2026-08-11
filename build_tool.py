#!/usr/bin/env python3
"""Build the self-contained GitHub Pages explorer from the frozen source files.

The ten-site comparison remains defined by sites.csv. water_source_evidence.csv
adds only explicit source classifications. The generated page embeds all data and
has no runtime dependencies.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
from typing import Any


HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_SITES = HERE / "sites.csv"
DEFAULT_SOURCES = HERE / "water_source_evidence.csv"
DEFAULT_HTML = HERE / "index.html"

DATA_PATTERN = re.compile(
    r"(?P<start>/\* DATA-START \*/\n).*?(?P<end>\n/\* DATA-END \*/)", re.DOTALL
)
STATUS_LABELS = {
    "primary": "Primary verified",
    "planning_not_measured": "Planning, not measured",
    "framework_secondary": "Framework secondary",
}
SOURCE_CLASSES = {"reclaimed_potable", "surface_water", "aquifer_municipal"}
EVIDENCE_TIERS = {"primary", "framework_secondary"}

UNKNOWN_SOURCE = {
    "source_class": "unknown",
    "source_label": "Unknown",
    "evidence_tier": "not_reported",
    "evidence_note": (
        "No potable, reclaimed, surface-water or groundwater classification is "
        "carried for this seed row. Grid and reservoir fields are not used to infer it."
    ),
    "detail_href": "SOURCES.md",
    "total_2024_Mgal": None,
    "potable_2024_Mgal": None,
    "reclaimed_2024_Mgal": None,
    "total_2025_Mgal": None,
    "potable_2025_Mgal": None,
    "reclaimed_2025_Mgal": None,
}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str | None) -> float | None:
    text = (value or "").strip()
    return None if not text else float(text)


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def water_metrics(
    withdrawal: float | None,
    consumptive_ratio: float | None,
    peaking_factor: float | None,
    capacity: float | None,
) -> dict[str, float | None]:
    if withdrawal is None or consumptive_ratio is None:
        consumed = None
        peak_consumed = None
    else:
        consumed = withdrawal * consumptive_ratio
        peak_consumed = (
            consumed * peaking_factor if peaking_factor is not None else None
        )
    return {
        "withdrawal": withdrawal,
        "consumed": consumed,
        "peak_consumed": peak_consumed,
        "wci": ratio(peak_consumed, capacity),
    }


def offsite_share(wue: float | None, ewif: float | None, pue: float = 1.2) -> float | None:
    if wue is None or ewif is None:
        return None
    offsite = pue * ewif
    total = wue + offsite
    return None if total == 0 else offsite / total


def evidence_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    numeric_fields = (
        "total_2024_Mgal",
        "potable_2024_Mgal",
        "reclaimed_2024_Mgal",
        "total_2025_Mgal",
        "potable_2025_Mgal",
        "reclaimed_2025_Mgal",
    )
    for row in rows:
        key = (row["operator"].strip(), row["location"].strip())
        if key in indexed:
            raise ValueError(f"duplicate water-source evidence row: {key}")
        source_class = row["source_class"].strip()
        evidence_tier = row["evidence_tier"].strip()
        if source_class not in SOURCE_CLASSES:
            raise ValueError(f"unknown water-source class for {key}: {source_class}")
        if evidence_tier not in EVIDENCE_TIERS:
            raise ValueError(f"unknown water-source evidence tier for {key}: {evidence_tier}")
        item: dict[str, Any] = {
            "source_class": source_class,
            "source_label": row["source_label"].strip(),
            "evidence_tier": evidence_tier,
            "evidence_note": row["evidence_note"].strip(),
            "detail_href": row["detail_href"].strip(),
        }
        item.update({field: number(row.get(field)) for field in numeric_fields})
        for year in ("2024", "2025"):
            total = item[f"total_{year}_Mgal"]
            potable = item[f"potable_{year}_Mgal"]
            reclaimed = item[f"reclaimed_{year}_Mgal"]
            present = [value is not None for value in (total, potable, reclaimed)]
            if any(present) and not all(present):
                raise ValueError(f"incomplete {year} source split for {key}")
            if total is not None and abs(total - potable - reclaimed) > 0.05:
                raise ValueError(f"{year} source split does not sum to total for {key}")
        indexed[key] = item
    return indexed


def build_site_data(
    site_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    evidence = evidence_index(evidence_rows)
    ordered_site_keys = [
        (row["operator"].strip(), row["location"].strip()) for row in site_rows
    ]
    site_keys = set(ordered_site_keys)
    if len(site_keys) != len(ordered_site_keys):
        raise ValueError("sites.csv contains a duplicate operator and location key")
    unused = sorted(set(evidence) - site_keys)
    if unused:
        raise ValueError(f"water-source evidence has no matching seed row: {unused}")

    result: list[dict[str, Any]] = []
    for row in site_rows:
        operator = row["operator"].strip()
        location = row["location"].strip()
        tier = row["motive_tier"].strip()
        if tier not in STATUS_LABELS:
            raise ValueError(f"unknown motive_tier for {operator}, {location}: {tier}")

        withdrawal_2024 = number(row.get("W_d_ML_d"))
        ratio_2024 = number(row.get("r"))
        withdrawal_2025 = number(row.get("W_d_2025_ML_d"))
        ratio_2025 = number(row.get("r_2025"))
        peaking_factor = number(row.get("PF"))
        capacity = number(row.get("K_ML_d"))
        wue = number(row.get("WUE_L_per_kWh"))
        ewif_lo = number(row.get("EWIF_lo"))
        ewif_hi = number(row.get("EWIF_hi"))

        source = dict(UNKNOWN_SOURCE)
        source.update(evidence.get((operator, location), {}))

        result.append(
            {
                "operator": operator,
                "location": location,
                "status": tier,
                "status_label": STATUS_LABELS[tier],
                "cooling": row["cooling"].strip(),
                "grid_region": row["grid_region"].strip(),
                "hydro_coupled": row["double_coupled_candidate"].strip().upper().startswith("Y"),
                "reservoir": row["reservoir"].strip(),
                "dam": row["dam"].strip(),
                "source_tag": row["source_tag"].strip(),
                "vintage_note": row["vintage_note"].strip(),
                "range_flag": row["range_flag"].strip(),
                "reported_wci_2024": number(row.get("stated_WCI")),
                "fy2024": water_metrics(
                    withdrawal_2024, ratio_2024, peaking_factor, capacity
                ),
                "fy2025": water_metrics(
                    withdrawal_2025, ratio_2025, peaking_factor, capacity
                ),
                "offsite_share": {
                    "low": offsite_share(wue, ewif_lo),
                    "high": offsite_share(wue, ewif_hi),
                },
                "water_source": source,
            }
        )
    return result


def json_for_script(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    if "</script" in text.lower():
        raise ValueError("embedded data contains a closing script tag")
    return text


def render_html(template: str, sites: list[dict[str, Any]]) -> str:
    if not DATA_PATTERN.search(template):
        raise ValueError("index.html is missing the DATA marker pair")
    rendered = DATA_PATTERN.sub(
        lambda match: match.group("start")
        + "const DATA = "
        + json_for_script(sites)
        + ";"
        + match.group("end"),
        template,
    )
    return rendered


def run(
    sites_path: pathlib.Path,
    sources_path: pathlib.Path,
    html_path: pathlib.Path,
    check: bool,
) -> int:
    sites = build_site_data(read_csv(sites_path), read_csv(sources_path))
    template = html_path.read_text(encoding="utf-8")
    rendered = render_html(template, sites)

    if check:
        if rendered != template:
            print("index.html data blocks are stale; run python3 build_tool.py")
            return 1
        print(f"index.html is current: {len(sites)} seed rows")
        return 0

    html_path.write_text(rendered, encoding="utf-8")
    print(f"wrote {html_path.name}: {len(sites)} seed rows")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites", type=pathlib.Path, default=DEFAULT_SITES)
    parser.add_argument("--sources", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--html", type=pathlib.Path, default=DEFAULT_HTML)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        return run(args.sites, args.sources, args.html, args.check)
    except (OSError, KeyError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
