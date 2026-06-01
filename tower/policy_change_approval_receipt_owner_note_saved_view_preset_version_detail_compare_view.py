
"""
PACK 177 - Owner Note Saved View Preset Version Detail / Compare View.

This module sits on top of Pack 176.

Pack 176 creates preview-only edit history/version scaffolding.
Pack 177 creates preview-only version detail/compare scaffolding:
- version detail drawers
- side-by-side original vs preview compare rows
- changed/unchanged groups
- blocked restore/rollback/save/version/history writes

Important:
- simulated-only
- version-detail-preview-only
- compare-view-preview-only
- edit-history-preview-only
- version-preview-only
- rollback-preview-only
- saved-view-preset-detail-preview-only
- saved-view-preset-edit-preview-only
- saved-navigation-preview-only
- saved-filter-preset-preview-only
- no real history written
- no real version written
- no real version saved
- no real rollback executed
- no real restore executed
- no real edit persisted
- no real saved-view writes
- no real user-preference writes
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


PACK_ID = "PACK_177"
VERSION_DETAIL_COMPARE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"
EDIT_HISTORY_VERSION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json"


COMPARE_FIELDS = [
    "label",
    "description",
    "filter_lane_id",
    "view_priority",
    "is_default",
]


FIELD_LABELS = {
    "label": "Preset Label",
    "description": "Preset Description",
    "filter_lane_id": "Filter Lane",
    "view_priority": "View Priority",
    "is_default": "Default View",
}


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


def _load_pack_176_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_176",
            "status": "review",
            "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
            "simulated_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "summary": {
                "edit_history_timeline_count": 0,
                "version_card_count": 0,
                "field_change_event_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 176 saved view preset edit history/version payload unavailable",
            },
            "edit_history_timelines": [],
            "load_error": str(exc),
        }

    return {
        "pack_id": "PACK_176",
        "status": "review",
        "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "simulated_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "summary": {
            "edit_history_timeline_count": 0,
            "version_card_count": 0,
            "field_change_event_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 176 saved view preset edit history/version payload unavailable",
        },
        "edit_history_timelines": [],
    }


def _priority_rank(priority: Any) -> int:
    ranking = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }
    return ranking.get(_safe_text(priority), 99)


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _normalize_compare_value(value: Any) -> Dict[str, Any]:
    if isinstance(value, bool):
        return {
            "kind": "boolean",
            "value": value,
            "display_value": "Yes" if value else "No",
            "safe_preview_only": True,
        }

    if isinstance(value, list):
        return {
            "kind": "list",
            "value": [_safe_text(item) for item in value],
            "item_count": len(value),
            "safe_preview_only": True,
        }

    if isinstance(value, dict):
        return {
            "kind": "object",
            "value": {
                _safe_text(k): _safe_text(v)
                for k, v in value.items()
            },
            "item_count": len(value),
            "safe_preview_only": True,
        }

    text = _safe_text(value)
    return {
        "kind": "text",
        "value": text,
        "length": len(text),
        "safe_preview_only": True,
    }


def _build_compare_row(timeline: Dict[str, Any], field_id: str, sequence: int) -> Dict[str, Any]:
    original = timeline.get("original_snapshot", {})
    preview = timeline.get("preview_edit_snapshot", {})

    if not isinstance(original, dict):
        original = {}
    if not isinstance(preview, dict):
        preview = {}

    original_value = original.get(field_id)
    preview_value = preview.get(field_id)

    normalized_original = _normalize_compare_value(original_value)
    normalized_preview = _normalize_compare_value(preview_value)
    changed = normalized_original != normalized_preview

    identity = {
        "pack": PACK_ID,
        "timeline": timeline.get("edit_history_timeline_id"),
        "field_id": field_id,
        "sequence": sequence,
        "original": normalized_original,
        "preview": normalized_preview,
    }

    return {
        "compare_row_id": f"saved_view_preset_version_compare_row_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(timeline.get("saved_view_preset_id")),
        "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
        "detail_edit_drawer_id": _safe_text(timeline.get("detail_edit_drawer_id")),
        "sequence": int(sequence),
        "field_id": field_id,
        "field_label": FIELD_LABELS.get(field_id, field_id),
        "original_value": normalized_original,
        "preview_value": normalized_preview,
        "changed": changed,
        "comparison_status": "saved_view_preset_version_compare_row_preview_ready",
        "comparison_result_type": "owner_note_saved_view_preset_version_compare_row_preview",
        "safe_preview_only": True,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def _build_comparison_groups(compare_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    changed_rows = [row for row in compare_rows if row.get("changed") is True]
    unchanged_rows = [row for row in compare_rows if row.get("changed") is False]

    return {
        "changed_fields": {
            "count": len(changed_rows),
            "field_ids": [row.get("field_id") for row in changed_rows],
            "rows": changed_rows,
        },
        "unchanged_fields": {
            "count": len(unchanged_rows),
            "field_ids": [row.get("field_id") for row in unchanged_rows],
            "rows": unchanged_rows,
        },
        "group_status": "saved_view_preset_version_compare_groups_preview_ready",
        "group_result_type": "owner_note_saved_view_preset_version_compare_groups_preview",
        "safe_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_version_detail_drawer(timeline: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    timeline = dict(timeline or {})

    compare_rows = [
        _build_compare_row(timeline, field_id, idx)
        for idx, field_id in enumerate(COMPARE_FIELDS, start=1)
    ]

    comparison_groups = _build_comparison_groups(compare_rows)

    identity = {
        "pack": PACK_ID,
        "timeline": timeline.get("edit_history_timeline_id"),
        "preset": timeline.get("saved_view_preset_id"),
        "sequence": sequence,
    }

    drawer_sections = [
        {
            "section_id": "version_identity",
            "title": "Version Identity",
            "safe_for_preview": True,
            "content": {
                "saved_view_preset_id": _safe_text(timeline.get("saved_view_preset_id")),
                "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
                "detail_edit_drawer_id": _safe_text(timeline.get("detail_edit_drawer_id")),
            },
        },
        {
            "section_id": "original_snapshot",
            "title": "Original Snapshot",
            "safe_for_preview": True,
            "content": timeline.get("original_snapshot", {}),
        },
        {
            "section_id": "preview_edit_snapshot",
            "title": "Preview Edit Snapshot",
            "safe_for_preview": True,
            "content": timeline.get("preview_edit_snapshot", {}),
        },
        {
            "section_id": "compare_rows",
            "title": "Compare Rows",
            "safe_for_preview": True,
            "content": {
                "compare_row_count": len(compare_rows),
                "changed_field_count": comparison_groups.get("changed_fields", {}).get("count"),
                "unchanged_field_count": comparison_groups.get("unchanged_fields", {}).get("count"),
            },
        },
        {
            "section_id": "blocked_restore_rollback",
            "title": "Blocked Restore / Rollback",
            "safe_for_preview": True,
            "content": {
                "restore_allowed_now": False,
                "rollback_allowed_now": False,
                "real_restore_executed": False,
                "real_rollback_executed": False,
            },
        },
        {
            "section_id": "blocked_history_version_writes",
            "title": "Blocked History / Version Writes",
            "safe_for_preview": True,
            "content": {
                "history_write_allowed_now": False,
                "version_write_allowed_now": False,
                "real_history_written": False,
                "real_version_written": False,
                "real_version_saved": False,
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
        "version_detail_drawer_id": f"saved_view_preset_version_detail_compare_drawer_{_stable_hash(identity, 18)}",
        "sequence": int(sequence),
        "saved_view_preset_id": _safe_text(timeline.get("saved_view_preset_id")),
        "edit_history_timeline_id": _safe_text(timeline.get("edit_history_timeline_id")),
        "detail_edit_drawer_id": _safe_text(timeline.get("detail_edit_drawer_id")),
        "label": _safe_text(timeline.get("label")),
        "filter_lane_id": _safe_text(timeline.get("filter_lane_id")),
        "view_priority": _safe_text(timeline.get("view_priority")),
        "is_default": bool(timeline.get("is_default", False)),
        "drawer_status": "saved_view_preset_version_detail_compare_view_preview_ready",
        "drawer_result_type": "owner_note_saved_view_preset_version_detail_compare_drawer_preview",
        "original_snapshot": timeline.get("original_snapshot", {}),
        "preview_edit_snapshot": timeline.get("preview_edit_snapshot", {}),
        "version_cards": timeline.get("version_cards", []),
        "version_card_count": int(timeline.get("version_card_count") or 0),
        "field_change_events": timeline.get("field_change_events", []),
        "field_change_event_count": int(timeline.get("field_change_event_count") or 0),
        "compare_rows": compare_rows,
        "comparison_row_count": len(compare_rows),
        "comparison_groups": comparison_groups,
        "changed_field_count": comparison_groups.get("changed_fields", {}).get("count", 0),
        "unchanged_field_count": comparison_groups.get("unchanged_fields", {}).get("count", 0),
        "drawer_sections": drawer_sections,
        "drawer_section_count": len(drawer_sections),
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
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
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_detail_indexes(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_version_detail_drawer_id": {},
        "by_edit_history_timeline_id": {},
        "by_detail_edit_drawer_id": {},
        "by_saved_view_preset_id": {},
        "by_filter_lane_id": {},
        "by_view_priority": {},
        "by_default_state": {},
        "by_drawer_status": {},
        "compare_rows_by_id": {},
    }

    for drawer in drawers:
        drawer_id = _safe_text(drawer.get("version_detail_drawer_id"))
        if drawer_id:
            indexes["by_version_detail_drawer_id"][drawer_id] = drawer

        timeline_id = _safe_text(drawer.get("edit_history_timeline_id"))
        if timeline_id:
            indexes["by_edit_history_timeline_id"][timeline_id] = drawer

        detail_id = _safe_text(drawer.get("detail_edit_drawer_id"))
        if detail_id:
            indexes["by_detail_edit_drawer_id"][detail_id] = drawer

        preset_id = _safe_text(drawer.get("saved_view_preset_id"))
        if preset_id:
            indexes["by_saved_view_preset_id"][preset_id] = drawer

        lane_id = _safe_text(drawer.get("filter_lane_id")) or "unknown"
        indexes["by_filter_lane_id"].setdefault(lane_id, []).append(drawer)

        priority = _safe_text(drawer.get("view_priority")) or "unknown"
        indexes["by_view_priority"].setdefault(priority, []).append(drawer)

        default_key = "default" if drawer.get("is_default") else "not_default"
        indexes["by_default_state"].setdefault(default_key, []).append(drawer)

        status = _safe_text(drawer.get("drawer_status")) or "unknown"
        indexes["by_drawer_status"].setdefault(status, []).append(drawer)

        for row in drawer.get("compare_rows", []):
            row_id = _safe_text(row.get("compare_row_id"))
            if row_id:
                indexes["compare_rows_by_id"][row_id] = row

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload_cached() -> Dict[str, Any]:
    pack_176_payload = _load_pack_176_payload(force_refresh=False)
    timelines = pack_176_payload.get("edit_history_timelines", [])

    if not isinstance(timelines, list):
        timelines = []

    sorted_timelines = sorted(
        [timeline for timeline in timelines if isinstance(timeline, dict)],
        key=lambda item: (
            0 if item.get("is_default") else 1,
            _priority_rank(item.get("view_priority")),
            _safe_text(item.get("saved_view_preset_id")),
        ),
    )

    drawers = [
        _build_version_detail_drawer(timeline, sequence=idx)
        for idx, timeline in enumerate(sorted_timelines, start=1)
    ]

    indexes = _build_detail_indexes(drawers)

    drawer_status_counts = _count_by(drawers, "drawer_status")
    view_priority_counts = _count_by(drawers, "view_priority")
    filter_lane_counts = _count_by(drawers, "filter_lane_id")
    default_state_counts = {
        "default": len([drawer for drawer in drawers if drawer.get("is_default") is True]),
        "not_default": len([drawer for drawer in drawers if drawer.get("is_default") is False]),
    }

    total_compare_rows = sum(int(drawer.get("comparison_row_count") or 0) for drawer in drawers)
    total_changed_fields = sum(int(drawer.get("changed_field_count") or 0) for drawer in drawers)
    total_unchanged_fields = sum(int(drawer.get("unchanged_field_count") or 0) for drawer in drawers)
    total_drawer_sections = sum(int(drawer.get("drawer_section_count") or 0) for drawer in drawers)
    total_version_cards = sum(int(drawer.get("version_card_count") or 0) for drawer in drawers)
    total_field_events = sum(int(drawer.get("field_change_event_count") or 0) for drawer in drawers)

    drawer_preview = {
        drawer.get("saved_view_preset_id"): drawer
        for drawer in drawers
        if drawer.get("saved_view_preset_id")
    }

    readiness_checks = {
        "pack_176_ready": pack_176_payload.get("status") == "ready",
        "has_version_detail_drawers": len(drawers) >= 1,
        "drawer_count_matches_timelines": len(drawers) == len(timelines),
        "all_drawers_ready": all(drawer.get("drawer_status") == "saved_view_preset_version_detail_compare_view_preview_ready" for drawer in drawers),
        "all_have_five_compare_rows": all(int(drawer.get("comparison_row_count") or 0) == 5 for drawer in drawers),
        "all_have_three_version_cards": all(int(drawer.get("version_card_count") or 0) == 3 for drawer in drawers),
        "all_have_five_field_change_events": all(int(drawer.get("field_change_event_count") or 0) == 5 for drawer in drawers),
        "all_have_seven_drawer_sections": all(int(drawer.get("drawer_section_count") or 0) >= 7 for drawer in drawers),
        "all_have_comparison_groups": all(isinstance(drawer.get("comparison_groups"), dict) for drawer in drawers),
        "all_have_original_snapshot": all(isinstance(drawer.get("original_snapshot"), dict) and bool(drawer.get("original_snapshot")) for drawer in drawers),
        "all_have_preview_edit_snapshot": all(isinstance(drawer.get("preview_edit_snapshot"), dict) and bool(drawer.get("preview_edit_snapshot")) for drawer in drawers),
        "all_simulated_only": all(drawer.get("simulated_only") is True for drawer in drawers),
        "all_version_detail_preview_only": all(drawer.get("version_detail_preview_only") is True for drawer in drawers),
        "all_compare_view_preview_only": all(drawer.get("compare_view_preview_only") is True for drawer in drawers),
        "all_edit_history_preview_only": all(drawer.get("edit_history_preview_only") is True for drawer in drawers),
        "all_version_preview_only": all(drawer.get("version_preview_only") is True for drawer in drawers),
        "all_rollback_preview_only": all(drawer.get("rollback_preview_only") is True for drawer in drawers),
        "all_saved_view_preset_detail_preview_only": all(drawer.get("saved_view_preset_detail_preview_only") is True for drawer in drawers),
        "all_saved_view_preset_edit_preview_only": all(drawer.get("saved_view_preset_edit_preview_only") is True for drawer in drawers),
        "all_saved_navigation_preview_only": all(drawer.get("saved_navigation_preview_only") is True for drawer in drawers),
        "all_saved_filter_preset_preview_only": all(drawer.get("saved_filter_preset_preview_only") is True for drawer in drawers),
        "all_navigation_preview_only": all(drawer.get("navigation_preview_only") is True for drawer in drawers),
        "all_filter_navigation_preview_only": all(drawer.get("filter_navigation_preview_only") is True for drawer in drawers),
        "all_saved_view_preview_only": all(drawer.get("saved_view_preview_only") is True for drawer in drawers),
        "all_filter_preset_preview_only": all(drawer.get("filter_preset_preview_only") is True for drawer in drawers),
        "no_real_history_written": all(drawer.get("real_history_written") is False for drawer in drawers),
        "no_real_version_written": all(drawer.get("real_version_written") is False for drawer in drawers),
        "no_real_version_saved": all(drawer.get("real_version_saved") is False for drawer in drawers),
        "no_real_rollback_executed": all(drawer.get("real_rollback_executed") is False for drawer in drawers),
        "no_real_restore_executed": all(drawer.get("real_restore_executed") is False for drawer in drawers),
        "no_real_edit_persisted": all(drawer.get("real_edit_persisted") is False for drawer in drawers),
        "no_real_saved_view_written": all(drawer.get("real_saved_view_written") is False for drawer in drawers),
        "no_real_user_preference_written": all(drawer.get("real_user_preference_written") is False for drawer in drawers),
        "no_real_filter_preference_saved": all(drawer.get("real_filter_preference_saved") is False for drawer in drawers),
        "no_real_navigation_state_persisted": all(drawer.get("real_navigation_state_persisted") is False for drawer in drawers),
        "no_real_drawer_selection_saved": all(drawer.get("real_drawer_selection_saved") is False for drawer in drawers),
        "all_restore_actions_blocked": all(drawer.get("restore_allowed_now") is False for drawer in drawers),
        "all_rollback_actions_blocked": all(drawer.get("rollback_allowed_now") is False for drawer in drawers),
        "all_save_actions_blocked": all(drawer.get("save_allowed_now") is False for drawer in drawers),
        "all_persist_actions_blocked": all(drawer.get("persist_allowed_now") is False for drawer in drawers),
        "all_history_writes_blocked": all(drawer.get("history_write_allowed_now") is False for drawer in drawers),
        "all_version_writes_blocked": all(drawer.get("version_write_allowed_now") is False for drawer in drawers),
        "all_saved_view_writes_blocked": all(drawer.get("saved_view_write_allowed_now") is False for drawer in drawers),
        "all_user_preference_writes_blocked": all(drawer.get("user_preference_write_allowed_now") is False for drawer in drawers),
        "all_raw_evidence_reveal_blocked": all(drawer.get("raw_evidence_reveal_allowed") is False for drawer in drawers),
        "all_raw_evidence_lookup_blocked": all(drawer.get("raw_evidence_lookup_allowed") is False for drawer in drawers),
        "default_all_compare_drawers_drawer_present": "default_all_compare_drawers" in drawer_preview,
        "owner_review_focus_drawer_present": "owner_review_focus" in drawer_preview,
        "critical_priority_focus_drawer_present": "critical_priority_focus" in drawer_preview,
        "high_priority_focus_drawer_present": "high_priority_focus" in drawer_preview,
        "monitor_only_focus_drawer_present": "monitor_only_focus" in drawer_preview,
        "safe_preview_focus_drawer_present": "safe_preview_focus" in drawer_preview,
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
        "pack_number": 177,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Version Detail / Compare View",
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "source_endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "cached_non_recursive": True,
        "source_pack_176": {
            "status": pack_176_payload.get("status"),
            "readiness_score": pack_176_payload.get("summary", {}).get("readiness_score"),
            "edit_history_timeline_count": pack_176_payload.get("summary", {}).get("edit_history_timeline_count"),
            "version_card_count": pack_176_payload.get("summary", {}).get("version_card_count"),
            "field_change_event_count": pack_176_payload.get("summary", {}).get("field_change_event_count"),
        },
        "summary": {
            "version_detail_drawer_count": len(drawers),
            "source_edit_history_timeline_count": len(timelines),
            "comparison_row_count": total_compare_rows,
            "changed_field_count": total_changed_fields,
            "unchanged_field_count": total_unchanged_fields,
            "drawer_section_count": total_drawer_sections,
            "version_card_count": total_version_cards,
            "field_change_event_count": total_field_events,
            "compare_field_count": len(COMPARE_FIELDS),
            "drawer_status_counts": drawer_status_counts,
            "view_priority_counts": view_priority_counts,
            "filter_lane_counts": filter_lane_counts,
            "default_state_counts": default_state_counts,
            "readiness_score": readiness_score,
            "readiness_label": "Owner note saved view preset version detail/compare preview ready" if readiness_score == 100 else "Owner note saved view preset version detail/compare preview needs review",
        },
        "readiness_checks": readiness_checks,
        "compare_fields": COMPARE_FIELDS,
        "field_labels": FIELD_LABELS,
        "version_detail_drawers": drawers,
        "drawer_preview": drawer_preview,
        "version_detail_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 177,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", VERSION_DETAIL_COMPARE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", EDIT_HISTORY_VERSION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note saved view preset version detail/compare preview ready"),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count", 0),
        "source_edit_history_timeline_count": summary.get("source_edit_history_timeline_count", 0),
        "comparison_row_count": summary.get("comparison_row_count", 0),
        "changed_field_count": summary.get("changed_field_count", 0),
        "unchanged_field_count": summary.get("unchanged_field_count", 0),
        "drawer_section_count": summary.get("drawer_section_count", 0),
        "version_card_count": summary.get("version_card_count", 0),
        "field_change_event_count": summary.get("field_change_event_count", 0),
        "compare_field_count": summary.get("compare_field_count", 0),
        "drawer_status_counts": summary.get("drawer_status_counts", {}),
        "view_priority_counts": summary.get("view_priority_counts", {}),
        "filter_lane_counts": summary.get("filter_lane_counts", {}),
        "default_state_counts": summary.get("default_state_counts", {}),
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view",
        "label": "Owner Note Preset Version Compare",
        "title": "Owner Note Saved View Preset Version Detail / Compare View",
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "description": "Preview saved view preset version detail drawers, compare rows, changed fields, and blocked rollback/restore.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 177",
        "category": "policy",
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "version_detail_readiness",
            "title": "Version compare readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note saved view preset version detail/compare preview ready"),
        },
        {
            "id": "detail_drawers",
            "title": "Detail drawers",
            "value": summary.get("version_detail_drawer_count", 0),
            "label": "Preset version detail drawers",
        },
        {
            "id": "compare_rows",
            "title": "Compare rows",
            "value": summary.get("comparison_row_count", 0),
            "label": "Side-by-side field comparisons",
        },
        {
            "id": "changed_fields",
            "title": "Changed fields",
            "value": summary.get("changed_field_count", 0),
            "label": "Preview changes detected",
        },
        {
            "id": "history_version_write",
            "title": "History/version write",
            "value": "Blocked" if checks.get("all_history_writes_blocked") and checks.get("all_version_writes_blocked") else "Review",
            "label": "No real history/version write",
        },
        {
            "id": "rollback_restore",
            "title": "Rollback / restore",
            "value": "Blocked" if checks.get("all_rollback_actions_blocked") and checks.get("all_restore_actions_blocked") else "Review",
            "label": "No real rollback",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view",
        "title": "Owner Note Preset Version Compare",
        "subtitle": "Preview saved view preset version detail drawers, side-by-side compare rows, changed fields, and blocked rollback/restore.",
        "status": payload.get("status", "ready"),
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-preset-version-compare-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-preset-version-compare-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 177</p>
            <h2>{section.get('title', 'Owner Note Preset Version Compare')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{VERSION_DETAIL_COMPARE_ENDPOINT}">Open owner note preset version compare JSON</a>
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
    "COMPARE_FIELDS",
    "FIELD_LABELS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_html_section",
]
