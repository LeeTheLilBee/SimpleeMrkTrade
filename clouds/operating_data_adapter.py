"""
GP018 — Simplee Operating Data Adapter Foundation.

Clouds receives approved summary projections only.

No downstream application Python imports are allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OperatingSourceKind(str, Enum):
    APPLICATION = "application"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"


class OperatingHealth(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class OperatingReadiness(str, Enum):
    READY = "ready"
    BUILDING = "building"
    PLANNING = "planning"
    RESERVED = "reserved"
    BLOCKED = "blocked"


class OperatingAttention(str, Enum):
    NONE = "none"
    INFORMATIONAL = "informational"
    REVIEW = "review"
    ACTION_REQUIRED = "action_required"


class OperatingAuthority(str, Enum):
    SOURCE = "source"
    CLOUDS = "clouds"
    TOWER = "tower"
    OWNER = "owner"


@dataclass(frozen=True)
class OperatingMetric:
    metric_id: str
    label: str
    value: str
    unit: str | None
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OperatingSummary:
    source_id: str
    source_label: str
    source_kind: str

    health: str
    readiness: str
    attention: str

    headline: str
    explanation: str
    owner_message: str

    metrics: tuple[
        OperatingMetric,
        ...
    ]

    source_authority: str
    clouds_authority: str

    freshness_label: str
    live_feed_connected: bool
    approved_summary_projection: bool

    source_integrity_verified: bool
    downstream_execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_label": self.source_label,
            "source_kind": self.source_kind,
            "health": self.health,
            "readiness": self.readiness,
            "attention": self.attention,
            "headline": self.headline,
            "explanation": self.explanation,
            "owner_message": self.owner_message,
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
            "source_authority": self.source_authority,
            "clouds_authority": self.clouds_authority,
            "freshness_label": self.freshness_label,
            "live_feed_connected": self.live_feed_connected,
            "approved_summary_projection": (
                self.approved_summary_projection
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OperatingAdapterSurface:
    title: str
    summaries: tuple[
        OperatingSummary,
        ...
    ]

    source_count: int
    live_source_count: int
    projected_source_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "summaries": [
                item.to_dict()
                for item in self.summaries
            ],
            "source_count": self.source_count,
            "live_source_count": self.live_source_count,
            "projected_source_count": (
                self.projected_source_count
            ),
            "boundary_notice": self.boundary_notice,
        }
