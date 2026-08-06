from tower.tower_owner_console_v1 import (
    OWNER_CONSOLE_JSON_ROUTE,
    OWNER_CONSOLE_ROUTE,
    build_owner_console_cert,
    build_owner_console_payload,
    owner_console_contract,
    render_owner_console,
)


def test_owner_console_contract_keeps_owner_controls_in_tower():
    contract = owner_console_contract()

    assert contract["contract"] == "owner_console_v1"
    assert contract["route"] == OWNER_CONSOLE_ROUTE
    assert contract["json_route"] == OWNER_CONSOLE_JSON_ROUTE
    assert contract[
        "owner_controls_centralized_in_tower"
    ] is True
    assert contract[
        "ordinary_app_pages_keep_global_owner_controls_out"
    ] is True
    assert contract["approval_queue_surface"] is True
    assert contract["dangerous_action_review_cards"] is True
    assert contract["step_up_freshness_status_panel"] is True
    assert contract["app_permission_overview"] is True
    assert contract["security_session_summary"] is True
    assert contract[
        "deployment_activation_hold_panel"
    ] is True
    assert contract[
        "owner_decision_evidence_drawers"
    ] is True
    assert contract["evidence_hidden_by_default"] is True
    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["production_deployment"] is False
    assert contract["manual_live_authorized"] is False
    assert contract["live_auto_authorized"] is False
    assert contract["direct_vault_write"] is False


def test_owner_console_payload_has_owner_decision_surfaces():
    payload = build_owner_console_payload(
        owner_session={
            "authenticated": True,
            "role": "owner",
            "owner_id": "owner_solice",
        },
        step_up_active=True,
    )

    assert payload["surface"] == "owner_console_v1"
    assert payload["owner_authenticated"] is True
    assert payload["owner_id_present"] is True
    assert payload["role"] == "owner"
    assert payload["step_up_active"] is True
    assert len(payload["approval_queue"]) >= 3
    assert len(payload["dangerous_action_reviews"]) >= 4
    assert len(payload["app_permission_overview"]) >= 5
    assert payload[
        "security_session_summary"
    ]["anonymous_denied"] is True
    assert payload[
        "deployment_hold_panel"
    ]["staging_ready"] is False
    assert payload[
        "deployment_hold_panel"
    ]["production_deployment_authorized"] is False
    assert payload["payload_hash"]


def test_owner_console_html_is_owner_desk_not_evidence_wall():
    payload = build_owner_console_payload(
        owner_session={
            "authenticated": True,
            "role": "owner",
            "owner_id": "owner_solice",
        },
        step_up_active=False,
    )

    html = render_owner_console(payload)

    assert "Tower Owner Console" in html
    assert "Owner Desk" in html
    assert "What needs my owner decision?" in html
    assert "Approval Queue" in html
    assert "Dangerous Action Review" in html
    assert "Step-up & Session" in html
    assert "Deployment Hold" in html
    assert "App Permission Overview" in html
    assert "Owner Decision Evidence Drawers" in html
    assert "<details" in html
    assert "Broker submission" in html
    assert "Capital movement" in html
    assert "Production deployment" in html
    assert "Direct Vault write" in html


def test_owner_console_cert_pack_2532_safe_checkpoint():
    payload = build_owner_console_cert(2532)

    assert payload["pack"] == "2532"
    assert payload["pack_name"] == "Owner Console Checkpoint"
    assert payload["tower_owner_console_v1"] is True
    assert payload["owner_console_checkpoint_ready"] is True
    assert payload["owner_controls_centralized_in_tower"] is True
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["production_deployment"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False
    assert payload["direct_vault_write"] is False
    assert payload["destructive_action_unlocked"] is False
