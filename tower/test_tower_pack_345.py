"""
SEARCHABLE LABEL: TOWER_PACK_345_HANDOFF_POLICY_ROUTE_ENFORCEMENT_OWNER_ACCEPTANCE_RECEIPT_SEAL_BATCH_CLOSE_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_345_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_v345")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()

    assert payload["pack"] == "345"
    assert payload["pack_number"] == 345
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-batch-close-readiness-v345.json"
    assert payload["tower_sublayer"] == "Handoff Policy Route Enforcement Owner Acceptance Receipt Seal layer"
    assert payload["source_closed_batch"] == "336-340"
    assert payload["save_batch"] == "341-345"
    assert payload["save_after_pack"] == 345
    assert payload["next_batch"] == "346-350"
    assert payload["next_pack"] == "346"
    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True
    assert payload["seal_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["retrieval_preview_only"] is True
    assert payload["archive_preview_only"] is True
    assert payload["safe_to_push_packs_341_to_345"] is True
    assert payload["safe_to_continue_to_pack_346"] is True
    assert payload["prepare_pack_346_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_index"]["pack"] == "346"


def test_pack_345_source_packs_and_summary_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_v345")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()

    for pack in ["341", "342", "343", "344"]:
        assert payload["source_packs"][pack]["pack"] == pack
        assert payload["source_packs"][pack]["status"] == "ready"
        assert payload["source_packs"][pack]["readiness"] == 100
        assert payload["source_packs"][pack]["preview_only"] is True
        assert payload["source_packs"][pack]["seal_preview_only"] is True

    summary = payload["owner_acceptance_receipt_seal_batch_close_summary"]

    assert summary["source_closed_batch"] == "336-340"
    assert summary["save_batch"] == "341-345"
    assert summary["save_after_pack"] == 345
    assert summary["next_batch"] == "346-350"
    assert summary["next_pack"] == "346"

    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 19
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_count"] >= 6
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
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
    assert summary["owner_acceptance_receipt_seal_batch_ready_to_push"] is True

    assert summary["real_owner_acceptance_receipt_seal_execute_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_write_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_apply_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_sign_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_seal_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_export_enabled"] is False
    assert summary["real_owner_acceptance_receipt_seal_delete_enabled"] is False
    assert summary["real_receipt_write_enabled"] is False
    assert summary["real_receipt_sign_enabled"] is False
    assert summary["real_receipt_seal_enabled"] is False
    assert summary["real_receipt_export_enabled"] is False
    assert summary["real_evidence_reveal_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_345_manifest_endpoint_bridge_and_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_v345")
    payload = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()

    manifest = payload["owner_acceptance_receipt_seal_save_manifest_preview"]
    expected = {
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_index_v341.py",
        "tower/test_tower_pack_341.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_detail_drawer_v342.py",
        "tower/test_tower_pack_342.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_note_draft_v343.py",
        "tower/test_tower_pack_343.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_note_version_v344.py",
        "tower/test_tower_pack_344.py",
        "tower/receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_v345.py",
        "tower/test_tower_pack_345.py",
        "web/app.py",
    }
    assert expected.issubset({row["path"] for row in manifest})
    assert all(row["include_in_commit"] is True for row in manifest)

    bridge = mod.build_pack_345_status_bridge()
    assert bridge["pack"] == "345"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["owner_acceptance_receipt_seal_batch_ready_to_push"] is True
    assert bridge["safe_to_push_packs_341_to_345"] is True
    assert bridge["safe_to_continue_to_pack_346"] is True

    prep = mod.prepare_pack_346_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_verification_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "346"
    assert prep["closed_batch"] == "341-345"

    import web.app as web_app
    app = getattr(web_app, "app", None)
    assert app is not None
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-batch-close-readiness-v345.json" in rules

    response = app.test_client().get("/tower/receipt-chain-saved-view-owner-review-handoff-policy-route-enforcement-owner-acceptance-receipt-seal-batch-close-readiness-v345.json")
    assert response.status_code in {200, 302, 401, 403}
    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "345"
        assert data["status"] == "ready"
        assert data["seal_preview_only"] is True
        assert data["safe_to_push_packs_341_to_345"] is True

    first = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()
    assert first == second
    assert first is not second
    first["status"] = "mutated"
    third = mod.build_receipt_chain_saved_view_owner_review_handoff_policy_route_enforcement_owner_acceptance_receipt_seal_batch_close_readiness_preview()
    assert third["status"] == "ready"
