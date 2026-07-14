from tower.tower_ir_cert_p2398 import (
    build_owner_session_audit,
)


def test_pack_2398_owner_audit_summary():
    summary = build_owner_session_audit(
        handoff={
            "handoff_id": "oblaunch_1",
            "owner_id": "owner_1",
            "session_id": "session_1",
            "approved_room_id": "ob_room_dashboard",
            "canonical_path": "/dashboard",
            "mode": "paper",
        },
        enforcement_decision={
            "allowed": True,
            "reason_code": "allow",
        },
        launch_use_receipt={
            "launch_use_receipt_id": "obuse_1",
        },
        completion_intake={
            "accepted": True,
        },
        close_receipt={
            "close_receipt_id": "obclose_1",
            "ob_access_state": "locked_back",
            "default_deny_restored": True,
        },
        denial_receipt=None,
    )

    assert summary["enforcement_result"] == "allowed"
    assert summary["final_ob_access_state"] == "locked_back"
