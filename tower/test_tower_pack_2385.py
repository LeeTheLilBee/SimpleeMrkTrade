from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2385 import (
    evaluate_handoff_replay_guard,
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


def test_pack_2385_fresh_handoff_allowed():
    handoff = _handoff()

    result = evaluate_handoff_replay_guard(
        handoff=handoff,
        evaluation_time="2026-07-14T12:00:01+00:00",
        consumed_handoff_ids=[],
        revoked_handoff_ids=[],
    )

    assert result["allowed"] is True


def test_pack_2385_consumed_handoff_blocked():
    handoff = _handoff()

    result = evaluate_handoff_replay_guard(
        handoff=handoff,
        evaluation_time="2026-07-14T12:00:01+00:00",
        consumed_handoff_ids=[handoff["handoff_id"]],
        revoked_handoff_ids=[],
    )

    assert result["allowed"] is False
    assert result["reason_code"] == (
        "ob_launch_handoff_replay_blocked"
    )
