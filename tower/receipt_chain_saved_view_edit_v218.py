
"""
PACK 218 - Receipt Chain Saved View Edit Preview.

Short module filename:
    tower.receipt_chain_saved_view_edit_v218

This module sits on top of Pack 217.

Pack 217 created saved view detail drawer previews.
Pack 218 adds saved view edit previews:
- editable field preview rows
- edit validation rule cards
- edit diff preview rows
- edit conflict preview cards
- blocked edit/save/apply/export action menu
- owner saved view edit review queue
- no real saved view writes
- no real saved view edits
- no real saved view applies
- no real exports
- no raw evidence reveal

Important:
- simulated-only
- saved-view-edit-preview-only
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


PACK_ID = "PACK_218"
SAVED_VIEW_EDIT_ENDPOINT = "/tower/receipt-chain-saved-view-edit-v218.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-saved-view-detail-v217.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "saved_view_edit_preview_only": True,
        "editable_field_preview_only": True,
        "edit_validation_rule_preview_only": True,
        "edit_diff_preview_only": True,
        "edit_conflict_preview_only": True,
        "saved_view_edit_action_menu_preview_only": True,
        "owner_saved_view_edit_queue_preview_only": True,
        "saved_view_detail_preview_only": True,
        "selected_preset_detail_preview_only": True,
        "preset_field_detail_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "saved_view_write_allowed_now": False,
        "saved_view_edit_allowed_now": False,
        "saved_view_delete_allowed_now": False,
        "saved_view_apply_allowed_now": False,
        "saved_view_export_allowed_now": False,
        "edit_preview_save_allowed_now": False,
        "edit_diff_save_allowed_now": False,
        "edit_validation_save_allowed_now": False,
        "edit_conflict_save_allowed_now": False,
        "detail_state_persistence_allowed_now": False,
        "detail_selection_save_allowed_now": False,
        "field_detail_save_allowed_now": False,
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
        "real_edit_preview_saved": False,
        "real_edit_diff_saved": False,
        "real_edit_validation_saved": False,
        "real_edit_conflict_saved": False,
        "real_detail_state_persisted": False,
        "real_detail_selection_saved": False,
        "real_field_detail_saved": False,
        "real_user_preference_written": False,
        "real_navigation_state_persisted": False,
        "real_owner_review_saved": False,
        "real_archive_written": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_pack_217_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_saved_view_detail_v217")
        fn = getattr(mod, "build_receipt_chain_saved_view_detail_v217_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_217",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_218": False},
            "selected_preset_detail_previews": [],
            "preset_field_detail_row_previews": [],
            "linked_filter_detail_card_previews": [],
            "linked_scope_detail_card_previews": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_217",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_218": False},
        "selected_preset_detail_previews": [],
        "preset_field_detail_row_previews": [],
        "linked_filter_detail_card_previews": [],
        "linked_scope_detail_card_previews": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_editable_fields(pack_217: Dict[str, object]) -> List[Dict[str, object]]:
    rows = [item for item in _list(pack_217.get("preset_field_detail_row_previews")) if isinstance(item, dict)]
    selected = rows[:8]

    editable_fields = []
    for sequence, row in enumerate(selected, start=1):
        field_key = row.get("preset_field_detail_key") or f"field_{sequence}"
        allow_preview_edit = field_key in {"preset_key", "preset_type", "preset_value", "next_action"}

        item = {
            "editable_field_preview_id": f"receipt_chain_saved_view_edit_field_{_stable_hash((PACK_ID, field_key), 18)}",
            "editable_field_key": field_key,
            "label": f"Editable Preview: {row.get('label') or field_key}",
            "field_type": row.get("field_type") or "unknown",
            "sequence": sequence,
            "source_field_detail_row_preview_id": row.get("preset_field_detail_row_preview_id"),
            "source_endpoint": SOURCE_ENDPOINT,
            "current_value_preview": row.get("field_value_preview") or "preview_only_redacted_safe_value",
            "proposed_value_preview": f"preview_edit_{field_key}",
            "edit_preview_allowed": bool(allow_preview_edit),
            "real_edit_allowed_now": False,
            "saved_view_edit_allowed_now": False,
            "edit_preview_save_allowed_now": False,
            "field_status": "receipt_chain_saved_view_editable_field_preview_ready",
            "field_result_type": "tower_receipt_chain_saved_view_editable_field_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        editable_fields.append(item)

    return editable_fields


def _build_validation_rules(fields: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rule_defs = [
        ("deny_real_write", "Deny real saved view write", "deny_write", "blocked"),
        ("deny_real_apply", "Deny real saved view apply", "deny_apply", "blocked"),
        ("deny_raw_reveal", "Deny raw evidence reveal", "redaction", "blocked"),
        ("require_preview_mode", "Require preview mode", "mode", "required"),
        ("require_owner_review", "Require owner review", "owner_review", "required"),
        ("preserve_batch_scope", "Preserve batch scope", "scope", "required"),
        ("preserve_route_wall", "Preserve route wall filter", "route_wall", "required"),
    ]

    field_keys = [item.get("editable_field_key") for item in fields]

    rules = []
    for sequence, (rule_key, label, rule_type, rule_outcome) in enumerate(rule_defs, start=1):
        item = {
            "edit_validation_rule_card_preview_id": f"receipt_chain_saved_view_edit_rule_{_stable_hash((PACK_ID, rule_key), 18)}",
            "edit_validation_rule_key": rule_key,
            "label": label,
            "rule_type": rule_type,
            "rule_outcome": rule_outcome,
            "sequence": sequence,
            "linked_editable_field_keys": field_keys,
            "linked_editable_field_count": len(field_keys),
            "validation_passed_preview": True,
            "edit_validation_save_allowed_now": False,
            "rule_status": "receipt_chain_saved_view_edit_validation_rule_preview_ready",
            "rule_result_type": "tower_receipt_chain_saved_view_edit_validation_rule_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        rules.append(item)

    return rules


def _build_edit_diffs(fields: List[Dict[str, object]], rules: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rule_keys = [item.get("edit_validation_rule_key") for item in rules]

    diffs = []
    for sequence, field in enumerate(fields, start=1):
        field_key = field.get("editable_field_key")
        item = {
            "edit_diff_row_preview_id": f"receipt_chain_saved_view_edit_diff_{_stable_hash((PACK_ID, field_key), 18)}",
            "edit_diff_key": f"diff_{field_key}",
            "label": f"Edit Diff: {field.get('label') or field_key}",
            "diff_type": field.get("field_type") or "unknown",
            "sequence": sequence,
            "field_key": field_key,
            "current_value_preview": field.get("current_value_preview"),
            "proposed_value_preview": field.get("proposed_value_preview"),
            "diff_result": "preview_only_no_persist",
            "linked_validation_rule_keys": rule_keys,
            "linked_validation_rule_count": len(rule_keys),
            "edit_diff_save_allowed_now": False,
            "diff_status": "receipt_chain_saved_view_edit_diff_preview_ready",
            "diff_result_type": "tower_receipt_chain_saved_view_edit_diff_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        diffs.append(item)

    return diffs


def _build_conflict_cards(fields: List[Dict[str, object]], diffs: List[Dict[str, object]]) -> List[Dict[str, object]]:
    conflict_defs = [
        ("write_block_conflict", "Write blocked conflict", "write_block", "blocked_by_policy"),
        ("apply_block_conflict", "Apply blocked conflict", "apply_block", "blocked_by_policy"),
        ("raw_reveal_conflict", "Raw reveal conflict", "raw_evidence", "blocked_by_redaction"),
        ("navigation_persist_conflict", "Navigation persist conflict", "navigation", "blocked_by_preview"),
        ("owner_review_required_conflict", "Owner review required conflict", "owner_review", "requires_review"),
    ]

    field_keys = [item.get("editable_field_key") for item in fields]
    diff_keys = [item.get("edit_diff_key") for item in diffs]

    conflicts = []
    for sequence, (conflict_key, label, conflict_type, conflict_result) in enumerate(conflict_defs, start=1):
        item = {
            "edit_conflict_card_preview_id": f"receipt_chain_saved_view_edit_conflict_{_stable_hash((PACK_ID, conflict_key), 18)}",
            "edit_conflict_key": conflict_key,
            "label": label,
            "conflict_type": conflict_type,
            "conflict_result": conflict_result,
            "sequence": sequence,
            "linked_editable_field_keys": field_keys,
            "linked_editable_field_count": len(field_keys),
            "linked_edit_diff_keys": diff_keys,
            "linked_edit_diff_count": len(diff_keys),
            "edit_conflict_save_allowed_now": False,
            "conflict_status": "receipt_chain_saved_view_edit_conflict_preview_ready",
            "conflict_result_type": "tower_receipt_chain_saved_view_edit_conflict_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        conflicts.append(item)

    return conflicts


def _build_edit_actions(fields, rules, diffs, conflicts) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_edit_status", "Preview edit status", True, "Preview saved view edit health."),
        ("preview_edit_diff", "Preview edit diff", True, "Preview safe edit diff rows."),
        ("open_pack_217_saved_view_detail", "Open Pack 217 saved view detail", True, "Open Pack 217 JSON."),
        ("blocked_save_edit_preview", "Save edit preview", False, "Blocked: real edit save is not enabled in Pack 218."),
        ("blocked_apply_saved_view_edit", "Apply saved view edit", False, "Blocked: real saved view apply is not enabled in Pack 218."),
        ("blocked_write_user_preference", "Write user preference", False, "Blocked: real user preference writes are not enabled in Pack 218."),
        ("blocked_export_edit_packet", "Export edit packet", False, "Blocked: real edit export is not enabled in Pack 218."),
        ("blocked_reveal_raw_evidence", "Reveal raw evidence", False, "Blocked: raw evidence reveal is not enabled in Pack 218."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        item = {
            "saved_view_edit_action_menu_item_preview_id": f"receipt_chain_saved_view_edit_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "saved_view_edit_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "editable_field_count": len(fields),
            "validation_rule_count": len(rules),
            "edit_diff_row_count": len(diffs),
            "edit_conflict_card_count": len(conflicts),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_saved_view_edit_action": False,
            "action_status": "receipt_chain_saved_view_edit_action_preview_ready" if allowed else "receipt_chain_saved_view_edit_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_saved_view_edit_action_menu_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        actions.append(item)

    return actions


def _build_owner_edit_queue(fields, rules, diffs, conflicts, actions) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_editable_fields", "Review editable fields", "field_review", len(fields)),
        ("review_validation_rules", "Review validation rules", "validation_review", len(rules)),
        ("review_edit_diffs", "Review edit diffs", "diff_review", len(diffs)),
        ("review_edit_conflicts", "Review edit conflicts", "conflict_review", len(conflicts)),
        ("prepare_pack_219_saved_view_history", "Prepare Pack 219 saved view history", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_saved_view_edit_queue_item_preview_id": f"receipt_chain_owner_saved_view_edit_queue_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_owner_saved_view_edit_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_saved_view_edit_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(fields, rules, diffs, conflicts, actions, queue) -> Dict[str, object]:
    all_items = fields + rules + diffs + conflicts + actions + queue

    summary = {
        "saved_view_edit_safety_summary_id": f"receipt_chain_saved_view_edit_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "editable_field_count": len(fields),
        "edit_validation_rule_count": len(rules),
        "edit_diff_row_count": len(diffs),
        "edit_conflict_card_count": len(conflicts),
        "saved_view_edit_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_saved_view_edit_queue_item_count": len(queue),
        "real_saved_view_written_count": 0,
        "real_saved_view_edited_count": 0,
        "real_saved_view_deleted_count": 0,
        "real_saved_view_applied_count": 0,
        "real_saved_view_exported_count": 0,
        "real_edit_preview_saved_count": 0,
        "real_edit_diff_saved_count": 0,
        "real_edit_validation_saved_count": 0,
        "real_edit_conflict_saved_count": 0,
        "real_user_preference_written_count": 0,
        "real_navigation_state_persisted_count": 0,
        "real_owner_review_saved_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_fields_preview_only": all(item.get("editable_field_preview_only") is True for item in fields),
        "all_rules_preview_only": all(item.get("edit_validation_rule_preview_only") is True for item in rules),
        "all_diffs_preview_only": all(item.get("edit_diff_preview_only") is True for item in diffs),
        "all_conflicts_preview_only": all(item.get("edit_conflict_preview_only") is True for item in conflicts),
        "all_actions_preview_only": all(item.get("saved_view_edit_action_menu_preview_only") is True for item in actions),
        "all_queue_preview_only": all(item.get("owner_saved_view_edit_queue_preview_only") is True for item in queue),
        "all_saved_view_edit_writes_blocked": True,
        "all_raw_evidence_reveal_blocked": True,
        "summary_status": "receipt_chain_saved_view_edit_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_saved_view_edit_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("editable_field_count") == 8
        and safety.get("edit_validation_rule_count") == 7
        and safety.get("edit_diff_row_count") == 8
        and safety.get("edit_conflict_card_count") == 5
        and safety.get("saved_view_edit_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_saved_view_edit_queue_item_count") == 5
        and safety.get("real_saved_view_written_count") == 0
        and safety.get("real_saved_view_edited_count") == 0
        and safety.get("real_saved_view_applied_count") == 0
        and safety.get("real_edit_preview_saved_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "saved_view_edit_checkpoint_id": f"receipt_chain_saved_view_edit_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_saved_view_edit_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_saved_view_edit_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_saved_view_edit_checkpoint_preview",
        "safe_to_continue_to_pack_219": checkpoint_ok,
        "save_batch": "216-220",
        "save_after_pack": 220,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(fields, rules, diffs, conflicts, actions, queue, checkpoint) -> Dict[str, object]:
    indexes = {
        "editable_fields_by_id": {},
        "editable_fields_by_key": {},
        "validation_rules_by_id": {},
        "validation_rules_by_key": {},
        "edit_diffs_by_id": {},
        "edit_diffs_by_key": {},
        "edit_conflicts_by_id": {},
        "edit_conflicts_by_key": {},
        "actions_by_id": {},
        "actions_by_key": {},
        "owner_edit_queue_by_id": {},
        "owner_edit_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in fields:
        indexes["editable_fields_by_id"][item.get("editable_field_preview_id")] = item
        indexes["editable_fields_by_key"][item.get("editable_field_key")] = item

    for item in rules:
        indexes["validation_rules_by_id"][item.get("edit_validation_rule_card_preview_id")] = item
        indexes["validation_rules_by_key"][item.get("edit_validation_rule_key")] = item

    for item in diffs:
        indexes["edit_diffs_by_id"][item.get("edit_diff_row_preview_id")] = item
        indexes["edit_diffs_by_key"][item.get("edit_diff_key")] = item

    for item in conflicts:
        indexes["edit_conflicts_by_id"][item.get("edit_conflict_card_preview_id")] = item
        indexes["edit_conflicts_by_key"][item.get("edit_conflict_key")] = item

    for item in actions:
        indexes["actions_by_id"][item.get("saved_view_edit_action_menu_item_preview_id")] = item
        indexes["actions_by_key"][item.get("saved_view_edit_action_key")] = item

    for item in queue:
        indexes["owner_edit_queue_by_id"][item.get("owner_saved_view_edit_queue_item_preview_id")] = item
        indexes["owner_edit_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("saved_view_edit_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_saved_view_edit_v218_payload_cached() -> Dict[str, object]:
    pack_217 = _load_pack_217_payload(force_refresh=True)

    fields = _build_editable_fields(pack_217)
    rules = _build_validation_rules(fields)
    diffs = _build_edit_diffs(fields, rules)
    conflicts = _build_conflict_cards(fields, diffs)
    actions = _build_edit_actions(fields, rules, diffs, conflicts)
    queue = _build_owner_edit_queue(fields, rules, diffs, conflicts, actions)
    safety = _build_safety_summary(fields, rules, diffs, conflicts, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(fields, rules, diffs, conflicts, actions, queue, checkpoint)

    all_items = fields + rules + diffs + conflicts + actions + queue

    readiness_checks = {
        "pack_217_ready": pack_217.get("status") == "ready",
        "pack_217_safe_to_continue": pack_217.get("summary", {}).get("safe_to_continue_to_pack_218") is True,
        "has_editable_fields": len(fields) == 8,
        "has_validation_rules": len(rules) == 7,
        "has_edit_diffs": len(diffs) == 8,
        "has_edit_conflicts": len(conflicts) == 5,
        "has_edit_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_edit_queue": len(queue) == 5,
        "all_fields_ready": all(item.get("field_status") == "receipt_chain_saved_view_editable_field_preview_ready" for item in fields),
        "all_rules_ready": all(item.get("rule_status") == "receipt_chain_saved_view_edit_validation_rule_preview_ready" for item in rules),
        "all_diffs_ready": all(item.get("diff_status") == "receipt_chain_saved_view_edit_diff_preview_ready" for item in diffs),
        "all_conflicts_ready": all(item.get("conflict_status") == "receipt_chain_saved_view_edit_conflict_preview_ready" for item in conflicts),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_saved_view_edit_action_preview_ready", "receipt_chain_saved_view_edit_action_preview_blocked"} for item in actions),
        "all_queue_blocked": all(item.get("queue_status") == "receipt_chain_owner_saved_view_edit_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_saved_view_edit_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_saved_view_edit_checkpoint_preview_ready",
        "safe_to_continue_to_pack_219": checkpoint.get("safe_to_continue_to_pack_219") is True,
        "indexes_present": bool(indexes.get("editable_fields_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_saved_view_edit_preview_only": all(item.get("saved_view_edit_preview_only") is True for item in all_items),
        "no_real_saved_view_written": all(item.get("real_saved_view_written") is False for item in all_items),
        "no_real_saved_view_edited": all(item.get("real_saved_view_edited") is False for item in all_items),
        "no_real_saved_view_deleted": all(item.get("real_saved_view_deleted") is False for item in all_items),
        "no_real_saved_view_applied": all(item.get("real_saved_view_applied") is False for item in all_items),
        "no_real_saved_view_exported": all(item.get("real_saved_view_exported") is False for item in all_items),
        "no_real_edit_preview_saved": all(item.get("real_edit_preview_saved") is False for item in all_items),
        "no_real_edit_diff_saved": all(item.get("real_edit_diff_saved") is False for item in all_items),
        "no_real_edit_validation_saved": all(item.get("real_edit_validation_saved") is False for item in all_items),
        "no_real_edit_conflict_saved": all(item.get("real_edit_conflict_saved") is False for item in all_items),
        "no_real_user_preference_written": all(item.get("real_user_preference_written") is False for item in all_items),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in all_items),
        "no_real_owner_review_saved": all(item.get("real_owner_review_saved") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_edit_writes_blocked": all(item.get("saved_view_edit_allowed_now") is False for item in all_items),
        "all_saved_view_writes_blocked": all(item.get("saved_view_write_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 218,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Saved View Edit Preview",
        "endpoint": SAVED_VIEW_EDIT_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_217": {
            "status": pack_217.get("status"),
            "readiness_score": pack_217.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_218": pack_217.get("summary", {}).get("safe_to_continue_to_pack_218"),
            "save_batch": pack_217.get("summary", {}).get("save_batch"),
        },
        "summary": {
            "editable_field_count": len(fields),
            "edit_validation_rule_count": len(rules),
            "edit_diff_row_count": len(diffs),
            "edit_conflict_card_count": len(conflicts),
            "saved_view_edit_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_saved_view_edit_queue_item_count": len(queue),
            "real_saved_view_written_count": safety.get("real_saved_view_written_count"),
            "real_saved_view_edited_count": safety.get("real_saved_view_edited_count"),
            "real_saved_view_deleted_count": safety.get("real_saved_view_deleted_count"),
            "real_saved_view_applied_count": safety.get("real_saved_view_applied_count"),
            "real_saved_view_exported_count": safety.get("real_saved_view_exported_count"),
            "real_edit_preview_saved_count": safety.get("real_edit_preview_saved_count"),
            "real_edit_diff_saved_count": safety.get("real_edit_diff_saved_count"),
            "real_edit_validation_saved_count": safety.get("real_edit_validation_saved_count"),
            "real_edit_conflict_saved_count": safety.get("real_edit_conflict_saved_count"),
            "real_user_preference_written_count": safety.get("real_user_preference_written_count"),
            "real_navigation_state_persisted_count": safety.get("real_navigation_state_persisted_count"),
            "real_owner_review_saved_count": safety.get("real_owner_review_saved_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_219": checkpoint.get("safe_to_continue_to_pack_219"),
            "save_batch": "216-220",
            "save_after_pack": 220,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain saved view edit preview ready" if readiness_score == 100 else "Receipt chain saved view edit preview needs review",
        },
        "readiness_checks": readiness_checks,
        "editable_field_previews": fields,
        "edit_validation_rule_card_previews": rules,
        "edit_diff_row_previews": diffs,
        "edit_conflict_card_previews": conflicts,
        "saved_view_edit_action_menu_previews": actions,
        "owner_saved_view_edit_queue_previews": queue,
        "saved_view_edit_safety_summary": safety,
        "saved_view_edit_checkpoint": checkpoint,
        "saved_view_edit_indexes": indexes,
    }


def build_receipt_chain_saved_view_edit_v218_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_saved_view_edit_v218_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_saved_view_edit_v218_payload_cached())


def get_receipt_chain_saved_view_edit_v218_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_edit_v218_payload(force_refresh=force_refresh)


def build_receipt_chain_saved_view_edit_v218_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_edit_v218_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 218,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "editable_field_count": summary.get("editable_field_count"),
        "edit_validation_rule_count": summary.get("edit_validation_rule_count"),
        "edit_diff_row_count": summary.get("edit_diff_row_count"),
        "edit_conflict_card_count": summary.get("edit_conflict_card_count"),
        "saved_view_edit_action_menu_item_count": summary.get("saved_view_edit_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_saved_view_edit_queue_item_count": summary.get("owner_saved_view_edit_queue_item_count"),
        "real_saved_view_written_count": summary.get("real_saved_view_written_count"),
        "real_saved_view_edited_count": summary.get("real_saved_view_edited_count"),
        "real_saved_view_deleted_count": summary.get("real_saved_view_deleted_count"),
        "real_saved_view_applied_count": summary.get("real_saved_view_applied_count"),
        "real_saved_view_exported_count": summary.get("real_saved_view_exported_count"),
        "real_edit_preview_saved_count": summary.get("real_edit_preview_saved_count"),
        "real_edit_diff_saved_count": summary.get("real_edit_diff_saved_count"),
        "real_edit_validation_saved_count": summary.get("real_edit_validation_saved_count"),
        "real_edit_conflict_saved_count": summary.get("real_edit_conflict_saved_count"),
        "real_user_preference_written_count": summary.get("real_user_preference_written_count"),
        "real_navigation_state_persisted_count": summary.get("real_navigation_state_persisted_count"),
        "real_owner_review_saved_count": summary.get("real_owner_review_saved_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_219": summary.get("safe_to_continue_to_pack_219"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_saved_view_edit_v218_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_saved_view_edit_v218_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_saved_view_edit_v218_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_saved_view_edit_v218_status_bridge()
    action = {
        "id": "receipt_chain_saved_view_edit_v218",
        "label": "Receipt Chain Saved View Edit",
        "title": "Receipt Chain Saved View Edit Preview",
        "href": SAVED_VIEW_EDIT_ENDPOINT,
        "endpoint": SAVED_VIEW_EDIT_ENDPOINT,
        "description": "Preview editable fields, validation rules, diffs, conflicts, and blocked edit actions.",
        "status": bridge.get("status"),
        "pack": "Pack 218",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_saved_view_edit_v218_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_saved_view_edit_v218_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_saved_view_edit_v218",
        "title": "Receipt Chain Saved View Edit",
        "subtitle": "Preview editable saved view fields, validation rules, edit diffs, conflicts, and blocked edit writes.",
        "status": payload.get("status"),
        "href": SAVED_VIEW_EDIT_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Edit readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "fields", "title": "Editable fields", "value": summary.get("editable_field_count"), "label": "Preview only"},
            {"id": "rules", "title": "Validation rules", "value": summary.get("edit_validation_rule_count"), "label": "Guardrails"},
            {"id": "diffs", "title": "Diff rows", "value": summary.get("edit_diff_row_count"), "label": "No persist"},
            {"id": "conflicts", "title": "Conflict cards", "value": summary.get("edit_conflict_card_count"), "label": "Blocked changes"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_saved_view_edited") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No edit/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "SAVED_VIEW_EDIT_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_saved_view_edit_v218_payload",
    "get_receipt_chain_saved_view_edit_v218_payload",
    "build_receipt_chain_saved_view_edit_v218_status_bridge",
    "get_receipt_chain_saved_view_edit_v218_status_bridge",
    "build_receipt_chain_saved_view_edit_v218_quick_action",
    "build_receipt_chain_saved_view_edit_v218_unified_owner_section",
]
