from tower.tower_ir_cert_p2395 import (
    create_launch_use_receipt,
)


def test_pack_2395_use_receipt_consumes_authorization():
    receipt = create_launch_use_receipt(
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
            "reason_code": (
                "ob_protected_route_enforcement_allow"
            ),
        },
        used_at="2026-07-14T12:00:00+00:00",
        state_transition_reference="obauthstate_1",
    )

    assert receipt["authorization_consumed"] is True
    assert receipt["replay_allowed"] is False
