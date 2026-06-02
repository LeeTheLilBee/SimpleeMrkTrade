
"""
PACK 193 - Owner Note Version Compare Navigation Saved View / Filter Preset
Version Detail Compare Filter / Search Facets Preview.

Short module filename:
    tower.owner_note_vc_nav_compare_filter_v193

This module sits on top of Pack 192.

Pack 192 creates preview-only version detail drawers and compare rows.

Pack 193 creates preview-only filter/search scaffolding:
- filter lanes
- search facets
- quick filter chips
- selected filter/search preview
- filtered drawer/result indexes
- blocked filter preference/navigation/drawer selection persistence

Important:
- simulated-only
- filter-preview-only
- search-facet-preview-only
- version-detail-preview-only
- compare-view-preview-only
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
from typing import Any, Dict, List, Set


PACK_ID = "PACK_193"
COMPARE_FILTER_ENDPOINT = "/tower/owner-note-vc-nav-compare-filter-v193.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-version-compare-v192.json"


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
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "restore_preview_only": True,
        "compare_preview_only": True,
        "detail_edit_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_preview_only": True,
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


def _load_pack_192_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_version_compare_v192")
        fn = getattr(mod, "build_owner_note_vc_nav_version_compare_v192_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_192",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "version_detail_drawer_count": 0,
                "comparison_row_count": 0,
                "readiness_score": 0,
            },
            "version_detail_drawers": [],
            "selected_version_detail_preview": {},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_192",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "version_detail_drawer_count": 0,
            "comparison_row_count": 0,
            "readiness_score": 0,
        },
        "version_detail_drawers": [],
        "selected_version_detail_preview": {},
        **_base_flags(),
    }


def _drawer_id(drawer: Dict[str, object]) -> str:
    return _safe_text(drawer.get("version_detail_drawer_id"))


def _row_ids(drawer: Dict[str, object]) -> List[str]:
    rows = drawer.get("compare_rows", [])
    if not isinstance(rows, list):
        return []
    return [_safe_text(row.get("compare_row_id")) for row in rows if isinstance(row, dict)]


def _field_ids(drawer: Dict[str, object]) -> Set[str]:
    rows = drawer.get("compare_rows", [])
    if not isinstance(rows, list):
        return set()
    return {_safe_text(row.get("field_id")) for row in rows if isinstance(row, dict) and row.get("field_id")}


def _build_filter_lane(
    lane_id: str,
    label: str,
    filter_type: str,
    drawers: List[Dict[str, object]],
    matched_drawers: List[Dict[str, object]],
    sequence: int,
    description: str,
) -> Dict[str, object]:
    matched_ids = [_drawer_id(drawer) for drawer in matched_drawers]
    matched_row_ids = []
    for drawer in matched_drawers:
        matched_row_ids.extend(_row_ids(drawer))

    lane = {
        "filter_lane_preview_id": f"version_compare_navigation_filter_lane_{_stable_hash((PACK_ID, lane_id, sequence), 18)}",
        "filter_lane_id": lane_id,
        "label": label,
        "description": description,
        "filter_type": filter_type,
        "sequence": int(sequence),
        "matched_version_detail_drawer_count": len(matched_drawers),
        "matched_version_detail_drawer_ids": matched_ids,
        "matched_compare_row_count": len(matched_row_ids),
        "matched_compare_row_ids": matched_row_ids,
        "filter_lane_status": "version_compare_navigation_compare_filter_lane_preview_ready",
        "filter_lane_result_type": "owner_note_version_compare_navigation_compare_filter_lane_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    lane.update(_base_flags())
    return lane


def _build_filter_lanes(drawers: List[Dict[str, object]]) -> List[Dict[str, object]]:
    changed = [drawer for drawer in drawers if int(drawer.get("changed_compare_row_count") or 0) > 0]
    unchanged = [drawer for drawer in drawers if int(drawer.get("unchanged_compare_row_count") or 0) > 0]
    saved_view = [drawer for drawer in drawers if drawer.get("source_kind") == "saved_view_preset"]
    filter_preset = [drawer for drawer in drawers if drawer.get("source_kind") == "filter_preset"]
    reveal_blocked = [drawer for drawer in drawers if drawer.get("raw_evidence_reveal_allowed") is False]
    rollback_blocked = [drawer for drawer in drawers if drawer.get("rollback_allowed_now") is False]
    restore_blocked = [drawer for drawer in drawers if drawer.get("restore_allowed_now") is False]
    safe_preview = [drawer for drawer in drawers if drawer.get("simulated_only") is True and drawer.get("real_raw_evidence_revealed") is False]

    lane_defs = [
        ("all_compare_drawers", "All compare drawers", "all", drawers, "All version detail compare drawers."),
        ("saved_view_preset_drawers", "Saved view preset drawers", "source_kind", saved_view, "Only saved view preset version detail drawers."),
        ("filter_preset_drawers", "Filter preset drawers", "source_kind", filter_preset, "Only filter preset version detail drawers."),
        ("changed_compare_rows", "Changed compare rows", "change_state", changed, "Drawers with at least one changed compare row."),
        ("unchanged_compare_rows", "Unchanged compare rows", "change_state", unchanged, "Drawers with at least one unchanged compare row."),
        ("raw_reveal_blocked", "Raw reveal blocked", "safety", reveal_blocked, "Drawers where raw evidence reveal is blocked."),
        ("rollback_blocked", "Rollback blocked", "blocked_action", rollback_blocked, "Drawers where rollback remains blocked."),
        ("restore_blocked", "Restore blocked", "blocked_action", restore_blocked, "Drawers where restore remains blocked."),
        ("safe_preview_only", "Safe preview only", "safety", safe_preview, "Drawers that remain preview-only with no real reveal/write."),
    ]

    return [
        _build_filter_lane(
            lane_id=lane_id,
            label=label,
            filter_type=filter_type,
            drawers=drawers,
            matched_drawers=matched,
            sequence=idx,
            description=description,
        )
        for idx, (lane_id, label, filter_type, matched, description) in enumerate(lane_defs, start=1)
    ]


def _build_search_facet(
    facet_id: str,
    label: str,
    facet_type: str,
    values: List[Dict[str, object]],
    sequence: int,
) -> Dict[str, object]:
    facet = {
        "search_facet_preview_id": f"version_compare_navigation_search_facet_{_stable_hash((PACK_ID, facet_id, sequence), 18)}",
        "search_facet_id": facet_id,
        "label": label,
        "facet_type": facet_type,
        "sequence": int(sequence),
        "values": values,
        "value_count": len(values),
        "search_facet_status": "version_compare_navigation_compare_search_facet_preview_ready",
        "search_facet_result_type": "owner_note_version_compare_navigation_compare_search_facet_preview",
        "search_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    facet.update(_base_flags())
    return facet


def _value_item(value: str, count: int, drawer_ids: List[str]) -> Dict[str, object]:
    return {
        "value_id": _safe_text(value),
        "label": _safe_text(value).replace("_", " ").title(),
        "count": int(count),
        "matched_version_detail_drawer_ids": drawer_ids,
    }


def _build_search_facets(drawers: List[Dict[str, object]]) -> List[Dict[str, object]]:
    source_kind_map: Dict[str, List[str]] = {}
    status_map: Dict[str, List[str]] = {}
    field_map: Dict[str, Set[str]] = {}
    change_state_map: Dict[str, List[str]] = {"changed": [], "unchanged": []}
    safety_map: Dict[str, List[str]] = {"raw_reveal_blocked": [], "no_real_writes": []}

    for drawer in drawers:
        did = _drawer_id(drawer)
        source_kind_map.setdefault(_safe_text(drawer.get("source_kind")), []).append(did)
        status_map.setdefault(_safe_text(drawer.get("drawer_status")), []).append(did)

        if int(drawer.get("changed_compare_row_count") or 0) > 0:
            change_state_map["changed"].append(did)
        if int(drawer.get("unchanged_compare_row_count") or 0) > 0:
            change_state_map["unchanged"].append(did)

        if drawer.get("raw_evidence_reveal_allowed") is False:
            safety_map["raw_reveal_blocked"].append(did)
        if (
            drawer.get("real_version_written") is False
            and drawer.get("real_version_saved") is False
            and drawer.get("real_edit_persisted") is False
        ):
            safety_map["no_real_writes"].append(did)

        for field_id in _field_ids(drawer):
            field_map.setdefault(field_id, set()).add(did)

    source_values = [_value_item(key, len(ids), ids) for key, ids in sorted(source_kind_map.items())]
    status_values = [_value_item(key, len(ids), ids) for key, ids in sorted(status_map.items())]
    field_values = [_value_item(key, len(ids), sorted(ids)) for key, ids in sorted(field_map.items())]
    change_values = [_value_item(key, len(ids), ids) for key, ids in sorted(change_state_map.items()) if ids]
    safety_values = [_value_item(key, len(ids), ids) for key, ids in sorted(safety_map.items()) if ids]

    return [
        _build_search_facet("source_kind", "Source kind", "source_kind", source_values, 1),
        _build_search_facet("drawer_status", "Drawer status", "status", status_values, 2),
        _build_search_facet("field_id", "Field", "field", field_values, 3),
        _build_search_facet("change_state", "Change state", "change_state", change_values, 4),
        _build_search_facet("safety_state", "Safety state", "safety", safety_values, 5),
    ]


def _build_quick_filter_chip(lane: Dict[str, object], sequence: int) -> Dict[str, object]:
    chip = {
        "quick_filter_chip_id": f"version_compare_navigation_quick_filter_chip_{_stable_hash((PACK_ID, lane.get('filter_lane_id'), sequence), 18)}",
        "filter_lane_id": lane.get("filter_lane_id"),
        "label": lane.get("label"),
        "sequence": int(sequence),
        "matched_version_detail_drawer_count": lane.get("matched_version_detail_drawer_count"),
        "matched_compare_row_count": lane.get("matched_compare_row_count"),
        "chip_status": "version_compare_navigation_quick_filter_chip_preview_ready",
        "chip_result_type": "owner_note_version_compare_navigation_quick_filter_chip_preview",
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    chip.update(_base_flags())
    return chip


def _build_selected_filter_preview(lanes: List[Dict[str, object]], facets: List[Dict[str, object]]) -> Dict[str, object]:
    selected = next((lane for lane in lanes if lane.get("filter_lane_id") == "all_compare_drawers"), lanes[0] if lanes else {})

    preview = {
        "selected_filter_preview_id": f"version_compare_navigation_selected_filter_{_stable_hash(selected.get('filter_lane_id'), 18)}",
        "selected_filter_lane_id": selected.get("filter_lane_id"),
        "selected_filter_lane_preview_id": selected.get("filter_lane_preview_id"),
        "selected_search_query": "",
        "selected_search_facet_ids": [facet.get("search_facet_id") for facet in facets],
        "selected_version_detail_drawer_count": selected.get("matched_version_detail_drawer_count"),
        "selected_compare_row_count": selected.get("matched_compare_row_count"),
        "selected_version_detail_drawer_ids": selected.get("matched_version_detail_drawer_ids"),
        "selection_status": "version_compare_navigation_selected_compare_filter_preview_ready",
        "selection_result_type": "owner_note_version_compare_navigation_selected_compare_filter_preview",
        "filter_allowed_in_preview": True,
        "search_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "safe_preview_only": True,
    }
    preview.update(_base_flags())
    return preview


def _build_indexes(
    drawers: List[Dict[str, object]],
    lanes: List[Dict[str, object]],
    facets: List[Dict[str, object]],
    chips: List[Dict[str, object]],
) -> Dict[str, object]:
    indexes = {
        "filter_lanes_by_id": {},
        "filter_lanes_by_type": {},
        "search_facets_by_id": {},
        "search_facets_by_type": {},
        "quick_filter_chips_by_id": {},
        "quick_filter_chips_by_lane_id": {},
        "version_detail_drawers_by_filter_lane_id": {},
        "compare_rows_by_filter_lane_id": {},
        "drawer_search_text_by_id": {},
    }

    drawer_map = {_drawer_id(drawer): drawer for drawer in drawers}

    for lane in lanes:
        lane_id = lane.get("filter_lane_id")
        indexes["filter_lanes_by_id"][lane_id] = lane
        indexes["filter_lanes_by_type"].setdefault(lane.get("filter_type"), []).append(lane)
        indexes["version_detail_drawers_by_filter_lane_id"][lane_id] = [
            drawer_map.get(drawer_id)
            for drawer_id in lane.get("matched_version_detail_drawer_ids", [])
            if drawer_id in drawer_map
        ]
        indexes["compare_rows_by_filter_lane_id"][lane_id] = lane.get("matched_compare_row_ids", [])

    for facet in facets:
        indexes["search_facets_by_id"][facet.get("search_facet_id")] = facet
        indexes["search_facets_by_type"].setdefault(facet.get("facet_type"), []).append(facet)

    for chip in chips:
        indexes["quick_filter_chips_by_id"][chip.get("quick_filter_chip_id")] = chip
        indexes["quick_filter_chips_by_lane_id"][chip.get("filter_lane_id")] = chip

    for drawer in drawers:
        did = _drawer_id(drawer)
        text_parts = [
            drawer.get("source_kind"),
            drawer.get("source_id"),
            drawer.get("drawer_status"),
            " ".join(sorted(_field_ids(drawer))),
        ]
        indexes["drawer_search_text_by_id"][did] = " ".join(_safe_text(part) for part in text_parts).lower()

    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_compare_filter_v193_payload_cached() -> Dict[str, object]:
    pack_192 = _load_pack_192_payload(force_refresh=False)

    drawers = pack_192.get("version_detail_drawers", [])
    if not isinstance(drawers, list):
        drawers = []
    drawer_items = [drawer for drawer in drawers if isinstance(drawer, dict)]

    lanes = _build_filter_lanes(drawer_items)
    facets = _build_search_facets(drawer_items)
    chips = [_build_quick_filter_chip(lane, idx) for idx, lane in enumerate(lanes, start=1)]
    selected_preview = _build_selected_filter_preview(lanes, facets)
    indexes = _build_indexes(drawer_items, lanes, facets, chips)

    all_lane_matches = sum(int(lane.get("matched_version_detail_drawer_count") or 0) for lane in lanes)
    all_row_matches = sum(int(lane.get("matched_compare_row_count") or 0) for lane in lanes)

    readiness_checks = {
        "pack_192_ready": pack_192.get("status") == "ready",
        "has_version_detail_drawers": len(drawer_items) >= 15,
        "has_filter_lanes": len(lanes) == 9,
        "has_search_facets": len(facets) == 5,
        "has_quick_filter_chips": len(chips) == 9,
        "default_all_compare_lane_present": "all_compare_drawers" in {lane.get("filter_lane_id") for lane in lanes},
        "saved_view_lane_present": "saved_view_preset_drawers" in {lane.get("filter_lane_id") for lane in lanes},
        "filter_preset_lane_present": "filter_preset_drawers" in {lane.get("filter_lane_id") for lane in lanes},
        "changed_lane_present": "changed_compare_rows" in {lane.get("filter_lane_id") for lane in lanes},
        "safe_preview_lane_present": "safe_preview_only" in {lane.get("filter_lane_id") for lane in lanes},
        "all_filter_lanes_ready": all(lane.get("filter_lane_status") == "version_compare_navigation_compare_filter_lane_preview_ready" for lane in lanes),
        "all_search_facets_ready": all(facet.get("search_facet_status") == "version_compare_navigation_compare_search_facet_preview_ready" for facet in facets),
        "all_quick_chips_ready": all(chip.get("chip_status") == "version_compare_navigation_quick_filter_chip_preview_ready" for chip in chips),
        "selected_filter_preview_ready": selected_preview.get("selection_status") == "version_compare_navigation_selected_compare_filter_preview_ready",
        "filter_lane_indexes_present": bool(indexes.get("filter_lanes_by_id")),
        "search_facet_indexes_present": bool(indexes.get("search_facets_by_id")),
        "quick_chip_indexes_present": bool(indexes.get("quick_filter_chips_by_id")),
        "drawer_search_text_index_present": bool(indexes.get("drawer_search_text_by_id")),
        "has_lane_drawer_matches": all_lane_matches >= len(drawer_items),
        "has_lane_row_matches": all_row_matches >= int(pack_192.get("summary", {}).get("comparison_row_count") or 0),
        "all_simulated_only": all(item.get("simulated_only") is True for item in lanes + facets + chips),
        "all_filter_preview_only": all(item.get("filter_preview_only") is True for item in lanes + facets + chips),
        "all_search_facet_preview_only": all(item.get("search_facet_preview_only") is True for item in lanes + facets + chips),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in lanes + facets + chips),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in lanes + facets + chips),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in lanes + facets + chips),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in lanes + facets + chips),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in lanes + facets + chips),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in lanes + facets + chips),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in lanes + facets + chips),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in lanes + facets + chips),
        "all_drawer_selection_saves_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in lanes + facets + chips),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in lanes + facets + chips),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 193,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Compare Filter / Search Facets Preview",
        "endpoint": COMPARE_FILTER_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_192": {
            "status": pack_192.get("status"),
            "readiness_score": pack_192.get("summary", {}).get("readiness_score"),
            "version_detail_drawer_count": pack_192.get("summary", {}).get("version_detail_drawer_count"),
            "comparison_row_count": pack_192.get("summary", {}).get("comparison_row_count"),
            "changed_compare_row_count": pack_192.get("summary", {}).get("changed_compare_row_count"),
            "unchanged_compare_row_count": pack_192.get("summary", {}).get("unchanged_compare_row_count"),
        },
        "summary": {
            "filter_lane_count": len(lanes),
            "search_facet_count": len(facets),
            "quick_filter_chip_count": len(chips),
            "source_version_detail_drawer_count": len(drawer_items),
            "total_lane_drawer_match_count": all_lane_matches,
            "total_lane_compare_row_match_count": all_row_matches,
            "default_filter_lane_id": selected_preview.get("selected_filter_lane_id"),
            "selected_version_detail_drawer_count": selected_preview.get("selected_version_detail_drawer_count"),
            "selected_compare_row_count": selected_preview.get("selected_compare_row_count"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare navigation compare filter/search facets preview ready" if readiness_score == 100 else "Owner note version compare navigation compare filter/search facets preview needs review",
        },
        "readiness_checks": readiness_checks,
        "filter_lanes": lanes,
        "search_facets": facets,
        "quick_filter_chips": chips,
        "selected_filter_preview": selected_preview,
        "compare_filter_indexes": indexes,
    }


def build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_compare_filter_v193_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_compare_filter_v193_payload_cached())


def get_owner_note_vc_nav_compare_filter_v193_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_compare_filter_v193_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_compare_filter_v193_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 193,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "filter_lane_count": summary.get("filter_lane_count"),
        "search_facet_count": summary.get("search_facet_count"),
        "quick_filter_chip_count": summary.get("quick_filter_chip_count"),
        "source_version_detail_drawer_count": summary.get("source_version_detail_drawer_count"),
        "total_lane_drawer_match_count": summary.get("total_lane_drawer_match_count"),
        "total_lane_compare_row_match_count": summary.get("total_lane_compare_row_match_count"),
        "default_filter_lane_id": summary.get("default_filter_lane_id"),
        "selected_version_detail_drawer_count": summary.get("selected_version_detail_drawer_count"),
        "selected_compare_row_count": summary.get("selected_compare_row_count"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_compare_filter_v193_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_compare_filter_v193_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_compare_filter_v193_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_compare_filter_v193_status_bridge()

    action = {
        "id": "owner_note_vc_nav_compare_filter_v193",
        "label": "Owner Note Compare Filters",
        "title": "Owner Note Version Compare Navigation Compare Filter / Search Facets Preview",
        "href": COMPARE_FILTER_ENDPOINT,
        "endpoint": COMPARE_FILTER_ENDPOINT,
        "description": "Preview filter lanes, search facets, and quick chips for version detail compare drawers.",
        "status": bridge.get("status"),
        "pack": "Pack 193",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_compare_filter_v193_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_compare_filter_v193_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_compare_filter_v193",
        "title": "Owner Note Compare Filters",
        "subtitle": "Preview filter lanes, search facets, and quick filter chips for version compare drawers.",
        "status": payload.get("status"),
        "href": COMPARE_FILTER_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Filter readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "lanes", "title": "Filter lanes", "value": summary.get("filter_lane_count"), "label": "Compare filter lanes"},
            {"id": "facets", "title": "Search facets", "value": summary.get("search_facet_count"), "label": "Search facet groups"},
            {"id": "chips", "title": "Quick chips", "value": summary.get("quick_filter_chip_count"), "label": "Quick filter chips"},
            {"id": "selected", "title": "Selected rows", "value": summary.get("selected_compare_row_count"), "label": "Default selected compare rows"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("all_filter_preference_saves_blocked") and checks.get("all_drawer_selection_saves_blocked") else "Review", "label": "No filter preference/drawer selection write"},
        ],
    }
    section.update(_base_flags())
    return section


def build_owner_note_vc_nav_compare_filter_v193_html_section() -> str:
    section = build_owner_note_vc_nav_compare_filter_v193_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card owner-note-vc-nav-compare-filter-v193-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section owner-note-vc-nav-compare-filter-v193-section" id="owner-note-vc-nav-compare-filter-v193">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 193</p>
            <h2>{section.get('title', 'Owner Note Compare Filters')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{COMPARE_FILTER_ENDPOINT}">Open compare filter JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "COMPARE_FILTER_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_owner_note_vc_nav_compare_filter_v193_payload",
    "get_owner_note_vc_nav_compare_filter_v193_payload",
    "build_owner_note_vc_nav_compare_filter_v193_status_bridge",
    "get_owner_note_vc_nav_compare_filter_v193_status_bridge",
    "build_owner_note_vc_nav_compare_filter_v193_quick_action",
    "build_owner_note_vc_nav_compare_filter_v193_unified_owner_section",
    "build_owner_note_vc_nav_compare_filter_v193_html_section",
]
