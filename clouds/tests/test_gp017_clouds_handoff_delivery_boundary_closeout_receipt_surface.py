import ast
from pathlib import Path

import pytest

from clouds.clouds_handoff_delivery_boundary_service import (
    get_clouds_gp017_status_payload,
    get_clouds_handoff_boundary_record,
    get_clouds_handoff_boundary_records,
    get_clouds_handoff_boundary_surface,
    get_clouds_handoff_boundary_surface_payload,
    get_clouds_handoff_closeout_receipt,
    get_clouds_handoff_closeout_receipts,
)


def test_gp017_boundary_inventory():
    assert len(
        get_clouds_handoff_boundary_records()
    ) == 11


def test_gp017_receipt_inventory():
    assert len(
        get_clouds_handoff_closeout_receipts()
    ) == 11


def test_gp017_all_ready_for_external_tower():
    assert all(
        item.boundary_state
        == "ready_for_external_tower_intake"
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_clouds_scope_complete():
    assert all(
        item.clouds_work_complete is True
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_delivery_state_not_delivered():
    assert all(
        item.delivery_state == "not_delivered"
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_tower_delivery():
    assert all(
        item.delivered_to_tower is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_tower_request():
    assert all(
        item.tower_request_created is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_tower_acceptance():
    assert all(
        item.tower_acceptance_recorded
        is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_tower_receipt():
    assert all(
        item.tower_receipt_created is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_handoff_execution():
    assert all(
        item.handoff_executed is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_no_downstream_execution():
    assert all(
        item.downstream_execution_performed
        is False
        for item
        in get_clouds_handoff_boundary_records()
    )


def test_gp017_receipt_conclusion():
    assert all(
        item.conclusion
        ==
        (
            "CLOUDS_SCOPE_COMPLETE_"
            "READY_FOR_EXTERNAL_TOWER_INTAKE_"
            "NOT_DELIVERED"
        )
        for item
        in get_clouds_handoff_closeout_receipts()
    )


def test_gp017_receipts_require_external_tower():
    assert all(
        item.external_tower_intake_required
        is True
        for item
        in get_clouds_handoff_closeout_receipts()
    )


def test_gp017_receipts_do_not_claim_delivery():
    assert all(
        item.delivered_to_tower is False
        and item.tower_acceptance_recorded
        is False
        and item.execution_performed
        is False
        for item
        in get_clouds_handoff_closeout_receipts()
    )


def test_gp017_lookup():
    boundary = (
        get_clouds_handoff_boundary_records()[0]
    )

    receipt = (
        get_clouds_handoff_closeout_receipts()[0]
    )

    assert (
        get_clouds_handoff_boundary_record(
            boundary.boundary_id
        )
        == boundary
    )

    assert (
        get_clouds_handoff_closeout_receipt(
            receipt.receipt_id
        )
        == receipt
    )


def test_gp017_unknown_fails_closed():
    with pytest.raises(KeyError):
        get_clouds_handoff_boundary_record(
            "missing"
        )

    with pytest.raises(KeyError):
        get_clouds_handoff_closeout_receipt(
            "missing"
        )


def test_gp017_surface_counts():
    surface = (
        get_clouds_handoff_boundary_surface()
    )

    assert surface.boundary_count == 11
    assert surface.closeout_receipt_count == 11

    assert (
        surface
        .ready_for_external_tower_intake_count
        == 11
    )


def test_gp017_surface_notice():
    text = (
        get_clouds_handoff_boundary_surface()
        .boundary_notice
        .lower()
    )

    assert "nothing has been delivered" in text
    assert "tower-controlled" in text


def test_gp017_payload():
    payload = (
        get_clouds_handoff_boundary_surface_payload()
    )

    assert payload["boundary_count"] == 11
    assert payload["closeout_receipt_count"] == 11


def test_gp017_status():
    status = get_clouds_gp017_status_payload()

    assert status["pack"] == "GP017"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert status["boundary_count"] == 11
    assert status["closeout_receipt_count"] == 11

    assert (
        status["clouds_handoff_scope_complete"]
        is True
    )

    assert (
        status["external_tower_intake_required"]
        is True
    )

    assert (
        status["delivered_to_tower"]
        is False
    )

    assert (
        status["tower_request_created"]
        is False
    )

    assert (
        status["tower_acceptance_recorded"]
        is False
    )

    assert (
        status["tower_receipt_created"]
        is False
    )

    assert (
        status["handoff_executed"]
        is False
    )

    assert (
        status["downstream_execution_performed"]
        is False
    )

    assert status["next_pack"] == (
        "GP018 — SIMPLEE OPERATING DATA "
        "ADAPTER FOUNDATION"
    )


def test_gp017_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "clouds_handoff_delivery_boundary.py",
        root / "clouds" / "clouds_handoff_delivery_boundary_service.py",
    )

    forbidden = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in files:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0].lower()
                        not in forbidden
                    )

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                assert (
                    module.lstrip(".")
                    .split(".")[0]
                    .lower()
                    not in forbidden
                )
