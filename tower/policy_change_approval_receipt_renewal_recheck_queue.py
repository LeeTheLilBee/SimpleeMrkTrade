
"""
PACK 163 - Approval Receipt Renewal / Recheck Queue.

This module sits on top of Pack 162.

Pack 162 assigns simulated expiration, renewal, and recheck windows.
Pack 163 turns those expiration items into a simulated renewal/recheck queue.

Important:
- simulated-only
- queue-preview-only
- renewal-preview-only
- recheck-preview-only
- expiration-preview-only
- vault-preview-only
- index-preview-only
- receipt-preview-only
- approval-preview-only
- evidence-preview-only
- no real approvals executed
- no real policy changes
- no real permission changes
- no real access grants
- no real enforcement
- no real audit writes
- no real receipt writes
- no real archive writes
- no real vault writes
- no real expiration enforcement
- no real rechecks
- no real renewals
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


PACK_ID = "PACK_163"
APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT = "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"
APPROVAL_RECEIPT_EXPIRATION_ENDPOINT = "/tower/policy-change-approval-receipt-expiration-rules.json"


QUEUE_LANES = {
    "owner_recheck_required": {
        "label": "Owner Recheck Required",
        "description": "Expired or fast-expiring items that cannot renew automatically.",
        "queue_priority": "critical",
        "owner_review_required": True,
        "fresh_recheck_required": True,
        "renewal_candidate": False,
    },
    "fresh_recheck_required": {
        "label": "Fresh Recheck Required",
        "description": "Items needing a fresh review before reuse.",
        "queue_priority": "high",
        "owner_review_required": True,
        "fresh_recheck_required": True,
        "renewal_candidate": False,
    },
    "renewal_eligible_review": {
        "label": "Renewal Eligible Review",
        "description": "Items that may be renewed after owner review.",
        "queue_priority": "medium",
        "owner_review_required": True,
        "fresh_recheck_required": False,
        "renewal_candidate": True,
    },
    "monitor_only_renewal": {
        "label": "Monitor-Only Renewal",
        "description": "Monitor-only items that may stay low-risk and read-only.",
        "queue_priority": "monitor",
        "owner_review_required": False,
        "fresh_recheck_required": False,
        "renewal_candidate": True,
    },
}


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
    forbidden_fragments = [
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
    lowered = text.lower()
    for fragment in forbidden_fragments:
        if fragment in lowered:
            return "[REDACTED]"
    return text


def _load_pack_162_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_expiration_rules")
        fn = getattr(mod, "build_policy_change_approval_receipt_expiration_rules_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_162",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
            "simulated_only": True,
            "expiration_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "expiration_item_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 162 approval receipt expiration payload unavailable",
            },
            "expiration_items": [],
        }

    return {
        "pack_id": "PACK_162",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "summary": {
            "expiration_item_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 162 approval receipt expiration payload unavailable",
        },
        "expiration_items": [],
    }


def _select_queue_lane(expiration_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the simulated renewal/recheck queue lane.

    This does not renew anything.
    This does not recheck anything.
    This only previews where the item belongs in the queue.
    """

    expiration_state = str(expiration_item.get("expiration_state") or "").lower()
    priority = str(expiration_item.get("priority") or "").lower()
    vault_bucket = str(expiration_item.get("vault_bucket") or "").lower()
    recheck_required = bool(expiration_item.get("recheck_required", False))
    renewal_allowed = bool(expiration_item.get("renewal_allowed", False))

    if expiration_state == "expires_fast_recheck_required" or priority == "critical":
        lane = "owner_recheck_required"
        recommended_action = "owner_recheck_before_reuse"
        renewal_status = "renewal_blocked_owner_recheck_required"
        queue_reason = "Critical expiration items cannot renew automatically and require owner recheck."

    elif expiration_state == "expires_soon_recheck_required" or priority == "high" or vault_bucket == "quarantine_reviews":
        lane = "owner_recheck_required"
        recommended_action = "owner_recheck_before_reuse"
        renewal_status = "renewal_blocked_quarantine_recheck_required"
        queue_reason = "High/quarantine items must be rechecked by owner before reuse."

    elif recheck_required is True:
        lane = "fresh_recheck_required"
        recommended_action = "prepare_fresh_recheck"
        renewal_status = "renewal_blocked_fresh_recheck_required"
        queue_reason = "This item requires a fresh recheck before renewal can be considered."

    elif renewal_allowed is True and priority == "monitor":
        lane = "monitor_only_renewal"
        recommended_action = "continue_monitor_or_renew_preview"
        renewal_status = "monitor_renewal_preview_allowed"
        queue_reason = "Monitor-only items may stay low-risk and read-only with preview renewal."

    elif renewal_allowed is True:
        lane = "renewal_eligible_review"
        recommended_action = "prepare_renewal_review"
        renewal_status = "renewal_preview_allowed_after_review"
        queue_reason = "This item may be renewed after owner review."

    else:
        lane = "fresh_recheck_required"
        recommended_action = "prepare_fresh_recheck"
        renewal_status = "renewal_blocked_recheck_required"
        queue_reason = "Unknown or blocked state defaults to fresh recheck."

    meta = dict(QUEUE_LANES.get(lane) or QUEUE_LANES["fresh_recheck_required"])

    return {
        "queue_lane": lane,
        "queue_lane_label": meta["label"],
        "queue_lane_description": meta["description"],
        "queue_priority": meta["queue_priority"],
        "queue_owner_review_required": bool(meta["owner_review_required"]),
        "fresh_recheck_required": bool(meta["fresh_recheck_required"]),
        "renewal_candidate": bool(meta["renewal_candidate"]),
        "recommended_action": recommended_action,
        "renewal_status": renewal_status,
        "queue_reason": queue_reason,
    }


def _build_required_queue_steps(expiration_item: Dict[str, Any], lane: Dict[str, Any]) -> List[str]:
    steps: List[str] = []

    if lane.get("queue_owner_review_required") is True:
        steps.append("owner_review")

    if lane.get("fresh_recheck_required") is True:
        steps.append("fresh_recheck")

    if str(expiration_item.get("vault_bucket") or "") == "privacy_reviews":
        steps.append("privacy_review")

    if str(expiration_item.get("vault_bucket") or "") == "quarantine_reviews":
        steps.append("quarantine_review")

    if lane.get("renewal_candidate") is True:
        steps.append("renewal_preview")

    if not steps:
        steps.append("monitor_acknowledgement")

    return steps


def _queue_soulaana_translation(expiration_item: Dict[str, Any], lane: Dict[str, Any]) -> str:
    scenario_id = _safe_text(expiration_item.get("scenario_id"))
    queue_lane = str(lane.get("queue_lane") or "")

    if queue_lane == "owner_recheck_required":
        return f"{scenario_id}: This approval receipt goes to owner recheck. No renewal can happen until review is complete."
    if queue_lane == "fresh_recheck_required":
        return f"{scenario_id}: This approval receipt needs a fresh recheck before renewal can even be considered."
    if queue_lane == "renewal_eligible_review":
        return f"{scenario_id}: This approval receipt can enter renewal review, but nothing renews for real yet."
    if queue_lane == "monitor_only_renewal":
        return f"{scenario_id}: This approval receipt can stay monitor-only or renew as a preview without adding access."
    return f"{scenario_id}: This approval receipt goes to the safest recheck lane."


def build_policy_change_approval_receipt_renewal_recheck_queue_item(expiration_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 162 approval receipt expiration item into one simulated
    renewal/recheck queue item.
    """

    expiration_item = dict(expiration_item or {})
    lane = _select_queue_lane(expiration_item)
    required_steps = _build_required_queue_steps(expiration_item, lane)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "expiration_preview_id": expiration_item.get("expiration_preview_id"),
        "vault_preview_id": expiration_item.get("vault_preview_id"),
        "scenario_id": expiration_item.get("scenario_id"),
        "queue_lane": lane.get("queue_lane"),
        "renewal_status": lane.get("renewal_status"),
    }

    queue_item_id = f"approval_receipt_queue_preview_{_stable_hash(identity, 18)}"

    return {
        "queue_item_id": queue_item_id,
        "sequence": sequence,
        "expiration_preview_id": _safe_text(expiration_item.get("expiration_preview_id")),
        "vault_preview_id": _safe_text(expiration_item.get("vault_preview_id")),
        "ledger_index_id": _safe_text(expiration_item.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(expiration_item.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(expiration_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(expiration_item.get("risk_score_id")),
        "recommendation_id": _safe_text(expiration_item.get("recommendation_id")),
        "scenario_id": _safe_text(expiration_item.get("scenario_id")),
        "matched_policy_id": _safe_text(expiration_item.get("matched_policy_id")),
        "decision": _safe_text(expiration_item.get("decision")),
        "risk_score": int(expiration_item.get("risk_score") or 0),
        "risk_band": _safe_text(expiration_item.get("risk_band")),
        "approval_path": _safe_text(expiration_item.get("approval_path")),
        "receipt_type": _safe_text(expiration_item.get("receipt_type")),
        "receipt_severity": _safe_text(expiration_item.get("receipt_severity")),
        "vault_bucket": _safe_text(expiration_item.get("vault_bucket")),
        "retention_class": _safe_text(expiration_item.get("retention_class")),
        "priority": _safe_text(expiration_item.get("priority")),
        "expiration_state": _safe_text(expiration_item.get("expiration_state")),
        "ttl_hours": int(expiration_item.get("ttl_hours") or 0),
        "warning_hours": int(expiration_item.get("warning_hours") or 0),
        "created_at": _safe_text(expiration_item.get("created_at")),
        "warning_at": _safe_text(expiration_item.get("warning_at")),
        "expires_at": _safe_text(expiration_item.get("expires_at")),
        "queue_lane": lane["queue_lane"],
        "queue_lane_label": lane["queue_lane_label"],
        "queue_lane_description": lane["queue_lane_description"],
        "queue_priority": lane["queue_priority"],
        "queue_owner_review_required": lane["queue_owner_review_required"],
        "fresh_recheck_required": lane["fresh_recheck_required"],
        "renewal_candidate": lane["renewal_candidate"],
        "recommended_action": lane["recommended_action"],
        "renewal_status": lane["renewal_status"],
        "queue_reason": lane["queue_reason"],
        "required_queue_steps": required_steps,
        "renewal_allowed_by_rule": bool(expiration_item.get("renewal_allowed", False)),
        "recheck_required_by_rule": bool(expiration_item.get("recheck_required", False)),
        "owner_review_required_by_rule": bool(expiration_item.get("owner_review_required", False)),
        "queue_action_allowed_now": False,
        "real_recheck_allowed_now": False,
        "real_renewal_allowed_now": False,
        "real_queue_action_executed": False,
        "soulaana_queue_translation": _queue_soulaana_translation(expiration_item, lane),
        "source_endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "simulated_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
    }



def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        group_key = str(item.get(key) or "unknown")
        counts[group_key] = counts.get(group_key, 0) + 1
    return counts


def _group_by(items: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        group_key = str(item.get(key) or "unknown")
        grouped.setdefault(group_key, []).append(item)
    return grouped


def _sort_queue_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    lane_rank = {
        "owner_recheck_required": 1,
        "fresh_recheck_required": 2,
        "renewal_eligible_review": 3,
        "monitor_only_renewal": 4,
    }
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "monitor": 4,
    }
    return sorted(
        items,
        key=lambda item: (
            lane_rank.get(str(item.get("queue_lane")), 99),
            priority_rank.get(str(item.get("queue_priority")), 99),
            int(item.get("ttl_hours") or 999999),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_renewal_recheck_queue_payload_cached() -> Dict[str, Any]:
    pack_162_payload = _load_pack_162_payload(force_refresh=False)
    expiration_items = pack_162_payload.get("expiration_items", [])

    if not isinstance(expiration_items, list):
        expiration_items = []

    queue_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(expiration_items, start=1):
        if isinstance(item, dict):
            queue_items.append(build_policy_change_approval_receipt_renewal_recheck_queue_item(item, sequence=idx))

    queue_items = _sort_queue_items(queue_items)

    lane_counts = _count_by(queue_items, "queue_lane")
    queue_priority_counts = _count_by(queue_items, "queue_priority")
    renewal_status_counts = _count_by(queue_items, "renewal_status")
    recommended_action_counts = _count_by(queue_items, "recommended_action")
    vault_bucket_counts = _count_by(queue_items, "vault_bucket")
    expiration_state_counts = _count_by(queue_items, "expiration_state")
    receipt_type_counts = _count_by(queue_items, "receipt_type")

    by_queue_lane = _group_by(queue_items, "queue_lane")
    by_queue_priority = _group_by(queue_items, "queue_priority")
    by_renewal_status = _group_by(queue_items, "renewal_status")
    by_recommended_action = _group_by(queue_items, "recommended_action")
    by_vault_bucket = _group_by(queue_items, "vault_bucket")
    by_expiration_state = _group_by(queue_items, "expiration_state")
    by_receipt_type = _group_by(queue_items, "receipt_type")

    owner_recheck_required = [
        item for item in queue_items
        if item.get("queue_lane") == "owner_recheck_required"
    ]
    fresh_recheck_required = [
        item for item in queue_items
        if item.get("queue_lane") == "fresh_recheck_required"
    ]
    renewal_eligible_review = [
        item for item in queue_items
        if item.get("queue_lane") == "renewal_eligible_review"
    ]
    monitor_only_renewal = [
        item for item in queue_items
        if item.get("queue_lane") == "monitor_only_renewal"
    ]

    owner_review_required_items = [
        item for item in queue_items
        if item.get("queue_owner_review_required") is True
    ]
    fresh_recheck_items = [
        item for item in queue_items
        if item.get("fresh_recheck_required") is True
    ]
    renewal_candidate_items = [
        item for item in queue_items
        if item.get("renewal_candidate") is True
    ]

    required_lanes = set(QUEUE_LANES.keys())
    observed_lanes = set(lane_counts.keys())

    required_actions = {
        "owner_recheck_before_reuse",
        "prepare_fresh_recheck",
        "prepare_renewal_review",
        "continue_monitor_or_renew_preview",
    }
    observed_actions = set(recommended_action_counts.keys())

    readiness_checks = {
        "pack_162_ready": pack_162_payload.get("status") == "ready",
        "has_queue_items": len(queue_items) >= 1,
        "queue_count_matches_expiration_items": len(queue_items) == len(expiration_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in queue_items),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in queue_items),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in queue_items),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in queue_items),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in queue_items),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in queue_items),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in queue_items),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in queue_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in queue_items),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in queue_items),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in queue_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in queue_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in queue_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in queue_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in queue_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in queue_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in queue_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in queue_items),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in queue_items),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in queue_items),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in queue_items),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in queue_items),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in queue_items),
        "queue_action_never_allowed_now": all(item.get("queue_action_allowed_now") is False for item in queue_items),
        "real_recheck_never_allowed_now": all(item.get("real_recheck_allowed_now") is False for item in queue_items),
        "real_renewal_never_allowed_now": all(item.get("real_renewal_allowed_now") is False for item in queue_items),
        "all_queue_ids_present": all(bool(item.get("queue_item_id")) for item in queue_items),
        "all_lanes_present": all(bool(item.get("queue_lane")) for item in queue_items),
        "all_recommended_actions_present": all(bool(item.get("recommended_action")) for item in queue_items),
        "all_required_steps_present": all(isinstance(item.get("required_queue_steps"), list) and item.get("required_queue_steps") for item in queue_items),
        "owner_recheck_required_present": len(owner_recheck_required) >= 1,
        "fresh_recheck_required_present": len(fresh_recheck_required) >= 1,
        "renewal_eligible_review_present": len(renewal_eligible_review) >= 1,
        "monitor_only_renewal_present": len(monitor_only_renewal) >= 1,
        "owner_review_required_items_present": len(owner_review_required_items) >= 1,
        "fresh_recheck_items_present": len(fresh_recheck_items) >= 1,
        "renewal_candidate_items_present": len(renewal_candidate_items) >= 1,
        "required_lane_coverage": required_lanes.issubset(observed_lanes),
        "required_action_coverage": required_actions.issubset(observed_actions),
        "endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "cached_non_recursive": True,
    }

    bool_checks = [
        value
        for value in readiness_checks.values()
        if isinstance(value, bool)
    ]
    readiness_score = 100 if all(bool_checks) else 90

    return {
        "pack_id": PACK_ID,
        "pack_number": 163,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Approval Receipt Renewal / Recheck Queue",
        "endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "cached_non_recursive": True,
        "source_pack_162": {
            "status": pack_162_payload.get("status"),
            "readiness_score": pack_162_payload.get("summary", {}).get("readiness_score"),
            "expiration_item_count": pack_162_payload.get("summary", {}).get("expiration_item_count"),
            "expiration_state_counts": pack_162_payload.get("summary", {}).get("expiration_state_counts", {}),
            "priority_counts": pack_162_payload.get("summary", {}).get("priority_counts", {}),
        },
        "summary": {
            "queue_item_count": len(queue_items),
            "owner_recheck_required_count": len(owner_recheck_required),
            "fresh_recheck_required_count": len(fresh_recheck_required),
            "renewal_eligible_review_count": len(renewal_eligible_review),
            "monitor_only_renewal_count": len(monitor_only_renewal),
            "owner_review_required_count": len(owner_review_required_items),
            "fresh_recheck_item_count": len(fresh_recheck_items),
            "renewal_candidate_count": len(renewal_candidate_items),
            "lane_counts": lane_counts,
            "queue_priority_counts": queue_priority_counts,
            "renewal_status_counts": renewal_status_counts,
            "recommended_action_counts": recommended_action_counts,
            "vault_bucket_counts": vault_bucket_counts,
            "expiration_state_counts": expiration_state_counts,
            "receipt_type_counts": receipt_type_counts,
            "observed_lanes": sorted(observed_lanes),
            "required_lanes": sorted(required_lanes),
            "observed_actions": sorted(observed_actions),
            "required_actions": sorted(required_actions),
            "readiness_score": readiness_score,
            "readiness_label": "Approval receipt renewal/recheck queue ready" if readiness_score == 100 else "Approval receipt renewal/recheck queue needs review",
        },
        "readiness_checks": readiness_checks,
        "queue_items": queue_items,
        "indexes": {
            "by_queue_lane": by_queue_lane,
            "by_queue_priority": by_queue_priority,
            "by_renewal_status": by_renewal_status,
            "by_recommended_action": by_recommended_action,
            "by_vault_bucket": by_vault_bucket,
            "by_expiration_state": by_expiration_state,
            "by_receipt_type": by_receipt_type,
        },
        "owner_recheck_required": owner_recheck_required,
        "fresh_recheck_required": fresh_recheck_required,
        "renewal_eligible_review": renewal_eligible_review,
        "monitor_only_renewal": monitor_only_renewal,
        "owner_review_required_items": owner_review_required_items,
        "fresh_recheck_items": fresh_recheck_items,
        "renewal_candidate_items": renewal_candidate_items,
        "quick_action": {
            "id": "policy_change_approval_receipt_renewal_recheck_queue",
            "label": "Approval Receipt Renewal Queue",
            "href": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
            "description": "Preview renewal and recheck queue lanes for approval receipt expiration items.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_renewal_recheck_queue",
            "title": "Approval Receipt Renewal Queue",
            "subtitle": "Previews renewal and recheck queues before any real renewal or recheck happens.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_renewal_recheck_queue_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_renewal_recheck_queue_payload_cached())


def get_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_renewal_recheck_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_renewal_recheck_queue_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 163,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_EXPIRATION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Approval receipt renewal/recheck queue ready"),
        "queue_item_count": summary.get("queue_item_count", 0),
        "owner_recheck_required_count": summary.get("owner_recheck_required_count", 0),
        "fresh_recheck_required_count": summary.get("fresh_recheck_required_count", 0),
        "renewal_eligible_review_count": summary.get("renewal_eligible_review_count", 0),
        "monitor_only_renewal_count": summary.get("monitor_only_renewal_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "fresh_recheck_item_count": summary.get("fresh_recheck_item_count", 0),
        "renewal_candidate_count": summary.get("renewal_candidate_count", 0),
        "lane_counts": summary.get("lane_counts", {}),
        "queue_priority_counts": summary.get("queue_priority_counts", {}),
        "renewal_status_counts": summary.get("renewal_status_counts", {}),
        "recommended_action_counts": summary.get("recommended_action_counts", {}),
        "simulated_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "real_approval_executed": False,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "real_archive_written": False,
        "real_vault_written": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "real_queue_action_executed": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_renewal_recheck_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_renewal_recheck_queue_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_renewal_recheck_queue_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_renewal_recheck_queue_status_bridge()
    return {
        "id": "policy_change_approval_receipt_renewal_recheck_queue",
        "label": "Approval Receipt Renewal Queue",
        "title": "Approval Receipt Renewal / Recheck Queue",
        "href": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "description": "Preview renewal and recheck queue lanes for approval receipt expiration items.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 163",
        "category": "policy",
        "simulated_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_renewal_recheck_queue_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "renewal_queue_readiness",
            "title": "Queue readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Approval receipt renewal/recheck queue ready"),
        },
        {
            "id": "queue_items",
            "title": "Queue items",
            "value": summary.get("queue_item_count", 0),
            "label": "Expiration items mapped to queue lanes",
        },
        {
            "id": "owner_recheck_required",
            "title": "Owner recheck",
            "value": summary.get("owner_recheck_required_count", 0),
            "label": "Critical/high items blocked until recheck",
        },
        {
            "id": "fresh_recheck_required",
            "title": "Fresh recheck",
            "value": summary.get("fresh_recheck_required_count", 0),
            "label": "Needs fresh review before renewal",
        },
        {
            "id": "renewal_candidates",
            "title": "Renewal candidates",
            "value": summary.get("renewal_candidate_count", 0),
            "label": "Preview renewal only",
        },
        {
            "id": "no_real_queue_action",
            "title": "Real queue actions",
            "value": "No" if checks.get("no_real_queue_action_executed") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_renewal_recheck_queue",
        "title": "Approval Receipt Renewal Queue",
        "subtitle": "Previews renewal and recheck queues before any real renewal, recheck, or enforcement happens.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "queue_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "expiration_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_renewal_recheck_queue_html_section() -> str:
    section = build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-renewal-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-renewal-section" id="policy-change-approval-receipt-renewal-recheck-queue">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 163</p>
            <h2>{section.get('title', 'Approval Receipt Renewal Queue')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT}">Open approval receipt renewal queue JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT",
    "APPROVAL_RECEIPT_EXPIRATION_ENDPOINT",
    "QUEUE_LANES",
    "build_policy_change_approval_receipt_renewal_recheck_queue_item",
    "build_policy_change_approval_receipt_renewal_recheck_queue_payload",
    "get_policy_change_approval_receipt_renewal_recheck_queue_payload",
    "build_policy_change_approval_receipt_renewal_recheck_queue_status_bridge",
    "get_policy_change_approval_receipt_renewal_recheck_queue_status_bridge",
    "build_policy_change_approval_receipt_renewal_recheck_queue_quick_action",
    "build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section",
    "build_policy_change_approval_receipt_renewal_recheck_queue_html_section",
]
