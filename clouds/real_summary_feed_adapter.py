"""
GP041 — Real Summary Feed Adapter Contract.

Defines the external-summary shape that source-owned applications
may publish into Clouds.

The result is always converted into the canonical GP025
OperatingFeedEnvelope.

No downstream application package is imported.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExternalSummaryMetric:
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
class ExternalOperatingSummaryPayload:
    source_contract_version: str

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
        ExternalSummaryMetric,
        ...
    ]

    source_claims_live: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_contract_version": (
                self.source_contract_version
            ),

            "feed_id": self.feed_id,

            "source_id": self.source_id,
            "source_label": self.source_label,

            "mode": self.mode,

            "source_sequence": (
                self.source_sequence
            ),

            "observed_at": (
                self.observed_at
            ),

            "health": self.health,
            "readiness": self.readiness,
            "attention": self.attention,

            "headline": self.headline,
            "explanation": self.explanation,
            "owner_message": (
                self.owner_message
            ),

            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],

            "source_claims_live": (
                self.source_claims_live
            ),
        }


@dataclass(frozen=True)
class RealSummaryFeedAdapterSpec:
    adapter_id: str

    source_id: str
    source_label: str

    source_contract_version: str

    clouds_feed_schema_version: str

    supports_projection: bool
    supports_live: bool

    external_connection_verification_required: bool

    raw_source_access_allowed: bool
    downstream_execution_allowed: bool
    cross_app_import_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class RealSummaryFeedAdapterResult:
    adapter_id: str

    source_id: str
    source_label: str

    source_contract_version: str

    adapter_contract_ready: bool

    certification_fixture_only: bool

    external_source_connected: bool

    external_connection_verified: bool

    envelope_mode: str

    accepted_for_clouds_interpretation: bool

    validation_state: str
    replay_state: str

    source_integrity_verified: bool

    counts_as_real_live_connection: bool

    raw_source_access_performed: bool
    downstream_execution_performed: bool
    cross_app_imports_used: bool

    envelope: Any
    validation_receipt: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,

            "source_id": self.source_id,
            "source_label": self.source_label,

            "source_contract_version": (
                self.source_contract_version
            ),

            "adapter_contract_ready": (
                self.adapter_contract_ready
            ),

            "certification_fixture_only": (
                self.certification_fixture_only
            ),

            "external_source_connected": (
                self.external_source_connected
            ),

            "external_connection_verified": (
                self.external_connection_verified
            ),

            "envelope_mode": (
                self.envelope_mode
            ),

            "accepted_for_clouds_interpretation": (
                self.accepted_for_clouds_interpretation
            ),

            "validation_state": (
                self.validation_state
            ),

            "replay_state": (
                self.replay_state
            ),

            "source_integrity_verified": (
                self.source_integrity_verified
            ),

            "counts_as_real_live_connection": (
                self.counts_as_real_live_connection
            ),

            "raw_source_access_performed": (
                self.raw_source_access_performed
            ),

            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),

            "cross_app_imports_used": (
                self.cross_app_imports_used
            ),

            "envelope": (
                self.envelope.to_dict()
            ),

            "validation_receipt": (
                self.validation_receipt.to_dict()
            ),
        }
