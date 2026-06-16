"""
SEARCHABLE LABEL: TOWER_PACK_289_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_NOTE_VERSION_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_289_evidence_note_version_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    assert payload["pack"] == "289"
    assert payload["pack_number"] == 289
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-note-version-v289.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"

    assert payload["source_pack"] == "288"
    assert payload["source_closed_batch"] == "281-285"
    assert payload["save_batch"] == "286-290"
    assert payload["save_after_pack"] == 290
    assert payload["next_pack"] == "290"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_290"] is True
    assert payload["prepare_pack_290_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_batch_close_readiness"]["pack"] == "290"


def test_pack_289_evidence_note_version_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    summary = payload["handoff_policy_route_audit_evidence_note_version_summary"]

    assert summary["source_note_draft_count"] >= 11
    assert summary["version_card_count"] >= 11
    assert summary["version_field_count"] >= 154
    assert summary["version_action_count"] >= 231
    assert summary["version_checkpoint_count"] >= 8

    assert summary["enabled_action_count"] >= 11
    assert summary["blocked_action_count"] >= 220
    assert summary["redacted_field_count"] >= 22
    assert summary["editable_field_count"] >= 44

    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_pointer_only"] is True
    assert summary["all_cards_no_writes"] is True
    assert summary["all_cards_non_executable"] is True
    assert summary["all_cards_no_raw_evidence"] is True
    assert summary["all_fields_no_writes"] is True
    assert summary["all_fields_no_raw_evidence"] is True
    assert summary["all_actions_safe"] is True
    assert summary["all_checkpoints_passed"] is True
    assert summary["all_checkpoints_no_writes"] is True
    assert summary["evidence_note_version_ready"] is True

    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_note_version_save_enabled"] is False
    assert summary["real_note_version_restore_enabled"] is False
    assert summary["real_note_version_apply_enabled"] is False
    assert summary["real_note_version_delete_enabled"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_save_enabled"] is False
    assert summary["real_note_submit_enabled"] is False
    assert summary["real_note_delete_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_audit_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_289_cards_fields_actions_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    cards = payload["handoff_policy_route_audit_evidence_note_version_cards"]
    fields = payload["handoff_policy_route_audit_evidence_note_version_fields"]
    actions = payload["handoff_policy_route_audit_evidence_note_version_actions"]
    checkpoints = payload["handoff_policy_route_audit_evidence_note_version_checkpoints"]

    assert cards
    assert fields
    assert actions
    assert checkpoints

    assert all(card["version_mode"] == "preview_only" for card in cards)
    assert all(card["pointer_only"] is True for card in cards)
    assert all(card["writes_state"] is False for card in cards)
    assert all(card["executable"] is False for card in cards)
    assert all(card["raw_evidence_visible"] is False for card in cards)

    redactions = {field["redaction_state"] for field in fields}
    assert "redacted_pointer_only" in redactions
    assert "safe_preview" in redactions
    assert all(field["writes_state"] is False for field in fields)
    assert all(field["raw_evidence_visible"] is False for field in fields)

    preview_actions = [action for action in actions if action["result"] == "preview_allowed"]
    blocked_actions = [action for action in actions if action["result"] == "blocked_preview_only"]

    assert len(preview_actions) >= 11
    assert all(action["enabled"] is True for action in preview_actions)
    assert len(blocked_actions) >= 220
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_289_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_note_version_write"] is True
    assert safety["no_real_note_version_save"] is True
    assert safety["no_real_note_version_restore"] is True
    assert safety["no_real_note_version_apply"] is True
    assert safety["no_real_note_version_delete"] is True
    assert safety["no_real_note_write"] is True
    assert safety["no_real_note_save"] is True
    assert safety["no_real_note_submit"] is True
    assert safety["no_real_note_delete"] is True
    assert safety["no_real_evidence_write"] is True
    assert safety["no_real_evidence_export"] is True
    assert safety["no_real_evidence_reveal"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_audit_write"] is True
    assert safety["no_real_policy_write"] is True
    assert safety["no_real_route_change"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_registry_write"] is True
    assert safety["no_real_clearance_write"] is True
    assert safety["no_real_billing_write"] is True
    assert safety["no_real_receipt_write"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True
    assert safety["ob_ui_not_built_in_tower_pack"] is True
    assert safety["teller_ui_not_built_in_tower_pack"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_289_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_preview()

    assert third["status"] == "ready"


def test_pack_289_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_note_version_v289")

    bridge = mod.build_pack_289_status_bridge()
    assert bridge["pack"] == "289"
    assert bridge["pack_number"] == 289
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
    assert bridge["source_pack"] == "288"
    assert bridge["source_closed_batch"] == "281-285"
    assert bridge["save_batch"] == "286-290"
    assert bridge["save_after_pack"] == 290
    assert bridge["next_pack"] == "290"
    assert bridge["version_card_count"] >= 11
    assert bridge["version_field_count"] >= 154
    assert bridge["version_action_count"] >= 231
    assert bridge["evidence_note_version_ready"] is True
    assert bridge["safe_to_continue_to_pack_290"] is True

    prep = mod.prepare_pack_290_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_batch_close_readiness()
    assert prep["ready"] is True
    assert prep["next_pack"] == "290"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
    assert prep["source_closed_batch"] == "281-285"
    assert prep["save_batch"] == "286-290"
    assert prep["save_after_pack"] == 290
    assert prep["safe_to_continue"] is True


def test_pack_289_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-note-version-v289.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-note-version-v289.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "289"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence layer"
        assert data["source_closed_batch"] == "281-285"
        assert data["save_batch"] == "286-290"
