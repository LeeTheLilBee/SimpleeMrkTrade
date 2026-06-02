
"""
PACK 202 - Receipt Chain Operational Handoff Saved Views / Filter Presets Preview.

Short module filename:
    tower.receipt_chain_handoff_saved_views_v202

This module sits on top of Pack 201.

Pack 201 creates the operational handoff preview.
Pack 202 adds preview-only saved views and filter presets:
- operational handoff saved view previews
- handoff filter preset previews
- owner action menu view presets
- evidence map saved view previews
- selected saved view / filter preset preview
- no real saved view writes
- no real preference writes
- no real navigation persistence
- no real action / handoff / evidence export / raw reveal

Important:
- simulated-only
- saved-view-preview-only
- filter-preset-preview-only
- no real saved view written
- no real user preference written
- no real action executed
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


PACK_ID = "PACK_202"
HANDOFF_SAVED_VIEWS_ENDPOINT = "/tower/receipt-chain-handoff-saved-views-v202.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-operational-handoff-v201.json"


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
        "selected_saved_view_preview_only": True,
        "operational_handoff_preview_only": True,
        "receipt_chain_handoff_preview_only": True,
        "checkpoint_preview_only": True,
        "receipt_chain_checkpoint_preview_only": True,
        "owner_action_menu_preview_only": True,
        "evidence_map_preview_only": True,
        "routing_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "owner_action_execution_allowed_now": False,
        "handoff_execution_allowed_now": False,
        "evidence_export_allowed_now": False,
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
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
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


def _load_pack_201_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_operational_handoff_v201")
        fn = getattr(mod, "build_receipt_chain_operational_handoff_v201_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_201",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "readiness_score": 0,
                "handoff_route_count": 0,
                "owner_action_menu_item_count": 0,
                "evidence_map_item_count": 0,
                "next_batch_card_count": 0,
                "safe_to_continue_to_pack_202": False,
            },
            "handoff_routes": [],
            "owner_action_menu_items": [],
            "handoff_evidence_map_items": [],
            "next_batch_board": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_201",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "readiness_score": 0,
            "handoff_route_count": 0,
            "owner_action_menu_item_count": 0,
            "evidence_map_item_count": 0,
            "next_batch_card_count": 0,
            "safe_to_continue_to_pack_202": False,
        },
        "handoff_routes": [],
        "owner_action_menu_items": [],
        "handoff_evidence_map_items": [],
        "next_batch_board": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _ids(items: List[Dict[str, object]], key: str) -> List[object]:
    return [item.get(key) for item in items if isinstance(item, dict)]


def _build_saved_views(routes: List[Dict[str, object]], actions: List[Dict[str, object]], evidence: List[Dict[str, object]], next_batch: List[Dict[str, object]]) -> List[Dict[str, object]]:
    ready_routes = [route for route in routes if route.get("route_state") == "ready"]
    blocked_actions = [action for action in actions if action.get("blocked_in_preview") is True]
    allowed_actions = [action for action in actions if action.get("allowed_in_preview") is True]

    view_defs = [
        {
            "saved_view_id": "default_full_handoff",
            "label": "Full handoff",
            "description": "All handoff routes, owner actions, evidence map items, and next-batch cards.",
            "route_keys": _ids(routes, "route_key"),
            "owner_action_keys": _ids(actions, "owner_action_key"),
            "source_pack_numbers": _ids(evidence, "source_pack_number"),
            "next_pack_numbers": _ids(next_batch, "pack_number"),
        },
        {
            "saved_view_id": "routes_only",
            "label": "Routes only",
            "description": "Preview operational handoff routing lanes only.",
            "route_keys": _ids(ready_routes, "route_key"),
            "owner_action_keys": [],
            "source_pack_numbers": [],
            "next_pack_numbers": [],
        },
        {
            "saved_view_id": "blocked_owner_actions",
            "label": "Blocked owner actions",
            "description": "Preview blocked execution/export/access actions.",
            "route_keys": [],
            "owner_action_keys": _ids(blocked_actions, "owner_action_key"),
            "source_pack_numbers": [],
            "next_pack_numbers": [],
        },
        {
            "saved_view_id": "allowed_preview_actions",
            "label": "Allowed preview actions",
            "description": "Preview actions allowed only as preview navigation.",
            "route_keys": [],
            "owner_action_keys": _ids(allowed_actions, "owner_action_key"),
            "source_pack_numbers": [],
            "next_pack_numbers": [],
        },
        {
            "saved_view_id": "evidence_map",
            "label": "Evidence map",
            "description": "Preview mapped evidence from Packs 196-199.",
            "route_keys": [],
            "owner_action_keys": [],
            "source_pack_numbers": _ids(evidence, "source_pack_number"),
            "next_pack_numbers": [],
        },
        {
            "saved_view_id": "next_batch_201_205",
            "label": "Next batch 201-205",
            "description": "Preview the next five-pack board.",
            "route_keys": [],
            "owner_action_keys": [],
            "source_pack_numbers": [],
            "next_pack_numbers": _ids(next_batch, "pack_number"),
        },
    ]

    views = []
    for sequence, view_def in enumerate(view_defs, start=1):
        view = {
            "handoff_saved_view_preview_id": f"receipt_chain_handoff_saved_view_{_stable_hash((PACK_ID, view_def['saved_view_id']), 18)}",
            "saved_view_id": view_def["saved_view_id"],
            "label": view_def["label"],
            "description": view_def["description"],
            "sequence": sequence,
            "matched_handoff_route_count": len(view_def["route_keys"]),
            "matched_route_keys": view_def["route_keys"],
            "matched_owner_action_count": len(view_def["owner_action_keys"]),
            "matched_owner_action_keys": view_def["owner_action_keys"],
            "matched_evidence_map_item_count": len(view_def["source_pack_numbers"]),
            "matched_source_pack_numbers": view_def["source_pack_numbers"],
            "matched_next_batch_card_count": len(view_def["next_pack_numbers"]),
            "matched_next_pack_numbers": view_def["next_pack_numbers"],
            "save_batch": "201-205",
            "view_status": "receipt_chain_handoff_saved_view_preview_ready",
            "view_result_type": "tower_receipt_chain_handoff_saved_view_preview",
            "safe_preview_only": True,
        }
        view.update(_base_flags())
        views.append(view)

    return views


def _build_filter_presets(routes: List[Dict[str, object]], actions: List[Dict[str, object]], evidence: List[Dict[str, object]], next_batch: List[Dict[str, object]]) -> List[Dict[str, object]]:
    preset_defs = [
        ("all_handoff_items", "All handoff items", "all", len(routes), len(actions), len(evidence), len(next_batch)),
        ("ready_routes", "Ready routes", "route_state", sum(1 for route in routes if route.get("route_state") == "ready"), 0, 0, 0),
        ("blocked_actions", "Blocked actions", "owner_action_state", 0, sum(1 for action in actions if action.get("blocked_in_preview") is True), 0, 0),
        ("allowed_preview_actions", "Allowed preview actions", "owner_action_state", 0, sum(1 for action in actions if action.get("allowed_in_preview") is True), 0, 0),
        ("evidence_pack_map", "Evidence pack map", "evidence_map", 0, 0, len(evidence), 0),
        ("next_batch_board", "Next batch board", "next_batch", 0, 0, 0, len(next_batch)),
        ("no_real_execution", "No real execution", "safety", len(routes), len(actions), len(evidence), len(next_batch)),
        ("export_blocked", "Export blocked", "safety", 0, sum(1 for action in actions if "export" in str(action.get("owner_action_key"))), len(evidence), 0),
    ]

    presets = []
    for sequence, (preset_id, label, preset_type, route_count, action_count, evidence_count, batch_count) in enumerate(preset_defs, start=1):
        preset = {
            "handoff_filter_preset_preview_id": f"receipt_chain_handoff_filter_preset_{_stable_hash((PACK_ID, preset_id), 18)}",
            "filter_preset_id": preset_id,
            "label": label,
            "filter_type": preset_type,
            "sequence": sequence,
            "matched_handoff_route_count": route_count,
            "matched_owner_action_count": action_count,
            "matched_evidence_map_item_count": evidence_count,
            "matched_next_batch_card_count": batch_count,
            "preset_status": "receipt_chain_handoff_filter_preset_preview_ready",
            "preset_result_type": "tower_receipt_chain_handoff_filter_preset_preview",
            "safe_preview_only": True,
        }
        preset.update(_base_flags())
        presets.append(preset)

    return presets


def _build_selected_view(views: List[Dict[str, object]], presets: List[Dict[str, object]]) -> Dict[str, object]:
    default_view = next((view for view in views if view.get("saved_view_id") == "default_full_handoff"), views[0] if views else {})
    default_preset = next((preset for preset in presets if preset.get("filter_preset_id") == "all_handoff_items"), presets[0] if presets else {})

    selected = {
        "selected_handoff_saved_view_preview_id": f"receipt_chain_selected_handoff_saved_view_{_stable_hash((PACK_ID, default_view.get('saved_view_id'), default_preset.get('filter_preset_id')), 18)}",
        "selected_saved_view_id": default_view.get("saved_view_id"),
        "selected_saved_view_preview_id": default_view.get("handoff_saved_view_preview_id"),
        "selected_filter_preset_id": default_preset.get("filter_preset_id"),
        "selected_filter_preset_preview_id": default_preset.get("handoff_filter_preset_preview_id"),
        "selected_handoff_route_count": default_view.get("matched_handoff_route_count"),
        "selected_owner_action_count": default_view.get("matched_owner_action_count"),
        "selected_evidence_map_item_count": default_view.get("matched_evidence_map_item_count"),
        "selected_next_batch_card_count": default_view.get("matched_next_batch_card_count"),
        "selection_status": "receipt_chain_selected_handoff_saved_view_preview_ready",
        "selection_result_type": "tower_receipt_chain_selected_handoff_saved_view_preview",
        "safe_preview_only": True,
    }
    selected.update(_base_flags())
    return selected


def _build_safety_summary(views: List[Dict[str, object]], presets: List[Dict[str, object]], selected: Dict[str, object]) -> Dict[str, object]:
    summary = {
        "handoff_saved_view_safety_summary_id": f"receipt_chain_handoff_saved_view_safety_{_stable_hash((PACK_ID, len(views), len(presets)), 18)}",
        "saved_view_preview_count": len(views),
        "filter_preset_preview_count": len(presets),
        "selected_saved_view_preview_count": 1 if selected else 0,
        "real_saved_view_written_count": 0,
        "real_user_preference_written_count": 0,
        "real_navigation_state_persisted_count": 0,
        "real_action_executed_count": 0,
        "real_handoff_executed_count": 0,
        "real_owner_action_executed_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_saved_views_preview_only": all(view.get("saved_view_preview_only") is True for view in views),
        "all_filter_presets_preview_only": all(preset.get("filter_preset_preview_only") is True for preset in presets),
        "all_real_writes_blocked": True,
        "summary_status": "receipt_chain_handoff_saved_view_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_handoff_saved_view_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_indexes(views: List[Dict[str, object]], presets: List[Dict[str, object]], selected: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "handoff_saved_views_by_id": {},
        "handoff_saved_views_by_key": {},
        "handoff_filter_presets_by_id": {},
        "handoff_filter_presets_by_key": {},
        "handoff_filter_presets_by_type": {},
        "selected_handoff_saved_view_by_id": {},
    }

    for view in views:
        indexes["handoff_saved_views_by_id"][view.get("handoff_saved_view_preview_id")] = view
        indexes["handoff_saved_views_by_key"][view.get("saved_view_id")] = view

    for preset in presets:
        indexes["handoff_filter_presets_by_id"][preset.get("handoff_filter_preset_preview_id")] = preset
        indexes["handoff_filter_presets_by_key"][preset.get("filter_preset_id")] = preset
        indexes["handoff_filter_presets_by_type"].setdefault(preset.get("filter_type"), []).append(preset)

    indexes["selected_handoff_saved_view_by_id"][selected.get("selected_handoff_saved_view_preview_id")] = selected
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_handoff_saved_views_v202_payload_cached() -> Dict[str, object]:
    pack_201 = _load_pack_201_payload(force_refresh=True)

    routes = [item for item in _list(pack_201.get("handoff_routes")) if isinstance(item, dict)]
    actions = [item for item in _list(pack_201.get("owner_action_menu_items")) if isinstance(item, dict)]
    evidence = [item for item in _list(pack_201.get("handoff_evidence_map_items")) if isinstance(item, dict)]
    next_batch = [item for item in _list(pack_201.get("next_batch_board")) if isinstance(item, dict)]

    views = _build_saved_views(routes, actions, evidence, next_batch)
    presets = _build_filter_presets(routes, actions, evidence, next_batch)
    selected = _build_selected_view(views, presets)
    safety = _build_safety_summary(views, presets, selected)
    indexes = _build_indexes(views, presets, selected)

    readiness_checks = {
        "pack_201_ready": pack_201.get("status") == "ready",
        "pack_201_safe_to_continue": pack_201.get("summary", {}).get("safe_to_continue_to_pack_202") is True,
        "has_saved_view_previews": len(views) == 6,
        "has_filter_preset_previews": len(presets) == 8,
        "has_selected_saved_view": selected.get("selection_status") == "receipt_chain_selected_handoff_saved_view_preview_ready",
        "default_saved_view_selected": selected.get("selected_saved_view_id") == "default_full_handoff",
        "default_filter_preset_selected": selected.get("selected_filter_preset_id") == "all_handoff_items",
        "all_saved_views_ready": all(view.get("view_status") == "receipt_chain_handoff_saved_view_preview_ready" for view in views),
        "all_filter_presets_ready": all(preset.get("preset_status") == "receipt_chain_handoff_filter_preset_preview_ready" for preset in presets),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_handoff_saved_view_safety_summary_preview_ready",
        "indexes_present": bool(indexes.get("handoff_saved_views_by_id")),
        "preset_indexes_present": bool(indexes.get("handoff_filter_presets_by_id")),
        "selected_index_present": bool(indexes.get("selected_handoff_saved_view_by_id")),
        "selected_counts_match_source": (
            selected.get("selected_handoff_route_count") == len(routes)
            and selected.get("selected_owner_action_count") == len(actions)
            and selected.get("selected_evidence_map_item_count") == len(evidence)
            and selected.get("selected_next_batch_card_count") == len(next_batch)
        ),
        "all_simulated_only": all(item.get("simulated_only") is True for item in views + presets),
        "all_saved_view_preview_only": all(item.get("saved_view_preview_only") is True for item in views + presets),
        "all_filter_preset_preview_only": all(item.get("filter_preset_preview_only") is True for item in views + presets),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in views + presets),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in views + presets),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in views + presets),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in views + presets),
        "no_real_handoff_executed": all(item.get("real_handoff_executed") is False for item in views + presets),
        "no_real_owner_action_executed": all(item.get("real_owner_action_executed") is False for item in views + presets),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in views + presets),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in views + presets),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in views + presets),
        "all_user_preference_writes_blocked": all(item.get("user_preference_write_allowed_now") is False for item in views + presets),
        "all_filter_preference_saves_blocked": all(item.get("filter_preference_save_allowed_now") is False for item in views + presets),
        "all_navigation_persistence_blocked": all(item.get("navigation_persistence_allowed_now") is False for item in views + presets),
        "all_action_execution_blocked": all(item.get("action_execution_allowed_now") is False for item in views + presets),
        "all_evidence_export_blocked": all(item.get("evidence_export_allowed_now") is False for item in views + presets),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in views + presets),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 202,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Operational Handoff Saved Views / Filter Presets Preview",
        "endpoint": HANDOFF_SAVED_VIEWS_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_201": {
            "status": pack_201.get("status"),
            "readiness_score": pack_201.get("summary", {}).get("readiness_score"),
            "handoff_route_count": pack_201.get("summary", {}).get("handoff_route_count"),
            "owner_action_menu_item_count": pack_201.get("summary", {}).get("owner_action_menu_item_count"),
            "evidence_map_item_count": pack_201.get("summary", {}).get("evidence_map_item_count"),
            "next_batch_card_count": pack_201.get("summary", {}).get("next_batch_card_count"),
            "safe_to_continue_to_pack_202": pack_201.get("summary", {}).get("safe_to_continue_to_pack_202"),
        },
        "summary": {
            "handoff_saved_view_preview_count": len(views),
            "handoff_filter_preset_preview_count": len(presets),
            "selected_handoff_saved_view_preview_count": 1 if selected else 0,
            "selected_saved_view_id": selected.get("selected_saved_view_id"),
            "selected_filter_preset_id": selected.get("selected_filter_preset_id"),
            "selected_handoff_route_count": selected.get("selected_handoff_route_count"),
            "selected_owner_action_count": selected.get("selected_owner_action_count"),
            "selected_evidence_map_item_count": selected.get("selected_evidence_map_item_count"),
            "selected_next_batch_card_count": selected.get("selected_next_batch_card_count"),
            "real_saved_view_written_count": safety.get("real_saved_view_written_count"),
            "real_user_preference_written_count": safety.get("real_user_preference_written_count"),
            "real_navigation_state_persisted_count": safety.get("real_navigation_state_persisted_count"),
            "real_action_executed_count": safety.get("real_action_executed_count"),
            "real_handoff_executed_count": safety.get("real_handoff_executed_count"),
            "real_owner_action_executed_count": safety.get("real_owner_action_executed_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "save_batch": "201-205",
            "save_after_pack": 205,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain handoff saved views/filter presets preview ready" if readiness_score == 100 else "Receipt chain handoff saved views/filter presets preview needs review",
        },
        "readiness_checks": readiness_checks,
        "handoff_saved_view_previews": views,
        "handoff_filter_preset_previews": presets,
        "selected_handoff_saved_view_preview": selected,
        "handoff_saved_view_safety_summary": safety,
        "handoff_saved_view_indexes": indexes,
    }


def build_receipt_chain_handoff_saved_views_v202_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_handoff_saved_views_v202_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_handoff_saved_views_v202_payload_cached())


def get_receipt_chain_handoff_saved_views_v202_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_handoff_saved_views_v202_payload(force_refresh=force_refresh)


def build_receipt_chain_handoff_saved_views_v202_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_handoff_saved_views_v202_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 202,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "handoff_saved_view_preview_count": summary.get("handoff_saved_view_preview_count"),
        "handoff_filter_preset_preview_count": summary.get("handoff_filter_preset_preview_count"),
        "selected_handoff_saved_view_preview_count": summary.get("selected_handoff_saved_view_preview_count"),
        "selected_saved_view_id": summary.get("selected_saved_view_id"),
        "selected_filter_preset_id": summary.get("selected_filter_preset_id"),
        "selected_handoff_route_count": summary.get("selected_handoff_route_count"),
        "selected_owner_action_count": summary.get("selected_owner_action_count"),
        "selected_evidence_map_item_count": summary.get("selected_evidence_map_item_count"),
        "selected_next_batch_card_count": summary.get("selected_next_batch_card_count"),
        "real_saved_view_written_count": summary.get("real_saved_view_written_count"),
        "real_user_preference_written_count": summary.get("real_user_preference_written_count"),
        "real_navigation_state_persisted_count": summary.get("real_navigation_state_persisted_count"),
        "real_action_executed_count": summary.get("real_action_executed_count"),
        "real_handoff_executed_count": summary.get("real_handoff_executed_count"),
        "real_owner_action_executed_count": summary.get("real_owner_action_executed_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_handoff_saved_views_v202_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_handoff_saved_views_v202_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_handoff_saved_views_v202_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_handoff_saved_views_v202_status_bridge()

    action = {
        "id": "receipt_chain_handoff_saved_views_v202",
        "label": "Receipt Chain Handoff Saved Views",
        "title": "Receipt Chain Operational Handoff Saved Views / Filter Presets Preview",
        "href": HANDOFF_SAVED_VIEWS_ENDPOINT,
        "endpoint": HANDOFF_SAVED_VIEWS_ENDPOINT,
        "description": "Preview saved views and filter presets for the receipt-chain operational handoff.",
        "status": bridge.get("status"),
        "pack": "Pack 202",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_handoff_saved_views_v202_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_handoff_saved_views_v202_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_handoff_saved_views_v202",
        "title": "Receipt Chain Handoff Saved Views",
        "subtitle": "Preview saved views and filter presets for handoff routes, actions, evidence, and next-batch board.",
        "status": payload.get("status"),
        "href": HANDOFF_SAVED_VIEWS_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Saved-view readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "views", "title": "Saved views", "value": summary.get("handoff_saved_view_preview_count"), "label": "Preview-only saved views"},
            {"id": "presets", "title": "Filter presets", "value": summary.get("handoff_filter_preset_preview_count"), "label": "Preview-only filter presets"},
            {"id": "selected", "title": "Selected view", "value": summary.get("selected_saved_view_id"), "label": "Default selected saved view"},
            {"id": "batch", "title": "Save batch", "value": summary.get("save_batch"), "label": "Save after Pack 205"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_saved_view_written") and checks.get("no_real_user_preference_written") else "Review", "label": "No saved view/preference writes"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "HANDOFF_SAVED_VIEWS_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_handoff_saved_views_v202_payload",
    "get_receipt_chain_handoff_saved_views_v202_payload",
    "build_receipt_chain_handoff_saved_views_v202_status_bridge",
    "get_receipt_chain_handoff_saved_views_v202_status_bridge",
    "build_receipt_chain_handoff_saved_views_v202_quick_action",
    "build_receipt_chain_handoff_saved_views_v202_unified_owner_section",
]
