import importlib


def test_pack_1982_ready():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_v1982"
    )

    payload = mod.build_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_preview()

    assert payload["pack"] == "1982"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "1981"
    assert payload["current_packs"] == "1963-2012"
    assert payload["save_block"] == "1962-2012"
    assert payload["next_pack"] == "1983"
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1983"] is True


def test_pack_1982_locks():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_v1982"
    )

    payload = mod.build_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_preview()
    summary = payload["tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 160
    assert summary["tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_ready"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True

    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False

    assert summary["vault_answers_tower_only"] is True

    for key in [
        "real_owner_decision_enabled",
        "real_owner_decision_apply_enabled",
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


def test_pack_1982_bridge_prep_copy():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_v1982"
    )

    bridge = mod.build_pack_1982_status_bridge()
    prep = mod.prepare_pack_1983_tower_beta_incident_response_owner_decision_blocker_review_index()

    assert bridge["status"] == "ready"
    assert bridge["safe_to_continue_to_pack_1983"] is True
    assert prep["ready"] is True
    assert prep["next_pack"] == "1983"

    first = mod.build_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_preview()
    second = mod.build_tower_beta_incident_response_owner_decision_route_review_batch_close_readiness_preview()

    assert first == second
    assert first is not second
