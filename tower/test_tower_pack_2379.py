from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2378 import (
    create_room_access_receipt,
)
from tower.tower_ir_cert_p2379 import (
    close_ob_launch_session,
)


def test_pack_2379_close_and_lockback():
    handoff = create_ob_launch_handoff(
        owner_id="owner_1",
        session_id="session_1",
        approved_room={
            "room_id": "ob_room_owner_console",
            "display_name": "Owner Console",
        },
        canonical_path="/owner-console",
        mode="paper",
        step_up_reference="stepup_1",
        clearance_decision_reference="obclr_1",
        issued_at="2026-07-13T12:00:00+00:00",
    )

    access = create_room_access_receipt(
        handoff=handoff,
        bridge_decision="ob_room_contract_allow",
        clearance_value="ob_owner_command",
        clearance_rank=900,
        step_up_state="validated",
        launch_time="2026-07-13T12:00:01+00:00",
    )

    close = close_ob_launch_session(
        handoff=handoff,
        access_receipt=access,
        close_time="2026-07-13T12:05:00+00:00",
        close_reason="rehearsal_complete",
    )

    assert close["launch_authorization_state"] == (
        "revoked"
    )
    assert close["handoff_replay_state"] == "blocked"
    assert close["step_up_state"] == (
        "consumed_or_revoked"
    )
    assert close["ob_access_state"] == "locked_back"
    assert close["default_deny_restored"] is True
