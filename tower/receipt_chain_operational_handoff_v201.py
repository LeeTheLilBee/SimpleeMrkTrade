
"""
PACK 201 - Receipt Chain Operational Handoff Preview.

Short module filename:
    tower.receipt_chain_operational_handoff_v201

This module sits on top of Pack 200.

Pack 200 proves Packs 196-199 are ready as a receipt-chain checkpoint.
Pack 201 creates the next-era operational handoff preview:
- checkpoint-to-next-workstream routing
- post-checkpoint owner action menu preview
- safe handoff evidence map
- blocked execution/write/reveal proof
- readiness board for the next five-pack batch

Important:
- simulated-only
- operational-handoff-preview-only
- receipt-chain-handoff-preview-only
- no real action executed
- no real filter preference saved
- no real navigation state persisted
- no real drawer selection saved
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


PACK_ID = "PACK_201"
OPERATIONAL_HANDOFF_ENDPOINT = "/tower/receipt-chain-operational-handoff-v201.json"
SOURCE_ENDPOINT = "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"


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
        "operational_handoff_preview_only": True,
        "receipt_chain_handoff_preview_only": True,
        "checkpoint_preview_only": True,
        "receipt_chain_checkpoint_preview_only": True,
        "owner_action_menu_preview_only": True,
        "evidence_map_preview_only": True,
        "routing_preview_only": True,
        "receipt_detail_focus_preview_only": True,
        "receipt_safety_detail_preview_only": True,
        "receipt_action_panel_preview_only": True,
        "receipt_breadcrumb_preview_only": True,
        "action_receipt_navigation_preview_only": True,
        "receipt_selection_preview_only": True,
        "action_receipt_filter_preview_only": True,
        "search_facet_preview_only": True,
        "filter_preview_only": True,
        "filter_navigation_preview_only": True,
        "action_receipt_preview_only": True,
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


def _load_pack_200_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.owner_note_vc_nav_receipt_chain_checkpoint_v200")
        fn = getattr(mod, "build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_200",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {
                "readiness_score": 0,
                "safe_to_save_packs_196_to_200": False,
                "ready_pack_count": 0,
                "review_pack_count": 1,
            },
            "final_receipt_chain_checkpoint": {},
            "receipt_chain_pack_cards": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_200",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {
            "readiness_score": 0,
            "safe_to_save_packs_196_to_200": False,
            "ready_pack_count": 0,
            "review_pack_count": 1,
        },
        "final_receipt_chain_checkpoint": {},
        "receipt_chain_pack_cards": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_handoff_routes(pack_200: Dict[str, object]) -> List[Dict[str, object]]:
    summary = pack_200.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    route_defs = [
        (
            "checkpoint_to_operational_hardening",
            "Operational hardening lane",
            "Begin the post-Pack-200 containment and operational-hardening block.",
            "ready" if summary.get("safe_to_save_packs_196_to_200") is True else "blocked",
            1,
        ),
        (
            "checkpoint_to_receipt_vault_expansion",
            "Receipt vault expansion lane",
            "Prepare receipt vault packet previews and controlled evidence bundle structure.",
            "ready" if summary.get("safe_to_save_packs_196_to_200") is True else "blocked",
            2,
        ),
        (
            "checkpoint_to_owner_workflow_surface",
            "Owner workflow surface lane",
            "Prepare owner-facing action routing without executing real owner actions.",
            "ready" if summary.get("safe_to_save_packs_196_to_200") is True else "blocked",
            3,
        ),
        (
            "checkpoint_to_recheck_expiration_hooks",
            "Recheck and expiration lane",
            "Prepare preview-only renewal/recheck handoff hooks for later packs.",
            "ready" if summary.get("safe_to_save_packs_196_to_200") is True else "blocked",
            4,
        ),
        (
            "checkpoint_to_gateway_readiness",
            "Gateway readiness lane",
            "Prepare future Tower gateway readiness checks while keeping access grants blocked.",
            "ready" if summary.get("safe_to_save_packs_196_to_200") is True else "blocked",
            5,
        ),
    ]

    routes = []
    for route_id, label, description, route_state, sequence in route_defs:
        route = {
            "handoff_route_id": f"receipt_chain_handoff_route_{_stable_hash((PACK_ID, route_id), 18)}",
            "route_key": route_id,
            "label": label,
            "description": description,
            "sequence": sequence,
            "route_state": route_state,
            "source_checkpoint_endpoint": SOURCE_ENDPOINT,
            "route_status": "receipt_chain_handoff_route_preview_ready" if route_state == "ready" else "receipt_chain_handoff_route_preview_blocked",
            "route_result_type": "tower_receipt_chain_operational_handoff_route_preview",
            "safe_preview_only": True,
        }
        route.update(_base_flags())
        routes.append(route)

    return routes


def _build_owner_action_menu(routes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    menu_defs = [
        ("review_handoff_summary", "Review handoff summary", True, "Preview the post-checkpoint handoff summary."),
        ("preview_next_batch", "Preview next five-pack batch", True, "Preview Packs 201-205 planning lane."),
        ("open_receipt_chain_checkpoint", "Open receipt-chain checkpoint", True, "Open Pack 200 checkpoint JSON."),
        ("blocked_execute_handoff", "Execute operational handoff", False, "Blocked: no real handoff execution yet."),
        ("blocked_export_evidence_bundle", "Export evidence bundle", False, "Blocked: no real evidence export yet."),
        ("blocked_grant_gateway_access", "Grant gateway access", False, "Blocked: no real gateway access grant yet."),
    ]

    actions = []
    ready_route_count = sum(1 for route in routes if route.get("route_state") == "ready")

    for sequence, (action_key, label, allowed, description) in enumerate(menu_defs, start=1):
        action = {
            "owner_action_menu_item_id": f"receipt_chain_handoff_owner_action_{_stable_hash((PACK_ID, action_key), 18)}",
            "owner_action_key": action_key,
            "label": label,
            "description": description,
            "sequence": sequence,
            "ready_route_count": ready_route_count,
            "allowed_in_preview": bool(allowed),
            "blocked_in_preview": not bool(allowed),
            "executes_real_action": False,
            "action_status": "receipt_chain_handoff_owner_action_preview_ready" if allowed else "receipt_chain_handoff_owner_action_preview_blocked",
            "action_result_type": "tower_receipt_chain_operational_handoff_owner_action_preview",
            "safe_preview_only": True,
        }
        action.update(_base_flags())
        actions.append(action)

    return actions


def _build_evidence_map(pack_200: Dict[str, object], routes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    cards = _list(pack_200.get("receipt_chain_pack_cards"))
    mapped_cards = [card for card in cards if isinstance(card, dict)]

    evidence_items = []
    for sequence, card in enumerate(mapped_cards, start=1):
        pack_number = card.get("pack_number")
        item = {
            "handoff_evidence_map_item_id": f"receipt_chain_handoff_evidence_{_stable_hash((PACK_ID, pack_number), 18)}",
            "source_pack_number": pack_number,
            "source_pack_id": card.get("pack_id"),
            "source_endpoint": card.get("endpoint"),
            "source_card_id": card.get("receipt_chain_pack_card_id"),
            "source_card_status": card.get("card_status"),
            "metric_checks_ok": card.get("all_metric_checks_ok"),
            "safety_flags_ok": card.get("safety_flags_ok"),
            "sequence": sequence,
            "mapped_route_keys": [route.get("route_key") for route in routes],
            "raw_evidence_redacted": True,
            "evidence_export_allowed_now": False,
            "map_status": "receipt_chain_handoff_evidence_map_item_preview_ready",
            "map_result_type": "tower_receipt_chain_operational_handoff_evidence_map_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        evidence_items.append(item)

    return evidence_items


def _build_next_batch_board() -> List[Dict[str, object]]:
    pack_defs = [
        (201, "Operational handoff preview", "active_current_pack"),
        (202, "Receipt handoff saved view preview", "planned_preview_only"),
        (203, "Evidence bundle packet preview", "planned_preview_only"),
        (204, "Recheck/expiration handoff hook preview", "planned_preview_only"),
        (205, "Five-pack operational checkpoint", "planned_checkpoint"),
    ]

    cards = []
    for sequence, (pack_number, label, lane_state) in enumerate(pack_defs, start=1):
        card = {
            "next_batch_card_id": f"receipt_chain_next_batch_card_{_stable_hash((PACK_ID, pack_number), 18)}",
            "pack_number": pack_number,
            "label": label,
            "lane_state": lane_state,
            "sequence": sequence,
            "save_batch": "201-205",
            "save_after_pack": 205,
            "card_status": "receipt_chain_next_batch_card_preview_ready",
            "card_result_type": "tower_receipt_chain_next_batch_card_preview",
            "safe_preview_only": True,
        }
        card.update(_base_flags())
        cards.append(card)

    return cards


def _build_safety_summary(routes: List[Dict[str, object]], actions: List[Dict[str, object]], evidence_items: List[Dict[str, object]]) -> Dict[str, object]:
    blocked_actions = [action for action in actions if action.get("blocked_in_preview") is True]
    allowed_preview_actions = [action for action in actions if action.get("allowed_in_preview") is True]

    summary = {
        "handoff_safety_summary_id": f"receipt_chain_handoff_safety_{_stable_hash((PACK_ID, len(routes), len(actions), len(evidence_items)), 18)}",
        "handoff_route_count": len(routes),
        "ready_handoff_route_count": sum(1 for route in routes if route.get("route_state") == "ready"),
        "owner_action_menu_item_count": len(actions),
        "allowed_preview_action_count": len(allowed_preview_actions),
        "blocked_action_count": len(blocked_actions),
        "evidence_map_item_count": len(evidence_items),
        "real_action_executed_count": 0,
        "real_handoff_executed_count": 0,
        "real_owner_action_executed_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "persistence_write_count": 0,
        "all_routes_preview_only": all(route.get("operational_handoff_preview_only") is True for route in routes),
        "all_owner_actions_preview_only": all(action.get("owner_action_menu_preview_only") is True for action in actions),
        "all_evidence_maps_preview_only": all(item.get("evidence_map_preview_only") is True for item in evidence_items),
        "all_real_execution_blocked": True,
        "summary_status": "receipt_chain_handoff_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_operational_handoff_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_handoff_checkpoint(routes: List[Dict[str, object]], actions: List[Dict[str, object]], evidence_items: List[Dict[str, object]], next_batch: List[Dict[str, object]], safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        len(routes) == 5
        and len(actions) == 6
        and len(evidence_items) == 4
        and len(next_batch) == 5
        and safety.get("real_action_executed_count") == 0
        and safety.get("real_handoff_executed_count") == 0
        and safety.get("real_owner_action_executed_count") == 0
        and safety.get("real_evidence_exported_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
        and safety.get("persistence_write_count") == 0
    )

    checkpoint = {
        "operational_handoff_checkpoint_id": f"receipt_chain_operational_handoff_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_operational_handoff_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_operational_handoff_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_operational_handoff_checkpoint_preview",
        "safe_to_continue_to_pack_202": checkpoint_ok,
        "save_batch": "201-205",
        "save_after_pack": 205,
        "handoff_safety_summary_id": safety.get("handoff_safety_summary_id"),
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(routes: List[Dict[str, object]], actions: List[Dict[str, object]], evidence: List[Dict[str, object]], next_batch: List[Dict[str, object]], checkpoint: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "handoff_routes_by_id": {},
        "handoff_routes_by_key": {},
        "owner_action_menu_items_by_id": {},
        "owner_action_menu_items_by_key": {},
        "evidence_map_items_by_id": {},
        "evidence_map_items_by_pack_number": {},
        "next_batch_cards_by_id": {},
        "next_batch_cards_by_pack_number": {},
        "operational_handoff_checkpoint_by_id": {},
    }

    for route in routes:
        indexes["handoff_routes_by_id"][route.get("handoff_route_id")] = route
        indexes["handoff_routes_by_key"][route.get("route_key")] = route

    for action in actions:
        indexes["owner_action_menu_items_by_id"][action.get("owner_action_menu_item_id")] = action
        indexes["owner_action_menu_items_by_key"][action.get("owner_action_key")] = action

    for item in evidence:
        indexes["evidence_map_items_by_id"][item.get("handoff_evidence_map_item_id")] = item
        indexes["evidence_map_items_by_pack_number"][str(item.get("source_pack_number"))] = item

    for card in next_batch:
        indexes["next_batch_cards_by_id"][card.get("next_batch_card_id")] = card
        indexes["next_batch_cards_by_pack_number"][str(card.get("pack_number"))] = card

    indexes["operational_handoff_checkpoint_by_id"][checkpoint.get("operational_handoff_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_operational_handoff_v201_payload_cached() -> Dict[str, object]:
    pack_200 = _load_pack_200_payload(force_refresh=True)

    routes = _build_handoff_routes(pack_200)
    actions = _build_owner_action_menu(routes)
    evidence_items = _build_evidence_map(pack_200, routes)
    next_batch = _build_next_batch_board()
    safety = _build_safety_summary(routes, actions, evidence_items)
    checkpoint = _build_handoff_checkpoint(routes, actions, evidence_items, next_batch, safety)
    indexes = _build_indexes(routes, actions, evidence_items, next_batch, checkpoint)

    readiness_checks = {
        "pack_200_ready": pack_200.get("status") == "ready",
        "pack_200_safe_to_save": pack_200.get("summary", {}).get("safe_to_save_packs_196_to_200") is True,
        "has_handoff_routes": len(routes) == 5,
        "all_handoff_routes_ready": all(route.get("route_status") == "receipt_chain_handoff_route_preview_ready" for route in routes),
        "has_owner_action_menu": len(actions) == 6,
        "has_allowed_preview_actions": sum(1 for action in actions if action.get("allowed_in_preview") is True) == 3,
        "has_blocked_actions": sum(1 for action in actions if action.get("blocked_in_preview") is True) == 3,
        "all_owner_actions_ready_or_blocked": all(action.get("action_status") in {"receipt_chain_handoff_owner_action_preview_ready", "receipt_chain_handoff_owner_action_preview_blocked"} for action in actions),
        "has_evidence_map": len(evidence_items) == 4,
        "all_evidence_items_ready": all(item.get("map_status") == "receipt_chain_handoff_evidence_map_item_preview_ready" for item in evidence_items),
        "has_next_batch_board": len(next_batch) == 5,
        "next_batch_save_after_205": all(card.get("save_after_pack") == 205 for card in next_batch),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_handoff_safety_summary_preview_ready",
        "handoff_checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_operational_handoff_checkpoint_preview_ready",
        "safe_to_continue_to_pack_202": checkpoint.get("safe_to_continue_to_pack_202") is True,
        "indexes_present": bool(indexes.get("handoff_routes_by_id")),
        "checkpoint_index_present": bool(indexes.get("operational_handoff_checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in routes + actions + evidence_items + next_batch),
        "all_operational_handoff_preview_only": all(item.get("operational_handoff_preview_only") is True for item in routes + actions + evidence_items + next_batch),
        "all_receipt_chain_handoff_preview_only": all(item.get("receipt_chain_handoff_preview_only") is True for item in routes + actions + evidence_items + next_batch),
        "no_real_action_executed": all(item.get("real_action_executed") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_handoff_executed": all(item.get("real_handoff_executed") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_owner_action_executed": all(item.get("real_owner_action_executed") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_filter_preference_saved": all(item.get("real_filter_preference_saved") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_navigation_state_persisted": all(item.get("real_navigation_state_persisted") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_drawer_selection_saved": all(item.get("real_drawer_selection_saved") is False for item in routes + actions + evidence_items + next_batch),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in routes + actions + evidence_items + next_batch),
        "all_action_execution_blocked": all(item.get("action_execution_allowed_now") is False for item in routes + actions + evidence_items + next_batch),
        "all_handoff_execution_blocked": all(item.get("handoff_execution_allowed_now") is False for item in routes + actions + evidence_items + next_batch),
        "all_owner_action_execution_blocked": all(item.get("owner_action_execution_allowed_now") is False for item in routes + actions + evidence_items + next_batch),
        "all_evidence_export_blocked": all(item.get("evidence_export_allowed_now") is False for item in routes + actions + evidence_items + next_batch),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in routes + actions + evidence_items + next_batch),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 201,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Operational Handoff Preview",
        "endpoint": OPERATIONAL_HANDOFF_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_200": {
            "status": pack_200.get("status"),
            "readiness_score": pack_200.get("summary", {}).get("readiness_score"),
            "safe_to_save_packs_196_to_200": pack_200.get("summary", {}).get("safe_to_save_packs_196_to_200"),
            "ready_pack_count": pack_200.get("summary", {}).get("ready_pack_count"),
            "review_pack_count": pack_200.get("summary", {}).get("review_pack_count"),
        },
        "summary": {
            "handoff_route_count": len(routes),
            "owner_action_menu_item_count": len(actions),
            "allowed_preview_action_count": safety.get("allowed_preview_action_count"),
            "blocked_action_count": safety.get("blocked_action_count"),
            "evidence_map_item_count": len(evidence_items),
            "next_batch_card_count": len(next_batch),
            "save_batch": "201-205",
            "save_after_pack": 205,
            "safe_to_continue_to_pack_202": checkpoint.get("safe_to_continue_to_pack_202"),
            "real_action_executed_count": safety.get("real_action_executed_count"),
            "real_handoff_executed_count": safety.get("real_handoff_executed_count"),
            "real_owner_action_executed_count": safety.get("real_owner_action_executed_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "persistence_write_count": safety.get("persistence_write_count"),
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain operational handoff preview ready" if readiness_score == 100 else "Receipt chain operational handoff preview needs review",
        },
        "readiness_checks": readiness_checks,
        "handoff_routes": routes,
        "owner_action_menu_items": actions,
        "handoff_evidence_map_items": evidence_items,
        "next_batch_board": next_batch,
        "handoff_safety_summary": safety,
        "operational_handoff_checkpoint": checkpoint,
        "operational_handoff_indexes": indexes,
    }


def build_receipt_chain_operational_handoff_v201_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_operational_handoff_v201_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_operational_handoff_v201_payload_cached())


def get_receipt_chain_operational_handoff_v201_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_operational_handoff_v201_payload(force_refresh=force_refresh)


def build_receipt_chain_operational_handoff_v201_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_operational_handoff_v201_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 201,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "handoff_route_count": summary.get("handoff_route_count"),
        "owner_action_menu_item_count": summary.get("owner_action_menu_item_count"),
        "allowed_preview_action_count": summary.get("allowed_preview_action_count"),
        "blocked_action_count": summary.get("blocked_action_count"),
        "evidence_map_item_count": summary.get("evidence_map_item_count"),
        "next_batch_card_count": summary.get("next_batch_card_count"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        "safe_to_continue_to_pack_202": summary.get("safe_to_continue_to_pack_202"),
        "real_action_executed_count": summary.get("real_action_executed_count"),
        "real_handoff_executed_count": summary.get("real_handoff_executed_count"),
        "real_owner_action_executed_count": summary.get("real_owner_action_executed_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "persistence_write_count": summary.get("persistence_write_count"),
        **_base_flags(),
    }


def get_receipt_chain_operational_handoff_v201_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_operational_handoff_v201_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_operational_handoff_v201_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_operational_handoff_v201_status_bridge()

    action = {
        "id": "receipt_chain_operational_handoff_v201",
        "label": "Receipt Chain Operational Handoff",
        "title": "Receipt Chain Operational Handoff Preview",
        "href": OPERATIONAL_HANDOFF_ENDPOINT,
        "endpoint": OPERATIONAL_HANDOFF_ENDPOINT,
        "description": "Preview the post-Pack-200 operational handoff and next five-pack batch path.",
        "status": bridge.get("status"),
        "pack": "Pack 201",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_operational_handoff_v201_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_operational_handoff_v201_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_operational_handoff_v201",
        "title": "Receipt Chain Operational Handoff",
        "subtitle": "Preview the post-checkpoint operational handoff and next five-pack batch route.",
        "status": payload.get("status"),
        "href": OPERATIONAL_HANDOFF_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Handoff readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "routes", "title": "Handoff routes", "value": summary.get("handoff_route_count"), "label": "Preview-only next routes"},
            {"id": "actions", "title": "Owner actions", "value": summary.get("owner_action_menu_item_count"), "label": "Owner action menu items"},
            {"id": "blocked", "title": "Blocked actions", "value": summary.get("blocked_action_count"), "label": "Blocked execution/export/access actions"},
            {"id": "next_batch", "title": "Next batch", "value": summary.get("save_batch"), "label": "Save after Pack 205"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No real execution/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "OPERATIONAL_HANDOFF_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_operational_handoff_v201_payload",
    "get_receipt_chain_operational_handoff_v201_payload",
    "build_receipt_chain_operational_handoff_v201_status_bridge",
    "get_receipt_chain_operational_handoff_v201_status_bridge",
    "build_receipt_chain_operational_handoff_v201_quick_action",
    "build_receipt_chain_operational_handoff_v201_unified_owner_section",
]
