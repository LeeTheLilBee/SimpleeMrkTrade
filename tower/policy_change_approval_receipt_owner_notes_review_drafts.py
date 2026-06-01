
"""
PACK 169 - Evidence Drawer Owner Notes / Review Drafts.

This module sits on top of Pack 168.

Pack 168 creates preview-only saved views/filter presets for evidence drawer records.
Pack 169 creates preview-only owner notes/review drafts:
- note draft templates
- owner-review comment drafts
- decision draft language
- acknowledgement draft language
- review reason fields
- draft tags and safety notes

Important:
- simulated-only
- owner-note-preview-only
- review-draft-preview-only
- saved-view-preview-only
- filter-preset-preview-only
- filter-preview-only
- search-facet-preview-only
- lookup-preview-only
- detail-preview-only
- evidence-drawer-preview-only
- owner-review-preview-only
- queue-preview-only
- renewal-preview-only
- recheck-preview-only
- expiration-preview-only
- vault-preview-only
- index-preview-only
- receipt-preview-only
- approval-preview-only
- evidence-preview-only
- no real notes written
- no real drafts saved
- no real approvals executed
- no real rejections executed
- no real acknowledgements executed
- no real policy changes
- no real permission changes
- no real access grants
- no real enforcement
- no real audit writes
- no real receipt writes
- no real archive writes
- no real vault writes
- no real evidence revealed
- cached
- non-recursive
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "PACK_169"
OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT = "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"
SAVED_VIEWS_ENDPOINT = "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"


DRAFT_TEMPLATE_BLUEPRINTS = {
    "critical_owner_review": {
        "draft_type": "owner_review_comment",
        "tone": "firm",
        "default_reason": "Critical owner recheck required before reuse.",
        "decision_language": "Hold this receipt for owner recheck. Do not approve, renew, or execute anything from this preview.",
        "acknowledgement_language": "Owner has reviewed the critical preview context but no real action has been executed.",
        "draft_priority": "critical",
    },
    "quarantine_review": {
        "draft_type": "quarantine_review_comment",
        "tone": "cautious",
        "default_reason": "Quarantine review required before any follow-up.",
        "decision_language": "Keep this receipt in quarantine review. Do not convert the preview into an action.",
        "acknowledgement_language": "Owner has acknowledged the quarantine preview context without releasing the hold.",
        "draft_priority": "high",
    },
    "fresh_recheck": {
        "draft_type": "fresh_recheck_comment",
        "tone": "precise",
        "default_reason": "Fresh recheck needed before using this approval receipt again.",
        "decision_language": "Require a fresh recheck before renewal or reuse.",
        "acknowledgement_language": "Owner has acknowledged that a fresh recheck is needed.",
        "draft_priority": "high",
    },
    "renewal_review": {
        "draft_type": "renewal_review_comment",
        "tone": "balanced",
        "default_reason": "Renewal review preview should be inspected before reuse.",
        "decision_language": "Review renewal context before any future approval path.",
        "acknowledgement_language": "Owner has reviewed the renewal preview without executing renewal.",
        "draft_priority": "medium",
    },
    "monitor_only": {
        "draft_type": "monitor_acknowledgement_comment",
        "tone": "calm",
        "default_reason": "Monitor-only preview acknowledged.",
        "decision_language": "Continue monitor-only status. No owner approval is required from this preview.",
        "acknowledgement_language": "Owner has acknowledged monitor-only context.",
        "draft_priority": "monitor",
    },
    "high_sensitivity_redacted": {
        "draft_type": "redaction_review_comment",
        "tone": "protective",
        "default_reason": "High-sensitivity redacted preview should remain protected.",
        "decision_language": "Keep sensitive details redacted unless a later authorized reveal workflow is approved.",
        "acknowledgement_language": "Owner has acknowledged high-sensitivity redaction without revealing raw evidence.",
        "draft_priority": "high",
    },
    "safe_preview_only": {
        "draft_type": "safe_preview_acknowledgement",
        "tone": "simple",
        "default_reason": "Safe preview-only context is available.",
        "decision_language": "Keep this view as preview-only. Do not write notes, preferences, or evidence reveals.",
        "acknowledgement_language": "Owner has viewed safe preview-only context.",
        "draft_priority": "standard",
    },
    "all_evidence_drawers": {
        "draft_type": "general_owner_note",
        "tone": "summary",
        "default_reason": "General evidence drawer review summary.",
        "decision_language": "Use this as a summary note preview only.",
        "acknowledgement_language": "Owner has reviewed the general evidence drawer summary preview.",
        "draft_priority": "standard",
    },
}


EXPECTED_DRAFT_TEMPLATES = set(DRAFT_TEMPLATE_BLUEPRINTS.keys())


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
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
    lowered = text.lower()
    for fragment in forbidden_fragments:
        if fragment in lowered:
            return "[REDACTED]"
    return text


def _load_pack_168_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
        fn = getattr(mod, "build_policy_change_approval_receipt_saved_views_filter_presets_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_168",
            "status": "review",
            "endpoint": SAVED_VIEWS_ENDPOINT,
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "saved_view_count": 0,
                "filter_record_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 168 saved views/filter presets payload unavailable",
            },
            "saved_views": [],
        }

    return {
        "pack_id": "PACK_168",
        "status": "review",
        "endpoint": SAVED_VIEWS_ENDPOINT,
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "summary": {
            "saved_view_count": 0,
            "filter_record_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 168 saved views/filter presets payload unavailable",
        },
        "saved_views": [],
    }


def _blueprint_for_saved_view(saved_view_id: str) -> Dict[str, Any]:
    return dict(DRAFT_TEMPLATE_BLUEPRINTS.get(saved_view_id) or {
        "draft_type": "general_owner_note",
        "tone": "summary",
        "default_reason": "Owner review note preview.",
        "decision_language": "Use this as a preview-only owner note.",
        "acknowledgement_language": "Owner has reviewed this preview context.",
        "draft_priority": "standard",
    })


def _build_owner_note_draft(saved_view: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    saved_view = dict(saved_view or {})
    saved_view_id = _safe_text(saved_view.get("saved_view_id"))
    blueprint = _blueprint_for_saved_view(saved_view_id)

    identity = {
        "pack": PACK_ID,
        "saved_view_id": saved_view_id,
        "saved_view_preview_id": saved_view.get("saved_view_preview_id"),
        "sequence": sequence,
        "draft_type": blueprint.get("draft_type"),
    }

    draft_preview_id = f"evidence_drawer_owner_note_draft_{_stable_hash(identity, 18)}"

    matched_record_count = int(saved_view.get("matched_record_count") or 0)
    requires_owner_review = bool(saved_view.get("requires_owner_review", False))

    review_reason_fields = {
        "default_reason": _safe_text(blueprint.get("default_reason")),
        "view_reason": _safe_text(saved_view.get("description")),
        "matched_record_count": matched_record_count,
        "requires_owner_review": requires_owner_review,
        "view_priority": _safe_text(saved_view.get("view_priority")),
        "draft_priority": _safe_text(blueprint.get("draft_priority")),
    }

    draft_tags = [
        f"view:{saved_view_id}",
        f"priority:{_safe_text(blueprint.get('draft_priority'))}",
        "preview_only",
        "no_real_action",
    ]

    if requires_owner_review:
        draft_tags.append("owner_review_required")
    else:
        draft_tags.append("owner_review_not_required")

    if saved_view.get("empty_view"):
        draft_tags.append("empty_view")
    else:
        draft_tags.append("has_matches")

    note_body = (
        f"{_safe_text(saved_view.get('label'))}: "
        f"{_safe_text(blueprint.get('default_reason'))} "
        f"Matched records: {matched_record_count}. "
        f"Decision draft: {_safe_text(blueprint.get('decision_language'))}"
    )

    return {
        "owner_note_draft_id": draft_preview_id,
        "sequence": sequence,
        "saved_view_id": saved_view_id,
        "saved_view_preview_id": _safe_text(saved_view.get("saved_view_preview_id")),
        "label": _safe_text(saved_view.get("label")),
        "description": _safe_text(saved_view.get("description")),
        "draft_type": _safe_text(blueprint.get("draft_type")),
        "draft_priority": _safe_text(blueprint.get("draft_priority")),
        "tone": _safe_text(blueprint.get("tone")),
        "matched_record_count": matched_record_count,
        "requires_owner_review": requires_owner_review,
        "review_reason_fields": review_reason_fields,
        "owner_review_comment_draft": note_body,
        "decision_draft_language": _safe_text(blueprint.get("decision_language")),
        "acknowledgement_draft_language": _safe_text(blueprint.get("acknowledgement_language")),
        "draft_tags": draft_tags,
        "draft_status": "owner_note_review_draft_ready",
        "draft_result_type": "evidence_drawer_owner_note_review_draft_preview",
        "note_write_allowed_now": False,
        "draft_save_allowed_now": False,
        "owner_approval_allowed_now": False,
        "owner_rejection_allowed_now": False,
        "owner_acknowledgement_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
    }


def _sort_note_drafts(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            priority_rank.get(str(item.get("draft_priority")), 99),
            int(item.get("sequence") or 999),
        ),
    )


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_draft_indexes(note_drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_owner_note_draft_id": {},
        "by_saved_view_id": {},
        "by_draft_type": {},
        "by_draft_priority": {},
        "by_requires_owner_review": {},
        "by_draft_status": {},
    }

    for draft in note_drafts:
        draft_id = _safe_text(draft.get("owner_note_draft_id"))
        if draft_id:
            indexes["by_owner_note_draft_id"][draft_id] = draft

        saved_view_id = _safe_text(draft.get("saved_view_id")) or "unknown"
        indexes["by_saved_view_id"][saved_view_id] = draft

        draft_type = _safe_text(draft.get("draft_type")) or "unknown"
        indexes["by_draft_type"].setdefault(draft_type, []).append(draft)

        priority = _safe_text(draft.get("draft_priority")) or "unknown"
        indexes["by_draft_priority"].setdefault(priority, []).append(draft)

        review_key = "owner_review_required" if draft.get("requires_owner_review") else "owner_review_not_required"
        indexes["by_requires_owner_review"].setdefault(review_key, []).append(draft)

        status = _safe_text(draft.get("draft_status")) or "unknown"
        indexes["by_draft_status"].setdefault(status, []).append(draft)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_notes_review_drafts_payload_cached() -> Dict[str, Any]:
    pack_168_payload = _load_pack_168_payload(force_refresh=False)
    saved_views = pack_168_payload.get("saved_views", [])

    if not isinstance(saved_views, list):
        saved_views = []

    note_drafts = []
    for idx, saved_view in enumerate(saved_views, start=1):
        if isinstance(saved_view, dict):
            note_drafts.append(_build_owner_note_draft(saved_view, sequence=idx))

    note_drafts = _sort_note_drafts(note_drafts)
    indexes = _build_draft_indexes(note_drafts)

    draft_type_counts = _count_by(note_drafts, "draft_type")
    draft_priority_counts = _count_by(note_drafts, "draft_priority")
    draft_status_counts = _count_by(note_drafts, "draft_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([draft for draft in note_drafts if draft.get("requires_owner_review") is True]),
        "owner_review_not_required": len([draft for draft in note_drafts if draft.get("requires_owner_review") is False]),
    }

    note_draft_preview = {
        draft.get("saved_view_id"): draft
        for draft in note_drafts
        if draft.get("saved_view_id")
    }

    readiness_checks = {
        "pack_168_ready": pack_168_payload.get("status") == "ready",
        "has_note_drafts": len(note_drafts) >= 1,
        "note_draft_count_matches_saved_views": len(note_drafts) == len(saved_views),
        "all_expected_draft_templates_present": EXPECTED_DRAFT_TEMPLATES.issubset({draft.get("saved_view_id") for draft in note_drafts}),
        "all_simulated_only": all(draft.get("simulated_only") is True for draft in note_drafts),
        "all_owner_note_preview_only": all(draft.get("owner_note_preview_only") is True for draft in note_drafts),
        "all_review_draft_preview_only": all(draft.get("review_draft_preview_only") is True for draft in note_drafts),
        "all_saved_view_preview_only": all(draft.get("saved_view_preview_only") is True for draft in note_drafts),
        "all_filter_preset_preview_only": all(draft.get("filter_preset_preview_only") is True for draft in note_drafts),
        "all_filter_preview_only": all(draft.get("filter_preview_only") is True for draft in note_drafts),
        "all_search_facet_preview_only": all(draft.get("search_facet_preview_only") is True for draft in note_drafts),
        "all_lookup_preview_only": all(draft.get("lookup_preview_only") is True for draft in note_drafts),
        "all_detail_preview_only": all(draft.get("detail_preview_only") is True for draft in note_drafts),
        "all_evidence_drawer_preview_only": all(draft.get("evidence_drawer_preview_only") is True for draft in note_drafts),
        "all_owner_review_preview_only": all(draft.get("owner_review_preview_only") is True for draft in note_drafts),
        "all_queue_preview_only": all(draft.get("queue_preview_only") is True for draft in note_drafts),
        "all_renewal_preview_only": all(draft.get("renewal_preview_only") is True for draft in note_drafts),
        "all_recheck_preview_only": all(draft.get("recheck_preview_only") is True for draft in note_drafts),
        "all_expiration_preview_only": all(draft.get("expiration_preview_only") is True for draft in note_drafts),
        "all_vault_preview_only": all(draft.get("vault_preview_only") is True for draft in note_drafts),
        "all_index_preview_only": all(draft.get("index_preview_only") is True for draft in note_drafts),
        "all_receipt_preview_only": all(draft.get("receipt_preview_only") is True for draft in note_drafts),
        "all_approval_preview_only": all(draft.get("approval_preview_only") is True for draft in note_drafts),
        "all_evidence_preview_only": all(draft.get("evidence_preview_only") is True for draft in note_drafts),
        "no_real_note_written": all(draft.get("real_note_written") is False for draft in note_drafts),
        "no_real_draft_saved": all(draft.get("real_draft_saved") is False for draft in note_drafts),
        "no_real_approval_executed": all(draft.get("real_approval_executed") is False for draft in note_drafts),
        "no_real_policy_change": all(draft.get("real_policy_change_executed") is False for draft in note_drafts),
        "no_real_permission_change": all(draft.get("real_permission_change_executed") is False for draft in note_drafts),
        "no_real_access_granted": all(draft.get("real_access_granted") is False for draft in note_drafts),
        "no_real_enforcement": all(draft.get("real_enforcement_executed") is False for draft in note_drafts),
        "no_real_audit_written": all(draft.get("real_audit_written") is False for draft in note_drafts),
        "no_real_receipt_written": all(draft.get("real_receipt_written") is False for draft in note_drafts),
        "no_real_archive_written": all(draft.get("real_archive_written") is False for draft in note_drafts),
        "no_real_vault_written": all(draft.get("real_vault_written") is False for draft in note_drafts),
        "no_real_expiration_enforced": all(draft.get("real_expiration_enforced") is False for draft in note_drafts),
        "no_real_recheck_executed": all(draft.get("real_recheck_executed") is False for draft in note_drafts),
        "no_real_renewal_executed": all(draft.get("real_renewal_executed") is False for draft in note_drafts),
        "no_real_queue_action_executed": all(draft.get("real_queue_action_executed") is False for draft in note_drafts),
        "no_real_owner_review_completed": all(draft.get("real_owner_review_completed") is False for draft in note_drafts),
        "no_real_owner_approval_executed": all(draft.get("real_owner_approval_executed") is False for draft in note_drafts),
        "no_real_owner_rejection_executed": all(draft.get("real_owner_rejection_executed") is False for draft in note_drafts),
        "no_real_owner_acknowledgement_executed": all(draft.get("real_owner_acknowledgement_executed") is False for draft in note_drafts),
        "no_real_evidence_revealed": all(draft.get("real_evidence_revealed") is False for draft in note_drafts),
        "no_real_saved_view_written": all(draft.get("real_saved_view_written") is False for draft in note_drafts),
        "no_real_user_preference_written": all(draft.get("real_user_preference_written") is False for draft in note_drafts),
        "all_note_write_actions_blocked": all(draft.get("note_write_allowed_now") is False for draft in note_drafts),
        "all_draft_save_actions_blocked": all(draft.get("draft_save_allowed_now") is False for draft in note_drafts),
        "all_owner_approval_actions_blocked": all(draft.get("owner_approval_allowed_now") is False for draft in note_drafts),
        "all_owner_rejection_actions_blocked": all(draft.get("owner_rejection_allowed_now") is False for draft in note_drafts),
        "all_owner_acknowledgement_actions_blocked": all(draft.get("owner_acknowledgement_allowed_now") is False for draft in note_drafts),
        "all_raw_evidence_reveal_blocked": all(draft.get("raw_evidence_reveal_allowed") is False for draft in note_drafts),
        "all_raw_evidence_lookup_blocked": all(draft.get("raw_evidence_lookup_allowed") is False for draft in note_drafts),
        "all_note_draft_ids_present": all(bool(draft.get("owner_note_draft_id")) for draft in note_drafts),
        "all_saved_view_ids_present": all(bool(draft.get("saved_view_id")) for draft in note_drafts),
        "all_draft_types_present": all(bool(draft.get("draft_type")) for draft in note_drafts),
        "all_review_reason_fields_present": all(isinstance(draft.get("review_reason_fields"), dict) and bool(draft.get("review_reason_fields")) for draft in note_drafts),
        "all_owner_review_comment_drafts_present": all(bool(draft.get("owner_review_comment_draft")) for draft in note_drafts),
        "all_decision_draft_language_present": all(bool(draft.get("decision_draft_language")) for draft in note_drafts),
        "all_acknowledgement_draft_language_present": all(bool(draft.get("acknowledgement_draft_language")) for draft in note_drafts),
        "all_draft_tags_present": all(isinstance(draft.get("draft_tags"), list) and bool(draft.get("draft_tags")) for draft in note_drafts),
        "all_draft_result_type_present": all(draft.get("draft_result_type") == "evidence_drawer_owner_note_review_draft_preview" for draft in note_drafts),
        "all_drafts_ready": all(draft.get("draft_status") == "owner_note_review_draft_ready" for draft in note_drafts),
        "critical_owner_review_draft_present": "critical_owner_review" in note_draft_preview,
        "quarantine_review_draft_present": "quarantine_review" in note_draft_preview,
        "fresh_recheck_draft_present": "fresh_recheck" in note_draft_preview,
        "renewal_review_draft_present": "renewal_review" in note_draft_preview,
        "monitor_only_draft_present": "monitor_only" in note_draft_preview,
        "high_sensitivity_draft_present": "high_sensitivity_redacted" in note_draft_preview,
        "safe_preview_draft_present": "safe_preview_only" in note_draft_preview,
        "all_evidence_drawers_draft_present": "all_evidence_drawers" in note_draft_preview,
        "endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value
        for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 169,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Evidence Drawer Owner Notes / Review Drafts",
        "endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "source_endpoint": SAVED_VIEWS_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
        "source_pack_168": {
            "status": pack_168_payload.get("status"),
            "readiness_score": pack_168_payload.get("summary", {}).get("readiness_score"),
            "saved_view_count": pack_168_payload.get("summary", {}).get("saved_view_count"),
            "filter_record_count": pack_168_payload.get("summary", {}).get("filter_record_count"),
        },
        "summary": {
            "owner_note_draft_count": len(note_drafts),
            "saved_view_count": len(saved_views),
            "draft_type_counts": draft_type_counts,
            "draft_priority_counts": draft_priority_counts,
            "draft_status_counts": draft_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "expected_draft_templates": sorted(EXPECTED_DRAFT_TEMPLATES),
            "observed_draft_templates": sorted([draft.get("saved_view_id") for draft in note_drafts]),
            "readiness_score": readiness_score,
            "readiness_label": "Evidence drawer owner notes/review drafts ready" if readiness_score == 100 else "Evidence drawer owner notes/review drafts need review",
        },
        "readiness_checks": readiness_checks,
        "draft_template_blueprints": DRAFT_TEMPLATE_BLUEPRINTS,
        "owner_note_drafts": note_drafts,
        "note_draft_preview": note_draft_preview,
        "draft_indexes": indexes,
        "quick_action": {
            "id": "policy_change_approval_receipt_owner_notes_review_drafts",
            "label": "Evidence Drawer Owner Notes",
            "href": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
            "description": "Preview owner note and review draft language for approval receipt evidence drawers.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_owner_notes_review_drafts",
            "title": "Evidence Drawer Owner Notes",
            "subtitle": "Preview owner notes, review comments, decision draft language, and acknowledgement draft language.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_notes_review_drafts_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_notes_review_drafts_payload_cached())


def get_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_notes_review_drafts_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 169,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", SAVED_VIEWS_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Evidence drawer owner notes/review drafts ready"),
        "owner_note_draft_count": summary.get("owner_note_draft_count", 0),
        "saved_view_count": summary.get("saved_view_count", 0),
        "draft_type_counts": summary.get("draft_type_counts", {}),
        "draft_priority_counts": summary.get("draft_priority_counts", {}),
        "draft_status_counts": summary.get("draft_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "simulated_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_notes_review_drafts_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_notes_review_drafts",
        "label": "Evidence Drawer Owner Notes",
        "title": "Evidence Drawer Owner Notes / Review Drafts",
        "href": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "description": "Preview owner note and review draft language for approval receipt evidence drawers.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 169",
        "category": "policy",
        "simulated_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_notes_review_drafts_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    review_counts = summary.get("owner_review_requirement_counts", {})

    cards = [
        {
            "id": "draft_readiness",
            "title": "Draft readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Evidence drawer owner notes/review drafts ready"),
        },
        {
            "id": "owner_note_drafts",
            "title": "Owner note drafts",
            "value": summary.get("owner_note_draft_count", 0),
            "label": "Preview-only draft notes",
        },
        {
            "id": "review_required",
            "title": "Review-required drafts",
            "value": review_counts.get("owner_review_required", 0),
            "label": "Drafts tied to owner attention",
        },
        {
            "id": "no_review_required",
            "title": "No-review drafts",
            "value": review_counts.get("owner_review_not_required", 0),
            "label": "Monitor/safe preview drafts",
        },
        {
            "id": "draft_types",
            "title": "Draft types",
            "value": len(summary.get("draft_type_counts", {})),
            "label": "Comment/acknowledgement/recheck templates",
        },
        {
            "id": "real_note_write",
            "title": "Real note write",
            "value": "No" if checks.get("no_real_note_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_notes_review_drafts",
        "title": "Evidence Drawer Owner Notes",
        "subtitle": "Preview owner notes, review comments, decision draft language, and acknowledgement draft language.",
        "status": payload.get("status", "ready"),
        "href": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_owner_notes_review_drafts_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-section" id="policy-change-approval-receipt-owner-notes-review-drafts">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 169</p>
            <h2>{section.get('title', 'Evidence Drawer Owner Notes')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT}">Open evidence drawer owner notes JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT",
    "SAVED_VIEWS_ENDPOINT",
    "DRAFT_TEMPLATE_BLUEPRINTS",
    "EXPECTED_DRAFT_TEMPLATES",
    "build_policy_change_approval_receipt_owner_notes_review_drafts_payload",
    "get_policy_change_approval_receipt_owner_notes_review_drafts_payload",
    "build_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge",
    "get_policy_change_approval_receipt_owner_notes_review_drafts_status_bridge",
    "build_policy_change_approval_receipt_owner_notes_review_drafts_quick_action",
    "build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section",
    "build_policy_change_approval_receipt_owner_notes_review_drafts_html_section",
]
