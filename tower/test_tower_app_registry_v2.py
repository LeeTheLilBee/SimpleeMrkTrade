from tower.tower_app_registry_v2 import (
    APP_REGISTRY_JSON_ROUTE,
    APP_REGISTRY_ROUTE,
    app_registry_contract,
    build_app_registry_cert,
    build_app_registry_payload,
    door_by_id,
    ecosystem_doors,
    render_app_registry,
)


def test_app_registry_contract_declares_tower_door_source_of_truth():
    contract = app_registry_contract()

    assert contract["contract"] == "app_registry_v2"
    assert contract["route"] == APP_REGISTRY_ROUTE
    assert contract["json_route"] == APP_REGISTRY_JSON_ROUTE
    assert contract[
        "tower_source_of_truth_for_app_doors"
    ] is True
    assert contract["ecosystem_doors_registered"] is True
    assert contract["door_card_metadata_model"] is True
    assert contract["door_status_readiness_model"] is True
    assert contract["door_permission_boundary_model"] is True
    assert contract["door_launch_route_map"] is True
    assert contract["door_owner_control_linkage"] is True
    assert contract["door_integration_readiness_view"] is True
    assert contract["door_evidence_drawers"] is True
    assert contract["visible_door_count"] == 5
    assert contract["owner_controls_route"] == "/tower/owner-console"
    assert contract["access_home_route"] == "/tower/access-home"
    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["production_deployment"] is False
    assert contract["manual_live_authorized"] is False
    assert contract["live_auto_authorized"] is False
    assert contract["direct_vault_write"] is False


def test_ecosystem_doors_register_all_five_simplee_doors():
    doors = ecosystem_doors()
    ids = {door["id"] for door in doors}

    assert ids == {
        "observatory",
        "vault",
        "teller",
        "grounds",
        "clouds",
    }

    observatory = door_by_id("observatory")
    assert observatory["launch_route"] == "/tower/launch/observatory"
    assert observatory["return_route"] == "/tower/return/observatory"
    assert observatory[
        "permission_boundary"
    ] == "owner_session_required_plus_step_up_for_launch"
    assert observatory["owner_controls_route"] == "/tower/owner-console"
    assert "no broker submission" in observatory["danger_boundary"]


def test_app_registry_payload_has_integration_readiness_and_evidence_drawers():
    payload = build_app_registry_payload(
        owner_authenticated=True,
        role="owner",
    )

    assert payload["surface"] == "app_registry_v2"
    assert payload["owner_authenticated"] is True
    assert payload["role"] == "owner"
    assert len(payload["doors"]) == 5
    assert payload[
        "integration_readiness"
    ]["tower_access_home_v2"] == "closed"
    assert payload[
        "integration_readiness"
    ]["tower_owner_console_v1"] == "closed"
    assert payload[
        "integration_readiness"
    ]["observatory_simplification"] == "pending"
    assert payload[
        "integration_readiness"
    ]["staging_ready"] is False
    assert len(payload["evidence_drawers"]) >= 3
    assert payload["payload_hash"]


def test_app_registry_html_is_door_map_not_proof_wall():
    payload = build_app_registry_payload(
        owner_authenticated=True,
        role="owner",
    )

    html = render_app_registry(payload)

    assert "Tower App Registry" in html
    assert "Ecosystem Door Registry" in html
    assert "What doors exist in Simplee?" in html
    assert "Registered Doors" in html
    assert "The Observatory" in html
    assert "Archive Vault" in html
    assert "The Teller" in html
    assert "The Grounds" in html
    assert "The Clouds" in html
    assert "Integration Readiness" in html
    assert "Registry Evidence Drawers" in html
    assert "<details" in html
    assert "/tower/owner-console" in html
    assert "/tower/access-home" in html


def test_app_registry_cert_pack_2542_safe_checkpoint():
    payload = build_app_registry_cert(2542)

    assert payload["pack"] == "2542"
    assert payload["pack_name"] == "Ecosystem Door Registry Checkpoint"
    assert payload["tower_app_registry_v2"] is True
    assert payload["ecosystem_door_registry_checkpoint_ready"] is True
    assert payload["registered_door_count"] == 5
    assert payload["observatory_registered"] is True
    assert payload["vault_registered"] is True
    assert payload["teller_registered"] is True
    assert payload["grounds_registered"] is True
    assert payload["clouds_registered"] is True
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["production_deployment"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False
    assert payload["direct_vault_write"] is False
    assert payload["destructive_action_unlocked"] is False
