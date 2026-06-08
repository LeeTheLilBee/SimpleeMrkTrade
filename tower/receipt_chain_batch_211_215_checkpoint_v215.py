
"""
PACK 215 - Receipt Chain Batch 211-215 Checkpoint Preview.

Short module filename:
    tower.receipt_chain_batch_211_215_checkpoint_v215

This module sits on top of Pack 214.

Pack 215 closes the 211-215 batch:
- source pack readiness cards for Packs 211-214
- recovered dependency awareness for Packs 208-210
- evidence/detail safety rollup
- batch closure checkpoint
- save/push readiness preview
- next batch 216-220 handoff preview
- no real save/push/export/raw reveal

Important:
- simulated-only
- batch-checkpoint-preview-only
- no real persistence
- no real exports
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
from typing import Any, Dict, List, Tuple


PACK_ID = "PACK_215"
BATCH_CHECKPOINT_ENDPOINT = "/tower/receipt-chain-batch-211-215-checkpoint-v215.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-evidence-detail-drawer-v214.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "batch_checkpoint_preview_only": True,
        "source_pack_readiness_preview_only": True,
        "recovered_dependency_awareness_preview_only": True,
        "evidence_detail_rollup_preview_only": True,
        "batch_safety_rollup_preview_only": True,
        "save_push_readiness_preview_only": True,
        "next_batch_handoff_preview_only": True,
        "evidence_detail_drawer_preview_only": True,
        "owner_review_drawer_preview_only": True,
        "checkpoint_filter_search_preview_only": True,
        "saved_checkpoint_lookup_preview_only": True,
        "raw_evidence_redacted": True,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "save_allowed_now": False,
        "push_allowed_now": False,
        "commit_allowed_now": False,
        "git_write_allowed_now": False,
        "batch_checkpoint_write_allowed_now": False,
        "batch_checkpoint_seal_allowed_now": False,
        "evidence_export_allowed_now": False,
        "archive_write_allowed_now": False,
        "archive_packet_write_allowed_now": False,
        "archive_packet_seal_allowed_now": False,
        "archive_export_allowed_now": False,
        "owner_action_execution_allowed_now": False,
        "handoff_execution_allowed_now": False,
        "gateway_access_grant_allowed_now": False,
        "persist_allowed_now": False,
        "action_execution_allowed_now": False,
        "real_action_executed": False,
        "real_handoff_executed": False,
        "real_owner_action_executed": False,
        "real_evidence_exported": False,
        "real_export_request_created": False,
        "real_packet_written": False,
        "real_packet_sealed": False,
        "real_save_executed": False,
        "real_push_executed": False,
        "real_commit_executed": False,
        "real_git_write_executed": False,
        "real_batch_checkpoint_written": False,
        "real_batch_checkpoint_sealed": False,
        "real_archive_written": False,
        "real_archive_packet_written": False,
        "real_archive_packet_sealed": False,
        "real_archive_exported": False,
        "real_gateway_access_granted": False,
        "real_raw_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def _load_bridge(module_name: str, fn_name: str) -> Dict[str, object]:
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            try:
                payload = fn(force_refresh=True)
            except TypeError:
                payload = fn()
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_number": None,
            "status": "review",
            "readiness_score": 0,
            "error": str(exc),
        }
    return {
        "pack_number": None,
        "status": "review",
        "readiness_score": 0,
        "error": f"Missing bridge {fn_name}",
    }


def _pack_specs() -> List[Tuple[int, str, str, str]]:
    return [
        (211, "tower.receipt_chain_saved_checkpoint_lookup_v211", "build_receipt_chain_saved_checkpoint_lookup_v211_status_bridge", "/tower/receipt-chain-saved-checkpoint-lookup-v211.json"),
        (212, "tower.receipt_chain_checkpoint_filter_search_v212", "build_receipt_chain_checkpoint_filter_search_v212_status_bridge", "/tower/receipt-chain-checkpoint-filter-search-v212.json"),
        (213, "tower.receipt_chain_owner_review_drawer_v213", "build_receipt_chain_owner_review_drawer_v213_status_bridge", "/tower/receipt-chain-owner-review-drawer-v213.json"),
        (214, "tower.receipt_chain_evidence_detail_drawer_v214", "build_receipt_chain_evidence_detail_drawer_v214_status_bridge", "/tower/receipt-chain-evidence-detail-drawer-v214.json"),
    ]


def _recovered_dependency_specs() -> List[Tuple[int, str, str, str]]:
    return [
        (208, "tower.receipt_chain_incident_lane_v208", "build_receipt_chain_incident_lane_v208_status_bridge", "/tower/receipt-chain-incident-lane-v208.json"),
        (209, "tower.receipt_chain_archive_handoff_v209", "build_receipt_chain_archive_handoff_v209_status_bridge", "/tower/receipt-chain-archive-handoff-v209.json"),
        (210, "tower.receipt_chain_post_batch_checkpoint_v210", "build_receipt_chain_post_batch_checkpoint_v210_status_bridge", "/tower/receipt-chain-post-batch-checkpoint-v210.json"),
    ]


def _build_source_pack_cards() -> List[Dict[str, object]]:
    cards = []
    for sequence, (pack_number, module_name, fn_name, endpoint) in enumerate(_pack_specs(), start=1):
        bridge = _load_bridge(module_name, fn_name)
        real_count = sum(
            int(value or 0)
            for key, value in bridge.items()
            if key.startswith("real_") and key.endswith("_count") and isinstance(value, int)
        )
        raw_reveal_count = int(bridge.get("raw_evidence_revealed_count") or 0)

        card = {
            "source_pack_readiness_card_id": f"receipt_chain_batch_211_215_source_pack_{pack_number}_{_stable_hash((PACK_ID, pack_number), 10)}",
            "pack_number": pack_number,
            "pack_id": f"PACK_{pack_number}",
            "sequence": sequence,
            "module_name": module_name,
            "bridge_function": fn_name,
            "endpoint": endpoint,
            "source_status": bridge.get("status"),
            "source_readiness_score": bridge.get("readiness_score"),
            "source_pack_ready": bridge.get("status") == "ready" and bridge.get("readiness_score") == 100,
            "real_flag_count": real_count,
            "raw_evidence_revealed_count": raw_reveal_count,
            "source_safe_to_continue": bool(
                bridge.get(f"safe_to_continue_to_pack_{pack_number + 1}") is True
                or pack_number == 214 and bridge.get("safe_to_continue_to_pack_215") is True
            ),
            "card_status": "receipt_chain_batch_211_215_source_pack_card_ready",
            "safe_preview_only": True,
        }
        card.update(_base_flags())
        cards.append(card)
    return cards


def _build_recovered_dependency_cards() -> List[Dict[str, object]]:
    cards = []
    for sequence, (pack_number, module_name, fn_name, endpoint) in enumerate(_recovered_dependency_specs(), start=1):
        bridge = _load_bridge(module_name, fn_name)
        real_count = sum(
            int(value or 0)
            for key, value in bridge.items()
            if key.startswith("real_") and key.endswith("_count") and isinstance(value, int)
        )
        card = {
            "recovered_dependency_card_id": f"receipt_chain_recovered_dependency_{pack_number}_{_stable_hash((PACK_ID, pack_number), 10)}",
            "pack_number": pack_number,
            "pack_id": f"PACK_{pack_number}",
            "sequence": sequence,
            "module_name": module_name,
            "bridge_function": fn_name,
            "endpoint": endpoint,
            "source_status": bridge.get("status"),
            "source_readiness_score": bridge.get("readiness_score"),
            "dependency_ready": bridge.get("status") == "ready" and bridge.get("readiness_score") == 100,
            "dependency_recovered_locally": True,
            "must_save_push_to_remote": True,
            "real_flag_count": real_count,
            "raw_evidence_revealed_count": int(bridge.get("raw_evidence_revealed_count") or 0),
            "card_status": "receipt_chain_recovered_dependency_awareness_preview_ready",
            "safe_preview_only": True,
        }
        card.update(_base_flags())
        cards.append(card)
    return cards


def _build_evidence_detail_rollup(source_cards: List[Dict[str, object]]) -> Dict[str, object]:
    pack_214 = _load_bridge(
        "tower.receipt_chain_evidence_detail_drawer_v214",
        "build_receipt_chain_evidence_detail_drawer_v214_status_bridge",
    )
    rollup = {
        "evidence_detail_rollup_id": f"receipt_chain_evidence_detail_rollup_{_stable_hash((PACK_ID, 'evidence'), 12)}",
        "redacted_evidence_panel_count": pack_214.get("redacted_evidence_panel_count"),
        "evidence_source_trace_card_count": pack_214.get("evidence_source_trace_card_count"),
        "evidence_comparison_row_count": pack_214.get("evidence_comparison_row_count"),
        "evidence_review_tab_count": pack_214.get("evidence_review_tab_count"),
        "evidence_action_menu_item_count": pack_214.get("evidence_action_menu_item_count"),
        "raw_field_count": pack_214.get("raw_field_count"),
        "real_evidence_exported_count": pack_214.get("real_evidence_exported_count"),
        "real_archive_packet_written_count": pack_214.get("real_archive_packet_written_count"),
        "real_archive_packet_sealed_count": pack_214.get("real_archive_packet_sealed_count"),
        "raw_evidence_revealed_count": pack_214.get("raw_evidence_revealed_count"),
        "source_pack_count": len(source_cards),
        "rollup_status": "receipt_chain_evidence_detail_rollup_preview_ready",
        "safe_preview_only": True,
    }
    rollup.update(_base_flags())
    return rollup


def _build_batch_safety_rollup(source_cards, dependency_cards, evidence_rollup) -> Dict[str, object]:
    all_cards = source_cards + dependency_cards
    total_real_flags = sum(int(card.get("real_flag_count") or 0) for card in all_cards)
    total_raw_reveals = sum(int(card.get("raw_evidence_revealed_count") or 0) for card in all_cards)
    total_raw_reveals += int(evidence_rollup.get("raw_evidence_revealed_count") or 0)

    rollup = {
        "batch_safety_rollup_id": f"receipt_chain_batch_safety_rollup_{_stable_hash((PACK_ID, 'safety'), 12)}",
        "source_pack_count": len(source_cards),
        "ready_source_pack_count": sum(1 for card in source_cards if card.get("source_pack_ready") is True),
        "recovered_dependency_count": len(dependency_cards),
        "ready_recovered_dependency_count": sum(1 for card in dependency_cards if card.get("dependency_ready") is True),
        "total_real_flag_count": total_real_flags,
        "total_raw_evidence_revealed_count": total_raw_reveals,
        "raw_field_count": evidence_rollup.get("raw_field_count"),
        "all_source_packs_ready": all(card.get("source_pack_ready") is True for card in source_cards),
        "all_recovered_dependencies_ready": all(card.get("dependency_ready") is True for card in dependency_cards),
        "all_real_flags_zero": total_real_flags == 0,
        "all_raw_reveals_zero": total_raw_reveals == 0,
        "all_raw_fields_zero": evidence_rollup.get("raw_field_count") == 0,
        "safety_status": "receipt_chain_batch_211_215_safety_rollup_preview_ready",
        "safe_preview_only": True,
    }
    rollup.update(_base_flags())
    return rollup


def _build_save_push_readiness(safety_rollup: Dict[str, object]) -> Dict[str, object]:
    safe_to_save = (
        safety_rollup.get("all_source_packs_ready") is True
        and safety_rollup.get("all_recovered_dependencies_ready") is True
        and safety_rollup.get("all_real_flags_zero") is True
        and safety_rollup.get("all_raw_reveals_zero") is True
        and safety_rollup.get("all_raw_fields_zero") is True
    )

    readiness = {
        "save_push_readiness_id": f"receipt_chain_save_push_readiness_{_stable_hash((PACK_ID, safe_to_save), 12)}",
        "safe_to_save_recovered_packs_208_to_215": safe_to_save,
        "safe_to_push_recovered_packs_208_to_215": safe_to_save,
        "must_include_recovered_packs_208_to_210": True,
        "must_include_batch_211_to_215": True,
        "remote_recovery_note": "Fresh clone showed GitHub only had Pack 207; save/push must include recovered Packs 208-215.",
        "recommended_commit_message": "Recover Packs 208-212 and add Packs 213-215 receipt chain checkpoint",
        "real_save_executed": False,
        "real_push_executed": False,
        "real_commit_executed": False,
        "save_allowed_now": False,
        "push_allowed_now": False,
        "commit_allowed_now": False,
        "readiness_status": "receipt_chain_batch_211_215_save_push_readiness_preview_ready",
        "safe_preview_only": True,
    }
    readiness.update(_base_flags())
    return readiness


def _build_next_batch_handoffs() -> List[Dict[str, object]]:
    defs = [
        (216, "Receipt chain checkpoint saved view presets", "saved_view_presets"),
        (217, "Receipt chain checkpoint saved view detail drawer", "saved_view_detail"),
        (218, "Receipt chain checkpoint saved view edit preview", "saved_view_edit"),
        (219, "Receipt chain checkpoint saved view history preview", "saved_view_history"),
        (220, "Receipt chain batch 216-220 checkpoint", "batch_checkpoint"),
    ]

    handoffs = []
    for sequence, (pack_number, label, lane_type) in enumerate(defs, start=1):
        item = {
            "next_batch_handoff_preview_id": f"receipt_chain_next_batch_{pack_number}_{_stable_hash((PACK_ID, pack_number), 10)}",
            "pack_number": pack_number,
            "pack_id": f"PACK_{pack_number}",
            "label": label,
            "lane_type": lane_type,
            "sequence": sequence,
            "target_batch": "216-220",
            "planned_endpoint_preview": f"/tower/receipt-chain-pack-{pack_number}-preview.json",
            "handoff_status": "receipt_chain_next_batch_216_220_handoff_preview_ready",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        handoffs.append(item)
    return handoffs


def _build_checkpoint(safety_rollup, save_push, next_handoffs) -> Dict[str, object]:
    checkpoint_ok = (
        safety_rollup.get("all_source_packs_ready") is True
        and safety_rollup.get("all_recovered_dependencies_ready") is True
        and safety_rollup.get("all_real_flags_zero") is True
        and safety_rollup.get("all_raw_reveals_zero") is True
        and safety_rollup.get("all_raw_fields_zero") is True
        and save_push.get("safe_to_save_recovered_packs_208_to_215") is True
        and save_push.get("safe_to_push_recovered_packs_208_to_215") is True
        and len(next_handoffs) == 5
    )

    checkpoint = {
        "batch_checkpoint_id": f"receipt_chain_batch_211_215_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_batch_211_215_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_batch_211_215_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_batch_211_215_checkpoint_preview",
        "safe_to_save_recovered_packs_208_to_215": checkpoint_ok,
        "safe_to_push_recovered_packs_208_to_215": checkpoint_ok,
        "safe_to_continue_to_pack_216": checkpoint_ok,
        "closed_batch": "211-215",
        "recovered_dependency_batch": "208-210",
        "save_batch": "208-215",
        "save_after_pack": 215,
        "next_batch": "216-220",
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(source_cards, dependency_cards, handoffs, checkpoint) -> Dict[str, object]:
    return {
        "source_pack_cards_by_pack_number": {str(item["pack_number"]): item for item in source_cards},
        "recovered_dependency_cards_by_pack_number": {str(item["pack_number"]): item for item in dependency_cards},
        "next_batch_handoffs_by_pack_number": {str(item["pack_number"]): item for item in handoffs},
        "checkpoint_by_id": {checkpoint["batch_checkpoint_id"]: checkpoint},
    }


@lru_cache(maxsize=1)
def build_receipt_chain_batch_211_215_checkpoint_v215_payload_cached() -> Dict[str, object]:
    source_cards = _build_source_pack_cards()
    dependency_cards = _build_recovered_dependency_cards()
    evidence_rollup = _build_evidence_detail_rollup(source_cards)
    safety_rollup = _build_batch_safety_rollup(source_cards, dependency_cards, evidence_rollup)
    save_push = _build_save_push_readiness(safety_rollup)
    next_handoffs = _build_next_batch_handoffs()
    checkpoint = _build_checkpoint(safety_rollup, save_push, next_handoffs)
    indexes = _build_indexes(source_cards, dependency_cards, next_handoffs, checkpoint)

    all_cards = source_cards + dependency_cards + next_handoffs

    readiness_checks = {
        "has_four_source_packs_211_214": len(source_cards) == 4,
        "pack_211_ready": indexes["source_pack_cards_by_pack_number"].get("211", {}).get("source_pack_ready") is True,
        "pack_212_ready": indexes["source_pack_cards_by_pack_number"].get("212", {}).get("source_pack_ready") is True,
        "pack_213_ready": indexes["source_pack_cards_by_pack_number"].get("213", {}).get("source_pack_ready") is True,
        "pack_214_ready": indexes["source_pack_cards_by_pack_number"].get("214", {}).get("source_pack_ready") is True,
        "has_recovered_dependencies_208_210": len(dependency_cards) == 3,
        "pack_208_recovered_ready": indexes["recovered_dependency_cards_by_pack_number"].get("208", {}).get("dependency_ready") is True,
        "pack_209_recovered_ready": indexes["recovered_dependency_cards_by_pack_number"].get("209", {}).get("dependency_ready") is True,
        "pack_210_recovered_ready": indexes["recovered_dependency_cards_by_pack_number"].get("210", {}).get("dependency_ready") is True,
        "evidence_rollup_ready": evidence_rollup.get("rollup_status") == "receipt_chain_evidence_detail_rollup_preview_ready",
        "safety_rollup_ready": safety_rollup.get("safety_status") == "receipt_chain_batch_211_215_safety_rollup_preview_ready",
        "save_push_readiness_ready": save_push.get("readiness_status") == "receipt_chain_batch_211_215_save_push_readiness_preview_ready",
        "safe_to_save_recovered_packs_208_to_215": save_push.get("safe_to_save_recovered_packs_208_to_215") is True,
        "safe_to_push_recovered_packs_208_to_215": save_push.get("safe_to_push_recovered_packs_208_to_215") is True,
        "has_next_batch_handoffs_216_220": len(next_handoffs) == 5,
        "all_next_batch_handoffs_ready": all(item.get("handoff_status") == "receipt_chain_next_batch_216_220_handoff_preview_ready" for item in next_handoffs),
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_batch_211_215_checkpoint_preview_ready",
        "safe_to_continue_to_pack_216": checkpoint.get("safe_to_continue_to_pack_216") is True,
        "indexes_present": bool(indexes.get("source_pack_cards_by_pack_number")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_cards),
        "all_batch_checkpoint_preview_only": all(item.get("batch_checkpoint_preview_only") is True for item in all_cards),
        "no_real_save_executed": save_push.get("real_save_executed") is False,
        "no_real_push_executed": save_push.get("real_push_executed") is False,
        "no_real_commit_executed": save_push.get("real_commit_executed") is False,
        "no_real_evidence_exported": evidence_rollup.get("real_evidence_exported_count") == 0,
        "no_real_archive_written": evidence_rollup.get("real_archive_packet_written_count") == 0,
        "no_real_archive_sealed": evidence_rollup.get("real_archive_packet_sealed_count") == 0,
        "no_real_raw_evidence_revealed": safety_rollup.get("total_raw_evidence_revealed_count") == 0,
        "all_real_flags_zero": safety_rollup.get("all_real_flags_zero") is True,
        "all_raw_fields_zero": safety_rollup.get("all_raw_fields_zero") is True,
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    summary = {
        "source_pack_count": len(source_cards),
        "ready_source_pack_count": safety_rollup.get("ready_source_pack_count"),
        "recovered_dependency_count": len(dependency_cards),
        "ready_recovered_dependency_count": safety_rollup.get("ready_recovered_dependency_count"),
        "evidence_detail_rollup_count": 1,
        "batch_safety_rollup_count": 1,
        "save_push_readiness_count": 1,
        "next_batch_handoff_count": len(next_handoffs),
        "final_checkpoint_count": 1,
        "total_real_flag_count": safety_rollup.get("total_real_flag_count"),
        "total_raw_evidence_revealed_count": safety_rollup.get("total_raw_evidence_revealed_count"),
        "raw_field_count": safety_rollup.get("raw_field_count"),
        "real_save_executed_count": 0,
        "real_push_executed_count": 0,
        "real_commit_executed_count": 0,
        "real_batch_checkpoint_written_count": 0,
        "real_batch_checkpoint_sealed_count": 0,
        "real_evidence_exported_count": evidence_rollup.get("real_evidence_exported_count"),
        "real_archive_written_count": evidence_rollup.get("real_archive_packet_written_count"),
        "real_archive_packet_sealed_count": evidence_rollup.get("real_archive_packet_sealed_count"),
        "raw_evidence_revealed_count": safety_rollup.get("total_raw_evidence_revealed_count"),
        "safe_to_save_recovered_packs_208_to_215": checkpoint.get("safe_to_save_recovered_packs_208_to_215"),
        "safe_to_push_recovered_packs_208_to_215": checkpoint.get("safe_to_push_recovered_packs_208_to_215"),
        "safe_to_continue_to_pack_216": checkpoint.get("safe_to_continue_to_pack_216"),
        "closed_batch": "211-215",
        "recovered_dependency_batch": "208-210",
        "save_batch": "208-215",
        "save_after_pack": 215,
        "next_batch": "216-220",
        "readiness_score": readiness_score,
        "readiness_label": "Receipt chain 211-215 batch checkpoint ready" if readiness_score == 100 else "Receipt chain 211-215 batch checkpoint needs review",
    }

    return {
        "pack_id": PACK_ID,
        "pack_number": 215,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Batch 211-215 Checkpoint Preview",
        "endpoint": BATCH_CHECKPOINT_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "summary": summary,
        "readiness_checks": readiness_checks,
        "source_pack_readiness_cards": source_cards,
        "recovered_dependency_awareness_cards": dependency_cards,
        "evidence_detail_rollup": evidence_rollup,
        "batch_safety_rollup": safety_rollup,
        "save_push_readiness_preview": save_push,
        "next_batch_handoff_previews": next_handoffs,
        "batch_checkpoint": checkpoint,
        "batch_checkpoint_indexes": indexes,
    }


def build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_batch_211_215_checkpoint_v215_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_batch_211_215_checkpoint_v215_payload_cached())


def get_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh=force_refresh)


def build_receipt_chain_batch_211_215_checkpoint_v215_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_batch_211_215_checkpoint_v215_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 215,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "source_pack_count": summary.get("source_pack_count"),
        "ready_source_pack_count": summary.get("ready_source_pack_count"),
        "recovered_dependency_count": summary.get("recovered_dependency_count"),
        "ready_recovered_dependency_count": summary.get("ready_recovered_dependency_count"),
        "evidence_detail_rollup_count": summary.get("evidence_detail_rollup_count"),
        "batch_safety_rollup_count": summary.get("batch_safety_rollup_count"),
        "save_push_readiness_count": summary.get("save_push_readiness_count"),
        "next_batch_handoff_count": summary.get("next_batch_handoff_count"),
        "final_checkpoint_count": summary.get("final_checkpoint_count"),
        "total_real_flag_count": summary.get("total_real_flag_count"),
        "total_raw_evidence_revealed_count": summary.get("total_raw_evidence_revealed_count"),
        "raw_field_count": summary.get("raw_field_count"),
        "real_save_executed_count": summary.get("real_save_executed_count"),
        "real_push_executed_count": summary.get("real_push_executed_count"),
        "real_commit_executed_count": summary.get("real_commit_executed_count"),
        "real_batch_checkpoint_written_count": summary.get("real_batch_checkpoint_written_count"),
        "real_batch_checkpoint_sealed_count": summary.get("real_batch_checkpoint_sealed_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "real_archive_written_count": summary.get("real_archive_written_count"),
        "real_archive_packet_sealed_count": summary.get("real_archive_packet_sealed_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_save_recovered_packs_208_to_215": summary.get("safe_to_save_recovered_packs_208_to_215"),
        "safe_to_push_recovered_packs_208_to_215": summary.get("safe_to_push_recovered_packs_208_to_215"),
        "safe_to_continue_to_pack_216": summary.get("safe_to_continue_to_pack_216"),
        "closed_batch": summary.get("closed_batch"),
        "recovered_dependency_batch": summary.get("recovered_dependency_batch"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        "next_batch": summary.get("next_batch"),
        **_base_flags(),
    }


def get_receipt_chain_batch_211_215_checkpoint_v215_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_batch_211_215_checkpoint_v215_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_batch_211_215_checkpoint_v215_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_batch_211_215_checkpoint_v215_status_bridge()
    action = {
        "id": "receipt_chain_batch_211_215_checkpoint_v215",
        "label": "Receipt Chain Batch 211-215 Checkpoint",
        "title": "Receipt Chain Batch 211-215 Checkpoint Preview",
        "href": BATCH_CHECKPOINT_ENDPOINT,
        "endpoint": BATCH_CHECKPOINT_ENDPOINT,
        "description": "Preview batch closure, recovered dependency awareness, save/push readiness, and next batch handoff.",
        "status": bridge.get("status"),
        "pack": "Pack 215",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_batch_211_215_checkpoint_v215_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_batch_211_215_checkpoint_v215_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    section = {
        "section_id": "receipt_chain_batch_211_215_checkpoint_v215",
        "title": "Receipt Chain Batch 211-215 Checkpoint",
        "subtitle": "Closes the 211-215 batch and confirms recovered 208-210 dependencies must be saved/pushed with this batch.",
        "status": payload.get("status"),
        "href": BATCH_CHECKPOINT_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Batch readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "source_packs", "title": "Source packs", "value": summary.get("ready_source_pack_count"), "label": "Ready of 4"},
            {"id": "recovered", "title": "Recovered deps", "value": summary.get("ready_recovered_dependency_count"), "label": "Ready of 3"},
            {"id": "handoff", "title": "Next handoffs", "value": summary.get("next_batch_handoff_count"), "label": "216-220"},
            {"id": "save", "title": "Save/push", "value": "Ready" if checks.get("safe_to_push_recovered_packs_208_to_215") else "Review", "label": "Include 208-215"},
            {"id": "safety", "title": "Safety", "value": "Clean" if checks.get("all_real_flags_zero") and checks.get("no_real_raw_evidence_revealed") else "Review", "label": "No real flags"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "BATCH_CHECKPOINT_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_batch_211_215_checkpoint_v215_payload",
    "get_receipt_chain_batch_211_215_checkpoint_v215_payload",
    "build_receipt_chain_batch_211_215_checkpoint_v215_status_bridge",
    "get_receipt_chain_batch_211_215_checkpoint_v215_status_bridge",
    "build_receipt_chain_batch_211_215_checkpoint_v215_quick_action",
    "build_receipt_chain_batch_211_215_checkpoint_v215_unified_owner_section",
]
