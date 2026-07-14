from tower.tower_ir_cert_p2392 import (
    transition_launch_authorization,
)


def test_pack_2392_consume_transition():
    result = transition_launch_authorization(
        handoff_id="oblaunch_1",
        current_state="active_preview",
        requested_action="consume",
        reason_code="ob_launch_authorization_consumed",
        event_time="2026-07-14T12:00:00+00:00",
    )

    assert result["allowed"] is True
    assert result["next_state"] == "consumed"


def test_pack_2392_closed_cannot_reactivate():
    result = transition_launch_authorization(
        handoff_id="oblaunch_1",
        current_state="closed",
        requested_action="consume",
        reason_code="bad",
        event_time="2026-07-14T12:00:00+00:00",
    )

    assert result["allowed"] is False
    assert result["next_state"] == "closed"
