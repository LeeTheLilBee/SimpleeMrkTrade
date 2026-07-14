from tower.tower_ir_cert_p2387 import (
    intake_ob_completion_receipt,
)


HANDOFF = {
    "handoff_id": "oblaunch_1",
    "session_id": "session_1",
    "approved_room_id": "ob_room_dashboard",
    "canonical_path": "/dashboard",
}


def test_pack_2387_completion_receipt_accepted():
    result = intake_ob_completion_receipt(
        handoff=HANDOFF,
        ob_completion_payload={
            "handoff_id": "oblaunch_1",
            "session_id": "session_1",
            "room_id": "ob_room_dashboard",
            "canonical_path": "/dashboard",
            "completion_state": "completed_preview",
            "completion_time": "2026-07-14T12:05:00+00:00",
            "ob_receipt_reference": "ob_receipt_1",
        },
    )

    assert result["accepted"] is True
    assert len(result["tower_intake_integrity_hash"]) == 64


def test_pack_2387_wrong_room_rejected():
    result = intake_ob_completion_receipt(
        handoff=HANDOFF,
        ob_completion_payload={
            "handoff_id": "oblaunch_1",
            "session_id": "session_1",
            "room_id": "ob_room_owner_console",
            "canonical_path": "/dashboard",
            "completion_state": "completed_preview",
        },
    )

    assert result["accepted"] is False
    assert result["reason_code"] == (
        "ob_completion_room_mismatch"
    )
