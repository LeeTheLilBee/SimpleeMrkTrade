
"""
PACK 213 fast test - Receipt Chain Owner Review Drawer Preview.

Uses short safe module:
    tower.receipt_chain_owner_review_drawer_v213
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_213_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_owner_review_drawer_v213")
    payload = mod.build_receipt_chain_owner_review_drawer_v213_payload(force_refresh=True)

    assert payload["pack_number"] == 213
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-owner-review-drawer-v213.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-checkpoint-filter-search-v212.json"

    required_true = [
        "simulated_only",
        "owner_review_drawer_preview_only",
        "selected_result_drawer_preview_only",
        "owner_review_tab_preview_only",
        "owner_note_draft_preview_only",
        "owner_review_decision_preview_only",
        "owner_drawer_action_menu_preview_only",
        "checkpoint_filter_search_preview_only",
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
        "real_owner_note_saved",
        "real_owner_review_decision_saved",
        "real_drawer_selection_saved",
        "real_drawer_state_persisted",
        "real_owner_drawer_action_executed",
        "real_filter_preference_saved",
        "real_query_preset_saved",
        "real_search_state_persisted",
        "real_lookup_persisted",
        "real_archive_written",
        "real_archive_exported",
        "real_gateway_access_granted",
        "real_navigation_state_persisted",
        "real_saved_view_written",
        "real_user_preference_written",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["selected_result_drawer_count"] == 6
    assert summary["owner_review_tab_count"] == 6
    assert summary["owner_note_draft_count"] == 5
    assert summary["owner_review_decision_count"] == 5
    assert summary["owner_drawer_action_menu_item_count"] == 8
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 5
    assert summary["owner_drawer_queue_item_count"] == 5
    assert summary["real_owner_note_saved_count"] == 0
    assert summary["real_owner_review_decision_saved_count"] == 0
    assert summary["real_drawer_selection_saved_count"] == 0
    assert summary["real_drawer_state_persisted_count"] == 0
    assert summary["real_owner_drawer_action_executed_count"] == 0
    assert summary["real_archive_written_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_214"] is True
    assert summary["save_batch"] == "211-215"
    assert summary["save_after_pack"] == 215

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_212_ready",
        "pack_212_safe_to_continue",
        "has_selected_result_drawers",
        "has_owner_review_tabs",
        "has_owner_note_drafts",
        "has_owner_review_decisions",
        "has_owner_drawer_actions",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "has_owner_drawer_queue",
        "all_drawers_ready",
        "all_tabs_ready",
        "all_drafts_ready",
        "all_decisions_ready_or_blocked",
        "all_actions_ready_or_blocked",
        "all_queue_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_214",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_owner_review_drawer_preview_only",
        "no_real_owner_note_saved",
        "no_real_owner_review_decision_saved",
        "no_real_drawer_selection_saved",
        "no_real_drawer_state_persisted",
        "no_real_owner_drawer_action_executed",
        "no_real_archive_written",
        "no_real_evidence_exported",
        "no_real_raw_evidence_revealed",
        "all_note_saves_blocked",
        "all_decision_saves_blocked",
        "all_drawer_persistence_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_213_drawers_tabs_drafts_decisions_actions_and_queue():
    mod = importlib.import_module("tower.receipt_chain_owner_review_drawer_v213")
    payload = mod.build_receipt_chain_owner_review_drawer_v213_payload(force_refresh=True)

    drawers = payload["selected_result_drawer_previews"]
    tabs = payload["owner_review_tab_previews"]
    drafts = payload["owner_note_draft_previews"]
    decisions = payload["owner_review_decision_previews"]
    actions = payload["owner_drawer_action_menu_previews"]
    queue = payload["owner_drawer_queue_previews"]

    assert len(drawers) == 6
    assert len(tabs) == 6
    assert len(drafts) == 5
    assert len(decisions) == 5
    assert len(actions) == 8
    assert len(queue) == 5

    for item in drawers:
        assert item["selected_result_drawer_preview_id"].startswith("receipt_chain_owner_review_drawer_result_")
        assert item["selected_result_key"]
        assert item["label"]
        assert item["result_type"] in {"registry", "retrieval"}
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["drawer_section_count"] == 5
        assert item["drawer_sections"] == [
            "summary",
            "source_trace",
            "safety_flags",
            "owner_notes",
            "next_action_preview",
        ]
        assert item["raw_evidence_redacted"] is True
        assert item["drawer_selection_save_allowed_now"] is False
        assert item["drawer_state_persistence_allowed_now"] is False
        assert item["drawer_status"] == "receipt_chain_owner_review_selected_result_drawer_preview_ready"
        assert item["drawer_result_type"] == "tower_receipt_chain_owner_review_selected_result_drawer_preview"
        assert item["safe_preview_only"] is True
        assert item["real_drawer_selection_saved"] is False
        assert item["real_drawer_state_persisted"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_tabs = {
        "overview_tab",
        "safety_tab",
        "source_trace_tab",
        "owner_notes_tab",
        "decision_preview_tab",
        "next_step_tab",
    }

    assert {item["owner_review_tab_key"] for item in tabs} == expected_tabs

    for item in tabs:
        assert item["owner_review_tab_preview_id"].startswith("receipt_chain_owner_review_tab_")
        assert item["owner_review_tab_key"] in expected_tabs
        assert item["label"]
        assert item["tab_type"] in {
            "overview",
            "safety",
            "source_trace",
            "owner_notes",
            "decision",
            "next_step",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["linked_selected_result_count"] == 6
        assert len(item["linked_selected_result_keys"]) == 6
        assert item["tab_state_persistence_allowed_now"] is False
        assert item["tab_status"] == "receipt_chain_owner_review_tab_preview_ready"
        assert item["tab_result_type"] == "tower_receipt_chain_owner_review_tab_preview"
        assert item["safe_preview_only"] is True
        assert item["real_drawer_state_persisted"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_drafts = {
        "batch_status_note",
        "safety_confirmation_note",
        "lookup_context_note",
        "filter_result_note",
        "next_pack_note",
    }

    assert {item["owner_note_draft_key"] for item in drafts} == expected_drafts

    for item in drafts:
        assert item["owner_note_draft_preview_id"].startswith("receipt_chain_owner_review_note_draft_")
        assert item["owner_note_draft_key"] in expected_drafts
        assert item["label"]
        assert item["draft_type"] in {
            "status_note",
            "safety_note",
            "context_note",
            "result_note",
            "next_pack_note",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_selected_result_count"] >= 2
        assert len(item["linked_tab_keys"]) == 6
        assert "preview only" in item["draft_text_preview"].lower()
        assert item["note_save_allowed_now"] is False
        assert item["draft_status"] == "receipt_chain_owner_note_draft_preview_ready"
        assert item["draft_result_type"] == "tower_receipt_chain_owner_note_draft_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_note_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_decisions = {
        "mark_reviewed_preview",
        "hold_for_pack_214_preview",
        "request_more_context_preview",
        "blocked_save_review_decision",
        "blocked_execute_owner_action",
    }

    assert {item["owner_review_decision_key"] for item in decisions} == expected_decisions

    allowed_decisions = [item for item in decisions if item["allowed_in_preview"] is True]
    blocked_decisions = [item for item in decisions if item["blocked_in_preview"] is True]

    assert len(allowed_decisions) == 3
    assert len(blocked_decisions) == 2

    for item in decisions:
        assert item["owner_review_decision_preview_id"].startswith("receipt_chain_owner_review_decision_")
        assert item["owner_review_decision_key"] in expected_decisions
        assert item["label"]
        assert item["decision_type"] in {
            "reviewed",
            "hold",
            "request_context",
            "save_decision",
            "execute_owner_action",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_note_draft_count"] == 5
        assert item["linked_selected_result_count"] == 6
        assert item["decision_save_allowed_now"] is False
        assert item["decision_status"] in {
            "receipt_chain_owner_review_decision_preview_ready",
            "receipt_chain_owner_review_decision_preview_blocked",
        }
        assert item["decision_result_type"] == "tower_receipt_chain_owner_review_decision_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_review_decision_saved"] is False
        assert item["real_owner_action_executed"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_actions = {
        "preview_drawer_status",
        "preview_selected_result",
        "open_pack_212_filter_search",
        "blocked_save_owner_note",
        "blocked_save_review_decision",
        "blocked_persist_drawer_state",
        "blocked_export_drawer",
        "blocked_reveal_raw_evidence",
    }

    assert {item["owner_drawer_action_key"] for item in actions} == expected_actions

    allowed_actions = [item for item in actions if item["allowed_in_preview"] is True]
    blocked_actions = [item for item in actions if item["blocked_in_preview"] is True]

    assert len(allowed_actions) == 3
    assert len(blocked_actions) == 5

    assert {item["owner_drawer_action_key"] for item in allowed_actions} == {
        "preview_drawer_status",
        "preview_selected_result",
        "open_pack_212_filter_search",
    }

    assert {item["owner_drawer_action_key"] for item in blocked_actions} == {
        "blocked_save_owner_note",
        "blocked_save_review_decision",
        "blocked_persist_drawer_state",
        "blocked_export_drawer",
        "blocked_reveal_raw_evidence",
    }

    for item in actions:
        assert item["owner_drawer_action_menu_item_preview_id"].startswith("receipt_chain_owner_drawer_action_")
        assert item["selected_result_drawer_count"] == 6
        assert item["decision_preview_count"] == 5
        assert item["executes_real_owner_drawer_action"] is False
        assert item["action_status"] in {
            "receipt_chain_owner_drawer_action_preview_ready",
            "receipt_chain_owner_drawer_action_preview_blocked",
        }
        assert item["action_result_type"] == "tower_receipt_chain_owner_drawer_action_menu_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_drawer_action_executed"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_queue = {
        "review_selected_result_drawers",
        "review_owner_tabs",
        "review_note_drafts",
        "review_decision_previews",
        "prepare_pack_214_evidence_drawer",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_drawer_queue_item_preview_id"].startswith("receipt_chain_owner_drawer_queue_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {
            "drawer_review",
            "tab_review",
            "note_review",
            "decision_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_review_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_owner_drawer_queue_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_owner_drawer_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_owner_drawer_action_executed"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_213_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_owner_review_drawer_v213")
    payload = mod.build_receipt_chain_owner_review_drawer_v213_payload(force_refresh=True)

    safety = payload["owner_review_drawer_safety_summary"]
    checkpoint = payload["owner_review_drawer_checkpoint"]
    indexes = payload["owner_review_drawer_indexes"]

    assert safety["selected_result_drawer_count"] == 6
    assert safety["owner_review_tab_count"] == 6
    assert safety["owner_note_draft_count"] == 5
    assert safety["owner_review_decision_count"] == 5
    assert safety["owner_drawer_action_menu_item_count"] == 8
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 5
    assert safety["owner_drawer_queue_item_count"] == 5
    assert safety["real_owner_note_saved_count"] == 0
    assert safety["real_owner_review_decision_saved_count"] == 0
    assert safety["real_drawer_selection_saved_count"] == 0
    assert safety["real_drawer_state_persisted_count"] == 0
    assert safety["real_owner_drawer_action_executed_count"] == 0
    assert safety["real_archive_written_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_drawers_preview_only"] is True
    assert safety["all_tabs_preview_only"] is True
    assert safety["all_drafts_preview_only"] is True
    assert safety["all_decisions_preview_only"] is True
    assert safety["all_actions_preview_only"] is True
    assert safety["all_queue_preview_only"] is True
    assert safety["all_real_owner_drawer_persistence_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_owner_review_drawer_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_owner_review_drawer_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_owner_note_saved"] is False
    assert safety["real_owner_review_decision_saved"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_owner_review_drawer_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_owner_review_drawer_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_214"] is True
    assert checkpoint["save_batch"] == "211-215"
    assert checkpoint["save_after_pack"] == 215
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_owner_note_saved"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["selected_result_drawers_by_id"]
    assert indexes["selected_result_drawers_by_key"]
    assert indexes["owner_review_tabs_by_id"]
    assert indexes["owner_review_tabs_by_key"]
    assert indexes["owner_note_drafts_by_id"]
    assert indexes["owner_note_drafts_by_key"]
    assert indexes["owner_review_decisions_by_id"]
    assert indexes["owner_review_decisions_by_key"]
    assert indexes["owner_drawer_actions_by_id"]
    assert indexes["owner_drawer_actions_by_key"]
    assert indexes["owner_drawer_queue_by_id"]
    assert indexes["owner_drawer_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "overview_tab" in indexes["owner_review_tabs_by_key"]
    assert "safety_tab" in indexes["owner_review_tabs_by_key"]
    assert "batch_status_note" in indexes["owner_note_drafts_by_key"]
    assert "next_pack_note" in indexes["owner_note_drafts_by_key"]
    assert "mark_reviewed_preview" in indexes["owner_review_decisions_by_key"]
    assert "blocked_execute_owner_action" in indexes["owner_review_decisions_by_key"]
    assert "blocked_reveal_raw_evidence" in indexes["owner_drawer_actions_by_key"]
    assert "prepare_pack_214_evidence_drawer" in indexes["owner_drawer_queue_by_key"]
    assert checkpoint["owner_review_drawer_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_owner_review_drawer_v213_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 213
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-owner-review-drawer-v213.json"
    assert bridge["selected_result_drawer_count"] == 6
    assert bridge["owner_review_tab_count"] == 6
    assert bridge["owner_note_draft_count"] == 5
    assert bridge["owner_review_decision_count"] == 5
    assert bridge["owner_drawer_action_menu_item_count"] == 8
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 5
    assert bridge["owner_drawer_queue_item_count"] == 5
    assert bridge["real_owner_note_saved_count"] == 0
    assert bridge["real_owner_review_decision_saved_count"] == 0
    assert bridge["real_drawer_selection_saved_count"] == 0
    assert bridge["real_drawer_state_persisted_count"] == 0
    assert bridge["real_owner_drawer_action_executed_count"] == 0
    assert bridge["real_archive_written_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_214"] is True
    assert bridge["save_batch"] == "211-215"
    assert bridge["save_after_pack"] == 215

    action = mod.build_receipt_chain_owner_review_drawer_v213_quick_action()
    assert action["id"] == "receipt_chain_owner_review_drawer_v213"
    assert action["href"] == "/tower/receipt-chain-owner-review-drawer-v213.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_owner_review_drawer_v213_unified_owner_section()
    assert section["section_id"] == "receipt_chain_owner_review_drawer_v213"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-owner-review-drawer-v213.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_213_receipt_chain_owner_review_drawer_v213_status_bridge")
    tower_bridge = status.build_pack_213_receipt_chain_owner_review_drawer_v213_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_214"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_213_receipt_chain_owner_review_drawer_v213_quick_action")
    assert hasattr(qa, "append_pack_213_receipt_chain_owner_review_drawer_v213_quick_action")
    actions = qa.append_pack_213_receipt_chain_owner_review_drawer_v213_quick_action([])
    assert any(item.get("id") == "receipt_chain_owner_review_drawer_v213" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_213_receipt_chain_owner_review_drawer_v213_unified_section")
    assert hasattr(unified, "append_pack_213_receipt_chain_owner_review_drawer_v213_section")
    sections = unified.append_pack_213_receipt_chain_owner_review_drawer_v213_section([])
    assert any(item.get("section_id") == "receipt_chain_owner_review_drawer_v213" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-owner-review-drawer-v213.json" in app_text
    assert "tower_receipt_chain_owner_review_drawer_v213_json" in app_text
    assert "_pack_213_receipt_chain_owner_review_drawer_v213_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-owner-review-drawer-v213.json" in route_text
    assert "_pack_213_receipt_chain_owner_review_drawer_v213_route_guard" in route_text

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
