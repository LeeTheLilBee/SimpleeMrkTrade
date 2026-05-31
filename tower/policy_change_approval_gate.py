
"""
PACK 159 - Policy Change Approval Gate foundation.

This module sits on top of Pack 158.

Pack 158 scores how risky future policy changes would be.
Pack 159 decides what approval path would be required before a future real
policy change could ever happen.

Important:
- simulated-only
- approval-preview-only
- gate-preview-only
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


PACK_ID = "PACK_159"
APPROVAL_GATE_ENDPOINT = "/tower/policy-change-approval-gate.json"
RISK_SCORE_ENDPOINT = "/tower/policy-change-risk-score.json"


APPROVAL_PATHS = {
    "deny_automatic_change": {
        "label": "Deny Automatic Change",
        "owner_required": True,
        "step_up_required": True,
        "privacy_review_required": False,
        "quarantine_review_required": False,
        "auto_approval_allowed": False,
    },
    "owner_review_required": {
        "label": "Owner Review Required",
        "owner_required": True,
        "step_up_required": False,
        "privacy_review_required": False,
        "quarantine_review_required": False,
        "auto_approval_allowed": False,
    },
    "owner_step_up_required": {
        "label": "Owner Step-Up Required",
        "owner_required": True,
        "step_up_required": True,
        "privacy_review_required": False,
        "quarantine_review_required": False,
        "auto_approval_allowed": False,
    },
    "privacy_review_required": {
        "label": "Privacy Review Required",
        "owner_required": True,
        "step_up_required": True,
        "privacy_review_required": True,
        "quarantine_review_required": False,
        "auto_approval_allowed": False,
    },
    "quarantine_review_required": {
        "label": "Quarantine Review Required",
        "owner_required": True,
        "step_up_required": True,
        "privacy_review_required": False,
        "quarantine_review_required": True,
        "auto_approval_allowed": False,
    },
    "monitor_only_approval": {
        "label": "Monitor-Only Approval",
        "owner_required": False,
        "step_up_required": False,
        "privacy_review_required": False,
        "quarantine_review_required": False,
        "auto_approval_allowed": True,
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


def _load_pack_158_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_risk_score")
        fn = getattr(mod, "build_policy_change_risk_score_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_158",
            "status": "review",
            "endpoint": RISK_SCORE_ENDPOINT,
            "simulated_only": True,
            "scoring_only": True,
            "recommendation_only": True,
            "load_error": str(exc),
            "summary": {
                "risk_item_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 158 risk score payload unavailable",
            },
            "risk_items": [],
        }

    return {
        "pack_id": "PACK_158",
        "status": "review",
        "endpoint": RISK_SCORE_ENDPOINT,
        "simulated_only": True,
        "scoring_only": True,
        "recommendation_only": True,
        "summary": {
            "risk_item_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 158 risk score payload unavailable",
        },
        "risk_items": [],
    }



def _select_approval_path(risk_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide the required approval path for one Pack 158 risk item.

    This does not approve anything.
    This does not execute anything.
    This only previews the gate The Tower would require later.
    """

    risk_band = str(risk_item.get("risk_band") or "").lower()
    decision = str(risk_item.get("decision") or "").lower()
    recommended_access_level = str(risk_item.get("recommended_access_level") or "").lower()
    scenario_id = str(risk_item.get("scenario_id") or "").lower()
    bucket = str(risk_item.get("bucket") or "").lower()

    if risk_band == "critical":
        path = "deny_automatic_change"
        reason = "Critical risk items cannot be converted automatically. Owner review and step-up are required."

    elif decision == "quarantine" or bucket == "containment_queue":
        path = "quarantine_review_required"
        reason = "Quarantined items must stay contained until a quarantine review is completed."

    elif decision == "redact" or recommended_access_level == "redacted_summary_only":
        path = "privacy_review_required"
        reason = "Redacted/privacy-sensitive items require privacy review before any reveal or policy change."

    elif decision == "step_up" or recommended_access_level == "step_up_challenge_only":
        path = "owner_step_up_required"
        reason = "Step-up items require owner approval plus fresh confirmation before any future change."

    elif risk_band in {"high", "medium"}:
        path = "owner_review_required"
        reason = "Medium or high risk policy-change candidates require owner review before anything real happens."

    elif risk_band == "low":
        path = "owner_review_required"
        reason = "Low risk items still require owner review because this layer cannot approve real changes."

    elif risk_band == "monitor" and decision == "allow":
        path = "monitor_only_approval"
        reason = "Monitor-only allow remains read-only and may stay in low-access monitoring."

    else:
        path = "owner_review_required"
        reason = "Unknown approval state defaults to owner review."

    meta = dict(APPROVAL_PATHS.get(path) or APPROVAL_PATHS["owner_review_required"])

    return {
        "approval_path": path,
        "approval_label": meta["label"],
        "approval_reason": reason,
        "owner_required": bool(meta["owner_required"]),
        "step_up_required": bool(meta["step_up_required"]),
        "privacy_review_required": bool(meta["privacy_review_required"]),
        "quarantine_review_required": bool(meta["quarantine_review_required"]),
        "auto_approval_allowed": bool(meta["auto_approval_allowed"]),
    }


def _build_required_approvals(gate: Dict[str, Any]) -> List[str]:
    approvals: List[str] = []

    if gate.get("owner_required") is True:
        approvals.append("owner_review")

    if gate.get("step_up_required") is True:
        approvals.append("step_up_confirmation")

    if gate.get("privacy_review_required") is True:
        approvals.append("privacy_review")

    if gate.get("quarantine_review_required") is True:
        approvals.append("quarantine_review")

    if gate.get("auto_approval_allowed") is True:
        approvals.append("monitor_only_auto_ack")

    return approvals


def _build_blocked_until(gate: Dict[str, Any]) -> List[str]:
    blocked_until: List[str] = []

    if gate.get("approval_path") == "deny_automatic_change":
        blocked_until.append("owner_review_completed")
        blocked_until.append("step_up_completed")
        blocked_until.append("fresh_risk_recheck_completed")

    if gate.get("approval_path") == "quarantine_review_required":
        blocked_until.append("quarantine_review_completed")
        blocked_until.append("owner_review_completed")

    if gate.get("approval_path") == "privacy_review_required":
        blocked_until.append("privacy_review_completed")
        blocked_until.append("owner_review_completed")
        blocked_until.append("step_up_completed")

    if gate.get("approval_path") == "owner_step_up_required":
        blocked_until.append("owner_review_completed")
        blocked_until.append("step_up_completed")

    if gate.get("approval_path") == "owner_review_required":
        blocked_until.append("owner_review_completed")

    return blocked_until


def _approval_soulaana_translation(risk_item: Dict[str, Any], gate: Dict[str, Any]) -> str:
    scenario_id = _safe_text(risk_item.get("scenario_id"))
    path = str(gate.get("approval_path") or "")

    if path == "deny_automatic_change":
        return f"{scenario_id}: This cannot auto-change. The Tower must stop it until owner review, step-up, and fresh risk recheck happen."
    if path == "quarantine_review_required":
        return f"{scenario_id}: This stays in quarantine. The owner has to review the containment before anything moves."
    if path == "privacy_review_required":
        return f"{scenario_id}: This involves privacy. Keep it redacted until privacy review and owner approval happen."
    if path == "owner_step_up_required":
        return f"{scenario_id}: This needs owner approval and a fresh step-up before it can go anywhere."
    if path == "monitor_only_approval":
        return f"{scenario_id}: This can stay monitor-only. No real access gets added."
    return f"{scenario_id}: This needs owner review before any real policy change."


def build_policy_change_approval_gate_item(risk_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 158 risk item into one approval gate preview item.
    """

    risk_item = dict(risk_item or {})
    gate = _select_approval_path(risk_item)
    required_approvals = _build_required_approvals(gate)
    blocked_until = _build_blocked_until(gate)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "risk_score_id": risk_item.get("risk_score_id"),
        "scenario_id": risk_item.get("scenario_id"),
        "risk_band": risk_item.get("risk_band"),
        "approval_path": gate.get("approval_path"),
    }

    approval_gate_id = f"approval_gate_preview_{_stable_hash(identity, 18)}"

    return {
        "approval_gate_id": approval_gate_id,
        "sequence": sequence,
        "risk_score_id": _safe_text(risk_item.get("risk_score_id")),
        "recommendation_id": _safe_text(risk_item.get("recommendation_id")),
        "recheck_item_id": _safe_text(risk_item.get("recheck_item_id")),
        "expiration_check_id": _safe_text(risk_item.get("expiration_check_id")),
        "vault_entry_id": _safe_text(risk_item.get("vault_entry_id")),
        "ledger_entry_id": _safe_text(risk_item.get("ledger_entry_id")),
        "receipt_preview_id": _safe_text(risk_item.get("receipt_preview_id")),
        "scenario_id": _safe_text(risk_item.get("scenario_id")),
        "matched_policy_id": _safe_text(risk_item.get("matched_policy_id")),
        "decision": _safe_text(risk_item.get("decision")),
        "risk_score": int(risk_item.get("risk_score") or 0),
        "risk_band": _safe_text(risk_item.get("risk_band")),
        "recommended_access_level": _safe_text(risk_item.get("recommended_access_level")),
        "recommended_action": _safe_text(risk_item.get("recommended_action")),
        "approval_path": gate["approval_path"],
        "approval_label": gate["approval_label"],
        "approval_reason": gate["approval_reason"],
        "required_approvals": required_approvals,
        "blocked_until": blocked_until,
        "owner_required": gate["owner_required"],
        "step_up_required": gate["step_up_required"],
        "privacy_review_required": gate["privacy_review_required"],
        "quarantine_review_required": gate["quarantine_review_required"],
        "auto_approval_allowed": gate["auto_approval_allowed"],
        "auto_policy_change_allowed": False,
        "real_policy_change_allowed_now": False,
        "approval_preview_only": True,
        "gate_preview_only": True,
        "soulaana_approval_translation": _approval_soulaana_translation(risk_item, gate),
        "source_endpoint": RISK_SCORE_ENDPOINT,
        "simulated_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
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


def _sort_gate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    path_rank = {
        "deny_automatic_change": 1,
        "quarantine_review_required": 2,
        "privacy_review_required": 3,
        "owner_step_up_required": 4,
        "owner_review_required": 5,
        "monitor_only_approval": 6,
    }
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
            path_rank.get(str(item.get("approval_path")), 99),
            band_rank.get(str(item.get("risk_band")), 99),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_gate_payload_cached() -> Dict[str, Any]:
    pack_158_payload = _load_pack_158_payload(force_refresh=False)
    risk_items = pack_158_payload.get("risk_items", [])

    if not isinstance(risk_items, list):
        risk_items = []

    gate_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(risk_items, start=1):
        if isinstance(item, dict):
            gate_items.append(build_policy_change_approval_gate_item(item, sequence=idx))

    gate_items = _sort_gate_items(gate_items)

    approval_path_counts = _count_by(gate_items, "approval_path")
    risk_band_counts = _count_by(gate_items, "risk_band")
    decision_counts = _count_by(gate_items, "decision")
    owner_required_counts = _count_by(gate_items, "owner_required")
    step_up_required_counts = _count_by(gate_items, "step_up_required")
    auto_approval_counts = _count_by(gate_items, "auto_approval_allowed")

    by_approval_path = _group_by(gate_items, "approval_path")
    by_risk_band = _group_by(gate_items, "risk_band")
    by_decision = _group_by(gate_items, "decision")
    by_required_approval = {}
    for item in gate_items:
        approvals = item.get("required_approvals", [])
        if isinstance(approvals, list):
            for approval in approvals:
                by_required_approval.setdefault(str(approval), []).append(item)

    deny_auto_change = [
        item for item in gate_items
        if item.get("approval_path") == "deny_automatic_change"
    ]
    owner_review_required = [
        item for item in gate_items
        if item.get("owner_required") is True
    ]
    step_up_required = [
        item for item in gate_items
        if item.get("step_up_required") is True
    ]
    privacy_review_required = [
        item for item in gate_items
        if item.get("privacy_review_required") is True
    ]
    quarantine_review_required = [
        item for item in gate_items
        if item.get("quarantine_review_required") is True
    ]
    monitor_only_approval = [
        item for item in gate_items
        if item.get("approval_path") == "monitor_only_approval"
    ]

    required_paths = {
        "deny_automatic_change",
        "quarantine_review_required",
        "privacy_review_required",
        "owner_step_up_required",
        "owner_review_required",
        "monitor_only_approval",
    }
    observed_paths = set(approval_path_counts.keys())

    readiness_checks = {
        "pack_158_ready": pack_158_payload.get("status") == "ready",
        "has_gate_items": len(gate_items) >= 1,
        "gate_count_matches_risk_items": len(gate_items) == len(risk_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in gate_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in gate_items),
        "all_gate_preview_only": all(item.get("gate_preview_only") is True for item in gate_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in gate_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in gate_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in gate_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in gate_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in gate_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in gate_items),
        "all_gate_ids_present": all(bool(item.get("approval_gate_id")) for item in gate_items),
        "all_paths_present": all(bool(item.get("approval_path")) for item in gate_items),
        "all_reasons_present": all(bool(item.get("approval_reason")) for item in gate_items),
        "all_required_approval_lists_present": all(isinstance(item.get("required_approvals"), list) for item in gate_items),
        "auto_policy_change_never_allowed": all(item.get("auto_policy_change_allowed") is False for item in gate_items),
        "real_policy_change_allowed_now_never": all(item.get("real_policy_change_allowed_now") is False for item in gate_items),
        "deny_auto_change_present": len(deny_auto_change) >= 1,
        "owner_review_required_present": len(owner_review_required) >= 1,
        "step_up_required_present": len(step_up_required) >= 1,
        "privacy_review_required_present": len(privacy_review_required) >= 1,
        "quarantine_review_required_present": len(quarantine_review_required) >= 1,
        "monitor_only_approval_present": len(monitor_only_approval) >= 1,
        "required_path_coverage": required_paths.issubset(observed_paths),
        "endpoint": APPROVAL_GATE_ENDPOINT,
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
        "pack_number": 159,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Change Approval Gate foundation",
        "endpoint": APPROVAL_GATE_ENDPOINT,
        "source_endpoint": RISK_SCORE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "approval_preview_only": True,
        "gate_preview_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
        "source_pack_158": {
            "status": pack_158_payload.get("status"),
            "readiness_score": pack_158_payload.get("summary", {}).get("readiness_score"),
            "risk_item_count": pack_158_payload.get("summary", {}).get("risk_item_count"),
            "band_counts": pack_158_payload.get("summary", {}).get("band_counts", {}),
        },
        "summary": {
            "approval_gate_count": len(gate_items),
            "deny_auto_change_count": len(deny_auto_change),
            "owner_review_required_count": len(owner_review_required),
            "step_up_required_count": len(step_up_required),
            "privacy_review_required_count": len(privacy_review_required),
            "quarantine_review_required_count": len(quarantine_review_required),
            "monitor_only_approval_count": len(monitor_only_approval),
            "approval_path_counts": approval_path_counts,
            "risk_band_counts": risk_band_counts,
            "decision_counts": decision_counts,
            "owner_required_counts": owner_required_counts,
            "step_up_required_counts": step_up_required_counts,
            "auto_approval_counts": auto_approval_counts,
            "observed_paths": sorted(observed_paths),
            "required_paths": sorted(required_paths),
            "readiness_score": readiness_score,
            "readiness_label": "Policy change approval gate ready" if readiness_score == 100 else "Policy change approval gate needs review",
        },
        "readiness_checks": readiness_checks,
        "approval_gate_items": gate_items,
        "indexes": {
            "by_approval_path": by_approval_path,
            "by_risk_band": by_risk_band,
            "by_decision": by_decision,
            "by_required_approval": by_required_approval,
        },
        "deny_auto_change": deny_auto_change,
        "owner_review_required": owner_review_required,
        "step_up_required": step_up_required,
        "privacy_review_required": privacy_review_required,
        "quarantine_review_required": quarantine_review_required,
        "monitor_only_approval": monitor_only_approval,
        "quick_action": {
            "id": "policy_change_approval_gate",
            "label": "Policy Change Approval Gate",
            "href": APPROVAL_GATE_ENDPOINT,
            "description": "Preview which approval gate a future policy change would require.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_gate",
            "title": "Policy Change Approval Gate",
            "subtitle": "Maps risk scores into approval paths before any future real policy change.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_GATE_ENDPOINT,
        },
    }


def build_policy_change_approval_gate_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_gate_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_gate_payload_cached())


def get_policy_change_approval_gate_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_gate_payload(force_refresh=force_refresh)


def build_policy_change_approval_gate_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_gate_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 159,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_GATE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", RISK_SCORE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy change approval gate ready"),
        "approval_gate_count": summary.get("approval_gate_count", 0),
        "deny_auto_change_count": summary.get("deny_auto_change_count", 0),
        "owner_review_required_count": summary.get("owner_review_required_count", 0),
        "step_up_required_count": summary.get("step_up_required_count", 0),
        "privacy_review_required_count": summary.get("privacy_review_required_count", 0),
        "quarantine_review_required_count": summary.get("quarantine_review_required_count", 0),
        "monitor_only_approval_count": summary.get("monitor_only_approval_count", 0),
        "approval_path_counts": summary.get("approval_path_counts", {}),
        "risk_band_counts": summary.get("risk_band_counts", {}),
        "simulated_only": True,
        "approval_preview_only": True,
        "gate_preview_only": True,
        "real_policy_change_executed": False,
        "real_permission_change_executed": False,
        "real_access_granted": False,
        "real_enforcement_executed": False,
        "real_audit_written": False,
        "real_receipt_written": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_gate_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_gate_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_gate_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_gate_status_bridge()
    return {
        "id": "policy_change_approval_gate",
        "label": "Policy Change Approval Gate",
        "title": "Policy Change Approval Gate",
        "href": APPROVAL_GATE_ENDPOINT,
        "endpoint": APPROVAL_GATE_ENDPOINT,
        "description": "Preview which approval path a future policy change would require.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 159",
        "category": "policy",
        "simulated_only": True,
        "approval_preview_only": True,
        "gate_preview_only": True,
    }


def build_policy_change_approval_gate_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_gate_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "approval_gate_readiness",
            "title": "Approval gate readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy change approval gate ready"),
        },
        {
            "id": "approval_gate_items",
            "title": "Gate items",
            "value": summary.get("approval_gate_count", 0),
            "label": "Risk items mapped to approval paths",
        },
        {
            "id": "deny_auto_change",
            "title": "Deny automatic change",
            "value": summary.get("deny_auto_change_count", 0),
            "label": "Cannot auto-convert",
        },
        {
            "id": "owner_review",
            "title": "Owner review",
            "value": summary.get("owner_review_required_count", 0),
            "label": "Need owner attention",
        },
        {
            "id": "special_reviews",
            "title": "Privacy / quarantine",
            "value": f"{summary.get('privacy_review_required_count', 0)} / {summary.get('quarantine_review_required_count', 0)}",
            "label": "Special review paths",
        },
        {
            "id": "no_real_changes",
            "title": "Real policy changes",
            "value": "No" if checks.get("no_real_policy_change") else "Review",
            "label": "Gate preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_gate",
        "title": "Policy Change Approval Gate",
        "subtitle": "Maps policy-change risk scores into approval paths before any future real policy change.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_GATE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "approval_preview_only": True,
        "gate_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_gate_html_section() -> str:
    section = build_policy_change_approval_gate_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-gate-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-gate-section" id="policy-change-approval-gate">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 159</p>
            <h2>{section.get('title', 'Policy Change Approval Gate')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_GATE_ENDPOINT}">Open policy change approval gate JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_GATE_ENDPOINT",
    "RISK_SCORE_ENDPOINT",
    "APPROVAL_PATHS",
    "build_policy_change_approval_gate_item",
    "build_policy_change_approval_gate_payload",
    "get_policy_change_approval_gate_payload",
    "build_policy_change_approval_gate_status_bridge",
    "get_policy_change_approval_gate_status_bridge",
    "build_policy_change_approval_gate_quick_action",
    "build_policy_change_approval_gate_unified_owner_section",
    "build_policy_change_approval_gate_html_section",
]
