
"""
PACK 213 - Receipt Chain Owner Review Drawer Preview.

Short module filename:
    tower.receipt_chain_owner_review_drawer_v213

This module sits on top of Pack 212.

Pack 212 created checkpoint filter/search previews.
Pack 213 adds an owner review drawer layer:
- selected checkpoint search result detail drawer previews
- owner review tab previews
- owner note draft previews
- owner review decision preview cards
- blocked owner drawer action menu
- no real note save
- no real drawer selection persistence
- no real export
- no raw evidence reveal

Important:
- simulated-only
- owner-review-drawer-preview-only
- drawer/review preview only
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


PACK_ID = "PACK_213"
OWNER_REVIEW_DRAWER_ENDPOINT = "/tower/receipt-chain-owner-review-drawer-v213.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-checkpoint-filter-search-v212.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "owner_review_drawer_preview_only": True,
        "selected_result_drawer_preview_only": True,
        "owner_review_tab_preview_only": True,
        "owner_note_draft_preview_only": True,
        "owner_review_decision_preview_only": True,
        "owner_drawer_action_menu_preview_only": True,
        "checkpoint_filter_search_preview_only": True,
        "query_preset_preview_only": True,
        "filter_lane_preview_only": True,
        "search_result_card_preview_only": True,
        "filter_search_action_menu_preview_only": True,
        "owner_filter_search_queue_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "owner_note_save_allowed_now": False,
        "owner_review_decision_save_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
        "drawer_state_persistence_allowed_now": False,
        "owner_drawer_action_execution_allowed_now": False,
        "filter_preference_save_allowed_now": False,
        "query_preset_save_allowed_now": False,
        "search_state_persistence_allowed_now": False,
        "lookup_persistence_allowed_now": False,
        "archive_write_allowed_now": False,
        "archive_export_allowed_now": False,
        "evidence_export_allowed_now": False,
        "gateway_access_grant_allowed_now": False,
        "save_allowed_now": False,
        "push_allowed_now": False,
        "commit_allowed_now": False,
        "owner_action_execution_allowed_now": False,
        "handoff_execution_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "saved_view_write_allowed_now": False,
        "user_preference_write_allowed_now": False,
        "history_write_allowed_now": False,
        "version_write_allowed_now": False,
        "version_save_allowed_now": False,
        "restore_allowed_now": False,
        "rollback_allowed_now": False,
        "persist_allowed_now": False,
        "action_execution_allowed_now": False,
        "real_action_executed": False,
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
        "real_owner_note_saved": False,
        "real_owner_review_decision_saved": False,
        "real_drawer_selection_saved": False,
        "real_drawer_state_persisted": False,
        "real_owner_drawer_action_executed": False,
        "real_filter_preference_saved": False,
        "real_query_preset_saved": False,
        "real_search_state_persisted": False,
        "real_lookup_persisted": False,
        "real_archive_written": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_navigation_state_persisted": False,
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


def _load_pack_212_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_checkpoint_filter_search_v212")
        fn = getattr(mod, "build_receipt_chain_checkpoint_filter_search_v212_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_212",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_213": False},
            "query_preset_previews": [],
            "filter_lane_previews": [],
            "search_result_card_previews": [],
            "filter_search_action_menu_previews": [],
            "owner_filter_search_queue_previews": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_212",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_213": False},
        "query_preset_previews": [],
        "filter_lane_previews": [],
        "search_result_card_previews": [],
        "filter_search_action_menu_previews": [],
        "owner_filter_search_queue_previews": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_selected_result_drawers(pack_212: Dict[str, object]) -> List[Dict[str, object]]:
    search_results = [item for item in _list(pack_212.get("search_result_card_previews")) if isinstance(item, dict)]

    selected = search_results[:6]
    drawers = []

    for sequence, source in enumerate(selected, start=1):
        source_key = source.get("search_result_key") or f"result_{sequence}"
        drawer = {
            "selected_result_drawer_preview_id": f"receipt_chain_owner_review_drawer_result_{_stable_hash((PACK_ID, source_key), 18)}",
            "selected_result_key": source_key,
            "label": source.get("label") or f"Selected result {sequence}",
            "result_type": source.get("result_type"),
            "sequence": sequence,
            "source_preview_id": source.get("search_result_card_preview_id"),
            "source_key": source.get("source_key"),
            "drawer_sections": [
                "summary",
                "source_trace",
                "safety_flags",
                "owner_notes",
                "next_action_preview",
            ],
            "drawer_section_count": 5,
            "raw_evidence_redacted": True,
            "drawer_selection_save_allowed_now": False,
            "drawer_state_persistence_allowed_now": False,
            "drawer_status": "receipt_chain_owner_review_selected_result_drawer_preview_ready",
            "drawer_result_type": "tower_receipt_chain_owner_review_selected_result_drawer_preview",
            "safe_preview_only": True,
        }
        drawer.update(_base_flags())
        drawers.append(drawer)

    return drawers


def _build_owner_review_tabs(drawers: List[Dict[str, object]]) -> List[Dict[str, object]]:
    drawer_keys = [item.get("selected_result_key") for item in drawers]

    tab_defs = [
        ("overview_tab", "Overview", "overview"),
        ("safety_tab", "Safety", "safety"),
        ("source_trace_tab", "Source Trace", "source_trace"),
        ("owner_notes_tab", "Owner Notes", "owner_notes"),
        ("decision_preview_tab", "Decision Preview", "decision"),
        ("next_step_tab", "Next Step", "next_step"),
    ]

    tabs = []
    for sequence, (tab_key, label, tab_type) in enumerate(tab_defs, start=1):
        tab = {
            "owner_review_tab_preview_id": f"receipt_chain_owner_review_tab_{_stable_hash((PACK_ID, tab_key), 18)}",
            "owner_review_tab_key": tab_key,
            "label": label,
            "tab_type": tab_type,
            "sequence": sequence,
            "linked_selected_result_keys": drawer_keys,
            "linked_selected_result_count": len(drawer_keys),
            "tab_state_persistence_allowed_now": False,
            "tab_status": "receipt_chain_owner_review_tab_preview_ready",
            "tab_result_type": "tower_receipt_chain_owner_review_tab_preview",
            "safe_preview_only": True,
        }
        tab.update(_base_flags())
        tabs.append(tab)

    return tabs


def _build_owner_note_drafts(drawers: List[Dict[str, object]], tabs: List[Dict[str, object]]) -> List[Dict[str, object]]:
    tab_keys = [item.get("owner_review_tab_key") for item in tabs]

    draft_defs = [
        ("batch_status_note", "Batch status note", "status_note"),
        ("safety_confirmation_note", "Safety confirmation note", "safety_note"),
        ("lookup_context_note", "Lookup context note", "context_note"),
        ("filter_result_note", "Filter result note", "result_note"),
        ("next_pack_note", "Next Pack 214 note", "next_pack_note"),
    ]

    drafts = []
    for sequence, (draft_key, label, draft_type) in enumerate(draft_defs, start=1):
        linked_drawer_keys = [item.get("selected_result_key") for item in drawers[: min(len(drawers), sequence + 1)]]
        draft = {
            "owner_note_draft_preview_id": f"receipt_chain_owner_review_note_draft_{_stable_hash((PACK_ID, draft_key), 18)}",
            "owner_note_draft_key": draft_key,
            "label": label,
            "draft_type": draft_type,
            "sequence": sequence,
            "linked_selected_result_keys": linked_drawer_keys,
            "linked_selected_result_count": len(linked_drawer_keys),
            "linked_tab_keys": tab_keys,
            "draft_text_preview": f"{label}: preview only; no owner note saved.",
            "note_save_allowed_now": False,
            "draft_status": "receipt_chain_owner_note_draft_preview_ready",
            "draft_result_type": "tower_receipt_chain_owner_note_draft_preview",
            "safe_preview_only": True,
        }
        draft.update(_base_flags())
        drafts.append(draft)

    return drafts


def _build_owner_decision_previews(drawers: List[Dict[str, object]], drafts: List[Dict[str, object]]) -> List[Dict[str, object]]:
    draft_keys = [item.get("owner_note_draft_key") for item in drafts]

    decision_defs = [
        ("mark_reviewed_preview", "Mark reviewed preview", "reviewed", True),
        ("hold_for_pack_214_preview", "Hold for Pack 214 evidence drawer", "hold", True),
        ("request_more_context_preview", "Request more context preview", "request_context", True),
        ("blocked_save_review_decision", "Save real review decision", "save_decision", False),
        ("blocked_execute_owner_action", "Execute owner action", "execute_owner_action", False),
    ]

    decisions = []
    for sequence, (decision_key, label, decision_type, allowed) in enumerate(decision_defs, start=1):
        decision = {
            "owner_review_decision_preview_id": f"receipt_chain_owner_review_decision_{_stable_hash((PACK_ID, decision_key), 18)}",
            "owner_review_decision_key": decision_key,
            "label": label,
            "decision_type": decision_type,
            "sequence": sequence,
            "linked_note_draft_keys": draft_keys,
            "linked_note_draft_count": len(draft_keys),
            "linked_selected_result_count": len(drawers),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "decision_save_allowed_now": False,
            "decision_status": "receipt_chain_owner_review_decision_preview_ready" if allowed else "receipt_chain_owner_review_decision_preview_blocked",
            "decision_result_type": "tower_receipt_chain_owner_review_decision_preview",
            "safe_preview_only": True,
        }
        decision.update(_base_flags())
        decisions.append(decision)

    return decisions


def _build_owner_drawer_actions(drawers: List[Dict[str, object]], decisions: List[Dict[str, object]]) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_drawer_status", "Preview drawer status", True, "Preview owner drawer health."),
        ("preview_selected_result", "Preview selected result", True, "Preview selected result drawer."),
        ("open_pack_212_filter_search", "Open Pack 212 filter/search", True, "Open Pack 212 JSON."),
        ("blocked_save_owner_note", "Save owner note", False, "Blocked: real owner note save is not enabled in Pack 213."),
        ("blocked_save_review_decision", "Save review decision", False, "Blocked: real owner review decision save is not enabled in Pack 213."),
        ("blocked_persist_drawer_state", "Persist drawer state", False, "Blocked: real drawer persistence is not enabled in Pack 213."),
        ("blocked_export_drawer", "Export drawer", False, "Blocked: real drawer export is not enabled in Pack 213."),
        ("blocked_reveal_raw_evidence", "Reveal raw evidence", False, "Blocked: raw evidence reveal is not enabled in Pack 213."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        action = {
            "owner_drawer_action_menu_item_preview_id": f"receipt_chain_owner_drawer_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "owner_drawer_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "selected_result_drawer_count": len(drawers),
            "decision_preview_count": len(decisions),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_owner_drawer_action": False,
            "action_status": "receipt_chain_owner_drawer_action_preview_ready" if allowed else "receipt_chain_owner_drawer_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_owner_drawer_action_menu_preview",
            "safe_preview_only": True,
        }
        action.update(_base_flags())
        actions.append(action)

    return actions


def _build_owner_drawer_queue(drawers, tabs, drafts, decisions, actions) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_selected_result_drawers", "Review selected result drawers", "drawer_review", len(drawers)),
        ("review_owner_tabs", "Review owner review tabs", "tab_review", len(tabs)),
        ("review_note_drafts", "Review owner note drafts", "note_review", len(drafts)),
        ("review_decision_previews", "Review decision previews", "decision_review", len(decisions)),
        ("prepare_pack_214_evidence_drawer", "Prepare Pack 214 evidence drawer", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_drawer_queue_item_preview_id": f"receipt_chain_owner_drawer_queue_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_owner_drawer_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_drawer_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(drawers, tabs, drafts, decisions, actions, queue) -> Dict[str, object]:
    all_items = drawers + tabs + drafts + decisions + actions + queue

    summary = {
        "owner_review_drawer_safety_summary_id": f"receipt_chain_owner_review_drawer_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "selected_result_drawer_count": len(drawers),
        "owner_review_tab_count": len(tabs),
        "owner_note_draft_count": len(drafts),
        "owner_review_decision_count": len(decisions),
        "owner_drawer_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_drawer_queue_item_count": len(queue),
        "real_owner_note_saved_count": 0,
        "real_owner_review_decision_saved_count": 0,
        "real_drawer_selection_saved_count": 0,
        "real_drawer_state_persisted_count": 0,
        "real_owner_drawer_action_executed_count": 0,
        "real_archive_written_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_drawers_preview_only": all(item.get("selected_result_drawer_preview_only") is True for item in drawers),
        "all_tabs_preview_only": all(item.get("owner_review_tab_preview_only") is True for item in tabs),
        "all_drafts_preview_only": all(item.get("owner_note_draft_preview_only") is True for item in drafts),
        "all_decisions_preview_only": all(item.get("owner_review_decision_preview_only") is True for item in decisions),
        "all_actions_preview_only": all(item.get("owner_drawer_action_menu_preview_only") is True for item in actions),
        "all_queue_preview_only": all(item.get("owner_review_drawer_preview_only") is True for item in queue),
        "all_real_owner_drawer_persistence_blocked": True,
        "summary_status": "receipt_chain_owner_review_drawer_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_owner_review_drawer_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("selected_result_drawer_count") == 6
        and safety.get("owner_review_tab_count") == 6
        and safety.get("owner_note_draft_count") == 5
        and safety.get("owner_review_decision_count") == 5
        and safety.get("owner_drawer_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_drawer_queue_item_count") == 5
        and safety.get("real_owner_note_saved_count") == 0
        and safety.get("real_owner_review_decision_saved_count") == 0
        and safety.get("real_drawer_selection_saved_count") == 0
        and safety.get("real_drawer_state_persisted_count") == 0
        and safety.get("real_archive_written_count") == 0
        and safety.get("real_evidence_exported_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "owner_review_drawer_checkpoint_id": f"receipt_chain_owner_review_drawer_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_owner_review_drawer_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_owner_review_drawer_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_owner_review_drawer_checkpoint_preview",
        "safe_to_continue_to_pack_214": checkpoint_ok,
        "save_batch": "211-215",
        "save_after_pack": 215,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(drawers, tabs, drafts, decisions, actions, queue, checkpoint) -> Dict[str, object]:
    indexes = {
        "selected_result_drawers_by_id": {},
        "selected_result_drawers_by_key": {},
        "owner_review_tabs_by_id": {},
        "owner_review_tabs_by_key": {},
        "owner_note_drafts_by_id": {},
        "owner_note_drafts_by_key": {},
        "owner_review_decisions_by_id": {},
        "owner_review_decisions_by_key": {},
        "owner_drawer_actions_by_id": {},
        "owner_drawer_actions_by_key": {},
        "owner_drawer_queue_by_id": {},
        "owner_drawer_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in drawers:
        indexes["selected_result_drawers_by_id"][item.get("selected_result_drawer_preview_id")] = item
        indexes["selected_result_drawers_by_key"][item.get("selected_result_key")] = item

    for item in tabs:
        indexes["owner_review_tabs_by_id"][item.get("owner_review_tab_preview_id")] = item
        indexes["owner_review_tabs_by_key"][item.get("owner_review_tab_key")] = item

    for item in drafts:
        indexes["owner_note_drafts_by_id"][item.get("owner_note_draft_preview_id")] = item
        indexes["owner_note_drafts_by_key"][item.get("owner_note_draft_key")] = item

    for item in decisions:
        indexes["owner_review_decisions_by_id"][item.get("owner_review_decision_preview_id")] = item
        indexes["owner_review_decisions_by_key"][item.get("owner_review_decision_key")] = item

    for item in actions:
        indexes["owner_drawer_actions_by_id"][item.get("owner_drawer_action_menu_item_preview_id")] = item
        indexes["owner_drawer_actions_by_key"][item.get("owner_drawer_action_key")] = item

    for item in queue:
        indexes["owner_drawer_queue_by_id"][item.get("owner_drawer_queue_item_preview_id")] = item
        indexes["owner_drawer_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("owner_review_drawer_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_owner_review_drawer_v213_payload_cached() -> Dict[str, object]:
    pack_212 = _load_pack_212_payload(force_refresh=True)

    drawers = _build_selected_result_drawers(pack_212)
    tabs = _build_owner_review_tabs(drawers)
    drafts = _build_owner_note_drafts(drawers, tabs)
    decisions = _build_owner_decision_previews(drawers, drafts)
    actions = _build_owner_drawer_actions(drawers, decisions)
    queue = _build_owner_drawer_queue(drawers, tabs, drafts, decisions, actions)
    safety = _build_safety_summary(drawers, tabs, drafts, decisions, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(drawers, tabs, drafts, decisions, actions, queue, checkpoint)

    all_items = drawers + tabs + drafts + decisions + actions + queue

    readiness_checks = {
        "pack_212_ready": pack_212.get("status") == "ready",
        "pack_212_safe_to_continue": pack_212.get("summary", {}).get("safe_to_continue_to_pack_213") is True,
        "has_selected_result_drawers": len(drawers) == 6,
        "has_owner_review_tabs": len(tabs) == 6,
        "has_owner_note_drafts": len(drafts) == 5,
        "has_owner_review_decisions": len(decisions) == 5,
        "has_owner_drawer_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_drawer_queue": len(queue) == 5,
        "all_drawers_ready": all(item.get("drawer_status") == "receipt_chain_owner_review_selected_result_drawer_preview_ready" for item in drawers),
        "all_tabs_ready": all(item.get("tab_status") == "receipt_chain_owner_review_tab_preview_ready" for item in tabs),
        "all_drafts_ready": all(item.get("draft_status") == "receipt_chain_owner_note_draft_preview_ready" for item in drafts),
        "all_decisions_ready_or_blocked": all(item.get("decision_status") in {"receipt_chain_owner_review_decision_preview_ready", "receipt_chain_owner_review_decision_preview_blocked"} for item in decisions),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_owner_drawer_action_preview_ready", "receipt_chain_owner_drawer_action_preview_blocked"} for item in actions),
        "all_queue_blocked": all(item.get("queue_status") == "receipt_chain_owner_drawer_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_owner_review_drawer_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_owner_review_drawer_checkpoint_preview_ready",
        "safe_to_continue_to_pack_214": checkpoint.get("safe_to_continue_to_pack_214") is True,
        "indexes_present": bool(indexes.get("selected_result_drawers_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_owner_review_drawer_preview_only": all(item.get("owner_review_drawer_preview_only") is True for item in all_items),
        "no_real_owner_note_saved": all(item.get("real_owner_note_saved") is False for item in all_items),
        "no_real_owner_review_decision_saved": all(item.get("real_owner_review_decision_saved") is False for item in all_items),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in all_items),
        "no_real_drawer_state_persisted": all(item.get("real_drawer_state_persisted") is False for item in all_items),
        "no_real_owner_drawer_action_executed": all(item.get("real_owner_drawer_action_executed") is False for item in all_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_note_saves_blocked": all(item.get("owner_note_save_allowed_now") is False for item in all_items),
        "all_decision_saves_blocked": all(item.get("owner_review_decision_save_allowed_now") is False for item in all_items),
        "all_drawer_persistence_blocked": all(item.get("drawer_state_persistence_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 213,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Owner Review Drawer Preview",
        "endpoint": OWNER_REVIEW_DRAWER_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_212": {
            "status": pack_212.get("status"),
            "readiness_score": pack_212.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_213": pack_212.get("summary", {}).get("safe_to_continue_to_pack_213"),
            "save_batch": pack_212.get("summary", {}).get("save_batch"),
        },
        "summary": {
            "selected_result_drawer_count": len(drawers),
            "owner_review_tab_count": len(tabs),
            "owner_note_draft_count": len(drafts),
            "owner_review_decision_count": len(decisions),
            "owner_drawer_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_drawer_queue_item_count": len(queue),
            "real_owner_note_saved_count": safety.get("real_owner_note_saved_count"),
            "real_owner_review_decision_saved_count": safety.get("real_owner_review_decision_saved_count"),
            "real_drawer_selection_saved_count": safety.get("real_drawer_selection_saved_count"),
            "real_drawer_state_persisted_count": safety.get("real_drawer_state_persisted_count"),
            "real_owner_drawer_action_executed_count": safety.get("real_owner_drawer_action_executed_count"),
            "real_archive_written_count": safety.get("real_archive_written_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_214": checkpoint.get("safe_to_continue_to_pack_214"),
            "save_batch": "211-215",
            "save_after_pack": 215,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain owner review drawer preview ready" if readiness_score == 100 else "Receipt chain owner review drawer preview needs review",
        },
        "readiness_checks": readiness_checks,
        "selected_result_drawer_previews": drawers,
        "owner_review_tab_previews": tabs,
        "owner_note_draft_previews": drafts,
        "owner_review_decision_previews": decisions,
        "owner_drawer_action_menu_previews": actions,
        "owner_drawer_queue_previews": queue,
        "owner_review_drawer_safety_summary": safety,
        "owner_review_drawer_checkpoint": checkpoint,
        "owner_review_drawer_indexes": indexes,
    }


def build_receipt_chain_owner_review_drawer_v213_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_owner_review_drawer_v213_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_owner_review_drawer_v213_payload_cached())


def get_receipt_chain_owner_review_drawer_v213_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_owner_review_drawer_v213_payload(force_refresh=force_refresh)


def build_receipt_chain_owner_review_drawer_v213_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_owner_review_drawer_v213_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 213,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "selected_result_drawer_count": summary.get("selected_result_drawer_count"),
        "owner_review_tab_count": summary.get("owner_review_tab_count"),
        "owner_note_draft_count": summary.get("owner_note_draft_count"),
        "owner_review_decision_count": summary.get("owner_review_decision_count"),
        "owner_drawer_action_menu_item_count": summary.get("owner_drawer_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_drawer_queue_item_count": summary.get("owner_drawer_queue_item_count"),
        "real_owner_note_saved_count": summary.get("real_owner_note_saved_count"),
        "real_owner_review_decision_saved_count": summary.get("real_owner_review_decision_saved_count"),
        "real_drawer_selection_saved_count": summary.get("real_drawer_selection_saved_count"),
        "real_drawer_state_persisted_count": summary.get("real_drawer_state_persisted_count"),
        "real_owner_drawer_action_executed_count": summary.get("real_owner_drawer_action_executed_count"),
        "real_archive_written_count": summary.get("real_archive_written_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_214": summary.get("safe_to_continue_to_pack_214"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_owner_review_drawer_v213_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_owner_review_drawer_v213_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_owner_review_drawer_v213_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_owner_review_drawer_v213_status_bridge()
    action = {
        "id": "receipt_chain_owner_review_drawer_v213",
        "label": "Receipt Chain Owner Review Drawer",
        "title": "Receipt Chain Owner Review Drawer Preview",
        "href": OWNER_REVIEW_DRAWER_ENDPOINT,
        "endpoint": OWNER_REVIEW_DRAWER_ENDPOINT,
        "description": "Preview selected result drawer, tabs, note drafts, decision cards, and blocked owner drawer actions.",
        "status": bridge.get("status"),
        "pack": "Pack 213",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_owner_review_drawer_v213_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_owner_review_drawer_v213_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_owner_review_drawer_v213",
        "title": "Receipt Chain Owner Review Drawer",
        "subtitle": "Preview selected result drawers, owner tabs, note drafts, review decisions, and blocked drawer actions.",
        "status": payload.get("status"),
        "href": OWNER_REVIEW_DRAWER_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Drawer readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "drawers", "title": "Selected drawers", "value": summary.get("selected_result_drawer_count"), "label": "Result details"},
            {"id": "tabs", "title": "Review tabs", "value": summary.get("owner_review_tab_count"), "label": "Owner view tabs"},
            {"id": "notes", "title": "Note drafts", "value": summary.get("owner_note_draft_count"), "label": "Preview only"},
            {"id": "blocked", "title": "Blocked actions", "value": summary.get("blocked_action_count"), "label": "No note/decision save"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_owner_note_saved") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No persistence/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "OWNER_REVIEW_DRAWER_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_owner_review_drawer_v213_payload",
    "get_receipt_chain_owner_review_drawer_v213_payload",
    "build_receipt_chain_owner_review_drawer_v213_status_bridge",
    "get_receipt_chain_owner_review_drawer_v213_status_bridge",
    "build_receipt_chain_owner_review_drawer_v213_quick_action",
    "build_receipt_chain_owner_review_drawer_v213_unified_owner_section",
]
