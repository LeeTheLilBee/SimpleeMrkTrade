
"""
PACK 184 - Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview.

This module sits on top of Pack 183.

Pack 183 creates preview-only navigation/filter scaffolding for version compare drawers.
Pack 184 creates preview-only saved view/filter preset scaffolding for that navigation layer:
- saved view presets
- filter presets
- selected saved view preview
- saved view/filter preset indexes
- blocked saved view/filter/user preference/navigation persistence

Important:
- simulated-only
- saved-view-preview-only
- filter-preset-preview-only
- navigation-preview-only
- filter-navigation-preview-only
- version-detail-preview-only
- compare-view-preview-only
- edit-history-preview-only
- version-preview-only
- no real saved view written
- no real user preference written
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
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


PACK_ID = "PACK_184"
SAVED_VIEW_FILTER_PRESET_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"


SAVED_VIEW_PRESET_DEFS = [
    {
        "saved_view_preset_id": "default_all_version_compare_navigation",
        "label": "All Version Compare Navigation",
        "description": "Default saved view for all owner note saved view preset version compare navigation drawers.",
        "filter_lane_id": "all_compare_drawers",
        "view_priority": "standard",
        "is_default": True,
        "sort_order": 1,
    },
    {
        "saved_view_preset_id": "saved_view_preset_focus",
        "label": "Saved View Preset Focus",
        "description": "Focus on saved view preset compare drawers.",
        "filter_lane_id": "saved_view_preset_drawers",
        "view_priority": "high",
        "is_default": False,
        "sort_order": 2,
    },
    {
        "saved_view_preset_id": "filter_preset_focus",
        "label": "Filter Preset Focus",
        "description": "Focus on filter preset compare drawers.",
        "filter_lane_id": "filter_preset_drawers",
        "view_priority": "high",
        "is_default": False,
        "sort_order": 3,
    },
    {
        "saved_view_preset_id": "changed_fields_focus",
        "label": "Changed Fields Focus",
        "description": "Focus on drawers that contain changed compare rows.",
        "filter_lane_id": "changed_fields_present",
        "view_priority": "medium",
        "is_default": False,
        "sort_order": 4,
    },
    {
        "saved_view_preset_id": "blocked_actions_focus",
        "label": "Blocked Actions Focus",
        "description": "Focus on drawers where rollback, restore, and save remain blocked.",
        "filter_lane_id": "rollback_blocked",
        "view_priority": "critical",
        "is_default": False,
        "sort_order": 5,
    },
    {
        "saved_view_preset_id": "safe_preview_focus",
        "label": "Safe Preview Focus",
        "description": "Focus on safe preview-only drawers with no persistence allowed.",
        "filter_lane_id": "safe_preview_only",
        "view_priority": "monitor",
        "is_default": False,
        "sort_order": 6,
    },
]


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    return hashlib.sha256(repr(value).encode("utf-8", errors="ignore")).hexdigest()[:length]


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
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "edit_history_preview_only": True,
        "version_preview_only": True,
        "rollback_preview_only": True,
        "restore_preview_only": True,
        "compare_preview_only": True,
        "detail_edit_preview_only": True,
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


def _load_pack_183_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_183",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
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
        "pack_id": "PACK_183",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
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


def _count_by(items: List[Dict[str, object]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_filter_preset_from_lane(lane: Dict[str, object], sequence: int) -> Dict[str, object]:
    lane = dict(lane or {})
    identity = {
        "pack": PACK_ID,
        "lane_id": lane.get("filter_lane_id"),
        "sequence": sequence,
    }

    preset = {
        "filter_preset_id": f"version_compare_navigation_filter_preset_{_stable_hash(identity, 18)}",
        "source_filter_lane_preview_id": _safe_text(lane.get("filter_lane_preview_id")),
        "filter_lane_id": _safe_text(lane.get("filter_lane_id")),
        "label": _safe_text(lane.get("label")),
        "filter_type": _safe_text(lane.get("filter_type")),
        "sequence": int(sequence),
        "matched_drawer_count": int(lane.get("matched_drawer_count") or 0),
        "matched_version_detail_drawer_ids": lane.get("matched_version_detail_drawer_ids", []),
        "matched_source_ids": lane.get("matched_source_ids", []),
        "default_selected_version_detail_drawer_id": lane.get("default_selected_version_detail_drawer_id"),
        "filter_preset_status": "version_compare_navigation_filter_preset_preview_ready",
        "filter_preset_result_type": "owner_note_version_compare_navigation_filter_preset_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_saved_view_preset(
    preset_def: Dict[str, object],
    sequence: int,
    filter_preset_index: Dict[str, Dict[str, object]],
    navigation_items: List[Dict[str, object]],
) -> Dict[str, object]:
    lane_id = _safe_text(preset_def.get("filter_lane_id"))
    filter_preset = filter_preset_index.get(lane_id, {})
    matched_drawer_ids = set(filter_preset.get("matched_version_detail_drawer_ids", []))

    matched_items = [
        item for item in navigation_items
        if item.get("version_detail_drawer_id") in matched_drawer_ids
    ]

    if lane_id == "all_compare_drawers":
        matched_items = navigation_items

    default_item = matched_items[0] if matched_items else (navigation_items[0] if navigation_items else {})

    identity = {
        "pack": PACK_ID,
        "preset_id": preset_def.get("saved_view_preset_id"),
        "lane_id": lane_id,
        "sequence": sequence,
    }

    preset = {
        "saved_view_preset_preview_id": f"version_compare_navigation_saved_view_preset_{_stable_hash(identity, 18)}",
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
        "matched_source_ids": [item.get("source_id") for item in matched_items],
        "default_selected_navigation_item_id": default_item.get("navigation_item_id"),
        "default_selected_version_detail_drawer_id": default_item.get("version_detail_drawer_id"),
        "default_selected_source_id": default_item.get("source_id"),
        "comparison_row_count": sum(int(item.get("comparison_row_count") or 0) for item in matched_items),
        "changed_compare_row_count": sum(int(item.get("changed_compare_row_count") or 0) for item in matched_items),
        "unchanged_compare_row_count": sum(int(item.get("unchanged_compare_row_count") or 0) for item in matched_items),
        "saved_view_preset_status": "version_compare_navigation_saved_view_preset_preview_ready",
        "saved_view_preset_result_type": "owner_note_version_compare_navigation_saved_view_preset_preview",
        "view_allowed_in_preview": True,
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_selected_saved_view_preview(saved_view_presets: List[Dict[str, object]]) -> Dict[str, object]:
    selected = next((preset for preset in saved_view_presets if preset.get("is_default") is True), None)
    if selected is None and saved_view_presets:
        selected = saved_view_presets[0]
    selected = selected or {}

    payload = {
        "selected_saved_view_preview_id": f"version_compare_navigation_selected_saved_view_{_stable_hash(selected.get('saved_view_preset_id'), 18)}",
        "selected_saved_view_preset_preview_id": selected.get("saved_view_preset_preview_id"),
        "selected_saved_view_preset_id": selected.get("saved_view_preset_id"),
        "selected_label": selected.get("label"),
        "selected_filter_lane_id": selected.get("filter_lane_id"),
        "selected_linked_filter_preset_id": selected.get("linked_filter_preset_id"),
        "selected_navigation_item_count": selected.get("matched_navigation_item_count", 0),
        "selected_comparison_row_count": selected.get("comparison_row_count", 0),
        "selected_changed_compare_row_count": selected.get("changed_compare_row_count", 0),
        "selected_default_navigation_item_id": selected.get("default_selected_navigation_item_id"),
        "selected_default_version_detail_drawer_id": selected.get("default_selected_version_detail_drawer_id"),
        "selection_status": "version_compare_navigation_selected_saved_view_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_saved_view_preview",
        "view_allowed_in_preview": True,
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    payload.update(_base_flags())
    return payload


def _build_indexes(saved_view_presets: List[Dict[str, object]], filter_presets: List[Dict[str, object]]) -> Dict[str, object]:
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

        indexes["saved_views_by_preview_id"][preview_id] = preset
        indexes["saved_views_by_id"][preset_id] = preset
        indexes["saved_views_by_filter_lane_id"].setdefault(lane_id, []).append(preset)
        indexes["saved_views_by_priority"].setdefault(priority, []).append(preset)
        indexes["saved_views_by_default_state"].setdefault(default_key, []).append(preset)

    for preset in filter_presets:
        preset_id = _safe_text(preset.get("filter_preset_id"))
        lane_id = _safe_text(preset.get("filter_lane_id"))
        filter_type = _safe_text(preset.get("filter_type"))

        indexes["filter_presets_by_id"][preset_id] = preset
        indexes["filter_presets_by_lane_id"][lane_id] = preset
        indexes["filter_presets_by_filter_type"].setdefault(filter_type, []).append(preset)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached() -> Dict[str, object]:
    pack_183 = _load_pack_183_payload(force_refresh=False)

    navigation_preview = pack_183.get("navigation_preview", {})
    filter_lanes_preview = pack_183.get("filter_lanes_preview", {})

    navigation_items = navigation_preview.get("navigation_items", []) if isinstance(navigation_preview, dict) else []
    if not isinstance(navigation_items, list):
        navigation_items = []

    filter_lanes = filter_lanes_preview.get("filter_lanes", []) if isinstance(filter_lanes_preview, dict) else []
    if not isinstance(filter_lanes, list):
        filter_lanes = []

    filter_presets = [
        _build_filter_preset_from_lane(lane, idx)
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
    total_changed_rows = sum(int(preset.get("changed_compare_row_count") or 0) for preset in saved_view_presets)
    total_unchanged_rows = sum(int(preset.get("unchanged_compare_row_count") or 0) for preset in saved_view_presets)

    expected_saved_view_ids = {item.get("saved_view_preset_id") for item in SAVED_VIEW_PRESET_DEFS}
    actual_saved_view_ids = {item.get("saved_view_preset_id") for item in saved_view_presets}
    expected_filter_lane_ids = {
        "all_compare_drawers",
        "saved_view_preset_drawers",
        "filter_preset_drawers",
        "changed_fields_present",
        "unchanged_fields_present",
        "rollback_blocked",
        "restore_blocked",
        "save_blocked",
        "safe_preview_only",
    }
    actual_filter_lane_ids = {item.get("filter_lane_id") for item in filter_presets}

    readiness_checks = {
        "pack_183_ready": pack_183.get("status") == "ready",
        "has_navigation_items": len(navigation_items) >= 15,
        "has_filter_lanes": len(filter_lanes) >= 9,
        "has_saved_view_presets": len(saved_view_presets) == 6,
        "has_filter_presets": len(filter_presets) >= 9,
        "selected_saved_view_preview_ready": selected_saved_view_preview.get("selection_status") == "version_compare_navigation_selected_saved_view_preview_ready",
        "default_saved_view_present": "default_all_version_compare_navigation" in actual_saved_view_ids,
        "all_expected_saved_view_presets_present": expected_saved_view_ids.issubset(actual_saved_view_ids),
        "all_expected_filter_presets_present": expected_filter_lane_ids.issubset(actual_filter_lane_ids),
        "all_saved_view_presets_ready": all(preset.get("saved_view_preset_status") == "version_compare_navigation_saved_view_preset_preview_ready" for preset in saved_view_presets),
        "all_filter_presets_ready": all(preset.get("filter_preset_status") == "version_compare_navigation_filter_preset_preview_ready" for preset in filter_presets),
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
        "saved_view_indexes_present": bool(indexes.get("saved_views_by_id")),
        "filter_preset_indexes_present": bool(indexes.get("filter_presets_by_lane_id")),
        "default_all_version_compare_navigation_indexed": "default_all_version_compare_navigation" in indexes.get("saved_views_by_id", {}),
        "all_compare_drawers_filter_preset_indexed": "all_compare_drawers" in indexes.get("filter_presets_by_lane_id", {}),
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    payload = {
        "pack_id": PACK_ID,
        "pack_number": 184,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview",
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_183": {
            "status": pack_183.get("status"),
            "readiness_score": pack_183.get("summary", {}).get("readiness_score"),
            "navigation_item_count": pack_183.get("summary", {}).get("navigation_item_count"),
            "filter_lane_count": pack_183.get("summary", {}).get("filter_lane_count"),
            "quick_filter_chip_count": pack_183.get("summary", {}).get("quick_filter_chip_count"),
            "comparison_row_count": pack_183.get("summary", {}).get("comparison_row_count"),
        },
        "summary": {
            "saved_view_preset_count": len(saved_view_presets),
            "filter_preset_count": len(filter_presets),
            "source_navigation_item_count": len(navigation_items),
            "source_filter_lane_count": len(filter_lanes),
            "matched_navigation_item_total": total_matched_navigation_items,
            "comparison_row_count": total_comparison_rows,
            "changed_compare_row_count": total_changed_rows,
            "unchanged_compare_row_count": total_unchanged_rows,
            "saved_view_status_counts": _count_by(saved_view_presets, "saved_view_preset_status"),
            "filter_preset_status_counts": _count_by(filter_presets, "filter_preset_status"),
            "view_priority_counts": _count_by(saved_view_presets, "view_priority"),
            "filter_lane_counts": _count_by(saved_view_presets, "filter_lane_id"),
            "default_state_counts": {
                "default": len([preset for preset in saved_view_presets if preset.get("is_default") is True]),
                "not_default": len([preset for preset in saved_view_presets if preset.get("is_default") is False]),
            },
            "default_saved_view_preset_id": selected_saved_view_preview.get("selected_saved_view_preset_id"),
            "default_selected_version_detail_drawer_id": selected_saved_view_preview.get("selected_default_version_detail_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation saved view/filter preset preview ready" if readiness_score == 100 else "Owner note version compare navigation saved view/filter preset preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_preset_definitions": SAVED_VIEW_PRESET_DEFS,
        "saved_view_presets": saved_view_presets,
        "filter_presets": filter_presets,
        "selected_saved_view_preview": selected_saved_view_preview,
        "saved_view_filter_preset_indexes": indexes,
    }

    return payload


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 184,
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
        "changed_compare_row_count": summary.get("changed_compare_row_count"),
        "unchanged_compare_row_count": summary.get("unchanged_compare_row_count"),
        "default_saved_view_preset_id": summary.get("default_saved_view_preset_id"),
        "default_selected_version_detail_drawer_id": summary.get("default_selected_version_detail_drawer_id"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
        "label": "Owner Note Version Compare Saved Views",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview",
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "description": "Preview saved view/filter presets for version compare navigation with all persistence blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 184",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
        "title": "Owner Note Version Compare Saved Views",
        "subtitle": "Preview saved view/filter preset layer for owner note version compare navigation, with all persistence blocked.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Saved view readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "saved_views", "title": "Saved views", "value": summary.get("saved_view_preset_count"), "label": "Preview saved view presets"},
            {"id": "filter_presets", "title": "Filter presets", "value": summary.get("filter_preset_count"), "label": "Preview filter presets"},
            {"id": "source_navigation", "title": "Source navigation", "value": summary.get("source_navigation_item_count"), "label": "Pack 183 navigation items"},
            {"id": "default_saved_view", "title": "Default saved view", "value": summary.get("default_saved_view_preset_id"), "label": "Selected preset"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_saved_view_writes_blocked") and checks.get("all_filter_preference_saves_blocked") else "Review", "label": "No real saved view/filter write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-saved-view-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-saved-view-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 184</p>
            <h2>{section.get('title', 'Owner Note Version Compare Saved Views')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SAVED_VIEW_FILTER_PRESET_ENDPOINT}">Open version compare saved view/filter preset JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_FILTER_PRESET_ENDPOINT",
    "SOURCE_ENDPOINT",
    "SAVED_VIEW_PRESET_DEFS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_html_section",
]
