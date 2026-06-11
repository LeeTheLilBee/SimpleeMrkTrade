"""
SEARCHABLE LABEL: TOWER_PACK_261_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUITY_INDEX_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_261_continuity_index_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    assert payload["pack"] == "261"
    assert payload["pack_number"] == 261
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Continuity Index Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-continuity-index-v261.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Index Preview layer"

    assert payload["source_closed_batch"] == "251-260"
    assert payload["save_batch"] == "261-265"
    assert payload["save_after_pack"] == 265
    assert payload["next_batch"] == "261-265"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "260"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["source_safe_to_push"] is True

    assert payload["safe_to_continue_to_pack_262"] is True
    assert payload["prepare_pack_262_receipt_chain_saved_view_owner_review_governance_continuity_detail_drawer"]["pack"] == "262"


def test_pack_261_continuity_index_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    summary = payload["governance_continuity_index_summary"]

    assert summary["source_pack_card_count"] >= 10
    assert summary["continuity_card_count"] >= 10
    assert summary["handoff_marker_count"] >= 20
    assert summary["continuity_action_count"] >= 100
    assert summary["continuity_checkpoint_count"] >= 5
    assert summary["enabled_action_count"] >= 10
    assert summary["blocked_action_count"] >= 90
    assert summary["redacted_card_count"] >= 1

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_ready"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_markers_preview_only"] is True
    assert summary["all_markers_no_writes"] is True
    assert summary["all_markers_safe"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["continuity_index_ready"] is True

    assert summary["real_continuity_write_enabled"] is False
    assert summary["real_continuity_index_write_enabled"] is False
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


def test_pack_261_continuity_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    cards = payload["governance_continuity_index_cards"]
    markers = payload["governance_continuity_handoff_markers"]
    actions = payload["governance_continuity_index_actions"]
    checkpoints = payload["governance_continuity_index_checkpoints"]

    assert cards
    assert markers
    assert actions
    assert checkpoints

    lanes = {card["lane"] for card in cards}
    assert "closed_batch_integrity" in lanes
    assert "source_pack_handoff" in lanes
    assert "continuous_assurance_continuity" in lanes
    assert "escalation_continuity" in lanes
    assert "note_version_continuity" in lanes
    assert "guarded_route_continuity" in lanes
    assert "save_push_continuity" in lanes
    assert "next_batch_readiness" in lanes
    assert "mutation_boundary" in lanes
    assert "evidence_boundary" in lanes

    assert all(card["preview_only"] is True for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["writes_state"] is False for card in cards)
    assert all(card["executable"] is False for card in cards)
    assert all(card["raw_evidence_visible"] is False for card in cards)

    assert all(marker["handoff_mode"] == "preview_only" for marker in markers)
    assert all(marker["writes_state"] is False for marker in markers)
    assert all(marker["safe_to_continue"] is True for marker in markers)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 10
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 90
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_261_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_continuity_write"] is True
    assert safety["no_real_continuity_index_write"] is True
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


def test_pack_261_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_continuity_index_preview()

    assert third["status"] == "ready"


def test_pack_261_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuity_index_v261")

    bridge = mod.build_pack_261_status_bridge()
    assert bridge["pack"] == "261"
    assert bridge["pack_number"] == 261
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Index Preview layer"
    assert bridge["source_closed_batch"] == "251-260"
    assert bridge["save_batch"] == "261-265"
    assert bridge["save_after_pack"] == 265
    assert bridge["source_pack"] == "260"
    assert bridge["source_status"] == "ready"
    assert bridge["continuity_card_count"] >= 10
    assert bridge["handoff_marker_count"] >= 20
    assert bridge["continuity_action_count"] >= 100
    assert bridge["continuity_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_262"] is True

    prep = mod.prepare_pack_262_receipt_chain_saved_view_owner_review_governance_continuity_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "262"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Index Preview layer"
    assert prep["source_closed_batch"] == "251-260"
    assert prep["save_batch"] == "261-265"
    assert prep["save_after_pack"] == 265
    assert prep["safe_to_continue"] is True


def test_pack_261_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-continuity-index-v261.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-continuity-index-v261.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "261"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Index Preview layer"
        assert data["source_closed_batch"] == "251-260"
        assert data["save_batch"] == "261-265"
