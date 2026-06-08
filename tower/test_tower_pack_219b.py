"""
SEARCHABLE LABEL: TOWER_PACK_219B_RECEIPT_CHAIN_SAVED_VIEW_VERSION_COMPARE_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_219b_version_compare_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_version_compare_v219b")
    payload = mod.build_receipt_chain_saved_view_version_compare_preview()

    assert payload["pack"] == "219B"
    assert payload["pack_name"] == "Receipt Chain Saved View Version Compare Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-version-compare-v219b.json"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "219A"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    summary = payload["version_compare_summary"]
    assert summary["compare_pair_count"] >= 6
    assert summary["compare_row_count"] >= 12
    assert summary["summary_card_count"] >= 6
    assert summary["redacted_row_count"] >= 3
    assert summary["high_severity_row_count"] >= 3

    assert payload["safe_to_continue_to_pack_219C"] is True
    assert payload["prepare_pack_219C_saved_view_compare_filter_navigation"]["pack"] == "219C"


def test_pack_219b_blocks_restore_revert_export_and_mutations():
    mod = importlib.import_module("tower.receipt_chain_saved_view_version_compare_v219b")
    payload = mod.build_receipt_chain_saved_view_version_compare_preview()

    summary = payload["version_compare_summary"]
    assert summary["restore_enabled"] is False
    assert summary["revert_enabled"] is False
    assert summary["export_enabled"] is False
    assert summary["apply_enabled"] is False
    assert summary["delete_enabled"] is False
    assert summary["raw_evidence_visible"] is False

    controls = payload["compare_controls"]
    assert controls["left_version_selector_enabled"] is True
    assert controls["right_version_selector_enabled"] is True
    assert controls["compare_button_enabled"] is True
    assert controls["restore_left_button_visible"] is True
    assert controls["restore_left_button_enabled"] is False
    assert controls["restore_right_button_visible"] is True
    assert controls["restore_right_button_enabled"] is False
    assert controls["revert_button_visible"] is True
    assert controls["revert_button_enabled"] is False
    assert controls["export_compare_button_visible"] is True
    assert controls["export_compare_button_enabled"] is False

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_219b_compare_rows_and_pairs_are_safe_preview_only():
    mod = importlib.import_module("tower.receipt_chain_saved_view_version_compare_v219b")
    payload = mod.build_receipt_chain_saved_view_version_compare_preview()

    pairs = payload["compare_pairs"]
    rows = payload["compare_rows"]
    rows_by_pair = payload["compare_rows_by_pair"]

    assert pairs
    assert rows
    assert rows_by_pair

    assert all(pair["executable"] is False for pair in pairs)
    assert all(pair["raw_evidence_visible"] is False for pair in pairs)
    assert all(row["executable"] is False for row in rows)

    pair_ids = {pair["compare_pair_id"] for pair in pairs}
    assert set(rows_by_pair).issubset(pair_ids)

    redacted_states = {row["redaction_state"] for row in rows}
    assert "redacted_pointer_only" in redacted_states
    assert "redacted_summary_only" in redacted_states
    assert "safe_preview" in redacted_states

    severities = {row["severity"] for row in rows}
    assert {"low", "medium", "high"}.issubset(severities)


def test_pack_219b_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_version_compare_v219b")

    first = mod.build_receipt_chain_saved_view_version_compare_preview()
    second = mod.build_receipt_chain_saved_view_version_compare_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_version_compare_preview()

    assert third["status"] == "ready"


def test_pack_219b_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_version_compare_v219b")

    bridge = mod.build_pack_219b_status_bridge()
    assert bridge["pack"] == "219B"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["source_pack"] == "219A"
    assert bridge["source_status"] == "ready"
    assert bridge["compare_pair_count"] >= 6
    assert bridge["compare_row_count"] >= 12
    assert bridge["summary_card_count"] >= 6
    assert bridge["safe_to_continue_to_pack_219C"] is True

    prep = mod.prepare_pack_219C_saved_view_compare_filter_navigation()
    assert prep["ready"] is True
    assert prep["next_pack"] == "219C"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["safe_to_continue"] is True


def test_pack_219b_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-version-compare-v219b.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-version-compare-v219b.json")

    # Guarded Tower routes may deny unauthenticated test clients.
    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "219B"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
