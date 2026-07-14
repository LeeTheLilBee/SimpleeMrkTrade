from tower.tower_ir_cert_p2406 import (
    recover_failed_protected_launch,
)


def test_pack_2406_failed_launch_recovery():
    recovery = recover_failed_protected_launch(
        handoff={
            "handoff_id": "oblaunch_1",
            "owner_id": "owner_1",
            "session_id": "session_1",
            "approved_room_id": "ob_room_owner_console",
        },
        failure_code="ob_step_up_not_valid",
        failure_stage="step_up",
        detected_at="2026-07-14T13:00:00+00:00",
        step_up_required=True,
    )

    assert recovery["launch_authorization_state"] == (
        "revoked"
    )
    assert recovery["handoff_replay_state"] == "blocked"
    assert recovery["step_up_state"] == "revoked"
    assert recovery["ob_access_state"] == "locked_back"
    assert recovery["default_deny_restored"] is True
