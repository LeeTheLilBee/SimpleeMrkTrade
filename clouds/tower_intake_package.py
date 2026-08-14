"""
GP016 Tower Intake Package contracts.

Clouds builds and validates the package.
Clouds does not deliver the package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TowerIntakePackageState(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class TowerIntakeValidationCheck:
    check_id: str
    label: str
    passed: bool
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "label": self.label,
            "passed": self.passed,
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class TowerIntakePackage:
    package_id: str
    package_version: str

    submission_id: str
    draft_id: str
    envelope_id: str
    authorization_id: str

    destination_id: str
    open_route: str

    submission_hash: str
    package_hash: str

    requires_owner_permission: bool
    requires_step_up: bool

    validation_state: str

    checks: tuple[
        TowerIntakeValidationCheck,
        ...
    ]

    delivery_authorized: bool
    delivered_to_tower: bool
    tower_request_created: bool
    tower_receipt_created: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "package_version": self.package_version,
            "submission_id": self.submission_id,
            "draft_id": self.draft_id,
            "envelope_id": self.envelope_id,
            "authorization_id": self.authorization_id,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "submission_hash": self.submission_hash,
            "package_hash": self.package_hash,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": (
                self.requires_step_up
            ),
            "validation_state": (
                self.validation_state
            ),
            "checks": [
                item.to_dict()
                for item in self.checks
            ],
            "delivery_authorized": (
                self.delivery_authorized
            ),
            "delivered_to_tower": (
                self.delivered_to_tower
            ),
            "tower_request_created": (
                self.tower_request_created
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
class TowerIntakeValidationSurface:
    title: str
    packages: tuple[
        TowerIntakePackage,
        ...
    ]

    package_count: int
    valid_count: int
    invalid_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "packages": [
                item.to_dict()
                for item in self.packages
            ],
            "package_count": self.package_count,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "boundary_notice": self.boundary_notice,
        }
