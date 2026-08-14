"""
GP036 — Protected Handoff Release Record / Delivery Envelope Preparation.

Creates the release record and bounded delivery envelope.

No actual release or delivery occurs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProtectedReleaseRecordState(str, Enum):
    PREPARED = "prepared"
    BLOCKED = "blocked"


class ProtectedDeliveryEnvelopeState(str, Enum):
    PREPARED = "prepared"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProtectedHandoffReleaseRecord:
    release_record_id: str
    release_record_schema_version: str

    release_authorization_id: str

    handoff_package_id: str
    package_schema_version: str
    package_integrity_hash: str

    authorization_record_id: str
    intent_review_id: str
    choice_record_id: str
    decision_review_id: str
    decision_packet_id: str
    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    selected_option_id: str
    selected_option_kind: str
    selected_option_label: str

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool

    delivery_target_kind: str
    delivery_target_id: str

    owner_release_decision: str
    release_authorization_state: str

    owner_confirmation_recorded: bool

    package_integrity_verified: bool
    package_binding_verified: bool

    release_record_state: str
    release_record_prepared: bool

    delivery_release_authorized: bool

    delivery_release_executed: bool
    delivery_released: bool
    delivery_attempted: bool
    handoff_delivered: bool

    credentials_included: bool
    tower_session_material_included: bool
    raw_evidence_included: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    release_record_integrity_hash: str

    soulaana_release_record_summary: str
    soulaana_why_it_matters: str
    soulaana_release_boundary: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProtectedHandoffDeliveryEnvelope:
    delivery_envelope_id: str
    delivery_envelope_schema_version: str

    release_record_id: str
    release_record_integrity_hash: str

    release_authorization_id: str

    handoff_package_id: str
    package_integrity_hash: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    selected_option_id: str
    selected_option_kind: str
    selected_option_label: str

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool

    delivery_target_kind: str
    delivery_target_id: str

    envelope_state: str
    envelope_prepared: bool

    delivery_release_authorized: bool

    delivery_release_executed: bool
    delivery_released: bool
    delivery_attempted: bool
    handoff_delivered: bool

    credentials_included: bool
    tower_session_material_included: bool
    raw_evidence_included: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    delivery_envelope_integrity_hash: str

    soulaana_envelope_summary: str
    soulaana_why_it_matters: str
    soulaana_delivery_boundary: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProtectedHandoffReleasePreparationSurface:
    title: str

    release_records: tuple[
        ProtectedHandoffReleaseRecord,
        ...
    ]

    delivery_envelopes: tuple[
        ProtectedHandoffDeliveryEnvelope,
        ...
    ]

    release_record_count: int
    prepared_release_record_count: int

    delivery_envelope_count: int
    prepared_delivery_envelope_count: int

    blocked_count: int

    delivery_release_authorized: bool

    delivery_release_executed: bool
    delivery_released: bool
    delivery_attempted: bool
    handoff_delivered: bool

    credentials_included: bool
    tower_session_material_included: bool
    raw_evidence_included: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,

            "release_records": [
                item.to_dict()
                for item in self.release_records
            ],

            "delivery_envelopes": [
                item.to_dict()
                for item in self.delivery_envelopes
            ],

            "release_record_count": (
                self.release_record_count
            ),

            "prepared_release_record_count": (
                self.prepared_release_record_count
            ),

            "delivery_envelope_count": (
                self.delivery_envelope_count
            ),

            "prepared_delivery_envelope_count": (
                self.prepared_delivery_envelope_count
            ),

            "blocked_count": (
                self.blocked_count
            ),

            "delivery_release_authorized": (
                self.delivery_release_authorized
            ),

            "delivery_release_executed": (
                self.delivery_release_executed
            ),

            "delivery_released": (
                self.delivery_released
            ),

            "delivery_attempted": (
                self.delivery_attempted
            ),

            "handoff_delivered": (
                self.handoff_delivered
            ),

            "credentials_included": (
                self.credentials_included
            ),

            "tower_session_material_included": (
                self.tower_session_material_included
            ),

            "raw_evidence_included": (
                self.raw_evidence_included
            ),

            "approval_performed": (
                self.approval_performed
            ),

            "capital_movement_performed": (
                self.capital_movement_performed
            ),

            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),

            "boundary_notice": (
                self.boundary_notice
            ),
        }
