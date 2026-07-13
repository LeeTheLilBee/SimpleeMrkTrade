"""
SEARCHABLE LABEL: TOWER_TEST_PACK_2301
"""

from tower.tower_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_v2301 import (
    build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview,
    build_pack_2301_status_bridge,
    prepare_pack_2302_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_registry_contract,
)


def test_pack_2301_ready():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview()

    assert payload["pack"] == "2301"
    assert payload["pack_number"] == 2301
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-incident-response-owner-decision-execution-verification-index-post-closeout-index-post-closeout-index-post-verification-index-owner-readiness-review-index-v2301.json"
    assert payload["source_pack"] == "2300"
    assert payload["current_packs"] == "2270-2320"
    assert payload["save_block"] == "2270-2320"
    assert payload["next_pack"] == "2302"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_2302"] is True


def test_pack_2301_safety():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview()
    summary = payload["tower_pack_2301_summary"]

    assert summary["row_count"] >= 36
    assert summary["check_count"] >= 15
    assert summary["preview_item_count"] >= 15
    assert summary["blocked_real_action_count"] >= 21
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_2301_ready"] is True

    assert summary[
        "real_incident_response_execution_enabled"
    ] is False

    assert summary[
        "real_owner_decision_apply_enabled"
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


def test_pack_2301_bridge_handoff_copy_safety():
    bridge = build_pack_2301_status_bridge()

    assert bridge["pack"] == "2301"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_2301_ready"] is True
    assert bridge["safe_to_continue_to_pack_2302"] is True

    handoff = prepare_pack_2302_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_registry_contract()

    assert handoff["ready"] is True
    assert handoff["source_pack"] == "2301"
    assert handoff["next_pack"] == "2302"
    assert handoff["preview_only"] is True
    assert handoff["contract_only"] is True
    assert handoff["writes_state"] is False

    first = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview()
    second = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_index_preview()
    assert third["status"] == "ready"
