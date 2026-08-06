from tower.tower_ir_cert_p2530 import (
    build_ir_cert_p2530_preview,
)


def test_pack_2530_tower_owner_console_v1_contract():
    payload = build_ir_cert_p2530_preview()

    assert payload["pack"] == "2530"
    assert payload["pack_name"] == 'Owner Decision Evidence Drawers'
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["tower_owner_console_v1"] is True
    assert payload["owner_desk"] is True
    assert payload[
        "owner_controls_centralized_in_tower"
    ] is True
    assert payload[
        "ordinary_app_pages_keep_global_owner_controls_out"
    ] is True
    assert payload["owner_decision_evidence_drawers_ready"] is True
    assert payload["owner_console_route_shell"] is True
    assert payload["owner_approval_queue_surface"] is True
    assert payload["dangerous_action_review_cards"] is True
    assert payload[
        "step_up_freshness_status_panel"
    ] is True
    assert payload["app_permission_overview"] is True
    assert payload["security_session_summary"] is True
    assert payload[
        "deployment_activation_hold_panel"
    ] is True
    assert payload[
        "owner_decision_evidence_drawers"
    ] is True
    assert payload["owner_console_cert_routes"] is True
    assert payload["evidence_hidden_by_default"] is True
    assert payload["black_glass_theme"] is True
    assert payload["deep_violet_theme"] is True
    assert payload["gold_owner_accents"] is True
    assert payload["credentials_committed"] is False
    assert payload["secret_values_exposed"] is False
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["production_deployment"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False
    assert payload["direct_vault_write"] is False
    assert payload["destructive_action_unlocked"] is False
    assert payload[
        "safe_to_continue_to_pack_2531"
    ] is True
    assert payload["cert_hash"]
