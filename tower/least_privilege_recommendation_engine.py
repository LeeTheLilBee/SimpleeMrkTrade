
"""
PACK 157 - Least-Privilege Recommendation Engine foundation.

This layer sits on top of Pack 156.

Pack 156 turns expiration status into a renewal/recheck queue.
Pack 157 recommends the smallest safe action/access path for each queue item.

Important:
- recommendation-only
- simulated-only
- no real permission changes
- no real enforcement
- no real renewal
- no real recheck execution
- no real audit write
- no real receipt write
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


PACK_ID = "PACK_157"
LEAST_PRIVILEGE_ENDPOINT = "/tower/least-privilege-recommendations.json"
RENEWAL_QUEUE_ENDPOINT = "/tower/policy-renewal-recheck-queue.json"


ACCESS_LEVEL_RANK = {
    "none": 0,
    "deny_only": 1,
    "containment_only": 2,
    "redacted_summary_only": 3,
    "step_up_challenge_only": 4,
    "monitor_read_only": 5,
    "owner_review_only": 6,
}


RECOMMENDATION_PRIORITY_RANK = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "monitor": 5,
}


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


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


def _load_pack_156_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_renewal_recheck_queue")
        fn = getattr(mod, "build_policy_renewal_recheck_queue_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_156",
            "status": "review",
            "endpoint": RENEWAL_QUEUE_ENDPOINT,
            "simulated_only": True,
            "real_renewal_executed": False,
            "real_recheck_executed": False,
            "real_expiration_enforced": False,
            "real_enforcement_executed": False,
            "real_audit_written": False,
            "real_receipt_written": False,
            "load_error": str(exc),
            "summary": {
                "queue_item_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 156 renewal/recheck queue unavailable",
            },
            "queue_items": [],
        }

    return {
        "pack_id": "PACK_156",
        "status": "review",
        "endpoint": RENEWAL_QUEUE_ENDPOINT,
        "simulated_only": True,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "summary": {
            "queue_item_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 156 renewal/recheck queue unavailable",
        },
        "queue_items": [],
    }


def _base_recommendation_for_item(item: Dict[str, Any]) -> Dict[str, Any]:
    decision = str(item.get("decision") or "").lower()
    lane = str(item.get("lane") or "").lower()
    expiration_state = str(item.get("expiration_state") or "").lower()
    severity = str(item.get("severity") or "").lower()
    bucket = str(item.get("bucket") or "").lower()
    priority = str(item.get("priority") or "monitor").lower()

    # Fail-closed and critical safety: no access, owner recheck only.
    if decision == "fail_closed" or severity == "critical_safety" or bucket == "critical_safety_stops":
        return {
            "recommended_access_level": "none",
            "recommended_action": "owner_recheck_no_access",
            "recommendation_family": "critical_stop",
            "safe_capability_scope": [],
            "blocked_capabilities": [
                "open_ob",
                "live_mode",
                "automated_mode",
                "export",
                "secret_access",
                "sensitive_reveal",
                "permission_mutation",
            ],
            "owner_gate": "required",
            "step_up_required": True,
            "fresh_recheck_required": True,
            "renewal_allowed": False,
            "least_privilege_reason": "Critical safety or fail-closed items should not receive any access until owner recheck.",
        }

    # Quarantine: keep contained, no route trust.
    if decision == "quarantine" or bucket == "containment_queue":
        return {
            "recommended_access_level": "containment_only",
            "recommended_action": "keep_quarantined_until_rechecked",
            "recommendation_family": "containment",
            "safe_capability_scope": [
                "view_quarantine_summary",
                "owner_review_queue_only",
            ],
            "blocked_capabilities": [
                "route_trust",
                "open_sensitive_route",
                "export",
                "secret_access",
                "permission_mutation",
            ],
            "owner_gate": "required",
            "step_up_required": True,
            "fresh_recheck_required": True,
            "renewal_allowed": False,
            "least_privilege_reason": "Quarantined items should stay contained and only expose a review summary.",
        }

    # Step-up: do not reveal data; only issue/prepare a challenge.
    if decision == "step_up" or lane == "recheck_required_soon":
        return {
            "recommended_access_level": "step_up_challenge_only",
            "recommended_action": "issue_fresh_step_up_challenge_preview",
            "recommendation_family": "step_up",
            "safe_capability_scope": [
                "view_step_up_prompt",
                "prepare_recheck",
            ],
            "blocked_capabilities": [
                "sensitive_reveal_before_step_up",
                "export_before_step_up",
                "permission_mutation",
                "automated_approval",
            ],
            "owner_gate": "required",
            "step_up_required": True,
            "fresh_recheck_required": True,
            "renewal_allowed": False,
            "least_privilege_reason": "Step-up items should only get a fresh confirmation path, not access to the protected data.",
        }

    # Redaction: summary only unless reveal gets approved.
    if decision == "redact" or bucket == "privacy_redactions":
        return {
            "recommended_access_level": "redacted_summary_only",
            "recommended_action": "keep_redacted_prepare_privacy_review",
            "recommendation_family": "privacy",
            "safe_capability_scope": [
                "view_redacted_summary",
                "prepare_privacy_review",
            ],
            "blocked_capabilities": [
                "raw_private_data",
                "sensitive_reveal_without_approval",
                "export_unredacted",
                "permission_mutation",
            ],
            "owner_gate": "conditional",
            "step_up_required": True,
            "fresh_recheck_required": False,
            "renewal_allowed": bool(item.get("renewal_allowed", False)),
            "least_privilege_reason": "Private data should remain hidden unless a proper reveal approval exists.",
        }

    # Deny/block: keep deny as deny, with renewal review if warning.
    if decision == "deny" or bucket == "blocked_decisions":
        return {
            "recommended_access_level": "deny_only",
            "recommended_action": "maintain_deny_prepare_limited_renewal_review",
            "recommendation_family": "deny",
            "safe_capability_scope": [
                "view_denial_summary",
                "prepare_renewal_review",
            ],
            "blocked_capabilities": [
                "open_ob_without_clearance",
                "live_automated_public_access",
                "raw_secret_access",
                "object_access_without_permission",
                "permission_mutation",
            ],
            "owner_gate": "required_for_renewal",
            "step_up_required": False,
            "fresh_recheck_required": expiration_state == "expired",
            "renewal_allowed": bool(item.get("renewal_allowed", True)),
            "least_privilege_reason": "Denied items should stay denied. Only the denial reason may be reviewed or renewed.",
        }

    # Monitor-only allow: read-only/monitor only.
    if decision == "allow" or lane == "monitor_only_no_action":
        return {
            "recommended_access_level": "monitor_read_only",
            "recommended_action": "continue_monitor_only_read_only",
            "recommendation_family": "monitor",
            "safe_capability_scope": [
                "view_monitor_summary",
                "read_policy_status",
            ],
            "blocked_capabilities": [
                "write_policy",
                "permission_mutation",
                "live_mode_enable",
                "export_sensitive",
                "secret_access",
            ],
            "owner_gate": "not_required_for_monitoring",
            "step_up_required": False,
            "fresh_recheck_required": False,
            "renewal_allowed": bool(item.get("renewal_allowed", False)),
            "least_privilege_reason": "Monitor-only items can stay read-only because they do not grant real access.",
        }

    # Fallback: owner review only.
    return {
        "recommended_access_level": "owner_review_only",
        "recommended_action": "owner_review_before_any_access",
        "recommendation_family": "review",
        "safe_capability_scope": [
            "view_review_summary",
        ],
        "blocked_capabilities": [
            "all_sensitive_actions",
            "permission_mutation",
        ],
        "owner_gate": "required",
        "step_up_required": True,
        "fresh_recheck_required": True,
        "renewal_allowed": False,
        "least_privilege_reason": "Unknown queue items default to owner review only.",
    }


def _would_reduce_access(item: Dict[str, Any], recommendation: Dict[str, Any]) -> bool:
    decision = str(item.get("decision") or "").lower()
    access = str(recommendation.get("recommended_access_level") or "").lower()

    if decision in {"deny", "quarantine", "fail_closed", "redact", "step_up"}:
        return access in {
            "none",
            "deny_only",
            "containment_only",
            "redacted_summary_only",
            "step_up_challenge_only",
            "owner_review_only",
        }

    if decision == "allow":
        return access == "monitor_read_only"

    return True


def _risk_label(item: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
    decision = str(item.get("decision") or "").lower()
    severity = str(item.get("severity") or "").lower()
    priority = str(item.get("priority") or "").lower()
    access = str(recommendation.get("recommended_access_level") or "").lower()

    if decision == "fail_closed" or severity == "critical_safety" or priority == "critical":
        return "critical"
    if decision == "quarantine" or severity == "containment" or priority == "high":
        return "high"
    if access in {"deny_only", "step_up_challenge_only"}:
        return "medium"
    if access == "redacted_summary_only":
        return "privacy"
    if access == "monitor_read_only":
        return "low"
    return "review"


def _soulaana_recommendation_translation(item: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
    family = str(recommendation.get("recommendation_family") or "")
    scenario_id = _safe_text(item.get("scenario_id"))

    if family == "critical_stop":
        return f"{scenario_id}: This stays locked down. No access, no recycling, owner must recheck it."
    if family == "containment":
        return f"{scenario_id}: Keep it in the holding room. Only show a safe review summary."
    if family == "step_up":
        return f"{scenario_id}: Do not reveal anything yet. Only prepare a fresh confirmation path."
    if family == "privacy":
        return f"{scenario_id}: Keep private details hidden. Show only the redacted version unless reveal is approved."
    if family == "deny":
        return f"{scenario_id}: Keep the denial in place. Only the denial reason can be reviewed."
    if family == "monitor":
        return f"{scenario_id}: This can stay read-only and monitored. No extra powers needed."
    return f"{scenario_id}: Keep this owner-review-only until The Tower has a safer answer."


def build_least_privilege_recommendation_from_queue_item(item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 156 queue item into one least-privilege recommendation.
    """

    item = dict(item or {})
    base = _base_recommendation_for_item(item)
    risk_label = _risk_label(item, base)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "recheck_item_id": item.get("recheck_item_id"),
        "scenario_id": item.get("scenario_id"),
        "decision": item.get("decision"),
        "lane": item.get("lane"),
        "recommended_action": base.get("recommended_action"),
        "recommended_access_level": base.get("recommended_access_level"),
    }

    recommendation_id = f"least_privilege_preview_{_stable_hash(identity, 18)}"

    access_level = str(base.get("recommended_access_level") or "owner_review_only")
    access_rank = ACCESS_LEVEL_RANK.get(access_level, 99)

    recommendation_priority = str(item.get("priority") or "monitor").lower()
    recommendation_priority_rank = RECOMMENDATION_PRIORITY_RANK.get(recommendation_priority, 99)

    return {
        "recommendation_id": recommendation_id,
        "sequence": sequence,
        "queue_position": item.get("queue_position"),
        "recheck_item_id": _safe_text(item.get("recheck_item_id")),
        "expiration_check_id": _safe_text(item.get("expiration_check_id")),
        "vault_entry_id": _safe_text(item.get("vault_entry_id")),
        "ledger_entry_id": _safe_text(item.get("ledger_entry_id")),
        "receipt_preview_id": _safe_text(item.get("receipt_preview_id")),
        "scenario_id": _safe_text(item.get("scenario_id")),
        "matched_policy_id": _safe_text(item.get("matched_policy_id")),
        "decision": _safe_text(item.get("decision")),
        "severity": _safe_text(item.get("severity")),
        "bucket": _safe_text(item.get("bucket")),
        "lane": _safe_text(item.get("lane")),
        "expiration_state": _safe_text(item.get("expiration_state")),
        "priority": recommendation_priority,
        "priority_rank": recommendation_priority_rank,
        "risk_label": risk_label,
        "recommended_access_level": access_level,
        "recommended_access_rank": access_rank,
        "recommended_action": base.get("recommended_action"),
        "recommendation_family": base.get("recommendation_family"),
        "safe_capability_scope": base.get("safe_capability_scope", []),
        "blocked_capabilities": base.get("blocked_capabilities", []),
        "owner_gate": base.get("owner_gate"),
        "step_up_required": bool(base.get("step_up_required", False)),
        "fresh_recheck_required": bool(base.get("fresh_recheck_required", False)),
        "renewal_allowed": bool(base.get("renewal_allowed", False)),
        "requires_owner_review": bool(item.get("requires_owner_review", False)) or str(base.get("owner_gate")) in {"required", "required_for_renewal"},
        "would_reduce_access": _would_reduce_access(item, base),
        "would_grant_new_access": False,
        "would_mutate_permissions": False,
        "would_execute_action": False,
        "least_privilege_reason": base.get("least_privilege_reason"),
        "owner_prompt": _safe_text(item.get("owner_prompt")),
        "soulaana_recommendation_translation": _soulaana_recommendation_translation(item, base),
        "source_queue_recommendation": _safe_text(item.get("recommended_action")),
        "source_renewal_status": _safe_text(item.get("renewal_status")),
        "source_endpoint": RENEWAL_QUEUE_ENDPOINT,
        "simulated_only": True,
        "recommendation_only": True,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
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


def _sort_recommendations(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            item.get("priority_rank", 99),
            item.get("recommended_access_rank", 99),
            item.get("queue_position", 999),
            item.get("sequence", 999),
        ),
    )


@lru_cache(maxsize=1)
def build_least_privilege_recommendation_payload_cached() -> Dict[str, Any]:
    queue_payload = _load_pack_156_payload(force_refresh=False)
    queue_items = queue_payload.get("queue_items", [])
    if not isinstance(queue_items, list):
        queue_items = []

    recommendations: List[Dict[str, Any]] = []
    for idx, item in enumerate(queue_items, start=1):
        if isinstance(item, dict):
            recommendations.append(build_least_privilege_recommendation_from_queue_item(item, sequence=idx))

    recommendations = _sort_recommendations(recommendations)

    access_level_counts = _count_by(recommendations, "recommended_access_level")
    action_counts = _count_by(recommendations, "recommended_action")
    family_counts = _count_by(recommendations, "recommendation_family")
    risk_counts = _count_by(recommendations, "risk_label")
    decision_counts = _count_by(recommendations, "decision")
    lane_counts = _count_by(recommendations, "lane")
    owner_gate_counts = _count_by(recommendations, "owner_gate")

    by_access_level = _group_by(recommendations, "recommended_access_level")
    by_action = _group_by(recommendations, "recommended_action")
    by_family = _group_by(recommendations, "recommendation_family")
    by_risk = _group_by(recommendations, "risk_label")
    by_decision = _group_by(recommendations, "decision")

    owner_review_recommendations = [
        item for item in recommendations
        if item.get("requires_owner_review") is True
    ]
    step_up_recommendations = [
        item for item in recommendations
        if item.get("step_up_required") is True
    ]
    no_access_recommendations = [
        item for item in recommendations
        if item.get("recommended_access_level") in {"none", "deny_only", "containment_only"}
    ]
    redaction_recommendations = [
        item for item in recommendations
        if item.get("recommended_access_level") == "redacted_summary_only"
    ]
    monitor_recommendations = [
        item for item in recommendations
        if item.get("recommended_access_level") == "monitor_read_only"
    ]

    required_access_levels = {
        "none",
        "deny_only",
        "containment_only",
        "redacted_summary_only",
        "step_up_challenge_only",
        "monitor_read_only",
    }
    observed_access_levels = set(access_level_counts.keys())

    required_families = {
        "critical_stop",
        "containment",
        "deny",
        "privacy",
        "step_up",
        "monitor",
    }
    observed_families = set(family_counts.keys())

    readiness_checks = {
        "pack_156_ready": queue_payload.get("status") == "ready",
        "has_recommendations": len(recommendations) >= 1,
        "recommendation_count_matches_queue": len(recommendations) == len(queue_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in recommendations),
        "all_recommendation_only": all(item.get("recommendation_only") is True for item in recommendations),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in recommendations),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in recommendations),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in recommendations),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in recommendations),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in recommendations),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in recommendations),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in recommendations),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in recommendations),
        "all_recommendation_ids_present": all(bool(item.get("recommendation_id")) for item in recommendations),
        "all_access_levels_present": all(bool(item.get("recommended_access_level")) for item in recommendations),
        "all_actions_present": all(bool(item.get("recommended_action")) for item in recommendations),
        "all_reasons_present": all(bool(item.get("least_privilege_reason")) for item in recommendations),
        "all_reduce_or_safe_monitor": all(item.get("would_reduce_access") is True for item in recommendations),
        "no_new_access_grants": all(item.get("would_grant_new_access") is False for item in recommendations),
        "no_permission_mutations": all(item.get("would_mutate_permissions") is False for item in recommendations),
        "owner_review_recommendations_present": len(owner_review_recommendations) >= 1,
        "step_up_recommendations_present": len(step_up_recommendations) >= 1,
        "no_access_recommendations_present": len(no_access_recommendations) >= 1,
        "redaction_recommendations_present": len(redaction_recommendations) >= 1,
        "monitor_recommendations_present": len(monitor_recommendations) >= 1,
        "required_access_level_coverage": required_access_levels.issubset(observed_access_levels),
        "required_family_coverage": required_families.issubset(observed_families),
        "endpoint": LEAST_PRIVILEGE_ENDPOINT,
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
        "pack_number": 157,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Least-Privilege Recommendation Engine foundation",
        "endpoint": LEAST_PRIVILEGE_ENDPOINT,
        "source_endpoint": RENEWAL_QUEUE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "recommendation_only": True,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_156": {
            "status": queue_payload.get("status"),
            "readiness_score": queue_payload.get("summary", {}).get("readiness_score"),
            "queue_item_count": queue_payload.get("summary", {}).get("queue_item_count"),
            "owner_review_required_count": queue_payload.get("summary", {}).get("owner_review_required_count"),
            "fresh_recheck_required_count": queue_payload.get("summary", {}).get("fresh_recheck_required_count"),
            "renewal_candidate_count": queue_payload.get("summary", {}).get("renewal_candidate_count"),
            "monitor_only_count": queue_payload.get("summary", {}).get("monitor_only_count"),
            "lane_counts": queue_payload.get("summary", {}).get("lane_counts", {}),
            "priority_counts": queue_payload.get("summary", {}).get("priority_counts", {}),
        },
        "summary": {
            "recommendation_count": len(recommendations),
            "owner_review_recommendation_count": len(owner_review_recommendations),
            "step_up_recommendation_count": len(step_up_recommendations),
            "no_access_recommendation_count": len(no_access_recommendations),
            "redaction_recommendation_count": len(redaction_recommendations),
            "monitor_recommendation_count": len(monitor_recommendations),
            "access_level_count": len(by_access_level),
            "family_count": len(by_family),
            "access_level_counts": access_level_counts,
            "action_counts": action_counts,
            "family_counts": family_counts,
            "risk_counts": risk_counts,
            "decision_counts": decision_counts,
            "lane_counts": lane_counts,
            "owner_gate_counts": owner_gate_counts,
            "observed_access_levels": sorted(observed_access_levels),
            "required_access_levels": sorted(required_access_levels),
            "observed_families": sorted(observed_families),
            "required_families": sorted(required_families),
            "readiness_score": readiness_score,
            "readiness_label": "Least-privilege recommendation engine ready" if readiness_score == 100 else "Least-privilege recommendation engine needs review",
        },
        "readiness_checks": readiness_checks,
        "recommendations": recommendations,
        "indexes": {
            "by_access_level": by_access_level,
            "by_action": by_action,
            "by_family": by_family,
            "by_risk": by_risk,
            "by_decision": by_decision,
        },
        "owner_review_recommendations": owner_review_recommendations,
        "step_up_recommendations": step_up_recommendations,
        "no_access_recommendations": no_access_recommendations,
        "redaction_recommendations": redaction_recommendations,
        "monitor_recommendations": monitor_recommendations,
        "quick_action": {
            "id": "least_privilege_recommendations",
            "label": "Least-Privilege Recommendations",
            "href": LEAST_PRIVILEGE_ENDPOINT,
            "description": "Preview the smallest safe access/action path for each policy queue item.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "least_privilege_recommendations",
            "title": "Least-Privilege Recommendations",
            "subtitle": "Recommends the smallest safe path without changing real permissions.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": LEAST_PRIVILEGE_ENDPOINT,
        },
    }


def build_least_privilege_recommendation_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_least_privilege_recommendation_payload_cached.cache_clear()
    return copy.deepcopy(build_least_privilege_recommendation_payload_cached())


def get_least_privilege_recommendation_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_least_privilege_recommendation_payload(force_refresh=force_refresh)


def build_least_privilege_recommendation_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_least_privilege_recommendation_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 157,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", LEAST_PRIVILEGE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", RENEWAL_QUEUE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Least-privilege recommendation engine ready"),
        "recommendation_count": summary.get("recommendation_count", 0),
        "owner_review_recommendation_count": summary.get("owner_review_recommendation_count", 0),
        "step_up_recommendation_count": summary.get("step_up_recommendation_count", 0),
        "no_access_recommendation_count": summary.get("no_access_recommendation_count", 0),
        "redaction_recommendation_count": summary.get("redaction_recommendation_count", 0),
        "monitor_recommendation_count": summary.get("monitor_recommendation_count", 0),
        "access_level_counts": summary.get("access_level_counts", {}),
        "family_counts": summary.get("family_counts", {}),
        "risk_counts": summary.get("risk_counts", {}),
        "simulated_only": True,
        "recommendation_only": True,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_renewal_executed": False,
        "real_recheck_executed": False,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_least_privilege_recommendation_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_least_privilege_recommendation_status_bridge(force_refresh=force_refresh)


def build_least_privilege_recommendation_quick_action() -> Dict[str, Any]:
    bridge = build_least_privilege_recommendation_status_bridge()
    return {
        "id": "least_privilege_recommendations",
        "label": "Least-Privilege Recommendations",
        "title": "Least-Privilege Recommendations",
        "href": LEAST_PRIVILEGE_ENDPOINT,
        "endpoint": LEAST_PRIVILEGE_ENDPOINT,
        "description": "Preview the smallest safe action/access path for each policy queue item.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 157",
        "category": "policy",
        "simulated_only": True,
        "recommendation_only": True,
    }


def build_least_privilege_recommendation_unified_owner_section() -> Dict[str, Any]:
    payload = build_least_privilege_recommendation_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "least_privilege_readiness",
            "title": "Least-privilege readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Least-privilege recommendation engine ready"),
        },
        {
            "id": "recommendations",
            "title": "Recommendations",
            "value": summary.get("recommendation_count", 0),
            "label": "Queue items mapped to smallest safe path",
        },
        {
            "id": "owner_review",
            "title": "Owner review",
            "value": summary.get("owner_review_recommendation_count", 0),
            "label": "Require owner attention",
        },
        {
            "id": "no_access",
            "title": "No/blocked access",
            "value": summary.get("no_access_recommendation_count", 0),
            "label": "Kept locked or contained",
        },
        {
            "id": "access_levels",
            "title": "Access levels",
            "value": summary.get("access_level_count", 0),
            "label": ", ".join(sorted(summary.get("access_level_counts", {}).keys())),
        },
        {
            "id": "no_real_access",
            "title": "Real access granted",
            "value": "No" if checks.get("no_real_access_granted") else "Review",
            "label": "Recommendation only",
        },
    ]

    return {
        "section_id": "least_privilege_recommendations",
        "title": "Least-Privilege Recommendations",
        "subtitle": "This recommends the smallest safe path without changing real permissions.",
        "status": payload.get("status", "ready"),
        "href": LEAST_PRIVILEGE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "recommendation_only": True,
        "cached_non_recursive": True,
    }


def build_least_privilege_recommendation_html_section() -> str:
    section = build_least_privilege_recommendation_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card least-privilege-recommendation-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section least-privilege-recommendation-section" id="least-privilege-recommendations">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 157</p>
            <h2>{section.get('title', 'Least-Privilege Recommendations')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{LEAST_PRIVILEGE_ENDPOINT}">Open least-privilege recommendations JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "LEAST_PRIVILEGE_ENDPOINT",
    "RENEWAL_QUEUE_ENDPOINT",
    "build_least_privilege_recommendation_from_queue_item",
    "build_least_privilege_recommendation_payload",
    "get_least_privilege_recommendation_payload",
    "build_least_privilege_recommendation_status_bridge",
    "get_least_privilege_recommendation_status_bridge",
    "build_least_privilege_recommendation_quick_action",
    "build_least_privilege_recommendation_unified_owner_section",
    "build_least_privilege_recommendation_html_section",
]
