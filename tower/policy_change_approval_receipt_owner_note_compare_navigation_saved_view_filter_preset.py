
"""
PACK 174 - Owner Note Compare Navigation Saved View / Filter Preset Preview.

This module sits on top of Pack 173.

Pack 173 creates preview-only filter/navigation scaffolding for compare drawers.
Pack 174 creates preview-only saved navigation/filter preset scaffolding:
- saved filter views
- saved navigation views
- preset chips
- default saved view selection
- preset detail previews
- blocked preference persistence

Important:
- simulated-only
- saved-navigation-preview-only
- saved-filter-preset-preview-only
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
- no real saved view written
- no real user preference written
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


PACK_ID = "PACK_174"
SAVED_VIEW_FILTER_PRESET_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json"
COMPARE_FILTER_NAVIGATION_ENDPOINT = "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json"


SAVED_VIEW_PRESETS = {
    "default_all_compare_drawers": {
        "label": "All Compare Drawers",
        "description": "Default view showing every owner note compare drawer.",
        "filter_lane_id": "all_compare_drawers",
        "is_default": True,
        "view_priority": "standard",
    },
    "owner_review_focus": {
        "label": "Owner Review Focus",
        "description": "Owner-review-required compare drawers for active decision review.",
        "filter_lane_id": "owner_review_required",
        "is_default": False,
        "view_priority": "high",
    },
    "critical_priority_focus": {
        "label": "Critical Priority Focus",
        "description": "Critical priority compare drawers only.",
        "filter_lane_id": "critical_priority",
        "is_default": False,
        "view_priority": "critical",
    },
    "high_priority_focus": {
        "label": "High Priority Focus",
        "description": "High priority compare drawers only.",
        "filter_lane_id": "high_priority",
        "is_default": False,
        "view_priority": "high",
    },
    "monitor_only_focus": {
        "label": "Monitor Only Focus",
        "description": "Monitor-only compare drawers.",
        "filter_lane_id": "monitor_priority",
        "is_default": False,
        "view_priority": "monitor",
    },
    "safe_preview_focus": {
        "label": "Safe Preview Focus",
        "description": "Safe preview-only compare drawer.",
        "filter_lane_id": "safe_preview_only",
        "is_default": False,
        "view_priority": "standard",
    },
}


EXPECTED_SAVED_VIEW_PRESETS = set(SAVED_VIEW_PRESETS.keys())


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


def _load_pack_173_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_173",
            "status": "review",
            "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "navigation_item_count": 0,
                "filter_lane_count": 0,
                "quick_filter_chip_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 173 compare filter/navigation payload unavailable",
            },
            "navigation_preview": {"navigation_items": []},
            "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
            "quick_filter_chips_preview": {"quick_filter_chips": []},
        }

    return {
        "pack_id": "PACK_173",
        "status": "review",
        "endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
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
        "summary": {
            "navigation_item_count": 0,
            "filter_lane_count": 0,
            "quick_filter_chip_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 173 compare filter/navigation payload unavailable",
        },
        "navigation_preview": {"navigation_items": []},
        "filter_lanes_preview": {"filter_lanes": [], "filter_lane_index": {}},
        "quick_filter_chips_preview": {"quick_filter_chips": []},
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


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _get_filter_lane(pack_173_payload: Dict[str, Any], filter_lane_id: str) -> Dict[str, Any]:
    lanes = pack_173_payload.get("filter_lanes_preview", {}).get("filter_lane_index", {})
    lane = lanes.get(filter_lane_id, {})
    return lane if isinstance(lane, dict) else {}


def _build_saved_view_preset(preset_id: str, preset_config: Dict[str, Any], pack_173_payload: Dict[str, Any]) -> Dict[str, Any]:
    preset_config = dict(preset_config or {})
    filter_lane_id = _safe_text(preset_config.get("filter_lane_id"))
    lane = _get_filter_lane(pack_173_payload, filter_lane_id)

    matched_ids = lane.get("matched_version_detail_drawer_ids", [])
    if not isinstance(matched_ids, list):
        matched_ids = []

    identity = {
        "pack": PACK_ID,
        "preset_id": preset_id,
        "filter_lane_id": filter_lane_id,
        "matched_ids": matched_ids,
    }

    return {
        "saved_view_preset_id": preset_id,
        "saved_view_preset_preview_id": f"owner_note_compare_saved_view_preset_{_stable_hash(identity, 18)}",
        "label": _safe_text(preset_config.get("label")),
        "description": _safe_text(preset_config.get("description")),
        "filter_lane_id": filter_lane_id,
        "filter_lane_label": _safe_text(lane.get("label")),
        "view_priority": _safe_text(preset_config.get("view_priority")),
        "is_default": bool(preset_config.get("is_default", False)),
        "matched_drawer_count": int(lane.get("matched_drawer_count") or 0),
        "matched_version_detail_drawer_ids": matched_ids,
        "default_selected_version_detail_drawer_id": _safe_text(lane.get("default_selected_version_detail_drawer_id")),
        "default_selected_saved_view_id": _safe_text(lane.get("default_selected_saved_view_id")),
        "preset_status": "saved_view_filter_preset_preview_ready",
        "preset_result_type": "owner_note_compare_navigation_saved_view_filter_preset_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "preset_detail_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
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
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
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
    }


def _build_saved_view_presets(pack_173_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    presets = [
        _build_saved_view_preset(preset_id, preset_config, pack_173_payload)
        for preset_id, preset_config in SAVED_VIEW_PRESETS.items()
    ]
    return sorted(
        presets,
        key=lambda item: (
            0 if item.get("is_default") else 1,
            _priority_rank(item.get("view_priority")),
            _safe_text(item.get("saved_view_preset_id")),
        ),
    )


def _build_preset_chip(preset: Dict[str, Any], order: int) -> Dict[str, Any]:
    preset = dict(preset or {})
    identity = {
        "pack": PACK_ID,
        "preset_id": preset.get("saved_view_preset_id"),
        "order": order,
    }

    return {
        "preset_chip_id": f"owner_note_compare_preset_chip_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
        "label": _safe_text(preset.get("label")),
        "order": int(order),
        "is_default": bool(preset.get("is_default", False)),
        "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
        "matched_drawer_count": int(preset.get("matched_drawer_count") or 0),
        "chip_status": "saved_view_preset_chip_preview_ready",
        "chip_result_type": "owner_note_compare_saved_view_preset_chip_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_filter_preference_saved": False,
        "real_user_preference_written": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def _build_preset_chips(presets: List[Dict[str, Any]]) -> Dict[str, Any]:
    chips = [
        _build_preset_chip(preset, order=idx)
        for idx, preset in enumerate(presets, start=1)
    ]

    return {
        "preset_chips_preview_id": f"owner_note_compare_preset_chips_{_stable_hash([chip.get('preset_chip_id') for chip in chips], 18)}",
        "preset_chips": chips,
        "preset_chip_count": len(chips),
        "preset_ids": [chip.get("saved_view_preset_id") for chip in chips],
        "default_preset_chip_id": next((chip.get("preset_chip_id") for chip in chips if chip.get("is_default")), None),
        "chips_status": "saved_view_preset_chips_preview_ready",
        "chips_result_type": "owner_note_compare_saved_view_preset_chips_preview",
        "filter_allowed_in_preview": True,
        "selection_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_filter_preference_saved": False,
        "real_user_preference_written": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_default_saved_view_selection(presets: List[Dict[str, Any]]) -> Dict[str, Any]:
    default_preset = next((preset for preset in presets if preset.get("is_default") is True), presets[0] if presets else {})

    identity = {
        "pack": PACK_ID,
        "default_preset": default_preset.get("saved_view_preset_id"),
        "drawer": default_preset.get("default_selected_version_detail_drawer_id"),
    }

    return {
        "default_saved_view_selection_id": f"owner_note_compare_default_saved_view_selection_{_stable_hash(identity, 18)}",
        "default_saved_view_preset_id": _safe_text(default_preset.get("saved_view_preset_id")),
        "default_filter_lane_id": _safe_text(default_preset.get("filter_lane_id")),
        "default_selected_version_detail_drawer_id": _safe_text(default_preset.get("default_selected_version_detail_drawer_id")),
        "default_selected_saved_view_id": _safe_text(default_preset.get("default_selected_saved_view_id")),
        "default_label": _safe_text(default_preset.get("label")),
        "selection_status": "default_saved_view_selection_preview_ready",
        "selection_result_type": "owner_note_compare_default_saved_view_selection_preview",
        "selection_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_preset_detail_preview(preset: Dict[str, Any], pack_173_payload: Dict[str, Any]) -> Dict[str, Any]:
    preset = dict(preset or {})
    nav_indexes = pack_173_payload.get("navigation_indexes", {})
    by_drawer = nav_indexes.get("by_version_detail_drawer_id", {}) if isinstance(nav_indexes, dict) else {}

    matched_ids = preset.get("matched_version_detail_drawer_ids", [])
    if not isinstance(matched_ids, list):
        matched_ids = []

    matched_nav_items = []
    if isinstance(by_drawer, dict):
        for drawer_id in matched_ids:
            item = by_drawer.get(drawer_id)
            if isinstance(item, dict):
                matched_nav_items.append(item)

    identity = {
        "pack": PACK_ID,
        "preset": preset.get("saved_view_preset_id"),
        "matched": matched_ids,
    }

    return {
        "preset_detail_preview_id": f"owner_note_compare_preset_detail_preview_{_stable_hash(identity, 18)}",
        "saved_view_preset_id": _safe_text(preset.get("saved_view_preset_id")),
        "label": _safe_text(preset.get("label")),
        "description": _safe_text(preset.get("description")),
        "filter_lane_id": _safe_text(preset.get("filter_lane_id")),
        "view_priority": _safe_text(preset.get("view_priority")),
        "is_default": bool(preset.get("is_default", False)),
        "matched_drawer_count": int(preset.get("matched_drawer_count") or 0),
        "matched_version_detail_drawer_ids": matched_ids,
        "matched_navigation_item_count": len(matched_nav_items),
        "matched_navigation_item_ids": [item.get("navigation_item_id") for item in matched_nav_items],
        "default_selected_version_detail_drawer_id": _safe_text(preset.get("default_selected_version_detail_drawer_id")),
        "detail_sections": [
            {
                "section_id": "preset_identity",
                "title": "Preset Identity",
                "safe_for_preview": True,
            },
            {
                "section_id": "matched_drawers",
                "title": "Matched Drawers",
                "safe_for_preview": True,
            },
            {
                "section_id": "default_selection",
                "title": "Default Selection",
                "safe_for_preview": True,
            },
            {
                "section_id": "blocked_persistence",
                "title": "Blocked Persistence",
                "safe_for_preview": True,
            },
        ],
        "detail_section_count": 4,
        "detail_status": "saved_view_preset_detail_preview_ready",
        "detail_result_type": "owner_note_compare_saved_view_preset_detail_preview",
        "preset_detail_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "real_filter_preference_saved": False,
        "real_navigation_state_persisted": False,
        "real_drawer_selection_saved": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_preset_detail_previews(presets: List[Dict[str, Any]], pack_173_payload: Dict[str, Any]) -> Dict[str, Any]:
    details = [
        _build_preset_detail_preview(preset, pack_173_payload)
        for preset in presets
    ]

    return {
        "preset_detail_previews_id": f"owner_note_compare_preset_detail_previews_{_stable_hash([detail.get('preset_detail_preview_id') for detail in details], 18)}",
        "preset_detail_previews": details,
        "preset_detail_count": len(details),
        "preset_detail_index": {
            detail.get("saved_view_preset_id"): detail
            for detail in details
            if detail.get("saved_view_preset_id")
        },
        "details_status": "saved_view_preset_detail_previews_ready",
        "details_result_type": "owner_note_compare_saved_view_preset_detail_previews",
        "preset_detail_allowed_in_preview": True,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "cached_non_recursive": True,
    }


def _build_saved_view_indexes(presets: List[Dict[str, Any]], details_payload: Dict[str, Any]) -> Dict[str, Any]:
    indexes = {
        "by_saved_view_preset_id": {},
        "by_filter_lane_id": {},
        "by_view_priority": {},
        "by_default_state": {},
        "by_preset_detail_id": {},
    }

    for preset in presets:
        preset_id = _safe_text(preset.get("saved_view_preset_id"))
        if preset_id:
            indexes["by_saved_view_preset_id"][preset_id] = preset

        lane_id = _safe_text(preset.get("filter_lane_id")) or "unknown"
        indexes["by_filter_lane_id"].setdefault(lane_id, []).append(preset)

        priority = _safe_text(preset.get("view_priority")) or "unknown"
        indexes["by_view_priority"].setdefault(priority, []).append(preset)

        default_key = "default" if preset.get("is_default") else "not_default"
        indexes["by_default_state"].setdefault(default_key, []).append(preset)

    for detail in details_payload.get("preset_detail_previews", []):
        detail_id = _safe_text(detail.get("preset_detail_preview_id"))
        if detail_id:
            indexes["by_preset_detail_id"][detail_id] = detail

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload_cached() -> Dict[str, Any]:
    pack_173_payload = _load_pack_173_payload(force_refresh=False)

    presets = _build_saved_view_presets(pack_173_payload)
    preset_chips_payload = _build_preset_chips(presets)
    default_selection = _build_default_saved_view_selection(presets)
    preset_detail_previews = _build_preset_detail_previews(presets, pack_173_payload)
    indexes = _build_saved_view_indexes(presets, preset_detail_previews)

    preset_status_counts = _count_by(presets, "preset_status")
    view_priority_counts = _count_by(presets, "view_priority")
    filter_lane_counts = _count_by(presets, "filter_lane_id")
    default_state_counts = {
        "default": len([preset for preset in presets if preset.get("is_default") is True]),
        "not_default": len([preset for preset in presets if preset.get("is_default") is False]),
    }

    readiness_checks = {
        "pack_173_ready": pack_173_payload.get("status") == "ready",
        "has_saved_view_presets": len(presets) >= len(SAVED_VIEW_PRESETS),
        "has_preset_chips": preset_chips_payload.get("preset_chip_count") == len(presets),
        "has_default_saved_view_selection": bool(default_selection.get("default_saved_view_preset_id")),
        "has_preset_detail_previews": preset_detail_previews.get("preset_detail_count") == len(presets),
        "all_expected_presets_present": EXPECTED_SAVED_VIEW_PRESETS.issubset({preset.get("saved_view_preset_id") for preset in presets}),
        "all_presets_ready": all(preset.get("preset_status") == "saved_view_filter_preset_preview_ready" for preset in presets),
        "all_preset_chips_ready": all(chip.get("chip_status") == "saved_view_preset_chip_preview_ready" for chip in preset_chips_payload.get("preset_chips", [])),
        "all_preset_details_ready": all(detail.get("detail_status") == "saved_view_preset_detail_preview_ready" for detail in preset_detail_previews.get("preset_detail_previews", [])),
        "default_selection_ready": default_selection.get("selection_status") == "default_saved_view_selection_preview_ready",
        "all_simulated_only": all(preset.get("simulated_only") is True for preset in presets),
        "all_saved_navigation_preview_only": all(preset.get("saved_navigation_preview_only") is True for preset in presets),
        "all_saved_filter_preset_preview_only": all(preset.get("saved_filter_preset_preview_only") is True for preset in presets),
        "all_navigation_preview_only": all(preset.get("navigation_preview_only") is True for preset in presets),
        "all_filter_navigation_preview_only": all(preset.get("filter_navigation_preview_only") is True for preset in presets),
        "all_version_detail_preview_only": all(preset.get("version_detail_preview_only") is True for preset in presets),
        "all_compare_view_preview_only": all(preset.get("compare_view_preview_only") is True for preset in presets),
        "all_version_preview_only": all(preset.get("version_preview_only") is True for preset in presets),
        "all_edit_history_preview_only": all(preset.get("edit_history_preview_only") is True for preset in presets),
        "all_rollback_preview_only": all(preset.get("rollback_preview_only") is True for preset in presets),
        "all_compare_preview_only": all(preset.get("compare_preview_only") is True for preset in presets),
        "all_edit_preview_only": all(preset.get("edit_preview_only") is True for preset in presets),
        "all_detail_drawer_preview_only": all(preset.get("detail_drawer_preview_only") is True for preset in presets),
        "all_owner_note_preview_only": all(preset.get("owner_note_preview_only") is True for preset in presets),
        "all_review_draft_preview_only": all(preset.get("review_draft_preview_only") is True for preset in presets),
        "all_saved_view_preview_only": all(preset.get("saved_view_preview_only") is True for preset in presets),
        "all_filter_preset_preview_only": all(preset.get("filter_preset_preview_only") is True for preset in presets),
        "all_filter_preview_only": all(preset.get("filter_preview_only") is True for preset in presets),
        "all_search_facet_preview_only": all(preset.get("search_facet_preview_only") is True for preset in presets),
        "all_lookup_preview_only": all(preset.get("lookup_preview_only") is True for preset in presets),
        "all_detail_preview_only": all(preset.get("detail_preview_only") is True for preset in presets),
        "all_evidence_drawer_preview_only": all(preset.get("evidence_drawer_preview_only") is True for preset in presets),
        "all_owner_review_preview_only": all(preset.get("owner_review_preview_only") is True for preset in presets),
        "all_queue_preview_only": all(preset.get("queue_preview_only") is True for preset in presets),
        "all_renewal_preview_only": all(preset.get("renewal_preview_only") is True for preset in presets),
        "all_recheck_preview_only": all(preset.get("recheck_preview_only") is True for preset in presets),
        "all_expiration_preview_only": all(preset.get("expiration_preview_only") is True for preset in presets),
        "all_vault_preview_only": all(preset.get("vault_preview_only") is True for preset in presets),
        "all_index_preview_only": all(preset.get("index_preview_only") is True for preset in presets),
        "all_receipt_preview_only": all(preset.get("receipt_preview_only") is True for preset in presets),
        "all_approval_preview_only": all(preset.get("approval_preview_only") is True for preset in presets),
        "all_evidence_preview_only": all(preset.get("evidence_preview_only") is True for preset in presets),
        "no_real_saved_view_written": all(preset.get("real_saved_view_written") is False for preset in presets),
        "no_real_user_preference_written": all(preset.get("real_user_preference_written") is False for preset in presets),
        "no_real_filter_preference_saved": all(preset.get("real_filter_preference_saved") is False for preset in presets),
        "no_real_navigation_state_persisted": all(preset.get("real_navigation_state_persisted") is False for preset in presets),
        "no_real_drawer_selection_saved": all(preset.get("real_drawer_selection_saved") is False for preset in presets),
        "no_real_history_written": all(preset.get("real_history_written") is False for preset in presets),
        "no_real_version_written": all(preset.get("real_version_written") is False for preset in presets),
        "no_real_version_saved": all(preset.get("real_version_saved") is False for preset in presets),
        "no_real_rollback_executed": all(preset.get("real_rollback_executed") is False for preset in presets),
        "no_real_restore_executed": all(preset.get("real_restore_executed") is False for preset in presets),
        "all_saved_view_writes_blocked": all(preset.get("saved_view_write_allowed_now") is False for preset in presets),
        "all_user_preference_writes_blocked": all(preset.get("user_preference_write_allowed_now") is False for preset in presets),
        "all_filter_preference_saves_blocked": all(preset.get("filter_preference_save_allowed_now") is False for preset in presets),
        "all_navigation_persistence_blocked": all(preset.get("navigation_persistence_allowed_now") is False for preset in presets),
        "all_drawer_selection_saves_blocked": all(preset.get("drawer_selection_save_allowed_now") is False for preset in presets),
        "all_raw_evidence_reveal_blocked": all(preset.get("raw_evidence_reveal_allowed") is False for preset in presets),
        "all_raw_evidence_lookup_blocked": all(preset.get("raw_evidence_lookup_allowed") is False for preset in presets),
        "default_all_compare_drawers_present": "default_all_compare_drawers" in {preset.get("saved_view_preset_id") for preset in presets},
        "owner_review_focus_present": "owner_review_focus" in {preset.get("saved_view_preset_id") for preset in presets},
        "critical_priority_focus_present": "critical_priority_focus" in {preset.get("saved_view_preset_id") for preset in presets},
        "high_priority_focus_present": "high_priority_focus" in {preset.get("saved_view_preset_id") for preset in presets},
        "monitor_only_focus_present": "monitor_only_focus" in {preset.get("saved_view_preset_id") for preset in presets},
        "safe_preview_focus_present": "safe_preview_focus" in {preset.get("saved_view_preset_id") for preset in presets},
        "exactly_one_default_preset": len([preset for preset in presets if preset.get("is_default") is True]) == 1,
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
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
        "pack_number": 174,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Compare Navigation Saved View / Filter Preset Preview",
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "source_endpoint": COMPARE_FILTER_NAVIGATION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
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
        "cached_non_recursive": True,
        "source_pack_173": {
            "status": pack_173_payload.get("status"),
            "readiness_score": pack_173_payload.get("summary", {}).get("readiness_score"),
            "navigation_item_count": pack_173_payload.get("summary", {}).get("navigation_item_count"),
            "filter_lane_count": pack_173_payload.get("summary", {}).get("filter_lane_count"),
            "quick_filter_chip_count": pack_173_payload.get("summary", {}).get("quick_filter_chip_count"),
        },
        "summary": {
            "saved_view_preset_count": len(presets),
            "preset_chip_count": preset_chips_payload.get("preset_chip_count", 0),
            "preset_detail_count": preset_detail_previews.get("preset_detail_count", 0),
            "default_saved_view_preset_id": default_selection.get("default_saved_view_preset_id"),
            "default_filter_lane_id": default_selection.get("default_filter_lane_id"),
            "preset_status_counts": preset_status_counts,
            "view_priority_counts": view_priority_counts,
            "filter_lane_counts": filter_lane_counts,
            "default_state_counts": default_state_counts,
            "readiness_score": readiness_score,
            "readiness_label": "Owner note compare navigation saved view/filter preset preview ready" if readiness_score == 100 else "Owner note compare navigation saved view/filter preset preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_presets_schema": SAVED_VIEW_PRESETS,
        "saved_view_presets": presets,
        "preset_chips_preview": preset_chips_payload,
        "default_saved_view_selection": default_selection,
        "preset_detail_previews": preset_detail_previews,
        "saved_view_indexes": indexes,
    }


def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload_cached())


def get_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 174,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", SAVED_VIEW_FILTER_PRESET_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", COMPARE_FILTER_NAVIGATION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Owner note compare navigation saved view/filter preset preview ready"),
        "saved_view_preset_count": summary.get("saved_view_preset_count", 0),
        "preset_chip_count": summary.get("preset_chip_count", 0),
        "preset_detail_count": summary.get("preset_detail_count", 0),
        "default_saved_view_preset_id": summary.get("default_saved_view_preset_id"),
        "default_filter_lane_id": summary.get("default_filter_lane_id"),
        "preset_status_counts": summary.get("preset_status_counts", {}),
        "view_priority_counts": summary.get("view_priority_counts", {}),
        "filter_lane_counts": summary.get("filter_lane_counts", {}),
        "default_state_counts": summary.get("default_state_counts", {}),
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
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
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset",
        "label": "Owner Note Saved Compare Views",
        "title": "Owner Note Compare Navigation Saved View / Filter Preset Preview",
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "endpoint": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "description": "Preview saved compare navigation views, filter presets, preset chips, default view selection, and blocked preference persistence.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 174",
        "category": "policy",
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
    }


def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "saved_view_readiness",
            "title": "Saved view readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Owner note compare navigation saved view/filter preset preview ready"),
        },
        {
            "id": "saved_view_presets",
            "title": "Saved view presets",
            "value": summary.get("saved_view_preset_count", 0),
            "label": "Preset views ready",
        },
        {
            "id": "preset_chips",
            "title": "Preset chips",
            "value": summary.get("preset_chip_count", 0),
            "label": "Saved filter chips",
        },
        {
            "id": "preset_details",
            "title": "Preset details",
            "value": summary.get("preset_detail_count", 0),
            "label": "Preset detail previews",
        },
        {
            "id": "default_saved_view",
            "title": "Default saved view",
            "value": summary.get("default_saved_view_preset_id", "missing"),
            "label": "Default selection preview",
        },
        {
            "id": "preference_persistence",
            "title": "Preference persistence",
            "value": "Blocked" if checks.get("all_user_preference_writes_blocked") else "Review",
            "label": "No real preference write",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset",
        "title": "Owner Note Saved Compare Views",
        "subtitle": "Preview saved compare navigation views, filter presets, preset chips, default selection, preset details, and blocked preference persistence.",
        "status": payload.get("status", "ready"),
        "href": SAVED_VIEW_FILTER_PRESET_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "saved_navigation_preview_only": True,
        "saved_filter_preset_preview_only": True,
        "navigation_preview_only": True,
        "filter_navigation_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-note-saved-view-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-note-saved-view-section" id="policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 174</p>
            <h2>{section.get('title', 'Owner Note Saved Compare Views')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SAVED_VIEW_FILTER_PRESET_ENDPOINT}">Open owner note saved compare views JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_FILTER_PRESET_ENDPOINT",
    "COMPARE_FILTER_NAVIGATION_ENDPOINT",
    "SAVED_VIEW_PRESETS",
    "EXPECTED_SAVED_VIEW_PRESETS",
    "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload",
    "get_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_payload",
    "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge",
    "get_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_status_bridge",
    "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_quick_action",
    "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section",
    "build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_html_section",
]
