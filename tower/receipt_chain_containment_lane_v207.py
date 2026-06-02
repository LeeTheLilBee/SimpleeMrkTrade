
"""
PACK 207 - Receipt Chain Containment Lane Preview.

Short module filename:
    tower.receipt_chain_containment_lane_v207

This module sits on top of Pack 206.

Pack 206 opened the post-batch operational readiness board.
Pack 207 expands the containment readiness lane:
- containment trigger previews
- containment scope map previews
- blocked containment action menu
- owner containment review queue preview
- containment safety summary
- no real containment execution
- no real incident action
- no real archive write
- no real gateway grant
- no raw evidence reveal

Important:
- simulated-only
- containment-lane-preview-only
- containment actions blocked
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


PACK_ID = "PACK_207"
CONTAINMENT_LANE_ENDPOINT = "/tower/receipt-chain-containment-lane-v207.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-post-batch-ops-v206.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "containment_lane_preview_only": True,
        "containment_trigger_preview_only": True,
        "containment_scope_map_preview_only": True,
        "containment_action_menu_preview_only": True,
        "owner_containment_review_queue_preview_only": True,
        "post_batch_ops_preview_only": True,
        "operational_readiness_preview_only": True,
        "incident_lane_preview_only": True,
        "archive_lane_preview_only": True,
        "gateway_lane_preview_only": True,
        "owner_next_action_preview_only": True,
        "next_batch_board_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "containment_execution_allowed_now": False,
        "incident_action_allowed_now": False,
        "archive_write_allowed_now": False,
        "gateway_access_grant_allowed_now": False,
        "owner_next_action_execution_allowed_now": False,
        "owner_containment_review_execution_allowed_now": False,
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
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_expiration_enforced": False,
        "real_owner_followup_executed": False,
        "real_containment_executed": False,
        "real_containment_triggered": False,
        "real_containment_scope_applied": False,
        "real_containment_action_executed": False,
        "real_owner_containment_review_executed": False,
        "real_incident_action_executed": False,
        "real_archive_written": False,
        "real_gateway_access_granted": False,
        "real_owner_next_action_executed": False,
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


def _load_pack_206_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_post_batch_ops_v206")
        fn = getattr(mod, "build_receipt_chain_post_batch_ops_v206_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_206",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_207": False},
            "operational_readiness_lanes": [],
            "owner_next_action_previews": [],
            "source_checkpoint_map_items": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_206",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_207": False},
        "operational_readiness_lanes": [],
        "owner_next_action_previews": [],
        "source_checkpoint_map_items": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_containment_triggers(pack_206: Dict[str, object]) -> List[Dict[str, object]]:
    summary = pack_206.get("summary", {}) if isinstance(pack_206.get("summary"), dict) else {}

    trigger_defs = [
        ("route_wall_regression", "Route wall regression trigger", "route_wall", "Would watch for guarded-route coverage regression."),
        ("object_checkpoint_regression", "Object checkpoint regression trigger", "object_checkpoint", "Would watch for object permission checkpoint regression."),
        ("raw_evidence_request", "Raw evidence request trigger", "raw_evidence", "Would watch for raw evidence reveal attempts."),
        ("gateway_grant_attempt", "Gateway grant attempt trigger", "gateway", "Would watch for premature gateway access grant attempts."),
        ("archive_write_attempt", "Archive write attempt trigger", "archive", "Would watch for premature archive write attempts."),
        ("owner_action_execution_attempt", "Owner action execution attempt trigger", "owner_action", "Would watch for real owner action execution attempts."),
    ]

    triggers = []
    for sequence, (trigger_key, label, trigger_type, description) in enumerate(trigger_defs, start=1):
        trigger = {
            "containment_trigger_preview_id": f"receipt_chain_containment_trigger_{_stable_hash((PACK_ID, trigger_key), 18)}",
            "containment_trigger_key": trigger_key,
            "label": label,
            "trigger_type": trigger_type,
            "description": description,
            "sequence": sequence,
            "source_pack_206_ready": pack_206.get("status") == "ready",
            "source_pack_206_safe_to_continue": summary.get("safe_to_continue_to_pack_207") is True,
            "trigger_armed_in_preview": True,
            "trigger_executes_real_containment": False,
            "trigger_status": "receipt_chain_containment_trigger_preview_ready",
            "trigger_result_type": "tower_receipt_chain_containment_trigger_preview",
            "safe_preview_only": True,
        }
        trigger.update(_base_flags())
        triggers.append(trigger)

    return triggers


def _build_scope_maps(pack_206: Dict[str, object], triggers: List[Dict[str, object]]) -> List[Dict[str, object]]:
    source_map = [item for item in _list(pack_206.get("source_checkpoint_map_items")) if isinstance(item, dict)]
    trigger_keys = [trigger.get("containment_trigger_key") for trigger in triggers]

    scope_defs = [
        ("source_pack_scope", "Source pack scope", "source_packs", [item.get("source_pack_number") for item in source_map]),
        ("route_scope", "Route scope", "routes", ["pack_206_endpoint", "pack_207_endpoint_preview"]),
        ("evidence_scope", "Evidence scope", "evidence", ["redacted_packet", "source_checkpoint_map"]),
        ("owner_action_scope", "Owner action scope", "owner_actions", ["preview_actions", "blocked_actions"]),
        ("gateway_scope", "Gateway scope", "gateway", ["future_gateway_checks", "no_access_grants"]),
    ]

    scopes = []
    for sequence, (scope_key, label, scope_type, matched_items) in enumerate(scope_defs, start=1):
        scope = {
            "containment_scope_map_preview_id": f"receipt_chain_containment_scope_{_stable_hash((PACK_ID, scope_key), 18)}",
            "containment_scope_key": scope_key,
            "label": label,
            "scope_type": scope_type,
            "sequence": sequence,
            "matched_item_count": len(matched_items),
            "matched_items": matched_items,
            "mapped_trigger_keys": trigger_keys,
            "scope_applied_now": False,
            "scope_status": "receipt_chain_containment_scope_map_preview_ready",
            "scope_result_type": "tower_receipt_chain_containment_scope_map_preview",
            "safe_preview_only": True,
        }
        scope.update(_base_flags())
        scopes.append(scope)

    return scopes


def _build_containment_actions(triggers: List[Dict[str, object]], scopes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_containment_status", "Preview containment status", True, "Preview containment lane health."),
        ("preview_trigger_matrix", "Preview trigger matrix", True, "Preview trigger-to-scope mapping."),
        ("open_pack_206_ops", "Open Pack 206 post-batch ops", True, "Open Pack 206 JSON."),
        ("blocked_apply_soft_hold", "Apply soft hold", False, "Blocked: real soft hold not enabled in Pack 207."),
        ("blocked_quarantine_route", "Quarantine route", False, "Blocked: real route quarantine not enabled in Pack 207."),
        ("blocked_freeze_gateway", "Freeze gateway grant", False, "Blocked: real gateway freeze not enabled in Pack 207."),
        ("blocked_open_incident", "Open incident", False, "Blocked: real incident opening not enabled in Pack 207."),
        ("blocked_write_archive_notice", "Write archive notice", False, "Blocked: real archive write not enabled in Pack 207."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        action = {
            "containment_action_menu_item_preview_id": f"receipt_chain_containment_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "containment_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "trigger_count": len(triggers),
            "scope_count": len(scopes),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_containment": False,
            "action_status": "receipt_chain_containment_action_preview_ready" if allowed else "receipt_chain_containment_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_containment_action_menu_preview",
            "safe_preview_only": True,
        }
        action.update(_base_flags())
        actions.append(action)

    return actions


def _build_owner_review_queue(triggers: List[Dict[str, object]], actions: List[Dict[str, object]]) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_trigger_coverage", "Review trigger coverage", "trigger_review", len(triggers)),
        ("review_scope_boundaries", "Review scope boundaries", "scope_review", 5),
        ("review_blocked_actions", "Review blocked containment actions", "action_review", sum(1 for action in actions if action.get("blocked_in_preview") is True)),
        ("confirm_no_real_containment", "Confirm no real containment", "safety_review", 0),
        ("prepare_pack_208_incident_lane", "Prepare Pack 208 incident lane", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_containment_review_queue_item_preview_id": f"receipt_chain_containment_owner_review_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_containment_owner_review_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_containment_owner_review_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(triggers: List[Dict[str, object]], scopes: List[Dict[str, object]], actions: List[Dict[str, object]], queue: List[Dict[str, object]]) -> Dict[str, object]:
    all_items = triggers + scopes + actions + queue

    summary = {
        "containment_lane_safety_summary_id": f"receipt_chain_containment_lane_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "containment_trigger_count": len(triggers),
        "containment_scope_map_count": len(scopes),
        "containment_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_containment_review_queue_item_count": len(queue),
        "real_containment_executed_count": 0,
        "real_containment_triggered_count": 0,
        "real_containment_scope_applied_count": 0,
        "real_containment_action_executed_count": 0,
        "real_owner_containment_review_executed_count": 0,
        "real_incident_action_executed_count": 0,
        "real_archive_written_count": 0,
        "real_gateway_access_granted_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_triggers_preview_only": all(item.get("containment_trigger_preview_only") is True for item in triggers),
        "all_scopes_preview_only": all(item.get("containment_scope_map_preview_only") is True for item in scopes),
        "all_actions_preview_only": all(item.get("containment_action_menu_preview_only") is True for item in actions),
        "all_owner_reviews_preview_only": all(item.get("owner_containment_review_queue_preview_only") is True for item in queue),
        "all_real_containment_blocked": True,
        "summary_status": "receipt_chain_containment_lane_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_containment_lane_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("containment_trigger_count") == 6
        and safety.get("containment_scope_map_count") == 5
        and safety.get("containment_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_containment_review_queue_item_count") == 5
        and safety.get("real_containment_executed_count") == 0
        and safety.get("real_containment_triggered_count") == 0
        and safety.get("real_containment_scope_applied_count") == 0
        and safety.get("real_containment_action_executed_count") == 0
        and safety.get("real_incident_action_executed_count") == 0
        and safety.get("real_archive_written_count") == 0
        and safety.get("real_gateway_access_granted_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "containment_lane_checkpoint_id": f"receipt_chain_containment_lane_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_containment_lane_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_containment_lane_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_containment_lane_checkpoint_preview",
        "safe_to_continue_to_pack_208": checkpoint_ok,
        "save_batch": "206-210",
        "save_after_pack": 210,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(triggers: List[Dict[str, object]], scopes: List[Dict[str, object]], actions: List[Dict[str, object]], queue: List[Dict[str, object]], checkpoint: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "containment_triggers_by_id": {},
        "containment_triggers_by_key": {},
        "containment_triggers_by_type": {},
        "containment_scopes_by_id": {},
        "containment_scopes_by_key": {},
        "containment_actions_by_id": {},
        "containment_actions_by_key": {},
        "owner_review_queue_by_id": {},
        "owner_review_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in triggers:
        indexes["containment_triggers_by_id"][item.get("containment_trigger_preview_id")] = item
        indexes["containment_triggers_by_key"][item.get("containment_trigger_key")] = item
        indexes["containment_triggers_by_type"].setdefault(item.get("trigger_type"), []).append(item)

    for item in scopes:
        indexes["containment_scopes_by_id"][item.get("containment_scope_map_preview_id")] = item
        indexes["containment_scopes_by_key"][item.get("containment_scope_key")] = item

    for item in actions:
        indexes["containment_actions_by_id"][item.get("containment_action_menu_item_preview_id")] = item
        indexes["containment_actions_by_key"][item.get("containment_action_key")] = item

    for item in queue:
        indexes["owner_review_queue_by_id"][item.get("owner_containment_review_queue_item_preview_id")] = item
        indexes["owner_review_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("containment_lane_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_containment_lane_v207_payload_cached() -> Dict[str, object]:
    pack_206 = _load_pack_206_payload(force_refresh=True)

    triggers = _build_containment_triggers(pack_206)
    scopes = _build_scope_maps(pack_206, triggers)
    actions = _build_containment_actions(triggers, scopes)
    queue = _build_owner_review_queue(triggers, actions)
    safety = _build_safety_summary(triggers, scopes, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(triggers, scopes, actions, queue, checkpoint)

    all_items = triggers + scopes + actions + queue

    readiness_checks = {
        "pack_206_ready": pack_206.get("status") == "ready",
        "pack_206_safe_to_continue": pack_206.get("summary", {}).get("safe_to_continue_to_pack_207") is True,
        "has_containment_triggers": len(triggers) == 6,
        "has_containment_scopes": len(scopes) == 5,
        "has_containment_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_review_queue": len(queue) == 5,
        "all_triggers_ready": all(item.get("trigger_status") == "receipt_chain_containment_trigger_preview_ready" for item in triggers),
        "all_scopes_ready": all(item.get("scope_status") == "receipt_chain_containment_scope_map_preview_ready" for item in scopes),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_containment_action_preview_ready", "receipt_chain_containment_action_preview_blocked"} for item in actions),
        "all_owner_reviews_blocked": all(item.get("queue_status") == "receipt_chain_containment_owner_review_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_containment_lane_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_containment_lane_checkpoint_preview_ready",
        "safe_to_continue_to_pack_208": checkpoint.get("safe_to_continue_to_pack_208") is True,
        "indexes_present": bool(indexes.get("containment_triggers_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_containment_lane_preview_only": all(item.get("containment_lane_preview_only") is True for item in all_items),
        "no_real_containment_executed": all(item.get("real_containment_executed") is False for item in all_items),
        "no_real_containment_triggered": all(item.get("real_containment_triggered") is False for item in all_items),
        "no_real_containment_scope_applied": all(item.get("real_containment_scope_applied") is False for item in all_items),
        "no_real_containment_action_executed": all(item.get("real_containment_action_executed") is False for item in all_items),
        "no_real_owner_containment_review_executed": all(item.get("real_owner_containment_review_executed") is False for item in all_items),
        "no_real_incident_action_executed": all(item.get("real_incident_action_executed") is False for item in all_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in all_items),
        "no_real_gateway_access_granted": all(item.get("real_gateway_access_granted") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_containment_execution_blocked": all(item.get("containment_execution_allowed_now") is False for item in all_items),
        "all_incident_actions_blocked": all(item.get("incident_action_allowed_now") is False for item in all_items),
        "all_archive_writes_blocked": all(item.get("archive_write_allowed_now") is False for item in all_items),
        "all_gateway_access_grants_blocked": all(item.get("gateway_access_grant_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 207,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Containment Lane Preview",
        "endpoint": CONTAINMENT_LANE_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_206": {
            "status": pack_206.get("status"),
            "readiness_score": pack_206.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_207": pack_206.get("summary", {}).get("safe_to_continue_to_pack_207"),
            "operational_readiness_lane_count": pack_206.get("summary", {}).get("operational_readiness_lane_count"),
            "owner_next_action_count": pack_206.get("summary", {}).get("owner_next_action_count"),
        },
        "summary": {
            "containment_trigger_count": len(triggers),
            "containment_scope_map_count": len(scopes),
            "containment_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_containment_review_queue_item_count": len(queue),
            "real_containment_executed_count": safety.get("real_containment_executed_count"),
            "real_containment_triggered_count": safety.get("real_containment_triggered_count"),
            "real_containment_scope_applied_count": safety.get("real_containment_scope_applied_count"),
            "real_containment_action_executed_count": safety.get("real_containment_action_executed_count"),
            "real_owner_containment_review_executed_count": safety.get("real_owner_containment_review_executed_count"),
            "real_incident_action_executed_count": safety.get("real_incident_action_executed_count"),
            "real_archive_written_count": safety.get("real_archive_written_count"),
            "real_gateway_access_granted_count": safety.get("real_gateway_access_granted_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_208": checkpoint.get("safe_to_continue_to_pack_208"),
            "save_batch": "206-210",
            "save_after_pack": 210,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain containment lane preview ready" if readiness_score == 100 else "Receipt chain containment lane preview needs review",
        },
        "readiness_checks": readiness_checks,
        "containment_trigger_previews": triggers,
        "containment_scope_map_previews": scopes,
        "containment_action_menu_previews": actions,
        "owner_containment_review_queue_previews": queue,
        "containment_lane_safety_summary": safety,
        "containment_lane_checkpoint": checkpoint,
        "containment_lane_indexes": indexes,
    }


def build_receipt_chain_containment_lane_v207_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_containment_lane_v207_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_containment_lane_v207_payload_cached())


def get_receipt_chain_containment_lane_v207_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_containment_lane_v207_payload(force_refresh=force_refresh)


def build_receipt_chain_containment_lane_v207_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_containment_lane_v207_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 207,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "containment_trigger_count": summary.get("containment_trigger_count"),
        "containment_scope_map_count": summary.get("containment_scope_map_count"),
        "containment_action_menu_item_count": summary.get("containment_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_containment_review_queue_item_count": summary.get("owner_containment_review_queue_item_count"),
        "real_containment_executed_count": summary.get("real_containment_executed_count"),
        "real_containment_triggered_count": summary.get("real_containment_triggered_count"),
        "real_containment_scope_applied_count": summary.get("real_containment_scope_applied_count"),
        "real_containment_action_executed_count": summary.get("real_containment_action_executed_count"),
        "real_owner_containment_review_executed_count": summary.get("real_owner_containment_review_executed_count"),
        "real_incident_action_executed_count": summary.get("real_incident_action_executed_count"),
        "real_archive_written_count": summary.get("real_archive_written_count"),
        "real_gateway_access_granted_count": summary.get("real_gateway_access_granted_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_208": summary.get("safe_to_continue_to_pack_208"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_containment_lane_v207_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_containment_lane_v207_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_containment_lane_v207_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_containment_lane_v207_status_bridge()
    action = {
        "id": "receipt_chain_containment_lane_v207",
        "label": "Receipt Chain Containment Lane",
        "title": "Receipt Chain Containment Lane Preview",
        "href": CONTAINMENT_LANE_ENDPOINT,
        "endpoint": CONTAINMENT_LANE_ENDPOINT,
        "description": "Preview containment triggers, scope maps, and blocked containment actions.",
        "status": bridge.get("status"),
        "pack": "Pack 207",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_containment_lane_v207_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_containment_lane_v207_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_containment_lane_v207",
        "title": "Receipt Chain Containment Lane",
        "subtitle": "Preview containment triggers, scope maps, blocked actions, and owner review queue.",
        "status": payload.get("status"),
        "href": CONTAINMENT_LANE_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Containment readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "triggers", "title": "Triggers", "value": summary.get("containment_trigger_count"), "label": "Preview-only triggers"},
            {"id": "scopes", "title": "Scope maps", "value": summary.get("containment_scope_map_count"), "label": "Preview scope boundaries"},
            {"id": "actions", "title": "Actions", "value": summary.get("containment_action_menu_item_count"), "label": "Containment action menu"},
            {"id": "blocked", "title": "Blocked actions", "value": summary.get("blocked_action_count"), "label": "Real containment blocked"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_containment_executed") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No containment/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "CONTAINMENT_LANE_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_containment_lane_v207_payload",
    "get_receipt_chain_containment_lane_v207_payload",
    "build_receipt_chain_containment_lane_v207_status_bridge",
    "get_receipt_chain_containment_lane_v207_status_bridge",
    "build_receipt_chain_containment_lane_v207_quick_action",
    "build_receipt_chain_containment_lane_v207_unified_owner_section",
]
