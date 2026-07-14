from tower.tower_ir_cert_p2386 import (
    evaluate_cross_room_scope,
)


HANDOFF = {
    "approved_room_id": "ob_room_dashboard",
    "canonical_path": "/dashboard",
    "mode": "paper",
    "session_id": "session_1",
}


def test_pack_2386_same_room_scope_valid():
    result = evaluate_cross_room_scope(
        handoff=HANDOFF,
        requested_room_id="ob_room_dashboard",
        requested_path="/dashboard",
        requested_mode="paper",
        requested_session_id="session_1",
    )

    assert result["allowed"] is True


def test_pack_2386_cross_room_blocked():
    result = evaluate_cross_room_scope(
        handoff=HANDOFF,
        requested_room_id="ob_room_owner_console",
        requested_path="/owner-console",
        requested_mode="paper",
        requested_session_id="session_1",
    )

    assert result["allowed"] is False
    assert result["reason_code"] == (
        "ob_cross_room_launch_blocked"
    )
