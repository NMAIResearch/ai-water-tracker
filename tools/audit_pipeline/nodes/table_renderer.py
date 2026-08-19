"""
table_renderer.py - Node E: Render empirical audit verification table.
Complies with Rule 14 (numerator, denominator, N) and Rule 15 (baseline comparison).
"""
from typing import Dict, Any
from state import DatasetAuditState


def render_audit_markdown(ctx: DatasetAuditState) -> str:
    """
    Renders structured verification table and summary statistics.
    """
    total = ctx.total_records
    clean = ctx.clean_records
    anomalous = ctx.anomalous_records
    clean_pct = round((clean / total) * 100.0, 1) if total > 0 else 0.0
    anom_pct = round((anomalous / total) * 100.0, 1) if total > 0 else 0.0

    lines = [
        f"### Dataset Verification Summary: `{ctx.shard_id}`",
        "",
        f"- **Sample Size (N)**: {total} total records",
        f"- **Clean Rows (Numerator/Denominator)**: {clean} of {total} ({clean_pct}%)",
        f"- **Flagged / Anomalous Rows**: {anomalous} of {total} ({anom_pct}%)",
        f"- **Reproduction Tolerance**: {int(ctx.tolerance * 100)}% relative error bound",
        f"- **Baseline Comparison (Rule 15)**: Trivial baseline assumes 100% agreement across all rows; observed defect rate is {anomalous}/{total} ({anom_pct}%).",
        "",
        "#### Summary Verification Table",
        "",
        "| Row | Operator & Location | Stated WCI | Recomputed WCI | Delta (%) | Category | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for rec in ctx.records:
        m = rec.computed_metrics
        stated = m.get("stated_WCI", "N/A")
        computed = m.get("recomputed_WCI", "N/A")
        delta = f"{round(m['relative_delta'] * 100.0, 1)}%" if "relative_delta" in m else "N/A"
        category = "Clean" if not rec.is_anomalous else "Flagged"

        # Check specific anomaly label
        for anom in ctx.anomalies:
            if anom.row_idx == rec.row_idx:
                category = anom.anomaly_category
                break

        status = "PASS" if not rec.is_anomalous else "DISCREPANCY"
        lines.append(f"| {rec.row_idx} | {rec.identifier} | {stated} | {computed} | {delta} | {category} | {status} |")

    if ctx.anomalies:
        lines.extend([
            "",
            "#### Isolated Anomalies Breakdown",
            "",
        ])
        for a in ctx.anomalies:
            lines.append(f"- **Row {a.row_idx} ({a.identifier})**: {a.note}")

    return "\n".join(lines)


def node_render_summary(ctx: DatasetAuditState) -> DatasetAuditState:
    """
    Node E execution function:
    Compiles summary markdown and registers in state.
    """
    ctx.summary_markdown = render_audit_markdown(ctx)
    ctx.stage = "TABLE_RENDERED"
    ctx.log("Rendered verification table and summary statistics.")
    return ctx
