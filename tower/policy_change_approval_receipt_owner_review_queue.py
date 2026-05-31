
"""
PACK 164 - Approval Receipt Owner Review Queue.

This module sits on top of Pack 163.

Pack 163 creates simulated renewal/recheck queue lanes.
Pack 164 converts those lanes into a simulated owner-review queue with
review reasons, required owner actions, review categories, and priority labels.

Important:
- simulated-only
- owner-review-preview-only
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
- no real queue actions
- no real owner review completed
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


PACK_ID = "PACK_164"
APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT = "/tower/policy-change-approval-receipt-owner-review-queue.json"
APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT = "/tower/policy-change-approval-receipt-renewal-recheck-queue.json"


OWNER_REVIEW_CATEGORIES = {
    "critical_owner_recheck": {
        "label": "Critical Owner Recheck",
        "description": "Critical/fail-closed receipts need explicit owner recheck before reuse.",
        "review_priority": "critical",
        "owner_action": "complete_owner_recheck",
        "step_up_required": True,
        "review_required": True,
    },
    "quarantine_owner_recheck": {
        "label": "Quarantine Owner Recheck",
        "description": "Quarantine/containment receipts need owner review before anything moves.",
        "review_priority": "high",
        "owner_action": "complete_quarantine_recheck",
        "step_up_required": True,
        "review_required": True,
    },
    "fresh_recheck_review": {
        "label": "Fresh Recheck Review",
        "description": "Receipts needing a fresh review before renewal can be considered.",
        "review_priority": "high",
        "owner_action": "complete_fresh_recheck",
        "step_up_required": True,
        "review_required": True,
    },
    "renewal_review": {
        "label": "Renewal Review",
        "description": "Receipts eligible for renewal preview after owner review.",
        "review_priority": "medium",
        "owner_action": "review_renewal_preview",
        "step_up_required": False,
        "review_required": True,
    },
    "monitor_acknowledgement": {
        "label": "Monitor Acknowledgement",
        "description": "Monitor-only receipt that can remain low-risk/read-only.",
        "review_priority": "monitor",
        "owner_action": "acknowledge_monitor_only",
        "step_up_required": False,
        "review_required": False,
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


def _load_pack_163_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_renewal_recheck_queue")
        fn = getattr(mod, "build_policy_change_approval_receipt_renewal_recheck_queue_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_163",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "queue_item_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 163 approval receipt renewal/recheck queue unavailable",
            },
            "queue_items": [],
        }

    return {
        "pack_id": "PACK_163",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
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
        "summary": {
            "queue_item_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 163 approval receipt renewal/recheck queue unavailable",
        },
        "queue_items": [],
    }



def _select_owner_review_category(queue_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the simulated owner-review category for one Pack 163 queue item.

    This does not complete review.
    This does not approve anything.
    This only previews the owner-review lane.
    """

    queue_lane = str(queue_item.get("queue_lane") or "").lower()
    renewal_status = str(queue_item.get("renewal_status") or "").lower()
    vault_bucket = str(queue_item.get("vault_bucket") or "").lower()
    priority = str(queue_item.get("priority") or "").lower()
    recommended_action = str(queue_item.get("recommended_action") or "").lower()

    if queue_lane == "owner_recheck_required" and priority == "critical":
        category = "critical_owner_recheck"
        review_reason = "Critical approval receipt requires explicit owner recheck before reuse."

    elif queue_lane == "owner_recheck_required" or vault_bucket == "quarantine_reviews":
        category = "quarantine_owner_recheck"
        review_reason = "Quarantine/high-risk approval receipt requires owner recheck before movement."

    elif queue_lane == "fresh_recheck_required" or recommended_action == "prepare_fresh_recheck":
        category = "fresh_recheck_review"
        review_reason = "Fresh recheck is required before renewal can be considered."

    elif queue_lane == "renewal_eligible_review" or recommended_action == "prepare_renewal_review":
        category = "renewal_review"
        review_reason = "Receipt is eligible for renewal preview after owner review."

    elif queue_lane == "monitor_only_renewal" or recommended_action == "continue_monitor_or_renew_preview":
        category = "monitor_acknowledgement"
        review_reason = "Monitor-only receipt can remain read-only with acknowledgement."

    elif "blocked" in renewal_status:
        category = "fresh_recheck_review"
        review_reason = "Blocked renewal status defaults to fresh recheck review."

    else:
        category = "renewal_review"
        review_reason = "Default owner review category for renewal-safe preview."

    meta = dict(OWNER_REVIEW_CATEGORIES.get(category) or OWNER_REVIEW_CATEGORIES["renewal_review"])

    return {
        "owner_review_category": category,
        "owner_review_label": meta["label"],
        "owner_review_description": meta["description"],
        "owner_review_priority": meta["review_priority"],
        "required_owner_action": meta["owner_action"],
        "owner_step_up_required": bool(meta["step_up_required"]),
        "owner_review_required": bool(meta["review_required"]),
        "owner_review_reason": review_reason,
    }


def _build_owner_review_steps(queue_item: Dict[str, Any], category: Dict[str, Any]) -> List[str]:
    steps: List[str] = []

    if category.get("owner_review_required") is True:
        steps.append("open_owner_review")

    if category.get("owner_step_up_required") is True:
        steps.append("complete_owner_step_up")

    owner_action = str(category.get("required_owner_action") or "")
    if owner_action:
        steps.append(owner_action)

    vault_bucket = str(queue_item.get("vault_bucket") or "")

    if vault_bucket == "privacy_reviews":
        steps.append("confirm_privacy_redaction_context")

    if vault_bucket == "quarantine_reviews":
        steps.append("confirm_quarantine_context")

    if bool(queue_item.get("renewal_candidate")) is True:
        steps.append("review_renewal_preview_only")

    if bool(queue_item.get("fresh_recheck_required")) is True:
        steps.append("review_fresh_recheck_preview_only")

    steps.append("leave_real_actions_disabled")

    # Keep order but remove duplicates.
    deduped: List[str] = []
    for step in steps:
        if step and step not in deduped:
            deduped.append(step)

    return deduped


def _owner_review_soulaana_translation(queue_item: Dict[str, Any], category: Dict[str, Any]) -> str:
    scenario_id = _safe_text(queue_item.get("scenario_id"))
    label = _safe_text(category.get("owner_review_label"))
    action = _safe_text(category.get("required_owner_action"))

    if category.get("owner_review_required") is False:
        return f"{scenario_id}: This goes to {label}. It can be acknowledged as monitor-only, but no real access changes happen."

    return f"{scenario_id}: This goes to {label}. Owner action needed: {action}. The Tower keeps all real actions disabled."


def build_policy_change_approval_receipt_owner_review_queue_item(queue_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 163 renewal/recheck queue item into one simulated owner-review queue item.
    """

    queue_item = dict(queue_item or {})
    category = _select_owner_review_category(queue_item)
    required_steps = _build_owner_review_steps(queue_item, category)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "queue_item_id": queue_item.get("queue_item_id"),
        "scenario_id": queue_item.get("scenario_id"),
        "owner_review_category": category.get("owner_review_category"),
        "required_owner_action": category.get("required_owner_action"),
    }

    owner_review_item_id = f"approval_receipt_owner_review_preview_{_stable_hash(identity, 18)}"

    return {
        "owner_review_item_id": owner_review_item_id,
        "sequence": sequence,
        "queue_item_id": _safe_text(queue_item.get("queue_item_id")),
        "expiration_preview_id": _safe_text(queue_item.get("expiration_preview_id")),
        "vault_preview_id": _safe_text(queue_item.get("vault_preview_id")),
        "ledger_index_id": _safe_text(queue_item.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(queue_item.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(queue_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(queue_item.get("risk_score_id")),
        "recommendation_id": _safe_text(queue_item.get("recommendation_id")),
        "scenario_id": _safe_text(queue_item.get("scenario_id")),
        "matched_policy_id": _safe_text(queue_item.get("matched_policy_id")),
        "decision": _safe_text(queue_item.get("decision")),
        "risk_score": int(queue_item.get("risk_score") or 0),
        "risk_band": _safe_text(queue_item.get("risk_band")),
        "approval_path": _safe_text(queue_item.get("approval_path")),
        "receipt_type": _safe_text(queue_item.get("receipt_type")),
        "receipt_severity": _safe_text(queue_item.get("receipt_severity")),
        "vault_bucket": _safe_text(queue_item.get("vault_bucket")),
        "retention_class": _safe_text(queue_item.get("retention_class")),
        "priority": _safe_text(queue_item.get("priority")),
        "expiration_state": _safe_text(queue_item.get("expiration_state")),
        "queue_lane": _safe_text(queue_item.get("queue_lane")),
        "queue_priority": _safe_text(queue_item.get("queue_priority")),
        "recommended_action": _safe_text(queue_item.get("recommended_action")),
        "renewal_status": _safe_text(queue_item.get("renewal_status")),
        "owner_review_category": category["owner_review_category"],
        "owner_review_label": category["owner_review_label"],
        "owner_review_description": category["owner_review_description"],
        "owner_review_priority": category["owner_review_priority"],
        "required_owner_action": category["required_owner_action"],
        "owner_step_up_required": category["owner_step_up_required"],
        "owner_review_required": category["owner_review_required"],
        "owner_review_reason": category["owner_review_reason"],
        "required_owner_review_steps": required_steps,
        "owner_review_status": "owner_review_pending" if category["owner_review_required"] else "monitor_acknowledgement_pending",
        "owner_review_action_allowed_now": False,
        "owner_step_up_allowed_now": False,
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "soulaana_owner_review_translation": _owner_review_soulaana_translation(queue_item, category),
        "source_endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "simulated_only": True,
        "owner_review_preview_only": True,
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


def _sort_owner_review_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "monitor": 4,
    }
    category_rank = {
        "critical_owner_recheck": 1,
        "quarantine_owner_recheck": 2,
        "fresh_recheck_review": 3,
        "renewal_review": 4,
        "monitor_acknowledgement": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            priority_rank.get(str(item.get("owner_review_priority")), 99),
            category_rank.get(str(item.get("owner_review_category")), 99),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_owner_review_queue_payload_cached() -> Dict[str, Any]:
    pack_163_payload = _load_pack_163_payload(force_refresh=False)
    queue_items = pack_163_payload.get("queue_items", [])

    if not isinstance(queue_items, list):
        queue_items = []

    owner_review_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(queue_items, start=1):
        if isinstance(item, dict):
            owner_review_items.append(build_policy_change_approval_receipt_owner_review_queue_item(item, sequence=idx))

    owner_review_items = _sort_owner_review_items(owner_review_items)

    category_counts = _count_by(owner_review_items, "owner_review_category")
    owner_review_priority_counts = _count_by(owner_review_items, "owner_review_priority")
    required_owner_action_counts = _count_by(owner_review_items, "required_owner_action")
    owner_review_status_counts = _count_by(owner_review_items, "owner_review_status")
    queue_lane_counts = _count_by(owner_review_items, "queue_lane")
    vault_bucket_counts = _count_by(owner_review_items, "vault_bucket")

    by_owner_review_category = _group_by(owner_review_items, "owner_review_category")
    by_owner_review_priority = _group_by(owner_review_items, "owner_review_priority")
    by_required_owner_action = _group_by(owner_review_items, "required_owner_action")
    by_owner_review_status = _group_by(owner_review_items, "owner_review_status")
    by_queue_lane = _group_by(owner_review_items, "queue_lane")
    by_vault_bucket = _group_by(owner_review_items, "vault_bucket")

    critical_owner_recheck = [
        item for item in owner_review_items
        if item.get("owner_review_category") == "critical_owner_recheck"
    ]
    quarantine_owner_recheck = [
        item for item in owner_review_items
        if item.get("owner_review_category") == "quarantine_owner_recheck"
    ]
    fresh_recheck_review = [
        item for item in owner_review_items
        if item.get("owner_review_category") == "fresh_recheck_review"
    ]
    renewal_review = [
        item for item in owner_review_items
        if item.get("owner_review_category") == "renewal_review"
    ]
    monitor_acknowledgement = [
        item for item in owner_review_items
        if item.get("owner_review_category") == "monitor_acknowledgement"
    ]

    owner_review_required_items = [
        item for item in owner_review_items
        if item.get("owner_review_required") is True
    ]
    owner_step_up_required_items = [
        item for item in owner_review_items
        if item.get("owner_step_up_required") is True
    ]
    monitor_acknowledgement_items = [
        item for item in owner_review_items
        if item.get("owner_review_required") is False
    ]

    required_categories = set(OWNER_REVIEW_CATEGORIES.keys())
    observed_categories = set(category_counts.keys())

    required_actions = {
        "complete_owner_recheck",
        "complete_quarantine_recheck",
        "complete_fresh_recheck",
        "review_renewal_preview",
        "acknowledge_monitor_only",
    }
    observed_actions = set(required_owner_action_counts.keys())

    readiness_checks = {
        "pack_163_ready": pack_163_payload.get("status") == "ready",
        "has_owner_review_items": len(owner_review_items) >= 1,
        "owner_review_count_matches_queue_items": len(owner_review_items) == len(queue_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in owner_review_items),
        "all_owner_review_preview_only": all(item.get("owner_review_preview_only") is True for item in owner_review_items),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in owner_review_items),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in owner_review_items),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in owner_review_items),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in owner_review_items),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in owner_review_items),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in owner_review_items),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in owner_review_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in owner_review_items),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in owner_review_items),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in owner_review_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in owner_review_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in owner_review_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in owner_review_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in owner_review_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in owner_review_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in owner_review_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in owner_review_items),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in owner_review_items),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in owner_review_items),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in owner_review_items),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in owner_review_items),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in owner_review_items),
        "no_real_owner_review_completed": all(item.get("real_owner_review_completed") is False for item in owner_review_items),
        "no_real_owner_approval_executed": all(item.get("real_owner_approval_executed") is False for item in owner_review_items),
        "no_real_owner_rejection_executed": all(item.get("real_owner_rejection_executed") is False for item in owner_review_items),
        "no_real_owner_acknowledgement_executed": all(item.get("real_owner_acknowledgement_executed") is False for item in owner_review_items),
        "owner_review_action_never_allowed_now": all(item.get("owner_review_action_allowed_now") is False for item in owner_review_items),
        "owner_step_up_never_allowed_now": all(item.get("owner_step_up_allowed_now") is False for item in owner_review_items),
        "all_owner_review_ids_present": all(bool(item.get("owner_review_item_id")) for item in owner_review_items),
        "all_categories_present": all(bool(item.get("owner_review_category")) for item in owner_review_items),
        "all_required_owner_actions_present": all(bool(item.get("required_owner_action")) for item in owner_review_items),
        "all_required_steps_present": all(isinstance(item.get("required_owner_review_steps"), list) and item.get("required_owner_review_steps") for item in owner_review_items),
        "critical_owner_recheck_present": len(critical_owner_recheck) >= 1,
        "quarantine_owner_recheck_present": len(quarantine_owner_recheck) >= 1,
        "fresh_recheck_review_present": len(fresh_recheck_review) >= 1,
        "renewal_review_present": len(renewal_review) >= 1,
        "monitor_acknowledgement_present": len(monitor_acknowledgement) >= 1,
        "owner_review_required_items_present": len(owner_review_required_items) >= 1,
        "owner_step_up_required_items_present": len(owner_step_up_required_items) >= 1,
        "monitor_acknowledgement_items_present": len(monitor_acknowledgement_items) >= 1,
        "required_category_coverage": required_categories.issubset(observed_categories),
        "required_action_coverage": required_actions.issubset(observed_actions),
        "endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
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
        "pack_number": 164,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Approval Receipt Owner Review Queue",
        "endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "owner_review_preview_only": True,
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
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "cached_non_recursive": True,
        "source_pack_163": {
            "status": pack_163_payload.get("status"),
            "readiness_score": pack_163_payload.get("summary", {}).get("readiness_score"),
            "queue_item_count": pack_163_payload.get("summary", {}).get("queue_item_count"),
            "lane_counts": pack_163_payload.get("summary", {}).get("lane_counts", {}),
            "recommended_action_counts": pack_163_payload.get("summary", {}).get("recommended_action_counts", {}),
        },
        "summary": {
            "owner_review_item_count": len(owner_review_items),
            "critical_owner_recheck_count": len(critical_owner_recheck),
            "quarantine_owner_recheck_count": len(quarantine_owner_recheck),
            "fresh_recheck_review_count": len(fresh_recheck_review),
            "renewal_review_count": len(renewal_review),
            "monitor_acknowledgement_count": len(monitor_acknowledgement),
            "owner_review_required_count": len(owner_review_required_items),
            "owner_step_up_required_count": len(owner_step_up_required_items),
            "monitor_acknowledgement_item_count": len(monitor_acknowledgement_items),
            "category_counts": category_counts,
            "owner_review_priority_counts": owner_review_priority_counts,
            "required_owner_action_counts": required_owner_action_counts,
            "owner_review_status_counts": owner_review_status_counts,
            "queue_lane_counts": queue_lane_counts,
            "vault_bucket_counts": vault_bucket_counts,
            "observed_categories": sorted(observed_categories),
            "required_categories": sorted(required_categories),
            "observed_actions": sorted(observed_actions),
            "required_actions": sorted(required_actions),
            "readiness_score": readiness_score,
            "readiness_label": "Approval receipt owner review queue ready" if readiness_score == 100 else "Approval receipt owner review queue needs review",
        },
        "readiness_checks": readiness_checks,
        "owner_review_items": owner_review_items,
        "indexes": {
            "by_owner_review_category": by_owner_review_category,
            "by_owner_review_priority": by_owner_review_priority,
            "by_required_owner_action": by_required_owner_action,
            "by_owner_review_status": by_owner_review_status,
            "by_queue_lane": by_queue_lane,
            "by_vault_bucket": by_vault_bucket,
        },
        "critical_owner_recheck": critical_owner_recheck,
        "quarantine_owner_recheck": quarantine_owner_recheck,
        "fresh_recheck_review": fresh_recheck_review,
        "renewal_review": renewal_review,
        "monitor_acknowledgement": monitor_acknowledgement,
        "owner_review_required_items": owner_review_required_items,
        "owner_step_up_required_items": owner_step_up_required_items,
        "monitor_acknowledgement_items": monitor_acknowledgement_items,
        "quick_action": {
            "id": "policy_change_approval_receipt_owner_review_queue",
            "label": "Approval Receipt Owner Review",
            "href": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
            "description": "Preview owner review lanes for approval receipt renewal/recheck items.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_owner_review_queue",
            "title": "Approval Receipt Owner Review",
            "subtitle": "Previews owner-review decisions before any real approval, rejection, recheck, renewal, or enforcement happens.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_owner_review_queue_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_owner_review_queue_payload_cached())


def get_policy_change_approval_receipt_owner_review_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_owner_review_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_review_queue_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 164,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Approval receipt owner review queue ready"),
        "owner_review_item_count": summary.get("owner_review_item_count", 0),
        "critical_owner_recheck_count": summary.get("critical_owner_recheck_count", 0),
        "quarantine_owner_recheck_count": summary.get("quarantine_owner_recheck_count", 0),
        "fresh_recheck_review_count": summary.get("fresh_recheck_review_count", 0),
        "renewal_review_count": summary.get("renewal_review_count", 0),
        "monitor_acknowledgement_count": summary.get("monitor_acknowledgement_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "owner_step_up_required_count": summary.get("owner_step_up_required_count", 0),
        "monitor_acknowledgement_item_count": summary.get("monitor_acknowledgement_item_count", 0),
        "category_counts": summary.get("category_counts", {}),
        "owner_review_priority_counts": summary.get("owner_review_priority_counts", {}),
        "required_owner_action_counts": summary.get("required_owner_action_counts", {}),
        "owner_review_status_counts": summary.get("owner_review_status_counts", {}),
        "simulated_only": True,
        "owner_review_preview_only": True,
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
        "real_owner_review_completed": False,
        "real_owner_approval_executed": False,
        "real_owner_rejection_executed": False,
        "real_owner_acknowledgement_executed": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_owner_review_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_owner_review_queue_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_owner_review_queue_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_owner_review_queue_status_bridge()
    return {
        "id": "policy_change_approval_receipt_owner_review_queue",
        "label": "Approval Receipt Owner Review",
        "title": "Approval Receipt Owner Review Queue",
        "href": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "description": "Preview owner-review lanes for approval receipt renewal/recheck items.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 164",
        "category": "policy",
        "simulated_only": True,
        "owner_review_preview_only": True,
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


def build_policy_change_approval_receipt_owner_review_queue_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_owner_review_queue_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "owner_review_readiness",
            "title": "Owner review readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Approval receipt owner review queue ready"),
        },
        {
            "id": "owner_review_items",
            "title": "Owner review items",
            "value": summary.get("owner_review_item_count", 0),
            "label": "Queue items mapped to owner-review lanes",
        },
        {
            "id": "critical_owner_recheck",
            "title": "Critical recheck",
            "value": summary.get("critical_owner_recheck_count", 0),
            "label": "Critical owner recheck items",
        },
        {
            "id": "fresh_recheck_review",
            "title": "Fresh recheck",
            "value": summary.get("fresh_recheck_review_count", 0),
            "label": "Fresh recheck review items",
        },
        {
            "id": "renewal_review",
            "title": "Renewal review",
            "value": summary.get("renewal_review_count", 0),
            "label": "Renewal-preview review items",
        },
        {
            "id": "no_real_owner_review",
            "title": "Real owner review",
            "value": "No" if checks.get("no_real_owner_review_completed") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_owner_review_queue",
        "title": "Approval Receipt Owner Review",
        "subtitle": "Previews owner-review decisions before any real approval, rejection, recheck, renewal, or enforcement happens.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "owner_review_preview_only": True,
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


def build_policy_change_approval_receipt_owner_review_queue_html_section() -> str:
    section = build_policy_change_approval_receipt_owner_review_queue_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-owner-review-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-owner-review-section" id="policy-change-approval-receipt-owner-review-queue">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 164</p>
            <h2>{section.get('title', 'Approval Receipt Owner Review')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT}">Open approval receipt owner review JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT",
    "APPROVAL_RECEIPT_RENEWAL_RECHECK_ENDPOINT",
    "OWNER_REVIEW_CATEGORIES",
    "build_policy_change_approval_receipt_owner_review_queue_item",
    "build_policy_change_approval_receipt_owner_review_queue_payload",
    "get_policy_change_approval_receipt_owner_review_queue_payload",
    "build_policy_change_approval_receipt_owner_review_queue_status_bridge",
    "get_policy_change_approval_receipt_owner_review_queue_status_bridge",
    "build_policy_change_approval_receipt_owner_review_queue_quick_action",
    "build_policy_change_approval_receipt_owner_review_queue_unified_owner_section",
    "build_policy_change_approval_receipt_owner_review_queue_html_section",
]
