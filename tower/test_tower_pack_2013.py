from tower.tower_beta_incident_response_owner_decision_execution_readiness_index_v2013 import (
    build_tower_beta_incident_response_owner_decision_execution_readiness_index_preview,
    build_pack_2013_status_bridge,
    prepare_pack_2014_tower_beta_incident_response_owner_decision_execution_readiness_index,
)


def test_pack_2013_ready():
    payload = (
        build_tower_beta_incident_response_owner_decision_execution_readiness_index_preview()
    )

    assert payload["pack"] == "2013"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "2012"
    assert payload["next_pack"] == "2014"
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_2014"] is True


def test_pack_2013_locks():
    payload = (
        build_tower_beta_incident_response_owner_decision_execution_readiness_index_preview()
    )

    summary = payload["tower_pack_2013_summary"]

    assert summary["row_count"] >= 160

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
        "pivot_to_initial_setup",
        "pivot_to_access_home",
        "pivot_to_waitlist",
        "pivot_to_admin_dashboard",
    ]:
        assert summary[key] is False


def test_pack_2013_bridge_prep_copy():
    bridge = build_pack_2013_status_bridge()

    prep = (
        prepare_pack_2014_tower_beta_incident_response_owner_decision_execution_readiness_index()
    )

    assert bridge["safe_to_continue_to_pack_2014"] is True
    assert prep["ready"] is True
    assert prep["next_pack"] == "2014"

    first = (
        build_tower_beta_incident_response_owner_decision_execution_readiness_index_preview()
    )

    second = (
        build_tower_beta_incident_response_owner_decision_execution_readiness_index_preview()
    )

    assert first == second
    assert first is not second
