
"""
PACK 187 - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History Version Detail / Compare View.

This module sits on top of Pack 186.

Pack 186 creates preview-only edit history timelines and version cards for
version compare saved view/filter preset detail edit drawers.

Pack 187 creates preview-only version detail/compare drawers:
- version detail compare drawers
- side-by-side original vs draft compare rows
- changed/unchanged grouping
- rollback/restore/save blocked action previews
- indexes for drawers/cards/rows

Important:
- simulated-only
- version-detail-preview-only
- compare-view-preview-only
- edit-history-preview-only
- version-preview-only
- rollback-preview-only
- restore-preview-only
- no real history written
- no real version written/saved
- no real rollback/restore
- no real edit persisted
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


PACK_ID = "PACK_187"
VERSION_DETAIL_COMPARE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-preview.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
    lowered = text.lower()
    forbidden = [
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
    return "[REDACTED]" if any(fragment in lowered for fragment in forbidden) else text


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "restore_preview_only": True,
        "compare_preview_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preset_detail_preview_only": True,
        "saved_view_preset_edit_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "cached_non_recursive": True,
    }


def _load_pack_186_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_186",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "edit_history_timeline_count": 0,
                "version_card_count": 0,
                "field_change_event_count": 0,
                "readiness_score": 0,
            },
            "edit_history_timelines": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_186",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "edit_history_timeline_count": 0,
            "version_card_count": 0,
            "field_change_event_count": 0,
            "readiness_score": 0,
        },
        "edit_history_timelines": [],
        **_base_flags(),
    }


def _display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        if "display_value" in value:
            return _safe_text(value.get("display_value"))
        if "value" in value:
            raw = value.get("value")
            if isinstance(raw, list):
                return f"{len(raw)} items"
            if isinstance(raw, dict):
                return f"{len(raw)} keys"
            return _safe_text(raw)
        return f"{len(value)} keys"
    if isinstance(value, list):
        return f"{len(value)} items"
    return _safe_text(value)


def _build_compare_row(timeline: Dict[str, object], event: Dict[str, object], sequence: int) -> Dict[str, object]:
    timeline_id = _safe_text(timeline.get("edit_history_timeline_id"))
    detail_edit_drawer_id = _safe_text(timeline.get("detail_edit_drawer_id"))
    event_id = _safe_text(event.get("field_change_event_id"))
    field_id = _safe_text(event.get("field_id"))
    source_kind = _safe_text(timeline.get("source_kind"))
    source_id = _safe_text(timeline.get("source_id"))
    changed = bool(event.get("changed", False))

    identity = {
        "pack": PACK_ID,
        "timeline_id": timeline_id,
        "detail_edit_drawer_id": detail_edit_drawer_id,
        "event_id": event_id,
        "field_id": field_id,
        "sequence": sequence,
    }

    row = {
        "version_compare_row_id": f"version_compare_saved_view_filter_detail_edit_compare_row_{_stable_hash(identity, 18)}",
        "edit_history_timeline_id": timeline_id,
        "detail_edit_drawer_id": detail_edit_drawer_id,
        "field_change_event_id": event_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "field_id": field_id,
        "field_label": _safe_text(event.get("field_label")),
        "field_type": _safe_text(event.get("field_type")),
        "sequence": int(sequence),
        "changed": changed,
        "change_group": "changed_fields" if changed else "unchanged_fields",
        "left_version_label": "Original Detail Edit Snapshot",
        "right_version_label": "Draft Detail Edit Snapshot",
        "left_display_value": _safe_text(event.get("current_display_value")),
        "right_display_value": _safe_text(event.get("preview_display_value")),
        "current_value": event.get("current_value"),
        "preview_value": event.get("preview_value"),
        "row_status": "version_compare_saved_view_filter_detail_edit_compare_row_preview_ready",
        "row_result_type": "owner_note_version_compare_saved_view_filter_detail_edit_compare_row_preview",
        "safe_preview_only": True,
    }
    row.update(_base_flags())
    return row


def _build_version_detail_drawer(timeline: Dict[str, object], sequence: int) -> Dict[str, object]:
    timeline = dict(timeline or {})
    timeline_id = _safe_text(timeline.get("edit_history_timeline_id"))
    detail_edit_drawer_id = _safe_text(timeline.get("detail_edit_drawer_id"))
    source_kind = _safe_text(timeline.get("source_kind"))
    source_id = _safe_text(timeline.get("source_id"))

    events = timeline.get("field_change_events", [])
    if not isinstance(events, list):
        events = []

    compare_rows = [
        _build_compare_row(timeline, event, idx)
        for idx, event in enumerate(events, start=1)
        if isinstance(event, dict)
    ]

    changed_rows = [row for row in compare_rows if row.get("changed") is True]
    unchanged_rows = [row for row in compare_rows if row.get("changed") is False]

    version_cards = timeline.get("version_cards", [])
    if not isinstance(version_cards, list):
        version_cards = []

    original_version = next(
        (card for card in version_cards if isinstance(card, dict) and card.get("version_role") == "original"),
        version_cards[0] if version_cards else {},
    )
    draft_version = next(
        (card for card in version_cards if isinstance(card, dict) and card.get("version_role") == "draft_preview"),
        version_cards[1] if len(version_cards) > 1 else {},
    )
    compare_version = next(
        (card for card in version_cards if isinstance(card, dict) and card.get("version_role") == "compare_preview"),
        version_cards[2] if len(version_cards) > 2 else {},
    )

    identity = {
        "pack": PACK_ID,
        "timeline_id": timeline_id,
        "detail_edit_drawer_id": detail_edit_drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": sequence,
    }

    drawer_id = f"version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_{_stable_hash(identity, 18)}"

    drawer = {
        "version_detail_drawer_id": drawer_id,
        "edit_history_timeline_id": timeline_id,
        "detail_edit_drawer_id": detail_edit_drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": int(sequence),
        "drawer_status": "version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_preview_ready",
        "drawer_result_type": "owner_note_version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_preview",
        "original_version_card_id": original_version.get("version_card_id") if isinstance(original_version, dict) else None,
        "draft_version_card_id": draft_version.get("version_card_id") if isinstance(draft_version, dict) else None,
        "compare_version_card_id": compare_version.get("version_card_id") if isinstance(compare_version, dict) else None,
        "active_version_card_id": timeline.get("active_version_card_id"),
        "version_cards": version_cards,
        "version_card_count": len(version_cards),
        "compare_rows": compare_rows,
        "comparison_rows": compare_rows,
        "comparison_row_count": len(compare_rows),
        "changed_compare_rows": changed_rows,
        "unchanged_compare_rows": unchanged_rows,
        "changed_field_count": len(changed_rows),
        "unchanged_field_count": len(unchanged_rows),
        "compare_grouping": {
            "changed_fields": {
                "label": "Changed Fields",
                "row_count": len(changed_rows),
                "row_ids": [row.get("version_compare_row_id") for row in changed_rows],
            },
            "unchanged_fields": {
                "label": "Unchanged Fields",
                "row_count": len(unchanged_rows),
                "row_ids": [row.get("version_compare_row_id") for row in unchanged_rows],
            },
        },
        "rollback_action_preview": {
            "action_id": f"version_compare_saved_view_filter_detail_edit_rollback_action_{_stable_hash((drawer_id, 'rollback'), 18)}",
            "action_label": "Rollback to original detail edit preview",
            "target_version_card_id": original_version.get("version_card_id") if isinstance(original_version, dict) else None,
            "allowed_in_preview": True,
            "allowed_now": False,
            "real_rollback_executed": False,
            "safe_preview_only": True,
        },
        "restore_action_preview": {
            "action_id": f"version_compare_saved_view_filter_detail_edit_restore_action_{_stable_hash((drawer_id, 'restore'), 18)}",
            "action_label": "Restore draft detail edit preview",
            "target_version_card_id": draft_version.get("version_card_id") if isinstance(draft_version, dict) else None,
            "allowed_in_preview": True,
            "allowed_now": False,
            "real_restore_executed": False,
            "safe_preview_only": True,
        },
        "save_action_preview": {
            "action_id": f"version_compare_saved_view_filter_detail_edit_save_action_{_stable_hash((drawer_id, 'save'), 18)}",
            "action_label": "Save detail edit version preview",
            "target_version_card_id": draft_version.get("version_card_id") if isinstance(draft_version, dict) else None,
            "allowed_in_preview": True,
            "allowed_now": False,
            "real_version_saved": False,
            "real_edit_persisted": False,
            "safe_preview_only": True,
        },
        "safe_preview_only": True,
    }
    drawer.update(_base_flags())
    return drawer


def _build_indexes(drawers: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "version_detail_drawers_by_id": {},
        "version_detail_drawers_by_timeline_id": {},
        "version_detail_drawers_by_detail_edit_drawer_id": {},
        "version_detail_drawers_by_source_kind": {},
        "version_detail_drawers_by_source_id": {},
        "compare_rows_by_id": {},
        "compare_rows_by_drawer_id": {},
        "compare_rows_by_source_kind": {},
        "changed_compare_rows_by_drawer_id": {},
        "unchanged_compare_rows_by_drawer_id": {},
        "version_cards_by_id": {},
    }

    for drawer in drawers:
        drawer_id = _safe_text(drawer.get("version_detail_drawer_id"))
        timeline_id = _safe_text(drawer.get("edit_history_timeline_id"))
        detail_edit_drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
        source_kind = _safe_text(drawer.get("source_kind"))
        source_id = _safe_text(drawer.get("source_id"))

        indexes["version_detail_drawers_by_id"][drawer_id] = drawer
        indexes["version_detail_drawers_by_timeline_id"][timeline_id] = drawer
        indexes["version_detail_drawers_by_detail_edit_drawer_id"][detail_edit_drawer_id] = drawer
        indexes["version_detail_drawers_by_source_kind"].setdefault(source_kind, []).append(drawer)
        indexes["version_detail_drawers_by_source_id"][source_id] = drawer

        for card in drawer.get("version_cards", []):
            if isinstance(card, dict):
                card_id = _safe_text(card.get("version_card_id"))
                indexes["version_cards_by_id"][card_id] = card

        for row in drawer.get("compare_rows", []):
            if not isinstance(row, dict):
                continue
            row_id = _safe_text(row.get("version_compare_row_id"))
            indexes["compare_rows_by_id"][row_id] = row
            indexes["compare_rows_by_drawer_id"].setdefault(drawer_id, []).append(row)
            indexes["compare_rows_by_source_kind"].setdefault(source_kind, []).append(row)

            if row.get("changed") is True:
                indexes["changed_compare_rows_by_drawer_id"].setdefault(drawer_id, []).append(row)
            else:
                indexes["unchanged_compare_rows_by_drawer_id"].setdefault(drawer_id, []).append(row)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload_cached() -> Dict[str, object]:
    pack_186 = _load_pack_186_payload(force_refresh=False)

    timelines = pack_186.get("edit_history_timelines", [])
    if not isinstance(timelines, list):
        timelines = []

    version_detail_drawers = [
        _build_version_detail_drawer(timeline, idx)
        for idx, timeline in enumerate(timelines, start=1)
        if isinstance(timeline, dict)
    ]

    all_compare_rows = []
    all_version_cards = []
    for drawer in version_detail_drawers:
        all_compare_rows.extend(drawer.get("compare_rows", []))
        all_version_cards.extend(drawer.get("version_cards", []))

    changed_rows = [row for row in all_compare_rows if isinstance(row, dict) and row.get("changed") is True]
    unchanged_rows = [row for row in all_compare_rows if isinstance(row, dict) and row.get("changed") is False]

    saved_view_drawers = [drawer for drawer in version_detail_drawers if drawer.get("source_kind") == "saved_view_preset"]
    filter_preset_drawers = [drawer for drawer in version_detail_drawers if drawer.get("source_kind") == "filter_preset"]

    indexes = _build_indexes(version_detail_drawers)

    readiness_checks = {
        "pack_186_ready": pack_186.get("status") == "ready",
        "has_timelines": len(timelines) >= 15,
        "has_version_detail_drawers": len(version_detail_drawers) >= 15,
        "version_detail_drawer_count_matches_timelines": len(version_detail_drawers) == len(timelines),
        "saved_view_drawer_count_is_six": len(saved_view_drawers) == 6,
        "filter_preset_drawer_count_is_nine": len(filter_preset_drawers) >= 9,
        "all_version_detail_drawers_ready": all(drawer.get("drawer_status") == "version_compare_saved_view_filter_detail_edit_version_detail_compare_drawer_preview_ready" for drawer in version_detail_drawers),
        "all_drawers_have_three_version_cards": all(int(drawer.get("version_card_count") or 0) == 3 for drawer in version_detail_drawers),
        "all_drawers_have_five_compare_rows": all(int(drawer.get("comparison_row_count") or 0) == 5 for drawer in version_detail_drawers),
        "has_compare_rows": len(all_compare_rows) >= 75,
        "has_changed_compare_rows": len(changed_rows) >= 1,
        "has_unchanged_compare_rows": len(unchanged_rows) >= 1,
        "has_version_cards": len(all_version_cards) >= 45,
        "all_compare_rows_ready": all(row.get("row_status") == "version_compare_saved_view_filter_detail_edit_compare_row_preview_ready" for row in all_compare_rows if isinstance(row, dict)),
        "all_rollback_actions_blocked": all(drawer.get("rollback_action_preview", {}).get("allowed_now") is False for drawer in version_detail_drawers),
        "all_restore_actions_blocked": all(drawer.get("restore_action_preview", {}).get("allowed_now") is False for drawer in version_detail_drawers),
        "all_save_actions_blocked": all(drawer.get("save_action_preview", {}).get("allowed_now") is False for drawer in version_detail_drawers),
        "version_detail_indexes_present": bool(indexes.get("version_detail_drawers_by_id")),
        "compare_row_indexes_present": bool(indexes.get("compare_rows_by_id")),
        "changed_compare_row_indexes_present": bool(indexes.get("changed_compare_rows_by_drawer_id")),
        "unchanged_compare_row_indexes_present": bool(indexes.get("unchanged_compare_rows_by_drawer_id")),
        "version_card_indexes_present": bool(indexes.get("version_cards_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_rollback_preview_only": all(item.get("rollback_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "all_restore_preview_only": all(item.get("restore_preview_only") is True for item in version_detail_drawers + all_compare_rows),
        "no_real_history_written": all(item.get("real_history_written") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_version_written": all(item.get("real_version_written") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in version_detail_drawers + all_compare_rows),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in version_detail_drawers + all_compare_rows),
        "all_history_writes_blocked": all(item.get("history_write_allowed_now") is False for item in version_detail_drawers + all_compare_rows),
        "all_version_writes_blocked": all(item.get("version_write_allowed_now") is False for item in version_detail_drawers + all_compare_rows),
        "all_version_saves_blocked": all(item.get("version_save_allowed_now") is False for item in version_detail_drawers + all_compare_rows),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in version_detail_drawers + all_compare_rows),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in version_detail_drawers + all_compare_rows),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in version_detail_drawers + all_compare_rows),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in version_detail_drawers + all_compare_rows),
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 187,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Saved View / Filter Preset Detail Edit History Version Detail / Compare View",
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_186": {
            "status": pack_186.get("status"),
            "readiness_score": pack_186.get("summary", {}).get("readiness_score"),
            "edit_history_timeline_count": pack_186.get("summary", {}).get("edit_history_timeline_count"),
            "version_card_count": pack_186.get("summary", {}).get("version_card_count"),
            "field_change_event_count": pack_186.get("summary", {}).get("field_change_event_count"),
            "changed_field_event_count": pack_186.get("summary", {}).get("changed_field_event_count"),
            "unchanged_field_event_count": pack_186.get("summary", {}).get("unchanged_field_event_count"),
        },
        "summary": {
            "version_detail_drawer_count": len(version_detail_drawers),
            "saved_view_version_detail_drawer_count": len(saved_view_drawers),
            "filter_preset_version_detail_drawer_count": len(filter_preset_drawers),
            "version_card_count": len(all_version_cards),
            "comparison_row_count": len(all_compare_rows),
            "changed_compare_row_count": len(changed_rows),
            "unchanged_compare_row_count": len(unchanged_rows),
            "rollback_action_preview_count": len(version_detail_drawers),
            "restore_action_preview_count": len(version_detail_drawers),
            "save_action_preview_count": len(version_detail_drawers),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare saved view/filter preset detail edit history version detail/compare view ready" if readiness_score == 100 else "Owner note version compare saved view/filter preset detail edit history version detail/compare view needs review",
        },
        "readiness_checks": readiness_checks,
        "version_detail_drawers": version_detail_drawers,
        "version_detail_compare_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 187,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count"),
        "saved_view_version_detail_drawer_count": summary.get("saved_view_version_detail_drawer_count"),
        "filter_preset_version_detail_drawer_count": summary.get("filter_preset_version_detail_drawer_count"),
        "version_card_count": summary.get("version_card_count"),
        "comparison_row_count": summary.get("comparison_row_count"),
        "changed_compare_row_count": summary.get("changed_compare_row_count"),
        "unchanged_compare_row_count": summary.get("unchanged_compare_row_count"),
        "rollback_action_preview_count": summary.get("rollback_action_preview_count"),
        "restore_action_preview_count": summary.get("restore_action_preview_count"),
        "save_action_preview_count": summary.get("save_action_preview_count"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view",
        "label": "Owner Note Version Compare Detail View",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Saved View / Filter Preset Detail Edit History Version Detail / Compare View",
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "description": "Preview version detail compare drawers, side-by-side compare rows, changed/unchanged grouping, and blocked rollback/restore/save actions.",
        "status": bridge.get("status"),
        "pack": "Pack 187",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view",
        "title": "Owner Note Version Compare Detail View",
        "subtitle": "Preview version detail compare drawers, side-by-side compare rows, changed/unchanged grouping, and blocked rollback/restore/save actions.",
        "status": payload.get("status"),
        "href": VERSION_DETAIL_COMPARE_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Version detail readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "drawers", "title": "Detail drawers", "value": summary.get("version_detail_drawer_count"), "label": "Version detail compare drawers"},
            {"id": "compare_rows", "title": "Compare rows", "value": summary.get("comparison_row_count"), "label": "Side-by-side compare rows"},
            {"id": "changed_rows", "title": "Changed rows", "value": summary.get("changed_compare_row_count"), "label": "Changed compare rows"},
            {"id": "version_cards", "title": "Version cards", "value": summary.get("version_card_count"), "label": "Preview version cards"},
            {"id": "blocked_actions", "title": "Actions", "value": "Blocked" if checks.get("all_save_actions_blocked") and checks.get("all_rollback_actions_blocked") else "Review", "label": "No real save/rollback/restore"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-detail-view-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-detail-view-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 187</p>
            <h2>{section.get('title', 'Owner Note Version Compare Detail View')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{VERSION_DETAIL_COMPARE_ENDPOINT}">Open version compare detail view JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "VERSION_DETAIL_COMPARE_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_html_section",
]
