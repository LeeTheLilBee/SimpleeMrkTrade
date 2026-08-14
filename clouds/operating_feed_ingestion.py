"""
GP025 — Real Operating Feed Ingestion Foundation.

Defines the canonical summary-feed boundary entering Clouds.

This module does not connect to downstream applications.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


CANONICAL_OPERATING_SOURCE_IDS = (
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
)


class OperatingFeedMode(str, Enum):
    PROJECTION = "projection"
    LIVE = "live"


class OperatingFeedValidationState(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class OperatingFeedReplayState(str, Enum):
    NEW = "new"
    DUPLICATE = "duplicate"
    STALE_SEQUENCE = "stale_sequence"


@dataclass(frozen=True)
class OperatingFeedMetric:
    metric_id: str
    label: str
    value: str
    unit: str | None
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OperatingFeedEnvelope:
    schema_version: str

    feed_id: str
    source_id: str
    source_label: str

    mode: str
    source_sequence: int
    observed_at: str

    health: str
    readiness: str
    attention: str

    headline: str
    explanation: str
    owner_message: str

    metrics: tuple[
        OperatingFeedMetric,
        ...
    ]

    source_integrity_hash: str

    source_claims_live: bool

    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "feed_id": self.feed_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "mode": self.mode,
            "source_sequence": self.source_sequence,
            "observed_at": self.observed_at,
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
            "source_integrity_hash": (
                self.source_integrity_hash
            ),
            "source_claims_live": (
                self.source_claims_live
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class OperatingFeedValidationReceipt:
    receipt_id: str

    feed_id: str
    source_id: str

    validation_state: str
    replay_state: str

    schema_valid: bool
    source_known: bool
    source_sequence_valid: bool
    timestamp_present: bool
    health_valid: bool
    readiness_valid: bool
    attention_valid: bool
    explanations_present: bool
    integrity_hash_valid: bool
    live_claim_consistent: bool

    accepted_for_clouds_interpretation: bool

    raw_source_access_performed: bool
    downstream_execution_performed: bool

    rejection_reasons: tuple[
        str,
        ...
    ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "feed_id": self.feed_id,
            "source_id": self.source_id,
            "validation_state": (
                self.validation_state
            ),
            "replay_state": (
                self.replay_state
            ),
            "schema_valid": (
                self.schema_valid
            ),
            "source_known": (
                self.source_known
            ),
            "source_sequence_valid": (
                self.source_sequence_valid
            ),
            "timestamp_present": (
                self.timestamp_present
            ),
            "health_valid": (
                self.health_valid
            ),
            "readiness_valid": (
                self.readiness_valid
            ),
            "attention_valid": (
                self.attention_valid
            ),
            "explanations_present": (
                self.explanations_present
            ),
            "integrity_hash_valid": (
                self.integrity_hash_valid
            ),
            "live_claim_consistent": (
                self.live_claim_consistent
            ),
            "accepted_for_clouds_interpretation": (
                self
                .accepted_for_clouds_interpretation
            ),
            "raw_source_access_performed": (
                self.raw_source_access_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "rejection_reasons": list(
                self.rejection_reasons
            ),
        }


@dataclass(frozen=True)
class OperatingFeedIngestionSurface:
    title: str

    envelopes: tuple[
        OperatingFeedEnvelope,
        ...
    ]

    receipts: tuple[
        OperatingFeedValidationReceipt,
        ...
    ]

    feed_count: int
    accepted_count: int
    rejected_count: int

    projection_count: int
    live_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "envelopes": [
                item.to_dict()
                for item in self.envelopes
            ],
            "receipts": [
                item.to_dict()
                for item in self.receipts
            ],
            "feed_count": self.feed_count,
            "accepted_count": (
                self.accepted_count
            ),
            "rejected_count": (
                self.rejected_count
            ),
            "projection_count": (
                self.projection_count
            ),
            "live_count": self.live_count,
            "boundary_notice": (
                self.boundary_notice
            ),
        }
