"""
SEARCHABLE LABEL: TOWER_PACK_219C_RECEIPT_CHAIN_SAVED_VIEW_COMPARE_FILTER_NAVIGATION_PREVIEW_TESTS
"""

from __future__ import annotations

import importlib


def test_pack_219c_compare_filter_navigation_contract_ready():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")
    payload = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    assert payload["pack"] == "219C"
    assert payload["pack_name"] == "Receipt Chain Saved View Compare Filter Navigation Preview"
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json"

    assert payload["cached"] is True
    assert payload["non_recursive"] is True
    assert payload["simulation_only"] is True
    assert payload["preview_only"] is True

    assert payload["source_pack"] == "219B"
    assert payload["source_status"] == "ready"
    assert payload["source_readiness"] == 100
    assert payload["source_safe_to_continue"] is True

    summary = payload["compare_filter_navigation_summary"]
    assert summary["filter_preset_count"] >= 6
    assert summary["navigation_lane_count"] >= 6
    assert summary["filter_result_preview_count"] >= 10
    assert summary["source_compare_pair_count"] >= 6
    assert summary["source_compare_row_count"] >= 12
    assert summary["enabled_filter_count"] >= 6
    assert summary["saved_filter_count"] == 0
    assert summary["preference_write_enabled"] is False
    assert summary["filter_apply_enabled"] is False
    assert summary["filter_save_enabled"] is False
    assert summary["filter_delete_enabled"] is False
    assert summary["raw_evidence_visible"] is False
    assert summary["real_action_execution_enabled"] is False

    assert payload["safe_to_continue_to_pack_220"] is True
    assert payload["prepare_pack_220_saved_view_batch_close_readiness"]["pack"] == "220"


def test_pack_219c_filter_controls_are_preview_only():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")
    payload = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    controls = payload["filter_controls"]

    assert controls["filter_selector_enabled"] is True
    assert controls["filter_preview_button_enabled"] is True
    assert controls["filter_apply_button_visible"] is True
    assert controls["filter_apply_button_enabled"] is False
    assert controls["save_filter_button_visible"] is True
    assert controls["save_filter_button_enabled"] is False
    assert controls["delete_filter_button_visible"] is True
    assert controls["delete_filter_button_enabled"] is False
    assert controls["remember_navigation_button_visible"] is True
    assert controls["remember_navigation_button_enabled"] is False
    assert controls["export_filtered_compare_button_visible"] is True
    assert controls["export_filtered_compare_button_enabled"] is False
    assert controls["control_mode"] == "preview_only"

    blocked = payload["blocked_action_matrix"]
    assert blocked
    assert all(row["allowed"] is False for row in blocked)
    assert all(row["result"] == "blocked_preview_only" for row in blocked)


def test_pack_219c_filter_presets_results_and_navigation_are_safe():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")
    payload = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    presets = payload["filter_presets"]
    lanes = payload["navigation_lanes"]
    results = payload["filter_result_previews"]

    assert presets
    assert lanes
    assert results

    assert all(item["saved_to_preferences"] is False for item in presets)
    assert all(item["executable"] is False for item in presets)
    assert all(item["action_mode"] == "view_only" for item in lanes)
    assert all(item["writes_preferences"] is False for item in lanes)
    assert all(item["raw_evidence_visible"] is False for item in results)
    assert all(item["executable"] is False for item in results)

    filter_ids = {item["filter_id"] for item in presets}
    result_filter_ids = {item["filter_id"] for item in results}
    assert result_filter_ids.issubset(filter_ids)

    labels = {item["label"] for item in presets}
    assert "High Severity Changes" in labels
    assert "Redacted Boundaries" in labels
    assert "Safety Control Changes" in labels
    assert "Navigation Changes" in labels
    assert "Owner Note Changes" in labels


def test_pack_219c_safety_invariants():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")
    payload = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    safety = payload["safety_invariants"]

    assert safety["no_real_compare_filter_save"] is True
    assert safety["no_real_compare_filter_apply"] is True
    assert safety["no_real_compare_filter_delete"] is True
    assert safety["no_real_compare_navigation_preference_write"] is True
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
    assert safety["all_filter_presets_non_executable"] is True
    assert safety["all_filter_results_non_executable"] is True
    assert safety["all_navigation_lanes_view_only"] is True
    assert safety["cached_non_recursive_builder"] is True


def test_pack_219c_public_builder_returns_defensive_copy():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")

    first = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()
    second = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    assert first == second
    assert first is not second

    first["status"] = "mutated_by_test"
    third = mod.build_receipt_chain_saved_view_compare_filter_navigation_preview()

    assert third["status"] == "ready"


def test_pack_219c_status_bridge_and_next_prep():
    mod = importlib.import_module("tower.receipt_chain_saved_view_compare_filter_navigation_v219c")

    bridge = mod.build_pack_219c_status_bridge()
    assert bridge["pack"] == "219C"
    assert bridge["status"] == "ready"
    assert bridge["readiness"] == 100
    assert bridge["preview_only"] is True
    assert bridge["source_pack"] == "219B"
    assert bridge["source_status"] == "ready"
    assert bridge["filter_preset_count"] >= 6
    assert bridge["navigation_lane_count"] >= 6
    assert bridge["filter_result_preview_count"] >= 10
    assert bridge["safe_to_continue_to_pack_220"] is True

    prep = mod.prepare_pack_220_saved_view_batch_close_readiness()
    assert prep["ready"] is True
    assert prep["next_pack"] == "220"
    assert prep["mode"] == "simulated_preview_only"
    assert prep["save_batch"] == "216-220"
    assert prep["save_after_pack"] == 220
    assert prep["safe_to_continue"] is True


def test_pack_219c_endpoint_is_registered_if_app_imports():
    import web.app as web_app

    app = getattr(web_app, "app", None)
    assert app is not None

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json" in rules

    client = app.test_client()
    response = client.get("/tower/receipt-chain-saved-view-compare-filter-navigation-v219c.json")

    assert response.status_code in {200, 302, 401, 403}

    if response.status_code == 200:
        data = response.get_json()
        assert data["pack"] == "219C"
        assert data["status"] == "ready"
        assert data["readiness"] == 100
        assert data["preview_only"] is True
