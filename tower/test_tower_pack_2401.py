from tower.tower_ir_cert_p2401 import (
    project_launch_state,
)


def test_pack_2401_state_projection():
    result = project_launch_state(
        handoff={
            "handoff_id": "oblaunch_1",
            "authorization_state": "issued_preview",
        },
        transition_events=[
            {"action": "activate", "reference": "event_1"},
            {"action": "consume", "reference": "event_2"},
            {"action": "close", "reference": "event_3"},
            {"action": "lockback", "reference": "event_4"},
        ],
    )

    assert result["projected_state"] == "locked_back"
    assert result["terminal"] is True
    assert result["reusable"] is False


def test_pack_2401_terminal_reactivation_blocked():
    result = project_launch_state(
        handoff={
            "handoff_id": "oblaunch_1",
            "authorization_state": "revoked",
        },
        transition_events=[
            {"action": "activate", "reference": "bad"},
        ],
    )

    assert result["projected_state"] == "revoked"
    assert len(result["blocked_events"]) == 1
