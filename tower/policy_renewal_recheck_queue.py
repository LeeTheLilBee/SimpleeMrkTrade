
"""
PACK 156 - Policy Renewal / Recheck Queue foundation.

This layer sits on top of Pack 155.

Pack 155 says whether a simulated policy receipt entry is fresh, warning, or expired.
Pack 156 turns that into a simulated queue of renewal/recheck work.

Important:
- no real renewal
- no real recheck execution
- no real expiration enforcement
- no real receipt write
- no real audit write
- no real access mutation
- cached
- non-recursive
- does not call unified owner page builders
- does not call quick-action builders
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "PACK_156"
RENEWAL_QUEUE_ENDPOINT = "/tower/policy-renewal-recheck-queue.json"
EXPIRATION_ENDPOINT = "/tower/policy-expiration-rules.json"


PRIORITY_RANK = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "monitor": 5,
}


STATE_RANK = {
    "expired": 1,
    "warning": 2,
    "fresh": 3,
}


SEVERITY_RANK = {
    "critical_safety": 1,
    "containment": 2,
    "blocked": 3,
    "challenge": 4,
    "privacy": 5,
    "monitor": 6,
    "review": 7,
}


def _utc_now_dt() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(microsecond=0)


def _utc_now() -> str:
    return _utc_now_dt().isoformat() + "Z"


def _iso(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"


def _stable_hash(value: Any, length: int = 18) -> str:
    raw = repr(value).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:length]


def _safe_text(value: Any) -> str:
    text = str(value or "")
    forbidden_fragments = [
        "sk-",
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


def _load_pack_155_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_expiration_rules")
        fn = getattr(mod, "build_policy_expiration_rules_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_155",
            "status": "review",
            "endpoint": EXPIRATION_ENDPOINT,
            "simulated_only": True,
            "real_expiration_enforced": False,
            "real_enforcement_executed": False,
            "real_audit_written": False,
            "real_receipt_written": False,
            "load_error": str(exc),
            "summary": {
                "expiration_entry_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 155 expiration payload unavailable",
            },
            "expiration_entries": [],
        }

    return {
        "pack_id": "PACK_155",
        "status": "review",
        "endpoint": EXPIRATION_ENDPOINT,
        "simulated_only": True,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "summary": {
            "expiration_entry_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 155 expiration payload unavailable",
        },
        "expiration_entries": [],
    }


def _priority_for_entry(entry: Dict[str, Any]) -> str:
    state = str(entry.get("expiration_state") or "")
    severity = str(entry.get("severity") or "")

    if state == "expired" and severity == "critical_safety":
        return "critical"
    if state == "expired":
        return "high"
    if state == "warning" and severity in {"blocked", "challenge", "containment"}:
        return "medium"
    if state == "warning":
        return "low"
    return "monitor"


def _queue_lane_for_entry(entry: Dict[str, Any]) -> str:
    state = str(entry.get("expiration_state") or "")
    renewal_allowed = bool(entry.get("renewal_allowed", False))
    decision = str(entry.get("decision") or "")

    if state == "expired" and not renewal_allowed:
        return "owner_recheck_required"
    if state == "expired" and renewal_allowed:
        return "renewal_review_required"
    if state == "warning" and renewal_allowed:
        return "renewal_eligible_review_soon"
    if state == "warning" and not renewal_allowed:
        return "recheck_required_soon"
    if state == "fresh" and decision == "allow":
        return "monitor_only_no_action"
    return "fresh_monitoring"


def _recommended_action_for_entry(entry: Dict[str, Any]) -> str:
    lane = _queue_lane_for_entry(entry)

    if lane == "owner_recheck_required":
        return "owner_recheck_before_reuse"
    if lane == "renewal_review_required":
        return "owner_decide_renew_or_keep_stale"
    if lane == "renewal_eligible_review_soon":
        return "prepare_renewal_review"
    if lane == "recheck_required_soon":
        return "prepare_recheck"
    if lane == "monitor_only_no_action":
        return "continue_monitoring"
    return "continue_monitoring"


def _renewal_status_for_entry(entry: Dict[str, Any]) -> str:
    state = str(entry.get("expiration_state") or "")
    renewal_allowed = bool(entry.get("renewal_allowed", False))

    if state == "expired" and renewal_allowed:
        return "renewal_available_but_requires_owner_review"
    if state == "expired" and not renewal_allowed:
        return "renewal_blocked_recheck_required"
    if state == "warning" and renewal_allowed:
        return "renewal_available_soon"
    if state == "warning" and not renewal_allowed:
        return "renewal_blocked_warning_recheck_required"
    if state == "fresh" and renewal_allowed:
        return "not_due_renewal_allowed_later"
    return "not_due_monitor_only"


def _owner_prompt_for_entry(entry: Dict[str, Any]) -> str:
    lane = _queue_lane_for_entry(entry)
    scenario_id = _safe_text(entry.get("scenario_id"))
    decision = _safe_text(entry.get("decision"))
    bucket = _safe_text(entry.get("bucket"))

    if lane == "owner_recheck_required":
        return f"Review {scenario_id}: this {decision} item in {bucket} is expired and cannot be renewed automatically."
    if lane == "renewal_review_required":
        return f"Review {scenario_id}: this expired {decision} item can be renewed only if owner confirms the reason still applies."
    if lane == "renewal_eligible_review_soon":
        return f"Check {scenario_id}: this {decision} item is close to expiring and can be renewed after owner review."
    if lane == "recheck_required_soon":
        return f"Check {scenario_id}: this {decision} item is close to expiring and needs a fresh recheck, not renewal."
    return f"Monitor {scenario_id}: no renewal or recheck is needed yet."


def _soulaana_queue_translation(entry: Dict[str, Any]) -> str:
    lane = _queue_lane_for_entry(entry)
    if lane == "owner_recheck_required":
        return "This one is expired and too sensitive to recycle. The Tower should make the owner look at it again."
    if lane == "renewal_review_required":
        return "This one is expired, but renewal may be allowed if the owner confirms the reason still holds."
    if lane == "renewal_eligible_review_soon":
        return "This one is getting stale. The Tower can prepare it for renewal review before it expires."
    if lane == "recheck_required_soon":
        return "This one is getting stale, but it cannot be renewed. It needs a fresh recheck soon."
    if lane == "monitor_only_no_action":
        return "This one is still fresh and only monitor-level. No action needed right now."
    return "This one is still fresh. The Tower can keep watching it."


def build_recheck_queue_item_from_expiration_entry(entry: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 155 expiration entry into a simulated renewal/recheck item.
    """

    entry = dict(entry or {})
    priority = _priority_for_entry(entry)
    lane = _queue_lane_for_entry(entry)
    recommended_action = _recommended_action_for_entry(entry)
    renewal_status = _renewal_status_for_entry(entry)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "expiration_check_id": entry.get("expiration_check_id"),
        "vault_entry_id": entry.get("vault_entry_id"),
        "ledger_entry_id": entry.get("ledger_entry_id"),
        "decision": entry.get("decision"),
        "expiration_state": entry.get("expiration_state"),
        "lane": lane,
    }

    recheck_item_id = f"recheck_preview_{_stable_hash(identity, 18)}"

    return {
        "recheck_item_id": recheck_item_id,
        "sequence": sequence,
        "lane": lane,
        "priority": priority,
        "priority_rank": PRIORITY_RANK.get(priority, 99),
        "state_rank": STATE_RANK.get(str(entry.get("expiration_state")), 99),
        "severity_rank": SEVERITY_RANK.get(str(entry.get("severity")), 99),
        "recommended_action": recommended_action,
        "renewal_status": renewal_status,
        "renewal_allowed": bool(entry.get("renewal_allowed", False)),
        "requires_owner_review": lane in {
            "owner_recheck_required",
            "renewal_review_required",
            "renewal_eligible_review_soon",
            "recheck_required_soon",
        },
        "requires_fresh_recheck": lane in {
            "owner_recheck_required",
            "recheck_required_soon",
        },
        "can_prepare_renewal": lane in {
            "renewal_review_required",
            "renewal_eligible_review_soon",
        },
        "is_monitor_only": lane in {
            "monitor_only_no_action",
            "fresh_monitoring",
        },
        "expiration_check_id": _safe_text(entry.get("expiration_check_id")),
        "vault_entry_id": _safe_text(entry.get("vault_entry_id")),
        "ledger_entry_id": _safe_text(entry.get("ledger_entry_id")),
        "receipt_preview_id": _safe_text(entry.get("receipt_preview_id")),
        "scenario_id": _safe_text(entry.get("scenario_id")),
        "matched_policy_id": _safe_text(entry.get("matched_policy_id")),
        "decision": _safe_text(entry.get("decision")),
        "severity": _safe_text(entry.get("severity")),
        "bucket": _safe_text(entry.get("bucket")),
        "expiration_state": _safe_text(entry.get("expiration_state")),
        "ttl_minutes": entry.get("ttl_minutes"),
        "simulated_age_minutes": entry.get("simulated_age_minutes"),
        "minutes_until_expiration": entry.get("minutes_until_expiration"),
        "review_action": _safe_text(entry.get("review_action")),
        "next_action_from_expiration": _safe_text(entry.get("next_action")),
        "owner_prompt": _owner_prompt_for_entry(entry),
        "owner_message_from_expiration": _safe_text(entry.get("owner_message")),
        "soulaana_queue_translation": _soulaana_queue_translation(entry),
        "soulaana_translation_from_expiration": _safe_text(entry.get("soulaana_translation")),
        "proof_bundle_hint": _safe_text(entry.get("proof_bundle_hint")),
        "simulated_only": True,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_receipt_written": False,
        "real_audit_written": False,
        "source_endpoint": EXPIRATION_ENDPOINT,
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


def _sort_queue(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            item.get("priority_rank", 99),
            item.get("state_rank", 99),
            item.get("severity_rank", 99),
            item.get("sequence", 999),
        ),
    )


def _add_queue_positions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    positioned = []
    for idx, item in enumerate(_sort_queue(items), start=1):
        new_item = dict(item)
        new_item["queue_position"] = idx
        positioned.append(new_item)
    return positioned


@lru_cache(maxsize=1)
def build_policy_renewal_recheck_queue_payload_cached() -> Dict[str, Any]:
    expiration_payload = _load_pack_155_payload(force_refresh=False)
    expiration_entries = expiration_payload.get("expiration_entries", [])
    if not isinstance(expiration_entries, list):
        expiration_entries = []

    queue_items: List[Dict[str, Any]] = []
    for idx, entry in enumerate(expiration_entries, start=1):
        if isinstance(entry, dict):
            queue_items.append(build_recheck_queue_item_from_expiration_entry(entry, sequence=idx))

    positioned_queue = _add_queue_positions(queue_items)

    lane_counts = _count_by(positioned_queue, "lane")
    priority_counts = _count_by(positioned_queue, "priority")
    renewal_status_counts = _count_by(positioned_queue, "renewal_status")
    recommended_action_counts = _count_by(positioned_queue, "recommended_action")
    expiration_state_counts = _count_by(positioned_queue, "expiration_state")
    decision_counts = _count_by(positioned_queue, "decision")
    bucket_counts = _count_by(positioned_queue, "bucket")

    by_lane = _group_by(positioned_queue, "lane")
    by_priority = _group_by(positioned_queue, "priority")
    by_renewal_status = _group_by(positioned_queue, "renewal_status")
    by_recommended_action = _group_by(positioned_queue, "recommended_action")
    by_bucket = _group_by(positioned_queue, "bucket")

    owner_review_required = [
        item for item in positioned_queue
        if item.get("requires_owner_review") is True
    ]
    fresh_recheck_required = [
        item for item in positioned_queue
        if item.get("requires_fresh_recheck") is True
    ]
    renewal_candidates = [
        item for item in positioned_queue
        if item.get("can_prepare_renewal") is True
    ]
    monitor_only_items = [
        item for item in positioned_queue
        if item.get("is_monitor_only") is True
    ]

    required_lanes = {
        "owner_recheck_required",
        "renewal_eligible_review_soon",
        "recheck_required_soon",
        "monitor_only_no_action",
    }

    observed_lanes = set(lane_counts.keys())

    required_priorities = {"critical", "high", "medium", "low", "monitor"}
    observed_priorities = set(priority_counts.keys())

    readiness_checks = {
        "pack_155_ready": expiration_payload.get("status") == "ready",
        "has_queue_items": len(positioned_queue) >= 1,
        "queue_count_matches_expiration_entries": len(positioned_queue) == len(expiration_entries),
        "all_simulated_only": all(item.get("simulated_only") is True for item in positioned_queue),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in positioned_queue),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in positioned_queue),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in positioned_queue),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in positioned_queue),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in positioned_queue),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in positioned_queue),
        "all_recheck_ids_present": all(bool(item.get("recheck_item_id")) for item in positioned_queue),
        "all_queue_positions_present": all(bool(item.get("queue_position")) for item in positioned_queue),
        "lane_index_present": bool(by_lane),
        "priority_index_present": bool(by_priority),
        "renewal_status_index_present": bool(by_renewal_status),
        "recommended_action_index_present": bool(by_recommended_action),
        "bucket_index_present": bool(by_bucket),
        "owner_review_required_present": len(owner_review_required) >= 1,
        "fresh_recheck_required_present": len(fresh_recheck_required) >= 1,
        "renewal_candidates_present": len(renewal_candidates) >= 1,
        "monitor_only_items_present": len(monitor_only_items) >= 1,
        "required_lane_coverage": required_lanes.issubset(observed_lanes),
        "required_priority_coverage": required_priorities.issubset(observed_priorities),
        "endpoint": RENEWAL_QUEUE_ENDPOINT,
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
        "pack_number": 156,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Renewal / Recheck Queue foundation",
        "endpoint": RENEWAL_QUEUE_ENDPOINT,
        "source_endpoint": EXPIRATION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_155": {
            "status": expiration_payload.get("status"),
            "readiness_score": expiration_payload.get("summary", {}).get("readiness_score"),
            "expiration_entry_count": expiration_payload.get("summary", {}).get("expiration_entry_count"),
            "expired_count": expiration_payload.get("summary", {}).get("expired_count"),
            "warning_count": expiration_payload.get("summary", {}).get("warning_count"),
            "fresh_count": expiration_payload.get("summary", {}).get("fresh_count"),
            "state_counts": expiration_payload.get("summary", {}).get("state_counts", {}),
        },
        "summary": {
            "queue_item_count": len(positioned_queue),
            "owner_review_required_count": len(owner_review_required),
            "fresh_recheck_required_count": len(fresh_recheck_required),
            "renewal_candidate_count": len(renewal_candidates),
            "monitor_only_count": len(monitor_only_items),
            "lane_count": len(by_lane),
            "priority_count": len(by_priority),
            "lane_counts": lane_counts,
            "priority_counts": priority_counts,
            "renewal_status_counts": renewal_status_counts,
            "recommended_action_counts": recommended_action_counts,
            "expiration_state_counts": expiration_state_counts,
            "decision_counts": decision_counts,
            "bucket_counts": bucket_counts,
            "observed_lanes": sorted(observed_lanes),
            "required_lanes": sorted(required_lanes),
            "observed_priorities": sorted(observed_priorities),
            "required_priorities": sorted(required_priorities),
            "readiness_score": readiness_score,
            "readiness_label": "Policy renewal/recheck queue ready" if readiness_score == 100 else "Policy renewal/recheck queue needs review",
        },
        "readiness_checks": readiness_checks,
        "queue_items": positioned_queue,
        "indexes": {
            "by_lane": by_lane,
            "by_priority": by_priority,
            "by_renewal_status": by_renewal_status,
            "by_recommended_action": by_recommended_action,
            "by_bucket": by_bucket,
        },
        "owner_review_required": owner_review_required,
        "fresh_recheck_required": fresh_recheck_required,
        "renewal_candidates": renewal_candidates,
        "monitor_only_items": monitor_only_items,
        "quick_action": {
            "id": "policy_renewal_recheck_queue",
            "label": "Policy Renewal / Recheck Queue",
            "href": RENEWAL_QUEUE_ENDPOINT,
            "description": "Preview which policy items need renewal, recheck, owner review, or monitoring.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_renewal_recheck_queue",
            "title": "Policy Renewal / Recheck Queue",
            "subtitle": "Turns expiration status into a simulated owner recheck and renewal queue.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": RENEWAL_QUEUE_ENDPOINT,
        },
    }


def build_policy_renewal_recheck_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_renewal_recheck_queue_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_renewal_recheck_queue_payload_cached())


def get_policy_renewal_recheck_queue_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_renewal_recheck_queue_payload(force_refresh=force_refresh)


def build_policy_renewal_recheck_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_renewal_recheck_queue_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 156,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", RENEWAL_QUEUE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", EXPIRATION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy renewal/recheck queue ready"),
        "queue_item_count": summary.get("queue_item_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "fresh_recheck_required_count": summary.get("fresh_recheck_required_count", 0),
        "renewal_candidate_count": summary.get("renewal_candidate_count", 0),
        "monitor_only_count": summary.get("monitor_only_count", 0),
        "lane_counts": summary.get("lane_counts", {}),
        "priority_counts": summary.get("priority_counts", {}),
        "renewal_status_counts": summary.get("renewal_status_counts", {}),
        "recommended_action_counts": summary.get("recommended_action_counts", {}),
        "simulated_only": True,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_renewal_recheck_queue_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_renewal_recheck_queue_status_bridge(force_refresh=force_refresh)


def build_policy_renewal_recheck_queue_quick_action() -> Dict[str, Any]:
    bridge = build_policy_renewal_recheck_queue_status_bridge()
    return {
        "id": "policy_renewal_recheck_queue",
        "label": "Policy Renewal / Recheck Queue",
        "title": "Policy Renewal / Recheck Queue",
        "href": RENEWAL_QUEUE_ENDPOINT,
        "endpoint": RENEWAL_QUEUE_ENDPOINT,
        "description": "Preview renewal and recheck work generated from policy expiration rules.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 156",
        "category": "policy",
        "simulated_only": True,
    }


def build_policy_renewal_recheck_queue_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_renewal_recheck_queue_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "renewal_queue_readiness",
            "title": "Renewal queue readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy renewal/recheck queue ready"),
        },
        {
            "id": "queue_items",
            "title": "Queue items",
            "value": summary.get("queue_item_count", 0),
            "label": "Expiration entries converted",
        },
        {
            "id": "owner_review",
            "title": "Owner review",
            "value": summary.get("owner_review_required_count", 0),
            "label": "Need owner attention",
        },
        {
            "id": "fresh_recheck",
            "title": "Fresh recheck",
            "value": summary.get("fresh_recheck_required_count", 0),
            "label": "Must be rechecked, not renewed",
        },
        {
            "id": "renewal_candidates",
            "title": "Renewal candidates",
            "value": summary.get("renewal_candidate_count", 0),
            "label": "Can prepare renewal review",
        },
        {
            "id": "no_real_recheck",
            "title": "Real recheck executed",
            "value": "No" if checks.get("no_real_recheck_executed") else "Review",
            "label": "Simulation only",
        },
    ]

    return {
        "section_id": "policy_renewal_recheck_queue",
        "title": "Policy Renewal / Recheck Queue",
        "subtitle": "This turns expiration status into a simulated owner renewal and recheck queue.",
        "status": payload.get("status", "ready"),
        "href": RENEWAL_QUEUE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "cached_non_recursive": True,
    }


def build_policy_renewal_recheck_queue_html_section() -> str:
    section = build_policy_renewal_recheck_queue_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-renewal-recheck-queue-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-renewal-recheck-queue-section" id="policy-renewal-recheck-queue">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 156</p>
            <h2>{section.get('title', 'Policy Renewal / Recheck Queue')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{RENEWAL_QUEUE_ENDPOINT}">Open renewal/recheck queue JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "RENEWAL_QUEUE_ENDPOINT",
    "EXPIRATION_ENDPOINT",
    "build_recheck_queue_item_from_expiration_entry",
    "build_policy_renewal_recheck_queue_payload",
    "get_policy_renewal_recheck_queue_payload",
    "build_policy_renewal_recheck_queue_status_bridge",
    "get_policy_renewal_recheck_queue_status_bridge",
    "build_policy_renewal_recheck_queue_quick_action",
    "build_policy_renewal_recheck_queue_unified_owner_section",
    "build_policy_renewal_recheck_queue_html_section",
]
