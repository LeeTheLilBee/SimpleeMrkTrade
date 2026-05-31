
"""
PACK 162 - Approval Receipt Expiration Rules.

This module sits on top of Pack 161.

Pack 161 creates simulated vault/index placement for approval receipt previews.
Pack 162 assigns simulated expiration, renewal, and recheck windows to those
approval receipt vault/index items before anything is enforced for real.

Important:
- simulated-only
- expiration-preview-only
- renewal-preview-only
- recheck-preview-only
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


PACK_ID = "PACK_162"
APPROVAL_RECEIPT_EXPIRATION_ENDPOINT = "/tower/policy-change-approval-receipt-expiration-rules.json"
APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT = "/tower/policy-change-approval-receipt-vault-index.json"


EXPIRATION_RULES = {
    "critical_denials": {
        "label": "Critical Denial Expiration Rule",
        "ttl_hours": 12,
        "warning_hours": 4,
        "recheck_required": True,
        "renewal_allowed": False,
        "owner_review_required": True,
        "priority": "critical",
    },
    "quarantine_reviews": {
        "label": "Quarantine Review Expiration Rule",
        "ttl_hours": 24,
        "warning_hours": 8,
        "recheck_required": True,
        "renewal_allowed": False,
        "owner_review_required": True,
        "priority": "high",
    },
    "privacy_reviews": {
        "label": "Privacy Review Expiration Rule",
        "ttl_hours": 48,
        "warning_hours": 12,
        "recheck_required": True,
        "renewal_allowed": True,
        "owner_review_required": True,
        "priority": "medium",
    },
    "owner_step_up": {
        "label": "Owner Step-Up Expiration Rule",
        "ttl_hours": 24,
        "warning_hours": 8,
        "recheck_required": True,
        "renewal_allowed": False,
        "owner_review_required": True,
        "priority": "medium",
    },
    "owner_reviews": {
        "label": "Owner Review Expiration Rule",
        "ttl_hours": 72,
        "warning_hours": 24,
        "recheck_required": False,
        "renewal_allowed": True,
        "owner_review_required": True,
        "priority": "medium",
    },
    "monitor_acknowledgements": {
        "label": "Monitor Acknowledgement Expiration Rule",
        "ttl_hours": 168,
        "warning_hours": 48,
        "recheck_required": False,
        "renewal_allowed": True,
        "owner_review_required": False,
        "priority": "monitor",
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


def _parse_utc(value: Any) -> datetime.datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.datetime.utcnow().replace(microsecond=0)

    try:
        if text.endswith("Z"):
            text = text[:-1]
        parsed = datetime.datetime.fromisoformat(text)
        return parsed.replace(tzinfo=None, microsecond=0)
    except Exception:
        return datetime.datetime.utcnow().replace(microsecond=0)


def _iso_from_dt(value: datetime.datetime) -> str:
    return value.replace(microsecond=0).isoformat() + "Z"


def _load_pack_161_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_vault_index")
        fn = getattr(mod, "build_policy_change_approval_receipt_vault_index_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_161",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
            "simulated_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "vault_item_count": 0,
                "ledger_index_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 161 approval receipt vault/index payload unavailable",
            },
            "vault_items": [],
        }

    return {
        "pack_id": "PACK_161",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "simulated_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "summary": {
            "vault_item_count": 0,
            "ledger_index_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 161 approval receipt vault/index payload unavailable",
        },
        "vault_items": [],
    }



def _select_expiration_rule(vault_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the simulated expiration rule for one Pack 161 vault/index item.

    This does not enforce expiration.
    This only previews the timing and review requirement.
    """

    bucket = str(vault_item.get("vault_bucket") or "").lower()
    rule = dict(EXPIRATION_RULES.get(bucket) or EXPIRATION_RULES["owner_reviews"])

    return {
        "expiration_rule_bucket": bucket if bucket in EXPIRATION_RULES else "owner_reviews",
        "expiration_rule_label": rule["label"],
        "ttl_hours": int(rule["ttl_hours"]),
        "warning_hours": int(rule["warning_hours"]),
        "recheck_required": bool(rule["recheck_required"]),
        "renewal_allowed": bool(rule["renewal_allowed"]),
        "owner_review_required": bool(rule["owner_review_required"]),
        "priority": _safe_text(rule["priority"]),
    }


def _calculate_expiration_window(vault_item: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build deterministic preview times from the source payload timestamp.

    If the source timestamp is missing, use current UTC.
    """

    source_time = (
        vault_item.get("generated_at")
        or vault_item.get("created_at")
        or vault_item.get("indexed_at")
        or _utc_now()
    )

    created_at_dt = _parse_utc(source_time)
    expires_at_dt = created_at_dt + datetime.timedelta(hours=int(rule.get("ttl_hours") or 0))
    warning_at_dt = expires_at_dt - datetime.timedelta(hours=int(rule.get("warning_hours") or 0))

    return {
        "created_at": _iso_from_dt(created_at_dt),
        "warning_at": _iso_from_dt(warning_at_dt),
        "expires_at": _iso_from_dt(expires_at_dt),
        "ttl_hours": int(rule.get("ttl_hours") or 0),
        "warning_hours": int(rule.get("warning_hours") or 0),
    }


def _derive_expiration_state(rule: Dict[str, Any]) -> str:
    """
    For Pack 162 preview, state is based on the rule class, not real time enforcement.
    """

    priority = str(rule.get("priority") or "").lower()

    if priority == "critical":
        return "expires_fast_recheck_required"
    if priority == "high":
        return "expires_soon_recheck_required"
    if rule.get("recheck_required") is True:
        return "recheck_required_before_reuse"
    if rule.get("renewal_allowed") is True:
        return "renewal_allowed_before_expiration"
    return "owner_review_required_before_reuse"


def _expiration_soulaana_translation(vault_item: Dict[str, Any], rule: Dict[str, Any], state: str) -> str:
    scenario_id = _safe_text(vault_item.get("scenario_id"))
    bucket = _safe_text(vault_item.get("vault_bucket"))
    ttl = int(rule.get("ttl_hours") or 0)

    if state == "expires_fast_recheck_required":
        return f"{scenario_id}: This {bucket} receipt expires fast in {ttl} hours and needs owner recheck before reuse."
    if state == "expires_soon_recheck_required":
        return f"{scenario_id}: This {bucket} receipt expires soon in {ttl} hours and must be rechecked before anything moves."
    if state == "recheck_required_before_reuse":
        return f"{scenario_id}: This {bucket} receipt needs a fresh recheck before it can be reused."
    if state == "renewal_allowed_before_expiration":
        return f"{scenario_id}: This {bucket} receipt can be renewed as a preview before expiration if the owner reviews it."
    return f"{scenario_id}: This {bucket} receipt stays blocked until owner review."


def build_policy_change_approval_receipt_expiration_item(vault_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 161 approval receipt vault/index item into one simulated
    expiration rule preview item.
    """

    vault_item = dict(vault_item or {})
    rule = _select_expiration_rule(vault_item)
    window = _calculate_expiration_window(vault_item, rule)
    expiration_state = _derive_expiration_state(rule)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "vault_preview_id": vault_item.get("vault_preview_id"),
        "ledger_index_id": vault_item.get("ledger_index_id"),
        "scenario_id": vault_item.get("scenario_id"),
        "vault_bucket": vault_item.get("vault_bucket"),
        "expiration_state": expiration_state,
    }

    expiration_preview_id = f"approval_receipt_expiration_preview_{_stable_hash(identity, 18)}"

    return {
        "expiration_preview_id": expiration_preview_id,
        "sequence": sequence,
        "vault_preview_id": _safe_text(vault_item.get("vault_preview_id")),
        "ledger_index_id": _safe_text(vault_item.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(vault_item.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(vault_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(vault_item.get("risk_score_id")),
        "recommendation_id": _safe_text(vault_item.get("recommendation_id")),
        "scenario_id": _safe_text(vault_item.get("scenario_id")),
        "matched_policy_id": _safe_text(vault_item.get("matched_policy_id")),
        "decision": _safe_text(vault_item.get("decision")),
        "risk_score": int(vault_item.get("risk_score") or 0),
        "risk_band": _safe_text(vault_item.get("risk_band")),
        "approval_path": _safe_text(vault_item.get("approval_path")),
        "receipt_type": _safe_text(vault_item.get("receipt_type")),
        "receipt_severity": _safe_text(vault_item.get("receipt_severity")),
        "vault_bucket": _safe_text(vault_item.get("vault_bucket")),
        "retention_class": _safe_text(vault_item.get("retention_class")),
        "index_status": _safe_text(vault_item.get("index_status")),
        "expiration_rule_bucket": rule["expiration_rule_bucket"],
        "expiration_rule_label": rule["expiration_rule_label"],
        "priority": rule["priority"],
        "ttl_hours": rule["ttl_hours"],
        "warning_hours": rule["warning_hours"],
        "created_at": window["created_at"],
        "warning_at": window["warning_at"],
        "expires_at": window["expires_at"],
        "expiration_state": expiration_state,
        "recheck_required": rule["recheck_required"],
        "renewal_allowed": rule["renewal_allowed"],
        "owner_review_required": rule["owner_review_required"],
        "expiration_enforcement_allowed_now": False,
        "auto_renewal_allowed_now": False,
        "real_expiration_enforced": False,
        "real_recheck_executed": False,
        "real_renewal_executed": False,
        "soulaana_expiration_translation": _expiration_soulaana_translation(vault_item, rule, expiration_state),
        "source_endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
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


def _sort_expiration_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "monitor": 4,
    }
    state_rank = {
        "expires_fast_recheck_required": 1,
        "expires_soon_recheck_required": 2,
        "recheck_required_before_reuse": 3,
        "renewal_allowed_before_expiration": 4,
        "owner_review_required_before_reuse": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            priority_rank.get(str(item.get("priority")), 99),
            state_rank.get(str(item.get("expiration_state")), 99),
            int(item.get("ttl_hours") or 999999),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_expiration_rules_payload_cached() -> Dict[str, Any]:
    pack_161_payload = _load_pack_161_payload(force_refresh=False)
    vault_items = pack_161_payload.get("vault_items", [])

    if not isinstance(vault_items, list):
        vault_items = []

    expiration_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(vault_items, start=1):
        if isinstance(item, dict):
            expiration_items.append(build_policy_change_approval_receipt_expiration_item(item, sequence=idx))

    expiration_items = _sort_expiration_items(expiration_items)

    priority_counts = _count_by(expiration_items, "priority")
    bucket_counts = _count_by(expiration_items, "vault_bucket")
    expiration_state_counts = _count_by(expiration_items, "expiration_state")
    receipt_type_counts = _count_by(expiration_items, "receipt_type")
    renewal_allowed_counts = _count_by(expiration_items, "renewal_allowed")
    recheck_required_counts = _count_by(expiration_items, "recheck_required")
    owner_review_counts = _count_by(expiration_items, "owner_review_required")

    by_priority = _group_by(expiration_items, "priority")
    by_bucket = _group_by(expiration_items, "vault_bucket")
    by_expiration_state = _group_by(expiration_items, "expiration_state")
    by_receipt_type = _group_by(expiration_items, "receipt_type")
    by_renewal_allowed = _group_by(expiration_items, "renewal_allowed")
    by_recheck_required = _group_by(expiration_items, "recheck_required")

    critical_items = [
        item for item in expiration_items
        if item.get("priority") == "critical"
    ]
    high_items = [
        item for item in expiration_items
        if item.get("priority") == "high"
    ]
    medium_items = [
        item for item in expiration_items
        if item.get("priority") == "medium"
    ]
    monitor_items = [
        item for item in expiration_items
        if item.get("priority") == "monitor"
    ]
    recheck_required_items = [
        item for item in expiration_items
        if item.get("recheck_required") is True
    ]
    renewal_allowed_items = [
        item for item in expiration_items
        if item.get("renewal_allowed") is True
    ]
    owner_review_required_items = [
        item for item in expiration_items
        if item.get("owner_review_required") is True
    ]

    required_buckets = set(EXPIRATION_RULES.keys())
    observed_buckets = set(bucket_counts.keys())

    required_states = {
        "expires_fast_recheck_required",
        "expires_soon_recheck_required",
        "recheck_required_before_reuse",
        "renewal_allowed_before_expiration",
    }
    observed_states = set(expiration_state_counts.keys())

    readiness_checks = {
        "pack_161_ready": pack_161_payload.get("status") == "ready",
        "has_expiration_items": len(expiration_items) >= 1,
        "expiration_count_matches_vault_items": len(expiration_items) == len(vault_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in expiration_items),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in expiration_items),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in expiration_items),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in expiration_items),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in expiration_items),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in expiration_items),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in expiration_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in expiration_items),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in expiration_items),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in expiration_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in expiration_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in expiration_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in expiration_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in expiration_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in expiration_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in expiration_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in expiration_items),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in expiration_items),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in expiration_items),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in expiration_items),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in expiration_items),
        "expiration_enforcement_never_allowed_now": all(item.get("expiration_enforcement_allowed_now") is False for item in expiration_items),
        "auto_renewal_never_allowed_now": all(item.get("auto_renewal_allowed_now") is False for item in expiration_items),
        "all_expiration_ids_present": all(bool(item.get("expiration_preview_id")) for item in expiration_items),
        "all_rules_present": all(bool(item.get("expiration_rule_label")) for item in expiration_items),
        "all_windows_present": all(bool(item.get("created_at")) and bool(item.get("warning_at")) and bool(item.get("expires_at")) for item in expiration_items),
        "all_states_present": all(bool(item.get("expiration_state")) for item in expiration_items),
        "critical_items_present": len(critical_items) >= 1,
        "high_items_present": len(high_items) >= 1,
        "medium_items_present": len(medium_items) >= 1,
        "monitor_items_present": len(monitor_items) >= 1,
        "recheck_required_items_present": len(recheck_required_items) >= 1,
        "renewal_allowed_items_present": len(renewal_allowed_items) >= 1,
        "owner_review_required_items_present": len(owner_review_required_items) >= 1,
        "required_bucket_coverage": required_buckets.issubset(observed_buckets),
        "required_state_coverage": required_states.issubset(observed_states),
        "endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
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
        "pack_number": 162,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Approval Receipt Expiration Rules",
        "endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
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
        "cached_non_recursive": True,
        "source_pack_161": {
            "status": pack_161_payload.get("status"),
            "readiness_score": pack_161_payload.get("summary", {}).get("readiness_score"),
            "vault_item_count": pack_161_payload.get("summary", {}).get("vault_item_count"),
            "ledger_index_count": pack_161_payload.get("summary", {}).get("ledger_index_count"),
            "bucket_counts": pack_161_payload.get("summary", {}).get("bucket_counts", {}),
        },
        "summary": {
            "expiration_item_count": len(expiration_items),
            "critical_count": len(critical_items),
            "high_count": len(high_items),
            "medium_count": len(medium_items),
            "monitor_count": len(monitor_items),
            "recheck_required_count": len(recheck_required_items),
            "renewal_allowed_count": len(renewal_allowed_items),
            "owner_review_required_count": len(owner_review_required_items),
            "priority_counts": priority_counts,
            "bucket_counts": bucket_counts,
            "expiration_state_counts": expiration_state_counts,
            "receipt_type_counts": receipt_type_counts,
            "renewal_allowed_counts": renewal_allowed_counts,
            "recheck_required_counts": recheck_required_counts,
            "owner_review_counts": owner_review_counts,
            "observed_buckets": sorted(observed_buckets),
            "required_buckets": sorted(required_buckets),
            "observed_states": sorted(observed_states),
            "required_states": sorted(required_states),
            "readiness_score": readiness_score,
            "readiness_label": "Approval receipt expiration rules ready" if readiness_score == 100 else "Approval receipt expiration rules need review",
        },
        "readiness_checks": readiness_checks,
        "expiration_items": expiration_items,
        "indexes": {
            "by_priority": by_priority,
            "by_bucket": by_bucket,
            "by_expiration_state": by_expiration_state,
            "by_receipt_type": by_receipt_type,
            "by_renewal_allowed": by_renewal_allowed,
            "by_recheck_required": by_recheck_required,
        },
        "critical_items": critical_items,
        "high_items": high_items,
        "medium_items": medium_items,
        "monitor_items": monitor_items,
        "recheck_required_items": recheck_required_items,
        "renewal_allowed_items": renewal_allowed_items,
        "owner_review_required_items": owner_review_required_items,
        "quick_action": {
            "id": "policy_change_approval_receipt_expiration_rules",
            "label": "Approval Receipt Expiration Rules",
            "href": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
            "description": "Preview expiration, renewal, and recheck rules for approval receipt evidence.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_expiration_rules",
            "title": "Approval Receipt Expiration Rules",
            "subtitle": "Previews expiration and recheck windows before any real enforcement happens.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_expiration_rules_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_expiration_rules_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_expiration_rules_payload_cached())


def get_policy_change_approval_receipt_expiration_rules_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_expiration_rules_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_expiration_rules_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 162,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_EXPIRATION_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Approval receipt expiration rules ready"),
        "expiration_item_count": summary.get("expiration_item_count", 0),
        "critical_count": summary.get("critical_count", 0),
        "high_count": summary.get("high_count", 0),
        "medium_count": summary.get("medium_count", 0),
        "monitor_count": summary.get("monitor_count", 0),
        "recheck_required_count": summary.get("recheck_required_count", 0),
        "renewal_allowed_count": summary.get("renewal_allowed_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "priority_counts": summary.get("priority_counts", {}),
        "bucket_counts": summary.get("bucket_counts", {}),
        "expiration_state_counts": summary.get("expiration_state_counts", {}),
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
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
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_expiration_rules_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_expiration_rules_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_expiration_rules_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_expiration_rules_status_bridge()
    return {
        "id": "policy_change_approval_receipt_expiration_rules",
        "label": "Approval Receipt Expiration Rules",
        "title": "Approval Receipt Expiration Rules",
        "href": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "description": "Preview expiration, renewal, and recheck windows for approval receipt evidence.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 162",
        "category": "policy",
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_expiration_rules_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_expiration_rules_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "expiration_readiness",
            "title": "Expiration readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Approval receipt expiration rules ready"),
        },
        {
            "id": "expiration_items",
            "title": "Expiration items",
            "value": summary.get("expiration_item_count", 0),
            "label": "Vault items with expiration windows",
        },
        {
            "id": "recheck_required",
            "title": "Recheck required",
            "value": summary.get("recheck_required_count", 0),
            "label": "Need fresh review before reuse",
        },
        {
            "id": "renewal_allowed",
            "title": "Renewal allowed",
            "value": summary.get("renewal_allowed_count", 0),
            "label": "Can renew by preview rule",
        },
        {
            "id": "critical_high",
            "title": "Critical / high",
            "value": f"{summary.get('critical_count', 0)} / {summary.get('high_count', 0)}",
            "label": "Fast expiration lanes",
        },
        {
            "id": "no_real_enforcement",
            "title": "Real enforcement",
            "value": "No" if checks.get("no_real_expiration_enforced") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_expiration_rules",
        "title": "Approval Receipt Expiration Rules",
        "subtitle": "Previews expiration, renewal, and recheck windows before any real enforcement happens.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_EXPIRATION_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "expiration_preview_only": True,
        "renewal_preview_only": True,
        "recheck_preview_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_expiration_rules_html_section() -> str:
    section = build_policy_change_approval_receipt_expiration_rules_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-expiration-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-expiration-section" id="policy-change-approval-receipt-expiration-rules">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 162</p>
            <h2>{section.get('title', 'Approval Receipt Expiration Rules')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_EXPIRATION_ENDPOINT}">Open approval receipt expiration rules JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_EXPIRATION_ENDPOINT",
    "APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT",
    "EXPIRATION_RULES",
    "build_policy_change_approval_receipt_expiration_item",
    "build_policy_change_approval_receipt_expiration_rules_payload",
    "get_policy_change_approval_receipt_expiration_rules_payload",
    "build_policy_change_approval_receipt_expiration_rules_status_bridge",
    "get_policy_change_approval_receipt_expiration_rules_status_bridge",
    "build_policy_change_approval_receipt_expiration_rules_quick_action",
    "build_policy_change_approval_receipt_expiration_rules_unified_owner_section",
    "build_policy_change_approval_receipt_expiration_rules_html_section",
]
