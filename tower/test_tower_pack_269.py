"""
SEARCHABLE LABEL: TOWER_PACK_269_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_HANDOFF_NOTE_VERSION_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_269_handoff_note_version_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    assert payload["pack"] == "269"
    assert payload["pack_number"] == 269
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Handoff Note Version Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-handoff-note-version-v269.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Handoff layer"

    assert payload["source_pack"] == "268"
    assert payload["source_closed_batch"] == "261-265"
    assert payload["save_batch"] == "266-270"
    assert payload["save_after_pack"] == 270
    assert payload["next_batch"] == "266-270"
    assert payload["next_pack"] == "270"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_270"] is True
    assert payload["prepare_pack_270_receipt_chain_saved_view_owner_review_governance_handoff_batch_close_readiness"]["pack"] == "270"


def test_pack_269_handoff_note_version_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    summary = payload["governance_handoff_note_version_summary"]

    assert summary["source_draft_card_count"] >= 12
    assert summary["version_card_count"] >= 24
    assert summary["compare_row_count"] >= 216
    assert summary["version_action_count"] >= 336
    assert summary["version_checkpoint_count"] >= 7

    assert summary["enabled_action_count"] >= 24
    assert summary["blocked_action_count"] >= 312
    assert summary["redacted_compare_row_count"] >= 24

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_rows_no_writes"] is True
    assert summary["all_rows_non_executable"] is True
    assert summary["all_rows_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["governance_handoff_note_version_ready"] is True

    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_handoff_note_write_enabled"] is False
    assert summary["real_handoff_note_save_enabled"] is False
    assert summary["real_handoff_note_submit_enabled"] is False
    assert summary["real_handoff_note_delete_enabled"] is False
    assert summary["real_handoff_note_version_write_enabled"] is False
    assert summary["real_handoff_note_version_restore_enabled"] is False
    assert summary["real_handoff_note_version_apply_enabled"] is False
    assert summary["real_handoff_note_version_delete_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
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
    assert summary["real_evidence_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_269_cards_rows_actions_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    cards = payload["governance_handoff_note_version_cards"]
    rows = payload["governance_handoff_note_version_compare_rows"]
    actions = payload["governance_handoff_note_version_actions"]
    checkpoints = payload["governance_handoff_note_version_checkpoints"]

    assert cards
    assert rows
    assert actions
    assert checkpoints

    assert all(card["version_mode"] == "preview_only" for card in cards)
    assert all(card["writes_state"] is False for card in cards)
    assert all(card["executable"] is False for card in cards)
    assert all(card["raw_evidence_visible"] is False for card in cards)

    assert all(row["writes_state"] is False for row in rows)
    assert all(row["executable"] is False for row in rows)
    assert all(row["raw_evidence_visible"] is False for row in rows)

    redaction_states = {row["redaction_state"] for row in rows}
    assert "safe_preview" in redaction_states
    assert "redacted_pointer_only" in redaction_states

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 24
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 312
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_269_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_handoff_write"] is True
    assert safety["no_real_handoff_note_write"] is True
    assert safety["no_real_handoff_note_save"] is True
    assert safety["no_real_handoff_note_submit"] is True
    assert safety["no_real_handoff_note_delete"] is True
    assert safety["no_real_handoff_note_version_write"] is True
    assert safety["no_real_handoff_note_version_restore"] is True
    assert safety["no_real_handoff_note_version_apply"] is True
    assert safety["no_real_handoff_note_version_delete"] is True
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


def test_pack_269_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_handoff_note_version_preview()

    assert third["status"] == "ready"


def test_pack_269_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_handoff_note_version_v269")

    bridge = mod.build_pack_269_status_bridge()
    assert bridge["pack"] == "269"
    assert bridge["pack_number"] == 269
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Handoff layer"
    assert bridge["source_pack"] == "268"
    assert bridge["source_closed_batch"] == "261-265"
    assert bridge["save_batch"] == "266-270"
    assert bridge["save_after_pack"] == 270
    assert bridge["next_pack"] == "270"
    assert bridge["version_card_count"] >= 24
    assert bridge["compare_row_count"] >= 216
    assert bridge["version_action_count"] >= 336
    assert bridge["governance_handoff_note_version_ready"] is True
    assert bridge["safe_to_continue_to_pack_270"] is True

    prep = mod.prepare_pack_270_receipt_chain_saved_view_owner_review_governance_handoff_batch_close_readiness()
    assert prep["ready"] is True
    assert prep["next_pack"] == "270"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Handoff layer"
    assert prep["source_closed_batch"] == "261-265"
    assert prep["save_batch"] == "266-270"
    assert prep["save_after_pack"] == 270
    assert prep["safe_to_continue"] is True


def test_pack_269_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-handoff-note-version-v269.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-handoff-note-version-v269.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "269"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Handoff layer"
        assert data["source_closed_batch"] == "261-265"
        assert data["save_batch"] == "266-270"
