"""
SEARCHABLE LABEL: TOWER_PACK_265_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUITY_BATCH_CLOSE_READINESS_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_265_continuity_batch_close_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    assert payload["pack"] == "265"
    assert payload["pack_number"] == 265
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Continuity Batch Close Readiness Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-continuity-batch-close-readiness-v265.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Index Preview layer"

    assert payload["source_closed_batch"] == "251-260"
    assert payload["save_batch"] == "261-265"
    assert payload["save_after_pack"] == 265
    assert payload["next_batch"] == "266-270"
    assert payload["next_pack"] == "266"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    for pack in ["261", "262", "263", "264"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    assert payload["safe_to_push_packs_261_to_265"] is True
    assert payload["safe_to_continue_to_pack_266"] is True
    assert payload["prepare_pack_266_receipt_chain_saved_view_owner_review_governance_handoff_index"]["pack"] == "266"


def test_pack_265_continuity_batch_close_summary_ready_to_push():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    summary = payload["governance_continuity_batch_close_summary"]

    assert summary["source_closed_batch"] == "251-260"
    assert summary["save_batch"] == "261-265"
    assert summary["save_after_pack"] == 265
    assert summary["next_batch"] == "266-270"
    assert summary["next_pack"] == "266"
    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 16
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_preview_count"] >= 3
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["continuity_batch_ready_to_push"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_continuity_write_enabled"] is False
    assert summary["real_continuity_index_write_enabled"] is False
    assert summary["real_continuity_detail_write_enabled"] is False
    assert summary["real_continuity_note_write_enabled"] is False
    assert summary["real_continuity_note_version_write_enabled"] is False
    assert summary["real_continuity_note_version_restore_enabled"] is False
    assert summary["real_continuity_note_version_apply_enabled"] is False
    assert summary["real_continuity_state_write_enabled"] is False
    assert summary["real_continuity_handoff_write_enabled"] is False
    assert summary["real_escalation_write_enabled"] is False
    assert summary["real_escalation_execute_enabled"] is False
    assert summary["real_continuous_assurance_write_enabled"] is False
    assert summary["real_continuous_assurance_check_execute_enabled"] is False
    assert summary["real_governance_decision_write_enabled"] is False
    assert summary["real_governance_decision_apply_enabled"] is False
    assert summary["real_governance_decision_override_enabled"] is False
    assert summary["real_policy_change_enabled"] is False
    assert summary["real_owner_review_execution_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_265_cards_checks_manifest_and_transitions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    cards = payload["governance_continuity_batch_pack_cards"]
    checks = payload["governance_continuity_batch_close_checks"]
    manifest = payload["governance_continuity_save_manifest_preview"]
    transitions = payload["governance_continuity_transition_previews"]

    packs = {card["pack"] for card in cards}
    assert {"261", "262", "263", "264", "265"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    assert all(check["passed"] is True for check in checks)
    assert all(check["writes_state"] is False for check in checks)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_owner_review_governance_continuity_index_v261.py",
        "tower/test_tower_pack_261.py",
        "tower/receipt_chain_saved_view_owner_review_governance_continuity_detail_drawer_v262.py",
        "tower/test_tower_pack_262.py",
        "tower/receipt_chain_saved_view_owner_review_governance_continuity_note_draft_v263.py",
        "tower/test_tower_pack_263.py",
        "tower/receipt_chain_saved_view_owner_review_governance_continuity_note_version_v264.py",
        "tower/test_tower_pack_264.py",
        "tower/receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265.py",
        "tower/test_tower_pack_265.py",
        "web/app.py",
    }
    assert expected_paths.issubset(manifest_paths)
    assert all(row["include_in_commit"] is True for row in manifest)

    assert transitions
    assert all(row["transition_mode"] == "preview_only" for row in transitions)
    assert all(row["writes_state"] is False for row in transitions)
    assert all(row["safe_to_continue"] is True for row in transitions)


def test_pack_265_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_continuity_write"] is True
    assert safety["no_real_continuity_index_write"] is True
    assert safety["no_real_continuity_detail_write"] is True
    assert safety["no_real_continuity_note_write"] is True
    assert safety["no_real_continuity_note_version_write"] is True
    assert safety["no_real_continuity_note_version_restore"] is True
    assert safety["no_real_continuity_note_version_apply"] is True
    assert safety["no_real_continuity_state_write"] is True
    assert safety["no_real_continuity_handoff_write"] is True
    assert safety["no_real_escalation_write"] is True
    assert safety["no_real_escalation_execute"] is True
    assert safety["no_real_continuous_assurance_write"] is True
    assert safety["no_real_continuous_assurance_check_execute"] is True
    assert safety["no_real_governance_decision_write"] is True
    assert safety["no_real_governance_decision_apply"] is True
    assert safety["no_real_governance_decision_override"] is True
    assert safety["no_real_policy_change_write"] is True
    assert safety["no_real_owner_review_execute"] is True
    assert safety["no_real_saved_view_write"] is True
    assert safety["no_archive_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_265_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_preview()

    assert third["status"] == "ready"


def test_pack_265_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_batch_close_readiness_v265")

    bridge = mod.build_pack_265_status_bridge()
    assert bridge["pack"] == "265"
    assert bridge["pack_number"] == 265
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Index Preview layer"
    assert bridge["source_closed_batch"] == "251-260"
    assert bridge["save_batch"] == "261-265"
    assert bridge["save_after_pack"] == 265
    assert bridge["next_batch"] == "266-270"
    assert bridge["next_pack"] == "266"
    assert bridge["pack_card_count"] >= 5
    assert bridge["close_check_count"] >= 16
    assert bridge["save_manifest_preview_count"] >= 11
    assert bridge["continuity_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_261_to_265"] is True
    assert bridge["safe_to_continue_to_pack_266"] is True

    prep = mod.prepare_pack_266_receipt_chain_saved_view_owner_review_governance_handoff_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "266"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Index Preview layer"
    assert prep["source_closed_batch"] == "251-260"
    assert prep["closed_batch"] == "261-265"
    assert prep["next_batch"] == "266-270"
    assert prep["save_after_pack"] == 270
    assert prep["safe_to_continue"] is True


def test_pack_265_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-continuity-batch-close-readiness-v265.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-continuity-batch-close-readiness-v265.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "265"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Index Preview layer"
        assert data["source_closed_batch"] == "251-260"
        assert data["save_batch"] == "261-265"
        assert data["next_batch"] == "266-270"
        assert data["safe_to_push_packs_261_to_265"] is True
        assert data["safe_to_continue_to_pack_266"] is True
