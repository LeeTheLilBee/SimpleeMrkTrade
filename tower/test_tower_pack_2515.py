from tower.tower_ir_cert_p2515 import (
    build_ir_cert_p2515_preview,
)


def test_pack_2515_tower_access_home_ui_v2_contract():
    payload = build_ir_cert_p2515_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Simplee App Launch Cards'
    assert payload["simplee_app_launch_cards_ready"] is True
    assert payload["tower_access_home_ui_v2"] is True
    assert payload["simplee_front_door"] is True
    assert payload["black_glass_theme"] is True
    assert payload["deep_violet_theme"] is True
    assert payload["gold_owner_accents"] is True
    assert payload["blue_minimized"] is True
    assert payload["owner_session_status"] is True
    assert payload["app_launch_cards"] is True
    assert payload["observatory_launch_door"] is True
    assert payload["ob_return_session_continuity"] is True
    assert payload["return_receipt_status_panel"] is True
    assert payload["owner_actions_panel"] is True
    assert payload["quick_launch_panel"] is True
    assert payload["hidden_evidence_drawers"] is True
    assert payload["proof_page_main_experience"] is False
    assert payload["list_heavy_main_surface"] is False
    assert payload["credentials_committed"] is False
    assert payload[
        "test_session_injection_required"
    ] is False
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["direct_vault_write"] is False
    assert payload["public_links"] is False
    assert payload[
        "safe_to_continue_to_pack_2516"
    ] is True
