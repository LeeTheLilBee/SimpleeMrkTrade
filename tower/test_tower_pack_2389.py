from tower.tower_ir_cert_p2389 import (
    run_six_room_protected_rehearsal,
)


def test_pack_2389_six_room_integration_passes():
    result = run_six_room_protected_rehearsal()

    assert result["status"] == "passed"
    assert result["room_count"] == 6
    assert result["all_rooms_passed"] is True
    assert result["default_deny_passed"] is True

    for room in result["rooms"]:
        assert room["status"] == "passed"
        assert room["launch_validation"]["allowed"] is True
        assert room["completion_intake"]["accepted"] is True
        assert room["lockback_verification"]["verified"] is True
