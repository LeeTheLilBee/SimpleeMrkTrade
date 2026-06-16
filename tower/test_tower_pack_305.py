"""
SEARCHABLE LABEL: TOWER_PACK_305_HANDOFF_POLICY_ROUTE_ENFORCEMENT_FINAL_HANDOFF_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_305_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_v305")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()

    assert payload["pack"] == "305"
    assert payload["pack_number"] == 305
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-handoff-batch-close-readiness-v305.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Final Handoff layer"

    assert payload["source_closed_batch"] == "296-300"
    assert payload["save_batch"] == "301-305"
    assert payload["save_after_pack"] == 305
    assert payload["next_batch"] == "306-310"
    assert payload["next_pack"] == "306"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["safe_to_push_packs_301_to_305"] is True
    assert payload["safe_to_continue_to_pack_306"] is True
    assert payload["prepare_pack_306_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_index"]["pack"] == "306"


def test_pack_305_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_v305")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()

    for pack in ["301", "302", "303", "304"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True

    summary = payload["final_handoff_batch_close_summary"]

    assert summary["source_closed_batch"] == "296-300"
    assert summary["save_batch"] == "301-305"
    assert summary["save_after_pack"] == 305
    assert summary["next_batch"] == "306-310"
    assert summary["next_pack"] == "306"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 14
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
    assert summary["final_handoff_batch_ready_to_push"] is True

    assert summary["real_final_handoff_execute_enabled"] is False
    assert summary["real_final_handoff_write_enabled"] is False
    assert summary["real_final_handoff_apply_enabled"] is False
    assert summary["real_final_handoff_transfer_enabled"] is False
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


def test_pack_305_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_v305")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()

    manifest = payload["final_handoff_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_index_v301.py",
        "tower/test_tower_pack_301.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_detail_drawer_v302.py",
        "tower/test_tower_pack_302.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_note_draft_v303.py",
        "tower/test_tower_pack_303.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_note_version_v304.py",
        "tower/test_tower_pack_304.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_v305.py",
        "tower/test_tower_pack_305.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_305_status_bridge()
    assert bridge["pack"] == "305"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["final_handoff_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_301_to_305"] is True
    assert bridge["safe_to_continue_to_pack_306"] is True

    prep = mod.prepare_pack_306_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "306"
    assert prep["closed_batch"] == "301-305"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-handoff-batch-close-readiness-v305.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-final-handoff-batch-close-readiness-v305.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "305"
        assert data["status"] == "ready"
        assert data["safe_to_push_packs_301_to_305"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_final_handoff_batch_close_readiness_preview()
    assert third["status"] == "ready"
