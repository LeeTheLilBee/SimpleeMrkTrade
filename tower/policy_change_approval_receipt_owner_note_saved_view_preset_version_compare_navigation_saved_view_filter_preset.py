
"""
PACK 179 - Owner Note Saved View Preset Version Compare Navigation Saved View / Filter Preset Preview.

This module sits on top of Pack 178.

Pack 178 creates preview-only saved view preset version compare navigation/filter scaffolding.
Pack 179 creates preview-only saved view/filter preset scaffolding for that navigation layer:
- saved view presets
- filter presets
- selected saved view preview
- saved view/filter preset indexes
- blocked saved-view/filter/user preference/navigation persistence

Important:
- simulated-only
- saved-view-preview-only
- filter-preset-preview-only
- navigation-preview-only
- filter-navigation-preview-only
- version-detail-preview-only
- compare-view-preview-only
- no real saved view written
- no real user preference written
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
- no real history/version writes
- no real rollback/restore
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


PACK_ID = "PACK_179"
SAVED_VIEW_FILTER_PRESET_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json"
VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json"


SAVED_VIEW_PRESET_DEFS = [
    {
        "saved_view_preset_id": "default_all_compare_navigation",
        "label": "All Compare Navigation",
        "description": "Default saved view for all saved view preset version compare navigation items.",
        "filter_lane_id": "all_compare_drawers",
        "view_priority": "standard",
        "is_default": True,
        "sort_order": 1,
    },
    {
        "saved_view_preset_id": "default_saved_view_focus",
        "label": "Default Saved View Focus",
        "description": "Focus only on the default saved view preset compare drawer.",
        "filter_lane_id": "default_saved_view",
        "view_priority": "standard",
        "is_default": False,
        "sort_order": 2,
    },
    {
        "saved_view_preset_id": "critical_priority_focus",
        "label": "Critical Priority Focus",
        "description": "Focus saved view preset compare navigation on critical priority drawers.",
        "filter_lane_id": "critical_priority",
        "view_priority": "critical",
        "is_default": False,
        "sort_order": 3,
    },
    {
        "saved_view_preset_id": "high_priority_focus",
        "label": "High Priority Focus",
        "description": "Focus saved view preset compare navigation on high priority drawers.",
        "filter_lane_id": "high_priority",
        "view_priority": "high",
        "is_default": False,
        "sort_order": 4,
    },
    {
        "saved_view_preset_id": "changed_fields_focus",
        "label": "Changed Fields Focus",
        "description": "Focus saved view preset compare navigation on drawers with changed fields.",
        "filter_lane_id": "changed_fields_present",
        "view_priority": "medium",
        "is_default": False,
        "sort_order": 5,
    },
    {
        "saved_view_preset_id": "safe_preview_focus",
        "label": "Safe Preview Focus",
        "description": "Focus on drawers that remain safe preview-only with persistence blocked.",
        "filter_lane_id": "safe_preview_only",
        "view_priority": "monitor",
        "is_default": False,
        "sort_order": 6,
    },
]


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


def _base_flags() -> Dict[str, Any]:
    return {
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
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


def _load_pack_178_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_178",
            "status": "review",
            "endpoint": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
            "summary": {
                "navigation_item_count": 0,
                "filter_lane_count": 0,
                "quick_filter_chip_count": 0,
                "readiness_score": 0,
            },
            "navigation_preview": {"navigation_items": []},
            "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
            "quick_filter_chips_preview": {"quick_filter_chips": []},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_178",
        "status": "review",
        "endpoint": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "summary": {
            "navigation_item_count": 0,
            "filter_lane_count": 0,
            "quick_filter_chip_count": 0,
            "readiness_score": 0,
        },
        "navigation_preview": {"navigation_items": []},
        "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
        "quick_filter_chips_preview": {"quick_filter_chips": []},
        **_base_flags(),
    }


def _priority_rank(priority: Any) -> int:
    return {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }.get(_safe_text(priority), 99)


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_filter_preset_from_lane(lane: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    lane = dict(lane or {})
    identity = {
        "pack": PACK_ID,
        "lane": lane.get("filter_lane_id"),
        "sequence": sequence,
    }

    preset = {
        "filter_preset_id": f"saved_view_preset_version_compare_filter_preset_{_stable_hash(identity, 18)}",
        "source_filter_lane_preview_id": _safe_text(lane.get("filter_lane_preview_id")),
        "filter_lane_id": _safe_text(lane.get("filter_lane_id")),
        "label": _safe_text(lane.get("label")),
        "description": _safe_text(lane.get("description")),
        "filter_type": _safe_text(lane.get("filter_type")),
        "sequence": int(sequence),
        "matched_drawer_count": int(lane.get("matched_drawer_count") or 0),
        "matched_version_detail_drawer_ids": lane.get("matched_version_detail_drawer_ids", []),
        "matched_saved_view_preset_ids": lane.get("matched_saved_view_preset_ids", []),
        "default_selected_version_detail_drawer_id": lane.get("default_selected_version_detail_drawer_id"),
        "default_selected_saved_view_preset_id": lane.get("default_selected_saved_view_preset_id"),
        "filter_preset_status": "saved_view_preset_version_compare_filter_preset_preview_ready",
        "filter_preset_result_type": "owner_note_saved_view_preset_version_compare_filter_preset_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_saved_view_preset(
    preset_def: Dict[str, Any],
    sequence: int,
    filter_preset_index: Dict[str, Dict[str, Any]],
    navigation_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    lane_id = _safe_text(preset_def.get("filter_lane_id"))
    filter_preset = filter_preset_index.get(lane_id, {})

    matched_ids = set(filter_preset.get("matched_saved_view_preset_ids", []))
    matched_items = [
        item for item in navigation_items
        if item.get("saved_view_preset_id") in matched_ids
    ]

    if lane_id == "all_compare_drawers":
        matched_items = navigation_items

    default_item = matched_items[0] if matched_items else (navigation_items[0] if navigation_items else {})

    identity = {
        "pack": PACK_ID,
        "preset": preset_def.get("saved_view_preset_id"),
        "sequence": sequence,
        "lane": lane_id,
    }

    preset = {
        "saved_view_preset_preview_id": f"saved_view_preset_version_compare_saved_view_preset_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(preset_def.get("saved_view_preset_id")),
        "label": _safe_text(preset_def.get("label")),
        "description": _safe_text(preset_def.get("description")),
        "filter_lane_id": lane_id,
        "linked_filter_preset_id": filter_preset.get("filter_preset_id"),
        "view_priority": _safe_text(preset_def.get("view_priority")),
        "is_default": bool(preset_def.get("is_default", False)),
        "sort_order": int(preset_def.get("sort_order") or sequence),
        "sequence": int(sequence),
        "matched_navigation_item_count": len(matched_items),
        "matched_navigation_item_ids": [item.get("navigation_item_id") for item in matched_items],
        "matched_version_detail_drawer_ids": [item.get("version_detail_drawer_id") for item in matched_items],
        "matched_source_saved_view_preset_ids": [item.get("saved_view_preset_id") for item in matched_items],
        "default_selected_navigation_item_id": default_item.get("navigation_item_id"),
        "default_selected_version_detail_drawer_id": default_item.get("version_detail_drawer_id"),
        "default_selected_source_saved_view_preset_id": default_item.get("saved_view_preset_id"),
        "comparison_row_count": sum(int(item.get("comparison_row_count") or 0) for item in matched_items),
        "changed_field_count": sum(int(item.get("changed_field_count") or 0) for item in matched_items),
        "unchanged_field_count": sum(int(item.get("unchanged_field_count") or 0) for item in matched_items),
        "saved_view_preset_status": "saved_view_preset_version_compare_saved_view_preset_preview_ready",
        "saved_view_preset_result_type": "owner_note_saved_view_preset_version_compare_saved_view_preset_preview",
        "view_allowed_in_preview": True,
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_selected_saved_view_preview(saved_view_presets: List[Dict[str, Any]]) -> Dict[str, Any]:
    selected = None
    for preset in saved_view_presets:
        if preset.get("is_default") is True:
            selected = preset
            break

    if selected is None and saved_view_presets:
        selected = saved_view_presets[0]

    selected = selected or {}

    payload = {
        "selected_saved_view_preview_id": f"saved_view_preset_version_compare_selected_saved_view_{_stable_hash(selected.get('saved_view_preset_id'), 18)}",
        "selected_saved_view_preset_preview_id": selected.get("saved_view_preset_preview_id"),
        "selected_saved_view_preset_id": selected.get("saved_view_preset_id"),
        "selected_label": selected.get("label"),
        "selected_filter_lane_id": selected.get("filter_lane_id"),
        "selected_linked_filter_preset_id": selected.get("linked_filter_preset_id"),
        "selected_navigation_item_count": selected.get("matched_navigation_item_count", 0),
        "selected_comparison_row_count": selected.get("comparison_row_count", 0),
        "selected_changed_field_count": selected.get("changed_field_count", 0),
        "selected_default_navigation_item_id": selected.get("default_selected_navigation_item_id"),
        "selected_default_version_detail_drawer_id": selected.get("default_selected_version_detail_drawer_id"),
        "selection_status": "saved_view_preset_version_compare_selected_saved_view_preview_ready",
        "selection_result_type": "owner_note_saved_view_preset_version_compare_selected_saved_view_preview",
        "view_allowed_in_preview": True,
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    payload.update(_base_flags())
    return payload


def _build_indexes(saved_view_presets: List[Dict[str, Any]], filter_presets: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "saved_views_by_preview_id": {},
        "saved_views_by_id": {},
        "saved_views_by_filter_lane_id": {},
        "saved_views_by_priority": {},
        "saved_views_by_default_state": {},
        "filter_presets_by_id": {},
        "filter_presets_by_lane_id": {},
        "filter_presets_by_filter_type": {},
    }

    for preset in saved_view_presets:
        preview_id = _safe_text(preset.get("saved_view_preset_preview_id"))
        preset_id = _safe_text(preset.get("saved_view_preset_id"))
        lane_id = _safe_text(preset.get("filter_lane_id"))
        priority = _safe_text(preset.get("view_priority"))
        default_key = "default" if preset.get("is_default") else "not_default"

        if preview_id:
            indexes["saved_views_by_preview_id"][preview_id] = preset
        if preset_id:
            indexes["saved_views_by_id"][preset_id] = preset
        indexes["saved_views_by_filter_lane_id"].setdefault(lane_id, []).append(preset)
        indexes["saved_views_by_priority"].setdefault(priority, []).append(preset)
        indexes["saved_views_by_default_state"].setdefault(default_key, []).append(preset)

    for preset in filter_presets:
        preset_id = _safe_text(preset.get("filter_preset_id"))
        lane_id = _safe_text(preset.get("filter_lane_id"))
        filter_type = _safe_text(preset.get("filter_type"))

        if preset_id:
            indexes["filter_presets_by_id"][preset_id] = preset
        indexes["filter_presets_by_lane_id"][lane_id] = preset
        indexes["filter_presets_by_filter_type"].setdefault(filter_type, []).append(preset)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload_cached() -> Dict[str, Any]:
    pack_178 = _load_pack_178_payload(force_refresh=False)
    navigation_preview = pack_178.get("navigation_preview", {})
    filter_lanes_preview = pack_178.get("filter_lanes_preview", {})

    navigation_items = navigation_preview.get("navigation_items", [])
    if not isinstance(navigation_items, list):
        navigation_items = []

    filter_lanes = filter_lanes_preview.get("filter_lanes", [])
    if not isinstance(filter_lanes, list):
        filter_lanes = []

    filter_presets = [
        _build_filter_preset_from_lane(lane, sequence=idx)
        for idx, lane in enumerate(filter_lanes, start=1)
        if isinstance(lane, dict)
    ]

    filter_preset_index = {
        preset.get("filter_lane_id"): preset
        for preset in filter_presets
        if preset.get("filter_lane_id")
    }

    saved_view_presets = [
        _build_saved_view_preset(preset_def, idx, filter_preset_index, navigation_items)
        for idx, preset_def in enumerate(SAVED_VIEW_PRESET_DEFS, start=1)
    ]

    selected_saved_view_preview = _build_selected_saved_view_preview(saved_view_presets)
    indexes = _build_indexes(saved_view_presets, filter_presets)

    total_matched_navigation_items = sum(int(preset.get("matched_navigation_item_count") or 0) for preset in saved_view_presets)
    total_comparison_rows = sum(int(preset.get("comparison_row_count") or 0) for preset in saved_view_presets)
    total_changed_fields = sum(int(preset.get("changed_field_count") or 0) for preset in saved_view_presets)
    total_unchanged_fields = sum(int(preset.get("unchanged_field_count") or 0) for preset in saved_view_presets)

    saved_view_status_counts = _count_by(saved_view_presets, "saved_view_preset_status")
    filter_preset_status_counts = _count_by(filter_presets, "filter_preset_status")
    view_priority_counts = _count_by(saved_view_presets, "view_priority")
    filter_lane_counts = _count_by(saved_view_presets, "filter_lane_id")
    default_state_counts = {
        "default": len([preset for preset in saved_view_presets if preset.get("is_default") is True]),
        "not_default": len([preset for preset in saved_view_presets if preset.get("is_default") is False]),
    }

    expected_saved_view_ids = {item.get("saved_view_preset_id") for item in SAVED_VIEW_PRESET_DEFS}
    actual_saved_view_ids = {item.get("saved_view_preset_id") for item in saved_view_presets}
    expected_filter_lane_ids = {
        "all_compare_drawers",
        "default_saved_view",
        "not_default_saved_views",
        "critical_priority",
        "high_priority",
        "standard_priority",
        "monitor_priority",
        "changed_fields_present",
        "safe_preview_only",
    }
    actual_filter_lane_ids = {item.get("filter_lane_id") for item in filter_presets}

    readiness_checks = {
        "pack_178_ready": pack_178.get("status") == "ready",
        "has_navigation_items": len(navigation_items) >= 1,
        "has_filter_lanes": len(filter_lanes) >= 9,
        "has_saved_view_presets": len(saved_view_presets) >= 6,
        "has_filter_presets": len(filter_presets) >= 9,
        "saved_view_preset_count_is_six": len(saved_view_presets) == 6,
        "filter_preset_count_is_nine": len(filter_presets) >= 9,
        "selected_saved_view_preview_ready": selected_saved_view_preview.get("selection_status") == "saved_view_preset_version_compare_selected_saved_view_preview_ready",
        "default_saved_view_present": "default_all_compare_navigation" in actual_saved_view_ids,
        "all_expected_saved_view_presets_present": expected_saved_view_ids.issubset(actual_saved_view_ids),
        "all_expected_filter_presets_present": expected_filter_lane_ids.issubset(actual_filter_lane_ids),
        "all_saved_view_presets_ready": all(preset.get("saved_view_preset_status") == "saved_view_preset_version_compare_saved_view_preset_preview_ready" for preset in saved_view_presets),
        "all_filter_presets_ready": all(preset.get("filter_preset_status") == "saved_view_preset_version_compare_filter_preset_preview_ready" for preset in filter_presets),
        "all_saved_view_presets_simulated_only": all(preset.get("simulated_only") is True for preset in saved_view_presets),
        "all_filter_presets_simulated_only": all(preset.get("simulated_only") is True for preset in filter_presets),
        "all_saved_view_preview_only": all(preset.get("saved_view_preview_only") is True for preset in saved_view_presets),
        "all_filter_preset_preview_only": all(preset.get("filter_preset_preview_only") is True for preset in filter_presets),
        "all_navigation_preview_only": all(preset.get("navigation_preview_only") is True for preset in saved_view_presets + filter_presets),
        "all_filter_navigation_preview_only": all(preset.get("filter_navigation_preview_only") is True for preset in saved_view_presets + filter_presets),
        "all_version_detail_preview_only": all(preset.get("version_detail_preview_only") is True for preset in saved_view_presets + filter_presets),
        "all_compare_view_preview_only": all(preset.get("compare_view_preview_only") is True for preset in saved_view_presets + filter_presets),
        "no_real_saved_view_written": all(preset.get("real_saved_view_written") is False for preset in saved_view_presets + filter_presets),
        "no_real_user_preference_written": all(preset.get("real_user_preference_written") is False for preset in saved_view_presets + filter_presets),
        "no_real_filter_preference_saved": all(preset.get("real_filter_preference_saved") is False for preset in saved_view_presets + filter_presets),
        "no_real_navigation_state_persisted": all(preset.get("real_navigation_state_persisted") is False for preset in saved_view_presets + filter_presets),
        "no_real_drawer_selection_saved": all(preset.get("real_drawer_selection_saved") is False for preset in saved_view_presets + filter_presets),
        "no_real_history_written": all(preset.get("real_history_written") is False for preset in saved_view_presets + filter_presets),
        "no_real_version_written": all(preset.get("real_version_written") is False for preset in saved_view_presets + filter_presets),
        "no_real_version_saved": all(preset.get("real_version_saved") is False for preset in saved_view_presets + filter_presets),
        "no_real_rollback_executed": all(preset.get("real_rollback_executed") is False for preset in saved_view_presets + filter_presets),
        "no_real_restore_executed": all(preset.get("real_restore_executed") is False for preset in saved_view_presets + filter_presets),
        "no_real_edit_persisted": all(preset.get("real_edit_persisted") is False for preset in saved_view_presets + filter_presets),
        "all_saved_view_writes_blocked": all(preset.get("saved_view_write_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_user_preference_writes_blocked": all(preset.get("user_preference_write_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_filter_preference_saves_blocked": all(preset.get("filter_preference_save_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_navigation_persistence_blocked": all(preset.get("navigation_persistence_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_drawer_selection_saves_blocked": all(preset.get("drawer_selection_save_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_restore_actions_blocked": all(preset.get("restore_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_rollback_actions_blocked": all(preset.get("rollback_allowed_now") is False for preset in saved_view_presets + filter_presets),
        "all_raw_evidence_reveal_blocked": all(preset.get("raw_evidence_reveal_allowed") is False for preset in saved_view_presets + filter_presets),
        "all_raw_evidence_lookup_blocked": all(preset.get("raw_evidence_lookup_allowed") is False for preset in saved_view_presets + filter_presets),
        "saved_view_indexes_present": bool(indexes.get("saved_views_by_id")),
        "filter_preset_indexes_present": bool(indexes.get("filter_presets_by_lane_id")),
        "default_all_compare_navigation_indexed": "default_all_compare_navigation" in indexes.get("saved_views_by_id", {}),
        "all_compare_drawers_filter_preset_indexed": "all_compare_drawers" in indexes.get("filter_presets_by_lane_id", {}),
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    payload = {
        "pack_id": PACK_ID,
        "pack_number": 179,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Version Compare Navigation Saved View / Filter Preset Preview",
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "source_endpoint": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_178": {
            "status": pack_178.get("status"),
            "readiness_score": pack_178.get("summary", {}).get("readiness_score"),
            "navigation_item_count": pack_178.get("summary", {}).get("navigation_item_count"),
            "filter_lane_count": pack_178.get("summary", {}).get("filter_lane_count"),
            "quick_filter_chip_count": pack_178.get("summary", {}).get("quick_filter_chip_count"),
            "group_count": pack_178.get("summary", {}).get("group_count"),
            "comparison_row_count": pack_178.get("summary", {}).get("comparison_row_count"),
        },
        "summary": {
            "saved_view_preset_count": len(saved_view_presets),
            "filter_preset_count": len(filter_presets),
            "source_navigation_item_count": len(navigation_items),
            "source_filter_lane_count": len(filter_lanes),
            "matched_navigation_item_total": total_matched_navigation_items,
            "comparison_row_count": total_comparison_rows,
            "changed_field_count": total_changed_fields,
            "unchanged_field_count": total_unchanged_fields,
            "saved_view_status_counts": saved_view_status_counts,
            "filter_preset_status_counts": filter_preset_status_counts,
            "view_priority_counts": view_priority_counts,
            "filter_lane_counts": filter_lane_counts,
            "default_state_counts": default_state_counts,
            "default_saved_view_preset_id": selected_saved_view_preview.get("selected_saved_view_preset_id"),
            "default_selected_version_detail_drawer_id": selected_saved_view_preview.get("selected_default_version_detail_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note saved view preset version compare navigation saved view/filter preset preview ready" if readiness_score == 100 else "Owner note saved view preset version compare navigation saved view/filter preset preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_preset_definitions": SAVED_VIEW_PRESET_DEFS,
        "saved_view_presets": saved_view_presets,
        "filter_presets": filter_presets,
        "selected_saved_view_preview": selected_saved_view_preview,
        "saved_view_filter_preset_indexes": indexes,
    }

    return payload


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 179,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "saved_view_preset_count": summary.get("saved_view_preset_count"),
        "filter_preset_count": summary.get("filter_preset_count"),
        "source_navigation_item_count": summary.get("source_navigation_item_count"),
        "source_filter_lane_count": summary.get("source_filter_lane_count"),
        "matched_navigation_item_total": summary.get("matched_navigation_item_total"),
        "comparison_row_count": summary.get("comparison_row_count"),
        "changed_field_count": summary.get("changed_field_count"),
        "unchanged_field_count": summary.get("unchanged_field_count"),
        "default_saved_view_preset_id": summary.get("default_saved_view_preset_id"),
        "default_selected_version_detail_drawer_id": summary.get("default_selected_version_detail_drawer_id"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset",
        "label": "Owner Note Preset Compare Saved Views",
        "title": "Owner Note Saved View Preset Version Compare Navigation Saved View / Filter Preset Preview",
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "description": "Preview saved view presets and filter presets for saved view preset version compare navigation, with persistence blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 179",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset",
        "title": "Owner Note Preset Compare Saved Views",
        "subtitle": "Preview saved view presets and filter presets for saved view preset version compare navigation, with all writes blocked.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cards": [
            {
                "id": "saved_view_filter_readiness",
                "title": "Saved view readiness",
                "value": summary.get("readiness_score"),
                "label": summary.get("readiness_label"),
            },
            {
                "id": "saved_view_presets",
                "title": "Saved view presets",
                "value": summary.get("saved_view_preset_count"),
                "label": "Preview saved views",
            },
            {
                "id": "filter_presets",
                "title": "Filter presets",
                "value": summary.get("filter_preset_count"),
                "label": "Preview filter presets",
            },
            {
                "id": "source_navigation_items",
                "title": "Source navigation",
                "value": summary.get("source_navigation_item_count"),
                "label": "Pack 178 navigation items",
            },
            {
                "id": "default_saved_view",
                "title": "Default saved view",
                "value": summary.get("default_saved_view_preset_id"),
                "label": "Selected preset",
            },
            {
                "id": "persistence",
                "title": "Persistence",
                "value": "Blocked" if checks.get("all_saved_view_writes_blocked") and checks.get("all_filter_preference_saves_blocked") else "Review",
                "label": "No real saved view/filter write",
            },
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-preset-saved-view-filter-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-preset-saved-view-filter-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 179</p>
            <h2>{section.get('title', 'Owner Note Preset Compare Saved Views')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SAVED_VIEW_FILTER_PRESET_ENDPOINT}">Open owner note preset compare saved views JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_FILTER_PRESET_ENDPOINT",
    "VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT",
    "SAVED_VIEW_PRESET_DEFS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_html_section",
]
