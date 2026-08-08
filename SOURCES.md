# Sources: AI Data-Centre Water Tracker

*AI disclosure: parts of this text were artificially generated with AI assistance
(Anthropic Opus 4.8-5.0) and reviewed by the author. Full note at the end.*

Every input in `sites.csv` is named here and tagged by the standing of its source, so a
reader can change an input, re-run `reproduce.py`, and see the index move. The point is
open recomputation rather than author trust.

## Tier key

- **primary**, operator environmental report, utility filing or open-records release, or
  government data (USGS, USBR, EIA).
- **framework_secondary**, taken from Ren et al.'s tables pending primary verification.
- **planning_not_measured**, a contracted, projected or full-buildout figure for a site that
  is not operating. Excluded from any measured reading of the index.

Each row of `sites.csv` carries these tags in two columns. `motive_tier` holds the standing
above and is the only tag `reproduce.py` reads, because it drives the planning exclusions.
`source_tag` is a short label for the document the row rests on, for example
`google_fy2024_verified`, `utility_openrecords_2024_verified` or
`contracted_2MGD_NOT_operational`.

## Seed

All ten rows originate in Ren et al., "AI Data Centers and the Water Use Feedback Loop",
arXiv 2606.21760, 19 June 2026, Table 6 with capacity values from Supplementary Table S5.
The seed set is inherited from that paper rather than author-selected, which removes site
selection as a bias vector. Figures below are the verification of that seed, not a copy of it.

## Per-row sources

| Site | Withdrawal and consumptive ratio | Tier |
|---|---|---|
| Google, Council Bluffs IA | Google 2025 Environmental Report (FY2024), 3.9 M gal/d withdrawn and 2.8 M consumed, r 0.718; 2026 report (FY2025) 1,746.4 M gal/yr, r 0.7707 | primary |
| Google, The Dalles OR | Google 2025 Environmental Report (FY2024), 461.1 M gal/yr withdrawn, 361.4 M consumed, r 0.784; 2026 report (FY2025) 654.3 M gal/yr, r 0.7168 | primary |
| Google, Douglas Co. GA | Google 2025 Environmental Report (FY2024), 366 M gal evaporated on roughly 440 M withdrawn, r 0.826; 2026 report (FY2025) 440.6 M gal/yr, r 0.8332. Site runs on reclaimed wastewater | primary |
| Google, Midlothian TX | Google 2025 Environmental Report (FY2024), 182.3 M gal consumed on 221 M withdrawn, r 0.825 | primary |
| Google, Henderson NV | Google 2025 Environmental Report (FY2024), 359.9 M gal withdrawn, 152.5 discharged, 207.4 consumed, r 0.5763; 2026 report (FY2025) 401.7 / 162.3 / 239.4 M gal, r 0.5960. Corroborated by City of Henderson open records, 352 M gal in 2024 | primary |
| Google, Mayes Co. OK | Utility open records for the MidAmerica Industrial Park intake on the Neosho River, July 2024 to June 2025, roughly 1.1 B gal/yr withdrawn against roughly 253 M gal discharged, r 0.73 to 0.77 | primary |
| Microsoft, Wisconsin | City of Racine, Office of the City Attorney, release letter for public records request PR2025-343, 17 September 2025, describing "estimated water use data" for a campus "currently under construction". The released data table is unpublished; the figures come from Wisconsin Public Radio and Wisconsin Examiner, both 17 September 2025 | planning_not_measured |
| Meta, Lebanon IN | Daily Journal and Indiana Capital Chronicle, 11 to 12 February 2026, for a February 2026 construction start. Circulating water figures are the Citizens-Lebanon supply ramp for the whole LEAP district, 2 MGD in 2027 to 25 MGD by 2031, not a Meta requirement | planning_not_measured |
| Google, Botetourt Co. VA | Western Virginia Water Authority agreement, October 2025, a contracted 2 MGD reservation rising to a potential 8 MGD for a campus not operating until roughly 2028. Reported by Cardinal News, Virginia Business and a Roanoke Rambler records request | planning_not_measured |
| xAI, Memphis TN | Protect Our Aquifer for current draw of roughly 0.81 MGD from the Memphis Sand Aquifer; Memphis Light, Gas and Water for a committed 1.3 MGD; up to 3.7 MGD requested across two sites. Carried as a band rather than a point | framework_secondary |

## Inputs that are not site measurements

- **Consumptive ratio on every non-Google row.** r = 0.77 is an assigned default, from Ren
  et al.'s footnote b and a weighted mean in Han et al., not a measurement at Meta,
  Microsoft, xAI or Botetourt.
- **Peaking factors.** None is a site measurement. The values carried in `sites.csv` are
  2.21 at The Dalles; 2.5 at Mayes, Douglas, Midlothian, Henderson and Botetourt; 4.5 at
  Memphis, a warm-climate default; 6.3 at Lebanon; 6.5 at Council Bluffs; and 30 at
  Microsoft Wisconsin, from Han et al.
- **WUE, on-site cooling water intensity.** Class estimates by cooling type, roughly
  1.8 L/kWh evaporative and 0.2 closed-loop, assigned from the cooling type established per
  site. Not metered.
- **EWIF, grid electricity-water intensity.** A grid-average bound, never a per-facility
  meter. The low and high bands are class estimates set from each region's generation mix,
  and are the values carried in `sites.csv`:

  | Grid region | EWIF band, L/kWh | Basis |
  |---|---|---|
  | SPP Oklahoma, ERCOT Texas | 0.8 to 1.5 | wind and solar heavy |
  | MISO Iowa | 1.5 to 3.0 | mixed thermal |
  | MISO Indiana, MISO Wisconsin, PJM Dominion Virginia | 1.8 to 3.0 | thermal |
  | Southern Company Georgia | 1.8 to 3.5 | thermal |
  | TVA Tennessee | 2.0 to 3.5 | thermal |
  | Colorado River, Nevada | 2.0 to 6.0 | mixed, some reservoir evaporation |
  | Columbia River | 5.0 to 15.0 | hydropower dominated, reservoir evaporation |

## Layer 2, the hydropower coupling

A site is flagged only where it draws from a reservoir that also feeds hydropower and that
reservoir carries a primary drought or streamflow signal.

- **Henderson NV.** USBR Lower Colorado 24-Month Study, June 2026, Most Probable, projects
  Lake Mead at about 1,037 feet on 31 December 2026, roughly 192 feet below full pool.
  Hoover Dam's effective generating capacity is head-dependent, so the same drought is a
  water shock and a power-price shock.
- **The Dalles OR.** USGS gauge 14105700 shows the Columbia running near 54 per cent of
  normal in mid-2026, feeding a 1.8 GW USACE project marketed by the Bonneville Power
  Administration. The Columbia is a far more resilient system than the Colorado with no
  minimum-power-pool threat, so this is a directional mechanism rather than acute stress.
- **Superseded figure.** An earlier projection that Glen Canyon Dam would breach its
  3,490-foot minimum power pool by about August 2026 is retired. The current Upper Colorado
  24-Month Study Most Probable run holds Lake Powell near 3,504 feet at year-end 2026, with
  Reclamation committed to avoiding a decline below 3,500 feet, despite water-year 2026
  inflow at 34 per cent of average.

## Layer 3, the relocation ledger

Off-site share = PUE x EWIF / (WUE + PUE x EWIF), with PUE fixed at 1.2. The share is
independent of a site's absolute energy use, so no per-site megawatt figure is required.

EWIF is anchored on Siddik, Shehabi and Marston (2021), Environmental Research Letters 16
064017, doi:10.1088/1748-9326/abfba1: a US mean of about 5.1 L/kWh including hydropower
reservoir evaporation, with a range from 0 to roughly 85 L/kWh by region.

**The direction holds and the band does not.** Evaporative sites relocate roughly 35 to 91
per cent off-site and closed-loop sites roughly 92 to 95 per cent, rounded from a computed
91.5 to 94.7. Raising the closed-loop WUE from 0.2 to 0.3 L/kWh gives 88 to 92 per cent, and
taking the low EWIF from 1.8 to 1.0 gives 86 per cent. What survives every perturbation is
the conclusion rather than the band: even at five times the assumed WUE the off-site share
is still 68 to 78 per cent. Withdrawn 2026-08-07: the earlier claim that the finding is
robust to the exact numbers.

Three caveats sit on this layer. Allocating hydropower reservoir evaporation to power is
contested for multi-use reservoirs, which is why The Dalles' high EWIF is a band rather than
a point. PUE is fixed at 1.2 in the code. And WUE is a class estimate per cooling type, not
a site measurement, and it is the input the band is most sensitive to.

## Empirical and methodological anchors

- Morrison, Na, Fernandez, Dettmers, Strubell and Dodge (2025), "Holistically Evaluating the
  Environmental Impact of Creating Language Models", ICLR 2025, arXiv 2503.05804. Reports a
  20-million to 13-billion-parameter model series consuming 2.769 million litres of water on
  an "extremely water-efficient" data centre, with model development at about half of
  training, and training power fluctuating between roughly 15 and 85 per cent of maximum
  draw, which is empirical support for the peaking factor.
- Zhang, Fang, Deng and Wang (2025), "Unveiling the Uncertainty in Embodied and Operational
  Carbon of Large AI Models through a Probabilistic Carbon Accounting Model", NeurIPS 2025.
  Deterministic footprint accounting understates spatial and temporal grid variance badly
  enough that a probabilistic treatment cuts error from about 108 to about 7 per cent. The
  argument is made on carbon and transfers to the water and EWIF bands here.

## Known limits

- Three rows are planning figures and one is a range. All four are flagged, not trusted, and
  none enters the measured set.
- With those excluded the measured set is seven rows, six of them Google, so its behaviour
  across two reporting years reflects one company's disclosure practice as much as the
  sector's.
- EWIF is a class band per grid. A per-balancing-authority value would be a stronger basis;
  the LBL Water IMPACT Tool and the eGRID-region dataset (doi:10.1088/1748-9326/ab2daa)
  publish factors and code at that resolution.
- The Microsoft Wisconsin data table released to the City of Racine has not been published,
  so its digits rest on two outlets reporting the same release on the same day.
- Henderson's consumptive ratio is confirmed against Google's reported consumption figure;
  the ratios on non-Google rows are not.
- Layer 4, the Cheyenne contamination episode, is a single-case qualitative flag and not an
  index term.

## Verification

Every per-site withdrawal and consumptive ratio for the six Google rows is traced to
Google's own environmental reports, FY2024 in the 2025 report and FY2025 in the 2026 report,
both independently assured by EY. The Microsoft Wisconsin row is traced to the City of
Racine release letter for public records request PR2025-343. Botetourt, Lebanon and Memphis
rest on contract documents and reporting rather than an operator's assured disclosure, which
is why all three are excluded from the measured set. Reservoir and streamflow figures come
from the USBR 24-Month Study and USGS gauge 14105700. The EWIF bands, the WUE class values,
the peaking factors and the consumptive ratios assigned to non-Google operators are
estimates rather than site measurements, and are tagged as such in `sites.csv`.

## Version history

- **v0.4 (8 August 2026).** Disclosure only. No figure, table, finding or input changed. The
  AI-assistance disclosure moves to the front of this ledger and uses the wording of the EU
  AI Act Article 50(4) transparency duty.
- **v0.3 (7 August 2026).** No figure, table or finding changed. This ledger was rebuilt as a
  per-row source table; the round-by-round working trail behind it is kept separately and is
  available on request. The claim that the Layer 3 finding is robust to the exact numbers was
  withdrawn and replaced by the sensitivity above.
- **v0.2 (7 August 2026).** Added Layer 1b, the FY2025 re-base with capacity and peaking held
  constant. Re-tagged Microsoft Wisconsin as planning rather than measured, taking the
  planning rows to three across three operators.
- **v0 (12 July 2026, record 10.5281/zenodo.21318961).** First public version.

## Conflict of interest and scope

The research question, method, sourcing decisions and analytical judgements are
the author's. Anthropic Opus 4.8-5.0 assisted with data retrieval, calculation,
literature search and drafting, so parts of this text were artificially generated
and were reviewed by the author before publication. The assisting model is not
always a neutral party
to the subject matter: Anthropic contracts for AI data centres, so this work is
non-neutral on the buildout. All operators are scored the same way.

Guarantee: every measured claim is traced to the primary document named in the
Verification note, and reproduce.py regenerates both tables from sites.csv.
Modelled or estimated inputs are identified as such in the Verification note
rather than presented as measurements. A reader can check this without
trusting either party.

What the author cannot guarantee: a language model's output can be wrong in ways
that survive review. In prose the error is locally plausible and consistent in
tone with what surrounds it; in code it simply runs, and a wrong constant or a
mis-set filter still returns a clean number. Several methods have been deployed to
mitigate this, including explicit instructions, internal red-teaming and cross-lab
blindspot checks, but the author does not claim the review is exhaustive.
Corrections are logged against the DOI when surfaced.

No warranty is offered beyond the terms of the CC BY 4.0 licence. Independent
analysis and open-science documentation only, not investment advice.
