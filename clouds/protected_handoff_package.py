"""
GP034 — Protected Handoff Package / Delivery Preparation.

Creates the bounded package authorized by GP033.

No delivery or downstream execution occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProtectedHandoffPackageState(str, Enum):
    PREPARED = "prepared"
    BLOCKED = "blocked"


class ProtectedHandoffDeliveryTargetKind(str, Enum):
    TOWER_MEDIATED = "tower_mediated"
    OWNING_APPLICATION = "owning_application"


@dataclass(frozen=True)
class ProtectedHandoffPackage:
    handoff_package_id: str
    schema_version: str

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

    preparation_authorized: bool

    package_state: str
    delivery_prepared: bool

    delivery_authorized: bool
    delivery_released: bool
    handoff_delivered: bool

    credentials_included: bool
    tower_session_material_included: bool
    raw_evidence_included: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    package_integrity_hash: str

    soulaana_package_summary: str
    soulaana_why_it_matters: str
    soulaana_delivery_boundary: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProtectedHandoffPreparationSurface:
    title: str

    packages: tuple[
        ProtectedHandoffPackage,
        ...
    ]

    package_count: int
    prepared_count: int
    blocked_count: int

    preparation_authorized: bool
    delivery_prepared: bool

    delivery_authorized: bool
    delivery_released: bool
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
            "packages": [
                item.to_dict()
                for item in self.packages
            ],
            "package_count": (
                self.package_count
            ),
            "prepared_count": (
                self.prepared_count
            ),
            "blocked_count": (
                self.blocked_count
            ),
            "preparation_authorized": (
                self.preparation_authorized
            ),
            "delivery_prepared": (
                self.delivery_prepared
            ),
            "delivery_authorized": (
                self.delivery_authorized
            ),
            "delivery_released": (
                self.delivery_released
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
