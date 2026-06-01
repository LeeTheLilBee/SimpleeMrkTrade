
"""
PACK 173 - Owner Note Draft Version Compare Filter / Drawer Navigation Preview.

This module sits on top of Pack 172.

Pack 172 creates preview-only version detail drawer / compare view scaffolding.
Pack 173 creates preview-only filter/navigation scaffolding for compare drawers:
- drawer navigation list
- selected drawer preview
- previous/next drawer pointers
- filter lanes
- quick filter chips
- grouped drawer navigation
- blocked navigation persistence

Important:
- simulated-only
- navigation-preview-only
- filter-navigation-preview-only
- version-detail-preview-only
- compare-view-preview-only
- version-preview-only
- edit-history-preview-only
- rollback-preview-only
- compare-preview-only
- edit-preview-only
- detail-drawer-preview-only
- owner-note-preview-only
- review-draft-preview-only
- saved-view-preview-only
- filter-preset-preview-only
- filter-preview-only
- search-facet-preview-only
- lookup-preview-only
- detail-preview-only
- evidence-drawer-preview-only
- owner-review-preview-only
- queue-preview-only
- renewal-preview-only
- recheck-preview-only
- expiration-preview-only
- vault-preview-only
- index-preview-only
- receipt-preview-only
- approval-preview-only
- evidence-preview-only
- no real navigation state persisted
- no real filter preference saved
- no real drawer selection saved
- no real history/version writes
- no real rollback/restore
- no raw evidence revealed
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


PACK_ID = "PACK_173"
COMPARE_FILTER_NAVIGATION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"
VERSION_DETAIL_COMPARE_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json"


FILTER_LANES = {
    "all_compare_drawers": {
        "label": "All Compare Drawers",
        "description": "All owner note version compare drawers.",
        "filter_type": "all",
    },
    "owner_review_required": {
        "label": "Owner Review Required",
        "description": "Compare drawers tied to owner-review-required items.",
        "filter_type": "review_requirement",
        "requires_owner_review": True,
    },
    "owner_review_not_required": {
        "label": "No Owner Review Required",
        "description": "Monitor/safe drawers that do not require owner review.",
        "filter_type": "review_requirement",
        "requires_owner_review": False,
    },
    "critical_priority": {
        "label": "Critical Priority",
        "description": "Critical compare drawers first.",
        "filter_type": "priority",
        "draft_priority": "critical",
    },
    "high_priority": {
        "label": "High Priority",
        "description": "High-priority compare drawers.",
        "filter_type": "priority",
        "draft_priority": "high",
    },
    "medium_priority": {
        "label": "Medium Priority",
        "description": "Medium-priority renewal review drawers.",
        "filter_type": "priority",
        "draft_priority": "medium",
    },
    "monitor_priority": {
        "label": "Monitor Priority",
        "description": "Monitor-only compare drawers.",
        "filter_type": "priority",
        "draft_priority": "monitor",
    },
    "safe_preview_only": {
        "label": "Safe Preview Only",
        "description": "Safe preview-only compare drawers.",
        "filter_type": "saved_view",
        "saved_view_id": "safe_preview_only",
    },
}


QUICK_FILTERS = [
    "all_compare_drawers",
    "owner_review_required",
    "critical_priority",
    "high_priority",
    "monitor_priority",
    "safe_preview_only",
]


EXPECTED_FILTER_LANES = set(FILTER_LANES.keys())


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


def _load_pack_172_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_172",
            "status": "review",
            "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "version_preview_only": True,
            "edit_history_preview_only": True,
            "rollback_preview_only": True,
            "compare_preview_only": True,
            "edit_preview_only": True,
            "detail_drawer_preview_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "version_detail_drawer_count": 0,
                "comparison_row_count": 0,
                "changed_field_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 172 version detail compare payload unavailable",
            },
            "version_detail_drawers": [],
        }

    return {
        "pack_id": "PACK_172",
        "status": "review",
        "endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "simulated_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "summary": {
            "version_detail_drawer_count": 0,
            "comparison_row_count": 0,
            "changed_field_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 172 version detail compare payload unavailable",
        },
        "version_detail_drawers": [],
    }



def _priority_rank(priority: Any) -> int:
    ranking = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }
    return ranking.get(_safe_text(priority), 99)


def _sort_drawers_for_navigation(drawers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [drawer for drawer in drawers if isinstance(drawer, dict)],
        key=lambda drawer: (
            _priority_rank(drawer.get("draft_priority")),
            0 if drawer.get("requires_owner_review") else 1,
            _safe_text(drawer.get("saved_view_id")),
        ),
    )


def _build_drawer_navigation_item(drawer: Dict[str, Any], position: int, total_count: int) -> Dict[str, Any]:
    drawer = dict(drawer or {})

    identity = {
        "pack": PACK_ID,
        "drawer_id": drawer.get("version_detail_drawer_id"),
        "saved_view_id": drawer.get("saved_view_id"),
        "position": position,
    }

    nav_item_id = f"version_compare_drawer_nav_item_{_stable_hash(identity, 18)}"

    return {
        "navigation_item_id": nav_item_id,
        "position": int(position),
        "total_count": int(total_count),
        "version_detail_drawer_id": _safe_text(drawer.get("version_detail_drawer_id")),
        "edit_history_timeline_id": _safe_text(drawer.get("edit_history_timeline_id")),
        "owner_note_draft_id": _safe_text(drawer.get("owner_note_draft_id")),
        "saved_view_id": _safe_text(drawer.get("saved_view_id")),
        "label": _safe_text(drawer.get("label")),
        "description": _safe_text(drawer.get("description")),
        "draft_type": _safe_text(drawer.get("draft_type")),
        "draft_priority": _safe_text(drawer.get("draft_priority")),
        "requires_owner_review": bool(drawer.get("requires_owner_review", False)),
        "drawer_status": _safe_text(drawer.get("drawer_status")),
        "comparison_row_count": int(drawer.get("comparison_row_count") or 0),
        "changed_field_count": int(drawer.get("comparison_groups", {}).get("changed_fields", {}).get("count") or 0),
        "unchanged_field_count": int(drawer.get("comparison_groups", {}).get("unchanged_fields", {}).get("count") or 0),
        "navigation_status": "drawer_navigation_item_preview_ready",
        "navigation_result_type": "owner_note_version_compare_drawer_navigation_item_preview",
        "selected_by_default": position == 1,
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "save_allowed_now": False,
        "submit_allowed_now": False,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
    }


def _attach_previous_next_pointers(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    output = []
    total = len(items)

    for idx, item in enumerate(items):
        new_item = dict(item)
        previous_item = items[idx - 1] if idx > 0 else None
        next_item = items[idx + 1] if idx < total - 1 else None

        new_item["previous_navigation_item_id"] = previous_item.get("navigation_item_id") if previous_item else None
        new_item["previous_version_detail_drawer_id"] = previous_item.get("version_detail_drawer_id") if previous_item else None
        new_item["next_navigation_item_id"] = next_item.get("navigation_item_id") if next_item else None
        new_item["next_version_detail_drawer_id"] = next_item.get("version_detail_drawer_id") if next_item else None
        new_item["has_previous"] = previous_item is not None
        new_item["has_next"] = next_item is not None

        output.append(new_item)

    return output


def _build_navigation_items(drawers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sorted_drawers = _sort_drawers_for_navigation(drawers)
    total = len(sorted_drawers)

    items = [
        _build_drawer_navigation_item(drawer, position=idx, total_count=total)
        for idx, drawer in enumerate(sorted_drawers, start=1)
    ]

    return _attach_previous_next_pointers(items)


def _build_selected_drawer_preview(drawers: List[Dict[str, Any]], navigation_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    selected_item = next(
        (item for item in navigation_items if item.get("selected_by_default") is True),
        navigation_items[0] if navigation_items else {},
    )

    selected_drawer_id = selected_item.get("version_detail_drawer_id")
    selected_drawer = next(
        (drawer for drawer in drawers if drawer.get("version_detail_drawer_id") == selected_drawer_id),
        drawers[0] if drawers else {},
    )

    identity = {
        "pack": PACK_ID,
        "selected_drawer_id": selected_drawer_id,
        "navigation_item_id": selected_item.get("navigation_item_id"),
    }

    return {
        "selected_drawer_preview_id": f"version_compare_selected_drawer_preview_{_stable_hash(identity, 18)}",
        "selected_navigation_item_id": selected_item.get("navigation_item_id"),
        "selected_version_detail_drawer_id": selected_item.get("version_detail_drawer_id"),
        "selected_saved_view_id": selected_item.get("saved_view_id"),
        "selected_label": selected_item.get("label"),
        "selected_position": selected_item.get("position"),
        "total_count": selected_item.get("total_count", len(navigation_items)),
        "has_previous": selected_item.get("has_previous", False),
        "has_next": selected_item.get("has_next", False),
        "previous_navigation_item_id": selected_item.get("previous_navigation_item_id"),
        "previous_version_detail_drawer_id": selected_item.get("previous_version_detail_drawer_id"),
        "next_navigation_item_id": selected_item.get("next_navigation_item_id"),
        "next_version_detail_drawer_id": selected_item.get("next_version_detail_drawer_id"),
        "selected_drawer_summary": {
            "drawer_status": selected_drawer.get("drawer_status"),
            "draft_priority": selected_drawer.get("draft_priority"),
            "requires_owner_review": selected_drawer.get("requires_owner_review"),
            "comparison_row_count": selected_drawer.get("comparison_row_count"),
            "changed_field_count": selected_drawer.get("comparison_groups", {}).get("changed_fields", {}).get("count"),
            "unchanged_field_count": selected_drawer.get("comparison_groups", {}).get("unchanged_fields", {}).get("count"),
        },
        "selection_status": "selected_drawer_preview_ready",
        "selection_result_type": "owner_note_version_compare_selected_drawer_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_navigation_preview(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    navigation_items = _build_navigation_items(drawers)
    selected_preview = _build_selected_drawer_preview(drawers, navigation_items)

    return {
        "navigation_preview_id": f"version_compare_navigation_preview_{_stable_hash([item.get('navigation_item_id') for item in navigation_items], 18)}",
        "navigation_items": navigation_items,
        "navigation_item_count": len(navigation_items),
        "selected_drawer_preview": selected_preview,
        "first_navigation_item_id": navigation_items[0].get("navigation_item_id") if navigation_items else None,
        "last_navigation_item_id": navigation_items[-1].get("navigation_item_id") if navigation_items else None,
        "default_selected_navigation_item_id": selected_preview.get("selected_navigation_item_id"),
        "default_selected_drawer_id": selected_preview.get("selected_version_detail_drawer_id"),
        "navigation_status": "drawer_navigation_preview_ready",
        "navigation_result_type": "owner_note_version_compare_drawer_navigation_preview",
        "open_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "navigation_persistence_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "cached_non_recursive": True,
    }



def _drawer_matches_filter(drawer: Dict[str, Any], filter_lane: Dict[str, Any]) -> bool:
    drawer = dict(drawer or {})
    filter_lane = dict(filter_lane or {})

    filter_type = _safe_text(filter_lane.get("filter_type"))

    if filter_type == "all":
        return True

    if filter_type == "review_requirement":
        return bool(drawer.get("requires_owner_review", False)) is bool(filter_lane.get("requires_owner_review", False))

    if filter_type == "priority":
        return _safe_text(drawer.get("draft_priority")) == _safe_text(filter_lane.get("draft_priority"))

    if filter_type == "saved_view":
        return _safe_text(drawer.get("saved_view_id")) == _safe_text(filter_lane.get("saved_view_id"))

    return False


def _build_filter_lane(lane_id: str, lane_config: Dict[str, Any], drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    lane_config = dict(lane_config or {})
    matched_drawers = [
        drawer
        for drawer in drawers
        if _drawer_matches_filter(drawer, lane_config)
    ]

    matched_drawers = _sort_drawers_for_navigation(matched_drawers)

    matched_ids = [
        _safe_text(drawer.get("version_detail_drawer_id"))
        for drawer in matched_drawers
        if drawer.get("version_detail_drawer_id")
    ]

    selected_drawer = matched_drawers[0] if matched_drawers else {}

    identity = {
        "pack": PACK_ID,
        "lane_id": lane_id,
        "matched_ids": matched_ids,
    }

    return {
        "filter_lane_id": lane_id,
        "filter_lane_preview_id": f"version_compare_filter_lane_{_stable_hash(identity, 18)}",
        "label": _safe_text(lane_config.get("label")),
        "description": _safe_text(lane_config.get("description")),
        "filter_type": _safe_text(lane_config.get("filter_type")),
        "criteria": {
            key: value
            for key, value in lane_config.items()
            if key not in {"label", "description", "filter_type"}
        },
        "matched_drawer_count": len(matched_drawers),
        "matched_version_detail_drawer_ids": matched_ids,
        "default_selected_version_detail_drawer_id": _safe_text(selected_drawer.get("version_detail_drawer_id")),
        "default_selected_saved_view_id": _safe_text(selected_drawer.get("saved_view_id")),
        "lane_status": "filter_lane_preview_ready",
        "lane_result_type": "owner_note_version_compare_filter_lane_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "filter_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_filter_lanes(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    lanes = [
        _build_filter_lane(lane_id, lane_config, drawers)
        for lane_id, lane_config in FILTER_LANES.items()
    ]

    lane_index = {
        lane.get("filter_lane_id"): lane
        for lane in lanes
        if lane.get("filter_lane_id")
    }

    return {
        "filter_lanes_preview_id": f"version_compare_filter_lanes_{_stable_hash([lane.get('filter_lane_preview_id') for lane in lanes], 18)}",
        "filter_lanes": lanes,
        "filter_lane_count": len(lanes),
        "filter_lane_index": lane_index,
        "default_filter_lane_id": "all_compare_drawers",
        "filter_status": "filter_lanes_preview_ready",
        "filter_result_type": "owner_note_version_compare_filter_lanes_preview",
        "filter_allowed_in_preview": True,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "filter_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_quick_filter_chip(lane: Dict[str, Any], order: int) -> Dict[str, Any]:
    lane = dict(lane or {})
    lane_id = _safe_text(lane.get("filter_lane_id"))

    identity = {
        "pack": PACK_ID,
        "lane_id": lane_id,
        "order": order,
        "matched_count": lane.get("matched_drawer_count"),
    }

    return {
        "quick_filter_chip_id": f"version_compare_quick_filter_chip_{_stable_hash(identity, 18)}",
        "filter_lane_id": lane_id,
        "label": _safe_text(lane.get("label")),
        "order": int(order),
        "matched_drawer_count": int(lane.get("matched_drawer_count") or 0),
        "default_selected_version_detail_drawer_id": _safe_text(lane.get("default_selected_version_detail_drawer_id")),
        "chip_status": "quick_filter_chip_preview_ready",
        "chip_result_type": "owner_note_version_compare_quick_filter_chip_preview",
        "filter_allowed_in_preview": True,
        "filter_preference_save_allowed_now": False,
        "real_filter_preference_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "filter_preview_only": True,
    }


def _build_quick_filter_chips(filter_lanes_payload: Dict[str, Any]) -> Dict[str, Any]:
    lane_index = filter_lanes_payload.get("filter_lane_index", {})
    chips = []

    for order, lane_id in enumerate(QUICK_FILTERS, start=1):
        lane = lane_index.get(lane_id, {})
        if lane:
            chips.append(_build_quick_filter_chip(lane, order=order))

    return {
        "quick_filter_chips_preview_id": f"version_compare_quick_filter_chips_{_stable_hash([chip.get('quick_filter_chip_id') for chip in chips], 18)}",
        "quick_filter_chips": chips,
        "quick_filter_chip_count": len(chips),
        "quick_filter_ids": [chip.get("filter_lane_id") for chip in chips],
        "quick_filter_status": "quick_filter_chips_preview_ready",
        "quick_filter_result_type": "owner_note_version_compare_quick_filter_chips_preview",
        "filter_allowed_in_preview": True,
        "filter_preference_save_allowed_now": False,
        "real_filter_preference_saved": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "filter_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_grouped_navigation(drawers: List[Dict[str, Any]]) -> Dict[str, Any]:
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for drawer in _sort_drawers_for_navigation(drawers):
        priority = _safe_text(drawer.get("draft_priority")) or "unknown"
        groups.setdefault(priority, []).append(drawer)

    group_payloads = {}
    for priority, group_drawers in groups.items():
        navigation_items = _build_navigation_items(group_drawers)
        group_payloads[priority] = {
            "group_id": f"priority_{priority}",
            "label": f"{priority.title()} Priority",
            "drawer_count": len(group_drawers),
            "navigation_items": navigation_items,
            "navigation_item_count": len(navigation_items),
            "group_status": "grouped_navigation_preview_ready",
        }

    return {
        "grouped_navigation_preview_id": f"version_compare_grouped_navigation_{_stable_hash(sorted(group_payloads.keys()), 18)}",
        "groups": group_payloads,
        "group_count": len(group_payloads),
        "group_keys": sorted(group_payloads.keys(), key=_priority_rank),
        "grouped_navigation_status": "grouped_navigation_preview_ready",
        "grouped_navigation_result_type": "owner_note_version_compare_grouped_navigation_preview",
        "navigation_persistence_allowed_now": False,
        "real_navigation_state_persisted": False,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "cached_non_recursive": True,
    }



def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_navigation_indexes(
    navigation_items: List[Dict[str, Any]],
    filter_lanes_payload: Dict[str, Any],
) -> Dict[str, Any]:
    indexes = {
        "by_navigation_item_id": {},
        "by_version_detail_drawer_id": {},
        "by_owner_note_draft_id": {},
        "by_saved_view_id": {},
        "by_draft_type": {},
        "by_draft_priority": {},
        "by_requires_owner_review": {},
        "by_filter_lane_id": {},
    }

    for item in navigation_items:
        nav_id = _safe_text(item.get("navigation_item_id"))
        if nav_id:
            indexes["by_navigation_item_id"][nav_id] = item

        drawer_id = _safe_text(item.get("version_detail_drawer_id"))
        if drawer_id:
            indexes["by_version_detail_drawer_id"][drawer_id] = item

        draft_id = _safe_text(item.get("owner_note_draft_id"))
        if draft_id:
            indexes["by_owner_note_draft_id"][draft_id] = item

        saved_view_id = _safe_text(item.get("saved_view_id")) or "unknown"
        indexes["by_saved_view_id"][saved_view_id] = item

        draft_type = _safe_text(item.get("draft_type")) or "unknown"
        indexes["by_draft_type"].setdefault(draft_type, []).append(item)

        priority = _safe_text(item.get("draft_priority")) or "unknown"
        indexes["by_draft_priority"].setdefault(priority, []).append(item)

        review_key = "owner_review_required" if item.get("requires_owner_review") else "owner_review_not_required"
        indexes["by_requires_owner_review"].setdefault(review_key, []).append(item)

    for lane in filter_lanes_payload.get("filter_lanes", []):
        if isinstance(lane, dict) and lane.get("filter_lane_id"):
            indexes["by_filter_lane_id"][lane.get("filter_lane_id")] = lane

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload_cached() -> Dict[str, Any]:
    pack_172_payload = _load_pack_172_payload(force_refresh=False)
    drawers = pack_172_payload.get("version_detail_drawers", [])

    if not isinstance(drawers, list):
        drawers = []

    sorted_drawers = _sort_drawers_for_navigation(drawers)
    navigation_preview = _build_navigation_preview(sorted_drawers)
    filter_lanes_payload = _build_filter_lanes(sorted_drawers)
    quick_filter_chips_payload = _build_quick_filter_chips(filter_lanes_payload)
    grouped_navigation = _build_grouped_navigation(sorted_drawers)

    navigation_items = navigation_preview.get("navigation_items", [])
    filter_lanes = filter_lanes_payload.get("filter_lanes", [])
    quick_filter_chips = quick_filter_chips_payload.get("quick_filter_chips", [])

    indexes = _build_navigation_indexes(navigation_items, filter_lanes_payload)

    draft_type_counts = _count_by(navigation_items, "draft_type")
    draft_priority_counts = _count_by(navigation_items, "draft_priority")
    navigation_status_counts = _count_by(navigation_items, "navigation_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([item for item in navigation_items if item.get("requires_owner_review") is True]),
        "owner_review_not_required": len([item for item in navigation_items if item.get("requires_owner_review") is False]),
    }

    filter_lane_match_counts = {
        lane.get("filter_lane_id"): lane.get("matched_drawer_count", 0)
        for lane in filter_lanes
        if isinstance(lane, dict)
    }

    readiness_checks = {
        "pack_172_ready": pack_172_payload.get("status") == "ready",
        "has_drawers": len(drawers) >= 1,
        "has_navigation_items": len(navigation_items) >= 1,
        "navigation_count_matches_drawers": len(navigation_items) == len(drawers),
        "has_filter_lanes": len(filter_lanes) >= len(FILTER_LANES),
        "has_quick_filter_chips": len(quick_filter_chips) == len(QUICK_FILTERS),
        "has_grouped_navigation": grouped_navigation.get("group_count", 0) >= 1,
        "all_simulated_only": all(item.get("simulated_only") is True for item in navigation_items),
        "all_navigation_preview_only": all(item.get("navigation_preview_only") is True for item in navigation_items),
        "all_filter_navigation_preview_only": all(item.get("filter_navigation_preview_only") is True for item in navigation_items),
        "all_version_detail_preview_only": all(item.get("version_detail_preview_only") is True for item in navigation_items),
        "all_compare_view_preview_only": all(item.get("compare_view_preview_only") is True for item in navigation_items),
        "all_version_preview_only": all(item.get("version_preview_only") is True for item in navigation_items),
        "all_edit_history_preview_only": all(item.get("edit_history_preview_only") is True for item in navigation_items),
        "all_rollback_preview_only": all(item.get("rollback_preview_only") is True for item in navigation_items),
        "all_compare_preview_only": all(item.get("compare_preview_only") is True for item in navigation_items),
        "all_edit_preview_only": all(item.get("edit_preview_only") is True for item in navigation_items),
        "all_detail_drawer_preview_only": all(item.get("detail_drawer_preview_only") is True for item in navigation_items),
        "all_owner_note_preview_only": all(item.get("owner_note_preview_only") is True for item in navigation_items),
        "all_review_draft_preview_only": all(item.get("review_draft_preview_only") is True for item in navigation_items),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in navigation_items),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in navigation_items),
        "all_filter_preview_only": all(item.get("filter_preview_only") is True for item in navigation_items),
        "all_search_facet_preview_only": all(item.get("search_facet_preview_only") is True for item in navigation_items),
        "all_lookup_preview_only": all(item.get("lookup_preview_only") is True for item in navigation_items),
        "all_detail_preview_only": all(item.get("detail_preview_only") is True for item in navigation_items),
        "all_evidence_drawer_preview_only": all(item.get("evidence_drawer_preview_only") is True for item in navigation_items),
        "all_owner_review_preview_only": all(item.get("owner_review_preview_only") is True for item in navigation_items),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in navigation_items),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in navigation_items),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in navigation_items),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in navigation_items),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in navigation_items),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in navigation_items),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in navigation_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in navigation_items),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in navigation_items),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in navigation_items),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in navigation_items),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in navigation_items),
        "no_real_history_written": all(item.get("real_history_written") is False for item in navigation_items),
        "no_real_version_written": all(item.get("real_version_written") is False for item in navigation_items),
        "no_real_version_saved": all(item.get("real_version_saved") is False for item in navigation_items),
        "no_real_rollback_executed": all(item.get("real_rollback_executed") is False for item in navigation_items),
        "no_real_restore_executed": all(item.get("real_restore_executed") is False for item in navigation_items),
        "no_real_edit_persisted": all(item.get("real_edit_persisted") is False for item in navigation_items),
        "no_real_note_written": all(item.get("real_note_written") is False for item in navigation_items),
        "no_real_draft_saved": all(item.get("real_draft_saved") is False for item in navigation_items),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in navigation_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in navigation_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in navigation_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in navigation_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in navigation_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in navigation_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in navigation_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in navigation_items),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in navigation_items),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in navigation_items),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in navigation_items),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in navigation_items),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in navigation_items),
        "no_real_owner_review_completed": all(item.get("real_owner_review_completed") is False for item in navigation_items),
        "no_real_owner_approval_executed": all(item.get("real_owner_approval_executed") is False for item in navigation_items),
        "no_real_owner_rejection_executed": all(item.get("real_owner_rejection_executed") is False for item in navigation_items),
        "no_real_owner_acknowledgement_executed": all(item.get("real_owner_acknowledgement_executed") is False for item in navigation_items),
        "no_real_evidence_revealed": all(item.get("real_evidence_revealed") is False for item in navigation_items),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in navigation_items),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in navigation_items),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in navigation_items),
        "all_filter_preference_save_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in navigation_items),
        "all_drawer_selection_save_blocked": all(item.get("drawer_selection_save_allowed_now") is False for item in navigation_items),
        "all_restore_actions_blocked": all(item.get("restore_allowed_now") is False for item in navigation_items),
        "all_rollback_actions_blocked": all(item.get("rollback_allowed_now") is False for item in navigation_items),
        "all_save_actions_blocked": all(item.get("save_allowed_now") is False for item in navigation_items),
        "all_submit_actions_blocked": all(item.get("submit_allowed_now") is False for item in navigation_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in navigation_items),
        "all_raw_evidence_lookup_blocked": all(item.get("raw_evidence_lookup_allowed") is False for item in navigation_items),
        "all_navigation_item_ids_present": all(bool(item.get("navigation_item_id")) for item in navigation_items),
        "all_drawer_ids_present": all(bool(item.get("version_detail_drawer_id")) for item in navigation_items),
        "all_owner_note_draft_ids_present": all(bool(item.get("owner_note_draft_id")) for item in navigation_items),
        "all_saved_view_ids_present": all(bool(item.get("saved_view_id")) for item in navigation_items),
        "all_navigation_items_ready": all(item.get("navigation_status") == "drawer_navigation_item_preview_ready" for item in navigation_items),
        "navigation_preview_ready": navigation_preview.get("navigation_status") == "drawer_navigation_preview_ready",
        "selected_drawer_preview_ready": navigation_preview.get("selected_drawer_preview", {}).get("selection_status") == "selected_drawer_preview_ready",
        "filter_lanes_ready": filter_lanes_payload.get("filter_status") == "filter_lanes_preview_ready",
        "quick_filter_chips_ready": quick_filter_chips_payload.get("quick_filter_status") == "quick_filter_chips_preview_ready",
        "grouped_navigation_ready": grouped_navigation.get("grouped_navigation_status") == "grouped_navigation_preview_ready",
        "all_expected_filter_lanes_present": EXPECTED_FILTER_LANES.issubset(set(filter_lanes_payload.get("filter_lane_index", {}).keys())),
        "all_quick_filters_present": set(QUICK_FILTERS).issubset(set(quick_filter_chips_payload.get("quick_filter_ids", []))),
        "all_compare_drawers_filter_present": filter_lane_match_counts.get("all_compare_drawers", 0) == len(drawers),
        "owner_review_required_filter_present": "owner_review_required" in filter_lane_match_counts,
        "critical_priority_filter_present": "critical_priority" in filter_lane_match_counts,
        "high_priority_filter_present": "high_priority" in filter_lane_match_counts,
        "monitor_priority_filter_present": "monitor_priority" in filter_lane_match_counts,
        "safe_preview_only_filter_present": "safe_preview_only" in filter_lane_match_counts,
        "has_previous_next_pointers": any(item.get("has_next") for item in navigation_items) and any(item.get("has_previous") for item in navigation_items),
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value
        for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 173,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Draft Version Compare Filter / Drawer Navigation Preview",
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "source_endpoint": VERSION_DETAIL_COMPARE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
        "source_pack_172": {
            "status": pack_172_payload.get("status"),
            "readiness_score": pack_172_payload.get("summary", {}).get("readiness_score"),
            "version_detail_drawer_count": pack_172_payload.get("summary", {}).get("version_detail_drawer_count"),
            "comparison_row_count": pack_172_payload.get("summary", {}).get("comparison_row_count"),
            "changed_field_count": pack_172_payload.get("summary", {}).get("changed_field_count"),
        },
        "summary": {
            "navigation_item_count": len(navigation_items),
            "version_detail_drawer_count": len(drawers),
            "filter_lane_count": len(filter_lanes),
            "quick_filter_chip_count": len(quick_filter_chips),
            "group_count": grouped_navigation.get("group_count", 0),
            "draft_type_counts": draft_type_counts,
            "draft_priority_counts": draft_priority_counts,
            "navigation_status_counts": navigation_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "filter_lane_match_counts": filter_lane_match_counts,
            "default_filter_lane_id": filter_lanes_payload.get("default_filter_lane_id"),
            "default_selected_drawer_id": navigation_preview.get("default_selected_drawer_id"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note version compare filter/navigation preview ready" if readiness_score == 100 else "Owner note version compare filter/navigation preview needs review",
        },
        "readiness_checks": readiness_checks,
        "filter_lanes_schema": FILTER_LANES,
        "quick_filters_schema": QUICK_FILTERS,
        "navigation_preview": navigation_preview,
        "filter_lanes_preview": filter_lanes_payload,
        "quick_filter_chips_preview": quick_filter_chips_payload,
        "grouped_navigation_preview": grouped_navigation,
        "navigation_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload_cached())


def get_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 173,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", COMPARE_FILTER_NAVIGATION_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", VERSION_DETAIL_COMPARE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note version compare filter/navigation preview ready"),
        "navigation_item_count": summary.get("navigation_item_count", 0),
        "version_detail_drawer_count": summary.get("version_detail_drawer_count", 0),
        "filter_lane_count": summary.get("filter_lane_count", 0),
        "quick_filter_chip_count": summary.get("quick_filter_chip_count", 0),
        "group_count": summary.get("group_count", 0),
        "draft_type_counts": summary.get("draft_type_counts", {}),
        "draft_priority_counts": summary.get("draft_priority_counts", {}),
        "navigation_status_counts": summary.get("navigation_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "filter_lane_match_counts": summary.get("filter_lane_match_counts", {}),
        "default_filter_lane_id": summary.get("default_filter_lane_id"),
        "default_selected_drawer_id": summary.get("default_selected_drawer_id"),
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_navigation_state_persisted": False,
        "real_filter_preference_saved": False,
        "real_drawer_selection_saved": False,
        "real_history_written": False,
        "real_version_written": False,
        "real_version_saved": False,
        "real_rollback_executed": False,
        "real_restore_executed": False,
        "real_edit_persisted": False,
        "real_note_written": False,
        "real_draft_saved": False,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "real_evidence_revealed": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation",
        "label": "Owner Note Compare Navigation",
        "title": "Owner Note Draft Version Compare Filter / Drawer Navigation Preview",
        "href": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "description": "Preview compare drawer navigation, filter lanes, quick filters, selected drawer preview, and blocked navigation persistence.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 173",
        "category": "policy",
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "navigation_readiness",
            "title": "Navigation readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note version compare filter/navigation preview ready"),
        },
        {
            "id": "navigation_items",
            "title": "Navigation items",
            "value": summary.get("navigation_item_count", 0),
            "label": "Compare drawers in navigation",
        },
        {
            "id": "filter_lanes",
            "title": "Filter lanes",
            "value": summary.get("filter_lane_count", 0),
            "label": "Preview filter lanes",
        },
        {
            "id": "quick_filters",
            "title": "Quick filters",
            "value": summary.get("quick_filter_chip_count", 0),
            "label": "Filter chips ready",
        },
        {
            "id": "selected_drawer",
            "title": "Selected drawer",
            "value": "Ready" if checks.get("selected_drawer_preview_ready") else "Review",
            "label": "Default drawer preview",
        },
        {
            "id": "navigation_persistence",
            "title": "Navigation persistence",
            "value": "Blocked" if checks.get("all_navigation_persistence_blocked") else "Review",
            "label": "No real preference save",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation",
        "title": "Owner Note Compare Navigation",
        "subtitle": "Preview compare drawer navigation, filter lanes, quick filters, grouped navigation, selected drawer preview, and blocked state persistence.",
        "status": payload.get("status", "ready"),
        "href": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "version_preview_only": True,
        "edit_history_preview_only": True,
        "rollback_preview_only": True,
        "compare_preview_only": True,
        "edit_preview_only": True,
        "detail_drawer_preview_only": True,
        "owner_note_preview_only": True,
        "review_draft_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
        "lookup_preview_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
        "owner_review_preview_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-compare-navigation-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-compare-navigation-section" id="policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 173</p>
            <h2>{section.get('title', 'Owner Note Compare Navigation')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{COMPARE_FILTER_NAVIGATION_ENDPOINT}">Open owner note compare navigation JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "COMPARE_FILTER_NAVIGATION_ENDPOINT",
    "VERSION_DETAIL_COMPARE_ENDPOINT",
    "FILTER_LANES",
    "QUICK_FILTERS",
    "EXPECTED_FILTER_LANES",
    "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload",
    "get_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload",
    "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge",
    "get_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_status_bridge",
    "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_quick_action",
    "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_html_section",
]
