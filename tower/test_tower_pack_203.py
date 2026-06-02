
"""
PACK 203 fast test - Receipt Chain Evidence Bundle Packet Preview.

Uses short safe module:
    tower.receipt_chain_evidence_packet_v203
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_203_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.receipt_chain_evidence_packet_v203")
    payload = mod.build_receipt_chain_evidence_packet_v203_payload(force_refresh=True)

    assert payload["pack_number"] == 203
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/receipt-chain-evidence-packet-v203.json"
    assert payload["source_endpoint"] == "/tower/receipt-chain-handoff-saved-views-v202.json"

    required_true = [
        "simulated_only",
        "evidence_packet_preview_only",
        "evidence_bundle_preview_only",
        "packet_section_preview_only",
        "export_request_preview_only",
        "export_blocked",
        "raw_evidence_redacted",
        "saved_view_preview_only",
        "filter_preset_preview_only",
        "cached_non_recursive",
    ]

    for key in required_true:
        assert payload[key] is True, key

    required_false = [
        "real_export_request_created",
        "real_evidence_exported",
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
    assert summary["packet_section_count"] == 6
    assert summary["evidence_bundle_packet_count"] == 3
    assert summary["export_request_preview_count"] == 3
    assert summary["owner_review_checklist_item_count"] == 5
    assert summary["redacted_item_count"] >= 1
    assert summary["raw_item_count"] == 0
    assert summary["real_export_request_created_count"] == 0
    assert summary["real_evidence_exported_count"] == 0
    assert summary["real_packet_written_count"] == 0
    assert summary["real_packet_sealed_count"] == 0
    assert summary["raw_evidence_revealed_count"] == 0
    assert summary["save_batch"] == "201-205"
    assert summary["save_after_pack"] == 205

    checks = payload["readiness_checks"]
    required_checks = [
        "pack_202_ready",
        "has_packet_sections",
        "has_evidence_bundle_packets",
        "has_export_request_previews",
        "has_owner_review_checklist",
        "all_packet_sections_ready",
        "all_packets_ready",
        "all_exports_blocked",
        "all_checklist_items_ready",
        "integrity_summary_ready",
        "indexes_present",
        "packet_indexes_present",
        "export_indexes_present",
        "all_simulated_only",
        "all_evidence_packet_preview_only",
        "all_exports_preview_only",
        "all_exports_blocked",
        "all_raw_evidence_redacted",
        "no_real_export_request_created",
        "no_real_evidence_exported",
        "no_real_packet_written",
        "no_real_packet_sealed",
        "no_real_saved_view_written",
        "no_real_user_preference_written",
        "no_real_action_executed",
        "no_real_raw_evidence_revealed",
        "all_evidence_export_blocked",
        "all_raw_evidence_reveal_blocked",
        "cached_non_recursive",
    ]

    for key in required_checks:
        assert checks[key] is True, key


def test_pack_203_packet_sections_packets_exports_and_checklist():
    mod = importlib.import_module("tower.receipt_chain_evidence_packet_v203")
    payload = mod.build_receipt_chain_evidence_packet_v203_payload(force_refresh=True)

    sections = payload["evidence_packet_sections"]
    packets = payload["evidence_bundle_packet_previews"]
    exports = payload["evidence_export_request_previews"]
    checklist = payload["owner_review_checklist"]

    assert len(sections) == 6
    assert len(packets) == 3
    assert len(exports) == 3
    assert len(checklist) == 5

    expected_sections = {
        "handoff_overview",
        "route_packet",
        "owner_action_packet",
        "evidence_map_packet",
        "next_batch_packet",
        "safety_packet",
    }

    section_keys = {section["section_key"] for section in sections}
    assert section_keys == expected_sections

    for section in sections:
        assert section["evidence_packet_section_id"].startswith("receipt_chain_evidence_packet_section_")
        assert section["section_key"] in expected_sections
        assert section["label"]
        assert section["description"]
        assert section["sequence"] in {1, 2, 3, 4, 5, 6}
        assert section["source_saved_view_id"] == "default_full_handoff"
        assert section["source_filter_preset_id"] == "all_handoff_items"
        assert section["redacted_item_count"] >= 0
        assert section["raw_item_count"] == 0
        assert section["raw_evidence_redacted"] is True
        assert section["section_status"] == "receipt_chain_evidence_packet_section_preview_ready"
        assert section["section_result_type"] == "tower_receipt_chain_evidence_packet_section_preview"
        assert section["safe_preview_only"] is True

        assert section["simulated_only"] is True
        assert section["evidence_packet_preview_only"] is True
        assert section["packet_section_preview_only"] is True
        assert section["export_request_preview_only"] is True
        assert section["export_blocked"] is True
        assert section["real_export_request_created"] is False
        assert section["real_evidence_exported"] is False
        assert section["real_packet_written"] is False
        assert section["real_packet_sealed"] is False
        assert section["real_saved_view_written"] is False
        assert section["real_user_preference_written"] is False
        assert section["real_action_executed"] is False
        assert section["real_raw_evidence_revealed"] is False
        assert section["evidence_export_allowed_now"] is False
        assert section["raw_evidence_reveal_allowed"] is False
        assert section["raw_evidence_lookup_allowed"] is False

    section_by_key = {section["section_key"]: section for section in sections}
    assert section_by_key["handoff_overview"]["redacted_item_count"] == 5
    assert section_by_key["route_packet"]["redacted_item_count"] == 5
    assert section_by_key["owner_action_packet"]["redacted_item_count"] == 6
    assert section_by_key["evidence_map_packet"]["redacted_item_count"] == 4
    assert section_by_key["next_batch_packet"]["redacted_item_count"] == 5
    assert section_by_key["safety_packet"]["redacted_item_count"] == 8

    expected_packets = {"owner_review_packet", "audit_preview_packet", "next_batch_packet"}
    packet_keys = {packet["packet_key"] for packet in packets}
    assert packet_keys == expected_packets

    for packet in packets:
        assert packet["evidence_bundle_packet_preview_id"].startswith("receipt_chain_evidence_bundle_packet_")
        assert packet["packet_key"] in expected_packets
        assert packet["label"]
        assert packet["sequence"] in {1, 2, 3}
        assert packet["section_count"] == len(packet["section_keys"])
        assert packet["section_count"] == len(packet["evidence_packet_section_ids"])
        assert packet["redacted_item_count"] >= 1
        assert packet["raw_item_count"] == 0
        assert packet["raw_evidence_redacted"] is True
        assert packet["export_allowed_now"] is False
        assert packet["packet_status"] == "receipt_chain_evidence_bundle_packet_preview_ready"
        assert packet["packet_result_type"] == "tower_receipt_chain_evidence_bundle_packet_preview"
        assert packet["safe_preview_only"] is True
        assert packet["real_export_request_created"] is False
        assert packet["real_evidence_exported"] is False
        assert packet["real_packet_written"] is False
        assert packet["real_packet_sealed"] is False
        assert packet["real_raw_evidence_revealed"] is False

    export_by_packet = {export["packet_key"]: export for export in exports}
    assert set(export_by_packet) == expected_packets

    for export in exports:
        assert export["evidence_export_request_preview_id"].startswith("receipt_chain_evidence_export_request_")
        assert export["packet_key"] in expected_packets
        assert export["evidence_bundle_packet_preview_id"]
        assert export["label"].startswith("Export ")
        assert export["sequence"] in {1, 2, 3}
        assert export["requested_format"] == "redacted_json_preview"
        assert export["export_allowed_now"] is False
        assert export["blocked_reason"] == "Evidence export is preview-only in Pack 203."
        assert export["raw_evidence_redacted"] is True
        assert export["export_status"] == "receipt_chain_evidence_export_request_preview_blocked"
        assert export["export_result_type"] == "tower_receipt_chain_evidence_export_request_preview"
        assert export["safe_preview_only"] is True
        assert export["real_export_request_created"] is False
        assert export["real_evidence_exported"] is False
        assert export["real_packet_written"] is False
        assert export["real_packet_sealed"] is False
        assert export["real_raw_evidence_revealed"] is False
        assert export["evidence_export_allowed_now"] is False

    expected_checks = {
        "confirm_packet_sections",
        "confirm_bundle_packets",
        "confirm_exports_blocked",
        "confirm_raw_evidence_redacted",
        "confirm_no_real_writes",
    }

    check_keys = {item["check_key"] for item in checklist}
    assert check_keys == expected_checks

    for item in checklist:
        assert item["owner_review_checklist_item_id"].startswith("receipt_chain_evidence_packet_checklist_")
        assert item["check_key"] in expected_checks
        assert item["label"]
        assert item["sequence"] in {1, 2, 3, 4, 5}
        assert item["preview_complete"] is True
        assert item["check_status"] == "receipt_chain_evidence_packet_checklist_item_preview_ready"
        assert item["check_result_type"] == "tower_receipt_chain_evidence_packet_checklist_preview"
        assert item["safe_preview_only"] is True
        assert item["real_export_request_created"] is False
        assert item["real_evidence_exported"] is False
        assert item["real_packet_written"] is False
        assert item["real_packet_sealed"] is False
        assert item["real_raw_evidence_revealed"] is False


def test_pack_203_integrity_indexes_bridge_integrations_route_and_no_secrets():
    mod = importlib.import_module("tower.receipt_chain_evidence_packet_v203")
    payload = mod.build_receipt_chain_evidence_packet_v203_payload(force_refresh=True)

    integrity = payload["evidence_packet_integrity_summary"]
    indexes = payload["evidence_packet_indexes"]

    assert integrity["evidence_packet_integrity_summary_id"].startswith("receipt_chain_evidence_packet_integrity_")
    assert integrity["packet_section_count"] == 6
    assert integrity["evidence_bundle_packet_count"] == 3
    assert integrity["export_request_preview_count"] == 3
    assert integrity["owner_review_checklist_item_count"] == 5
    assert integrity["redacted_item_count"] >= 1
    assert integrity["raw_item_count"] == 0
    assert integrity["real_export_request_created_count"] == 0
    assert integrity["real_evidence_exported_count"] == 0
    assert integrity["real_packet_written_count"] == 0
    assert integrity["real_packet_sealed_count"] == 0
    assert integrity["raw_evidence_revealed_count"] == 0
    assert integrity["all_sections_ready"] is True
    assert integrity["all_packets_ready"] is True
    assert integrity["all_exports_blocked"] is True
    assert integrity["all_checklist_items_ready"] is True
    assert integrity["integrity_status"] == "receipt_chain_evidence_packet_integrity_summary_preview_ready"
    assert integrity["integrity_result_type"] == "tower_receipt_chain_evidence_packet_integrity_summary_preview"
    assert integrity["safe_preview_only"] is True
    assert integrity["real_export_request_created"] is False
    assert integrity["real_evidence_exported"] is False
    assert integrity["real_packet_written"] is False
    assert integrity["real_packet_sealed"] is False
    assert integrity["real_raw_evidence_revealed"] is False

    assert indexes["packet_sections_by_id"]
    assert indexes["packet_sections_by_key"]
    assert indexes["evidence_packets_by_id"]
    assert indexes["evidence_packets_by_key"]
    assert indexes["export_requests_by_id"]
    assert indexes["export_requests_by_packet_key"]
    assert indexes["owner_review_checklist_by_id"]
    assert indexes["owner_review_checklist_by_key"]

    assert "handoff_overview" in indexes["packet_sections_by_key"]
    assert "safety_packet" in indexes["packet_sections_by_key"]
    assert "owner_review_packet" in indexes["evidence_packets_by_key"]
    assert "audit_preview_packet" in indexes["evidence_packets_by_key"]
    assert "next_batch_packet" in indexes["evidence_packets_by_key"]
    assert "owner_review_packet" in indexes["export_requests_by_packet_key"]
    assert "confirm_exports_blocked" in indexes["owner_review_checklist_by_key"]

    bridge = mod.build_receipt_chain_evidence_packet_v203_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 203
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/receipt-chain-evidence-packet-v203.json"
    assert bridge["packet_section_count"] == 6
    assert bridge["evidence_bundle_packet_count"] == 3
    assert bridge["export_request_preview_count"] == 3
    assert bridge["owner_review_checklist_item_count"] == 5
    assert bridge["redacted_item_count"] >= 1
    assert bridge["raw_item_count"] == 0
    assert bridge["real_export_request_created_count"] == 0
    assert bridge["real_evidence_exported_count"] == 0
    assert bridge["real_packet_written_count"] == 0
    assert bridge["real_packet_sealed_count"] == 0
    assert bridge["raw_evidence_revealed_count"] == 0
    assert bridge["save_batch"] == "201-205"
    assert bridge["save_after_pack"] == 205

    action = mod.build_receipt_chain_evidence_packet_v203_quick_action()
    assert action["id"] == "receipt_chain_evidence_packet_v203"
    assert action["href"] == "/tower/receipt-chain-evidence-packet-v203.json"
    assert action["status"] == "ready"

    section = mod.build_receipt_chain_evidence_packet_v203_unified_owner_section()
    assert section["section_id"] == "receipt_chain_evidence_packet_v203"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/receipt-chain-evidence-packet-v203.json"
    assert len(section["cards"]) >= 6

    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_203_receipt_chain_evidence_packet_v203_status_bridge")
    tower_bridge = status.build_pack_203_receipt_chain_evidence_packet_v203_status_bridge()
    assert tower_bridge["status"] == "ready"
    assert tower_bridge["readiness_score"] == 100

    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_203_receipt_chain_evidence_packet_v203_quick_action")
    assert hasattr(qa, "append_pack_203_receipt_chain_evidence_packet_v203_quick_action")
    actions = qa.append_pack_203_receipt_chain_evidence_packet_v203_quick_action([])
    assert any(item.get("id") == "receipt_chain_evidence_packet_v203" for item in actions)

    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_203_receipt_chain_evidence_packet_v203_unified_section")
    assert hasattr(unified, "append_pack_203_receipt_chain_evidence_packet_v203_section")
    sections = unified.append_pack_203_receipt_chain_evidence_packet_v203_section([])
    assert any(item.get("section_id") == "receipt_chain_evidence_packet_v203" for item in sections)

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-evidence-packet-v203.json" in app_text
    assert "tower_receipt_chain_evidence_packet_v203_json" in app_text
    assert "_pack_203_receipt_chain_evidence_packet_v203_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/receipt-chain-evidence-packet-v203.json" in route_text
    assert "_pack_203_receipt_chain_evidence_packet_v203_route_guard" in route_text

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
