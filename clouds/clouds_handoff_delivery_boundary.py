"""
GP017 — Clouds Handoff Delivery Boundary.

This closes Clouds-side responsibility without claiming
that Tower has received anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CloudsDeliveryBoundaryState(str, Enum):
    READY_FOR_EXTERNAL_TOWER_INTAKE = (
        "ready_for_external_tower_intake"
    )
    BLOCKED = "blocked"


class CloudsDeliveryState(str, Enum):
    NOT_DELIVERED = "not_delivered"


@dataclass(frozen=True)
class CloudsHandoffBoundaryRecord:
    boundary_id: str

    package_id: str
    submission_id: str
    destination_id: str

    package_hash: str
    submission_hash: str

    boundary_state: str
    delivery_state: str

    tower_authority_required: bool
    owner_permission_requirement_preserved: bool
    step_up_requirement_preserved: bool

    clouds_work_complete: bool

    delivered_to_tower: bool
    tower_request_created: bool
    tower_acceptance_recorded: bool
    tower_receipt_created: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_id": self.boundary_id,
            "package_id": self.package_id,
            "submission_id": self.submission_id,
            "destination_id": self.destination_id,
            "package_hash": self.package_hash,
            "submission_hash": self.submission_hash,
            "boundary_state": self.boundary_state,
            "delivery_state": self.delivery_state,
            "tower_authority_required": (
                self.tower_authority_required
            ),
            "owner_permission_requirement_preserved": (
                self.owner_permission_requirement_preserved
            ),
            "step_up_requirement_preserved": (
                self.step_up_requirement_preserved
            ),
            "clouds_work_complete": (
                self.clouds_work_complete
            ),
            "delivered_to_tower": (
                self.delivered_to_tower
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "tower_acceptance_recorded": (
                self.tower_acceptance_recorded
            ),
            "tower_receipt_created": (
                self.tower_receipt_created
            ),
            "handoff_executed": (
                self.handoff_executed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class CloudsHandoffCloseoutReceipt:
    receipt_id: str

    boundary_id: str
    package_id: str

    clouds_checkpoint: str
    conclusion: str

    clouds_scope_complete: bool
    external_tower_intake_required: bool

    delivered_to_tower: bool
    tower_acceptance_recorded: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "boundary_id": self.boundary_id,
            "package_id": self.package_id,
            "clouds_checkpoint": (
                self.clouds_checkpoint
            ),
            "conclusion": self.conclusion,
            "clouds_scope_complete": (
                self.clouds_scope_complete
            ),
            "external_tower_intake_required": (
                self.external_tower_intake_required
            ),
            "delivered_to_tower": (
                self.delivered_to_tower
            ),
            "tower_acceptance_recorded": (
                self.tower_acceptance_recorded
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class CloudsHandoffBoundarySurface:
    title: str

    boundaries: tuple[
        CloudsHandoffBoundaryRecord,
        ...
    ]

    receipts: tuple[
        CloudsHandoffCloseoutReceipt,
        ...
    ]

    boundary_count: int
    closeout_receipt_count: int

    ready_for_external_tower_intake_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "boundaries": [
                item.to_dict()
                for item in self.boundaries
            ],
            "receipts": [
                item.to_dict()
                for item in self.receipts
            ],
            "boundary_count": (
                self.boundary_count
            ),
            "closeout_receipt_count": (
                self.closeout_receipt_count
            ),
            "ready_for_external_tower_intake_count": (
                self
                .ready_for_external_tower_intake_count
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
