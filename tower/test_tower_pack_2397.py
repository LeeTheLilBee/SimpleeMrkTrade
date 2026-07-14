from tower.tower_ir_cert_p2397 import (
    create_emergency_lockback,
)


def test_pack_2397_emergency_lockback():
    receipt = create_emergency_lockback(
        handoff={
            "handoff_id": "oblaunch_1",
            "owner_id": "owner_1",
            "session_id": "session_1",
            "approved_room_id": "ob_room_dashboard",
            "step_up_reference": None,
        },
        trigger_code="owner_emergency_close",
        detected_at="2026-07-14T12:00:00+00:00",
    )

    assert receipt["ob_access_state"] == "locked_back"
    assert receipt["default_deny_restored"] is True
    assert receipt["handoff_replay_state"] == "blocked"
