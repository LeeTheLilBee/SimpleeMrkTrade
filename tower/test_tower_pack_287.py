"""
SEARCHABLE LABEL: TOWER_PACK_287_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_287_evidence_detail_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    assert payload["pack"] == "287"
    assert payload["pack_number"] == 287
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-detail-drawer-v287.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"

    assert payload["source_pack"] == "286"
    assert payload["source_closed_batch"] == "281-285"
    assert payload["save_batch"] == "286-290"
    assert payload["save_after_pack"] == 290
    assert payload["next_pack"] == "288"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_288"] is True
    assert payload["prepare_pack_288_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_draft"]["pack"] == "288"


def test_pack_287_evidence_detail_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    summary = payload["handoff_policy_route_audit_evidence_detail_summary"]

    assert summary["source_evidence_card_count"] >= 11
    assert summary["detail_drawer_count"] >= 11
    assert summary["detail_section_count"] >= 99
    assert summary["detail_field_count"] >= 99
    assert summary["detail_action_count"] >= 187
    assert summary["detail_checkpoint_count"] >= 8

    assert summary["enabled_action_count"] >= 11
    assert summary["blocked_action_count"] >= 176
    assert summary["redacted_section_count"] >= 22
    assert summary["blocked_section_count"] >= 11
    assert summary["redacted_field_count"] >= 22
    assert summary["editable_field_count"] >= 22

    assert summary["all_drawers_preview_only"] is True
    assert summary["all_drawers_pointer_only"] is True
    assert summary["all_drawers_no_writes"] is True
    assert summary["all_drawers_non_executable"] is True
    assert summary["all_drawers_no_raw_evidence"] is True
    assert summary["all_sections_no_writes"] is True
    assert summary["all_sections_non_executable"] is True
    assert summary["all_sections_no_raw_evidence"] is True
    assert summary["all_fields_no_writes"] is True
    assert summary["all_fields_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["evidence_detail_drawer_ready"] is True

    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_audit_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_287_drawers_sections_fields_actions_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    drawers = payload["handoff_policy_route_audit_evidence_detail_drawers"]
    sections = payload["handoff_policy_route_audit_evidence_detail_sections"]
    fields = payload["handoff_policy_route_audit_evidence_detail_fields"]
    actions = payload["handoff_policy_route_audit_evidence_detail_actions"]
    checkpoints = payload["handoff_policy_route_audit_evidence_detail_checkpoints"]

    assert drawers
    assert sections
    assert fields
    assert actions
    assert checkpoints

    assert all(drawer["preview_only"] is True for drawer in drawers)
    assert all(drawer["pointer_only"] is True for drawer in drawers)
    assert all(drawer["writes_state"] is False for drawer in drawers)
    assert all(drawer["executable"] is False for drawer in drawers)
    assert all(drawer["raw_evidence_visible"] is False for drawer in drawers)

    section_types = {section["section_type"] for section in sections}
    assert "pointer_detail" in section_types
    assert "redaction_detail" in section_types
    assert "mutation_block" in section_types
    assert "tower_boundary" in section_types

    assert all(section["writes_state"] is False for section in sections)
    assert all(section["executable"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)

    redactions = {field["redaction_state"] for field in fields}
    assert "redacted_pointer_only" in redactions
    assert "safe_preview" in redactions
    assert all(field["writes_state"] is False for field in fields)
    assert all(field["raw_evidence_visible"] is False for field in fields)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 11
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 176
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_287_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_evidence_write"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_real_evidence_reveal"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_evidence_restore"] is True
    assert safety["no_real_evidence_apply"] is True
    assert safety["no_real_evidence_delete"] is True
    assert safety["no_real_audit_write"] is True
    assert safety["no_real_policy_write"] is True
    assert safety["no_real_route_change"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_registry_write"] is True
    assert safety["no_real_clearance_write"] is True
    assert safety["no_real_billing_write"] is True
    assert safety["no_real_receipt_write"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True
    assert safety["ob_ui_not_built_in_tower_pack"] is True
    assert safety["teller_ui_not_built_in_tower_pack"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_287_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_preview()

    assert third["status"] == "ready"


def test_pack_287_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_detail_drawer_v287")

    bridge = mod.build_pack_287_status_bridge()
    assert bridge["pack"] == "287"
    assert bridge["pack_number"] == 287
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
    assert bridge["source_pack"] == "286"
    assert bridge["source_closed_batch"] == "281-285"
    assert bridge["save_batch"] == "286-290"
    assert bridge["save_after_pack"] == 290
    assert bridge["next_pack"] == "288"
    assert bridge["detail_drawer_count"] >= 11
    assert bridge["detail_section_count"] >= 99
    assert bridge["detail_field_count"] >= 99
    assert bridge["detail_action_count"] >= 187
    assert bridge["evidence_detail_drawer_ready"] is True
    assert bridge["safe_to_continue_to_pack_288"] is True

    prep = mod.prepare_pack_288_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "288"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
    assert prep["source_closed_batch"] == "281-285"
    assert prep["save_batch"] == "286-290"
    assert prep["save_after_pack"] == 290
    assert prep["safe_to_continue"] is True


def test_pack_287_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-detail-drawer-v287.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-detail-drawer-v287.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "287"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
        assert data["source_closed_batch"] == "281-285"
        assert data["save_batch"] == "286-290"
