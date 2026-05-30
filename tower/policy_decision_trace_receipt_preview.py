
"""
PACK 153 - Policy Decision Trace / Receipt Preview layer.

This layer sits on top of Pack 152 Policy Simulation Mode.

It creates a clear "what would be logged later" preview for each simulated
decision without enforcing policy and without writing real audit receipts.

Important safety rules:
- simulated-only
- no real enforcement
- no real receipt write
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
from typing import Any, Dict, List


PACK_ID = "PACK_153"
TRACE_PREVIEW_ENDPOINT = "/tower/policy-decision-trace-preview.json"
SIMULATION_ENDPOINT = "/tower/policy-simulation-mode.json"


DECISION_SEVERITY = {
    "allow": "monitor",
    "deny": "blocked",
    "step_up": "challenge",
    "redact": "privacy",
    "quarantine": "containment",
    "fail_closed": "critical_safety",
}


DECISION_TITLES = {
    "allow": "Allowed in simulation",
    "deny": "Denied in simulation",
    "step_up": "Step-up required in simulation",
    "redact": "Redacted in simulation",
    "quarantine": "Quarantined in simulation",
    "fail_closed": "Failed closed in simulation",
}


def _utc_now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def _stable_hash(value: Any, length: int = 16) -> str:
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


def _load_pack_152_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_simulation_mode")
        fn = getattr(mod, "build_policy_simulation_mode_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_152",
            "status": "review",
            "endpoint": SIMULATION_ENDPOINT,
            "simulated_only": True,
            "real_enforcement_executed": False,
            "load_error": str(exc),
            "summary": {
                "scenario_count": 0,
                "decision_counts": {},
                "readiness_score": 0,
                "readiness_label": "Pack 152 simulation payload unavailable",
            },
            "scenarios": [],
        }

    return {
        "pack_id": "PACK_152",
        "status": "review",
        "endpoint": SIMULATION_ENDPOINT,
        "simulated_only": True,
        "real_enforcement_executed": False,
        "summary": {
            "scenario_count": 0,
            "decision_counts": {},
            "readiness_score": 0,
            "readiness_label": "Pack 152 simulation payload unavailable",
        },
        "scenarios": [],
    }


def _receipt_action_for_decision(decision: str) -> str:
    decision = str(decision or "").lower()
    if decision == "allow":
        return "record_monitor_only_allow_preview"
    if decision == "deny":
        return "record_denial_preview"
    if decision == "step_up":
        return "record_step_up_challenge_preview"
    if decision == "redact":
        return "record_privacy_redaction_preview"
    if decision == "quarantine":
        return "record_quarantine_preview"
    if decision == "fail_closed":
        return "record_fail_closed_preview"
    return "record_unknown_policy_decision_preview"


def _owner_reason_prompt_for_decision(decision: str) -> str:
    decision = str(decision or "").lower()
    if decision == "allow":
        return "Owner note optional: confirm why this request is allowed to proceed in monitor-only mode."
    if decision == "deny":
        return "Owner note required later: confirm why this request should stay blocked."
    if decision == "step_up":
        return "Owner note required later: explain why extra confirmation is needed before continuing."
    if decision == "redact":
        return "Owner note required later: explain why private data must remain hidden unless approved."
    if decision == "quarantine":
        return "Owner note required later: explain why this request belongs in containment."
    if decision == "fail_closed":
        return "Owner note required later: explain the failed dependency or unsafe state that forced stop-closed."
    return "Owner note required later: explain the policy decision."


def _plain_language_trace(row: Dict[str, Any]) -> str:
    decision = _safe_text(row.get("decision"))
    policy_id = _safe_text(row.get("matched_policy_id"))
    label = _safe_text(row.get("label"))
    owner_reason = _safe_text(row.get("owner_reason"))

    if decision == "allow":
        return f"{label}: The Tower would allow this in monitor-only mode because {owner_reason}"
    if decision == "deny":
        return f"{label}: The Tower would block this because policy {policy_id} matched. Reason: {owner_reason}"
    if decision == "step_up":
        return f"{label}: The Tower would pause and ask for extra confirmation because policy {policy_id} matched."
    if decision == "redact":
        return f"{label}: The Tower would hide sensitive details first because policy {policy_id} matched."
    if decision == "quarantine":
        return f"{label}: The Tower would place this in containment because policy {policy_id} matched."
    if decision == "fail_closed":
        return f"{label}: The Tower would stop closed because policy {policy_id} says a failed dependency is not safe to ignore."

    return f"{label}: The Tower would create a policy receipt preview for decision {decision}."


def build_trace_receipt_preview_for_decision(row: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Build one trace + receipt preview from one Pack 152 simulated decision row.
    """

    row = dict(row or {})
    decision = _safe_text(row.get("decision")).lower() or "unknown"
    scenario_id = _safe_text(row.get("scenario_id")) or f"scenario_{sequence}"
    matched_policy_id = _safe_text(row.get("matched_policy_id")) or "unknown.policy"
    receipt_type = _safe_text(row.get("receipt_type")) or "policy_decision_preview"
    effect = _safe_text(row.get("effect")) or decision

    base_identity = {
        "pack": PACK_ID,
        "scenario_id": scenario_id,
        "matched_policy_id": matched_policy_id,
        "decision": decision,
        "sequence": sequence,
    }

    trace_id = f"trace_preview_{_stable_hash(base_identity, 18)}"
    receipt_preview_id = f"receipt_preview_{_stable_hash({**base_identity, 'receipt_type': receipt_type}, 18)}"

    receipt_preview = {
        "receipt_preview_id": receipt_preview_id,
        "receipt_type": receipt_type,
        "would_write_receipt": True,
        "real_receipt_written": False,
        "simulated_only": True,
        "receipt_action": _receipt_action_for_decision(decision),
        "receipt_status": "preview_only",
        "required_fields_preview": {
            "scenario_id": scenario_id,
            "decision": decision,
            "matched_policy_id": matched_policy_id,
            "effect": effect,
            "enforcement_mode": "simulation_only",
            "owner_reason": _safe_text(row.get("owner_reason")),
            "owner_reason_prompt": _owner_reason_prompt_for_decision(decision),
            "soulaana_translation": _safe_text(row.get("soulaana_translation")),
            "input_summary": row.get("input_summary", {}),
        },
    }

    return {
        "trace_id": trace_id,
        "sequence": sequence,
        "scenario_id": scenario_id,
        "scenario_label": _safe_text(row.get("label")),
        "decision": decision,
        "decision_title": DECISION_TITLES.get(decision, "Unknown policy decision"),
        "severity": DECISION_SEVERITY.get(decision, "review"),
        "matched_policy_id": matched_policy_id,
        "effect": effect,
        "enforcement_mode": "simulation_only",
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "trace_steps": [
            {
                "step": 1,
                "name": "receive_simulated_request",
                "status": "preview",
                "detail": "Pack 153 received a Pack 152 simulated scenario result.",
            },
            {
                "step": 2,
                "name": "match_policy",
                "status": "preview",
                "detail": f"Matched policy: {matched_policy_id}",
            },
            {
                "step": 3,
                "name": "choose_decision",
                "status": "preview",
                "detail": f"Decision preview: {decision}",
            },
            {
                "step": 4,
                "name": "prepare_receipt_preview",
                "status": "preview",
                "detail": f"Receipt preview type: {receipt_type}",
            },
            {
                "step": 5,
                "name": "hold_before_real_enforcement",
                "status": "safe_stop",
                "detail": "No real enforcement or receipt writing happened.",
            },
        ],
        "plain_language_trace": _plain_language_trace(row),
        "owner_reason": _safe_text(row.get("owner_reason")),
        "owner_reason_prompt": _owner_reason_prompt_for_decision(decision),
        "soulaana_translation": _safe_text(row.get("soulaana_translation")),
        "receipt_preview": receipt_preview,
        "input_summary": row.get("input_summary", {}),
    }


@lru_cache(maxsize=1)
def build_policy_decision_trace_preview_payload_cached() -> Dict[str, Any]:
    simulation_payload = _load_pack_152_payload(force_refresh=False)
    scenario_rows = simulation_payload.get("scenarios", [])
    if not isinstance(scenario_rows, list):
        scenario_rows = []

    traces: List[Dict[str, Any]] = []
    for idx, row in enumerate(scenario_rows, start=1):
        if isinstance(row, dict):
            traces.append(build_trace_receipt_preview_for_decision(row, sequence=idx))

    decision_counts: Dict[str, int] = {}
    severity_counts: Dict[str, int] = {}
    receipt_type_counts: Dict[str, int] = {}

    for trace in traces:
        decision = str(trace.get("decision") or "unknown")
        severity = str(trace.get("severity") or "review")
        receipt_type = str(trace.get("receipt_preview", {}).get("receipt_type") or "unknown")

        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        receipt_type_counts[receipt_type] = receipt_type_counts.get(receipt_type, 0) + 1

    required_decisions = {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
    observed_decisions = set(decision_counts.keys())

    readiness_checks = {
        "pack_152_ready": simulation_payload.get("status") == "ready",
        "has_traces": len(traces) >= 1,
        "trace_count_matches_scenarios": len(traces) == len(scenario_rows),
        "all_simulated_only": all(trace.get("simulated_only") is True for trace in traces),
        "no_real_enforcement": all(trace.get("real_enforcement_executed") is False for trace in traces),
        "no_real_audit_written": all(trace.get("real_audit_written") is False for trace in traces),
        "no_real_receipt_written": all(trace.get("real_receipt_written") is False for trace in traces),
        "all_receipt_previews_present": all(bool(trace.get("receipt_preview")) for trace in traces),
        "all_trace_ids_present": all(bool(trace.get("trace_id")) for trace in traces),
        "required_decision_coverage": required_decisions.issubset(observed_decisions),
        "endpoint": TRACE_PREVIEW_ENDPOINT,
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
        "pack_number": 153,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Decision Trace / Receipt Preview layer",
        "endpoint": TRACE_PREVIEW_ENDPOINT,
        "source_endpoint": SIMULATION_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_152": {
            "status": simulation_payload.get("status"),
            "readiness_score": simulation_payload.get("summary", {}).get("readiness_score"),
            "scenario_count": simulation_payload.get("summary", {}).get("scenario_count"),
            "decision_counts": simulation_payload.get("summary", {}).get("decision_counts", {}),
        },
        "summary": {
            "trace_count": len(traces),
            "receipt_preview_count": len([t for t in traces if t.get("receipt_preview")]),
            "decision_counts": decision_counts,
            "severity_counts": severity_counts,
            "receipt_type_counts": receipt_type_counts,
            "observed_decisions": sorted(observed_decisions),
            "required_decisions": sorted(required_decisions),
            "readiness_score": readiness_score,
            "readiness_label": "Policy decision trace previews ready" if readiness_score == 100 else "Policy decision trace previews need review",
        },
        "readiness_checks": readiness_checks,
        "traces": traces,
        "quick_action": {
            "id": "policy_decision_trace_preview",
            "label": "Policy Decision Trace Preview",
            "href": TRACE_PREVIEW_ENDPOINT,
            "description": "Preview the policy receipt trail before real enforcement exists.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_decision_trace_preview",
            "title": "Policy Decision Trace Preview",
            "subtitle": "Shows what The Tower would log later for each simulated policy decision.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": TRACE_PREVIEW_ENDPOINT,
        },
    }


def build_policy_decision_trace_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_decision_trace_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_decision_trace_preview_payload_cached())


def get_policy_decision_trace_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_decision_trace_preview_payload(force_refresh=force_refresh)


def build_policy_decision_trace_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_decision_trace_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 153,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", TRACE_PREVIEW_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", SIMULATION_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy decision trace previews ready"),
        "trace_count": summary.get("trace_count", 0),
        "receipt_preview_count": summary.get("receipt_preview_count", 0),
        "decision_counts": summary.get("decision_counts", {}),
        "simulated_only": True,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_decision_trace_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_decision_trace_preview_status_bridge(force_refresh=force_refresh)


def build_policy_decision_trace_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_decision_trace_preview_status_bridge()
    return {
        "id": "policy_decision_trace_preview",
        "label": "Policy Decision Trace Preview",
        "title": "Policy Decision Trace Preview",
        "href": TRACE_PREVIEW_ENDPOINT,
        "endpoint": TRACE_PREVIEW_ENDPOINT,
        "description": "Preview what receipt trail The Tower would create for simulated policy decisions.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 153",
        "category": "policy",
        "simulated_only": True,
    }


def build_policy_decision_trace_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_decision_trace_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "trace_readiness",
            "title": "Trace readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy decision trace previews ready"),
        },
        {
            "id": "trace_count",
            "title": "Trace previews",
            "value": summary.get("trace_count", 0),
            "label": "Decision paths mapped",
        },
        {
            "id": "receipt_preview_count",
            "title": "Receipt previews",
            "value": summary.get("receipt_preview_count", 0),
            "label": "Future receipt shapes prepared",
        },
        {
            "id": "decision_coverage",
            "title": "Decision coverage",
            "value": len(summary.get("observed_decisions", [])),
            "label": ", ".join(summary.get("observed_decisions", [])),
        },
        {
            "id": "no_real_receipts",
            "title": "Real receipts written",
            "value": "No" if checks.get("no_real_receipt_written") else "Review",
            "label": "Preview only",
        },
        {
            "id": "endpoint",
            "title": "Guarded endpoint",
            "value": TRACE_PREVIEW_ENDPOINT,
            "label": "Trace preview JSON",
        },
    ]

    return {
        "section_id": "policy_decision_trace_preview",
        "title": "Policy Decision Trace Preview",
        "subtitle": "This shows the receipt trail The Tower would create later, without writing real receipts yet.",
        "status": payload.get("status", "ready"),
        "href": TRACE_PREVIEW_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "cached_non_recursive": True,
    }


def build_policy_decision_trace_preview_html_section() -> str:
    section = build_policy_decision_trace_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-decision-trace-preview-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-decision-trace-preview-section" id="policy-decision-trace-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 153</p>
            <h2>{section.get('title', 'Policy Decision Trace Preview')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{TRACE_PREVIEW_ENDPOINT}">Open trace preview JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "TRACE_PREVIEW_ENDPOINT",
    "SIMULATION_ENDPOINT",
    "build_trace_receipt_preview_for_decision",
    "build_policy_decision_trace_preview_payload",
    "get_policy_decision_trace_preview_payload",
    "build_policy_decision_trace_preview_status_bridge",
    "get_policy_decision_trace_preview_status_bridge",
    "build_policy_decision_trace_preview_quick_action",
    "build_policy_decision_trace_preview_unified_owner_section",
    "build_policy_decision_trace_preview_html_section",
]
