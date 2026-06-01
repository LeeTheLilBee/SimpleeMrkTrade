
"""
PACK 186 - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History / Version Preview.

This module sits on top of Pack 185.

Pack 185 creates preview-only detail/edit drawers for version compare saved view/filter presets.
Pack 186 creates preview-only edit history/version scaffolding:
- edit history timelines
- version preview cards
- field change event previews
- compare preview metadata
- rollback/restore preview metadata
- blocked history/version/save/restore/rollback writes

Important:
- simulated-only
- edit-history-preview-only
- version-preview-only
- rollback-preview-only
- restore-preview-only
- detail-edit-preview-only
- saved-view-preview-only
- filter-preset-preview-only
- no real history written
- no real version written/saved
- no real rollback/restore
- no real edit persisted
- no real saved view written
- no real user preference written
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


PACK_ID = "PACK_186"
EDIT_HISTORY_VERSION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-preview.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-preview.json"


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
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
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


def _load_pack_185_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_185",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "total_detail_drawer_count": 0,
                "total_editable_row_count": 0,
                "readiness_score": 0,
            },
            "saved_view_detail_edit_drawers": [],
            "filter_preset_detail_edit_drawers": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_185",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "total_detail_drawer_count": 0,
            "total_editable_row_count": 0,
            "readiness_score": 0,
        },
        "saved_view_detail_edit_drawers": [],
        "filter_preset_detail_edit_drawers": [],
        **_base_flags(),
    }


def _value_display(value_payload: Any) -> str:
    if isinstance(value_payload, dict):
        if "display_value" in value_payload:
            return _safe_text(value_payload.get("display_value"))
        value = value_payload.get("value")
        if isinstance(value, list):
            return f"{len(value)} items"
        if isinstance(value, dict):
            return f"{len(value)} keys"
        return _safe_text(value)
    return _safe_text(value_payload)


def _build_field_change_event(drawer: Dict[str, object], row: Dict[str, object], sequence: int) -> Dict[str, object]:
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    row_id = _safe_text(row.get("editable_field_row_id"))
    field_id = _safe_text(row.get("field_id"))
    changed = bool(row.get("changed", False))

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "row_id": row_id,
        "field_id": field_id,
        "sequence": sequence,
    }

    event = {
        "field_change_event_id": f"version_compare_saved_view_filter_detail_edit_field_change_event_{_stable_hash(identity, 18)}",
        "detail_edit_drawer_id": drawer_id,
        "editable_field_row_id": row_id,
        "source_kind": _safe_text(drawer.get("source_kind")),
        "source_id": _safe_text(drawer.get("source_id")),
        "field_id": field_id,
        "field_label": _safe_text(row.get("field_label")),
        "field_type": _safe_text(row.get("field_type")),
        "sequence": int(sequence),
        "changed": changed,
        "change_status": "changed_preview" if changed else "unchanged_preview",
        "current_display_value": _value_display(row.get("current_value")),
        "preview_display_value": _value_display(row.get("preview_value")),
        "current_value": row.get("current_value"),
        "preview_value": row.get("preview_value"),
        "event_status": "version_compare_saved_view_filter_detail_edit_field_change_event_preview_ready",
        "event_result_type": "owner_note_version_compare_saved_view_filter_detail_edit_field_change_event_preview",
        "safe_preview_only": True,
    }
    event.update(_base_flags())
    return event


def _build_version_card(drawer: Dict[str, object], version_number: int, field_events: List[Dict[str, object]]) -> Dict[str, object]:
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    source_kind = _safe_text(drawer.get("source_kind"))
    source_id = _safe_text(drawer.get("source_id"))

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "version_number": version_number,
    }

    changed_count = len([event for event in field_events if event.get("changed") is True])
    unchanged_count = len([event for event in field_events if event.get("changed") is False])

    if version_number == 1:
        label = "Original Detail Edit Snapshot"
        version_role = "original"
        active = False
        field_change_ids = []
    elif version_number == 2:
        label = "Draft Detail Edit Snapshot"
        version_role = "draft_preview"
        active = True
        field_change_ids = [event.get("field_change_event_id") for event in field_events if event.get("changed") is True]
    else:
        label = "Compare Detail Edit Snapshot"
        version_role = "compare_preview"
        active = False
        field_change_ids = [event.get("field_change_event_id") for event in field_events]

    card = {
        "version_card_id": f"version_compare_saved_view_filter_detail_edit_version_card_{_stable_hash(identity, 18)}",
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "version_number": int(version_number),
        "version_label": label,
        "version_role": version_role,
        "is_active_preview": active,
        "field_change_event_ids": field_change_ids,
        "changed_field_count": changed_count if version_number != 1 else 0,
        "unchanged_field_count": unchanged_count if version_number == 3 else 0,
        "version_status": "version_compare_saved_view_filter_detail_edit_version_card_preview_ready",
        "version_result_type": "owner_note_version_compare_saved_view_filter_detail_edit_version_card_preview",
        "compare_allowed_in_preview": True,
        "rollback_allowed_in_preview": True,
        "restore_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    card.update(_base_flags())
    return card


def _build_edit_history_timeline(drawer: Dict[str, object], sequence: int) -> Dict[str, object]:
    drawer = dict(drawer or {})
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    source_kind = _safe_text(drawer.get("source_kind"))
    source_id = _safe_text(drawer.get("source_id"))

    rows = drawer.get("editable_field_rows", [])
    if not isinstance(rows, list):
        rows = []

    field_events = [
        _build_field_change_event(drawer, row, idx)
        for idx, row in enumerate(rows, start=1)
        if isinstance(row, dict)
    ]

    version_cards = [
        _build_version_card(drawer, version_number=1, field_events=field_events),
        _build_version_card(drawer, version_number=2, field_events=field_events),
        _build_version_card(drawer, version_number=3, field_events=field_events),
    ]

    changed_count = len([event for event in field_events if event.get("changed") is True])
    unchanged_count = len([event for event in field_events if event.get("changed") is False])

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": sequence,
    }

    timeline = {
        "edit_history_timeline_id": f"version_compare_saved_view_filter_detail_edit_history_timeline_{_stable_hash(identity, 18)}",
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": int(sequence),
        "timeline_status": "version_compare_saved_view_filter_detail_edit_history_timeline_preview_ready",
        "timeline_result_type": "owner_note_version_compare_saved_view_filter_detail_edit_history_timeline_preview",
        "version_cards": version_cards,
        "version_card_count": len(version_cards),
        "field_change_events": field_events,
        "field_change_event_count": len(field_events),
        "changed_field_count": changed_count,
        "unchanged_field_count": unchanged_count,
        "active_version_card_id": version_cards[1].get("version_card_id") if len(version_cards) > 1 else None,
        "original_version_card_id": version_cards[0].get("version_card_id") if version_cards else None,
        "compare_version_card_id": version_cards[2].get("version_card_id") if len(version_cards) > 2 else None,
        "rollback_preview": {
            "rollback_preview_id": f"version_compare_saved_view_filter_detail_edit_rollback_preview_{_stable_hash((drawer_id, source_id, 'rollback'), 18)}",
            "detail_edit_drawer_id": drawer_id,
            "source_kind": source_kind,
            "source_id": source_id,
            "rollback_target_version": 1,
            "rollback_allowed_in_preview": True,
            "rollback_allowed_now": False,
            "real_rollback_executed": False,
            "safe_preview_only": True,
        },
        "restore_preview": {
            "restore_preview_id": f"version_compare_saved_view_filter_detail_edit_restore_preview_{_stable_hash((drawer_id, source_id, 'restore'), 18)}",
            "detail_edit_drawer_id": drawer_id,
            "source_kind": source_kind,
            "source_id": source_id,
            "restore_target_version": 2,
            "restore_allowed_in_preview": True,
            "restore_allowed_now": False,
            "real_restore_executed": False,
            "safe_preview_only": True,
        },
        "compare_preview": {
            "compare_preview_id": f"version_compare_saved_view_filter_detail_edit_compare_preview_{_stable_hash((drawer_id, source_id, 'compare'), 18)}",
            "detail_edit_drawer_id": drawer_id,
            "source_kind": source_kind,
            "source_id": source_id,
            "compare_from_version": 1,
            "compare_to_version": 2,
            "compare_allowed_in_preview": True,
            "safe_preview_only": True,
        },
        "safe_preview_only": True,
    }
    timeline.update(_base_flags())
    return timeline


def _build_indexes(timelines: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "timelines_by_id": {},
        "timelines_by_drawer_id": {},
        "timelines_by_source_kind": {},
        "timelines_by_source_id": {},
        "version_cards_by_id": {},
        "version_cards_by_drawer_id": {},
        "field_change_events_by_id": {},
        "field_change_events_by_drawer_id": {},
        "field_change_events_by_source_kind": {},
        "changed_events_by_drawer_id": {},
    }

    for timeline in timelines:
        timeline_id = _safe_text(timeline.get("edit_history_timeline_id"))
        drawer_id = _safe_text(timeline.get("detail_edit_drawer_id"))
        source_kind = _safe_text(timeline.get("source_kind"))
        source_id = _safe_text(timeline.get("source_id"))

        indexes["timelines_by_id"][timeline_id] = timeline
        indexes["timelines_by_drawer_id"][drawer_id] = timeline
        indexes["timelines_by_source_kind"].setdefault(source_kind, []).append(timeline)
        indexes["timelines_by_source_id"][source_id] = timeline

        for card in timeline.get("version_cards", []):
            card_id = _safe_text(card.get("version_card_id"))
            indexes["version_cards_by_id"][card_id] = card
            indexes["version_cards_by_drawer_id"].setdefault(drawer_id, []).append(card)

        for event in timeline.get("field_change_events", []):
            event_id = _safe_text(event.get("field_change_event_id"))
            indexes["field_change_events_by_id"][event_id] = event
            indexes["field_change_events_by_drawer_id"].setdefault(drawer_id, []).append(event)
            indexes["field_change_events_by_source_kind"].setdefault(source_kind, []).append(event)
            if event.get("changed") is True:
                indexes["changed_events_by_drawer_id"].setdefault(drawer_id, []).append(event)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload_cached() -> Dict[str, object]:
    pack_185 = _load_pack_185_payload(force_refresh=False)

    saved_view_drawers = pack_185.get("saved_view_detail_edit_drawers", [])
    if not isinstance(saved_view_drawers, list):
        saved_view_drawers = []

    filter_preset_drawers = pack_185.get("filter_preset_detail_edit_drawers", [])
    if not isinstance(filter_preset_drawers, list):
        filter_preset_drawers = []

    all_drawers = [
        drawer for drawer in saved_view_drawers + filter_preset_drawers
        if isinstance(drawer, dict)
    ]

    timelines = [
        _build_edit_history_timeline(drawer, idx)
        for idx, drawer in enumerate(all_drawers, start=1)
    ]

    all_version_cards = []
    all_events = []
    for timeline in timelines:
        all_version_cards.extend(timeline.get("version_cards", []))
        all_events.extend(timeline.get("field_change_events", []))

    saved_view_timelines = [timeline for timeline in timelines if timeline.get("source_kind") == "saved_view_preset"]
    filter_preset_timelines = [timeline for timeline in timelines if timeline.get("source_kind") == "filter_preset"]

    changed_events = [event for event in all_events if event.get("changed") is True]
    unchanged_events = [event for event in all_events if event.get("changed") is False]

    indexes = _build_indexes(timelines)

    readiness_checks = {
        "pack_185_ready": pack_185.get("status") == "ready",
        "has_detail_edit_drawers": len(all_drawers) >= 15,
        "has_saved_view_timelines": len(saved_view_timelines) == 6,
        "has_filter_preset_timelines": len(filter_preset_timelines) >= 9,
        "timeline_count_matches_drawers": len(timelines) == len(all_drawers),
        "all_timelines_ready": all(timeline.get("timeline_status") == "version_compare_saved_view_filter_detail_edit_history_timeline_preview_ready" for timeline in timelines),
        "all_timelines_have_three_versions": all(int(timeline.get("version_card_count") or 0) == 3 for timeline in timelines),
        "all_timelines_have_five_events": all(int(timeline.get("field_change_event_count") or 0) == 5 for timeline in timelines),
        "has_version_cards": len(all_version_cards) >= 45,
        "has_field_change_events": len(all_events) >= 75,
        "has_changed_events": len(changed_events) >= 1,
        "has_unchanged_events": len(unchanged_events) >= 1,
        "all_version_cards_ready": all(card.get("version_status") == "version_compare_saved_view_filter_detail_edit_version_card_preview_ready" for card in all_version_cards),
        "all_field_change_events_ready": all(event.get("event_status") == "version_compare_saved_view_filter_detail_edit_field_change_event_preview_ready" for event in all_events),
        "timeline_indexes_present": bool(indexes.get("timelines_by_id")),
        "version_card_indexes_present": bool(indexes.get("version_cards_by_id")),
        "field_change_event_indexes_present": bool(indexes.get("field_change_events_by_id")),
        "changed_event_indexes_present": bool(indexes.get("changed_events_by_drawer_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in timelines + all_version_cards + all_events),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_rollback_preview_only": all(item.get("rollback_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_restore_preview_only": all(item.get("restore_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_detail_edit_preview_only": all(item.get("detail_edit_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in timelines + all_version_cards + all_events),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in timelines + all_version_cards + all_events),
        "no_real_history_written": all(item.get("real_history_written") is False for item in timelines + all_version_cards + all_events),
        "no_real_version_written": all(item.get("real_version_written") is False for item in timelines + all_version_cards + all_events),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in timelines + all_version_cards + all_events),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in timelines + all_version_cards + all_events),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in timelines + all_version_cards + all_events),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in timelines + all_version_cards + all_events),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in timelines + all_version_cards + all_events),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in timelines + all_version_cards + all_events),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in timelines + all_version_cards + all_events),
        "all_history_writes_blocked": all(item.get("history_write_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_version_writes_blocked": all(item.get("version_write_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_version_saves_blocked": all(item.get("version_save_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_rollback_actions_blocked": all(item.get("rollback_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_restore_actions_blocked": all(item.get("restore_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in timelines + all_version_cards + all_events),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in timelines + all_version_cards + all_events),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in timelines + all_version_cards + all_events),
        "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 186,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Saved View / Filter Preset Detail Edit History / Version Preview",
        "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_185": {
            "status": pack_185.get("status"),
            "readiness_score": pack_185.get("summary", {}).get("readiness_score"),
            "saved_view_detail_drawer_count": pack_185.get("summary", {}).get("saved_view_detail_drawer_count"),
            "filter_preset_detail_drawer_count": pack_185.get("summary", {}).get("filter_preset_detail_drawer_count"),
            "total_detail_drawer_count": pack_185.get("summary", {}).get("total_detail_drawer_count"),
            "total_editable_row_count": pack_185.get("summary", {}).get("total_editable_row_count"),
            "changed_field_count": pack_185.get("summary", {}).get("changed_field_count"),
        },
        "summary": {
            "edit_history_timeline_count": len(timelines),
            "saved_view_timeline_count": len(saved_view_timelines),
            "filter_preset_timeline_count": len(filter_preset_timelines),
            "version_card_count": len(all_version_cards),
            "field_change_event_count": len(all_events),
            "changed_field_event_count": len(changed_events),
            "unchanged_field_event_count": len(unchanged_events),
            "rollback_preview_count": len(timelines),
            "restore_preview_count": len(timelines),
            "compare_preview_count": len(timelines),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare saved view/filter preset detail edit history/version preview ready" if readiness_score == 100 else "Owner note version compare saved view/filter preset detail edit history/version preview needs review",
        },
        "readiness_checks": readiness_checks,
        "edit_history_timelines": timelines,
        "edit_history_version_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 186,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "edit_history_timeline_count": summary.get("edit_history_timeline_count"),
        "saved_view_timeline_count": summary.get("saved_view_timeline_count"),
        "filter_preset_timeline_count": summary.get("filter_preset_timeline_count"),
        "version_card_count": summary.get("version_card_count"),
        "field_change_event_count": summary.get("field_change_event_count"),
        "changed_field_event_count": summary.get("changed_field_event_count"),
        "unchanged_field_event_count": summary.get("unchanged_field_event_count"),
        "rollback_preview_count": summary.get("rollback_preview_count"),
        "restore_preview_count": summary.get("restore_preview_count"),
        "compare_preview_count": summary.get("compare_preview_count"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview",
        "label": "Owner Note Version Compare Saved View History",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Saved View / Filter Preset Detail Edit History / Version Preview",
        "href": EDIT_HISTORY_VERSION_ENDPOINT,
        "endpoint": EDIT_HISTORY_VERSION_ENDPOINT,
        "description": "Preview edit history timelines, version cards, field change events, and rollback/restore metadata for version compare saved view/filter preset detail edits.",
        "status": bridge.get("status"),
        "pack": "Pack 186",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview",
        "title": "Owner Note Version Compare Saved View History",
        "subtitle": "Preview edit history timelines, versions, field changes, compare, rollback, and restore metadata for saved view/filter preset detail edits.",
        "status": payload.get("status"),
        "href": EDIT_HISTORY_VERSION_ENDPOINT,
        "cards": [
            {"id": "history_readiness", "title": "History readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "timelines", "title": "Timelines", "value": summary.get("edit_history_timeline_count"), "label": "Edit history timelines"},
            {"id": "version_cards", "title": "Version cards", "value": summary.get("version_card_count"), "label": "Preview version cards"},
            {"id": "field_events", "title": "Field events", "value": summary.get("field_change_event_count"), "label": "Preview field change events"},
            {"id": "changed_events", "title": "Changed events", "value": summary.get("changed_field_event_count"), "label": "Preview changes"},
            {"id": "history_writes", "title": "History writes", "value": "Blocked" if checks.get("all_history_writes_blocked") and checks.get("all_version_writes_blocked") else "Review", "label": "No real history/version write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-saved-view-history-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-saved-view-history-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 186</p>
            <h2>{section.get('title', 'Owner Note Version Compare Saved View History')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{EDIT_HISTORY_VERSION_ENDPOINT}">Open version compare saved view/filter detail edit history JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "EDIT_HISTORY_VERSION_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_html_section",
]
