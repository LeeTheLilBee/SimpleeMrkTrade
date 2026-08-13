"""
GP016 Tower Intake Package validation.

No delivery occurs.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .executive_owner_handoff_submission_service import (
        get_clouds_gp015_status_payload,
        get_handoff_submission_packets,
    )

    from .tower_intake_package import (
        TowerIntakePackage,
        TowerIntakePackageState,
        TowerIntakeValidationCheck,
        TowerIntakeValidationSurface,
    )

except ImportError:
    from executive_owner_handoff_submission_service import (
        get_clouds_gp015_status_payload,
        get_handoff_submission_packets,
    )

    from tower_intake_package import (
        TowerIntakePackage,
        TowerIntakePackageState,
        TowerIntakeValidationCheck,
        TowerIntakeValidationSurface,
    )


def _hash(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def _build_package(submission):
    checks = (
        TowerIntakeValidationCheck(
            check_id=(
                f"{submission.submission_id}-ready"
            ),
            label="Submission preparation ready",
            passed=(
                submission.preparation_state
                == "ready"
            ),
            explanation=(
                "GP015 submission must be ready."
            ),
            display_order=10,
        ),

        TowerIntakeValidationCheck(
            check_id=(
                f"{submission.submission_id}-authorized"
            ),
            label="Submission authorized",
            passed=(
                submission.submission_authorized
            ),
            explanation=(
                "Owner-side submission authorization "
                "must remain true."
            ),
            display_order=20,
        ),

        TowerIntakeValidationCheck(
            check_id=(
                f"{submission.submission_id}-boundary"
            ),
            label="Tower boundary preserved",
            passed=(
                submission.tower_boundary_preserved
            ),
            explanation=(
                "Clouds may prepare intake but may not "
                "perform Tower authority."
            ),
            display_order=30,
        ),

        TowerIntakeValidationCheck(
            check_id=(
                f"{submission.submission_id}-destination"
            ),
            label="Protected destination valid",
            passed=bool(
                submission.destination_id
                and submission.open_route
            ),
            explanation=(
                "Protected destination and route must exist."
            ),
            display_order=40,
        ),

        TowerIntakeValidationCheck(
            check_id=(
                f"{submission.submission_id}-hash"
            ),
            label="Submission integrity hash valid",
            passed=(
                len(submission.submission_hash)
                == 64
            ),
            explanation=(
                "GP015 submission hash must remain valid."
            ),
            display_order=50,
        ),
    )

    valid = all(
        check.passed
        for check in checks
    )

    integrity = {
        "submission_id": submission.submission_id,
        "draft_id": submission.draft_id,
        "envelope_id": submission.envelope_id,
        "authorization_id": (
            submission.authorization_id
        ),
        "destination_id": (
            submission.destination_id
        ),
        "open_route": submission.open_route,
        "submission_hash": (
            submission.submission_hash
        ),
        "requires_owner_permission": (
            submission.requires_owner_permission
        ),
        "requires_step_up": (
            submission.requires_step_up
        ),
    }

    return TowerIntakePackage(
        package_id=(
            f"tower-intake-{submission.submission_id}"
        ),
        package_version="clouds-gp016-v1",
        submission_id=(
            submission.submission_id
        ),
        draft_id=submission.draft_id,
        envelope_id=submission.envelope_id,
        authorization_id=(
            submission.authorization_id
        ),
        destination_id=(
            submission.destination_id
        ),
        open_route=submission.open_route,
        submission_hash=(
            submission.submission_hash
        ),
        package_hash=_hash(integrity),
        requires_owner_permission=(
            submission.requires_owner_permission
        ),
        requires_step_up=(
            submission.requires_step_up
        ),
        validation_state=(
            TowerIntakePackageState.VALID.value
            if valid
            else TowerIntakePackageState.INVALID.value
        ),
        checks=checks,
        delivery_authorized=False,
        delivered_to_tower=False,
        tower_request_created=False,
        tower_receipt_created=False,
        handoff_executed=False,
        downstream_execution_performed=False,
    )


def get_tower_intake_packages():
    return tuple(
        _build_package(item)
        for item in get_handoff_submission_packets()
    )


def get_tower_intake_package(package_id):
    for item in get_tower_intake_packages():
        if item.package_id == package_id:
            return item

    raise KeyError(
        f"Unknown Tower intake package: {package_id}"
    )


def get_tower_intake_package_by_submission(
    submission_id,
):
    for item in get_tower_intake_packages():
        if (
            item.submission_id
            == submission_id
        ):
            return item

    raise KeyError(
        "No Tower intake package for submission: "
        f"{submission_id}"
    )


def get_tower_intake_validation_surface():
    packages = get_tower_intake_packages()

    return TowerIntakeValidationSurface(
        title="Tower Intake Package Validation",
        packages=packages,
        package_count=len(packages),
        valid_count=sum(
            item.validation_state == "valid"
            for item in packages
        ),
        invalid_count=sum(
            item.validation_state == "invalid"
            for item in packages
        ),
        boundary_notice=(
            "Validated means ready for a future delivery "
            "boundary. Clouds has not delivered to Tower."
        ),
    )


def get_tower_intake_validation_surface_payload():
    return (
        get_tower_intake_validation_surface()
        .to_dict()
    )


def get_clouds_gp016_status_payload():
    gp015 = get_clouds_gp015_status_payload()
    surface = (
        get_tower_intake_validation_surface()
    )

    packages = surface.packages

    safe = (
        gp015["status"] == "ready"
        and gp015["safe_to_continue"] is True
        and surface.package_count
        == gp015["submission_count"]
        and surface.invalid_count == 0
        and surface.valid_count
        == surface.package_count
        and all(
            len(item.package_hash) == 64
            for item in packages
        )
        and all(
            item.delivery_authorized is False
            and item.delivered_to_tower is False
            and item.tower_request_created is False
            and item.tower_receipt_created is False
            and item.handoff_executed is False
            and item.downstream_execution_performed
            is False
            for item in packages
        )
    )

    return {
        "pack": "GP016",
        "section": (
            "TOWER INTAKE PACKAGE "
            "/ VALIDATION SURFACE"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "package_count": surface.package_count,
        "valid_count": surface.valid_count,
        "invalid_count": surface.invalid_count,
        "tower_boundary_preserved": True,
        "delivery_authorized": False,
        "delivery_performed": False,
        "tower_request_created": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP017 — CLOUDS HANDOFF DELIVERY "
            "BOUNDARY / CLOSEOUT RECEIPT SURFACE"
        ),
    }
