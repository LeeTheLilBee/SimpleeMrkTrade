from tower.tower_ir_cert_p2421 import (
    VALIDATION_CYCLES_PER_ROOM,
    build_ir_cert_p2421_preview,
    run_protected_launch_operational_validation,
)


def test_pack_2421_operational_validation_passes():
    result = (
        run_protected_launch_operational_validation()
    )

    assert result["status"] == "passed"

    assert result["recommendation"] == (
        "GO_TOWER_OB_OPERATIONAL_PREVIEW_VALIDATED"
    )

    assert result["room_count"] == 6

    assert result["cycles_per_room"] == (
        VALIDATION_CYCLES_PER_ROOM
    )

    assert result["total_session_cycles"] == (
        6 * VALIDATION_CYCLES_PER_ROOM
    )

    assert result["unique_handoff_count"] == (
        result["total_session_cycles"]
    )

    assert all(result["checks"].values())


def test_pack_2421_each_room_repeatedly_passes():
    result = (
        run_protected_launch_operational_validation()
    )

    for room in result["rooms"]:
        assert room["status"] == "passed"

        assert room["cycle_count"] == (
            VALIDATION_CYCLES_PER_ROOM
        )

        assert room["canonical_resolution"][
            "allowed"
        ] is True

        assert room["alias_resolution"][
            "allowed"
        ] is True

        assert all(
            cycle["status"] == "passed"
            for cycle in room["cycles"]
        )

        assert all(
            cycle["final_access_state"]
            == "locked_back"
            for cycle in room["cycles"]
        )

        assert room["failure_validation"][
            "status"
        ] == "passed"


def test_pack_2421_checkpoint_handoff():
    payload = build_ir_cert_p2421_preview()

    assert payload[
        "operational_preview_validated"
    ] is True

    assert payload[
        "safe_to_continue_to_pack_2422"
    ] is True

    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
