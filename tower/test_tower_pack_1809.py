"""
SEARCHABLE LABEL:
TOWER_PACK_1809_INCIDENT_RESPONSE_RECOVERY_READINESS_TESTS
"""

from tower.tower_beta_incident_response_recovery_readiness_index_v1809 import (
    build_tower_beta_incident_response_recovery_readiness_index_preview,
    build_pack_1809_status_bridge,
    prepare_pack_1810_tower_beta_incident_response_recovery_readiness_index,
)


def test_pack_1809_ready():
    payload = (
        build_tower_beta_incident_response_recovery_readiness_index_preview()
    )

    assert payload["pack"] == "1809"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "1808"
    assert payload["next_pack"] == "1810"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1810"] is True


def test_pack_1809_locks():
    payload = (
        build_tower_beta_incident_response_recovery_readiness_index_preview()
    )
    summary = payload["tower_pack_1809_summary"]

    assert summary["row_count"] >= 165
    assert summary["incident_category_count"] >= 36
    assert summary["incident_item_count"] >= 60
    assert summary["blocked_real_action_count"] >= 65
    assert summary["tower_pack_1809_ready"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True
    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False
    assert summary["vault_answers_tower_only"] is True

    assert summary["real_incident_command_enabled"] is False
    assert summary["real_containment_enabled"] is False
    assert summary["real_emergency_lockback_enabled"] is False
    assert summary["real_recovery_execution_enabled"] is False
    assert summary["real_rebuild_execution_enabled"] is False
    assert summary["real_restore_enabled"] is False
    assert summary["real_delete_enabled"] is False
    assert summary["real_purge_enabled"] is False
    assert summary[
        "real_quarantine_release_enabled"
    ] is False
    assert summary[
        "real_physical_object_move_enabled"
    ] is False
    assert summary["real_vault_request_enabled"] is False
    assert summary["real_account_mutation_enabled"] is False
    assert summary["real_user_mutation_enabled"] is False
    assert summary["real_access_mutation_enabled"] is False

    assert summary["pivot_to_initial_setup"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_admin_dashboard"] is False


def test_pack_1809_bridge_prep_copy():
    bridge = build_pack_1809_status_bridge()
    prep = (
        prepare_pack_1810_tower_beta_incident_response_recovery_readiness_index()
    )

    assert bridge["pack"] == "1809"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["safe_to_continue_to_pack_1810"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1810"
    assert prep["source_pack"] == "1809"

    first = (
        build_tower_beta_incident_response_recovery_readiness_index_preview()
    )
    second = (
        build_tower_beta_incident_response_recovery_readiness_index_preview()
    )

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = (
        build_tower_beta_incident_response_recovery_readiness_index_preview()
    )
    assert third["status"] == "ready"
