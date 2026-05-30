
"""
PACK 155 - Policy Expiration Rules foundation.

This layer sits on top of Pack 154.

Pack 154 organizes simulated receipt previews into a vault/ledger index.
Pack 155 adds simulated expiration and staleness rules for those preview entries.

Important:
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
from typing import Any, Dict, List, Optional


PACK_ID = "PACK_155"
EXPIRATION_ENDPOINT = "/tower/policy-expiration-rules.json"
VAULT_PREVIEW_ENDPOINT = "/tower/policy-receipt-vault-preview.json"


# All windows are simulated. They describe what The Tower would use later.
# No real timers, jobs, or enforcement are created in this pack.
EXPIRATION_RULES: Dict[str, Dict[str, Any]] = {
    "critical_safety_stops": {
        "rule_id": "expiration.critical_safety_stop",
        "bucket": "critical_safety_stops",
        "ttl_minutes": 15,
        "review_action": "owner_review_required",
        "renewal_allowed": False,
        "stale_status": "expired_requires_owner_review",
        "owner_reason": "Critical safety stops get the shortest window because failed dependencies should not be trusted later without review.",
    },
    "containment_queue": {
        "rule_id": "expiration.containment_queue",
        "bucket": "containment_queue",
        "ttl_minutes": 30,
        "review_action": "containment_recheck_required",
        "renewal_allowed": False,
        "stale_status": "expired_requires_containment_recheck",
        "owner_reason": "Quarantined routes or actions must be rechecked before anything trusts them.",
    },
    "blocked_decisions": {
        "rule_id": "expiration.blocked_decision",
        "bucket": "blocked_decisions",
        "ttl_minutes": 60,
        "review_action": "block_review_required",
        "renewal_allowed": True,
        "stale_status": "stale_block_needs_review",
        "owner_reason": "Blocked decisions can remain blocked, but stale blocks should be reviewed before being reused as current evidence.",
    },
    "challenge_required": {
        "rule_id": "expiration.challenge_required",
        "bucket": "challenge_required",
        "ttl_minutes": 20,
        "review_action": "step_up_must_be_reissued",
        "renewal_allowed": False,
        "stale_status": "expired_step_up_challenge",
        "owner_reason": "Step-up challenges should expire quickly so old confirmations cannot be reused.",
    },
    "privacy_redactions": {
        "rule_id": "expiration.privacy_redaction",
        "bucket": "privacy_redactions",
        "ttl_minutes": 120,
        "review_action": "privacy_review_required",
        "renewal_allowed": True,
        "stale_status": "stale_privacy_redaction_needs_review",
        "owner_reason": "Redaction decisions can last longer, but private-data reveal conditions must still be reviewed.",
    },
    "monitor_only_allows": {
        "rule_id": "expiration.monitor_only_allow",
        "bucket": "monitor_only_allows",
        "ttl_minutes": 240,
        "review_action": "monitor_allow_refresh_required",
        "renewal_allowed": True,
        "stale_status": "stale_monitor_allow_needs_refresh",
        "owner_reason": "Monitor-only allows can be longer-lived because they do not grant real enforcement access.",
    },
    "review_queue": {
        "rule_id": "expiration.review_queue",
        "bucket": "review_queue",
        "ttl_minutes": 45,
        "review_action": "manual_review_required",
        "renewal_allowed": False,
        "stale_status": "expired_manual_review_required",
        "owner_reason": "Unknown preview entries should not stay fresh without human review.",
    },
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


def _load_pack_154_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_receipt_vault_preview")
        fn = getattr(mod, "build_policy_receipt_vault_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_154",
            "status": "review",
            "endpoint": VAULT_PREVIEW_ENDPOINT,
            "simulated_only": True,
            "real_enforcement_executed": False,
            "real_audit_written": False,
            "real_receipt_written": False,
            "load_error": str(exc),
            "summary": {
                "vault_entry_count": 0,
                "ledger_entry_count": 0,
                "receipt_preview_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 154 vault preview payload unavailable",
            },
            "vault_entries": [],
        }

    return {
        "pack_id": "PACK_154",
        "status": "review",
        "endpoint": VAULT_PREVIEW_ENDPOINT,
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "summary": {
            "vault_entry_count": 0,
            "ledger_entry_count": 0,
            "receipt_preview_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 154 vault preview payload unavailable",
        },
        "vault_entries": [],
    }


def get_expiration_rule_for_bucket(bucket: str) -> Dict[str, Any]:
    bucket = str(bucket or "review_queue")
    rule = EXPIRATION_RULES.get(bucket) or EXPIRATION_RULES["review_queue"]
    return copy.deepcopy(rule)


def _simulated_age_minutes_for_entry(entry: Dict[str, Any]) -> int:
    """
    Deterministic simulated age.

    This keeps tests stable and lets Pack 155 demonstrate:
    - fresh previews
    - warning previews
    - expired/stale previews

    No real clock mutation or persistence is used.
    """

    bucket = str(entry.get("bucket") or "")
    decision = str(entry.get("decision") or "")
    sequence = int(entry.get("sequence") or 1)

    if bucket == "critical_safety_stops":
        return 18
    if bucket == "containment_queue":
        return 31
    if bucket == "challenge_required":
        return 18
    if bucket == "blocked_decisions":
        return 50 + sequence
    if bucket == "privacy_redactions":
        return 100
    if bucket == "monitor_only_allows":
        return 60
    if decision == "allow":
        return 60
    return 40


def _expiration_state(age_minutes: int, ttl_minutes: int) -> str:
    if age_minutes >= ttl_minutes:
        return "expired"
    if age_minutes >= int(ttl_minutes * 0.75):
        return "warning"
    return "fresh"


def _next_action_for_state(state: str, rule: Dict[str, Any]) -> str:
    if state == "expired":
        return str(rule.get("review_action") or "owner_review_required")
    if state == "warning":
        return "review_soon"
    return "continue_monitoring"


def _owner_message_for_state(entry: Dict[str, Any], state: str, rule: Dict[str, Any]) -> str:
    decision = _safe_text(entry.get("decision"))
    bucket = _safe_text(entry.get("bucket"))
    scenario_id = _safe_text(entry.get("scenario_id"))

    if state == "expired":
        return f"{scenario_id} is expired for bucket {bucket}. Decision {decision} needs: {rule.get('review_action')}."
    if state == "warning":
        return f"{scenario_id} is close to expiring. Decision {decision} should be reviewed soon."
    return f"{scenario_id} is still fresh. Decision {decision} can remain monitor-only in this simulated preview."


def build_expiration_entry_from_vault_entry(entry: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 154 vault entry into one simulated expiration check.
    """

    entry = dict(entry or {})
    bucket = _safe_text(entry.get("bucket")) or "review_queue"
    rule = get_expiration_rule_for_bucket(bucket)

    created_at = _utc_now_dt()
    age_minutes = _simulated_age_minutes_for_entry(entry)
    ttl_minutes = int(rule.get("ttl_minutes") or 45)
    expires_at = created_at + datetime.timedelta(minutes=ttl_minutes)
    state = _expiration_state(age_minutes, ttl_minutes)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "vault_entry_id": entry.get("vault_entry_id"),
        "ledger_entry_id": entry.get("ledger_entry_id"),
        "bucket": bucket,
        "rule_id": rule.get("rule_id"),
        "decision": entry.get("decision"),
    }

    expiration_check_id = f"expiration_preview_{_stable_hash(identity, 18)}"

    return {
        "expiration_check_id": expiration_check_id,
        "sequence": sequence,
        "rule_id": rule.get("rule_id"),
        "bucket": bucket,
        "decision": _safe_text(entry.get("decision")),
        "severity": _safe_text(entry.get("severity")),
        "scenario_id": _safe_text(entry.get("scenario_id")),
        "matched_policy_id": _safe_text(entry.get("matched_policy_id")),
        "vault_entry_id": _safe_text(entry.get("vault_entry_id")),
        "ledger_entry_id": _safe_text(entry.get("ledger_entry_id")),
        "receipt_preview_id": _safe_text(entry.get("receipt_preview_id")),
        "ttl_minutes": ttl_minutes,
        "simulated_age_minutes": age_minutes,
        "expiration_state": state,
        "simulated_created_at": _iso(created_at),
        "simulated_expires_at": _iso(expires_at),
        "minutes_until_expiration": max(ttl_minutes - age_minutes, 0),
        "is_expired": state == "expired",
        "is_warning": state == "warning",
        "is_fresh": state == "fresh",
        "renewal_allowed": bool(rule.get("renewal_allowed", False)),
        "review_action": rule.get("review_action"),
        "stale_status": rule.get("stale_status"),
        "next_action": _next_action_for_state(state, rule),
        "owner_reason": _safe_text(rule.get("owner_reason")),
        "owner_message": _owner_message_for_state(entry, state, rule),
        "proof_bundle_hint": _safe_text(entry.get("proof_bundle_hint")),
        "soulaana_translation": _safe_text(entry.get("soulaana_translation")),
        "simulated_only": True,
        "real_expiration_enforced": False,
        "real_receipt_written": False,
        "real_audit_written": False,
        "real_enforcement_executed": False,
        "source_endpoint": VAULT_PREVIEW_ENDPOINT,
    }


def _count_by(entries: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for entry in entries:
        group_key = str(entry.get(key) or "unknown")
        counts[group_key] = counts.get(group_key, 0) + 1
    return counts


def _group_by(entries: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        group_key = str(entry.get(key) or "unknown")
        grouped.setdefault(group_key, []).append(entry)
    return grouped


def _build_expiration_owner_queue(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    state_rank = {
        "expired": 1,
        "warning": 2,
        "fresh": 3,
    }
    severity_rank = {
        "critical_safety": 1,
        "containment": 2,
        "blocked": 3,
        "challenge": 4,
        "privacy": 5,
        "monitor": 6,
        "review": 7,
    }

    sorted_entries = sorted(
        entries,
        key=lambda item: (
            state_rank.get(str(item.get("expiration_state")), 9),
            severity_rank.get(str(item.get("severity")), 9),
            item.get("sequence", 999),
        ),
    )

    queue = []
    for idx, entry in enumerate(sorted_entries, start=1):
        queue.append({
            "queue_position": idx,
            "expiration_check_id": entry.get("expiration_check_id"),
            "vault_entry_id": entry.get("vault_entry_id"),
            "ledger_entry_id": entry.get("ledger_entry_id"),
            "decision": entry.get("decision"),
            "severity": entry.get("severity"),
            "bucket": entry.get("bucket"),
            "expiration_state": entry.get("expiration_state"),
            "review_action": entry.get("review_action"),
            "next_action": entry.get("next_action"),
            "scenario_id": entry.get("scenario_id"),
            "matched_policy_id": entry.get("matched_policy_id"),
            "owner_message": entry.get("owner_message"),
            "simulated_only": True,
        })
    return queue


@lru_cache(maxsize=1)
def build_policy_expiration_rules_payload_cached() -> Dict[str, Any]:
    vault_payload = _load_pack_154_payload(force_refresh=False)
    vault_entries = vault_payload.get("vault_entries", [])
    if not isinstance(vault_entries, list):
        vault_entries = []

    expiration_entries: List[Dict[str, Any]] = []
    for idx, entry in enumerate(vault_entries, start=1):
        if isinstance(entry, dict):
            expiration_entries.append(build_expiration_entry_from_vault_entry(entry, sequence=idx))

    state_counts = _count_by(expiration_entries, "expiration_state")
    bucket_counts = _count_by(expiration_entries, "bucket")
    decision_counts = _count_by(expiration_entries, "decision")
    review_action_counts = _count_by(expiration_entries, "review_action")
    next_action_counts = _count_by(expiration_entries, "next_action")

    by_state = _group_by(expiration_entries, "expiration_state")
    by_bucket = _group_by(expiration_entries, "bucket")
    by_rule = _group_by(expiration_entries, "rule_id")
    by_next_action = _group_by(expiration_entries, "next_action")

    owner_review_queue = _build_expiration_owner_queue(expiration_entries)

    required_states = {"fresh", "warning", "expired"}
    observed_states = set(state_counts.keys())

    required_buckets = {
        "blocked_decisions",
        "challenge_required",
        "privacy_redactions",
        "containment_queue",
        "critical_safety_stops",
        "monitor_only_allows",
    }
    observed_buckets = set(bucket_counts.keys())

    readiness_checks = {
        "pack_154_ready": vault_payload.get("status") == "ready",
        "has_expiration_entries": len(expiration_entries) >= 1,
        "entry_count_matches_vault_entries": len(expiration_entries) == len(vault_entries),
        "all_simulated_only": all(entry.get("simulated_only") is True for entry in expiration_entries),
        "no_real_expiration_enforced": all(entry.get("real_expiration_enforced") is False for entry in expiration_entries),
        "no_real_receipt_written": all(entry.get("real_receipt_written") is False for entry in expiration_entries),
        "no_real_audit_written": all(entry.get("real_audit_written") is False for entry in expiration_entries),
        "no_real_enforcement": all(entry.get("real_enforcement_executed") is False for entry in expiration_entries),
        "all_expiration_ids_present": all(bool(entry.get("expiration_check_id")) for entry in expiration_entries),
        "all_rules_present": all(bool(entry.get("rule_id")) for entry in expiration_entries),
        "all_ttl_present": all(int(entry.get("ttl_minutes") or 0) > 0 for entry in expiration_entries),
        "state_index_present": bool(by_state),
        "bucket_index_present": bool(by_bucket),
        "rule_index_present": bool(by_rule),
        "next_action_index_present": bool(by_next_action),
        "owner_review_queue_present": len(owner_review_queue) == len(expiration_entries),
        "required_state_coverage": required_states.issubset(observed_states),
        "required_bucket_coverage": required_buckets.issubset(observed_buckets),
        "endpoint": EXPIRATION_ENDPOINT,
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
        "pack_number": 155,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Expiration Rules foundation",
        "endpoint": EXPIRATION_ENDPOINT,
        "source_endpoint": VAULT_PREVIEW_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_154": {
            "status": vault_payload.get("status"),
            "readiness_score": vault_payload.get("summary", {}).get("readiness_score"),
            "vault_entry_count": vault_payload.get("summary", {}).get("vault_entry_count"),
            "ledger_entry_count": vault_payload.get("summary", {}).get("ledger_entry_count"),
            "receipt_preview_count": vault_payload.get("summary", {}).get("receipt_preview_count"),
            "bucket_counts": vault_payload.get("summary", {}).get("bucket_counts", {}),
        },
        "summary": {
            "expiration_entry_count": len(expiration_entries),
            "owner_review_queue_count": len(owner_review_queue),
            "expiration_rule_count": len(EXPIRATION_RULES),
            "expired_count": state_counts.get("expired", 0),
            "warning_count": state_counts.get("warning", 0),
            "fresh_count": state_counts.get("fresh", 0),
            "state_counts": state_counts,
            "bucket_counts": bucket_counts,
            "decision_counts": decision_counts,
            "review_action_counts": review_action_counts,
            "next_action_counts": next_action_counts,
            "observed_states": sorted(observed_states),
            "required_states": sorted(required_states),
            "observed_buckets": sorted(observed_buckets),
            "required_buckets": sorted(required_buckets),
            "readiness_score": readiness_score,
            "readiness_label": "Policy expiration rules ready" if readiness_score == 100 else "Policy expiration rules need review",
        },
        "readiness_checks": readiness_checks,
        "expiration_rules": copy.deepcopy(EXPIRATION_RULES),
        "expiration_entries": expiration_entries,
        "indexes": {
            "by_state": by_state,
            "by_bucket": by_bucket,
            "by_rule": by_rule,
            "by_next_action": by_next_action,
        },
        "owner_review_queue": owner_review_queue,
        "quick_action": {
            "id": "policy_expiration_rules",
            "label": "Policy Expiration Rules",
            "href": EXPIRATION_ENDPOINT,
            "description": "Preview staleness and expiration rules for policy receipt entries.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_expiration_rules",
            "title": "Policy Expiration Rules",
            "subtitle": "Shows when simulated policy receipt entries become stale, expired, or need owner review.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": EXPIRATION_ENDPOINT,
        },
    }


def build_policy_expiration_rules_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_expiration_rules_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_expiration_rules_payload_cached())


def get_policy_expiration_rules_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_expiration_rules_payload(force_refresh=force_refresh)


def build_policy_expiration_rules_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_expiration_rules_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 155,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", EXPIRATION_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", VAULT_PREVIEW_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy expiration rules ready"),
        "expiration_entry_count": summary.get("expiration_entry_count", 0),
        "expiration_rule_count": summary.get("expiration_rule_count", 0),
        "owner_review_queue_count": summary.get("owner_review_queue_count", 0),
        "expired_count": summary.get("expired_count", 0),
        "warning_count": summary.get("warning_count", 0),
        "fresh_count": summary.get("fresh_count", 0),
        "state_counts": summary.get("state_counts", {}),
        "bucket_counts": summary.get("bucket_counts", {}),
        "review_action_counts": summary.get("review_action_counts", {}),
        "simulated_only": True,
        "real_expiration_enforced": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_expiration_rules_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_expiration_rules_status_bridge(force_refresh=force_refresh)


def build_policy_expiration_rules_quick_action() -> Dict[str, Any]:
    bridge = build_policy_expiration_rules_status_bridge()
    return {
        "id": "policy_expiration_rules",
        "label": "Policy Expiration Rules",
        "title": "Policy Expiration Rules",
        "href": EXPIRATION_ENDPOINT,
        "endpoint": EXPIRATION_ENDPOINT,
        "description": "Preview when policy receipt entries become stale or need owner review.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 155",
        "category": "policy",
        "simulated_only": True,
    }


def build_policy_expiration_rules_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_expiration_rules_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "expiration_readiness",
            "title": "Expiration readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy expiration rules ready"),
        },
        {
            "id": "expiration_entries",
            "title": "Expiration entries",
            "value": summary.get("expiration_entry_count", 0),
            "label": "Simulated vault entries checked",
        },
        {
            "id": "expired_count",
            "title": "Expired",
            "value": summary.get("expired_count", 0),
            "label": "Need review now",
        },
        {
            "id": "warning_count",
            "title": "Warning",
            "value": summary.get("warning_count", 0),
            "label": "Review soon",
        },
        {
            "id": "fresh_count",
            "title": "Fresh",
            "value": summary.get("fresh_count", 0),
            "label": "Continue monitoring",
        },
        {
            "id": "no_real_enforcement",
            "title": "Real expiration enforced",
            "value": "No" if checks.get("no_real_expiration_enforced") else "Review",
            "label": "Simulation only",
        },
    ]

    return {
        "section_id": "policy_expiration_rules",
        "title": "Policy Expiration Rules",
        "subtitle": "This previews when policy receipt entries become stale, expired, or need owner review.",
        "status": payload.get("status", "ready"),
        "href": EXPIRATION_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "cached_non_recursive": True,
    }


def build_policy_expiration_rules_html_section() -> str:
    section = build_policy_expiration_rules_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-expiration-rules-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-expiration-rules-section" id="policy-expiration-rules">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 155</p>
            <h2>{section.get('title', 'Policy Expiration Rules')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{EXPIRATION_ENDPOINT}">Open expiration rules JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "EXPIRATION_ENDPOINT",
    "VAULT_PREVIEW_ENDPOINT",
    "EXPIRATION_RULES",
    "get_expiration_rule_for_bucket",
    "build_expiration_entry_from_vault_entry",
    "build_policy_expiration_rules_payload",
    "get_policy_expiration_rules_payload",
    "build_policy_expiration_rules_status_bridge",
    "get_policy_expiration_rules_status_bridge",
    "build_policy_expiration_rules_quick_action",
    "build_policy_expiration_rules_unified_owner_section",
    "build_policy_expiration_rules_html_section",
]
