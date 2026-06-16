"""
SEARCHABLE LABEL: TOWER_PACK_292_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_292_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()

    assert payload["pack"] == "292"
    assert payload["pack_number"] == 292
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-detail-drawer-v292.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

    assert payload["source_pack"] == "291"
    assert payload["source_closed_batch"] == "286-290"
    assert payload["save_batch"] == "291-295"
    assert payload["save_after_pack"] == 295
    assert payload["next_pack"] == "293"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["preview_only"] is True
    assert payload["simulation_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_293"] is True
    assert payload["prepare_pack_293_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft"]["pack"] == "293"


def test_pack_292_summary_and_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()
    summary = payload["handoff_policy_route_audit_evidence_handoff_detail_summary"]

    assert summary["source_handoff_card_count"] >= 12
    assert summary["detail_drawer_count"] >= 12
    assert summary["detail_section_count"] >= 96
    assert summary["detail_action_count"] >= 168
    assert summary["detail_checkpoint_count"] >= 8
    assert summary["enabled_action_count"] >= 12
    assert summary["blocked_action_count"] >= 156

    assert summary["all_drawers_preview_only"] is True
    assert summary["all_drawers_pointer_only"] is True
    assert summary["all_drawers_no_writes"] is True
    assert summary["all_drawers_non_executable"] is True
    assert summary["all_drawers_no_raw_evidence"] is True
    assert summary["all_sections_no_writes"] is True
    assert summary["all_sections_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["handoff_detail_drawer_ready"] is True

    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_handoff_detail_write_enabled"] is False
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


def test_pack_292_drawers_sections_actions_checkpoint_shapes():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()

    drawers = payload["handoff_policy_route_audit_evidence_handoff_detail_drawers"]
    sections = payload["handoff_policy_route_audit_evidence_handoff_detail_sections"]
    actions = payload["handoff_policy_route_audit_evidence_handoff_detail_actions"]
    checkpoints = payload["handoff_policy_route_audit_evidence_handoff_detail_checkpoints"]

    assert drawers
    assert sections
    assert actions
    assert checkpoints

    families = {drawer["handoff_family"] for drawer in drawers}
    assert "EVIDENCE_INDEX_HANDOFF" in families
    assert "OB_BOUNDARY_HANDOFF" in families
    assert "TELLER_BOUNDARY_HANDOFF" in families

    assert all(drawer["preview_only"] is True for drawer in drawers)
    assert all(drawer["pointer_only"] is True for drawer in drawers)
    assert all(drawer["writes_state"] is False for drawer in drawers)
    assert all(drawer["executable"] is False for drawer in drawers)
    assert all(drawer["raw_evidence_visible"] is False for drawer in drawers)

    section_types = {section["section_type"] for section in sections}
    assert "raw_evidence" in section_types
    assert "handoff_execution" in section_types
    assert "mutation_block" in section_types
    assert "ob_teller_boundary" in section_types
    assert all(section["writes_state"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]
    assert len(preview_actions) >= 12
    assert len(blocked_actions) >= 156
    assert all(action["enabled"] is True for action in preview_actions)
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_292_status_bridge_next_prep_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292")

    bridge = mod.build_pack_292_status_bridge()
    assert bridge["pack"] == "292"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["detail_drawer_count"] >= 12
    assert bridge["handoff_detail_drawer_ready"] is True
    assert bridge["safe_to_continue_to_pack_293"] is True

    prep = mod.prepare_pack_293_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "293"
    assert prep["source_pack"] == "292"
    assert prep["safe_to_continue"] is True

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-detail-drawer-v292.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-detail-drawer-v292.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "292"
        assert data["status"] == "ready"
        assert data["safe_to_continue_to_pack_293"] is True


def test_pack_292_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292")
    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_preview()
    assert third["status"] == "ready"
