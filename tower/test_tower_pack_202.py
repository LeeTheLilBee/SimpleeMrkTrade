
"""
PACK 202 fast test - Receipt Chain Operational Handoff Saved Views /
Filter Presets Preview.

Uses short safe module:
    tower.receipt_chain_handoff_saved_views_v202
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_202_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_handoff_saved_views_v202")
    payload = mod.build_receipt_chain_handoff_saved_views_v202_payload(force_refresh=True)

    assert payload["pack_number"] == 202
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-handoff-saved-views-v202.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-operational-handoff-v201.json"

    required_true = [
        "simulated_only",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "selected_saved_view_preview_only",
        "operational_handoff_preview_only",
        "receipt_chain_handoff_preview_only",
        "owner_action_menu_preview_only",
        "evidence_map_preview_only",
        "routing_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_saved_view_written",
        "real_user_preference_written",
        "real_action_executed",
        "real_handoff_executed",
        "real_owner_action_executed",
        "real_evidence_exported",
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_history_written",
        "real_version_written",
        "real_version_saved",
        "real_rollback_executed",
        "real_restore_executed",
        "real_edit_persisted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["handoff_saved_view_preview_count"] == 6
    assert summary["handoff_filter_preset_preview_count"] == 8
    assert summary["selected_handoff_saved_view_preview_count"] == 1
    assert summary["selected_saved_view_id"] == "default_full_handoff"
    assert summary["selected_filter_preset_id"] == "all_handoff_items"
    assert summary["selected_handoff_route_count"] == 5
    assert summary["selected_owner_action_count"] == 6
    assert summary["selected_evidence_map_item_count"] == 4
    assert summary["selected_next_batch_card_count"] == 5
    assert summary["real_saved_view_written_count"] == 0
    assert summary["real_user_preference_written_count"] == 0
    assert summary["real_navigation_state_persisted_count"] == 0
    assert summary["real_action_executed_count"] == 0
    assert summary["real_handoff_executed_count"] == 0
    assert summary["real_owner_action_executed_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["save_batch"] == "201-205"
    assert summary["save_after_pack"] == 205

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_201_ready",
        "pack_201_safe_to_continue",
        "has_saved_view_previews",
        "has_filter_preset_previews",
        "has_selected_saved_view",
        "default_saved_view_selected",
        "default_filter_preset_selected",
        "all_saved_views_ready",
        "all_filter_presets_ready",
        "safety_summary_ready",
        "indexes_present",
        "preset_indexes_present",
        "selected_index_present",
        "selected_counts_match_source",
        "all_simulated_only",
        "all_saved_view_preview_only",
        "all_filter_preset_preview_only",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "no_real_navigation_state_persisted",
        "no_real_action_executed",
        "no_real_handoff_executed",
        "no_real_owner_action_executed",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_saved_view_writes_blocked",
        "all_user_preference_writes_blocked",
        "all_filter_preference_saves_blocked",
        "all_navigation_persistence_blocked",
        "all_action_execution_blocked",
        "all_evidence_export_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_202_saved_views_and_filter_presets():
    mod = importlib.import_module("tower.receipt_chain_handoff_saved_views_v202")
    payload = mod.build_receipt_chain_handoff_saved_views_v202_payload(force_refresh=True)

    views = payload["handoff_saved_view_previews"]
    presets = payload["handoff_filter_preset_previews"]

    assert len(views) == 6
    assert len(presets) == 8

    expected_views = {
        "default_full_handoff",
        "routes_only",
        "blocked_owner_actions",
        "allowed_preview_actions",
        "evidence_map",
        "next_batch_201_205",
    }

    view_ids = {view["saved_view_id"] for view in views}
    assert view_ids == expected_views

    view_by_id = {view["saved_view_id"]: view for view in views}

    assert view_by_id["default_full_handoff"]["matched_handoff_route_count"] == 5
    assert view_by_id["default_full_handoff"]["matched_owner_action_count"] == 6
    assert view_by_id["default_full_handoff"]["matched_evidence_map_item_count"] == 4
    assert view_by_id["default_full_handoff"]["matched_next_batch_card_count"] == 5

    assert view_by_id["routes_only"]["matched_handoff_route_count"] == 5
    assert view_by_id["routes_only"]["matched_owner_action_count"] == 0

    assert view_by_id["blocked_owner_actions"]["matched_owner_action_count"] == 3
    assert view_by_id["allowed_preview_actions"]["matched_owner_action_count"] == 3
    assert view_by_id["evidence_map"]["matched_evidence_map_item_count"] == 4
    assert view_by_id["next_batch_201_205"]["matched_next_batch_card_count"] == 5

    for view in views:
        assert view["handoff_saved_view_preview_id"].startswith("receipt_chain_handoff_saved_view_")
        assert view["saved_view_id"] in expected_views
        assert view["label"]
        assert view["description"]
        assert view["sequence"] in {1, 2, 3, 4, 5, 6}
        assert isinstance(view["matched_route_keys"], list)
        assert isinstance(view["matched_owner_action_keys"], list)
        assert isinstance(view["matched_source_pack_numbers"], list)
        assert isinstance(view["matched_next_pack_numbers"], list)
        assert view["matched_handoff_route_count"] == len(view["matched_route_keys"])
        assert view["matched_owner_action_count"] == len(view["matched_owner_action_keys"])
        assert view["matched_evidence_map_item_count"] == len(view["matched_source_pack_numbers"])
        assert view["matched_next_batch_card_count"] == len(view["matched_next_pack_numbers"])
        assert view["save_batch"] == "201-205"
        assert view["view_status"] == "receipt_chain_handoff_saved_view_preview_ready"
        assert view["view_result_type"] == "tower_receipt_chain_handoff_saved_view_preview"
        assert view["safe_preview_only"] is True

        assert view["simulated_only"] is True
        assert view["saved_view_preview_only"] is True
        assert view["filter_preset_preview_only"] is True
        assert view["operational_handoff_preview_only"] is True
        assert view["receipt_chain_handoff_preview_only"] is True
        assert view["real_saved_view_written"] is False
        assert view["real_user_preference_written"] is False
        assert view["real_action_executed"] is False
        assert view["real_handoff_executed"] is False
        assert view["real_owner_action_executed"] is False
        assert view["real_evidence_exported"] is False
        assert view["real_filter_preference_saved"] is False
        assert view["real_navigation_state_persisted"] is False
        assert view["real_raw_evidence_revealed"] is False
        assert view["saved_view_write_allowed_now"] is False
        assert view["user_preference_write_allowed_now"] is False
        assert view["filter_preference_save_allowed_now"] is False
        assert view["navigation_persistence_allowed_now"] is False
        assert view["evidence_export_allowed_now"] is False
        assert view["raw_evidence_reveal_allowed"] is False

    expected_presets = {
        "all_handoff_items",
        "ready_routes",
        "blocked_actions",
        "allowed_preview_actions",
        "evidence_pack_map",
        "next_batch_board",
        "no_real_execution",
        "export_blocked",
    }

    preset_ids = {preset["filter_preset_id"] for preset in presets}
    assert preset_ids == expected_presets

    preset_by_id = {preset["filter_preset_id"]: preset for preset in presets}

    assert preset_by_id["all_handoff_items"]["matched_handoff_route_count"] == 5
    assert preset_by_id["all_handoff_items"]["matched_owner_action_count"] == 6
    assert preset_by_id["all_handoff_items"]["matched_evidence_map_item_count"] == 4
    assert preset_by_id["all_handoff_items"]["matched_next_batch_card_count"] == 5

    assert preset_by_id["ready_routes"]["matched_handoff_route_count"] == 5
    assert preset_by_id["blocked_actions"]["matched_owner_action_count"] == 3
    assert preset_by_id["allowed_preview_actions"]["matched_owner_action_count"] == 3
    assert preset_by_id["evidence_pack_map"]["matched_evidence_map_item_count"] == 4
    assert preset_by_id["next_batch_board"]["matched_next_batch_card_count"] == 5
    assert preset_by_id["no_real_execution"]["matched_handoff_route_count"] == 5
    assert preset_by_id["no_real_execution"]["matched_owner_action_count"] == 6
    assert preset_by_id["export_blocked"]["matched_owner_action_count"] == 1
    assert preset_by_id["export_blocked"]["matched_evidence_map_item_count"] == 4

    for preset in presets:
        assert preset["handoff_filter_preset_preview_id"].startswith("receipt_chain_handoff_filter_preset_")
        assert preset["filter_preset_id"] in expected_presets
        assert preset["label"]
        assert preset["filter_type"] in {
            "all",
            "route_state",
            "owner_action_state",
            "evidence_map",
            "next_batch",
            "safety",
        }
        assert preset["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert preset["preset_status"] == "receipt_chain_handoff_filter_preset_preview_ready"
        assert preset["preset_result_type"] == "tower_receipt_chain_handoff_filter_preset_preview"
        assert preset["safe_preview_only"] is True

        assert preset["simulated_only"] is True
        assert preset["saved_view_preview_only"] is True
        assert preset["filter_preset_preview_only"] is True
        assert preset["real_saved_view_written"] is False
        assert preset["real_user_preference_written"] is False
        assert preset["real_action_executed"] is False
        assert preset["real_handoff_executed"] is False
        assert preset["real_owner_action_executed"] is False
        assert preset["real_evidence_exported"] is False
        assert preset["real_raw_evidence_revealed"] is False
        assert preset["saved_view_write_allowed_now"] is False
        assert preset["user_preference_write_allowed_now"] is False
        assert preset["filter_preference_save_allowed_now"] is False
        assert preset["navigation_persistence_allowed_now"] is False
        assert preset["evidence_export_allowed_now"] is False
        assert preset["raw_evidence_reveal_allowed"] is False


def test_pack_202_selected_view_safety_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_handoff_saved_views_v202")
    payload = mod.build_receipt_chain_handoff_saved_views_v202_payload(force_refresh=True)

    selected = payload["selected_handoff_saved_view_preview"]
    safety = payload["handoff_saved_view_safety_summary"]
    indexes = payload["handoff_saved_view_indexes"]

    assert selected["selected_handoff_saved_view_preview_id"].startswith("receipt_chain_selected_handoff_saved_view_")
    assert selected["selected_saved_view_id"] == "default_full_handoff"
    assert selected["selected_saved_view_preview_id"]
    assert selected["selected_filter_preset_id"] == "all_handoff_items"
    assert selected["selected_filter_preset_preview_id"]
    assert selected["selected_handoff_route_count"] == 5
    assert selected["selected_owner_action_count"] == 6
    assert selected["selected_evidence_map_item_count"] == 4
    assert selected["selected_next_batch_card_count"] == 5
    assert selected["selection_status"] == "receipt_chain_selected_handoff_saved_view_preview_ready"
    assert selected["selection_result_type"] == "tower_receipt_chain_selected_handoff_saved_view_preview"
    assert selected["safe_preview_only"] is True
    assert selected["real_saved_view_written"] is False
    assert selected["real_user_preference_written"] is False
    assert selected["real_action_executed"] is False
    assert selected["real_handoff_executed"] is False
    assert selected["real_owner_action_executed"] is False
    assert selected["real_evidence_exported"] is False
    assert selected["real_navigation_state_persisted"] is False
    assert selected["real_raw_evidence_revealed"] is False

    assert safety["handoff_saved_view_safety_summary_id"].startswith("receipt_chain_handoff_saved_view_safety_")
    assert safety["saved_view_preview_count"] == 6
    assert safety["filter_preset_preview_count"] == 8
    assert safety["selected_saved_view_preview_count"] == 1
    assert safety["real_saved_view_written_count"] == 0
    assert safety["real_user_preference_written_count"] == 0
    assert safety["real_navigation_state_persisted_count"] == 0
    assert safety["real_action_executed_count"] == 0
    assert safety["real_handoff_executed_count"] == 0
    assert safety["real_owner_action_executed_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_saved_views_preview_only"] is True
    assert safety["all_filter_presets_preview_only"] is True
    assert safety["all_real_writes_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_handoff_saved_view_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_handoff_saved_view_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_saved_view_written"] is False
    assert safety["real_user_preference_written"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert indexes["handoff_saved_views_by_id"]
    assert indexes["handoff_saved_views_by_key"]
    assert indexes["handoff_filter_presets_by_id"]
    assert indexes["handoff_filter_presets_by_key"]
    assert indexes["handoff_filter_presets_by_type"]
    assert indexes["selected_handoff_saved_view_by_id"]

    assert "default_full_handoff" in indexes["handoff_saved_views_by_key"]
    assert "routes_only" in indexes["handoff_saved_views_by_key"]
    assert "blocked_owner_actions" in indexes["handoff_saved_views_by_key"]
    assert "all_handoff_items" in indexes["handoff_filter_presets_by_key"]
    assert "blocked_actions" in indexes["handoff_filter_presets_by_key"]
    assert "saved" not in indexes
    assert selected["selected_handoff_saved_view_preview_id"] in indexes["selected_handoff_saved_view_by_id"]

    bridge = mod.build_receipt_chain_handoff_saved_views_v202_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 202
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-handoff-saved-views-v202.json"
    assert bridge["handoff_saved_view_preview_count"] == 6
    assert bridge["handoff_filter_preset_preview_count"] == 8
    assert bridge["selected_handoff_saved_view_preview_count"] == 1
    assert bridge["selected_saved_view_id"] == "default_full_handoff"
    assert bridge["selected_filter_preset_id"] == "all_handoff_items"
    assert bridge["selected_handoff_route_count"] == 5
    assert bridge["selected_owner_action_count"] == 6
    assert bridge["selected_evidence_map_item_count"] == 4
    assert bridge["selected_next_batch_card_count"] == 5
    assert bridge["real_saved_view_written_count"] == 0
    assert bridge["real_user_preference_written_count"] == 0
    assert bridge["real_navigation_state_persisted_count"] == 0
    assert bridge["real_action_executed_count"] == 0
    assert bridge["real_handoff_executed_count"] == 0
    assert bridge["real_owner_action_executed_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["save_batch"] == "201-205"
    assert bridge["save_after_pack"] == 205

    action = mod.build_receipt_chain_handoff_saved_views_v202_quick_action()
    assert action["id"] == "receipt_chain_handoff_saved_views_v202"
    assert action["href"] == "/tower/receipt-chain-handoff-saved-views-v202.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_handoff_saved_views_v202_unified_owner_section()
    assert section["section_id"] == "receipt_chain_handoff_saved_views_v202"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-handoff-saved-views-v202.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_202_receipt_chain_handoff_saved_views_v202_status_bridge")
    tower_bridge = status.build_pack_202_receipt_chain_handoff_saved_views_v202_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_202_receipt_chain_handoff_saved_views_v202_quick_action")
    assert hasattr(qa, "append_pack_202_receipt_chain_handoff_saved_views_v202_quick_action")
    actions = qa.append_pack_202_receipt_chain_handoff_saved_views_v202_quick_action([])
    assert any(item.get("id") == "receipt_chain_handoff_saved_views_v202" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_202_receipt_chain_handoff_saved_views_v202_unified_section")
    assert hasattr(unified, "append_pack_202_receipt_chain_handoff_saved_views_v202_section")
    sections = unified.append_pack_202_receipt_chain_handoff_saved_views_v202_section([])
    assert any(item.get("section_id") == "receipt_chain_handoff_saved_views_v202" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-handoff-saved-views-v202.json" in app_text
    assert "tower_receipt_chain_handoff_saved_views_v202_json" in app_text
    assert "_pack_202_receipt_chain_handoff_saved_views_v202_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-handoff-saved-views-v202.json" in route_text
    assert "_pack_202_receipt_chain_handoff_saved_views_v202_route_guard" in route_text

    payload_text = str(payload).lower()
    forbidden_fragments = [
        "sk_live_",
        "sk_test_",
        "github_pat_",
        "ghp_",
        "xoxb-",
        "aws_secret_access_key",
        "private_key-----",
        "broker_token_value",
        "api_secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
