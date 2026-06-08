
"""
PACK 214 - Receipt Chain Evidence Detail Drawer Preview.

Short module filename:
    tower.receipt_chain_evidence_detail_drawer_v214

This module sits on top of Pack 213.

Pack 213 created owner review drawer previews.
Pack 214 adds evidence detail drawer previews:
- redacted evidence panel previews
- evidence source trace cards
- evidence comparison rows
- evidence review tabs
- blocked evidence action menu
- owner evidence review queue preview
- no real evidence export
- no real archive write
- no raw evidence reveal

Important:
- simulated-only
- evidence-detail-drawer-preview-only
- redacted evidence only
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


PACK_ID = "PACK_214"
EVIDENCE_DETAIL_DRAWER_ENDPOINT = "/tower/receipt-chain-evidence-detail-drawer-v214.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-owner-review-drawer-v213.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "evidence_detail_drawer_preview_only": True,
        "redacted_evidence_panel_preview_only": True,
        "evidence_source_trace_preview_only": True,
        "evidence_comparison_row_preview_only": True,
        "evidence_review_tab_preview_only": True,
        "evidence_action_menu_preview_only": True,
        "owner_evidence_review_queue_preview_only": True,
        "owner_review_drawer_preview_only": True,
        "selected_result_drawer_preview_only": True,
        "owner_review_tab_preview_only": True,
        "owner_note_draft_preview_only": True,
        "owner_review_decision_preview_only": True,
        "owner_drawer_action_menu_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "evidence_export_allowed_now": False,
        "evidence_panel_save_allowed_now": False,
        "evidence_trace_save_allowed_now": False,
        "evidence_comparison_save_allowed_now": False,
        "evidence_review_save_allowed_now": False,
        "evidence_action_execution_allowed_now": False,
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
        "archive_packet_write_allowed_now": False,
        "archive_packet_seal_allowed_now": False,
        "archive_export_allowed_now": False,
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
        "real_evidence_panel_saved": False,
        "real_evidence_trace_saved": False,
        "real_evidence_comparison_saved": False,
        "real_evidence_review_saved": False,
        "real_evidence_action_executed": False,
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
        "real_archive_packet_written": False,
        "real_archive_packet_sealed": False,
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


def _load_pack_213_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_owner_review_drawer_v213")
        fn = getattr(mod, "build_receipt_chain_owner_review_drawer_v213_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_213",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0, "safe_to_continue_to_pack_214": False},
            "selected_result_drawer_previews": [],
            "owner_review_tab_previews": [],
            "owner_note_draft_previews": [],
            "owner_review_decision_previews": [],
            "owner_drawer_action_menu_previews": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_213",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0, "safe_to_continue_to_pack_214": False},
        "selected_result_drawer_previews": [],
        "owner_review_tab_previews": [],
        "owner_note_draft_previews": [],
        "owner_review_decision_previews": [],
        "owner_drawer_action_menu_previews": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_redacted_evidence_panels(pack_213: Dict[str, object]) -> List[Dict[str, object]]:
    drawers = [item for item in _list(pack_213.get("selected_result_drawer_previews")) if isinstance(item, dict)]
    selected = drawers[:6]

    panels = []
    for sequence, source in enumerate(selected, start=1):
        source_key = source.get("selected_result_key") or f"drawer_{sequence}"
        panel = {
            "redacted_evidence_panel_preview_id": f"receipt_chain_evidence_panel_{_stable_hash((PACK_ID, source_key), 18)}",
            "evidence_panel_key": f"panel_{source_key}",
            "label": f"Redacted Evidence Panel {sequence}",
            "panel_type": source.get("result_type") or "unknown",
            "sequence": sequence,
            "source_drawer_key": source_key,
            "source_preview_id": source.get("selected_result_drawer_preview_id"),
            "redacted_field_count": 8,
            "safe_field_count": 6,
            "raw_field_count": 0,
            "evidence_fields_preview": [
                "pack_id",
                "source_endpoint",
                "readiness_state",
                "safety_state",
                "preview_result_type",
                "owner_review_state",
            ],
            "raw_evidence_redacted": True,
            "evidence_panel_save_allowed_now": False,
            "panel_status": "receipt_chain_redacted_evidence_panel_preview_ready",
            "panel_result_type": "tower_receipt_chain_redacted_evidence_panel_preview",
            "safe_preview_only": True,
        }
        panel.update(_base_flags())
        panels.append(panel)

    return panels


def _build_evidence_source_trace_cards(pack_213: Dict[str, object], panels: List[Dict[str, object]]) -> List[Dict[str, object]]:
    panel_keys = [item.get("evidence_panel_key") for item in panels]

    trace_defs = [
        ("source_pack_212_trace", "Source Pack 212 filter/search trace", "source_pack"),
        ("pack_213_drawer_trace", "Pack 213 owner drawer trace", "owner_drawer"),
        ("result_selection_trace", "Result selection trace", "selection"),
        ("owner_note_draft_trace", "Owner note draft trace", "note_draft"),
        ("decision_preview_trace", "Decision preview trace", "decision"),
        ("raw_redaction_trace", "Raw evidence redaction trace", "redaction"),
    ]

    traces = []
    for sequence, (trace_key, label, trace_type) in enumerate(trace_defs, start=1):
        trace = {
            "evidence_source_trace_card_preview_id": f"receipt_chain_evidence_source_trace_{_stable_hash((PACK_ID, trace_key), 18)}",
            "evidence_source_trace_key": trace_key,
            "label": label,
            "trace_type": trace_type,
            "sequence": sequence,
            "linked_evidence_panel_keys": panel_keys,
            "linked_evidence_panel_count": len(panel_keys),
            "source_endpoint_chain": [
                "/tower/receipt-chain-checkpoint-filter-search-v212.json",
                "/tower/receipt-chain-owner-review-drawer-v213.json",
                EVIDENCE_DETAIL_DRAWER_ENDPOINT,
            ],
            "trace_save_allowed_now": False,
            "trace_status": "receipt_chain_evidence_source_trace_card_preview_ready",
            "trace_result_type": "tower_receipt_chain_evidence_source_trace_card_preview",
            "safe_preview_only": True,
        }
        trace.update(_base_flags())
        traces.append(trace)

    return traces


def _build_evidence_comparison_rows(panels: List[Dict[str, object]], traces: List[Dict[str, object]]) -> List[Dict[str, object]]:
    trace_keys = [item.get("evidence_source_trace_key") for item in traces]

    comparison_defs = [
        ("readiness_compare", "Readiness compare", "readiness", "ready", "ready"),
        ("safety_compare", "Safety compare", "safety", "blocked", "blocked"),
        ("raw_reveal_compare", "Raw reveal compare", "raw_evidence", "redacted", "redacted"),
        ("export_compare", "Export compare", "export", "blocked", "blocked"),
        ("archive_write_compare", "Archive write compare", "archive", "blocked", "blocked"),
        ("owner_action_compare", "Owner action compare", "owner_action", "preview", "preview"),
        ("drawer_state_compare", "Drawer state compare", "drawer_state", "not_persisted", "not_persisted"),
        ("next_pack_compare", "Next Pack 215 compare", "next_pack", "ready", "ready"),
    ]

    rows = []
    for sequence, (row_key, label, row_type, left_value, right_value) in enumerate(comparison_defs, start=1):
        row = {
            "evidence_comparison_row_preview_id": f"receipt_chain_evidence_comparison_{_stable_hash((PACK_ID, row_key), 18)}",
            "evidence_comparison_row_key": row_key,
            "label": label,
            "comparison_type": row_type,
            "sequence": sequence,
            "left_value_preview": left_value,
            "right_value_preview": right_value,
            "comparison_result": "match",
            "linked_trace_keys": trace_keys,
            "linked_trace_count": len(trace_keys),
            "comparison_save_allowed_now": False,
            "row_status": "receipt_chain_evidence_comparison_row_preview_ready",
            "row_result_type": "tower_receipt_chain_evidence_comparison_row_preview",
            "safe_preview_only": True,
        }
        row.update(_base_flags())
        rows.append(row)

    return rows


def _build_evidence_review_tabs(panels: List[Dict[str, object]], traces: List[Dict[str, object]], rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    tab_defs = [
        ("evidence_overview_tab", "Evidence Overview", "overview", len(panels)),
        ("redaction_tab", "Redaction", "redaction", len(panels)),
        ("source_trace_tab", "Source Trace", "source_trace", len(traces)),
        ("comparison_tab", "Comparison", "comparison", len(rows)),
        ("owner_review_tab", "Owner Review", "owner_review", len(panels)),
        ("next_pack_tab", "Next Pack 215", "next_pack", 1),
    ]

    tabs = []
    for sequence, (tab_key, label, tab_type, linked_count) in enumerate(tab_defs, start=1):
        tab = {
            "evidence_review_tab_preview_id": f"receipt_chain_evidence_review_tab_{_stable_hash((PACK_ID, tab_key), 18)}",
            "evidence_review_tab_key": tab_key,
            "label": label,
            "tab_type": tab_type,
            "sequence": sequence,
            "linked_preview_item_count": int(linked_count or 0),
            "tab_state_persistence_allowed_now": False,
            "tab_status": "receipt_chain_evidence_review_tab_preview_ready",
            "tab_result_type": "tower_receipt_chain_evidence_review_tab_preview",
            "safe_preview_only": True,
        }
        tab.update(_base_flags())
        tabs.append(tab)

    return tabs


def _build_evidence_actions(panels: List[Dict[str, object]], rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    action_defs = [
        ("preview_evidence_status", "Preview evidence status", True, "Preview evidence drawer health."),
        ("preview_redacted_panels", "Preview redacted panels", True, "Preview safe redacted evidence panels."),
        ("open_pack_213_owner_drawer", "Open Pack 213 owner drawer", True, "Open Pack 213 JSON."),
        ("blocked_export_evidence", "Export evidence", False, "Blocked: real evidence export is not enabled in Pack 214."),
        ("blocked_write_archive_packet", "Write archive packet", False, "Blocked: real archive packet write is not enabled in Pack 214."),
        ("blocked_seal_archive_packet", "Seal archive packet", False, "Blocked: real archive packet seal is not enabled in Pack 214."),
        ("blocked_save_evidence_review", "Save evidence review", False, "Blocked: real evidence review save is not enabled in Pack 214."),
        ("blocked_reveal_raw_evidence", "Reveal raw evidence", False, "Blocked: raw evidence reveal is not enabled in Pack 214."),
    ]

    actions = []
    for sequence, (action_key, label, allowed, description) in enumerate(action_defs, start=1):
        action = {
            "evidence_action_menu_item_preview_id": f"receipt_chain_evidence_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "evidence_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "redacted_evidence_panel_count": len(panels),
            "evidence_comparison_row_count": len(rows),
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_evidence_action": False,
            "action_status": "receipt_chain_evidence_action_preview_ready" if allowed else "receipt_chain_evidence_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_evidence_action_menu_preview",
            "safe_preview_only": True,
        }
        action.update(_base_flags())
        actions.append(action)

    return actions


def _build_owner_evidence_queue(panels, traces, rows, tabs, actions) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_redacted_evidence_panels", "Review redacted evidence panels", "panel_review", len(panels)),
        ("review_source_trace_cards", "Review source trace cards", "trace_review", len(traces)),
        ("review_comparison_rows", "Review comparison rows", "comparison_review", len(rows)),
        ("review_blocked_evidence_actions", "Review blocked evidence actions", "action_review", sum(1 for item in actions if item.get("blocked_in_preview") is True)),
        ("prepare_pack_215_batch_checkpoint", "Prepare Pack 215 batch checkpoint", "next_pack", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_evidence_queue_item_preview_id": f"receipt_chain_owner_evidence_queue_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_review_allowed_now": False,
            "queue_status": "receipt_chain_owner_evidence_queue_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_evidence_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(panels, traces, rows, tabs, actions, queue) -> Dict[str, object]:
    all_items = panels + traces + rows + tabs + actions + queue

    summary = {
        "evidence_detail_drawer_safety_summary_id": f"receipt_chain_evidence_detail_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "redacted_evidence_panel_count": len(panels),
        "evidence_source_trace_card_count": len(traces),
        "evidence_comparison_row_count": len(rows),
        "evidence_review_tab_count": len(tabs),
        "evidence_action_menu_item_count": len(actions),
        "allowed_preview_action_count": sum(1 for action in actions if action.get("allowed_in_preview") is True),
        "blocked_action_count": sum(1 for action in actions if action.get("blocked_in_preview") is True),
        "owner_evidence_review_queue_item_count": len(queue),
        "raw_field_count": sum(int(panel.get("raw_field_count") or 0) for panel in panels),
        "real_evidence_exported_count": 0,
        "real_evidence_panel_saved_count": 0,
        "real_evidence_trace_saved_count": 0,
        "real_evidence_comparison_saved_count": 0,
        "real_evidence_review_saved_count": 0,
        "real_evidence_action_executed_count": 0,
        "real_archive_written_count": 0,
        "real_archive_packet_written_count": 0,
        "real_archive_packet_sealed_count": 0,
        "real_archive_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_panels_preview_only": all(item.get("redacted_evidence_panel_preview_only") is True for item in panels),
        "all_traces_preview_only": all(item.get("evidence_source_trace_preview_only") is True for item in traces),
        "all_comparisons_preview_only": all(item.get("evidence_comparison_row_preview_only") is True for item in rows),
        "all_tabs_preview_only": all(item.get("evidence_review_tab_preview_only") is True for item in tabs),
        "all_actions_preview_only": all(item.get("evidence_action_menu_preview_only") is True for item in actions),
        "all_queue_preview_only": all(item.get("owner_evidence_review_queue_preview_only") is True for item in queue),
        "all_raw_fields_redacted": True,
        "all_real_evidence_writes_blocked": True,
        "summary_status": "receipt_chain_evidence_detail_drawer_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_evidence_detail_drawer_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("redacted_evidence_panel_count") == 6
        and safety.get("evidence_source_trace_card_count") == 6
        and safety.get("evidence_comparison_row_count") == 8
        and safety.get("evidence_review_tab_count") == 6
        and safety.get("evidence_action_menu_item_count") == 8
        and safety.get("allowed_preview_action_count") == 3
        and safety.get("blocked_action_count") == 5
        and safety.get("owner_evidence_review_queue_item_count") == 5
        and safety.get("raw_field_count") == 0
        and safety.get("real_evidence_exported_count") == 0
        and safety.get("real_evidence_panel_saved_count") == 0
        and safety.get("real_evidence_trace_saved_count") == 0
        and safety.get("real_evidence_comparison_saved_count") == 0
        and safety.get("real_evidence_review_saved_count") == 0
        and safety.get("real_archive_written_count") == 0
        and safety.get("real_archive_packet_written_count") == 0
        and safety.get("real_archive_packet_sealed_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "evidence_detail_drawer_checkpoint_id": f"receipt_chain_evidence_detail_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_evidence_detail_drawer_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_evidence_detail_drawer_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_evidence_detail_drawer_checkpoint_preview",
        "safe_to_continue_to_pack_215": checkpoint_ok,
        "save_batch": "211-215",
        "save_after_pack": 215,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(panels, traces, rows, tabs, actions, queue, checkpoint) -> Dict[str, object]:
    indexes = {
        "redacted_evidence_panels_by_id": {},
        "redacted_evidence_panels_by_key": {},
        "evidence_source_traces_by_id": {},
        "evidence_source_traces_by_key": {},
        "evidence_comparison_rows_by_id": {},
        "evidence_comparison_rows_by_key": {},
        "evidence_review_tabs_by_id": {},
        "evidence_review_tabs_by_key": {},
        "evidence_actions_by_id": {},
        "evidence_actions_by_key": {},
        "owner_evidence_queue_by_id": {},
        "owner_evidence_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in panels:
        indexes["redacted_evidence_panels_by_id"][item.get("redacted_evidence_panel_preview_id")] = item
        indexes["redacted_evidence_panels_by_key"][item.get("evidence_panel_key")] = item

    for item in traces:
        indexes["evidence_source_traces_by_id"][item.get("evidence_source_trace_card_preview_id")] = item
        indexes["evidence_source_traces_by_key"][item.get("evidence_source_trace_key")] = item

    for item in rows:
        indexes["evidence_comparison_rows_by_id"][item.get("evidence_comparison_row_preview_id")] = item
        indexes["evidence_comparison_rows_by_key"][item.get("evidence_comparison_row_key")] = item

    for item in tabs:
        indexes["evidence_review_tabs_by_id"][item.get("evidence_review_tab_preview_id")] = item
        indexes["evidence_review_tabs_by_key"][item.get("evidence_review_tab_key")] = item

    for item in actions:
        indexes["evidence_actions_by_id"][item.get("evidence_action_menu_item_preview_id")] = item
        indexes["evidence_actions_by_key"][item.get("evidence_action_key")] = item

    for item in queue:
        indexes["owner_evidence_queue_by_id"][item.get("owner_evidence_queue_item_preview_id")] = item
        indexes["owner_evidence_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("evidence_detail_drawer_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_evidence_detail_drawer_v214_payload_cached() -> Dict[str, object]:
    pack_213 = _load_pack_213_payload(force_refresh=True)

    panels = _build_redacted_evidence_panels(pack_213)
    traces = _build_evidence_source_trace_cards(pack_213, panels)
    rows = _build_evidence_comparison_rows(panels, traces)
    tabs = _build_evidence_review_tabs(panels, traces, rows)
    actions = _build_evidence_actions(panels, rows)
    queue = _build_owner_evidence_queue(panels, traces, rows, tabs, actions)
    safety = _build_safety_summary(panels, traces, rows, tabs, actions, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(panels, traces, rows, tabs, actions, queue, checkpoint)

    all_items = panels + traces + rows + tabs + actions + queue

    readiness_checks = {
        "pack_213_ready": pack_213.get("status") == "ready",
        "pack_213_safe_to_continue": pack_213.get("summary", {}).get("safe_to_continue_to_pack_214") is True,
        "has_redacted_evidence_panels": len(panels) == 6,
        "has_evidence_source_traces": len(traces) == 6,
        "has_evidence_comparison_rows": len(rows) == 8,
        "has_evidence_review_tabs": len(tabs) == 6,
        "has_evidence_actions": len(actions) == 8,
        "has_allowed_preview_actions": sum(1 for item in actions if item.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for item in actions if item.get("blocked_in_preview") is True) == 5,
        "has_owner_evidence_queue": len(queue) == 5,
        "no_raw_fields": sum(int(panel.get("raw_field_count") or 0) for panel in panels) == 0,
        "all_panels_ready": all(item.get("panel_status") == "receipt_chain_redacted_evidence_panel_preview_ready" for item in panels),
        "all_traces_ready": all(item.get("trace_status") == "receipt_chain_evidence_source_trace_card_preview_ready" for item in traces),
        "all_comparisons_ready": all(item.get("row_status") == "receipt_chain_evidence_comparison_row_preview_ready" for item in rows),
        "all_tabs_ready": all(item.get("tab_status") == "receipt_chain_evidence_review_tab_preview_ready" for item in tabs),
        "all_actions_ready_or_blocked": all(item.get("action_status") in {"receipt_chain_evidence_action_preview_ready", "receipt_chain_evidence_action_preview_blocked"} for item in actions),
        "all_queue_blocked": all(item.get("queue_status") == "receipt_chain_owner_evidence_queue_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_evidence_detail_drawer_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_evidence_detail_drawer_checkpoint_preview_ready",
        "safe_to_continue_to_pack_215": checkpoint.get("safe_to_continue_to_pack_215") is True,
        "indexes_present": bool(indexes.get("redacted_evidence_panels_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_evidence_detail_drawer_preview_only": all(item.get("evidence_detail_drawer_preview_only") is True for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_evidence_panel_saved": all(item.get("real_evidence_panel_saved") is False for item in all_items),
        "no_real_evidence_trace_saved": all(item.get("real_evidence_trace_saved") is False for item in all_items),
        "no_real_evidence_comparison_saved": all(item.get("real_evidence_comparison_saved") is False for item in all_items),
        "no_real_evidence_review_saved": all(item.get("real_evidence_review_saved") is False for item in all_items),
        "no_real_evidence_action_executed": all(item.get("real_evidence_action_executed") is False for item in all_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in all_items),
        "no_real_archive_packet_written": all(item.get("real_archive_packet_written") is False for item in all_items),
        "no_real_archive_packet_sealed": all(item.get("real_archive_packet_sealed") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_evidence_exports_blocked": all(item.get("evidence_export_allowed_now") is False for item in all_items),
        "all_archive_writes_blocked": all(item.get("archive_write_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 214,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Evidence Detail Drawer Preview",
        "endpoint": EVIDENCE_DETAIL_DRAWER_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_213": {
            "status": pack_213.get("status"),
            "readiness_score": pack_213.get("summary", {}).get("readiness_score"),
            "safe_to_continue_to_pack_214": pack_213.get("summary", {}).get("safe_to_continue_to_pack_214"),
            "save_batch": pack_213.get("summary", {}).get("save_batch"),
        },
        "summary": {
            "redacted_evidence_panel_count": len(panels),
            "evidence_source_trace_card_count": len(traces),
            "evidence_comparison_row_count": len(rows),
            "evidence_review_tab_count": len(tabs),
            "evidence_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "owner_evidence_review_queue_item_count": len(queue),
            "raw_field_count": safety.get("raw_field_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "real_evidence_panel_saved_count": safety.get("real_evidence_panel_saved_count"),
            "real_evidence_trace_saved_count": safety.get("real_evidence_trace_saved_count"),
            "real_evidence_comparison_saved_count": safety.get("real_evidence_comparison_saved_count"),
            "real_evidence_review_saved_count": safety.get("real_evidence_review_saved_count"),
            "real_evidence_action_executed_count": safety.get("real_evidence_action_executed_count"),
            "real_archive_written_count": safety.get("real_archive_written_count"),
            "real_archive_packet_written_count": safety.get("real_archive_packet_written_count"),
            "real_archive_packet_sealed_count": safety.get("real_archive_packet_sealed_count"),
            "real_archive_exported_count": safety.get("real_archive_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_215": checkpoint.get("safe_to_continue_to_pack_215"),
            "save_batch": "211-215",
            "save_after_pack": 215,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain evidence detail drawer preview ready" if readiness_score == 100 else "Receipt chain evidence detail drawer preview needs review",
        },
        "readiness_checks": readiness_checks,
        "redacted_evidence_panel_previews": panels,
        "evidence_source_trace_card_previews": traces,
        "evidence_comparison_row_previews": rows,
        "evidence_review_tab_previews": tabs,
        "evidence_action_menu_previews": actions,
        "owner_evidence_review_queue_previews": queue,
        "evidence_detail_drawer_safety_summary": safety,
        "evidence_detail_drawer_checkpoint": checkpoint,
        "evidence_detail_drawer_indexes": indexes,
    }


def build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_evidence_detail_drawer_v214_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_evidence_detail_drawer_v214_payload_cached())


def get_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh=force_refresh)


def build_receipt_chain_evidence_detail_drawer_v214_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_evidence_detail_drawer_v214_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 214,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "redacted_evidence_panel_count": summary.get("redacted_evidence_panel_count"),
        "evidence_source_trace_card_count": summary.get("evidence_source_trace_card_count"),
        "evidence_comparison_row_count": summary.get("evidence_comparison_row_count"),
        "evidence_review_tab_count": summary.get("evidence_review_tab_count"),
        "evidence_action_menu_item_count": summary.get("evidence_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "owner_evidence_review_queue_item_count": summary.get("owner_evidence_review_queue_item_count"),
        "raw_field_count": summary.get("raw_field_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "real_evidence_panel_saved_count": summary.get("real_evidence_panel_saved_count"),
        "real_evidence_trace_saved_count": summary.get("real_evidence_trace_saved_count"),
        "real_evidence_comparison_saved_count": summary.get("real_evidence_comparison_saved_count"),
        "real_evidence_review_saved_count": summary.get("real_evidence_review_saved_count"),
        "real_evidence_action_executed_count": summary.get("real_evidence_action_executed_count"),
        "real_archive_written_count": summary.get("real_archive_written_count"),
        "real_archive_packet_written_count": summary.get("real_archive_packet_written_count"),
        "real_archive_packet_sealed_count": summary.get("real_archive_packet_sealed_count"),
        "real_archive_exported_count": summary.get("real_archive_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_215": summary.get("safe_to_continue_to_pack_215"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_evidence_detail_drawer_v214_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_evidence_detail_drawer_v214_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_evidence_detail_drawer_v214_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_evidence_detail_drawer_v214_status_bridge()
    action = {
        "id": "receipt_chain_evidence_detail_drawer_v214",
        "label": "Receipt Chain Evidence Detail Drawer",
        "title": "Receipt Chain Evidence Detail Drawer Preview",
        "href": EVIDENCE_DETAIL_DRAWER_ENDPOINT,
        "endpoint": EVIDENCE_DETAIL_DRAWER_ENDPOINT,
        "description": "Preview redacted evidence panels, source trace cards, comparisons, and blocked evidence actions.",
        "status": bridge.get("status"),
        "pack": "Pack 214",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_evidence_detail_drawer_v214_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_evidence_detail_drawer_v214_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_evidence_detail_drawer_v214",
        "title": "Receipt Chain Evidence Detail Drawer",
        "subtitle": "Preview redacted evidence panels, source trace cards, comparison rows, and blocked evidence actions.",
        "status": payload.get("status"),
        "href": EVIDENCE_DETAIL_DRAWER_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Evidence readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "panels", "title": "Evidence panels", "value": summary.get("redacted_evidence_panel_count"), "label": "Redacted only"},
            {"id": "traces", "title": "Source traces", "value": summary.get("evidence_source_trace_card_count"), "label": "Trace cards"},
            {"id": "comparisons", "title": "Comparison rows", "value": summary.get("evidence_comparison_row_count"), "label": "Safe comparisons"},
            {"id": "blocked", "title": "Blocked actions", "value": summary.get("blocked_action_count"), "label": "No export/raw reveal"},
            {"id": "safety", "title": "Safety", "value": "Blocked" if checks.get("no_real_evidence_exported") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "Evidence safe"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "EVIDENCE_DETAIL_DRAWER_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_evidence_detail_drawer_v214_payload",
    "get_receipt_chain_evidence_detail_drawer_v214_payload",
    "build_receipt_chain_evidence_detail_drawer_v214_status_bridge",
    "get_receipt_chain_evidence_detail_drawer_v214_status_bridge",
    "build_receipt_chain_evidence_detail_drawer_v214_quick_action",
    "build_receipt_chain_evidence_detail_drawer_v214_unified_owner_section",
]
