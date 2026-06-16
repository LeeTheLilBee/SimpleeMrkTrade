"""
SEARCHABLE LABEL: TOWER_PACK_298_HANDOFF_POLICY_ROUTE_ENFORCEMENT_FINAL_AUDIT_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_298_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_v298")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()

    assert payload["pack"] == "298"
    assert payload["pack_number"] == 298
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-audit-note-draft-v298.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Final Audit layer"

    assert payload["source_pack"] == "297"
    assert payload["source_closed_batch"] == "291-295"
    assert payload["save_batch"] == "296-300"
    assert payload["save_after_pack"] == 300
    assert payload["next_pack"] == "299"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["preview_only"] is True
    assert payload["simulation_only"] is True

    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_continue_to_pack_299"] is True
    assert payload["prepare_pack_299_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_version"]["pack"] == "299"


def test_pack_298_summary_safety_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_v298")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()
    summary = payload["final_audit_note_draft_summary"]

    assert summary["card_count"] >= 13
    assert summary["field_count"] >= 104
    assert summary["action_count"] >= 13
    assert summary["checkpoint_count"] >= 9
    assert summary["enabled_action_count"] >= 13
    assert summary["blocked_action_count"] >= 13
    assert summary["redacted_field_count"] >= 20

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
    assert summary["final_audit_note_draft_ready"] is True

    assert summary["real_final_audit_write_enabled"] is False
    assert summary["real_final_audit_apply_enabled"] is False
    assert summary["real_audit_override_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_evidence_transfer_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_note_write_enabled"] is False
    assert summary["real_note_version_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_298_payload_shapes_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_v298")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()

    cards = payload["final_audit_note_draft_cards"]
    fields = payload["final_audit_note_draft_fields"]
    actions = payload["final_audit_note_draft_actions"]
    checkpoints = payload["final_audit_note_draft_checkpoints"]

    assert cards
    assert fields
    assert actions
    assert checkpoints

    assert all(row["preview_only"] is True for row in cards)
    assert all(row["pointer_only"] is True for row in cards)
    assert all(row["writes_state"] is False for row in cards)
    assert all(row["executable"] is False for row in cards)
    assert all(row["raw_evidence_visible"] is False for row in cards)

    assert all(row["writes_state"] is False for row in fields)
    assert all(row["raw_evidence_visible"] is False for row in fields)

    preview_actions = [row for row in actions if row["result"] == "preview_allowed"]
    blocked_actions = [row for row in actions if row["result"] == "blocked_preview_only"]
    assert preview_actions
    assert blocked_actions
    assert all(row["enabled"] is True for row in preview_actions)
    assert all(row["enabled"] is False for row in blocked_actions)

    assert all(row["passed"] is True for row in checkpoints)
    assert all(row["writes_state"] is False for row in checkpoints)

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-audit-note-draft-v298.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-audit-note-draft-v298.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "298"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["safe_to_continue_to_pack_299"] is True


def test_pack_298_bridge_prep_and_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_v298")

    bridge = mod.build_pack_298_status_bridge()
    assert bridge["pack"] == "298"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["card_count"] >= 13
    assert bridge["final_audit_note_draft_ready"] is True
    assert bridge["safe_to_continue_to_pack_299"] is True

    prep = mod.prepare_pack_299_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_version()
    assert prep["ready"] is True
    assert prep["next_pack"] == "299"
    assert prep["source_pack"] == "298"
    assert prep["safe_to_continue"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_note_draft_preview()
    assert third["status"] == "ready"
