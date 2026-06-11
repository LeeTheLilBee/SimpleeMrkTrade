"""
SEARCHABLE LABEL: TOWER_PACK_222_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_DETAIL_DRAWER_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_222_detail_drawer_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")
    payload = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    assert payload["pack"] == "222"
    assert payload["pack_number"] == 222
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Detail Drawer Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "221-225"
    assert payload["save_after_pack"] == 225

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "221"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_223"] is True
    assert payload["prepare_pack_223_saved_view_owner_review_note_draft_preview"]["pack"] == "223"


def test_pack_222_detail_drawer_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")
    payload = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    summary = payload["detail_drawer_summary"]

    assert summary["source_queue_item_count"] >= 6
    assert summary["detail_drawer_count"] >= 6
    assert summary["detail_section_count"] >= 18
    assert summary["detail_action_count"] >= 36
    assert summary["detail_evidence_pointer_count"] >= 12
    assert summary["detail_checkpoint_count"] >= 5
    assert summary["enabled_action_count"] >= 6
    assert summary["blocked_action_count"] >= 30

    assert summary["all_headers_preview_only"] is True
    assert summary["all_sections_no_writes"] is True
    assert summary["all_sections_no_raw_evidence"] is True
    assert summary["all_pointers_no_raw_evidence"] is True
    assert summary["all_blocking_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["detail_drawer_ready"] is True

    assert summary["real_owner_approval_enabled"] is False
    assert summary["real_owner_denial_enabled"] is False
    assert summary["real_owner_note_write_enabled"] is False
    assert summary["real_queue_state_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_222_detail_drawer_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")
    payload = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    headers = payload["detail_drawer_headers"]
    sections = payload["detail_drawer_sections"]
    actions = payload["detail_drawer_actions"]
    pointers = payload["detail_drawer_evidence_pointers"]
    checkpoints = payload["detail_drawer_checkpoints"]

    assert headers
    assert sections
    assert actions
    assert pointers
    assert checkpoints

    assert all(header["owner_action_mode"] == "preview_only" for header in headers)
    assert all(section["writes_state"] is False for section in sections)
    assert all(section["raw_evidence_visible"] is False for section in sections)
    assert all(pointer["raw_evidence_visible"] is False for pointer in pointers)
    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert preview_actions
    assert blocked_actions
    assert all(action["enabled"] is True for action in preview_actions)
    assert all(action["enabled"] is False for action in blocked_actions)


def test_pack_222_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")
    payload = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_owner_review_approve"] is True
    assert safety["no_real_owner_review_deny"] is True
    assert safety["no_real_owner_review_assign"] is True
    assert safety["no_real_owner_review_note_write"] is True
    assert safety["no_real_owner_review_status_write"] is True
    assert safety["no_real_detail_drawer_state_write"] is True
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


def test_pack_222_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")

    first = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_detail_drawer_preview()

    assert third["status"] == "ready"


def test_pack_222_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_detail_drawer_v222")

    bridge = mod.build_pack_222_status_bridge()
    assert bridge["pack"] == "222"
    assert bridge["pack_number"] == 222
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "221-225"
    assert bridge["save_after_pack"] == 225
    assert bridge["source_pack"] == "221"
    assert bridge["source_status"] == "ready"
    assert bridge["detail_drawer_count"] >= 6
    assert bridge["detail_section_count"] >= 18
    assert bridge["detail_action_count"] >= 36
    assert bridge["detail_drawer_ready"] is True
    assert bridge["safe_to_continue_to_pack_223"] is True

    prep = mod.prepare_pack_223_saved_view_owner_review_note_draft_preview()
    assert prep["ready"] is True
    assert prep["next_pack"] == "223"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["save_batch"] == "221-225"
    assert prep["save_after_pack"] == 225
    assert prep["safe_to_continue"] is True


def test_pack_222_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-detail-drawer-v222.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "222"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
