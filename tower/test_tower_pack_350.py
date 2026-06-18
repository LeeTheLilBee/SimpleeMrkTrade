"""
SEARCHABLE LABEL: TOWER_PACK_350_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_RECEIPT_SEAL_VERIFICATION_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_350_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_v350")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()

    assert payload["pack"] == "350"
    assert payload["pack_number"] == 350
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-verification-batch-close-readiness-v350.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Receipt Seal Verification layer"
    assert payload["source_closed_batch"] == "341-345"
    assert payload["save_batch"] == "346-350"
    assert payload["save_after_pack"] == 350
    assert payload["next_batch"] == "351-355"
    assert payload["next_pack"] == "351"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["verification_preview_only"] is True
    assert payload["seal_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["retrieval_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["safe_to_push_packs_346_to_350"] is True
    assert payload["safe_to_continue_to_pack_351"] is True
    assert payload["prepare_pack_351_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_release_index"]["pack"] == "351"


def test_pack_350_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_v350")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()

    for pack in ["346", "347", "348", "349"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True
        assert payload["source_packs"][pack]["verification_preview_only"] is True

    summary = payload["owner_acceptance_receipt_seal_verification_batch_close_summary"]

    assert summary["source_closed_batch"] == "341-345"
    assert summary["save_batch"] == "346-350"
    assert summary["save_after_pack"] == 350
    assert summary["next_batch"] == "351-355"
    assert summary["next_pack"] == "351"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 21
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_verification_preview_only"] is True
    assert summary["all_cards_seal_preview_only"] is True
    assert summary["all_cards_receipt_preview_only"] is True
    assert summary["all_cards_retrieval_preview_only"] is True
    assert summary["all_cards_archive_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_cards_safe_to_continue"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["all_transitions_preview_only"] is True
    assert summary["all_transitions_no_writes"] is True
    assert summary["all_transitions_safe"] is True
    assert summary["owner_acceptance_receipt_seal_verification_batch_ready_to_push"] is True

    assert summary["real_owner_acceptance_receipt_seal_verification_execute_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_verification_write_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_verification_apply_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_verification_pass_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_verification_fail_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_verification_export_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_sign_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_seal_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_receipt_sign_enabled"] is False
    assert summary["real_receipt_seal_enabled"] is False
    assert summary["real_receipt_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_350_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_v350")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_receipt_seal_verification_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_index_v346.py",
        "tower/test_tower_pack_346.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_detail_drawer_v347.py",
        "tower/test_tower_pack_347.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_note_draft_v348.py",
        "tower/test_tower_pack_348.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_note_version_v349.py",
        "tower/test_tower_pack_349.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_v350.py",
        "tower/test_tower_pack_350.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_350_status_bridge()
    assert bridge["pack"] == "350"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_receipt_seal_verification_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_346_to_350"] is True
    assert bridge["safe_to_continue_to_pack_351"] is True

    prep = mod.prepare_pack_351_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_release_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "351"
    assert prep["closed_batch"] == "346-350"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-verification-batch-close-readiness-v350.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-verification-batch-close-readiness-v350.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "350"
        assert data["status"] == "ready"
        assert data["verification_preview_only"] is True
        assert data["safe_to_push_packs_346_to_350"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_batch_close_readiness_preview()
    assert third["status"] == "ready"
