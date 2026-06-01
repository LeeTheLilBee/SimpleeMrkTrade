
"""
PACK 172 - Owner Note Draft Version Detail Drawer / Compare View.

This module sits on top of Pack 171.

Pack 171 creates preview-only edit history/version timelines.
Pack 172 creates deeper preview-only version detail drawer / compare view scaffolding:
- version detail drawer previews
- side-by-side original vs preview edit comparison
- field-by-field comparison rows
- changed/unchanged grouping
- compare drawer metadata
- blocked restore/rollback/save actions

Important:
- simulated-only
- version-detail-preview-only
- compare-view-preview-only
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
- no real version writes/saves
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


PACK_ID = "PACK_172"
VERSION_DETAIL_COMPARE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"
EDIT_HISTORY_VERSION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json"


COMPARE_FIELD_ORDER = [
    "review_reason",
    "owner_review_comment_draft",
    "decision_draft_language",
    "acknowledgement_draft_language",
    "draft_tags",
]


COMPARE_GROUPS = {
    "changed_fields": {
        "label": "Changed Fields",
        "description": "Fields where the preview edit differs from the original draft.",
    },
    "unchanged_fields": {
        "label": "Unchanged Fields",
        "description": "Fields where the preview edit matches the original draft.",
    },
}


EXPECTED_COMPARE_FIELDS = set(COMPARE_FIELD_ORDER)


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


def _safe_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [_safe_text(item) for item in value if _safe_text(item)]
    if value:
        return [_safe_text(value)]
    return []


def _load_pack_171_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_171",
            "status": "review",
            "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "edit_history_timeline_count": 0,
                "version_card_count": 0,
                "field_change_event_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 171 edit history/version preview payload unavailable",
            },
            "edit_history_timelines": [],
        }

    return {
        "pack_id": "PACK_171",
        "status": "review",
        "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
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
        "summary": {
            "edit_history_timeline_count": 0,
            "version_card_count": 0,
            "field_change_event_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 171 edit history/version preview payload unavailable",
        },
        "edit_history_timelines": [],
    }



def _find_version_card(timeline: Dict[str, Any], version_stage: str) -> Dict[str, Any]:
    for card in timeline.get("version_cards", []):
        if isinstance(card, dict) and card.get("version_stage") == version_stage:
            return card
    return {}


def _value_summary_to_compare_value(summary: Any) -> Dict[str, Any]:
    if not isinstance(summary, dict):
        return {
            "kind": "unknown",
            "display_value": _safe_text(summary),
            "safe_preview_only": True,
        }

    kind = _safe_text(summary.get("kind"))
    if kind == "list":
        preview = _safe_list(summary.get("preview"))
        return {
            "kind": "list",
            "display_value": preview,
            "item_count": int(summary.get("item_count") or len(preview)),
            "safe_preview_only": True,
        }

    return {
        "kind": kind or "text",
        "display_value": _safe_text(summary.get("preview")),
        "length": int(summary.get("length") or 0),
        "safe_preview_only": True,
    }


def _build_field_comparison_row(
    timeline: Dict[str, Any],
    field_id: str,
    original_card: Dict[str, Any],
    preview_card: Dict[str, Any],
) -> Dict[str, Any]:
    timeline = dict(timeline or {})
    original_card = dict(original_card or {})
    preview_card = dict(preview_card or {})

    field_meta = COMPARE_GROUPS  # keeps local lint/simple compile happy
    del field_meta

    original_values = original_card.get("field_values", {}) if isinstance(original_card.get("field_values"), dict) else {}
    preview_values = preview_card.get("field_values", {}) if isinstance(preview_card.get("field_values"), dict) else {}

    original_value = _value_summary_to_compare_value(original_values.get(field_id))
    preview_value = _value_summary_to_compare_value(preview_values.get(field_id))

    changed = original_value != preview_value

    identity = {
        "pack": PACK_ID,
        "timeline": timeline.get("edit_history_timeline_id"),
        "field_id": field_id,
        "original": original_value,
        "preview": preview_value,
    }

    row_id = f"version_detail_compare_row_{_stable_hash(identity, 18)}"

    return {
        "compare_row_id": row_id,
        "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
        "detail_edit_preview_id": _safe_text(timeline.get("detail_edit_preview_id")),
        "owner_note_draft_id": _safe_text(timeline.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(timeline.get("saved_view_id")),
        "field_id": field_id,
        "field_label": _safe_text(field_id.replace("_", " ").title()),
        "original_version_card_id": _safe_text(original_card.get("version_card_id")),
        "preview_version_card_id": _safe_text(preview_card.get("version_card_id")),
        "original_value": original_value,
        "preview_value": preview_value,
        "changed": changed,
        "change_group": "changed_fields" if changed else "unchanged_fields",
        "row_status": "field_compare_preview_ready",
        "row_result_type": "owner_note_draft_version_field_compare_row_preview",
        "safe_preview_only": True,
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
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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


def _group_comparison_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    changed_rows = [row for row in rows if row.get("changed") is True]
    unchanged_rows = [row for row in rows if row.get("changed") is False]

    return {
        "changed_fields": {
            "label": COMPARE_GROUPS["changed_fields"]["label"],
            "description": COMPARE_GROUPS["changed_fields"]["description"],
            "count": len(changed_rows),
            "field_ids": [row.get("field_id") for row in changed_rows],
            "rows": changed_rows,
        },
        "unchanged_fields": {
            "label": COMPARE_GROUPS["unchanged_fields"]["label"],
            "description": COMPARE_GROUPS["unchanged_fields"]["description"],
            "count": len(unchanged_rows),
            "field_ids": [row.get("field_id") for row in unchanged_rows],
            "rows": unchanged_rows,
        },
        "group_status": "comparison_groups_preview_ready",
        "safe_preview_only": True,
    }


def _build_compare_metadata(
    timeline: Dict[str, Any],
    original_card: Dict[str, Any],
    preview_card: Dict[str, Any],
    comparison_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    identity = {
        "pack": PACK_ID,
        "timeline": timeline.get("edit_history_timeline_id"),
        "original": original_card.get("version_card_id"),
        "preview": preview_card.get("version_card_id"),
    }

    changed_count = len([row for row in comparison_rows if row.get("changed") is True])
    unchanged_count = len([row for row in comparison_rows if row.get("changed") is False])

    return {
        "compare_metadata_id": f"version_detail_compare_metadata_{_stable_hash(identity, 18)}",
        "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
        "owner_note_draft_id": _safe_text(timeline.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(timeline.get("saved_view_id")),
        "from_version_card_id": _safe_text(original_card.get("version_card_id")),
        "to_version_card_id": _safe_text(preview_card.get("version_card_id")),
        "from_version_stage": _safe_text(original_card.get("version_stage")),
        "to_version_stage": _safe_text(preview_card.get("version_stage")),
        "field_count": len(comparison_rows),
        "changed_field_count": changed_count,
        "unchanged_field_count": unchanged_count,
        "compare_status": "version_detail_compare_metadata_ready",
        "compare_result_type": "owner_note_draft_version_detail_compare_metadata_preview",
        "compare_allowed_in_preview": True,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_history_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
    }


def _build_version_detail_drawer(timeline: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    timeline = dict(timeline or {})

    original_card = _find_version_card(timeline, "original_draft")
    preview_card = _find_version_card(timeline, "preview_edit")
    blocked_card = _find_version_card(timeline, "blocked_save_attempt")

    comparison_rows = [
        _build_field_comparison_row(timeline, field_id, original_card, preview_card)
        for field_id in COMPARE_FIELD_ORDER
    ]

    comparison_groups = _group_comparison_rows(comparison_rows)
    compare_metadata = _build_compare_metadata(timeline, original_card, preview_card, comparison_rows)

    identity = {
        "pack": PACK_ID,
        "timeline": timeline.get("edit_history_timeline_id"),
        "owner_note_draft_id": timeline.get("owner_note_draft_id"),
        "sequence": sequence,
    }

    drawer_id = f"owner_note_draft_version_detail_compare_drawer_{_stable_hash(identity, 18)}"

    drawer_sections = [
        {
            "section_id": "drawer_identity",
            "title": "Drawer Identity",
            "safe_for_preview": True,
            "content": {
                "drawer_id": drawer_id,
                "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
                "owner_note_draft_id": _safe_text(timeline.get("owner_note_draft_id")),
                "saved_view_id": _safe_text(timeline.get("saved_view_id")),
            },
        },
        {
            "section_id": "side_by_side_versions",
            "title": "Side-by-Side Versions",
            "safe_for_preview": True,
            "content": {
                "original_version_card_id": _safe_text(original_card.get("version_card_id")),
                "preview_version_card_id": _safe_text(preview_card.get("version_card_id")),
                "blocked_save_version_card_id": _safe_text(blocked_card.get("version_card_id")),
            },
        },
        {
            "section_id": "comparison_rows",
            "title": "Field Comparison Rows",
            "safe_for_preview": True,
            "content": {
                "row_count": len(comparison_rows),
                "field_ids": [row.get("field_id") for row in comparison_rows],
            },
        },
        {
            "section_id": "comparison_groups",
            "title": "Changed / Unchanged Groups",
            "safe_for_preview": True,
            "content": {
                "changed_count": comparison_groups["changed_fields"]["count"],
                "unchanged_count": comparison_groups["unchanged_fields"]["count"],
            },
        },
        {
            "section_id": "blocked_actions",
            "title": "Blocked Actions",
            "safe_for_preview": True,
            "content": {
                "restore_allowed_now": False,
                "rollback_allowed_now": False,
                "save_allowed_now": False,
                "submit_allowed_now": False,
                "real_history_written": False,
                "real_version_saved": False,
                "real_rollback_executed": False,
                "real_restore_executed": False,
            },
        },
        {
            "section_id": "safety_flags",
            "title": "Safety Flags",
            "safe_for_preview": True,
            "content": {
                "simulated_only": True,
                "version_detail_preview_only": True,
                "compare_view_preview_only": True,
                "raw_evidence_reveal_allowed": False,
            },
        },
    ]

    return {
        "version_detail_drawer_id": drawer_id,
        "sequence": sequence,
        "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
        "detail_edit_preview_id": _safe_text(timeline.get("detail_edit_preview_id")),
        "owner_note_draft_id": _safe_text(timeline.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(timeline.get("saved_view_id")),
        "saved_view_preview_id": _safe_text(timeline.get("saved_view_preview_id")),
        "label": _safe_text(timeline.get("label")),
        "description": _safe_text(timeline.get("description")),
        "draft_type": _safe_text(timeline.get("draft_type")),
        "draft_priority": _safe_text(timeline.get("draft_priority")),
        "requires_owner_review": bool(timeline.get("requires_owner_review", False)),
        "drawer_status": "version_detail_compare_view_preview_ready",
        "drawer_result_type": "owner_note_draft_version_detail_compare_drawer_preview",
        "original_version_card": original_card,
        "preview_edit_version_card": preview_card,
        "blocked_save_attempt_version_card": blocked_card,
        "comparison_rows": comparison_rows,
        "comparison_row_count": len(comparison_rows),
        "comparison_groups": comparison_groups,
        "compare_metadata": compare_metadata,
        "drawer_sections": drawer_sections,
        "drawer_section_count": len(drawer_sections),
        "compare_allowed_in_preview": True,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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



def _sort_version_detail_drawers(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def _build_version_detail_indexes(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_version_detail_drawer_id": {},
        "by_edit_history_timeline_id": {},
        "by_detail_edit_preview_id": {},
        "by_owner_note_draft_id": {},
        "by_saved_view_id": {},
        "by_draft_type": {},
        "by_draft_priority": {},
        "by_requires_owner_review": {},
        "by_drawer_status": {},
    }

    for drawer in drawers:
        drawer_id = _safe_text(drawer.get("version_detail_drawer_id"))
        if drawer_id:
            indexes["by_version_detail_drawer_id"][drawer_id] = drawer

        timeline_id = _safe_text(drawer.get("edit_history_timeline_id"))
        if timeline_id:
            indexes["by_edit_history_timeline_id"][timeline_id] = drawer

        detail_id = _safe_text(drawer.get("detail_edit_preview_id"))
        if detail_id:
            indexes["by_detail_edit_preview_id"][detail_id] = drawer

        draft_id = _safe_text(drawer.get("owner_note_draft_id"))
        if draft_id:
            indexes["by_owner_note_draft_id"][draft_id] = drawer

        saved_view_id = _safe_text(drawer.get("saved_view_id")) or "unknown"
        indexes["by_saved_view_id"][saved_view_id] = drawer

        draft_type = _safe_text(drawer.get("draft_type")) or "unknown"
        indexes["by_draft_type"].setdefault(draft_type, []).append(drawer)

        priority = _safe_text(drawer.get("draft_priority")) or "unknown"
        indexes["by_draft_priority"].setdefault(priority, []).append(drawer)

        review_key = "owner_review_required" if drawer.get("requires_owner_review") else "owner_review_not_required"
        indexes["by_requires_owner_review"].setdefault(review_key, []).append(drawer)

        status = _safe_text(drawer.get("drawer_status")) or "unknown"
        indexes["by_drawer_status"].setdefault(status, []).append(drawer)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload_cached() -> Dict[str, Any]:
    pack_171_payload = _load_pack_171_payload(force_refresh=False)
    timelines = pack_171_payload.get("edit_history_timelines", [])

    if not isinstance(timelines, list):
        timelines = []

    drawers = []
    for idx, timeline in enumerate(timelines, start=1):
        if isinstance(timeline, dict):
            drawers.append(_build_version_detail_drawer(timeline, sequence=idx))

    drawers = _sort_version_detail_drawers(drawers)
    indexes = _build_version_detail_indexes(drawers)

    draft_type_counts = _count_by(drawers, "draft_type")
    draft_priority_counts = _count_by(drawers, "draft_priority")
    drawer_status_counts = _count_by(drawers, "drawer_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([drawer for drawer in drawers if drawer.get("requires_owner_review") is True]),
        "owner_review_not_required": len([drawer for drawer in drawers if drawer.get("requires_owner_review") is False]),
    }

    drawer_preview = {
        drawer.get("saved_view_id"): drawer
        for drawer in drawers
        if drawer.get("saved_view_id")
    }

    total_comparison_rows = sum(int(drawer.get("comparison_row_count") or 0) for drawer in drawers)
    total_drawer_sections = sum(int(drawer.get("drawer_section_count") or 0) for drawer in drawers)
    total_changed_fields = sum(
        int(drawer.get("comparison_groups", {}).get("changed_fields", {}).get("count") or 0)
        for drawer in drawers
    )
    total_unchanged_fields = sum(
        int(drawer.get("comparison_groups", {}).get("unchanged_fields", {}).get("count") or 0)
        for drawer in drawers
    )

    readiness_checks = {
        "pack_171_ready": pack_171_payload.get("status") == "ready",
        "has_version_detail_drawers": len(drawers) >= 1,
        "drawer_count_matches_timelines": len(drawers) == len(timelines),
        "all_simulated_only": all(drawer.get("simulated_only") is True for drawer in drawers),
        "all_version_detail_preview_only": all(drawer.get("version_detail_preview_only") is True for drawer in drawers),
        "all_compare_view_preview_only": all(drawer.get("compare_view_preview_only") is True for drawer in drawers),
        "all_version_preview_only": all(drawer.get("version_preview_only") is True for drawer in drawers),
        "all_edit_history_preview_only": all(drawer.get("edit_history_preview_only") is True for drawer in drawers),
        "all_rollback_preview_only": all(drawer.get("rollback_preview_only") is True for drawer in drawers),
        "all_compare_preview_only": all(drawer.get("compare_preview_only") is True for drawer in drawers),
        "all_edit_preview_only": all(drawer.get("edit_preview_only") is True for drawer in drawers),
        "all_detail_drawer_preview_only": all(drawer.get("detail_drawer_preview_only") is True for drawer in drawers),
        "all_owner_note_preview_only": all(drawer.get("owner_note_preview_only") is True for drawer in drawers),
        "all_review_draft_preview_only": all(drawer.get("review_draft_preview_only") is True for drawer in drawers),
        "all_saved_view_preview_only": all(drawer.get("saved_view_preview_only") is True for drawer in drawers),
        "all_filter_preset_preview_only": all(drawer.get("filter_preset_preview_only") is True for drawer in drawers),
        "all_filter_preview_only": all(drawer.get("filter_preview_only") is True for drawer in drawers),
        "all_search_facet_preview_only": all(drawer.get("search_facet_preview_only") is True for drawer in drawers),
        "all_lookup_preview_only": all(drawer.get("lookup_preview_only") is True for drawer in drawers),
        "all_detail_preview_only": all(drawer.get("detail_preview_only") is True for drawer in drawers),
        "all_evidence_drawer_preview_only": all(drawer.get("evidence_drawer_preview_only") is True for drawer in drawers),
        "all_owner_review_preview_only": all(drawer.get("owner_review_preview_only") is True for drawer in drawers),
        "all_queue_preview_only": all(drawer.get("queue_preview_only") is True for drawer in drawers),
        "all_renewal_preview_only": all(drawer.get("renewal_preview_only") is True for drawer in drawers),
        "all_recheck_preview_only": all(drawer.get("recheck_preview_only") is True for drawer in drawers),
        "all_expiration_preview_only": all(drawer.get("expiration_preview_only") is True for drawer in drawers),
        "all_vault_preview_only": all(drawer.get("vault_preview_only") is True for drawer in drawers),
        "all_index_preview_only": all(drawer.get("index_preview_only") is True for drawer in drawers),
        "all_receipt_preview_only": all(drawer.get("receipt_preview_only") is True for drawer in drawers),
        "all_approval_preview_only": all(drawer.get("approval_preview_only") is True for drawer in drawers),
        "all_evidence_preview_only": all(drawer.get("evidence_preview_only") is True for drawer in drawers),
        "no_real_history_written": all(drawer.get("real_history_written") is False for drawer in drawers),
        "no_real_version_written": all(drawer.get("real_version_written") is False for drawer in drawers),
        "no_real_version_saved": all(drawer.get("real_version_saved") is False for drawer in drawers),
        "no_real_rollback_executed": all(drawer.get("real_rollback_executed") is False for drawer in drawers),
        "no_real_restore_executed": all(drawer.get("real_restore_executed") is False for drawer in drawers),
        "no_real_edit_persisted": all(drawer.get("real_edit_persisted") is False for drawer in drawers),
        "no_real_note_written": all(drawer.get("real_note_written") is False for drawer in drawers),
        "no_real_draft_saved": all(drawer.get("real_draft_saved") is False for drawer in drawers),
        "no_real_approval_executed": all(drawer.get("real_approval_executed") is False for drawer in drawers),
        "no_real_policy_change": all(drawer.get("real_policy_change_executed") is False for drawer in drawers),
        "no_real_permission_change": all(drawer.get("real_permission_change_executed") is False for drawer in drawers),
        "no_real_access_granted": all(drawer.get("real_access_granted") is False for drawer in drawers),
        "no_real_enforcement": all(drawer.get("real_enforcement_executed") is False for drawer in drawers),
        "no_real_audit_written": all(drawer.get("real_audit_written") is False for drawer in drawers),
        "no_real_receipt_written": all(drawer.get("real_receipt_written") is False for drawer in drawers),
        "no_real_archive_written": all(drawer.get("real_archive_written") is False for drawer in drawers),
        "no_real_vault_written": all(drawer.get("real_vault_written") is False for drawer in drawers),
        "no_real_expiration_enforced": all(drawer.get("real_expiration_enforced") is False for drawer in drawers),
        "no_real_recheck_executed": all(drawer.get("real_recheck_executed") is False for drawer in drawers),
        "no_real_renewal_executed": all(drawer.get("real_renewal_executed") is False for drawer in drawers),
        "no_real_queue_action_executed": all(drawer.get("real_queue_action_executed") is False for drawer in drawers),
        "no_real_owner_review_completed": all(drawer.get("real_owner_review_completed") is False for drawer in drawers),
        "no_real_owner_approval_executed": all(drawer.get("real_owner_approval_executed") is False for drawer in drawers),
        "no_real_owner_rejection_executed": all(drawer.get("real_owner_rejection_executed") is False for drawer in drawers),
        "no_real_owner_acknowledgement_executed": all(drawer.get("real_owner_acknowledgement_executed") is False for drawer in drawers),
        "no_real_evidence_revealed": all(drawer.get("real_evidence_revealed") is False for drawer in drawers),
        "no_real_saved_view_written": all(drawer.get("real_saved_view_written") is False for drawer in drawers),
        "no_real_user_preference_written": all(drawer.get("real_user_preference_written") is False for drawer in drawers),
        "all_restore_actions_blocked": all(drawer.get("restore_allowed_now") is False for drawer in drawers),
        "all_rollback_actions_blocked": all(drawer.get("rollback_allowed_now") is False for drawer in drawers),
        "all_save_actions_blocked": all(drawer.get("save_allowed_now") is False for drawer in drawers),
        "all_submit_actions_blocked": all(drawer.get("submit_allowed_now") is False for drawer in drawers),
        "all_history_write_actions_blocked": all(drawer.get("history_write_allowed_now") is False for drawer in drawers),
        "all_version_write_actions_blocked": all(drawer.get("version_write_allowed_now") is False for drawer in drawers),
        "all_raw_evidence_reveal_blocked": all(drawer.get("raw_evidence_reveal_allowed") is False for drawer in drawers),
        "all_raw_evidence_lookup_blocked": all(drawer.get("raw_evidence_lookup_allowed") is False for drawer in drawers),
        "all_drawer_ids_present": all(bool(drawer.get("version_detail_drawer_id")) for drawer in drawers),
        "all_timeline_ids_present": all(bool(drawer.get("edit_history_timeline_id")) for drawer in drawers),
        "all_detail_edit_preview_ids_present": all(bool(drawer.get("detail_edit_preview_id")) for drawer in drawers),
        "all_owner_note_draft_ids_present": all(bool(drawer.get("owner_note_draft_id")) for drawer in drawers),
        "all_saved_view_ids_present": all(bool(drawer.get("saved_view_id")) for drawer in drawers),
        "all_drawer_result_type_present": all(drawer.get("drawer_result_type") == "owner_note_draft_version_detail_compare_drawer_preview" for drawer in drawers),
        "all_drawers_ready": all(drawer.get("drawer_status") == "version_detail_compare_view_preview_ready" for drawer in drawers),
        "all_have_five_comparison_rows": all(int(drawer.get("comparison_row_count") or 0) == 5 for drawer in drawers),
        "all_have_six_drawer_sections": all(int(drawer.get("drawer_section_count") or 0) >= 6 for drawer in drawers),
        "all_have_original_version_card": all(bool(drawer.get("original_version_card", {}).get("version_card_id")) for drawer in drawers),
        "all_have_preview_version_card": all(bool(drawer.get("preview_edit_version_card", {}).get("version_card_id")) for drawer in drawers),
        "all_have_blocked_save_version_card": all(bool(drawer.get("blocked_save_attempt_version_card", {}).get("version_card_id")) for drawer in drawers),
        "all_have_compare_metadata": all(bool(drawer.get("compare_metadata", {}).get("compare_metadata_id")) for drawer in drawers),
        "all_compare_metadata_ready": all(drawer.get("compare_metadata", {}).get("compare_status") == "version_detail_compare_metadata_ready" for drawer in drawers),
        "all_changed_groups_present": all("changed_fields" in drawer.get("comparison_groups", {}) for drawer in drawers),
        "all_unchanged_groups_present": all("unchanged_fields" in drawer.get("comparison_groups", {}) for drawer in drawers),
        "all_expected_compare_fields_present": all(
            EXPECTED_COMPARE_FIELDS.issubset({row.get("field_id") for row in drawer.get("comparison_rows", [])})
            for drawer in drawers
        ),
        "critical_owner_review_compare_present": "critical_owner_review" in drawer_preview,
        "quarantine_review_compare_present": "quarantine_review" in drawer_preview,
        "fresh_recheck_compare_present": "fresh_recheck" in drawer_preview,
        "renewal_review_compare_present": "renewal_review" in drawer_preview,
        "monitor_only_compare_present": "monitor_only" in drawer_preview,
        "high_sensitivity_compare_present": "high_sensitivity_redacted" in drawer_preview,
        "safe_preview_compare_present": "safe_preview_only" in drawer_preview,
        "all_evidence_drawers_compare_present": "all_evidence_drawers" in drawer_preview,
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
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
        "pack_number": 172,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Draft Version Detail Drawer / Compare View",
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "source_endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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
        "real_version_written": False,
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
        "source_pack_171": {
            "status": pack_171_payload.get("status"),
            "readiness_score": pack_171_payload.get("summary", {}).get("readiness_score"),
            "edit_history_timeline_count": pack_171_payload.get("summary", {}).get("edit_history_timeline_count"),
            "version_card_count": pack_171_payload.get("summary", {}).get("version_card_count"),
            "field_change_event_count": pack_171_payload.get("summary", {}).get("field_change_event_count"),
        },
        "summary": {
            "version_detail_drawer_count": len(drawers),
            "edit_history_timeline_count": len(timelines),
            "comparison_row_count": total_comparison_rows,
            "drawer_section_count": total_drawer_sections,
            "changed_field_count": total_changed_fields,
            "unchanged_field_count": total_unchanged_fields,
            "compare_field_count": len(EXPECTED_COMPARE_FIELDS),
            "draft_type_counts": draft_type_counts,
            "draft_priority_counts": draft_priority_counts,
            "drawer_status_counts": drawer_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "expected_compare_fields": sorted(EXPECTED_COMPARE_FIELDS),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note draft version detail drawer/compare view ready" if readiness_score == 100 else "Owner note draft version detail drawer/compare view needs review",
        },
        "readiness_checks": readiness_checks,
        "compare_field_order": COMPARE_FIELD_ORDER,
        "compare_groups": COMPARE_GROUPS,
        "version_detail_drawers": drawers,
        "drawer_preview": drawer_preview,
        "version_detail_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload_cached())


def get_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 172,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", VERSION_DETAIL_COMPARE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", EDIT_HISTORY_VERSION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note draft version detail drawer/compare view ready"),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count", 0),
        "edit_history_timeline_count": summary.get("edit_history_timeline_count", 0),
        "comparison_row_count": summary.get("comparison_row_count", 0),
        "drawer_section_count": summary.get("drawer_section_count", 0),
        "changed_field_count": summary.get("changed_field_count", 0),
        "unchanged_field_count": summary.get("unchanged_field_count", 0),
        "compare_field_count": summary.get("compare_field_count", 0),
        "draft_type_counts": summary.get("draft_type_counts", {}),
        "draft_priority_counts": summary.get("draft_priority_counts", {}),
        "drawer_status_counts": summary.get("drawer_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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
        "real_version_written": False,
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


def get_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view",
        "label": "Owner Note Version Compare",
        "title": "Owner Note Draft Version Detail Drawer / Compare View",
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "description": "Preview side-by-side owner note version details, field comparison rows, changed/unchanged grouping, and blocked restore/save actions.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 172",
        "category": "policy",
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "compare_readiness",
            "title": "Compare readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note draft version detail drawer/compare view ready"),
        },
        {
            "id": "version_detail_drawers",
            "title": "Version detail drawers",
            "value": summary.get("version_detail_drawer_count", 0),
            "label": "Timelines with compare drawers",
        },
        {
            "id": "comparison_rows",
            "title": "Comparison rows",
            "value": summary.get("comparison_row_count", 0),
            "label": "Field-by-field preview rows",
        },
        {
            "id": "changed_fields",
            "title": "Changed fields",
            "value": summary.get("changed_field_count", 0),
            "label": "Preview differences grouped",
        },
        {
            "id": "blocked_restore",
            "title": "Restore/rollback",
            "value": "Blocked" if checks.get("all_restore_actions_blocked") and checks.get("all_rollback_actions_blocked") else "Review",
            "label": "No real restore",
        },
        {
            "id": "version_write",
            "title": "Real version write",
            "value": "No" if checks.get("no_real_version_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view",
        "title": "Owner Note Version Compare",
        "subtitle": "Preview side-by-side version detail drawers, field comparison rows, changed/unchanged grouping, and blocked restore/save actions.",
        "status": payload.get("status", "ready"),
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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


def build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-section" id="policy-change-approval-receipt-owner-note-draft-version-detail-compare-view">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 172</p>
            <h2>{section.get('title', 'Owner Note Version Compare')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{VERSION_DETAIL_COMPARE_ENDPOINT}">Open owner note version compare JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "VERSION_DETAIL_COMPARE_ENDPOINT",
    "EDIT_HISTORY_VERSION_ENDPOINT",
    "COMPARE_FIELD_ORDER",
    "COMPARE_GROUPS",
    "EXPECTED_COMPARE_FIELDS",
    "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload",
    "get_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload",
    "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge",
    "get_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_status_bridge",
    "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_quick_action",
    "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section",
]
