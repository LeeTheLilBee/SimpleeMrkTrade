"""
SEARCHABLE LABEL:
TOWER_PACK_1826_INCIDENT_RESPONSE_RECOVERY_TESTS
"""

import importlib


def test_pack_1826_ready():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_recovery_readiness_route_review_note_version_v1826"
    )

    payload = mod.build_tower_beta_incident_response_recovery_readiness_route_review_note_version_preview()

    assert payload["pack"] == "1826"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-incident-response-recovery-readiness-route-review-note-version-v1826.json"
    assert payload["source_pack"] == "1825"
    assert payload["current_packs"] == "1810-1859"
    assert payload["save_block"] == "1809-1859"
    assert payload["next_pack"] == "1827"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True

    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["safe_to_continue_to_pack_1827"] is True


def test_pack_1826_locks():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_recovery_readiness_route_review_note_version_v1826"
    )

    payload = mod.build_tower_beta_incident_response_recovery_readiness_route_review_note_version_preview()
    summary = payload["tower_beta_incident_response_recovery_readiness_route_review_note_version_summary"]

    assert summary["source_ready"] is True
    assert summary["row_count"] >= 165
    assert summary["incident_category_count"] >= 36
    assert summary["incident_item_count"] >= 60
    assert summary["blocked_real_action_count"] >= 65
    assert summary["tower_beta_incident_response_recovery_readiness_route_review_note_version_ready"] is True

    assert summary[
        "tower_is_only_vault_protocol_authority"
    ] is True
    assert summary[
        "teller_to_vault_direct_calls_allowed"
    ] is False
    assert summary["vault_answers_tower_only"] is True

    assert summary["real_incident_command_enabled"] is False
    assert summary["real_containment_enabled"] is False
    assert summary[
        "real_emergency_lockback_enabled"
    ] is False
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
    assert summary["save_push_performed"] is False


def test_pack_1826_bridge_prep_copy():
    mod = importlib.import_module(
        "tower.tower_tower_beta_incident_response_recovery_readiness_route_review_note_version_v1826"
    )

    bridge = mod.build_pack_1826_status_bridge()
    prep = mod.prepare_pack_1827_tower_beta_incident_response_recovery_readiness_route_review_handoff_contract()

    assert bridge["pack"] == "1826"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_beta_incident_response_recovery_readiness_route_review_note_version_ready"] is True
    assert bridge["safe_to_continue_to_pack_1827"] is True

    assert prep["ready"] is True
    assert prep["next_pack"] == "1827"
    assert prep["source_pack"] == "1826"

    first = mod.build_tower_beta_incident_response_recovery_readiness_route_review_note_version_preview()
    second = mod.build_tower_beta_incident_response_recovery_readiness_route_review_note_version_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = mod.build_tower_beta_incident_response_recovery_readiness_route_review_note_version_preview()
    assert third["status"] == "ready"
