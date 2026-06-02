
"""
PACK 204 fast test - Receipt Chain Recheck / Expiration Handoff Preview.

Uses short safe module:
    tower.receipt_chain_recheck_expiration_handoff_v204
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_204_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_recheck_expiration_handoff_v204")
    payload = mod.build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh=True)

    assert payload["pack_number"] == 204
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-recheck-expiration-handoff-v204.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-evidence-packet-v203.json"

    required_true = [
        "simulated_only",
        "recheck_expiration_handoff_preview_only",
        "recheck_hook_preview_only",
        "expiration_trigger_preview_only",
        "renewal_trigger_preview_only",
        "freshness_lane_preview_only",
        "owner_followup_queue_preview_only",
        "evidence_packet_preview_only",
        "evidence_bundle_preview_only",
        "export_blocked",
        "raw_evidence_redacted",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_recheck_executed",
        "real_renewal_executed",
        "real_expiration_enforced",
        "real_owner_followup_executed",
        "real_evidence_exported",
        "real_export_request_created",
        "real_packet_written",
        "real_packet_sealed",
        "real_saved_view_written",
        "real_user_preference_written",
        "real_action_executed",
        "real_handoff_executed",
        "real_owner_action_executed",
        "real_filter_preference_saved",
        "real_navigation_state_persisted",
        "real_drawer_selection_saved",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["freshness_lane_count"] == 5
    assert summary["recheck_hook_count"] == 4
    assert summary["expiration_trigger_count"] == 4
    assert summary["renewal_trigger_count"] == 3
    assert summary["owner_followup_queue_item_count"] == 5
    assert summary["real_recheck_executed_count"] == 0
    assert summary["real_renewal_executed_count"] == 0
    assert summary["real_expiration_enforced_count"] == 0
    assert summary["real_owner_followup_executed_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_205"] is True
    assert summary["save_batch"] == "201-205"
    assert summary["save_after_pack"] == 205

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_203_ready",
        "has_freshness_lanes",
        "has_recheck_hooks",
        "has_expiration_triggers",
        "has_renewal_triggers",
        "has_owner_followup_queue",
        "all_freshness_lanes_ready",
        "all_recheck_hooks_blocked",
        "all_expiration_triggers_blocked",
        "all_renewal_triggers_blocked",
        "all_owner_followups_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_205",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_recheck_expiration_preview_only",
        "no_real_recheck_executed",
        "no_real_renewal_executed",
        "no_real_expiration_enforced",
        "no_real_owner_followup_executed",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_recheck_execution_blocked",
        "all_renewal_execution_blocked",
        "all_expiration_enforcement_blocked",
        "all_owner_followup_execution_blocked",
        "all_evidence_export_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_204_lanes_hooks_expirations_renewals_and_queue():
    mod = importlib.import_module("tower.receipt_chain_recheck_expiration_handoff_v204")
    payload = mod.build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh=True)

    lanes = payload["freshness_lane_previews"]
    hooks = payload["recheck_handoff_hook_previews"]
    expirations = payload["expiration_trigger_previews"]
    renewals = payload["renewal_trigger_previews"]
    queue = payload["owner_followup_queue_previews"]

    assert len(lanes) == 5
    assert len(hooks) == 4
    assert len(expirations) == 4
    assert len(renewals) == 3
    assert len(queue) == 5

    expected_lanes = {
        "fresh_packet_sections",
        "fresh_bundle_packets",
        "recheck_required_later",
        "expiration_review_later",
        "renewal_candidate_later",
    }

    assert {lane["freshness_lane_key"] for lane in lanes} == expected_lanes

    for lane in lanes:
        assert lane["freshness_lane_preview_id"].startswith("receipt_chain_freshness_lane_")
        assert lane["freshness_lane_key"] in expected_lanes
        assert lane["label"]
        assert lane["description"]
        assert lane["freshness_state"] in {
            "fresh",
            "future_recheck",
            "future_expiration_review",
            "future_renewal_candidate",
        }
        assert lane["sequence"] in {1, 2, 3, 4, 5}
        assert lane["matched_item_count"] >= 0
        assert lane["lane_status"] == "receipt_chain_freshness_lane_preview_ready"
        assert lane["lane_result_type"] == "tower_receipt_chain_recheck_expiration_freshness_lane_preview"
        assert lane["safe_preview_only"] is True

        assert lane["simulated_only"] is True
        assert lane["recheck_expiration_handoff_preview_only"] is True
        assert lane["freshness_lane_preview_only"] is True
        assert lane["real_recheck_executed"] is False
        assert lane["real_renewal_executed"] is False
        assert lane["real_expiration_enforced"] is False
        assert lane["real_owner_followup_executed"] is False
        assert lane["real_evidence_exported"] is False
        assert lane["real_raw_evidence_revealed"] is False
        assert lane["recheck_execution_allowed_now"] is False
        assert lane["renewal_execution_allowed_now"] is False
        assert lane["expiration_enforcement_allowed_now"] is False
        assert lane["owner_followup_execution_allowed_now"] is False
        assert lane["evidence_export_allowed_now"] is False
        assert lane["raw_evidence_reveal_allowed"] is False

    lane_by_key = {lane["freshness_lane_key"]: lane for lane in lanes}
    assert lane_by_key["fresh_packet_sections"]["matched_item_count"] == 6
    assert lane_by_key["fresh_bundle_packets"]["matched_item_count"] == 3

    expected_hooks = {
        "owner_recheck_before_export",
        "owner_recheck_before_gateway_use",
        "owner_recheck_before_policy_reuse",
        "owner_recheck_before_archive_packet",
    }

    assert {hook["recheck_hook_key"] for hook in hooks} == expected_hooks

    for hook in hooks:
        assert hook["recheck_handoff_hook_preview_id"].startswith("receipt_chain_recheck_hook_")
        assert hook["recheck_hook_key"] in expected_hooks
        assert hook["label"]
        assert hook["target_area"] in {"export", "gateway", "policy", "archive"}
        assert hook["sequence"] in {1, 2, 3, 4}
        assert len(hook["source_freshness_lane_keys"]) == 5
        assert hook["recheck_allowed_now"] is False
        assert hook["recheck_status"] == "receipt_chain_recheck_handoff_hook_preview_blocked"
        assert hook["recheck_result_type"] == "tower_receipt_chain_recheck_handoff_hook_preview"
        assert hook["safe_preview_only"] is True
        assert hook["real_recheck_executed"] is False
        assert hook["recheck_execution_allowed_now"] is False
        assert hook["real_raw_evidence_revealed"] is False

    expected_expirations = {
        "packet_section_stale_later",
        "bundle_packet_stale_later",
        "export_request_stale_later",
        "owner_review_stale_later",
    }

    assert {item["expiration_trigger_key"] for item in expirations} == expected_expirations

    for item in expirations:
        assert item["expiration_trigger_preview_id"].startswith("receipt_chain_expiration_trigger_")
        assert item["expiration_trigger_key"] in expected_expirations
        assert item["label"]
        assert item["trigger_type"] in {"section_age", "bundle_age", "export_age", "review_age"}
        assert item["preview_days_until_review"] in {7, 14, 30}
        assert item["sequence"] in {1, 2, 3, 4}
        assert len(item["source_section_keys"]) == 6
        assert item["expiration_enforcement_allowed_now"] is False
        assert item["expiration_status"] == "receipt_chain_expiration_trigger_preview_blocked"
        assert item["expiration_result_type"] == "tower_receipt_chain_expiration_trigger_preview"
        assert item["safe_preview_only"] is True
        assert item["real_expiration_enforced"] is False

    expected_renewals = {
        "renew_owner_review_packet",
        "renew_audit_preview_packet",
        "renew_next_batch_packet",
    }

    assert {item["renewal_trigger_key"] for item in renewals} == expected_renewals

    for item in renewals:
        assert item["renewal_trigger_preview_id"].startswith("receipt_chain_renewal_trigger_")
        assert item["renewal_trigger_key"] in expected_renewals
        assert item["label"]
        assert item["packet_key"] in {"owner_review_packet", "audit_preview_packet", "next_batch_packet"}
        assert item["source_packet_available"] is True
        assert item["sequence"] in {1, 2, 3}
        assert item["renewal_allowed_now"] is False
        assert item["renewal_status"] == "receipt_chain_renewal_trigger_preview_blocked"
        assert item["renewal_result_type"] == "tower_receipt_chain_renewal_trigger_preview"
        assert item["safe_preview_only"] is True
        assert item["real_renewal_executed"] is False

    expected_queue = {
        "review_recheck_hooks",
        "review_expiration_triggers",
        "review_renewal_triggers",
        "confirm_no_real_enforcement",
        "prepare_pack_205_checkpoint",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_followup_queue_item_preview_id"].startswith("receipt_chain_owner_followup_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {"recheck", "expiration", "renewal", "safety", "checkpoint"}
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_followup_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_owner_followup_queue_item_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_owner_followup_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_followup_executed"] is False


def test_pack_204_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_recheck_expiration_handoff_v204")
    payload = mod.build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh=True)

    safety = payload["recheck_expiration_safety_summary"]
    checkpoint = payload["recheck_expiration_handoff_checkpoint"]
    indexes = payload["recheck_expiration_handoff_indexes"]

    assert safety["recheck_expiration_safety_summary_id"].startswith("receipt_chain_recheck_expiration_safety_")
    assert safety["freshness_lane_count"] == 5
    assert safety["recheck_hook_count"] == 4
    assert safety["expiration_trigger_count"] == 4
    assert safety["renewal_trigger_count"] == 3
    assert safety["owner_followup_queue_item_count"] == 5
    assert safety["real_recheck_executed_count"] == 0
    assert safety["real_renewal_executed_count"] == 0
    assert safety["real_expiration_enforced_count"] == 0
    assert safety["real_owner_followup_executed_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_rechecks_blocked"] is True
    assert safety["all_renewals_blocked"] is True
    assert safety["all_expirations_blocked"] is True
    assert safety["all_followups_blocked"] is True
    assert safety["all_raw_reveals_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_recheck_expiration_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_recheck_expiration_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_recheck_executed"] is False
    assert safety["real_renewal_executed"] is False
    assert safety["real_expiration_enforced"] is False
    assert safety["real_owner_followup_executed"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["recheck_expiration_handoff_checkpoint_id"].startswith("receipt_chain_recheck_expiration_checkpoint_")
    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_recheck_expiration_handoff_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_recheck_expiration_handoff_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_205"] is True
    assert checkpoint["save_batch"] == "201-205"
    assert checkpoint["save_after_pack"] == 205
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_recheck_executed"] is False
    assert checkpoint["real_renewal_executed"] is False
    assert checkpoint["real_expiration_enforced"] is False
    assert checkpoint["real_owner_followup_executed"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["freshness_lanes_by_id"]
    assert indexes["freshness_lanes_by_key"]
    assert indexes["recheck_hooks_by_id"]
    assert indexes["recheck_hooks_by_key"]
    assert indexes["expiration_triggers_by_id"]
    assert indexes["expiration_triggers_by_key"]
    assert indexes["renewal_triggers_by_id"]
    assert indexes["renewal_triggers_by_key"]
    assert indexes["owner_followup_queue_by_id"]
    assert indexes["owner_followup_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "fresh_packet_sections" in indexes["freshness_lanes_by_key"]
    assert "owner_recheck_before_export" in indexes["recheck_hooks_by_key"]
    assert "packet_section_stale_later" in indexes["expiration_triggers_by_key"]
    assert "renew_owner_review_packet" in indexes["renewal_triggers_by_key"]
    assert "prepare_pack_205_checkpoint" in indexes["owner_followup_queue_by_key"]
    assert checkpoint["recheck_expiration_handoff_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_recheck_expiration_handoff_v204_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 204
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-recheck-expiration-handoff-v204.json"
    assert bridge["freshness_lane_count"] == 5
    assert bridge["recheck_hook_count"] == 4
    assert bridge["expiration_trigger_count"] == 4
    assert bridge["renewal_trigger_count"] == 3
    assert bridge["owner_followup_queue_item_count"] == 5
    assert bridge["real_recheck_executed_count"] == 0
    assert bridge["real_renewal_executed_count"] == 0
    assert bridge["real_expiration_enforced_count"] == 0
    assert bridge["real_owner_followup_executed_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_205"] is True
    assert bridge["save_batch"] == "201-205"
    assert bridge["save_after_pack"] == 205

    action = mod.build_receipt_chain_recheck_expiration_handoff_v204_quick_action()
    assert action["id"] == "receipt_chain_recheck_expiration_handoff_v204"
    assert action["href"] == "/tower/receipt-chain-recheck-expiration-handoff-v204.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_recheck_expiration_handoff_v204_unified_owner_section()
    assert section["section_id"] == "receipt_chain_recheck_expiration_handoff_v204"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-recheck-expiration-handoff-v204.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_204_receipt_chain_recheck_expiration_handoff_v204_status_bridge")
    tower_bridge = status.build_pack_204_receipt_chain_recheck_expiration_handoff_v204_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_205"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_204_receipt_chain_recheck_expiration_handoff_v204_quick_action")
    assert hasattr(qa, "append_pack_204_receipt_chain_recheck_expiration_handoff_v204_quick_action")
    actions = qa.append_pack_204_receipt_chain_recheck_expiration_handoff_v204_quick_action([])
    assert any(item.get("id") == "receipt_chain_recheck_expiration_handoff_v204" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_204_receipt_chain_recheck_expiration_handoff_v204_unified_section")
    assert hasattr(unified, "append_pack_204_receipt_chain_recheck_expiration_handoff_v204_section")
    sections = unified.append_pack_204_receipt_chain_recheck_expiration_handoff_v204_section([])
    assert any(item.get("section_id") == "receipt_chain_recheck_expiration_handoff_v204" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-recheck-expiration-handoff-v204.json" in app_text
    assert "tower_receipt_chain_recheck_expiration_handoff_v204_json" in app_text
    assert "_pack_204_receipt_chain_recheck_expiration_handoff_v204_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-recheck-expiration-handoff-v204.json" in route_text
    assert "_pack_204_receipt_chain_recheck_expiration_handoff_v204_route_guard" in route_text

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
