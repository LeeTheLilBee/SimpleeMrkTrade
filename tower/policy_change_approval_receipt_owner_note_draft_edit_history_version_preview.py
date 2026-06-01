
"""
PACK 171 - Owner Note Draft Edit History / Version Preview.

This module sits on top of Pack 170.

Pack 170 creates preview-only detail/edit surfaces for owner note drafts.
Pack 171 creates preview-only edit history/version timeline scaffolding:
- version cards
- draft change events
- field-level change summaries
- compare preview
- rollback preview
- blocked restore/save behavior

Important:
- simulated-only
- version-preview-only
- edit-history-preview-only
- rollback-preview-only
- compare-preview-only
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
- no real history writes
- no real rollback executed
- no real restore executed
- no real edits persisted
- no real notes written
- no real drafts saved
- no real approvals/rejections/acknowledgements
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


PACK_ID = "PACK_171"
OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"
OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json"


VERSION_STAGES = [
    {
        "version_stage": "original_draft",
        "label": "Original Draft",
        "description": "The starting owner-note draft preview from Pack 169.",
        "version_order": 1,
    },
    {
        "version_stage": "preview_edit",
        "label": "Preview Edit",
        "description": "The edited preview from Pack 170 editable fields.",
        "version_order": 2,
    },
    {
        "version_stage": "blocked_save_attempt",
        "label": "Blocked Save Attempt",
        "description": "A simulated blocked save/submit event proving no real edit persisted.",
        "version_order": 3,
    },
]


TRACKED_FIELDS = {
    "review_reason": {
        "label": "Review Reason",
        "safe_preview_only": True,
    },
    "owner_review_comment_draft": {
        "label": "Owner Review Comment Draft",
        "safe_preview_only": True,
    },
    "decision_draft_language": {
        "label": "Decision Draft Language",
        "safe_preview_only": True,
    },
    "acknowledgement_draft_language": {
        "label": "Acknowledgement Draft Language",
        "safe_preview_only": True,
    },
    "draft_tags": {
        "label": "Draft Tags",
        "safe_preview_only": True,
    },
}


EXPECTED_TRACKED_FIELDS = set(TRACKED_FIELDS.keys())


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


def _load_pack_170_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_170",
            "status": "review",
            "endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "detail_edit_preview_count": 0,
                "owner_note_draft_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 170 owner note draft detail/edit preview payload unavailable",
            },
            "detail_edit_previews": [],
        }

    return {
        "pack_id": "PACK_170",
        "status": "review",
        "endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
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
        "summary": {
            "detail_edit_preview_count": 0,
            "owner_note_draft_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 170 owner note draft detail/edit preview payload unavailable",
        },
        "detail_edit_previews": [],
    }



def _summarize_value(value: Any) -> Dict[str, Any]:
    if isinstance(value, list):
        safe_items = [_safe_text(item) for item in value]
        return {
            "kind": "list",
            "item_count": len(safe_items),
            "preview": safe_items[:8],
            "safe_preview_only": True,
        }

    text = _safe_text(value)
    return {
        "kind": "text",
        "length": len(text),
        "preview": text[:220],
        "safe_preview_only": True,
    }


def _field_preview_map(detail_edit_preview: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    field_map: Dict[str, Dict[str, Any]] = {}

    for field in detail_edit_preview.get("editable_fields", []):
        if isinstance(field, dict) and field.get("field_id"):
            field_map[str(field.get("field_id"))] = field

    return field_map


def _build_version_card(detail_edit_preview: Dict[str, Any], stage: Dict[str, Any]) -> Dict[str, Any]:
    detail_edit_preview = dict(detail_edit_preview or {})
    stage = dict(stage or {})
    stage_id = _safe_text(stage.get("version_stage"))

    identity = {
        "pack": PACK_ID,
        "detail_edit_preview_id": detail_edit_preview.get("detail_edit_preview_id"),
        "owner_note_draft_id": detail_edit_preview.get("owner_note_draft_id"),
        "version_stage": stage_id,
    }

    version_card_id = f"owner_note_draft_version_card_{_stable_hash(identity, 18)}"

    field_map = _field_preview_map(detail_edit_preview)

    if stage_id == "original_draft":
        field_values = {
            field_id: _summarize_value(field.get("current_value"))
            for field_id, field in field_map.items()
        }
        change_summary = {
            "changed_field_count": 0,
            "changed_fields": [],
            "version_change_type": "baseline",
        }
    elif stage_id == "preview_edit":
        field_values = {
            field_id: _summarize_value(field.get("proposed_value"))
            for field_id, field in field_map.items()
        }
        changed_fields = [
            field_id
            for field_id, field in field_map.items()
            if field.get("changed") is True
        ]
        change_summary = {
            "changed_field_count": len(changed_fields),
            "changed_fields": changed_fields,
            "version_change_type": "preview_edit",
        }
    else:
        field_values = {
            field_id: _summarize_value(field.get("proposed_value"))
            for field_id, field in field_map.items()
        }
        changed_fields = [
            field_id
            for field_id, field in field_map.items()
            if field.get("changed") is True
        ]
        change_summary = {
            "changed_field_count": len(changed_fields),
            "changed_fields": changed_fields,
            "version_change_type": "blocked_save_attempt",
            "blocked_reason": "Preview-only pack. No real save, restore, rollback, or submit action is allowed.",
        }

    return {
        "version_card_id": version_card_id,
        "detail_edit_preview_id": _safe_text(detail_edit_preview.get("detail_edit_preview_id")),
        "owner_note_draft_id": _safe_text(detail_edit_preview.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(detail_edit_preview.get("saved_view_id")),
        "version_stage": stage_id,
        "version_order": int(stage.get("version_order") or 0),
        "label": _safe_text(stage.get("label")),
        "description": _safe_text(stage.get("description")),
        "field_values": field_values,
        "change_summary": change_summary,
        "version_status": "version_preview_ready",
        "version_result_type": "owner_note_draft_version_card_preview",
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_history_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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


def _build_field_change_event(detail_edit_preview: Dict[str, Any], field: Dict[str, Any]) -> Dict[str, Any]:
    detail_edit_preview = dict(detail_edit_preview or {})
    field = dict(field or {})

    field_id = _safe_text(field.get("field_id"))
    identity = {
        "pack": PACK_ID,
        "detail_edit_preview_id": detail_edit_preview.get("detail_edit_preview_id"),
        "owner_note_draft_id": detail_edit_preview.get("owner_note_draft_id"),
        "field_id": field_id,
    }

    event_id = f"owner_note_draft_field_change_event_{_stable_hash(identity, 18)}"

    return {
        "field_change_event_id": event_id,
        "detail_edit_preview_id": _safe_text(detail_edit_preview.get("detail_edit_preview_id")),
        "owner_note_draft_id": _safe_text(detail_edit_preview.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(detail_edit_preview.get("saved_view_id")),
        "field_id": field_id,
        "field_label": _safe_text(field.get("label")),
        "field_type": _safe_text(field.get("field_type")),
        "changed": bool(field.get("changed", False)),
        "current_value_summary": _summarize_value(field.get("current_value")),
        "proposed_value_summary": _summarize_value(field.get("proposed_value")),
        "validation": field.get("validation", {}),
        "change_event_status": "field_change_preview_ready",
        "change_event_type": "preview_field_change",
        "history_write_allowed_now": False,
        "real_history_written": False,
        "real_edit_persisted": False,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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


def _build_compare_preview(version_cards: List[Dict[str, Any]], field_change_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    original = next((card for card in version_cards if card.get("version_stage") == "original_draft"), {})
    preview = next((card for card in version_cards if card.get("version_stage") == "preview_edit"), {})

    changed_fields = [
        event.get("field_id")
        for event in field_change_events
        if event.get("changed") is True
    ]

    return {
        "compare_preview_id": f"owner_note_draft_compare_preview_{_stable_hash([original.get('version_card_id'), preview.get('version_card_id')], 18)}",
        "from_version_card_id": original.get("version_card_id"),
        "to_version_card_id": preview.get("version_card_id"),
        "from_version_stage": original.get("version_stage"),
        "to_version_stage": preview.get("version_stage"),
        "changed_field_count": len(changed_fields),
        "changed_fields": changed_fields,
        "compare_status": "compare_preview_ready",
        "compare_result_type": "owner_note_draft_version_compare_preview",
        "compare_allowed_in_preview": True,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_history_written": False,
        "real_edit_persisted": False,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "compare_preview_only": True,
        "rollback_preview_only": True,
    }


def _build_rollback_preview(version_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    preview = next((card for card in version_cards if card.get("version_stage") == "preview_edit"), {})
    original = next((card for card in version_cards if card.get("version_stage") == "original_draft"), {})

    return {
        "rollback_preview_id": f"owner_note_draft_rollback_preview_{_stable_hash([preview.get('version_card_id'), original.get('version_card_id')], 18)}",
        "from_version_card_id": preview.get("version_card_id"),
        "to_version_card_id": original.get("version_card_id"),
        "from_version_stage": preview.get("version_stage"),
        "to_version_stage": original.get("version_stage"),
        "rollback_status": "rollback_preview_blocked",
        "rollback_reason": "Rollback is preview-only. No real restore, save, history write, or edit persistence is allowed.",
        "rollback_allowed_in_preview": True,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_history_written": False,
        "real_edit_persisted": False,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "compare_preview_only": True,
        "rollback_preview_only": True,
    }



def _build_history_timeline(detail_edit_preview: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    detail_edit_preview = dict(detail_edit_preview or {})

    version_cards = [
        _build_version_card(detail_edit_preview, stage)
        for stage in VERSION_STAGES
    ]

    field_change_events = [
        _build_field_change_event(detail_edit_preview, field)
        for field in detail_edit_preview.get("editable_fields", [])
        if isinstance(field, dict)
    ]

    compare_preview = _build_compare_preview(version_cards, field_change_events)
    rollback_preview = _build_rollback_preview(version_cards)

    identity = {
        "pack": PACK_ID,
        "detail_edit_preview_id": detail_edit_preview.get("detail_edit_preview_id"),
        "owner_note_draft_id": detail_edit_preview.get("owner_note_draft_id"),
        "sequence": sequence,
    }

    timeline_id = f"owner_note_draft_edit_history_timeline_{_stable_hash(identity, 18)}"

    return {
        "edit_history_timeline_id": timeline_id,
        "sequence": sequence,
        "detail_edit_preview_id": _safe_text(detail_edit_preview.get("detail_edit_preview_id")),
        "owner_note_draft_id": _safe_text(detail_edit_preview.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(detail_edit_preview.get("saved_view_id")),
        "saved_view_preview_id": _safe_text(detail_edit_preview.get("saved_view_preview_id")),
        "label": _safe_text(detail_edit_preview.get("label")),
        "description": _safe_text(detail_edit_preview.get("description")),
        "draft_type": _safe_text(detail_edit_preview.get("draft_type")),
        "draft_priority": _safe_text(detail_edit_preview.get("draft_priority")),
        "requires_owner_review": bool(detail_edit_preview.get("requires_owner_review", False)),
        "timeline_status": "edit_history_version_preview_ready",
        "timeline_result_type": "owner_note_draft_edit_history_version_preview",
        "version_cards": version_cards,
        "version_card_count": len(version_cards),
        "field_change_events": field_change_events,
        "field_change_event_count": len(field_change_events),
        "compare_preview": compare_preview,
        "rollback_preview": rollback_preview,
        "tracked_fields": sorted(EXPECTED_TRACKED_FIELDS),
        "tracked_field_count": len(EXPECTED_TRACKED_FIELDS),
        "compare_allowed_in_preview": True,
        "rollback_allowed_in_preview": True,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "history_write_allowed_now": False,
        "real_history_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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


def _sort_timelines(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def _build_history_indexes(timelines: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_edit_history_timeline_id": {},
        "by_detail_edit_preview_id": {},
        "by_owner_note_draft_id": {},
        "by_saved_view_id": {},
        "by_draft_type": {},
        "by_draft_priority": {},
        "by_requires_owner_review": {},
        "by_timeline_status": {},
    }

    for item in timelines:
        timeline_id = _safe_text(item.get("edit_history_timeline_id"))
        if timeline_id:
            indexes["by_edit_history_timeline_id"][timeline_id] = item

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

        status = _safe_text(item.get("timeline_status")) or "unknown"
        indexes["by_timeline_status"].setdefault(status, []).append(item)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload_cached() -> Dict[str, Any]:
    pack_170_payload = _load_pack_170_payload(force_refresh=False)
    detail_edit_previews = pack_170_payload.get("detail_edit_previews", [])

    if not isinstance(detail_edit_previews, list):
        detail_edit_previews = []

    timelines = []
    for idx, detail_edit_preview in enumerate(detail_edit_previews, start=1):
        if isinstance(detail_edit_preview, dict):
            timelines.append(_build_history_timeline(detail_edit_preview, sequence=idx))

    timelines = _sort_timelines(timelines)
    indexes = _build_history_indexes(timelines)

    draft_type_counts = _count_by(timelines, "draft_type")
    draft_priority_counts = _count_by(timelines, "draft_priority")
    timeline_status_counts = _count_by(timelines, "timeline_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([item for item in timelines if item.get("requires_owner_review") is True]),
        "owner_review_not_required": len([item for item in timelines if item.get("requires_owner_review") is False]),
    }

    timeline_preview = {
        item.get("saved_view_id"): item
        for item in timelines
        if item.get("saved_view_id")
    }

    total_version_cards = sum(int(item.get("version_card_count") or 0) for item in timelines)
    total_field_change_events = sum(int(item.get("field_change_event_count") or 0) for item in timelines)

    readiness_checks = {
        "pack_170_ready": pack_170_payload.get("status") == "ready",
        "has_timelines": len(timelines) >= 1,
        "timeline_count_matches_detail_edit_previews": len(timelines) == len(detail_edit_previews),
        "all_simulated_only": all(item.get("simulated_only") is True for item in timelines),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in timelines),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in timelines),
        "all_rollback_preview_only": all(item.get("rollback_preview_only") is True for item in timelines),
        "all_compare_preview_only": all(item.get("compare_preview_only") is True for item in timelines),
        "all_edit_preview_only": all(item.get("edit_preview_only") is True for item in timelines),
        "all_detail_drawer_preview_only": all(item.get("detail_drawer_preview_only") is True for item in timelines),
        "all_owner_note_preview_only": all(item.get("owner_note_preview_only") is True for item in timelines),
        "all_review_draft_preview_only": all(item.get("review_draft_preview_only") is True for item in timelines),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in timelines),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in timelines),
        "all_filter_preview_only": all(item.get("filter_preview_only") is True for item in timelines),
        "all_search_facet_preview_only": all(item.get("search_facet_preview_only") is True for item in timelines),
        "all_lookup_preview_only": all(item.get("lookup_preview_only") is True for item in timelines),
        "all_detail_preview_only": all(item.get("detail_preview_only") is True for item in timelines),
        "all_evidence_drawer_preview_only": all(item.get("evidence_drawer_preview_only") is True for item in timelines),
        "all_owner_review_preview_only": all(item.get("owner_review_preview_only") is True for item in timelines),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in timelines),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in timelines),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in timelines),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in timelines),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in timelines),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in timelines),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in timelines),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in timelines),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in timelines),
        "no_real_history_written": all(item.get("real_history_written") is False for item in timelines),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in timelines),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in timelines),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in timelines),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in timelines),
        "no_real_note_written": all(item.get("real_note_written") is False for item in timelines),
        "no_real_draft_saved": all(item.get("real_draft_saved") is False for item in timelines),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in timelines),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in timelines),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in timelines),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in timelines),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in timelines),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in timelines),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in timelines),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in timelines),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in timelines),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in timelines),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in timelines),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in timelines),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in timelines),
        "no_real_owner_review_completed": all(item.get("real_owner_review_completed") is False for item in timelines),
        "no_real_owner_approval_executed": all(item.get("real_owner_approval_executed") is False for item in timelines),
        "no_real_owner_rejection_executed": all(item.get("real_owner_rejection_executed") is False for item in timelines),
        "no_real_owner_acknowledgement_executed": all(item.get("real_owner_acknowledgement_executed") is False for item in timelines),
        "no_real_evidence_revealed": all(item.get("real_evidence_revealed") is False for item in timelines),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in timelines),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in timelines),
        "all_restore_actions_blocked": all(item.get("restore_allowed_now") is False for item in timelines),
        "all_rollback_actions_blocked": all(item.get("rollback_allowed_now") is False for item in timelines),
        "all_save_actions_blocked": all(item.get("save_allowed_now") is False for item in timelines),
        "all_submit_actions_blocked": all(item.get("submit_allowed_now") is False for item in timelines),
        "all_history_write_actions_blocked": all(item.get("history_write_allowed_now") is False for item in timelines),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in timelines),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in timelines),
        "all_timeline_ids_present": all(bool(item.get("edit_history_timeline_id")) for item in timelines),
        "all_detail_edit_preview_ids_present": all(bool(item.get("detail_edit_preview_id")) for item in timelines),
        "all_owner_note_draft_ids_present": all(bool(item.get("owner_note_draft_id")) for item in timelines),
        "all_saved_view_ids_present": all(bool(item.get("saved_view_id")) for item in timelines),
        "all_timeline_result_type_present": all(item.get("timeline_result_type") == "owner_note_draft_edit_history_version_preview" for item in timelines),
        "all_timelines_ready": all(item.get("timeline_status") == "edit_history_version_preview_ready" for item in timelines),
        "all_have_three_version_cards": all(int(item.get("version_card_count") or 0) == 3 for item in timelines),
        "all_have_five_field_change_events": all(int(item.get("field_change_event_count") or 0) == 5 for item in timelines),
        "all_expected_tracked_fields_present": all(
            EXPECTED_TRACKED_FIELDS.issubset(set(item.get("tracked_fields", [])))
            for item in timelines
        ),
        "all_compare_previews_ready": all(item.get("compare_preview", {}).get("compare_status") == "compare_preview_ready" for item in timelines),
        "all_rollback_previews_blocked": all(item.get("rollback_preview", {}).get("rollback_status") == "rollback_preview_blocked" for item in timelines),
        "critical_owner_review_history_present": "critical_owner_review" in timeline_preview,
        "quarantine_review_history_present": "quarantine_review" in timeline_preview,
        "fresh_recheck_history_present": "fresh_recheck" in timeline_preview,
        "renewal_review_history_present": "renewal_review" in timeline_preview,
        "monitor_only_history_present": "monitor_only" in timeline_preview,
        "high_sensitivity_history_present": "high_sensitivity_redacted" in timeline_preview,
        "safe_preview_history_present": "safe_preview_only" in timeline_preview,
        "all_evidence_drawers_history_present": "all_evidence_drawers" in timeline_preview,
        "endpoint": OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT,
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
        "pack_number": 171,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Draft Edit History / Version Preview",
        "endpoint": OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT,
        "source_endpoint": OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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
        "real_history_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
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
        "source_pack_170": {
            "status": pack_170_payload.get("status"),
            "readiness_score": pack_170_payload.get("summary", {}).get("readiness_score"),
            "detail_edit_preview_count": pack_170_payload.get("summary", {}).get("detail_edit_preview_count"),
            "owner_note_draft_count": pack_170_payload.get("summary", {}).get("owner_note_draft_count"),
        },
        "summary": {
            "edit_history_timeline_count": len(timelines),
            "detail_edit_preview_count": len(detail_edit_previews),
            "version_card_count": total_version_cards,
            "field_change_event_count": total_field_change_events,
            "tracked_field_count": len(EXPECTED_TRACKED_FIELDS),
            "draft_type_counts": draft_type_counts,
            "draft_priority_counts": draft_priority_counts,
            "timeline_status_counts": timeline_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "expected_tracked_fields": sorted(EXPECTED_TRACKED_FIELDS),
            "version_stage_count": len(VERSION_STAGES),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note draft edit history/version preview ready" if readiness_score == 100 else "Owner note draft edit history/version preview needs review",
        },
        "readiness_checks": readiness_checks,
        "version_stages": VERSION_STAGES,
        "tracked_fields_schema": TRACKED_FIELDS,
        "edit_history_timelines": timelines,
        "timeline_preview": timeline_preview,
        "history_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 171,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note draft edit history/version preview ready"),
        "edit_history_timeline_count": summary.get("edit_history_timeline_count", 0),
        "detail_edit_preview_count": summary.get("detail_edit_preview_count", 0),
        "version_card_count": summary.get("version_card_count", 0),
        "field_change_event_count": summary.get("field_change_event_count", 0),
        "tracked_field_count": summary.get("tracked_field_count", 0),
        "draft_type_counts": summary.get("draft_type_counts", {}),
        "draft_priority_counts": summary.get("draft_priority_counts", {}),
        "timeline_status_counts": summary.get("timeline_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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
        "real_history_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
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


def get_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview",
        "label": "Owner Note Version History",
        "title": "Owner Note Draft Edit History / Version Preview",
        "href": OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT,
        "endpoint": OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT,
        "description": "Preview owner note draft version cards, field changes, compare preview, rollback preview, and blocked restore/save behavior.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 171",
        "category": "policy",
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "history_readiness",
            "title": "History readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note draft edit history/version preview ready"),
        },
        {
            "id": "timelines",
            "title": "History timelines",
            "value": summary.get("edit_history_timeline_count", 0),
            "label": "Drafts with preview version history",
        },
        {
            "id": "version_cards",
            "title": "Version cards",
            "value": summary.get("version_card_count", 0),
            "label": "Original/edit/blocked save stages",
        },
        {
            "id": "field_changes",
            "title": "Field changes",
            "value": summary.get("field_change_event_count", 0),
            "label": "Tracked field-level preview events",
        },
        {
            "id": "rollback",
            "title": "Rollback/restore",
            "value": "Blocked" if checks.get("all_rollback_actions_blocked") and checks.get("all_restore_actions_blocked") else "Review",
            "label": "Preview only",
        },
        {
            "id": "history_write",
            "title": "Real history write",
            "value": "No" if checks.get("no_real_history_written") else "Review",
            "label": "No persistence",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview",
        "title": "Owner Note Version History",
        "subtitle": "Preview version cards, field-level change summaries, compare views, rollback previews, and blocked restore/save actions.",
        "status": payload.get("status", "ready"),
        "href": OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-history-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-history-section" id="policy-change-approval-receipt-owner-note-draft-edit-history-version-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 171</p>
            <h2>{section.get('title', 'Owner Note Version History')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT}">Open owner note version history JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "OWNER_NOTE_DRAFT_EDIT_HISTORY_ENDPOINT",
    "OWNER_NOTE_DRAFT_DETAIL_EDIT_ENDPOINT",
    "VERSION_STAGES",
    "TRACKED_FIELDS",
    "EXPECTED_TRACKED_FIELDS",
    "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload",
    "get_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload",
    "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section",
]
