
"""
PACK 165 - Approval Receipt Detail Preview / Evidence Drawer.

This module sits on top of Pack 164.

Pack 164 creates simulated owner-review queue items.
Pack 165 turns those owner-review items into a simulated detail/evidence drawer
with receipt story, source chain, risk/gate/queue lineage, required owner action,
evidence summary, and safe preview detail cards.

Important:
- simulated-only
- detail-preview-only
- evidence-drawer-preview-only
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
- no real evidence revealed
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


PACK_ID = "PACK_165"
APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT = "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT = "/tower/policy-change-approval-receipt-owner-review-queue.json"


DETAIL_DRAWER_SECTIONS = {
    "receipt_story": {
        "label": "Receipt Story",
        "description": "Plain-language story of why the receipt exists and what owner attention is needed.",
        "sensitivity": "low",
        "redacted_by_default": False,
    },
    "source_chain": {
        "label": "Source Chain",
        "description": "Source IDs linking risk score, approval gate, receipt preview, vault index, expiration, queue, and owner review.",
        "sensitivity": "medium",
        "redacted_by_default": False,
    },
    "risk_gate_lineage": {
        "label": "Risk / Gate Lineage",
        "description": "Risk band, decision, approval path, queue lane, and owner review category.",
        "sensitivity": "medium",
        "redacted_by_default": False,
    },
    "owner_action": {
        "label": "Owner Action",
        "description": "Required owner action and preview-only review steps.",
        "sensitivity": "medium",
        "redacted_by_default": False,
    },
    "evidence_summary": {
        "label": "Evidence Summary",
        "description": "Safe evidence summary for owner review without exposing secrets or raw strategy internals.",
        "sensitivity": "high",
        "redacted_by_default": True,
    },
    "safety_flags": {
        "label": "Safety Flags",
        "description": "Flags proving no real approval, enforcement, recheck, renewal, vault write, or access grant happened.",
        "sensitivity": "high",
        "redacted_by_default": True,
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


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _load_pack_164_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_owner_review_queue")
        fn = getattr(mod, "build_policy_change_approval_receipt_owner_review_queue_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_164",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "owner_review_item_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 164 approval receipt owner review queue unavailable",
            },
            "owner_review_items": [],
        }

    return {
        "pack_id": "PACK_164",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
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
        "summary": {
            "owner_review_item_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 164 approval receipt owner review queue unavailable",
        },
        "owner_review_items": [],
    }



def _build_receipt_story(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    scenario_id = _safe_text(owner_review_item.get("scenario_id"))
    category = _safe_text(owner_review_item.get("owner_review_category"))
    label = _safe_text(owner_review_item.get("owner_review_label"))
    required_action = _safe_text(owner_review_item.get("required_owner_action"))
    reason = _safe_text(owner_review_item.get("owner_review_reason"))

    return {
        "section_id": "receipt_story",
        "section_label": DETAIL_DRAWER_SECTIONS["receipt_story"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["receipt_story"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["receipt_story"]["redacted_by_default"],
        "scenario_id": scenario_id,
        "owner_review_category": category,
        "owner_review_label": label,
        "required_owner_action": required_action,
        "story": f"{scenario_id}: {label} is pending. Required owner action: {required_action}. Reason: {reason}",
        "safe_for_preview": True,
    }


def _build_source_chain(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    chain = {
        "owner_review_item_id": _safe_text(owner_review_item.get("owner_review_item_id")),
        "queue_item_id": _safe_text(owner_review_item.get("queue_item_id")),
        "expiration_preview_id": _safe_text(owner_review_item.get("expiration_preview_id")),
        "vault_preview_id": _safe_text(owner_review_item.get("vault_preview_id")),
        "ledger_index_id": _safe_text(owner_review_item.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(owner_review_item.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(owner_review_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(owner_review_item.get("risk_score_id")),
        "recommendation_id": _safe_text(owner_review_item.get("recommendation_id")),
        "matched_policy_id": _safe_text(owner_review_item.get("matched_policy_id")),
    }

    return {
        "section_id": "source_chain",
        "section_label": DETAIL_DRAWER_SECTIONS["source_chain"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["source_chain"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["source_chain"]["redacted_by_default"],
        "chain": chain,
        "chain_depth": len([value for value in chain.values() if value]),
        "source_endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "safe_for_preview": True,
    }


def _build_risk_gate_lineage(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section_id": "risk_gate_lineage",
        "section_label": DETAIL_DRAWER_SECTIONS["risk_gate_lineage"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["risk_gate_lineage"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["risk_gate_lineage"]["redacted_by_default"],
        "decision": _safe_text(owner_review_item.get("decision")),
        "risk_score": int(owner_review_item.get("risk_score") or 0),
        "risk_band": _safe_text(owner_review_item.get("risk_band")),
        "approval_path": _safe_text(owner_review_item.get("approval_path")),
        "receipt_type": _safe_text(owner_review_item.get("receipt_type")),
        "receipt_severity": _safe_text(owner_review_item.get("receipt_severity")),
        "vault_bucket": _safe_text(owner_review_item.get("vault_bucket")),
        "retention_class": _safe_text(owner_review_item.get("retention_class")),
        "priority": _safe_text(owner_review_item.get("priority")),
        "expiration_state": _safe_text(owner_review_item.get("expiration_state")),
        "queue_lane": _safe_text(owner_review_item.get("queue_lane")),
        "queue_priority": _safe_text(owner_review_item.get("queue_priority")),
        "recommended_action": _safe_text(owner_review_item.get("recommended_action")),
        "renewal_status": _safe_text(owner_review_item.get("renewal_status")),
        "owner_review_category": _safe_text(owner_review_item.get("owner_review_category")),
        "owner_review_priority": _safe_text(owner_review_item.get("owner_review_priority")),
        "safe_for_preview": True,
    }


def _build_owner_action_summary(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    steps = owner_review_item.get("required_owner_review_steps", [])
    if not isinstance(steps, list):
        steps = []

    return {
        "section_id": "owner_action",
        "section_label": DETAIL_DRAWER_SECTIONS["owner_action"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["owner_action"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["owner_action"]["redacted_by_default"],
        "required_owner_action": _safe_text(owner_review_item.get("required_owner_action")),
        "owner_review_status": _safe_text(owner_review_item.get("owner_review_status")),
        "owner_review_required": _safe_bool(owner_review_item.get("owner_review_required")),
        "owner_step_up_required": _safe_bool(owner_review_item.get("owner_step_up_required")),
        "required_owner_review_steps": [_safe_text(step) for step in steps],
        "owner_review_reason": _safe_text(owner_review_item.get("owner_review_reason")),
        "safe_for_preview": True,
    }


def _build_evidence_summary(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section_id": "evidence_summary",
        "section_label": DETAIL_DRAWER_SECTIONS["evidence_summary"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["evidence_summary"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["evidence_summary"]["redacted_by_default"],
        "evidence_summary_id": f"evidence_summary_{_stable_hash(owner_review_item.get('owner_review_item_id'), 14)}",
        "summary": _safe_text(owner_review_item.get("soulaana_owner_review_translation")),
        "scenario_id": _safe_text(owner_review_item.get("scenario_id")),
        "matched_policy_id": _safe_text(owner_review_item.get("matched_policy_id")),
        "contains_raw_secret": False,
        "contains_raw_strategy": False,
        "contains_broker_token": False,
        "contains_unredacted_sensitive_value": False,
        "safe_for_preview": True,
    }


def _build_safety_flags(owner_review_item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section_id": "safety_flags",
        "section_label": DETAIL_DRAWER_SECTIONS["safety_flags"]["label"],
        "sensitivity": DETAIL_DRAWER_SECTIONS["safety_flags"]["sensitivity"],
        "redacted_by_default": DETAIL_DRAWER_SECTIONS["safety_flags"]["redacted_by_default"],
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
        "real_evidence_revealed": False,
        "owner_review_action_allowed_now": False,
        "owner_step_up_allowed_now": False,
        "safe_for_preview": True,
    }


def _build_detail_cards(owner_review_item: Dict[str, Any]) -> List[Dict[str, Any]]:
    risk_score = int(owner_review_item.get("risk_score") or 0)

    return [
        {
            "id": "owner_review_category",
            "title": "Owner review category",
            "value": _safe_text(owner_review_item.get("owner_review_category")),
            "label": _safe_text(owner_review_item.get("owner_review_label")),
        },
        {
            "id": "risk_score",
            "title": "Risk score",
            "value": risk_score,
            "label": _safe_text(owner_review_item.get("risk_band")),
        },
        {
            "id": "required_action",
            "title": "Required action",
            "value": _safe_text(owner_review_item.get("required_owner_action")),
            "label": "Preview only",
        },
        {
            "id": "queue_lane",
            "title": "Queue lane",
            "value": _safe_text(owner_review_item.get("queue_lane")),
            "label": _safe_text(owner_review_item.get("recommended_action")),
        },
        {
            "id": "step_up",
            "title": "Step-up required",
            "value": "Yes" if owner_review_item.get("owner_step_up_required") else "No",
            "label": "No real step-up executed",
        },
        {
            "id": "real_actions",
            "title": "Real actions",
            "value": "Disabled",
            "label": "No approval/recheck/renewal/enforcement",
        },
    ]


def build_policy_change_approval_receipt_detail_evidence_drawer_item(owner_review_item: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 164 owner-review item into one simulated detail/evidence drawer.
    """

    owner_review_item = dict(owner_review_item or {})

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "owner_review_item_id": owner_review_item.get("owner_review_item_id"),
        "scenario_id": owner_review_item.get("scenario_id"),
        "owner_review_category": owner_review_item.get("owner_review_category"),
    }

    detail_drawer_id = f"approval_receipt_detail_drawer_{_stable_hash(identity, 18)}"

    receipt_story = _build_receipt_story(owner_review_item)
    source_chain = _build_source_chain(owner_review_item)
    risk_gate_lineage = _build_risk_gate_lineage(owner_review_item)
    owner_action = _build_owner_action_summary(owner_review_item)
    evidence_summary = _build_evidence_summary(owner_review_item)
    safety_flags = _build_safety_flags(owner_review_item)

    sections = [
        receipt_story,
        source_chain,
        risk_gate_lineage,
        owner_action,
        evidence_summary,
        safety_flags,
    ]

    redacted_section_count = sum(1 for section in sections if section.get("redacted_by_default") is True)
    high_sensitivity_section_count = sum(1 for section in sections if section.get("sensitivity") == "high")

    return {
        "detail_drawer_id": detail_drawer_id,
        "sequence": sequence,
        "owner_review_item_id": _safe_text(owner_review_item.get("owner_review_item_id")),
        "queue_item_id": _safe_text(owner_review_item.get("queue_item_id")),
        "expiration_preview_id": _safe_text(owner_review_item.get("expiration_preview_id")),
        "vault_preview_id": _safe_text(owner_review_item.get("vault_preview_id")),
        "ledger_index_id": _safe_text(owner_review_item.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(owner_review_item.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(owner_review_item.get("approval_gate_id")),
        "risk_score_id": _safe_text(owner_review_item.get("risk_score_id")),
        "recommendation_id": _safe_text(owner_review_item.get("recommendation_id")),
        "scenario_id": _safe_text(owner_review_item.get("scenario_id")),
        "owner_review_category": _safe_text(owner_review_item.get("owner_review_category")),
        "owner_review_priority": _safe_text(owner_review_item.get("owner_review_priority")),
        "required_owner_action": _safe_text(owner_review_item.get("required_owner_action")),
        "owner_review_status": _safe_text(owner_review_item.get("owner_review_status")),
        "detail_status": "detail_preview_ready",
        "drawer_title": _safe_text(owner_review_item.get("owner_review_label")),
        "drawer_subtitle": _safe_text(owner_review_item.get("owner_review_reason")),
        "sections": sections,
        "detail_cards": _build_detail_cards(owner_review_item),
        "receipt_story": receipt_story,
        "source_chain": source_chain,
        "risk_gate_lineage": risk_gate_lineage,
        "owner_action": owner_action,
        "evidence_summary": evidence_summary,
        "safety_flags": safety_flags,
        "section_count": len(sections),
        "detail_card_count": 6,
        "redacted_section_count": redacted_section_count,
        "high_sensitivity_section_count": high_sensitivity_section_count,
        "safe_preview_mode": True,
        "raw_secret_visible": False,
        "raw_strategy_visible": False,
        "broker_token_visible": False,
        "unredacted_sensitive_value_visible": False,
        "source_endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "simulated_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
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
        "real_evidence_revealed": False,
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


def _sort_detail_drawers(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_detail_evidence_drawer_payload_cached() -> Dict[str, Any]:
    pack_164_payload = _load_pack_164_payload(force_refresh=False)
    owner_review_items = pack_164_payload.get("owner_review_items", [])

    if not isinstance(owner_review_items, list):
        owner_review_items = []

    detail_drawers: List[Dict[str, Any]] = []
    for idx, item in enumerate(owner_review_items, start=1):
        if isinstance(item, dict):
            detail_drawers.append(build_policy_change_approval_receipt_detail_evidence_drawer_item(item, sequence=idx))

    detail_drawers = _sort_detail_drawers(detail_drawers)

    owner_review_category_counts = _count_by(detail_drawers, "owner_review_category")
    owner_review_priority_counts = _count_by(detail_drawers, "owner_review_priority")
    required_owner_action_counts = _count_by(detail_drawers, "required_owner_action")
    detail_status_counts = _count_by(detail_drawers, "detail_status")
    owner_review_status_counts = _count_by(detail_drawers, "owner_review_status")

    by_owner_review_category = _group_by(detail_drawers, "owner_review_category")
    by_owner_review_priority = _group_by(detail_drawers, "owner_review_priority")
    by_required_owner_action = _group_by(detail_drawers, "required_owner_action")
    by_detail_status = _group_by(detail_drawers, "detail_status")
    by_owner_review_status = _group_by(detail_drawers, "owner_review_status")

    critical_drawers = [
        item for item in detail_drawers
        if item.get("owner_review_category") == "critical_owner_recheck"
    ]
    quarantine_drawers = [
        item for item in detail_drawers
        if item.get("owner_review_category") == "quarantine_owner_recheck"
    ]
    fresh_recheck_drawers = [
        item for item in detail_drawers
        if item.get("owner_review_category") == "fresh_recheck_review"
    ]
    renewal_drawers = [
        item for item in detail_drawers
        if item.get("owner_review_category") == "renewal_review"
    ]
    monitor_drawers = [
        item for item in detail_drawers
        if item.get("owner_review_category") == "monitor_acknowledgement"
    ]

    redacted_drawers = [
        item for item in detail_drawers
        if int(item.get("redacted_section_count") or 0) >= 1
    ]
    high_sensitivity_drawers = [
        item for item in detail_drawers
        if int(item.get("high_sensitivity_section_count") or 0) >= 1
    ]

    required_sections = set(DETAIL_DRAWER_SECTIONS.keys())
    observed_section_sets = [
        {str(section.get("section_id")) for section in item.get("sections", []) if isinstance(section, dict)}
        for item in detail_drawers
    ]

    required_categories = {
        "critical_owner_recheck",
        "quarantine_owner_recheck",
        "fresh_recheck_review",
        "renewal_review",
        "monitor_acknowledgement",
    }
    observed_categories = set(owner_review_category_counts.keys())

    readiness_checks = {
        "pack_164_ready": pack_164_payload.get("status") == "ready",
        "has_detail_drawers": len(detail_drawers) >= 1,
        "detail_count_matches_owner_review_items": len(detail_drawers) == len(owner_review_items),
        "all_simulated_only": all(item.get("simulated_only") is True for item in detail_drawers),
        "all_detail_preview_only": all(item.get("detail_preview_only") is True for item in detail_drawers),
        "all_evidence_drawer_preview_only": all(item.get("evidence_drawer_preview_only") is True for item in detail_drawers),
        "all_owner_review_preview_only": all(item.get("owner_review_preview_only") is True for item in detail_drawers),
        "all_queue_preview_only": all(item.get("queue_preview_only") is True for item in detail_drawers),
        "all_renewal_preview_only": all(item.get("renewal_preview_only") is True for item in detail_drawers),
        "all_recheck_preview_only": all(item.get("recheck_preview_only") is True for item in detail_drawers),
        "all_expiration_preview_only": all(item.get("expiration_preview_only") is True for item in detail_drawers),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in detail_drawers),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in detail_drawers),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in detail_drawers),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in detail_drawers),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in detail_drawers),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in detail_drawers),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in detail_drawers),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in detail_drawers),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in detail_drawers),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in detail_drawers),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in detail_drawers),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in detail_drawers),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in detail_drawers),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in detail_drawers),
        "no_real_expiration_enforced": all(item.get("real_expiration_enforced") is False for item in detail_drawers),
        "no_real_recheck_executed": all(item.get("real_recheck_executed") is False for item in detail_drawers),
        "no_real_renewal_executed": all(item.get("real_renewal_executed") is False for item in detail_drawers),
        "no_real_queue_action_executed": all(item.get("real_queue_action_executed") is False for item in detail_drawers),
        "no_real_owner_review_completed": all(item.get("real_owner_review_completed") is False for item in detail_drawers),
        "no_real_owner_approval_executed": all(item.get("real_owner_approval_executed") is False for item in detail_drawers),
        "no_real_owner_rejection_executed": all(item.get("real_owner_rejection_executed") is False for item in detail_drawers),
        "no_real_owner_acknowledgement_executed": all(item.get("real_owner_acknowledgement_executed") is False for item in detail_drawers),
        "no_real_evidence_revealed": all(item.get("real_evidence_revealed") is False for item in detail_drawers),
        "all_detail_drawer_ids_present": all(bool(item.get("detail_drawer_id")) for item in detail_drawers),
        "all_owner_review_ids_present": all(bool(item.get("owner_review_item_id")) for item in detail_drawers),
        "all_detail_cards_present": all(isinstance(item.get("detail_cards"), list) and len(item.get("detail_cards")) >= 6 for item in detail_drawers),
        "all_sections_present": all(isinstance(item.get("sections"), list) and len(item.get("sections")) >= 6 for item in detail_drawers),
        "all_required_sections_present": all(required_sections.issubset(section_set) for section_set in observed_section_sets),
        "all_safe_preview_mode": all(item.get("safe_preview_mode") is True for item in detail_drawers),
        "no_raw_secret_visible": all(item.get("raw_secret_visible") is False for item in detail_drawers),
        "no_raw_strategy_visible": all(item.get("raw_strategy_visible") is False for item in detail_drawers),
        "no_broker_token_visible": all(item.get("broker_token_visible") is False for item in detail_drawers),
        "no_unredacted_sensitive_value_visible": all(item.get("unredacted_sensitive_value_visible") is False for item in detail_drawers),
        "critical_drawers_present": len(critical_drawers) >= 1,
        "quarantine_drawers_present": len(quarantine_drawers) >= 1,
        "fresh_recheck_drawers_present": len(fresh_recheck_drawers) >= 1,
        "renewal_drawers_present": len(renewal_drawers) >= 1,
        "monitor_drawers_present": len(monitor_drawers) >= 1,
        "redacted_drawers_present": len(redacted_drawers) >= 1,
        "high_sensitivity_drawers_present": len(high_sensitivity_drawers) >= 1,
        "required_category_coverage": required_categories.issubset(observed_categories),
        "endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
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
        "pack_number": 165,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Approval Receipt Detail Preview / Evidence Drawer",
        "endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
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
        "real_evidence_revealed": False,
        "cached_non_recursive": True,
        "source_pack_164": {
            "status": pack_164_payload.get("status"),
            "readiness_score": pack_164_payload.get("summary", {}).get("readiness_score"),
            "owner_review_item_count": pack_164_payload.get("summary", {}).get("owner_review_item_count"),
            "category_counts": pack_164_payload.get("summary", {}).get("category_counts", {}),
            "required_owner_action_counts": pack_164_payload.get("summary", {}).get("required_owner_action_counts", {}),
        },
        "summary": {
            "detail_drawer_count": len(detail_drawers),
            "critical_drawer_count": len(critical_drawers),
            "quarantine_drawer_count": len(quarantine_drawers),
            "fresh_recheck_drawer_count": len(fresh_recheck_drawers),
            "renewal_drawer_count": len(renewal_drawers),
            "monitor_drawer_count": len(monitor_drawers),
            "redacted_drawer_count": len(redacted_drawers),
            "high_sensitivity_drawer_count": len(high_sensitivity_drawers),
            "owner_review_category_counts": owner_review_category_counts,
            "owner_review_priority_counts": owner_review_priority_counts,
            "required_owner_action_counts": required_owner_action_counts,
            "detail_status_counts": detail_status_counts,
            "owner_review_status_counts": owner_review_status_counts,
            "required_sections": sorted(required_sections),
            "observed_categories": sorted(observed_categories),
            "required_categories": sorted(required_categories),
            "readiness_score": readiness_score,
            "readiness_label": "Approval receipt detail evidence drawer ready" if readiness_score == 100 else "Approval receipt detail evidence drawer needs review",
        },
        "readiness_checks": readiness_checks,
        "detail_drawers": detail_drawers,
        "indexes": {
            "by_owner_review_category": by_owner_review_category,
            "by_owner_review_priority": by_owner_review_priority,
            "by_required_owner_action": by_required_owner_action,
            "by_detail_status": by_detail_status,
            "by_owner_review_status": by_owner_review_status,
        },
        "critical_drawers": critical_drawers,
        "quarantine_drawers": quarantine_drawers,
        "fresh_recheck_drawers": fresh_recheck_drawers,
        "renewal_drawers": renewal_drawers,
        "monitor_drawers": monitor_drawers,
        "redacted_drawers": redacted_drawers,
        "high_sensitivity_drawers": high_sensitivity_drawers,
        "quick_action": {
            "id": "policy_change_approval_receipt_detail_evidence_drawer",
            "label": "Approval Receipt Evidence Drawer",
            "href": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
            "description": "Preview evidence drawer details for owner-review approval receipts.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_detail_evidence_drawer",
            "title": "Approval Receipt Evidence Drawer",
            "subtitle": "Previews receipt story, source chain, lineage, evidence summary, and safety flags.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_detail_evidence_drawer_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_detail_evidence_drawer_payload_cached())


def get_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_detail_evidence_drawer_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 165,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Approval receipt detail evidence drawer ready"),
        "detail_drawer_count": summary.get("detail_drawer_count", 0),
        "critical_drawer_count": summary.get("critical_drawer_count", 0),
        "quarantine_drawer_count": summary.get("quarantine_drawer_count", 0),
        "fresh_recheck_drawer_count": summary.get("fresh_recheck_drawer_count", 0),
        "renewal_drawer_count": summary.get("renewal_drawer_count", 0),
        "monitor_drawer_count": summary.get("monitor_drawer_count", 0),
        "redacted_drawer_count": summary.get("redacted_drawer_count", 0),
        "high_sensitivity_drawer_count": summary.get("high_sensitivity_drawer_count", 0),
        "owner_review_category_counts": summary.get("owner_review_category_counts", {}),
        "required_owner_action_counts": summary.get("required_owner_action_counts", {}),
        "detail_status_counts": summary.get("detail_status_counts", {}),
        "simulated_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
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
        "real_evidence_revealed": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_detail_evidence_drawer_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_detail_evidence_drawer_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_detail_evidence_drawer_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_detail_evidence_drawer_status_bridge()
    return {
        "id": "policy_change_approval_receipt_detail_evidence_drawer",
        "label": "Approval Receipt Evidence Drawer",
        "title": "Approval Receipt Detail Preview / Evidence Drawer",
        "href": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "description": "Preview receipt story, source chain, lineage, evidence summary, and safety flags.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 165",
        "category": "policy",
        "simulated_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
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


def build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_detail_evidence_drawer_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "detail_drawer_readiness",
            "title": "Evidence drawer readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Approval receipt detail evidence drawer ready"),
        },
        {
            "id": "detail_drawers",
            "title": "Detail drawers",
            "value": summary.get("detail_drawer_count", 0),
            "label": "Owner-review receipts with drawer previews",
        },
        {
            "id": "redacted_drawers",
            "title": "Redacted drawers",
            "value": summary.get("redacted_drawer_count", 0),
            "label": "High-sensitivity sections redacted by default",
        },
        {
            "id": "high_sensitivity",
            "title": "High sensitivity",
            "value": summary.get("high_sensitivity_drawer_count", 0),
            "label": "Contains safe evidence/safety flag summaries",
        },
        {
            "id": "critical_detail",
            "title": "Critical / quarantine",
            "value": f"{summary.get('critical_drawer_count', 0)} / {summary.get('quarantine_drawer_count', 0)}",
            "label": "Highest attention evidence drawers",
        },
        {
            "id": "no_real_evidence",
            "title": "Real evidence reveal",
            "value": "No" if checks.get("no_real_evidence_revealed") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_detail_evidence_drawer",
        "title": "Approval Receipt Evidence Drawer",
        "subtitle": "Previews receipt story, source chain, lineage, evidence summary, and safety flags without revealing raw secrets.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "detail_preview_only": True,
        "evidence_drawer_preview_only": True,
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


def build_policy_change_approval_receipt_detail_evidence_drawer_html_section() -> str:
    section = build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-detail-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-detail-section" id="policy-change-approval-receipt-detail-evidence-drawer">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 165</p>
            <h2>{section.get('title', 'Approval Receipt Evidence Drawer')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT}">Open approval receipt evidence drawer JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT",
    "APPROVAL_RECEIPT_OWNER_REVIEW_ENDPOINT",
    "DETAIL_DRAWER_SECTIONS",
    "build_policy_change_approval_receipt_detail_evidence_drawer_item",
    "build_policy_change_approval_receipt_detail_evidence_drawer_payload",
    "get_policy_change_approval_receipt_detail_evidence_drawer_payload",
    "build_policy_change_approval_receipt_detail_evidence_drawer_status_bridge",
    "get_policy_change_approval_receipt_detail_evidence_drawer_status_bridge",
    "build_policy_change_approval_receipt_detail_evidence_drawer_quick_action",
    "build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section",
    "build_policy_change_approval_receipt_detail_evidence_drawer_html_section",
]
