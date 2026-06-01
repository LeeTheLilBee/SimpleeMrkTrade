
"""
PACK 171 fast test - Owner Note Draft Edit History / Version Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_171_payload_ready_and_version_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 171
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"

    assert payload["simulated_only"] is True
    assert payload["version_preview_only"] is True
    assert payload["edit_history_preview_only"] is True
    assert payload["rollback_preview_only"] is True
    assert payload["compare_preview_only"] is True
    assert payload["edit_preview_only"] is True
    assert payload["detail_drawer_preview_only"] is True
    assert payload["owner_note_preview_only"] is True
    assert payload["review_draft_preview_only"] is True
    assert payload["saved_view_preview_only"] is True
    assert payload["filter_preset_preview_only"] is True
    assert payload["filter_preview_only"] is True
    assert payload["search_facet_preview_only"] is True
    assert payload["lookup_preview_only"] is True
    assert payload["detail_preview_only"] is True
    assert payload["evidence_drawer_preview_only"] is True
    assert payload["owner_review_preview_only"] is True
    assert payload["queue_preview_only"] is True
    assert payload["renewal_preview_only"] is True
    assert payload["recheck_preview_only"] is True
    assert payload["expiration_preview_only"] is True
    assert payload["vault_preview_only"] is True
    assert payload["index_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["approval_preview_only"] is True
    assert payload["evidence_preview_only"] is True

    assert payload["real_history_written"] is False
    assert payload["real_version_saved"] is False
    assert payload["real_rollback_executed"] is False
    assert payload["real_restore_executed"] is False
    assert payload["real_edit_persisted"] is False
    assert payload["real_note_written"] is False
    assert payload["real_draft_saved"] is False
    assert payload["real_approval_executed"] is False
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["real_archive_written"] is False
    assert payload["real_vault_written"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_renewal_executed"] is False
    assert payload["real_queue_action_executed"] is False
    assert payload["real_owner_review_completed"] is False
    assert payload["real_owner_approval_executed"] is False
    assert payload["real_owner_rejection_executed"] is False
    assert payload["real_owner_acknowledgement_executed"] is False
    assert payload["real_evidence_revealed"] is False
    assert payload["real_saved_view_written"] is False
    assert payload["real_user_preference_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["edit_history_timeline_count"] >= 8
    assert summary["detail_edit_preview_count"] >= 8
    assert summary["version_card_count"] >= 24
    assert summary["field_change_event_count"] >= 40
    assert summary["tracked_field_count"] == 5
    assert summary["version_stage_count"] == 3

    checks = payload["readiness_checks"]
    assert checks["pack_170_ready"] is True
    assert checks["has_timelines"] is True
    assert checks["timeline_count_matches_detail_edit_previews"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_version_preview_only"] is True
    assert checks["all_edit_history_preview_only"] is True
    assert checks["all_rollback_preview_only"] is True
    assert checks["all_compare_preview_only"] is True
    assert checks["all_edit_preview_only"] is True
    assert checks["all_detail_drawer_preview_only"] is True
    assert checks["all_owner_note_preview_only"] is True
    assert checks["all_review_draft_preview_only"] is True
    assert checks["all_saved_view_preview_only"] is True
    assert checks["all_filter_preset_preview_only"] is True
    assert checks["all_filter_preview_only"] is True
    assert checks["all_search_facet_preview_only"] is True
    assert checks["all_lookup_preview_only"] is True
    assert checks["all_detail_preview_only"] is True
    assert checks["all_evidence_drawer_preview_only"] is True
    assert checks["all_owner_review_preview_only"] is True
    assert checks["all_queue_preview_only"] is True
    assert checks["all_renewal_preview_only"] is True
    assert checks["all_recheck_preview_only"] is True
    assert checks["all_expiration_preview_only"] is True
    assert checks["all_vault_preview_only"] is True
    assert checks["all_index_preview_only"] is True
    assert checks["all_receipt_preview_only"] is True
    assert checks["all_approval_preview_only"] is True
    assert checks["all_evidence_preview_only"] is True

    assert checks["no_real_history_written"] is True
    assert checks["no_real_version_saved"] is True
    assert checks["no_real_rollback_executed"] is True
    assert checks["no_real_restore_executed"] is True
    assert checks["no_real_edit_persisted"] is True
    assert checks["no_real_note_written"] is True
    assert checks["no_real_draft_saved"] is True
    assert checks["no_real_approval_executed"] is True
    assert checks["no_real_policy_change"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_archive_written"] is True
    assert checks["no_real_vault_written"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_recheck_executed"] is True
    assert checks["no_real_renewal_executed"] is True
    assert checks["no_real_queue_action_executed"] is True
    assert checks["no_real_owner_review_completed"] is True
    assert checks["no_real_owner_approval_executed"] is True
    assert checks["no_real_owner_rejection_executed"] is True
    assert checks["no_real_owner_acknowledgement_executed"] is True
    assert checks["no_real_evidence_revealed"] is True
    assert checks["no_real_saved_view_written"] is True
    assert checks["no_real_user_preference_written"] is True

    assert checks["all_restore_actions_blocked"] is True
    assert checks["all_rollback_actions_blocked"] is True
    assert checks["all_save_actions_blocked"] is True
    assert checks["all_submit_actions_blocked"] is True
    assert checks["all_history_write_actions_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_timeline_ids_present"] is True
    assert checks["all_detail_edit_preview_ids_present"] is True
    assert checks["all_owner_note_draft_ids_present"] is True
    assert checks["all_saved_view_ids_present"] is True
    assert checks["all_timeline_result_type_present"] is True
    assert checks["all_timelines_ready"] is True
    assert checks["all_have_three_version_cards"] is True
    assert checks["all_have_five_field_change_events"] is True
    assert checks["all_expected_tracked_fields_present"] is True
    assert checks["all_compare_previews_ready"] is True
    assert checks["all_rollback_previews_blocked"] is True
    assert checks["critical_owner_review_history_present"] is True
    assert checks["quarantine_review_history_present"] is True
    assert checks["fresh_recheck_history_present"] is True
    assert checks["renewal_review_history_present"] is True
    assert checks["monitor_only_history_present"] is True
    assert checks["high_sensitivity_history_present"] is True
    assert checks["safe_preview_history_present"] is True
    assert checks["all_evidence_drawers_history_present"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_171_timelines_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=True)

    expected_fields = {
        "review_reason",
        "owner_review_comment_draft",
        "decision_draft_language",
        "acknowledgement_draft_language",
        "draft_tags",
    }

    expected_stages = {
        "original_draft",
        "preview_edit",
        "blocked_save_attempt",
    }

    for item in payload["edit_history_timelines"]:
        assert item["edit_history_timeline_id"].startswith("owner_note_draft_edit_history_timeline_")
        assert item["detail_edit_preview_id"].startswith("owner_note_draft_detail_edit_preview_")
        assert item["owner_note_draft_id"].startswith("evidence_drawer_owner_note_draft_")
        assert item["saved_view_id"]
        assert item["label"]
        assert item["description"]
        assert item["draft_type"]
        assert item["draft_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(item["requires_owner_review"], bool)
        assert item["timeline_status"] == "edit_history_version_preview_ready"
        assert item["timeline_result_type"] == "owner_note_draft_edit_history_version_preview"
        assert item["version_card_count"] == 3
        assert item["field_change_event_count"] == 5
        assert item["tracked_field_count"] == 5
        assert expected_fields.issubset(set(item["tracked_fields"]))

        stages = {card["version_stage"] for card in item["version_cards"]}
        assert expected_stages.issubset(stages)

        for card in item["version_cards"]:
            assert card["version_card_id"].startswith("owner_note_draft_version_card_")
            assert card["version_stage"] in expected_stages
            assert card["version_order"] in {1, 2, 3}
            assert card["label"]
            assert card["description"]
            assert isinstance(card["field_values"], dict)
            assert isinstance(card["change_summary"], dict)
            assert card["version_status"] == "version_preview_ready"
            assert card["version_result_type"] == "owner_note_draft_version_card_preview"
            assert card["restore_allowed_now"] is False
            assert card["rollback_allowed_now"] is False
            assert card["save_allowed_now"] is False
            assert card["submit_allowed_now"] is False
            assert card["real_history_written"] is False
            assert card["real_version_saved"] is False
            assert card["real_rollback_executed"] is False
            assert card["real_restore_executed"] is False
            assert card["real_edit_persisted"] is False
            assert card["raw_evidence_reveal_allowed"] is False
            assert card["raw_evidence_lookup_allowed"] is False
            assert card["simulated_only"] is True
            assert card["version_preview_only"] is True
            assert card["edit_history_preview_only"] is True
            assert card["rollback_preview_only"] is True
            assert card["compare_preview_only"] is True

        for event in item["field_change_events"]:
            assert event["field_change_event_id"].startswith("owner_note_draft_field_change_event_")
            assert event["field_id"] in expected_fields
            assert event["field_label"]
            assert event["field_type"] in {"textarea", "tag_list"}
            assert event["changed"] is True
            assert isinstance(event["current_value_summary"], dict)
            assert isinstance(event["proposed_value_summary"], dict)
            assert isinstance(event["validation"], dict)
            assert event["change_event_status"] == "field_change_preview_ready"
            assert event["change_event_type"] == "preview_field_change"
            assert event["history_write_allowed_now"] is False
            assert event["real_history_written"] is False
            assert event["real_edit_persisted"] is False
            assert event["simulated_only"] is True
            assert event["version_preview_only"] is True
            assert event["edit_history_preview_only"] is True

        compare = item["compare_preview"]
        assert compare["compare_preview_id"].startswith("owner_note_draft_compare_preview_")
        assert compare["from_version_stage"] == "original_draft"
        assert compare["to_version_stage"] == "preview_edit"
        assert compare["changed_field_count"] == 5
        assert expected_fields.issubset(set(compare["changed_fields"]))
        assert compare["compare_status"] == "compare_preview_ready"
        assert compare["compare_result_type"] == "owner_note_draft_version_compare_preview"
        assert compare["compare_allowed_in_preview"] is True
        assert compare["save_allowed_now"] is False
        assert compare["submit_allowed_now"] is False
        assert compare["real_history_written"] is False
        assert compare["real_edit_persisted"] is False

        rollback = item["rollback_preview"]
        assert rollback["rollback_preview_id"].startswith("owner_note_draft_rollback_preview_")
        assert rollback["from_version_stage"] == "preview_edit"
        assert rollback["to_version_stage"] == "original_draft"
        assert rollback["rollback_status"] == "rollback_preview_blocked"
        assert rollback["rollback_allowed_in_preview"] is True
        assert rollback["restore_allowed_now"] is False
        assert rollback["rollback_allowed_now"] is False
        assert rollback["save_allowed_now"] is False
        assert rollback["submit_allowed_now"] is False
        assert rollback["real_rollback_executed"] is False
        assert rollback["real_restore_executed"] is False
        assert rollback["real_history_written"] is False
        assert rollback["real_edit_persisted"] is False

        assert item["compare_allowed_in_preview"] is True
        assert item["rollback_allowed_in_preview"] is True
        assert item["restore_allowed_now"] is False
        assert item["rollback_allowed_now"] is False
        assert item["save_allowed_now"] is False
        assert item["submit_allowed_now"] is False
        assert item["history_write_allowed_now"] is False
        assert item["real_history_written"] is False
        assert item["real_version_saved"] is False
        assert item["real_rollback_executed"] is False
        assert item["real_restore_executed"] is False
        assert item["real_edit_persisted"] is False
        assert item["raw_evidence_reveal_allowed"] is False
        assert item["raw_evidence_lookup_allowed"] is False


def test_pack_171_specific_timeline_previews_exist():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=True)

    previews = payload["timeline_preview"]

    expected = {
        "critical_owner_review",
        "quarantine_review",
        "fresh_recheck",
        "renewal_review",
        "monitor_only",
        "high_sensitivity_redacted",
        "safe_preview_only",
        "all_evidence_drawers",
    }

    assert expected.issubset(set(previews.keys()))

    assert previews["critical_owner_review"]["draft_priority"] == "critical"
    assert previews["quarantine_review"]["draft_priority"] == "high"
    assert previews["fresh_recheck"]["draft_priority"] == "high"
    assert previews["renewal_review"]["draft_priority"] == "medium"
    assert previews["monitor_only"]["draft_priority"] == "monitor"
    assert previews["safe_preview_only"]["draft_priority"] == "standard"


def test_pack_171_history_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=True)

    indexes = payload["history_indexes"]

    assert indexes["by_edit_history_timeline_id"]
    assert indexes["by_detail_edit_preview_id"]
    assert indexes["by_owner_note_draft_id"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_draft_type"]
    assert indexes["by_draft_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_timeline_status"]

    assert "critical_owner_review" in indexes["by_saved_view_id"]
    assert "quarantine_review" in indexes["by_saved_view_id"]
    assert "owner_review_required" in indexes["by_requires_owner_review"]
    assert "owner_review_not_required" in indexes["by_requires_owner_review"]
    assert "edit_history_version_preview_ready" in indexes["by_timeline_status"]


def test_pack_171_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")

    bridge = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 171
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
    assert bridge["readiness_score"] == 100
    assert bridge["edit_history_timeline_count"] >= 8
    assert bridge["version_card_count"] >= 24
    assert bridge["field_change_event_count"] >= 40
    assert bridge["tracked_field_count"] == 5

    assert bridge["simulated_only"] is True
    assert bridge["version_preview_only"] is True
    assert bridge["edit_history_preview_only"] is True
    assert bridge["rollback_preview_only"] is True
    assert bridge["compare_preview_only"] is True
    assert bridge["real_history_written"] is False
    assert bridge["real_version_saved"] is False
    assert bridge["real_rollback_executed"] is False
    assert bridge["real_restore_executed"] is False
    assert bridge["real_edit_persisted"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
    assert action["simulated_only"] is True
    assert action["version_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
    assert section["simulated_only"] is True
    assert section["version_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_171_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge")

    bridge = status.build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge()
    assert bridge["pack_number"] == 171
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
    assert bridge["readiness_score"] == 100


def test_pack_171_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action")
    assert hasattr(qa, "append_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action")

    action = qa.build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"

    actions = qa.append_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview" for item in actions)


def test_pack_171_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_section")
    assert hasattr(unified, "build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section")
    assert hasattr(unified, "append_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_section")

    section = unified.build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"

    sections = unified.append_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview" for item in sections)


def test_pack_171_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_json" in app_text
    assert "_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json" in route_text
    assert "_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_route_guard" in route_text


def test_pack_171_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=True)).lower()

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
