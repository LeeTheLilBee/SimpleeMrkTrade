from tower.tower_ir_cert_p2402 import (
    verify_step_up_lifecycle,
)


def test_pack_2402_valid_step_up():
    result = verify_step_up_lifecycle(
        step_up_required=True,
        step_up_reference="stepup_1",
        step_up_state="validated",
        owner_id="owner_1",
        step_up_owner_id="owner_1",
        session_id="session_1",
        step_up_session_id="session_1",
        room_id="ob_room_owner_console",
        step_up_room_id="ob_room_owner_console",
    )

    assert result["allowed"] is True


def test_pack_2402_revoked_step_up_blocked():
    result = verify_step_up_lifecycle(
        step_up_required=True,
        step_up_reference="stepup_1",
        step_up_state="revoked",
        owner_id="owner_1",
        step_up_owner_id="owner_1",
        session_id="session_1",
        step_up_session_id="session_1",
        room_id="ob_room_owner_console",
        step_up_room_id="ob_room_owner_console",
    )

    assert result["allowed"] is False
    assert result["reason_code"] == "ob_step_up_not_valid"
