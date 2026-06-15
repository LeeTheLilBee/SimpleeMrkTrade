"""
SEARCHABLE LABEL: TOWER_PACK_277_HANDOFF_POLICY_ROUTE_ENFORCEMENT_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_277_policy_route_enforcement_detail_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    assert payload["pack"] == "277"
    assert payload["pack_number"] == 277
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Detail Drawer Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-detail-drawer-v277.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement layer"

    assert payload["source_pack"] == "276"
    assert payload["source_closed_batch"] == "271-275"
    assert payload["save_batch"] == "276-280"
    assert payload["save_after_pack"] == 280
    assert payload["next_batch"] == "276-280"
    assert payload["next_pack"] == "278"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_278"] is True
    assert payload["prepare_pack_278_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft"]["pack"] == "278"


def test_pack_277_policy_route_enforcement_detail_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    summary = payload["handoff_policy_route_enforcement_detail_summary"]

    assert summary["source_enforcement_lane_count"] >= 14
    assert summary["detail_drawer_count"] >= 14
    assert summary["detail_section_count"] >= 140
    assert summary["detail_field_count"] >= 126
    assert summary["detail_action_count"] >= 210
    assert summary["detail_checkpoint_count"] >= 8

    assert summary["enabled_action_count"] >= 14
    assert summary["blocked_action_count"] >= 196
    assert summary["editable_field_count"] >= 14
    assert summary["locked_field_count"] >= 112
    assert summary["redacted_field_count"] >= 14
    assert summary["blocked_section_count"] >= 42
    assert summary["redacted_section_count"] >= 14

    assert summary["all_drawers_preview_only"] is True
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
    assert summary["handoff_policy_route_enforcement_detail_ready"] is True

    assert summary["real_policy_write_enabled"] is False
    assert summary["real_policy_apply_enabled"] is False
    assert summary["real_policy_override_enabled"] is False
    assert summary["real_route_enforcement_write_enabled"] is False
    assert summary["real_route_enforcement_apply_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_route_activation_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_app_registry_write_enabled"] is False
    assert summary["real_room_registry_write_enabled"] is False
    assert summary["real_mission_account_registry_write_enabled"] is False
    assert summary["real_ob_route_change_enabled"] is False
    assert summary["real_teller_route_change_enabled"] is False
    assert summary["real_tower_route_change_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_permission_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_subscription_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_277_drawers_sections_fields_actions_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    drawers = payload["handoff_policy_route_enforcement_detail_drawers"]
    sections = payload["handoff_policy_route_enforcement_detail_sections"]
    fields = payload["handoff_policy_route_enforcement_detail_fields"]
    actions = payload["handoff_policy_route_enforcement_detail_actions"]
    checkpoints = payload["handoff_policy_route_enforcement_detail_checkpoints"]

    assert drawers
    assert sections
    assert fields
    assert actions
    assert checkpoints

    assert all(drawer["preview_only"] is True for drawer in drawers)
    assert all(drawer["writes_state"] is False for drawer in drawers)
    assert all(drawer["executable"] is False for drawer in drawers)
    assert all(drawer["raw_evidence_visible"] is False for drawer in drawers)

    assert all(section["writes_state"] is False for section in sections)
    assert all(section["executable"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)

    section_types = {section["section_type"] for section in sections}
    assert "policy" in section_types
    assert "gate" in section_types
    assert "enforcement_mode" in section_types
    assert "denial_behavior" in section_types
    assert "data_boundary" in section_types
    assert "mutation_block" in section_types

    section_modes = {section["evidence_mode"] for section in sections}
    assert "safe_summary_only" in section_modes
    assert "blocked_action_summary" in section_modes
    assert "redacted_pointer_only" in section_modes

    assert all(field["writes_state"] is False for field in fields)
    assert all(field["raw_evidence_visible"] is False for field in fields)

    redaction_states = {field["redaction_state"] for field in fields}
    assert "safe_preview" in redaction_states
    assert "redacted_pointer_only" in redaction_states

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 14
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 196
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_277_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_policy_write"] is True
    assert safety["no_real_policy_apply"] is True
    assert safety["no_real_policy_override"] is True
    assert safety["no_real_route_enforcement_write"] is True
    assert safety["no_real_route_enforcement_apply"] is True
    assert safety["no_real_route_change"] is True
    assert safety["no_real_route_activation"] is True
    assert safety["no_real_evidence_write"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_handoff_write"] is True
    assert safety["no_real_app_registry_write"] is True
    assert safety["no_real_room_registry_write"] is True
    assert safety["no_real_mission_account_registry_write"] is True
    assert safety["no_real_clearance_write"] is True
    assert safety["no_real_permission_write"] is True
    assert safety["no_real_billing_write"] is True
    assert safety["no_real_subscription_write"] is True
    assert safety["no_real_receipt_write"] is True
    assert safety["no_real_archive_write"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True
    assert safety["ob_ui_not_built_in_tower_pack"] is True
    assert safety["teller_ui_not_built_in_tower_pack"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_277_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_preview()

    assert third["status"] == "ready"


def test_pack_277_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_detail_drawer_v277")

    bridge = mod.build_pack_277_status_bridge()
    assert bridge["pack"] == "277"
    assert bridge["pack_number"] == 277
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Handoff Policy Route Enforcement layer"
    assert bridge["source_pack"] == "276"
    assert bridge["source_closed_batch"] == "271-275"
    assert bridge["save_batch"] == "276-280"
    assert bridge["save_after_pack"] == 280
    assert bridge["next_pack"] == "278"
    assert bridge["detail_drawer_count"] >= 14
    assert bridge["detail_section_count"] >= 140
    assert bridge["detail_field_count"] >= 126
    assert bridge["detail_action_count"] >= 210
    assert bridge["handoff_policy_route_enforcement_detail_ready"] is True
    assert bridge["safe_to_continue_to_pack_278"] is True

    prep = mod.prepare_pack_278_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "278"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Handoff Policy Route Enforcement layer"
    assert prep["source_closed_batch"] == "271-275"
    assert prep["save_batch"] == "276-280"
    assert prep["save_after_pack"] == 280
    assert prep["safe_to_continue"] is True


def test_pack_277_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-detail-drawer-v277.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-detail-drawer-v277.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "277"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Handoff Policy Route Enforcement layer"
        assert data["source_closed_batch"] == "271-275"
        assert data["save_batch"] == "276-280"
