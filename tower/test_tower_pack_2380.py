from tower.tower_ir_cert_p2380 import (
    build_ir_cert_p2380_preview,
    run_owner_rehearsal,
)


def test_pack_2380_dashboard_complete_rehearsal():
    result = run_owner_rehearsal(
        requested_path="/dashboard",
        mode="paper",
    )

    assert result["status"] == "passed"
    assert result["canonical_path"] == "/dashboard"

    assert result["clearance"][
        "canonical_clearance_value"
    ] == "ob_owner_command"

    assert result["close_receipt"][
        "ob_access_state"
    ] == "locked_back"

    assert all(
        step["passed"]
        for step in result["sequence"]
    )


def test_pack_2380_owner_console_complete_rehearsal():
    result = run_owner_rehearsal(
        requested_path="/owner-console",
        mode="paper",
        step_up_reference="stepup_owner_1",
    )

    assert result["status"] == "passed"
    assert result["room_id"] == "ob_room_owner_console"

    assert result["access_receipt"][
        "step_up_state"
    ] == "validated"

    assert result["close_receipt"][
        "step_up_state"
    ] == "consumed_or_revoked"


def test_pack_2380_unmapped_route_stays_blocked():
    result = run_owner_rehearsal(
        requested_path="/fake-ob-room",
        mode="paper",
    )

    assert result["status"] == "blocked"
    assert result["reason_code"] == (
        "ob_route_unmapped_default_deny"
    )


def test_pack_2380_checkpoint_ready():
    payload = build_ir_cert_p2380_preview()

    assert payload["complete_sequence_proven"] is True
    assert payload["safe_to_continue_to_pack_2381"] is True
