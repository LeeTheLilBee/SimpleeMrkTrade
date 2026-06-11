"""
SEARCHABLE LABEL: TOWER_PACK_257_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_CONTINUOUS_ASSURANCE_ESCALATION_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_257_escalation_detail_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    assert payload["pack"] == "257"
    assert payload["pack_number"] == 257
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Continuous Assurance Escalation Detail Drawer Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-detail-drawer-v257.json"

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

    assert payload["source_pack"] == "256"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_258"] is True
    assert payload["prepare_pack_258_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_note_draft"]["pack"] == "258"


def test_pack_257_escalation_detail_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    summary = payload["governance_continuous_assurance_escalation_detail_summary"]

    assert summary["source_queue_item_count"] >= 8
    assert summary["detail_drawer_count"] >= 8
    assert summary["detail_section_count"] >= 56
    assert summary["evidence_pointer_count"] >= 32
    assert summary["detail_action_count"] >= 104
    assert summary["detail_checkpoint_count"] >= 5
    assert summary["enabled_action_count"] >= 8
    assert summary["blocked_action_count"] >= 96
    assert summary["redacted_section_count"] >= 8
    assert summary["redacted_pointer_count"] >= 8

    assert summary["all_drawers_preview_only"] is True
    assert summary["all_drawers_no_writes"] is True
    assert summary["all_drawers_non_executable"] is True
    assert summary["all_drawers_no_raw_evidence"] is True
    assert summary["all_sections_no_writes"] is True
    assert summary["all_sections_non_executable"] is True
    assert summary["all_sections_no_raw_evidence"] is True
    assert summary["all_pointers_no_reveal"] is True
    assert summary["all_pointers_no_export"] is True
    assert summary["all_pointers_no_writes"] is True
    assert summary["all_pointers_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["escalation_detail_ready"] is True

    assert summary["real_escalation_write_enabled"] is False
    assert summary["real_escalation_detail_write_enabled"] is False
    assert summary["real_escalation_detail_drawer_state_write_enabled"] is False
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


def test_pack_257_detail_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    drawers = payload["governance_continuous_assurance_escalation_detail_drawers"]
    sections = payload["governance_continuous_assurance_escalation_detail_sections"]
    pointers = payload["governance_continuous_assurance_escalation_evidence_pointers"]
    actions = payload["governance_continuous_assurance_escalation_detail_actions"]
    checkpoints = payload["governance_continuous_assurance_escalation_detail_checkpoints"]

    assert drawers
    assert sections
    assert pointers
    assert actions
    assert checkpoints

    assert all(drawer["preview_only"] is True for drawer in drawers)
    assert all(drawer["writes_state"] is False for drawer in drawers)
    assert all(drawer["executable"] is False for drawer in drawers)
    assert all(drawer["raw_evidence_visible"] is False for drawer in drawers)

    assert all(section["writes_state"] is False for section in sections)
    assert all(section["executable"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)

    evidence_modes = {section["evidence_mode"] for section in sections}
    assert "safe_summary_only" in evidence_modes
    assert "blocked_action_summary" in evidence_modes
    assert "redacted_pointer_only" in evidence_modes

    assert all(pointer["reveal_allowed"] is False for pointer in pointers)
    assert all(pointer["export_allowed"] is False for pointer in pointers)
    assert all(pointer["writes_state"] is False for pointer in pointers)
    assert all(pointer["raw_evidence_visible"] is False for pointer in pointers)

    pointer_modes = {pointer["pointer_mode"] for pointer in pointers}
    assert "safe_pointer_only" in pointer_modes
    assert "redacted_pointer_only" in pointer_modes

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 8
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 96
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_257_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_escalation_write"] is True
    assert safety["no_real_escalation_detail_write"] is True
    assert safety["no_real_escalation_detail_drawer_state_write"] is True
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


def test_pack_257_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_preview()

    assert third["status"] == "ready"


def test_pack_257_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_detail_drawer_v257")

    bridge = mod.build_pack_257_status_bridge()
    assert bridge["pack"] == "257"
    assert bridge["pack_number"] == 257
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Index Preview layer"
    assert bridge["save_batch"] == "251-260"
    assert bridge["save_after_pack"] == 260
    assert bridge["source_pack"] == "256"
    assert bridge["source_status"] == "ready"
    assert bridge["detail_drawer_count"] >= 8
    assert bridge["detail_section_count"] >= 56
    assert bridge["evidence_pointer_count"] >= 32
    assert bridge["detail_action_count"] >= 104
    assert bridge["escalation_detail_ready"] is True
    assert bridge["safe_to_continue_to_pack_258"] is True

    prep = mod.prepare_pack_258_receipt_chain_saved_view_owner_review_governance_continuous_assurance_escalation_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "258"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Index Preview layer"
    assert prep["save_batch"] == "251-260"
    assert prep["save_after_pack"] == 260
    assert prep["safe_to_continue"] is True


def test_pack_257_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-detail-drawer-v257.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-continuous-assurance-escalation-detail-drawer-v257.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "257"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Index Preview layer"
