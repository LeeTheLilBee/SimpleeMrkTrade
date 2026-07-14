from tower.tower_ir_cert_p2396 import (
    verify_launch_receipt_chain,
)


def test_pack_2396_receipt_chain_verified():
    handoff = {
        "handoff_id": "oblaunch_1",
        "owner_id": "owner_1",
        "session_id": "session_1",
        "approved_room_id": "ob_room_dashboard",
        "canonical_path": "/dashboard",
    }

    result = verify_launch_receipt_chain(
        handoff=handoff,
        launch_use_receipt={
            "handoff_id": "oblaunch_1",
            "owner_id": "owner_1",
            "session_id": "session_1",
            "room_id": "ob_room_dashboard",
            "canonical_path": "/dashboard",
            "authorization_consumed": True,
        },
        room_access_receipt={
            "handoff_id": "oblaunch_1",
        },
        completion_intake={
            "handoff_id": "oblaunch_1",
            "accepted": True,
        },
        close_receipt={
            "handoff_id": "oblaunch_1",
            "launch_authorization_state": "revoked",
            "ob_access_state": "locked_back",
        },
    )

    assert result["verified"] is True
