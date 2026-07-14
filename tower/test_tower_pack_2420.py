from tower.tower_ir_cert_p2420 import (
    build_certification_closeout,
    build_ir_cert_p2420_preview,
)


def test_pack_2420_certification_closeout():
    closeout = build_certification_closeout()

    assert closeout["ready"] is True
    assert closeout["recommendation"] == (
        "GO_TOWER_OB_PROTECTED_LAUNCH_PREVIEW_CERTIFIED"
    )
    assert all(closeout["checks"].values())
    assert closeout["production_scope_certified"] is False
    assert closeout["manual_live_scope_certified"] is False
    assert closeout["live_auto_scope_certified"] is False


def test_pack_2420_next_handoff():
    payload = build_ir_cert_p2420_preview()

    assert payload[
        "protected_launch_preview_certified"
    ] is True

    assert payload["production_scope_certified"] is False
    assert payload["safe_to_continue_to_pack_2421"] is True
