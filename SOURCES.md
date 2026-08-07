# SOURCES: AI Data-Centre Water Tracker

Every input is named and motive-tagged. The reproducibility (change an input,
re-run, watch WCI move) is the contribution, not author trust. See spec_v0.md.

## Verification

Verification: the six Google rows are traced to Google's own environmental reports, FY2024
in the 2025 report and FY2025 in the 2026 report, both independently assured by EY; both
withdrawal and consumptive ratio reproduce against the seed to three decimal places in
FY2024. The Microsoft Wisconsin row is traced to the City of Racine's release letter for
public records request PR2025-343, 17 September 2025, which describes the material as
estimated water use for a campus under construction; the released data table itself has not
been published, so its digits come from Wisconsin Public Radio and Wisconsin Examiner, both
17 September 2025. Meta Lebanon and Google Botetourt rest on the sources named in
verification rounds 2 and 3 above. xAI Memphis rests on Protect Our Aquifer and Memphis
Light, Gas and Water, and is carried as a band. Reservoir and streamflow figures come from
the USBR 24-Month Study (June 2026) and USGS gauge 14105700.

Not measurements: the consumptive ratio of 0.77 assigned to every non-Google row, the
default peaking factors, the EWIF bands and the WUE values are estimates drawn from the
sources named per row, and are tagged as such in the tier column of sites.csv.

## Tier key
- **primary**, operator environmental report, utility PUC/permit filing, USGS/USBR/EIA gov data.
- **framework_secondary**, taken from Ren et al.'s tables (a framework paper), pending primary verification.
- **vendor**, operator/vendor marketing claim (e.g. NVIDIA closed-loop "300x"); kept but tagged.

## Current seed data (sites.csv)
- **All 10 rows: `framework_secondary`.** Transcribed from Ren et al., "AI Data Centers and the Water Use Feedback Loop", arXiv 2606.21760 (19 Jun 2026), Table 6 + Supplementary Table S5 (K values). These are the seed, NOT yet verified against primary. The point of `reproduce.py` is to check them and to replace each with a primary pull.
  - ⚠️ The seed itself was read from the arXiv HTML by an automated fetch; treat the digits as unverified until a human confirms them against the paper PDF. `reproduce.py`'s internal check is a partial guard only (it catches self-inconsistency, not a wrong-but-consistent row).

## Reproduction-check flags (run 2026-07-11, tol 5%)
- **Microsoft / Wisconsin, 22% off** (recomputed WCI 0.264 vs cited 0.340). Real gap. First verify target: pull W_d and K from a primary Wisconsin PUC filing / Microsoft env report. Likely a transcription error in W_d or K in the seed.
- **Google / Mayes Co., OK, 6% off** (0.415 vs 0.440). Borderline; probably table rounding, but confirm.

## Primary verification log (2026-07-11)
Checked seed rows against operator/utility primary sources. 2 of 10 now `primary`.
- **Google / Council Bluffs, IA: VERIFIED.** Google 2025 Env Report (FY2024): 3.9 M gal/d
  withdrawn, 2.8 M consumed -> r = 0.718 and W ~= 14.8 ML/d. Seed (r 0.716, W 14.62) matches
  within rounding. Row re-tagged `google_fy2024_verified` / `primary`.
- **Google / The Dalles, OR: VERIFIED.** Google FY2024: 461.1 M gal/yr withdrawn, 361.4 M
  consumed (78%) -> r = 0.784 (exact), W = 4.78 ML/d (exact). Row re-tagged `primary`.
- **Microsoft / Wisconsin (Mount Pleasant), flag explained, NOT yet re-based.** Microsoft/
  DNR/city primary: avg ~15,000 gal/d, peak up to 468,000 gal/d (PF ~= 31), Racine/Lake
  Michigan supply. This is Microsoft's closed-loop *zero-water* pilot (all designs from Aug
  2024). So (a) Ren's row is internally inconsistent (its own W/K/r/PF give WCI 0.264, not the
  cited 0.34 -> a Ren-table error, not ours), and (b) the site is a transitional special case a
  static WCI misrepresents. Leave the seed row flagged; rebuild only with a single dated basis
  (do not mix Ren's K with Microsoft's W). Src: WPR / WisconsinWatch / DCD, 2026.

### Verification round 2 (2026-07-11, remaining Google sites)
- **Google / Mayes Co., OK: VERIFIED.** Utility open-records (The Frontier, Neosho River via
  MidAmerica Industrial Park, Jul 2024-Jun 2025): ~1.1 B gal/yr withdrawn (3.0 MGD = 11.4 ML/d),
  ~253 M gal discharged -> consumed ~0.85 B, r ~= 0.73-0.77. Matches seed W 11.49, r 0.752. The
  6% WCI flag is rounding in Ren's cited value. NB Google's own report cites ~800 M gal for Mayes
  = the *consumed* figure, consistent with the 1.1 B withdrawal. Row -> `primary`.
- **Google / Henderson, NV: W VERIFIED, r NOT.** City of Henderson records (public-records
  request): 352 M gal in 2024 (0.96 MGD = 3.65 ML/d) vs seed 3.73 -> W confirmed. Confirmed it
  draws **Colorado River** water (site broke ground 2019, pre-moratorium) = Layer 2 Hoover
  coupling basis solid (coupling flag upgraded to `Y_source_confirmed`). Seed r = 0.576 is
  unusually LOW for a desert site and is NOT confirmed from a consumption figure -> verify r.
- **Google / Botetourt Co., VA: NOT a measured site.** Seed W 7.57 ML/d = the initial
  **contracted 2 MGD** from the Western Virginia Water Authority agreement (Oct 2025), rising to
  a potential 8 MGD; three buildings ~921k sqft, not operational (online ~2028). The high WCI
  1.45 is a reserved-capacity planning worst-case against a small local system ("reserve 200
  seats, 80 attend"), NOT measured use. Row -> `planning_not_measured`; exclude from any
  measured-WCI headline. Src: Cardinal News / Virginia Business / Roanoke Rambler FOIA, 2026.
### Verification round 3 (2026-07-11, last two Google sites)
- **Google / Midlothian, TX: VERIFIED.** Google 2025 Env Report (FY2024): 182.3 M gal *consumed*.
  Seed W 2.29 ML/d (= 221 M gal/yr withdrawn) x r 0.825 = 182.3 M consumed. Exact. Row -> `primary`.
- **Google / Douglas Co., GA: VERIFIED (reclaimed water).** Google reports 366 M gal evaporated
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
    **0.81-1.3 MGD current band + 3.7 MGD requested ceiling**, not a point.
    (Colossus 1 ~222k GPUs, 300MW+) + line 313 (June-2026 federal class-action vs xAI/SpaceX, Memphis).
  Src: Protect Our Aquifer / Memphis Flyer / Governing / E&E News (POLITICO) / laynemcdonald / Wikipedia, 2026.

## Layer 2, double-coupling ASSERTED (water + hydropower), 2026-07-11
Both flags upgraded from "geographic proximity" to "mechanism + primary source." The coupling stays
a **flagged mechanism + directional price transmission, NOT a $/household forecast** (honest ceiling).
`double_coupled_candidate` in sites.csv is now `Y_primary` / `Y_source_confirmed`.

- **Google / Henderson, NV: STRONG coupling (Colorado River / Lake Mead / Hoover Dam).** Mechanism
  ASSERTED on a primary: **USBR June-2026 24-Month Study** (Most Probable) projects **Lake Mead ~1,037 ft
  on 31 Dec 2026** (Level-1 Shortage; year-end range ~1,035-1,040 ft), ~192 ft below full pool (1,229 ft).
  Hoover's **effective generating capacity is head-dependent** (USBR: effective capacity set by projected
  Mead elevation); a lower reservoir cuts both SNWA delivery headroom AND Hoover hydro output -> the same
  drought is a water shock AND a regional power-price shock. The site draws Colorado River water (broke
  ground 2019, pre-moratorium), so the water leg is confirmed. Src: USBR Lower Colorado 24-Month Study
  (usbr.gov/lc/region/g4000/24mo.pdf, Jun-2026); shortage tiers per the 2007 Interim Guidelines / 2019 DCP.
- **Google / The Dalles, OR: REAL but WEAKER coupling (Columbia River / The Dalles Dam).** Mechanism
  ASSERTED on a primary streamflow gauge: **USGS 14105700 (Columbia at The Dalles)** shows flow running
  **~54% of normal in mid-2026** (~179k cfs vs a much higher seasonal norm) = a drought signal; The Dalles
  Dam is a **1.8 GW** USACE project (22 units) whose output scales with flow/head, marketed by **BPA**. So
  low Columbia flow -> less Northwest hydro -> tighter regional power market (already stressed by DC load).
  ⚠️ **Honest calibration:** the Columbia is a far larger, more resilient system than the Colorado, with
  **no minimum-power-pool threat**, so this coupling is a real directional mechanism, NOT the acute stress
  Henderson faces. Src: USGS 14105700; BPA historical streamflow (bpa.gov); NOAA 2026 National Hydrologic
  Assessment; USACE The Dalles project page.
- **CORRECTION to an earlier reading of this project's own notes:** the "Lake
  Powell / Glen Canyon min-power-pool breach ~Aug 2026" line is now **too pessimistic** against the current
  study. The **May/June-2026 24-Month Study (Most Probable)** puts **Powell at ~3,504 ft on 31 Dec 2026**,
  ~14 ft above the **3,490 ft min-power-pool**, and Reclamation states it **"will avoid Powell declining
  below 3,500 ft"** (aided by a 0.66-1.0 maf Flaming Gorge drought-response release), despite WY2026 inflow
  at just **34% of average**. So Glen Canyon hydropower is NOT projected to fail in 2026 Most Probable; the
  binding 2026 event is the **post-2026 rules expiry (1 Oct 2026, 2007 Interim Guidelines)**, already a tracked
  row. Src: USBR Upper Colorado 24-Month Study (usbr.gov/uc/water/crsp/studies/, May/Jun-2026).

## Layer 3, relocation ledger EWIF sourcing (2026-07-11)
Layer 3 splits each site's footprint into on-site (WUE) and off-site (PUE x EWIF) per unit IT energy; the
off-site *share* is independent of absolute energy, so no per-site MW figure is needed. Inputs + tiers:
- **WUE (on-site cooling water intensity, L/kWh):** class estimates, NOT metered, **evaporative ~1.8**
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

## Comparator tool: EcoLogits (GenAI Impact), water method (checked 2026-07-11)
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
  consistent framings from one family at two altitudes, a cross-validation, not a rival.
- **It does NOT close the hydropower coupling.** EcoLogits treats electricity-water as an
  additive EWIF term, exactly the additive Scope-2 treatment our Layer 2 exists to replace.
  So its water method confirms Layer 2 is still an open seat.
- **Inherited weakness to note:** EcoLogits' closed-model *energy* is a guesstimate (active-param
  count assumed by analogy). Because water = WUE x energy +
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
1. ✅ Ren et al. 2606.21760, framework anchor + seed (cite, do not copy the conclusion).
2. ✅ Google 2025 Environmental Report (FY2024, EY-assured), 6/6 Google sites primary-verified.
3. ⬜ One utility PUC/permit filing per flagged site (Wisconsin first): Wisconsin explained (Ren-table
   inconsistency + zero-water pilot), not yet re-based; the 2 non-Google seeds (Meta/xAI) still open.
4. ~ USGS water-use, used at national/grid level for Layer 3 EWIF; per-site consumptive still from Ren.
5. ✅ USBR 24-Month Study (Jun-2026): Layer 2 ASSERTED (Mead/Powell). EIA per-dam generation still to add
   if a hard MW-lost figure is ever wanted (mechanism holds without it).
6. ✅ Siddik et al. 2021: Layer 3 EWIF grid-average bound wired into sites.csv + reproduce.py.

## Still open before a red-team / mint
- The **2 non-Google seed rows** (Meta/Lebanon = planning; xAI/Memphis = range) and **Wisconsin** stay
  un-rebased, documented, not fixed. Fine for v0 (they are flagged, not trusted).
- **EWIF per-balancing-authority** is currently a class band; a v-next could pull LBL Water IMPACT Tool
  BA-level factors to replace the lo/hi estimates.
- **Layer 4** (Cheyenne contamination) stays a qualitative flag, n=1.
- Then: self red-team + the standing independent Gemini pass, then mint as a v0 working note.

## Conflict of interest and scope

The research question, method, sourcing decisions and analytical judgements are
the author's. Anthropic Opus 4.8 assisted with data retrieval,
calculation, literature search and drafting. The assisting model is not always
a neutral party to the subject matter.

Guarantee: every anchor claim is traced to the primary document named in the
Verification note, reproduce.py regenerates every table from sites.csv. A
reader can check this without trusting either party.

What the author cannot guarantee: text drafted by a language model can carry
errors that are locally plausible, consistent in tone with the surrounding
prose, and therefore survive review. Several methods have been deployed to
mitigate this, including explicit instructions, internal red-teaming and
cross-lab blindspot checks, but the author does not claim the review is
exhaustive. Corrections are logged against the DOI when surfaced.

No warranty is offered beyond the terms of the CC BY 4.0 licence. Independent
analysis and open-science documentation only, not investment advice.

## Verification round 4 (2026-08-07): the three open rows

Sources for this round: Ren et al., arXiv 2606.21760, Table 6 (p. 16) and Table 4, retrieved
2026-08-07; Google 2025 Environmental Report (FY2024 data) and Google 2026 Environmental Report
(FY2025 data), both from sustainability.google; Wisconsin Public Radio, 17 Sep 2025.

### Google / Henderson, NV: r VERIFIED, row now `primary`
Google 2025 Environmental Report, "Water use by data center location", 2024:
Henderson, NV withdrawal 359.9, discharge 152.5, consumption 207.4 million gallons.
  r = 207.4 / 359.9 = 0.5763 against seed 0.576 (0.05% apart)
  W = 359.9 M gal/yr / 365 = 3.7325 ML/d against seed 3.73 (0.07% apart)
Ren's footnote a states the same provenance: site-specific withdrawal, consumption and PUE
per campus on p. 110, FY2024, independently assured by EY, with r computed as C/W. The seed
is a correct transcription. The earlier "r NOT confirmed" note is closed.
Vintage: Google's 2026 report gives Henderson FY2025 as 401.7 / 162.3 / 239.4 M gal,
i.e. W 4.166 ML/d and r 0.5960. Re-basing the tracker to FY2025 is a separate decision and
would move all six Google rows, not this one.

### Microsoft / Wisconsin (Mount Pleasant): the 22% flag is a CLASS error, not a transcription error
Ren Table 6 sources this row to Wisconsin Public Radio [44] and Han et al. §3.1.2, and
footnote f identifies the site as Mount Pleasant / Racine County.
WPR, 17 Sep 2025, reporting records released by the City of Racine: phase 1 peak
234,000 gal/day or 2.8 M gal/year; subsequent phases peak 702,000 gal/day or 8.4 M gal
annually.
  8,442,000 gal/yr / 365 = 23,129 gal/d = 0.0876 ML/d against seed 0.087 (0.6% apart)
So W_d is the projected FULL-BUILDOUT ANNUAL AVERAGE for phases that are not built, taken
from a utility records release, not a measurement at an operating site. Two of the other
three inputs are also not site-measured: r = 0.77 is the assigned non-Google default
(Ren footnote b, weighted mean from Han et al. App. A.5) and PF = 30 comes from Han et al.
Microsoft's own operating figure, via Wisconsin DNR water use section manager Adam
Freihoefer, is roughly 15,000 gal/day average (0.0568 ML/d) and 468,000 gal/day on the
hottest days (1.77 ML/d), a closed-loop profile that the annual-average row cannot represent.
=> Same error class as Botetourt and Lebanon. Proposed re-tag: `planning_not_measured`,
excluded from any measured-WCI headline. PRIMARY STILL OUTSTANDING: the City of Racine
records themselves. WPR is coverage of them and names the figures, but the release document
has not been retrieved.

### Meta / Lebanon, IN: the Layer-3 anchor is a conflation, and it inverts the source
The tracker's anchor reads "Meta Indiana closed-loop STILL needs 30.3 ML/d (8 MGD)".
Ren Table 4 lists Lebanon under "Infrastructure constraint mechanisms", capacity bottleneck:
"30.3 ML/d (8 MGD) not available until 2031; multi-year capacity expansion", consequence
"6+ year delay". Footnote d: current-phase intake 4.81 ML/d (1.27 MGD) from Han et al.
App. D recomputation, "phased buildout to 30.3 ML/d (8 MGD) by 2031 per City of Lebanon,
Indiana".
So 30.3 ML/d is the CITY's phased supply capacity with a 2031 delivery date, not Meta's
requirement. Ren uses it as evidence of a constraint on the buildout; the anchor uses it as
evidence of demand. => Do not carry the anchor as written.

### Carried forward from this round
- Ren marks Lebanon's W_d with the "value derived analytically in an upstream source rather
  than measured directly at the site" symbol, consistent with the existing
  `planning_not_measured` re-tag.
- r = 0.77 is an assigned default on every non-Google row (Meta, Microsoft, xAI, Botetourt),
  not a site measurement.
- xAI / Memphis: Ren sources W_d to Protect Our Aquifer [97]; PF 4.5 is the warm-climate
  default; r is the 0.77 assignment.

### Microsoft / Wisconsin: PRIMARY OBTAINED for the class, not for the digits (2026-08-07)
City of Racine, Office of the City Attorney, letter re Public Records Request PR2025-343,
17 September 2025, Assistant City Attorney Ian R. Pomplin, to Cheryl Nenn (Milwaukee
Riverkeeper) and Attorney Michael Griefe (Midwest Environmental Advocates).
Hosted at midwestadvocates.org/wp-content/uploads/PR2025-343-Release-Cover-Letter.pdf
Request scope, quoted: "estimated water use at the Microsoft data center currently under
construction in the Village of Mount Pleasant".
Nature of the data, quoted: "estimated water use data that had been provided to the City of
Racine Water Utility".
Release history, quoted: "This release was delayed due to Microsoft Corporation raising an
objection regarding the application of the Uniform Trade Secrets Act to estimated water use
data ... That objection has been withdrawn".
=> The figures are operator-supplied ESTIMATES for a site under construction, on the City's
own record. This is primary evidence for the `planning_not_measured` class, independent of
the digits.
Companion filing: Racine-PRR-Summons-Complaint-9.15.25.pdf (MEA on behalf of Milwaukee
Riverkeeper, filed 15 Sep 2025, seven months after the February 2025 request).
STILL OUTSTANDING: the attached data table itself. Not in the cover letter and not posted by
MEA. The 234,000 / 2.8 M and 702,000 / 8.4 M gallon figures rest on Wisconsin Public Radio
(Danielle Kaeding, 17 Sep 2025) and Wisconsin Examiner (Henry Redman, 17 Sep 2025), two
outlets reporting the same release on the same day.

### Vintage flag (2026-08-07)
Google 2026 Environmental Report carries FY2025 site-level water. PDF CreationDate 24 June
2026, ModDate 10 July 2026; this tracker published 12 July 2026 on FY2024 figures. FY2025
values for the six Google rows, withdrawal M gal/yr and r = C/W:
  Council Bluffs, IA  1,746.4  r 0.7707     (FY2024: 14.62 ML/d, r 0.716)
  The Dalles, OR        654.3  r 0.7168
  Douglas County, GA    440.6  r 0.8332
  Henderson, NV         401.7  r 0.5960
  Bristow, VA           359.6  r 0.7442
  Ashburn, VA            76.5  r 0.6954
Re-basing to FY2025 moves all six rows and is a version decision, not a correction.

### Wisconsin Examiner, exact wording (capture reviewed 2026-08-07)
Henry Redman, Wisconsin Examiner, 17 September 2025, 3:19 pm, quoted verbatim:
  "According to the Racine projections, the first phase of operations on the data center
  campus would use a peak of 234,000 gallons per day or 2.8 million gallons per year. In
  later phases, as more substations go online, the campus would use 702,000 gallons per day
  or 8.4 million gallons per year."
Two points this fixes. The outlet calls them "the Racine projections" in its own voice,
corroborating the City Attorney letter's "estimated water use data". And the later phases
are tied to substations coming online, not to a date, so the 8.4 M gal figure is contingent
on electrical buildout rather than on calendar time.
The saved capture contains no source document (one HTML part, 33 CSS, 7 images, no PDF), so
it is coverage, not the released table.

### v0.2 build, FY2025 re-base (2026-08-07)
Layer 1 stays on FY2024 because it reproduces Ren et al. against the inputs they used.
Layer 1b recomputes the same index on FY2025 inputs from Google's 2026 Environmental Report,
holding K and PF constant, so the change is withdrawal and consumptive ratio only.

FY2024 seed check, all six Google rows against Google 2025 Environmental Report (FY2024):
  Council Bluffs 14.626 vs seed 14.62, r 0.7163 vs 0.716
  Mayes Co.      11.494 vs seed 11.49, r 0.7518 vs 0.752
  The Dalles      4.782 vs seed 4.78,  r 0.7838 vs 0.784
  Douglas Co.     4.606 vs seed 4.60,  r 0.8262 vs 0.826
  Midlothian      2.292 vs seed 2.29,  r 0.8249 vs 0.825
  Henderson       3.733 vs seed 3.73,  r 0.5763 vs 0.576
All six reproduce. The Google half of the seed is primary-verified in full.

Movement FY2024 to FY2025, WCI:
  Council Bluffs 1.859 -> 2.479  +33.3%
  Mayes Co.      0.415 -> 0.539  +29.8%
  The Dalles     0.182 -> 0.237  +29.8%
  Douglas Co.    0.418 -> 0.419   +0.2%
  Midlothian     0.313 -> 0.378  +20.9%
  Henderson      0.353 -> 0.408  +15.6%
Measured set, 7 rows after the Microsoft re-tag: FY2024 range 0.182 to 1.859,
FY2025 range 0.237 to 2.479.

### The Douglas County exception: the total hides the change
Google reports the source split for this site.
  FY2024 total 444.1 M gal = potable 7.4 + reclaimed wastewater 436.7
  FY2025 total 440.6 M gal = potable 46.3 + reclaimed wastewater 394.3
Total withdrawal is flat at -0.8%, which is why its WCI barely moves. Underneath, draw on
POTABLE municipal supply rose from 7.4 to 46.3 M gal, +525.7%, while reclaimed fell 9.7%.
A WCI computed on total withdrawal cannot see this. Consequence for the method: where an
operator reports the potable / reclaimed split, carry it as its own column; the substitution
away from reclaimed supply is a distinct signal from total volume.
Eemshaven, Netherlands reports the same style of split (3.6 potable, 528.6 non-potable in
FY2025) and is a candidate second instance if the site set widens.

### Microsoft / Wisconsin re-tagged to `planning_not_measured` (decision 2026-08-07)
Basis: City of Racine PR2025-343 letter (operator-supplied estimates, site under
construction), Wisconsin Examiner "the Racine projections", W_d = full-buildout annual
average / 365, r and PF both assigned defaults rather than site measurements.
Effect on Layer 1 output: one word, FLAG to PLANNING. WCI range, reproduction count,
Layer 2 and Layer 3 all unchanged. The row remains in the FLAGGED list because it still
does not reproduce against the cited value.
Consequence to state in the paper: the measured set is now 7 rows, 6 of them Google.
