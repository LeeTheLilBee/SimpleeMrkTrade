"""
SEARCHABLE LABEL: TOWER_PACK_256_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUOUS_ASSURANCE_ESCALATION_QUEUE_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_256_escalation_queue_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    assert payload["pack"] == "256"
    assert payload["pack_number"] == 256
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Continuous Assurance Escalation Queue Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-queue-v256.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Index Preview layer"

    assert payload["save_batch"] == "251-260"
    assert payload["save_after_pack"] == 260
    assert payload["next_batch"] == "251-260"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "255"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_257"] is True
    assert payload["prepare_pack_257_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer"]["pack"] == "257"


def test_pack_256_escalation_queue_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    summary = payload["governance_continuous_assurance_escalation_queue_summary"]

    assert summary["source_close_check_count"] >= 11
    assert summary["queue_item_count"] >= 8
    assert summary["queue_signal_count"] >= 32
    assert summary["queue_action_count"] >= 88
    assert summary["queue_checkpoint_count"] >= 5
    assert summary["enabled_action_count"] >= 8
    assert summary["blocked_action_count"] >= 80
    assert summary["high_priority_count"] >= 7
    assert summary["critical_priority_count"] >= 1
    assert summary["redacted_signal_count"] >= 8

    assert summary["all_items_preview_only"] is True
    assert summary["all_items_no_writes"] is True
    assert summary["all_items_non_executable"] is True
    assert summary["all_items_no_raw_evidence"] is True
    assert summary["all_signals_no_writes"] is True
    assert summary["all_signals_non_executable"] is True
    assert summary["all_signals_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["escalation_queue_ready"] is True

    assert summary["real_escalation_write_enabled"] is False
    assert summary["real_escalation_queue_write_enabled"] is False
    assert summary["real_escalation_queue_state_write_enabled"] is False
    assert summary["real_escalation_assignment_write_enabled"] is False
    assert summary["real_escalation_execute_enabled"] is False
    assert summary["real_escalation_status_write_enabled"] is False
    assert summary["real_escalation_resolution_write_enabled"] is False
    assert summary["real_continuous_assurance_write_enabled"] is False
    assert summary["real_continuous_assurance_check_execute_enabled"] is False
    assert summary["real_continuous_assurance_status_write_enabled"] is False
    assert summary["real_governance_decision_write_enabled"] is False
    assert summary["real_governance_decision_apply_enabled"] is False
    assert summary["real_governance_decision_override_enabled"] is False
    assert summary["real_policy_change_enabled"] is False
    assert summary["real_owner_review_execution_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_256_queue_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    items = payload["governance_continuous_assurance_escalation_queue_items"]
    signals = payload["governance_continuous_assurance_escalation_queue_signals"]
    actions = payload["governance_continuous_assurance_escalation_queue_actions"]
    checkpoints = payload["governance_continuous_assurance_escalation_queue_checkpoints"]

    assert items
    assert signals
    assert actions
    assert checkpoints

    lanes = {item["lane"] for item in items}
    assert "batch_integrity" in lanes
    assert "write_boundary" in lanes
    assert "execution_boundary" in lanes
    assert "governance_boundary" in lanes
    assert "policy_boundary" in lanes
    assert "owner_review_boundary" in lanes
    assert "saved_view_boundary" in lanes
    assert "evidence_boundary" in lanes

    assert all(item["preview_only"] is True for item in items)
    assert all(item["writes_state"] is False for item in items)
    assert all(item["executable"] is False for item in items)
    assert all(item["raw_evidence_visible"] is False for item in items)

    assert all(signal["writes_state"] is False for signal in signals)
    assert all(signal["executable"] is False for signal in signals)
    assert all(signal["raw_evidence_visible"] is False for signal in signals)

    evidence_modes = {signal["evidence_mode"] for signal in signals}
    assert "safe_summary_only" in evidence_modes
    assert "blocked_action_summary" in evidence_modes
    assert "redacted_pointer_only" in evidence_modes

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 8
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 80
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_256_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_escalation_write"] is True
    assert safety["no_real_escalation_queue_write"] is True
    assert safety["no_real_escalation_queue_state_write"] is True
    assert safety["no_real_escalation_assignment_write"] is True
    assert safety["no_real_escalation_execute"] is True
    assert safety["no_real_escalation_status_write"] is True
    assert safety["no_real_escalation_resolution_write"] is True
    assert safety["no_real_continuous_assurance_write"] is True
    assert safety["no_real_continuous_assurance_check_execute"] is True
    assert safety["no_real_continuous_assurance_status_write"] is True
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


def test_pack_256_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_preview()

    assert third["status"] == "ready"


def test_pack_256_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_queue_v256")

    bridge = mod.build_pack_256_status_bridge()
    assert bridge["pack"] == "256"
    assert bridge["pack_number"] == 256
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Index Preview layer"
    assert bridge["save_batch"] == "251-260"
    assert bridge["save_after_pack"] == 260
    assert bridge["source_pack"] == "255"
    assert bridge["source_status"] == "ready"
    assert bridge["queue_item_count"] >= 8
    assert bridge["queue_signal_count"] >= 32
    assert bridge["queue_action_count"] >= 88
    assert bridge["escalation_queue_ready"] is True
    assert bridge["safe_to_continue_to_pack_257"] is True

    prep = mod.prepare_pack_257_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "257"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Index Preview layer"
    assert prep["save_batch"] == "251-260"
    assert prep["save_after_pack"] == 260
    assert prep["safe_to_continue"] is True


def test_pack_256_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-queue-v256.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-queue-v256.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "256"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Index Preview layer"
