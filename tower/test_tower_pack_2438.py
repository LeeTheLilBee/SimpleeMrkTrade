from tower.tower_ir_cert_p2438 import (
    build_ir_cert_p2438_preview,
)


def test_pack_2438_real_surface_contract():
    payload = build_ir_cert_p2438_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["symbol_page_real_surface_ready"] is True
    assert payload["real_room_count"] == 6
    assert payload["response_overlay_integration"] is True
    assert payload["existing_room_guard_preserved"] is True
    assert payload["existing_templates_preserved"] is True
    assert payload["owner_only"] is True
    assert payload["tower_clearance_value"] == (
        "ob_owner_command"
    )
    assert payload["tower_clearance_rank"] == 900
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["direct_vault_upload"] is False
    assert payload["preview_only"] is True
    assert payload["writes_state"] is False
    assert payload[
        "safe_to_continue_to_pack_2439"
    ] is True

    assert payload["target_room"][
        "room_id"
    ] == 'ob_room_symbol_page'
