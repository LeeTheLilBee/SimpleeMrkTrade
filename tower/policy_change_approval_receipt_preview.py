
"""
PACK 160 - Policy Change Approval Receipt Preview foundation.

This module sits on top of Pack 159.

Pack 159 decides what approval path a future policy change would require.
Pack 160 builds a simulated receipt/evidence preview for each approval-gate
decision before any real approval, policy change, access grant, or enforcement
can happen.

Important:
- simulated-only
- receipt-preview-only
- approval-preview-only
- evidence-preview-only
- no real policy changes
- no real approvals executed
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


PACK_ID = "PACK_160"
APPROVAL_RECEIPT_ENDPOINT = "/tower/policy-change-approval-receipt-preview.json"
APPROVAL_GATE_ENDPOINT = "/tower/policy-change-approval-gate.json"


RECEIPT_TYPES = {
    "auto_change_denied": {
        "label": "Automatic Change Denied Receipt",
        "severity": "critical",
        "requires_owner_review": True,
    },
    "quarantine_review_required": {
        "label": "Quarantine Review Required Receipt",
        "severity": "high",
        "requires_owner_review": True,
    },
    "privacy_review_required": {
        "label": "Privacy Review Required Receipt",
        "severity": "privacy",
        "requires_owner_review": True,
    },
    "owner_step_up_required": {
        "label": "Owner Step-Up Required Receipt",
        "severity": "medium",
        "requires_owner_review": True,
    },
    "owner_review_required": {
        "label": "Owner Review Required Receipt",
        "severity": "medium",
        "requires_owner_review": True,
    },
    "monitor_only_ack": {
        "label": "Monitor-Only Acknowledgement Receipt",
        "severity": "monitor",
        "requires_owner_review": False,
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


def _load_pack_159_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_gate")
        fn = getattr(mod, "build_policy_change_approval_gate_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_159",
            "status": "review",
            "endpoint": APPROVAL_GATE_ENDPOINT,
            "simulated_only": True,
            "approval_preview_only": True,
            "gate_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "approval_gate_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 159 approval gate payload unavailable",
            },
            "approval_gate_items": [],
        }

    return {
        "pack_id": "PACK_159",
        "status": "review",
        "endpoint": APPROVAL_GATE_ENDPOINT,
        "simulated_only": True,
        "approval_preview_only": True,
        "gate_preview_only": True,
        "summary": {
            "approval_gate_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 159 approval gate payload unavailable",
        },
        "approval_gate_items": [],
    }



def _select_receipt_type(gate_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Choose the simulated receipt type for one Pack 159 approval gate item.

    This does not write a real receipt.
    This does not approve anything.
    This only previews what evidence would be prepared later.
    """

    approval_path = str(gate_item.get("approval_path") or "").lower()

    if approval_path == "deny_automatic_change":
        receipt_type = "auto_change_denied"
        receipt_reason = "Automatic policy change is denied because the item is critical-risk or fail-closed."

    elif approval_path == "quarantine_review_required":
        receipt_type = "quarantine_review_required"
        receipt_reason = "A quarantine review receipt is required because the item must remain contained."

    elif approval_path == "privacy_review_required":
        receipt_type = "privacy_review_required"
        receipt_reason = "A privacy review receipt is required because the item involves redaction or sensitive reveal control."

    elif approval_path == "owner_step_up_required":
        receipt_type = "owner_step_up_required"
        receipt_reason = "An owner step-up receipt is required before a future policy change can be considered."

    elif approval_path == "owner_review_required":
        receipt_type = "owner_review_required"
        receipt_reason = "An owner review receipt is required before a future real policy change can be considered."

    elif approval_path == "monitor_only_approval":
        receipt_type = "monitor_only_ack"
        receipt_reason = "A monitor-only acknowledgement receipt is enough because no real access or policy change is allowed."

    else:
        receipt_type = "owner_review_required"
        receipt_reason = "Unknown approval path defaults to owner review receipt preview."

    meta = dict(RECEIPT_TYPES.get(receipt_type) or RECEIPT_TYPES["owner_review_required"])

    return {
        "receipt_type": receipt_type,
        "receipt_label": meta["label"],
        "receipt_severity": meta["severity"],
        "receipt_reason": receipt_reason,
        "requires_owner_review": bool(meta["requires_owner_review"]),
    }


def _build_evidence_fields(gate_item: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the safe evidence preview fields that would be included in the receipt.
    """

    return {
        "approval_gate_id": _safe_text(gate_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(gate_item.get("risk_score_id")),
        "recommendation_id": _safe_text(gate_item.get("recommendation_id")),
        "scenario_id": _safe_text(gate_item.get("scenario_id")),
        "matched_policy_id": _safe_text(gate_item.get("matched_policy_id")),
        "decision": _safe_text(gate_item.get("decision")),
        "risk_score": int(gate_item.get("risk_score") or 0),
        "risk_band": _safe_text(gate_item.get("risk_band")),
        "approval_path": _safe_text(gate_item.get("approval_path")),
        "approval_label": _safe_text(gate_item.get("approval_label")),
        "required_approvals": list(gate_item.get("required_approvals") or []),
        "blocked_until": list(gate_item.get("blocked_until") or []),
        "receipt_type": receipt.get("receipt_type"),
        "receipt_label": receipt.get("receipt_label"),
        "receipt_severity": receipt.get("receipt_severity"),
    }


def _build_receipt_controls(gate_item: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preview control flags. Everything stays non-mutating.
    """

    return {
        "owner_review_required": bool(gate_item.get("owner_required", False)) or bool(receipt.get("requires_owner_review", False)),
        "step_up_required": bool(gate_item.get("step_up_required", False)),
        "privacy_review_required": bool(gate_item.get("privacy_review_required", False)),
        "quarantine_review_required": bool(gate_item.get("quarantine_review_required", False)),
        "auto_approval_allowed": bool(gate_item.get("auto_approval_allowed", False)),
        "auto_policy_change_allowed": False,
        "real_policy_change_allowed_now": False,
        "receipt_write_allowed_now": False,
        "audit_write_allowed_now": False,
        "archive_write_allowed_now": False,
    }


def _receipt_soulaana_translation(gate_item: Dict[str, Any], receipt: Dict[str, Any]) -> str:
    scenario_id = _safe_text(gate_item.get("scenario_id"))
    receipt_type = str(receipt.get("receipt_type") or "")

    if receipt_type == "auto_change_denied":
        return f"{scenario_id}: The receipt preview says automatic change is denied. Nothing moves without owner review and step-up."
    if receipt_type == "quarantine_review_required":
        return f"{scenario_id}: The receipt preview says this stays contained until quarantine review is complete."
    if receipt_type == "privacy_review_required":
        return f"{scenario_id}: The receipt preview says privacy review is required before any reveal or change."
    if receipt_type == "owner_step_up_required":
        return f"{scenario_id}: The receipt preview says owner approval and step-up are required first."
    if receipt_type == "monitor_only_ack":
        return f"{scenario_id}: The receipt preview only acknowledges monitor-only status. No new access is granted."
    return f"{scenario_id}: The receipt preview says owner review is required before any real policy change."


def build_policy_change_approval_receipt_preview_item(gate_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 159 approval gate item into one simulated receipt preview.
    """

    gate_item = dict(gate_item or {})
    receipt = _select_receipt_type(gate_item)
    evidence = _build_evidence_fields(gate_item, receipt)
    controls = _build_receipt_controls(gate_item, receipt)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "approval_gate_id": gate_item.get("approval_gate_id"),
        "scenario_id": gate_item.get("scenario_id"),
        "approval_path": gate_item.get("approval_path"),
        "receipt_type": receipt.get("receipt_type"),
    }

    receipt_preview_id = f"approval_receipt_preview_{_stable_hash(identity, 18)}"

    return {
        "approval_receipt_preview_id": receipt_preview_id,
        "sequence": sequence,
        "approval_gate_id": _safe_text(gate_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(gate_item.get("risk_score_id")),
        "recommendation_id": _safe_text(gate_item.get("recommendation_id")),
        "recheck_item_id": _safe_text(gate_item.get("recheck_item_id")),
        "expiration_check_id": _safe_text(gate_item.get("expiration_check_id")),
        "vault_entry_id": _safe_text(gate_item.get("vault_entry_id")),
        "ledger_entry_id": _safe_text(gate_item.get("ledger_entry_id")),
        "source_receipt_preview_id": _safe_text(gate_item.get("receipt_preview_id")),
        "scenario_id": _safe_text(gate_item.get("scenario_id")),
        "matched_policy_id": _safe_text(gate_item.get("matched_policy_id")),
        "decision": _safe_text(gate_item.get("decision")),
        "risk_score": int(gate_item.get("risk_score") or 0),
        "risk_band": _safe_text(gate_item.get("risk_band")),
        "approval_path": _safe_text(gate_item.get("approval_path")),
        "approval_label": _safe_text(gate_item.get("approval_label")),
        "receipt_type": receipt["receipt_type"],
        "receipt_label": receipt["receipt_label"],
        "receipt_severity": receipt["receipt_severity"],
        "receipt_reason": receipt["receipt_reason"],
        "evidence_preview": evidence,
        "control_preview": controls,
        "required_approvals": list(gate_item.get("required_approvals") or []),
        "blocked_until": list(gate_item.get("blocked_until") or []),
        "soulaana_receipt_translation": _receipt_soulaana_translation(gate_item, receipt),
        "source_endpoint": APPROVAL_GATE_ENDPOINT,
        "simulated_only": True,
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


def _sort_receipt_previews(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    type_rank = {
        "auto_change_denied": 1,
        "quarantine_review_required": 2,
        "privacy_review_required": 3,
        "owner_step_up_required": 4,
        "owner_review_required": 5,
        "monitor_only_ack": 6,
    }
    severity_rank = {
        "critical": 1,
        "high": 2,
        "privacy": 3,
        "medium": 4,
        "monitor": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            type_rank.get(str(item.get("receipt_type")), 99),
            severity_rank.get(str(item.get("receipt_severity")), 99),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_preview_payload_cached() -> Dict[str, Any]:
    pack_159_payload = _load_pack_159_payload(force_refresh=False)
    gate_items = pack_159_payload.get("approval_gate_items", [])

    if not isinstance(gate_items, list):
        gate_items = []

    receipt_previews: List[Dict[str, Any]] = []
    for idx, item in enumerate(gate_items, start=1):
        if isinstance(item, dict):
            receipt_previews.append(build_policy_change_approval_receipt_preview_item(item, sequence=idx))

    receipt_previews = _sort_receipt_previews(receipt_previews)

    receipt_type_counts = _count_by(receipt_previews, "receipt_type")
    receipt_severity_counts = _count_by(receipt_previews, "receipt_severity")
    approval_path_counts = _count_by(receipt_previews, "approval_path")
    decision_counts = _count_by(receipt_previews, "decision")
    risk_band_counts = _count_by(receipt_previews, "risk_band")

    by_receipt_type = _group_by(receipt_previews, "receipt_type")
    by_receipt_severity = _group_by(receipt_previews, "receipt_severity")
    by_approval_path = _group_by(receipt_previews, "approval_path")
    by_decision = _group_by(receipt_previews, "decision")

    auto_change_denied = [
        item for item in receipt_previews
        if item.get("receipt_type") == "auto_change_denied"
    ]
    quarantine_review_receipts = [
        item for item in receipt_previews
        if item.get("receipt_type") == "quarantine_review_required"
    ]
    privacy_review_receipts = [
        item for item in receipt_previews
        if item.get("receipt_type") == "privacy_review_required"
    ]
    owner_step_up_receipts = [
        item for item in receipt_previews
        if item.get("receipt_type") == "owner_step_up_required"
    ]
    owner_review_receipts = [
        item for item in receipt_previews
        if item.get("receipt_type") == "owner_review_required"
    ]
    monitor_only_receipts = [
        item for item in receipt_previews
        if item.get("receipt_type") == "monitor_only_ack"
    ]

    required_receipt_types = {
        "auto_change_denied",
        "quarantine_review_required",
        "privacy_review_required",
        "owner_step_up_required",
        "owner_review_required",
        "monitor_only_ack",
    }
    observed_receipt_types = set(receipt_type_counts.keys())

    readiness_checks = {
        "pack_159_ready": pack_159_payload.get("status") == "ready",
        "has_receipt_previews": len(receipt_previews) >= 1,
        "receipt_count_matches_gate_items": len(receipt_previews) == len(gate_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in receipt_previews),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in receipt_previews),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in receipt_previews),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in receipt_previews),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in receipt_previews),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in receipt_previews),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in receipt_previews),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in receipt_previews),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in receipt_previews),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in receipt_previews),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in receipt_previews),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in receipt_previews),
        "all_receipt_ids_present": all(bool(item.get("approval_receipt_preview_id")) for item in receipt_previews),
        "all_receipt_types_present": all(bool(item.get("receipt_type")) for item in receipt_previews),
        "all_receipt_reasons_present": all(bool(item.get("receipt_reason")) for item in receipt_previews),
        "all_evidence_preview_present": all(isinstance(item.get("evidence_preview"), dict) for item in receipt_previews),
        "all_control_preview_present": all(isinstance(item.get("control_preview"), dict) for item in receipt_previews),
        "auto_change_denied_present": len(auto_change_denied) >= 1,
        "quarantine_review_receipts_present": len(quarantine_review_receipts) >= 1,
        "privacy_review_receipts_present": len(privacy_review_receipts) >= 1,
        "owner_step_up_receipts_present": len(owner_step_up_receipts) >= 1,
        "owner_review_receipts_present": len(owner_review_receipts) >= 1,
        "monitor_only_receipts_present": len(monitor_only_receipts) >= 1,
        "required_receipt_type_coverage": required_receipt_types.issubset(observed_receipt_types),
        "endpoint": APPROVAL_RECEIPT_ENDPOINT,
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
        "pack_number": 160,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Change Approval Receipt Preview foundation",
        "endpoint": APPROVAL_RECEIPT_ENDPOINT,
        "source_endpoint": APPROVAL_GATE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
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
        "cached_non_recursive": True,
        "source_pack_159": {
            "status": pack_159_payload.get("status"),
            "readiness_score": pack_159_payload.get("summary", {}).get("readiness_score"),
            "approval_gate_count": pack_159_payload.get("summary", {}).get("approval_gate_count"),
            "approval_path_counts": pack_159_payload.get("summary", {}).get("approval_path_counts", {}),
        },
        "summary": {
            "receipt_preview_count": len(receipt_previews),
            "auto_change_denied_count": len(auto_change_denied),
            "quarantine_review_receipt_count": len(quarantine_review_receipts),
            "privacy_review_receipt_count": len(privacy_review_receipts),
            "owner_step_up_receipt_count": len(owner_step_up_receipts),
            "owner_review_receipt_count": len(owner_review_receipts),
            "monitor_only_receipt_count": len(monitor_only_receipts),
            "receipt_type_counts": receipt_type_counts,
            "receipt_severity_counts": receipt_severity_counts,
            "approval_path_counts": approval_path_counts,
            "decision_counts": decision_counts,
            "risk_band_counts": risk_band_counts,
            "observed_receipt_types": sorted(observed_receipt_types),
            "required_receipt_types": sorted(required_receipt_types),
            "readiness_score": readiness_score,
            "readiness_label": "Policy change approval receipt preview ready" if readiness_score == 100 else "Policy change approval receipt preview needs review",
        },
        "readiness_checks": readiness_checks,
        "receipt_previews": receipt_previews,
        "indexes": {
            "by_receipt_type": by_receipt_type,
            "by_receipt_severity": by_receipt_severity,
            "by_approval_path": by_approval_path,
            "by_decision": by_decision,
        },
        "auto_change_denied": auto_change_denied,
        "quarantine_review_receipts": quarantine_review_receipts,
        "privacy_review_receipts": privacy_review_receipts,
        "owner_step_up_receipts": owner_step_up_receipts,
        "owner_review_receipts": owner_review_receipts,
        "monitor_only_receipts": monitor_only_receipts,
        "quick_action": {
            "id": "policy_change_approval_receipt_preview",
            "label": "Policy Change Approval Receipts",
            "href": APPROVAL_RECEIPT_ENDPOINT,
            "description": "Preview receipt/evidence packets for approval-gate decisions.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_preview",
            "title": "Policy Change Approval Receipts",
            "subtitle": "Previews approval-gate receipts before any real approval, audit, or policy write.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_preview_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_preview_payload_cached())


def get_policy_change_approval_receipt_preview_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_preview_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_preview_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 160,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_GATE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy change approval receipt preview ready"),
        "receipt_preview_count": summary.get("receipt_preview_count", 0),
        "auto_change_denied_count": summary.get("auto_change_denied_count", 0),
        "quarantine_review_receipt_count": summary.get("quarantine_review_receipt_count", 0),
        "privacy_review_receipt_count": summary.get("privacy_review_receipt_count", 0),
        "owner_step_up_receipt_count": summary.get("owner_step_up_receipt_count", 0),
        "owner_review_receipt_count": summary.get("owner_review_receipt_count", 0),
        "monitor_only_receipt_count": summary.get("monitor_only_receipt_count", 0),
        "receipt_type_counts": summary.get("receipt_type_counts", {}),
        "receipt_severity_counts": summary.get("receipt_severity_counts", {}),
        "simulated_only": True,
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
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_preview_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_preview_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_preview_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_preview_status_bridge()
    return {
        "id": "policy_change_approval_receipt_preview",
        "label": "Policy Change Approval Receipts",
        "title": "Policy Change Approval Receipts",
        "href": APPROVAL_RECEIPT_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_ENDPOINT,
        "description": "Preview approval receipt/evidence packets without writing real receipts.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 160",
        "category": "policy",
        "simulated_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_preview_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_preview_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "approval_receipt_readiness",
            "title": "Receipt preview readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy change approval receipt preview ready"),
        },
        {
            "id": "receipt_previews",
            "title": "Receipt previews",
            "value": summary.get("receipt_preview_count", 0),
            "label": "Approval-gate receipts prepared as previews",
        },
        {
            "id": "automatic_denied",
            "title": "Automatic denied",
            "value": summary.get("auto_change_denied_count", 0),
            "label": "Auto-change denial receipts",
        },
        {
            "id": "owner_review_receipts",
            "title": "Owner review receipts",
            "value": summary.get("owner_review_receipt_count", 0),
            "label": "Need owner review evidence",
        },
        {
            "id": "special_review_receipts",
            "title": "Privacy / quarantine",
            "value": f"{summary.get('privacy_review_receipt_count', 0)} / {summary.get('quarantine_review_receipt_count', 0)}",
            "label": "Special receipt paths",
        },
        {
            "id": "no_real_receipts",
            "title": "Real receipt writes",
            "value": "No" if checks.get("no_real_receipt_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_preview",
        "title": "Policy Change Approval Receipts",
        "subtitle": "Previews approval-gate evidence packets before any real approval, audit, archive, or receipt write.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_preview_html_section() -> str:
    section = build_policy_change_approval_receipt_preview_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-section" id="policy-change-approval-receipt-preview">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 160</p>
            <h2>{section.get('title', 'Policy Change Approval Receipts')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_ENDPOINT}">Open policy change approval receipt preview JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_ENDPOINT",
    "APPROVAL_GATE_ENDPOINT",
    "RECEIPT_TYPES",
    "build_policy_change_approval_receipt_preview_item",
    "build_policy_change_approval_receipt_preview_payload",
    "get_policy_change_approval_receipt_preview_payload",
    "build_policy_change_approval_receipt_preview_status_bridge",
    "get_policy_change_approval_receipt_preview_status_bridge",
    "build_policy_change_approval_receipt_preview_quick_action",
    "build_policy_change_approval_receipt_preview_unified_owner_section",
    "build_policy_change_approval_receipt_preview_html_section",
]
