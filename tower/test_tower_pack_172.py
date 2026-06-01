
"""
PACK 172 fast test - Owner Note Draft Version Detail Drawer / Compare View.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_172_payload_ready_and_compare_view_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=True)

    assert payload["pack_number"] == 172
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"

    assert payload["simulated_only"] is True
    assert payload["version_detail_preview_only"] is True
    assert payload["compare_view_preview_only"] is True
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
    assert payload["real_version_written"] is False
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
    assert summary["version_detail_drawer_count"] >= 8
    assert summary["edit_history_timeline_count"] >= 8
    assert summary["comparison_row_count"] >= 40
    assert summary["drawer_section_count"] >= 48
    assert summary["changed_field_count"] >= 40
    assert summary["compare_field_count"] == 5

    checks = payload["readiness_checks"]
    assert checks["pack_171_ready"] is True
    assert checks["has_version_detail_drawers"] is True
    assert checks["drawer_count_matches_timelines"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_version_detail_preview_only"] is True
    assert checks["all_compare_view_preview_only"] is True
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
    assert checks["no_real_version_written"] is True
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
    assert checks["all_version_write_actions_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_drawer_ids_present"] is True
    assert checks["all_timeline_ids_present"] is True
    assert checks["all_detail_edit_preview_ids_present"] is True
    assert checks["all_owner_note_draft_ids_present"] is True
    assert checks["all_saved_view_ids_present"] is True
    assert checks["all_drawer_result_type_present"] is True
    assert checks["all_drawers_ready"] is True
    assert checks["all_have_five_comparison_rows"] is True
    assert checks["all_have_six_drawer_sections"] is True
    assert checks["all_have_original_version_card"] is True
    assert checks["all_have_preview_version_card"] is True
    assert checks["all_have_blocked_save_version_card"] is True
    assert checks["all_have_compare_metadata"] is True
    assert checks["all_compare_metadata_ready"] is True
    assert checks["all_changed_groups_present"] is True
    assert checks["all_unchanged_groups_present"] is True
    assert checks["all_expected_compare_fields_present"] is True
    assert checks["critical_owner_review_compare_present"] is True
    assert checks["quarantine_review_compare_present"] is True
    assert checks["fresh_recheck_compare_present"] is True
    assert checks["renewal_review_compare_present"] is True
    assert checks["monitor_only_compare_present"] is True
    assert checks["high_sensitivity_compare_present"] is True
    assert checks["safe_preview_compare_present"] is True
    assert checks["all_evidence_drawers_compare_present"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_172_drawers_have_required_compare_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=True)

    expected_fields = {
        "review_reason",
        "owner_review_comment_draft",
        "decision_draft_language",
        "acknowledgement_draft_language",
        "draft_tags",
    }

    expected_sections = {
        "drawer_identity",
        "side_by_side_versions",
        "comparison_rows",
        "comparison_groups",
        "blocked_actions",
        "safety_flags",
    }

    for drawer in payload["version_detail_drawers"]:
        assert drawer["version_detail_drawer_id"].startswith("owner_note_draft_version_detail_compare_drawer_")
        assert drawer["edit_history_timeline_id"].startswith("owner_note_draft_edit_history_timeline_")
        assert drawer["detail_edit_preview_id"].startswith("owner_note_draft_detail_edit_preview_")
        assert drawer["owner_note_draft_id"].startswith("evidence_drawer_owner_note_draft_")
        assert drawer["saved_view_id"]
        assert drawer["label"]
        assert drawer["description"]
        assert drawer["draft_type"]
        assert drawer["draft_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(drawer["requires_owner_review"], bool)
        assert drawer["drawer_status"] == "version_detail_compare_view_preview_ready"
        assert drawer["drawer_result_type"] == "owner_note_draft_version_detail_compare_drawer_preview"

        assert drawer["original_version_card"]["version_stage"] == "original_draft"
        assert drawer["preview_edit_version_card"]["version_stage"] == "preview_edit"
        assert drawer["blocked_save_attempt_version_card"]["version_stage"] == "blocked_save_attempt"

        assert drawer["comparison_row_count"] == 5
        observed_fields = {row["field_id"] for row in drawer["comparison_rows"]}
        assert expected_fields.issubset(observed_fields)

        for row in drawer["comparison_rows"]:
            assert row["compare_row_id"].startswith("version_detail_compare_row_")
            assert row["field_id"] in expected_fields
            assert row["field_label"]
            assert row["original_version_card_id"].startswith("owner_note_draft_version_card_")
            assert row["preview_version_card_id"].startswith("owner_note_draft_version_card_")
            assert isinstance(row["original_value"], dict)
            assert isinstance(row["preview_value"], dict)
            assert row["changed"] is True
            assert row["change_group"] == "changed_fields"
            assert row["row_status"] == "field_compare_preview_ready"
            assert row["row_result_type"] == "owner_note_draft_version_field_compare_row_preview"
            assert row["safe_preview_only"] is True
            assert row["restore_allowed_now"] is False
            assert row["rollback_allowed_now"] is False
            assert row["save_allowed_now"] is False
            assert row["submit_allowed_now"] is False
            assert row["real_history_written"] is False
            assert row["real_version_saved"] is False
            assert row["real_rollback_executed"] is False
            assert row["real_restore_executed"] is False
            assert row["real_edit_persisted"] is False
            assert row["raw_evidence_reveal_allowed"] is False
            assert row["raw_evidence_lookup_allowed"] is False
            assert row["simulated_only"] is True
            assert row["version_detail_preview_only"] is True
            assert row["compare_view_preview_only"] is True

        groups = drawer["comparison_groups"]
        assert groups["group_status"] == "comparison_groups_preview_ready"
        assert groups["safe_preview_only"] is True
        assert groups["changed_fields"]["count"] == 5
        assert set(groups["changed_fields"]["field_ids"]) == expected_fields
        assert groups["unchanged_fields"]["count"] == 0
        assert groups["unchanged_fields"]["field_ids"] == []

        metadata = drawer["compare_metadata"]
        assert metadata["compare_metadata_id"].startswith("version_detail_compare_metadata_")
        assert metadata["from_version_stage"] == "original_draft"
        assert metadata["to_version_stage"] == "preview_edit"
        assert metadata["field_count"] == 5
        assert metadata["changed_field_count"] == 5
        assert metadata["unchanged_field_count"] == 0
        assert metadata["compare_status"] == "version_detail_compare_metadata_ready"
        assert metadata["compare_result_type"] == "owner_note_draft_version_detail_compare_metadata_preview"
        assert metadata["compare_allowed_in_preview"] is True
        assert metadata["restore_allowed_now"] is False
        assert metadata["rollback_allowed_now"] is False
        assert metadata["save_allowed_now"] is False
        assert metadata["submit_allowed_now"] is False
        assert metadata["real_history_written"] is False
        assert metadata["real_version_saved"] is False
        assert metadata["real_rollback_executed"] is False
        assert metadata["real_restore_executed"] is False
        assert metadata["real_edit_persisted"] is False

        section_ids = {section["section_id"] for section in drawer["drawer_sections"]}
        assert expected_sections.issubset(section_ids)
        assert drawer["drawer_section_count"] >= 6

        assert drawer["compare_allowed_in_preview"] is True
        assert drawer["restore_allowed_now"] is False
        assert drawer["rollback_allowed_now"] is False
        assert drawer["save_allowed_now"] is False
        assert drawer["submit_allowed_now"] is False
        assert drawer["history_write_allowed_now"] is False
        assert drawer["version_write_allowed_now"] is False
        assert drawer["real_history_written"] is False
        assert drawer["real_version_written"] is False
        assert drawer["real_version_saved"] is False
        assert drawer["real_rollback_executed"] is False
        assert drawer["real_restore_executed"] is False
        assert drawer["real_edit_persisted"] is False
        assert drawer["raw_evidence_reveal_allowed"] is False
        assert drawer["raw_evidence_lookup_allowed"] is False


def test_pack_172_specific_drawer_previews_exist():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=True)

    previews = payload["drawer_preview"]

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


def test_pack_172_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=True)

    indexes = payload["version_detail_indexes"]

    assert indexes["by_version_detail_drawer_id"]
    assert indexes["by_edit_history_timeline_id"]
    assert indexes["by_detail_edit_preview_id"]
    assert indexes["by_owner_note_draft_id"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_draft_type"]
    assert indexes["by_draft_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_drawer_status"]

    assert "critical_owner_review" in indexes["by_saved_view_id"]
    assert "quarantine_review" in indexes["by_saved_view_id"]
    assert "owner_review_required" in indexes["by_requires_owner_review"]
    assert "owner_review_not_required" in indexes["by_requires_owner_review"]
    assert "version_detail_compare_view_preview_ready" in indexes["by_drawer_status"]


def test_pack_172_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")

    bridge = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 172
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
    assert bridge["readiness_score"] == 100
    assert bridge["version_detail_drawer_count"] >= 8
    assert bridge["comparison_row_count"] >= 40
    assert bridge["changed_field_count"] >= 40
    assert bridge["compare_field_count"] == 5

    assert bridge["simulated_only"] is True
    assert bridge["version_detail_preview_only"] is True
    assert bridge["compare_view_preview_only"] is True
    assert bridge["real_history_written"] is False
    assert bridge["real_version_written"] is False
    assert bridge["real_version_saved"] is False
    assert bridge["real_rollback_executed"] is False
    assert bridge["real_restore_executed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
    assert action["simulated_only"] is True
    assert action["version_detail_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
    assert section["simulated_only"] is True
    assert section["version_detail_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_172_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge")

    bridge = status.build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge()
    assert bridge["pack_number"] == 172
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
    assert bridge["readiness_score"] == 100


def test_pack_172_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action")
    assert hasattr(qa, "append_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action")

    action = qa.build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"

    actions = qa.append_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view" for item in actions)


def test_pack_172_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_section")
    assert hasattr(unified, "build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section")
    assert hasattr(unified, "append_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_section")

    section = unified.build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"

    sections = unified.append_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view" for item in sections)


def test_pack_172_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_json" in app_text
    assert "_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json" in route_text
    assert "_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_route_guard" in route_text


def test_pack_172_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=True)).lower()

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
