
"""
PACK 166 - Approval Receipt Evidence Drawer UI Index / Detail Lookup.

This module sits on top of Pack 165.

Pack 165 creates simulated approval receipt detail/evidence drawers.
Pack 166 builds a lookup/index layer so the Tower can retrieve drawer previews by:
- detail drawer ID
- owner review item ID
- queue item ID
- scenario ID
- owner review category
- required owner action
- owner review priority
- detail status
- risk/evidence lane

Important:
- simulated-only
- lookup-preview-only
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
- no raw secrets exposed
- cached
- non-recursive
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib
from functools import lru_cache
from typing import Any, Dict, List, Optional


PACK_ID = "PACK_166"
APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT = "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT = "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"


LOOKUP_KEYS = {
    "by_detail_drawer_id": {
        "label": "Detail Drawer ID",
        "description": "Direct lookup by Pack 165 detail drawer ID.",
        "unique": True,
    },
    "by_owner_review_item_id": {
        "label": "Owner Review Item ID",
        "description": "Direct lookup by Pack 164 owner-review item ID.",
        "unique": True,
    },
    "by_queue_item_id": {
        "label": "Queue Item ID",
        "description": "Direct lookup by Pack 163 queue item ID.",
        "unique": True,
    },
    "by_scenario_id": {
        "label": "Scenario ID",
        "description": "Lookup by scenario/policy simulation identifier.",
        "unique": False,
    },
    "by_owner_review_category": {
        "label": "Owner Review Category",
        "description": "Group drawers by owner-review category.",
        "unique": False,
    },
    "by_required_owner_action": {
        "label": "Required Owner Action",
        "description": "Group drawers by required owner action.",
        "unique": False,
    },
    "by_owner_review_priority": {
        "label": "Owner Review Priority",
        "description": "Group drawers by priority lane.",
        "unique": False,
    },
    "by_detail_status": {
        "label": "Detail Status",
        "description": "Group drawers by detail status.",
        "unique": False,
    },
    "by_risk_lane": {
        "label": "Risk / Evidence Lane",
        "description": "Group drawers by derived risk/evidence UI lane.",
        "unique": False,
    },
}


RISK_LANE_RULES = {
    "critical_owner_recheck": "critical_evidence_lane",
    "quarantine_owner_recheck": "quarantine_evidence_lane",
    "fresh_recheck_review": "fresh_recheck_evidence_lane",
    "renewal_review": "renewal_evidence_lane",
    "monitor_acknowledgement": "monitor_evidence_lane",
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


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _load_pack_165_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
        fn = getattr(mod, "build_policy_change_approval_receipt_detail_evidence_drawer_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_165",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "detail_drawer_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 165 detail evidence drawer payload unavailable",
            },
            "detail_drawers": [],
        }

    return {
        "pack_id": "PACK_165",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
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
        "summary": {
            "detail_drawer_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 165 detail evidence drawer payload unavailable",
        },
        "detail_drawers": [],
    }



def _derive_risk_lane(detail_drawer: Dict[str, Any]) -> str:
    category = _safe_text(detail_drawer.get("owner_review_category"))
    if category in RISK_LANE_RULES:
        return RISK_LANE_RULES[category]

    priority = _safe_text(detail_drawer.get("owner_review_priority")).lower()
    if priority == "critical":
        return "critical_evidence_lane"
    if priority == "high":
        return "high_evidence_lane"
    if priority == "medium":
        return "medium_evidence_lane"
    if priority == "monitor":
        return "monitor_evidence_lane"

    return "unknown_evidence_lane"


def _build_lookup_display_record(detail_drawer: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    detail_drawer = dict(detail_drawer or {})
    risk_lane = _derive_risk_lane(detail_drawer)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "detail_drawer_id": detail_drawer.get("detail_drawer_id"),
        "owner_review_item_id": detail_drawer.get("owner_review_item_id"),
        "scenario_id": detail_drawer.get("scenario_id"),
        "risk_lane": risk_lane,
    }

    lookup_record_id = f"evidence_drawer_lookup_record_{_stable_hash(identity, 18)}"

    return {
        "lookup_record_id": lookup_record_id,
        "sequence": sequence,
        "detail_drawer_id": _safe_text(detail_drawer.get("detail_drawer_id")),
        "owner_review_item_id": _safe_text(detail_drawer.get("owner_review_item_id")),
        "queue_item_id": _safe_text(detail_drawer.get("queue_item_id")),
        "expiration_preview_id": _safe_text(detail_drawer.get("expiration_preview_id")),
        "vault_preview_id": _safe_text(detail_drawer.get("vault_preview_id")),
        "ledger_index_id": _safe_text(detail_drawer.get("ledger_index_id")),
        "approval_receipt_preview_id": _safe_text(detail_drawer.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(detail_drawer.get("approval_gate_id")),
        "risk_score_id": _safe_text(detail_drawer.get("risk_score_id")),
        "recommendation_id": _safe_text(detail_drawer.get("recommendation_id")),
        "scenario_id": _safe_text(detail_drawer.get("scenario_id")),
        "owner_review_category": _safe_text(detail_drawer.get("owner_review_category")),
        "owner_review_priority": _safe_text(detail_drawer.get("owner_review_priority")),
        "required_owner_action": _safe_text(detail_drawer.get("required_owner_action")),
        "owner_review_status": _safe_text(detail_drawer.get("owner_review_status")),
        "detail_status": _safe_text(detail_drawer.get("detail_status")),
        "risk_lane": risk_lane,
        "drawer_title": _safe_text(detail_drawer.get("drawer_title")),
        "drawer_subtitle": _safe_text(detail_drawer.get("drawer_subtitle")),
        "section_count": int(detail_drawer.get("section_count") or 0),
        "detail_card_count": int(detail_drawer.get("detail_card_count") or 0),
        "redacted_section_count": int(detail_drawer.get("redacted_section_count") or 0),
        "high_sensitivity_section_count": int(detail_drawer.get("high_sensitivity_section_count") or 0),
        "safe_preview_mode": bool(detail_drawer.get("safe_preview_mode", False)),
        "raw_secret_visible": False,
        "raw_strategy_visible": False,
        "broker_token_visible": False,
        "unredacted_sensitive_value_visible": False,
        "lookup_result_type": "detail_drawer_preview",
        "detail_lookup_allowed": True,
        "raw_evidence_lookup_allowed": False,
        "source_endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "simulated_only": True,
        "lookup_preview_only": True,
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


def _add_to_unique_index(index: Dict[str, Dict[str, Any]], key: Any, record: Dict[str, Any]) -> None:
    safe_key = _safe_text(key)
    if safe_key:
        index[safe_key] = record


def _add_to_group_index(index: Dict[str, List[Dict[str, Any]]], key: Any, record: Dict[str, Any]) -> None:
    safe_key = _safe_text(key) or "unknown"
    index.setdefault(safe_key, []).append(record)


def _build_lookup_indexes(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes: Dict[str, Any] = {
        "by_detail_drawer_id": {},
        "by_owner_review_item_id": {},
        "by_queue_item_id": {},
        "by_scenario_id": {},
        "by_owner_review_category": {},
        "by_required_owner_action": {},
        "by_owner_review_priority": {},
        "by_detail_status": {},
        "by_risk_lane": {},
    }

    for record in records:
        if not isinstance(record, dict):
            continue

        _add_to_unique_index(indexes["by_detail_drawer_id"], record.get("detail_drawer_id"), record)
        _add_to_unique_index(indexes["by_owner_review_item_id"], record.get("owner_review_item_id"), record)
        _add_to_unique_index(indexes["by_queue_item_id"], record.get("queue_item_id"), record)

        _add_to_group_index(indexes["by_scenario_id"], record.get("scenario_id"), record)
        _add_to_group_index(indexes["by_owner_review_category"], record.get("owner_review_category"), record)
        _add_to_group_index(indexes["by_required_owner_action"], record.get("required_owner_action"), record)
        _add_to_group_index(indexes["by_owner_review_priority"], record.get("owner_review_priority"), record)
        _add_to_group_index(indexes["by_detail_status"], record.get("detail_status"), record)
        _add_to_group_index(indexes["by_risk_lane"], record.get("risk_lane"), record)

    return indexes


def _lookup_one(index: Dict[str, Dict[str, Any]], key: Any) -> Optional[Dict[str, Any]]:
    safe_key = _safe_text(key)
    if not safe_key or not isinstance(index, dict):
        return None
    record = index.get(safe_key)
    if isinstance(record, dict):
        return copy.deepcopy(record)
    return None


def _lookup_many(index: Dict[str, List[Dict[str, Any]]], key: Any) -> List[Dict[str, Any]]:
    safe_key = _safe_text(key) or "unknown"
    if not isinstance(index, dict):
        return []
    records = index.get(safe_key, [])
    if not isinstance(records, list):
        return []
    return copy.deepcopy([record for record in records if isinstance(record, dict)])


def _build_lookup_query_examples(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    examples: Dict[str, Any] = {
        "detail_drawer_id": None,
        "owner_review_item_id": None,
        "queue_item_id": None,
        "scenario_id": None,
        "owner_review_category": None,
        "required_owner_action": None,
        "owner_review_priority": None,
        "detail_status": None,
        "risk_lane": None,
    }

    if records:
        first = records[0]
        for key in examples:
            examples[key] = first.get(key)

    return examples



def _count_by(records: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        group_key = _safe_text(record.get(key)) or "unknown"
        counts[group_key] = counts.get(group_key, 0) + 1
    return counts


def _sort_lookup_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "monitor": 4,
    }
    lane_rank = {
        "critical_evidence_lane": 1,
        "quarantine_evidence_lane": 2,
        "fresh_recheck_evidence_lane": 3,
        "renewal_evidence_lane": 4,
        "monitor_evidence_lane": 5,
    }
    return sorted(
        records,
        key=lambda record: (
            priority_rank.get(str(record.get("owner_review_priority")), 99),
            lane_rank.get(str(record.get("risk_lane")), 99),
            int(record.get("sequence") or 999),
        ),
    )


def _build_lookup_preview(indexes: Dict[str, Any], examples: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "by_detail_drawer_id": _lookup_one(indexes.get("by_detail_drawer_id", {}), examples.get("detail_drawer_id")),
        "by_owner_review_item_id": _lookup_one(indexes.get("by_owner_review_item_id", {}), examples.get("owner_review_item_id")),
        "by_queue_item_id": _lookup_one(indexes.get("by_queue_item_id", {}), examples.get("queue_item_id")),
        "by_scenario_id": _lookup_many(indexes.get("by_scenario_id", {}), examples.get("scenario_id")),
        "by_owner_review_category": _lookup_many(indexes.get("by_owner_review_category", {}), examples.get("owner_review_category")),
        "by_required_owner_action": _lookup_many(indexes.get("by_required_owner_action", {}), examples.get("required_owner_action")),
        "by_owner_review_priority": _lookup_many(indexes.get("by_owner_review_priority", {}), examples.get("owner_review_priority")),
        "by_detail_status": _lookup_many(indexes.get("by_detail_status", {}), examples.get("detail_status")),
        "by_risk_lane": _lookup_many(indexes.get("by_risk_lane", {}), examples.get("risk_lane")),
    }


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_evidence_drawer_lookup_payload_cached() -> Dict[str, Any]:
    pack_165_payload = _load_pack_165_payload(force_refresh=False)
    detail_drawers = pack_165_payload.get("detail_drawers", [])

    if not isinstance(detail_drawers, list):
        detail_drawers = []

    lookup_records: List[Dict[str, Any]] = []
    for idx, drawer in enumerate(detail_drawers, start=1):
        if isinstance(drawer, dict):
            lookup_records.append(_build_lookup_display_record(drawer, sequence=idx))

    lookup_records = _sort_lookup_records(lookup_records)
    indexes = _build_lookup_indexes(lookup_records)
    examples = _build_lookup_query_examples(lookup_records)
    lookup_preview = _build_lookup_preview(indexes, examples)

    risk_lane_counts = _count_by(lookup_records, "risk_lane")
    owner_review_category_counts = _count_by(lookup_records, "owner_review_category")
    required_owner_action_counts = _count_by(lookup_records, "required_owner_action")
    owner_review_priority_counts = _count_by(lookup_records, "owner_review_priority")
    detail_status_counts = _count_by(lookup_records, "detail_status")

    unique_index_counts = {
        "by_detail_drawer_id": len(indexes.get("by_detail_drawer_id", {})),
        "by_owner_review_item_id": len(indexes.get("by_owner_review_item_id", {})),
        "by_queue_item_id": len(indexes.get("by_queue_item_id", {})),
    }

    group_index_counts = {
        "by_scenario_id": len(indexes.get("by_scenario_id", {})),
        "by_owner_review_category": len(indexes.get("by_owner_review_category", {})),
        "by_required_owner_action": len(indexes.get("by_required_owner_action", {})),
        "by_owner_review_priority": len(indexes.get("by_owner_review_priority", {})),
        "by_detail_status": len(indexes.get("by_detail_status", {})),
        "by_risk_lane": len(indexes.get("by_risk_lane", {})),
    }

    expected_risk_lanes = {
        "critical_evidence_lane",
        "quarantine_evidence_lane",
        "fresh_recheck_evidence_lane",
        "renewal_evidence_lane",
        "monitor_evidence_lane",
    }
    observed_risk_lanes = set(risk_lane_counts.keys())

    expected_group_indexes = {
        "by_scenario_id",
        "by_owner_review_category",
        "by_required_owner_action",
        "by_owner_review_priority",
        "by_detail_status",
        "by_risk_lane",
    }

    expected_unique_indexes = {
        "by_detail_drawer_id",
        "by_owner_review_item_id",
        "by_queue_item_id",
    }

    lookup_preview_checks = {
        "detail_drawer_lookup_returns_record": isinstance(lookup_preview.get("by_detail_drawer_id"), dict),
        "owner_review_lookup_returns_record": isinstance(lookup_preview.get("by_owner_review_item_id"), dict),
        "queue_item_lookup_returns_record": isinstance(lookup_preview.get("by_queue_item_id"), dict),
        "scenario_lookup_returns_list": isinstance(lookup_preview.get("by_scenario_id"), list) and len(lookup_preview.get("by_scenario_id", [])) >= 1,
        "category_lookup_returns_list": isinstance(lookup_preview.get("by_owner_review_category"), list) and len(lookup_preview.get("by_owner_review_category", [])) >= 1,
        "action_lookup_returns_list": isinstance(lookup_preview.get("by_required_owner_action"), list) and len(lookup_preview.get("by_required_owner_action", [])) >= 1,
        "priority_lookup_returns_list": isinstance(lookup_preview.get("by_owner_review_priority"), list) and len(lookup_preview.get("by_owner_review_priority", [])) >= 1,
        "detail_status_lookup_returns_list": isinstance(lookup_preview.get("by_detail_status"), list) and len(lookup_preview.get("by_detail_status", [])) >= 1,
        "risk_lane_lookup_returns_list": isinstance(lookup_preview.get("by_risk_lane"), list) and len(lookup_preview.get("by_risk_lane", [])) >= 1,
    }

    readiness_checks = {
        "pack_165_ready": pack_165_payload.get("status") == "ready",
        "has_lookup_records": len(lookup_records) >= 1,
        "lookup_count_matches_detail_drawers": len(lookup_records) == len(detail_drawers),
        "all_simulated_only": all(record.get("simulated_only") is True for record in lookup_records),
        "all_lookup_preview_only": all(record.get("lookup_preview_only") is True for record in lookup_records),
        "all_detail_preview_only": all(record.get("detail_preview_only") is True for record in lookup_records),
        "all_evidence_drawer_preview_only": all(record.get("evidence_drawer_preview_only") is True for record in lookup_records),
        "all_owner_review_preview_only": all(record.get("owner_review_preview_only") is True for record in lookup_records),
        "all_queue_preview_only": all(record.get("queue_preview_only") is True for record in lookup_records),
        "all_renewal_preview_only": all(record.get("renewal_preview_only") is True for record in lookup_records),
        "all_recheck_preview_only": all(record.get("recheck_preview_only") is True for record in lookup_records),
        "all_expiration_preview_only": all(record.get("expiration_preview_only") is True for record in lookup_records),
        "all_vault_preview_only": all(record.get("vault_preview_only") is True for record in lookup_records),
        "all_index_preview_only": all(record.get("index_preview_only") is True for record in lookup_records),
        "all_receipt_preview_only": all(record.get("receipt_preview_only") is True for record in lookup_records),
        "all_approval_preview_only": all(record.get("approval_preview_only") is True for record in lookup_records),
        "all_evidence_preview_only": all(record.get("evidence_preview_only") is True for record in lookup_records),
        "no_real_approval_executed": all(record.get("real_approval_executed") is False for record in lookup_records),
        "no_real_policy_change": all(record.get("real_policy_change_executed") is False for record in lookup_records),
        "no_real_permission_change": all(record.get("real_permission_change_executed") is False for record in lookup_records),
        "no_real_access_granted": all(record.get("real_access_granted") is False for record in lookup_records),
        "no_real_enforcement": all(record.get("real_enforcement_executed") is False for record in lookup_records),
        "no_real_audit_written": all(record.get("real_audit_written") is False for record in lookup_records),
        "no_real_receipt_written": all(record.get("real_receipt_written") is False for record in lookup_records),
        "no_real_archive_written": all(record.get("real_archive_written") is False for record in lookup_records),
        "no_real_vault_written": all(record.get("real_vault_written") is False for record in lookup_records),
        "no_real_expiration_enforced": all(record.get("real_expiration_enforced") is False for record in lookup_records),
        "no_real_recheck_executed": all(record.get("real_recheck_executed") is False for record in lookup_records),
        "no_real_renewal_executed": all(record.get("real_renewal_executed") is False for record in lookup_records),
        "no_real_queue_action_executed": all(record.get("real_queue_action_executed") is False for record in lookup_records),
        "no_real_owner_review_completed": all(record.get("real_owner_review_completed") is False for record in lookup_records),
        "no_real_owner_approval_executed": all(record.get("real_owner_approval_executed") is False for record in lookup_records),
        "no_real_owner_rejection_executed": all(record.get("real_owner_rejection_executed") is False for record in lookup_records),
        "no_real_owner_acknowledgement_executed": all(record.get("real_owner_acknowledgement_executed") is False for record in lookup_records),
        "no_real_evidence_revealed": all(record.get("real_evidence_revealed") is False for record in lookup_records),
        "no_raw_secret_visible": all(record.get("raw_secret_visible") is False for record in lookup_records),
        "no_raw_strategy_visible": all(record.get("raw_strategy_visible") is False for record in lookup_records),
        "no_broker_token_visible": all(record.get("broker_token_visible") is False for record in lookup_records),
        "no_unredacted_sensitive_value_visible": all(record.get("unredacted_sensitive_value_visible") is False for record in lookup_records),
        "all_lookup_record_ids_present": all(bool(record.get("lookup_record_id")) for record in lookup_records),
        "all_detail_drawer_ids_present": all(bool(record.get("detail_drawer_id")) for record in lookup_records),
        "all_owner_review_item_ids_present": all(bool(record.get("owner_review_item_id")) for record in lookup_records),
        "all_queue_item_ids_present": all(bool(record.get("queue_item_id")) for record in lookup_records),
        "all_risk_lanes_present": all(bool(record.get("risk_lane")) for record in lookup_records),
        "all_lookup_result_type_present": all(record.get("lookup_result_type") == "detail_drawer_preview" for record in lookup_records),
        "all_detail_lookup_allowed": all(record.get("detail_lookup_allowed") is True for record in lookup_records),
        "all_raw_evidence_lookup_blocked": all(record.get("raw_evidence_lookup_allowed") is False for record in lookup_records),
        "all_unique_indexes_present": expected_unique_indexes.issubset(set(indexes.keys())),
        "all_group_indexes_present": expected_group_indexes.issubset(set(indexes.keys())),
        "unique_detail_drawer_index_complete": unique_index_counts["by_detail_drawer_id"] == len(lookup_records),
        "unique_owner_review_index_complete": unique_index_counts["by_owner_review_item_id"] == len(lookup_records),
        "unique_queue_item_index_complete": unique_index_counts["by_queue_item_id"] == len(lookup_records),
        "risk_lane_coverage": expected_risk_lanes.issubset(observed_risk_lanes),
        "lookup_preview_checks_pass": all(lookup_preview_checks.values()),
        "endpoint": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
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
        "pack_number": 166,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Approval Receipt Evidence Drawer UI Index / Detail Lookup",
        "endpoint": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "lookup_preview_only": True,
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
        "source_pack_165": {
            "status": pack_165_payload.get("status"),
            "readiness_score": pack_165_payload.get("summary", {}).get("readiness_score"),
            "detail_drawer_count": pack_165_payload.get("summary", {}).get("detail_drawer_count"),
            "owner_review_category_counts": pack_165_payload.get("summary", {}).get("owner_review_category_counts", {}),
            "detail_status_counts": pack_165_payload.get("summary", {}).get("detail_status_counts", {}),
        },
        "summary": {
            "lookup_record_count": len(lookup_records),
            "detail_drawer_count": len(detail_drawers),
            "unique_index_counts": unique_index_counts,
            "group_index_counts": group_index_counts,
            "risk_lane_counts": risk_lane_counts,
            "owner_review_category_counts": owner_review_category_counts,
            "required_owner_action_counts": required_owner_action_counts,
            "owner_review_priority_counts": owner_review_priority_counts,
            "detail_status_counts": detail_status_counts,
            "observed_risk_lanes": sorted(observed_risk_lanes),
            "expected_risk_lanes": sorted(expected_risk_lanes),
            "lookup_key_count": len(LOOKUP_KEYS),
            "readiness_score": readiness_score,
            "readiness_label": "Approval receipt evidence drawer lookup ready" if readiness_score == 100 else "Approval receipt evidence drawer lookup needs review",
        },
        "readiness_checks": readiness_checks,
        "lookup_preview_checks": lookup_preview_checks,
        "lookup_records": lookup_records,
        "lookup_keys": LOOKUP_KEYS,
        "indexes": indexes,
        "lookup_query_examples": examples,
        "lookup_preview": lookup_preview,
        "quick_action": {
            "id": "policy_change_approval_receipt_evidence_drawer_lookup",
            "label": "Evidence Drawer Lookup",
            "href": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
            "description": "Preview lookup indexes for approval receipt evidence drawers.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_evidence_drawer_lookup",
            "title": "Evidence Drawer Lookup",
            "subtitle": "Preview lookup by drawer ID, owner-review ID, scenario, category, action, priority, status, or risk lane.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_evidence_drawer_lookup_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_evidence_drawer_lookup_payload_cached())


def get_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 166,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Approval receipt evidence drawer lookup ready"),
        "lookup_record_count": summary.get("lookup_record_count", 0),
        "detail_drawer_count": summary.get("detail_drawer_count", 0),
        "lookup_key_count": summary.get("lookup_key_count", 0),
        "unique_index_counts": summary.get("unique_index_counts", {}),
        "group_index_counts": summary.get("group_index_counts", {}),
        "risk_lane_counts": summary.get("risk_lane_counts", {}),
        "owner_review_category_counts": summary.get("owner_review_category_counts", {}),
        "required_owner_action_counts": summary.get("required_owner_action_counts", {}),
        "owner_review_priority_counts": summary.get("owner_review_priority_counts", {}),
        "detail_status_counts": summary.get("detail_status_counts", {}),
        "simulated_only": True,
        "lookup_preview_only": True,
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


def get_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_evidence_drawer_lookup_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge()
    return {
        "id": "policy_change_approval_receipt_evidence_drawer_lookup",
        "label": "Evidence Drawer Lookup",
        "title": "Approval Receipt Evidence Drawer UI Index / Detail Lookup",
        "href": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "description": "Preview lookup indexes for approval receipt evidence drawers.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 166",
        "category": "policy",
        "simulated_only": True,
        "lookup_preview_only": True,
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


def build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_evidence_drawer_lookup_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    unique_indexes = summary.get("unique_index_counts", {})
    group_indexes = summary.get("group_index_counts", {})

    cards = [
        {
            "id": "lookup_readiness",
            "title": "Lookup readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Approval receipt evidence drawer lookup ready"),
        },
        {
            "id": "lookup_records",
            "title": "Lookup records",
            "value": summary.get("lookup_record_count", 0),
            "label": "Evidence drawer records indexed",
        },
        {
            "id": "lookup_keys",
            "title": "Lookup keys",
            "value": summary.get("lookup_key_count", 0),
            "label": "Supported lookup routes",
        },
        {
            "id": "unique_indexes",
            "title": "Unique indexes",
            "value": sum(int(v or 0) for v in unique_indexes.values()),
            "label": "Drawer/owner/queue direct lookups",
        },
        {
            "id": "group_indexes",
            "title": "Group indexes",
            "value": len(group_indexes),
            "label": "Scenario/category/action/priority/status/risk",
        },
        {
            "id": "raw_evidence_lookup",
            "title": "Raw evidence lookup",
            "value": "Blocked" if checks.get("all_raw_evidence_lookup_blocked") else "Review",
            "label": "Preview detail only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_evidence_drawer_lookup",
        "title": "Evidence Drawer Lookup",
        "subtitle": "Preview lookup by drawer ID, owner-review ID, scenario, category, action, priority, status, or risk lane.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "lookup_preview_only": True,
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


def build_policy_change_approval_receipt_evidence_drawer_lookup_html_section() -> str:
    section = build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-lookup-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-lookup-section" id="policy-change-approval-receipt-evidence-drawer-lookup">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 166</p>
            <h2>{section.get('title', 'Evidence Drawer Lookup')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT}">Open evidence drawer lookup JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_EVIDENCE_DRAWER_LOOKUP_ENDPOINT",
    "APPROVAL_RECEIPT_DETAIL_EVIDENCE_ENDPOINT",
    "LOOKUP_KEYS",
    "RISK_LANE_RULES",
    "build_policy_change_approval_receipt_evidence_drawer_lookup_payload",
    "get_policy_change_approval_receipt_evidence_drawer_lookup_payload",
    "build_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge",
    "get_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge",
    "build_policy_change_approval_receipt_evidence_drawer_lookup_quick_action",
    "build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section",
    "build_policy_change_approval_receipt_evidence_drawer_lookup_html_section",
]
