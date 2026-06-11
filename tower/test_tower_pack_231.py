"""
SEARCHABLE LABEL: TOWER_PACK_231_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CONTINUITY_QUEUE_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_231_continuity_queue_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")
    payload = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    assert payload["pack"] == "231"
    assert payload["pack_number"] == 231
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Continuity Queue Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-continuity-queue-v231.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "231-235"
    assert payload["save_after_pack"] == 235

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "230"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_232"] is True
    assert payload["prepare_pack_232_receipt_chain_saved_view_owner_review_continuity_detail_drawer"]["pack"] == "232"


def test_pack_231_continuity_queue_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")
    payload = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    summary = payload["continuity_queue_summary"]

    assert summary["continuity_item_count"] >= 8
    assert summary["continuity_lane_count"] >= 6
    assert summary["continuity_control_count"] >= 7
    assert summary["continuity_checkpoint_count"] >= 5
    assert summary["enabled_control_count"] == 1
    assert summary["blocked_control_count"] >= 6
    assert summary["critical_item_count"] >= 3
    assert summary["high_item_count"] >= 3
    assert summary["repair_bridge_item_count"] >= 1

    assert summary["all_items_preview_only"] is True
    assert summary["all_items_non_executable"] is True
    assert summary["all_raw_evidence_hidden"] is True
    assert summary["all_lanes_view_only"] is True
    assert summary["all_lanes_no_writes"] is True
    assert summary["all_controls_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["continuity_queue_ready"] is True

    assert summary["real_continuity_assignment_enabled"] is False
    assert summary["real_continuity_status_write_enabled"] is False
    assert summary["real_continuity_queue_write_enabled"] is False
    assert summary["real_continuity_checkpoint_write_enabled"] is False
    assert summary["real_followup_write_enabled"] is False
    assert summary["real_owner_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_231_continuity_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")
    payload = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    items = payload["continuity_queue_items"]
    lanes = payload["continuity_queue_lanes"]
    controls = payload["continuity_queue_controls"]
    checkpoints = payload["continuity_queue_checkpoints"]

    assert items
    assert lanes
    assert controls
    assert checkpoints

    assert all(item["continuity_mode"] == "preview_only" for item in items)
    assert all(item["raw_evidence_visible"] is False for item in items)
    assert all(item["executable"] is False for item in items)

    assert all(lane["action_mode"] == "view_only" for lane in lanes)
    assert all(lane["writes_state"] is False for lane in lanes)

    preview_controls = [control for control in controls if control["result"] == "preview_allowed"]
    blocked_controls = [control for control in controls if control["result"] == "blocked_preview_only"]

    assert len(preview_controls) == 1
    assert preview_controls[0]["enabled"] is True
    assert blocked_controls
    assert all(control["enabled"] is False for control in blocked_controls)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_231_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")
    payload = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_continuity_assignment_write"] is True
    assert safety["no_real_continuity_status_write"] is True
    assert safety["no_real_continuity_queue_write"] is True
    assert safety["no_real_continuity_checkpoint_write"] is True
    assert safety["no_real_followup_assignment_write"] is True
    assert safety["no_real_followup_status_write"] is True
    assert safety["no_real_followup_note_write"] is True
    assert safety["no_real_followup_note_version_write"] is True
    assert safety["no_real_owner_review_note_write"] is True
    assert safety["no_real_owner_review_approve"] is True
    assert safety["no_real_owner_review_deny"] is True
    assert safety["no_real_queue_reorder_write"] is True
    assert safety["no_real_saved_view_restore"] is True
    assert safety["no_real_saved_view_revert"] is True
    assert safety["no_real_saved_view_write"] is True
    assert safety["no_real_saved_view_edit"] is True
    assert safety["no_real_saved_view_delete"] is True
    assert safety["no_real_saved_view_apply"] is True
    assert safety["no_real_saved_view_export"] is True
    assert safety["no_real_user_preference_write"] is True
    assert safety["no_archive_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_231_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")

    first = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_continuity_queue_preview()

    assert third["status"] == "ready"


def test_pack_231_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_continuity_queue_v231")

    bridge = mod.build_pack_231_status_bridge()
    assert bridge["pack"] == "231"
    assert bridge["pack_number"] == 231
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "231-235"
    assert bridge["save_after_pack"] == 235
    assert bridge["source_pack"] == "230"
    assert bridge["source_status"] == "ready"
    assert bridge["continuity_item_count"] >= 8
    assert bridge["continuity_lane_count"] >= 6
    assert bridge["continuity_control_count"] >= 7
    assert bridge["repair_bridge_item_count"] >= 1
    assert bridge["continuity_queue_ready"] is True
    assert bridge["safe_to_continue_to_pack_232"] is True

    prep = mod.prepare_pack_232_receipt_chain_saved_view_owner_review_continuity_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "232"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["save_batch"] == "231-235"
    assert prep["save_after_pack"] == 235
    assert prep["safe_to_continue"] is True


def test_pack_231_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-continuity-queue-v231.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-continuity-queue-v231.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "231"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
