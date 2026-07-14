from tower.tower_ir_cert_p2383 import (
    build_room_decision_envelope,
)


def test_pack_2383_allowed_decision_envelope():
    envelope = build_room_decision_envelope(
        bridge_request={
            "valid": True,
            "request_id": "request_1",
            "request_integrity_reference": "obreq_1",
        },
        route_decision={
            "allowed": True,
            "room_id": "ob_room_dashboard",
            "canonical_path": "/dashboard",
            "object_context": {},
        },
        clearance_decision={
            "allowed": True,
            "canonical_clearance_value": (
                "ob_owner_command"
            ),
            "canonical_clearance_rank": 900,
            "clearance_decision_reference": "obclr_1",
        },
        room_access_decision={
            "allowed": True,
            "reason_code": "ob_room_contract_allow",
            "step_up_reference": None,
        },
    )

    assert envelope["allowed"] is True
    assert envelope["room_id"] == "ob_room_dashboard"
    assert len(envelope["decision_integrity_hash"]) == 64
