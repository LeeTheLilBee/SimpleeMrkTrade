"""
SEARCHABLE LABEL: TOWER_PACK_236_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_INDEX_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_236_cross_batch_index_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    assert payload["pack"] == "236"
    assert payload["pack_number"] == 236
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Cross-Batch Index Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-cross-batch-index-v236.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "236-240"
    assert payload["save_after_pack"] == 240
    assert payload["next_batch"] == "236-240"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_batches"]["221-225"]["pack"] == "225"
    assert payload["source_batches"]["226-230"]["pack"] == "230"
    assert payload["source_batches"]["231-235"]["pack"] == "235"

    assert payload["safe_to_continue_to_pack_237"] is True
    assert payload["prepare_pack_237_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer"]["pack"] == "237"


def test_pack_236_cross_batch_index_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    summary = payload["cross_batch_index_summary"]

    assert summary["indexed_batch_count"] == 3
    assert summary["cross_batch_link_count"] >= 5
    assert summary["cross_batch_lane_count"] >= 5
    assert summary["cross_batch_control_count"] >= 7
    assert summary["cross_batch_checkpoint_count"] >= 6
    assert summary["enabled_control_count"] == 1
    assert summary["blocked_control_count"] >= 6
    assert summary["repair_bridge_link_count"] >= 1
    assert summary["safety_boundary_link_count"] >= 1

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_links_preview_only"] is True
    assert summary["all_links_no_writes"] is True
    assert summary["all_links_no_raw_evidence"] is True
    assert summary["all_lanes_view_only"] is True
    assert summary["all_lanes_no_writes"] is True
    assert summary["all_controls_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["cross_batch_index_ready"] is True

    assert summary["real_cross_batch_index_write_enabled"] is False
    assert summary["real_cross_batch_link_write_enabled"] is False
    assert summary["real_cross_batch_status_write_enabled"] is False
    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_236_cards_links_lanes_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    cards = payload["cross_batch_index_cards"]
    links = payload["cross_batch_links"]
    lanes = payload["cross_batch_lanes"]
    controls = payload["cross_batch_controls"]
    checkpoints = payload["cross_batch_checkpoints"]

    assert cards
    assert links
    assert lanes
    assert controls
    assert checkpoints

    assert {card["batch_range"] for card in cards} == {"221-225", "226-230", "231-235"}
    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    assert all(link["link_mode"] == "preview_only" for link in links)
    assert all(link["writes_state"] is False for link in links)
    assert all(link["raw_evidence_visible"] is False for link in links)

    link_types = {link["link_type"] for link in links}
    assert "repair_bridge_reference" in link_types
    assert "safety_boundary_reference" in link_types
    assert "batch_continuation" in link_types

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


def test_pack_236_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_cross_batch_index_write"] is True
    assert safety["no_real_cross_batch_link_write"] is True
    assert safety["no_real_cross_batch_status_write"] is True
    assert safety["no_real_cross_batch_checkpoint_write"] is True
    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_continuity_write"] is True
    assert safety["no_real_followup_write"] is True
    assert safety["no_real_owner_review_write"] is True
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


def test_pack_236_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")

    first = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_cross_batch_index_preview()

    assert third["status"] == "ready"


def test_pack_236_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_index_v236")

    bridge = mod.build_pack_236_status_bridge()
    assert bridge["pack"] == "236"
    assert bridge["pack_number"] == 236
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "236-240"
    assert bridge["save_after_pack"] == 240
    assert bridge["next_batch"] == "236-240"
    assert bridge["indexed_batch_count"] == 3
    assert bridge["cross_batch_link_count"] >= 5
    assert bridge["repair_bridge_link_count"] >= 1
    assert bridge["cross_batch_index_ready"] is True
    assert bridge["safe_to_continue_to_pack_237"] is True

    prep = mod.prepare_pack_237_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer()
    assert prep["ready"] is True
    assert prep["next_pack"] == "237"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["save_batch"] == "236-240"
    assert prep["save_after_pack"] == 240
    assert prep["safe_to_continue"] is True


def test_pack_236_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-cross-batch-index-v236.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-cross-batch-index-v236.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "236"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
