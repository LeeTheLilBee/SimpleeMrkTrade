
"""
PACK 189 - Owner Note Saved View Preset Detail Edit History Version Compare
Saved View / Filter Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview.

This module sits on top of Pack 188.

Pack 188 creates preview-only filter/navigation scaffolding for version detail compare drawers.
Pack 189 creates preview-only saved view/filter preset scaffolding:
- saved view presets
- filter presets
- selected saved view preview
- indexes
- blocked saved view/user preference/filter/navigation/drawer persistence

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


PACK_ID = "PACK_189"
SAVED_VIEW_FILTER_PRESET_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-filter-navigation.json"


SAVED_VIEW_PRESET_DEFS = [
    {
        "saved_view_preset_id": "default_all_version_compare_navigation",
        "label": "All Version Compare Navigation",
        "description": "Default view showing all version detail compare navigation drawers.",
        "filter_lane_id": "all_compare_drawers",
        "linked_filter_preset_id": "all_compare_drawers",
        "view_priority": "critical",
        "is_default": True,
        "sort_order": 1,
    },
    {
        "saved_view_preset_id": "saved_view_preset_focus",
        "label": "Saved View Preset Focus",
        "description": "Focus on saved view preset version compare drawers.",
        "filter_lane_id": "saved_view_preset_drawers",
        "linked_filter_preset_id": "saved_view_preset_drawers",
        "view_priority": "high",
        "is_default": False,
        "sort_order": 2,
    },
    {
        "saved_view_preset_id": "filter_preset_focus",
        "label": "Filter Preset Focus",
        "description": "Focus on filter preset version compare drawers.",
        "filter_lane_id": "filter_preset_drawers",
        "linked_filter_preset_id": "filter_preset_drawers",
        "view_priority": "high",
        "is_default": False,
        "sort_order": 3,
    },
    {
        "saved_view_preset_id": "changed_fields_focus",
        "label": "Changed Fields Focus",
        "description": "Focus on drawers with changed comparison rows.",
        "filter_lane_id": "changed_fields_present",
        "linked_filter_preset_id": "changed_fields_present",
        "view_priority": "medium",
        "is_default": False,
        "sort_order": 4,
    },
    {
        "saved_view_preset_id": "blocked_actions_focus",
        "label": "Blocked Actions Focus",
        "description": "Focus on drawers where save/rollback/restore are blocked.",
        "filter_lane_id": "rollback_blocked",
        "linked_filter_preset_id": "rollback_blocked",
        "view_priority": "critical",
        "is_default": False,
        "sort_order": 5,
    },
    {
        "saved_view_preset_id": "safe_preview_focus",
        "label": "Safe Preview Focus",
        "description": "Focus on safe preview-only drawers with no persistence.",
        "filter_lane_id": "safe_preview_only",
        "linked_filter_preset_id": "safe_preview_only",
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


def _load_pack_188_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_188",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"navigation_item_count": 0, "filter_lane_count": 0, "readiness_score": 0},
            "navigation_preview": {"navigation_items": []},
            "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_188",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"navigation_item_count": 0, "filter_lane_count": 0, "readiness_score": 0},
        "navigation_preview": {"navigation_items": []},
        "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
        **_base_flags(),
    }


def _lane_index(pack_188: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    payload = pack_188.get("filter_lanes_preview", {})
    index = payload.get("filter_lane_index", {}) if isinstance(payload, dict) else {}
    if isinstance(index, dict) and index:
        return index

    lanes = payload.get("filter_lanes", []) if isinstance(payload, dict) else []
    return {lane.get("filter_lane_id"): lane for lane in lanes if isinstance(lane, dict)}


def _navigation_items(pack_188: Dict[str, object]) -> List[Dict[str, object]]:
    payload = pack_188.get("navigation_preview", {})
    items = payload.get("navigation_items", []) if isinstance(payload, dict) else []
    return [item for item in items if isinstance(item, dict)]


def _matching_nav_items_for_lane(nav_items: List[Dict[str, object]], lane: Dict[str, object]) -> List[Dict[str, object]]:
    matched_ids = set(lane.get("matched_version_detail_drawer_ids", []))
    return [item for item in nav_items if item.get("version_detail_drawer_id") in matched_ids]


def _build_saved_view_preset(defn: Dict[str, object], pack_188: Dict[str, object], nav_items: List[Dict[str, object]], lanes: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    lane_id = defn["filter_lane_id"]
    lane = lanes.get(lane_id, {})
    matched_items = _matching_nav_items_for_lane(nav_items, lane)
    comparison_count = sum(int(item.get("comparison_row_count") or 0) for item in matched_items)
    changed_count = sum(int(item.get("changed_compare_row_count") or 0) for item in matched_items)
    unchanged_count = sum(int(item.get("unchanged_compare_row_count") or 0) for item in matched_items)

    preset = {
        "saved_view_preset_preview_id": f"version_compare_navigation_saved_view_preset_{_stable_hash((PACK_ID, defn['saved_view_preset_id'], lane_id), 18)}",
        "saved_view_preset_id": defn["saved_view_preset_id"],
        "label": defn["label"],
        "description": defn["description"],
        "filter_lane_id": lane_id,
        "linked_filter_preset_id": defn["linked_filter_preset_id"],
        "view_priority": defn["view_priority"],
        "is_default": bool(defn["is_default"]),
        "sort_order": int(defn["sort_order"]),
        "matched_navigation_item_count": len(matched_items),
        "matched_navigation_item_ids": [item.get("navigation_item_id") for item in matched_items],
        "matched_version_detail_drawer_ids": [item.get("version_detail_drawer_id") for item in matched_items],
        "matched_source_ids": [item.get("source_id") for item in matched_items],
        "default_selected_navigation_item_id": matched_items[0].get("navigation_item_id") if matched_items else None,
        "default_selected_version_detail_drawer_id": matched_items[0].get("version_detail_drawer_id") if matched_items else None,
        "comparison_row_count": comparison_count,
        "changed_compare_row_count": changed_count,
        "unchanged_compare_row_count": unchanged_count,
        "saved_view_preset_status": "version_compare_navigation_saved_view_preset_preview_ready",
        "saved_view_preset_result_type": "owner_note_version_compare_navigation_saved_view_preset_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_filter_preset(lane: Dict[str, object], nav_items: List[Dict[str, object]], order: int) -> Dict[str, object]:
    matched_items = _matching_nav_items_for_lane(nav_items, lane)
    comparison_count = sum(int(item.get("comparison_row_count") or 0) for item in matched_items)
    changed_count = sum(int(item.get("changed_compare_row_count") or 0) for item in matched_items)

    preset = {
        "filter_preset_id": f"version_compare_navigation_filter_preset_{_stable_hash((lane.get('filter_lane_id'), order), 18)}",
        "source_filter_lane_preview_id": lane.get("filter_lane_preview_id"),
        "filter_lane_id": lane.get("filter_lane_id"),
        "label": lane.get("label"),
        "filter_type": lane.get("filter_type"),
        "sort_order": int(order),
        "matched_drawer_count": len(matched_items),
        "matched_navigation_item_count": len(matched_items),
        "matched_navigation_item_ids": [item.get("navigation_item_id") for item in matched_items],
        "matched_version_detail_drawer_ids": [item.get("version_detail_drawer_id") for item in matched_items],
        "matched_source_ids": [item.get("source_id") for item in matched_items],
        "default_selected_navigation_item_id": matched_items[0].get("navigation_item_id") if matched_items else None,
        "default_selected_version_detail_drawer_id": matched_items[0].get("version_detail_drawer_id") if matched_items else None,
        "comparison_row_count": comparison_count,
        "changed_compare_row_count": changed_count,
        "filter_preset_status": "version_compare_navigation_filter_preset_preview_ready",
        "filter_preset_result_type": "owner_note_version_compare_navigation_filter_preset_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    preset.update(_base_flags())
    return preset


def _build_selected_saved_view_preview(saved_views: List[Dict[str, object]], filter_presets: List[Dict[str, object]]) -> Dict[str, object]:
    selected = next((item for item in saved_views if item.get("is_default") is True), saved_views[0] if saved_views else {})
    linked_filter = next(
        (item for item in filter_presets if item.get("filter_lane_id") == selected.get("linked_filter_preset_id")),
        {},
    )

    payload = {
        "selected_saved_view_preview_id": f"version_compare_navigation_selected_saved_view_{_stable_hash((selected.get('saved_view_preset_id'), selected.get('filter_lane_id')), 18)}",
        "selected_saved_view_preset_id": selected.get("saved_view_preset_id"),
        "selected_saved_view_preset_preview_id": selected.get("saved_view_preset_preview_id"),
        "selected_filter_lane_id": selected.get("filter_lane_id"),
        "selected_linked_filter_preset_id": linked_filter.get("filter_preset_id"),
        "selected_navigation_item_count": selected.get("matched_navigation_item_count"),
        "selected_comparison_row_count": selected.get("comparison_row_count"),
        "selected_changed_compare_row_count": selected.get("changed_compare_row_count"),
        "selected_default_navigation_item_id": selected.get("default_selected_navigation_item_id"),
        "selected_default_version_detail_drawer_id": selected.get("default_selected_version_detail_drawer_id"),
        "selection_status": "version_compare_navigation_selected_saved_view_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_saved_view_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    payload.update(_base_flags())
    return payload


def _build_indexes(saved_views: List[Dict[str, object]], filter_presets: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "saved_views_by_preview_id": {},
        "saved_views_by_id": {},
        "saved_views_by_filter_lane_id": {},
        "saved_views_by_priority": {},
        "saved_views_by_default_state": {"default": [], "not_default": []},
        "filter_presets_by_id": {},
        "filter_presets_by_lane_id": {},
        "filter_presets_by_filter_type": {},
    }

    for preset in saved_views:
        indexes["saved_views_by_preview_id"][preset["saved_view_preset_preview_id"]] = preset
        indexes["saved_views_by_id"][preset["saved_view_preset_id"]] = preset
        indexes["saved_views_by_filter_lane_id"].setdefault(preset["filter_lane_id"], []).append(preset)
        indexes["saved_views_by_priority"].setdefault(preset["view_priority"], []).append(preset)
        default_key = "default" if preset.get("is_default") else "not_default"
        indexes["saved_views_by_default_state"][default_key].append(preset)

    for preset in filter_presets:
        indexes["filter_presets_by_id"][preset["filter_preset_id"]] = preset
        indexes["filter_presets_by_lane_id"][preset["filter_lane_id"]] = preset
        indexes["filter_presets_by_filter_type"].setdefault(preset["filter_type"], []).append(preset)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached() -> Dict[str, object]:
    pack_188 = _load_pack_188_payload(force_refresh=False)
    nav_items = _navigation_items(pack_188)
    lanes = _lane_index(pack_188)

    saved_view_presets = [
        _build_saved_view_preset(defn, pack_188, nav_items, lanes)
        for defn in SAVED_VIEW_PRESET_DEFS
    ]

    ordered_lanes = []
    lane_defs = pack_188.get("filter_lanes_preview", {}).get("filter_lanes", [])
    if isinstance(lane_defs, list):
        ordered_lanes = [lane for lane in lane_defs if isinstance(lane, dict)]
    if not ordered_lanes:
        ordered_lanes = [lanes[key] for key in sorted(lanes.keys()) if isinstance(lanes.get(key), dict)]

    filter_presets = [
        _build_filter_preset(lane, nav_items, idx)
        for idx, lane in enumerate(ordered_lanes, start=1)
    ]

    selected_saved_view_preview = _build_selected_saved_view_preview(saved_view_presets, filter_presets)
    indexes = _build_indexes(saved_view_presets, filter_presets)

    matched_total = sum(int(preset.get("matched_navigation_item_count") or 0) for preset in saved_view_presets)
    comparison_total = sum(int(preset.get("comparison_row_count") or 0) for preset in saved_view_presets)
    changed_total = sum(int(preset.get("changed_compare_row_count") or 0) for preset in saved_view_presets)
    unchanged_total = sum(int(preset.get("unchanged_compare_row_count") or 0) for preset in saved_view_presets)

    expected_saved_view_ids = {item["saved_view_preset_id"] for item in SAVED_VIEW_PRESET_DEFS}
    expected_lane_ids = {
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

    readiness_checks = {
        "pack_188_ready": pack_188.get("status") == "ready",
        "has_navigation_items": len(nav_items) >= 15,
        "has_filter_lanes": len(lanes) >= 9,
        "has_saved_view_presets": len(saved_view_presets) == 6,
        "has_filter_presets": len(filter_presets) >= 9,
        "selected_saved_view_preview_ready": selected_saved_view_preview.get("selection_status") == "version_compare_navigation_selected_saved_view_preview_ready",
        "default_saved_view_present": any(item.get("is_default") is True for item in saved_view_presets),
        "all_expected_saved_view_presets_present": expected_saved_view_ids.issubset({item.get("saved_view_preset_id") for item in saved_view_presets}),
        "all_expected_filter_presets_present": expected_lane_ids.issubset({item.get("filter_lane_id") for item in filter_presets}),
        "all_saved_view_presets_ready": all(item.get("saved_view_preset_status") == "version_compare_navigation_saved_view_preset_preview_ready" for item in saved_view_presets),
        "all_filter_presets_ready": all(item.get("filter_preset_status") == "version_compare_navigation_filter_preset_preview_ready" for item in filter_presets),
        "all_saved_view_presets_simulated_only": all(item.get("simulated_only") is True for item in saved_view_presets),
        "all_filter_presets_simulated_only": all(item.get("simulated_only") is True for item in filter_presets),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in saved_view_presets + filter_presets),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in saved_view_presets + filter_presets),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in saved_view_presets + filter_presets),
        "all_filter_navigation_preview_only": all(item.get("filter_navigation_preview_only") is True for item in saved_view_presets + filter_presets),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in saved_view_presets + filter_presets),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in saved_view_presets + filter_presets),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in saved_view_presets + filter_presets),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in saved_view_presets + filter_presets),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in saved_view_presets + filter_presets),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in saved_view_presets + filter_presets),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in saved_view_presets + filter_presets),
        "no_real_history_written": all(item.get("real_history_written") is False for item in saved_view_presets + filter_presets),
        "no_real_version_written": all(item.get("real_version_written") is False for item in saved_view_presets + filter_presets),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in saved_view_presets + filter_presets),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in saved_view_presets + filter_presets),
        "all_user_preference_writes_blocked": all(item.get("user_preference_write_allowed_now") is False for item in saved_view_presets + filter_presets),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in saved_view_presets + filter_presets),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in saved_view_presets + filter_presets),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in saved_view_presets + filter_presets),
        "saved_view_indexes_present": bool(indexes.get("saved_views_by_id")),
        "filter_preset_indexes_present": bool(indexes.get("filter_presets_by_lane_id")),
        "default_all_version_compare_navigation_indexed": "default_all_version_compare_navigation" in indexes.get("saved_views_by_id", {}),
        "all_compare_drawers_filter_preset_indexed": "all_compare_drawers" in indexes.get("filter_presets_by_lane_id", {}),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 189,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Saved View / Filter Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview",
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_188": {
            "status": pack_188.get("status"),
            "readiness_score": pack_188.get("summary", {}).get("readiness_score"),
            "navigation_item_count": pack_188.get("summary", {}).get("navigation_item_count"),
            "version_detail_drawer_count": pack_188.get("summary", {}).get("version_detail_drawer_count"),
            "filter_lane_count": pack_188.get("summary", {}).get("filter_lane_count"),
            "quick_filter_chip_count": pack_188.get("summary", {}).get("quick_filter_chip_count"),
            "comparison_row_count": pack_188.get("summary", {}).get("comparison_row_count"),
        },
        "summary": {
            "saved_view_preset_count": len(saved_view_presets),
            "filter_preset_count": len(filter_presets),
            "source_navigation_item_count": len(nav_items),
            "source_filter_lane_count": len(lanes),
            "matched_navigation_item_total": matched_total,
            "comparison_row_count": comparison_total,
            "changed_compare_row_count": changed_total,
            "unchanged_compare_row_count": unchanged_total,
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


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 189,
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


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
        "label": "Owner Note Version Compare Saved Views",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Navigation Saved View / Filter Preset Preview",
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "description": "Preview saved view and filter presets for version compare navigation with all persistence blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 189",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
        "title": "Owner Note Version Compare Saved Views",
        "subtitle": "Preview saved view presets, filter presets, selected saved view state, and blocked persistence for version compare navigation.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Saved view readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "saved_views", "title": "Saved views", "value": summary.get("saved_view_preset_count"), "label": "Saved view presets"},
            {"id": "filter_presets", "title": "Filter presets", "value": summary.get("filter_preset_count"), "label": "Filter presets"},
            {"id": "source_navigation", "title": "Navigation source", "value": summary.get("source_navigation_item_count"), "label": "Source navigation items"},
            {"id": "matched_items", "title": "Matched items", "value": summary.get("matched_navigation_item_total"), "label": "Saved view matches"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_saved_view_writes_blocked") and checks.get("all_user_preference_writes_blocked") else "Review", "label": "No real saved view/preference write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
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
            <p class="tower-kicker">Pack 189</p>
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
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_html_section",
]
