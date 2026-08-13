
"""
Canonical Tower-side Clouds intake contract.

This is the Tower integration boundary for Clouds GP016/GP017 packages.
It does not claim Clouds GP024 defined Flask session keys. Tower defines
its own explicit integration handoff when launching Clouds through Tower.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Dict, List


APP_ID = "clouds"
APP_NAME = "The Clouds"
CANONICAL_OWNER_ROUTE = "/clouds"
CANONICAL_OWNER_SURFACE = "OwnerCommandExperience"
CANONICAL_OWNER_SERVICE_GETTER = "get_owner_command_experience"
CANONICAL_TITLE = "The Clouds"
CANONICAL_SUBTITLE = "Simplee World Owner Command"

TOWER_INTAKE_PACKAGE_TYPE = "TowerIntakePackage"
TOWER_INTAKE_PACKAGE_VERSION = "clouds-gp016-v1"

BOUNDARY_RECORD_TYPE = "CloudsHandoffBoundaryRecord"
CANONICAL_BOUNDARY_STATE = "ready_for_external_tower_intake"
CANONICAL_DELIVERY_STATE = "not_delivered"

REQUIRED_TOWER_INTAKE_FIELDS = (
    "package_id",
    "package_version",
    "submission_id",
    "draft_id",
    "envelope_id",
    "authorization_id",
    "destination_id",
    "open_route",
    "submission_hash",
    "package_hash",
    "requires_owner_permission",
    "requires_step_up",
    "validation_state",
    "checks",
    "delivery_authorized",
    "delivered_to_tower",
    "tower_request_created",
    "tower_receipt_created",
    "handoff_executed",
    "downstream_execution_performed",
)

REQUIRED_CHECK_FIELDS = (
    "check_id",
    "label",
    "passed",
    "explanation",
    "display_order",
)

REQUIRED_BOUNDARY_FIELDS = (
    "boundary_id",
    "package_id",
    "submission_id",
    "destination_id",
    "package_hash",
    "submission_hash",
    "boundary_state",
    "delivery_state",
    "tower_authority_required",
    "owner_permission_requirement_preserved",
    "step_up_requirement_preserved",
    "clouds_work_complete",
    "delivered_to_tower",
    "tower_request_created",
    "tower_acceptance_recorded",
    "tower_receipt_created",
    "handoff_executed",
    "downstream_execution_performed",
)


@dataclass(frozen=True)
class TowerCloudsValidation:
    valid: bool
    reason_code: str
    package_id: str
    errors: List[str]
    normalized: Dict[str, Any]


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def build_canonical_tower_intake_package(
    *,
    submission_id: str = "clouds-owner-command-gp024",
) -> Dict[str, Any]:
    package_id = f"tower-intake-{submission_id}"

    return {
        "package_id": package_id,
        "package_version": TOWER_INTAKE_PACKAGE_VERSION,
        "submission_id": submission_id,
        "draft_id": f"clouds-draft-{submission_id}",
        "envelope_id": f"clouds-envelope-{submission_id}",
        "authorization_id": f"clouds-authorization-{submission_id}",
        "destination_id": APP_ID,
        "open_route": CANONICAL_OWNER_ROUTE,
        "submission_hash": "clouds-submission-hash-gp024",
        "package_hash": "clouds-package-hash-gp024",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "validation_state": "validated",
        "checks": [
            {
                "check_id": "protected-tower-launch-reference",
                "label": "Protected Tower launch reference exists",
                "passed": True,
                "explanation": "Tower remains the protected owner entry authority for The Clouds.",
                "display_order": 10,
            },
            {
                "check_id": "clouds-owner-command-opens",
                "label": "Clouds owner command opens",
                "passed": True,
                "explanation": "The canonical owner command route reference is /clouds.",
                "display_order": 20,
            },
            {
                "check_id": "soulaana-explains-first",
                "label": "Soulaana explains first",
                "passed": True,
                "explanation": "The Clouds should lead with Soulaana's explanation layer.",
                "display_order": 30,
            },
            {
                "check_id": "protected-handoff-remains-non-executing",
                "label": "Protected handoff remains non-executing",
                "passed": True,
                "explanation": "Tower launch does not execute downstream actions.",
                "display_order": 40,
            },
        ],
        "delivery_authorized": False,
        "delivered_to_tower": False,
        "tower_request_created": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
    }


def build_canonical_clouds_boundary_record(
    *,
    package: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "boundary_id": f"clouds-boundary-{package['submission_id']}",
        "package_id": package["package_id"],
        "submission_id": package["submission_id"],
        "destination_id": package["destination_id"],
        "package_hash": package["package_hash"],
        "submission_hash": package["submission_hash"],
        "boundary_state": CANONICAL_BOUNDARY_STATE,
        "delivery_state": CANONICAL_DELIVERY_STATE,
        "tower_authority_required": True,
        "owner_permission_requirement_preserved": True,
        "step_up_requirement_preserved": True,
        "clouds_work_complete": True,
        "delivered_to_tower": False,
        "tower_request_created": False,
        "tower_acceptance_recorded": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
    }


def validate_tower_clouds_intake_package(
    package: Mapping[str, Any],
) -> TowerCloudsValidation:
    errors: List[str] = []

    if not isinstance(package, Mapping):
        return TowerCloudsValidation(
            valid=False,
            reason_code="tower_clouds_intake_mapping_required",
            package_id="",
            errors=["package_not_mapping"],
            normalized={},
        )

    normalized = dict(package)

    for field in REQUIRED_TOWER_INTAKE_FIELDS:
        if field not in normalized:
            errors.append(f"missing:{field}")

    package_id = str(normalized.get("package_id") or "").strip()
    submission_id = str(normalized.get("submission_id") or "").strip()

    if not _text(package_id):
        errors.append("package_id_required")

    if not _text(submission_id):
        errors.append("submission_id_required")

    if package_id and submission_id and package_id != f"tower-intake-{submission_id}":
        errors.append("package_id_must_be_tower_intake_submission_id")

    if normalized.get("package_version") != TOWER_INTAKE_PACKAGE_VERSION:
        errors.append("package_version_must_be_clouds_gp016_v1")

    if normalized.get("destination_id") != APP_ID:
        errors.append("destination_id_must_be_clouds")

    if normalized.get("open_route") != CANONICAL_OWNER_ROUTE:
        errors.append("open_route_must_be_clouds")

    for field in (
        "draft_id",
        "envelope_id",
        "authorization_id",
        "submission_hash",
        "package_hash",
        "validation_state",
    ):
        if not _text(normalized.get(field)):
            errors.append(f"{field}_required")

    if normalized.get("requires_owner_permission") is not True:
        errors.append("requires_owner_permission_must_be_true")

    if normalized.get("requires_step_up") is not True:
        errors.append("requires_step_up_must_be_true")

    for field in (
        "delivery_authorized",
        "delivered_to_tower",
        "tower_request_created",
        "tower_receipt_created",
        "handoff_executed",
        "downstream_execution_performed",
    ):
        if normalized.get(field) is not False:
            errors.append(f"{field}_must_be_false_before_tower_acceptance")

    checks = normalized.get("checks")
    if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)) or not checks:
        errors.append("checks_sequence_required")
    else:
        for index, check in enumerate(checks):
            if not isinstance(check, Mapping):
                errors.append(f"check_{index}_mapping_required")
                continue

            for field in REQUIRED_CHECK_FIELDS:
                if field not in check:
                    errors.append(f"check_{index}_missing_{field}")

            if check.get("passed") is not True:
                errors.append(f"check_{index}_passed_must_be_true")

            if not isinstance(check.get("display_order"), int):
                errors.append(f"check_{index}_display_order_int_required")

    if errors:
        return TowerCloudsValidation(
            valid=False,
            reason_code="tower_clouds_intake_invalid",
            package_id=package_id,
            errors=errors,
            normalized=normalized,
        )

    return TowerCloudsValidation(
        valid=True,
        reason_code="tower_clouds_intake_validated",
        package_id=package_id,
        errors=[],
        normalized=normalized,
    )


def validate_clouds_handoff_boundary_record(
    record: Mapping[str, Any],
) -> TowerCloudsValidation:
    errors: List[str] = []

    if not isinstance(record, Mapping):
        return TowerCloudsValidation(
            valid=False,
            reason_code="clouds_handoff_boundary_mapping_required",
            package_id="",
            errors=["boundary_not_mapping"],
            normalized={},
        )

    normalized = dict(record)

    for field in REQUIRED_BOUNDARY_FIELDS:
        if field not in normalized:
            errors.append(f"missing:{field}")

    package_id = str(normalized.get("package_id") or "").strip()

    if normalized.get("destination_id") != APP_ID:
        errors.append("boundary_destination_id_must_be_clouds")

    if normalized.get("boundary_state") != CANONICAL_BOUNDARY_STATE:
        errors.append("boundary_state_must_be_ready_for_external_tower_intake")

    if normalized.get("delivery_state") != CANONICAL_DELIVERY_STATE:
        errors.append("delivery_state_must_be_not_delivered")

    for field in (
        "tower_authority_required",
        "owner_permission_requirement_preserved",
        "step_up_requirement_preserved",
        "clouds_work_complete",
    ):
        if normalized.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in (
        "delivered_to_tower",
        "tower_request_created",
        "tower_acceptance_recorded",
        "tower_receipt_created",
        "handoff_executed",
        "downstream_execution_performed",
    ):
        if normalized.get(field) is not False:
            errors.append(f"{field}_must_be_false_before_tower_acceptance")

    if errors:
        return TowerCloudsValidation(
            valid=False,
            reason_code="clouds_handoff_boundary_invalid",
            package_id=package_id,
            errors=errors,
            normalized=normalized,
        )

    return TowerCloudsValidation(
        valid=True,
        reason_code="clouds_handoff_boundary_validated",
        package_id=package_id,
        errors=[],
        normalized=normalized,
    )
