"""
SEARCHABLE LABEL: TOWER_PACK_325_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_FINAL_LOCK_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_325_contract_ready_and_save_enabled():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_v325")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()

    assert payload["pack"] == "325"
    assert payload["pack_number"] == 325
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-lock-batch-close-readiness-v325.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Lock layer"

    assert payload["source_closed_batch"] == "316-320"
    assert payload["current_batch"] == "321-325"
    assert payload["save_batch"] == "311-325"
    assert payload["save_after_pack"] == 325
    assert payload["save_now"] is True
    assert payload["next_batch"] == "326-330"
    assert payload["next_pack"] == "326"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["safe_to_push_packs_311_to_325"] is True
    assert payload["safe_to_continue_to_pack_326"] is True
    assert payload["prepare_pack_326_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_index"]["pack"] == "326"


def test_pack_325_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_v325")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()

    for pack in ["321", "322", "323", "324"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    summary = payload["owner_acceptance_final_lock_batch_close_summary"]

    assert summary["source_closed_batch"] == "316-320"
    assert summary["current_batch"] == "321-325"
    assert summary["save_batch"] == "311-325"
    assert summary["save_after_pack"] == 325
    assert summary["save_now"] is True
    assert summary["next_batch"] == "326-330"
    assert summary["next_pack"] == "326"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 14
    assert summary["save_manifest_count"] >= 31
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 31

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
    assert summary["owner_acceptance_final_lock_batch_ready_to_push"] is True
    assert summary["safe_to_push_now"] is True

    assert summary["real_owner_acceptance_final_lock_execute_enabled"] is False
    assert summary["real_owner_acceptance_final_lock_write_enabled"] is False
    assert summary["real_owner_acceptance_final_lock_apply_enabled"] is False
    assert summary["real_owner_acceptance_final_lock_decide_enabled"] is False
    assert summary["real_owner_acceptance_final_lock_sign_enabled"] is False
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


def test_pack_325_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_v325")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_final_lock_save_manifest"]
    assert len(manifest) >= 31
    assert all(row["include_in_commit"] is True for row in manifest)
    assert all(row["save_now"] is True for row in manifest)

    expected_tail = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_index_v321.py",
        "tower/test_tower_pack_321.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_detail_drawer_v322.py",
        "tower/test_tower_pack_322.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_note_draft_v323.py",
        "tower/test_tower_pack_323.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_note_version_v324.py",
        "tower/test_tower_pack_324.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_v325.py",
        "tower/test_tower_pack_325.py",
        "web/app.py",
    }
    assert expected_tail.issubset({row["path"] for row in manifest})

    bridge = mod.build_pack_325_status_bridge()
    assert bridge["pack"] == "325"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["save_now"] is True
    assert bridge["owner_acceptance_final_lock_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_311_to_325"] is True
    assert bridge["safe_to_continue_to_pack_326"] is True

    prep = mod.prepare_pack_326_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "326"
    assert prep["closed_batch"] == "321-325"
    assert prep["save_batch"] == "311-325"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-lock-batch-close-readiness-v325.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-lock-batch-close-readiness-v325.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "325"
        assert data["status"] == "ready"
        assert data["save_now"] is True
        assert data["safe_to_push_packs_311_to_325"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_lock_batch_close_readiness_preview()
    assert third["status"] == "ready"
