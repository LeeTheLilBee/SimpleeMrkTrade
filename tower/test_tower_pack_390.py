"""
SEARCHABLE LABEL: TOWER_PACK_390_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_FINAL_CLOSEOUT_ARCHIVE_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_390_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_v390")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()

    assert payload["pack"] == "390"
    assert payload["pack_number"] == 390
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-batch-close-readiness-v390.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Closeout Archive layer"
    assert payload["source_closed_batch"] == "366-385"
    assert payload["save_batch"] == "386-390"
    assert payload["save_after_pack"] == 390
    assert payload["next_batch"] == "391-395"
    assert payload["next_pack"] == "391"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["final_closeout_archive_preview_only"] is True
    assert payload["safe_to_push_packs_386_to_390"] is True
    assert payload["safe_to_continue_to_pack_391"] is True
    assert payload["prepare_pack_391_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index"]["pack"] == "391"


def test_pack_390_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_v390")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()

    for pack in ["386", "387", "388", "389"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True
        assert payload["source_packs"][pack]["archive_preview_only"] is True

    summary = payload["owner_acceptance_final_closeout_archive_batch_close_summary"]

    assert summary["source_closed_batch"] == "366-385"
    assert summary["save_batch"] == "386-390"
    assert summary["save_after_pack"] == 390
    assert summary["next_batch"] == "391-395"
    assert summary["next_pack"] == "391"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 27
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_archive_preview_only"] is True
    assert summary["all_cards_final_closeout_archive_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["owner_acceptance_final_closeout_archive_batch_ready_to_push"] is True

    assert summary["real_owner_acceptance_final_closeout_archive_execute_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_archive_write_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_archive_restore_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_archive_delete_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_archive_purge_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_archive_export_enabled"] is False
    assert summary["real_owner_acceptance_final_closeout_enabled"] is False
    assert summary["real_release_enabled"] is False
    assert summary["real_publish_enabled"] is False
    assert summary["real_sign_enabled"] is False
    assert summary["real_seal_enabled"] is False
    assert summary["real_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_390_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_v390")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_final_closeout_archive_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_index_v386.py",
        "tower/test_tower_pack_386.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_detail_drawer_v387.py",
        "tower/test_tower_pack_387.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_note_draft_v388.py",
        "tower/test_tower_pack_388.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_note_version_v389.py",
        "tower/test_tower_pack_389.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_v390.py",
        "tower/test_tower_pack_390.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_390_status_bridge()
    assert bridge["pack"] == "390"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_final_closeout_archive_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_386_to_390"] is True
    assert bridge["safe_to_continue_to_pack_391"] is True

    prep = mod.prepare_pack_391_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "391"
    assert prep["closed_batch"] == "386-390"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-batch-close-readiness-v390.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-batch-close-readiness-v390.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "390"
        assert data["status"] == "ready"
        assert data["archive_preview_only"] is True
        assert data["safe_to_push_packs_386_to_390"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_batch_close_readiness_preview()
    assert third["status"] == "ready"
