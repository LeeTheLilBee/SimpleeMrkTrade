from tower.tower_ir_cert_p2409 import (
    build_owner_assurance_summary,
)


def test_pack_2409_owner_assurance_summary():
    summary = build_owner_assurance_summary()

    assert summary["ready"] is True
    assert summary["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_ASSURANCE_READY"
    )
    assert summary["room_count"] == 6
    assert summary["default_deny_restored"] is True

    for scenario in summary["scenario_summaries"]:
        assert scenario["status"] == "passed"
        assert scenario["final_access_state"] == (
            "locked_back"
        )
