from tower.tower_beta_incident_response_owner_command_index_v1911 import (
    build_tower_beta_incident_response_owner_command_index_preview,
    build_pack_1911_status_bridge,
    prepare_pack_1912_tower_beta_incident_response_owner_command_index,
)


def test_pack_1911_ready():
    payload = (
        build_tower_beta_incident_response_owner_command_index_preview()
    )

    assert payload["pack"] == "1911"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "1910"
    assert payload["next_pack"] == "1912"
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1912"] is True


def test_pack_1911_locks():
    payload = (
        build_tower_beta_incident_response_owner_command_index_preview()
    )
    summary = payload["tower_pack_1911_summary"]

    assert summary["row_count"] >= 155
    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True
    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False
    assert summary["vault_answers_tower_only"] is True

    for key in [
        "real_owner_incident_command_enabled",
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


def test_pack_1911_bridge_prep_copy():
    bridge = build_pack_1911_status_bridge()
    prep = (
        prepare_pack_1912_tower_beta_incident_response_owner_command_index()
    )

    assert bridge["safe_to_continue_to_pack_1912"] is True
    assert prep["ready"] is True
    assert prep["next_pack"] == "1912"

    first = (
        build_tower_beta_incident_response_owner_command_index_preview()
    )
    second = (
        build_tower_beta_incident_response_owner_command_index_preview()
    )

    assert first == second
    assert first is not second
