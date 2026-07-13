"""
SEARCHABLE LABEL: TOWER_TEST_PACK_2138
"""

from __future__ import annotations

from tower.tower_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_v2138 import (
    build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview,
    build_pack_2138_status_bridge,
    prepare_pack_2139_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_registry_contract,
)


def test_pack_2138_ready():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview()

    assert payload["pack"] == "2138"
    assert payload["pack_number"] == 2138
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-incident-response-owner-decision-execution-verification-index-blocker-review-index-v2138.json"
    assert payload["source_pack"] == "2137"
    assert payload["current_packs"] == "2117-2167"
    assert payload["save_block"] == "2117-2167"
    assert payload["next_pack"] == "2139"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_2139"] is True


def test_pack_2138_safety():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview()
    summary = payload["tower_pack_2138_summary"]

    assert summary["row_count"] >= 36
    assert summary["check_count"] >= 15
    assert summary["preview_item_count"] >= 15
    assert summary["blocked_real_action_count"] >= 21
    assert summary["all_rows_preview_only"] is True
    assert summary["all_rows_contract_only"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_2138_ready"] is True

    assert summary[
        "real_incident_response_execution_enabled"
    ] is False

    assert summary[
        "real_owner_decision_apply_enabled"
    ] is False

    assert summary[
        "real_owner_approval_apply_enabled"
    ] is False

    assert summary[
        "real_account_mutation_enabled"
    ] is False

    assert summary[
        "real_access_mutation_enabled"
    ] is False

    assert summary[
        "real_route_mutation_enabled"
    ] is False

    assert summary[
        "real_session_mutation_enabled"
    ] is False

    assert summary[
        "real_clouds_write_enabled"
    ] is False

    assert summary[
        "real_vault_write_enabled"
    ] is False

    assert summary["external_share_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["pivot_to_access_home"] is False
    assert summary["pivot_to_admin_dashboard"] is False
    assert summary["pivot_to_waitlist"] is False
    assert summary["pivot_to_initial_setup"] is False
    assert summary["save_push_performed"] is False


def test_pack_2138_bridge_handoff_copy_safety():
    bridge = build_pack_2138_status_bridge()

    assert bridge["pack"] == "2138"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_2138_ready"] is True
    assert bridge["safe_to_continue_to_pack_2139"] is True

    handoff = prepare_pack_2139_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_registry_contract()

    assert handoff["ready"] is True
    assert handoff["source_pack"] == "2138"
    assert handoff["next_pack"] == "2139"
    assert handoff["preview_only"] is True
    assert handoff["contract_only"] is True
    assert handoff["writes_state"] is False

    first = build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview()
    second = build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = build_tower_beta_incident_response_owner_decision_execution_verification_index_blocker_review_index_preview()
    assert third["status"] == "ready"
