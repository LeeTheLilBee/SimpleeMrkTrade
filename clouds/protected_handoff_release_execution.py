"""
GP037 — Protected Handoff Release Execution / Delivery Attempt Boundary.

Releases the exact GP036 envelope to the external-delivery boundary.

No external transport or Tower contact occurs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProtectedReleaseExecutionState(str, Enum):
    RELEASED_TO_EXTERNAL_BOUNDARY = (
        "released_to_external_boundary"
    )
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProtectedHandoffReleaseExecution:
    release_execution_id: str

    release_record_id: str
    release_record_integrity_hash: str

    delivery_envelope_id: str
    delivery_envelope_integrity_hash: str

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

    release_execution_state: str

    delivery_release_authorized: bool
    delivery_release_executed: bool

    released_to_delivery_boundary: bool

    external_transport_invoked: bool
    tower_contacted: bool
    external_delivery_attempted: bool
    external_receipt_present: bool

    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_summary: str
    soulaana_what_this_means: str
    soulaana_what_did_not_happen: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
