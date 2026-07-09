import importlib


def test_pack_2030_ready():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_v2030"
    )

    payload = mod.build_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_preview()

    assert payload["pack"] == "2030"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "2029"
    assert payload["current_packs"] == "2014-2063"
    assert payload["save_block"] == "2013-2063"
    assert payload["next_pack"] == "2031"
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_2031"] is True


def test_pack_2030_locks():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_v2030"
    )

    payload = mod.build_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_preview()
    summary = payload["tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 160
    assert summary["tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_ready"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True

    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False

    assert summary["vault_answers_tower_only"] is True

    for key in [
        "real_owner_decision_execution_enabled",
        "real_execution_gate_open_enabled",
        "real_incident_declaration_enabled",
        "real_containment_enabled",
        "real_lockback_enabled",
        "real_revocation_enabled",
        "real_recovery_enabled",
        "real_restore_enabled",
        "real_vault_request_enabled",
        "real_account_mutation_enabled",
        "real_user_mutation_enabled",
        "real_access_mutation_enabled",
        "raw_file_bytes_json_enabled",
        "raw_path_enabled",
        "raw_file_url_enabled",
        "raw_download_token_enabled",
        "public_vault_link_enabled",
        "shared_folder_browsing_enabled",
        "pivot_to_initial_setup",
        "pivot_to_access_home",
        "pivot_to_waitlist",
        "pivot_to_admin_dashboard",
    ]:
        assert summary[key] is False


def test_pack_2030_bridge_prep_copy():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_v2030"
    )

    bridge = mod.build_pack_2030_status_bridge()
    prep = mod.prepare_pack_2031_tower_beta_incident_response_owner_decision_execution_readiness_route_review_handoff_contract()

    assert bridge["status"] == "ready"
    assert bridge["safe_to_continue_to_pack_2031"] is True
    assert prep["ready"] is True
    assert prep["next_pack"] == "2031"

    first = mod.build_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_preview()
    second = mod.build_tower_beta_incident_response_owner_decision_execution_readiness_route_review_note_version_preview()

    assert first == second
    assert first is not second
