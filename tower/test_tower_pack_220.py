"""
SEARCHABLE LABEL: TOWER_PACK_220_RECEIPT_CHAIN_SAVED_VIEW_BATCH_CLOSE_READINESS_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_220_batch_close_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")
    payload = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    assert payload["pack"] == "220"
    assert payload["pack_number"] == 220
    assert payload["pack_name"] == "Receipt Chain Saved View Batch Close Readiness Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-batch-close-readiness-v220.json"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["save_batch"] == "216-220"
    assert payload["save_after_pack"] == 220
    assert payload["source_pack"] == "219C"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    assert payload["safe_to_push_packs_216_to_220"] is True
    assert payload["safe_to_continue_to_pack_221"] is True
    assert payload["prepare_pack_221_receipt_chain_saved_view_owner_review_queue"]["pack"] == "221"


def test_pack_220_batch_summary_ready_to_save():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")
    payload = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    summary = payload["batch_close_summary"]

    assert summary["save_batch"] == "216-220"
    assert summary["save_after_pack"] == 220
    assert summary["pack_card_count"] >= 7
    assert summary["batch_close_check_count"] >= 8
    assert summary["save_manifest_preview_count"] >= 9
    assert summary["all_cards_ready"] is True
    assert summary["all_cards_preview_only"] is True
    assert summary["all_cards_cached"] is True
    assert summary["all_cards_non_recursive"] is True
    assert summary["all_checks_passed"] is True
    assert summary["all_checks_no_writes"] is True
    assert summary["batch_ready_to_save"] is True

    assert summary["real_batch_close_write_enabled"] is False
    assert summary["real_saved_view_mutation_enabled"] is False
    assert summary["real_archive_write_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False


def test_pack_220_pack_cards_and_save_manifest():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")
    payload = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    cards = payload["batch_pack_cards"]
    manifest = payload["save_manifest_preview"]

    packs = {card["pack"] for card in cards}
    assert {"216", "217", "218", "219A", "219B", "219C", "220"}.issubset(packs)

    assert all(card["status"] == "ready" for card in cards)
    assert all(card["readiness"] == 100 for card in cards)
    assert all(card["preview_only"] is True for card in cards)
    assert all(card["cached"] is True for card in cards)
    assert all(card["non_recursive"] is True for card in cards)
    assert all(card["safe_to_continue"] is True for card in cards)

    manifest_paths = {row["path"] for row in manifest}
    expected_paths = {
        "tower/receipt_chain_saved_view_history_v219a.py",
        "tower/test_tower_pack_219a.py",
        "tower/receipt_chain_saved_view_version_compare_v219b.py",
        "tower/test_tower_pack_219b.py",
        "tower/receipt_chain_saved_view_compare_filter_navigation_v219c.py",
        "tower/test_tower_pack_219c.py",
        "tower/receipt_chain_saved_view_batch_close_readiness_v220.py",
        "tower/test_tower_pack_220.py",
        "web/app.py",
    }

    assert expected_paths.issubset(manifest_paths)
    assert all(row["include_in_commit"] is True for row in manifest)


def test_pack_220_safety_invariants_and_blocked_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")
    payload = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_batch_close_write"] is True
    assert safety["no_real_saved_view_restore"] is True
    assert safety["no_real_saved_view_revert"] is True
    assert safety["no_real_saved_view_write"] is True
    assert safety["no_real_saved_view_edit"] is True
    assert safety["no_real_saved_view_delete"] is True
    assert safety["no_real_saved_view_apply"] is True
    assert safety["no_real_saved_view_export"] is True
    assert safety["no_real_compare_filter_save"] is True
    assert safety["no_real_compare_filter_apply"] is True
    assert safety["no_real_compare_filter_delete"] is True
    assert safety["no_real_user_preference_write"] is True
    assert safety["no_archive_write"] is True
    assert safety["no_raw_evidence_reveal"] is True
    assert safety["no_real_action_execution"] is True
    assert safety["cached_non_recursive_builder"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_220_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")

    first = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()
    second = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_batch_close_readiness_preview()

    assert third["status"] == "ready"


def test_pack_220_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_batch_close_readiness_v220")

    bridge = mod.build_pack_220_status_bridge()
    assert bridge["pack"] == "220"
    assert bridge["pack_number"] == 220
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["save_batch"] == "216-220"
    assert bridge["save_after_pack"] == 220
    assert bridge["batch_ready_to_save"] is True
    assert bridge["safe_to_push_packs_216_to_220"] is True
    assert bridge["safe_to_continue_to_pack_221"] is True

    prep = mod.prepare_pack_221_receipt_chain_saved_view_owner_review_queue()
    assert prep["ready"] is True
    assert prep["next_pack"] == "221"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["next_batch"] == "221-225"
    assert prep["safe_to_continue"] is True


def test_pack_220_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-batch-close-readiness-v220.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-batch-close-readiness-v220.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "220"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
        assert data["safe_to_push_packs_216_to_220"] is True
