"""
anomaly_isolator.py - Node C & D: Isolate anomalies, calculate deltas, and accumulate clean rows.
Standard library only.
"""
from state import DatasetAuditState, AnomalyRecord
from nodes.reproduce_filter import filter_record


def node_isolate_anomalies(ctx: DatasetAuditState) -> DatasetAuditState:
    """
    Node C & D execution function:
    Applies deterministic checks to each streamed record.
    If discrepancy > tolerance, routes to anomaly isolation; else accumulates as clean record.
    """
    ctx.anomalies = []
    clean_count = 0
    anomalous_count = 0

    for record in ctx.records:
        filter_record(record)
        metrics = record.computed_metrics
        raw = record.raw_data

        rel_delta = metrics.get("relative_delta")
        stated_wci = metrics.get("stated_WCI")
        computed_wci = metrics.get("recomputed_WCI")
        source_tag = raw.get("source_tag", "")
        motive_tier = raw.get("motive_tier", "")

        is_anomaly = False

        # Check 1: Mathematical reproduction drift
        if rel_delta is not None and stated_wci is not None and computed_wci is not None:
            if rel_delta > ctx.tolerance:
                is_anomaly = True
                delta_pct = round(rel_delta * 100.0, 2)
                note = (
                    f"Stated WCI ({stated_wci}) disagrees with component calculation "
                    f"({computed_wci}) by {delta_pct}% (tolerance: {int(ctx.tolerance * 100)}%)."
                )
                anom = AnomalyRecord(
                    row_idx=record.row_idx,
                    identifier=record.identifier,
                    field_name="stated_WCI",
                    stated_value=stated_wci,
                    computed_value=computed_wci,
                    relative_delta_pct=delta_pct,
                    tolerance_threshold=ctx.tolerance,
                    anomaly_category="REPRODUCTION_DRIFT",
                    note=note
                )
                ctx.anomalies.append(anom)

        # Check 2: Non-measured planning status
        if "planning_not_measured" in (source_tag, motive_tier) or "NOT_operational" in source_tag:
            is_anomaly = True
            note = f"Row is a planning-only or non-operational estimate presented alongside measured figures ({source_tag})."
            anom = AnomalyRecord(
                row_idx=record.row_idx,
                identifier=record.identifier,
                field_name="source_tag",
                stated_value=stated_wci or 0.0,
                computed_value=computed_wci or 0.0,
                relative_delta_pct=0.0,
                tolerance_threshold=ctx.tolerance,
                anomaly_category="PLANNING_UNMEASURED",
                note=note
            )
            ctx.anomalies.append(anom)

        record.is_anomalous = is_anomaly
        if is_anomaly:
            anomalous_count += 1
        else:
            clean_count += 1

    ctx.clean_records = clean_count
    ctx.anomalous_records = anomalous_count
    ctx.log(
        f"Audit complete: {ctx.total_records} total records, "
        f"{ctx.clean_records} clean, {ctx.anomalous_records} anomalous/flagged."
    )
    ctx.stage = "ANOMALIES_ISOLATED"
    return ctx
