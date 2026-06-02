
"""
PACK 207 fast test - Receipt Chain Containment Lane Preview.

Uses short safe module:
    tower.receipt_chain_containment_lane_v207
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_207_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_containment_lane_v207")
    payload = mod.build_receipt_chain_containment_lane_v207_payload(force_refresh=True)

    assert payload["pack_number"] == 207
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-containment-lane-v207.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-post-batch-ops-v206.json"

    required_true = [
        "simulated_only",
        "containment_lane_preview_only",
        "containment_trigger_preview_only",
        "containment_scope_map_preview_only",
        "containment_action_menu_preview_only",
        "owner_containment_review_queue_preview_only",
        "post_batch_ops_preview_only",
        "operational_readiness_preview_only",
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
        "real_recheck_executed",
        "real_renewal_executed",
        "real_expiration_enforced",
        "real_owner_followup_executed",
        "real_containment_executed",
        "real_containment_triggered",
        "real_containment_scope_applied",
        "real_containment_action_executed",
        "real_owner_containment_review_executed",
        "real_incident_action_executed",
        "real_archive_written",
        "real_gateway_access_granted",
        "real_owner_next_action_executed",
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_saved_view_written",
        "real_user_preference_written",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["containment_trigger_count"] == 6
    assert summary["containment_scope_map_count"] == 5
    assert summary["containment_action_menu_item_count"] == 8
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 5
    assert summary["owner_containment_review_queue_item_count"] == 5
    assert summary["real_containment_executed_count"] == 0
    assert summary["real_containment_triggered_count"] == 0
    assert summary["real_containment_scope_applied_count"] == 0
    assert summary["real_containment_action_executed_count"] == 0
    assert summary["real_owner_containment_review_executed_count"] == 0
    assert summary["real_incident_action_executed_count"] == 0
    assert summary["real_archive_written_count"] == 0
    assert summary["real_gateway_access_granted_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_208"] is True
    assert summary["save_batch"] == "206-210"
    assert summary["save_after_pack"] == 210

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_206_ready",
        "pack_206_safe_to_continue",
        "has_containment_triggers",
        "has_containment_scopes",
        "has_containment_actions",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "has_owner_review_queue",
        "all_triggers_ready",
        "all_scopes_ready",
        "all_actions_ready_or_blocked",
        "all_owner_reviews_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_208",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_containment_lane_preview_only",
        "no_real_containment_executed",
        "no_real_containment_triggered",
        "no_real_containment_scope_applied",
        "no_real_containment_action_executed",
        "no_real_owner_containment_review_executed",
        "no_real_incident_action_executed",
        "no_real_archive_written",
        "no_real_gateway_access_granted",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_containment_execution_blocked",
        "all_incident_actions_blocked",
        "all_archive_writes_blocked",
        "all_gateway_access_grants_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_207_triggers_scopes_actions_and_owner_queue():
    mod = importlib.import_module("tower.receipt_chain_containment_lane_v207")
    payload = mod.build_receipt_chain_containment_lane_v207_payload(force_refresh=True)

    triggers = payload["containment_trigger_previews"]
    scopes = payload["containment_scope_map_previews"]
    actions = payload["containment_action_menu_previews"]
    queue = payload["owner_containment_review_queue_previews"]

    assert len(triggers) == 6
    assert len(scopes) == 5
    assert len(actions) == 8
    assert len(queue) == 5

    expected_triggers = {
        "route_wall_regression",
        "object_checkpoint_regression",
        "raw_evidence_request",
        "gateway_grant_attempt",
        "archive_write_attempt",
        "owner_action_execution_attempt",
    }

    assert {item["containment_trigger_key"] for item in triggers} == expected_triggers

    for trigger in triggers:
        assert trigger["containment_trigger_preview_id"].startswith("receipt_chain_containment_trigger_")
        assert trigger["containment_trigger_key"] in expected_triggers
        assert trigger["label"]
        assert trigger["trigger_type"] in {
            "route_wall",
            "object_checkpoint",
            "raw_evidence",
            "gateway",
            "archive",
            "owner_action",
        }
        assert trigger["description"]
        assert trigger["sequence"] in {1, 2, 3, 4, 5, 6}
        assert trigger["source_pack_206_ready"] is True
        assert trigger["source_pack_206_safe_to_continue"] is True
        assert trigger["trigger_armed_in_preview"] is True
        assert trigger["trigger_executes_real_containment"] is False
        assert trigger["trigger_status"] == "receipt_chain_containment_trigger_preview_ready"
        assert trigger["trigger_result_type"] == "tower_receipt_chain_containment_trigger_preview"
        assert trigger["safe_preview_only"] is True

        assert trigger["simulated_only"] is True
        assert trigger["containment_lane_preview_only"] is True
        assert trigger["containment_trigger_preview_only"] is True
        assert trigger["real_containment_executed"] is False
        assert trigger["real_containment_triggered"] is False
        assert trigger["real_containment_scope_applied"] is False
        assert trigger["real_containment_action_executed"] is False
        assert trigger["real_raw_evidence_revealed"] is False
        assert trigger["containment_execution_allowed_now"] is False
        assert trigger["raw_evidence_reveal_allowed"] is False

    expected_scopes = {
        "source_pack_scope",
        "route_scope",
        "evidence_scope",
        "owner_action_scope",
        "gateway_scope",
    }

    assert {item["containment_scope_key"] for item in scopes} == expected_scopes

    for scope in scopes:
        assert scope["containment_scope_map_preview_id"].startswith("receipt_chain_containment_scope_")
        assert scope["containment_scope_key"] in expected_scopes
        assert scope["label"]
        assert scope["scope_type"] in {"source_packs", "routes", "evidence", "owner_actions", "gateway"}
        assert scope["sequence"] in {1, 2, 3, 4, 5}
        assert scope["matched_item_count"] == len(scope["matched_items"])
        assert len(scope["mapped_trigger_keys"]) == 6
        assert set(scope["mapped_trigger_keys"]) == expected_triggers
        assert scope["scope_applied_now"] is False
        assert scope["scope_status"] == "receipt_chain_containment_scope_map_preview_ready"
        assert scope["scope_result_type"] == "tower_receipt_chain_containment_scope_map_preview"
        assert scope["safe_preview_only"] is True

        assert scope["simulated_only"] is True
        assert scope["containment_scope_map_preview_only"] is True
        assert scope["real_containment_scope_applied"] is False
        assert scope["real_containment_executed"] is False
        assert scope["real_raw_evidence_revealed"] is False

    scope_by_key = {scope["containment_scope_key"]: scope for scope in scopes}
    assert scope_by_key["source_pack_scope"]["matched_items"] == [201, 202, 203, 204]
    assert scope_by_key["gateway_scope"]["matched_items"] == ["future_gateway_checks", "no_access_grants"]

    expected_actions = {
        "preview_containment_status",
        "preview_trigger_matrix",
        "open_pack_206_ops",
        "blocked_apply_soft_hold",
        "blocked_quarantine_route",
        "blocked_freeze_gateway",
        "blocked_open_incident",
        "blocked_write_archive_notice",
    }

    assert {item["containment_action_key"] for item in actions} == expected_actions

    allowed = [item for item in actions if item["allowed_in_preview"] is True]
    blocked = [item for item in actions if item["blocked_in_preview"] is True]

    assert len(allowed) == 3
    assert len(blocked) == 5

    assert {item["containment_action_key"] for item in allowed} == {
        "preview_containment_status",
        "preview_trigger_matrix",
        "open_pack_206_ops",
    }

    assert {item["containment_action_key"] for item in blocked} == {
        "blocked_apply_soft_hold",
        "blocked_quarantine_route",
        "blocked_freeze_gateway",
        "blocked_open_incident",
        "blocked_write_archive_notice",
    }

    for action in actions:
        assert action["containment_action_menu_item_preview_id"].startswith("receipt_chain_containment_action_")
        assert action["containment_action_key"] in expected_actions
        assert action["label"]
        assert action["description"]
        assert action["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert action["trigger_count"] == 6
        assert action["scope_count"] == 5
        assert action["executes_real_containment"] is False
        assert action["action_status"] in {
            "receipt_chain_containment_action_preview_ready",
            "receipt_chain_containment_action_preview_blocked",
        }
        assert action["action_result_type"] == "tower_receipt_chain_containment_action_menu_preview"
        assert action["safe_preview_only"] is True
        assert action["real_containment_executed"] is False
        assert action["real_containment_action_executed"] is False
        assert action["real_incident_action_executed"] is False
        assert action["real_archive_written"] is False
        assert action["real_gateway_access_granted"] is False
        assert action["real_raw_evidence_revealed"] is False

    expected_queue = {
        "review_trigger_coverage",
        "review_scope_boundaries",
        "review_blocked_actions",
        "confirm_no_real_containment",
        "prepare_pack_208_incident_lane",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_containment_review_queue_item_preview_id"].startswith("receipt_chain_containment_owner_review_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {
            "trigger_review",
            "scope_review",
            "action_review",
            "safety_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_review_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_containment_owner_review_queue_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_containment_owner_review_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_containment_review_executed"] is False
        assert item["real_containment_executed"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_207_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_containment_lane_v207")
    payload = mod.build_receipt_chain_containment_lane_v207_payload(force_refresh=True)

    safety = payload["containment_lane_safety_summary"]
    checkpoint = payload["containment_lane_checkpoint"]
    indexes = payload["containment_lane_indexes"]

    assert safety["containment_lane_safety_summary_id"].startswith("receipt_chain_containment_lane_safety_")
    assert safety["containment_trigger_count"] == 6
    assert safety["containment_scope_map_count"] == 5
    assert safety["containment_action_menu_item_count"] == 8
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 5
    assert safety["owner_containment_review_queue_item_count"] == 5
    assert safety["real_containment_executed_count"] == 0
    assert safety["real_containment_triggered_count"] == 0
    assert safety["real_containment_scope_applied_count"] == 0
    assert safety["real_containment_action_executed_count"] == 0
    assert safety["real_owner_containment_review_executed_count"] == 0
    assert safety["real_incident_action_executed_count"] == 0
    assert safety["real_archive_written_count"] == 0
    assert safety["real_gateway_access_granted_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_triggers_preview_only"] is True
    assert safety["all_scopes_preview_only"] is True
    assert safety["all_actions_preview_only"] is True
    assert safety["all_owner_reviews_preview_only"] is True
    assert safety["all_real_containment_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_containment_lane_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_containment_lane_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_containment_executed"] is False
    assert safety["real_containment_triggered"] is False
    assert safety["real_containment_scope_applied"] is False
    assert safety["real_containment_action_executed"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["containment_lane_checkpoint_id"].startswith("receipt_chain_containment_lane_checkpoint_")
    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_containment_lane_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_containment_lane_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_208"] is True
    assert checkpoint["save_batch"] == "206-210"
    assert checkpoint["save_after_pack"] == 210
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_containment_executed"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["containment_triggers_by_id"]
    assert indexes["containment_triggers_by_key"]
    assert indexes["containment_triggers_by_type"]
    assert indexes["containment_scopes_by_id"]
    assert indexes["containment_scopes_by_key"]
    assert indexes["containment_actions_by_id"]
    assert indexes["containment_actions_by_key"]
    assert indexes["owner_review_queue_by_id"]
    assert indexes["owner_review_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "route_wall_regression" in indexes["containment_triggers_by_key"]
    assert "raw_evidence_request" in indexes["containment_triggers_by_key"]
    assert "gateway_grant_attempt" in indexes["containment_triggers_by_key"]
    assert "source_pack_scope" in indexes["containment_scopes_by_key"]
    assert "gateway_scope" in indexes["containment_scopes_by_key"]
    assert "preview_containment_status" in indexes["containment_actions_by_key"]
    assert "blocked_quarantine_route" in indexes["containment_actions_by_key"]
    assert "prepare_pack_208_incident_lane" in indexes["owner_review_queue_by_key"]
    assert checkpoint["containment_lane_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_containment_lane_v207_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 207
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-containment-lane-v207.json"
    assert bridge["containment_trigger_count"] == 6
    assert bridge["containment_scope_map_count"] == 5
    assert bridge["containment_action_menu_item_count"] == 8
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 5
    assert bridge["owner_containment_review_queue_item_count"] == 5
    assert bridge["real_containment_executed_count"] == 0
    assert bridge["real_containment_triggered_count"] == 0
    assert bridge["real_containment_scope_applied_count"] == 0
    assert bridge["real_containment_action_executed_count"] == 0
    assert bridge["real_owner_containment_review_executed_count"] == 0
    assert bridge["real_incident_action_executed_count"] == 0
    assert bridge["real_archive_written_count"] == 0
    assert bridge["real_gateway_access_granted_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_208"] is True
    assert bridge["save_batch"] == "206-210"
    assert bridge["save_after_pack"] == 210

    action = mod.build_receipt_chain_containment_lane_v207_quick_action()
    assert action["id"] == "receipt_chain_containment_lane_v207"
    assert action["href"] == "/tower/receipt-chain-containment-lane-v207.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_containment_lane_v207_unified_owner_section()
    assert section["section_id"] == "receipt_chain_containment_lane_v207"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-containment-lane-v207.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_207_receipt_chain_containment_lane_v207_status_bridge")
    tower_bridge = status.build_pack_207_receipt_chain_containment_lane_v207_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_208"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_207_receipt_chain_containment_lane_v207_quick_action")
    assert hasattr(qa, "append_pack_207_receipt_chain_containment_lane_v207_quick_action")
    actions = qa.append_pack_207_receipt_chain_containment_lane_v207_quick_action([])
    assert any(item.get("id") == "receipt_chain_containment_lane_v207" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_207_receipt_chain_containment_lane_v207_unified_section")
    assert hasattr(unified, "append_pack_207_receipt_chain_containment_lane_v207_section")
    sections = unified.append_pack_207_receipt_chain_containment_lane_v207_section([])
    assert any(item.get("section_id") == "receipt_chain_containment_lane_v207" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-containment-lane-v207.json" in app_text
    assert "tower_receipt_chain_containment_lane_v207_json" in app_text
    assert "_pack_207_receipt_chain_containment_lane_v207_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-containment-lane-v207.json" in route_text
    assert "_pack_207_receipt_chain_containment_lane_v207_route_guard" in route_text

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
