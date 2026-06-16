"""
SEARCHABLE LABEL: TOWER_PACK_320_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_FINAL_REVIEW_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_320_contract_ready_and_save_deferred():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_v320")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()

    assert payload["pack"] == "320"
    assert payload["pack_number"] == 320
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-review-batch-close-readiness-v320.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Review layer"

    assert payload["source_closed_batch"] == "311-315"
    assert payload["current_batch"] == "316-320"
    assert payload["save_batch"] == "311-325"
    assert payload["save_after_pack"] == 325
    assert payload["save_now"] is False
    assert payload["next_batch"] == "321-325"
    assert payload["next_pack"] == "321"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["safe_to_push_packs_311_to_325_after_pack_325"] is False
    assert payload["safe_to_continue_to_pack_321"] is True
    assert payload["prepare_pack_321_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_index"]["pack"] == "321"


def test_pack_320_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_v320")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()

    for pack in ["316", "317", "318", "319"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    summary = payload["owner_acceptance_final_review_batch_close_summary"]

    assert summary["source_closed_batch"] == "311-315"
    assert summary["current_batch"] == "316-320"
    assert summary["save_batch"] == "311-325"
    assert summary["save_after_pack"] == 325
    assert summary["save_now"] is False
    assert summary["next_batch"] == "321-325"
    assert summary["next_pack"] == "321"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 13
    assert summary["deferred_save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["deferred_manifest_count"] >= 11

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
    assert summary["owner_acceptance_final_review_batch_ready_to_continue"] is True
    assert summary["safe_to_push_now"] is False

    assert summary["real_owner_acceptance_final_review_execute_enabled"] is False
    assert summary["real_owner_acceptance_final_review_write_enabled"] is False
    assert summary["real_owner_acceptance_final_review_apply_enabled"] is False
    assert summary["real_owner_acceptance_final_review_decide_enabled"] is False
    assert summary["real_owner_acceptance_final_review_sign_enabled"] is False
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


def test_pack_320_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_v320")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_final_review_deferred_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_index_v316.py",
        "tower/test_tower_pack_316.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_detail_drawer_v317.py",
        "tower/test_tower_pack_317.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_note_draft_v318.py",
        "tower/test_tower_pack_318.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_note_version_v319.py",
        "tower/test_tower_pack_319.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_v320.py",
        "tower/test_tower_pack_320.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_final_pack_325_commit"] is True for row in manifest)
    assert all(row["save_now"] is False for row in manifest)

    bridge = mod.build_pack_320_status_bridge()
    assert bridge["pack"] == "320"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["save_now"] is False
    assert bridge["owner_acceptance_final_review_batch_ready_to_continue"] is True
    assert bridge["safe_to_push_packs_311_to_325_after_pack_325"] is False
    assert bridge["safe_to_continue_to_pack_321"] is True

    prep = mod.prepare_pack_321_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "321"
    assert prep["closed_batch"] == "316-320"
    assert prep["save_batch"] == "311-325"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-review-batch-close-readiness-v320.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-review-batch-close-readiness-v320.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "320"
        assert data["status"] == "ready"
        assert data["save_now"] is False
        assert data["safe_to_continue_to_pack_321"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_review_batch_close_readiness_preview()
    assert third["status"] == "ready"
