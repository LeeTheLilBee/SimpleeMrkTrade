"""
SEARCHABLE LABEL: TOWER_PACK_295_HANDOFF_POLICY_ROUTE_ENFORCEMENT_AUDIT_EVIDENCE_HANDOFF_BATCH_CLOSE_READINESS_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_295_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()

    assert payload["pack"] == "295"
    assert payload["pack_number"] == 295
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-batch-close-readiness-v295.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Audit Evidence Handoff layer"

    assert payload["source_closed_batch"] == "286-290"
    assert payload["save_batch"] == "291-295"
    assert payload["save_after_pack"] == 295
    assert payload["next_batch"] == "296-300"
    assert payload["next_pack"] == "296"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["safe_to_push_packs_291_to_295"] is True
    assert payload["safe_to_continue_to_pack_296"] is True
    assert payload["prepare_pack_296_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_index"]["pack"] == "296"


def test_pack_295_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()

    for pack in ["291", "292", "293", "294"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    summary = payload["handoff_policy_route_audit_evidence_handoff_batch_close_summary"]

    assert summary["source_closed_batch"] == "286-290"
    assert summary["save_batch"] == "291-295"
    assert summary["save_after_pack"] == 295
    assert summary["next_batch"] == "296-300"
    assert summary["next_pack"] == "296"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 17
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["handoff_batch_ready_to_push"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_handoff_execute_enabled"] is False
    assert summary["real_handoff_write_enabled"] is False
    assert summary["real_handoff_transfer_enabled"] is False
    assert summary["real_handoff_note_write_enabled"] is False
    assert summary["real_handoff_note_version_write_enabled"] is False
    assert summary["real_handoff_note_version_restore_enabled"] is False
    assert summary["real_handoff_note_version_apply_enabled"] is False
    assert summary["real_handoff_note_version_delete_enabled"] is False
    assert summary["real_evidence_transfer_enabled"] is False
    assert summary["real_evidence_write_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_audit_write_enabled"] is False
    assert summary["real_policy_write_enabled"] is False
    assert summary["real_route_change_enabled"] is False
    assert summary["real_registry_write_enabled"] is False
    assert summary["real_clearance_write_enabled"] is False
    assert summary["real_billing_write_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_295_cards_checks_manifest_transitions_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()

    cards = payload["handoff_policy_route_audit_evidence_handoff_batch_pack_cards"]
    checks = payload["handoff_policy_route_audit_evidence_handoff_batch_close_checks"]
    manifest = payload["handoff_policy_route_audit_evidence_handoff_save_manifest_preview"]
    transitions = payload["handoff_policy_route_audit_evidence_handoff_batch_transitions"]

    packs = {card["pack"] for card in cards}
    assert {"291", "292", "293", "294", "295"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    assert all(check["passed"] is True for check in checks)
    assert all(check["writes_state"] is False for check in checks)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_index_v291.py",
        "tower/test_tower_pack_291.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_detail_drawer_v292.py",
        "tower/test_tower_pack_292.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_draft_v293.py",
        "tower/test_tower_pack_293.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_note_version_v294.py",
        "tower/test_tower_pack_294.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295.py",
        "tower/test_tower_pack_295.py",
        "web/app.py",
    }
    assert expected_paths.issubset(manifest_paths)
    assert all(row["include_in_commit"] is True for row in manifest)

    assert all(row["transition_mode"] == "preview_only" for row in transitions)
    assert all(row["writes_state"] is False for row in transitions)
    assert all(row["safe_to_continue"] is True for row in transitions)


def test_pack_295_safety_invariants_and_endpoint():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()

    safety = payload["safety_invariants"]
    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_handoff_execute"] is True
    assert safety["no_real_handoff_write"] is True
    assert safety["no_real_handoff_transfer"] is True
    assert safety["no_real_handoff_note_write"] is True
    assert safety["no_real_handoff_note_version_write"] is True
    assert safety["no_real_handoff_note_version_restore"] is True
    assert safety["no_real_handoff_note_version_apply"] is True
    assert safety["no_real_handoff_note_version_delete"] is True
    assert safety["no_real_evidence_transfer"] is True
    assert safety["no_real_evidence_write"] is True
    assert safety["no_real_evidence_reveal"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_audit_write"] is True
    assert safety["no_real_policy_write"] is True
    assert safety["no_real_route_change"] is True
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

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-batch-close-readiness-v295.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-audit-evidence-handoff-batch-close-readiness-v295.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "295"
        assert data["status"] == "ready"
        assert data["safe_to_push_packs_291_to_295"] is True
        assert data["safe_to_continue_to_pack_296"] is True


def test_pack_295_status_bridge_next_prep_and_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_v295")

    bridge = mod.build_pack_295_status_bridge()
    assert bridge["pack"] == "295"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["source_closed_batch"] == "286-290"
    assert bridge["save_batch"] == "291-295"
    assert bridge["save_after_pack"] == 295
    assert bridge["next_batch"] == "296-300"
    assert bridge["next_pack"] == "296"
    assert bridge["pack_card_count"] >= 5
    assert bridge["close_check_count"] >= 17
    assert bridge["save_manifest_preview_count"] >= 11
    assert bridge["handoff_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_291_to_295"] is True
    assert bridge["safe_to_continue_to_pack_296"] is True

    prep = mod.prepare_pack_296_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_audit_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "296"
    assert prep["source_pack"] == "295"
    assert prep["closed_batch"] == "291-295"
    assert prep["next_batch"] == "296-300"
    assert prep["save_after_pack"] == 300
    assert prep["safe_to_continue"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_audit_evidence_handoff_batch_close_readiness_preview()
    assert third["status"] == "ready"
