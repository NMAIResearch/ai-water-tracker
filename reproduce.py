#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reproduce.py - open, reproducible referee for data-centre water burden.

Rebuilds Ren et al.'s Water Consumption Impact index (WCI) from public per-site
inputs and ships the code the framework paper (arXiv 2606.21760) does not.

    WCI = C_peak / K = (W/K) * r * PF

    W  = average daily withdrawal            (ML/d)
    K  = host utility max deliverable capacity (ML/d)
    r  = consumptive ratio (fraction evaporated)
    PF = peaking factor (peak-day / average-day)

Layer 1  recompute WCI from components and CHECK it against the value the
         source reported (stated_WCI). A row whose recomputed WCI disagrees
         with the stated value beyond tolerance is FLAGGED: it is the first
         thing to verify against a primary source, not a number to trust.
Layer 2  flag sites double-coupled to a reservoir-fed grid (water + hydropower),
         where the same drought that lowers the reservoir also cuts hydropower.
         A flagged mechanism, not a price forecast.
Layer 3  the relocation ledger: split each site's water footprint into ON-SITE
         (cooling) and OFF-SITE (the water the grid electricity carries), to show
         that "closed-loop = near-zero water" RELOCATES water off-site, it does
         not remove it. Per unit of IT energy:
             on-site  = WUE               (L/kWh, ~1.8 evaporative, ~0.2 closed-loop)
             off-site = PUE * EWIF         (L/kWh, EWIF = grid electricity-water factor)
             off-site share = off / (on + off)      [independent of absolute energy]
         EWIF is a grid-average BAND, not a per-DC meter (Siddik et al. 2021: US
         mean ~5.1 L/kWh incl. hydro reservoir evaporation, ~1.2-1.8 thermoelectric
         only, 0 to ~85 by region). WUE by cooling class is an estimate. So Layer 3
         is a reproducible band + mechanism, never a metered per-site litre count.

Bands, not point numbers: r and PF are ranges in reality; a single figure is a
convenience, the decomposition is the honest output. Stdlib only.

Usage:
    python3 reproduce.py                 # read sites.csv, print the table
    python3 reproduce.py --tol 0.03      # tighten the reproduction tolerance (rel.)
    python3 reproduce.py --csv other.csv

Exit code is 1 whenever a row is flagged. On the seed as shipped that is always:
two of Ren et al.'s ten rows do not reproduce within tolerance (Mayes at 6 per
cent, Wisconsin at 22 per cent). The flags are part of the finding, not a fault
to be cleared.

Disclosure: this script was written with the assistance of Anthropic Opus
4.8-5.0. A language model's output can be wrong in ways that survive review; in
code it simply runs, and a wrong constant or a mis-set filter still returns a
clean number. The method it implements, and the sourcing of every input it
reads, are set out in the working note and in SOURCES.md, so the arithmetic here
can be checked against them rather than trusted. CC BY 4.0.
"""
import argparse
import csv
import sys

DEFAULT_TOL = 0.05  # 5% relative: within here we call the row "reproduced"
PUE_DEFAULT = 1.2   # power usage effectiveness: total facility energy / IT energy


def wci(W, K, r, PF):
    """WCI = (W/K) * r * PF. Returns None if capacity is missing/zero."""
    if not K:
        return None
    return (W / K) * r * PF


def offsite_share(WUE, EWIF, PUE=PUE_DEFAULT):
    """Layer 3: fraction of the water footprint that sits OFF-SITE (carried by
    the grid electricity), per unit of IT energy. Independent of absolute energy:
        on-site  = WUE            (L/kWh)
        off-site = PUE * EWIF     (L/kWh)
        share    = off-site / (on-site + off-site)
    Returns None if inputs are missing."""
    if WUE is None or EWIF is None:
        return None
    off = PUE * EWIF
    total = WUE + off
    if total == 0:
        return None
    return off / total


def rel_gap(a, b):
    """Relative gap of a vs reference b; None if b missing/zero."""
    if b in (None, 0):
        return None
    return abs(a - b) / b


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(row, key):
    v = (row.get(key) or "").strip()
    if v == "":
        return None
    return float(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reproduce Ren et al. WCI, open.")
    ap.add_argument("--csv", default="sites.csv")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL,
                    help="relative tolerance for the reproduction check")
    args = ap.parse_args(argv)

    rows = load(args.csv)
    flagged, coupled, computed = [], [], []

    hdr = ("operator", "location", "W/K", "r", "PF",
           "WCI(calc)", "WCI(cited)", "gap", "check", "coupling")
    widths = (10, 20, 6, 6, 5, 9, 9, 6, 7, 22)
    line = "  ".join(h.ljust(w) for h, w in zip(hdr, widths))
    print(line)
    print("-" * len(line))

    for row in rows:
        W, K = num(row, "W_d_ML_d"), num(row, "K_ML_d")
        r, PF = num(row, "r"), num(row, "PF")
        stated = num(row, "stated_WCI")

        if None in (W, K, r, PF):
            calc = None
            check = "NO-INPUT"
        else:
            calc = wci(W, K, r, PF)
            computed.append(calc)
            gap = rel_gap(calc, stated)
            if stated is None:
                check = "no-cite"
            elif gap is not None and gap <= args.tol:
                check = "ok"
            else:
                check = "FLAG"
                flagged.append((row, calc, stated, gap))

        # Planning/non-operational rows: WCI is a reserved-capacity figure, not
        # a measurement. Mark it so it is never read as a measured value.
        tier = (row.get("motive_tier") or "").strip().lower()
        if tier.startswith("planning"):
            check = "PLANNING"

        # Layer 2: reservoir-fed grid double-coupling
        dc = (row.get("double_coupled_candidate") or "").strip()
        if dc.upper().startswith("Y"):
            res = (row.get("reservoir") or "?").strip()
            dam = (row.get("dam") or "?").strip()
            coupling = "water+hydro:%s/%s" % (res, dam)
            coupled.append(row)
        else:
            coupling = "water-only"

        gap = rel_gap(calc, stated) if calc is not None else None
        cells = (
            (row.get("operator") or "")[:10],
            (row.get("location") or "")[:20],
            "%.3f" % (W / K) if (W and K) else "-",
            "%.3f" % r if r is not None else "-",
            "%.2f" % PF if PF is not None else "-",
            "%.3f" % calc if calc is not None else "-",
            "%.3f" % stated if stated is not None else "-",
            "%.1f%%" % (gap * 100) if gap is not None else "-",
            check,
            coupling,
        )
        print("  ".join(str(c).ljust(w) for c, w in zip(cells, widths)))

    print("-" * len(line))
    if computed:
        print("WCI range across %d computed sites: %.3f - %.3f"
              % (len(computed), min(computed), max(computed)))
    print("Reproduced within %.0f%%: %d/%d rows"
          % (args.tol * 100, len(computed) - len(flagged), len(computed)))

    # Layer 1b: vintage movement. Layer 1 above reproduces Ren et al. against the FY2024
    # inputs they used, and stays on FY2024 for that reason. This layer recomputes the same
    # index on FY2025 inputs from the operator's own report and reports the change. Only
    # rows carrying W_d_2025_ML_d participate. Rows tagged planning_not_measured are
    # excluded from the measured range in both years.
    #
    # A measured row with no FY2025 figure is held at its FY2024 value in the FY2025
    # range rather than dropped, so both ranges cover the same set of sites. Only the
    # six Google rows are actually re-based; xAI Memphis has no FY2025 disclosure and
    # is carried forward. The count of re-based rows is printed below so the FY2025
    # range is not read as seven fresh values.
    moved, meas_24, meas_25 = [], [], []
    for row in rows:
        K, PF = num(row, "K_ML_d"), num(row, "PF")
        w24, r24 = num(row, "W_d_ML_d"), num(row, "r")
        c24 = wci(w24, K, r24, PF)
        planning = (row.get("motive_tier") or "").strip().lower().startswith("planning")
        w25, r25 = num(row, "W_d_2025_ML_d"), num(row, "r_2025")
        c25 = wci(w25, K, r25, PF) if w25 and r25 else None
        if c24 is not None and not planning:
            meas_24.append(c24)
            meas_25.append(c25 if c25 is not None else c24)
        if c25 is not None and c24:
            moved.append((row, c24, c25, c25 / c24 - 1))

    if moved:
        print("\nLAYER 1b - VINTAGE MOVEMENT (FY2024 -> FY2025, operator reports; K and PF "
              "held constant, so the change is withdrawal and consumptive ratio only):")
        print("  %-9s %-18s %8s %8s %8s" % ("operator", "location", "WCI'24", "WCI'25", "change"))
        for row, a, b, d in moved:
            print("  %-9s %-18s %8.3f %8.3f %+7.1f%%"
                  % (row.get("operator"), row.get("location"), a, b, d * 100))
        print("  measured set, %d rows (planning rows excluded from both years):" % len(meas_24))
        print("    FY2024 range %.3f - %.3f" % (min(meas_24), max(meas_24)))
        print("    FY2025 range %.3f - %.3f  (%d of %d rows re-based on FY2025 reports; "
              "the rest are held at FY2024)"
              % (min(meas_25), max(meas_25), len(moved), len(meas_24)))
        print("  -> the index is recomputed on the operator's own later report, not on a "
              "revised estimate; movement is measured, the level is not re-litigated.")

    if flagged:
        print("\nFLAGGED (recomputed WCI disagrees with cited value -> verify "
              "against a PRIMARY source before trusting):")
        for row, calc, stated, gap in flagged:
            print("  - %-9s %-18s calc=%.3f cited=%.3f (%.0f%% off)"
                  % (row.get("operator"), row.get("location"),
                     calc, stated, (gap or 0) * 100))

    if coupled:
        print("\nDOUBLE-COUPLED (water + hydropower; same drought lowers reservoir "
              "AND cuts hydropower -> regional price channel; flagged mechanism, "
              "not a $ forecast). Primary sources in SOURCES.md:")
        for row in coupled:
            dc = (row.get("double_coupled_candidate") or "").strip()
            tag = "ASSERTED (primary)" if dc.upper().startswith(
                ("Y_PRIMARY", "Y_SOURCE")) else "candidate [verify]"
            print("  - %-9s %-18s reservoir=%s dam=%s  %s"
                  % (row.get("operator"), row.get("location"),
                     row.get("reservoir") or "?", row.get("dam") or "?", tag))

    # Layer 3: the relocation ledger. Off-site share = PUE*EWIF / (WUE + PUE*EWIF),
    # reported as a band across the per-grid EWIF low/high. The finding is the
    # POINT: even evaporative sites relocate much of the footprint off-site, and
    # "closed-loop = near-zero water" relocates almost all of it, it does not
    # remove it. Bands, not metered litres.
    l3 = []
    for row in rows:
        WUE = num(row, "WUE_L_per_kWh")
        elo, ehi = num(row, "EWIF_lo"), num(row, "EWIF_hi")
        if None in (WUE, elo, ehi):
            continue
        s_lo = offsite_share(WUE, elo)
        s_hi = offsite_share(WUE, ehi)
        l3.append((row, WUE, elo, ehi, min(s_lo, s_hi), max(s_lo, s_hi)))

    if l3:
        print("\nLAYER 3 - RELOCATION LEDGER (water RELOCATED off-site, not removed; "
              "off-site share = PUE*EWIF / (WUE + PUE*EWIF), PUE=%.1f; EWIF band is a "
              "GRID-AVERAGE BOUND per Siddik et al. 2021, not a per-DC meter):"
              % PUE_DEFAULT)
        hdr3 = ("operator", "location", "cooling", "WUE", "EWIF band",
                "off-site share")
        w3 = (10, 20, 12, 5, 12, 16)
        print("  " + "  ".join(h.ljust(w) for h, w in zip(hdr3, w3)))
        for row, WUE, elo, ehi, s_lo, s_hi in l3:
            cells = (
                (row.get("operator") or "")[:10],
                (row.get("location") or "")[:20],
                (row.get("cooling") or "?")[:12],
                "%.1f" % WUE,
                "%.1f-%.1f" % (elo, ehi),
                "%.0f-%.0f%%" % (s_lo * 100, s_hi * 100),
            )
            print("  " + "  ".join(str(c).ljust(w) for c, w in zip(cells, w3)))
        ev = [x for x in l3 if (x[0].get("cooling") or "").startswith("evap")]
        cl = [x for x in l3 if (x[0].get("cooling") or "").startswith("closed")]
        if ev:
            print("  -> evaporative sites relocate %.0f-%.0f%% of the footprint "
                  "off-site (to the grid's water)."
                  % (min(x[4] for x in ev) * 100, max(x[5] for x in ev) * 100))
        if cl:
            print("  -> closed-loop sites relocate %.0f-%.0f%% off-site: on-site "
                  "water drops toward zero, the footprint MOVES, it does not vanish."
                  % (min(x[4] for x in cl) * 100, max(x[5] for x in cl) * 100))

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
