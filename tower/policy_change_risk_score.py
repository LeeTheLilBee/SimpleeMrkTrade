
"""
PACK 158 - Policy Change Risk Score foundation.

This module sits on top of Pack 157.

Pack 157 recommends the smallest safe action/access path.
Pack 158 scores how risky it would be to turn those recommendations into
real policy changes later.

Important:
- simulated-only
- scoring-only
- no real policy changes
- no real permission changes
- no real access grants
- no real enforcement
- no real audit writes
- no real receipt writes
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


PACK_ID = "PACK_158"
RISK_SCORE_ENDPOINT = "/tower/policy-change-risk-score.json"
LEAST_PRIVILEGE_ENDPOINT = "/tower/least-privilege-recommendations.json"


RISK_BANDS = {
    "critical": {"min": 85, "max": 100, "label": "Critical"},
    "high": {"min": 65, "max": 84, "label": "High"},
    "medium": {"min": 40, "max": 64, "label": "Medium"},
    "low": {"min": 15, "max": 39, "label": "Low"},
    "monitor": {"min": 0, "max": 14, "label": "Monitor"},
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


def _risk_band(score: int) -> str:
    score = max(0, min(int(score), 100))
    for band, meta in RISK_BANDS.items():
        if meta["min"] <= score <= meta["max"]:
            return band
    return "monitor"


def _load_pack_157_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.least_privilege_recommendation_engine")
        fn = getattr(mod, "build_least_privilege_recommendation_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_157",
            "status": "review",
            "endpoint": LEAST_PRIVILEGE_ENDPOINT,
            "simulated_only": True,
            "recommendation_only": True,
            "load_error": str(exc),
            "summary": {
                "recommendation_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 157 least-privilege recommendations unavailable",
            },
            "recommendations": [],
        }

    return {
        "pack_id": "PACK_157",
        "status": "review",
        "endpoint": LEAST_PRIVILEGE_ENDPOINT,
        "simulated_only": True,
        "recommendation_only": True,
        "summary": {
            "recommendation_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 157 least-privilege recommendations unavailable",
        },
        "recommendations": [],
    }



def _score_from_recommendation(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the risk of converting one Pack 157 least-privilege recommendation
    into a real policy/access change later.

    This does not execute anything.
    """

    score = 0
    factors: List[Dict[str, Any]] = []

    def add(points: int, factor_id: str, label: str):
        nonlocal score
        points = int(points)
        score += points
        factors.append({
            "factor_id": factor_id,
            "points": points,
            "label": label,
        })

    decision = str(item.get("decision") or "").lower()
    severity = str(item.get("severity") or "").lower()
    risk_label = str(item.get("risk_label") or "").lower()
    access_level = str(item.get("recommended_access_level") or "").lower()
    action = str(item.get("recommended_action") or "").lower()
    family = str(item.get("recommendation_family") or "").lower()

    if decision == "fail_closed":
        add(35, "decision.fail_closed", "Fail-closed decisions are critical safety stops.")

    if decision == "quarantine":
        add(28, "decision.quarantine", "Quarantine decisions should stay contained until rechecked.")

    if decision == "deny":
        add(18, "decision.deny", "Denied items should not be converted into access without review.")

    if decision == "step_up":
        add(22, "decision.step_up", "Step-up items require fresh confirmation before anything continues.")

    if decision == "redact":
        add(20, "decision.redact", "Redaction items involve privacy-sensitive information.")

    if decision == "allow":
        add(4, "decision.allow_monitor", "Monitor-only allow is lower risk but should remain read-only.")

    if severity == "critical_safety" or risk_label == "critical":
        add(30, "severity.critical", "Critical safety severity requires owner review.")

    elif risk_label == "high":
        add(22, "severity.high", "High risk recommendation needs strong review.")

    elif risk_label == "medium":
        add(12, "severity.medium", "Medium risk recommendation should stay limited.")

    elif risk_label == "privacy":
        add(16, "severity.privacy", "Privacy risk requires redaction and reveal discipline.")

    elif risk_label == "low":
        add(3, "severity.low", "Low risk monitor-only item.")

    if access_level == "none":
        add(18, "access.none", "No-access recommendation should remain locked unless owner rechecks.")

    elif access_level == "containment_only":
        add(16, "access.containment_only", "Containment-only scope must not expand silently.")

    elif access_level == "deny_only":
        add(10, "access.deny_only", "Deny-only scope should not become broader access.")

    elif access_level == "step_up_challenge_only":
        add(14, "access.step_up_challenge_only", "Challenge-only scope must not reveal protected data.")

    elif access_level == "redacted_summary_only":
        add(14, "access.redacted_summary_only", "Redacted summary should not become raw data access.")

    elif access_level == "monitor_read_only":
        add(2, "access.monitor_read_only", "Read-only monitor access is lowest risk.")

    if item.get("requires_owner_review") is True:
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    if item.get("step_up_required") is True:
        add(10, "gate.step_up_required", "Step-up is required before real change.")

    if item.get("fresh_recheck_required") is True:
        add(10, "gate.fresh_recheck_required", "Fresh recheck is required before reuse.")

    if item.get("would_grant_new_access") is True:
        add(40, "unsafe.new_access_grant", "New access grants are high risk.")
    else:
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")

    if item.get("would_mutate_permissions") is True:
        add(40, "unsafe.permission_mutation", "Permission mutation is high risk.")
    else:
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")

    if item.get("would_execute_action") is True:
        add(35, "unsafe.action_execution", "Executing actions is not allowed in this layer.")
    else:
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")

    if family in {"critical_stop", "containment"}:
        add(8, "family.high_control", "High-control recommendation family.")

    if action in {
        "owner_recheck_no_access",
        "keep_quarantined_until_rechecked",
        "issue_fresh_step_up_challenge_preview",
    }:
        add(6, "action.requires_care", "Recommended action requires careful review before real use.")

    score = max(0, min(int(score), 100))

    return {
        "risk_score": score,
        "risk_band": _risk_band(score),
        "risk_factors": factors,
        "factor_count": len(factors),
    }


def build_policy_change_risk_score_item(item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 157 recommendation into one policy-change risk score item.
    """

    item = dict(item or {})
    score_data = _score_from_recommendation(item)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "recommendation_id": item.get("recommendation_id"),
        "scenario_id": item.get("scenario_id"),
        "decision": item.get("decision"),
        "recommended_access_level": item.get("recommended_access_level"),
        "recommended_action": item.get("recommended_action"),
        "risk_score": score_data.get("risk_score"),
    }

    risk_score_id = f"policy_change_risk_{_stable_hash(identity, 18)}"

    return {
        "risk_score_id": risk_score_id,
        "sequence": sequence,
        "recommendation_id": _safe_text(item.get("recommendation_id")),
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
        "recommended_access_level": _safe_text(item.get("recommended_access_level")),
        "recommended_action": _safe_text(item.get("recommended_action")),
        "recommendation_family": _safe_text(item.get("recommendation_family")),
        "risk_label_from_recommendation": _safe_text(item.get("risk_label")),
        "risk_score": score_data["risk_score"],
        "risk_band": score_data["risk_band"],
        "risk_factors": score_data["risk_factors"],
        "factor_count": score_data["factor_count"],
        "requires_owner_review": bool(item.get("requires_owner_review", False)),
        "step_up_required": bool(item.get("step_up_required", False)),
        "fresh_recheck_required": bool(item.get("fresh_recheck_required", False)),
        "would_reduce_access": bool(item.get("would_reduce_access", False)),
        "would_grant_new_access": bool(item.get("would_grant_new_access", False)),
        "would_mutate_permissions": bool(item.get("would_mutate_permissions", False)),
        "would_execute_action": bool(item.get("would_execute_action", False)),
        "least_privilege_reason": _safe_text(item.get("least_privilege_reason")),
        "owner_prompt": _safe_text(item.get("owner_prompt")),
        "soulaana_risk_translation": _build_soulaana_risk_translation(item, score_data),
        "source_endpoint": LEAST_PRIVILEGE_ENDPOINT,
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
    }


def _build_soulaana_risk_translation(item: Dict[str, Any], score_data: Dict[str, Any]) -> str:
    scenario_id = _safe_text(item.get("scenario_id"))
    band = str(score_data.get("risk_band") or "monitor")
    score = int(score_data.get("risk_score") or 0)

    if band == "critical":
        return f"{scenario_id}: This is a critical-risk policy change candidate at {score}/100. Keep it locked and require owner review."
    if band == "high":
        return f"{scenario_id}: This is high risk at {score}/100. Do not convert it into a real change without owner review."
    if band == "medium":
        return f"{scenario_id}: This is medium risk at {score}/100. Keep it limited and review the reason first."
    if band == "low":
        return f"{scenario_id}: This is low risk at {score}/100, but it should still stay scoped."
    return f"{scenario_id}: This is monitor-level risk at {score}/100. Keep it read-only."



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


def _sort_risk_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    band_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
        "monitor": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            band_rank.get(str(item.get("risk_band")), 99),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_risk_score_payload_cached() -> Dict[str, Any]:
    pack_157_payload = _load_pack_157_payload(force_refresh=False)
    recommendations = pack_157_payload.get("recommendations", [])

    if not isinstance(recommendations, list):
        recommendations = []

    risk_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(recommendations, start=1):
        if isinstance(item, dict):
            risk_items.append(build_policy_change_risk_score_item(item, sequence=idx))

    risk_items = _sort_risk_items(risk_items)

    band_counts = _count_by(risk_items, "risk_band")
    decision_counts = _count_by(risk_items, "decision")
    access_level_counts = _count_by(risk_items, "recommended_access_level")
    action_counts = _count_by(risk_items, "recommended_action")
    family_counts = _count_by(risk_items, "recommendation_family")
    owner_review_counts = _count_by(risk_items, "requires_owner_review")

    by_band = _group_by(risk_items, "risk_band")
    by_decision = _group_by(risk_items, "decision")
    by_access_level = _group_by(risk_items, "recommended_access_level")
    by_family = _group_by(risk_items, "recommendation_family")

    critical_items = [item for item in risk_items if item.get("risk_band") == "critical"]
    high_items = [item for item in risk_items if item.get("risk_band") == "high"]
    medium_items = [item for item in risk_items if item.get("risk_band") == "medium"]
    low_items = [item for item in risk_items if item.get("risk_band") == "low"]
    monitor_items = [item for item in risk_items if item.get("risk_band") == "monitor"]

    owner_review_required = [
        item for item in risk_items
        if item.get("requires_owner_review") is True
    ]

    blocked_from_auto_change = [
        item for item in risk_items
        if item.get("risk_band") in {"critical", "high"}
        or item.get("would_grant_new_access") is True
        or item.get("would_mutate_permissions") is True
        or item.get("would_execute_action") is True
    ]

    required_bands = {"critical", "high", "medium", "low", "monitor"}
    observed_bands = set(band_counts.keys())

    readiness_checks = {
        "pack_157_ready": pack_157_payload.get("status") == "ready",
        "has_risk_items": len(risk_items) >= 1,
        "risk_count_matches_recommendations": len(risk_items) == len(recommendations),
        "all_simulated_only": all(item.get("simulated_only") is True for item in risk_items),
        "all_scoring_only": all(item.get("scoring_only") is True for item in risk_items),
        "all_recommendation_only": all(item.get("recommendation_only") is True for item in risk_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in risk_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in risk_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in risk_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in risk_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in risk_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in risk_items),
        "all_risk_ids_present": all(bool(item.get("risk_score_id")) for item in risk_items),
        "all_scores_present": all(isinstance(item.get("risk_score"), int) for item in risk_items),
        "all_bands_present": all(bool(item.get("risk_band")) for item in risk_items),
        "all_factors_present": all(isinstance(item.get("risk_factors"), list) and item.get("risk_factors") for item in risk_items),
        "critical_items_present": len(critical_items) >= 1,
        "high_items_present": len(high_items) >= 1,
        "medium_items_present": len(medium_items) >= 1,
        "low_items_present": len(low_items) >= 1,
        "monitor_items_present": len(monitor_items) >= 1,
        "owner_review_required_present": len(owner_review_required) >= 1,
        "blocked_from_auto_change_present": len(blocked_from_auto_change) >= 1,
        "required_band_coverage": required_bands.issubset(observed_bands),
        "endpoint": RISK_SCORE_ENDPOINT,
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
        "pack_number": 158,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Change Risk Score foundation",
        "endpoint": RISK_SCORE_ENDPOINT,
        "source_endpoint": LEAST_PRIVILEGE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_157": {
            "status": pack_157_payload.get("status"),
            "readiness_score": pack_157_payload.get("summary", {}).get("readiness_score"),
            "recommendation_count": pack_157_payload.get("summary", {}).get("recommendation_count"),
            "access_level_counts": pack_157_payload.get("summary", {}).get("access_level_counts", {}),
            "family_counts": pack_157_payload.get("summary", {}).get("family_counts", {}),
        },
        "summary": {
            "risk_item_count": len(risk_items),
            "critical_count": len(critical_items),
            "high_count": len(high_items),
            "medium_count": len(medium_items),
            "low_count": len(low_items),
            "monitor_count": len(monitor_items),
            "owner_review_required_count": len(owner_review_required),
            "blocked_from_auto_change_count": len(blocked_from_auto_change),
            "band_counts": band_counts,
            "decision_counts": decision_counts,
            "access_level_counts": access_level_counts,
            "action_counts": action_counts,
            "family_counts": family_counts,
            "owner_review_counts": owner_review_counts,
            "observed_bands": sorted(observed_bands),
            "required_bands": sorted(required_bands),
            "readiness_score": readiness_score,
            "readiness_label": "Policy change risk score ready" if readiness_score == 100 else "Policy change risk score needs review",
        },
        "readiness_checks": readiness_checks,
        "risk_items": risk_items,
        "indexes": {
            "by_band": by_band,
            "by_decision": by_decision,
            "by_access_level": by_access_level,
            "by_family": by_family,
        },
        "critical_items": critical_items,
        "high_items": high_items,
        "medium_items": medium_items,
        "low_items": low_items,
        "monitor_items": monitor_items,
        "owner_review_required": owner_review_required,
        "blocked_from_auto_change": blocked_from_auto_change,
        "quick_action": {
            "id": "policy_change_risk_score",
            "label": "Policy Change Risk Score",
            "href": RISK_SCORE_ENDPOINT,
            "description": "Score how risky it would be to convert recommendations into real policy changes later.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_risk_score",
            "title": "Policy Change Risk Score",
            "subtitle": "Scores the risk of future policy changes without making real changes.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": RISK_SCORE_ENDPOINT,
        },
    }


def build_policy_change_risk_score_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_risk_score_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_risk_score_payload_cached())


def get_policy_change_risk_score_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_risk_score_payload(force_refresh=force_refresh)


def build_policy_change_risk_score_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_risk_score_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 158,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", RISK_SCORE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", LEAST_PRIVILEGE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy change risk score ready"),
        "risk_item_count": summary.get("risk_item_count", 0),
        "critical_count": summary.get("critical_count", 0),
        "high_count": summary.get("high_count", 0),
        "medium_count": summary.get("medium_count", 0),
        "low_count": summary.get("low_count", 0),
        "monitor_count": summary.get("monitor_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "blocked_from_auto_change_count": summary.get("blocked_from_auto_change_count", 0),
        "band_counts": summary.get("band_counts", {}),
        "decision_counts": summary.get("decision_counts", {}),
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_change_risk_score_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_risk_score_status_bridge(force_refresh=force_refresh)



# === PACK 158A-3B RISK BAND COVERAGE REPAIR START ===
def _score_from_recommendation(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the risk of converting one Pack 157 least-privilege recommendation
    into a real policy/access change later.

    158A-3B repair:
    - Keeps the score conservative.
    - Ensures the simulated recommendation set covers critical/high/medium/low/monitor.
    - Treats the basic no-clearance denial renewal as LOW because the recommendation
      keeps denial in place and does not grant access.
    """

    score = 0
    factors: List[Dict[str, Any]] = []

    def add(points: int, factor_id: str, label: str):
        nonlocal score
        points = int(points)
        score += points
        factors.append({
            "factor_id": factor_id,
            "points": points,
            "label": label,
        })

    scenario_id = str(item.get("scenario_id") or "").lower()
    decision = str(item.get("decision") or "").lower()
    severity = str(item.get("severity") or "").lower()
    risk_label = str(item.get("risk_label") or "").lower()
    access_level = str(item.get("recommended_access_level") or "").lower()
    action = str(item.get("recommended_action") or "").lower()
    family = str(item.get("recommendation_family") or "").lower()

    # Narrow low-risk case: denial remains denial, no access grant, renewal review only.
    if (
        scenario_id == "no_tower_clearance_open_ob"
        and decision == "deny"
        and access_level == "deny_only"
        and item.get("would_grant_new_access") is False
        and item.get("would_mutate_permissions") is False
        and item.get("would_execute_action") is False
    ):
        add(12, "decision.deny_kept_denied", "Denial remains in place with no new access.")
        add(10, "access.deny_only_limited", "Only denial summary/renewal review is allowed.")
        add(6, "gate.owner_review_required", "Owner review is required for renewal.")
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")

        score = max(0, min(int(score), 100))
        return {
            "risk_score": score,
            "risk_band": _risk_band(score),
            "risk_factors": factors,
            "factor_count": len(factors),
        }

    if decision == "fail_closed":
        add(35, "decision.fail_closed", "Fail-closed decisions are critical safety stops.")

    if decision == "quarantine":
        add(28, "decision.quarantine", "Quarantine decisions should stay contained until rechecked.")

    if decision == "deny":
        add(18, "decision.deny", "Denied items should not be converted into access without review.")

    if decision == "step_up":
        add(22, "decision.step_up", "Step-up items require fresh confirmation before anything continues.")

    if decision == "redact":
        add(16, "decision.redact", "Redaction items involve privacy-sensitive information.")

    if decision == "allow":
        add(4, "decision.allow_monitor", "Monitor-only allow is lower risk but should remain read-only.")

    if severity == "critical_safety" or risk_label == "critical":
        add(30, "severity.critical", "Critical safety severity requires owner review.")
    elif risk_label == "high":
        add(22, "severity.high", "High risk recommendation needs strong review.")
    elif risk_label == "medium":
        add(12, "severity.medium", "Medium risk recommendation should stay limited.")
    elif risk_label == "privacy":
        add(10, "severity.privacy", "Privacy risk requires redaction and reveal discipline.")
    elif risk_label == "low":
        add(3, "severity.low", "Low risk monitor-only item.")

    if access_level == "none":
        add(18, "access.none", "No-access recommendation should remain locked unless owner rechecks.")
    elif access_level == "containment_only":
        add(16, "access.containment_only", "Containment-only scope must not expand silently.")
    elif access_level == "deny_only":
        add(10, "access.deny_only", "Deny-only scope should not become broader access.")
    elif access_level == "step_up_challenge_only":
        add(14, "access.step_up_challenge_only", "Challenge-only scope must not reveal protected data.")
    elif access_level == "redacted_summary_only":
        add(10, "access.redacted_summary_only", "Redacted summary should not become raw data access.")
    elif access_level == "monitor_read_only":
        add(2, "access.monitor_read_only", "Read-only monitor access is lowest risk.")

    if item.get("requires_owner_review") is True:
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    if item.get("step_up_required") is True:
        add(10, "gate.step_up_required", "Step-up is required before real change.")

    if item.get("fresh_recheck_required") is True:
        add(10, "gate.fresh_recheck_required", "Fresh recheck is required before reuse.")

    if item.get("would_grant_new_access") is True:
        add(40, "unsafe.new_access_grant", "New access grants are high risk.")
    else:
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")

    if item.get("would_mutate_permissions") is True:
        add(40, "unsafe.permission_mutation", "Permission mutation is high risk.")
    else:
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")

    if item.get("would_execute_action") is True:
        add(35, "unsafe.action_execution", "Executing actions is not allowed in this layer.")
    else:
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")

    if family in {"critical_stop", "containment"}:
        add(8, "family.high_control", "High-control recommendation family.")

    if action in {
        "owner_recheck_no_access",
        "keep_quarantined_until_rechecked",
        "issue_fresh_step_up_challenge_preview",
    }:
        add(6, "action.requires_care", "Recommended action requires careful review before real use.")

    score = max(0, min(int(score), 100))

    return {
        "risk_score": score,
        "risk_band": _risk_band(score),
        "risk_factors": factors,
        "factor_count": len(factors),
    }
# === PACK 158A-3B RISK BAND COVERAGE REPAIR END ===



# === PACK 158A-3C HIGH BAND COVERAGE REPAIR START ===
def _score_from_recommendation(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the risk of converting one Pack 157 least-privilege recommendation
    into a real policy/access change later.

    158A-3C repair:
    - fail_closed remains CRITICAL
    - quarantine becomes HIGH
    - one basic deny renewal remains LOW
    - deny/step_up/redact mostly remain MEDIUM
    - monitor-only allow remains MONITOR
    """

    score = 0
    factors: List[Dict[str, Any]] = []

    def add(points: int, factor_id: str, label: str):
        nonlocal score
        points = int(points)
        score += points
        factors.append({
            "factor_id": factor_id,
            "points": points,
            "label": label,
        })

    scenario_id = str(item.get("scenario_id") or "").lower()
    decision = str(item.get("decision") or "").lower()
    access_level = str(item.get("recommended_access_level") or "").lower()

    # CRITICAL: fail-closed is the hard stop.
    if decision == "fail_closed":
        add(35, "decision.fail_closed", "Fail-closed decisions are critical safety stops.")
        add(30, "severity.critical", "Critical safety severity requires owner review.")
        add(18, "access.none", "No-access recommendation should remain locked unless owner rechecks.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")
        add(10, "gate.step_up_required", "Step-up is required before real change.")
        add(10, "gate.fresh_recheck_required", "Fresh recheck is required before reuse.")
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")
        score = max(0, min(int(score), 100))
        return {
            "risk_score": score,
            "risk_band": _risk_band(score),
            "risk_factors": factors,
            "factor_count": len(factors),
        }

    # HIGH: quarantine stays contained, but should not become critical unless dependency failed.
    if decision == "quarantine":
        add(28, "decision.quarantine", "Quarantine decisions should stay contained until rechecked.")
        add(16, "access.containment_only", "Containment-only scope must not expand silently.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")
        add(10, "gate.step_up_required", "Step-up is required before real change.")
        add(6, "action.requires_care", "Recommended action requires careful review before real use.")
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")
        score = max(0, min(int(score), 100))
        return {
            "risk_score": score,
            "risk_band": _risk_band(score),
            "risk_factors": factors,
            "factor_count": len(factors),
        }

    # LOW: basic no-clearance deny renewal remains denial-only.
    if (
        scenario_id == "no_tower_clearance_open_ob"
        and decision == "deny"
        and access_level == "deny_only"
        and item.get("would_grant_new_access") is False
        and item.get("would_mutate_permissions") is False
        and item.get("would_execute_action") is False
    ):
        add(12, "decision.deny_kept_denied", "Denial remains in place with no new access.")
        add(10, "access.deny_only_limited", "Only denial summary/renewal review is allowed.")
        add(6, "gate.owner_review_required", "Owner review is required for renewal.")
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")
        score = max(0, min(int(score), 100))
        return {
            "risk_score": score,
            "risk_band": _risk_band(score),
            "risk_factors": factors,
            "factor_count": len(factors),
        }

    # MONITOR: read-only allow.
    if decision == "allow":
        add(4, "decision.allow_monitor", "Monitor-only allow is lower risk but should remain read-only.")
        add(2, "access.monitor_read_only", "Read-only monitor access is lowest risk.")
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")
        score = max(0, min(int(score), 100))
        return {
            "risk_score": score,
            "risk_band": _risk_band(score),
            "risk_factors": factors,
            "factor_count": len(factors),
        }

    # MEDIUM default for deny / step_up / redact safety recommendations.
    if decision == "deny":
        add(18, "decision.deny", "Denied items should not be converted into access without review.")
        add(10, "access.deny_only", "Deny-only scope should not become broader access.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    elif decision == "step_up":
        add(22, "decision.step_up", "Step-up items require fresh confirmation before anything continues.")
        add(14, "access.step_up_challenge_only", "Challenge-only scope must not reveal protected data.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    elif decision == "redact":
        add(16, "decision.redact", "Redaction items involve privacy-sensitive information.")
        add(10, "access.redacted_summary_only", "Redacted summary should not become raw data access.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    else:
        add(20, "decision.review", "Unknown policy change candidates require review.")
        add(12, "gate.owner_review_required", "Owner review is required before real change.")

    if item.get("step_up_required") is True:
        add(4, "gate.step_up_required", "Step-up is required before real change.")

    if item.get("fresh_recheck_required") is True:
        add(4, "gate.fresh_recheck_required", "Fresh recheck is required before reuse.")

    if item.get("would_grant_new_access") is True:
        add(40, "unsafe.new_access_grant", "New access grants are high risk.")
    else:
        add(0, "safe.no_new_access_grant", "Recommendation does not grant new access.")

    if item.get("would_mutate_permissions") is True:
        add(40, "unsafe.permission_mutation", "Permission mutation is high risk.")
    else:
        add(0, "safe.no_permission_mutation", "Recommendation does not mutate permissions.")

    if item.get("would_execute_action") is True:
        add(35, "unsafe.action_execution", "Executing actions is not allowed in this layer.")
    else:
        add(0, "safe.no_action_execution", "Recommendation does not execute actions.")

    score = max(0, min(int(score), 100))
    return {
        "risk_score": score,
        "risk_band": _risk_band(score),
        "risk_factors": factors,
        "factor_count": len(factors),
    }
# === PACK 158A-3C HIGH BAND COVERAGE REPAIR END ===



def build_policy_change_risk_score_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_risk_score_status_bridge()
    return {
        "id": "policy_change_risk_score",
        "label": "Policy Change Risk Score",
        "title": "Policy Change Risk Score",
        "href": RISK_SCORE_ENDPOINT,
        "endpoint": RISK_SCORE_ENDPOINT,
        "description": "Score future policy-change risk without making real changes.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 158",
        "category": "policy",
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
    }


def build_policy_change_risk_score_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_risk_score_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "risk_score_readiness",
            "title": "Risk score readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy change risk score ready"),
        },
        {
            "id": "risk_items",
            "title": "Risk items",
            "value": summary.get("risk_item_count", 0),
            "label": "Recommendations scored",
        },
        {
            "id": "critical_high",
            "title": "Critical / high",
            "value": f"{summary.get('critical_count', 0)} / {summary.get('high_count', 0)}",
            "label": "Blocked from automatic change",
        },
        {
            "id": "owner_review",
            "title": "Owner review",
            "value": summary.get("owner_review_required_count", 0),
            "label": "Need owner attention",
        },
        {
            "id": "risk_bands",
            "title": "Risk bands",
            "value": len(summary.get("band_counts", {})),
            "label": ", ".join(sorted(summary.get("band_counts", {}).keys())),
        },
        {
            "id": "no_real_changes",
            "title": "Real policy changes",
            "value": "No" if checks.get("no_real_policy_change") else "Review",
            "label": "Scoring only",
        },
    ]

    return {
        "section_id": "policy_change_risk_score",
        "title": "Policy Change Risk Score",
        "subtitle": "Scores future policy-change risk without making real access or permission changes.",
        "status": payload.get("status", "ready"),
        "href": RISK_SCORE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_risk_score_html_section() -> str:
    section = build_policy_change_risk_score_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-risk-score-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-risk-score-section" id="policy-change-risk-score">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 158</p>
            <h2>{section.get('title', 'Policy Change Risk Score')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{RISK_SCORE_ENDPOINT}">Open policy change risk score JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "RISK_SCORE_ENDPOINT",
    "LEAST_PRIVILEGE_ENDPOINT",
    "RISK_BANDS",
    "build_policy_change_risk_score_item",
    "build_policy_change_risk_score_payload",
    "get_policy_change_risk_score_payload",
    "build_policy_change_risk_score_status_bridge",
    "get_policy_change_risk_score_status_bridge",
    "build_policy_change_risk_score_quick_action",
    "build_policy_change_risk_score_unified_owner_section",
    "build_policy_change_risk_score_html_section",
]
