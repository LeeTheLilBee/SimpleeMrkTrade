"""
SEARCHABLE LABEL: TOWER_PACK_266_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_HANDOFF_INDEX_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_266_handoff_index_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    assert payload["pack"] == "266"
    assert payload["pack_number"] == 266
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Handoff Index Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-handoff-index-v266.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Handoff layer"

    assert payload["source_closed_batch"] == "261-265"
    assert payload["save_batch"] == "266-270"
    assert payload["save_after_pack"] == 270
    assert payload["next_batch"] == "266-270"
    assert payload["next_pack"] == "267"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "265"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True
    assert payload["source_safe_to_push"] is True

    assert payload["safe_to_continue_to_pack_267"] is True
    assert payload["prepare_pack_267_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer"]["pack"] == "267"


def test_pack_266_ob_teller_tower_references_are_indexed_not_built():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    ob_ref = payload["ob_reference_only"]
    teller_ref = payload["teller_reference_only"]
    tower_surfaces = payload["tower_owned_surfaces"]

    assert ob_ref["ob_ui_not_built_here"] is True
    assert "OB.Dashboard" in ob_ref["ob_protected_rooms"]
    assert "OB.MarketMap" in ob_ref["ob_protected_rooms"]
    assert "OB.SymbolPage" in ob_ref["ob_protected_rooms"]
    assert "OB.TradeCenter" in ob_ref["ob_protected_rooms"]
    assert "OB.ReviewCenter" in ob_ref["ob_protected_rooms"]
    assert "OB.OwnerConsole" in ob_ref["ob_protected_rooms"]

    assert "OB.PersonalAccount" in ob_ref["ob_mission_accounts"]
    assert "OB.TrustAccount" in ob_ref["ob_mission_accounts"]
    assert "OB.SimpleeWorldBusinessAccount" in ob_ref["ob_mission_accounts"]
    assert "OB.SimpleeOnTheGoATMAccount" in ob_ref["ob_mission_accounts"]
    assert "OB.SimpleePropertyApartmentAccount" in ob_ref["ob_mission_accounts"]
    assert "OB.ProofDemoAccount" in ob_ref["ob_mission_accounts"]

    assert teller_ref["teller_ui_not_built_here"] is True
    assert "Teller.EmployeePortal" in teller_ref["teller_protected_surfaces"]
    assert "Teller.ManagerPortal" in teller_ref["teller_protected_surfaces"]
    assert "Teller.OwnerDashboard" in teller_ref["teller_protected_surfaces"]
    assert "Teller.Payroll" in teller_ref["teller_protected_surfaces"]

    assert "Tower.Login" in tower_surfaces
    assert "Tower.Billing" in tower_surfaces
    assert "Tower.Subscription" in tower_surfaces
    assert "Tower.Clearance" in tower_surfaces
    assert "Tower.ModePermissions" in tower_surfaces


def test_pack_266_handoff_index_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    summary = payload["governance_handoff_index_summary"]

    assert summary["handoff_lane_count"] >= 12
    assert summary["boundary_rule_count"] >= 60
    assert summary["handoff_action_count"] >= 84
    assert summary["handoff_checkpoint_count"] >= 7
    assert summary["enabled_action_count"] >= 12
    assert summary["blocked_action_count"] >= 72
    assert summary["allowed_rule_count"] >= 24
    assert summary["blocked_rule_count"] >= 36

    assert "OB_ROOM_ACCESS" in summary["handoff_families"]
    assert "MISSION_ACCOUNT_ACCESS" in summary["handoff_families"]
    assert "OB_TO_TELLER_BUSINESS_HANDOFF" in summary["handoff_families"]
    assert "TELLER_TO_OB_STATUS_HANDOFF" in summary["handoff_families"]
    assert "PROOF_RECEIPT_HANDOFF" in summary["handoff_families"]

    assert summary["ob_room_lane_count"] >= 4
    assert summary["mission_account_lane_count"] >= 4
    assert summary["teller_lane_count"] >= 4
    assert summary["tower_lane_count"] >= 4

    assert summary["all_lanes_preview_only"] is True
    assert summary["all_lanes_no_writes"] is True
    assert summary["all_lanes_non_executable"] is True
    assert summary["all_lanes_no_raw_evidence"] is True
    assert summary["all_rules_no_writes"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["governance_handoff_index_ready"] is True

    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_app_registry_write_enabled"] is False
    assert summary["real_room_registry_write_enabled"] is False
    assert summary["real_mission_account_registry_write_enabled"] is False
    assert summary["real_ob_route_change_enabled"] is False
    assert summary["real_teller_route_change_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_permission_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_subscription_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_266_handoff_lanes_rules_and_actions_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    lanes = payload["governance_handoff_index_lanes"]
    rules = payload["governance_handoff_boundary_rules"]
    actions = payload["governance_handoff_index_actions"]
    checkpoints = payload["governance_handoff_index_checkpoints"]

    assert lanes
    assert rules
    assert actions
    assert checkpoints

    assert all(lane["preview_only"] is True for lane in lanes)
    assert all(lane["writes_state"] is False for lane in lanes)
    assert all(lane["executable"] is False for lane in lanes)
    assert all(lane["raw_evidence_visible"] is False for lane in lanes)

    assert all(rule["writes_state"] is False for rule in rules)

    blocked_rules = [rule for rule in rules if rule["blocked"] is True]
    allowed_rules = [rule for rule in rules if rule["allowed"] is True]
    assert blocked_rules
    assert allowed_rules

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 12
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 72
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_266_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_handoff_write"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_route_change"] is True
    assert safety["no_real_app_registry_write"] is True
    assert safety["no_real_room_registry_write"] is True
    assert safety["no_real_mission_account_registry_write"] is True
    assert safety["no_real_clearance_write"] is True
    assert safety["no_real_permission_write"] is True
    assert safety["no_real_billing_write"] is True
    assert safety["no_real_subscription_write"] is True
    assert safety["no_real_receipt_write"] is True
    assert safety["no_real_archive_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True
    assert safety["ob_ui_not_built_in_tower_pack"] is True
    assert safety["teller_ui_not_built_in_tower_pack"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_266_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_index_preview()

    assert third["status"] == "ready"


def test_pack_266_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_index_v266")

    bridge = mod.build_pack_266_status_bridge()
    assert bridge["pack"] == "266"
    assert bridge["pack_number"] == 266
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Handoff layer"
    assert bridge["source_closed_batch"] == "261-265"
    assert bridge["save_batch"] == "266-270"
    assert bridge["save_after_pack"] == 270
    assert bridge["next_pack"] == "267"
    assert bridge["source_pack"] == "265"
    assert bridge["source_status"] == "ready"
    assert bridge["handoff_lane_count"] >= 12
    assert bridge["boundary_rule_count"] >= 60
    assert bridge["handoff_action_count"] >= 84
    assert bridge["governance_handoff_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_267"] is True

    prep = mod.prepare_pack_267_receipt_chain_saved_view_owner_review_governance_handoff_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "267"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Handoff layer"
    assert prep["source_closed_batch"] == "261-265"
    assert prep["save_batch"] == "266-270"
    assert prep["save_after_pack"] == 270
    assert prep["safe_to_continue"] is True


def test_pack_266_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-handoff-index-v266.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-handoff-index-v266.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "266"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Handoff layer"
        assert data["source_closed_batch"] == "261-265"
        assert data["save_batch"] == "266-270"
