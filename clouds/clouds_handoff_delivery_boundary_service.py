"""
GP017 — Clouds Handoff Delivery Boundary service.

No Tower delivery occurs.

This is the final Clouds-side closeout of the protected
handoff preparation corridor.
"""

from __future__ import annotations

try:
    from .clouds_handoff_delivery_boundary import (
        CloudsDeliveryBoundaryState,
        CloudsDeliveryState,
        CloudsHandoffBoundaryRecord,
        CloudsHandoffBoundarySurface,
        CloudsHandoffCloseoutReceipt,
    )

    from .tower_intake_package_service import (
        get_clouds_gp016_status_payload,
        get_tower_intake_packages,
    )

except ImportError:
    from clouds_handoff_delivery_boundary import (
        CloudsDeliveryBoundaryState,
        CloudsDeliveryState,
        CloudsHandoffBoundaryRecord,
        CloudsHandoffBoundarySurface,
        CloudsHandoffCloseoutReceipt,
    )

    from tower_intake_package_service import (
        get_clouds_gp016_status_payload,
        get_tower_intake_packages,
    )


def _boundary(package):
    ready = (
        package.validation_state == "valid"
        and len(package.package_hash) == 64
        and len(package.submission_hash) == 64
        and package.delivered_to_tower is False
        and package.tower_request_created is False
    )

    return CloudsHandoffBoundaryRecord(
        boundary_id=(
            f"clouds-boundary-{package.package_id}"
        ),
        package_id=package.package_id,
        submission_id=(
            package.submission_id
        ),
        destination_id=(
            package.destination_id
        ),
        package_hash=package.package_hash,
        submission_hash=(
            package.submission_hash
        ),
        boundary_state=(
            CloudsDeliveryBoundaryState
            .READY_FOR_EXTERNAL_TOWER_INTAKE.value
            if ready
            else CloudsDeliveryBoundaryState
            .BLOCKED.value
        ),
        delivery_state=(
            CloudsDeliveryState
            .NOT_DELIVERED.value
        ),
        tower_authority_required=True,
        owner_permission_requirement_preserved=(
            package.requires_owner_permission
        ),
        step_up_requirement_preserved=(
            package.requires_step_up
        ),
        clouds_work_complete=ready,
        delivered_to_tower=False,
        tower_request_created=False,
        tower_acceptance_recorded=False,
        tower_receipt_created=False,
        handoff_executed=False,
        downstream_execution_performed=False,
    )


def get_clouds_handoff_boundary_records():
    return tuple(
        _boundary(package)
        for package
        in get_tower_intake_packages()
    )


def get_clouds_handoff_boundary_record(
    boundary_id,
):
    for item in (
        get_clouds_handoff_boundary_records()
    ):
        if item.boundary_id == boundary_id:
            return item

    raise KeyError(
        f"Unknown Clouds handoff boundary: {boundary_id}"
    )


def _receipt(boundary):
    complete = (
        boundary.boundary_state
        == "ready_for_external_tower_intake"
        and boundary.clouds_work_complete
        and boundary.delivered_to_tower
        is False
    )

    return CloudsHandoffCloseoutReceipt(
        receipt_id=(
            f"clouds-closeout-{boundary.boundary_id}"
        ),
        boundary_id=boundary.boundary_id,
        package_id=boundary.package_id,
        clouds_checkpoint="GP017",
        conclusion=(
            "CLOUDS_SCOPE_COMPLETE_"
            "READY_FOR_EXTERNAL_TOWER_INTAKE_"
            "NOT_DELIVERED"
            if complete
            else
            "CLOUDS_SCOPE_BLOCKED"
        ),
        clouds_scope_complete=complete,
        external_tower_intake_required=complete,
        delivered_to_tower=False,
        tower_acceptance_recorded=False,
        execution_performed=False,
    )


def get_clouds_handoff_closeout_receipts():
    return tuple(
        _receipt(item)
        for item
        in get_clouds_handoff_boundary_records()
    )


def get_clouds_handoff_closeout_receipt(
    receipt_id,
):
    for item in (
        get_clouds_handoff_closeout_receipts()
    ):
        if item.receipt_id == receipt_id:
            return item

    raise KeyError(
        f"Unknown Clouds closeout receipt: {receipt_id}"
    )


def get_clouds_handoff_boundary_surface():
    boundaries = (
        get_clouds_handoff_boundary_records()
    )

    receipts = (
        get_clouds_handoff_closeout_receipts()
    )

    return CloudsHandoffBoundarySurface(
        title=(
            "Clouds Handoff Delivery Boundary "
            "/ Closeout Receipt"
        ),
        boundaries=boundaries,
        receipts=receipts,
        boundary_count=len(boundaries),
        closeout_receipt_count=len(
            receipts
        ),
        ready_for_external_tower_intake_count=sum(
            item.boundary_state
            == "ready_for_external_tower_intake"
            for item in boundaries
        ),
        boundary_notice=(
            "Clouds-side preparation is complete. "
            "Nothing has been delivered to Tower. "
            "Any actual Tower intake must occur in a "
            "separate Tower-controlled integration corridor."
        ),
    )


def get_clouds_handoff_boundary_surface_payload():
    return (
        get_clouds_handoff_boundary_surface()
        .to_dict()
    )


def get_clouds_gp017_status_payload():
    gp016 = get_clouds_gp016_status_payload()

    surface = (
        get_clouds_handoff_boundary_surface()
    )

    boundaries = surface.boundaries
    receipts = surface.receipts

    safe = (
        gp016["status"] == "ready"
        and gp016["safe_to_continue"] is True
        and surface.boundary_count
        == gp016["package_count"]
        and surface.closeout_receipt_count
        == surface.boundary_count
        and surface
        .ready_for_external_tower_intake_count
        == surface.boundary_count
        and all(
            item.clouds_work_complete
            is True
            for item in boundaries
        )
        and all(
            item.delivered_to_tower is False
            and item.tower_request_created is False
            and item.tower_acceptance_recorded is False
            and item.tower_receipt_created is False
            and item.handoff_executed is False
            and item.downstream_execution_performed
            is False
            for item in boundaries
        )
        and all(
            item.clouds_scope_complete
            is True
            and item.external_tower_intake_required
            is True
            and item.delivered_to_tower is False
            and item.tower_acceptance_recorded
            is False
            and item.execution_performed is False
            for item in receipts
        )
    )

    return {
        "pack": "GP017",
        "section": (
            "CLOUDS HANDOFF DELIVERY BOUNDARY "
            "/ CLOSEOUT RECEIPT SURFACE"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "boundary_count": (
            surface.boundary_count
        ),
        "closeout_receipt_count": (
            surface.closeout_receipt_count
        ),
        "ready_for_external_tower_intake_count": (
            surface
            .ready_for_external_tower_intake_count
        ),
        "clouds_handoff_scope_complete": safe,
        "external_tower_intake_required": True,
        "delivered_to_tower": False,
        "tower_request_created": False,
        "tower_acceptance_recorded": False,
        "tower_receipt_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP018 — SIMPLEE OPERATING DATA "
            "ADAPTER FOUNDATION"
        ),
    }
