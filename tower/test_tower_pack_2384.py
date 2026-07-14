from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2384 import (
    validate_ob_launch_authorization,
)


def _handoff():
    return create_ob_launch_handoff(
        owner_id="owner_1",
        session_id="session_1",
        approved_room={
            "room_id": "ob_room_dashboard",
            "display_name": "Dashboard",
        },
        canonical_path="/dashboard",
        mode="paper",
        step_up_reference=None,
        clearance_decision_reference="obclr_1",
        issued_at="2026-07-14T12:00:00+00:00",
    )


def test_pack_2384_matching_launch_valid():
    handoff = _handoff()

    result = validate_ob_launch_authorization(
        decision_envelope={
            "allowed": True,
            "room_id": "ob_room_dashboard",
        },
        handoff=handoff,
        owner_id="owner_1",
        session_id="session_1",
        requested_path="/dashboard",
        requested_mode="paper",
    )

    assert result["allowed"] is True


def test_pack_2384_path_mismatch_blocked():
    handoff = _handoff()

    result = validate_ob_launch_authorization(
        decision_envelope={
            "allowed": True,
            "room_id": "ob_room_dashboard",
        },
        handoff=handoff,
        owner_id="owner_1",
        session_id="session_1",
        requested_path="/owner-console",
        requested_mode="paper",
    )

    assert result["allowed"] is False
    assert result["reason_code"] == (
        "ob_launch_path_scope_mismatch"
    )
