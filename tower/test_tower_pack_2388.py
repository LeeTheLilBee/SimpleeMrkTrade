from tower.tower_ir_cert_p2388 import (
    verify_ob_lockback,
)


def test_pack_2388_complete_lockback_verified():
    result = verify_ob_lockback(
        handoff={
            "handoff_id": "oblaunch_1",
            "approved_room_id": "ob_room_dashboard",
        },
        completion_intake={
            "accepted": True,
        },
        close_receipt={
            "handoff_id": "oblaunch_1",
            "launch_authorization_state": "revoked",
            "handoff_replay_state": "blocked",
            "ob_access_state": "locked_back",
            "default_deny_restored": True,
            "unmapped_routes_blocked": True,
            "step_up_state": "not_required",
        },
    )

    assert result["verified"] is True
    assert result["default_deny_active"] is True
