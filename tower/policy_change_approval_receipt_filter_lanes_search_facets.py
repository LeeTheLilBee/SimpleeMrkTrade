
"""
PACK 167 - Evidence Drawer Filter Lanes / Search Facets.

This module sits on top of Pack 166.

Pack 166 creates simulated evidence drawer lookup records and indexes.
Pack 167 creates safe filter lanes and search facets for the evidence drawer UI:
- category filters
- required action filters
- priority filters
- risk lane filters
- detail status filters
- scenario filters
- sensitivity/redaction filters
- safety visibility filters

Important:
- simulated-only
- filter-preview-only
- search-facet-preview-only
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
- no raw evidence lookup
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


PACK_ID = "PACK_167"
FILTER_LANES_ENDPOINT = "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
EVIDENCE_DRAWER_LOOKUP_ENDPOINT = "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"


FILTER_LANES = {
    "owner_review_category": {
        "label": "Owner Review Category",
        "description": "Filter evidence drawer records by owner-review category.",
        "source_field": "owner_review_category",
        "lane_type": "category",
    },
    "required_owner_action": {
        "label": "Required Owner Action",
        "description": "Filter evidence drawer records by required owner action.",
        "source_field": "required_owner_action",
        "lane_type": "action",
    },
    "owner_review_priority": {
        "label": "Owner Review Priority",
        "description": "Filter evidence drawer records by priority.",
        "source_field": "owner_review_priority",
        "lane_type": "priority",
    },
    "risk_lane": {
        "label": "Risk Lane",
        "description": "Filter evidence drawer records by derived risk/evidence lane.",
        "source_field": "risk_lane",
        "lane_type": "risk",
    },
    "detail_status": {
        "label": "Detail Status",
        "description": "Filter evidence drawer records by drawer/detail status.",
        "source_field": "detail_status",
        "lane_type": "status",
    },
    "scenario_id": {
        "label": "Scenario",
        "description": "Filter evidence drawer records by scenario ID.",
        "source_field": "scenario_id",
        "lane_type": "scenario",
    },
    "sensitivity_redaction": {
        "label": "Sensitivity / Redaction",
        "description": "Filter evidence drawer records by redaction and high-sensitivity state.",
        "source_field": "sensitivity_redaction",
        "lane_type": "safety",
    },
    "safety_visibility": {
        "label": "Safety Visibility",
        "description": "Filter evidence drawer records by safe preview and raw evidence visibility rules.",
        "source_field": "safety_visibility",
        "lane_type": "safety",
    },
}


EXPECTED_FILTER_LANES = set(FILTER_LANES.keys())


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


def _load_pack_166_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
        fn = getattr(mod, "build_policy_change_approval_receipt_evidence_drawer_lookup_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_166",
            "status": "review",
            "endpoint": EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "lookup_record_count": 0,
                "detail_drawer_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 166 evidence drawer lookup payload unavailable",
            },
            "lookup_records": [],
        }

    return {
        "pack_id": "PACK_166",
        "status": "review",
        "endpoint": EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
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
        "summary": {
            "lookup_record_count": 0,
            "detail_drawer_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 166 evidence drawer lookup payload unavailable",
        },
        "lookup_records": [],
    }


def _derive_sensitivity_redaction(record: Dict[str, Any]) -> str:
    redacted = int(record.get("redacted_section_count") or 0)
    high = int(record.get("high_sensitivity_section_count") or 0)

    if redacted >= 1 and high >= 1:
        return "redacted_high_sensitivity"
    if redacted >= 1:
        return "redacted"
    if high >= 1:
        return "high_sensitivity"
    return "standard_preview"


def _derive_safety_visibility(record: Dict[str, Any]) -> str:
    safe_preview = bool(record.get("safe_preview_mode", False))
    raw_secret_visible = bool(record.get("raw_secret_visible", False))
    raw_strategy_visible = bool(record.get("raw_strategy_visible", False))
    broker_token_visible = bool(record.get("broker_token_visible", False))
    raw_evidence_allowed = bool(record.get("raw_evidence_lookup_allowed", False))

    if not safe_preview:
        return "unsafe_preview_blocked"

    if raw_secret_visible or raw_strategy_visible or broker_token_visible or raw_evidence_allowed:
        return "raw_visibility_blocked"

    return "safe_preview_only"


def _build_filter_record(record: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    record = dict(record or {})
    sensitivity_redaction = _derive_sensitivity_redaction(record)
    safety_visibility = _derive_safety_visibility(record)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "lookup_record_id": record.get("lookup_record_id"),
        "detail_drawer_id": record.get("detail_drawer_id"),
        "risk_lane": record.get("risk_lane"),
        "sensitivity_redaction": sensitivity_redaction,
        "safety_visibility": safety_visibility,
    }

    filter_record_id = f"evidence_drawer_filter_record_{_stable_hash(identity, 18)}"

    return {
        "filter_record_id": filter_record_id,
        "sequence": sequence,
        "lookup_record_id": _safe_text(record.get("lookup_record_id")),
        "detail_drawer_id": _safe_text(record.get("detail_drawer_id")),
        "owner_review_item_id": _safe_text(record.get("owner_review_item_id")),
        "queue_item_id": _safe_text(record.get("queue_item_id")),
        "scenario_id": _safe_text(record.get("scenario_id")),
        "owner_review_category": _safe_text(record.get("owner_review_category")),
        "owner_review_priority": _safe_text(record.get("owner_review_priority")),
        "required_owner_action": _safe_text(record.get("required_owner_action")),
        "owner_review_status": _safe_text(record.get("owner_review_status")),
        "detail_status": _safe_text(record.get("detail_status")),
        "risk_lane": _safe_text(record.get("risk_lane")),
        "drawer_title": _safe_text(record.get("drawer_title")),
        "drawer_subtitle": _safe_text(record.get("drawer_subtitle")),
        "section_count": int(record.get("section_count") or 0),
        "detail_card_count": int(record.get("detail_card_count") or 0),
        "redacted_section_count": int(record.get("redacted_section_count") or 0),
        "high_sensitivity_section_count": int(record.get("high_sensitivity_section_count") or 0),
        "sensitivity_redaction": sensitivity_redaction,
        "safety_visibility": safety_visibility,
        "safe_preview_mode": bool(record.get("safe_preview_mode", False)),
        "raw_secret_visible": False,
        "raw_strategy_visible": False,
        "broker_token_visible": False,
        "unredacted_sensitive_value_visible": False,
        "raw_evidence_lookup_allowed": False,
        "filter_result_type": "evidence_drawer_filter_preview",
        "facet_result_allowed": True,
        "raw_evidence_reveal_allowed": False,
        "source_endpoint": EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
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


def _sort_filter_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "monitor": 4,
    }
    risk_rank = {
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
            risk_rank.get(str(record.get("risk_lane")), 99),
            int(record.get("sequence") or 999),
        ),
    )


def _count_by(records: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        value = _safe_text(record.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_facet_option(lane_id: str, value: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    lane = FILTER_LANES.get(lane_id, {})
    safe_value = _safe_text(value) or "unknown"
    record_ids = [
        _safe_text(record.get("filter_record_id"))
        for record in records
        if isinstance(record, dict) and record.get("filter_record_id")
    ]

    detail_drawer_ids = [
        _safe_text(record.get("detail_drawer_id"))
        for record in records
        if isinstance(record, dict) and record.get("detail_drawer_id")
    ]

    identity = {
        "lane": lane_id,
        "value": safe_value,
        "record_ids": record_ids,
    }

    return {
        "facet_option_id": f"evidence_drawer_facet_{_stable_hash(identity, 18)}",
        "lane_id": lane_id,
        "lane_label": _safe_text(lane.get("label")),
        "lane_type": _safe_text(lane.get("lane_type")),
        "value": safe_value,
        "label": safe_value.replace("_", " ").title(),
        "count": len(records),
        "filter_record_ids": record_ids,
        "detail_drawer_ids": detail_drawer_ids,
        "safe_for_preview": True,
        "raw_evidence_reveal_allowed": False,
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
    }


def _build_facets(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    facets: Dict[str, Any] = {}

    for lane_id, lane_meta in FILTER_LANES.items():
        source_field = lane_meta.get("source_field")
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for record in records:
            value = _safe_text(record.get(source_field)) or "unknown"
            grouped.setdefault(value, []).append(record)

        options = [
            _build_facet_option(lane_id, value, grouped_records)
            for value, grouped_records in sorted(grouped.items(), key=lambda item: item[0])
        ]

        facets[lane_id] = {
            "lane_id": lane_id,
            "lane_label": lane_meta.get("label"),
            "lane_description": lane_meta.get("description"),
            "lane_type": lane_meta.get("lane_type"),
            "source_field": source_field,
            "option_count": len(options),
            "record_count": sum(option.get("count", 0) for option in options),
            "options": options,
            "safe_for_preview": True,
            "raw_evidence_reveal_allowed": False,
            "simulated_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
        }

    return facets


def _build_filter_indexes(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    indexes: Dict[str, List[Dict[str, Any]]] = {}

    for lane_id, lane_meta in FILTER_LANES.items():
        source_field = lane_meta.get("source_field")
        index_key = f"by_{lane_id}"
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for record in records:
            value = _safe_text(record.get(source_field)) or "unknown"
            grouped.setdefault(value, []).append(record)

        indexes[index_key] = grouped

    return indexes


def _build_filter_preview(facets: Dict[str, Any]) -> Dict[str, Any]:
    preview: Dict[str, Any] = {}

    for lane_id, lane_payload in facets.items():
        options = lane_payload.get("options", [])
        first = options[0] if options else None
        preview[lane_id] = first if isinstance(first, dict) else {}

    return preview


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_filter_lanes_search_facets_payload_cached() -> Dict[str, Any]:
    pack_166_payload = _load_pack_166_payload(force_refresh=False)
    lookup_records = pack_166_payload.get("lookup_records", [])

    if not isinstance(lookup_records, list):
        lookup_records = []

    filter_records = []
    for idx, record in enumerate(lookup_records, start=1):
        if isinstance(record, dict):
            filter_records.append(_build_filter_record(record, sequence=idx))

    filter_records = _sort_filter_records(filter_records)
    facets = _build_facets(filter_records)
    filter_indexes = _build_filter_indexes(filter_records)
    filter_preview = _build_filter_preview(facets)

    owner_review_category_counts = _count_by(filter_records, "owner_review_category")
    required_owner_action_counts = _count_by(filter_records, "required_owner_action")
    owner_review_priority_counts = _count_by(filter_records, "owner_review_priority")
    risk_lane_counts = _count_by(filter_records, "risk_lane")
    detail_status_counts = _count_by(filter_records, "detail_status")
    scenario_counts = _count_by(filter_records, "scenario_id")
    sensitivity_redaction_counts = _count_by(filter_records, "sensitivity_redaction")
    safety_visibility_counts = _count_by(filter_records, "safety_visibility")

    observed_lanes = set(facets.keys())
    expected_risk_lanes = {
        "critical_evidence_lane",
        "quarantine_evidence_lane",
        "fresh_recheck_evidence_lane",
        "renewal_evidence_lane",
        "monitor_evidence_lane",
    }

    facet_option_counts = {
        lane_id: int(lane_payload.get("option_count") or 0)
        for lane_id, lane_payload in facets.items()
        if isinstance(lane_payload, dict)
    }

    facet_preview_checks = {
        f"{lane_id}_preview_present": isinstance(filter_preview.get(lane_id), dict) and bool(filter_preview.get(lane_id))
        for lane_id in FILTER_LANES.keys()
    }

    readiness_checks = {
        "pack_166_ready": pack_166_payload.get("status") == "ready",
        "has_filter_records": len(filter_records) >= 1,
        "filter_count_matches_lookup_records": len(filter_records) == len(lookup_records),
        "all_simulated_only": all(record.get("simulated_only") is True for record in filter_records),
        "all_filter_preview_only": all(record.get("filter_preview_only") is True for record in filter_records),
        "all_search_facet_preview_only": all(record.get("search_facet_preview_only") is True for record in filter_records),
        "all_lookup_preview_only": all(record.get("lookup_preview_only") is True for record in filter_records),
        "all_detail_preview_only": all(record.get("detail_preview_only") is True for record in filter_records),
        "all_evidence_drawer_preview_only": all(record.get("evidence_drawer_preview_only") is True for record in filter_records),
        "all_owner_review_preview_only": all(record.get("owner_review_preview_only") is True for record in filter_records),
        "all_queue_preview_only": all(record.get("queue_preview_only") is True for record in filter_records),
        "all_renewal_preview_only": all(record.get("renewal_preview_only") is True for record in filter_records),
        "all_recheck_preview_only": all(record.get("recheck_preview_only") is True for record in filter_records),
        "all_expiration_preview_only": all(record.get("expiration_preview_only") is True for record in filter_records),
        "all_vault_preview_only": all(record.get("vault_preview_only") is True for record in filter_records),
        "all_index_preview_only": all(record.get("index_preview_only") is True for record in filter_records),
        "all_receipt_preview_only": all(record.get("receipt_preview_only") is True for record in filter_records),
        "all_approval_preview_only": all(record.get("approval_preview_only") is True for record in filter_records),
        "all_evidence_preview_only": all(record.get("evidence_preview_only") is True for record in filter_records),
        "no_real_approval_executed": all(record.get("real_approval_executed") is False for record in filter_records),
        "no_real_policy_change": all(record.get("real_policy_change_executed") is False for record in filter_records),
        "no_real_permission_change": all(record.get("real_permission_change_executed") is False for record in filter_records),
        "no_real_access_granted": all(record.get("real_access_granted") is False for record in filter_records),
        "no_real_enforcement": all(record.get("real_enforcement_executed") is False for record in filter_records),
        "no_real_audit_written": all(record.get("real_audit_written") is False for record in filter_records),
        "no_real_receipt_written": all(record.get("real_receipt_written") is False for record in filter_records),
        "no_real_archive_written": all(record.get("real_archive_written") is False for record in filter_records),
        "no_real_vault_written": all(record.get("real_vault_written") is False for record in filter_records),
        "no_real_expiration_enforced": all(record.get("real_expiration_enforced") is False for record in filter_records),
        "no_real_recheck_executed": all(record.get("real_recheck_executed") is False for record in filter_records),
        "no_real_renewal_executed": all(record.get("real_renewal_executed") is False for record in filter_records),
        "no_real_queue_action_executed": all(record.get("real_queue_action_executed") is False for record in filter_records),
        "no_real_owner_review_completed": all(record.get("real_owner_review_completed") is False for record in filter_records),
        "no_real_owner_approval_executed": all(record.get("real_owner_approval_executed") is False for record in filter_records),
        "no_real_owner_rejection_executed": all(record.get("real_owner_rejection_executed") is False for record in filter_records),
        "no_real_owner_acknowledgement_executed": all(record.get("real_owner_acknowledgement_executed") is False for record in filter_records),
        "no_real_evidence_revealed": all(record.get("real_evidence_revealed") is False for record in filter_records),
        "no_raw_secret_visible": all(record.get("raw_secret_visible") is False for record in filter_records),
        "no_raw_strategy_visible": all(record.get("raw_strategy_visible") is False for record in filter_records),
        "no_broker_token_visible": all(record.get("broker_token_visible") is False for record in filter_records),
        "no_unredacted_sensitive_value_visible": all(record.get("unredacted_sensitive_value_visible") is False for record in filter_records),
        "all_raw_evidence_lookup_blocked": all(record.get("raw_evidence_lookup_allowed") is False for record in filter_records),
        "all_raw_evidence_reveal_blocked": all(record.get("raw_evidence_reveal_allowed") is False for record in filter_records),
        "all_filter_record_ids_present": all(bool(record.get("filter_record_id")) for record in filter_records),
        "all_lookup_record_ids_present": all(bool(record.get("lookup_record_id")) for record in filter_records),
        "all_detail_drawer_ids_present": all(bool(record.get("detail_drawer_id")) for record in filter_records),
        "all_facet_results_allowed": all(record.get("facet_result_allowed") is True for record in filter_records),
        "all_filter_result_type_present": all(record.get("filter_result_type") == "evidence_drawer_filter_preview" for record in filter_records),
        "all_filter_lanes_present": EXPECTED_FILTER_LANES.issubset(observed_lanes),
        "all_facets_have_options": all(int(facet.get("option_count") or 0) >= 1 for facet in facets.values()),
        "all_facet_options_safe": all(
            option.get("safe_for_preview") is True and option.get("raw_evidence_reveal_allowed") is False
            for facet in facets.values()
            for option in facet.get("options", [])
        ),
        "risk_lane_coverage": expected_risk_lanes.issubset(set(risk_lane_counts.keys())),
        "sensitivity_redaction_present": len(sensitivity_redaction_counts) >= 1,
        "safety_visibility_present": "safe_preview_only" in safety_visibility_counts,
        "facet_preview_checks_pass": all(facet_preview_checks.values()),
        "endpoint": FILTER_LANES_ENDPOINT,
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
        "pack_number": 167,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Evidence Drawer Filter Lanes / Search Facets",
        "endpoint": FILTER_LANES_ENDPOINT,
        "source_endpoint": EVIDENCE_DRAWER_LOOKUP_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
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
        "source_pack_166": {
            "status": pack_166_payload.get("status"),
            "readiness_score": pack_166_payload.get("summary", {}).get("readiness_score"),
            "lookup_record_count": pack_166_payload.get("summary", {}).get("lookup_record_count"),
            "detail_drawer_count": pack_166_payload.get("summary", {}).get("detail_drawer_count"),
            "risk_lane_counts": pack_166_payload.get("summary", {}).get("risk_lane_counts", {}),
        },
        "summary": {
            "filter_record_count": len(filter_records),
            "lookup_record_count": len(lookup_records),
            "filter_lane_count": len(FILTER_LANES),
            "facet_count": len(facets),
            "facet_option_counts": facet_option_counts,
            "owner_review_category_counts": owner_review_category_counts,
            "required_owner_action_counts": required_owner_action_counts,
            "owner_review_priority_counts": owner_review_priority_counts,
            "risk_lane_counts": risk_lane_counts,
            "detail_status_counts": detail_status_counts,
            "scenario_counts": scenario_counts,
            "sensitivity_redaction_counts": sensitivity_redaction_counts,
            "safety_visibility_counts": safety_visibility_counts,
            "observed_filter_lanes": sorted(observed_lanes),
            "expected_filter_lanes": sorted(EXPECTED_FILTER_LANES),
            "readiness_score": readiness_score,
            "readiness_label": "Evidence drawer filter lanes/search facets ready" if readiness_score == 100 else "Evidence drawer filter lanes/search facets need review",
        },
        "readiness_checks": readiness_checks,
        "facet_preview_checks": facet_preview_checks,
        "filter_records": filter_records,
        "filter_lanes": FILTER_LANES,
        "facets": facets,
        "filter_indexes": filter_indexes,
        "filter_preview": filter_preview,
        "quick_action": {
            "id": "policy_change_approval_receipt_filter_lanes_search_facets",
            "label": "Evidence Drawer Filters",
            "href": FILTER_LANES_ENDPOINT,
            "description": "Preview filter lanes and search facets for approval receipt evidence drawers.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_filter_lanes_search_facets",
            "title": "Evidence Drawer Filters",
            "subtitle": "Preview safe filters by category, action, priority, risk lane, detail status, scenario, and redaction.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": FILTER_LANES_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_filter_lanes_search_facets_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_filter_lanes_search_facets_payload_cached())


def get_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 167,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", FILTER_LANES_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", EVIDENCE_DRAWER_LOOKUP_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Evidence drawer filter lanes/search facets ready"),
        "filter_record_count": summary.get("filter_record_count", 0),
        "lookup_record_count": summary.get("lookup_record_count", 0),
        "filter_lane_count": summary.get("filter_lane_count", 0),
        "facet_count": summary.get("facet_count", 0),
        "facet_option_counts": summary.get("facet_option_counts", {}),
        "owner_review_category_counts": summary.get("owner_review_category_counts", {}),
        "required_owner_action_counts": summary.get("required_owner_action_counts", {}),
        "owner_review_priority_counts": summary.get("owner_review_priority_counts", {}),
        "risk_lane_counts": summary.get("risk_lane_counts", {}),
        "detail_status_counts": summary.get("detail_status_counts", {}),
        "sensitivity_redaction_counts": summary.get("sensitivity_redaction_counts", {}),
        "safety_visibility_counts": summary.get("safety_visibility_counts", {}),
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
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


def get_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_filter_lanes_search_facets_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge()
    return {
        "id": "policy_change_approval_receipt_filter_lanes_search_facets",
        "label": "Evidence Drawer Filters",
        "title": "Evidence Drawer Filter Lanes / Search Facets",
        "href": FILTER_LANES_ENDPOINT,
        "endpoint": FILTER_LANES_ENDPOINT,
        "description": "Preview filter lanes and search facets for approval receipt evidence drawers.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 167",
        "category": "policy",
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
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


def build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_filter_lanes_search_facets_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "filter_readiness",
            "title": "Filter readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Evidence drawer filter lanes/search facets ready"),
        },
        {
            "id": "filter_records",
            "title": "Filter records",
            "value": summary.get("filter_record_count", 0),
            "label": "Lookup records mapped to filters",
        },
        {
            "id": "filter_lanes",
            "title": "Filter lanes",
            "value": summary.get("filter_lane_count", 0),
            "label": "Category/action/priority/risk/status/scenario/safety",
        },
        {
            "id": "facets",
            "title": "Facet groups",
            "value": summary.get("facet_count", 0),
            "label": "Searchable UI facet groups",
        },
        {
            "id": "risk_lanes",
            "title": "Risk lanes",
            "value": len(summary.get("risk_lane_counts", {})),
            "label": "Critical/quarantine/fresh/renewal/monitor",
        },
        {
            "id": "raw_reveal",
            "title": "Raw evidence reveal",
            "value": "Blocked" if checks.get("all_raw_evidence_reveal_blocked") else "Review",
            "label": "Preview filters only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_filter_lanes_search_facets",
        "title": "Evidence Drawer Filters",
        "subtitle": "Preview safe filters by category, action, priority, risk lane, detail status, scenario, and redaction.",
        "status": payload.get("status", "ready"),
        "href": FILTER_LANES_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "filter_preview_only": True,
        "search_facet_preview_only": True,
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


def build_policy_change_approval_receipt_filter_lanes_search_facets_html_section() -> str:
    section = build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-filter-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-filter-section" id="policy-change-approval-receipt-filter-lanes-search-facets">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 167</p>
            <h2>{section.get('title', 'Evidence Drawer Filters')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{FILTER_LANES_ENDPOINT}">Open evidence drawer filters JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "FILTER_LANES_ENDPOINT",
    "EVIDENCE_DRAWER_LOOKUP_ENDPOINT",
    "FILTER_LANES",
    "EXPECTED_FILTER_LANES",
    "build_policy_change_approval_receipt_filter_lanes_search_facets_payload",
    "get_policy_change_approval_receipt_filter_lanes_search_facets_payload",
    "build_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge",
    "get_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge",
    "build_policy_change_approval_receipt_filter_lanes_search_facets_quick_action",
    "build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section",
    "build_policy_change_approval_receipt_filter_lanes_search_facets_html_section",
]
