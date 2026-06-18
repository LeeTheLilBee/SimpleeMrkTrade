"""
SEARCHABLE LABEL: TOWER_PACK_395_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_FINAL_CLOSEOUT_ARCHIVE_VERIFICATION_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_395_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_v395")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()

    assert payload["pack"] == "395"
    assert payload["pack_number"] == 395
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-batch-close-readiness-v395.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Final Closeout Archive Verification layer"
    assert payload["source_closed_batch"] == "386-390"
    assert payload["save_batch"] == "391-395"
    assert payload["save_after_pack"] == 395
    assert payload["next_batch"] == "396-400"
    assert payload["next_pack"] == "396"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["archive_verification_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["safe_to_push_packs_391_to_395"] is True
    assert payload["safe_to_continue_to_pack_396"] is True
    assert payload["prepare_pack_396_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_final_index"]["pack"] == "396"


def test_pack_395_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_v395")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()

    for pack in ["391", "392", "393", "394"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True
        assert payload["source_packs"][pack]["archive_verification_preview_only"] is True

    summary = payload["owner_acceptance_final_closeout_archive_verification_batch_close_summary"]

    assert summary["source_closed_batch"] == "386-390"
    assert summary["save_batch"] == "391-395"
    assert summary["save_after_pack"] == 395
    assert summary["next_batch"] == "396-400"
    assert summary["next_pack"] == "396"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 23
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_archive_verification_preview_only"] is True
    assert summary["all_cards_archive_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["owner_acceptance_final_closeout_archive_verification_batch_ready_to_push"] is True

    assert summary["real_archive_verification_execute_enabled"] is False
    assert summary["real_archive_verification_pass_enabled"] is False
    assert summary["real_archive_verification_fail_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_archive_restore_enabled"] is False
    assert summary["real_archive_delete_enabled"] is False
    assert summary["real_archive_purge_enabled"] is False
    assert summary["real_archive_export_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_395_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_v395")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_final_closeout_archive_verification_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_index_v391.py",
        "tower/test_tower_pack_391.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_detail_drawer_v392.py",
        "tower/test_tower_pack_392.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_note_draft_v393.py",
        "tower/test_tower_pack_393.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_note_version_v394.py",
        "tower/test_tower_pack_394.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_v395.py",
        "tower/test_tower_pack_395.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_395_status_bridge()
    assert bridge["pack"] == "395"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_final_closeout_archive_verification_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_391_to_395"] is True
    assert bridge["safe_to_continue_to_pack_396"] is True

    prep = mod.prepare_pack_396_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_final_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "396"
    assert prep["closed_batch"] == "391-395"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-batch-close-readiness-v395.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-final-closeout-archive-verification-batch-close-readiness-v395.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "395"
        assert data["status"] == "ready"
        assert data["archive_verification_preview_only"] is True
        assert data["safe_to_push_packs_391_to_395"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_final_closeout_archive_verification_batch_close_readiness_preview()
    assert third["status"] == "ready"
