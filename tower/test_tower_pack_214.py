
"""
PACK 214 fast test - Receipt Chain Evidence Detail Drawer Preview.

Uses short safe module:
    tower.receipt_chain_evidence_detail_drawer_v214
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_214_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_evidence_detail_drawer_v214")
    payload = mod.build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh=True)

    assert payload["pack_number"] == 214
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-evidence-detail-drawer-v214.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-owner-review-drawer-v213.json"

    required_true = [
        "simulated_only",
        "evidence_detail_drawer_preview_only",
        "redacted_evidence_panel_preview_only",
        "evidence_source_trace_preview_only",
        "evidence_comparison_row_preview_only",
        "evidence_review_tab_preview_only",
        "evidence_action_menu_preview_only",
        "owner_evidence_review_queue_preview_only",
        "owner_review_drawer_preview_only",
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
        "real_evidence_panel_saved",
        "real_evidence_trace_saved",
        "real_evidence_comparison_saved",
        "real_evidence_review_saved",
        "real_evidence_action_executed",
        "real_owner_note_saved",
        "real_owner_review_decision_saved",
        "real_drawer_selection_saved",
        "real_drawer_state_persisted",
        "real_owner_drawer_action_executed",
        "real_archive_written",
        "real_archive_packet_written",
        "real_archive_packet_sealed",
        "real_archive_exported",
        "real_gateway_access_granted",
        "real_raw_evidence_revealed",
    ]

    for key in required_false:
        assert payload[key] is False, key

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["redacted_evidence_panel_count"] == 6
    assert summary["evidence_source_trace_card_count"] == 6
    assert summary["evidence_comparison_row_count"] == 8
    assert summary["evidence_review_tab_count"] == 6
    assert summary["evidence_action_menu_item_count"] == 8
    assert summary["allowed_preview_action_count"] == 3
    assert summary["blocked_action_count"] == 5
    assert summary["owner_evidence_review_queue_item_count"] == 5
    assert summary["raw_field_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["real_evidence_panel_saved_count"] == 0
    assert summary["real_evidence_trace_saved_count"] == 0
    assert summary["real_evidence_comparison_saved_count"] == 0
    assert summary["real_evidence_review_saved_count"] == 0
    assert summary["real_evidence_action_executed_count"] == 0
    assert summary["real_archive_written_count"] == 0
    assert summary["real_archive_packet_written_count"] == 0
    assert summary["real_archive_packet_sealed_count"] == 0
    assert summary["real_archive_exported_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["safe_to_continue_to_pack_215"] is True
    assert summary["save_batch"] == "211-215"
    assert summary["save_after_pack"] == 215

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_213_ready",
        "pack_213_safe_to_continue",
        "has_redacted_evidence_panels",
        "has_evidence_source_traces",
        "has_evidence_comparison_rows",
        "has_evidence_review_tabs",
        "has_evidence_actions",
        "has_allowed_preview_actions",
        "has_blocked_actions",
        "has_owner_evidence_queue",
        "no_raw_fields",
        "all_panels_ready",
        "all_traces_ready",
        "all_comparisons_ready",
        "all_tabs_ready",
        "all_actions_ready_or_blocked",
        "all_queue_blocked",
        "safety_summary_ready",
        "checkpoint_ready",
        "safe_to_continue_to_pack_215",
        "indexes_present",
        "checkpoint_index_present",
        "all_simulated_only",
        "all_evidence_detail_drawer_preview_only",
        "no_real_evidence_exported",
        "no_real_evidence_panel_saved",
        "no_real_evidence_trace_saved",
        "no_real_evidence_comparison_saved",
        "no_real_evidence_review_saved",
        "no_real_evidence_action_executed",
        "no_real_archive_written",
        "no_real_archive_packet_written",
        "no_real_archive_packet_sealed",
        "no_real_raw_evidence_revealed",
        "all_evidence_exports_blocked",
        "all_archive_writes_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_214_panels_traces_comparisons_tabs_actions_and_queue():
    mod = importlib.import_module("tower.receipt_chain_evidence_detail_drawer_v214")
    payload = mod.build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh=True)

    panels = payload["redacted_evidence_panel_previews"]
    traces = payload["evidence_source_trace_card_previews"]
    rows = payload["evidence_comparison_row_previews"]
    tabs = payload["evidence_review_tab_previews"]
    actions = payload["evidence_action_menu_previews"]
    queue = payload["owner_evidence_review_queue_previews"]

    assert len(panels) == 6
    assert len(traces) == 6
    assert len(rows) == 8
    assert len(tabs) == 6
    assert len(actions) == 8
    assert len(queue) == 5

    for item in panels:
        assert item["redacted_evidence_panel_preview_id"].startswith("receipt_chain_evidence_panel_")
        assert item["evidence_panel_key"].startswith("panel_")
        assert item["label"]
        assert item["panel_type"] in {"registry", "retrieval", "unknown"}
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["redacted_field_count"] == 8
        assert item["safe_field_count"] == 6
        assert item["raw_field_count"] == 0
        assert len(item["evidence_fields_preview"]) == 6
        assert item["raw_evidence_redacted"] is True
        assert item["evidence_panel_save_allowed_now"] is False
        assert item["panel_status"] == "receipt_chain_redacted_evidence_panel_preview_ready"
        assert item["panel_result_type"] == "tower_receipt_chain_redacted_evidence_panel_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_panel_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_trace_keys = {
        "source_pack_212_trace",
        "pack_213_drawer_trace",
        "result_selection_trace",
        "owner_note_draft_trace",
        "decision_preview_trace",
        "raw_redaction_trace",
    }

    assert {item["evidence_source_trace_key"] for item in traces} == expected_trace_keys

    for item in traces:
        assert item["evidence_source_trace_card_preview_id"].startswith("receipt_chain_evidence_source_trace_")
        assert item["evidence_source_trace_key"] in expected_trace_keys
        assert item["label"]
        assert item["trace_type"] in {
            "source_pack",
            "owner_drawer",
            "selection",
            "note_draft",
            "decision",
            "redaction",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["linked_evidence_panel_count"] == 6
        assert len(item["linked_evidence_panel_keys"]) == 6
        assert "/tower/receipt-chain-checkpoint-filter-search-v212.json" in item["source_endpoint_chain"]
        assert "/tower/receipt-chain-owner-review-drawer-v213.json" in item["source_endpoint_chain"]
        assert "/tower/receipt-chain-evidence-detail-drawer-v214.json" in item["source_endpoint_chain"]
        assert item["trace_save_allowed_now"] is False
        assert item["trace_status"] == "receipt_chain_evidence_source_trace_card_preview_ready"
        assert item["trace_result_type"] == "tower_receipt_chain_evidence_source_trace_card_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_trace_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_row_keys = {
        "readiness_compare",
        "safety_compare",
        "raw_reveal_compare",
        "export_compare",
        "archive_write_compare",
        "owner_action_compare",
        "drawer_state_compare",
        "next_pack_compare",
    }

    assert {item["evidence_comparison_row_key"] for item in rows} == expected_row_keys

    for item in rows:
        assert item["evidence_comparison_row_preview_id"].startswith("receipt_chain_evidence_comparison_")
        assert item["evidence_comparison_row_key"] in expected_row_keys
        assert item["label"]
        assert item["comparison_type"] in {
            "readiness",
            "safety",
            "raw_evidence",
            "export",
            "archive",
            "owner_action",
            "drawer_state",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6, 7, 8}
        assert item["comparison_result"] == "match"
        assert item["linked_trace_count"] == 6
        assert item["comparison_save_allowed_now"] is False
        assert item["row_status"] == "receipt_chain_evidence_comparison_row_preview_ready"
        assert item["row_result_type"] == "tower_receipt_chain_evidence_comparison_row_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_comparison_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_tab_keys = {
        "evidence_overview_tab",
        "redaction_tab",
        "source_trace_tab",
        "comparison_tab",
        "owner_review_tab",
        "next_pack_tab",
    }

    assert {item["evidence_review_tab_key"] for item in tabs} == expected_tab_keys

    for item in tabs:
        assert item["evidence_review_tab_preview_id"].startswith("receipt_chain_evidence_review_tab_")
        assert item["evidence_review_tab_key"] in expected_tab_keys
        assert item["label"]
        assert item["tab_type"] in {
            "overview",
            "redaction",
            "source_trace",
            "comparison",
            "owner_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5, 6}
        assert item["linked_preview_item_count"] >= 1
        assert item["tab_state_persistence_allowed_now"] is False
        assert item["tab_status"] == "receipt_chain_evidence_review_tab_preview_ready"
        assert item["tab_result_type"] == "tower_receipt_chain_evidence_review_tab_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_review_saved"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_actions = {
        "preview_evidence_status",
        "preview_redacted_panels",
        "open_pack_213_owner_drawer",
        "blocked_export_evidence",
        "blocked_write_archive_packet",
        "blocked_seal_archive_packet",
        "blocked_save_evidence_review",
        "blocked_reveal_raw_evidence",
    }

    assert {item["evidence_action_key"] for item in actions} == expected_actions

    allowed_actions = [item for item in actions if item["allowed_in_preview"] is True]
    blocked_actions = [item for item in actions if item["blocked_in_preview"] is True]

    assert len(allowed_actions) == 3
    assert len(blocked_actions) == 5

    assert {item["evidence_action_key"] for item in allowed_actions} == {
        "preview_evidence_status",
        "preview_redacted_panels",
        "open_pack_213_owner_drawer",
    }

    assert {item["evidence_action_key"] for item in blocked_actions} == {
        "blocked_export_evidence",
        "blocked_write_archive_packet",
        "blocked_seal_archive_packet",
        "blocked_save_evidence_review",
        "blocked_reveal_raw_evidence",
    }

    for item in actions:
        assert item["evidence_action_menu_item_preview_id"].startswith("receipt_chain_evidence_action_")
        assert item["redacted_evidence_panel_count"] == 6
        assert item["evidence_comparison_row_count"] == 8
        assert item["executes_real_evidence_action"] is False
        assert item["action_status"] in {
            "receipt_chain_evidence_action_preview_ready",
            "receipt_chain_evidence_action_preview_blocked",
        }
        assert item["action_result_type"] == "tower_receipt_chain_evidence_action_menu_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_action_executed"] is False
        assert item["real_raw_evidence_revealed"] is False

    expected_queue = {
        "review_redacted_evidence_panels",
        "review_source_trace_cards",
        "review_comparison_rows",
        "review_blocked_evidence_actions",
        "prepare_pack_215_batch_checkpoint",
    }

    assert {item["queue_key"] for item in queue} == expected_queue

    for item in queue:
        assert item["owner_evidence_queue_item_preview_id"].startswith("receipt_chain_owner_evidence_queue_")
        assert item["queue_key"] in expected_queue
        assert item["label"]
        assert item["queue_type"] in {
            "panel_review",
            "trace_review",
            "comparison_review",
            "action_review",
            "next_pack",
        }
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["linked_preview_item_count"] >= 0
        assert item["owner_review_allowed_now"] is False
        assert item["queue_status"] == "receipt_chain_owner_evidence_queue_preview_blocked"
        assert item["queue_result_type"] == "tower_receipt_chain_owner_evidence_queue_preview"
        assert item["safe_preview_only"] is True
        assert item["real_evidence_review_saved"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_214_safety_checkpoint_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_evidence_detail_drawer_v214")
    payload = mod.build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh=True)

    safety = payload["evidence_detail_drawer_safety_summary"]
    checkpoint = payload["evidence_detail_drawer_checkpoint"]
    indexes = payload["evidence_detail_drawer_indexes"]

    assert safety["redacted_evidence_panel_count"] == 6
    assert safety["evidence_source_trace_card_count"] == 6
    assert safety["evidence_comparison_row_count"] == 8
    assert safety["evidence_review_tab_count"] == 6
    assert safety["evidence_action_menu_item_count"] == 8
    assert safety["allowed_preview_action_count"] == 3
    assert safety["blocked_action_count"] == 5
    assert safety["owner_evidence_review_queue_item_count"] == 5
    assert safety["raw_field_count"] == 0
    assert safety["real_evidence_exported_count"] == 0
    assert safety["real_evidence_panel_saved_count"] == 0
    assert safety["real_evidence_trace_saved_count"] == 0
    assert safety["real_evidence_comparison_saved_count"] == 0
    assert safety["real_evidence_review_saved_count"] == 0
    assert safety["real_evidence_action_executed_count"] == 0
    assert safety["real_archive_written_count"] == 0
    assert safety["real_archive_packet_written_count"] == 0
    assert safety["real_archive_packet_sealed_count"] == 0
    assert safety["real_archive_exported_count"] == 0
    assert safety["raw_evidence_revealed_count"] == 0
    assert safety["all_panels_preview_only"] is True
    assert safety["all_traces_preview_only"] is True
    assert safety["all_comparisons_preview_only"] is True
    assert safety["all_tabs_preview_only"] is True
    assert safety["all_actions_preview_only"] is True
    assert safety["all_queue_preview_only"] is True
    assert safety["all_raw_fields_redacted"] is True
    assert safety["all_real_evidence_writes_blocked"] is True
    assert safety["summary_status"] == "receipt_chain_evidence_detail_drawer_safety_summary_preview_ready"
    assert safety["summary_result_type"] == "tower_receipt_chain_evidence_detail_drawer_safety_summary_preview"
    assert safety["safe_preview_only"] is True
    assert safety["real_evidence_exported"] is False
    assert safety["real_archive_written"] is False
    assert safety["real_raw_evidence_revealed"] is False

    assert checkpoint["checkpoint_ok"] is True
    assert checkpoint["checkpoint_status"] == "receipt_chain_evidence_detail_drawer_checkpoint_preview_ready"
    assert checkpoint["checkpoint_result_type"] == "tower_receipt_chain_evidence_detail_drawer_checkpoint_preview"
    assert checkpoint["safe_to_continue_to_pack_215"] is True
    assert checkpoint["save_batch"] == "211-215"
    assert checkpoint["save_after_pack"] == 215
    assert checkpoint["safe_preview_only"] is True
    assert checkpoint["real_evidence_exported"] is False
    assert checkpoint["real_raw_evidence_revealed"] is False

    assert indexes["redacted_evidence_panels_by_id"]
    assert indexes["redacted_evidence_panels_by_key"]
    assert indexes["evidence_source_traces_by_id"]
    assert indexes["evidence_source_traces_by_key"]
    assert indexes["evidence_comparison_rows_by_id"]
    assert indexes["evidence_comparison_rows_by_key"]
    assert indexes["evidence_review_tabs_by_id"]
    assert indexes["evidence_review_tabs_by_key"]
    assert indexes["evidence_actions_by_id"]
    assert indexes["evidence_actions_by_key"]
    assert indexes["owner_evidence_queue_by_id"]
    assert indexes["owner_evidence_queue_by_key"]
    assert indexes["checkpoint_by_id"]

    assert "source_pack_212_trace" in indexes["evidence_source_traces_by_key"]
    assert "raw_redaction_trace" in indexes["evidence_source_traces_by_key"]
    assert "readiness_compare" in indexes["evidence_comparison_rows_by_key"]
    assert "next_pack_compare" in indexes["evidence_comparison_rows_by_key"]
    assert "evidence_overview_tab" in indexes["evidence_review_tabs_by_key"]
    assert "next_pack_tab" in indexes["evidence_review_tabs_by_key"]
    assert "blocked_reveal_raw_evidence" in indexes["evidence_actions_by_key"]
    assert "prepare_pack_215_batch_checkpoint" in indexes["owner_evidence_queue_by_key"]
    assert checkpoint["evidence_detail_drawer_checkpoint_id"] in indexes["checkpoint_by_id"]

    bridge = mod.build_receipt_chain_evidence_detail_drawer_v214_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 214
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-evidence-detail-drawer-v214.json"
    assert bridge["redacted_evidence_panel_count"] == 6
    assert bridge["evidence_source_trace_card_count"] == 6
    assert bridge["evidence_comparison_row_count"] == 8
    assert bridge["evidence_review_tab_count"] == 6
    assert bridge["evidence_action_menu_item_count"] == 8
    assert bridge["allowed_preview_action_count"] == 3
    assert bridge["blocked_action_count"] == 5
    assert bridge["owner_evidence_review_queue_item_count"] == 5
    assert bridge["raw_field_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["real_evidence_panel_saved_count"] == 0
    assert bridge["real_evidence_trace_saved_count"] == 0
    assert bridge["real_evidence_comparison_saved_count"] == 0
    assert bridge["real_evidence_review_saved_count"] == 0
    assert bridge["real_evidence_action_executed_count"] == 0
    assert bridge["real_archive_written_count"] == 0
    assert bridge["real_archive_packet_written_count"] == 0
    assert bridge["real_archive_packet_sealed_count"] == 0
    assert bridge["real_archive_exported_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["safe_to_continue_to_pack_215"] is True
    assert bridge["save_batch"] == "211-215"
    assert bridge["save_after_pack"] == 215

    action = mod.build_receipt_chain_evidence_detail_drawer_v214_quick_action()
    assert action["id"] == "receipt_chain_evidence_detail_drawer_v214"
    assert action["href"] == "/tower/receipt-chain-evidence-detail-drawer-v214.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_evidence_detail_drawer_v214_unified_owner_section()
    assert section["section_id"] == "receipt_chain_evidence_detail_drawer_v214"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-evidence-detail-drawer-v214.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_214_receipt_chain_evidence_detail_drawer_v214_status_bridge")
    tower_bridge = status.build_pack_214_receipt_chain_evidence_detail_drawer_v214_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100
    assert tower_bridge["safe_to_continue_to_pack_215"] is True

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_214_receipt_chain_evidence_detail_drawer_v214_quick_action")
    assert hasattr(qa, "append_pack_214_receipt_chain_evidence_detail_drawer_v214_quick_action")
    actions = qa.append_pack_214_receipt_chain_evidence_detail_drawer_v214_quick_action([])
    assert any(item.get("id") == "receipt_chain_evidence_detail_drawer_v214" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_214_receipt_chain_evidence_detail_drawer_v214_unified_section")
    assert hasattr(unified, "append_pack_214_receipt_chain_evidence_detail_drawer_v214_section")
    sections = unified.append_pack_214_receipt_chain_evidence_detail_drawer_v214_section([])
    assert any(item.get("section_id") == "receipt_chain_evidence_detail_drawer_v214" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-evidence-detail-drawer-v214.json" in app_text
    assert "tower_receipt_chain_evidence_detail_drawer_v214_json" in app_text
    assert "_pack_214_receipt_chain_evidence_detail_drawer_v214_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-evidence-detail-drawer-v214.json" in route_text
    assert "_pack_214_receipt_chain_evidence_detail_drawer_v214_route_guard" in route_text

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
