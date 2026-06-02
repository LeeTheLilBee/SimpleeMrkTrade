
"""
PACK 205 - Receipt Chain Operational Batch Checkpoint.

Short module filename:
    tower.receipt_chain_operational_batch_checkpoint_v205

This module sits on top of Packs 201-204.

Pack 205 closes the 201-205 batch:
- Pack 201 operational handoff proof
- Pack 202 saved views/filter presets proof
- Pack 203 evidence packet/export-block proof
- Pack 204 recheck/expiration/renewal hook proof
- final save gate for Packs 201-205

Important:
- simulated-only
- batch-checkpoint-preview-only
- no real action executed
- no real handoff executed
- no real evidence export
- no real recheck/renewal/expiration
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


PACK_ID = "PACK_205"
BATCH_CHECKPOINT_ENDPOINT = "/tower/receipt-chain-operational-batch-checkpoint-v205.json"

PACK_SOURCES = [
    {
        "pack_number": 201,
        "pack_id": "PACK_201",
        "module": "tower.receipt_chain_operational_handoff_v201",
        "payload_fn": "build_receipt_chain_operational_handoff_v201_payload",
        "endpoint": "/tower/receipt-chain-operational-handoff-v201.json",
        "title": "Receipt Chain Operational Handoff Preview",
        "expected": {
            "handoff_route_count": 5,
            "owner_action_menu_item_count": 6,
            "allowed_preview_action_count": 3,
            "blocked_action_count": 3,
            "evidence_map_item_count": 4,
            "next_batch_card_count": 5,
            "safe_to_continue_to_pack_202": True,
        },
    },
    {
        "pack_number": 202,
        "pack_id": "PACK_202",
        "module": "tower.receipt_chain_handoff_saved_views_v202",
        "payload_fn": "build_receipt_chain_handoff_saved_views_v202_payload",
        "endpoint": "/tower/receipt-chain-handoff-saved-views-v202.json",
        "title": "Receipt Chain Handoff Saved Views / Filter Presets Preview",
        "expected": {
            "handoff_saved_view_preview_count": 6,
            "handoff_filter_preset_preview_count": 8,
            "selected_handoff_saved_view_preview_count": 1,
            "selected_saved_view_id": "default_full_handoff",
            "selected_filter_preset_id": "all_handoff_items",
            "selected_handoff_route_count": 5,
            "selected_owner_action_count": 6,
            "selected_evidence_map_item_count": 4,
            "selected_next_batch_card_count": 5,
        },
    },
    {
        "pack_number": 203,
        "pack_id": "PACK_203",
        "module": "tower.receipt_chain_evidence_packet_v203",
        "payload_fn": "build_receipt_chain_evidence_packet_v203_payload",
        "endpoint": "/tower/receipt-chain-evidence-packet-v203.json",
        "title": "Receipt Chain Evidence Bundle Packet Preview",
        "expected": {
            "packet_section_count": 6,
            "evidence_bundle_packet_count": 3,
            "export_request_preview_count": 3,
            "owner_review_checklist_item_count": 5,
            "raw_item_count": 0,
            "real_export_request_created_count": 0,
            "real_evidence_exported_count": 0,
            "real_packet_written_count": 0,
            "real_packet_sealed_count": 0,
            "raw_evidence_revealed_count": 0,
        },
    },
    {
        "pack_number": 204,
        "pack_id": "PACK_204",
        "module": "tower.receipt_chain_recheck_expiration_handoff_v204",
        "payload_fn": "build_receipt_chain_recheck_expiration_handoff_v204_payload",
        "endpoint": "/tower/receipt-chain-recheck-expiration-handoff-v204.json",
        "title": "Receipt Chain Recheck / Expiration Handoff Preview",
        "expected": {
            "freshness_lane_count": 5,
            "recheck_hook_count": 4,
            "expiration_trigger_count": 4,
            "renewal_trigger_count": 3,
            "owner_followup_queue_item_count": 5,
            "safe_to_continue_to_pack_205": True,
            "real_recheck_executed_count": 0,
            "real_renewal_executed_count": 0,
            "real_expiration_enforced_count": 0,
            "real_owner_followup_executed_count": 0,
            "real_evidence_exported_count": 0,
            "raw_evidence_revealed_count": 0,
        },
    },
]


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "batch_checkpoint_preview_only": True,
        "operational_batch_checkpoint_preview_only": True,
        "operational_handoff_preview_only": True,
        "receipt_chain_handoff_preview_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "evidence_packet_preview_only": True,
        "evidence_bundle_preview_only": True,
        "packet_section_preview_only": True,
        "export_request_preview_only": True,
        "export_blocked": True,
        "raw_evidence_redacted": True,
        "recheck_expiration_handoff_preview_only": True,
        "recheck_hook_preview_only": True,
        "expiration_trigger_preview_only": True,
        "renewal_trigger_preview_only": True,
        "freshness_lane_preview_only": True,
        "owner_followup_queue_preview_only": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "recheck_execution_allowed_now": False,
        "renewal_execution_allowed_now": False,
        "expiration_enforcement_allowed_now": False,
        "owner_followup_execution_allowed_now": False,
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
            "ok": actual == expected_value,
        }

    status_ready = payload.get("status") == "ready"
    readiness_ready = _summary_value(payload, "readiness_score") == 100
    all_metric_checks_ok = all(item.get("ok") is True for item in metric_checks.values())

    safety_flags_ok = (
        payload.get("simulated_only") is True
        and payload.get("cached_non_recursive") is True
        and payload.get("real_action_executed") is False
        and payload.get("real_handoff_executed") is False
        and payload.get("real_owner_action_executed") is False
        and payload.get("real_evidence_exported") is False
        and payload.get("real_raw_evidence_revealed") is False
    )

    card = {
        "operational_batch_pack_card_id": f"receipt_chain_operational_batch_pack_{_stable_hash((PACK_ID, source.get('pack_number')), 18)}",
        "pack_number": source.get("pack_number"),
        "pack_id": source.get("pack_id"),
        "title": source.get("title"),
        "endpoint": source.get("endpoint"),
        "sequence": int(sequence),
        "status": payload.get("status"),
        "readiness_score": _summary_value(payload, "readiness_score"),
        "metric_checks": metric_checks,
        "status_ready": status_ready,
        "readiness_ready": readiness_ready,
        "all_metric_checks_ok": all_metric_checks_ok,
        "safety_flags_ok": safety_flags_ok,
        "pack_checkpoint_ok": bool(status_ready and readiness_ready and all_metric_checks_ok and safety_flags_ok),
        "card_status": "receipt_chain_operational_batch_pack_card_ready" if status_ready and readiness_ready and all_metric_checks_ok and safety_flags_ok else "receipt_chain_operational_batch_pack_card_review",
        "card_result_type": "tower_receipt_chain_operational_batch_pack_card_preview",
        "safe_preview_only": True,
    }
    card.update(_base_flags())
    return card


def _build_batch_groups(cards: List[Dict[str, object]]) -> List[Dict[str, object]]:
    ready = [card for card in cards if card.get("pack_checkpoint_ok") is True]
    review = [card for card in cards if card.get("pack_checkpoint_ok") is not True]

    group_defs = [
        ("ready_operational_batch_packs", "Ready operational batch packs", ready),
        ("review_operational_batch_packs", "Review operational batch packs", review),
        ("all_operational_batch_packs", "All operational batch packs", cards),
    ]

    groups = []
    for sequence, (key, label, items) in enumerate(group_defs, start=1):
        group = {
            "operational_batch_group_id": f"receipt_chain_operational_batch_group_{_stable_hash((PACK_ID, key), 18)}",
            "operational_batch_group_key": key,
            "label": label,
            "sequence": sequence,
            "pack_card_count": len(items),
            "pack_numbers": [item.get("pack_number") for item in items],
            "pack_card_ids": [item.get("operational_batch_pack_card_id") for item in items],
            "group_status": "receipt_chain_operational_batch_group_preview_ready",
            "group_result_type": "tower_receipt_chain_operational_batch_group_preview",
            "safe_preview_only": True,
        }
        group.update(_base_flags())
        groups.append(group)

    return groups


def _build_safety_summary(cards: List[Dict[str, object]]) -> Dict[str, object]:
    summary = {
        "operational_batch_safety_summary_id": f"receipt_chain_operational_batch_safety_{_stable_hash((PACK_ID, [card.get('pack_number') for card in cards]), 18)}",
        "source_pack_count": len(cards),
        "ready_pack_count": sum(1 for card in cards if card.get("pack_checkpoint_ok") is True),
        "review_pack_count": sum(1 for card in cards if card.get("pack_checkpoint_ok") is not True),
        "real_action_executed_count": 0,
        "real_handoff_executed_count": 0,
        "real_owner_action_executed_count": 0,
        "real_evidence_exported_count": 0,
        "real_export_request_created_count": 0,
        "real_packet_written_count": 0,
        "real_packet_sealed_count": 0,
        "real_recheck_executed_count": 0,
        "real_renewal_executed_count": 0,
        "real_expiration_enforced_count": 0,
        "real_owner_followup_executed_count": 0,
        "real_saved_view_written_count": 0,
        "real_user_preference_written_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_packs_ready": all(card.get("pack_checkpoint_ok") is True for card in cards),
        "all_metrics_ready": all(card.get("all_metric_checks_ok") is True for card in cards),
        "all_safety_flags_ok": all(card.get("safety_flags_ok") is True for card in cards),
        "summary_status": "receipt_chain_operational_batch_safety_summary_preview_ready" if all(card.get("pack_checkpoint_ok") is True for card in cards) else "receipt_chain_operational_batch_safety_summary_preview_review",
        "summary_result_type": "tower_receipt_chain_operational_batch_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_final_checkpoint(cards: List[Dict[str, object]], groups: List[Dict[str, object]], safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        len(cards) == 4
        and len(groups) == 3
        and safety.get("ready_pack_count") == 4
        and safety.get("review_pack_count") == 0
        and safety.get("all_packs_ready") is True
        and safety.get("all_metrics_ready") is True
        and safety.get("all_safety_flags_ok") is True
        and safety.get("real_action_executed_count") == 0
        and safety.get("real_handoff_executed_count") == 0
        and safety.get("real_owner_action_executed_count") == 0
        and safety.get("real_evidence_exported_count") == 0
        and safety.get("real_export_request_created_count") == 0
        and safety.get("real_packet_written_count") == 0
        and safety.get("real_packet_sealed_count") == 0
        and safety.get("real_recheck_executed_count") == 0
        and safety.get("real_renewal_executed_count") == 0
        and safety.get("real_expiration_enforced_count") == 0
        and safety.get("real_owner_followup_executed_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "operational_batch_checkpoint_id": f"receipt_chain_operational_batch_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_operational_batch_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_operational_batch_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_operational_batch_checkpoint_preview",
        "ready_pack_numbers": [card.get("pack_number") for card in cards if card.get("pack_checkpoint_ok") is True],
        "review_pack_numbers": [card.get("pack_number") for card in cards if card.get("pack_checkpoint_ok") is not True],
        "safe_to_save_packs_201_to_205": checkpoint_ok,
        "safe_to_continue_to_pack_206": checkpoint_ok,
        "save_batch": "201-205",
        "save_after_pack": 205,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(cards: List[Dict[str, object]], groups: List[Dict[str, object]], checkpoint: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "pack_cards_by_id": {},
        "pack_cards_by_number": {},
        "pack_cards_by_status": {},
        "batch_groups_by_id": {},
        "batch_groups_by_key": {},
        "final_checkpoint_by_id": {},
    }

    for card in cards:
        indexes["pack_cards_by_id"][card.get("operational_batch_pack_card_id")] = card
        indexes["pack_cards_by_number"][str(card.get("pack_number"))] = card
        indexes["pack_cards_by_status"].setdefault(card.get("card_status"), []).append(card)

    for group in groups:
        indexes["batch_groups_by_id"][group.get("operational_batch_group_id")] = group
        indexes["batch_groups_by_key"][group.get("operational_batch_group_key")] = group

    indexes["final_checkpoint_by_id"][checkpoint.get("operational_batch_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_operational_batch_checkpoint_v205_payload_cached() -> Dict[str, object]:
    payloads = [_load_payload(source) for source in PACK_SOURCES]
    cards = [_build_pack_card(source, payload, idx) for idx, (source, payload) in enumerate(zip(PACK_SOURCES, payloads), start=1)]
    groups = _build_batch_groups(cards)
    safety = _build_safety_summary(cards)
    checkpoint = _build_final_checkpoint(cards, groups, safety)
    indexes = _build_indexes(cards, groups, checkpoint)

    readiness_checks = {
        "has_four_source_packs": len(cards) == 4,
        "pack_201_ready": any(card.get("pack_number") == 201 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_202_ready": any(card.get("pack_number") == 202 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_203_ready": any(card.get("pack_number") == 203 and card.get("pack_checkpoint_ok") is True for card in cards),
        "pack_204_ready": any(card.get("pack_number") == 204 and card.get("pack_checkpoint_ok") is True for card in cards),
        "all_pack_cards_ready": all(card.get("pack_checkpoint_ok") is True for card in cards),
        "all_pack_metrics_ready": all(card.get("all_metric_checks_ok") is True for card in cards),
        "all_pack_safety_flags_ok": all(card.get("safety_flags_ok") is True for card in cards),
        "has_batch_groups": len(groups) == 3,
        "all_batch_groups_ready": all(group.get("group_status") == "receipt_chain_operational_batch_group_preview_ready" for group in groups),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_operational_batch_safety_summary_preview_ready",
        "final_checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_operational_batch_checkpoint_preview_ready",
        "safe_to_save_packs_201_to_205": checkpoint.get("safe_to_save_packs_201_to_205") is True,
        "safe_to_continue_to_pack_206": checkpoint.get("safe_to_continue_to_pack_206") is True,
        "indexes_present": bool(indexes.get("pack_cards_by_id")),
        "checkpoint_index_present": bool(indexes.get("final_checkpoint_by_id")),
        "all_simulated_only": all(card.get("simulated_only") is True for card in cards),
        "all_batch_checkpoint_preview_only": all(card.get("batch_checkpoint_preview_only") is True for card in cards),
        "no_real_action_executed": all(card.get("real_action_executed") is False for card in cards),
        "no_real_handoff_executed": all(card.get("real_handoff_executed") is False for card in cards),
        "no_real_owner_action_executed": all(card.get("real_owner_action_executed") is False for card in cards),
        "no_real_evidence_exported": all(card.get("real_evidence_exported") is False for card in cards),
        "no_real_export_request_created": all(card.get("real_export_request_created") is False for card in cards),
        "no_real_packet_written": all(card.get("real_packet_written") is False for card in cards),
        "no_real_packet_sealed": all(card.get("real_packet_sealed") is False for card in cards),
        "no_real_recheck_executed": all(card.get("real_recheck_executed") is False for card in cards),
        "no_real_renewal_executed": all(card.get("real_renewal_executed") is False for card in cards),
        "no_real_expiration_enforced": all(card.get("real_expiration_enforced") is False for card in cards),
        "no_real_raw_evidence_revealed": all(card.get("real_raw_evidence_revealed") is False for card in cards),
        "all_action_execution_blocked": all(card.get("action_execution_allowed_now") is False for card in cards),
        "all_handoff_execution_blocked": all(card.get("handoff_execution_allowed_now") is False for card in cards),
        "all_evidence_export_blocked": all(card.get("evidence_export_allowed_now") is False for card in cards),
        "all_recheck_execution_blocked": all(card.get("recheck_execution_allowed_now") is False for card in cards),
        "all_renewal_execution_blocked": all(card.get("renewal_execution_allowed_now") is False for card in cards),
        "all_expiration_enforcement_blocked": all(card.get("expiration_enforcement_allowed_now") is False for card in cards),
        "all_raw_evidence_reveal_blocked": all(card.get("raw_evidence_reveal_allowed") is False for card in cards),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 205,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Operational Batch Checkpoint",
        "endpoint": BATCH_CHECKPOINT_ENDPOINT,
        "source_endpoints": [source.get("endpoint") for source in PACK_SOURCES],
        "generated_at": _utc_now(),
        **_base_flags(),
        "summary": {
            "source_pack_count": len(PACK_SOURCES),
            "operational_batch_pack_card_count": len(cards),
            "ready_pack_count": safety.get("ready_pack_count"),
            "review_pack_count": safety.get("review_pack_count"),
            "batch_group_count": len(groups),
            "final_checkpoint_count": 1 if checkpoint else 0,
            "safe_to_save_packs_201_to_205": checkpoint.get("safe_to_save_packs_201_to_205"),
            "safe_to_continue_to_pack_206": checkpoint.get("safe_to_continue_to_pack_206"),
            "ready_pack_numbers": checkpoint.get("ready_pack_numbers"),
            "review_pack_numbers": checkpoint.get("review_pack_numbers"),
            "real_action_executed_count": safety.get("real_action_executed_count"),
            "real_handoff_executed_count": safety.get("real_handoff_executed_count"),
            "real_owner_action_executed_count": safety.get("real_owner_action_executed_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "real_export_request_created_count": safety.get("real_export_request_created_count"),
            "real_packet_written_count": safety.get("real_packet_written_count"),
            "real_packet_sealed_count": safety.get("real_packet_sealed_count"),
            "real_recheck_executed_count": safety.get("real_recheck_executed_count"),
            "real_renewal_executed_count": safety.get("real_renewal_executed_count"),
            "real_expiration_enforced_count": safety.get("real_expiration_enforced_count"),
            "real_owner_followup_executed_count": safety.get("real_owner_followup_executed_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "save_batch": "201-205",
            "save_after_pack": 205,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain operational batch checkpoint ready" if readiness_score == 100 else "Receipt chain operational batch checkpoint needs review",
        },
        "readiness_checks": readiness_checks,
        "operational_batch_pack_cards": cards,
        "operational_batch_groups": groups,
        "operational_batch_safety_summary": safety,
        "final_operational_batch_checkpoint": checkpoint,
        "operational_batch_indexes": indexes,
    }


def build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_operational_batch_checkpoint_v205_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_operational_batch_checkpoint_v205_payload_cached())


def get_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh=force_refresh)


def build_receipt_chain_operational_batch_checkpoint_v205_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_operational_batch_checkpoint_v205_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})
    return {
        "pack_id": PACK_ID,
        "pack_number": 205,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoints": payload.get("source_endpoints"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "source_pack_count": summary.get("source_pack_count"),
        "operational_batch_pack_card_count": summary.get("operational_batch_pack_card_count"),
        "ready_pack_count": summary.get("ready_pack_count"),
        "review_pack_count": summary.get("review_pack_count"),
        "batch_group_count": summary.get("batch_group_count"),
        "final_checkpoint_count": summary.get("final_checkpoint_count"),
        "safe_to_save_packs_201_to_205": summary.get("safe_to_save_packs_201_to_205"),
        "safe_to_continue_to_pack_206": summary.get("safe_to_continue_to_pack_206"),
        "ready_pack_numbers": summary.get("ready_pack_numbers"),
        "review_pack_numbers": summary.get("review_pack_numbers"),
        "real_action_executed_count": summary.get("real_action_executed_count"),
        "real_handoff_executed_count": summary.get("real_handoff_executed_count"),
        "real_owner_action_executed_count": summary.get("real_owner_action_executed_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "real_export_request_created_count": summary.get("real_export_request_created_count"),
        "real_packet_written_count": summary.get("real_packet_written_count"),
        "real_packet_sealed_count": summary.get("real_packet_sealed_count"),
        "real_recheck_executed_count": summary.get("real_recheck_executed_count"),
        "real_renewal_executed_count": summary.get("real_renewal_executed_count"),
        "real_expiration_enforced_count": summary.get("real_expiration_enforced_count"),
        "real_owner_followup_executed_count": summary.get("real_owner_followup_executed_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_operational_batch_checkpoint_v205_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_operational_batch_checkpoint_v205_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_operational_batch_checkpoint_v205_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_operational_batch_checkpoint_v205_status_bridge()
    action = {
        "id": "receipt_chain_operational_batch_checkpoint_v205",
        "label": "Receipt Chain Batch Checkpoint",
        "title": "Receipt Chain Operational Batch Checkpoint",
        "href": BATCH_CHECKPOINT_ENDPOINT,
        "endpoint": BATCH_CHECKPOINT_ENDPOINT,
        "description": "Final checkpoint proving Packs 201-205 operational handoff/evidence/recheck previews are safe together.",
        "status": bridge.get("status"),
        "pack": "Pack 205",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_operational_batch_checkpoint_v205_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_operational_batch_checkpoint_v205_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})
    section = {
        "section_id": "receipt_chain_operational_batch_checkpoint_v205",
        "title": "Receipt Chain Batch Checkpoint",
        "subtitle": "Final readiness checkpoint for Packs 201-205.",
        "status": payload.get("status"),
        "href": BATCH_CHECKPOINT_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Batch readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "source_packs", "title": "Source packs", "value": summary.get("source_pack_count"), "label": "Packs 201-204"},
            {"id": "ready", "title": "Ready packs", "value": summary.get("ready_pack_count"), "label": "Operational batch packs ready"},
            {"id": "safe_save", "title": "Safe save", "value": summary.get("safe_to_save_packs_201_to_205"), "label": "Combined save gate"},
            {"id": "next", "title": "Continue", "value": summary.get("safe_to_continue_to_pack_206"), "label": "Safe to continue to Pack 206"},
            {"id": "safety", "title": "Execution", "value": "Blocked" if checks.get("no_real_action_executed") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No real execution/raw reveal"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "BATCH_CHECKPOINT_ENDPOINT",
    "PACK_SOURCES",
    "build_receipt_chain_operational_batch_checkpoint_v205_payload",
    "get_receipt_chain_operational_batch_checkpoint_v205_payload",
    "build_receipt_chain_operational_batch_checkpoint_v205_status_bridge",
    "get_receipt_chain_operational_batch_checkpoint_v205_status_bridge",
    "build_receipt_chain_operational_batch_checkpoint_v205_quick_action",
    "build_receipt_chain_operational_batch_checkpoint_v205_unified_owner_section",
]
