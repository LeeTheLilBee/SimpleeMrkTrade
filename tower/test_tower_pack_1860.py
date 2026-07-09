"""
SEARCHABLE LABEL:
TOWER_PACK_1860_INCIDENT_RESPONSE_OPERATIONS_TESTS
"""

from tower.tower_beta_incident_response_operations_index_v1860 import (
    build_tower_beta_incident_response_operations_index_preview,
    build_pack_1860_status_bridge,
    prepare_pack_1861_tower_beta_incident_response_operations_index,
)


def test_pack_1860_ready():
    payload = (
        build_tower_beta_incident_response_operations_index_preview()
    )

    assert payload["pack"] == "1860"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["source_pack"] == "1859"
    assert payload["next_pack"] == "1861"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_1861"] is True


def test_pack_1860_locks():
    payload = (
        build_tower_beta_incident_response_operations_index_preview()
    )
    summary = payload["tower_pack_1860_summary"]

    assert summary["row_count"] >= 175
    assert summary["operations_category_count"] >= 37
    assert summary["operations_item_count"] >= 70
    assert summary["blocked_real_action_count"] >= 70
    assert summary["tower_pack_1860_ready"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True
    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False
    assert summary["vault_answers_tower_only"] is True

    assert summary[
        "real_incident_declaration_enabled"
    ] is False
    assert summary["real_incident_command_enabled"] is False
    assert summary[
        "real_incident_owner_assignment_enabled"
    ] is False
    assert summary["real_containment_enabled"] is False
    assert summary[
        "real_emergency_lockback_enabled"
    ] is False
    assert summary["real_revocation_enabled"] is False
    assert summary[
        "real_recovery_execution_enabled"
    ] is False
    assert summary[
        "real_rebuild_execution_enabled"
    ] is False
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


def test_pack_1860_bridge_prep_copy():
    bridge = build_pack_1860_status_bridge()
    prep = (
        prepare_pack_1861_tower_beta_incident_response_operations_index()
    )

    assert bridge["pack"] == "1860"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["safe_to_continue_to_pack_1861"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1861"
    assert prep["source_pack"] == "1860"

    first = (
        build_tower_beta_incident_response_operations_index_preview()
    )
    second = (
        build_tower_beta_incident_response_operations_index_preview()
    )

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = (
        build_tower_beta_incident_response_operations_index_preview()
    )
    assert third["status"] == "ready"
