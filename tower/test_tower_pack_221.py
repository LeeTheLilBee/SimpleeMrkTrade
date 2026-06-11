"""
SEARCHABLE LABEL: TOWER_PACK_221_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_QUEUE_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_221_owner_review_queue_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")
    payload = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    assert payload["pack"] == "221"
    assert payload["pack_number"] == 221
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Queue Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-queue-v221.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "221-225"
    assert payload["save_after_pack"] == 225

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "220"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_222"] is True
    assert payload["prepare_pack_222_saved_view_owner_review_detail_drawer"]["pack"] == "222"


def test_pack_221_owner_review_queue_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")
    payload = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    summary = payload["owner_review_queue_summary"]

    assert summary["queue_item_count"] >= 6
    assert summary["queue_lane_count"] >= 4
    assert summary["queue_control_count"] >= 7
    assert summary["queue_checkpoint_count"] >= 6
    assert summary["enabled_control_count"] == 1
    assert summary["blocked_control_count"] >= 6
    assert summary["critical_item_count"] >= 2
    assert summary["high_item_count"] >= 2

    assert summary["all_items_preview_only"] is True
    assert summary["all_items_non_executable"] is True
    assert summary["all_raw_evidence_hidden"] is True
    assert summary["all_lanes_view_only"] is True
    assert summary["all_lanes_no_writes"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["owner_review_queue_ready"] is True

    assert summary["real_owner_approval_enabled"] is False
    assert summary["real_owner_denial_enabled"] is False
    assert summary["real_owner_note_write_enabled"] is False
    assert summary["real_queue_state_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_221_queue_items_lanes_controls_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")
    payload = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    items = payload["owner_review_queue_items"]
    lanes = payload["owner_review_queue_lanes"]
    controls = payload["owner_review_queue_controls"]
    checkpoints = payload["owner_review_queue_checkpoints"]

    assert items
    assert lanes
    assert controls
    assert checkpoints

    assert all(item["owner_action_mode"] == "preview_only" for item in items)
    assert all(item["raw_evidence_visible"] is False for item in items)
    assert all(item["executable"] is False for item in items)

    assert all(lane["action_mode"] == "view_only" for lane in lanes)
    assert all(lane["writes_state"] is False for lane in lanes)

    open_detail = [control for control in controls if control["control_id"] == "owner_review_control_221_open_detail"]
    assert open_detail
    assert open_detail[0]["enabled"] is True
    assert open_detail[0]["result"] == "preview_allowed"

    blocked_controls = [control for control in controls if control["enabled"] is False]
    assert len(blocked_controls) >= 6
    assert all(control["result"] == "blocked_preview_only" for control in blocked_controls)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_221_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")
    payload = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_owner_review_approve"] is True
    assert safety["no_real_owner_review_deny"] is True
    assert safety["no_real_owner_review_assign"] is True
    assert safety["no_real_owner_review_note_write"] is True
    assert safety["no_real_queue_reorder_write"] is True
    assert safety["no_real_queue_filter_save"] is True
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


def test_pack_221_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")

    first = mod.build_receipt_chain_saved_view_owner_review_queue_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_queue_preview()

    assert third["status"] == "ready"


def test_pack_221_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_queue_v221")

    bridge = mod.build_pack_221_status_bridge()
    assert bridge["pack"] == "221"
    assert bridge["pack_number"] == 221
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "221-225"
    assert bridge["save_after_pack"] == 225
    assert bridge["source_pack"] == "220"
    assert bridge["source_status"] == "ready"
    assert bridge["queue_item_count"] >= 6
    assert bridge["queue_lane_count"] >= 4
    assert bridge["queue_control_count"] >= 7
    assert bridge["owner_review_queue_ready"] is True
    assert bridge["safe_to_continue_to_pack_222"] is True

    prep = mod.prepare_pack_222_saved_view_owner_review_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "222"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["save_batch"] == "221-225"
    assert prep["save_after_pack"] == 225
    assert prep["safe_to_continue"] is True


def test_pack_221_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-queue-v221.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-queue-v221.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "221"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
