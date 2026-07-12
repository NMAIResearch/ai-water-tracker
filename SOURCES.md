# SOURCES — AI Data-Centre Water Tracker

Every input is named and motive-tagged. The reproducibility (change an input,
re-run, watch WCI move) is the contribution, not author trust. See spec_v0.md.

## Tier key
- **primary** — operator environmental report, utility PUC/permit filing, USGS/USBR/EIA gov data.
- **framework_secondary** — taken from Ren et al.'s tables (a framework paper), pending primary verification.
- **vendor** — operator/vendor marketing claim (e.g. NVIDIA closed-loop "300x"); kept but tagged.

## Current seed data (sites.csv)
- **All 10 rows: `framework_secondary`.** Transcribed from Ren et al., "AI Data Centers and the Water Use Feedback Loop", arXiv 2606.21760 (19 Jun 2026), Table 6 + Supplementary Table S5 (K values). These are the seed, NOT yet verified against primary. The point of `reproduce.py` is to check them and to replace each with a primary pull.
  - ⚠️ The seed itself was read from the arXiv HTML by an automated fetch; treat the digits as unverified until a human confirms them against the paper PDF. `reproduce.py`'s internal check is a partial guard only (it catches self-inconsistency, not a wrong-but-consistent row).

## Reproduction-check flags (run 2026-07-11, tol 5%)
- **Microsoft / Wisconsin — 22% off** (recomputed WCI 0.264 vs cited 0.340). Real gap. First verify target: pull W_d and K from a primary Wisconsin PUC filing / Microsoft env report. Likely a transcription error in W_d or K in the seed.
- **Google / Mayes Co., OK — 6% off** (0.415 vs 0.440). Borderline; probably table rounding, but confirm.

## Primary verification log (2026-07-11)
Checked seed rows against operator/utility primary sources. 2 of 10 now `primary`.
- **Google / Council Bluffs, IA — VERIFIED.** Google 2025 Env Report (FY2024): 3.9 M gal/d
  withdrawn, 2.8 M consumed -> r = 0.718 and W ~= 14.8 ML/d. Seed (r 0.716, W 14.62) matches
  within rounding. Row re-tagged `google_fy2024_verified` / `primary`.
- **Google / The Dalles, OR — VERIFIED.** Google FY2024: 461.1 M gal/yr withdrawn, 361.4 M
  consumed (78%) -> r = 0.784 (exact), W = 4.78 ML/d (exact). Row re-tagged `primary`.
- **Microsoft / Wisconsin (Mount Pleasant) — flag explained, NOT yet re-based.** Microsoft/
  DNR/city primary: avg ~15,000 gal/d, peak up to 468,000 gal/d (PF ~= 31), Racine/Lake
  Michigan supply. This is Microsoft's closed-loop *zero-water* pilot (all designs from Aug
  2024). So (a) Ren's row is internally inconsistent (its own W/K/r/PF give WCI 0.264, not the
  cited 0.34 -> a Ren-table error, not ours), and (b) the site is a transitional special case a
  static WCI misrepresents. Leave the seed row flagged; rebuild only with a single dated basis
  (do not mix Ren's K with Microsoft's W). Src: WPR / WisconsinWatch / DCD, 2026.

### Verification round 2 (2026-07-11, remaining Google sites)
- **Google / Mayes Co., OK — VERIFIED.** Utility open-records (The Frontier, Neosho River via
  MidAmerica Industrial Park, Jul 2024-Jun 2025): ~1.1 B gal/yr withdrawn (3.0 MGD = 11.4 ML/d),
  ~253 M gal discharged -> consumed ~0.85 B, r ~= 0.73-0.77. Matches seed W 11.49, r 0.752. The
  6% WCI flag is rounding in Ren's cited value. NB Google's own report cites ~800 M gal for Mayes
  = the *consumed* figure, consistent with the 1.1 B withdrawal. Row -> `primary`.
- **Google / Henderson, NV — W VERIFIED, r NOT.** City of Henderson records (public-records
  request): 352 M gal in 2024 (0.96 MGD = 3.65 ML/d) vs seed 3.73 -> W confirmed. Confirmed it
  draws **Colorado River** water (site broke ground 2019, pre-moratorium) = Layer 2 Hoover
  coupling basis solid (coupling flag upgraded to `Y_source_confirmed`). Seed r = 0.576 is
  unusually LOW for a desert site and is NOT confirmed from a consumption figure -> verify r.
- **Google / Botetourt Co., VA — NOT a measured site.** Seed W 7.57 ML/d = the initial
  **contracted 2 MGD** from the Western Virginia Water Authority agreement (Oct 2025), rising to
  a potential 8 MGD; three buildings ~921k sqft, not operational (online ~2028). The high WCI
  1.45 is a reserved-capacity planning worst-case against a small local system ("reserve 200
  seats, 80 attend"), NOT measured use. Row -> `planning_not_measured`; exclude from any
  measured-WCI headline. Src: Cardinal News / Virginia Business / Roanoke Rambler FOIA, 2026.
### Verification round 3 (2026-07-11, last two Google sites)
- **Google / Midlothian, TX — VERIFIED.** Google 2025 Env Report (FY2024): 182.3 M gal *consumed*.
  Seed W 2.29 ML/d (= 221 M gal/yr withdrawn) x r 0.825 = 182.3 M consumed. Exact. Row -> `primary`.
- **Google / Douglas Co., GA — VERIFIED (reclaimed water).** Google reports 366 M gal evaporated
  (~83% of withdrawals) -> ~440 M gal withdrawn. Seed W 4.60 ML/d (= 444 M gal/yr) and r 0.826
  both land there. NB this site runs on **reclaimed wastewater**, not potable, and the county
  redacted the agreement specifics (WSB-TV FOIA). Row -> `primary`. Src: WSB-TV / Trellis / WABE.

### Verification round 4 (2026-07-11, the 2 non-Google seed sites)
Both resolved via press + NGO + utility reporting (neither operator publishes a Google-style
assured env report). Neither becomes a clean `primary` row; the findings are more useful than that.
- **Meta / Lebanon, IN -> `planning_not_measured` (a SECOND Botetourt).** The campus is NOT
  operational: construction began **Feb 2026** (Daily Journal / Indiana Capital Chronicle, 11-12 Feb
  2026); Meta's own announcement is Feb 2026. Design is **closed-loop, "zero water for the majority
  of the year."** The water figures in circulation are **pipeline / phase capacities for the whole
  LEAP district, not Meta's metered use**: the Citizens-Lebanon supply ramps 2 MGD (2027) -> 10 MGD
  (2028) -> 25 MGD (2031, project complete); a $560M pipe from Eagle Creek Reservoir. Meta pledges
  100% watershed restoration + water-positive by 2030 (Arable/Upper Wabash, ~200 M gal/yr for 10 yr).
  So Ren's 4.81 ML/d row is a **design/planning figure for a non-operational site**, exactly the
  Botetourt error class -> re-tagged `planning_not_measured`, excluded from any measured-WCI headline.
  ⚠️ Also flag for spec review: the Layer-3 anchor "Meta Indiana closed-loop STILL needs 30.3 ML/d
  (8 MGD)" may conflate Ren's K (30.3 ML/d = 8 MGD *capacity*) with need, or reference a different
  Meta Indiana site (New Albany/Jeffersonville) -> verify before it goes in a deliverable.
  Src: Daily Journal / Indiana Capital Chronicle / CNHI (Herald Bulletin, Tribune Star) / about.fb.com, Feb-2026.
- **xAI / Memphis, TN -> stays `framework_secondary`; W corroborated as a RANGE, multi-site moving
  target.** Ren's W 3.79 ML/d = 1.00 MGD sits inside the real spread but a single static row
  misrepresents it (Wisconsin-class caveat):
  - MLGW committed **1.3 MGD** (4.92 ML/d) municipal drinking water to Colossus 1 until a reuse plant is built.
  - Protect Our Aquifer: current draw **~0.81 MGD** (812,502 gal/d = 3.08 ML/d) from the Memphis Sand
    Aquifer; >25 M gal bought from MLGW in March 2026; xAI pays $0.19/100 gal vs $0.32 retail.
  - xAI has **requested up to 3.7 MGD** (14.0 ML/d) across the original + a second site.
  - r 0.77 plausible (open-loop cooling towers evaporate ~85%) but **NOT confirmed** from a consumption figure.
  - The **$80M reuse plant** (13 MGD / 49.2 ML/d of T.E. Maxson effluent, ~70 MGD plant) that was meant
    to drop aquifer draw toward zero is **STALLED**: paused April 2026, restart Q1 2027 (Mayor Young) /
    Q4 2026 (Musk). **Colossus 2** (South Memphis, online Jan 2026) + a planned third site are too far
    to use the reuse water -> more drinking water, not less. Aquifer context: Shelby Co. pumps more than
    is replenished (POA); historic peak pumpage 190 MGD (1974).
  - Keep the row on seed W, tier `framework_secondary`; when it goes in the note, report it as the
    **0.81-1.3 MGD current band + 3.7 MGD requested ceiling**, not a point. Ties MASTER_TRACKER line 243
    (Colossus 1 ~222k GPUs, 300MW+) + line 313 (June-2026 federal class-action vs xAI/SpaceX, Memphis).
  Src: Protect Our Aquifer / Memphis Flyer / Governing / E&E News (POLITICO) / laynemcdonald / Wikipedia, 2026.

## Layer 2 — double-coupling ASSERTED (water + hydropower), 2026-07-11
Both flags upgraded from "geographic proximity" to "mechanism + primary source." The coupling stays
a **flagged mechanism + directional price transmission, NOT a $/household forecast** (honest ceiling).
`double_coupled_candidate` in sites.csv is now `Y_primary` / `Y_source_confirmed`.

- **Google / Henderson, NV — STRONG coupling (Colorado River / Lake Mead / Hoover Dam).** Mechanism
  ASSERTED on a primary: **USBR June-2026 24-Month Study** (Most Probable) projects **Lake Mead ~1,037 ft
  on 31 Dec 2026** (Level-1 Shortage; year-end range ~1,035-1,040 ft), ~192 ft below full pool (1,229 ft).
  Hoover's **effective generating capacity is head-dependent** (USBR: effective capacity set by projected
  Mead elevation); a lower reservoir cuts both SNWA delivery headroom AND Hoover hydro output -> the same
  drought is a water shock AND a regional power-price shock. The site draws Colorado River water (broke
  ground 2019, pre-moratorium), so the water leg is confirmed. Src: USBR Lower Colorado 24-Month Study
  (usbr.gov/lc/region/g4000/24mo.pdf, Jun-2026); shortage tiers per the 2007 Interim Guidelines / 2019 DCP.
- **Google / The Dalles, OR — REAL but WEAKER coupling (Columbia River / The Dalles Dam).** Mechanism
  ASSERTED on a primary streamflow gauge: **USGS 14105700 (Columbia at The Dalles)** shows flow running
  **~54% of normal in mid-2026** (~179k cfs vs a much higher seasonal norm) = a drought signal; The Dalles
  Dam is a **1.8 GW** USACE project (22 units) whose output scales with flow/head, marketed by **BPA**. So
  low Columbia flow -> less Northwest hydro -> tighter regional power market (already stressed by DC load).
  ⚠️ **Honest calibration:** the Columbia is a far larger, more resilient system than the Colorado, with
  **no minimum-power-pool threat**, so this coupling is a real directional mechanism, NOT the acute stress
  Henderson faces. Src: USGS 14105700; BPA historical streamflow (bpa.gov); NOAA 2026 National Hydrologic
  Assessment; USACE The Dalles project page.
- ⛔ **CORRECTION banked for MASTER_TRACKER §3.6 / §RC (flag to N., not yet edited there):** the "Lake
  Powell / Glen Canyon min-power-pool breach ~Aug 2026" line is now **too pessimistic** against the current
  study. The **May/June-2026 24-Month Study (Most Probable)** puts **Powell at ~3,504 ft on 31 Dec 2026**,
  ~14 ft above the **3,490 ft min-power-pool**, and Reclamation states it **"will avoid Powell declining
  below 3,500 ft"** (aided by a 0.66-1.0 maf Flaming Gorge drought-response release), despite WY2026 inflow
  at just **34% of average**. So Glen Canyon hydropower is NOT projected to fail in 2026 Most Probable; the
  binding 2026 event is the **post-2026 rules expiry (1 Oct 2026, 2007 Interim Guidelines)**, already a §RC
  row. Src: USBR Upper Colorado 24-Month Study (usbr.gov/uc/water/crsp/studies/, May/Jun-2026).

## Layer 3 — relocation ledger EWIF sourcing (2026-07-11)
Layer 3 splits each site's footprint into on-site (WUE) and off-site (PUE x EWIF) per unit IT energy; the
off-site *share* is independent of absolute energy, so no per-site MW figure is needed. Inputs + tiers:
- **WUE (on-site cooling water intensity, L/kWh):** class estimates, NOT metered — **evaporative ~1.8**
  (Siddik et al. direct-cooling factor 1.8 m3/MWh), **closed-loop ~0.2** (small make-up only). Assigned per
  site from the cooling type established in the verification log (e.g. Wisconsin + Lebanon = closed-loop;
  the open-loop Google/xAI sites = evaporative, ~85% tower evaporation).
- **EWIF (grid electricity-water intensity, L/kWh):** a **grid-average BOUND, not a per-DC meter.** Anchored
  on **Siddik, Shehabi & Marston 2021** (Environ. Res. Lett. 16 064017, DOI 10.1088/1748-9326/abfba1):
  US mean **~5.1 L/kWh** (INCLUDES hydro reservoir evaporation), range **0 to ~85 L/kWh** by region; SRP
  Arizona example **1.62**. Thermoelectric-only consumptive is lower, **~1.2-1.8 L/kWh** (median 1.22,
  CONUS 234 plants; NREL 1.8 at end-use). Fossil ~2-3, nuclear similar-or-higher, wind/solar ~0, hydro very
  high (reservoir evaporation). Per-grid **lo/hi bands in sites.csv** are set from each region's energy mix
  as a CLASS estimate (SPP/ERCOT wind+solar heavy -> low 0.8-1.5; MISO/Southern/PJM/TVA thermal -> ~1.8-3.5;
  Columbia hydro-dominated -> HIGH 5-15 from reservoir evaporation; Colorado/NV 2-6). For a defensible
  per-balancing-authority value later, the **LBL Water IMPACT Tool** (industrialapplications.lbl.gov) and
  the eGRID-region dataset (IOPscience 10.1088/1748-9326/ab2daa) publish BA-level factors + code.
- **The finding is robust to the exact numbers:** even evaporative sites relocate ~35-91% off-site, and
  closed-loop sites relocate **~92-95%** off-site (`reproduce.py` Layer 3). ⚠️ **Two honest caveats:**
  (a) allocating hydro **reservoir evaporation** to power is contested for multi-use reservoirs, which is
  why The Dalles' high EWIF is a band, not a point; (b) PUE fixed at 1.2 (hyperscale-typical) in the code.
  So Layer 3 is "water relocated, not removed" as a **mechanism + band**, never a metered litre count.

## Comparator tool — EcoLogits (GenAI Impact), water method (checked 2026-07-11)
EcoLogits is the demand-side (per-request) tool we nearly used for the energy work.
How it does water, and why it matters here:
- **Definition matches ours.** Its Water Consumption Factor (WCF) = water *consumed*
  (not returned to source), i.e. the same "consumptive, not withdrawn" basis as our `r`.
- **Same two-component split as our Layer 1 + Layer 3.** Following Li et al. (2025) it sums
  (a) on-site cooling = WUE x water-overhead x compute energy, and (b) off-site electricity
  = EWIF (grid electricity-water-intensity factor) x total energy. That off-site term IS our
  Layer 3 relocation ledger, at the per-token altitude.
- **Same research lineage.** Li et al. is Shaolei Ren's group; our anchor Ren et al. 2606.21760
  is the site-level extension. So EcoLogits (per-request) and this tracker (per-site) are
  consistent framings from one family at two altitudes — a cross-validation, not a rival.
- **It does NOT close the hydropower coupling.** EcoLogits treats electricity-water as an
  additive EWIF term, exactly the additive Scope-2 treatment our Layer 2 exists to replace.
  So its water method confirms Layer 2 is still an open seat.
- **Inherited weakness to note:** EcoLogits' closed-model *energy* is a guesstimate (active-param
  count assumed by analogy; see MASTER_TRACKER 2026-07-08 (4)). Because water = WUE x energy +
  EWIF x energy, that energy error propagates linearly into its water number, on top of WUE/EWIF
  uncertainty. Reliable for open-weight models; a bound, not a measurement, for closed ones.
- Validation point it publishes: vs Mistral Large 2 LCA (Carbone 4 / ADEME, Jul 2025), ~45 mL
  WCF per 400-token page. Water was added to EcoLogits only in Jul 2025.
- Source: ecologits.ai/latest/methodology/ (cite, do not copy).

## Prior-art / literature positioning (CSPaper sweep, verified 2026-07-11)
A semantic-scholar-style sweep of 10 related papers; none owns this tracker's object (open per-site
public-data referee + hydropower coupling + relocation ledger). The two load-bearing citations, both
verified against arXiv / the venue proceedings:
- **Morrison, Na, Fernandez, Dettmers, Strubell, Dodge (2025), "Holistically Evaluating the Environmental
  Impact of Creating Language Models," ICLR 2025 (arXiv 2503.05804; Allen Institute for AI + CMU).** A
  20M-13B-param model series consuming a reported **2.769M L of water** on an "extremely water-efficient"
  DC; **model development ≈50% of training**; training power **fluctuates ~15-85% of max draw** (= empirical
  support for our peaking-factor PF). Nearest neighbour but a *training-lifecycle telemetry* study on the
  authors' own DC = a complement + a modern water anchor, NOT a per-site public referee. Replaces the dated
  Li et al. GPT-3 figure as Layer 3's empirical anchor.
- **Zhang, Fang, Deng, Wang (2025), "Unveiling the Uncertainty in Embodied and Operational Carbon of Large
  AI Models through a Probabilistic Carbon Accounting Model (PCAM)," NeurIPS 2025 (OpenReview; HKUST).**
  Deterministic footprint accounting understates spatial/temporal grid variance so badly that a KDE-based
  probabilistic treatment cuts error from **~108% (LLMCarbon) to ~7%**. Peer-reviewed support for our
  bands-not-points discipline (carbon, but the variance argument transfers to water/EWIF).
- **Gap the sweep names (novelty claim):** "no papers address the economic/financial impact... how regional
  water pricing affects DC operating expenditure" -> exactly where **Layer 2's price-transmission** sits.
- **Boundary the sweep names (scope, not solved):** the field "relies on static datasets, historical bounds,
  retrospective accounting" -> this tracker is in that camp (grid-average EWIF); v-next = dynamic per-BA EWIF.
- Context-only neighbours: DC-cooling RL/MPC (Lazic 2018; Zhan et al. 2025) and utility-flow / hydro-control
  (Smith et al. 2022; Grinberg et al. 2014) - orthogonal method, useful background for Layer 2 only.

## Sources to wire (next, cheapest first)
1. ✅ Ren et al. 2606.21760 — framework anchor + seed (cite, do not copy the conclusion).
2. ✅ Google 2025 Environmental Report (FY2024, EY-assured) — 6/6 Google sites primary-verified.
3. ⬜ One utility PUC/permit filing per flagged site (Wisconsin first) — Wisconsin explained (Ren-table
   inconsistency + zero-water pilot), not yet re-based; the 2 non-Google seeds (Meta/xAI) still open.
4. ~ USGS water-use — used at national/grid level for Layer 3 EWIF; per-site consumptive still from Ren.
5. ✅ USBR 24-Month Study (Jun-2026) — Layer 2 ASSERTED (Mead/Powell). EIA per-dam generation still to add
   if a hard MW-lost figure is ever wanted (mechanism holds without it).
6. ✅ Siddik et al. 2021 — Layer 3 EWIF grid-average bound wired into sites.csv + reproduce.py.

## Still open before a red-team / mint
- The **2 non-Google seed rows** (Meta/Lebanon = planning; xAI/Memphis = range) and **Wisconsin** stay
  un-rebased — documented, not fixed. Fine for v0 (they are flagged, not trusted).
- **EWIF per-balancing-authority** is currently a class band; a v-next could pull LBL Water IMPACT Tool
  BA-level factors to replace the lo/hi estimates.
- **Layer 4** (Cheyenne contamination) stays a qualitative flag, n=1.
- Then: self red-team + the standing independent Gemini pass, then mint as a v0 working note.
