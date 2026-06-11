"""
SEARCHABLE LABEL: TOWER_PACK_243_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_GOVERNANCE_NOTE_DRAFT_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_243_governance_note_draft_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    assert payload["pack"] == "243"
    assert payload["pack_number"] == 243
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Governance Note Draft Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-governance-note-draft-v243.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Governance Index Preview layer"

    assert payload["save_batch"] == "241-245"
    assert payload["save_after_pack"] == 245

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "242"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_244"] is True
    assert payload["prepare_pack_244_receipt_chain_saved_view_owner_review_governance_note_version"]["pack"] == "244"


def test_pack_243_governance_note_draft_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    summary = payload["governance_note_draft_summary"]

    assert summary["source_detail_drawer_count"] >= 8
    assert summary["draft_card_count"] >= 8
    assert summary["draft_field_count"] >= 56
    assert summary["draft_action_count"] >= 64
    assert summary["checkpoint_count"] >= 5
    assert summary["enabled_action_count"] >= 8
    assert summary["blocked_action_count"] >= 56
    assert summary["editable_field_count"] >= 24
    assert summary["locked_field_count"] >= 32
    assert summary["redacted_field_count"] >= 8

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_fields_no_writes"] is True
    assert summary["all_fields_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["governance_note_draft_ready"] is True

    assert summary["real_governance_note_write_enabled"] is False
    assert summary["real_governance_note_save_enabled"] is False
    assert summary["real_governance_note_submit_enabled"] is False
    assert summary["real_governance_note_delete_enabled"] is False
    assert summary["real_governance_note_version_write_enabled"] is False
    assert summary["real_governance_index_write_enabled"] is False
    assert summary["real_governance_control_write_enabled"] is False
    assert summary["real_policy_change_enabled"] is False
    assert summary["real_approval_execution_enabled"] is False
    assert summary["real_denial_execution_enabled"] is False
    assert summary["real_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_243_governance_note_draft_parts_are_preview_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    cards = payload["governance_note_draft_cards"]
    fields = payload["governance_note_draft_fields"]
    actions = payload["governance_note_draft_actions"]
    checkpoints = payload["governance_note_draft_checkpoints"]

    assert cards
    assert fields
    assert actions
    assert checkpoints

    assert all(card["draft_mode"] == "preview_only" for card in cards)
    assert all(card["writes_state"] is False for card in cards)
    assert all(card["executable"] is False for card in cards)
    assert all(card["raw_evidence_visible"] is False for card in cards)

    assert all(field["writes_state"] is False for field in fields)
    assert all(field["raw_evidence_visible"] is False for field in fields)

    redaction_states = {field["redaction_state"] for field in fields}
    assert "safe_preview" in redaction_states
    assert "redacted_pointer_only" in redaction_states

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 8
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 56
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_243_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")
    payload = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_governance_note_write"] is True
    assert safety["no_real_governance_note_save"] is True
    assert safety["no_real_governance_note_submit"] is True
    assert safety["no_real_governance_note_delete"] is True
    assert safety["no_real_governance_note_version_write"] is True
    assert safety["no_real_governance_note_version_restore"] is True
    assert safety["no_real_governance_detail_state_write"] is True
    assert safety["no_real_governance_index_write"] is True
    assert safety["no_real_governance_control_write"] is True
    assert safety["no_real_governance_status_write"] is True
    assert safety["no_real_governance_checkpoint_write"] is True
    assert safety["no_real_policy_change_write"] is True
    assert safety["no_real_policy_enable"] is True
    assert safety["no_real_policy_disable"] is True
    assert safety["no_real_policy_override"] is True
    assert safety["no_real_approval_execute"] is True
    assert safety["no_real_denial_execute"] is True
    assert safety["no_real_owner_review_execute"] is True
    assert safety["no_real_cross_batch_write"] is True
    assert safety["no_real_continuity_write"] is True
    assert safety["no_real_followup_write"] is True
    assert safety["no_real_owner_review_write"] is True
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


def test_pack_243_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")

    first = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_governance_note_draft_preview()

    assert third["status"] == "ready"


def test_pack_243_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_governance_note_draft_v243")

    bridge = mod.build_pack_243_status_bridge()
    assert bridge["pack"] == "243"
    assert bridge["pack_number"] == 243
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Governance Index Preview layer"
    assert bridge["save_batch"] == "241-245"
    assert bridge["save_after_pack"] == 245
    assert bridge["source_pack"] == "242"
    assert bridge["source_status"] == "ready"
    assert bridge["draft_card_count"] >= 8
    assert bridge["draft_field_count"] >= 56
    assert bridge["draft_action_count"] >= 64
    assert bridge["governance_note_draft_ready"] is True
    assert bridge["safe_to_continue_to_pack_244"] is True

    prep = mod.prepare_pack_244_receipt_chain_saved_view_owner_review_governance_note_version()
    assert prep["ready"] is True
    assert prep["next_pack"] == "244"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Governance Index Preview layer"
    assert prep["save_batch"] == "241-245"
    assert prep["save_after_pack"] == 245
    assert prep["safe_to_continue"] is True


def test_pack_243_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-governance-note-draft-v243.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-governance-note-draft-v243.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "243"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["tower_sublayer"] == "Governance Index Preview layer"
