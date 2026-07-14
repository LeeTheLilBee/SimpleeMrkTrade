from tower.tower_ir_cert_p2408 import (
    run_six_room_failure_rehearsal,
)


def test_pack_2408_failure_injection():
    result = run_six_room_failure_rehearsal()

    assert result["status"] == "passed"
    assert result["room_count"] == 6
    assert result["all_failures_detected"] is True
    assert result["all_sessions_locked_back"] is True
    assert result["all_default_deny_restored"] is True
    assert result["all_new_handoffs_required"] is True

    for item in result["results"]:
        assert item["status"] == "passed"
        assert item["recovery_receipt"][
            "ob_access_state"
        ] == "locked_back"
