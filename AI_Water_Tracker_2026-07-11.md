# AI Data-Centre Water Tracker: an open, reproducible referee for data-centre water burden

**NM AI Research** (ORCID 0009-0003-4213-7769) · 11 July 2026 · v0 working note
Repository: `sites.csv` + `reproduce.py` + `SOURCES.md` (stdlib Python, no dependencies) · CC BY 4.0

## Summary

Ren et al. (arXiv 2606.21760, June 2026) define a Water Consumption Impact index (WCI) for AI data centres and apply it to ten sites, but release no code or data and leave two channels open: the coupling between a data centre and the hydropower on its grid, and the off-site relocation of water that "closed-loop" cooling produces. This note ships the open, reproducible version. It rebuilds the WCI from public inputs and checks each recomputed value against the published one; it adds a hydropower-coupling flag asserted on primary reservoir data; and it adds a relocation ledger that quantifies how much of a site's water footprint moves off-site into the electricity supply. The finding that motivates the exercise: closed-loop cooling does not remove water, it relocates roughly 92 to 95 per cent of the footprint to the grid.

Figures are reported with their ranges where they are ranges: the off-site relocation shares are bands, and each per-site WCI is a single reproduced value sitting on an (r, PF) decomposition a reader can vary. Every input is named and motive-tagged. The contribution is the open recomputation and the source ledger, not automated data extraction.

## Scope, stated plainly

The index operates at three altitudes, and the note claims "per-site" only for what is measured per-site:

- **Direct WCI (Layer 1): per-site.** The site's own withdrawal against its host utility's water capacity. Primary-verified for six of ten seed sites.
- **Off-site footprint (Layer 3): a grid-average bound.** Estimated from a regional electricity-water intensity factor, never a metered per-facility litre count.
- **Hydropower coupling (Layer 2): a cluster / reservoir-level flag**, a mechanism with a directional price implication, not a dollar forecast.

## Method (Layer 1)

The index is

    WCI = C_peak / K = (W / K) x r x PF

where W is the average daily water withdrawal (ML/d), K is the host utility's maximum deliverable water capacity (ML/d, not electrical capacity), r is the consumptive ratio (fraction evaporated, dimensionless), and PF is the peaking factor (peak day over average day, dimensionless). W/K is water on water, so the WCI is the dimensionless peak consumptive draw as a fraction of the utility's deliverable water capacity.

`reproduce.py` recomputes the WCI for each row of `sites.csv` and flags any row whose recomputed value disagrees with the source's cited value beyond a 5 per cent tolerance. A flag is an instruction to verify against a primary source, not a number to trust. The seed is Ren et al.'s Table 6, inherited from the framework paper rather than author-selected, which removes site cherry-picking as a bias vector.

## Results

Across the ten seed sites the reproduced WCI spans 0.18 to 1.86, and eight of ten reproduce within 5 per cent. Verification against operator environmental reports and utility open-records upgraded six sites to primary, caught two as non-operational planning figures, isolated one special case, and held one as a range.

| Site | WCI | Status | Off-site share (Layer 3) | Hydropower coupling (Layer 2) |
|---|---|---|---|---|
| Google, Council Bluffs IA | 1.86 | primary | 50–67% | water-only |
| Google, The Dalles OR | 0.18 | primary | 77–91% | water + hydro (Columbia / The Dalles) |
| Google, Douglas Co. GA | 0.42 | primary (reclaimed water) | 55–70% | water-only |
| Google, Midlothian TX | 0.31 | primary | 35–50% | water-only |
| Google, Henderson NV | 0.35 | primary (r unconfirmed) | 57–80% | water + hydro (Lake Mead / Hoover) |
| Google, Mayes Co. OK | 0.42 (cited 0.44) | primary; 6% flag (rounding) | 35–50% | water-only |
| xAI, Memphis TN | 0.58 | range, framework-secondary | 57–70% | water-only |
| Microsoft, Wisconsin | 0.26 (cited 0.34) | special case; 22% flag | 92–95% | water-only |
| Meta, Lebanon IN | 0.77 | planning, not operational | 92–95% | water-only |
| Google, Botetourt Co. VA | 1.43 | planning, not operational | 55–67% | water-only |

Two of Ren et al.'s ten "sites" are non-operational planning figures presented as measured. Botetourt is a contracted 2 MGD reservation for a campus not online until roughly 2028; Lebanon began construction in February 2026 and is a closed-loop design whose circulating water figures are pipeline capacity for the whole LEAP district (2 to 25 MGD phased to 2031), not Meta's metered use. Both are excluded from any measured-WCI reading. The Wisconsin row is internally inconsistent in Ren's own table (its components give 0.26, not the cited 0.34) and is a transitional closed-loop pilot that a static WCI misrepresents. Memphis is a moving multi-site target: the reproduced withdrawal sits inside the real range (Memphis Light, Gas and Water committed 1.3 MGD; current aquifer draw around 0.81 MGD; up to 3.7 MGD requested across two sites), so it is reported as a band, not a point.

## Layer 2: the hydropower coupling

For a site drawing on a reservoir-fed grid, one exogenous drought reaches it through two channels at once: it lowers the reservoir that supplies cooling water, and it cuts the hydropower on the same reservoir, which raises the regional power price. The causal arrow runs from drought to both; the data centre is the exposed party, not the cause. Data-centre water use remains a small fraction of agriculture, and this note does not claim otherwise.

A site is flagged as double-coupled only when it draws from a reservoir that also feeds hydropower and that reservoir carries a primary drought or streamflow signal.

- **Henderson NV, strong.** The USBR June 2026 24-Month Study (Most Probable) projects Lake Mead at about 1,037 feet at year-end 2026, a Level-1 shortage roughly 192 feet below full pool. Hoover Dam's effective generating capacity is head-dependent, so a lower reservoir is simultaneously a water shock and a power-price shock. The site draws Colorado River water.
- **The Dalles OR, real but weaker.** The Columbia at The Dalles (USGS 14105700) has run near 54 per cent of normal in mid-2026, feeding a 1.8 GW dam marketed by the Bonneville Power Administration. The Columbia is a far more resilient system than the Colorado with no minimum-power-pool threat, so this is a directional mechanism rather than acute stress.

A note on a superseded figure: the earlier projection that Glen Canyon Dam would breach its 3,490-foot minimum-power-pool by about August 2026 is retired. The current study's Most Probable run holds Lake Powell near 3,504 feet at year-end 2026, above the line, with Reclamation committed to avoid a decline below 3,500 feet, despite water-year 2026 inflow at 34 per cent of average.

## Layer 3: the relocation ledger

"Closed-loop equals near-zero water" is a claim about on-site cooling only. Per unit of IT energy, the off-site share of the total footprint is

    off-site share = (PUE x EWIF) / (WUE + PUE x EWIF)

which is independent of the site's absolute energy use, so no per-site megawatt figure is required. WUE is the on-site cooling water intensity (about 1.8 L/kWh for evaporative, about 0.2 for closed-loop), EWIF is the grid electricity-water intensity (a grid-average bound), and PUE is fixed at 1.2. The EWIF band per grid is drawn from Siddik, Shehabi and Marston (2021), whose US mean is about 5.1 L/kWh including hydropower reservoir evaporation, with a range from 0 to roughly 85 L/kWh by region.

The result is robust to the exact inputs. Evaporative sites relocate roughly 35 to 91 per cent of their water footprint off-site; closed-loop sites relocate roughly 92 to 95 per cent: the on-site number falls toward zero, but the footprint moves to the grid, it does not vanish. The Dalles sits at 77 to 91 per cent off-site, a consequence of the Columbia grid's high water intensity from hydropower reservoir evaporation, which ties the relocation ledger back to the Layer 2 coupling.

The empirical anchor is Morrison, Strubell et al. (2025, ICLR), who report a 20-million to 13-billion-parameter model series consuming 2.769 million litres of water even on an "extremely water-efficient" data centre, with model development at about half of training. Their finding that training power fluctuates between roughly 15 and 85 per cent of maximum draw is direct support for the peaking factor in the WCI.

## Layer 4: water quality, a flagged channel only

Layers 1 to 3 are quantity channels. A distinct quality channel is flagged but not quantified: construction-phase discharge fouling municipal water before a data centre is operational. In July 2026, Meta's construction entity in Cheyenne, Wyoming discharged the pathogen *Cupriavidus gilardii* into the city's reclaimed-water system during a cooling-loop fill-and-flush; the Board of Public Utilities suspended industrial data-centre wastewater connections area-wide while it cleaned up. The bacterium's origin is unconfirmed. This is kept strictly as a single-case qualitative flag, not an index term and not evidence of a systemic pattern; a second case would be required before it became a layer.

## Honest ceilings

- **Bands, not points.** r, PF and EWIF are ranges; the decomposition is the honest output. Peer-reviewed support: Zhang et al. (2025, NeurIPS, "PCAM") show that deterministic footprint accounting understates spatial and temporal grid variance badly enough that a probabilistic treatment cuts error from about 108 to about 7 per cent.
- **Off-site water is a grid-average bound**, not a per-facility meter.
- **Static-bounds boundary.** This tracker uses grid-average intensities and annual reservoir studies. It does not attempt real-time macro-grid simulation; a dynamic per-balancing-authority EWIF (via the LBL Water IMPACT Tool) is the natural next version.
- **Reproducible means open recomputation, not scraping.** `sites.csv` is manually curated from cited primaries, because operator environmental reports are non-standardised and shift boundaries year on year. The script recomputes and self-checks; anyone can change an input and re-run.
- **Motive-neutral.** Developers' "we are a fraction of agriculture" counter is correct and stays in; the vendor "closed-loop is near-zero water" framing is corrected by Layer 3. The accurate counter is left standing and the overstated one is checked against the same method.

## Positioning against prior work

A literature sweep confirms the gap and narrows it. The nearest neighbour, Morrison, Strubell et al. (2025), is a training-lifecycle telemetry study on the authors' own data centre, a complement and a modern water anchor rather than a per-site public referee of operators' facilities, and it does not address the hydropower coupling. The premise that water is under-reported and off-site matters is now well established, so the contribution here is narrow and specific: an open, reproducible, per-site referee of operators' facilities from public data, plus the two couplings the framework leaves open. The sweep also names an unaddressed gap, the economic impact of regional water pricing on data-centre operating expenditure, which is exactly where the Layer 2 price-transmission channel sits.

## Reproduce

    python3 reproduce.py            # print the table, the flags, and the relocation ledger
    python3 reproduce.py --tol 0.03 # tighten the reproduction tolerance

The exit code is non-zero if any row fails the reproduction check.

## Conflict of interest [1]

## Sources

Primary and public throughout. Operator environmental reports (Google 2025 Environmental Report, FY2024, EY-assured; utility open-records for Mayes and Henderson; Microsoft/DNR filings for Wisconsin); USGS 14105700 (Columbia at The Dalles); USBR Lower and Upper Colorado 24-Month Study (June 2026); Siddik, Shehabi and Marston (2021, Environ. Res. Lett. 16 064017) for EWIF; Morrison, Strubell et al. (2025, ICLR, arXiv 2503.05804) and Zhang et al. (2025, NeurIPS) for the empirical and methodological anchors; Ren et al. (arXiv 2606.21760) as the framework anchor and seed, cited not copied. Full motive-tiered ledger in `SOURCES.md`.

---

[1] The author is assisted by an Anthropic model, and Anthropic contracts for AI data centres, so this work is non-neutral on the buildout. All operators are scored the same way. Reproducibility gives calculation transparency; it does not by itself remove seed-selection or imputation bias, which is why the seed set is Ren et al.'s Table 6 rather than author-chosen and every estimate is named and motive-tagged. Independent analysis and open-science documentation only, not investment advice.
