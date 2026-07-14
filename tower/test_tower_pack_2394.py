from tower.tower_ir_cert_p2394 import (
    create_authorization_denial_receipt,
)


def test_pack_2394_denial_receipt():
    receipt = create_authorization_denial_receipt(
        request_id="request_1",
        owner_id="owner_1",
        session_id="session_1",
        requested_room_id="ob_room_dashboard",
        requested_path="/dashboard",
        requested_mode="paper",
        reason_code="ob_launch_handoff_replay_blocked",
        denied_at="2026-07-14T12:00:00+00:00",
        handoff_id="oblaunch_1",
    )

    assert receipt["decision"] == "deny"
    assert receipt["ob_access_granted"] is False
    assert receipt["default_deny_preserved"] is True
