
"""
PACK 216 - Receipt Chain Saved View Presets Preview.

Short module filename:
    tower.receipt_chain_saved_view_presets_v216

This module sits on top of Pack 215.

Pack 215 closed the recovered 208-215 checkpoint batch.
Pack 216 begins the 216-220 batch with saved view preset previews:
- checkpoint saved view preset cards
- preset filter maps
- preset scope cards
- preset action menu
- owner saved view review queue
- no real saved view writes
- no real user preference writes
- no real exports
- no raw evidence reveal

Important:
- simulated-only
- saved-view-preset-preview-only
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
from typing import Any, Dict, List, Tuple


PACK_ID = "PACK_216"
SAVED_VIEW_PRESETS_ENDPOINT = "/tower/receipt-chain-saved-view-presets-v216.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "saved_view_preset_preview_only": True,
        "saved_view_filter_map_preview_only": True,
        "saved_view_scope_card_preview_only": True,
        "saved_view_action_menu_preview_only": True,
        "owner_saved_view_review_queue_preview_only": True,
        "batch_checkpoint_preview_only": True,
        "source_pack_readiness_preview_only": True,
        "recovered_dependency_awareness_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "saved_view_write_allowed_now": False,
        "saved_view_edit_allowed_now": False,
        "saved_view_delete_allowed_now": False,
        "saved_view_apply_allowed_now": False,
        "saved_view_export_allowed_now": False,
        "filter_map_save_allowed_now": False,
        "scope_card_save_allowed_now": False,
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
        "real_filter_map_saved": False,
        "real_scope_card_saved": False,
        "real_user_preference_written": False,
        "real_navigation_state_persisted": False,
        "real_owner_review_saved": False,
        "real_archive_written": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_215_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_batch_211_215_checkpoint_v215")
        fn = getattr(mod, "build_receipt_chain_batch_211_215_checkpoint_v215_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_215",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_216": False},
            "source_pack_readiness_cards": [],
            "recovered_dependency_awareness_cards": [],
            "next_batch_handoff_previews": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_215",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_216": False},
        "source_pack_readiness_cards": [],
        "recovered_dependency_awareness_cards": [],
        "next_batch_handoff_previews": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_saved_view_presets(pack_215: Dict[str, object]) -> List[Dict[str, object]]:
    preset_defs = [
        ("all_recovered_checkpoint_packs", "All recovered checkpoint packs", "batch", "208-215"),
        ("batch_211_215_only", "Batch 211-215 only", "batch", "211-215"),
        ("recovered_dependencies_208_210", "Recovered dependencies 208-210", "dependency", "208-210"),
        ("ready_only_checkpoint_packs", "Ready checkpoint packs only", "status", "ready"),
        ("no_real_action_safety_view", "No real action safety view", "safety", "real_flags_zero"),
        ("raw_redaction_view", "Raw redaction view", "redaction", "raw_reveal_zero"),
        ("next_batch_216_220_handoff", "Next batch 216-220 handoff", "next_batch", "216-220"),
    ]

    presets = []
    for sequence, (preset_key, label, preset_type, preset_value) in enumerate(preset_defs, start=1):
        preset = {
            "saved_view_preset_preview_id": f"receipt_chain_saved_view_preset_{_stable_hash((PACK_ID, preset_key), 18)}",
            "saved_view_preset_key": preset_key,
            "label": label,
            "preset_type": preset_type,
            "preset_value": preset_value,
            "sequence": sequence,
            "source_endpoint": SOURCE_ENDPOINT,
            "source_closed_batch": pack_215.get("summary", {}).get("closed_batch"),
            "source_save_batch": pack_215.get("summary", {}).get("save_batch"),
            "source_next_batch": pack_215.get("summary", {}).get("next_batch"),
            "source_safe_to_continue_to_pack_216": pack_215.get("summary", {}).get("safe_to_continue_to_pack_216"),
            "saved_view_write_allowed_now": False,
            "saved_view_edit_allowed_now": False,
            "saved_view_delete_allowed_now": False,
            "preset_status": "receipt_chain_saved_view_preset_preview_ready",
            "preset_result_type": "tower_receipt_chain_saved_view_preset_preview",
            "safe_preview_only": True,
        }
        preset.update(_base_flags())
        presets.append(preset)

    return presets


def _build_filter_maps(presets: List[Dict[str, object]]) -> List[Dict[str, object]]:
    filter_defs = [
        ("pack_range_filter", "Pack range filter", "pack_range", ["208-215", "211-215", "216-220"]),
        ("status_filter", "Status filter", "status", ["ready", "review"]),
        ("safety_filter", "Safety filter", "safety", ["real_flags_zero", "raw_reveal_zero", "raw_fields_zero"]),
        ("dependency_filter", "Recovered dependency filter", "dependency", ["208-210", "211-215"]),
        ("handoff_filter", "Next batch handoff filter", "handoff", ["216-220", "pack_217_detail"]),
        ("owner_review_filter", "Owner review filter", "owner_review", ["blocked", "preview_only"]),
        ("route_wall_filter", "Route wall filter", "route_wall", ["guarded", "coverage_100"]),
    ]

    preset_keys = [item.get("saved_view_preset_key") for item in presets]

    maps = []
    for sequence, (filter_key, label, filter_type, values) in enumerate(filter_defs, start=1):
        item = {
            "saved_view_filter_map_preview_id": f"receipt_chain_saved_view_filter_map_{_stable_hash((PACK_ID, filter_key), 18)}",
            "saved_view_filter_map_key": filter_key,
            "label": label,
            "filter_type": filter_type,
            "filter_values": values,
            "filter_value_count": len(values),
            "sequence": sequence,
            "linked_saved_view_preset_keys": preset_keys,
            "linked_saved_view_preset_count": len(preset_keys),
            "filter_map_save_allowed_now": False,
            "filter_map_status": "receipt_chain_saved_view_filter_map_preview_ready",
            "filter_map_result_type": "tower_receipt_chain_saved_view_filter_map_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        maps.append(item)

    return maps


def _build_scope_cards(pack_215: Dict[str, object], presets: List[Dict[str, object]], filter_maps: List[Dict[str, object]]) -> List[Dict[str, object]]:
    source_cards = _list(pack_215.get("source_pack_readiness_cards"))
    recovered_cards = _list(pack_215.get("recovered_dependency_awareness_cards"))
    handoffs = _list(pack_215.get("next_batch_handoff_previews"))

    scope_defs = [
        ("source_pack_scope", "Source pack scope", "source_pack", len(source_cards)),
        ("recovered_dependency_scope", "Recovered dependency scope", "recovered_dependency", len(recovered_cards)),
        ("safety_rollup_scope", "Safety rollup scope", "safety_rollup", 1),
        ("save_push_scope", "Save/push scope", "save_push", 1),
        ("next_batch_handoff_scope", "Next batch handoff scope", "next_batch", len(handoffs)),
        ("owner_navigation_scope", "Owner navigation scope", "navigation", len(presets)),
    ]

    preset_keys = [item.get("saved_view_preset_key") for item in presets]
    filter_keys = [item.get("saved_view_filter_map_key") for item in filter_maps]

    scopes = []
    for sequence, (scope_key, label, scope_type, source_count) in enumerate(scope_defs, start=1):
        item = {
            "saved_view_scope_card_preview_id": f"receipt_chain_saved_view_scope_{_stable_hash((PACK_ID, scope_key), 18)}",
            "saved_view_scope_key": scope_key,
            "label": label,
            "scope_type": scope_type,
            "sequence": sequence,
            "source_item_count": int(source_count or 0),
            "linked_saved_view_preset_keys": preset_keys,
            "linked_saved_view_preset_count": len(preset_keys),
            "linked_filter_map_keys": filter_keys,
            "linked_filter_map_count": len(filter_keys),
            "scope_card_save_allowed_now": False,
            "scope_status": "receipt_chain_saved_view_scope_card_preview_ready",
            "scope_result_type": "tower_receipt_chain_saved_view_scope_card_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        scopes.append(item)

    return scopes


def _build_saved_view_actions(presets: List[Dict[str, object]], filter_maps: List[Dict[str, object]], scopes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_saved_view_status", "Preview saved view status", True, "Preview saved view preset health."),
        ("preview_filter_maps", "Preview filter maps", True, "Preview filter map lanes."),
        ("open_pack_215_batch_checkpoint", "Open Pack 215 batch checkpoint", True, "Open Pack 215 JSON."),
        ("blocked_save_saved_view", "Save saved view", False, "Blocked: real saved view writes are not enabled in Pack 216."),
        ("blocked_edit_saved_view", "Edit saved view", False, "Blocked: real saved view edits are not enabled in Pack 216."),
        ("blocked_delete_saved_view", "Delete saved view", False, "Blocked: real saved view deletion is not enabled in Pack 216."),
        ("blocked_export_saved_view", "Export saved view", False, "Blocked: real saved view export is not enabled in Pack 216."),
        ("blocked_reveal_raw_evidence", "Reveal raw evidence", False, "Blocked: raw evidence reveal is not enabled in Pack 216."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        item = {
            "saved_view_action_menu_item_preview_id": f"receipt_chain_saved_view_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "saved_view_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "saved_view_preset_count": len(presets),
            "filter_map_count": len(filter_maps),
            "scope_card_count": len(scopes),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_saved_view_action": False,
            "action_status": "receipt_chain_saved_view_action_preview_ready" if allowed else "receipt_chain_saved_view_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_saved_view_action_menu_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        actions.append(item)

    return actions


def _build_owner_saved_view_queue(presets, filter_maps, scopes, actions) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_saved_view_presets", "Review saved view presets", "preset_review", len(presets)),
        ("review_filter_maps", "Review filter maps", "filter_review", len(filter_maps)),
        ("review_scope_cards", "Review scope cards", "scope_review", len(scopes)),
        ("review_blocked_saved_view_actions", "Review blocked saved view actions", "action_review", sum(1 for item in actions if item.get("blocked_in_preview") is True)),
        ("prepare_pack_217_saved_view_detail", "Prepare Pack 217 saved view detail", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_saved_view_queue_item_preview_id": f"receipt_chain_owner_saved_view_queue_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_owner_saved_view_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_saved_view_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(presets, filter_maps, scopes, actions, queue) -> Dict[str, object]:
    all_items = presets + filter_maps + scopes + actions + queue

    summary = {
        "saved_view_preset_safety_summary_id": f"receipt_chain_saved_view_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "saved_view_preset_count": len(presets),
        "filter_map_count": len(filter_maps),
        "scope_card_count": len(scopes),
        "saved_view_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_saved_view_queue_item_count": len(queue),
        "real_saved_view_written_count": 0,
        "real_saved_view_edited_count": 0,
        "real_saved_view_deleted_count": 0,
        "real_saved_view_applied_count": 0,
        "real_saved_view_exported_count": 0,
        "real_filter_map_saved_count": 0,
        "real_scope_card_saved_count": 0,
        "real_user_preference_written_count": 0,
        "real_navigation_state_persisted_count": 0,
        "real_owner_review_saved_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_presets_preview_only": all(item.get("saved_view_preset_preview_only") is True for item in presets),
        "all_filter_maps_preview_only": all(item.get("saved_view_filter_map_preview_only") is True for item in filter_maps),
        "all_scope_cards_preview_only": all(item.get("saved_view_scope_card_preview_only") is True for item in scopes),
        "all_actions_preview_only": all(item.get("saved_view_action_menu_preview_only") is True for item in actions),
        "all_queue_preview_only": all(item.get("owner_saved_view_review_queue_preview_only") is True for item in queue),
        "all_saved_view_writes_blocked": True,
        "all_raw_evidence_reveal_blocked": True,
        "summary_status": "receipt_chain_saved_view_preset_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_saved_view_preset_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("saved_view_preset_count") == 7
        and safety.get("filter_map_count") == 7
        and safety.get("scope_card_count") == 6
        and safety.get("saved_view_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_saved_view_queue_item_count") == 5
        and safety.get("real_saved_view_written_count") == 0
        and safety.get("real_saved_view_edited_count") == 0
        and safety.get("real_saved_view_deleted_count") == 0
        and safety.get("real_saved_view_exported_count") == 0
        and safety.get("real_user_preference_written_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "saved_view_preset_checkpoint_id": f"receipt_chain_saved_view_preset_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_saved_view_preset_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_saved_view_preset_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_saved_view_preset_checkpoint_preview",
        "safe_to_continue_to_pack_217": checkpoint_ok,
        "save_batch": "216-220",
        "save_after_pack": 220,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(presets, filter_maps, scopes, actions, queue, checkpoint) -> Dict[str, object]:
    indexes = {
        "saved_view_presets_by_id": {},
        "saved_view_presets_by_key": {},
        "filter_maps_by_id": {},
        "filter_maps_by_key": {},
        "scope_cards_by_id": {},
        "scope_cards_by_key": {},
        "actions_by_id": {},
        "actions_by_key": {},
        "owner_saved_view_queue_by_id": {},
        "owner_saved_view_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in presets:
        indexes["saved_view_presets_by_id"][item.get("saved_view_preset_preview_id")] = item
        indexes["saved_view_presets_by_key"][item.get("saved_view_preset_key")] = item

    for item in filter_maps:
        indexes["filter_maps_by_id"][item.get("saved_view_filter_map_preview_id")] = item
        indexes["filter_maps_by_key"][item.get("saved_view_filter_map_key")] = item

    for item in scopes:
        indexes["scope_cards_by_id"][item.get("saved_view_scope_card_preview_id")] = item
        indexes["scope_cards_by_key"][item.get("saved_view_scope_key")] = item

    for item in actions:
        indexes["actions_by_id"][item.get("saved_view_action_menu_item_preview_id")] = item
        indexes["actions_by_key"][item.get("saved_view_action_key")] = item

    for item in queue:
        indexes["owner_saved_view_queue_by_id"][item.get("owner_saved_view_queue_item_preview_id")] = item
        indexes["owner_saved_view_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("saved_view_preset_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_saved_view_presets_v216_payload_cached() -> Dict[str, object]:
    pack_215 = _load_pack_215_payload(force_refresh=True)

    presets = _build_saved_view_presets(pack_215)
    filter_maps = _build_filter_maps(presets)
    scopes = _build_scope_cards(pack_215, presets, filter_maps)
    actions = _build_saved_view_actions(presets, filter_maps, scopes)
    queue = _build_owner_saved_view_queue(presets, filter_maps, scopes, actions)
    safety = _build_safety_summary(presets, filter_maps, scopes, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(presets, filter_maps, scopes, actions, queue, checkpoint)

    all_items = presets + filter_maps + scopes + actions + queue

    readiness_checks = {
        "pack_215_ready": pack_215.get("status") == "ready",
        "pack_215_safe_to_continue": pack_215.get("summary", {}).get("safe_to_continue_to_pack_216") is True,
        "has_saved_view_presets": len(presets) == 7,
        "has_filter_maps": len(filter_maps) == 7,
        "has_scope_cards": len(scopes) == 6,
        "has_saved_view_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_saved_view_queue": len(queue) == 5,
        "all_presets_ready": all(item.get("preset_status") == "receipt_chain_saved_view_preset_preview_ready" for item in presets),
        "all_filter_maps_ready": all(item.get("filter_map_status") == "receipt_chain_saved_view_filter_map_preview_ready" for item in filter_maps),
        "all_scope_cards_ready": all(item.get("scope_status") == "receipt_chain_saved_view_scope_card_preview_ready" for item in scopes),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_saved_view_action_preview_ready", "receipt_chain_saved_view_action_preview_blocked"} for item in actions),
        "all_queue_blocked": all(item.get("queue_status") == "receipt_chain_owner_saved_view_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_saved_view_preset_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_saved_view_preset_checkpoint_preview_ready",
        "safe_to_continue_to_pack_217": checkpoint.get("safe_to_continue_to_pack_217") is True,
        "indexes_present": bool(indexes.get("saved_view_presets_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_saved_view_preset_preview_only": all(item.get("saved_view_preset_preview_only") is True for item in all_items),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in all_items),
        "no_real_saved_view_edited": all(item.get("real_saved_view_edited") is False for item in all_items),
        "no_real_saved_view_deleted": all(item.get("real_saved_view_deleted") is False for item in all_items),
        "no_real_saved_view_exported": all(item.get("real_saved_view_exported") is False for item in all_items),
        "no_real_filter_map_saved": all(item.get("real_filter_map_saved") is False for item in all_items),
        "no_real_scope_card_saved": all(item.get("real_scope_card_saved") is False for item in all_items),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in all_items),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in all_items),
        "no_real_owner_review_saved": all(item.get("real_owner_review_saved") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in all_items),
        "all_user_preference_writes_blocked": all(item.get("user_preference_write_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 216,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Saved View Presets Preview",
        "endpoint": SAVED_VIEW_PRESETS_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_215": {
            "status": pack_215.get("status"),
            "readiness_score": pack_215.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_216": pack_215.get("summary", {}).get("safe_to_continue_to_pack_216"),
            "closed_batch": pack_215.get("summary", {}).get("closed_batch"),
            "save_batch": pack_215.get("summary", {}).get("save_batch"),
            "next_batch": pack_215.get("summary", {}).get("next_batch"),
        },
        "summary": {
            "saved_view_preset_count": len(presets),
            "filter_map_count": len(filter_maps),
            "scope_card_count": len(scopes),
            "saved_view_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_saved_view_queue_item_count": len(queue),
            "real_saved_view_written_count": safety.get("real_saved_view_written_count"),
            "real_saved_view_edited_count": safety.get("real_saved_view_edited_count"),
            "real_saved_view_deleted_count": safety.get("real_saved_view_deleted_count"),
            "real_saved_view_applied_count": safety.get("real_saved_view_applied_count"),
            "real_saved_view_exported_count": safety.get("real_saved_view_exported_count"),
            "real_filter_map_saved_count": safety.get("real_filter_map_saved_count"),
            "real_scope_card_saved_count": safety.get("real_scope_card_saved_count"),
            "real_user_preference_written_count": safety.get("real_user_preference_written_count"),
            "real_navigation_state_persisted_count": safety.get("real_navigation_state_persisted_count"),
            "real_owner_review_saved_count": safety.get("real_owner_review_saved_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_217": checkpoint.get("safe_to_continue_to_pack_217"),
            "save_batch": "216-220",
            "save_after_pack": 220,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain saved view presets preview ready" if readiness_score == 100 else "Receipt chain saved view presets preview needs review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_preset_previews": presets,
        "saved_view_filter_map_previews": filter_maps,
        "saved_view_scope_card_previews": scopes,
        "saved_view_action_menu_previews": actions,
        "owner_saved_view_review_queue_previews": queue,
        "saved_view_preset_safety_summary": safety,
        "saved_view_preset_checkpoint": checkpoint,
        "saved_view_preset_indexes": indexes,
    }


def build_receipt_chain_saved_view_presets_v216_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_saved_view_presets_v216_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_saved_view_presets_v216_payload_cached())


def get_receipt_chain_saved_view_presets_v216_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_presets_v216_payload(force_refresh=force_refresh)


def build_receipt_chain_saved_view_presets_v216_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_presets_v216_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 216,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "saved_view_preset_count": summary.get("saved_view_preset_count"),
        "filter_map_count": summary.get("filter_map_count"),
        "scope_card_count": summary.get("scope_card_count"),
        "saved_view_action_menu_item_count": summary.get("saved_view_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_saved_view_queue_item_count": summary.get("owner_saved_view_queue_item_count"),
        "real_saved_view_written_count": summary.get("real_saved_view_written_count"),
        "real_saved_view_edited_count": summary.get("real_saved_view_edited_count"),
        "real_saved_view_deleted_count": summary.get("real_saved_view_deleted_count"),
        "real_saved_view_applied_count": summary.get("real_saved_view_applied_count"),
        "real_saved_view_exported_count": summary.get("real_saved_view_exported_count"),
        "real_filter_map_saved_count": summary.get("real_filter_map_saved_count"),
        "real_scope_card_saved_count": summary.get("real_scope_card_saved_count"),
        "real_user_preference_written_count": summary.get("real_user_preference_written_count"),
        "real_navigation_state_persisted_count": summary.get("real_navigation_state_persisted_count"),
        "real_owner_review_saved_count": summary.get("real_owner_review_saved_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_217": summary.get("safe_to_continue_to_pack_217"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_saved_view_presets_v216_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_presets_v216_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_saved_view_presets_v216_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_saved_view_presets_v216_status_bridge()
    action = {
        "id": "receipt_chain_saved_view_presets_v216",
        "label": "Receipt Chain Saved View Presets",
        "title": "Receipt Chain Saved View Presets Preview",
        "href": SAVED_VIEW_PRESETS_ENDPOINT,
        "endpoint": SAVED_VIEW_PRESETS_ENDPOINT,
        "description": "Preview saved view presets, filter maps, scope cards, and blocked saved-view actions.",
        "status": bridge.get("status"),
        "pack": "Pack 216",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_saved_view_presets_v216_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_presets_v216_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_saved_view_presets_v216",
        "title": "Receipt Chain Saved View Presets",
        "subtitle": "Preview saved view presets, filter maps, scope cards, and blocked saved-view writes.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_PRESETS_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Preset readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "presets", "title": "Saved presets", "value": summary.get("saved_view_preset_count"), "label": "Preview only"},
            {"id": "filters", "title": "Filter maps", "value": summary.get("filter_map_count"), "label": "Safe filters"},
            {"id": "scopes", "title": "Scope cards", "value": summary.get("scope_card_count"), "label": "Batch scope"},
            {"id": "blocked", "title": "Blocked actions", "value": summary.get("blocked_action_count"), "label": "No write/delete"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_saved_view_written") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No persistence/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_PRESETS_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_saved_view_presets_v216_payload",
    "get_receipt_chain_saved_view_presets_v216_payload",
    "build_receipt_chain_saved_view_presets_v216_status_bridge",
    "get_receipt_chain_saved_view_presets_v216_status_bridge",
    "build_receipt_chain_saved_view_presets_v216_quick_action",
    "build_receipt_chain_saved_view_presets_v216_unified_owner_section",
]
