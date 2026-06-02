
"""
PACK 191 - Owner Note Saved View Preset Detail Edit History Version Compare
Navigation Saved View / Filter Preset Detail Edit History / Version Preview.

Short module filename:
    tower.owner_note_vc_nav_detail_history_v191

This module sits on top of Pack 190.

Pack 190 creates preview-only detail edit drawers and editable rows for
version compare navigation saved view/filter presets.

Pack 191 creates preview-only history/version scaffolding:
- edit history timelines
- version cards
- field change events
- rollback/restore/compare previews
- indexes
- blocked history/version/save/rollback/restore/edit persistence

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


PACK_ID = "PACK_191"
DETAIL_EDIT_HISTORY_VERSION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-history-version-preview.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json"


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
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
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


def _load_pack_190_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_190",
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
        "pack_id": "PACK_190",
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


def _display(value: Any) -> str:
    if isinstance(value, dict):
        if "display_value" in value:
            return _safe_text(value.get("display_value"))
        if "value" in value:
            return _safe_text(value.get("value"))
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None:
        return ""
    return _safe_text(value)


def _extract_value(value_payload: Any) -> Any:
    if isinstance(value_payload, dict) and "value" in value_payload:
        return value_payload.get("value")
    return value_payload


def _build_version_card(drawer: Dict[str, object], role: str, version_number: int) -> Dict[str, object]:
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    source_kind = _safe_text(drawer.get("source_kind"))
    source_id = _safe_text(drawer.get("source_id"))

    if role == "original":
        snapshot = drawer.get("original_snapshot", {})
        label = "Original detail edit snapshot"
    elif role == "draft_preview":
        snapshot = drawer.get("preview_edit_snapshot", {})
        label = "Draft detail edit preview"
    else:
        snapshot = {
            "changed_field_count": drawer.get("changed_field_count"),
            "unchanged_field_count": drawer.get("unchanged_field_count"),
            "editable_field_row_count": drawer.get("editable_field_row_count"),
        }
        label = "Compare preview summary"

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "role": role,
        "version_number": version_number,
    }

    card = {
        "version_card_id": f"version_compare_navigation_saved_view_filter_detail_edit_history_version_card_{_stable_hash(identity, 18)}",
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "version_number": int(version_number),
        "version_role": role,
        "version_label": label,
        "version_snapshot": snapshot if isinstance(snapshot, dict) else {},
        "version_status": "version_compare_navigation_saved_view_filter_detail_edit_history_version_card_preview_ready",
        "version_result_type": "owner_note_version_compare_navigation_saved_view_filter_detail_edit_history_version_card_preview",
        "compare_allowed_in_preview": True,
        "rollback_allowed_in_preview": True,
        "restore_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    card.update(_base_flags())
    return card


def _build_field_change_event(drawer: Dict[str, object], row: Dict[str, object], sequence: int) -> Dict[str, object]:
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    source_kind = _safe_text(drawer.get("source_kind"))
    source_id = _safe_text(drawer.get("source_id"))

    current_payload = row.get("current_value", {})
    preview_payload = row.get("preview_value", {})
    current_value = _extract_value(current_payload)
    preview_value = _extract_value(preview_payload)
    changed = bool(row.get("changed", current_value != preview_value))

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "row_id": row.get("editable_field_row_id"),
        "field_id": row.get("field_id"),
        "sequence": sequence,
    }

    event = {
        "field_change_event_id": f"version_compare_navigation_saved_view_filter_detail_edit_history_field_change_event_{_stable_hash(identity, 18)}",
        "detail_edit_drawer_id": drawer_id,
        "editable_field_row_id": row.get("editable_field_row_id"),
        "source_kind": source_kind,
        "source_id": source_id,
        "field_id": row.get("field_id"),
        "field_label": row.get("field_label"),
        "field_type": row.get("field_type"),
        "sequence": int(sequence),
        "current_value": current_value,
        "preview_value": preview_value,
        "current_display_value": _display(current_payload),
        "preview_display_value": _display(preview_payload),
        "changed": changed,
        "change_status": "changed_preview" if changed else "unchanged_preview",
        "event_status": "version_compare_navigation_saved_view_filter_detail_edit_history_field_change_event_preview_ready",
        "event_result_type": "owner_note_version_compare_navigation_saved_view_filter_detail_edit_history_field_change_event_preview",
        "safe_preview_only": True,
    }
    event.update(_base_flags())
    return event


def _build_edit_history_timeline(drawer: Dict[str, object], sequence: int) -> Dict[str, object]:
    drawer_id = _safe_text(drawer.get("detail_edit_drawer_id"))
    source_kind = _safe_text(drawer.get("source_kind"))
    source_id = _safe_text(drawer.get("source_id"))

    version_cards = [
        _build_version_card(drawer, "original", 1),
        _build_version_card(drawer, "draft_preview", 2),
        _build_version_card(drawer, "compare_preview", 3),
    ]

    rows = drawer.get("editable_field_rows", [])
    if not isinstance(rows, list):
        rows = []

    field_events = [
        _build_field_change_event(drawer, row, idx)
        for idx, row in enumerate(rows, start=1)
        if isinstance(row, dict)
    ]

    changed_events = [event for event in field_events if event.get("changed") is True]
    unchanged_events = [event for event in field_events if event.get("changed") is False]

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": sequence,
    }

    timeline_id = f"version_compare_navigation_saved_view_filter_detail_edit_history_timeline_{_stable_hash(identity, 18)}"

    timeline = {
        "edit_history_timeline_id": timeline_id,
        "detail_edit_drawer_id": drawer_id,
        "source_kind": source_kind,
        "source_id": source_id,
        "sequence": int(sequence),
        "timeline_status": "version_compare_navigation_saved_view_filter_detail_edit_history_timeline_preview_ready",
        "timeline_result_type": "owner_note_version_compare_navigation_saved_view_filter_detail_edit_history_timeline_preview",
        "version_cards": version_cards,
        "version_card_count": len(version_cards),
        "field_change_events": field_events,
        "field_change_event_count": len(field_events),
        "changed_field_count": len(changed_events),
        "unchanged_field_count": len(unchanged_events),
        "active_version_card_id": version_cards[1].get("version_card_id"),
        "original_version_card_id": version_cards[0].get("version_card_id"),
        "compare_version_card_id": version_cards[2].get("version_card_id"),
        "rollback_preview": {
            "rollback_preview_id": f"version_compare_navigation_saved_view_filter_detail_edit_history_rollback_{_stable_hash((timeline_id, 'rollback'), 18)}",
            "target_version_card_id": version_cards[0].get("version_card_id"),
            "rollback_allowed_in_preview": True,
            "rollback_allowed_now": False,
            "real_rollback_executed": False,
            "safe_preview_only": True,
        },
        "restore_preview": {
            "restore_preview_id": f"version_compare_navigation_saved_view_filter_detail_edit_history_restore_{_stable_hash((timeline_id, 'restore'), 18)}",
            "target_version_card_id": version_cards[1].get("version_card_id"),
            "restore_allowed_in_preview": True,
            "restore_allowed_now": False,
            "real_restore_executed": False,
            "safe_preview_only": True,
        },
        "compare_preview": {
            "compare_preview_id": f"version_compare_navigation_saved_view_filter_detail_edit_history_compare_{_stable_hash((timeline_id, 'compare'), 18)}",
            "left_version_card_id": version_cards[0].get("version_card_id"),
            "right_version_card_id": version_cards[1].get("version_card_id"),
            "compare_allowed_in_preview": True,
            "changed_field_count": len(changed_events),
            "unchanged_field_count": len(unchanged_events),
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
        "unchanged_events_by_drawer_id": {},
    }

    for timeline in timelines:
        timeline_id = timeline.get("edit_history_timeline_id")
        drawer_id = timeline.get("detail_edit_drawer_id")
        source_kind = timeline.get("source_kind")
        source_id = timeline.get("source_id")

        indexes["timelines_by_id"][timeline_id] = timeline
        indexes["timelines_by_drawer_id"][drawer_id] = timeline
        indexes["timelines_by_source_kind"].setdefault(source_kind, []).append(timeline)
        indexes["timelines_by_source_id"][source_id] = timeline

        for card in timeline.get("version_cards", []):
            if isinstance(card, dict):
                card_id = card.get("version_card_id")
                indexes["version_cards_by_id"][card_id] = card
                indexes["version_cards_by_drawer_id"].setdefault(drawer_id, []).append(card)

        for event in timeline.get("field_change_events", []):
            if not isinstance(event, dict):
                continue
            event_id = event.get("field_change_event_id")
            indexes["field_change_events_by_id"][event_id] = event
            indexes["field_change_events_by_drawer_id"].setdefault(drawer_id, []).append(event)
            indexes["field_change_events_by_source_kind"].setdefault(source_kind, []).append(event)
            if event.get("changed") is True:
                indexes["changed_events_by_drawer_id"].setdefault(drawer_id, []).append(event)
            else:
                indexes["unchanged_events_by_drawer_id"].setdefault(drawer_id, []).append(event)

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_detail_history_v191_payload_cached() -> Dict[str, object]:
    pack_190 = _load_pack_190_payload(force_refresh=False)

    saved_view_drawers = pack_190.get("saved_view_detail_edit_drawers", [])
    if not isinstance(saved_view_drawers, list):
        saved_view_drawers = []

    filter_preset_drawers = pack_190.get("filter_preset_detail_edit_drawers", [])
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
    all_field_events = []
    for timeline in timelines:
        all_version_cards.extend(timeline.get("version_cards", []))
        all_field_events.extend(timeline.get("field_change_events", []))

    saved_view_timelines = [timeline for timeline in timelines if timeline.get("source_kind") == "saved_view_preset"]
    filter_preset_timelines = [timeline for timeline in timelines if timeline.get("source_kind") == "filter_preset"]
    changed_events = [event for event in all_field_events if isinstance(event, dict) and event.get("changed") is True]
    unchanged_events = [event for event in all_field_events if isinstance(event, dict) and event.get("changed") is False]

    indexes = _build_indexes(timelines)

    readiness_checks = {
        "pack_190_ready": pack_190.get("status") == "ready",
        "has_detail_edit_drawers": len(all_drawers) >= 15,
        "has_saved_view_timelines": len(saved_view_timelines) == 6,
        "has_filter_preset_timelines": len(filter_preset_timelines) >= 9,
        "timeline_count_matches_drawers": len(timelines) == len(all_drawers),
        "all_timelines_ready": all(timeline.get("timeline_status") == "version_compare_navigation_saved_view_filter_detail_edit_history_timeline_preview_ready" for timeline in timelines),
        "all_timelines_have_three_versions": all(int(timeline.get("version_card_count") or 0) == 3 for timeline in timelines),
        "all_timelines_have_five_events": all(int(timeline.get("field_change_event_count") or 0) == 5 for timeline in timelines),
        "has_version_cards": len(all_version_cards) >= 45,
        "has_field_change_events": len(all_field_events) >= 75,
        "has_changed_events": len(changed_events) >= 1,
        "has_unchanged_events": len(unchanged_events) >= 1,
        "all_version_cards_ready": all(card.get("version_status") == "version_compare_navigation_saved_view_filter_detail_edit_history_version_card_preview_ready" for card in all_version_cards if isinstance(card, dict)),
        "all_field_change_events_ready": all(event.get("event_status") == "version_compare_navigation_saved_view_filter_detail_edit_history_field_change_event_preview_ready" for event in all_field_events if isinstance(event, dict)),
        "timeline_indexes_present": bool(indexes.get("timelines_by_id")),
        "version_card_indexes_present": bool(indexes.get("version_cards_by_id")),
        "field_change_event_indexes_present": bool(indexes.get("field_change_events_by_id")),
        "changed_event_indexes_present": bool(indexes.get("changed_events_by_drawer_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_rollback_preview_only": all(item.get("rollback_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_restore_preview_only": all(item.get("restore_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_detail_edit_preview_only": all(item.get("detail_edit_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in timelines + all_version_cards + all_field_events),
        "no_real_history_written": all(item.get("real_history_written") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_version_written": all(item.get("real_version_written") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in timelines + all_version_cards + all_field_events),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in timelines + all_version_cards + all_field_events),
        "all_history_writes_blocked": all(item.get("history_write_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_version_writes_blocked": all(item.get("version_write_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_version_saves_blocked": all(item.get("version_save_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_rollback_actions_blocked": all(item.get("rollback_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_restore_actions_blocked": all(item.get("restore_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in timelines + all_version_cards + all_field_events),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in timelines + all_version_cards + all_field_events),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in timelines + all_version_cards + all_field_events),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 191,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Detail Edit History / Version Preview",
        "endpoint": DETAIL_EDIT_HISTORY_VERSION_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_190": {
            "status": pack_190.get("status"),
            "readiness_score": pack_190.get("summary", {}).get("readiness_score"),
            "saved_view_detail_drawer_count": pack_190.get("summary", {}).get("saved_view_detail_drawer_count"),
            "filter_preset_detail_drawer_count": pack_190.get("summary", {}).get("filter_preset_detail_drawer_count"),
            "total_detail_drawer_count": pack_190.get("summary", {}).get("total_detail_drawer_count"),
            "total_editable_row_count": pack_190.get("summary", {}).get("total_editable_row_count"),
        },
        "summary": {
            "edit_history_timeline_count": len(timelines),
            "saved_view_timeline_count": len(saved_view_timelines),
            "filter_preset_timeline_count": len(filter_preset_timelines),
            "version_card_count": len(all_version_cards),
            "field_change_event_count": len(all_field_events),
            "changed_field_event_count": len(changed_events),
            "unchanged_field_event_count": len(unchanged_events),
            "rollback_preview_count": len(timelines),
            "restore_preview_count": len(timelines),
            "compare_preview_count": len(timelines),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation saved view/filter preset detail edit history/version preview ready" if readiness_score == 100 else "Owner note version compare navigation saved view/filter preset detail edit history/version preview needs review",
        },
        "readiness_checks": readiness_checks,
        "edit_history_timelines": timelines,
        "edit_history_version_indexes": indexes,
    }


def build_owner_note_vc_nav_detail_history_v191_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_detail_history_v191_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_detail_history_v191_payload_cached())


def get_owner_note_vc_nav_detail_history_v191_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_detail_history_v191_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_detail_history_v191_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_detail_history_v191_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 191,
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


def get_owner_note_vc_nav_detail_history_v191_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_detail_history_v191_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_detail_history_v191_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_detail_history_v191_status_bridge()

    action = {
        "id": "owner_note_vc_nav_detail_history_v191",
        "label": "Owner Note Version Compare Saved View History",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Detail Edit History / Version Preview",
        "href": DETAIL_EDIT_HISTORY_VERSION_ENDPOINT,
        "endpoint": DETAIL_EDIT_HISTORY_VERSION_ENDPOINT,
        "description": "Preview edit history timelines, version cards, field change events, and rollback/restore metadata for navigation saved view/filter preset detail edits.",
        "status": bridge.get("status"),
        "pack": "Pack 191",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_detail_history_v191_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_detail_history_v191_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_detail_history_v191",
        "title": "Owner Note Version Compare Saved View History",
        "subtitle": "Preview edit history timelines and version cards for version compare navigation saved view/filter preset detail edits.",
        "status": payload.get("status"),
        "href": DETAIL_EDIT_HISTORY_VERSION_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "History readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "timelines", "title": "Timelines", "value": summary.get("edit_history_timeline_count"), "label": "Edit history timelines"},
            {"id": "version_cards", "title": "Version cards", "value": summary.get("version_card_count"), "label": "Preview version cards"},
            {"id": "field_events", "title": "Field events", "value": summary.get("field_change_event_count"), "label": "Field change events"},
            {"id": "changed_events", "title": "Changed events", "value": summary.get("changed_field_event_count"), "label": "Changed field events"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_history_writes_blocked") and checks.get("all_version_writes_blocked") else "Review", "label": "No real history/version write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_detail_history_v191_html_section() -> str:
    section = build_owner_note_vc_nav_detail_history_v191_unified_owner_section()
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
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-saved-view-history-section" id="owner-note-vc-nav-detail-history-v191">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 191</p>
            <h2>{section.get('title', 'Owner Note Version Compare Saved View History')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{DETAIL_EDIT_HISTORY_VERSION_ENDPOINT}">Open version compare saved view/filter preset detail edit history JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "DETAIL_EDIT_HISTORY_VERSION_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_detail_history_v191_payload",
    "get_owner_note_vc_nav_detail_history_v191_payload",
    "build_owner_note_vc_nav_detail_history_v191_status_bridge",
    "get_owner_note_vc_nav_detail_history_v191_status_bridge",
    "build_owner_note_vc_nav_detail_history_v191_quick_action",
    "build_owner_note_vc_nav_detail_history_v191_unified_owner_section",
    "build_owner_note_vc_nav_detail_history_v191_html_section",
]
