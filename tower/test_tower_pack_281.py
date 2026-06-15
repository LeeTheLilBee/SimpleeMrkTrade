"""
SEARCHABLE LABEL: TOWER_PACK_281_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_INDEX_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_281_policy_route_audit_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    assert payload["pack"] == "281"
    assert payload["pack_number"] == 281
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Handoff Policy Route Enforcement Audit Index Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-index-v281.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit layer"

    assert payload["source_closed_batch"] == "276-280"
    assert payload["save_batch"] == "281-285"
    assert payload["save_after_pack"] == 285
    assert payload["next_batch"] == "281-285"
    assert payload["next_pack"] == "282"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "280"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_push"] is True
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_282"] is True
    assert payload["prepare_pack_282_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_detail_drawer"]["pack"] == "282"


def test_pack_281_policy_route_audit_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    summary = payload["handoff_policy_route_enforcement_audit_summary"]

    assert summary["audit_lane_count"] >= 11
    assert summary["audit_gate_count"] >= 55
    assert summary["audit_action_count"] >= 165
    assert summary["audit_checkpoint_count"] >= 8

    assert summary["enabled_action_count"] >= 11
    assert summary["blocked_action_count"] >= 154
    assert summary["critical_audit_count"] >= 6
    assert summary["high_audit_count"] >= 4

    assert "POLICY_COMPLETENESS_AUDIT" in summary["audit_families"]
    assert "DEFAULT_DENY_AUDIT" in summary["audit_families"]
    assert "TOWER_OWNERSHIP_AUDIT" in summary["audit_families"]
    assert "ROUTE_MUTATION_BLOCK_AUDIT" in summary["audit_families"]
    assert "EVIDENCE_REDACTION_AUDIT" in summary["audit_families"]
    assert "OB_ROOM_BOUNDARY_AUDIT" in summary["audit_families"]
    assert "OB_MISSION_ACCOUNT_BOUNDARY_AUDIT" in summary["audit_families"]
    assert "OB_TELLER_BOUNDARY_AUDIT" in summary["audit_families"]
    assert "BILLING_SECURITY_BOUNDARY_AUDIT" in summary["audit_families"]
    assert "OWNER_REVIEW_BOUNDARY_AUDIT" in summary["audit_families"]
    assert "RECEIPT_CHAIN_MUTATION_AUDIT" in summary["audit_families"]

    assert summary["all_lanes_preview_only"] is True
    assert summary["all_audit_no_write"] is True
    assert summary["all_policy_no_write"] is True
    assert summary["all_routes_no_change"] is True
    assert summary["all_lanes_non_executable"] is True
    assert summary["all_lanes_no_raw_evidence"] is True
    assert summary["all_gates_required"] is True
    assert summary["all_gates_passed"] is True
    assert summary["all_gates_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["handoff_policy_route_enforcement_audit_index_ready"] is True

    assert summary["real_audit_write_enabled"] is False
    assert summary["real_audit_result_apply_enabled"] is False
    assert summary["real_audit_override_enabled"] is False
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


def test_pack_281_lanes_gates_actions_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    lanes = payload["handoff_policy_route_enforcement_audit_lanes"]
    gates = payload["handoff_policy_route_enforcement_audit_gates"]
    actions = payload["handoff_policy_route_enforcement_audit_actions"]
    checkpoints = payload["handoff_policy_route_enforcement_audit_checkpoints"]

    assert lanes
    assert gates
    assert actions
    assert checkpoints

    assert all(lane["preview_only"] is True for lane in lanes)
    assert all(lane["audit_write_enabled"] is False for lane in lanes)
    assert all(lane["policy_write_enabled"] is False for lane in lanes)
    assert all(lane["route_change_enabled"] is False for lane in lanes)
    assert all(lane["executable"] is False for lane in lanes)
    assert all(lane["raw_evidence_visible"] is False for lane in lanes)

    assert all(gate["required"] is True for gate in gates)
    assert all(gate["passed"] is True for gate in gates)
    assert all(gate["writes_state"] is False for gate in gates)

    gate_types = {gate["gate_type"] for gate in gates}
    assert "source_batch_closed" in gate_types
    assert "preview_only" in gate_types
    assert "mutation_block" in gate_types
    assert "data_boundary" in gate_types
    assert "detail_drawer_ready" in gate_types

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 11
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 154
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_281_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_audit_write"] is True
    assert safety["no_real_audit_apply"] is True
    assert safety["no_real_audit_override"] is True
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


def test_pack_281_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_preview()

    assert third["status"] == "ready"


def test_pack_281_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_index_v281")

    bridge = mod.build_pack_281_status_bridge()
    assert bridge["pack"] == "281"
    assert bridge["pack_number"] == 281
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Handoff Policy Route Enforcement Audit layer"
    assert bridge["source_closed_batch"] == "276-280"
    assert bridge["save_batch"] == "281-285"
    assert bridge["save_after_pack"] == 285
    assert bridge["next_pack"] == "282"
    assert bridge["source_pack"] == "280"
    assert bridge["source_status"] == "ready"
    assert bridge["audit_lane_count"] >= 11
    assert bridge["audit_gate_count"] >= 55
    assert bridge["audit_action_count"] >= 165
    assert bridge["critical_audit_count"] >= 6
    assert bridge["handoff_policy_route_enforcement_audit_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_282"] is True

    prep = mod.prepare_pack_282_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "282"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Handoff Policy Route Enforcement Audit layer"
    assert prep["source_closed_batch"] == "276-280"
    assert prep["save_batch"] == "281-285"
    assert prep["save_after_pack"] == 285
    assert prep["safe_to_continue"] is True


def test_pack_281_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-index-v281.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-index-v281.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "281"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Handoff Policy Route Enforcement Audit layer"
        assert data["source_closed_batch"] == "276-280"
        assert data["save_batch"] == "281-285"
