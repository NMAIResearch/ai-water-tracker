#!/usr/bin/env python3
"""
audit_runner.py - Orchestrator for the empirical dataset audit pipeline.
Standard library only. Complies with Rule 14, 15, and 33.
"""
import argparse
import json
import sys
from pathlib import Path

# Local imports
from state import DatasetAuditState
from nodes.shard_streamer import node_stream_shard
from nodes.anomaly_isolator import node_isolate_anomalies
from nodes.table_renderer import node_render_summary


def resolve_default_shard() -> Path:
    candidates = [
        Path.cwd() / "sites.csv",
        Path(__file__).resolve().parents[2] / "sites.csv",
        Path("/var/home/Noel/Desktop/ai-water-tracker/sites.csv"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


def log_audit_run(ctx: DatasetAuditState, log_path: Path) -> None:
    record = {
        "shard_id": ctx.shard_id,
        "total_records": ctx.total_records,
        "clean_records": ctx.clean_records,
        "anomalous_records": ctx.anomalous_records,
        "tolerance": ctx.tolerance,
        "anomalies": [
            {
                "row": a.row_idx,
                "identifier": a.identifier,
                "field": a.field_name,
                "delta_pct": a.relative_delta_pct,
                "category": a.anomaly_category,
                "note": a.note,
            }
            for a in ctx.anomalies
        ],
        "errors": ctx.errors,
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def run_audit(shard_path: Path, tolerance: float = 0.05) -> DatasetAuditState:
    ctx = DatasetAuditState(shard_id=shard_path.name, tolerance=tolerance)
    log_path = Path(__file__).resolve().parent / "audit_log.jsonl"

    print(f"\n[Audit Pipeline] Processing shard: {shard_path} (tol: {int(tolerance * 100)}%)...")

    # Node A: Stream Shard
    ctx = node_stream_shard(ctx, shard_path)
    if ctx.errors:
        print(f"  [ERROR] {ctx.errors[-1]}")
        log_audit_run(ctx, log_path)
        return ctx

    # Node B, C, D: Deterministic Scoring & Anomaly Isolation
    ctx = node_isolate_anomalies(ctx)

    # Node E: Compile Statistics & Render Summary
    ctx = node_render_summary(ctx)
    log_audit_run(ctx, log_path)

    print("\n" + ctx.summary_markdown)
    return ctx


def main():
    parser = argparse.ArgumentParser(description="Empirical Dataset Audit Pipeline")
    parser.add_argument("--shard", type=str, default=None, help="Path to CSV or JSONL dataset shard")
    parser.add_argument("--tol", type=float, default=0.05, help="Relative error tolerance (default: 0.05 = 5%%)")
    args = parser.parse_args()

    shard_path = Path(args.shard) if args.shard else resolve_default_shard()
    ctx = run_audit(shard_path, tolerance=args.tol)

    # Exit code: 0 if all clean, 1 if anomalies isolated (matches reproduce.py convention)
    sys.exit(1 if ctx.anomalous_records > 0 else 0)


if __name__ == "__main__":
    main()
