# AI Data-Centre Water Tracker

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21318960.svg)](https://doi.org/10.5281/zenodo.21318960)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
![Python 3](https://img.shields.io/badge/python-3-blue.svg)
![No dependencies](https://img.shields.io/badge/dependencies-none%20(stdlib)-brightgreen.svg)

*AI disclosure: parts of this text were artificially generated with AI assistance
and reviewed by the author. The models, and the conflicts they create, are named
in the Conflict of interest and scope section.*

An open, reproducible referee for data-centre water burden: the open-artifact
version of the Ren et al. Water Consumption Impact index (WCI), extended with the
two couplings that framework leaves open. Bands and decompositions, not single
scary numbers; every input named and motive-tagged.

    WCI = C_peak / K = (W/K) * r * PF

## Interactive explorer

[Open the AI Data-Centre Water Evidence Explorer](https://nmairesearch.github.io/ai-water-tracker/).

The self-contained page compares FY2024 and FY2025 withdrawal, estimated
consumption, recomputed WCI and modelled off-site water share. Evidence-status
filters keep planning figures separate from measured rows. A conservative
water-source overlay distinguishes potable, reclaimed, surface-water and
groundwater evidence only where the source ledger supports it; all other rows
remain labelled unknown.

The explorer is interactive, not live metering. The dataset remains a dated,
hand-curated snapshot of non-standardised public disclosures.

## Quick start

    python3 reproduce.py            # print the table + flags + relocation ledger

No installation, no dependencies: Python 3 standard library only. Change any input
in `sites.csv` and re-run. The exit code is non-zero if any row fails the
reproduction check. On the seed as shipped it is always non-zero: two of Ren
et al.'s ten rows do not reproduce within tolerance, Mayes at 6% and Wisconsin
at 22%, and those flags are part of the finding rather than a fault to be
cleared.

    python3 reproduce.py --tol 0.03 # tighter reproduction tolerance

## Files
- The working note (paper), v0.5, 8 August 2026. On Zenodo as
  `AI_Water_Tracker_2026-08-08.pdf`, in this repository as the matching `.md`.
  [DOI 10.5281/zenodo.21318960](https://doi.org/10.5281/zenodo.21318960).
- `sites.csv`: per-site inputs (operator, location, W, r, PF, K, grid, reservoir,
  dam, cooling, WUE, EWIF band), FY2024 and FY2025.
- `reproduce.py`: stdlib. Recomputes WCI, checks it against the cited value,
  flags mismatches, marks reservoir-coupled sites, and prints the off-site
  relocation ledger. No dependencies.
- `SOURCES.md`: the source ledger. Per-row sources for all ten sites, the inputs
  that are estimates rather than site measurements, the Layer 2 and Layer 3 sources,
  the tier scheme carried in `sites.csv`, and the known limits.
- `index.html`: dependency-free GitHub Pages explorer with the data embedded.
- `build_tool.py`: regenerates the embedded data from `sites.csv` and
  `water_source_evidence.csv`, or checks that the page is current with `--check`.
- `water_source_evidence.csv`: explicit source classifications only; omission
  means unknown rather than inferred.

## Status (2026-08-08, v0.5)
- Layer 1 (WCI reproduced + opened): working. 10 Ren seed sites load; 8/10
  reproduce within 5%. Flagged: Microsoft/Wisconsin (22% off) and Google/Mayes
  (6%, rounding) see SOURCES.md.
- Primary verification: 6/10 clean primary (all six Google sites, on
  withdrawal and consumptive ratio alike, across two reporting years).
  3/10 caught as `planning_not_measured`, across three different operators:
  Botetourt VA (contracted 2 MGD, online ~2028); Meta/Lebanon IN (construction
  began Feb 2026, closed-loop, the circulating figures are LEAP-district pipeline
  capacity not Meta's use); and Microsoft/Wisconsin, established by the City of
  Racine's own release letter for records request PR2025-343, 17 September 2025,
  which calls the material "estimated water use data" for a campus "currently
  under construction". That is three of Ren's ten "sites" that are non-operational
  planning numbers presented as measured, a finding rather than a cleanup.
  1/10 corroborated as a range (xAI/Memphis: W in the 0.81-1.3 MGD current
  band, 3.7 MGD requested ceiling; stays framework_secondary).
- Layer 1b (second reporting year): NEW in v0.2. Layer 1 stays on FY2024
  because that is what reproduces Ren et al.; Layer 1b recomputes the same index
  on the operators' FY2025 reports with K and PF held constant, so only withdrawal
  and consumptive ratio move. Five of the six primary sites rise 15.6% to 33.3%
  in one reporting year; the measured range widens from 0.18-1.86 to 0.24-2.48.
  Because the denominator is held constant, that is growth in draw against the
  same utility, not a re-estimate of the utility.
- **Douglas Co. GA carries the method point.** Its total withdrawal is flat, down
  0.8%, so its WCI does not move (0.418 to 0.419). Underneath the flat total the
  potable municipal draw rose from 7.4 to 46.3 million gallons, up 526%, while
  reclaimed wastewater fell 9.7%. An index built on total withdrawal cannot see a
  sixfold rise in draw on drinking-water supply. Where an operator publishes the
  split it belongs in its own column. Eemshaven is the candidate second instance.
- Layer 2 (hydropower coupling): ASSERTED on primary sources. Henderson =
  STRONG (USBR Jun-2026 24-Month Study: Lake Mead ~1,037 ft end-2026,
  head-dependent Hoover output). The Dalles = REAL but WEAKER (USGS 14105700:
  Columbia ~54% of normal; 1.8 GW dam; a far more resilient system, no
  min-power-pool threat). Correction banked: Glen Canyon is NOT projected to
  breach min-power-pool in 2026 Most Probable (Powell ~3,504 ft > 3,490).
- Layer 3 (on-site vs off-site relocation ledger): BUILT. Off-site share =
  PUE*EWIF / (WUE + PUE*EWIF), a grid-average band per Siddik et al. 2021.
  Finding: evaporative sites relocate ~35-91% of the footprint off-site;
  closed-loop sites relocate ~92-95%, rounded from a computed 91.5-94.7.
  "Closed-loop = near-zero water" MOVES the water to the grid, it does not
  remove it. The direction holds and the band does not: raising the
  closed-loop WUE from 0.2 to 0.3 L/kWh gives 88-92%, and even at five times
  the assumed WUE the off-site share is still 68-78%. Bands + mechanism,
  never a metered per-site litre count.
- Layer 4 (water quality): qualitative flag only, n=1, not an index term. In July
  2026 Meta's construction entity in Cheyenne, Wyoming discharged *Cupriavidus
  gilardii* into the city's reclaimed-water system during a cooling-loop
  fill-and-flush; the bacterium's origin is unconfirmed. A second case would be
  required before it became a layer.

## Honest ceilings
- **Altitude is explicit per layer.** *Per-site* applies to the direct WCI (Layer 1,
  6/10 primary-verified); the off-site relocated footprint (Layer 3) is a
  grid-average bound, not a per-DC meter; the hydropower coupling (Layer 2) is a
  cluster/reservoir-level flag. This is not, and does not claim to be, a metered
  per-site off-site footprint.
- **The measured set is small and concentrated.** With the three planning rows
  excluded, seven sites remain and six of them are Google. The measured layer is
  close to a single-operator dataset, and its behaviour across two reporting years
  reflects one company's disclosure practice as much as it reflects the sector.
- **"Reproducible" = open recomputation, not automated scraping.** `sites.csv` is
  hand-curated from cited primaries (operator env reports are non-standardised
  and shift boundaries year on year); `reproduce.py` recomputes and self-checks
  against Ren's cited values. Change an input, re-run. Every estimate is named
  in `SOURCES.md` and tagged in the `motive_tier` column of `sites.csv`.
- The 3 planning rows are flagged, not trusted; the reproduction check catches
  self-inconsistency only.
- The hydropower coupling is a flagged mechanism + directional price transmission,
  never a $/household forecast.

## Conflict of interest and scope

The research question, method, sourcing decisions and analytical judgements are
the author's. Anthropic Opus 4.8-5.0 assisted with data retrieval, calculation,
literature search and drafting across v0 through v0.4. OpenAI GPT-5.6 Sol
assisted with the v0.5 disclosure and bundle revision. Parts of this text were
artificially generated and were reviewed by the author before publication. Each
assisting model is not always a neutral party to the subject matter.

Anthropic states that it signed an agreement to use all of the compute capacity at
SpaceX's Colossus 1 data centre (Anthropic, *"Higher usage limits for Claude and a
compute deal with SpaceX"*, 6 May 2026,
[anthropic.com/news/higher-limits-spacex](https://www.anthropic.com/news/higher-limits-spacex)).
OpenAI and Oracle state that they entered an agreement to develop an additional
4.5 GW of Stargate data-centre capacity in the United States (OpenAI, *"Stargate
advances with 4.5 GW partnership with Oracle"*, 22 July 2025,
[openai.com/index/stargate-advances-with-partnership-with-oracle](https://openai.com/index/stargate-advances-with-partnership-with-oracle/)). The author therefore treats neither lab as neutral on the
buildout. All operators are scored the same way. Reproducibility gives
*calculation* transparency; it does not by itself remove seed-selection or
imputation bias, so two guards: the 10 seed sites are Ren's Table 6, inherited
from the framework paper, not author-chosen, and every estimate (WUE, EWIF band,
planning-vs-measured tags) is named in `SOURCES.md` and tagged in `sites.csv`.

Guarantee: every measured claim is traced to the primary document named in the
Verification note, and reproduce.py regenerates both tables from sites.csv.
Modelled or estimated inputs are identified as such in the Verification note
rather than presented as measurements. A reader can check this without
trusting either party.

What the author cannot guarantee: a language model's output can be wrong in ways
that survive review. In prose the error is locally plausible and consistent in
tone with what surrounds it; in code it simply runs, and a wrong constant or a
mis-set filter still returns a clean number. Several methods have been deployed to
mitigate this, including explicit instructions, internal red-teaming and
cross-lab blindspot checks, but the author does not claim the review is
exhaustive. Corrections are logged against the DOI when surfaced.

No warranty is offered beyond the terms of the CC BY 4.0 licence. Independent
analysis and open-science documentation only, not investment advice.

## Citation
NMAI Research (2026). *AI Data-Centre Water Tracker: an open, reproducible referee
for data-centre water burden.* Zenodo. https://doi.org/10.5281/zenodo.21318960

## License
CC BY 4.0. See `LICENSE`.
