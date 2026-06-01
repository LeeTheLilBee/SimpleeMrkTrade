
from __future__ import annotations
import copy, datetime, hashlib, importlib
from functools import lru_cache
from typing import Any, Dict, List

PACK_ID = "PACK_178"
VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json"
VERSION_DETAIL_COMPARE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json"

FILTER_LANE_DEFS = [
    {"filter_lane_id":"all_compare_drawers","label":"All Compare Drawers","filter_type":"all"},
    {"filter_lane_id":"default_saved_view","label":"Default Saved View","filter_type":"default_state","default_state":"default"},
    {"filter_lane_id":"not_default_saved_views","label":"Not Default","filter_type":"default_state","default_state":"not_default"},
    {"filter_lane_id":"critical_priority","label":"Critical Priority","filter_type":"priority","priority":"critical"},
    {"filter_lane_id":"high_priority","label":"High Priority","filter_type":"priority","priority":"high"},
    {"filter_lane_id":"standard_priority","label":"Standard Priority","filter_type":"priority","priority":"standard"},
    {"filter_lane_id":"monitor_priority","label":"Monitor Priority","filter_type":"priority","priority":"monitor"},
    {"filter_lane_id":"changed_fields_present","label":"Changed Fields","filter_type":"change_state","change_state":"changed"},
    {"filter_lane_id":"safe_preview_only","label":"Safe Preview Only","filter_type":"safety"},
]
QUICK_FILTER_IDS = ["all_compare_drawers","default_saved_view","critical_priority","high_priority","changed_fields_present","safe_preview_only"]

def _now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _hash(v, n=16):
    return hashlib.sha256(repr(v).encode()).hexdigest()[:n]

def _safe(v):
    s = str(v or "")
    bad = ["sk_live_","sk_test_","github_pat_","ghp_","xoxb-","aws_secret_access_key","private_key-----","broker_token_value","api_secret_value"]
    return "[REDACTED]" if any(b in s.lower() for b in bad) else s

def _priority_rank(p):
    return {"critical":1,"high":2,"medium":3,"standard":4,"monitor":5}.get(_safe(p), 99)

def _base_flags():
    return {
        "simulated_only": True,
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
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "persist_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
    }

def _count_by(items, key):
    out = {}
    for item in items:
        v = _safe(item.get(key)) or "unknown"
        out[v] = out.get(v, 0) + 1
    return out

def _load_177(force_refresh=False):
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_payload")
        payload = fn(force_refresh=force_refresh)
        if isinstance(payload, dict):
            return payload
    except Exception as exc:
        return {
            "status": "review",
            "error": str(exc),
            "summary": {"version_detail_drawer_count": 0, "comparison_row_count": 0, "readiness_score": 0},
            "version_detail_drawers": [],
        }
    return {"status": "review", "summary": {}, "version_detail_drawers": []}

def _sort_drawers(drawers):
    return sorted(
        [d for d in drawers if isinstance(d, dict)],
        key=lambda d: (0 if d.get("is_default") else 1, _priority_rank(d.get("view_priority")), _safe(d.get("saved_view_preset_id"))),
    )

def _nav_item(drawer, pos, total, ordered):
    prev_d = ordered[pos-2] if pos > 1 else None
    next_d = ordered[pos] if pos < total else None
    item = {
        "navigation_item_id": f"saved_view_preset_version_compare_nav_item_{_hash((drawer.get('version_detail_drawer_id'), pos))}",
        "position": pos,
        "total_count": total,
        "saved_view_preset_id": _safe(drawer.get("saved_view_preset_id")),
        "version_detail_drawer_id": _safe(drawer.get("version_detail_drawer_id")),
        "edit_history_timeline_id": _safe(drawer.get("edit_history_timeline_id")),
        "detail_edit_drawer_id": _safe(drawer.get("detail_edit_drawer_id")),
        "label": _safe(drawer.get("label")),
        "filter_lane_id": _safe(drawer.get("filter_lane_id")),
        "view_priority": _safe(drawer.get("view_priority")),
        "is_default": bool(drawer.get("is_default")),
        "drawer_status": _safe(drawer.get("drawer_status")),
        "comparison_row_count": int(drawer.get("comparison_row_count") or 0),
        "changed_field_count": int(drawer.get("changed_field_count") or 0),
        "unchanged_field_count": int(drawer.get("unchanged_field_count") or 0),
        "version_card_count": int(drawer.get("version_card_count") or 0),
        "field_change_event_count": int(drawer.get("field_change_event_count") or 0),
        "has_previous": prev_d is not None,
        "previous_version_detail_drawer_id": prev_d.get("version_detail_drawer_id") if isinstance(prev_d, dict) else None,
        "previous_saved_view_preset_id": prev_d.get("saved_view_preset_id") if isinstance(prev_d, dict) else None,
        "has_next": next_d is not None,
        "next_version_detail_drawer_id": next_d.get("version_detail_drawer_id") if isinstance(next_d, dict) else None,
        "next_saved_view_preset_id": next_d.get("saved_view_preset_id") if isinstance(next_d, dict) else None,
        "navigation_status": "saved_view_preset_version_compare_navigation_item_preview_ready",
        "navigation_result_type": "owner_note_saved_view_preset_version_compare_navigation_item_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    item.update(_base_flags())
    return item

def _matches(drawer, lane):
    t = lane.get("filter_type")
    if t == "all": return True
    if t == "default_state":
        return ("default" if drawer.get("is_default") else "not_default") == lane.get("default_state")
    if t == "priority":
        return _safe(drawer.get("view_priority")) == lane.get("priority")
    if t == "change_state":
        return int(drawer.get("changed_field_count") or 0) > 0
    if t == "safety":
        return drawer.get("simulated_only") is True and drawer.get("real_saved_view_written") is False
    return False

def _filter_lane(lane_def, drawers):
    matched = [d for d in drawers if _matches(d, lane_def)]
    lane = {
        "filter_lane_preview_id": f"saved_view_preset_version_compare_filter_lane_{_hash((lane_def.get('filter_lane_id'), len(matched)))}",
        "filter_lane_id": lane_def["filter_lane_id"],
        "label": lane_def["label"],
        "description": lane_def.get("description", lane_def["label"]),
        "filter_type": lane_def["filter_type"],
        "matched_drawer_count": len(matched),
        "matched_version_detail_drawer_ids": [d.get("version_detail_drawer_id") for d in matched],
        "matched_saved_view_preset_ids": [d.get("saved_view_preset_id") for d in matched],
        "default_selected_version_detail_drawer_id": matched[0].get("version_detail_drawer_id") if matched else None,
        "default_selected_saved_view_preset_id": matched[0].get("saved_view_preset_id") if matched else None,
        "lane_status": "saved_view_preset_version_compare_filter_lane_preview_ready",
        "lane_result_type": "owner_note_saved_view_preset_version_compare_filter_lane_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
    }
    lane.update(_base_flags())
    return lane

def _filter_lanes(drawers):
    lanes = [_filter_lane(ld, drawers) for ld in FILTER_LANE_DEFS]
    return {
        "filter_lanes_preview_id": f"saved_view_preset_version_compare_filter_lanes_{_hash([l['filter_lane_id'] for l in lanes])}",
        "filter_lanes": lanes,
        "filter_lane_count": len(lanes),
        "filter_lane_ids": [l["filter_lane_id"] for l in lanes],
        "filter_lane_index": {l["filter_lane_id"]: l for l in lanes},
        "default_filter_lane_id": "all_compare_drawers",
        "filter_status": "saved_view_preset_version_compare_filter_lanes_preview_ready",
        "filter_result_type": "owner_note_saved_view_preset_version_compare_filter_lanes_preview",
        "filter_allowed_in_preview": True,
        **_base_flags(),
    }

def _quick_chips(lanes_payload):
    idx = lanes_payload.get("filter_lane_index", {})
    chips = []
    for order, lane_id in enumerate(QUICK_FILTER_IDS, start=1):
        lane = idx.get(lane_id)
        if lane:
            chip = {
                "quick_filter_chip_id": f"saved_view_preset_version_compare_quick_filter_chip_{_hash((lane_id, order))}",
                "filter_lane_id": lane_id,
                "label": lane.get("label"),
                "order": order,
                "matched_drawer_count": lane.get("matched_drawer_count", 0),
                "chip_status": "saved_view_preset_version_compare_quick_filter_chip_preview_ready",
                "chip_result_type": "owner_note_saved_view_preset_version_compare_quick_filter_chip_preview",
                "filter_allowed_in_preview": True,
                "selection_allowed_in_preview": True,
            }
            chip.update(_base_flags())
            chips.append(chip)
    return {
        "quick_filter_chips_preview_id": f"saved_view_preset_version_compare_quick_filter_chips_{_hash([c['filter_lane_id'] for c in chips])}",
        "quick_filter_chips": chips,
        "quick_filter_chip_count": len(chips),
        "quick_filter_ids": [c["filter_lane_id"] for c in chips],
        "quick_filter_status": "saved_view_preset_version_compare_quick_filter_chips_preview_ready",
        "quick_filter_result_type": "owner_note_saved_view_preset_version_compare_quick_filter_chips_preview",
        **_base_flags(),
    }

def _grouped(nav_items):
    groups = {}
    for item in nav_items:
        key = _safe(item.get("view_priority")) or "unknown"
        groups.setdefault(key, {"group_id": f"priority_{key}", "group_key": key, "label": f"{key.title()} Priority", "navigation_items": [], "drawer_count": 0, "group_status": "saved_view_preset_version_compare_grouped_navigation_preview_ready"})
        groups[key]["navigation_items"].append(item)
        groups[key]["drawer_count"] += 1
        groups[key]["navigation_item_count"] = len(groups[key]["navigation_items"])
    return {
        "grouped_navigation_preview_id": f"saved_view_preset_version_compare_grouped_navigation_{_hash(list(groups.keys()))}",
        "groups": groups,
        "group_keys": list(groups.keys()),
        "group_count": len(groups),
        "grouped_navigation_status": "saved_view_preset_version_compare_grouped_navigation_preview_ready",
        "grouped_navigation_result_type": "owner_note_saved_view_preset_version_compare_grouped_navigation_preview",
        **_base_flags(),
    }

def _selected(nav_items, drawers_by_id):
    selected = nav_items[0] if nav_items else {}
    did = selected.get("version_detail_drawer_id")
    drawer = drawers_by_id.get(did, {}) if did else {}
    return {
        "selected_drawer_preview_id": f"saved_view_preset_version_compare_selected_drawer_preview_{_hash((did, selected.get('saved_view_preset_id')))}",
        "selected_navigation_item_id": selected.get("navigation_item_id"),
        "selected_version_detail_drawer_id": did,
        "selected_saved_view_preset_id": selected.get("saved_view_preset_id"),
        "selected_label": selected.get("label"),
        "selected_filter_lane_id": selected.get("filter_lane_id"),
        "selected_view_priority": selected.get("view_priority"),
        "selected_comparison_row_count": selected.get("comparison_row_count"),
        "selected_changed_field_count": selected.get("changed_field_count"),
        "selected_unchanged_field_count": selected.get("unchanged_field_count"),
        "selected_drawer_status": drawer.get("drawer_status"),
        "selection_status": "saved_view_preset_version_compare_selected_drawer_preview_ready",
        "selection_result_type": "owner_note_saved_view_preset_version_compare_selected_drawer_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        **_base_flags(),
    }

def _indexes(nav_items, lanes_payload):
    idx = {k: {} for k in ["by_navigation_item_id","by_version_detail_drawer_id","by_edit_history_timeline_id","by_detail_edit_drawer_id","by_saved_view_preset_id"]}
    idx.update({"by_filter_lane_id": {}, "by_view_priority": {}, "by_default_state": {}})
    for item in nav_items:
        idx["by_navigation_item_id"][item["navigation_item_id"]] = item
        idx["by_version_detail_drawer_id"][item["version_detail_drawer_id"]] = item
        idx["by_edit_history_timeline_id"][item["edit_history_timeline_id"]] = item
        idx["by_detail_edit_drawer_id"][item["detail_edit_drawer_id"]] = item
        idx["by_saved_view_preset_id"][item["saved_view_preset_id"]] = item
        idx["by_filter_lane_id"].setdefault(item["filter_lane_id"], []).append(item)
        idx["by_view_priority"].setdefault(item["view_priority"], []).append(item)
        idx["by_default_state"].setdefault("default" if item.get("is_default") else "not_default", []).append(item)
    for lane in lanes_payload.get("filter_lanes", []):
        idx["by_filter_lane_id"].setdefault(lane.get("filter_lane_id"), [])
    return idx

@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload_cached():
    source = _load_177(False)
    drawers = _sort_drawers(source.get("version_detail_drawers", []))
    drawers_by_id = {d.get("version_detail_drawer_id"): d for d in drawers}
    nav_items = [_nav_item(d, i, len(drawers), drawers) for i, d in enumerate(drawers, start=1)]
    lanes = _filter_lanes(drawers)
    chips = _quick_chips(lanes)
    grouped = _grouped(nav_items)
    selected = _selected(nav_items, drawers_by_id)
    indexes = _indexes(nav_items, lanes)

    total_changed = sum(i.get("changed_field_count", 0) for i in nav_items)
    total_unchanged = sum(i.get("unchanged_field_count", 0) for i in nav_items)
    expected_lanes = {x["filter_lane_id"] for x in FILTER_LANE_DEFS}

    checks = {
        "pack_177_ready": source.get("status") == "ready",
        "has_drawers": len(drawers) >= 1,
        "has_navigation_items": len(nav_items) >= 1,
        "navigation_count_matches_drawers": len(nav_items) == len(drawers),
        "has_filter_lanes": lanes.get("filter_lane_count") >= 9,
        "has_quick_filter_chips": chips.get("quick_filter_chip_count") == 6,
        "has_grouped_navigation": grouped.get("group_count", 0) >= 1,
        "has_selected_drawer_preview": bool(selected.get("selected_version_detail_drawer_id")),
        "all_simulated_only": all(i.get("simulated_only") is True for i in nav_items),
        "all_navigation_preview_only": all(i.get("navigation_preview_only") is True for i in nav_items),
        "all_filter_navigation_preview_only": all(i.get("filter_navigation_preview_only") is True for i in nav_items),
        "all_version_detail_preview_only": all(i.get("version_detail_preview_only") is True for i in nav_items),
        "all_compare_view_preview_only": all(i.get("compare_view_preview_only") is True for i in nav_items),
        "all_edit_history_preview_only": all(i.get("edit_history_preview_only") is True for i in nav_items),
        "all_version_preview_only": all(i.get("version_preview_only") is True for i in nav_items),
        "all_rollback_preview_only": all(i.get("rollback_preview_only") is True for i in nav_items),
        "all_saved_view_preset_detail_preview_only": all(i.get("saved_view_preset_detail_preview_only") is True for i in nav_items),
        "all_saved_view_preset_edit_preview_only": all(i.get("saved_view_preset_edit_preview_only") is True for i in nav_items),
        "all_saved_navigation_preview_only": all(i.get("saved_navigation_preview_only") is True for i in nav_items),
        "all_saved_filter_preset_preview_only": all(i.get("saved_filter_preset_preview_only") is True for i in nav_items),
        "all_saved_view_preview_only": all(i.get("saved_view_preview_only") is True for i in nav_items),
        "all_filter_preset_preview_only": all(i.get("filter_preset_preview_only") is True for i in nav_items),
        "no_real_navigation_state_persisted": all(i.get("real_navigation_state_persisted") is False for i in nav_items),
        "no_real_filter_preference_saved": all(i.get("real_filter_preference_saved") is False for i in nav_items),
        "no_real_drawer_selection_saved": all(i.get("real_drawer_selection_saved") is False for i in nav_items),
        "no_real_history_written": all(i.get("real_history_written") is False for i in nav_items),
        "no_real_version_written": all(i.get("real_version_written") is False for i in nav_items),
        "no_real_version_saved": all(i.get("real_version_saved") is False for i in nav_items),
        "no_real_rollback_executed": all(i.get("real_rollback_executed") is False for i in nav_items),
        "no_real_restore_executed": all(i.get("real_restore_executed") is False for i in nav_items),
        "no_real_edit_persisted": all(i.get("real_edit_persisted") is False for i in nav_items),
        "no_real_saved_view_written": all(i.get("real_saved_view_written") is False for i in nav_items),
        "no_real_user_preference_written": all(i.get("real_user_preference_written") is False for i in nav_items),
        "all_navigation_persistence_blocked": all(i.get("navigation_persistence_allowed_now") is False for i in nav_items),
        "all_filter_preference_save_blocked": all(i.get("filter_preference_save_allowed_now") is False for i in nav_items),
        "all_drawer_selection_save_blocked": all(i.get("drawer_selection_save_allowed_now") is False for i in nav_items),
        "all_restore_actions_blocked": all(i.get("restore_allowed_now") is False for i in nav_items),
        "all_rollback_actions_blocked": all(i.get("rollback_allowed_now") is False for i in nav_items),
        "all_save_actions_blocked": all(i.get("save_allowed_now") is False for i in nav_items),
        "all_persist_actions_blocked": all(i.get("persist_allowed_now") is False for i in nav_items),
        "all_history_writes_blocked": all(i.get("history_write_allowed_now") is False for i in nav_items),
        "all_version_writes_blocked": all(i.get("version_write_allowed_now") is False for i in nav_items),
        "all_raw_evidence_reveal_blocked": all(i.get("raw_evidence_reveal_allowed") is False for i in nav_items),
        "all_raw_evidence_lookup_blocked": all(i.get("raw_evidence_lookup_allowed") is False for i in nav_items),
        "all_navigation_item_ids_present": all(bool(i.get("navigation_item_id")) for i in nav_items),
        "all_drawer_ids_present": all(bool(i.get("version_detail_drawer_id")) for i in nav_items),
        "all_saved_view_preset_ids_present": all(bool(i.get("saved_view_preset_id")) for i in nav_items),
        "all_navigation_items_ready": all(i.get("navigation_status") == "saved_view_preset_version_compare_navigation_item_preview_ready" for i in nav_items),
        "navigation_preview_ready": True,
        "selected_drawer_preview_ready": selected.get("selection_status") == "saved_view_preset_version_compare_selected_drawer_preview_ready",
        "filter_lanes_ready": lanes.get("filter_status") == "saved_view_preset_version_compare_filter_lanes_preview_ready",
        "quick_filter_chips_ready": chips.get("quick_filter_status") == "saved_view_preset_version_compare_quick_filter_chips_preview_ready",
        "grouped_navigation_ready": grouped.get("grouped_navigation_status") == "saved_view_preset_version_compare_grouped_navigation_preview_ready",
        "all_expected_filter_lanes_present": expected_lanes.issubset(set(lanes.get("filter_lane_ids", []))),
        "all_quick_filters_present": set(QUICK_FILTER_IDS).issubset(set(chips.get("quick_filter_ids", []))),
        "all_compare_drawers_filter_present": "all_compare_drawers" in lanes.get("filter_lane_index", {}),
        "default_saved_view_filter_present": "default_saved_view" in lanes.get("filter_lane_index", {}),
        "critical_priority_filter_present": "critical_priority" in lanes.get("filter_lane_index", {}),
        "high_priority_filter_present": "high_priority" in lanes.get("filter_lane_index", {}),
        "changed_fields_filter_present": "changed_fields_present" in lanes.get("filter_lane_index", {}),
        "safe_preview_only_filter_present": "safe_preview_only" in lanes.get("filter_lane_index", {}),
        "has_previous_next_pointers": len(nav_items) <= 1 or (nav_items[0]["has_previous"] is False and nav_items[0]["has_next"] is True and nav_items[-1]["has_next"] is False and nav_items[-1]["has_previous"] is True),
        "cached_non_recursive": True,
    }
    score = 100 if all(v for v in checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 178,
        "status": "ready" if score == 100 else "review",
        "title": "Owner Note Saved View Preset Version Compare Filter / Drawer Navigation Preview",
        "endpoint": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "source_endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "generated_at": _now(),
        **_base_flags(),
        "source_pack_177": {
            "status": source.get("status"),
            "readiness_score": source.get("summary", {}).get("readiness_score"),
            "version_detail_drawer_count": source.get("summary", {}).get("version_detail_drawer_count"),
            "comparison_row_count": source.get("summary", {}).get("comparison_row_count"),
        },
        "summary": {
            "navigation_item_count": len(nav_items),
            "version_detail_drawer_count": len(drawers),
            "filter_lane_count": lanes.get("filter_lane_count"),
            "quick_filter_chip_count": chips.get("quick_filter_chip_count"),
            "group_count": grouped.get("group_count"),
            "comparison_row_count": sum(i.get("comparison_row_count", 0) for i in nav_items),
            "changed_field_count": total_changed,
            "unchanged_field_count": total_unchanged,
            "navigation_status_counts": _count_by(nav_items, "navigation_status"),
            "view_priority_counts": _count_by(nav_items, "view_priority"),
            "filter_lane_counts": _count_by(nav_items, "filter_lane_id"),
            "default_state_counts": {"default": len([i for i in nav_items if i.get("is_default")]), "not_default": len([i for i in nav_items if not i.get("is_default")])},
            "filter_lane_match_counts": {l.get("filter_lane_id"): l.get("matched_drawer_count") for l in lanes.get("filter_lanes", [])},
            "default_filter_lane_id": lanes.get("default_filter_lane_id"),
            "default_selected_drawer_id": selected.get("selected_version_detail_drawer_id"),
            "default_selected_saved_view_preset_id": selected.get("selected_saved_view_preset_id"),
            "readiness_score": score,
            "readiness_label": "Owner note saved view preset version compare filter/navigation preview ready" if score == 100 else "Owner note saved view preset version compare filter/navigation preview needs review",
        },
        "readiness_checks": checks,
        "filter_lane_definitions": FILTER_LANE_DEFS,
        "quick_filter_ids": QUICK_FILTER_IDS,
        "navigation_preview": {
            "navigation_preview_id": f"saved_view_preset_version_compare_navigation_{_hash([i.get('navigation_item_id') for i in nav_items])}",
            "navigation_items": nav_items,
            "navigation_item_count": len(nav_items),
            "first_navigation_item_id": nav_items[0].get("navigation_item_id") if nav_items else None,
            "last_navigation_item_id": nav_items[-1].get("navigation_item_id") if nav_items else None,
            "default_selected_navigation_item_id": nav_items[0].get("navigation_item_id") if nav_items else None,
            "default_selected_drawer_id": selected.get("selected_version_detail_drawer_id"),
            "default_selected_saved_view_preset_id": selected.get("selected_saved_view_preset_id"),
            "selected_drawer_preview": selected,
            "navigation_status": "saved_view_preset_version_compare_drawer_navigation_preview_ready",
            "navigation_result_type": "owner_note_saved_view_preset_version_compare_drawer_navigation_preview",
            **_base_flags(),
        },
        "filter_lanes_preview": lanes,
        "quick_filter_chips_preview": chips,
        "grouped_navigation_preview": grouped,
        "navigation_indexes": indexes,
    }

def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh=False):
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload_cached())

def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh=False):
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh)

def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge(force_refresh=False):
    p = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload(force_refresh)
    s = p.get("summary", {})
    return {
        "pack_id": PACK_ID,
        "pack_number": 178,
        "status": p.get("status"),
        "endpoint": p.get("endpoint"),
        "source_endpoint": p.get("source_endpoint"),
        "readiness_score": s.get("readiness_score"),
        "readiness_label": s.get("readiness_label"),
        "navigation_item_count": s.get("navigation_item_count"),
        "version_detail_drawer_count": s.get("version_detail_drawer_count"),
        "filter_lane_count": s.get("filter_lane_count"),
        "quick_filter_chip_count": s.get("quick_filter_chip_count"),
        "group_count": s.get("group_count"),
        "comparison_row_count": s.get("comparison_row_count"),
        "changed_field_count": s.get("changed_field_count"),
        "unchanged_field_count": s.get("unchanged_field_count"),
        "default_filter_lane_id": s.get("default_filter_lane_id"),
        "default_selected_drawer_id": s.get("default_selected_drawer_id"),
        "default_selected_saved_view_preset_id": s.get("default_selected_saved_view_preset_id"),
        **_base_flags(),
    }

def get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge(force_refresh=False):
    return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge(force_refresh)

def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_quick_action():
    b = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation",
        "label": "Owner Note Preset Compare Navigation",
        "title": "Owner Note Saved View Preset Version Compare Filter / Drawer Navigation Preview",
        "href": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "endpoint": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "description": "Preview saved view preset version compare navigation, filter lanes, quick filters, grouped navigation, selected drawer preview, and blocked persistence.",
        "status": b.get("status"),
        "pack": "Pack 178",
        "category": "policy",
        **_base_flags(),
    }

def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_owner_section():
    p = build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload()
    s = p.get("summary", {})
    checks = p.get("readiness_checks", {})
    return {
        "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation",
        "title": "Owner Note Preset Compare Navigation",
        "subtitle": "Preview saved view preset version compare navigation, filters, selected drawer, and blocked persistence.",
        "status": p.get("status"),
        "href": VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "cards": [
            {"id":"readiness","title":"Navigation readiness","value":s.get("readiness_score"),"label":s.get("readiness_label")},
            {"id":"items","title":"Navigation items","value":s.get("navigation_item_count"),"label":"Preset compare drawer links"},
            {"id":"lanes","title":"Filter lanes","value":s.get("filter_lane_count"),"label":"Drawer filter lanes"},
            {"id":"chips","title":"Quick filters","value":s.get("quick_filter_chip_count"),"label":"Quick filter chips"},
            {"id":"selected","title":"Selected drawer","value":s.get("default_selected_saved_view_preset_id"),"label":"Default selected preset"},
            {"id":"persist","title":"Navigation persistence","value":"Blocked" if checks.get("all_navigation_persistence_blocked") else "Review","label":"No real preference write"},
        ],
        **_base_flags(),
    }

def build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_html_section():
    return f'<section id="policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation"><h2>Owner Note Preset Compare Navigation</h2><a href="{VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT}">Open JSON</a></section>'

__all__ = [
    "PACK_ID",
    "VERSION_COMPARE_FILTER_NAVIGATION_ENDPOINT",
    "VERSION_DETAIL_COMPARE_ENDPOINT",
    "FILTER_LANE_DEFS",
    "QUICK_FILTER_IDS",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_payload",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge",
    "get_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_status_bridge",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_quick_action",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_html_section",
]
