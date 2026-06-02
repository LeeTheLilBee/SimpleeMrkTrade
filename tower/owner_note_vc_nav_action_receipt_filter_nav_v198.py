
"""
PACK 198 - Owner Note Version Compare Navigation Action Receipt
Filter Navigation / Receipt Selection Preview.

Short module filename:
    tower.owner_note_vc_nav_action_receipt_filter_nav_v198

This module sits on top of Pack 197.

Pack 197 creates preview-only action receipt filter/search scaffolding.
Pack 198 creates preview-only action receipt navigation scaffolding:
- navigation items for action receipt filter lanes
- receipt selection previews
- filter-lane-to-receipt navigation groups
- search/facet navigation summary
- default selected receipt navigation preview
- navigation indexes
- blocked action execution/preference/navigation/drawer persistence
- blocked raw evidence reveal

Important:
- simulated-only
- action-receipt-navigation-preview-only
- receipt-selection-preview-only
- action-receipt-filter-preview-only
- no real action executed
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
- no raw evidence reveal
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


PACK_ID = "PACK_198"
ACTION_RECEIPT_FILTER_NAV_ENDPOINT = "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-action-receipt-filter-v197.json"


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
        "action_receipt_navigation_preview_only": True,
        "receipt_selection_preview_only": True,
        "action_receipt_filter_preview_only": True,
        "search_facet_preview_only": True,
        "filter_preview_only": True,
        "filter_navigation_preview_only": True,
        "action_receipt_preview_only": True,
        "blocked_action_receipt_preview_only": True,
        "preview_action_receipt_preview_only": True,
        "drawer_action_preview_only": True,
        "selected_drawer_preview_only": True,
        "compare_row_focus_preview_only": True,
        "navigation_preview_only": True,
        "drawer_selection_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "action_execution_allowed_now": False,
        "real_action_executed": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_197_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_action_receipt_filter_v197")
        fn = getattr(mod, "build_owner_note_vc_nav_action_receipt_filter_v197_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_197",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "action_receipt_filter_lane_count": 0,
                "action_receipt_search_facet_count": 0,
                "action_receipt_quick_filter_chip_count": 0,
                "selected_action_receipt_count": 0,
                "readiness_score": 0,
            },
            "action_receipt_filter_lanes": [],
            "action_receipt_search_facets": [],
            "action_receipt_quick_filter_chips": [],
            "selected_action_receipt_filter_preview": {},
            "action_receipt_filter_indexes": {},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_197",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "action_receipt_filter_lane_count": 0,
            "action_receipt_search_facet_count": 0,
            "action_receipt_quick_filter_chip_count": 0,
            "selected_action_receipt_count": 0,
            "readiness_score": 0,
        },
        "action_receipt_filter_lanes": [],
        "action_receipt_search_facets": [],
        "action_receipt_quick_filter_chips": [],
        "selected_action_receipt_filter_preview": {},
        "action_receipt_filter_indexes": {},
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_navigation_item(lane: Dict[str, object], sequence: int) -> Dict[str, object]:
    lane_id = _safe_text(lane.get("action_receipt_filter_lane_id"))
    receipt_ids = _list(lane.get("matched_action_receipt_ids"))

    item = {
        "action_receipt_navigation_item_id": f"version_compare_navigation_action_receipt_nav_item_{_stable_hash((PACK_ID, lane_id, sequence), 18)}",
        "action_receipt_filter_lane_id": lane_id,
        "action_receipt_filter_lane_preview_id": lane.get("action_receipt_filter_lane_preview_id"),
        "label": lane.get("label"),
        "description": lane.get("description"),
        "filter_type": lane.get("filter_type"),
        "sequence": int(sequence),
        "matched_action_receipt_count": len(receipt_ids),
        "matched_action_receipt_ids": receipt_ids,
        "default_action_receipt_id": receipt_ids[0] if receipt_ids else None,
        "navigation_status": "version_compare_navigation_action_receipt_navigation_item_preview_ready",
        "navigation_result_type": "owner_note_version_compare_navigation_action_receipt_navigation_item_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    item.update(_base_flags())
    return item


def _build_receipt_selection_preview(nav_item: Dict[str, object], sequence: int) -> Dict[str, object]:
    receipt_ids = _list(nav_item.get("matched_action_receipt_ids"))
    selected_receipt_id = nav_item.get("default_action_receipt_id")

    selection = {
        "action_receipt_selection_preview_id": f"version_compare_navigation_action_receipt_selection_{_stable_hash((PACK_ID, nav_item.get('action_receipt_filter_lane_id'), selected_receipt_id, sequence), 18)}",
        "action_receipt_navigation_item_id": nav_item.get("action_receipt_navigation_item_id"),
        "action_receipt_filter_lane_id": nav_item.get("action_receipt_filter_lane_id"),
        "selected_action_receipt_id": selected_receipt_id,
        "available_action_receipt_count": len(receipt_ids),
        "available_action_receipt_ids": receipt_ids,
        "selection_status": "version_compare_navigation_action_receipt_selection_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_action_receipt_selection_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    selection.update(_base_flags())
    return selection


def _build_navigation_group(nav_item: Dict[str, object], selection: Dict[str, object], sequence: int) -> Dict[str, object]:
    group = {
        "action_receipt_navigation_group_id": f"version_compare_navigation_action_receipt_navigation_group_{_stable_hash((PACK_ID, nav_item.get('action_receipt_filter_lane_id'), sequence), 18)}",
        "action_receipt_navigation_item_id": nav_item.get("action_receipt_navigation_item_id"),
        "action_receipt_selection_preview_id": selection.get("action_receipt_selection_preview_id"),
        "action_receipt_filter_lane_id": nav_item.get("action_receipt_filter_lane_id"),
        "label": nav_item.get("label"),
        "sequence": int(sequence),
        "action_receipt_count": nav_item.get("matched_action_receipt_count"),
        "selected_action_receipt_id": selection.get("selected_action_receipt_id"),
        "group_status": "version_compare_navigation_action_receipt_navigation_group_preview_ready",
        "group_result_type": "owner_note_version_compare_navigation_action_receipt_navigation_group_preview",
        "safe_preview_only": True,
    }
    group.update(_base_flags())
    return group


def _build_search_navigation_summary(facets: List[Dict[str, object]], chips: List[Dict[str, object]]) -> Dict[str, object]:
    facet_ids = [facet.get("action_receipt_search_facet_id") for facet in facets if isinstance(facet, dict)]
    chip_ids = [chip.get("action_receipt_quick_filter_chip_id") for chip in chips if isinstance(chip, dict)]

    value_count = 0
    for facet in facets:
        if isinstance(facet, dict):
            value_count += int(facet.get("value_count") or 0)

    summary = {
        "action_receipt_search_navigation_summary_id": f"version_compare_navigation_action_receipt_search_summary_{_stable_hash((PACK_ID, facet_ids, chip_ids), 18)}",
        "action_receipt_search_facet_count": len(facet_ids),
        "action_receipt_search_facet_ids": facet_ids,
        "action_receipt_search_facet_value_count": value_count,
        "action_receipt_quick_filter_chip_count": len(chip_ids),
        "action_receipt_quick_filter_chip_ids": chip_ids,
        "search_query_preview": "",
        "summary_status": "version_compare_navigation_action_receipt_search_summary_preview_ready",
        "summary_result_type": "owner_note_version_compare_navigation_action_receipt_search_summary_preview",
        "search_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_selected_navigation(nav_items: List[Dict[str, object]], selections: List[Dict[str, object]]) -> Dict[str, object]:
    selected_item = next((item for item in nav_items if item.get("action_receipt_filter_lane_id") == "all_action_receipts"), nav_items[0] if nav_items else {})
    selected_selection = next(
        (item for item in selections if item.get("action_receipt_filter_lane_id") == selected_item.get("action_receipt_filter_lane_id")),
        selections[0] if selections else {},
    )

    selected = {
        "selected_action_receipt_navigation_preview_id": f"version_compare_navigation_selected_action_receipt_nav_{_stable_hash(selected_item.get('action_receipt_navigation_item_id'), 18)}",
        "default_action_receipt_filter_lane_id": selected_item.get("action_receipt_filter_lane_id"),
        "selected_action_receipt_navigation_item_id": selected_item.get("action_receipt_navigation_item_id"),
        "selected_action_receipt_selection_preview_id": selected_selection.get("action_receipt_selection_preview_id"),
        "selected_action_receipt_id": selected_selection.get("selected_action_receipt_id"),
        "selected_action_receipt_count": selected_item.get("matched_action_receipt_count"),
        "selected_action_receipt_ids": selected_item.get("matched_action_receipt_ids"),
        "selection_status": "version_compare_navigation_selected_action_receipt_navigation_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_action_receipt_navigation_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    selected.update(_base_flags())
    return selected


def _build_indexes(nav_items: List[Dict[str, object]], selections: List[Dict[str, object]], groups: List[Dict[str, object]]) -> Dict[str, object]:
    indexes = {
        "action_receipt_navigation_items_by_id": {},
        "action_receipt_navigation_items_by_filter_lane_id": {},
        "action_receipt_navigation_items_by_filter_type": {},
        "action_receipt_selections_by_id": {},
        "action_receipt_selections_by_filter_lane_id": {},
        "action_receipt_navigation_groups_by_id": {},
        "action_receipt_navigation_groups_by_filter_lane_id": {},
        "action_receipt_ids_by_filter_lane_id": {},
    }

    for item in nav_items:
        item_id = item.get("action_receipt_navigation_item_id")
        lane_id = item.get("action_receipt_filter_lane_id")
        indexes["action_receipt_navigation_items_by_id"][item_id] = item
        indexes["action_receipt_navigation_items_by_filter_lane_id"][lane_id] = item
        indexes["action_receipt_navigation_items_by_filter_type"].setdefault(item.get("filter_type"), []).append(item)
        indexes["action_receipt_ids_by_filter_lane_id"][lane_id] = item.get("matched_action_receipt_ids", [])

    for selection in selections:
        selection_id = selection.get("action_receipt_selection_preview_id")
        lane_id = selection.get("action_receipt_filter_lane_id")
        indexes["action_receipt_selections_by_id"][selection_id] = selection
        indexes["action_receipt_selections_by_filter_lane_id"][lane_id] = selection

    for group in groups:
        group_id = group.get("action_receipt_navigation_group_id")
        lane_id = group.get("action_receipt_filter_lane_id")
        indexes["action_receipt_navigation_groups_by_id"][group_id] = group
        indexes["action_receipt_navigation_groups_by_filter_lane_id"][lane_id] = group

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload_cached() -> Dict[str, object]:
    pack_197 = _load_pack_197_payload(force_refresh=False)

    lanes = _list(pack_197.get("action_receipt_filter_lanes"))
    lanes = [item for item in lanes if isinstance(item, dict)]

    facets = _list(pack_197.get("action_receipt_search_facets"))
    facets = [item for item in facets if isinstance(item, dict)]

    chips = _list(pack_197.get("action_receipt_quick_filter_chips"))
    chips = [item for item in chips if isinstance(item, dict)]

    nav_items = [_build_navigation_item(lane, idx) for idx, lane in enumerate(lanes, start=1)]
    selections = [_build_receipt_selection_preview(item, idx) for idx, item in enumerate(nav_items, start=1)]
    groups = [
        _build_navigation_group(item, selection, idx)
        for idx, (item, selection) in enumerate(zip(nav_items, selections), start=1)
    ]
    search_summary = _build_search_navigation_summary(facets, chips)
    selected = _build_selected_navigation(nav_items, selections)
    indexes = _build_indexes(nav_items, selections, groups)

    total_receipt_refs = sum(int(item.get("matched_action_receipt_count") or 0) for item in nav_items)

    readiness_checks = {
        "pack_197_ready": pack_197.get("status") == "ready",
        "has_filter_lanes": len(lanes) == 8,
        "has_navigation_items": len(nav_items) == 8,
        "has_receipt_selection_previews": len(selections) == 8,
        "has_navigation_groups": len(groups) == 8,
        "has_search_navigation_summary": search_summary.get("summary_status") == "version_compare_navigation_action_receipt_search_summary_preview_ready",
        "default_selected_navigation_ready": selected.get("selection_status") == "version_compare_navigation_selected_action_receipt_navigation_preview_ready",
        "default_all_action_receipts_navigation_present": selected.get("default_action_receipt_filter_lane_id") == "all_action_receipts",
        "all_navigation_items_ready": all(item.get("navigation_status") == "version_compare_navigation_action_receipt_navigation_item_preview_ready" for item in nav_items),
        "all_receipt_selections_ready": all(item.get("selection_status") == "version_compare_navigation_action_receipt_selection_preview_ready" for item in selections),
        "all_navigation_groups_ready": all(item.get("group_status") == "version_compare_navigation_action_receipt_navigation_group_preview_ready" for item in groups),
        "navigation_indexes_present": bool(indexes.get("action_receipt_navigation_items_by_id")),
        "selection_indexes_present": bool(indexes.get("action_receipt_selections_by_id")),
        "group_indexes_present": bool(indexes.get("action_receipt_navigation_groups_by_id")),
        "has_receipt_references": total_receipt_refs >= int(pack_197.get("summary", {}).get("selected_action_receipt_count") or 0),
        "selected_receipt_present": bool(selected.get("selected_action_receipt_id")),
        "selected_receipts_match_total": int(selected.get("selected_action_receipt_count") or 0) == int(pack_197.get("summary", {}).get("selected_action_receipt_count") or 0),
        "all_simulated_only": all(item.get("simulated_only") is True for item in nav_items + selections + groups),
        "all_action_receipt_navigation_preview_only": all(item.get("action_receipt_navigation_preview_only") is True for item in nav_items + selections + groups),
        "all_receipt_selection_preview_only": all(item.get("receipt_selection_preview_only") is True for item in nav_items + selections + groups),
        "all_action_receipt_filter_preview_only": all(item.get("action_receipt_filter_preview_only") is True for item in nav_items + selections + groups),
        "all_action_receipt_preview_only": all(item.get("action_receipt_preview_only") is True for item in nav_items + selections + groups),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in nav_items + selections + groups),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in nav_items + selections + groups),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in nav_items + selections + groups),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in nav_items + selections + groups),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in nav_items + selections + groups),
        "all_action_execution_blocked": all(item.get("action_execution_allowed_now") is False for item in nav_items + selections + groups),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in nav_items + selections + groups),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in nav_items + selections + groups),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in nav_items + selections + groups),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in nav_items + selections + groups),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 198,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Action Receipt Filter Navigation / Receipt Selection Preview",
        "endpoint": ACTION_RECEIPT_FILTER_NAV_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_197": {
            "status": pack_197.get("status"),
            "readiness_score": pack_197.get("summary", {}).get("readiness_score"),
            "action_receipt_filter_lane_count": pack_197.get("summary", {}).get("action_receipt_filter_lane_count"),
            "action_receipt_search_facet_count": pack_197.get("summary", {}).get("action_receipt_search_facet_count"),
            "action_receipt_quick_filter_chip_count": pack_197.get("summary", {}).get("action_receipt_quick_filter_chip_count"),
            "selected_action_receipt_count": pack_197.get("summary", {}).get("selected_action_receipt_count"),
        },
        "summary": {
            "action_receipt_navigation_item_count": len(nav_items),
            "action_receipt_selection_preview_count": len(selections),
            "action_receipt_navigation_group_count": len(groups),
            "search_navigation_facet_count": search_summary.get("action_receipt_search_facet_count"),
            "search_navigation_chip_count": search_summary.get("action_receipt_quick_filter_chip_count"),
            "total_navigation_receipt_reference_count": total_receipt_refs,
            "default_action_receipt_filter_lane_id": selected.get("default_action_receipt_filter_lane_id"),
            "selected_action_receipt_navigation_item_id": selected.get("selected_action_receipt_navigation_item_id"),
            "selected_action_receipt_selection_preview_id": selected.get("selected_action_receipt_selection_preview_id"),
            "selected_action_receipt_id": selected.get("selected_action_receipt_id"),
            "selected_action_receipt_count": selected.get("selected_action_receipt_count"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note action receipt filter navigation/receipt selection preview ready" if readiness_score == 100 else "Owner note action receipt filter navigation/receipt selection preview needs review",
        },
        "readiness_checks": readiness_checks,
        "action_receipt_navigation_items": nav_items,
        "action_receipt_selection_previews": selections,
        "action_receipt_navigation_groups": groups,
        "action_receipt_search_navigation_summary": search_summary,
        "selected_action_receipt_navigation_preview": selected,
        "action_receipt_filter_navigation_indexes": indexes,
    }


def build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload_cached())


def get_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 198,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "action_receipt_navigation_item_count": summary.get("action_receipt_navigation_item_count"),
        "action_receipt_selection_preview_count": summary.get("action_receipt_selection_preview_count"),
        "action_receipt_navigation_group_count": summary.get("action_receipt_navigation_group_count"),
        "search_navigation_facet_count": summary.get("search_navigation_facet_count"),
        "search_navigation_chip_count": summary.get("search_navigation_chip_count"),
        "total_navigation_receipt_reference_count": summary.get("total_navigation_receipt_reference_count"),
        "default_action_receipt_filter_lane_id": summary.get("default_action_receipt_filter_lane_id"),
        "selected_action_receipt_navigation_item_id": summary.get("selected_action_receipt_navigation_item_id"),
        "selected_action_receipt_selection_preview_id": summary.get("selected_action_receipt_selection_preview_id"),
        "selected_action_receipt_id": summary.get("selected_action_receipt_id"),
        "selected_action_receipt_count": summary.get("selected_action_receipt_count"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge()

    action = {
        "id": "owner_note_vc_nav_action_receipt_filter_nav_v198",
        "label": "Owner Note Action Receipt Navigation",
        "title": "Owner Note Version Compare Navigation Action Receipt Filter Navigation / Receipt Selection Preview",
        "href": ACTION_RECEIPT_FILTER_NAV_ENDPOINT,
        "endpoint": ACTION_RECEIPT_FILTER_NAV_ENDPOINT,
        "description": "Preview navigation and receipt selection for action receipt filter lanes.",
        "status": bridge.get("status"),
        "pack": "Pack 198",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_action_receipt_filter_nav_v198",
        "title": "Owner Note Action Receipt Navigation",
        "subtitle": "Preview navigation and selection for action receipt filter lanes.",
        "status": payload.get("status"),
        "href": ACTION_RECEIPT_FILTER_NAV_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Navigation readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "items", "title": "Navigation items", "value": summary.get("action_receipt_navigation_item_count"), "label": "Action receipt navigation items"},
            {"id": "selections", "title": "Receipt selections", "value": summary.get("action_receipt_selection_preview_count"), "label": "Receipt selection previews"},
            {"id": "groups", "title": "Navigation groups", "value": summary.get("action_receipt_navigation_group_count"), "label": "Filter-lane navigation groups"},
            {"id": "selected", "title": "Selected receipts", "value": summary.get("selected_action_receipt_count"), "label": "Default selected receipt count"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("all_navigation_persistence_blocked") else "Review", "label": "No real execution/navigation write"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "ACTION_RECEIPT_FILTER_NAV_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload",
    "get_owner_note_vc_nav_action_receipt_filter_nav_v198_payload",
    "build_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge",
    "get_owner_note_vc_nav_action_receipt_filter_nav_v198_status_bridge",
    "build_owner_note_vc_nav_action_receipt_filter_nav_v198_quick_action",
    "build_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_owner_section",
]
