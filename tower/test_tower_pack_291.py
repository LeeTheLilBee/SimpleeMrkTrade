"""
SEARCHABLE LABEL: TOWER_PACK_291_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_INDEX_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_291_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()

    assert payload["pack"] == "291"
    assert payload["pack_number"] == 291
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-index-v291.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

    assert payload["source_pack"] == "290"
    assert payload["source_closed_batch"] == "286-290"
    assert payload["save_batch"] == "291-295"
    assert payload["save_after_pack"] == 295
    assert payload["next_pack"] == "292"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["preview_only"] is True
    assert payload["simulation_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_292"] is True
    assert payload["prepare_pack_292_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer"]["pack"] == "292"


def test_pack_291_summary_and_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()
    summary = payload["handoff_policy_route_audit_evidence_handoff_index_summary"]

    assert summary["handoff_card_count"] >= 12
    assert summary["handoff_gate_count"] >= 60
    assert summary["handoff_action_count"] >= 168
    assert summary["handoff_checkpoint_count"] >= 8
    assert summary["enabled_action_count"] >= 12
    assert summary["blocked_action_count"] >= 156

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_pointer_only"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_gates_passed"] is True
    assert summary["all_gates_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["handoff_index_ready"] is True

    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_evidence_transfer_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_audit_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_291_cards_gates_actions_checkpoint_shapes():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()

    cards = payload["handoff_policy_route_audit_evidence_handoff_index_cards"]
    gates = payload["handoff_policy_route_audit_evidence_handoff_gates"]
    actions = payload["handoff_policy_route_audit_evidence_handoff_actions"]
    checkpoints = payload["handoff_policy_route_audit_evidence_handoff_checkpoints"]

    families = {card["handoff_family"] for card in cards}
    assert "EVIDENCE_INDEX_HANDOFF" in families
    assert "OB_BOUNDARY_HANDOFF" in families
    assert "TELLER_BOUNDARY_HANDOFF" in families
    assert "MISSION_ACCOUNT_BOUNDARY_HANDOFF" in families
    assert "RECEIPT_CHAIN_BOUNDARY_HANDOFF" in families

    assert all(card["preview_only"] is True for card in cards)
    assert all(card["pointer_only"] is True for card in cards)
    assert all(card["writes_state"] is False for card in cards)
    assert all(card["executable"] is False for card in cards)
    assert all(card["raw_evidence_visible"] is False for card in cards)

    assert all(gate["required"] is True for gate in gates)
    assert all(gate["passed"] is True for gate in gates)
    assert all(gate["writes_state"] is False for gate in gates)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]
    assert len(preview_actions) >= 12
    assert len(blocked_actions) >= 156
    assert all(action["enabled"] is True for action in preview_actions)
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_291_status_bridge_next_prep_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291")

    bridge = mod.build_pack_291_status_bridge()
    assert bridge["pack"] == "291"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["handoff_card_count"] >= 12
    assert bridge["handoff_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_292"] is True

    prep = mod.prepare_pack_292_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "292"
    assert prep["source_pack"] == "291"
    assert prep["safe_to_continue"] is True

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-index-v291.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-index-v291.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "291"
        assert data["status"] == "ready"
        assert data["safe_to_continue_to_pack_292"] is True


def test_pack_291_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291")
    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_preview()
    assert third["status"] == "ready"
