from tower.tower_ir_cert_p2535 import (
    build_ir_cert_p2535_preview,
)


def test_pack_2535_tower_app_registry_v2_contract():
    payload = build_ir_cert_p2535_preview()

    assert payload["pack"] == "2535"
    assert payload["pack_name"] == 'Door Status + Readiness Model'
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["tower_app_registry_v2"] is True
    assert payload["ecosystem_door_registry"] is True
    assert payload[
        "tower_source_of_truth_for_app_doors"
    ] is True
    assert payload["door_status_readiness_model_ready"] is True
    assert payload["ecosystem_doors_registered"] is True
    assert payload["door_card_metadata_model"] is True
    assert payload["door_status_readiness_model"] is True
    assert payload["door_permission_boundary_model"] is True
    assert payload["door_launch_route_map"] is True
    assert payload["door_owner_control_linkage"] is True
    assert payload[
        "door_integration_readiness_view"
    ] is True
    assert payload["door_evidence_drawers"] is True
    assert payload["registry_cert_routes"] is True
    assert payload["registered_door_count"] == 5
    assert payload["observatory_registered"] is True
    assert payload["vault_registered"] is True
    assert payload["teller_registered"] is True
    assert payload["grounds_registered"] is True
    assert payload["clouds_registered"] is True
    assert payload["owner_controls_route"] == "/tower/owner-console"
    assert payload["access_home_route"] == "/tower/access-home"
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
        "safe_to_continue_to_pack_2536"
    ] is True
    assert payload["cert_hash"]
