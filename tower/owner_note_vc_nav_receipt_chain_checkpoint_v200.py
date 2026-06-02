
"""
PACK 200 - Owner Note Version Compare Navigation Receipt Chain Checkpoint.

Short module filename:
    tower.owner_note_vc_nav_receipt_chain_checkpoint_v200

This module sits on top of Packs 196-199.

Pack 200 proves the action receipt chain is ready as a coordinated checkpoint:
- Pack 196 focus action receipt proof
- Pack 197 action receipt filter/search proof
- Pack 198 action receipt filter navigation proof
- Pack 199 selected receipt detail focus proof
- combined receipt-chain readiness board
- final preview-only safety proof

Important:
- simulated-only
- checkpoint-preview-only
- receipt-chain-checkpoint-preview-only
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


PACK_ID = "PACK_200"
RECEIPT_CHAIN_CHECKPOINT_ENDPOINT = "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json"

PACK_SOURCES = [
    {
        "pack_number": 196,
        "pack_id": "PACK_196",
        "module": "tower.owner_note_vc_nav_focus_action_receipts_v196",
        "payload_fn": "build_owner_note_vc_nav_focus_action_receipts_v196_payload",
        "endpoint": "/tower/owner-note-vc-nav-focus-action-receipts-v196.json",
        "title": "Focus Action Result / Blocked Action Receipt Preview",
        "expected": {
            "action_receipt_count": 5,
            "preview_action_receipt_count": 3,
            "blocked_action_receipt_count": 2,
            "real_action_executed_count": 0,
            "raw_evidence_revealed_count": 0,
            "persistence_write_count": 0,
        },
    },
    {
        "pack_number": 197,
        "pack_id": "PACK_197",
        "module": "tower.owner_note_vc_nav_action_receipt_filter_v197",
        "payload_fn": "build_owner_note_vc_nav_action_receipt_filter_v197_payload",
        "endpoint": "/tower/owner-note-vc-nav-action-receipt-filter-v197.json",
        "title": "Action Receipt Filter / Search Facets Preview",
        "expected": {
            "action_receipt_filter_lane_count": 8,
            "action_receipt_search_facet_count": 5,
            "action_receipt_quick_filter_chip_count": 8,
            "source_action_receipt_count": 5,
            "selected_action_receipt_count": 5,
        },
    },
    {
        "pack_number": 198,
        "pack_id": "PACK_198",
        "module": "tower.owner_note_vc_nav_action_receipt_filter_nav_v198",
        "payload_fn": "build_owner_note_vc_nav_action_receipt_filter_nav_v198_payload",
        "endpoint": "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json",
        "title": "Action Receipt Filter Navigation / Receipt Selection Preview",
        "expected": {
            "action_receipt_navigation_item_count": 8,
            "action_receipt_selection_preview_count": 8,
            "action_receipt_navigation_group_count": 8,
            "search_navigation_facet_count": 5,
            "search_navigation_chip_count": 8,
            "selected_action_receipt_count": 5,
        },
    },
    {
        "pack_number": 199,
        "pack_id": "PACK_199",
        "module": "tower.owner_note_vc_nav_receipt_detail_focus_v199",
        "payload_fn": "build_owner_note_vc_nav_receipt_detail_focus_v199_payload",
        "endpoint": "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json",
        "title": "Selected Action Receipt Detail Focus Preview",
        "expected": {
            "selected_receipt_detail_focus_count": 1,
            "breadcrumb_count": 4,
            "receipt_safety_detail_card_count": 6,
            "blocked_safety_detail_card_count": 5,
            "preview_scope_detail_card_count": 1,
            "receipt_detail_focus_group_count": 3,
            "receipt_action_count": 6,
            "selected_action_receipt_count": 5,
        },
    },
]


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
        "checkpoint_preview_only": True,
        "receipt_chain_checkpoint_preview_only": True,
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
        "blocked_action_receipt_preview_only": True,
        "preview_action_receipt_preview_only": True,
        "drawer_action_preview_only": True,
        "selected_drawer_preview_only": True,
        "compare_row_focus_preview_only": True,
        "navigation_preview_only": True,
        "drawer_selection_preview_only": True,
        "version_detail_preview_only": True,
        "compare_view_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "filter_preference_save_allowed_now": False,
        "navigation_persistence_allowed_now": False,
        "drawer_selection_save_allowed_now": False,
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


def _load_payload(source: Dict[str, object]) -> Dict[str, object]:
    try:
        module = importlib.import_module(str(source["module"]))
        fn = getattr(module, str(source["payload_fn"]), None)
        if callable(fn):
            payload = fn(force_refresh=True)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": source.get("pack_id"),
            "pack_number": source.get("pack_number"),
            "status": "review",
            "endpoint": source.get("endpoint"),
            "summary": {"readiness_score": 0},
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": source.get("pack_id"),
        "pack_number": source.get("pack_number"),
        "status": "review",
        "endpoint": source.get("endpoint"),
        "summary": {"readiness_score": 0},
        **_base_flags(),
    }


def _summary_value(payload: Dict[str, object], key: str) -> Any:
    summary = payload.get("summary", {})
    if isinstance(summary, dict) and key in summary:
        return summary.get(key)
    return payload.get(key)


def _build_pack_card(source: Dict[str, object], payload: Dict[str, object], sequence: int) -> Dict[str, object]:
    expected = source.get("expected", {})
    if not isinstance(expected, dict):
        expected = {}

    metric_checks = {}
    for key, expected_value in expected.items():
        actual = _summary_value(payload, key)
        metric_checks[key] = {
            "expected": expected_value,
            "actual": actual,
            "ok": actual == expected_value if isinstance(expected_value, int) else actual == expected_value,
        }

    all_metric_checks_ok = all(item.get("ok") is True for item in metric_checks.values())
    status_ready = payload.get("status") == "ready"
    readiness_ready = _summary_value(payload, "readiness_score") == 100

    safety_flags_ok = (
        payload.get("real_action_executed") is False
        and payload.get("real_filter_preference_saved") is False
        and payload.get("real_navigation_state_persisted") is False
        and payload.get("real_drawer_selection_saved") is False
        and payload.get("real_raw_evidence_revealed") is False
        and payload.get("simulated_only") is True
        and payload.get("cached_non_recursive") is True
    )

    card = {
        "receipt_chain_pack_card_id": f"version_compare_navigation_receipt_chain_pack_{_stable_hash((PACK_ID, source.get('pack_number')), 18)}",
        "pack_number": source.get("pack_number"),
        "pack_id": source.get("pack_id"),
        "title": source.get("title"),
        "endpoint": source.get("endpoint"),
        "sequence": int(sequence),
        "status": payload.get("status"),
        "readiness_score": _summary_value(payload, "readiness_score"),
        "metric_checks": metric_checks,
        "all_metric_checks_ok": all_metric_checks_ok,
        "status_ready": status_ready,
        "readiness_ready": readiness_ready,
        "safety_flags_ok": safety_flags_ok,
        "pack_checkpoint_ok": bool(status_ready and readiness_ready and all_metric_checks_ok and safety_flags_ok),
        "card_status": "version_compare_navigation_receipt_chain_pack_card_ready" if status_ready and readiness_ready and all_metric_checks_ok and safety_flags_ok else "version_compare_navigation_receipt_chain_pack_card_review",
        "card_result_type": "owner_note_version_compare_navigation_receipt_chain_pack_card_preview",
        "safe_preview_only": True,
    }
    card.update(_base_flags())
    return card


def _build_chain_safety_summary(cards: List[Dict[str, object]]) -> Dict[str, object]:
    summary = {
        "receipt_chain_safety_summary_id": f"version_compare_navigation_receipt_chain_safety_{_stable_hash((PACK_ID, [card.get('pack_number') for card in cards]), 18)}",
        "pack_card_count": len(cards),
        "ready_pack_count": sum(1 for card in cards if card.get("pack_checkpoint_ok") is True),
        "review_pack_count": sum(1 for card in cards if card.get("pack_checkpoint_ok") is not True),
        "real_action_executed_count": 0,
        "raw_evidence_revealed_count": 0,
        "persistence_write_count": 0,
        "all_packs_ready": all(card.get("pack_checkpoint_ok") is True for card in cards),
        "all_metrics_ready": all(card.get("all_metric_checks_ok") is True for card in cards),
        "all_safety_flags_ok": all(card.get("safety_flags_ok") is True for card in cards),
        "summary_status": "version_compare_navigation_receipt_chain_safety_summary_ready" if all(card.get("pack_checkpoint_ok") is True for card in cards) else "version_compare_navigation_receipt_chain_safety_summary_review",
        "summary_result_type": "owner_note_version_compare_navigation_receipt_chain_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint_groups(cards: List[Dict[str, object]]) -> List[Dict[str, object]]:
    ready = [card for card in cards if card.get("pack_checkpoint_ok") is True]
    review = [card for card in cards if card.get("pack_checkpoint_ok") is not True]

    group_defs = [
        ("ready_receipt_chain_packs", "Ready receipt-chain packs", ready),
        ("review_receipt_chain_packs", "Review receipt-chain packs", review),
        ("all_receipt_chain_packs", "All receipt-chain packs", cards),
    ]

    groups = []
    for sequence, (key, label, items) in enumerate(group_defs, start=1):
        group = {
            "receipt_chain_checkpoint_group_id": f"version_compare_navigation_receipt_chain_group_{_stable_hash((PACK_ID, key), 18)}",
            "receipt_chain_checkpoint_group_key": key,
            "label": label,
            "sequence": int(sequence),
            "pack_card_count": len(items),
            "pack_numbers": [item.get("pack_number") for item in items],
            "pack_card_ids": [item.get("receipt_chain_pack_card_id") for item in items],
            "group_status": "version_compare_navigation_receipt_chain_checkpoint_group_ready",
            "group_result_type": "owner_note_version_compare_navigation_receipt_chain_checkpoint_group_preview",
            "safe_preview_only": True,
        }
        group.update(_base_flags())
        groups.append(group)

    return groups


def _build_final_checkpoint(cards: List[Dict[str, object]], safety_summary: Dict[str, object], groups: List[Dict[str, object]]) -> Dict[str, object]:
    checkpoint_ok = (
        len(cards) == 4
        and safety_summary.get("all_packs_ready") is True
        and safety_summary.get("all_metrics_ready") is True
        and safety_summary.get("all_safety_flags_ok") is True
        and safety_summary.get("real_action_executed_count") == 0
        and safety_summary.get("raw_evidence_revealed_count") == 0
        and safety_summary.get("persistence_write_count") == 0
    )

    checkpoint = {
        "receipt_chain_checkpoint_id": f"version_compare_navigation_receipt_chain_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "version_compare_navigation_receipt_chain_checkpoint_ready" if checkpoint_ok else "version_compare_navigation_receipt_chain_checkpoint_review",
        "checkpoint_result_type": "owner_note_version_compare_navigation_receipt_chain_checkpoint_preview",
        "pack_card_count": len(cards),
        "checkpoint_group_count": len(groups),
        "ready_pack_numbers": [card.get("pack_number") for card in cards if card.get("pack_checkpoint_ok") is True],
        "review_pack_numbers": [card.get("pack_number") for card in cards if card.get("pack_checkpoint_ok") is not True],
        "safety_summary_id": safety_summary.get("receipt_chain_safety_summary_id"),
        "safe_to_save_packs_196_to_200": checkpoint_ok,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(cards: List[Dict[str, object]], groups: List[Dict[str, object]], checkpoint: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "pack_cards_by_id": {},
        "pack_cards_by_number": {},
        "pack_cards_by_status": {},
        "checkpoint_groups_by_id": {},
        "checkpoint_groups_by_key": {},
        "final_checkpoint_by_id": {},
    }

    for card in cards:
        indexes["pack_cards_by_id"][card.get("receipt_chain_pack_card_id")] = card
        indexes["pack_cards_by_number"][str(card.get("pack_number"))] = card
        indexes["pack_cards_by_status"].setdefault(card.get("card_status"), []).append(card)

    for group in groups:
        indexes["checkpoint_groups_by_id"][group.get("receipt_chain_checkpoint_group_id")] = group
        indexes["checkpoint_groups_by_key"][group.get("receipt_chain_checkpoint_group_key")] = group

    indexes["final_checkpoint_by_id"][checkpoint.get("receipt_chain_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload_cached() -> Dict[str, object]:
    payloads = [_load_payload(source) for source in PACK_SOURCES]
    cards = [_build_pack_card(source, payload, idx) for idx, (source, payload) in enumerate(zip(PACK_SOURCES, payloads), start=1)]
    safety_summary = _build_chain_safety_summary(cards)
    groups = _build_checkpoint_groups(cards)
    final_checkpoint = _build_final_checkpoint(cards, safety_summary, groups)
    indexes = _build_indexes(cards, groups, final_checkpoint)

    readiness_checks = {
        "has_four_source_packs": len(cards) == 4,
        "pack_196_ready": any(card.get("pack_number") == 196 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_197_ready": any(card.get("pack_number") == 197 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_198_ready": any(card.get("pack_number") == 198 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_199_ready": any(card.get("pack_number") == 199 and card.get("pack_checkpoint_ok") is True for card in cards),
        "all_pack_cards_ready": all(card.get("pack_checkpoint_ok") is True for card in cards),
        "all_pack_metrics_ready": all(card.get("all_metric_checks_ok") is True for card in cards),
        "all_pack_safety_flags_ok": all(card.get("safety_flags_ok") is True for card in cards),
        "safety_summary_ready": safety_summary.get("summary_status") == "version_compare_navigation_receipt_chain_safety_summary_ready",
        "has_checkpoint_groups": len(groups) == 3,
        "all_checkpoint_groups_ready": all(group.get("group_status") == "version_compare_navigation_receipt_chain_checkpoint_group_ready" for group in groups),
        "final_checkpoint_ready": final_checkpoint.get("checkpoint_status") == "version_compare_navigation_receipt_chain_checkpoint_ready",
        "safe_to_save_packs_196_to_200": final_checkpoint.get("safe_to_save_packs_196_to_200") is True,
        "indexes_present": bool(indexes.get("pack_cards_by_id")),
        "checkpoint_indexes_present": bool(indexes.get("final_checkpoint_by_id")),
        "all_simulated_only": all(card.get("simulated_only") is True for card in cards),
        "all_checkpoint_preview_only": all(card.get("checkpoint_preview_only") is True for card in cards),
        "all_receipt_chain_checkpoint_preview_only": all(card.get("receipt_chain_checkpoint_preview_only") is True for card in cards),
        "no_real_action_executed": all(card.get("real_action_executed") is False for card in cards),
        "no_real_filter_preference_saved": all(card.get("real_filter_preference_saved") is False for card in cards),
        "no_real_navigation_state_persisted": all(card.get("real_navigation_state_persisted") is False for card in cards),
        "no_real_drawer_selection_saved": all(card.get("real_drawer_selection_saved") is False for card in cards),
        "no_real_raw_evidence_revealed": all(card.get("real_raw_evidence_revealed") is False for card in cards),
        "all_action_execution_blocked": all(card.get("action_execution_allowed_now") is False for card in cards),
        "all_filter_preference_saves_blocked": all(card.get("filter_preference_save_allowed_now") is False for card in cards),
        "all_navigation_persistence_blocked": all(card.get("navigation_persistence_allowed_now") is False for card in cards),
        "all_drawer_selection_saves_blocked": all(card.get("drawer_selection_save_allowed_now") is False for card in cards),
        "all_raw_evidence_reveal_blocked": all(card.get("raw_evidence_reveal_allowed") is False for card in cards),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 200,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Owner Note Version Compare Navigation Receipt Chain Checkpoint",
        "endpoint": RECEIPT_CHAIN_CHECKPOINT_ENDPOINT,
        "source_endpoints": [source.get("endpoint") for source in PACK_SOURCES],
        "generated_at": _utc_now(),
        **_base_flags(),
        "summary": {
            "source_pack_count": len(PACK_SOURCES),
            "receipt_chain_pack_card_count": len(cards),
            "ready_pack_count": safety_summary.get("ready_pack_count"),
            "review_pack_count": safety_summary.get("review_pack_count"),
            "checkpoint_group_count": len(groups),
            "final_checkpoint_count": 1 if final_checkpoint else 0,
            "safe_to_save_packs_196_to_200": final_checkpoint.get("safe_to_save_packs_196_to_200"),
            "real_action_executed_count": safety_summary.get("real_action_executed_count"),
            "raw_evidence_revealed_count": safety_summary.get("raw_evidence_revealed_count"),
            "persistence_write_count": safety_summary.get("persistence_write_count"),
            "ready_pack_numbers": final_checkpoint.get("ready_pack_numbers"),
            "review_pack_numbers": final_checkpoint.get("review_pack_numbers"),
            "readiness_score": readiness_score,
            "readiness_label": "Owner note receipt chain checkpoint ready" if readiness_score == 100 else "Owner note receipt chain checkpoint needs review",
        },
        "readiness_checks": readiness_checks,
        "receipt_chain_pack_cards": cards,
        "receipt_chain_safety_summary": safety_summary,
        "receipt_chain_checkpoint_groups": groups,
        "final_receipt_chain_checkpoint": final_checkpoint,
        "receipt_chain_checkpoint_indexes": indexes,
    }


def build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload_cached.cache_clear()
    return copy.deepcopy(build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload_cached())


def get_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh=force_refresh)


def build_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 200,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoints": payload.get("source_endpoints"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "source_pack_count": summary.get("source_pack_count"),
        "receipt_chain_pack_card_count": summary.get("receipt_chain_pack_card_count"),
        "ready_pack_count": summary.get("ready_pack_count"),
        "review_pack_count": summary.get("review_pack_count"),
        "checkpoint_group_count": summary.get("checkpoint_group_count"),
        "final_checkpoint_count": summary.get("final_checkpoint_count"),
        "safe_to_save_packs_196_to_200": summary.get("safe_to_save_packs_196_to_200"),
        "real_action_executed_count": summary.get("real_action_executed_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "persistence_write_count": summary.get("persistence_write_count"),
        "ready_pack_numbers": summary.get("ready_pack_numbers"),
        "review_pack_numbers": summary.get("review_pack_numbers"),
        **_base_flags(),
    }


def get_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge(force_refresh=force_refresh)


def build_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action() -> Dict[str, object]:
    bridge = build_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge()

    action = {
        "id": "owner_note_vc_nav_receipt_chain_checkpoint_v200",
        "label": "Owner Note Receipt Chain Checkpoint",
        "title": "Owner Note Version Compare Navigation Receipt Chain Checkpoint",
        "href": RECEIPT_CHAIN_CHECKPOINT_ENDPOINT,
        "endpoint": RECEIPT_CHAIN_CHECKPOINT_ENDPOINT,
        "description": "Final checkpoint proving Packs 196–199 receipt chain readiness and preview-only safety.",
        "status": bridge.get("status"),
        "pack": "Pack 200",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_owner_section() -> Dict[str, object]:
    payload = build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "owner_note_vc_nav_receipt_chain_checkpoint_v200",
        "title": "Owner Note Receipt Chain Checkpoint",
        "subtitle": "Final readiness checkpoint for Packs 196–199 receipt-chain preview layers.",
        "status": payload.get("status"),
        "href": RECEIPT_CHAIN_CHECKPOINT_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Checkpoint readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "source_packs", "title": "Source packs", "value": summary.get("source_pack_count"), "label": "Packs 196–199"},
            {"id": "ready_packs", "title": "Ready packs", "value": summary.get("ready_pack_count"), "label": "Receipt-chain packs ready"},
            {"id": "review_packs", "title": "Review packs", "value": summary.get("review_pack_count"), "label": "Receipt-chain packs needing review"},
            {"id": "safe_save", "title": "Safe to save", "value": summary.get("safe_to_save_packs_196_to_200"), "label": "Combined save gate"},
            {"id": "persistence", "title": "Persistence", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("all_raw_evidence_reveal_blocked") else "Review", "label": "No real execution/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "RECEIPT_CHAIN_CHECKPOINT_ENDPOINT",
    "PACK_SOURCES",
    "build_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload",
    "get_owner_note_vc_nav_receipt_chain_checkpoint_v200_payload",
    "build_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge",
    "get_owner_note_vc_nav_receipt_chain_checkpoint_v200_status_bridge",
    "build_owner_note_vc_nav_receipt_chain_checkpoint_v200_quick_action",
    "build_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_owner_section",
]
