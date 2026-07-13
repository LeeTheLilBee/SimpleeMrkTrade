"""
SEARCHABLE LABEL: TOWER_TEST_PACK_2307
"""

from tower.tower_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_v2307 import (
    build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview,
    build_pack_2307_status_bridge,
    prepare_pack_2308_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_handoff_contract,
)


def test_pack_2307_ready():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview()

    assert payload["pack"] == "2307"
    assert payload["pack_number"] == 2307
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/tower-beta-incident-response-owner-decision-execution-verification-index-post-closeout-index-post-closeout-index-post-verification-index-owner-readiness-review-note-version-v2307.json"
    assert payload["source_pack"] == "2306"
    assert payload["current_packs"] == "2270-2320"
    assert payload["save_block"] == "2270-2320"
    assert payload["next_pack"] == "2308"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["recursion_safe"] is True
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload["safe_to_continue_to_pack_2308"] is True


def test_pack_2307_safety():
    payload = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview()
    summary = payload["tower_pack_2307_summary"]

    assert summary["row_count"] >= 36
    assert summary["check_count"] >= 15
    assert summary["preview_item_count"] >= 15
    assert summary["blocked_real_action_count"] >= 21
    assert summary["all_rows_no_writes"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["tower_pack_2307_ready"] is True

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


def test_pack_2307_bridge_handoff_copy_safety():
    bridge = build_pack_2307_status_bridge()

    assert bridge["pack"] == "2307"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["tower_pack_2307_ready"] is True
    assert bridge["safe_to_continue_to_pack_2308"] is True

    handoff = prepare_pack_2308_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_handoff_contract()

    assert handoff["ready"] is True
    assert handoff["source_pack"] == "2307"
    assert handoff["next_pack"] == "2308"
    assert handoff["preview_only"] is True
    assert handoff["contract_only"] is True
    assert handoff["writes_state"] is False

    first = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview()
    second = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated"

    third = build_tower_beta_incident_response_owner_decision_execution_verification_index_post_closeout_index_post_closeout_index_post_verification_index_owner_readiness_review_note_version_preview()
    assert third["status"] == "ready"
