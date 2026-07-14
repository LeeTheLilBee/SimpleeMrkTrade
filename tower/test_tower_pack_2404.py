from tower.tower_ir_cert_p2404 import (
    detect_protected_session_drift,
)


HANDOFF = {
    "owner_id": "owner_1",
    "session_id": "session_1",
    "approved_room_id": "ob_room_dashboard",
    "canonical_path": "/dashboard",
    "mode": "paper",
}


def test_pack_2404_stable_session():
    result = detect_protected_session_drift(
        handoff=HANDOFF,
        current_owner_id="owner_1",
        current_session_id="session_1",
        current_room_id="ob_room_dashboard",
        current_path="/dashboard",
        current_mode="paper",
    )

    assert result["drift_detected"] is False


def test_pack_2404_session_drift_blocked():
    result = detect_protected_session_drift(
        handoff=HANDOFF,
        current_owner_id="owner_1",
        current_session_id="different_session",
        current_room_id="ob_room_dashboard",
        current_path="/dashboard",
        current_mode="paper",
    )

    assert result["drift_detected"] is True
    assert result["reason_code"] == (
        "ob_launch_session_mismatch"
    )
