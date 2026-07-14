from tower.tower_ir_cert_p2399 import (
    run_six_room_enforcement_rehearsal,
)


def test_pack_2399_six_room_enforcement():
    result = run_six_room_enforcement_rehearsal()

    assert result["status"] == "passed"
    assert result["room_count"] == 6
    assert result["all_rooms_passed"] is True
    assert result["replay_blocking_passed"] is True
    assert result["receipt_chain_passed"] is True

    for room in result["rooms"]:
        assert room["enforcement"]["allowed"] is True
        assert room["consume_transition"]["next_state"] == (
            "consumed"
        )
        assert room["replay_attempt"]["allowed"] is False
        assert room["receipt_chain"]["verified"] is True
