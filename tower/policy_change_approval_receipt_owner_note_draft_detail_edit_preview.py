
"""
PACK 170 - Owner Note Draft Detail Drawer / Edit Preview.

This module sits on top of Pack 169.

Pack 169 creates preview-only owner notes/review drafts.
Pack 170 creates preview-only detail/edit surfaces for each owner note draft:
- detail drawer preview
- editable field preview
- validation preview
- before/after draft comparison
- reason/body/tag edit preview
- blocked save/submit behavior

Important:
- simulated-only
- edit-preview-only
- detail-drawer-preview-only
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
- no real edits persisted
- no real approvals/rejections/acknowledgements
- no real policy changes
- no real permission changes
- no real access grants
- no real enforcement
- no real audit writes
- no real receipt writes
- no real archive writes
- no real vault writes
- no raw evidence revealed
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


PACK_ID = "PACK_170"
OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"
OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT = "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json"


EDITABLE_FIELDS = {
    "review_reason": {
        "label": "Review Reason",
        "field_type": "textarea",
        "required": True,
        "max_length": 280,
        "safe_preview_only": True,
    },
    "owner_review_comment_draft": {
        "label": "Owner Review Comment Draft",
        "field_type": "textarea",
        "required": True,
        "max_length": 1200,
        "safe_preview_only": True,
    },
    "decision_draft_language": {
        "label": "Decision Draft Language",
        "field_type": "textarea",
        "required": True,
        "max_length": 700,
        "safe_preview_only": True,
    },
    "acknowledgement_draft_language": {
        "label": "Acknowledgement Draft Language",
        "field_type": "textarea",
        "required": True,
        "max_length": 700,
        "safe_preview_only": True,
    },
    "draft_tags": {
        "label": "Draft Tags",
        "field_type": "tag_list",
        "required": True,
        "max_length": 12,
        "safe_preview_only": True,
    },
}


EXPECTED_EDITABLE_FIELDS = set(EDITABLE_FIELDS.keys())


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


def _safe_tags(value: Any) -> List[str]:
    if isinstance(value, list):
        return [_safe_text(item) for item in value if _safe_text(item)]
    if value:
        return [_safe_text(value)]
    return []


def _load_pack_169_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_notes_review_drafts")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_notes_review_drafts_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_169",
            "status": "review",
            "endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "owner_note_draft_count": 0,
                "saved_view_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 169 owner notes/review drafts payload unavailable",
            },
            "owner_note_drafts": [],
        }

    return {
        "pack_id": "PACK_169",
        "status": "review",
        "endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
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
        "summary": {
            "owner_note_draft_count": 0,
            "saved_view_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 169 owner notes/review drafts payload unavailable",
        },
        "owner_note_drafts": [],
    }


def _proposed_field_value(draft: Dict[str, Any], field_id: str) -> Any:
    if field_id == "review_reason":
        reason = draft.get("review_reason_fields", {}).get("default_reason")
        return f"{_safe_text(reason)} Preview edit note: confirm context before any real workflow."
    if field_id == "owner_review_comment_draft":
        return f"{_safe_text(draft.get('owner_review_comment_draft'))} [Preview edit: owner may refine wording later.]"
    if field_id == "decision_draft_language":
        return f"{_safe_text(draft.get('decision_draft_language'))} [Preview edit only.]"
    if field_id == "acknowledgement_draft_language":
        return f"{_safe_text(draft.get('acknowledgement_draft_language'))} [Preview acknowledgement edit only.]"
    if field_id == "draft_tags":
        tags = _safe_tags(draft.get("draft_tags"))
        if "edit_preview" not in tags:
            tags.append("edit_preview")
        return tags
    return ""


def _current_field_value(draft: Dict[str, Any], field_id: str) -> Any:
    if field_id == "review_reason":
        return _safe_text(draft.get("review_reason_fields", {}).get("default_reason"))
    if field_id == "draft_tags":
        return _safe_tags(draft.get("draft_tags"))
    return _safe_text(draft.get(field_id))


def _validate_preview_value(field_id: str, value: Any) -> Dict[str, Any]:
    meta = EDITABLE_FIELDS.get(field_id, {})
    required = bool(meta.get("required", False))
    max_length = int(meta.get("max_length") or 0)

    errors: List[str] = []
    warnings: List[str] = []

    if field_id == "draft_tags":
        tags = _safe_tags(value)
        if required and not tags:
            errors.append("At least one preview tag is required.")
        if max_length and len(tags) > max_length:
            errors.append("Too many preview tags.")
        if "preview_only" not in tags:
            warnings.append("Recommended preview_only tag is missing.")
        value_length = len(tags)
    else:
        text = _safe_text(value)
        if required and not text:
            errors.append("This preview field is required.")
        if max_length and len(text) > max_length:
            errors.append("Preview field is too long.")
        value_length = len(text)

    return {
        "field_id": field_id,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "value_length": value_length,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "preview_validation_only": True,
    }


def _build_editable_field_preview(draft: Dict[str, Any], field_id: str) -> Dict[str, Any]:
    meta = EDITABLE_FIELDS.get(field_id, {})
    current_value = _current_field_value(draft, field_id)
    proposed_value = _proposed_field_value(draft, field_id)
    validation = _validate_preview_value(field_id, proposed_value)

    changed = current_value != proposed_value

    return {
        "field_id": field_id,
        "label": _safe_text(meta.get("label")),
        "field_type": _safe_text(meta.get("field_type")),
        "required": bool(meta.get("required", False)),
        "max_length": int(meta.get("max_length") or 0),
        "safe_preview_only": True,
        "current_value": current_value,
        "proposed_value": proposed_value,
        "changed": changed,
        "validation": validation,
        "edit_allowed_in_preview": True,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_edit_persisted": False,
        "raw_evidence_reveal_allowed": False,
    }


def _build_before_after_comparison(field_previews: List[Dict[str, Any]]) -> Dict[str, Any]:
    changed_fields = [
        field.get("field_id")
        for field in field_previews
        if field.get("changed") is True
    ]

    return {
        "changed_field_count": len(changed_fields),
        "changed_fields": changed_fields,
        "has_preview_changes": len(changed_fields) >= 1,
        "comparison_status": "before_after_preview_ready",
        "preview_only": True,
        "real_edit_persisted": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
    }


def _build_detail_edit_preview(draft: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    draft = dict(draft or {})
    identity = {
        "pack": PACK_ID,
        "owner_note_draft_id": draft.get("owner_note_draft_id"),
        "saved_view_id": draft.get("saved_view_id"),
        "sequence": sequence,
    }
    detail_edit_preview_id = f"owner_note_draft_detail_edit_preview_{_stable_hash(identity, 18)}"

    editable_fields = [
        _build_editable_field_preview(draft, field_id)
        for field_id in EDITABLE_FIELDS.keys()
    ]

    validation_preview = {
        "valid": all(field.get("validation", {}).get("valid") is True for field in editable_fields),
        "field_count": len(editable_fields),
        "valid_field_count": len([field for field in editable_fields if field.get("validation", {}).get("valid") is True]),
        "error_count": sum(len(field.get("validation", {}).get("errors", [])) for field in editable_fields),
        "warning_count": sum(len(field.get("validation", {}).get("warnings", [])) for field in editable_fields),
        "preview_validation_only": True,
        "save_allowed_now": False,
        "submit_allowed_now": False,
    }

    before_after = _build_before_after_comparison(editable_fields)

    drawer_sections = [
        {
            "section_id": "draft_identity",
            "title": "Draft Identity",
            "safe_for_preview": True,
            "content": {
                "owner_note_draft_id": _safe_text(draft.get("owner_note_draft_id")),
                "saved_view_id": _safe_text(draft.get("saved_view_id")),
                "draft_type": _safe_text(draft.get("draft_type")),
                "draft_priority": _safe_text(draft.get("draft_priority")),
            },
        },
        {
            "section_id": "editable_fields",
            "title": "Editable Fields",
            "safe_for_preview": True,
            "content": {
                "editable_field_count": len(editable_fields),
                "editable_field_ids": [field.get("field_id") for field in editable_fields],
            },
        },
        {
            "section_id": "validation_preview",
            "title": "Validation Preview",
            "safe_for_preview": True,
            "content": validation_preview,
        },
        {
            "section_id": "before_after_comparison",
            "title": "Before / After Preview",
            "safe_for_preview": True,
            "content": before_after,
        },
        {
            "section_id": "blocked_actions",
            "title": "Blocked Save / Submit Actions",
            "safe_for_preview": True,
            "content": {
                "note_write_allowed_now": False,
                "draft_save_allowed_now": False,
                "owner_approval_allowed_now": False,
                "owner_rejection_allowed_now": False,
                "owner_acknowledgement_allowed_now": False,
                "raw_evidence_reveal_allowed": False,
            },
        },
        {
            "section_id": "safety_flags",
            "title": "Safety Flags",
            "safe_for_preview": True,
            "content": {
                "simulated_only": True,
                "edit_preview_only": True,
                "real_edit_persisted": False,
                "real_note_written": False,
                "real_draft_saved": False,
                "real_evidence_revealed": False,
            },
        },
    ]

    return {
        "detail_edit_preview_id": detail_edit_preview_id,
        "sequence": sequence,
        "owner_note_draft_id": _safe_text(draft.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(draft.get("saved_view_id")),
        "saved_view_preview_id": _safe_text(draft.get("saved_view_preview_id")),
        "label": _safe_text(draft.get("label")),
        "description": _safe_text(draft.get("description")),
        "draft_type": _safe_text(draft.get("draft_type")),
        "draft_priority": _safe_text(draft.get("draft_priority")),
        "tone": _safe_text(draft.get("tone")),
        "matched_record_count": int(draft.get("matched_record_count") or 0),
        "requires_owner_review": bool(draft.get("requires_owner_review", False)),
        "detail_drawer_status": "owner_note_draft_detail_edit_preview_ready",
        "editable_fields": editable_fields,
        "editable_field_count": len(editable_fields),
        "validation_preview": validation_preview,
        "before_after_comparison": before_after,
        "drawer_sections": drawer_sections,
        "drawer_section_count": len(drawer_sections),
        "edit_result_type": "owner_note_draft_detail_edit_preview",
        "edit_allowed_in_preview": True,
        "note_write_allowed_now": False,
        "draft_save_allowed_now": False,
        "submit_allowed_now": False,
        "owner_approval_allowed_now": False,
        "owner_rejection_allowed_now": False,
        "owner_acknowledgement_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_edit_persisted": False,
        "simulated_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
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


def _sort_detail_edit_previews(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def _build_detail_edit_indexes(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_detail_edit_preview_id": {},
        "by_owner_note_draft_id": {},
        "by_saved_view_id": {},
        "by_draft_type": {},
        "by_draft_priority": {},
        "by_requires_owner_review": {},
        "by_detail_drawer_status": {},
    }

    for item in items:
        detail_id = _safe_text(item.get("detail_edit_preview_id"))
        if detail_id:
            indexes["by_detail_edit_preview_id"][detail_id] = item

        draft_id = _safe_text(item.get("owner_note_draft_id"))
        if draft_id:
            indexes["by_owner_note_draft_id"][draft_id] = item

        saved_view_id = _safe_text(item.get("saved_view_id")) or "unknown"
        indexes["by_saved_view_id"][saved_view_id] = item

        draft_type = _safe_text(item.get("draft_type")) or "unknown"
        indexes["by_draft_type"].setdefault(draft_type, []).append(item)

        priority = _safe_text(item.get("draft_priority")) or "unknown"
        indexes["by_draft_priority"].setdefault(priority, []).append(item)

        review_key = "owner_review_required" if item.get("requires_owner_review") else "owner_review_not_required"
        indexes["by_requires_owner_review"].setdefault(review_key, []).append(item)

        status = _safe_text(item.get("detail_drawer_status")) or "unknown"
        indexes["by_detail_drawer_status"].setdefault(status, []).append(item)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload_cached() -> Dict[str, Any]:
    pack_169_payload = _load_pack_169_payload(force_refresh=False)
    owner_note_drafts = pack_169_payload.get("owner_note_drafts", [])

    if not isinstance(owner_note_drafts, list):
        owner_note_drafts = []

    detail_edit_previews = []
    for idx, draft in enumerate(owner_note_drafts, start=1):
        if isinstance(draft, dict):
            detail_edit_previews.append(_build_detail_edit_preview(draft, sequence=idx))

    detail_edit_previews = _sort_detail_edit_previews(detail_edit_previews)
    indexes = _build_detail_edit_indexes(detail_edit_previews)

    draft_type_counts = _count_by(detail_edit_previews, "draft_type")
    draft_priority_counts = _count_by(detail_edit_previews, "draft_priority")
    detail_drawer_status_counts = _count_by(detail_edit_previews, "detail_drawer_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([item for item in detail_edit_previews if item.get("requires_owner_review") is True]),
        "owner_review_not_required": len([item for item in detail_edit_previews if item.get("requires_owner_review") is False]),
    }

    detail_edit_preview = {
        item.get("saved_view_id"): item
        for item in detail_edit_previews
        if item.get("saved_view_id")
    }

    validation_summary = {
        "valid_preview_count": len([item for item in detail_edit_previews if item.get("validation_preview", {}).get("valid") is True]),
        "invalid_preview_count": len([item for item in detail_edit_previews if item.get("validation_preview", {}).get("valid") is False]),
        "total_warning_count": sum(int(item.get("validation_preview", {}).get("warning_count") or 0) for item in detail_edit_previews),
        "total_error_count": sum(int(item.get("validation_preview", {}).get("error_count") or 0) for item in detail_edit_previews),
    }

    readiness_checks = {
        "pack_169_ready": pack_169_payload.get("status") == "ready",
        "has_detail_edit_previews": len(detail_edit_previews) >= 1,
        "detail_edit_count_matches_owner_note_drafts": len(detail_edit_previews) == len(owner_note_drafts),
        "all_simulated_only": all(item.get("simulated_only") is True for item in detail_edit_previews),
        "all_edit_preview_only": all(item.get("edit_preview_only") is True for item in detail_edit_previews),
        "all_detail_drawer_preview_only": all(item.get("detail_drawer_preview_only") is True for item in detail_edit_previews),
        "all_owner_note_preview_only": all(item.get("owner_note_preview_only") is True for item in detail_edit_previews),
        "all_review_draft_preview_only": all(item.get("review_draft_preview_only") is True for item in detail_edit_previews),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in detail_edit_previews),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in detail_edit_previews),
        "all_filter_preview_only": all(item.get("filter_preview_only") is True for item in detail_edit_previews),
        "all_search_facet_preview_only": all(item.get("search_facet_preview_only") is True for item in detail_edit_previews),
        "all_lookup_preview_only": all(item.get("lookup_preview_only") is True for item in detail_edit_previews),
        "all_detail_preview_only": all(item.get("detail_preview_only") is True for item in detail_edit_previews),
        "all_evidence_drawer_preview_only": all(item.get("evidence_drawer_preview_only") is True for item in detail_edit_previews),
        "all_owner_review_preview_only": all(item.get("owner_review_preview_only") is True for item in detail_edit_previews),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in detail_edit_previews),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in detail_edit_previews),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in detail_edit_previews),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in detail_edit_previews),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in detail_edit_previews),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in detail_edit_previews),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in detail_edit_previews),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in detail_edit_previews),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in detail_edit_previews),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in detail_edit_previews),
        "no_real_note_written": all(item.get("real_note_written") is False for item in detail_edit_previews),
        "no_real_draft_saved": all(item.get("real_draft_saved") is False for item in detail_edit_previews),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in detail_edit_previews),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in detail_edit_previews),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in detail_edit_previews),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in detail_edit_previews),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in detail_edit_previews),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in detail_edit_previews),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in detail_edit_previews),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in detail_edit_previews),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in detail_edit_previews),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in detail_edit_previews),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in detail_edit_previews),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in detail_edit_previews),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in detail_edit_previews),
        "no_real_owner_review_completed": all(item.get("real_owner_review_completed") is False for item in detail_edit_previews),
        "no_real_owner_approval_executed": all(item.get("real_owner_approval_executed") is False for item in detail_edit_previews),
        "no_real_owner_rejection_executed": all(item.get("real_owner_rejection_executed") is False for item in detail_edit_previews),
        "no_real_owner_acknowledgement_executed": all(item.get("real_owner_acknowledgement_executed") is False for item in detail_edit_previews),
        "no_real_evidence_revealed": all(item.get("real_evidence_revealed") is False for item in detail_edit_previews),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in detail_edit_previews),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in detail_edit_previews),
        "all_note_write_actions_blocked": all(item.get("note_write_allowed_now") is False for item in detail_edit_previews),
        "all_draft_save_actions_blocked": all(item.get("draft_save_allowed_now") is False for item in detail_edit_previews),
        "all_submit_actions_blocked": all(item.get("submit_allowed_now") is False for item in detail_edit_previews),
        "all_owner_approval_actions_blocked": all(item.get("owner_approval_allowed_now") is False for item in detail_edit_previews),
        "all_owner_rejection_actions_blocked": all(item.get("owner_rejection_allowed_now") is False for item in detail_edit_previews),
        "all_owner_acknowledgement_actions_blocked": all(item.get("owner_acknowledgement_allowed_now") is False for item in detail_edit_previews),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in detail_edit_previews),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in detail_edit_previews),
        "all_detail_edit_ids_present": all(bool(item.get("detail_edit_preview_id")) for item in detail_edit_previews),
        "all_owner_note_draft_ids_present": all(bool(item.get("owner_note_draft_id")) for item in detail_edit_previews),
        "all_saved_view_ids_present": all(bool(item.get("saved_view_id")) for item in detail_edit_previews),
        "all_edit_result_type_present": all(item.get("edit_result_type") == "owner_note_draft_detail_edit_preview" for item in detail_edit_previews),
        "all_detail_drawers_ready": all(item.get("detail_drawer_status") == "owner_note_draft_detail_edit_preview_ready" for item in detail_edit_previews),
        "all_have_editable_fields": all(int(item.get("editable_field_count") or 0) == len(EDITABLE_FIELDS) for item in detail_edit_previews),
        "all_expected_editable_fields_present": all(
            EXPECTED_EDITABLE_FIELDS.issubset({field.get("field_id") for field in item.get("editable_fields", [])})
            for item in detail_edit_previews
        ),
        "all_validation_previews_present": all(isinstance(item.get("validation_preview"), dict) and bool(item.get("validation_preview")) for item in detail_edit_previews),
        "all_before_after_previews_present": all(isinstance(item.get("before_after_comparison"), dict) and bool(item.get("before_after_comparison")) for item in detail_edit_previews),
        "all_drawer_sections_present": all(int(item.get("drawer_section_count") or 0) >= 6 for item in detail_edit_previews),
        "all_validation_previews_valid": validation_summary.get("invalid_preview_count") == 0,
        "all_before_after_have_changes": all(item.get("before_after_comparison", {}).get("has_preview_changes") is True for item in detail_edit_previews),
        "critical_owner_review_edit_present": "critical_owner_review" in detail_edit_preview,
        "quarantine_review_edit_present": "quarantine_review" in detail_edit_preview,
        "fresh_recheck_edit_present": "fresh_recheck" in detail_edit_preview,
        "renewal_review_edit_present": "renewal_review" in detail_edit_preview,
        "monitor_only_edit_present": "monitor_only" in detail_edit_preview,
        "high_sensitivity_edit_present": "high_sensitivity_redacted" in detail_edit_preview,
        "safe_preview_edit_present": "safe_preview_only" in detail_edit_preview,
        "all_evidence_drawers_edit_present": "all_evidence_drawers" in detail_edit_preview,
        "endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
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
        "pack_number": 170,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Draft Detail Drawer / Edit Preview",
        "endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        "source_endpoint": OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
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
        "real_edit_persisted": False,
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
        "source_pack_169": {
            "status": pack_169_payload.get("status"),
            "readiness_score": pack_169_payload.get("summary", {}).get("readiness_score"),
            "owner_note_draft_count": pack_169_payload.get("summary", {}).get("owner_note_draft_count"),
            "saved_view_count": pack_169_payload.get("summary", {}).get("saved_view_count"),
        },
        "summary": {
            "detail_edit_preview_count": len(detail_edit_previews),
            "owner_note_draft_count": len(owner_note_drafts),
            "editable_field_count": len(EDITABLE_FIELDS),
            "drawer_section_count": sum(int(item.get("drawer_section_count") or 0) for item in detail_edit_previews),
            "draft_type_counts": draft_type_counts,
            "draft_priority_counts": draft_priority_counts,
            "detail_drawer_status_counts": detail_drawer_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "validation_summary": validation_summary,
            "expected_editable_fields": sorted(EXPECTED_EDITABLE_FIELDS),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note draft detail drawer/edit preview ready" if readiness_score == 100 else "Owner note draft detail drawer/edit preview needs review",
        },
        "readiness_checks": readiness_checks,
        "editable_fields_schema": EDITABLE_FIELDS,
        "detail_edit_previews": detail_edit_previews,
        "detail_edit_preview": detail_edit_preview,
        "detail_edit_indexes": indexes,
        "quick_action": {
            "id": "policy_change_approval_receipt_owner_note_draft_detail_edit_preview",
            "label": "Owner Note Draft Edit Preview",
            "href": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
            "description": "Preview owner note draft detail drawers, editable fields, validation, and blocked save/submit behavior.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_owner_note_draft_detail_edit_preview",
            "title": "Owner Note Draft Edit Preview",
            "subtitle": "Preview editable fields, validation, before/after comparison, and blocked save/submit actions.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 170,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note draft detail drawer/edit preview ready"),
        "detail_edit_preview_count": summary.get("detail_edit_preview_count", 0),
        "owner_note_draft_count": summary.get("owner_note_draft_count", 0),
        "editable_field_count": summary.get("editable_field_count", 0),
        "drawer_section_count": summary.get("drawer_section_count", 0),
        "draft_type_counts": summary.get("draft_type_counts", {}),
        "draft_priority_counts": summary.get("draft_priority_counts", {}),
        "detail_drawer_status_counts": summary.get("detail_drawer_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "validation_summary": summary.get("validation_summary", {}),
        "simulated_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
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
        "real_edit_persisted": False,
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


def get_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_draft_detail_edit_preview",
        "label": "Owner Note Draft Edit Preview",
        "title": "Owner Note Draft Detail Drawer / Edit Preview",
        "href": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        "endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        "description": "Preview owner note draft detail drawers, editable fields, validation, and blocked save/submit behavior.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 170",
        "category": "policy",
        "simulated_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})
    validation = summary.get("validation_summary", {})

    cards = [
        {
            "id": "edit_readiness",
            "title": "Edit preview readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note draft detail drawer/edit preview ready"),
        },
        {
            "id": "detail_edit_previews",
            "title": "Detail edit previews",
            "value": summary.get("detail_edit_preview_count", 0),
            "label": "Owner-note drafts with edit previews",
        },
        {
            "id": "editable_fields",
            "title": "Editable fields",
            "value": summary.get("editable_field_count", 0),
            "label": "Reason/body/decision/ack/tags",
        },
        {
            "id": "valid_previews",
            "title": "Valid previews",
            "value": validation.get("valid_preview_count", 0),
            "label": "Validation preview passed",
        },
        {
            "id": "blocked_submit",
            "title": "Submit/save",
            "value": "Blocked" if checks.get("all_submit_actions_blocked") else "Review",
            "label": "No real edit saved",
        },
        {
            "id": "real_edit_persisted",
            "title": "Real edit persisted",
            "value": "No" if checks.get("no_real_edit_persisted") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_draft_detail_edit_preview",
        "title": "Owner Note Draft Edit Preview",
        "subtitle": "Preview editable fields, validation, before/after comparison, and blocked save/submit actions.",
        "status": payload.get("status", "ready"),
        "href": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-edit-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-edit-section" id="policy-change-approval-receipt-owner-note-draft-detail-edit-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 170</p>
            <h2>{section.get('title', 'Owner Note Draft Edit Preview')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT}">Open owner note draft edit preview JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT",
    "OWNER_NOTES_REVIEW_DRAFTS_ENDPOINT",
    "EDITABLE_FIELDS",
    "EXPECTED_EDITABLE_FIELDS",
    "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload",
    "get_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload",
    "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section",
]
