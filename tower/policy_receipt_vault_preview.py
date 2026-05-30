
"""
PACK 154 - Policy Receipt Vault Preview / Simulated Ledger Index.

This layer sits on top of Pack 153.

Pack 153 creates trace + receipt previews.
Pack 154 organizes those receipt previews into a simulated vault index.

Important:
- no real receipt write
- no real audit write
- no real enforcement
- no mutation
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
from typing import Any, Dict, List, Tuple


PACK_ID = "PACK_154"
VAULT_PREVIEW_ENDPOINT = "/tower/policy-receipt-vault-preview.json"
TRACE_PREVIEW_ENDPOINT = "/tower/policy-decision-trace-preview.json"


VAULT_BUCKETS = {
    "deny": "blocked_decisions",
    "step_up": "challenge_required",
    "redact": "privacy_redactions",
    "quarantine": "containment_queue",
    "fail_closed": "critical_safety_stops",
    "allow": "monitor_only_allows",
}


SEVERITY_SORT = {
    "critical_safety": 1,
    "containment": 2,
    "blocked": 3,
    "challenge": 4,
    "privacy": 5,
    "monitor": 6,
    "review": 7,
}


def _utc_now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


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


def _load_pack_153_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_decision_trace_receipt_preview")
        fn = getattr(mod, "build_policy_decision_trace_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_153",
            "status": "review",
            "endpoint": TRACE_PREVIEW_ENDPOINT,
            "simulated_only": True,
            "real_enforcement_executed": False,
            "real_audit_written": False,
            "real_receipt_written": False,
            "load_error": str(exc),
            "summary": {
                "trace_count": 0,
                "receipt_preview_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 153 trace preview payload unavailable",
            },
            "traces": [],
        }

    return {
        "pack_id": "PACK_153",
        "status": "review",
        "endpoint": TRACE_PREVIEW_ENDPOINT,
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "summary": {
            "trace_count": 0,
            "receipt_preview_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 153 trace preview payload unavailable",
        },
        "traces": [],
    }


def _vault_bucket_for_decision(decision: str) -> str:
    return VAULT_BUCKETS.get(str(decision or "").lower(), "review_queue")


def _ledger_status_for_decision(decision: str) -> str:
    decision = str(decision or "").lower()
    if decision == "allow":
        return "monitor_indexed"
    if decision == "deny":
        return "blocked_indexed"
    if decision == "step_up":
        return "challenge_indexed"
    if decision == "redact":
        return "privacy_indexed"
    if decision == "quarantine":
        return "containment_indexed"
    if decision == "fail_closed":
        return "critical_stop_indexed"
    return "review_indexed"


def _proof_bundle_hint(decision: str) -> str:
    decision = str(decision or "").lower()
    if decision == "allow":
        return "Monitor-only proof bundle can include policy id, explicit allow reason, and source scenario."
    if decision == "deny":
        return "Denial proof bundle should include policy id, blocked action, owner reason, and Soulaana explanation."
    if decision == "step_up":
        return "Step-up proof bundle should include challenge reason, required confirmation, and unresolved status."
    if decision == "redact":
        return "Privacy proof bundle should include redaction reason and reveal-approval requirement."
    if decision == "quarantine":
        return "Containment proof bundle should include route/action context, quarantine reason, and owner review path."
    if decision == "fail_closed":
        return "Critical safety proof bundle should include dependency failure and why fail-closed was safer."
    return "Review proof bundle should include policy match, decision, reason, and source trace."


def build_vault_entry_from_trace(trace: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 153 trace into one simulated receipt vault index entry.
    """

    trace = dict(trace or {})
    receipt = trace.get("receipt_preview", {})
    if not isinstance(receipt, dict):
        receipt = {}

    decision = _safe_text(trace.get("decision")).lower() or "unknown"
    severity = _safe_text(trace.get("severity")) or "review"
    scenario_id = _safe_text(trace.get("scenario_id")) or f"scenario_{sequence}"
    matched_policy_id = _safe_text(trace.get("matched_policy_id")) or "unknown.policy"
    trace_id = _safe_text(trace.get("trace_id")) or f"trace_preview_missing_{sequence}"
    receipt_preview_id = _safe_text(receipt.get("receipt_preview_id")) or f"receipt_preview_missing_{sequence}"

    bucket = _vault_bucket_for_decision(decision)

    entry_identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "trace_id": trace_id,
        "receipt_preview_id": receipt_preview_id,
        "scenario_id": scenario_id,
        "matched_policy_id": matched_policy_id,
        "decision": decision,
    }

    ledger_entry_id = f"ledger_preview_{_stable_hash(entry_identity, 18)}"
    vault_entry_id = f"vault_preview_{_stable_hash({**entry_identity, 'bucket': bucket}, 18)}"

    return {
        "vault_entry_id": vault_entry_id,
        "ledger_entry_id": ledger_entry_id,
        "sequence": sequence,
        "bucket": bucket,
        "ledger_status": _ledger_status_for_decision(decision),
        "decision": decision,
        "severity": severity,
        "severity_rank": SEVERITY_SORT.get(severity, 99),
        "scenario_id": scenario_id,
        "scenario_label": _safe_text(trace.get("scenario_label")),
        "matched_policy_id": matched_policy_id,
        "effect": _safe_text(trace.get("effect")) or decision,
        "trace_id": trace_id,
        "receipt_preview_id": receipt_preview_id,
        "receipt_type": _safe_text(receipt.get("receipt_type")) or "unknown_receipt_type",
        "receipt_status": _safe_text(receipt.get("receipt_status")) or "preview_only",
        "receipt_action": _safe_text(receipt.get("receipt_action")) or "record_preview",
        "owner_reason": _safe_text(trace.get("owner_reason")),
        "owner_reason_prompt": _safe_text(trace.get("owner_reason_prompt")),
        "soulaana_translation": _safe_text(trace.get("soulaana_translation")),
        "plain_language_trace": _safe_text(trace.get("plain_language_trace")),
        "proof_bundle_hint": _proof_bundle_hint(decision),
        "simulated_only": True,
        "real_receipt_written": False,
        "real_audit_written": False,
        "real_enforcement_executed": False,
        "source_endpoint": TRACE_PREVIEW_ENDPOINT,
    }


def _group_entries(entries: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        group_key = str(entry.get(key) or "unknown")
        grouped.setdefault(group_key, []).append(entry)
    return grouped


def _count_by(entries: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for entry in entries:
        group_key = str(entry.get(key) or "unknown")
        counts[group_key] = counts.get(group_key, 0) + 1
    return counts


def _build_owner_review_queue(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a simulated owner review queue sorted by safety importance.
    """
    sorted_entries = sorted(
        entries,
        key=lambda item: (
            item.get("severity_rank", 99),
            item.get("sequence", 999),
        ),
    )

    queue = []
    for idx, entry in enumerate(sorted_entries, start=1):
        queue.append({
            "queue_position": idx,
            "vault_entry_id": entry.get("vault_entry_id"),
            "ledger_entry_id": entry.get("ledger_entry_id"),
            "decision": entry.get("decision"),
            "severity": entry.get("severity"),
            "bucket": entry.get("bucket"),
            "scenario_id": entry.get("scenario_id"),
            "matched_policy_id": entry.get("matched_policy_id"),
            "owner_reason_prompt": entry.get("owner_reason_prompt"),
            "simulated_only": True,
        })
    return queue


@lru_cache(maxsize=1)
def build_policy_receipt_vault_preview_payload_cached() -> Dict[str, Any]:
    trace_payload = _load_pack_153_payload(force_refresh=False)
    traces = trace_payload.get("traces", [])
    if not isinstance(traces, list):
        traces = []

    entries: List[Dict[str, Any]] = []
    for idx, trace in enumerate(traces, start=1):
        if isinstance(trace, dict):
            entries.append(build_vault_entry_from_trace(trace, sequence=idx))

    decision_counts = _count_by(entries, "decision")
    severity_counts = _count_by(entries, "severity")
    bucket_counts = _count_by(entries, "bucket")
    receipt_type_counts = _count_by(entries, "receipt_type")
    ledger_status_counts = _count_by(entries, "ledger_status")

    required_decisions = {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
    observed_decisions = set(decision_counts.keys())

    bucket_index = _group_entries(entries, "bucket")
    decision_index = _group_entries(entries, "decision")
    severity_index = _group_entries(entries, "severity")
    policy_index = _group_entries(entries, "matched_policy_id")

    owner_review_queue = _build_owner_review_queue(entries)

    readiness_checks = {
        "pack_153_ready": trace_payload.get("status") == "ready",
        "has_entries": len(entries) >= 1,
        "entry_count_matches_traces": len(entries) == len(traces),
        "all_simulated_only": all(entry.get("simulated_only") is True for entry in entries),
        "no_real_receipt_written": all(entry.get("real_receipt_written") is False for entry in entries),
        "no_real_audit_written": all(entry.get("real_audit_written") is False for entry in entries),
        "no_real_enforcement": all(entry.get("real_enforcement_executed") is False for entry in entries),
        "all_vault_ids_present": all(bool(entry.get("vault_entry_id")) for entry in entries),
        "all_ledger_ids_present": all(bool(entry.get("ledger_entry_id")) for entry in entries),
        "all_receipt_preview_ids_present": all(bool(entry.get("receipt_preview_id")) for entry in entries),
        "bucket_index_present": bool(bucket_index),
        "decision_index_present": bool(decision_index),
        "severity_index_present": bool(severity_index),
        "policy_index_present": bool(policy_index),
        "owner_review_queue_present": len(owner_review_queue) == len(entries),
        "required_decision_coverage": required_decisions.issubset(observed_decisions),
        "endpoint": VAULT_PREVIEW_ENDPOINT,
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
        "pack_number": 154,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Receipt Vault Preview / Simulated Ledger Index",
        "endpoint": VAULT_PREVIEW_ENDPOINT,
        "source_endpoint": TRACE_PREVIEW_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_153": {
            "status": trace_payload.get("status"),
            "readiness_score": trace_payload.get("summary", {}).get("readiness_score"),
            "trace_count": trace_payload.get("summary", {}).get("trace_count"),
            "receipt_preview_count": trace_payload.get("summary", {}).get("receipt_preview_count"),
            "decision_counts": trace_payload.get("summary", {}).get("decision_counts", {}),
        },
        "summary": {
            "vault_entry_count": len(entries),
            "ledger_entry_count": len(entries),
            "receipt_preview_count": len([entry for entry in entries if entry.get("receipt_preview_id")]),
            "owner_review_queue_count": len(owner_review_queue),
            "bucket_count": len(bucket_index),
            "decision_counts": decision_counts,
            "severity_counts": severity_counts,
            "bucket_counts": bucket_counts,
            "receipt_type_counts": receipt_type_counts,
            "ledger_status_counts": ledger_status_counts,
            "observed_decisions": sorted(observed_decisions),
            "required_decisions": sorted(required_decisions),
            "readiness_score": readiness_score,
            "readiness_label": "Policy receipt vault preview ready" if readiness_score == 100 else "Policy receipt vault preview needs review",
        },
        "readiness_checks": readiness_checks,
        "vault_entries": entries,
        "indexes": {
            "by_bucket": bucket_index,
            "by_decision": decision_index,
            "by_severity": severity_index,
            "by_policy": policy_index,
        },
        "owner_review_queue": owner_review_queue,
        "quick_action": {
            "id": "policy_receipt_vault_preview",
            "label": "Policy Receipt Vault Preview",
            "href": VAULT_PREVIEW_ENDPOINT,
            "description": "View the simulated vault index for future policy receipts.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_receipt_vault_preview",
            "title": "Policy Receipt Vault Preview",
            "subtitle": "Organizes simulated receipt previews into a vault-style ledger index.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": VAULT_PREVIEW_ENDPOINT,
        },
    }


def build_policy_receipt_vault_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_receipt_vault_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_receipt_vault_preview_payload_cached())


def get_policy_receipt_vault_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_receipt_vault_preview_payload(force_refresh=force_refresh)


def build_policy_receipt_vault_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_receipt_vault_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 154,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", VAULT_PREVIEW_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", TRACE_PREVIEW_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy receipt vault preview ready"),
        "vault_entry_count": summary.get("vault_entry_count", 0),
        "ledger_entry_count": summary.get("ledger_entry_count", 0),
        "receipt_preview_count": summary.get("receipt_preview_count", 0),
        "owner_review_queue_count": summary.get("owner_review_queue_count", 0),
        "bucket_count": summary.get("bucket_count", 0),
        "decision_counts": summary.get("decision_counts", {}),
        "bucket_counts": summary.get("bucket_counts", {}),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_receipt_vault_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_receipt_vault_preview_status_bridge(force_refresh=force_refresh)


def build_policy_receipt_vault_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_receipt_vault_preview_status_bridge()
    return {
        "id": "policy_receipt_vault_preview",
        "label": "Policy Receipt Vault Preview",
        "title": "Policy Receipt Vault Preview",
        "href": VAULT_PREVIEW_ENDPOINT,
        "endpoint": VAULT_PREVIEW_ENDPOINT,
        "description": "View the simulated vault index for future policy receipts.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 154",
        "category": "policy",
        "simulated_only": True,
    }


def build_policy_receipt_vault_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_receipt_vault_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "vault_readiness",
            "title": "Vault preview readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy receipt vault preview ready"),
        },
        {
            "id": "vault_entries",
            "title": "Vault entries",
            "value": summary.get("vault_entry_count", 0),
            "label": "Simulated receipt entries indexed",
        },
        {
            "id": "ledger_entries",
            "title": "Ledger entries",
            "value": summary.get("ledger_entry_count", 0),
            "label": "Preview ledger rows prepared",
        },
        {
            "id": "owner_queue",
            "title": "Owner review queue",
            "value": summary.get("owner_review_queue_count", 0),
            "label": "Sorted by safety importance",
        },
        {
            "id": "bucket_count",
            "title": "Vault buckets",
            "value": summary.get("bucket_count", 0),
            "label": ", ".join(sorted(summary.get("bucket_counts", {}).keys())),
        },
        {
            "id": "no_real_writes",
            "title": "Real writes",
            "value": "No" if checks.get("no_real_receipt_written") and checks.get("no_real_audit_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_receipt_vault_preview",
        "title": "Policy Receipt Vault Preview",
        "subtitle": "This organizes receipt previews into a simulated vault/ledger index without writing real records.",
        "status": payload.get("status", "ready"),
        "href": VAULT_PREVIEW_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "cached_non_recursive": True,
    }


def build_policy_receipt_vault_preview_html_section() -> str:
    section = build_policy_receipt_vault_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-receipt-vault-preview-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-receipt-vault-preview-section" id="policy-receipt-vault-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 154</p>
            <h2>{section.get('title', 'Policy Receipt Vault Preview')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{VAULT_PREVIEW_ENDPOINT}">Open vault preview JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "VAULT_PREVIEW_ENDPOINT",
    "TRACE_PREVIEW_ENDPOINT",
    "build_vault_entry_from_trace",
    "build_policy_receipt_vault_preview_payload",
    "get_policy_receipt_vault_preview_payload",
    "build_policy_receipt_vault_preview_status_bridge",
    "get_policy_receipt_vault_preview_status_bridge",
    "build_policy_receipt_vault_preview_quick_action",
    "build_policy_receipt_vault_preview_unified_owner_section",
    "build_policy_receipt_vault_preview_html_section",
]
