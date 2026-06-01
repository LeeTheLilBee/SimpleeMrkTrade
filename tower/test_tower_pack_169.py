
"""
PACK 169 fast test - Evidence Drawer Owner Notes / Review Drafts.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_169_payload_ready_and_review_draft_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
    payload = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=True)

    assert payload["pack_number"] == 169
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"

    assert payload["simulated_only"] is True
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
    assert summary["owner_note_draft_count"] >= 8
    assert summary["saved_view_count"] >= 8
    assert "critical_owner_review" in summary["observed_draft_templates"]
    assert "quarantine_review" in summary["observed_draft_templates"]
    assert "fresh_recheck" in summary["observed_draft_templates"]
    assert "renewal_review" in summary["observed_draft_templates"]
    assert "monitor_only" in summary["observed_draft_templates"]
    assert "high_sensitivity_redacted" in summary["observed_draft_templates"]
    assert "safe_preview_only" in summary["observed_draft_templates"]
    assert "all_evidence_drawers" in summary["observed_draft_templates"]

    checks = payload["readiness_checks"]
    assert checks["pack_168_ready"] is True
    assert checks["has_note_drafts"] is True
    assert checks["note_draft_count_matches_saved_views"] is True
    assert checks["all_expected_draft_templates_present"] is True
    assert checks["all_simulated_only"] is True
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
    assert checks["all_owner_approval_actions_blocked"] is True
    assert checks["all_owner_rejection_actions_blocked"] is True
    assert checks["all_owner_acknowledgement_actions_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_note_draft_ids_present"] is True
    assert checks["all_saved_view_ids_present"] is True
    assert checks["all_draft_types_present"] is True
    assert checks["all_review_reason_fields_present"] is True
    assert checks["all_owner_review_comment_drafts_present"] is True
    assert checks["all_decision_draft_language_present"] is True
    assert checks["all_acknowledgement_draft_language_present"] is True
    assert checks["all_draft_tags_present"] is True
    assert checks["all_draft_result_type_present"] is True
    assert checks["all_drafts_ready"] is True
    assert checks["critical_owner_review_draft_present"] is True
    assert checks["quarantine_review_draft_present"] is True
    assert checks["fresh_recheck_draft_present"] is True
    assert checks["renewal_review_draft_present"] is True
    assert checks["monitor_only_draft_present"] is True
    assert checks["high_sensitivity_draft_present"] is True
    assert checks["safe_preview_draft_present"] is True
    assert checks["all_evidence_drawers_draft_present"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_169_owner_note_drafts_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
    payload = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=True)

    expected_templates = {
        "critical_owner_review",
        "quarantine_review",
        "fresh_recheck",
        "renewal_review",
        "monitor_only",
        "high_sensitivity_redacted",
        "safe_preview_only",
        "all_evidence_drawers",
    }
    observed_templates = set()

    for draft in payload["owner_note_drafts"]:
        observed_templates.add(draft["saved_view_id"])

        assert draft["owner_note_draft_id"].startswith("evidence_drawer_owner_note_draft_")
        assert draft["saved_view_id"]
        assert draft["saved_view_preview_id"].startswith("evidence_drawer_saved_view_")
        assert draft["label"]
        assert draft["description"]
        assert draft["draft_type"]
        assert draft["draft_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert draft["tone"]
        assert isinstance(draft["matched_record_count"], int)
        assert isinstance(draft["requires_owner_review"], bool)
        assert isinstance(draft["review_reason_fields"], dict)
        assert draft["review_reason_fields"]
        assert draft["owner_review_comment_draft"]
        assert draft["decision_draft_language"]
        assert draft["acknowledgement_draft_language"]
        assert isinstance(draft["draft_tags"], list)
        assert "preview_only" in draft["draft_tags"]
        assert "no_real_action" in draft["draft_tags"]
        assert draft["draft_status"] == "owner_note_review_draft_ready"
        assert draft["draft_result_type"] == "evidence_drawer_owner_note_review_draft_preview"

        assert draft["note_write_allowed_now"] is False
        assert draft["draft_save_allowed_now"] is False
        assert draft["owner_approval_allowed_now"] is False
        assert draft["owner_rejection_allowed_now"] is False
        assert draft["owner_acknowledgement_allowed_now"] is False
        assert draft["raw_evidence_reveal_allowed"] is False
        assert draft["raw_evidence_lookup_allowed"] is False

        assert draft["simulated_only"] is True
        assert draft["owner_note_preview_only"] is True
        assert draft["review_draft_preview_only"] is True
        assert draft["saved_view_preview_only"] is True
        assert draft["filter_preset_preview_only"] is True
        assert draft["filter_preview_only"] is True
        assert draft["search_facet_preview_only"] is True
        assert draft["lookup_preview_only"] is True
        assert draft["detail_preview_only"] is True
        assert draft["evidence_drawer_preview_only"] is True
        assert draft["owner_review_preview_only"] is True
        assert draft["queue_preview_only"] is True
        assert draft["renewal_preview_only"] is True
        assert draft["recheck_preview_only"] is True
        assert draft["expiration_preview_only"] is True
        assert draft["vault_preview_only"] is True
        assert draft["index_preview_only"] is True
        assert draft["receipt_preview_only"] is True
        assert draft["approval_preview_only"] is True
        assert draft["evidence_preview_only"] is True

        assert draft["real_note_written"] is False
        assert draft["real_draft_saved"] is False
        assert draft["real_approval_executed"] is False
        assert draft["real_policy_change_executed"] is False
        assert draft["real_permission_change_executed"] is False
        assert draft["real_access_granted"] is False
        assert draft["real_enforcement_executed"] is False
        assert draft["real_audit_written"] is False
        assert draft["real_receipt_written"] is False
        assert draft["real_archive_written"] is False
        assert draft["real_vault_written"] is False
        assert draft["real_expiration_enforced"] is False
        assert draft["real_recheck_executed"] is False
        assert draft["real_renewal_executed"] is False
        assert draft["real_queue_action_executed"] is False
        assert draft["real_owner_review_completed"] is False
        assert draft["real_owner_approval_executed"] is False
        assert draft["real_owner_rejection_executed"] is False
        assert draft["real_owner_acknowledgement_executed"] is False
        assert draft["real_evidence_revealed"] is False
        assert draft["real_saved_view_written"] is False
        assert draft["real_user_preference_written"] is False

    assert expected_templates.issubset(observed_templates)


def test_pack_169_specific_draft_templates_have_expected_language():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
    payload = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=True)

    drafts = payload["note_draft_preview"]

    critical = drafts["critical_owner_review"]
    assert critical["draft_type"] == "owner_review_comment"
    assert critical["draft_priority"] == "critical"
    assert critical["requires_owner_review"] is True
    assert "Critical owner recheck" in critical["review_reason_fields"]["default_reason"]

    quarantine = drafts["quarantine_review"]
    assert quarantine["draft_type"] == "quarantine_review_comment"
    assert quarantine["draft_priority"] == "high"
    assert quarantine["requires_owner_review"] is True

    fresh = drafts["fresh_recheck"]
    assert fresh["draft_type"] == "fresh_recheck_comment"
    assert fresh["requires_owner_review"] is True

    renewal = drafts["renewal_review"]
    assert renewal["draft_type"] == "renewal_review_comment"
    assert renewal["requires_owner_review"] is True

    monitor = drafts["monitor_only"]
    assert monitor["draft_type"] == "monitor_acknowledgement_comment"
    assert monitor["draft_priority"] == "monitor"
    assert monitor["requires_owner_review"] is False

    redacted = drafts["high_sensitivity_redacted"]
    assert redacted["draft_type"] == "redaction_review_comment"
    assert redacted["requires_owner_review"] is True

    safe_only = drafts["safe_preview_only"]
    assert safe_only["draft_type"] == "safe_preview_acknowledgement"
    assert safe_only["requires_owner_review"] is False

    all_drawers = drafts["all_evidence_drawers"]
    assert all_drawers["draft_type"] == "general_owner_note"
    assert all_drawers["requires_owner_review"] is False


def test_pack_169_draft_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
    payload = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=True)

    indexes = payload["draft_indexes"]
    assert indexes["by_owner_note_draft_id"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_draft_type"]
    assert indexes["by_draft_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_draft_status"]

    assert "critical_owner_review" in indexes["by_saved_view_id"]
    assert "quarantine_review" in indexes["by_saved_view_id"]
    assert "owner_note_review_draft_ready" in indexes["by_draft_status"]
    assert "owner_review_required" in indexes["by_requires_owner_review"]
    assert "owner_review_not_required" in indexes["by_requires_owner_review"]


def test_pack_169_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")

    bridge = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 169
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
    assert bridge["readiness_score"] == 100
    assert bridge["owner_note_draft_count"] >= 8
    assert bridge["saved_view_count"] >= 8

    assert bridge["simulated_only"] is True
    assert bridge["owner_note_preview_only"] is True
    assert bridge["review_draft_preview_only"] is True
    assert bridge["real_note_written"] is False
    assert bridge["real_draft_saved"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_notes_review_drafts"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
    assert action["simulated_only"] is True
    assert action["owner_note_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_notes_review_drafts"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
    assert section["simulated_only"] is True
    assert section["owner_note_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_169_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge")

    bridge = status.build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge()
    assert bridge["pack_number"] == 169
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
    assert bridge["readiness_score"] == 100


def test_pack_169_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_quick_action")
    assert hasattr(qa, "append_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_quick_action")

    action = qa.build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_quick_action()
    assert action["id"] == "policy_change_approval_receipt_owner_notes_review_drafts"
    assert action["href"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"

    actions = qa.append_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_owner_notes_review_drafts" for item in actions)


def test_pack_169_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_unified_section")
    assert hasattr(unified, "build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_html_section")
    assert hasattr(unified, "append_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_section")

    section = unified.build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_owner_notes_review_drafts"
    assert section["href"] == "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"

    sections = unified.append_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_owner_notes_review_drafts" for item in sections)


def test_pack_169_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json" in app_text
    assert "tower_policy_change_approval_receipt_owner_notes_review_drafts_json" in app_text
    assert "_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json" in route_text
    assert "_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_route_guard" in route_text


def test_pack_169_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
    payload_text = str(mod.build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=True)).lower()

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
