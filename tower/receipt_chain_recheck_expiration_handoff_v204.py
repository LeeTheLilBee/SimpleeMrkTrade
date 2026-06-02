
"""
PACK 204 - Receipt Chain Recheck / Expiration Handoff Preview.

Short module filename:
    tower.receipt_chain_recheck_expiration_handoff_v204

This module sits on top of Pack 203.

Pack 203 created redacted evidence packet previews and blocked export requests.
Pack 204 creates preview-only recheck/expiration handoff hooks:
- recheck handoff hook previews
- expiration trigger previews
- renewal trigger previews
- evidence packet freshness lane previews
- owner follow-up review queue preview
- blocked recheck/renewal/expiration/export/write proof

Important:
- simulated-only
- recheck-expiration-handoff-preview-only
- no real recheck executed
- no real renewal executed
- no real expiration enforced
- no real evidence export
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


PACK_ID = "PACK_204"
RECHECK_EXPIRATION_HANDOFF_ENDPOINT = "/tower/receipt-chain-recheck-expiration-handoff-v204.json"
SOURCE_ENDPOINT = "/tower/receipt-chain-evidence-packet-v203.json"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _base_flags() -> Dict[str, object]:
    return {
        "simulated_only": True,
        "recheck_expiration_handoff_preview_only": True,
        "recheck_hook_preview_only": True,
        "expiration_trigger_preview_only": True,
        "renewal_trigger_preview_only": True,
        "freshness_lane_preview_only": True,
        "owner_followup_queue_preview_only": True,
        "evidence_packet_preview_only": True,
        "evidence_bundle_preview_only": True,
        "packet_section_preview_only": True,
        "export_request_preview_only": True,
        "export_blocked": True,
        "raw_evidence_redacted": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
        "operational_handoff_preview_only": True,
        "receipt_chain_handoff_preview_only": True,
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


def _load_pack_203_payload(force_refresh: bool = False) -> Dict[str, object]:
    try:
        mod = importlib.import_module("tower.receipt_chain_evidence_packet_v203")
        fn = getattr(mod, "build_receipt_chain_evidence_packet_v203_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_203",
            "status": "review",
            "endpoint": SOURCE_ENDPOINT,
            "summary": {"readiness_score": 0},
            "evidence_packet_sections": [],
            "evidence_bundle_packet_previews": [],
            "evidence_export_request_previews": [],
            "owner_review_checklist": [],
            "load_error": str(exc),
            **_base_flags(),
        }

    return {
        "pack_id": "PACK_203",
        "status": "review",
        "endpoint": SOURCE_ENDPOINT,
        "summary": {"readiness_score": 0},
        "evidence_packet_sections": [],
        "evidence_bundle_packet_previews": [],
        "evidence_export_request_previews": [],
        "owner_review_checklist": [],
        **_base_flags(),
    }


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_freshness_lanes(packet_sections: List[Dict[str, object]], packets: List[Dict[str, object]]) -> List[Dict[str, object]]:
    section_count = len(packet_sections)
    packet_count = len(packets)

    lane_defs = [
        ("fresh_packet_sections", "Fresh packet sections", "fresh", section_count, "Evidence packet sections are preview-fresh."),
        ("fresh_bundle_packets", "Fresh bundle packets", "fresh", packet_count, "Evidence bundle packets are preview-fresh."),
        ("recheck_required_later", "Recheck required later", "future_recheck", 3, "Future owner recheck should occur before real export or enforcement."),
        ("expiration_review_later", "Expiration review later", "future_expiration_review", 2, "Future expiration review should occur before real policy use."),
        ("renewal_candidate_later", "Renewal candidate later", "future_renewal_candidate", 2, "Future renewal review should occur before reuse."),
    ]

    lanes = []
    for sequence, (lane_key, label, freshness_state, item_count, description) in enumerate(lane_defs, start=1):
        lane = {
            "freshness_lane_preview_id": f"receipt_chain_freshness_lane_{_stable_hash((PACK_ID, lane_key), 18)}",
            "freshness_lane_key": lane_key,
            "label": label,
            "description": description,
            "freshness_state": freshness_state,
            "sequence": sequence,
            "matched_item_count": int(item_count or 0),
            "lane_status": "receipt_chain_freshness_lane_preview_ready",
            "lane_result_type": "tower_receipt_chain_recheck_expiration_freshness_lane_preview",
            "safe_preview_only": True,
        }
        lane.update(_base_flags())
        lanes.append(lane)

    return lanes


def _build_recheck_hooks(freshness_lanes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    hook_defs = [
        ("owner_recheck_before_export", "Owner recheck before export", "export", "blocked_until_future_owner_review"),
        ("owner_recheck_before_gateway_use", "Owner recheck before gateway use", "gateway", "blocked_until_future_owner_review"),
        ("owner_recheck_before_policy_reuse", "Owner recheck before policy reuse", "policy", "blocked_until_future_owner_review"),
        ("owner_recheck_before_archive_packet", "Owner recheck before archive packet", "archive", "blocked_until_future_owner_review"),
    ]

    hooks = []
    lane_keys = [lane.get("freshness_lane_key") for lane in freshness_lanes]

    for sequence, (hook_key, label, target_area, state) in enumerate(hook_defs, start=1):
        hook = {
            "recheck_handoff_hook_preview_id": f"receipt_chain_recheck_hook_{_stable_hash((PACK_ID, hook_key), 18)}",
            "recheck_hook_key": hook_key,
            "label": label,
            "target_area": target_area,
            "sequence": sequence,
            "hook_state": state,
            "source_freshness_lane_keys": lane_keys,
            "recheck_allowed_now": False,
            "recheck_status": "receipt_chain_recheck_handoff_hook_preview_blocked",
            "recheck_result_type": "tower_receipt_chain_recheck_handoff_hook_preview",
            "safe_preview_only": True,
        }
        hook.update(_base_flags())
        hooks.append(hook)

    return hooks


def _build_expiration_triggers(packet_sections: List[Dict[str, object]]) -> List[Dict[str, object]]:
    trigger_defs = [
        ("packet_section_stale_later", "Packet section stale later", "section_age", 30),
        ("bundle_packet_stale_later", "Bundle packet stale later", "bundle_age", 30),
        ("export_request_stale_later", "Export request stale later", "export_age", 7),
        ("owner_review_stale_later", "Owner review stale later", "review_age", 14),
    ]

    triggers = []
    section_keys = [section.get("section_key") for section in packet_sections]

    for sequence, (trigger_key, label, trigger_type, preview_days) in enumerate(trigger_defs, start=1):
        trigger = {
            "expiration_trigger_preview_id": f"receipt_chain_expiration_trigger_{_stable_hash((PACK_ID, trigger_key), 18)}",
            "expiration_trigger_key": trigger_key,
            "label": label,
            "trigger_type": trigger_type,
            "preview_days_until_review": int(preview_days),
            "sequence": sequence,
            "source_section_keys": section_keys,
            "expiration_enforcement_allowed_now": False,
            "expiration_status": "receipt_chain_expiration_trigger_preview_blocked",
            "expiration_result_type": "tower_receipt_chain_expiration_trigger_preview",
            "safe_preview_only": True,
        }
        trigger.update(_base_flags())
        triggers.append(trigger)

    return triggers


def _build_renewal_triggers(packets: List[Dict[str, object]]) -> List[Dict[str, object]]:
    trigger_defs = [
        ("renew_owner_review_packet", "Renew owner review packet", "owner_review_packet"),
        ("renew_audit_preview_packet", "Renew audit preview packet", "audit_preview_packet"),
        ("renew_next_batch_packet", "Renew next batch packet", "next_batch_packet"),
    ]

    packet_keys = {packet.get("packet_key") for packet in packets}
    triggers = []

    for sequence, (trigger_key, label, packet_key) in enumerate(trigger_defs, start=1):
        trigger = {
            "renewal_trigger_preview_id": f"receipt_chain_renewal_trigger_{_stable_hash((PACK_ID, trigger_key), 18)}",
            "renewal_trigger_key": trigger_key,
            "label": label,
            "packet_key": packet_key,
            "source_packet_available": packet_key in packet_keys,
            "sequence": sequence,
            "renewal_allowed_now": False,
            "renewal_status": "receipt_chain_renewal_trigger_preview_blocked",
            "renewal_result_type": "tower_receipt_chain_renewal_trigger_preview",
            "safe_preview_only": True,
        }
        trigger.update(_base_flags())
        triggers.append(trigger)

    return triggers


def _build_owner_followup_queue(recheck_hooks: List[Dict[str, object]], expirations: List[Dict[str, object]], renewals: List[Dict[str, object]]) -> List[Dict[str, object]]:
    queue_defs = [
        ("review_recheck_hooks", "Review recheck hooks", "recheck", len(recheck_hooks)),
        ("review_expiration_triggers", "Review expiration triggers", "expiration", len(expirations)),
        ("review_renewal_triggers", "Review renewal triggers", "renewal", len(renewals)),
        ("confirm_no_real_enforcement", "Confirm no real enforcement", "safety", 0),
        ("prepare_pack_205_checkpoint", "Prepare Pack 205 checkpoint", "checkpoint", 0),
    ]

    queue = []
    for sequence, (queue_key, label, queue_type, item_count) in enumerate(queue_defs, start=1):
        item = {
            "owner_followup_queue_item_preview_id": f"receipt_chain_owner_followup_{_stable_hash((PACK_ID, queue_key), 18)}",
            "queue_key": queue_key,
            "label": label,
            "queue_type": queue_type,
            "sequence": sequence,
            "linked_preview_item_count": int(item_count or 0),
            "owner_followup_allowed_now": False,
            "queue_status": "receipt_chain_owner_followup_queue_item_preview_blocked",
            "queue_result_type": "tower_receipt_chain_owner_followup_queue_preview",
            "safe_preview_only": True,
        }
        item.update(_base_flags())
        queue.append(item)

    return queue


def _build_safety_summary(lanes: List[Dict[str, object]], hooks: List[Dict[str, object]], expirations: List[Dict[str, object]], renewals: List[Dict[str, object]], queue: List[Dict[str, object]]) -> Dict[str, object]:
    all_items = lanes + hooks + expirations + renewals + queue

    summary = {
        "recheck_expiration_safety_summary_id": f"receipt_chain_recheck_expiration_safety_{_stable_hash((PACK_ID, len(all_items)), 18)}",
        "freshness_lane_count": len(lanes),
        "recheck_hook_count": len(hooks),
        "expiration_trigger_count": len(expirations),
        "renewal_trigger_count": len(renewals),
        "owner_followup_queue_item_count": len(queue),
        "real_recheck_executed_count": 0,
        "real_renewal_executed_count": 0,
        "real_expiration_enforced_count": 0,
        "real_owner_followup_executed_count": 0,
        "real_evidence_exported_count": 0,
        "raw_evidence_revealed_count": 0,
        "all_rechecks_blocked": all(item.get("recheck_execution_allowed_now") is False for item in all_items),
        "all_renewals_blocked": all(item.get("renewal_execution_allowed_now") is False for item in all_items),
        "all_expirations_blocked": all(item.get("expiration_enforcement_allowed_now") is False for item in all_items),
        "all_followups_blocked": all(item.get("owner_followup_execution_allowed_now") is False for item in all_items),
        "all_raw_reveals_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "summary_status": "receipt_chain_recheck_expiration_safety_summary_preview_ready",
        "summary_result_type": "tower_receipt_chain_recheck_expiration_safety_summary_preview",
        "safe_preview_only": True,
    }
    summary.update(_base_flags())
    return summary


def _build_checkpoint(safety: Dict[str, object]) -> Dict[str, object]:
    checkpoint_ok = (
        safety.get("freshness_lane_count") == 5
        and safety.get("recheck_hook_count") == 4
        and safety.get("expiration_trigger_count") == 4
        and safety.get("renewal_trigger_count") == 3
        and safety.get("owner_followup_queue_item_count") == 5
        and safety.get("real_recheck_executed_count") == 0
        and safety.get("real_renewal_executed_count") == 0
        and safety.get("real_expiration_enforced_count") == 0
        and safety.get("real_owner_followup_executed_count") == 0
        and safety.get("real_evidence_exported_count") == 0
        and safety.get("raw_evidence_revealed_count") == 0
    )

    checkpoint = {
        "recheck_expiration_handoff_checkpoint_id": f"receipt_chain_recheck_expiration_checkpoint_{_stable_hash((PACK_ID, checkpoint_ok), 18)}",
        "checkpoint_ok": checkpoint_ok,
        "checkpoint_status": "receipt_chain_recheck_expiration_handoff_checkpoint_preview_ready" if checkpoint_ok else "receipt_chain_recheck_expiration_handoff_checkpoint_preview_review",
        "checkpoint_result_type": "tower_receipt_chain_recheck_expiration_handoff_checkpoint_preview",
        "safe_to_continue_to_pack_205": checkpoint_ok,
        "save_batch": "201-205",
        "save_after_pack": 205,
        "safe_preview_only": True,
    }
    checkpoint.update(_base_flags())
    return checkpoint


def _build_indexes(lanes: List[Dict[str, object]], hooks: List[Dict[str, object]], expirations: List[Dict[str, object]], renewals: List[Dict[str, object]], queue: List[Dict[str, object]], checkpoint: Dict[str, object]) -> Dict[str, object]:
    indexes = {
        "freshness_lanes_by_id": {},
        "freshness_lanes_by_key": {},
        "recheck_hooks_by_id": {},
        "recheck_hooks_by_key": {},
        "expiration_triggers_by_id": {},
        "expiration_triggers_by_key": {},
        "renewal_triggers_by_id": {},
        "renewal_triggers_by_key": {},
        "owner_followup_queue_by_id": {},
        "owner_followup_queue_by_key": {},
        "checkpoint_by_id": {},
    }

    for item in lanes:
        indexes["freshness_lanes_by_id"][item.get("freshness_lane_preview_id")] = item
        indexes["freshness_lanes_by_key"][item.get("freshness_lane_key")] = item

    for item in hooks:
        indexes["recheck_hooks_by_id"][item.get("recheck_handoff_hook_preview_id")] = item
        indexes["recheck_hooks_by_key"][item.get("recheck_hook_key")] = item

    for item in expirations:
        indexes["expiration_triggers_by_id"][item.get("expiration_trigger_preview_id")] = item
        indexes["expiration_triggers_by_key"][item.get("expiration_trigger_key")] = item

    for item in renewals:
        indexes["renewal_triggers_by_id"][item.get("renewal_trigger_preview_id")] = item
        indexes["renewal_triggers_by_key"][item.get("renewal_trigger_key")] = item

    for item in queue:
        indexes["owner_followup_queue_by_id"][item.get("owner_followup_queue_item_preview_id")] = item
        indexes["owner_followup_queue_by_key"][item.get("queue_key")] = item

    indexes["checkpoint_by_id"][checkpoint.get("recheck_expiration_handoff_checkpoint_id")] = checkpoint
    return indexes


@lru_cache(maxsize=1)
def build_receipt_chain_recheck_expiration_handoff_v204_payload_cached() -> Dict[str, object]:
    pack_203 = _load_pack_203_payload(force_refresh=True)

    packet_sections = [item for item in _list(pack_203.get("evidence_packet_sections")) if isinstance(item, dict)]
    packets = [item for item in _list(pack_203.get("evidence_bundle_packet_previews")) if isinstance(item, dict)]

    lanes = _build_freshness_lanes(packet_sections, packets)
    hooks = _build_recheck_hooks(lanes)
    expirations = _build_expiration_triggers(packet_sections)
    renewals = _build_renewal_triggers(packets)
    queue = _build_owner_followup_queue(hooks, expirations, renewals)
    safety = _build_safety_summary(lanes, hooks, expirations, renewals, queue)
    checkpoint = _build_checkpoint(safety)
    indexes = _build_indexes(lanes, hooks, expirations, renewals, queue, checkpoint)

    all_items = lanes + hooks + expirations + renewals + queue

    readiness_checks = {
        "pack_203_ready": pack_203.get("status") == "ready",
        "has_freshness_lanes": len(lanes) == 5,
        "has_recheck_hooks": len(hooks) == 4,
        "has_expiration_triggers": len(expirations) == 4,
        "has_renewal_triggers": len(renewals) == 3,
        "has_owner_followup_queue": len(queue) == 5,
        "all_freshness_lanes_ready": all(item.get("lane_status") == "receipt_chain_freshness_lane_preview_ready" for item in lanes),
        "all_recheck_hooks_blocked": all(item.get("recheck_status") == "receipt_chain_recheck_handoff_hook_preview_blocked" for item in hooks),
        "all_expiration_triggers_blocked": all(item.get("expiration_status") == "receipt_chain_expiration_trigger_preview_blocked" for item in expirations),
        "all_renewal_triggers_blocked": all(item.get("renewal_status") == "receipt_chain_renewal_trigger_preview_blocked" for item in renewals),
        "all_owner_followups_blocked": all(item.get("queue_status") == "receipt_chain_owner_followup_queue_item_preview_blocked" for item in queue),
        "safety_summary_ready": safety.get("summary_status") == "receipt_chain_recheck_expiration_safety_summary_preview_ready",
        "checkpoint_ready": checkpoint.get("checkpoint_status") == "receipt_chain_recheck_expiration_handoff_checkpoint_preview_ready",
        "safe_to_continue_to_pack_205": checkpoint.get("safe_to_continue_to_pack_205") is True,
        "indexes_present": bool(indexes.get("freshness_lanes_by_id")),
        "checkpoint_index_present": bool(indexes.get("checkpoint_by_id")),
        "all_simulated_only": all(item.get("simulated_only") is True for item in all_items),
        "all_recheck_expiration_preview_only": all(item.get("recheck_expiration_handoff_preview_only") is True for item in all_items),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in all_items),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in all_items),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in all_items),
        "no_real_owner_followup_executed": all(item.get("real_owner_followup_executed") is False for item in all_items),
        "no_real_evidence_exported": all(item.get("real_evidence_exported") is False for item in all_items),
        "no_real_raw_evidence_revealed": all(item.get("real_raw_evidence_revealed") is False for item in all_items),
        "all_recheck_execution_blocked": all(item.get("recheck_execution_allowed_now") is False for item in all_items),
        "all_renewal_execution_blocked": all(item.get("renewal_execution_allowed_now") is False for item in all_items),
        "all_expiration_enforcement_blocked": all(item.get("expiration_enforcement_allowed_now") is False for item in all_items),
        "all_owner_followup_execution_blocked": all(item.get("owner_followup_execution_allowed_now") is False for item in all_items),
        "all_evidence_export_blocked": all(item.get("evidence_export_allowed_now") is False for item in all_items),
        "all_raw_evidence_reveal_blocked": all(item.get("raw_evidence_reveal_allowed") is False for item in all_items),
        "cached_non_recursive": True,
    }

    readiness_score = 100 if all(v for v in readiness_checks.values() if isinstance(v, bool)) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 204,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Receipt Chain Recheck / Expiration Handoff Preview",
        "endpoint": RECHECK_EXPIRATION_HANDOFF_ENDPOINT,
        "source_endpoint": SOURCE_ENDPOINT,
        "generated_at": _utc_now(),
        **_base_flags(),
        "source_pack_203": {
            "status": pack_203.get("status"),
            "readiness_score": pack_203.get("summary", {}).get("readiness_score"),
            "packet_section_count": pack_203.get("summary", {}).get("packet_section_count"),
            "evidence_bundle_packet_count": pack_203.get("summary", {}).get("evidence_bundle_packet_count"),
        },
        "summary": {
            "freshness_lane_count": len(lanes),
            "recheck_hook_count": len(hooks),
            "expiration_trigger_count": len(expirations),
            "renewal_trigger_count": len(renewals),
            "owner_followup_queue_item_count": len(queue),
            "real_recheck_executed_count": safety.get("real_recheck_executed_count"),
            "real_renewal_executed_count": safety.get("real_renewal_executed_count"),
            "real_expiration_enforced_count": safety.get("real_expiration_enforced_count"),
            "real_owner_followup_executed_count": safety.get("real_owner_followup_executed_count"),
            "real_evidence_exported_count": safety.get("real_evidence_exported_count"),
            "raw_evidence_revealed_count": safety.get("raw_evidence_revealed_count"),
            "safe_to_continue_to_pack_205": checkpoint.get("safe_to_continue_to_pack_205"),
            "save_batch": "201-205",
            "save_after_pack": 205,
            "readiness_score": readiness_score,
            "readiness_label": "Receipt chain recheck/expiration handoff preview ready" if readiness_score == 100 else "Receipt chain recheck/expiration handoff preview needs review",
        },
        "readiness_checks": readiness_checks,
        "freshness_lane_previews": lanes,
        "recheck_handoff_hook_previews": hooks,
        "expiration_trigger_previews": expirations,
        "renewal_trigger_previews": renewals,
        "owner_followup_queue_previews": queue,
        "recheck_expiration_safety_summary": safety,
        "recheck_expiration_handoff_checkpoint": checkpoint,
        "recheck_expiration_handoff_indexes": indexes,
    }


def build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh: bool = False) -> Dict[str, object]:
    if force_refresh:
        build_receipt_chain_recheck_expiration_handoff_v204_payload_cached.cache_clear()
    return copy.deepcopy(build_receipt_chain_recheck_expiration_handoff_v204_payload_cached())


def get_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh=force_refresh)


def build_receipt_chain_recheck_expiration_handoff_v204_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    payload = build_receipt_chain_recheck_expiration_handoff_v204_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})
    return {
        "pack_id": PACK_ID,
        "pack_number": 204,
        "status": payload.get("status"),
        "endpoint": payload.get("endpoint"),
        "source_endpoint": payload.get("source_endpoint"),
        "readiness_score": summary.get("readiness_score"),
        "readiness_label": summary.get("readiness_label"),
        "freshness_lane_count": summary.get("freshness_lane_count"),
        "recheck_hook_count": summary.get("recheck_hook_count"),
        "expiration_trigger_count": summary.get("expiration_trigger_count"),
        "renewal_trigger_count": summary.get("renewal_trigger_count"),
        "owner_followup_queue_item_count": summary.get("owner_followup_queue_item_count"),
        "real_recheck_executed_count": summary.get("real_recheck_executed_count"),
        "real_renewal_executed_count": summary.get("real_renewal_executed_count"),
        "real_expiration_enforced_count": summary.get("real_expiration_enforced_count"),
        "real_owner_followup_executed_count": summary.get("real_owner_followup_executed_count"),
        "real_evidence_exported_count": summary.get("real_evidence_exported_count"),
        "raw_evidence_revealed_count": summary.get("raw_evidence_revealed_count"),
        "safe_to_continue_to_pack_205": summary.get("safe_to_continue_to_pack_205"),
        "save_batch": summary.get("save_batch"),
        "save_after_pack": summary.get("save_after_pack"),
        **_base_flags(),
    }


def get_receipt_chain_recheck_expiration_handoff_v204_status_bridge(force_refresh: bool = False) -> Dict[str, object]:
    return build_receipt_chain_recheck_expiration_handoff_v204_status_bridge(force_refresh=force_refresh)


def build_receipt_chain_recheck_expiration_handoff_v204_quick_action() -> Dict[str, object]:
    bridge = build_receipt_chain_recheck_expiration_handoff_v204_status_bridge()
    action = {
        "id": "receipt_chain_recheck_expiration_handoff_v204",
        "label": "Receipt Chain Recheck Handoff",
        "title": "Receipt Chain Recheck / Expiration Handoff Preview",
        "href": RECHECK_EXPIRATION_HANDOFF_ENDPOINT,
        "endpoint": RECHECK_EXPIRATION_HANDOFF_ENDPOINT,
        "description": "Preview recheck, expiration, renewal, and owner follow-up handoff hooks with real enforcement blocked.",
        "status": bridge.get("status"),
        "pack": "Pack 204",
        "category": "policy",
    }
    action.update(_base_flags())
    return action


def build_receipt_chain_recheck_expiration_handoff_v204_unified_owner_section() -> Dict[str, object]:
    payload = build_receipt_chain_recheck_expiration_handoff_v204_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})
    section = {
        "section_id": "receipt_chain_recheck_expiration_handoff_v204",
        "title": "Receipt Chain Recheck Handoff",
        "subtitle": "Preview recheck, expiration, renewal, and owner follow-up hooks.",
        "status": payload.get("status"),
        "href": RECHECK_EXPIRATION_HANDOFF_ENDPOINT,
        "cards": [
            {"id": "readiness", "title": "Handoff readiness", "value": summary.get("readiness_score"), "label": summary.get("readiness_label")},
            {"id": "freshness", "title": "Freshness lanes", "value": summary.get("freshness_lane_count"), "label": "Preview freshness lanes"},
            {"id": "recheck", "title": "Recheck hooks", "value": summary.get("recheck_hook_count"), "label": "Blocked recheck hooks"},
            {"id": "expiration", "title": "Expiration triggers", "value": summary.get("expiration_trigger_count"), "label": "Blocked expiration triggers"},
            {"id": "renewal", "title": "Renewal triggers", "value": summary.get("renewal_trigger_count"), "label": "Blocked renewal triggers"},
            {"id": "safety", "title": "Enforcement", "value": "Blocked" if checks.get("no_real_recheck_executed") and checks.get("no_real_expiration_enforced") else "Review", "label": "No real recheck/expiration"},
        ],
    }
    section.update(_base_flags())
    return section


__all__ = [
    "PACK_ID",
    "RECHECK_EXPIRATION_HANDOFF_ENDPOINT",
    "SOURCE_ENDPOINT",
    "build_receipt_chain_recheck_expiration_handoff_v204_payload",
    "get_receipt_chain_recheck_expiration_handoff_v204_payload",
    "build_receipt_chain_recheck_expiration_handoff_v204_status_bridge",
    "get_receipt_chain_recheck_expiration_handoff_v204_status_bridge",
    "build_receipt_chain_recheck_expiration_handoff_v204_quick_action",
    "build_receipt_chain_recheck_expiration_handoff_v204_unified_owner_section",
]
