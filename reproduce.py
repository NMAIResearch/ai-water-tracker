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
    python3 reproduce.py --tol 0.05      # set the reproduction tolerance (rel.)
    python3 reproduce.py --csv other.csv
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
