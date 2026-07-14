from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)


def test_pack_2377_launch_handoff_contract():
    handoff = create_ob_launch_handoff(
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
        issued_at="2026-07-13T12:00:00+00:00",
    )

    assert handoff["handoff_id"].startswith("oblaunch_")
    assert handoff["approved_room_id"] == (
        "ob_room_dashboard"
    )
    assert handoff["replay_policy"] == (
        "single_use_same_session"
    )
    assert len(handoff["integrity_hash"]) == 64

    safety = handoff["safety_boundaries"]

    assert safety["broker_order_submission"] is False
    assert safety["real_capital_movement"] is False
    assert safety["live_auto_activation"] is False
