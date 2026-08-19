"""
shard_streamer.py - Node A: Stream and parse dataset shards.
Memory-bounded iterator for CSV and JSONL datasets.
"""
import csv
import json
from pathlib import Path
from typing import Iterator, Dict, Any, Tuple
from state import DatasetAuditState, DatasetRecord


def stream_dataset_file(filepath: Path) -> Iterator[Tuple[int, Dict[str, Any]]]:
    """
    Stream records from CSV or JSONL.
    """
    if filepath.suffix == ".csv":
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                yield idx, dict(row)
    elif filepath.suffix in (".jsonl", ".json"):
        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.suffix == ".jsonl":
                for idx, line in enumerate(f, start=1):
                    if line.strip():
                        yield idx, json.loads(line.strip())
            else:
                data = json.load(f)
                if isinstance(data, list):
                    for idx, item in enumerate(data, start=1):
                        yield idx, item


def node_stream_shard(ctx: DatasetAuditState, shard_path: Path) -> DatasetAuditState:
    """
    Node A execution function:
    Streams shard records and populates initial dataset records in state.
    """
    if not shard_path.is_file():
        ctx.errors.append(f"Shard file not found: {shard_path}")
        return ctx

    ctx.shard_id = shard_path.name
    ctx.records = []
    for idx, raw in stream_dataset_file(shard_path):
        operator = raw.get("operator", "Unknown")
        location = raw.get("location", f"Row-{idx}")
        identifier = f"{operator} ({location})"
        rec = DatasetRecord(
            row_idx=idx,
            identifier=identifier,
            raw_data=raw,
        )
        ctx.records.append(rec)

    ctx.total_records = len(ctx.records)
    ctx.log(f"Streamed {ctx.total_records} records from shard: {ctx.shard_id}")
    ctx.stage = "SHARD_STREAMED"
    return ctx
