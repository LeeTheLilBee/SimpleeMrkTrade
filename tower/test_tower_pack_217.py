
"""
PACK 217 fast test - Receipt Chain Saved View Detail Preview.

Uses short safe module:
    tower.receipt_chain_saved_view_detail_v217
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_217_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_saved_view_detail_v217")
    payload = mod.build_receipt_chain_saved_view_detail_v217_payload(force_refresh=True)

    assert payload["pack_number"] == 217
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-detail-v217.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-saved-view-presets-v216.json"

    required_true = [
        "simulated_only",
        "saved_view_detail_preview_only",
        "selected_preset_detail_preview_only",
        "preset_field_detail_preview_only",
        "linked_filter_detail_preview_only",
        "linked_scope_detail_preview_only",
        "saved_view_detail_action_menu_preview_only",
        "owner_saved_view_detail_queue_preview_only",
        "saved_view_preset_preview_only",
        "saved_view_filter_map_preview_only",
        "saved_view_scope_card_preview_only",
        "raw_evidence_redacted",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_action_executed",
        "real_handoff_executed",
        "real_owner_action_executed",
        "real_evidence_exported",
        "real_export_request_created",
        "real_packet_written",
        "real_packet_sealed",
        "real_saved_view_written",
        "real_saved_view_edited",
        "real_saved_view_deleted",
        "real_saved_view_applied",
        "real_saved_view_exported",
        "real_detail_state_persisted",
        "real_detail_selection_saved",
        "real_field_detail_saved",
        "real_linked_filter_detail_saved",
        "real_linked_scope_detail_saved",
        "real_user_preference_written",
        "real_navigation_state_persisted",
        "real_owner_review_saved",
        "real_archive_written",
        "real_archive_exported",
        "real_gateway_access_granted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]

    assert summary["readiness_score"] == 100
    assert summary["selected_preset_detail_count"] == 7
    assert summary["preset_field_detail_row_count"] == 8
    assert summary["linked_filter_detail_card_count"] == 7
    assert summary["linked_scope_detail_card_count"] == 6
    assert summary["saved_view_detail_action_menu_item_count"] == 8
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 5
    assert summary["owner_saved_view_detail_queue_item_count"] == 5
    assert summary["real_saved_view_written_count"] == 0
    assert summary["real_saved_view_edited_count"] == 0
    assert summary["real_saved_view_deleted_count"] == 0
    assert summary["real_saved_view_applied_count"] == 0
    assert summary["real_saved_view_exported_count"] == 0
    assert summary["real_detail_state_persisted_count"] == 0
    assert summary["real_detail_selection_saved_count"] == 0
    assert summary["real_field_detail_saved_count"] == 0
    assert summary["real_linked_filter_detail_saved_count"] == 0
    assert summary["real_linked_scope_detail_saved_count"] == 0
    assert summary["real_user_preference_written_count"] == 0
    assert summary["real_navigation_state_persisted_count"] == 0
    assert summary["real_owner_review_saved_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_218"] is True
    assert summary["save_batch"] == "216-220"
    assert summary["save_after_pack"] == 220

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_216_ready",
        "pack_216_safe_to_continue",
        "has_selected_preset_details",
        "has_field_detail_rows",
        "has_linked_filter_details",
        "has_linked_scope_details",
        "has_detail_actions",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "has_owner_detail_queue",
        "all_details_ready",
        "all_rows_ready",
        "all_filter_details_ready",
        "all_scope_details_ready",
        "all_actions_ready_or_blocked",
        "all_queue_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_218",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_saved_view_detail_preview_only",
        "no_real_saved_view_written",
        "no_real_saved_view_edited",
        "no_real_saved_view_deleted",
        "no_real_saved_view_applied",
        "no_real_saved_view_exported",
        "no_real_detail_state_persisted",
        "no_real_detail_selection_saved",
        "no_real_field_detail_saved",
        "no_real_linked_filter_detail_saved",
        "no_real_linked_scope_detail_saved",
        "no_real_user_preference_written",
        "no_real_navigation_state_persisted",
        "no_real_owner_review_saved",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_detail_writes_blocked",
        "all_saved_view_writes_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_217_details_fields_filters_scopes_actions_and_queue():
    mod = importlib.import_module("tower.receipt_chain_saved_view_detail_v217")
    payload = mod.build_receipt_chain_saved_view_detail_v217_payload(force_refresh=True)

    details = payload["selected_preset_detail_previews"]
    rows = payload["preset_field_detail_row_previews"]
    filters = payload["linked_filter_detail_card_previews"]
    scopes = payload["linked_scope_detail_card_previews"]
    actions = payload["saved_view_detail_action_menu_previews"]
    queue = payload["owner_saved_view_detail_queue_previews"]

    assert len(details) == 7
    assert len(rows) == 8
    assert len(filters) == 7
    assert len(scopes) == 6
    assert len(actions) == 8
    assert len(queue) == 5

    expected_details = {
        "all_recovered_checkpoint_packs",
        "batch_211_215_only",
        "recovered_dependencies_208_210",
        "ready_only_checkpoint_packs",
        "no_real_action_safety_view",
        "raw_redaction_view",
        "next_batch_216_220_handoff",
    }

    assert {item["selected_preset_key"] for item in details} == expected_details

    for item in details:
        assert item["selected_preset_detail_preview_id"].startswith("receipt_chain_saved_view_detail_")
        assert item["selected_preset_key"] in expected_details
        assert item["label"]
        assert item["detail_type"] in {
            "batch",
            "dependency",
            "status",
            "safety",
            "redaction",
            "next_batch",
            "unknown",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7}
        assert item["source_endpoint"] == "/tower/receipt-chain-saved-view-presets-v216.json"
        assert item["detail_section_count"] == 6
        assert item["detail_sections"] == [
            "summary",
            "filter_values",
            "scope",
            "safety_flags",
            "owner_review",
            "next_action_preview",
        ]
        assert item["detail_state_persistence_allowed_now"] is False
        assert item["detail_selection_save_allowed_now"] is False
        assert item["detail_status"] == "receipt_chain_saved_view_selected_preset_detail_preview_ready"
        assert item["detail_result_type"] == "tower_receipt_chain_saved_view_selected_preset_detail_preview"
        assert item["safe_preview_only"] is True
        assert item["real_detail_state_persisted"] is False
        assert item["real_detail_selection_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_rows = {
        "preset_key",
        "preset_type",
        "preset_value",
        "source_batch",
        "safety_state",
        "write_policy",
        "raw_evidence_policy",
        "next_action",
    }

    assert {item["preset_field_detail_key"] for item in rows} == expected_rows

    for item in rows:
        assert item["preset_field_detail_row_preview_id"].startswith("receipt_chain_saved_view_field_detail_")
        assert item["preset_field_detail_key"] in expected_rows
        assert item["label"]
        assert item["field_type"] in {
            "identity",
            "classification",
            "value",
            "source",
            "safety",
            "policy",
            "redaction",
            "next_step",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert item["linked_selected_preset_count"] == 7
        assert len(item["linked_selected_preset_keys"]) == 7
        assert item["field_value_preview"] == "preview_only_redacted_safe_value"
        assert item["field_detail_save_allowed_now"] is False
        assert item["row_status"] == "receipt_chain_saved_view_preset_field_detail_row_preview_ready"
        assert item["row_result_type"] == "tower_receipt_chain_saved_view_preset_field_detail_row_preview"
        assert item["safe_preview_only"] is True
        assert item["real_field_detail_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_filters = {
        "pack_range_filter",
        "status_filter",
        "safety_filter",
        "dependency_filter",
        "handoff_filter",
        "owner_review_filter",
        "route_wall_filter",
    }

    assert {item["linked_filter_detail_key"] for item in filters} == expected_filters

    for item in filters:
        assert item["linked_filter_detail_card_preview_id"].startswith("receipt_chain_saved_view_linked_filter_")
        assert item["linked_filter_detail_key"] in expected_filters
        assert item["label"]
        assert item["filter_type"] in {
            "pack_range",
            "status",
            "safety",
            "dependency",
            "handoff",
            "owner_review",
            "route_wall",
            "unknown",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7}
        assert item["filter_value_count"] >= 2
        assert item["linked_selected_preset_count"] == 7
        assert len(item["linked_selected_preset_keys"]) == 7
        assert item["linked_filter_detail_save_allowed_now"] is False
        assert item["card_status"] == "receipt_chain_saved_view_linked_filter_detail_preview_ready"
        assert item["card_result_type"] == "tower_receipt_chain_saved_view_linked_filter_detail_preview"
        assert item["safe_preview_only"] is True
        assert item["real_linked_filter_detail_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_scopes = {
        "source_pack_scope",
        "recovered_dependency_scope",
        "safety_rollup_scope",
        "save_push_scope",
        "next_batch_handoff_scope",
        "owner_navigation_scope",
    }

    assert {item["linked_scope_detail_key"] for item in scopes} == expected_scopes

    for item in scopes:
        assert item["linked_scope_detail_card_preview_id"].startswith("receipt_chain_saved_view_linked_scope_")
        assert item["linked_scope_detail_key"] in expected_scopes
        assert item["label"]
        assert item["scope_type"] in {
            "source_pack",
            "recovered_dependency",
            "safety_rollup",
            "save_push",
            "next_batch",
            "navigation",
            "unknown",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["linked_selected_preset_count"] == 7
        assert item["linked_filter_map_count"] == 7
        assert item["linked_scope_detail_save_allowed_now"] is False
        assert item["card_status"] == "receipt_chain_saved_view_linked_scope_detail_preview_ready"
        assert item["card_result_type"] == "tower_receipt_chain_saved_view_linked_scope_detail_preview"
        assert item["safe_preview_only"] is True
        assert item["real_linked_scope_detail_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_actions = {
        "preview_saved_view_detail_status",
        "preview_selected_preset_detail",
        "open_pack_216_saved_view_presets",
        "blocked_save_detail_state",
        "blocked_apply_saved_view",
        "blocked_edit_saved_view_detail",
        "blocked_export_saved_view_detail",
        "blocked_reveal_raw_evidence",
    }

    assert {item["saved_view_detail_action_key"] for item in actions} == expected_actions

    allowed_actions = [item for item in actions if item["allowed_in_preview"] is True]
    blocked_actions = [item for item in actions if item["blocked_in_preview"] is True]

    assert len(allowed_actions) == 3
    assert len(blocked_actions) == 5

    assert {item["saved_view_detail_action_key"] for item in allowed_actions} == {
        "preview_saved_view_detail_status",
        "preview_selected_preset_detail",
        "open_pack_216_saved_view_presets",
    }

    assert {item["saved_view_detail_action_key"] for item in blocked_actions} == {
        "blocked_save_detail_state",
        "blocked_apply_saved_view",
        "blocked_edit_saved_view_detail",
        "blocked_export_saved_view_detail",
        "blocked_reveal_raw_evidence",
    }

    for item in actions:
        assert item["saved_view_detail_action_menu_item_preview_id"].startswith("receipt_chain_saved_view_detail_action_")
        assert item["selected_preset_detail_count"] == 7
        assert item["field_detail_row_count"] == 8
        assert item["linked_filter_detail_count"] == 7
        assert item["linked_scope_detail_count"] == 6
        assert item["executes_real_saved_view_detail_action"] is False
        assert item["action_status"] in {
            "receipt_chain_saved_view_detail_action_preview_ready",
            "receipt_chain_saved_view_detail_action_preview_blocked",
        }
        assert item["action_result_type"] == "tower_receipt_chain_saved_view_detail_action_menu_preview"
        assert item["safe_preview_only"] is True
        assert item["real_action_executed"] is False
        assert item["real_saved_view_applied"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_queue = {
        "review_selected_preset_details",
        "review_field_detail_rows",
        "review_linked_filters",
        "review_linked_scopes",
        "prepare_pack_218_saved_view_edit",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_saved_view_detail_queue_item_preview_id"].startswith("receipt_chain_owner_saved_view_detail_queue_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {
            "detail_review",
            "field_review",
            "filter_review",
            "scope_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_review_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_owner_saved_view_detail_queue_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_owner_saved_view_detail_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_review_saved"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_217_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_saved_view_detail_v217")
    payload = mod.build_receipt_chain_saved_view_detail_v217_payload(force_refresh=True)

    safety = payload["saved_view_detail_safety_summary"]
    checkpoint = payload["saved_view_detail_checkpoint"]
    indexes = payload["saved_view_detail_indexes"]

    assert safety["selected_preset_detail_count"] == 7
    assert safety["preset_field_detail_row_count"] == 8
    assert safety["linked_filter_detail_card_count"] == 7
    assert safety["linked_scope_detail_card_count"] == 6
    assert safety["saved_view_detail_action_menu_item_count"] == 8
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 5
    assert safety["owner_saved_view_detail_queue_item_count"] == 5
    assert safety["real_saved_view_written_count"] == 0
    assert safety["real_saved_view_edited_count"] == 0
    assert safety["real_saved_view_deleted_count"] == 0
    assert safety["real_saved_view_applied_count"] == 0
    assert safety["real_saved_view_exported_count"] == 0
    assert safety["real_detail_state_persisted_count"] == 0
    assert safety["real_detail_selection_saved_count"] == 0
    assert safety["real_field_detail_saved_count"] == 0
    assert safety["real_linked_filter_detail_saved_count"] == 0
    assert safety["real_linked_scope_detail_saved_count"] == 0
    assert safety["real_user_preference_written_count"] == 0
    assert safety["real_navigation_state_persisted_count"] == 0
    assert safety["real_owner_review_saved_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_details_preview_only"] is True
    assert safety["all_rows_preview_only"] is True
    assert safety["all_filter_details_preview_only"] is True
    assert safety["all_scope_details_preview_only"] is True
    assert safety["all_actions_preview_only"] is True
    assert safety["all_queue_preview_only"] is True
    assert safety["all_saved_view_detail_writes_blocked"] is True
    assert safety["all_raw_evidence_reveal_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_saved_view_detail_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_saved_view_detail_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_saved_view_applied"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_saved_view_detail_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_saved_view_detail_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_218"] is True
    assert checkpoint["save_batch"] == "216-220"
    assert checkpoint["save_after_pack"] == 220
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_saved_view_applied"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["selected_preset_details_by_id"]
    assert indexes["selected_preset_details_by_key"]
    assert indexes["field_detail_rows_by_id"]
    assert indexes["field_detail_rows_by_key"]
    assert indexes["linked_filter_details_by_id"]
    assert indexes["linked_filter_details_by_key"]
    assert indexes["linked_scope_details_by_id"]
    assert indexes["linked_scope_details_by_key"]
    assert indexes["actions_by_id"]
    assert indexes["actions_by_key"]
    assert indexes["owner_detail_queue_by_id"]
    assert indexes["owner_detail_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "all_recovered_checkpoint_packs" in indexes["selected_preset_details_by_key"]
    assert "next_batch_216_220_handoff" in indexes["selected_preset_details_by_key"]
    assert "preset_key" in indexes["field_detail_rows_by_key"]
    assert "raw_evidence_policy" in indexes["field_detail_rows_by_key"]
    assert "pack_range_filter" in indexes["linked_filter_details_by_key"]
    assert "route_wall_filter" in indexes["linked_filter_details_by_key"]
    assert "owner_navigation_scope" in indexes["linked_scope_details_by_key"]
    assert "blocked_reveal_raw_evidence" in indexes["actions_by_key"]
    assert "prepare_pack_218_saved_view_edit" in indexes["owner_detail_queue_by_key"]
    assert checkpoint["saved_view_detail_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_saved_view_detail_v217_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 217
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-saved-view-detail-v217.json"
    assert bridge["selected_preset_detail_count"] == 7
    assert bridge["preset_field_detail_row_count"] == 8
    assert bridge["linked_filter_detail_card_count"] == 7
    assert bridge["linked_scope_detail_card_count"] == 6
    assert bridge["saved_view_detail_action_menu_item_count"] == 8
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 5
    assert bridge["owner_saved_view_detail_queue_item_count"] == 5
    assert bridge["real_saved_view_written_count"] == 0
    assert bridge["real_saved_view_edited_count"] == 0
    assert bridge["real_saved_view_deleted_count"] == 0
    assert bridge["real_saved_view_applied_count"] == 0
    assert bridge["real_saved_view_exported_count"] == 0
    assert bridge["real_detail_state_persisted_count"] == 0
    assert bridge["real_detail_selection_saved_count"] == 0
    assert bridge["real_field_detail_saved_count"] == 0
    assert bridge["real_linked_filter_detail_saved_count"] == 0
    assert bridge["real_linked_scope_detail_saved_count"] == 0
    assert bridge["real_user_preference_written_count"] == 0
    assert bridge["real_navigation_state_persisted_count"] == 0
    assert bridge["real_owner_review_saved_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_218"] is True
    assert bridge["save_batch"] == "216-220"
    assert bridge["save_after_pack"] == 220

    action = mod.build_receipt_chain_saved_view_detail_v217_quick_action()
    assert action["id"] == "receipt_chain_saved_view_detail_v217"
    assert action["href"] == "/tower/receipt-chain-saved-view-detail-v217.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_saved_view_detail_v217_unified_owner_section()
    assert section["section_id"] == "receipt_chain_saved_view_detail_v217"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-saved-view-detail-v217.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_217_receipt_chain_saved_view_detail_v217_status_bridge")
    tower_bridge = status.build_pack_217_receipt_chain_saved_view_detail_v217_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_218"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_217_receipt_chain_saved_view_detail_v217_quick_action")
    assert hasattr(qa, "append_pack_217_receipt_chain_saved_view_detail_v217_quick_action")
    actions = qa.append_pack_217_receipt_chain_saved_view_detail_v217_quick_action([])
    assert any(item.get("id") == "receipt_chain_saved_view_detail_v217" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_217_receipt_chain_saved_view_detail_v217_unified_section")
    assert hasattr(unified, "append_pack_217_receipt_chain_saved_view_detail_v217_section")
    sections = unified.append_pack_217_receipt_chain_saved_view_detail_v217_section([])
    assert any(item.get("section_id") == "receipt_chain_saved_view_detail_v217" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-saved-view-detail-v217.json" in app_text
    assert "tower_receipt_chain_saved_view_detail_v217_json" in app_text
    assert "_pack_217_receipt_chain_saved_view_detail_v217_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-saved-view-detail-v217.json" in route_text
    assert "_pack_217_receipt_chain_saved_view_detail_v217_route_guard" in route_text

    payload_text = str(payload).lower()
    forbidden_fragments = [
        "sk_" + "live_",
        "sk_" + "test_",
        "github_" + "pat_",
        "g" + "hp_",
        "xox" + "b-",
        "aws_" + "secret_access_key",
        "private_key" + "-----",
        "broker_" + "token_value",
        "api_" + "secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
