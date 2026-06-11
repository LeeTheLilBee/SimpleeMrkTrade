"""
SEARCHABLE LABEL: TOWER_PACK_240_RECEIPT_CHAIN_SAVED_VIEW_OWNER_REVIEW_CROSS_BATCH_CLOSE_READINESS_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_240_cross_batch_close_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    assert payload["pack"] == "240"
    assert payload["pack_number"] == 240
    assert payload["pack_name"] == "Receipt Chain Saved View Owner Review Cross-Batch Close Readiness Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-owner-review-cross-batch-close-readiness-v240.json"

    assert payload["tower_area"] == "The Tower"
    assert payload["tower_section"] == "Operational Containment"
    assert payload["tower_layer"] == "Receipt Chain Saved View Review Layer"

    assert payload["save_batch"] == "236-240"
    assert payload["save_after_pack"] == 240
    assert payload["next_batch"] == "241-245"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_packs"]["236"]["pack"] == "236"
    assert payload["source_packs"]["237"]["pack"] == "237"
    assert payload["source_packs"]["238"]["pack"] == "238"
    assert payload["source_packs"]["239"]["pack"] == "239"

    assert payload["safe_to_push_packs_236_to_240"] is True
    assert payload["safe_to_continue_to_pack_241"] is True
    assert payload["prepare_pack_241_receipt_chain_saved_view_owner_review_governance_index"]["pack"] == "241"


def test_pack_240_cross_batch_close_summary_ready_to_save():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    summary = payload["cross_batch_close_summary"]

    assert summary["save_batch"] == "236-240"
    assert summary["save_after_pack"] == 240
    assert summary["next_batch"] == "241-245"
    assert summary["pack_card_count"] >= 5
    assert summary["close_check_count"] >= 10
    assert summary["save_manifest_preview_count"] >= 11
    assert summary["transition_preview_count"] >= 2
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
    assert summary["cross_batch_ready_to_save"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_cross_batch_note_version_write_enabled"] is False
    assert summary["real_cross_batch_note_write_enabled"] is False
    assert summary["real_cross_batch_index_write_enabled"] is False
    assert summary["real_cross_batch_link_write_enabled"] is False
    assert summary["real_cross_batch_status_write_enabled"] is False
    assert summary["real_review_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_240_cards_manifest_and_transitions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    cards = payload["cross_batch_close_pack_cards"]
    manifest = payload["cross_batch_save_manifest_preview"]
    transitions = payload["cross_batch_transition_previews"]

    packs = {card["pack"] for card in cards}
    assert {"236", "237", "238", "239", "240"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_owner_review_cross_batch_index_v236.py",
        "tower/test_tower_pack_236.py",
        "tower/receipt_chain_saved_view_owner_review_cross_batch_detail_drawer_v237.py",
        "tower/test_tower_pack_237.py",
        "tower/receipt_chain_saved_view_owner_review_cross_batch_note_draft_v238.py",
        "tower/test_tower_pack_238.py",
        "tower/receipt_chain_saved_view_owner_review_cross_batch_note_version_v239.py",
        "tower/test_tower_pack_239.py",
        "tower/receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240.py",
        "tower/test_tower_pack_240.py",
        "web/app.py",
    }

    assert expected_paths.issubset(manifest_paths)

    include_paths = {row["path"] for row in manifest if row["include_in_commit"] is True}
    assert expected_paths == include_paths

    assert transitions
    assert all(row["transition_mode"] == "preview_only" for row in transitions)
    assert all(row["writes_state"] is False for row in transitions)
    assert all(row["safe_to_continue"] is True for row in transitions)


def test_pack_240_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")
    payload = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_cross_batch_note_version_write"] is True
    assert safety["no_real_cross_batch_note_version_restore"] is True
    assert safety["no_real_cross_batch_note_version_apply"] is True
    assert safety["no_real_cross_batch_note_write"] is True
    assert safety["no_real_cross_batch_note_save"] is True
    assert safety["no_real_cross_batch_note_submit"] is True
    assert safety["no_real_cross_batch_note_delete"] is True
    assert safety["no_real_cross_batch_detail_state_write"] is True
    assert safety["no_real_cross_batch_index_write"] is True
    assert safety["no_real_cross_batch_link_write"] is True
    assert safety["no_real_cross_batch_status_write"] is True
    assert safety["no_real_cross_batch_checkpoint_write"] is True
    assert safety["no_real_continuity_write"] is True
    assert safety["no_real_followup_write"] is True
    assert safety["no_real_owner_review_write"] is True
    assert safety["no_real_owner_review_approve"] is True
    assert safety["no_real_owner_review_deny"] is True
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


def test_pack_240_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")

    first = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_owner_review_cross_batch_close_readiness_preview()

    assert third["status"] == "ready"


def test_pack_240_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_owner_review_cross_batch_close_readiness_v240")

    bridge = mod.build_pack_240_status_bridge()
    assert bridge["pack"] == "240"
    assert bridge["pack_number"] == 240
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["tower_section"] == "Operational Containment"
    assert bridge["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert bridge["save_batch"] == "236-240"
    assert bridge["save_after_pack"] == 240
    assert bridge["next_batch"] == "241-245"
    assert bridge["cross_batch_ready_to_save"] is True
    assert bridge["safe_to_push_packs_236_to_240"] is True
    assert bridge["safe_to_continue_to_pack_241"] is True

    prep = mod.prepare_pack_241_receipt_chain_saved_view_owner_review_governance_index()
    assert prep["ready"] is True
    assert prep["next_pack"] == "241"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["tower_section"] == "Operational Containment"
    assert prep["tower_layer"] == "Receipt Chain Saved View Review Layer"
    assert prep["next_batch"] == "241-245"
    assert prep["safe_to_continue"] is True


def test_pack_240_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-owner-review-cross-batch-close-readiness-v240.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-owner-review-cross-batch-close-readiness-v240.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "240"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["tower_section"] == "Operational Containment"
        assert data["tower_layer"] == "Receipt Chain Saved View Review Layer"
        assert data["safe_to_push_packs_236_to_240"] is True
