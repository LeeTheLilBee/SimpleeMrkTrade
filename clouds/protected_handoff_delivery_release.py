"""
GP035 — Protected Handoff Delivery Release / Authorization Gate.

Records whether the owner authorizes the exact GP034 package
to enter the release lane.

This does not release or deliver the package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProtectedHandoffReleaseDecision(str, Enum):
    AUTHORIZE_RELEASE = "authorize_release"
    DECLINE_RELEASE = "decline_release"


class ProtectedHandoffReleaseState(str, Enum):
    AUTHORIZED_FOR_RELEASE = "authorized_for_release"
    DECLINED = "declined"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProtectedHandoffReleaseAuthorization:
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
    release_state: str

    owner_confirmation_recorded: bool

    package_integrity_verified: bool
    package_binding_verified: bool

    delivery_release_authorized: bool
    delivery_released: bool
    handoff_delivered: bool

    credentials_included: bool
    tower_session_material_included: bool
    raw_evidence_included: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_release_summary: str
    soulaana_what_this_means: str
    soulaana_what_did_not_happen: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProtectedHandoffReleaseAuthorizationSurface:
    title: str

    records: tuple[
        ProtectedHandoffReleaseAuthorization,
        ...
    ]

    record_count: int
    authorized_count: int
    declined_count: int
    blocked_count: int

    owner_confirmation_recorded: bool

    package_integrity_verified: bool
    package_binding_verified: bool

    delivery_release_authorized: bool

    delivery_released: bool
    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,

            "records": [
                item.to_dict()
                for item in self.records
            ],

            "record_count": (
                self.record_count
            ),

            "authorized_count": (
                self.authorized_count
            ),

            "declined_count": (
                self.declined_count
            ),

            "blocked_count": (
                self.blocked_count
            ),

            "owner_confirmation_recorded": (
                self.owner_confirmation_recorded
            ),

            "package_integrity_verified": (
                self.package_integrity_verified
            ),

            "package_binding_verified": (
                self.package_binding_verified
            ),

            "delivery_release_authorized": (
                self.delivery_release_authorized
            ),

            "delivery_released": (
                self.delivery_released
            ),

            "handoff_delivered": (
                self.handoff_delivered
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
