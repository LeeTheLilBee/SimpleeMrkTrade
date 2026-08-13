import ast
from pathlib import Path

import pytest

from clouds.executive_owner_handoff_submission_service import (
    get_clouds_gp015_status_payload,
    get_handoff_submission_packet,
    get_handoff_submission_packet_by_draft,
    get_handoff_submission_packets,
    get_tower_intake_preparation_surface,
    get_tower_intake_preparation_surface_payload,
)


def test_gp015_submission_inventory():
    status = get_clouds_gp015_status_payload()

    packets = get_handoff_submission_packets()

    assert len(packets) == status["submission_count"]
    assert len(packets) == 11


def test_gp015_all_are_ready():
    packets = get_handoff_submission_packets()

    assert all(
        item.preparation_state == "ready"
        for item in packets
    )


def test_gp015_hashes_are_sha256():
    for item in get_handoff_submission_packets():
        assert len(item.submission_hash) == 64
        int(item.submission_hash, 16)


def test_gp015_hashes_are_deterministic():
    first = [
        item.submission_hash
        for item in get_handoff_submission_packets()
    ]

    second = [
        item.submission_hash
        for item in get_handoff_submission_packets()
    ]

    assert first == second


def test_gp015_requirements_exist():
    for item in get_handoff_submission_packets():
        assert len(item.requirements) == 6


def test_gp015_submission_is_authorized():
    for item in get_handoff_submission_packets():
        assert item.submission_authorized is True


def test_gp015_permission_and_step_up_are_preserved():
    for item in get_handoff_submission_packets():
        labels = {
            requirement.label
            for requirement in item.requirements
        }

        assert (
            "Owner permission requirement preserved"
            in labels
        )

        assert (
            "Step-up requirement preserved"
            in labels
        )


def test_gp015_no_tower_request_created():
    assert all(
        item.tower_request_created is False
        for item in get_handoff_submission_packets()
    )


def test_gp015_no_delivery():
    assert all(
        item.delivered_to_tower is False
        for item in get_handoff_submission_packets()
    )


def test_gp015_no_receipt():
    assert all(
        item.tower_receipt_created is False
        for item in get_handoff_submission_packets()
    )


def test_gp015_no_handoff():
    assert all(
        item.handoff_executed is False
        for item in get_handoff_submission_packets()
    )


def test_gp015_no_downstream_execution():
    assert all(
        item.downstream_execution_performed is False
        for item in get_handoff_submission_packets()
    )


def test_gp015_lookup():
    item = get_handoff_submission_packets()[0]

    assert (
        get_handoff_submission_packet(
            item.submission_id
        )
        == item
    )

    assert (
        get_handoff_submission_packet_by_draft(
            item.draft_id
        )
        == item
    )


def test_gp015_unknown_submission_fails_closed():
    with pytest.raises(KeyError):
        get_handoff_submission_packet(
            "missing"
        )


def test_gp015_unknown_draft_fails_closed():
    with pytest.raises(KeyError):
        get_handoff_submission_packet_by_draft(
            "missing"
        )


def test_gp015_surface_counts():
    surface = (
        get_tower_intake_preparation_surface()
    )

    assert surface.submission_count == 11
    assert surface.ready_count == 11
    assert surface.blocked_count == 0


def test_gp015_surface_payload():
    payload = (
        get_tower_intake_preparation_surface_payload()
    )

    assert payload["submission_count"] == 11
    assert len(payload["submissions"]) == 11


def test_gp015_status():
    status = get_clouds_gp015_status_payload()

    assert status["pack"] == "GP015"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["submission_count"] == 11
    assert status["ready_count"] == 11
    assert status["blocked_count"] == 0
    assert status["tower_request_created"] is False
    assert status["delivery_performed"] is False
    assert status["tower_receipt_created"] is False
    assert status["handoff_executed"] is False
    assert status["downstream_execution_performed"] is False


def test_gp015_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "executive_owner_handoff_submission.py",
        root / "clouds" / "executive_owner_handoff_submission_service.py",
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
