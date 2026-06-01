
"""
PACK 183 - Owner Note Saved View Preset Detail Edit History Version Compare Filter / Drawer Navigation Preview.

This module sits on top of Pack 182.

Pack 182 creates preview-only version detail/compare drawers.
Pack 183 creates preview-only navigation/filter scaffolding for those drawers:
- navigation items
- filter lanes
- quick filters
- grouped navigation
- selected drawer preview
- previous/next pointers
- blocked navigation/filter/drawer persistence

Important:
- simulated-only
- navigation-preview-only
- filter-navigation-preview-only
- version-detail-preview-only
- compare-view-preview-only
- edit-history-preview-only
- version-preview-only
- rollback-preview-only
- restore-preview-only
- no real navigation state persisted
- no real filter preference saved
- no real drawer selection saved
- no real history/version writes
- no real rollback/restore/save
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


PACK_ID = "PACK_183"
COMPARE_FILTER_NAVIGATION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json"
SOURCE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-detail-compare-view.json"


FILTER_LANE_DEFS = [
    {"filter_lane_id": "all_compare_drawers", "label": "All Compare Drawers", "filter_type": "all"},
    {"filter_lane_id": "saved_view_preset_drawers", "label": "Saved View Presets", "filter_type": "source_kind", "source_kind": "saved_view_preset"},
    {"filter_lane_id": "filter_preset_drawers", "label": "Filter Presets", "filter_type": "source_kind", "source_kind": "filter_preset"},
    {"filter_lane_id": "changed_fields_present", "label": "Changed Fields", "filter_type": "change_state", "change_state": "changed"},
    {"filter_lane_id": "unchanged_fields_present", "label": "Unchanged Fields", "filter_type": "change_state", "change_state": "unchanged"},
    {"filter_lane_id": "rollback_blocked", "label": "Rollback Blocked", "filter_type": "blocked_action", "blocked_action": "rollback"},
    {"filter_lane_id": "restore_blocked", "label": "Restore Blocked", "filter_type": "blocked_action", "blocked_action": "restore"},
    {"filter_lane_id": "save_blocked", "label": "Save Blocked", "filter_type": "blocked_action", "blocked_action": "save"},
    {"filter_lane_id": "safe_preview_only", "label": "Safe Preview Only", "filter_type": "safety"},
]

QUICK_FILTER_IDS = [
    "all_compare_drawers",
    "saved_view_preset_drawers",
    "filter_preset_drawers",
    "changed_fields_present",
    "rollback_blocked",
    "safe_preview_only",
]


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value, length: int = 18) -> str:
    return hashlib.sha256(repr(value).encode("utf-8", errors="ignore")).hexdigest()[:length]


def _safe_text(value) -> str:
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
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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


def _load_pack_182_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module(
            "tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view"
        )
        fn = getattr(
            mod,
            "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_payload",
            None,
        )
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_182",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "version_detail_drawer_count": 0,
                "comparison_row_count": 0,
                "readiness_score": 0,
            },
            "version_detail_drawers": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_182",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "version_detail_drawer_count": 0,
            "comparison_row_count": 0,
            "readiness_score": 0,
        },
        "version_detail_drawers": [],
        **_base_flags(),
    }


def _source_kind_rank(kind: str) -> int:
    return {"saved_view_preset": 1, "filter_preset": 2}.get(_safe_text(kind), 99)


def _sort_drawers(drawers: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted(
        [drawer for drawer in drawers if isinstance(drawer, dict)],
        key=lambda item: (
            _source_kind_rank(item.get("source_kind")),
            _safe_text(item.get("source_id")),
            _safe_text(item.get("version_detail_drawer_id")),
        ),
    )


def _count_by(items: List[Dict[str, object]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_navigation_item(drawer: Dict[str, object], position: int, total: int, ordered: List[Dict[str, object]]) -> Dict[str, object]:
    previous_drawer = ordered[position - 2] if position > 1 else None
    next_drawer = ordered[position] if position < total else None

    identity = {
        "pack": PACK_ID,
        "drawer": drawer.get("version_detail_drawer_id"),
        "timeline": drawer.get("edit_history_timeline_id"),
        "position": position,
    }

    item = {
        "navigation_item_id": f"saved_view_preset_version_compare_nav_item_{_stable_hash(identity, 18)}",
        "position": int(position),
        "total_count": int(total),
        "version_detail_drawer_id": _safe_text(drawer.get("version_detail_drawer_id")),
        "edit_history_timeline_id": _safe_text(drawer.get("edit_history_timeline_id")),
        "detail_edit_drawer_id": _safe_text(drawer.get("detail_edit_drawer_id")),
        "source_kind": _safe_text(drawer.get("source_kind")),
        "source_id": _safe_text(drawer.get("source_id")),
        "label": f"{_safe_text(drawer.get('source_kind')).replace('_', ' ').title()} · {_safe_text(drawer.get('source_id'))}",
        "comparison_row_count": int(drawer.get("comparison_row_count") or 0),
        "changed_compare_row_count": int(drawer.get("changed_field_count") or 0),
        "unchanged_compare_row_count": int(drawer.get("unchanged_field_count") or 0),
        "version_card_count": int(drawer.get("version_card_count") or 0),
        "has_previous": previous_drawer is not None,
        "previous_version_detail_drawer_id": previous_drawer.get("version_detail_drawer_id") if isinstance(previous_drawer, dict) else None,
        "previous_source_id": previous_drawer.get("source_id") if isinstance(previous_drawer, dict) else None,
        "has_next": next_drawer is not None,
        "next_version_detail_drawer_id": next_drawer.get("version_detail_drawer_id") if isinstance(next_drawer, dict) else None,
        "next_source_id": next_drawer.get("source_id") if isinstance(next_drawer, dict) else None,
        "navigation_status": "saved_view_preset_version_compare_navigation_item_preview_ready",
        "navigation_result_type": "owner_note_saved_view_preset_version_compare_navigation_item_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    item.update(_base_flags())
    return item


def _matches_lane(drawer: Dict[str, object], lane: Dict[str, object]) -> bool:
    filter_type = lane.get("filter_type")
    if filter_type == "all":
        return True
    if filter_type == "source_kind":
        return _safe_text(drawer.get("source_kind")) == lane.get("source_kind")
    if filter_type == "change_state":
        if lane.get("change_state") == "changed":
            return int(drawer.get("changed_field_count") or 0) > 0
        if lane.get("change_state") == "unchanged":
            return int(drawer.get("unchanged_field_count") or 0) > 0
    if filter_type == "blocked_action":
        action = lane.get("blocked_action")
        if action == "rollback":
            return drawer.get("rollback_action_preview", {}).get("allowed_now") is False
        if action == "restore":
            return drawer.get("restore_action_preview", {}).get("allowed_now") is False
        if action == "save":
            return drawer.get("save_action_preview", {}).get("allowed_now") is False
    if filter_type == "safety":
        return drawer.get("simulated_only") is True and drawer.get("real_version_saved") is False
    return False


def _build_filter_lane(lane_def: Dict[str, object], drawers: List[Dict[str, object]]) -> Dict[str, object]:
    matched = [drawer for drawer in drawers if _matches_lane(drawer, lane_def)]
    lane = {
        "filter_lane_preview_id": f"saved_view_preset_version_compare_filter_lane_{_stable_hash((lane_def.get('filter_lane_id'), len(matched)), 18)}",
        "filter_lane_id": lane_def["filter_lane_id"],
        "label": lane_def["label"],
        "filter_type": lane_def["filter_type"],
        "matched_drawer_count": len(matched),
        "matched_version_detail_drawer_ids": [drawer.get("version_detail_drawer_id") for drawer in matched],
        "matched_source_ids": [drawer.get("source_id") for drawer in matched],
        "default_selected_version_detail_drawer_id": matched[0].get("version_detail_drawer_id") if matched else None,
        "lane_status": "saved_view_preset_version_compare_filter_lane_preview_ready",
        "lane_result_type": "owner_note_saved_view_preset_version_compare_filter_lane_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    lane.update(_base_flags())
    return lane


def _build_filter_lanes(drawers: List[Dict[str, object]]) -> Dict[str, object]:
    lanes = [_build_filter_lane(defn, drawers) for defn in FILTER_LANE_DEFS]
    return {
        "filter_lanes_preview_id": f"saved_view_preset_version_compare_filter_lanes_{_stable_hash([lane['filter_lane_id'] for lane in lanes], 18)}",
        "filter_lanes": lanes,
        "filter_lane_count": len(lanes),
        "filter_lane_ids": [lane["filter_lane_id"] for lane in lanes],
        "filter_lane_index": {lane["filter_lane_id"]: lane for lane in lanes},
        "default_filter_lane_id": "all_compare_drawers",
        "filter_status": "saved_view_preset_version_compare_filter_lanes_preview_ready",
        "filter_result_type": "owner_note_saved_view_preset_version_compare_filter_lanes_preview",
        "filter_allowed_in_preview": True,
        **_base_flags(),
    }


def _build_quick_filter_chips(filter_lanes_payload: Dict[str, object]) -> Dict[str, object]:
    index = filter_lanes_payload.get("filter_lane_index", {})
    chips = []
    for order, lane_id in enumerate(QUICK_FILTER_IDS, start=1):
        lane = index.get(lane_id) if isinstance(index, dict) else None
        if not isinstance(lane, dict):
            continue
        chip = {
            "quick_filter_chip_id": f"saved_view_preset_version_compare_quick_filter_chip_{_stable_hash((lane_id, order), 18)}",
            "filter_lane_id": lane_id,
            "label": lane.get("label"),
            "order": int(order),
            "matched_drawer_count": lane.get("matched_drawer_count", 0),
            "chip_status": "saved_view_preset_version_compare_quick_filter_chip_preview_ready",
            "chip_result_type": "owner_note_saved_view_preset_version_compare_quick_filter_chip_preview",
            "filter_allowed_in_preview": True,
            "selection_allowed_in_preview": True,
            **_base_flags(),
        }
        chips.append(chip)

    return {
        "quick_filter_chips_preview_id": f"saved_view_preset_version_compare_quick_filter_chips_{_stable_hash([chip['filter_lane_id'] for chip in chips], 18)}",
        "quick_filter_chips": chips,
        "quick_filter_chip_count": len(chips),
        "quick_filter_ids": [chip["filter_lane_id"] for chip in chips],
        "quick_filter_status": "saved_view_preset_version_compare_quick_filter_chips_preview_ready",
        "quick_filter_result_type": "owner_note_saved_view_preset_version_compare_quick_filter_chips_preview",
        **_base_flags(),
    }


def _build_grouped_navigation(nav_items: List[Dict[str, object]]) -> Dict[str, object]:
    groups: Dict[str, Dict[str, object]] = {}
    for item in nav_items:
        key = _safe_text(item.get("source_kind")) or "unknown"
        groups.setdefault(
            key,
            {
                "group_id": f"source_kind_{key}",
                "group_key": key,
                "label": key.replace("_", " ").title(),
                "navigation_items": [],
                "navigation_item_count": 0,
                "group_status": "saved_view_preset_version_compare_grouped_navigation_preview_ready",
            },
        )
        groups[key]["navigation_items"].append(item)
        groups[key]["navigation_item_count"] = len(groups[key]["navigation_items"])

    return {
        "grouped_navigation_preview_id": f"saved_view_preset_version_compare_grouped_navigation_{_stable_hash(list(groups.keys()), 18)}",
        "groups": groups,
        "group_keys": list(groups.keys()),
        "group_count": len(groups),
        "grouped_navigation_status": "saved_view_preset_version_compare_grouped_navigation_preview_ready",
        "grouped_navigation_result_type": "owner_note_saved_view_preset_version_compare_grouped_navigation_preview",
        **_base_flags(),
    }


def _build_selected_drawer_preview(nav_items: List[Dict[str, object]], drawers_by_id: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    selected = nav_items[0] if nav_items else {}
    drawer_id = selected.get("version_detail_drawer_id")
    drawer = drawers_by_id.get(drawer_id, {}) if drawer_id else {}

    selected_payload = {
        "selected_drawer_preview_id": f"saved_view_preset_version_compare_selected_drawer_{_stable_hash((drawer_id, selected.get('source_id')), 18)}",
        "selected_navigation_item_id": selected.get("navigation_item_id"),
        "selected_version_detail_drawer_id": drawer_id,
        "selected_edit_history_timeline_id": selected.get("edit_history_timeline_id"),
        "selected_source_kind": selected.get("source_kind"),
        "selected_source_id": selected.get("source_id"),
        "selected_label": selected.get("label"),
        "selected_comparison_row_count": selected.get("comparison_row_count"),
        "selected_changed_compare_row_count": selected.get("changed_compare_row_count"),
        "selected_unchanged_compare_row_count": selected.get("unchanged_compare_row_count"),
        "selected_drawer_status": drawer.get("drawer_status"),
        "selection_status": "saved_view_preset_version_compare_selected_drawer_preview_ready",
        "selection_result_type": "owner_note_saved_view_preset_version_compare_selected_drawer_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        **_base_flags(),
    }
    return selected_payload


def _build_indexes(nav_items: List[Dict[str, object]], lanes_payload: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "navigation_items_by_id": {},
        "navigation_items_by_version_detail_drawer_id": {},
        "navigation_items_by_timeline_id": {},
        "navigation_items_by_detail_edit_drawer_id": {},
        "navigation_items_by_source_kind": {},
        "navigation_items_by_source_id": {},
        "filter_lanes_by_id": {},
        "navigation_items_by_filter_lane_id": {},
    }

    for item in nav_items:
        indexes["navigation_items_by_id"][item["navigation_item_id"]] = item
        indexes["navigation_items_by_version_detail_drawer_id"][item["version_detail_drawer_id"]] = item
        indexes["navigation_items_by_timeline_id"][item["edit_history_timeline_id"]] = item
        indexes["navigation_items_by_detail_edit_drawer_id"][item["detail_edit_drawer_id"]] = item
        indexes["navigation_items_by_source_kind"].setdefault(item["source_kind"], []).append(item)
        indexes["navigation_items_by_source_id"][item["source_id"]] = item

    lanes = lanes_payload.get("filter_lanes", [])
    if isinstance(lanes, list):
        for lane in lanes:
            lane_id = lane.get("filter_lane_id")
            indexes["filter_lanes_by_id"][lane_id] = lane
            drawer_ids = set(lane.get("matched_version_detail_drawer_ids", []))
            indexes["navigation_items_by_filter_lane_id"][lane_id] = [
                item for item in nav_items if item.get("version_detail_drawer_id") in drawer_ids
            ]

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload_cached() -> Dict[str, object]:
    pack_182 = _load_pack_182_payload(force_refresh=False)
    drawers = pack_182.get("version_detail_drawers", [])
    if not isinstance(drawers, list):
        drawers = []

    ordered_drawers = _sort_drawers(drawers)
    drawers_by_id = {drawer.get("version_detail_drawer_id"): drawer for drawer in ordered_drawers}

    navigation_items = [
        _build_navigation_item(drawer, idx, len(ordered_drawers), ordered_drawers)
        for idx, drawer in enumerate(ordered_drawers, start=1)
    ]

    filter_lanes_payload = _build_filter_lanes(ordered_drawers)
    quick_filter_payload = _build_quick_filter_chips(filter_lanes_payload)
    grouped_payload = _build_grouped_navigation(navigation_items)
    selected_payload = _build_selected_drawer_preview(navigation_items, drawers_by_id)
    indexes = _build_indexes(navigation_items, filter_lanes_payload)

    total_rows = sum(int(item.get("comparison_row_count") or 0) for item in navigation_items)
    changed_rows = sum(int(item.get("changed_compare_row_count") or 0) for item in navigation_items)
    unchanged_rows = sum(int(item.get("unchanged_compare_row_count") or 0) for item in navigation_items)

    expected_lane_ids = {lane["filter_lane_id"] for lane in FILTER_LANE_DEFS}

    readiness_checks = {
        "pack_182_ready": pack_182.get("status") == "ready",
        "has_version_detail_drawers": len(ordered_drawers) >= 15,
        "has_navigation_items": len(navigation_items) >= 15,
        "navigation_count_matches_drawers": len(navigation_items) == len(ordered_drawers),
        "has_filter_lanes": filter_lanes_payload.get("filter_lane_count") >= 9,
        "has_quick_filter_chips": quick_filter_payload.get("quick_filter_chip_count") == 6,
        "has_grouped_navigation": grouped_payload.get("group_count") >= 2,
        "has_selected_drawer_preview": bool(selected_payload.get("selected_version_detail_drawer_id")),
        "all_navigation_items_ready": all(item.get("navigation_status") == "saved_view_preset_version_compare_navigation_item_preview_ready" for item in navigation_items),
        "filter_lanes_ready": filter_lanes_payload.get("filter_status") == "saved_view_preset_version_compare_filter_lanes_preview_ready",
        "quick_filter_chips_ready": quick_filter_payload.get("quick_filter_status") == "saved_view_preset_version_compare_quick_filter_chips_preview_ready",
        "grouped_navigation_ready": grouped_payload.get("grouped_navigation_status") == "saved_view_preset_version_compare_grouped_navigation_preview_ready",
        "selected_drawer_preview_ready": selected_payload.get("selection_status") == "saved_view_preset_version_compare_selected_drawer_preview_ready",
        "all_expected_filter_lanes_present": expected_lane_ids.issubset(set(filter_lanes_payload.get("filter_lane_ids", []))),
        "all_quick_filters_present": set(QUICK_FILTER_IDS).issubset(set(quick_filter_payload.get("quick_filter_ids", []))),
        "has_previous_next_pointers": len(navigation_items) <= 1 or (
            navigation_items[0].get("has_previous") is False
            and navigation_items[0].get("has_next") is True
            and navigation_items[-1].get("has_next") is False
            and navigation_items[-1].get("has_previous") is True
        ),
        "navigation_indexes_present": bool(indexes.get("navigation_items_by_id")),
        "filter_lane_indexes_present": bool(indexes.get("filter_lanes_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in navigation_items),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in navigation_items),
        "all_filter_navigation_preview_only": all(item.get("filter_navigation_preview_only") is True for item in navigation_items),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in navigation_items),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in navigation_items),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in navigation_items),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in navigation_items),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in navigation_items),
        "no_real_history_written": all(item.get("real_history_written") is False for item in navigation_items),
        "no_real_version_written": all(item.get("real_version_written") is False for item in navigation_items),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in navigation_items),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in navigation_items),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in navigation_items),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in navigation_items),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in navigation_items),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in navigation_items),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in navigation_items),
        "all_saves_blocked": all(item.get("save_allowed_now") is False for item in navigation_items),
        "all_persists_blocked": all(item.get("persist_allowed_now") is False for item in navigation_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in navigation_items),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in navigation_items),
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 183,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Filter / Drawer Navigation Preview",
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_182": {
            "status": pack_182.get("status"),
            "readiness_score": pack_182.get("summary", {}).get("readiness_score"),
            "version_detail_drawer_count": pack_182.get("summary", {}).get("version_detail_drawer_count"),
            "version_card_count": pack_182.get("summary", {}).get("version_card_count"),
            "comparison_row_count": pack_182.get("summary", {}).get("comparison_row_count"),
            "changed_compare_row_count": pack_182.get("summary", {}).get("changed_compare_row_count"),
            "unchanged_compare_row_count": pack_182.get("summary", {}).get("unchanged_compare_row_count"),
        },
        "summary": {
            "navigation_item_count": len(navigation_items),
            "version_detail_drawer_count": len(ordered_drawers),
            "filter_lane_count": filter_lanes_payload.get("filter_lane_count"),
            "quick_filter_chip_count": quick_filter_payload.get("quick_filter_chip_count"),
            "group_count": grouped_payload.get("group_count"),
            "comparison_row_count": total_rows,
            "changed_compare_row_count": changed_rows,
            "unchanged_compare_row_count": unchanged_rows,
            "source_kind_counts": _count_by(navigation_items, "source_kind"),
            "default_filter_lane_id": filter_lanes_payload.get("default_filter_lane_id"),
            "default_selected_version_detail_drawer_id": selected_payload.get("selected_version_detail_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note saved view preset version compare filter/navigation preview ready" if readiness_score == 100 else "Owner note saved view preset version compare filter/navigation preview needs review",
        },
        "readiness_checks": readiness_checks,
        "filter_lane_definitions": FILTER_LANE_DEFS,
        "quick_filter_ids": QUICK_FILTER_IDS,
        "navigation_preview": {
            "navigation_preview_id": f"saved_view_preset_version_compare_navigation_{_stable_hash([item.get('navigation_item_id') for item in navigation_items], 18)}",
            "navigation_items": navigation_items,
            "navigation_item_count": len(navigation_items),
            "first_navigation_item_id": navigation_items[0].get("navigation_item_id") if navigation_items else None,
            "last_navigation_item_id": navigation_items[-1].get("navigation_item_id") if navigation_items else None,
            "default_selected_navigation_item_id": navigation_items[0].get("navigation_item_id") if navigation_items else None,
            "default_selected_version_detail_drawer_id": selected_payload.get("selected_version_detail_drawer_id"),
            "selected_drawer_preview": selected_payload,
            "navigation_status": "saved_view_preset_version_compare_drawer_navigation_preview_ready",
            "navigation_result_type": "owner_note_saved_view_preset_version_compare_drawer_navigation_preview",
            **_base_flags(),
        },
        "filter_lanes_preview": filter_lanes_payload,
        "quick_filter_chips_preview": quick_filter_payload,
        "grouped_navigation_preview": grouped_payload,
        "navigation_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload_cached())


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 183,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "navigation_item_count": summary.get("navigation_item_count"),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count"),
        "filter_lane_count": summary.get("filter_lane_count"),
        "quick_filter_chip_count": summary.get("quick_filter_chip_count"),
        "group_count": summary.get("group_count"),
        "comparison_row_count": summary.get("comparison_row_count"),
        "changed_compare_row_count": summary.get("changed_compare_row_count"),
        "unchanged_compare_row_count": summary.get("unchanged_compare_row_count"),
        "default_filter_lane_id": summary.get("default_filter_lane_id"),
        "default_selected_version_detail_drawer_id": summary.get("default_selected_version_detail_drawer_id"),
        **_base_flags(),
    }


def get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action() -> Dict[str, object]:
    bridge = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge()

    action = {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation",
        "label": "Owner Note Version Compare Navigation",
        "title": "Owner Note Saved View Preset Detail Edit History Version Compare Filter / Drawer Navigation Preview",
        "href": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "description": "Preview navigation, filters, quick chips, grouped navigation, and selected drawer state for version compare drawers.",
        "status": bridge.get("status"),
        "pack": "Pack 183",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section() -> Dict[str, object]:
    payload = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation",
        "title": "Owner Note Version Compare Navigation",
        "subtitle": "Preview navigation, filters, grouped drawer movement, selected drawer, and blocked navigation persistence for version compare drawers.",
        "status": payload.get("status"),
        "href": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "cards": [
            {"id": "navigation_readiness", "title": "Navigation readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "navigation_items", "title": "Navigation items", "value": summary.get("navigation_item_count"), "label": "Version compare drawer links"},
            {"id": "filter_lanes", "title": "Filter lanes", "value": summary.get("filter_lane_count"), "label": "Drawer filters"},
            {"id": "quick_filters", "title": "Quick filters", "value": summary.get("quick_filter_chip_count"), "label": "Quick filter chips"},
            {"id": "selected_drawer", "title": "Selected drawer", "value": summary.get("default_selected_version_detail_drawer_id"), "label": "Default selected drawer"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_navigation_persistence_blocked") else "Review", "label": "No real navigation/filter write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-version-compare-navigation-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-navigation-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 183</p>
            <h2>{section.get('title', 'Owner Note Version Compare Navigation')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{COMPARE_FILTER_NAVIGATION_ENDPOINT}">Open version compare navigation JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "COMPARE_FILTER_NAVIGATION_ENDPOINT",
    "SOURCE_ENDPOINT",
    "FILTER_LANE_DEFS",
    "QUICK_FILTER_IDS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_html_section",
]
