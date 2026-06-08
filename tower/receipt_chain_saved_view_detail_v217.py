
"""
PACK 217 - Receipt Chain Saved View Detail Drawer Preview.

Short module filename:
    tower.receipt_chain_saved_view_detail_v217

This module sits on top of Pack 216.

Pack 216 created saved view preset previews.
Pack 217 adds saved view detail drawer previews:
- selected preset detail cards
- preset field detail rows
- linked filter detail cards
- linked scope detail cards
- detail action menu
- owner saved view detail review queue
- no real saved view writes
- no real user preference writes
- no real exports
- no raw evidence reveal

Important:
- simulated-only
- saved-view-detail-preview-only
- no real persistence
- no real exports
- raw evidence redacted
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


PACK_ID = "PACK_217"
SAVED_VIEW_DETAIL_ENDPOINT = "/tower/receipt-chain-saved-view-detail-v217.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-saved-view-presets-v216.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "saved_view_detail_preview_only": True,
        "selected_preset_detail_preview_only": True,
        "preset_field_detail_preview_only": True,
        "linked_filter_detail_preview_only": True,
        "linked_scope_detail_preview_only": True,
        "saved_view_detail_action_menu_preview_only": True,
        "owner_saved_view_detail_queue_preview_only": True,
        "saved_view_preset_preview_only": True,
        "saved_view_filter_map_preview_only": True,
        "saved_view_scope_card_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "saved_view_write_allowed_now": False,
        "saved_view_edit_allowed_now": False,
        "saved_view_delete_allowed_now": False,
        "saved_view_apply_allowed_now": False,
        "saved_view_export_allowed_now": False,
        "detail_state_persistence_allowed_now": False,
        "detail_selection_save_allowed_now": False,
        "field_detail_save_allowed_now": False,
        "linked_filter_detail_save_allowed_now": False,
        "linked_scope_detail_save_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "owner_review_save_allowed_now": False,
        "evidence_export_allowed_now": False,
        "archive_write_allowed_now": False,
        "archive_export_allowed_now": False,
        "gateway_access_grant_allowed_now": False,
        "save_allowed_now": False,
        "push_allowed_now": False,
        "commit_allowed_now": False,
        "owner_action_execution_allowed_now": False,
        "handoff_execution_allowed_now": False,
        "persist_allowed_now": False,
        "action_execution_allowed_now": False,
        "real_action_executed": False,
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
        "real_saved_view_written": False,
        "real_saved_view_edited": False,
        "real_saved_view_deleted": False,
        "real_saved_view_applied": False,
        "real_saved_view_exported": False,
        "real_detail_state_persisted": False,
        "real_detail_selection_saved": False,
        "real_field_detail_saved": False,
        "real_linked_filter_detail_saved": False,
        "real_linked_scope_detail_saved": False,
        "real_user_preference_written": False,
        "real_navigation_state_persisted": False,
        "real_owner_review_saved": False,
        "real_archive_written": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_216_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_saved_view_presets_v216")
        fn = getattr(mod, "build_receipt_chain_saved_view_presets_v216_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_216",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_217": False},
            "saved_view_preset_previews": [],
            "saved_view_filter_map_previews": [],
            "saved_view_scope_card_previews": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_216",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_217": False},
        "saved_view_preset_previews": [],
        "saved_view_filter_map_previews": [],
        "saved_view_scope_card_previews": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_selected_preset_details(pack_216: Dict[str, object]) -> List[Dict[str, object]]:
    presets = [item for item in _list(pack_216.get("saved_view_preset_previews")) if isinstance(item, dict)]
    selected = presets[:7]

    details = []
    for sequence, preset in enumerate(selected, start=1):
        preset_key = preset.get("saved_view_preset_key") or f"preset_{sequence}"
        item = {
            "selected_preset_detail_preview_id": f"receipt_chain_saved_view_detail_{_stable_hash((PACK_ID, preset_key), 18)}",
            "selected_preset_key": preset_key,
            "label": f"Saved View Detail: {preset.get('label') or preset_key}",
            "detail_type": preset.get("preset_type") or "unknown",
            "preset_value": preset.get("preset_value"),
            "sequence": sequence,
            "source_preset_preview_id": preset.get("saved_view_preset_preview_id"),
            "source_endpoint": SOURCE_ENDPOINT,
            "detail_section_count": 6,
            "detail_sections": [
                "summary",
                "filter_values",
                "scope",
                "safety_flags",
                "owner_review",
                "next_action_preview",
            ],
            "detail_state_persistence_allowed_now": False,
            "detail_selection_save_allowed_now": False,
            "detail_status": "receipt_chain_saved_view_selected_preset_detail_preview_ready",
            "detail_result_type": "tower_receipt_chain_saved_view_selected_preset_detail_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        details.append(item)

    return details


def _build_field_detail_rows(details: List[Dict[str, object]]) -> List[Dict[str, object]]:
    field_defs = [
        ("preset_key", "Preset key", "identity"),
        ("preset_type", "Preset type", "classification"),
        ("preset_value", "Preset value", "value"),
        ("source_batch", "Source batch", "source"),
        ("safety_state", "Safety state", "safety"),
        ("write_policy", "Write policy", "policy"),
        ("raw_evidence_policy", "Raw evidence policy", "redaction"),
        ("next_action", "Next action", "next_step"),
    ]

    detail_keys = [item.get("selected_preset_key") for item in details]

    rows = []
    for sequence, (field_key, label, field_type) in enumerate(field_defs, start=1):
        item = {
            "preset_field_detail_row_preview_id": f"receipt_chain_saved_view_field_detail_{_stable_hash((PACK_ID, field_key), 18)}",
            "preset_field_detail_key": field_key,
            "label": label,
            "field_type": field_type,
            "sequence": sequence,
            "linked_selected_preset_keys": detail_keys,
            "linked_selected_preset_count": len(detail_keys),
            "field_value_preview": "preview_only_redacted_safe_value",
            "field_detail_save_allowed_now": False,
            "row_status": "receipt_chain_saved_view_preset_field_detail_row_preview_ready",
            "row_result_type": "tower_receipt_chain_saved_view_preset_field_detail_row_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        rows.append(item)

    return rows


def _build_linked_filter_details(pack_216: Dict[str, object], details: List[Dict[str, object]]) -> List[Dict[str, object]]:
    filters = [item for item in _list(pack_216.get("saved_view_filter_map_previews")) if isinstance(item, dict)]
    selected = filters[:7]
    detail_keys = [item.get("selected_preset_key") for item in details]

    cards = []
    for sequence, filter_item in enumerate(selected, start=1):
        filter_key = filter_item.get("saved_view_filter_map_key") or f"filter_{sequence}"
        item = {
            "linked_filter_detail_card_preview_id": f"receipt_chain_saved_view_linked_filter_{_stable_hash((PACK_ID, filter_key), 18)}",
            "linked_filter_detail_key": filter_key,
            "label": f"Linked Filter: {filter_item.get('label') or filter_key}",
            "filter_type": filter_item.get("filter_type") or "unknown",
            "sequence": sequence,
            "filter_value_count": filter_item.get("filter_value_count"),
            "filter_values_preview": filter_item.get("filter_values") or [],
            "linked_selected_preset_keys": detail_keys,
            "linked_selected_preset_count": len(detail_keys),
            "linked_filter_detail_save_allowed_now": False,
            "card_status": "receipt_chain_saved_view_linked_filter_detail_preview_ready",
            "card_result_type": "tower_receipt_chain_saved_view_linked_filter_detail_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        cards.append(item)

    return cards


def _build_linked_scope_details(pack_216: Dict[str, object], details: List[Dict[str, object]]) -> List[Dict[str, object]]:
    scopes = [item for item in _list(pack_216.get("saved_view_scope_card_previews")) if isinstance(item, dict)]
    selected = scopes[:6]
    detail_keys = [item.get("selected_preset_key") for item in details]

    cards = []
    for sequence, scope in enumerate(selected, start=1):
        scope_key = scope.get("saved_view_scope_key") or f"scope_{sequence}"
        item = {
            "linked_scope_detail_card_preview_id": f"receipt_chain_saved_view_linked_scope_{_stable_hash((PACK_ID, scope_key), 18)}",
            "linked_scope_detail_key": scope_key,
            "label": f"Linked Scope: {scope.get('label') or scope_key}",
            "scope_type": scope.get("scope_type") or "unknown",
            "sequence": sequence,
            "source_item_count": scope.get("source_item_count"),
            "linked_selected_preset_keys": detail_keys,
            "linked_selected_preset_count": len(detail_keys),
            "linked_filter_map_count": scope.get("linked_filter_map_count"),
            "linked_scope_detail_save_allowed_now": False,
            "card_status": "receipt_chain_saved_view_linked_scope_detail_preview_ready",
            "card_result_type": "tower_receipt_chain_saved_view_linked_scope_detail_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        cards.append(item)

    return cards


def _build_detail_actions(details, rows, filter_details, scope_details) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_saved_view_detail_status", "Preview saved view detail status", True, "Preview saved view detail health."),
        ("preview_selected_preset_detail", "Preview selected preset detail", True, "Preview safe selected preset details."),
        ("open_pack_216_saved_view_presets", "Open Pack 216 saved view presets", True, "Open Pack 216 JSON."),
        ("blocked_save_detail_state", "Save detail state", False, "Blocked: real detail state persistence is not enabled in Pack 217."),
        ("blocked_apply_saved_view", "Apply saved view", False, "Blocked: real saved view application is not enabled in Pack 217."),
        ("blocked_edit_saved_view_detail", "Edit saved view detail", False, "Blocked: real saved view edit is not enabled in Pack 217."),
        ("blocked_export_saved_view_detail", "Export saved view detail", False, "Blocked: real saved view export is not enabled in Pack 217."),
        ("blocked_reveal_raw_evidence", "Reveal raw evidence", False, "Blocked: raw evidence reveal is not enabled in Pack 217."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        item = {
            "saved_view_detail_action_menu_item_preview_id": f"receipt_chain_saved_view_detail_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "saved_view_detail_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "selected_preset_detail_count": len(details),
            "field_detail_row_count": len(rows),
            "linked_filter_detail_count": len(filter_details),
            "linked_scope_detail_count": len(scope_details),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_saved_view_detail_action": False,
            "action_status": "receipt_chain_saved_view_detail_action_preview_ready" if allowed else "receipt_chain_saved_view_detail_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_saved_view_detail_action_menu_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        actions.append(item)

    return actions


def _build_owner_detail_queue(details, rows, filter_details, scope_details, actions) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_selected_preset_details", "Review selected preset details", "detail_review", len(details)),
        ("review_field_detail_rows", "Review field detail rows", "field_review", len(rows)),
        ("review_linked_filters", "Review linked filters", "filter_review", len(filter_details)),
        ("review_linked_scopes", "Review linked scopes", "scope_review", len(scope_details)),
        ("prepare_pack_218_saved_view_edit", "Prepare Pack 218 saved view edit", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_saved_view_detail_queue_item_preview_id": f"receipt_chain_owner_saved_view_detail_queue_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_owner_saved_view_detail_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_saved_view_detail_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(details, rows, filter_details, scope_details, actions, queue) -> Dict[str, object]:
    all_items = details + rows + filter_details + scope_details + actions + queue

    summary = {
        "saved_view_detail_safety_summary_id": f"receipt_chain_saved_view_detail_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "selected_preset_detail_count": len(details),
        "preset_field_detail_row_count": len(rows),
        "linked_filter_detail_card_count": len(filter_details),
        "linked_scope_detail_card_count": len(scope_details),
        "saved_view_detail_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_saved_view_detail_queue_item_count": len(queue),
        "real_saved_view_written_count": 0,
        "real_saved_view_edited_count": 0,
        "real_saved_view_deleted_count": 0,
        "real_saved_view_applied_count": 0,
        "real_saved_view_exported_count": 0,
        "real_detail_state_persisted_count": 0,
        "real_detail_selection_saved_count": 0,
        "real_field_detail_saved_count": 0,
        "real_linked_filter_detail_saved_count": 0,
        "real_linked_scope_detail_saved_count": 0,
        "real_user_preference_written_count": 0,
        "real_navigation_state_persisted_count": 0,
        "real_owner_review_saved_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_details_preview_only": all(item.get("selected_preset_detail_preview_only") is True for item in details),
        "all_rows_preview_only": all(item.get("preset_field_detail_preview_only") is True for item in rows),
        "all_filter_details_preview_only": all(item.get("linked_filter_detail_preview_only") is True for item in filter_details),
        "all_scope_details_preview_only": all(item.get("linked_scope_detail_preview_only") is True for item in scope_details),
        "all_actions_preview_only": all(item.get("saved_view_detail_action_menu_preview_only") is True for item in actions),
        "all_queue_preview_only": all(item.get("owner_saved_view_detail_queue_preview_only") is True for item in queue),
        "all_saved_view_detail_writes_blocked": True,
        "all_raw_evidence_reveal_blocked": True,
        "summary_status": "receipt_chain_saved_view_detail_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_saved_view_detail_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("selected_preset_detail_count") == 7
        and safety.get("preset_field_detail_row_count") == 8
        and safety.get("linked_filter_detail_card_count") == 7
        and safety.get("linked_scope_detail_card_count") == 6
        and safety.get("saved_view_detail_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_saved_view_detail_queue_item_count") == 5
        and safety.get("real_saved_view_written_count") == 0
        and safety.get("real_saved_view_edited_count") == 0
        and safety.get("real_saved_view_applied_count") == 0
        and safety.get("real_detail_state_persisted_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "saved_view_detail_checkpoint_id": f"receipt_chain_saved_view_detail_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_saved_view_detail_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_saved_view_detail_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_saved_view_detail_checkpoint_preview",
        "safe_to_continue_to_pack_218": checkpoint_ok,
        "save_batch": "216-220",
        "save_after_pack": 220,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(details, rows, filter_details, scope_details, actions, queue, checkpoint) -> Dict[str, object]:
    indexes = {
        "selected_preset_details_by_id": {},
        "selected_preset_details_by_key": {},
        "field_detail_rows_by_id": {},
        "field_detail_rows_by_key": {},
        "linked_filter_details_by_id": {},
        "linked_filter_details_by_key": {},
        "linked_scope_details_by_id": {},
        "linked_scope_details_by_key": {},
        "actions_by_id": {},
        "actions_by_key": {},
        "owner_detail_queue_by_id": {},
        "owner_detail_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in details:
        indexes["selected_preset_details_by_id"][item.get("selected_preset_detail_preview_id")] = item
        indexes["selected_preset_details_by_key"][item.get("selected_preset_key")] = item

    for item in rows:
        indexes["field_detail_rows_by_id"][item.get("preset_field_detail_row_preview_id")] = item
        indexes["field_detail_rows_by_key"][item.get("preset_field_detail_key")] = item

    for item in filter_details:
        indexes["linked_filter_details_by_id"][item.get("linked_filter_detail_card_preview_id")] = item
        indexes["linked_filter_details_by_key"][item.get("linked_filter_detail_key")] = item

    for item in scope_details:
        indexes["linked_scope_details_by_id"][item.get("linked_scope_detail_card_preview_id")] = item
        indexes["linked_scope_details_by_key"][item.get("linked_scope_detail_key")] = item

    for item in actions:
        indexes["actions_by_id"][item.get("saved_view_detail_action_menu_item_preview_id")] = item
        indexes["actions_by_key"][item.get("saved_view_detail_action_key")] = item

    for item in queue:
        indexes["owner_detail_queue_by_id"][item.get("owner_saved_view_detail_queue_item_preview_id")] = item
        indexes["owner_detail_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("saved_view_detail_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_saved_view_detail_v217_payload_cached() -> Dict[str, object]:
    pack_216 = _load_pack_216_payload(force_refresh=True)

    details = _build_selected_preset_details(pack_216)
    rows = _build_field_detail_rows(details)
    filter_details = _build_linked_filter_details(pack_216, details)
    scope_details = _build_linked_scope_details(pack_216, details)
    actions = _build_detail_actions(details, rows, filter_details, scope_details)
    queue = _build_owner_detail_queue(details, rows, filter_details, scope_details, actions)
    safety = _build_safety_summary(details, rows, filter_details, scope_details, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(details, rows, filter_details, scope_details, actions, queue, checkpoint)

    all_items = details + rows + filter_details + scope_details + actions + queue

    readiness_checks = {
        "pack_216_ready": pack_216.get("status") == "ready",
        "pack_216_safe_to_continue": pack_216.get("summary", {}).get("safe_to_continue_to_pack_217") is True,
        "has_selected_preset_details": len(details) == 7,
        "has_field_detail_rows": len(rows) == 8,
        "has_linked_filter_details": len(filter_details) == 7,
        "has_linked_scope_details": len(scope_details) == 6,
        "has_detail_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_detail_queue": len(queue) == 5,
        "all_details_ready": all(item.get("detail_status") == "receipt_chain_saved_view_selected_preset_detail_preview_ready" for item in details),
        "all_rows_ready": all(item.get("row_status") == "receipt_chain_saved_view_preset_field_detail_row_preview_ready" for item in rows),
        "all_filter_details_ready": all(item.get("card_status") == "receipt_chain_saved_view_linked_filter_detail_preview_ready" for item in filter_details),
        "all_scope_details_ready": all(item.get("card_status") == "receipt_chain_saved_view_linked_scope_detail_preview_ready" for item in scope_details),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_saved_view_detail_action_preview_ready", "receipt_chain_saved_view_detail_action_preview_blocked"} for item in actions),
        "all_queue_blocked": all(item.get("queue_status") == "receipt_chain_owner_saved_view_detail_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_saved_view_detail_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_saved_view_detail_checkpoint_preview_ready",
        "safe_to_continue_to_pack_218": checkpoint.get("safe_to_continue_to_pack_218") is True,
        "indexes_present": bool(indexes.get("selected_preset_details_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_saved_view_detail_preview_only": all(item.get("saved_view_detail_preview_only") is True for item in all_items),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in all_items),
        "no_real_saved_view_edited": all(item.get("real_saved_view_edited") is False for item in all_items),
        "no_real_saved_view_deleted": all(item.get("real_saved_view_deleted") is False for item in all_items),
        "no_real_saved_view_applied": all(item.get("real_saved_view_applied") is False for item in all_items),
        "no_real_saved_view_exported": all(item.get("real_saved_view_exported") is False for item in all_items),
        "no_real_detail_state_persisted": all(item.get("real_detail_state_persisted") is False for item in all_items),
        "no_real_detail_selection_saved": all(item.get("real_detail_selection_saved") is False for item in all_items),
        "no_real_field_detail_saved": all(item.get("real_field_detail_saved") is False for item in all_items),
        "no_real_linked_filter_detail_saved": all(item.get("real_linked_filter_detail_saved") is False for item in all_items),
        "no_real_linked_scope_detail_saved": all(item.get("real_linked_scope_detail_saved") is False for item in all_items),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in all_items),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in all_items),
        "no_real_owner_review_saved": all(item.get("real_owner_review_saved") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_detail_writes_blocked": all(item.get("detail_state_persistence_allowed_now") is False for item in all_items),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 217,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Saved View Detail Drawer Preview",
        "endpoint": SAVED_VIEW_DETAIL_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_216": {
            "status": pack_216.get("status"),
            "readiness_score": pack_216.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_217": pack_216.get("summary", {}).get("safe_to_continue_to_pack_217"),
            "save_batch": pack_216.get("summary", {}).get("save_batch"),
        },
        "summary": {
            "selected_preset_detail_count": len(details),
            "preset_field_detail_row_count": len(rows),
            "linked_filter_detail_card_count": len(filter_details),
            "linked_scope_detail_card_count": len(scope_details),
            "saved_view_detail_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_saved_view_detail_queue_item_count": len(queue),
            "real_saved_view_written_count": safety.get("real_saved_view_written_count"),
            "real_saved_view_edited_count": safety.get("real_saved_view_edited_count"),
            "real_saved_view_deleted_count": safety.get("real_saved_view_deleted_count"),
            "real_saved_view_applied_count": safety.get("real_saved_view_applied_count"),
            "real_saved_view_exported_count": safety.get("real_saved_view_exported_count"),
            "real_detail_state_persisted_count": safety.get("real_detail_state_persisted_count"),
            "real_detail_selection_saved_count": safety.get("real_detail_selection_saved_count"),
            "real_field_detail_saved_count": safety.get("real_field_detail_saved_count"),
            "real_linked_filter_detail_saved_count": safety.get("real_linked_filter_detail_saved_count"),
            "real_linked_scope_detail_saved_count": safety.get("real_linked_scope_detail_saved_count"),
            "real_user_preference_written_count": safety.get("real_user_preference_written_count"),
            "real_navigation_state_persisted_count": safety.get("real_navigation_state_persisted_count"),
            "real_owner_review_saved_count": safety.get("real_owner_review_saved_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_218": checkpoint.get("safe_to_continue_to_pack_218"),
            "save_batch": "216-220",
            "save_after_pack": 220,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain saved view detail preview ready" if readiness_score == 100 else "Receipt chain saved view detail preview needs review",
        },
        "readiness_checks": readiness_checks,
        "selected_preset_detail_previews": details,
        "preset_field_detail_row_previews": rows,
        "linked_filter_detail_card_previews": filter_details,
        "linked_scope_detail_card_previews": scope_details,
        "saved_view_detail_action_menu_previews": actions,
        "owner_saved_view_detail_queue_previews": queue,
        "saved_view_detail_safety_summary": safety,
        "saved_view_detail_checkpoint": checkpoint,
        "saved_view_detail_indexes": indexes,
    }


def build_receipt_chain_saved_view_detail_v217_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_saved_view_detail_v217_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_saved_view_detail_v217_payload_cached())


def get_receipt_chain_saved_view_detail_v217_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_detail_v217_payload(force_refresh=force_refresh)


def build_receipt_chain_saved_view_detail_v217_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_detail_v217_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 217,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "selected_preset_detail_count": summary.get("selected_preset_detail_count"),
        "preset_field_detail_row_count": summary.get("preset_field_detail_row_count"),
        "linked_filter_detail_card_count": summary.get("linked_filter_detail_card_count"),
        "linked_scope_detail_card_count": summary.get("linked_scope_detail_card_count"),
        "saved_view_detail_action_menu_item_count": summary.get("saved_view_detail_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_saved_view_detail_queue_item_count": summary.get("owner_saved_view_detail_queue_item_count"),
        "real_saved_view_written_count": summary.get("real_saved_view_written_count"),
        "real_saved_view_edited_count": summary.get("real_saved_view_edited_count"),
        "real_saved_view_deleted_count": summary.get("real_saved_view_deleted_count"),
        "real_saved_view_applied_count": summary.get("real_saved_view_applied_count"),
        "real_saved_view_exported_count": summary.get("real_saved_view_exported_count"),
        "real_detail_state_persisted_count": summary.get("real_detail_state_persisted_count"),
        "real_detail_selection_saved_count": summary.get("real_detail_selection_saved_count"),
        "real_field_detail_saved_count": summary.get("real_field_detail_saved_count"),
        "real_linked_filter_detail_saved_count": summary.get("real_linked_filter_detail_saved_count"),
        "real_linked_scope_detail_saved_count": summary.get("real_linked_scope_detail_saved_count"),
        "real_user_preference_written_count": summary.get("real_user_preference_written_count"),
        "real_navigation_state_persisted_count": summary.get("real_navigation_state_persisted_count"),
        "real_owner_review_saved_count": summary.get("real_owner_review_saved_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_218": summary.get("safe_to_continue_to_pack_218"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_saved_view_detail_v217_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_detail_v217_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_saved_view_detail_v217_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_saved_view_detail_v217_status_bridge()
    action = {
        "id": "receipt_chain_saved_view_detail_v217",
        "label": "Receipt Chain Saved View Detail",
        "title": "Receipt Chain Saved View Detail Preview",
        "href": SAVED_VIEW_DETAIL_ENDPOINT,
        "endpoint": SAVED_VIEW_DETAIL_ENDPOINT,
        "description": "Preview selected preset details, field rows, linked filters, linked scopes, and blocked detail actions.",
        "status": bridge.get("status"),
        "pack": "Pack 217",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_saved_view_detail_v217_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_detail_v217_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_saved_view_detail_v217",
        "title": "Receipt Chain Saved View Detail",
        "subtitle": "Preview selected saved view preset detail, linked filters, scope cards, and blocked detail writes.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_DETAIL_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Detail readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "details", "title": "Preset details", "value": summary.get("selected_preset_detail_count"), "label": "Selected presets"},
            {"id": "fields", "title": "Field rows", "value": summary.get("preset_field_detail_row_count"), "label": "Safe values"},
            {"id": "filters", "title": "Linked filters", "value": summary.get("linked_filter_detail_card_count"), "label": "Filter detail"},
            {"id": "scopes", "title": "Linked scopes", "value": summary.get("linked_scope_detail_card_count"), "label": "Scope detail"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_saved_view_applied") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No apply/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_DETAIL_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_saved_view_detail_v217_payload",
    "get_receipt_chain_saved_view_detail_v217_payload",
    "build_receipt_chain_saved_view_detail_v217_status_bridge",
    "get_receipt_chain_saved_view_detail_v217_status_bridge",
    "build_receipt_chain_saved_view_detail_v217_quick_action",
    "build_receipt_chain_saved_view_detail_v217_unified_owner_section",
]
