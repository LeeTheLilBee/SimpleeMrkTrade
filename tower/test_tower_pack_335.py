"""
SEARCHABLE LABEL: TOWER_PACK_335_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_ARCHIVE_RETRIEVAL_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_335_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_v335")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()

    assert payload["pack"] == "335"
    assert payload["pack_number"] == 335
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-archive-retrieval-batch-close-readiness-v335.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Archive Retrieval layer"
    assert payload["source_closed_batch"] == "326-330"
    assert payload["save_batch"] == "331-335"
    assert payload["save_after_pack"] == 335
    assert payload["next_batch"] == "336-340"
    assert payload["next_pack"] == "336"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["retrieval_preview_only"] is True
    assert payload["safe_to_push_packs_331_to_335"] is True
    assert payload["safe_to_continue_to_pack_336"] is True
    assert payload["prepare_pack_336_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index"]["pack"] == "336"


def test_pack_335_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_v335")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()

    for pack in ["331", "332", "333", "334"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True
        assert payload["source_packs"][pack]["archive_preview_only"] is True
        assert payload["source_packs"][pack]["retrieval_preview_only"] is True

    summary = payload["owner_acceptance_archive_retrieval_batch_close_summary"]

    assert summary["source_closed_batch"] == "326-330"
    assert summary["save_batch"] == "331-335"
    assert summary["save_after_pack"] == 335
    assert summary["next_batch"] == "336-340"
    assert summary["next_pack"] == "336"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 16
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_archive_preview_only"] is True
    assert summary["all_cards_retrieval_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["owner_acceptance_archive_retrieval_batch_ready_to_push"] is True

    assert summary["real_owner_acceptance_archive_retrieval_execute_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_write_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_apply_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_restore_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_delete_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_purge_enabled"] is False
    assert summary["real_owner_acceptance_archive_retrieval_export_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["real_archive_restore_enabled"] is False
    assert summary["real_archive_delete_enabled"] is False
    assert summary["real_archive_purge_enabled"] is False
    assert summary["real_archive_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_335_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_v335")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_archive_retrieval_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_index_v331.py",
        "tower/test_tower_pack_331.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_detail_drawer_v332.py",
        "tower/test_tower_pack_332.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_note_draft_v333.py",
        "tower/test_tower_pack_333.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_note_version_v334.py",
        "tower/test_tower_pack_334.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_v335.py",
        "tower/test_tower_pack_335.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_335_status_bridge()
    assert bridge["pack"] == "335"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_archive_retrieval_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_331_to_335"] is True
    assert bridge["safe_to_continue_to_pack_336"] is True

    prep = mod.prepare_pack_336_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_retrieval_receipt_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "336"
    assert prep["closed_batch"] == "331-335"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-archive-retrieval-batch-close-readiness-v335.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-archive-retrieval-batch-close-readiness-v335.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "335"
        assert data["status"] == "ready"
        assert data["retrieval_preview_only"] is True
        assert data["safe_to_push_packs_331_to_335"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_archive_retrieval_batch_close_readiness_preview()
    assert third["status"] == "ready"
