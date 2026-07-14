from tower.tower_ir_cert_p2422 import (
    build_ir_cert_p2422_preview,
    build_observatory_corridor_closeout,
    prepare_pack_2423_ob_post_closeout,
    verify_corridor_closeout,
)


def test_pack_2422_corridor_closeout():
    closeout = (
        build_observatory_corridor_closeout()
    )

    assert closeout["ready"] is True

    assert closeout["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_LAUNCH_CORRIDOR_CLOSED"
    )

    assert closeout["pack_range"] == "2372-2422"
    assert closeout["official_room_count"] == 6

    assert len(
        closeout["corridor_sections"]
    ) == 6

    assert all(
        section["passed"]
        for section in closeout[
            "corridor_sections"
        ]
    )

    assert all(closeout["checks"].values())

    assert closeout[
        "production_scope_certified"
    ] is False

    assert closeout[
        "manual_live_scope_certified"
    ] is False

    assert closeout[
        "live_auto_scope_certified"
    ] is False


def test_pack_2422_closeout_integrity():
    closeout = (
        build_observatory_corridor_closeout()
    )

    verification = verify_corridor_closeout(
        closeout
    )

    assert verification["valid"] is True

    assert verification["reason_code"] == (
        "tower_ob_corridor_closeout_verified"
    )


def test_pack_2422_final_checkpoint():
    payload = build_ir_cert_p2422_preview()

    assert payload["corridor_closed"] is True

    assert payload[
        "safe_to_continue_to_pack_2423"
    ] is True

    assert payload["preview_only"] is True
    assert payload["contract_only"] is True


def test_pack_2422_pack_2423_handoff():
    handoff = (
        prepare_pack_2423_ob_post_closeout()
    )

    assert handoff["ready"] is True
    assert handoff["source_pack"] == "2422"
    assert handoff["next_pack"] == "2423"

    assert handoff[
        "production_authorization_granted"
    ] is False

    assert handoff[
        "manual_live_authorization_granted"
    ] is False

    assert handoff[
        "live_auto_authorization_granted"
    ] is False
