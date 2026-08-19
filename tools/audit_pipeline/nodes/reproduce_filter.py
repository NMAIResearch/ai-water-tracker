"""
reproduce_filter.py - Node B: Deterministic scoring filter.
Reconstructs Water Consumption Impact (WCI) index and relocation ledger values.
"""
from typing import Dict, Any, Optional
from state import DatasetRecord


def safe_float(val: Any) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def calculate_deterministic_wci(raw: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes:
      recomputed_WCI = (W / K) * r * PF
      consumptive_withdrawal = W * r
      offsite_share_lo / hi = (PUE * EWIF) / (WUE + PUE * EWIF) [PUE ~ 1.15]
    """
    metrics = {}
    W = safe_float(raw.get("W_d_ML_d"))
    K = safe_float(raw.get("K_ML_d"))
    r = safe_float(raw.get("r"))
    PF = safe_float(raw.get("PF"))
    stated_WCI = safe_float(raw.get("stated_WCI"))

    if W is not None and K is not None and r is not None and PF is not None and K > 0:
        recomputed_WCI = (W / K) * r * PF
        metrics["recomputed_WCI"] = round(recomputed_WCI, 4)
        metrics["consumptive_withdrawal_ML_d"] = round(W * r, 4)

        if stated_WCI is not None and stated_WCI > 0:
            rel_delta = abs(recomputed_WCI - stated_WCI) / stated_WCI
            metrics["relative_delta"] = round(rel_delta, 4)
            metrics["stated_WCI"] = stated_WCI

    # Layer 3: Relocation calculations
    WUE = safe_float(raw.get("WUE_L_per_kWh")) or 1.8
    EWIF_lo = safe_float(raw.get("EWIF_lo"))
    EWIF_hi = safe_float(raw.get("EWIF_hi"))
    pue = 1.15

    if EWIF_lo is not None:
        off_lo = pue * EWIF_lo
        metrics["offsite_share_lo_pct"] = round((off_lo / (WUE + off_lo)) * 100.0, 1)

    if EWIF_hi is not None:
        off_hi = pue * EWIF_hi
        metrics["offsite_share_hi_pct"] = round((off_hi / (WUE + off_hi)) * 100.0, 1)

    return metrics


def filter_record(record: DatasetRecord) -> DatasetRecord:
    """
    Applies deterministic scoring formula to a single record.
    """
    record.computed_metrics = calculate_deterministic_wci(record.raw_data)
    return record
