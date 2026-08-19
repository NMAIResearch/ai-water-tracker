"""
state.py - Typed state schemas for the empirical dataset audit pipeline.
Standard library only.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class DatasetRecord:
    row_idx: int
    identifier: str
    raw_data: Dict[str, Any]
    computed_metrics: Dict[str, float] = field(default_factory=dict)
    is_anomalous: bool = False


@dataclass
class AnomalyRecord:
    row_idx: int
    identifier: str
    field_name: str
    stated_value: float
    computed_value: float
    relative_delta_pct: float
    tolerance_threshold: float
    anomaly_category: str  # e.g. "REPRODUCTION_DRIFT", "PLANNING_UNMEASURED", "UNVERIFIED"
    note: str = ""


@dataclass
class DatasetAuditState:
    shard_id: str
    tolerance: float = 0.05
    total_records: int = 0
    clean_records: int = 0
    anomalous_records: int = 0
    records: List[DatasetRecord] = field(default_factory=list)
    anomalies: List[AnomalyRecord] = field(default_factory=list)
    stage: str = "INIT"
    summary_markdown: str = ""
    log_messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        self.log_messages.append(msg)
