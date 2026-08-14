"""
GP038 — Delivery Attempt Record / External Receipt Preparation.

Prepares the external-delivery attempt record.

It does not invoke external transport.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProtectedDeliveryAttemptState(str, Enum):
    AWAITING_EXTERNAL_TRANSPORT = (
        "awaiting_external_transport"
    )
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProtectedHandoffDeliveryAttemptRecord:
    delivery_attempt_record_id: str

    release_execution_id: str

    delivery_envelope_id: str
    delivery_envelope_integrity_hash: str

    release_record_id: str
    release_record_integrity_hash: str

    handoff_package_id: str
    package_integrity_hash: str

    source_id: str
    source_label: str

    selected_option_id: str
    selected_option_kind: str
    selected_option_label: str

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool

    delivery_target_kind: str
    delivery_target_id: str

    attempt_state: str

    delivery_attempt_record_prepared: bool

    external_transport_required: bool
    external_transport_invoked: bool

    tower_contacted: bool

    external_delivery_attempted: bool

    external_receipt_required: bool
    external_receipt_present: bool

    external_acceptance_verified: bool

    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_summary: str
    soulaana_what_this_means: str
    soulaana_what_can_wait: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
