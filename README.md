# AI Data-Centre Water Tracker

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21318960.svg)](https://doi.org/10.5281/zenodo.21318960)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
![Python 3](https://img.shields.io/badge/python-3-blue.svg)
![No dependencies](https://img.shields.io/badge/dependencies-none%20(stdlib)-brightgreen.svg)

An open, reproducible referee for data-centre water burden: the open-artifact
version of the Ren et al. Water Consumption Impact index (WCI), extended with the
two couplings that framework leaves open. Bands and decompositions, not single
scary numbers; every input named and motive-tagged.

    WCI = C_peak / K = (W/K) * r * PF

## Quick start

    python3 reproduce.py            # print the table + flags + relocation ledger

No installation, no dependencies: Python 3 standard library only. Change any input
in `sites.csv` and re-run. The exit code is non-zero if any row fails the
reproduction check, so it drops straight into CI.

    python3 reproduce.py --tol 0.03 # tighter reproduction tolerance

## Files
- `AI_Water_Tracker_2026-07-11.md` — the working note (paper). Also on Zenodo, [DOI 10.5281/zenodo.21318960](https://doi.org/10.5281/zenodo.21318960).
- `sites.csv` — per-site inputs (operator, location, W, r, PF, K, grid, reservoir, dam, cooling, WUE, EWIF band).
- `reproduce.py` — stdlib. Recomputes WCI, checks it against the cited value,
  flags mismatches, marks reservoir-coupled sites, and prints the off-site
  relocation ledger. No dependencies.
- `SOURCES.md` — motive-tiered source ledger + the current verify targets.
- `powerbi/` — a small SQL analysis layer over the site data (DuckDB, `run_queries.py`), the
  shaping half of a BI project whose Power BI presentation layer is built on the same table.

## Status (2026-07-11, v0 build)
- Layer 1 (WCI reproduced + opened): **working.** 10 Ren seed sites load; 8/10
  reproduce within 5%. Flagged: Microsoft/Wisconsin (22% off) and Google/Mayes
  (6%, borderline) — see SOURCES.md.
- Primary verification: **6/10 clean primary** (all six Google sites). **2/10
  caught as `planning_not_measured`** — Botetourt VA (contracted 2 MGD, online
  ~2028) AND Meta/Lebanon IN (construction began Feb 2026, closed-loop, the
  circulating figures are LEAP-district pipeline capacity not Meta's use). That is
  two of Ren's ten "sites" that are non-operational planning numbers presented as
  measured — a finding, not just a cleanup. **1/10 special case** (Microsoft/
  Wisconsin, Ren's own table inconsistent + zero-water pilot). **1/10 corroborated
  as a range** (xAI/Memphis: W in the 0.81–1.3 MGD current band, 3.7 MGD requested
  ceiling, reuse plant stalled; stays framework_secondary). Round-4 detail in SOURCES.md.
- Layer 2 (hydropower coupling): **ASSERTED on primary sources (2026-07-11).**
  Henderson = STRONG (USBR Jun-2026 24-Month Study: Lake Mead ~1,037 ft end-2026,
  head-dependent Hoover output). The Dalles = REAL but WEAKER (USGS 14105700:
  Columbia ~54% of normal; 1.8 GW dam; but a far more resilient system, no
  min-power-pool threat). Correction banked: Glen Canyon is NOT projected to breach
  min-power-pool in 2026 Most Probable (Powell ~3,504 ft > 3,490). See SOURCES.md.
- Layer 3 (on-site vs off-site relocation ledger): **BUILT.** Off-site share =
  PUE*EWIF / (WUE + PUE*EWIF), a grid-average band per Siddik et al. 2021. Finding:
  evaporative sites relocate ~35-91% of the footprint off-site; **closed-loop sites
  relocate ~92-95%** - "closed-loop = near-zero water" MOVES the water to the grid,
  it does not remove it. Bands + mechanism, never a metered per-site litre count.
- Layer 4 (contamination, Cheyenne / Meta "Goat Systems"): qualitative flag only,
  n=1, not an index term. See spec_v0.md.

## Honest ceilings
- **Altitude is explicit per layer.** *Per-site* applies to the direct WCI (Layer 1,
  6/10 primary-verified); the off-site relocated footprint (Layer 3) is a
  **grid-average bound, not a per-DC meter**; the hydropower coupling (Layer 2) is a
  **cluster/reservoir-level flag**. This is not, and does not claim to be, a metered
  per-site off-site footprint.
- **"Reproducible" = open recomputation, not automated scraping.** `sites.csv` is
  **hand-curated from cited primaries** (operator env reports are non-standardised);
  `reproduce.py` recomputes and self-checks against Ren's cited values. Change an
  input, re-run. Every estimate is motive-tagged in `SOURCES.md`.
- The 3 remaining non-primary rows (2 planning-only + Wisconsin special-case) are
  flagged, not trusted; the reproduction check catches self-inconsistency only.
- The hydropower coupling is a flagged mechanism + directional price transmission,
  never a $/household forecast.

## COI
Anthropic (this author's maker) contracts for AI data centres, so it is non-
neutral on the buildout. All operators are scored the same way. Reproducibility
gives *calculation* transparency; it does not by itself remove seed-selection or
imputation bias, so two guards: the 10 seed sites are **Ren's Table 6, inherited
from the framework paper, not author-chosen**, and every estimate (WUE, EWIF band,
planning-vs-measured tags) is named and motive-tagged in `SOURCES.md`.

## Citation
NM AI Research (2026). *AI Data-Centre Water Tracker: an open, reproducible referee
for data-centre water burden.* Zenodo. https://doi.org/10.5281/zenodo.21318960

## License
CC BY 4.0. See `LICENSE`.
