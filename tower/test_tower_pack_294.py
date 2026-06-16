"""
SEARCHABLE LABEL: TOWER_PACK_294_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_NOTE_VERSION_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_294_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()

    assert payload["pack"] == "294"
    assert payload["pack_number"] == 294
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-note-version-v294.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

    assert payload["source_pack"] == "293"
    assert payload["source_closed_batch"] == "286-290"
    assert payload["save_batch"] == "291-295"
    assert payload["save_after_pack"] == 295
    assert payload["next_pack"] == "295"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["preview_only"] is True
    assert payload["simulation_only"] is True
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_295"] is True
    assert payload["prepare_pack_295_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness"]["pack"] == "295"


def test_pack_294_summary_and_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()
    summary = payload["handoff_policy_route_audit_evidence_handoff_note_version_summary"]

    assert summary["source_note_draft_count"] >= 12
    assert summary["version_card_count"] >= 12
    assert summary["version_field_count"] >= 156
    assert summary["version_action_count"] >= 240
    assert summary["version_checkpoint_count"] >= 8
    assert summary["enabled_action_count"] >= 12
    assert summary["blocked_action_count"] >= 228
    assert summary["redacted_field_count"] >= 24
    assert summary["editable_field_count"] >= 24

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
    assert summary["handoff_note_version_ready"] is True

    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_handoff_note_version_write_enabled"] is False
    assert summary["real_handoff_note_version_save_enabled"] is False
    assert summary["real_handoff_note_version_restore_enabled"] is False
    assert summary["real_handoff_note_version_apply_enabled"] is False
    assert summary["real_handoff_note_version_delete_enabled"] is False
    assert summary["real_handoff_note_write_enabled"] is False
    assert summary["real_handoff_note_save_enabled"] is False
    assert summary["real_handoff_note_submit_enabled"] is False
    assert summary["real_handoff_note_delete_enabled"] is False
    assert summary["real_evidence_transfer_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_audit_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_294_cards_fields_actions_checkpoint_shapes():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()

    cards = payload["handoff_policy_route_audit_evidence_handoff_note_version_cards"]
    fields = payload["handoff_policy_route_audit_evidence_handoff_note_version_fields"]
    actions = payload["handoff_policy_route_audit_evidence_handoff_note_version_actions"]
    checkpoints = payload["handoff_policy_route_audit_evidence_handoff_note_version_checkpoints"]

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
    assert len(preview_actions) >= 12
    assert len(blocked_actions) >= 228
    assert all(action["enabled"] is True for action in preview_actions)
    assert all(action["enabled"] is False for action in blocked_actions)

    assert all(checkpoint["passed"] is True for checkpoint in checkpoints)
    assert all(checkpoint["writes_state"] is False for checkpoint in checkpoints)


def test_pack_294_status_bridge_next_prep_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294")

    bridge = mod.build_pack_294_status_bridge()
    assert bridge["pack"] == "294"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["version_card_count"] >= 12
    assert bridge["handoff_note_version_ready"] is True
    assert bridge["safe_to_continue_to_pack_295"] is True

    prep = mod.prepare_pack_295_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness()
    assert prep["ready"] is True
    assert prep["next_pack"] == "295"
    assert prep["source_pack"] == "294"
    assert prep["safe_to_continue"] is True

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-note-version-v294.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-note-version-v294.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "294"
        assert data["status"] == "ready"
        assert data["safe_to_continue_to_pack_295"] is True


def test_pack_294_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294")
    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_preview()
    assert third["status"] == "ready"
