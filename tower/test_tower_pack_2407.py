from tower.tower_ir_cert_p2407 import (
    create_protected_launch_incident_receipt,
)


def test_pack_2407_incident_receipt():
    receipt = create_protected_launch_incident_receipt(
        handoff={
            "handoff_id": "oblaunch_1",
            "owner_id": "owner_1",
            "session_id": "session_1",
            "approved_room_id": "ob_room_dashboard",
            "canonical_path": "/dashboard",
        },
        incident_type="session_drift",
        reason_code="ob_launch_session_mismatch",
        incident_stage="ob_room_entry",
        detected_at="2026-07-14T13:00:00+00:00",
        recovery_receipt={
            "recovery_receipt_id": "obrecovery_1",
            "recovery_status": "recovered_preview",
            "ob_access_state": "locked_back",
            "default_deny_restored": True,
        },
    )

    assert receipt["incident_receipt_id"].startswith(
        "obincident_"
    )
    assert receipt["ob_access_state"] == "locked_back"
    assert receipt["default_deny_restored"] is True
