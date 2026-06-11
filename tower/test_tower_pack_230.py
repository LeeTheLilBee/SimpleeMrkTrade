"""
SEARCHABLE LABEL: TOWER_PACK_230_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_FOLLOWUP_BATCH_CLOSE_READINESS_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_230_followup_batch_close_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")
    payload = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    assert payload["pack"] == "230"
    assert payload["pack_number"] == 230
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Follow-up Batch Close Readiness Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-followup-batch-close-readiness-v230.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "226-230"
    assert payload["save_after_pack"] == 230

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "229"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_push_packs_226_to_230"] is True
    assert payload["safe_to_continue_to_pack_231"] is True
    assert payload["prepare_pack_231_receipt_chain_saved_view_owner_review_continuity_queue"]["pack"] == "231"


def test_pack_230_followup_batch_summary_ready_to_save():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")
    payload = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    summary = payload["followup_batch_close_summary"]

    assert summary["save_batch"] == "226-230"
    assert summary["save_after_pack"] == 230
    assert summary["pack_card_count"] >= 5
    assert summary["batch_close_check_count"] >= 10
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["commit_manifest_count"] >= 11

    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["followup_batch_ready_to_save"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_followup_write_enabled"] is False
    assert summary["real_followup_note_write_enabled"] is False
    assert summary["real_followup_note_version_write_enabled"] is False
    assert summary["real_owner_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_230_pack_cards_and_save_manifest():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")
    payload = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    cards = payload["followup_batch_pack_cards"]
    manifest = payload["followup_batch_save_manifest_preview"]

    packs = {card["pack"] for card in cards}
    assert {"226", "227", "228", "229", "230"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_owner_review_followup_queue_v226.py",
        "tower/test_tower_pack_226.py",
        "tower/receipt_chain_saved_view_owner_review_followup_detail_drawer_v227.py",
        "tower/test_tower_pack_227.py",
        "tower/receipt_chain_saved_view_owner_review_followup_note_draft_v228.py",
        "tower/test_tower_pack_228.py",
        "tower/receipt_chain_saved_view_owner_review_followup_note_version_v229.py",
        "tower/test_tower_pack_229.py",
        "tower/receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230.py",
        "tower/test_tower_pack_230.py",
        "web/app.py",
    }

    assert expected_paths.issubset(manifest_paths)

    include_paths = {row["path"] for row in manifest if row["include_in_commit"] is True}
    assert expected_paths == include_paths


def test_pack_230_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")
    payload = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_followup_note_version_write"] is True
    assert safety["no_real_followup_note_version_restore"] is True
    assert safety["no_real_followup_note_write"] is True
    assert safety["no_real_followup_note_save"] is True
    assert safety["no_real_followup_note_submit"] is True
    assert safety["no_real_followup_note_delete"] is True
    assert safety["no_real_followup_assignment_write"] is True
    assert safety["no_real_followup_status_write"] is True
    assert safety["no_real_followup_due_date_write"] is True
    assert safety["no_real_followup_detail_state_write"] is True
    assert safety["no_real_followup_packet_export"] is True
    assert safety["no_real_owner_review_approve"] is True
    assert safety["no_real_owner_review_deny"] is True
    assert safety["no_real_owner_review_assign"] is True
    assert safety["no_real_owner_review_status_write"] is True
    assert safety["no_real_saved_view_restore"] is True
    assert safety["no_real_saved_view_revert"] is True
    assert safety["no_real_saved_view_write"] is True
    assert safety["no_real_saved_view_edit"] is True
    assert safety["no_real_saved_view_delete"] is True
    assert safety["no_real_saved_view_apply"] is True
    assert safety["no_real_saved_view_export"] is True
    assert safety["no_real_user_preference_write"] is True
    assert safety["no_archive_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_230_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")

    first = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_followup_batch_close_readiness_preview()

    assert third["status"] == "ready"


def test_pack_230_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_followup_batch_close_readiness_v230")

    bridge = mod.build_pack_230_status_bridge()
    assert bridge["pack"] == "230"
    assert bridge["pack_number"] == 230
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "226-230"
    assert bridge["save_after_pack"] == 230
    assert bridge["source_pack"] == "229"
    assert bridge["source_status"] == "ready"
    assert bridge["followup_batch_ready_to_save"] is True
    assert bridge["safe_to_push_packs_226_to_230"] is True
    assert bridge["safe_to_continue_to_pack_231"] is True

    prep = mod.prepare_pack_231_receipt_chain_saved_view_owner_review_continuity_queue()
    assert prep["ready"] is True
    assert prep["next_pack"] == "231"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["next_batch"] == "231-235"
    assert prep["safe_to_continue"] is True


def test_pack_230_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-followup-batch-close-readiness-v230.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-followup-batch-close-readiness-v230.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "230"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["safe_to_push_packs_226_to_230"] is True
