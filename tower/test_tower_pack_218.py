
"""
PACK 218 fast test - Receipt Chain Saved View Edit Preview.

Uses short safe module:
    tower.receipt_chain_saved_view_edit_v218
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_218_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_saved_view_edit_v218")
    payload = mod.build_receipt_chain_saved_view_edit_v218_payload(force_refresh=True)

    assert payload["pack_number"] == 218
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-saved-view-edit-v218.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-saved-view-detail-v217.json"

    required_true = [
        "simulated_only",
        "saved_view_edit_preview_only",
        "editable_field_preview_only",
        "edit_validation_rule_preview_only",
        "edit_diff_preview_only",
        "edit_conflict_preview_only",
        "saved_view_edit_action_menu_preview_only",
        "owner_saved_view_edit_queue_preview_only",
        "saved_view_detail_preview_only",
        "selected_preset_detail_preview_only",
        "preset_field_detail_preview_only",
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
        "real_edit_preview_saved",
        "real_edit_diff_saved",
        "real_edit_validation_saved",
        "real_edit_conflict_saved",
        "real_detail_state_persisted",
        "real_detail_selection_saved",
        "real_field_detail_saved",
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
    assert summary["editable_field_count"] == 8
    assert summary["edit_validation_rule_count"] == 7
    assert summary["edit_diff_row_count"] == 8
    assert summary["edit_conflict_card_count"] == 5
    assert summary["saved_view_edit_action_menu_item_count"] == 8
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 5
    assert summary["owner_saved_view_edit_queue_item_count"] == 5
    assert summary["real_saved_view_written_count"] == 0
    assert summary["real_saved_view_edited_count"] == 0
    assert summary["real_saved_view_deleted_count"] == 0
    assert summary["real_saved_view_applied_count"] == 0
    assert summary["real_saved_view_exported_count"] == 0
    assert summary["real_edit_preview_saved_count"] == 0
    assert summary["real_edit_diff_saved_count"] == 0
    assert summary["real_edit_validation_saved_count"] == 0
    assert summary["real_edit_conflict_saved_count"] == 0
    assert summary["real_user_preference_written_count"] == 0
    assert summary["real_navigation_state_persisted_count"] == 0
    assert summary["real_owner_review_saved_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_219"] is True
    assert summary["save_batch"] == "216-220"
    assert summary["save_after_pack"] == 220

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_217_ready",
        "pack_217_safe_to_continue",
        "has_editable_fields",
        "has_validation_rules",
        "has_edit_diffs",
        "has_edit_conflicts",
        "has_edit_actions",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "has_owner_edit_queue",
        "all_fields_ready",
        "all_rules_ready",
        "all_diffs_ready",
        "all_conflicts_ready",
        "all_actions_ready_or_blocked",
        "all_queue_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_219",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_saved_view_edit_preview_only",
        "no_real_saved_view_written",
        "no_real_saved_view_edited",
        "no_real_saved_view_deleted",
        "no_real_saved_view_applied",
        "no_real_saved_view_exported",
        "no_real_edit_preview_saved",
        "no_real_edit_diff_saved",
        "no_real_edit_validation_saved",
        "no_real_edit_conflict_saved",
        "no_real_user_preference_written",
        "no_real_navigation_state_persisted",
        "no_real_owner_review_saved",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_edit_writes_blocked",
        "all_saved_view_writes_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_218_fields_rules_diffs_conflicts_actions_and_queue():
    mod = importlib.import_module("tower.receipt_chain_saved_view_edit_v218")
    payload = mod.build_receipt_chain_saved_view_edit_v218_payload(force_refresh=True)

    fields = payload["editable_field_previews"]
    rules = payload["edit_validation_rule_card_previews"]
    diffs = payload["edit_diff_row_previews"]
    conflicts = payload["edit_conflict_card_previews"]
    actions = payload["saved_view_edit_action_menu_previews"]
    queue = payload["owner_saved_view_edit_queue_previews"]

    assert len(fields) == 8
    assert len(rules) == 7
    assert len(diffs) == 8
    assert len(conflicts) == 5
    assert len(actions) == 8
    assert len(queue) == 5

    expected_fields = {
        "preset_key",
        "preset_type",
        "preset_value",
        "source_batch",
        "safety_state",
        "write_policy",
        "raw_evidence_policy",
        "next_action",
    }

    assert {item["editable_field_key"] for item in fields} == expected_fields

    preview_edit_allowed_fields = {
        "preset_key",
        "preset_type",
        "preset_value",
        "next_action",
    }

    for item in fields:
        assert item["editable_field_preview_id"].startswith("receipt_chain_saved_view_edit_field_")
        assert item["editable_field_key"] in expected_fields
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
            "unknown",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert item["source_endpoint"] == "/tower/receipt-chain-saved-view-detail-v217.json"
        assert item["current_value_preview"]
        assert item["proposed_value_preview"].startswith("preview_edit_")
        assert item["edit_preview_allowed"] == (item["editable_field_key"] in preview_edit_allowed_fields)
        assert item["real_edit_allowed_now"] is False
        assert item["saved_view_edit_allowed_now"] is False
        assert item["edit_preview_save_allowed_now"] is False
        assert item["field_status"] == "receipt_chain_saved_view_editable_field_preview_ready"
        assert item["field_result_type"] == "tower_receipt_chain_saved_view_editable_field_preview"
        assert item["safe_preview_only"] is True
        assert item["real_saved_view_edited"] is False
        assert item["real_edit_preview_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_rules = {
        "deny_real_write",
        "deny_real_apply",
        "deny_raw_reveal",
        "require_preview_mode",
        "require_owner_review",
        "preserve_batch_scope",
        "preserve_route_wall",
    }

    assert {item["edit_validation_rule_key"] for item in rules} == expected_rules

    for item in rules:
        assert item["edit_validation_rule_card_preview_id"].startswith("receipt_chain_saved_view_edit_rule_")
        assert item["edit_validation_rule_key"] in expected_rules
        assert item["label"]
        assert item["rule_type"] in {
            "deny_write",
            "deny_apply",
            "redaction",
            "mode",
            "owner_review",
            "scope",
            "route_wall",
        }
        assert item["rule_outcome"] in {"blocked", "required"}
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7}
        assert item["linked_editable_field_count"] == 8
        assert len(item["linked_editable_field_keys"]) == 8
        assert item["validation_passed_preview"] is True
        assert item["edit_validation_save_allowed_now"] is False
        assert item["rule_status"] == "receipt_chain_saved_view_edit_validation_rule_preview_ready"
        assert item["rule_result_type"] == "tower_receipt_chain_saved_view_edit_validation_rule_preview"
        assert item["safe_preview_only"] is True
        assert item["real_edit_validation_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    assert {item["edit_diff_key"] for item in diffs} == {f"diff_{key}" for key in expected_fields}

    for item in diffs:
        assert item["edit_diff_row_preview_id"].startswith("receipt_chain_saved_view_edit_diff_")
        assert item["edit_diff_key"].startswith("diff_")
        assert item["field_key"] in expected_fields
        assert item["label"]
        assert item["diff_type"] in {
            "identity",
            "classification",
            "value",
            "source",
            "safety",
            "policy",
            "redaction",
            "next_step",
            "unknown",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert item["current_value_preview"]
        assert item["proposed_value_preview"].startswith("preview_edit_")
        assert item["diff_result"] == "preview_only_no_persist"
        assert item["linked_validation_rule_count"] == 7
        assert len(item["linked_validation_rule_keys"]) == 7
        assert item["edit_diff_save_allowed_now"] is False
        assert item["diff_status"] == "receipt_chain_saved_view_edit_diff_preview_ready"
        assert item["diff_result_type"] == "tower_receipt_chain_saved_view_edit_diff_preview"
        assert item["safe_preview_only"] is True
        assert item["real_edit_diff_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_conflicts = {
        "write_block_conflict",
        "apply_block_conflict",
        "raw_reveal_conflict",
        "navigation_persist_conflict",
        "owner_review_required_conflict",
    }

    assert {item["edit_conflict_key"] for item in conflicts} == expected_conflicts

    for item in conflicts:
        assert item["edit_conflict_card_preview_id"].startswith("receipt_chain_saved_view_edit_conflict_")
        assert item["edit_conflict_key"] in expected_conflicts
        assert item["label"]
        assert item["conflict_type"] in {
            "write_block",
            "apply_block",
            "raw_evidence",
            "navigation",
            "owner_review",
        }
        assert item["conflict_result"] in {
            "blocked_by_policy",
            "blocked_by_redaction",
            "blocked_by_preview",
            "requires_review",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_editable_field_count"] == 8
        assert len(item["linked_editable_field_keys"]) == 8
        assert item["linked_edit_diff_count"] == 8
        assert len(item["linked_edit_diff_keys"]) == 8
        assert item["edit_conflict_save_allowed_now"] is False
        assert item["conflict_status"] == "receipt_chain_saved_view_edit_conflict_preview_ready"
        assert item["conflict_result_type"] == "tower_receipt_chain_saved_view_edit_conflict_preview"
        assert item["safe_preview_only"] is True
        assert item["real_edit_conflict_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_actions = {
        "preview_edit_status",
        "preview_edit_diff",
        "open_pack_217_saved_view_detail",
        "blocked_save_edit_preview",
        "blocked_apply_saved_view_edit",
        "blocked_write_user_preference",
        "blocked_export_edit_packet",
        "blocked_reveal_raw_evidence",
    }

    assert {item["saved_view_edit_action_key"] for item in actions} == expected_actions

    allowed_actions = [item for item in actions if item["allowed_in_preview"] is True]
    blocked_actions = [item for item in actions if item["blocked_in_preview"] is True]

    assert len(allowed_actions) == 3
    assert len(blocked_actions) == 5

    assert {item["saved_view_edit_action_key"] for item in allowed_actions} == {
        "preview_edit_status",
        "preview_edit_diff",
        "open_pack_217_saved_view_detail",
    }

    assert {item["saved_view_edit_action_key"] for item in blocked_actions} == {
        "blocked_save_edit_preview",
        "blocked_apply_saved_view_edit",
        "blocked_write_user_preference",
        "blocked_export_edit_packet",
        "blocked_reveal_raw_evidence",
    }

    for item in actions:
        assert item["saved_view_edit_action_menu_item_preview_id"].startswith("receipt_chain_saved_view_edit_action_")
        assert item["editable_field_count"] == 8
        assert item["validation_rule_count"] == 7
        assert item["edit_diff_row_count"] == 8
        assert item["edit_conflict_card_count"] == 5
        assert item["executes_real_saved_view_edit_action"] is False
        assert item["action_status"] in {
            "receipt_chain_saved_view_edit_action_preview_ready",
            "receipt_chain_saved_view_edit_action_preview_blocked",
        }
        assert item["action_result_type"] == "tower_receipt_chain_saved_view_edit_action_menu_preview"
        assert item["safe_preview_only"] is True
        assert item["real_action_executed"] is False
        assert item["real_saved_view_applied"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_queue = {
        "review_editable_fields",
        "review_validation_rules",
        "review_edit_diffs",
        "review_edit_conflicts",
        "prepare_pack_219_saved_view_history",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_saved_view_edit_queue_item_preview_id"].startswith("receipt_chain_owner_saved_view_edit_queue_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {
            "field_review",
            "validation_review",
            "diff_review",
            "conflict_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_review_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_owner_saved_view_edit_queue_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_owner_saved_view_edit_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_review_saved"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_218_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_saved_view_edit_v218")
    payload = mod.build_receipt_chain_saved_view_edit_v218_payload(force_refresh=True)

    safety = payload["saved_view_edit_safety_summary"]
    checkpoint = payload["saved_view_edit_checkpoint"]
    indexes = payload["saved_view_edit_indexes"]

    assert safety["editable_field_count"] == 8
    assert safety["edit_validation_rule_count"] == 7
    assert safety["edit_diff_row_count"] == 8
    assert safety["edit_conflict_card_count"] == 5
    assert safety["saved_view_edit_action_menu_item_count"] == 8
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 5
    assert safety["owner_saved_view_edit_queue_item_count"] == 5
    assert safety["real_saved_view_written_count"] == 0
    assert safety["real_saved_view_edited_count"] == 0
    assert safety["real_saved_view_deleted_count"] == 0
    assert safety["real_saved_view_applied_count"] == 0
    assert safety["real_saved_view_exported_count"] == 0
    assert safety["real_edit_preview_saved_count"] == 0
    assert safety["real_edit_diff_saved_count"] == 0
    assert safety["real_edit_validation_saved_count"] == 0
    assert safety["real_edit_conflict_saved_count"] == 0
    assert safety["real_user_preference_written_count"] == 0
    assert safety["real_navigation_state_persisted_count"] == 0
    assert safety["real_owner_review_saved_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_fields_preview_only"] is True
    assert safety["all_rules_preview_only"] is True
    assert safety["all_diffs_preview_only"] is True
    assert safety["all_conflicts_preview_only"] is True
    assert safety["all_actions_preview_only"] is True
    assert safety["all_queue_preview_only"] is True
    assert safety["all_saved_view_edit_writes_blocked"] is True
    assert safety["all_raw_evidence_reveal_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_saved_view_edit_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_saved_view_edit_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_saved_view_applied"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_saved_view_edit_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_saved_view_edit_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_219"] is True
    assert checkpoint["save_batch"] == "216-220"
    assert checkpoint["save_after_pack"] == 220
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_saved_view_applied"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["editable_fields_by_id"]
    assert indexes["editable_fields_by_key"]
    assert indexes["validation_rules_by_id"]
    assert indexes["validation_rules_by_key"]
    assert indexes["edit_diffs_by_id"]
    assert indexes["edit_diffs_by_key"]
    assert indexes["edit_conflicts_by_id"]
    assert indexes["edit_conflicts_by_key"]
    assert indexes["actions_by_id"]
    assert indexes["actions_by_key"]
    assert indexes["owner_edit_queue_by_id"]
    assert indexes["owner_edit_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "preset_key" in indexes["editable_fields_by_key"]
    assert "raw_evidence_policy" in indexes["editable_fields_by_key"]
    assert "deny_real_write" in indexes["validation_rules_by_key"]
    assert "deny_raw_reveal" in indexes["validation_rules_by_key"]
    assert "diff_preset_key" in indexes["edit_diffs_by_key"]
    assert "diff_raw_evidence_policy" in indexes["edit_diffs_by_key"]
    assert "write_block_conflict" in indexes["edit_conflicts_by_key"]
    assert "raw_reveal_conflict" in indexes["edit_conflicts_by_key"]
    assert "blocked_reveal_raw_evidence" in indexes["actions_by_key"]
    assert "prepare_pack_219_saved_view_history" in indexes["owner_edit_queue_by_key"]
    assert checkpoint["saved_view_edit_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_saved_view_edit_v218_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 218
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-saved-view-edit-v218.json"
    assert bridge["editable_field_count"] == 8
    assert bridge["edit_validation_rule_count"] == 7
    assert bridge["edit_diff_row_count"] == 8
    assert bridge["edit_conflict_card_count"] == 5
    assert bridge["saved_view_edit_action_menu_item_count"] == 8
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 5
    assert bridge["owner_saved_view_edit_queue_item_count"] == 5
    assert bridge["real_saved_view_written_count"] == 0
    assert bridge["real_saved_view_edited_count"] == 0
    assert bridge["real_saved_view_deleted_count"] == 0
    assert bridge["real_saved_view_applied_count"] == 0
    assert bridge["real_saved_view_exported_count"] == 0
    assert bridge["real_edit_preview_saved_count"] == 0
    assert bridge["real_edit_diff_saved_count"] == 0
    assert bridge["real_edit_validation_saved_count"] == 0
    assert bridge["real_edit_conflict_saved_count"] == 0
    assert bridge["real_user_preference_written_count"] == 0
    assert bridge["real_navigation_state_persisted_count"] == 0
    assert bridge["real_owner_review_saved_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_219"] is True
    assert bridge["save_batch"] == "216-220"
    assert bridge["save_after_pack"] == 220

    action = mod.build_receipt_chain_saved_view_edit_v218_quick_action()
    assert action["id"] == "receipt_chain_saved_view_edit_v218"
    assert action["href"] == "/tower/receipt-chain-saved-view-edit-v218.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_saved_view_edit_v218_unified_owner_section()
    assert section["section_id"] == "receipt_chain_saved_view_edit_v218"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-saved-view-edit-v218.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_218_receipt_chain_saved_view_edit_v218_status_bridge")
    tower_bridge = status.build_pack_218_receipt_chain_saved_view_edit_v218_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_219"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_218_receipt_chain_saved_view_edit_v218_quick_action")
    assert hasattr(qa, "append_pack_218_receipt_chain_saved_view_edit_v218_quick_action")
    actions = qa.append_pack_218_receipt_chain_saved_view_edit_v218_quick_action([])
    assert any(item.get("id") == "receipt_chain_saved_view_edit_v218" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_218_receipt_chain_saved_view_edit_v218_unified_section")
    assert hasattr(unified, "append_pack_218_receipt_chain_saved_view_edit_v218_section")
    sections = unified.append_pack_218_receipt_chain_saved_view_edit_v218_section([])
    assert any(item.get("section_id") == "receipt_chain_saved_view_edit_v218" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-saved-view-edit-v218.json" in app_text
    assert "tower_receipt_chain_saved_view_edit_v218_json" in app_text
    assert "_pack_218_receipt_chain_saved_view_edit_v218_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-saved-view-edit-v218.json" in route_text
    assert "_pack_218_receipt_chain_saved_view_edit_v218_route_guard" in route_text

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
