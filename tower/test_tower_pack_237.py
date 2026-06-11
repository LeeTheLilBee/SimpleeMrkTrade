"""
SEARCHABLE LABEL: TOWER_PACK_237_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_237_cross_batch_detail_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    assert payload["pack"] == "237"
    assert payload["pack_number"] == 237
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Cross-Batch Detail Drawer Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-cross-batch-detail-drawer-v237.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "236-240"
    assert payload["save_after_pack"] == 240

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "236"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_238"] is True
    assert payload["prepare_pack_238_receipt_chain_saved_view_owner_review_cross_batch_note_draft"]["pack"] == "238"


def test_pack_237_cross_batch_detail_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    summary = payload["cross_batch_detail_summary"]

    assert summary["source_indexed_batch_count"] == 3
    assert summary["source_link_count"] >= 5
    assert summary["detail_drawer_count"] == 3
    assert summary["detail_section_count"] >= 15
    assert summary["detail_link_pointer_count"] >= 8
    assert summary["detail_action_count"] >= 21
    assert summary["detail_checkpoint_count"] >= 5
    assert summary["enabled_action_count"] == 3
    assert summary["blocked_action_count"] >= 18
    assert summary["repair_bridge_pointer_count"] >= 1
    assert summary["safety_boundary_pointer_count"] >= 1

    assert summary["all_headers_preview_only"] is True
    assert summary["all_headers_no_raw_evidence"] is True
    assert summary["all_sections_no_writes"] is True
    assert summary["all_sections_no_raw_evidence"] is True
    assert summary["all_pointers_no_writes"] is True
    assert summary["all_pointers_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["cross_batch_detail_ready"] is True

    assert summary["real_cross_batch_detail_state_write_enabled"] is False
    assert summary["real_cross_batch_index_write_enabled"] is False
    assert summary["real_cross_batch_link_write_enabled"] is False
    assert summary["real_cross_batch_status_write_enabled"] is False
    assert summary["real_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_237_detail_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    headers = payload["cross_batch_detail_headers"]
    sections = payload["cross_batch_detail_sections"]
    pointers = payload["cross_batch_detail_link_pointers"]
    actions = payload["cross_batch_detail_actions"]
    checkpoints = payload["cross_batch_detail_checkpoints"]

    assert headers
    assert sections
    assert pointers
    assert actions
    assert checkpoints

    assert {header["batch_range"] for header in headers} == {"221-225", "226-230", "231-235"}
    assert all(header["detail_mode"] == "preview_only" for header in headers)
    assert all(header["raw_evidence_visible"] is False for header in headers)

    assert all(section["writes_state"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)

    assert all(pointer["reveal_mode"] == "safe_pointer_only" for pointer in pointers)
    assert all(pointer["writes_state"] is False for pointer in pointers)
    assert all(pointer["raw_evidence_visible"] is False for pointer in pointers)

    pointer_types = {pointer["link_type"] for pointer in pointers}
    assert "repair_bridge_reference" in pointer_types
    assert "safety_boundary_reference" in pointer_types

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) == 3
    assert all(action["enabled"] is True for action in preview_actions)
    assert blocked_actions
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_237_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_cross_batch_detail_state_write"] is True
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


def test_pack_237_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")

    first = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_preview()

    assert third["status"] == "ready"


def test_pack_237_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237")

    bridge = mod.build_pack_237_status_bridge()
    assert bridge["pack"] == "237"
    assert bridge["pack_number"] == 237
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "236-240"
    assert bridge["save_after_pack"] == 240
    assert bridge["source_pack"] == "236"
    assert bridge["source_status"] == "ready"
    assert bridge["detail_drawer_count"] == 3
    assert bridge["detail_section_count"] >= 15
    assert bridge["detail_link_pointer_count"] >= 8
    assert bridge["repair_bridge_pointer_count"] >= 1
    assert bridge["cross_batch_detail_ready"] is True
    assert bridge["safe_to_continue_to_pack_238"] is True

    prep = mod.prepare_pack_238_receipt_chain_saved_view_owner_review_cross_batch_note_draft()
    assert prep["ready"] is True
    assert prep["next_pack"] == "238"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["save_batch"] == "236-240"
    assert prep["save_after_pack"] == 240
    assert prep["safe_to_continue"] is True


def test_pack_237_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-cross-batch-detail-drawer-v237.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-cross-batch-detail-drawer-v237.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "237"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
