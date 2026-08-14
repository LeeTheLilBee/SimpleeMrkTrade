"""
GP019 — Operating Data Normalization / Trust.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OperatingTrustState(str, Enum):
    TRUSTED_PROJECTION = "trusted_projection"
    TRUSTED_LIVE = "trusted_live"
    LIMITED = "limited"
    UNTRUSTED = "untrusted"


class NormalizationState(str, Enum):
    NORMALIZED = "normalized"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OperatingTrustRecord:
    source_id: str

    trust_state: str
    normalization_state: str

    health: str
    readiness: str
    attention: str

    confidence_score: int
    freshness_score: int

    live_feed_connected: bool
    approved_projection: bool

    owner_visible: bool
    owner_attention_required: bool

    source_integrity_verified: bool
    clouds_interpretation_allowed: bool

    raw_source_access_performed: bool
    downstream_execution_performed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OperatingTrustSurface:
    title: str

    records: tuple[
        OperatingTrustRecord,
        ...
    ]

    source_count: int
    trusted_count: int
    rejected_count: int
    owner_attention_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "records": [
                item.to_dict()
                for item in self.records
            ],
            "source_count": self.source_count,
            "trusted_count": self.trusted_count,
            "rejected_count": self.rejected_count,
            "owner_attention_count": (
                self.owner_attention_count
            ),
            "boundary_notice": self.boundary_notice,
        }
