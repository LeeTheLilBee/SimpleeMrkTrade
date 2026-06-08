"""
SEARCHABLE LABEL: TOWER_PACK_219A_RECEIPT_CHAIN_SAVED_VIEW_HISTORY_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_219a_history_preview_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_history_v219a")
    payload = mod.build_receipt_chain_saved_view_history_preview()

    assert payload["pack"] == "219A"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-history-v219a.json"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["saved_view_history_summary"]["history_event_count"] >= 6
    assert payload["saved_view_history_summary"]["version_card_count"] >= 6
    assert payload["saved_view_history_summary"]["field_change_preview_count"] >= 7

    assert payload["safe_to_continue_to_pack_219B"] is True
    assert payload["prepare_pack_219B_saved_view_version_compare"]["pack"] == "219B"


def test_pack_219a_blocks_real_mutation_actions():
    mod = importlib.import_module("tower.receipt_chain_saved_view_history_v219a")
    payload = mod.build_receipt_chain_saved_view_history_preview()

    invariants = payload["safety_invariants"]

    assert invariants["no_real_saved_view_write"] is True
    assert invariants["no_real_saved_view_edit"] is True
    assert invariants["no_real_saved_view_delete"] is True
    assert invariants["no_real_saved_view_apply"] is True
    assert invariants["no_real_saved_view_export"] is True
    assert invariants["no_real_user_preference_write"] is True
    assert invariants["no_archive_write"] is True
    assert invariants["no_raw_evidence_reveal"] is True
    assert invariants["no_real_action_execution"] is True
    assert invariants["cached_non_recursive_builder"] is True

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)

    restore = payload["restore_revert_simulation"]
    assert restore["restore_button_visible"] is True
    assert restore["restore_button_enabled"] is False
    assert restore["revert_button_visible"] is True
    assert restore["revert_button_enabled"] is False


def test_pack_219a_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_history_v219a")

    first = mod.build_receipt_chain_saved_view_history_preview()
    second = mod.build_receipt_chain_saved_view_history_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_history_preview()

    assert third["status"] == "ready"


def test_pack_219a_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_history_v219a")

    bridge = mod.build_pack_219a_status_bridge()
    assert bridge["pack"] == "219A"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["safe_to_continue_to_pack_219B"] is True

    prep = mod.prepare_pack_219B_saved_view_version_compare()
    assert prep["ready"] is True
    assert prep["next_pack"] == "219B"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["safe_to_continue"] is True


def test_pack_219a_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-history-v219a.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-history-v219a.json")

    # A guarded Tower route may deny unauthenticated test clients.
    # The contract here is: route exists, guard does not crash, and if allowed, returns Pack 219A JSON.
    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "219A"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
