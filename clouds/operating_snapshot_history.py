"""
GP026 — Operating Snapshot History / Change Memory Foundation.

Provides deterministic historical comparison contracts for
Clouds operating summaries.

No live historical feed is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ChangeState(str, Enum):
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class ChangeDirection(str, Enum):
    IMPROVING = "improving"
    WORSENING = "worsening"
    MIXED = "mixed"
    STABLE = "stable"


class ChangeMateriality(str, Enum):
    MATERIAL = "material"
    INFORMATIONAL = "informational"
    NONE = "none"


class MetricDeltaKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class HistoricalMetricSnapshot:
    metric_id: str
    label: str
    value: str
    unit: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
        }


@dataclass(frozen=True)
class OperatingSourceSnapshot:
    snapshot_id: str

    source_id: str
    source_label: str

    sequence: int
    observed_at: str
    mode: str

    health: str
    readiness: str
    attention: str

    headline: str
    explanation: str
    owner_message: str

    metrics: tuple[
        HistoricalMetricSnapshot,
        ...
    ]

    source_integrity_verified: bool
    live_feed_claimed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "sequence": self.sequence,
            "observed_at": self.observed_at,
            "mode": self.mode,
            "health": self.health,
            "readiness": self.readiness,
            "attention": self.attention,
            "headline": self.headline,
            "explanation": self.explanation,
            "owner_message": self.owner_message,
            "metrics": [
                item.to_dict()
                for item in self.metrics
            ],
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "live_feed_claimed": (
                self.live_feed_claimed
            ),
        }


@dataclass(frozen=True)
class MetricDelta:
    metric_id: str
    label: str

    prior_value: str | None
    current_value: str | None

    unit: str | None

    delta_kind: str

    changed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "prior_value": self.prior_value,
            "current_value": self.current_value,
            "unit": self.unit,
            "delta_kind": self.delta_kind,
            "changed": self.changed,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OperatingSnapshotDelta:
    delta_id: str

    source_id: str
    source_label: str

    prior_snapshot_id: str
    current_snapshot_id: str

    change_state: str
    direction: str
    materiality: str

    health_changed: bool
    readiness_changed: bool
    attention_changed: bool

    prior_health: str
    current_health: str

    prior_readiness: str
    current_readiness: str

    prior_attention: str
    current_attention: str

    metric_deltas: tuple[
        MetricDelta,
        ...
    ]

    changed_metric_count: int

    soulaana_what_changed: str
    soulaana_why_it_matters: str
    soulaana_owner_attention: str
    soulaana_what_can_wait: str

    owner_attention_required: bool

    live_history_claimed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "prior_snapshot_id": (
                self.prior_snapshot_id
            ),
            "current_snapshot_id": (
                self.current_snapshot_id
            ),
            "change_state": self.change_state,
            "direction": self.direction,
            "materiality": self.materiality,
            "health_changed": (
                self.health_changed
            ),
            "readiness_changed": (
                self.readiness_changed
            ),
            "attention_changed": (
                self.attention_changed
            ),
            "prior_health": self.prior_health,
            "current_health": self.current_health,
            "prior_readiness": (
                self.prior_readiness
            ),
            "current_readiness": (
                self.current_readiness
            ),
            "prior_attention": (
                self.prior_attention
            ),
            "current_attention": (
                self.current_attention
            ),
            "metric_deltas": [
                item.to_dict()
                for item in self.metric_deltas
            ],
            "changed_metric_count": (
                self.changed_metric_count
            ),
            "soulaana_what_changed": (
                self.soulaana_what_changed
            ),
            "soulaana_why_it_matters": (
                self.soulaana_why_it_matters
            ),
            "soulaana_owner_attention": (
                self.soulaana_owner_attention
            ),
            "soulaana_what_can_wait": (
                self.soulaana_what_can_wait
            ),
            "owner_attention_required": (
                self.owner_attention_required
            ),
            "live_history_claimed": (
                self.live_history_claimed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class OperatingHistorySurface:
    title: str

    prior_snapshots: tuple[
        OperatingSourceSnapshot,
        ...
    ]

    current_snapshots: tuple[
        OperatingSourceSnapshot,
        ...
    ]

    deltas: tuple[
        OperatingSnapshotDelta,
        ...
    ]

    source_count: int
    changed_source_count: int
    unchanged_source_count: int
    material_change_count: int
    owner_attention_count: int

    live_history_connected: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "prior_snapshots": [
                item.to_dict()
                for item in self.prior_snapshots
            ],
            "current_snapshots": [
                item.to_dict()
                for item in self.current_snapshots
            ],
            "deltas": [
                item.to_dict()
                for item in self.deltas
            ],
            "source_count": self.source_count,
            "changed_source_count": (
                self.changed_source_count
            ),
            "unchanged_source_count": (
                self.unchanged_source_count
            ),
            "material_change_count": (
                self.material_change_count
            ),
            "owner_attention_count": (
                self.owner_attention_count
            ),
            "live_history_connected": (
                self.live_history_connected
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
