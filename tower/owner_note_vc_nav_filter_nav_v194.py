
"""
PACK 194 - Owner Note Version Compare Navigation Compare Filter
Navigation / Drawer Selection Preview.

Short module filename:
    tower.owner_note_vc_nav_filter_nav_v194

This module sits on top of Pack 193.

Pack 193 creates preview-only compare filters/search facets.
Pack 194 creates preview-only navigation scaffolding:
- navigation items for compare filter lanes
- lane-to-drawer navigation groups
- drawer selection previews
- search/facet navigation summary
- default selected navigation item
- indexes
- blocked filter preference/navigation/drawer selection persistence

Important:
- simulated-only
- navigation-preview-only
- filter-navigation-preview-only
- drawer-selection-preview-only
- filter-preview-only
- search-facet-preview-only
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


PACK_ID = "PACK_194"
FILTER_NAV_ENDPOINT = "/tower/owner-note-vc-nav-filter-nav-v194.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-compare-filter-v193.json"


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
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "drawer_selection_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
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


def _load_pack_193_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_compare_filter_v193")
        fn = getattr(mod, "build_owner_note_vc_nav_compare_filter_v193_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_193",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "filter_lane_count": 0,
                "search_facet_count": 0,
                "quick_filter_chip_count": 0,
                "readiness_score": 0,
            },
            "filter_lanes": [],
            "search_facets": [],
            "quick_filter_chips": [],
            "selected_filter_preview": {},
            "compare_filter_indexes": {},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_193",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "filter_lane_count": 0,
            "search_facet_count": 0,
            "quick_filter_chip_count": 0,
            "readiness_score": 0,
        },
        "filter_lanes": [],
        "search_facets": [],
        "quick_filter_chips": [],
        "selected_filter_preview": {},
        "compare_filter_indexes": {},
        **_base_flags(),
    }


def _build_navigation_item(lane: Dict[str, object], sequence: int) -> Dict[str, object]:
    lane_id = _safe_text(lane.get("filter_lane_id"))
    matched_drawer_ids = lane.get("matched_version_detail_drawer_ids", [])
    if not isinstance(matched_drawer_ids, list):
        matched_drawer_ids = []

    matched_row_ids = lane.get("matched_compare_row_ids", [])
    if not isinstance(matched_row_ids, list):
        matched_row_ids = []

    nav = {
        "navigation_item_id": f"version_compare_navigation_filter_nav_item_{_stable_hash((PACK_ID, lane_id, sequence), 18)}",
        "filter_lane_id": lane_id,
        "filter_lane_preview_id": lane.get("filter_lane_preview_id"),
        "label": lane.get("label"),
        "description": lane.get("description"),
        "filter_type": lane.get("filter_type"),
        "sequence": int(sequence),
        "matched_version_detail_drawer_count": len(matched_drawer_ids),
        "matched_version_detail_drawer_ids": matched_drawer_ids,
        "matched_compare_row_count": len(matched_row_ids),
        "matched_compare_row_ids": matched_row_ids,
        "default_version_detail_drawer_id": matched_drawer_ids[0] if matched_drawer_ids else None,
        "navigation_status": "version_compare_navigation_filter_navigation_item_preview_ready",
        "navigation_result_type": "owner_note_version_compare_navigation_filter_navigation_item_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    nav.update(_base_flags())
    return nav


def _build_drawer_selection_preview(nav_item: Dict[str, object], sequence: int) -> Dict[str, object]:
    selected_drawer_id = nav_item.get("default_version_detail_drawer_id")
    drawer_ids = nav_item.get("matched_version_detail_drawer_ids", [])
    if not isinstance(drawer_ids, list):
        drawer_ids = []

    row_ids = nav_item.get("matched_compare_row_ids", [])
    if not isinstance(row_ids, list):
        row_ids = []

    selection = {
        "drawer_selection_preview_id": f"version_compare_navigation_drawer_selection_{_stable_hash((PACK_ID, nav_item.get('filter_lane_id'), selected_drawer_id, sequence), 18)}",
        "navigation_item_id": nav_item.get("navigation_item_id"),
        "filter_lane_id": nav_item.get("filter_lane_id"),
        "selected_version_detail_drawer_id": selected_drawer_id,
        "available_version_detail_drawer_count": len(drawer_ids),
        "available_version_detail_drawer_ids": drawer_ids,
        "visible_compare_row_count": len(row_ids),
        "visible_compare_row_ids": row_ids,
        "selection_status": "version_compare_navigation_drawer_selection_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_drawer_selection_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    selection.update(_base_flags())
    return selection


def _build_navigation_group(nav_item: Dict[str, object], selection: Dict[str, object], sequence: int) -> Dict[str, object]:
    group = {
        "navigation_group_id": f"version_compare_navigation_filter_group_{_stable_hash((PACK_ID, nav_item.get('filter_lane_id'), sequence), 18)}",
        "navigation_item_id": nav_item.get("navigation_item_id"),
        "drawer_selection_preview_id": selection.get("drawer_selection_preview_id"),
        "filter_lane_id": nav_item.get("filter_lane_id"),
        "label": nav_item.get("label"),
        "sequence": int(sequence),
        "drawer_count": nav_item.get("matched_version_detail_drawer_count"),
        "row_count": nav_item.get("matched_compare_row_count"),
        "selected_version_detail_drawer_id": selection.get("selected_version_detail_drawer_id"),
        "group_status": "version_compare_navigation_filter_group_preview_ready",
        "group_result_type": "owner_note_version_compare_navigation_filter_group_preview",
        "safe_preview_only": True,
    }
    group.update(_base_flags())
    return group


def _build_search_navigation_summary(facets: List[Dict[str, object]], chips: List[Dict[str, object]]) -> Dict[str, object]:
    facet_ids = [facet.get("search_facet_id") for facet in facets if isinstance(facet, dict)]
    chip_ids = [chip.get("quick_filter_chip_id") for chip in chips if isinstance(chip, dict)]

    value_count = 0
    for facet in facets:
        if isinstance(facet, dict):
            value_count += int(facet.get("value_count") or 0)

    summary = {
        "search_navigation_summary_id": f"version_compare_navigation_search_summary_{_stable_hash((PACK_ID, facet_ids, chip_ids), 18)}",
        "search_facet_count": len(facet_ids),
        "search_facet_ids": facet_ids,
        "search_facet_value_count": value_count,
        "quick_filter_chip_count": len(chip_ids),
        "quick_filter_chip_ids": chip_ids,
        "search_query_preview": "",
        "summary_status": "version_compare_navigation_search_summary_preview_ready",
        "summary_result_type": "owner_note_version_compare_navigation_search_summary_preview",
        "search_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_default_selected_navigation(nav_items: List[Dict[str, object]], selections: List[Dict[str, object]]) -> Dict[str, object]:
    default_item = next((item for item in nav_items if item.get("filter_lane_id") == "all_compare_drawers"), nav_items[0] if nav_items else {})
    default_selection = next(
        (item for item in selections if item.get("filter_lane_id") == default_item.get("filter_lane_id")),
        selections[0] if selections else {},
    )

    selected = {
        "selected_navigation_preview_id": f"version_compare_navigation_selected_nav_{_stable_hash(default_item.get('navigation_item_id'), 18)}",
        "default_filter_lane_id": default_item.get("filter_lane_id"),
        "selected_navigation_item_id": default_item.get("navigation_item_id"),
        "selected_drawer_selection_preview_id": default_selection.get("drawer_selection_preview_id"),
        "selected_version_detail_drawer_id": default_selection.get("selected_version_detail_drawer_id"),
        "selected_version_detail_drawer_count": default_item.get("matched_version_detail_drawer_count"),
        "selected_compare_row_count": default_item.get("matched_compare_row_count"),
        "selected_compare_row_ids": default_item.get("matched_compare_row_ids"),
        "selection_status": "version_compare_navigation_selected_navigation_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_navigation_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    selected.update(_base_flags())
    return selected


def _build_indexes(
    nav_items: List[Dict[str, object]],
    selections: List[Dict[str, object]],
    groups: List[Dict[str, object]],
) -> Dict[str, object]:
    indexes = {
        "navigation_items_by_id": {},
        "navigation_items_by_filter_lane_id": {},
        "navigation_items_by_filter_type": {},
        "drawer_selections_by_id": {},
        "drawer_selections_by_filter_lane_id": {},
        "navigation_groups_by_id": {},
        "navigation_groups_by_filter_lane_id": {},
        "version_detail_drawer_ids_by_filter_lane_id": {},
        "compare_row_ids_by_filter_lane_id": {},
    }

    for item in nav_items:
        item_id = item.get("navigation_item_id")
        lane_id = item.get("filter_lane_id")
        indexes["navigation_items_by_id"][item_id] = item
        indexes["navigation_items_by_filter_lane_id"][lane_id] = item
        indexes["navigation_items_by_filter_type"].setdefault(item.get("filter_type"), []).append(item)
        indexes["version_detail_drawer_ids_by_filter_lane_id"][lane_id] = item.get("matched_version_detail_drawer_ids", [])
        indexes["compare_row_ids_by_filter_lane_id"][lane_id] = item.get("matched_compare_row_ids", [])

    for selection in selections:
        selection_id = selection.get("drawer_selection_preview_id")
        lane_id = selection.get("filter_lane_id")
        indexes["drawer_selections_by_id"][selection_id] = selection
        indexes["drawer_selections_by_filter_lane_id"][lane_id] = selection

    for group in groups:
        group_id = group.get("navigation_group_id")
        lane_id = group.get("filter_lane_id")
        indexes["navigation_groups_by_id"][group_id] = group
        indexes["navigation_groups_by_filter_lane_id"][lane_id] = group

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_filter_nav_v194_payload_cached() -> Dict[str, object]:
    pack_193 = _load_pack_193_payload(force_refresh=False)

    lanes = pack_193.get("filter_lanes", [])
    if not isinstance(lanes, list):
        lanes = []
    lane_items = [lane for lane in lanes if isinstance(lane, dict)]

    facets = pack_193.get("search_facets", [])
    if not isinstance(facets, list):
        facets = []
    facet_items = [facet for facet in facets if isinstance(facet, dict)]

    chips = pack_193.get("quick_filter_chips", [])
    if not isinstance(chips, list):
        chips = []
    chip_items = [chip for chip in chips if isinstance(chip, dict)]

    nav_items = [_build_navigation_item(lane, idx) for idx, lane in enumerate(lane_items, start=1)]
    selections = [_build_drawer_selection_preview(item, idx) for idx, item in enumerate(nav_items, start=1)]
    groups = [
        _build_navigation_group(item, selection, idx)
        for idx, (item, selection) in enumerate(zip(nav_items, selections), start=1)
    ]
    search_summary = _build_search_navigation_summary(facet_items, chip_items)
    selected_navigation = _build_default_selected_navigation(nav_items, selections)
    indexes = _build_indexes(nav_items, selections, groups)

    total_drawer_refs = sum(int(item.get("matched_version_detail_drawer_count") or 0) for item in nav_items)
    total_row_refs = sum(int(item.get("matched_compare_row_count") or 0) for item in nav_items)

    readiness_checks = {
        "pack_193_ready": pack_193.get("status") == "ready",
        "has_filter_lanes": len(lane_items) == 9,
        "has_navigation_items": len(nav_items) == 9,
        "has_drawer_selection_previews": len(selections) == 9,
        "has_navigation_groups": len(groups) == 9,
        "has_search_navigation_summary": search_summary.get("summary_status") == "version_compare_navigation_search_summary_preview_ready",
        "default_selected_navigation_ready": selected_navigation.get("selection_status") == "version_compare_navigation_selected_navigation_preview_ready",
        "default_all_compare_navigation_present": selected_navigation.get("default_filter_lane_id") == "all_compare_drawers",
        "all_navigation_items_ready": all(item.get("navigation_status") == "version_compare_navigation_filter_navigation_item_preview_ready" for item in nav_items),
        "all_drawer_selections_ready": all(item.get("selection_status") == "version_compare_navigation_drawer_selection_preview_ready" for item in selections),
        "all_navigation_groups_ready": all(item.get("group_status") == "version_compare_navigation_filter_group_preview_ready" for item in groups),
        "navigation_indexes_present": bool(indexes.get("navigation_items_by_id")),
        "drawer_selection_indexes_present": bool(indexes.get("drawer_selections_by_id")),
        "navigation_group_indexes_present": bool(indexes.get("navigation_groups_by_id")),
        "has_drawer_references": total_drawer_refs >= int(pack_193.get("summary", {}).get("source_version_detail_drawer_count") or 0),
        "has_compare_row_references": total_row_refs >= int(pack_193.get("summary", {}).get("selected_compare_row_count") or 0),
        "selected_drawer_present": bool(selected_navigation.get("selected_version_detail_drawer_id")),
        "selected_rows_present": int(selected_navigation.get("selected_compare_row_count") or 0) >= 75,
        "all_simulated_only": all(item.get("simulated_only") is True for item in nav_items + selections + groups),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in nav_items + selections + groups),
        "all_filter_navigation_preview_only": all(item.get("filter_navigation_preview_only") is True for item in nav_items + selections + groups),
        "all_drawer_selection_preview_only": all(item.get("drawer_selection_preview_only") is True for item in nav_items + selections + groups),
        "all_filter_preview_only": all(item.get("filter_preview_only") is True for item in nav_items + selections + groups),
        "all_search_facet_preview_only": all(item.get("search_facet_preview_only") is True for item in nav_items + selections + groups),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in nav_items + selections + groups),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in nav_items + selections + groups),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in nav_items + selections + groups),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in nav_items + selections + groups),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in nav_items + selections + groups),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in nav_items + selections + groups),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in nav_items + selections + groups),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in nav_items + selections + groups),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 194,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Compare Filter Navigation / Drawer Selection Preview",
        "endpoint": FILTER_NAV_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_193": {
            "status": pack_193.get("status"),
            "readiness_score": pack_193.get("summary", {}).get("readiness_score"),
            "filter_lane_count": pack_193.get("summary", {}).get("filter_lane_count"),
            "search_facet_count": pack_193.get("summary", {}).get("search_facet_count"),
            "quick_filter_chip_count": pack_193.get("summary", {}).get("quick_filter_chip_count"),
            "selected_version_detail_drawer_count": pack_193.get("summary", {}).get("selected_version_detail_drawer_count"),
            "selected_compare_row_count": pack_193.get("summary", {}).get("selected_compare_row_count"),
        },
        "summary": {
            "navigation_item_count": len(nav_items),
            "drawer_selection_preview_count": len(selections),
            "navigation_group_count": len(groups),
            "search_navigation_facet_count": search_summary.get("search_facet_count"),
            "search_navigation_chip_count": search_summary.get("quick_filter_chip_count"),
            "total_navigation_drawer_reference_count": total_drawer_refs,
            "total_navigation_compare_row_reference_count": total_row_refs,
            "default_filter_lane_id": selected_navigation.get("default_filter_lane_id"),
            "selected_navigation_item_id": selected_navigation.get("selected_navigation_item_id"),
            "selected_version_detail_drawer_id": selected_navigation.get("selected_version_detail_drawer_id"),
            "selected_compare_row_count": selected_navigation.get("selected_compare_row_count"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation filter navigation/drawer selection preview ready" if readiness_score == 100 else "Owner note version compare navigation filter navigation/drawer selection preview needs review",
        },
        "readiness_checks": readiness_checks,
        "navigation_items": nav_items,
        "drawer_selection_previews": selections,
        "navigation_groups": groups,
        "search_navigation_summary": search_summary,
        "selected_navigation_preview": selected_navigation,
        "filter_navigation_indexes": indexes,
    }


def build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_filter_nav_v194_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_filter_nav_v194_payload_cached())


def get_owner_note_vc_nav_filter_nav_v194_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_filter_nav_v194_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_filter_nav_v194_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 194,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "navigation_item_count": summary.get("navigation_item_count"),
        "drawer_selection_preview_count": summary.get("drawer_selection_preview_count"),
        "navigation_group_count": summary.get("navigation_group_count"),
        "search_navigation_facet_count": summary.get("search_navigation_facet_count"),
        "search_navigation_chip_count": summary.get("search_navigation_chip_count"),
        "total_navigation_drawer_reference_count": summary.get("total_navigation_drawer_reference_count"),
        "total_navigation_compare_row_reference_count": summary.get("total_navigation_compare_row_reference_count"),
        "default_filter_lane_id": summary.get("default_filter_lane_id"),
        "selected_navigation_item_id": summary.get("selected_navigation_item_id"),
        "selected_version_detail_drawer_id": summary.get("selected_version_detail_drawer_id"),
        "selected_compare_row_count": summary.get("selected_compare_row_count"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_filter_nav_v194_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_filter_nav_v194_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_filter_nav_v194_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_filter_nav_v194_status_bridge()

    action = {
        "id": "owner_note_vc_nav_filter_nav_v194",
        "label": "Owner Note Compare Filter Navigation",
        "title": "Owner Note Version Compare Navigation Compare Filter Navigation / Drawer Selection Preview",
        "href": FILTER_NAV_ENDPOINT,
        "endpoint": FILTER_NAV_ENDPOINT,
        "description": "Preview navigation items, drawer selection previews, and groups for version compare filter lanes.",
        "status": bridge.get("status"),
        "pack": "Pack 194",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_filter_nav_v194_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_filter_nav_v194_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_filter_nav_v194",
        "title": "Owner Note Compare Filter Navigation",
        "subtitle": "Preview navigation and drawer selection for version compare filter lanes.",
        "status": payload.get("status"),
        "href": FILTER_NAV_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Navigation readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "items", "title": "Navigation items", "value": summary.get("navigation_item_count"), "label": "Filter navigation items"},
            {"id": "selections", "title": "Drawer selections", "value": summary.get("drawer_selection_preview_count"), "label": "Drawer selection previews"},
            {"id": "groups", "title": "Navigation groups", "value": summary.get("navigation_group_count"), "label": "Lane-to-drawer groups"},
            {"id": "selected_rows", "title": "Selected rows", "value": summary.get("selected_compare_row_count"), "label": "Default selected compare rows"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_navigation_persistence_blocked") and checks.get("all_drawer_selection_saves_blocked") else "Review", "label": "No navigation/drawer selection write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_filter_nav_v194_html_section() -> str:
    section = build_owner_note_vc_nav_filter_nav_v194_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card owner-note-vc-nav-filter-nav-v194-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section owner-note-vc-nav-filter-nav-v194-section" id="owner-note-vc-nav-filter-nav-v194">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 194</p>
            <h2>{section.get('title', 'Owner Note Compare Filter Navigation')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{FILTER_NAV_ENDPOINT}">Open compare filter navigation JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "FILTER_NAV_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_filter_nav_v194_payload",
    "get_owner_note_vc_nav_filter_nav_v194_payload",
    "build_owner_note_vc_nav_filter_nav_v194_status_bridge",
    "get_owner_note_vc_nav_filter_nav_v194_status_bridge",
    "build_owner_note_vc_nav_filter_nav_v194_quick_action",
    "build_owner_note_vc_nav_filter_nav_v194_unified_owner_section",
    "build_owner_note_vc_nav_filter_nav_v194_html_section",
]
