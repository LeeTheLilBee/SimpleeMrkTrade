
"""
PACK 170 fast test - Owner Note Draft Detail Drawer / Edit Preview.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_170_payload_ready_and_edit_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 170
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"

    assert payload["simulated_only"] is True
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
    assert summary["detail_edit_preview_count"] >= 8
    assert summary["owner_note_draft_count"] >= 8
    assert summary["editable_field_count"] == 5
    assert summary["validation_summary"]["invalid_preview_count"] == 0
    assert summary["validation_summary"]["valid_preview_count"] >= 8

    checks = payload["readiness_checks"]
    assert checks["pack_169_ready"] is True
    assert checks["has_detail_edit_previews"] is True
    assert checks["detail_edit_count_matches_owner_note_drafts"] is True
    assert checks["all_simulated_only"] is True
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

    assert checks["all_note_write_actions_blocked"] is True
    assert checks["all_draft_save_actions_blocked"] is True
    assert checks["all_submit_actions_blocked"] is True
    assert checks["all_owner_approval_actions_blocked"] is True
    assert checks["all_owner_rejection_actions_blocked"] is True
    assert checks["all_owner_acknowledgement_actions_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_detail_edit_ids_present"] is True
    assert checks["all_owner_note_draft_ids_present"] is True
    assert checks["all_saved_view_ids_present"] is True
    assert checks["all_edit_result_type_present"] is True
    assert checks["all_detail_drawers_ready"] is True
    assert checks["all_have_editable_fields"] is True
    assert checks["all_expected_editable_fields_present"] is True
    assert checks["all_validation_previews_present"] is True
    assert checks["all_before_after_previews_present"] is True
    assert checks["all_drawer_sections_present"] is True
    assert checks["all_validation_previews_valid"] is True
    assert checks["all_before_after_have_changes"] is True
    assert checks["critical_owner_review_edit_present"] is True
    assert checks["quarantine_review_edit_present"] is True
    assert checks["fresh_recheck_edit_present"] is True
    assert checks["renewal_review_edit_present"] is True
    assert checks["monitor_only_edit_present"] is True
    assert checks["high_sensitivity_edit_present"] is True
    assert checks["safe_preview_edit_present"] is True
    assert checks["all_evidence_drawers_edit_present"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_170_detail_edit_previews_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=True)

    expected_fields = {
        "review_reason",
        "owner_review_comment_draft",
        "decision_draft_language",
        "acknowledgement_draft_language",
        "draft_tags",
    }

    expected_sections = {
        "draft_identity",
        "editable_fields",
        "validation_preview",
        "before_after_comparison",
        "blocked_actions",
        "safety_flags",
    }

    for item in payload["detail_edit_previews"]:
        assert item["detail_edit_preview_id"].startswith("owner_note_draft_detail_edit_preview_")
        assert item["owner_note_draft_id"].startswith("evidence_drawer_owner_note_draft_")
        assert item["saved_view_id"]
        assert item["saved_view_preview_id"].startswith("evidence_drawer_saved_view_")
        assert item["label"]
        assert item["description"]
        assert item["draft_type"]
        assert item["draft_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert item["tone"]
        assert isinstance(item["matched_record_count"], int)
        assert isinstance(item["requires_owner_review"], bool)
        assert item["detail_drawer_status"] == "owner_note_draft_detail_edit_preview_ready"
        assert item["editable_field_count"] == 5

        field_ids = {field["field_id"] for field in item["editable_fields"]}
        assert expected_fields.issubset(field_ids)

        for field in item["editable_fields"]:
            assert field["field_id"] in expected_fields
            assert field["label"]
            assert field["field_type"] in {"textarea", "tag_list"}
            assert field["required"] is True
            assert field["safe_preview_only"] is True
            assert field["changed"] is True
            assert field["edit_allowed_in_preview"] is True
            assert field["save_allowed_now"] is False
            assert field["submit_allowed_now"] is False
            assert field["real_edit_persisted"] is False
            assert field["raw_evidence_reveal_allowed"] is False
            assert field["validation"]["valid"] is True
            assert field["validation"]["save_allowed_now"] is False
            assert field["validation"]["submit_allowed_now"] is False
            assert field["validation"]["preview_validation_only"] is True

        validation = item["validation_preview"]
        assert validation["valid"] is True
        assert validation["field_count"] == 5
        assert validation["valid_field_count"] == 5
        assert validation["error_count"] == 0
        assert validation["preview_validation_only"] is True
        assert validation["save_allowed_now"] is False
        assert validation["submit_allowed_now"] is False

        before_after = item["before_after_comparison"]
        assert before_after["changed_field_count"] == 5
        assert set(before_after["changed_fields"]) == expected_fields
        assert before_after["has_preview_changes"] is True
        assert before_after["comparison_status"] == "before_after_preview_ready"
        assert before_after["preview_only"] is True
        assert before_after["real_edit_persisted"] is False
        assert before_after["save_allowed_now"] is False
        assert before_after["submit_allowed_now"] is False

        section_ids = {section["section_id"] for section in item["drawer_sections"]}
        assert expected_sections.issubset(section_ids)
        assert item["drawer_section_count"] >= 6
        assert item["edit_result_type"] == "owner_note_draft_detail_edit_preview"

        assert item["edit_allowed_in_preview"] is True
        assert item["note_write_allowed_now"] is False
        assert item["draft_save_allowed_now"] is False
        assert item["submit_allowed_now"] is False
        assert item["owner_approval_allowed_now"] is False
        assert item["owner_rejection_allowed_now"] is False
        assert item["owner_acknowledgement_allowed_now"] is False
        assert item["raw_evidence_reveal_allowed"] is False
        assert item["raw_evidence_lookup_allowed"] is False
        assert item["real_edit_persisted"] is False


def test_pack_170_specific_detail_edit_previews_exist():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=True)

    previews = payload["detail_edit_preview"]

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


def test_pack_170_detail_edit_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
    payload = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=True)

    indexes = payload["detail_edit_indexes"]

    assert indexes["by_detail_edit_preview_id"]
    assert indexes["by_owner_note_draft_id"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_draft_type"]
    assert indexes["by_draft_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_detail_drawer_status"]

    assert "critical_owner_review" in indexes["by_saved_view_id"]
    assert "quarantine_review" in indexes["by_saved_view_id"]
    assert "owner_review_required" in indexes["by_requires_owner_review"]
    assert "owner_review_not_required" in indexes["by_requires_owner_review"]
    assert "owner_note_draft_detail_edit_preview_ready" in indexes["by_detail_drawer_status"]


def test_pack_170_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")

    bridge = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 170
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
    assert bridge["readiness_score"] == 100
    assert bridge["detail_edit_preview_count"] >= 8
    assert bridge["owner_note_draft_count"] >= 8
    assert bridge["editable_field_count"] == 5

    assert bridge["simulated_only"] is True
    assert bridge["edit_preview_only"] is True
    assert bridge["detail_drawer_preview_only"] is True
    assert bridge["real_edit_persisted"] is False
    assert bridge["real_note_written"] is False
    assert bridge["real_draft_saved"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
    assert action["simulated_only"] is True
    assert action["edit_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
    assert section["simulated_only"] is True
    assert section["edit_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_170_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge")

    bridge = status.build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge()
    assert bridge["pack_number"] == 170
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
    assert bridge["readiness_score"] == 100


def test_pack_170_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action")
    assert hasattr(qa, "append_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action")

    action = qa.build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"

    actions = qa.append_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview" for item in actions)


def test_pack_170_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_section")
    assert hasattr(unified, "build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section")
    assert hasattr(unified, "append_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_section")

    section = unified.build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"

    sections = unified.append_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_note_draft_detail_edit_preview" for item in sections)


def test_pack_170_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_json" in app_text
    assert "_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json" in route_text
    assert "_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_route_guard" in route_text


def test_pack_170_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
    payload_text = str(mod.build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=True)).lower()

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
