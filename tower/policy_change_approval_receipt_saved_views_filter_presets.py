
"""
PACK 168 - Evidence Drawer Saved Views / Filter Presets.

This module sits on top of Pack 167.

Pack 167 creates safe filter lanes/search facets for evidence drawer records.
Pack 168 creates saved view/filter preset previews:
- critical owner review
- quarantine review
- fresh recheck
- renewal review
- monitor only
- high sensitivity/redacted
- safe preview only
- all evidence drawers

Important:
- simulated-only
- saved-view-preview-only
- filter-preset-preview-only
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
- no saved view persisted
- no user preference written
- no raw evidence lookup
- no raw evidence reveal
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


PACK_ID = "PACK_168"
SAVED_VIEWS_ENDPOINT = "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
FILTER_LANES_ENDPOINT = "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"


SAVED_VIEW_BLUEPRINTS = {
    "all_evidence_drawers": {
        "label": "All Evidence Drawers",
        "description": "All preview-safe evidence drawer filter records.",
        "filters": {},
        "view_priority": "standard",
        "requires_owner_review": False,
    },
    "critical_owner_review": {
        "label": "Critical Owner Review",
        "description": "Critical owner recheck drawer records.",
        "filters": {"owner_review_category": ["critical_owner_recheck"]},
        "view_priority": "critical",
        "requires_owner_review": True,
    },
    "quarantine_review": {
        "label": "Quarantine Review",
        "description": "Quarantine owner recheck drawer records.",
        "filters": {"owner_review_category": ["quarantine_owner_recheck"]},
        "view_priority": "high",
        "requires_owner_review": True,
    },
    "fresh_recheck": {
        "label": "Fresh Recheck",
        "description": "Fresh recheck evidence drawer records.",
        "filters": {"owner_review_category": ["fresh_recheck_review"]},
        "view_priority": "high",
        "requires_owner_review": True,
    },
    "renewal_review": {
        "label": "Renewal Review",
        "description": "Renewal review evidence drawer records.",
        "filters": {"owner_review_category": ["renewal_review"]},
        "view_priority": "medium",
        "requires_owner_review": True,
    },
    "monitor_only": {
        "label": "Monitor Only",
        "description": "Monitor acknowledgement evidence drawer records.",
        "filters": {"owner_review_category": ["monitor_acknowledgement"]},
        "view_priority": "monitor",
        "requires_owner_review": False,
    },
    "high_sensitivity_redacted": {
        "label": "High Sensitivity / Redacted",
        "description": "Evidence drawer records with redacted high-sensitivity sections.",
        "filters": {"sensitivity_redaction": ["redacted_high_sensitivity"]},
        "view_priority": "high",
        "requires_owner_review": True,
    },
    "safe_preview_only": {
        "label": "Safe Preview Only",
        "description": "Evidence drawer records where only preview-safe details are visible.",
        "filters": {"safety_visibility": ["safe_preview_only"]},
        "view_priority": "standard",
        "requires_owner_review": False,
    },
}


EXPECTED_SAVED_VIEWS = set(SAVED_VIEW_BLUEPRINTS.keys())


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


def _load_pack_167_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
        fn = getattr(mod, "build_policy_change_approval_receipt_filter_lanes_search_facets_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_167",
            "status": "review",
            "endpoint": FILTER_LANES_ENDPOINT,
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
            "load_error": str(exc),
            "summary": {
                "filter_record_count": 0,
                "lookup_record_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 167 filter lanes/search facets payload unavailable",
            },
            "filter_records": [],
            "facets": {},
        }

    return {
        "pack_id": "PACK_167",
        "status": "review",
        "endpoint": FILTER_LANES_ENDPOINT,
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
        "summary": {
            "filter_record_count": 0,
            "lookup_record_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 167 filter lanes/search facets payload unavailable",
        },
        "filter_records": [],
        "facets": {},
    }


def _record_matches_filters(record: Dict[str, Any], filters: Dict[str, List[str]]) -> bool:
    if not filters:
        return True

    for field, allowed_values in filters.items():
        if not isinstance(allowed_values, list):
            allowed_values = [allowed_values]
        safe_allowed = {_safe_text(value) for value in allowed_values}
        if _safe_text(record.get(field)) not in safe_allowed:
            return False

    return True


def _apply_saved_view(records: List[Dict[str, Any]], filters: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    return [
        record
        for record in records
        if isinstance(record, dict) and _record_matches_filters(record, filters)
    ]


def _build_saved_view_record(view_id: str, blueprint: Dict[str, Any], records: List[Dict[str, Any]], sequence: int) -> Dict[str, Any]:
    filters = dict(blueprint.get("filters") or {})
    matched_records = _apply_saved_view(records, filters)

    filter_record_ids = [
        _safe_text(record.get("filter_record_id"))
        for record in matched_records
        if record.get("filter_record_id")
    ]

    detail_drawer_ids = [
        _safe_text(record.get("detail_drawer_id"))
        for record in matched_records
        if record.get("detail_drawer_id")
    ]

    identity = {
        "pack": PACK_ID,
        "view_id": view_id,
        "filters": filters,
        "filter_record_ids": filter_record_ids,
    }

    saved_view_preview_id = f"evidence_drawer_saved_view_{_stable_hash(identity, 18)}"

    risk_lane_counts: Dict[str, int] = {}
    category_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    sensitivity_counts: Dict[str, int] = {}

    for record in matched_records:
        risk_lane = _safe_text(record.get("risk_lane")) or "unknown"
        category = _safe_text(record.get("owner_review_category")) or "unknown"
        priority = _safe_text(record.get("owner_review_priority")) or "unknown"
        sensitivity = _safe_text(record.get("sensitivity_redaction")) or "unknown"

        risk_lane_counts[risk_lane] = risk_lane_counts.get(risk_lane, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        sensitivity_counts[sensitivity] = sensitivity_counts.get(sensitivity, 0) + 1

    return {
        "saved_view_preview_id": saved_view_preview_id,
        "saved_view_id": view_id,
        "sequence": sequence,
        "label": _safe_text(blueprint.get("label")),
        "description": _safe_text(blueprint.get("description")),
        "view_priority": _safe_text(blueprint.get("view_priority")),
        "requires_owner_review": bool(blueprint.get("requires_owner_review", False)),
        "filters": filters,
        "matched_record_count": len(matched_records),
        "filter_record_ids": filter_record_ids,
        "detail_drawer_ids": detail_drawer_ids,
        "risk_lane_counts": risk_lane_counts,
        "owner_review_category_counts": category_counts,
        "owner_review_priority_counts": priority_counts,
        "sensitivity_redaction_counts": sensitivity_counts,
        "empty_view": len(matched_records) == 0,
        "view_status": "saved_view_preview_ready",
        "view_result_type": "evidence_drawer_saved_view_preview",
        "save_action_allowed_now": False,
        "set_default_allowed_now": False,
        "share_view_allowed_now": False,
        "raw_evidence_reveal_allowed": False,
        "raw_evidence_lookup_allowed": False,
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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
        "real_saved_view_written": False,
        "real_user_preference_written": False,
    }


def _sort_saved_views(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_rank = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "standard": 4,
        "monitor": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            priority_rank.get(str(item.get("view_priority")), 99),
            int(item.get("sequence") or 999),
        ),
    )


def _count_by(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = _safe_text(item.get(key)) or "unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _build_preset_indexes(saved_views: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexes = {
        "by_saved_view_id": {},
        "by_view_priority": {},
        "by_requires_owner_review": {},
        "by_view_status": {},
    }

    for view in saved_views:
        view_id = _safe_text(view.get("saved_view_id"))
        if view_id:
            indexes["by_saved_view_id"][view_id] = view

        priority = _safe_text(view.get("view_priority")) or "unknown"
        indexes["by_view_priority"].setdefault(priority, []).append(view)

        review_key = "owner_review_required" if view.get("requires_owner_review") else "owner_review_not_required"
        indexes["by_requires_owner_review"].setdefault(review_key, []).append(view)

        status = _safe_text(view.get("view_status")) or "unknown"
        indexes["by_view_status"].setdefault(status, []).append(view)

    return indexes


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_saved_views_filter_presets_payload_cached() -> Dict[str, Any]:
    pack_167_payload = _load_pack_167_payload(force_refresh=False)
    filter_records = pack_167_payload.get("filter_records", [])

    if not isinstance(filter_records, list):
        filter_records = []

    saved_views = []
    for idx, (view_id, blueprint) in enumerate(SAVED_VIEW_BLUEPRINTS.items(), start=1):
        saved_views.append(_build_saved_view_record(view_id, blueprint, filter_records, sequence=idx))

    saved_views = _sort_saved_views(saved_views)
    indexes = _build_preset_indexes(saved_views)

    view_priority_counts = _count_by(saved_views, "view_priority")
    view_status_counts = _count_by(saved_views, "view_status")
    owner_review_requirement_counts = {
        "owner_review_required": len([view for view in saved_views if view.get("requires_owner_review") is True]),
        "owner_review_not_required": len([view for view in saved_views if view.get("requires_owner_review") is False]),
    }

    empty_view_count = len([view for view in saved_views if view.get("empty_view") is True])
    non_empty_view_count = len([view for view in saved_views if view.get("empty_view") is False])

    saved_view_preview = {
        view.get("saved_view_id"): view
        for view in saved_views
        if view.get("saved_view_id")
    }

    readiness_checks = {
        "pack_167_ready": pack_167_payload.get("status") == "ready",
        "has_saved_views": len(saved_views) >= 1,
        "all_expected_saved_views_present": EXPECTED_SAVED_VIEWS.issubset({view.get("saved_view_id") for view in saved_views}),
        "saved_view_count_matches_blueprints": len(saved_views) == len(SAVED_VIEW_BLUEPRINTS),
        "all_simulated_only": all(view.get("simulated_only") is True for view in saved_views),
        "all_saved_view_preview_only": all(view.get("saved_view_preview_only") is True for view in saved_views),
        "all_filter_preset_preview_only": all(view.get("filter_preset_preview_only") is True for view in saved_views),
        "all_filter_preview_only": all(view.get("filter_preview_only") is True for view in saved_views),
        "all_search_facet_preview_only": all(view.get("search_facet_preview_only") is True for view in saved_views),
        "all_lookup_preview_only": all(view.get("lookup_preview_only") is True for view in saved_views),
        "all_detail_preview_only": all(view.get("detail_preview_only") is True for view in saved_views),
        "all_evidence_drawer_preview_only": all(view.get("evidence_drawer_preview_only") is True for view in saved_views),
        "all_owner_review_preview_only": all(view.get("owner_review_preview_only") is True for view in saved_views),
        "all_queue_preview_only": all(view.get("queue_preview_only") is True for view in saved_views),
        "all_renewal_preview_only": all(view.get("renewal_preview_only") is True for view in saved_views),
        "all_recheck_preview_only": all(view.get("recheck_preview_only") is True for view in saved_views),
        "all_expiration_preview_only": all(view.get("expiration_preview_only") is True for view in saved_views),
        "all_vault_preview_only": all(view.get("vault_preview_only") is True for view in saved_views),
        "all_index_preview_only": all(view.get("index_preview_only") is True for view in saved_views),
        "all_receipt_preview_only": all(view.get("receipt_preview_only") is True for view in saved_views),
        "all_approval_preview_only": all(view.get("approval_preview_only") is True for view in saved_views),
        "all_evidence_preview_only": all(view.get("evidence_preview_only") is True for view in saved_views),
        "no_real_approval_executed": all(view.get("real_approval_executed") is False for view in saved_views),
        "no_real_policy_change": all(view.get("real_policy_change_executed") is False for view in saved_views),
        "no_real_permission_change": all(view.get("real_permission_change_executed") is False for view in saved_views),
        "no_real_access_granted": all(view.get("real_access_granted") is False for view in saved_views),
        "no_real_enforcement": all(view.get("real_enforcement_executed") is False for view in saved_views),
        "no_real_audit_written": all(view.get("real_audit_written") is False for view in saved_views),
        "no_real_receipt_written": all(view.get("real_receipt_written") is False for view in saved_views),
        "no_real_archive_written": all(view.get("real_archive_written") is False for view in saved_views),
        "no_real_vault_written": all(view.get("real_vault_written") is False for view in saved_views),
        "no_real_expiration_enforced": all(view.get("real_expiration_enforced") is False for view in saved_views),
        "no_real_recheck_executed": all(view.get("real_recheck_executed") is False for view in saved_views),
        "no_real_renewal_executed": all(view.get("real_renewal_executed") is False for view in saved_views),
        "no_real_queue_action_executed": all(view.get("real_queue_action_executed") is False for view in saved_views),
        "no_real_owner_review_completed": all(view.get("real_owner_review_completed") is False for view in saved_views),
        "no_real_owner_approval_executed": all(view.get("real_owner_approval_executed") is False for view in saved_views),
        "no_real_owner_rejection_executed": all(view.get("real_owner_rejection_executed") is False for view in saved_views),
        "no_real_owner_acknowledgement_executed": all(view.get("real_owner_acknowledgement_executed") is False for view in saved_views),
        "no_real_evidence_revealed": all(view.get("real_evidence_revealed") is False for view in saved_views),
        "no_real_saved_view_written": all(view.get("real_saved_view_written") is False for view in saved_views),
        "no_real_user_preference_written": all(view.get("real_user_preference_written") is False for view in saved_views),
        "all_save_actions_blocked": all(view.get("save_action_allowed_now") is False for view in saved_views),
        "all_set_default_actions_blocked": all(view.get("set_default_allowed_now") is False for view in saved_views),
        "all_share_actions_blocked": all(view.get("share_view_allowed_now") is False for view in saved_views),
        "all_raw_evidence_reveal_blocked": all(view.get("raw_evidence_reveal_allowed") is False for view in saved_views),
        "all_raw_evidence_lookup_blocked": all(view.get("raw_evidence_lookup_allowed") is False for view in saved_views),
        "all_saved_view_ids_present": all(bool(view.get("saved_view_id")) for view in saved_views),
        "all_saved_view_preview_ids_present": all(bool(view.get("saved_view_preview_id")) for view in saved_views),
        "all_view_result_type_present": all(view.get("view_result_type") == "evidence_drawer_saved_view_preview" for view in saved_views),
        "all_views_have_status": all(view.get("view_status") == "saved_view_preview_ready" for view in saved_views),
        "non_empty_views_present": non_empty_view_count >= 1,
        "all_evidence_drawers_view_present": "all_evidence_drawers" in saved_view_preview,
        "critical_owner_review_view_present": "critical_owner_review" in saved_view_preview,
        "quarantine_review_view_present": "quarantine_review" in saved_view_preview,
        "fresh_recheck_view_present": "fresh_recheck" in saved_view_preview,
        "renewal_review_view_present": "renewal_review" in saved_view_preview,
        "monitor_only_view_present": "monitor_only" in saved_view_preview,
        "high_sensitivity_view_present": "high_sensitivity_redacted" in saved_view_preview,
        "safe_preview_view_present": "safe_preview_only" in saved_view_preview,
        "endpoint": SAVED_VIEWS_ENDPOINT,
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
        "pack_number": 168,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Evidence Drawer Saved Views / Filter Presets",
        "endpoint": SAVED_VIEWS_ENDPOINT,
        "source_endpoint": FILTER_LANES_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
        "source_pack_167": {
            "status": pack_167_payload.get("status"),
            "readiness_score": pack_167_payload.get("summary", {}).get("readiness_score"),
            "filter_record_count": pack_167_payload.get("summary", {}).get("filter_record_count"),
            "filter_lane_count": pack_167_payload.get("summary", {}).get("filter_lane_count"),
            "facet_count": pack_167_payload.get("summary", {}).get("facet_count"),
        },
        "summary": {
            "saved_view_count": len(saved_views),
            "filter_record_count": len(filter_records),
            "non_empty_view_count": non_empty_view_count,
            "empty_view_count": empty_view_count,
            "view_priority_counts": view_priority_counts,
            "view_status_counts": view_status_counts,
            "owner_review_requirement_counts": owner_review_requirement_counts,
            "expected_saved_views": sorted(EXPECTED_SAVED_VIEWS),
            "observed_saved_views": sorted([view.get("saved_view_id") for view in saved_views]),
            "readiness_score": readiness_score,
            "readiness_label": "Evidence drawer saved views/filter presets ready" if readiness_score == 100 else "Evidence drawer saved views/filter presets need review",
        },
        "readiness_checks": readiness_checks,
        "saved_view_blueprints": SAVED_VIEW_BLUEPRINTS,
        "saved_views": saved_views,
        "saved_view_preview": saved_view_preview,
        "preset_indexes": indexes,
        "quick_action": {
            "id": "policy_change_approval_receipt_saved_views_filter_presets",
            "label": "Evidence Drawer Saved Views",
            "href": SAVED_VIEWS_ENDPOINT,
            "description": "Preview saved views and filter presets for approval receipt evidence drawers.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_saved_views_filter_presets",
            "title": "Evidence Drawer Saved Views",
            "subtitle": "Preview saved views for critical, quarantine, fresh recheck, renewal, monitor, redacted, and safe-only filters.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": SAVED_VIEWS_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_saved_views_filter_presets_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_saved_views_filter_presets_payload_cached())


def get_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_saved_views_filter_presets_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 168,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", SAVED_VIEWS_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", FILTER_LANES_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Evidence drawer saved views/filter presets ready"),
        "saved_view_count": summary.get("saved_view_count", 0),
        "filter_record_count": summary.get("filter_record_count", 0),
        "non_empty_view_count": summary.get("non_empty_view_count", 0),
        "empty_view_count": summary.get("empty_view_count", 0),
        "view_priority_counts": summary.get("view_priority_counts", {}),
        "view_status_counts": summary.get("view_status_counts", {}),
        "owner_review_requirement_counts": summary.get("owner_review_requirement_counts", {}),
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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
        "real_saved_view_written": False,
        "real_user_preference_written": False,
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_saved_views_filter_presets_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_saved_views_filter_presets_status_bridge(force_refresh=force_refresh)


def build_policy_change_approval_receipt_saved_views_filter_presets_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_saved_views_filter_presets_status_bridge()
    return {
        "id": "policy_change_approval_receipt_saved_views_filter_presets",
        "label": "Evidence Drawer Saved Views",
        "title": "Evidence Drawer Saved Views / Filter Presets",
        "href": SAVED_VIEWS_ENDPOINT,
        "endpoint": SAVED_VIEWS_ENDPOINT,
        "description": "Preview saved views and filter presets for approval receipt evidence drawers.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 168",
        "category": "policy",
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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


def build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_saved_views_filter_presets_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    review_counts = summary.get("owner_review_requirement_counts", {})

    cards = [
        {
            "id": "saved_view_readiness",
            "title": "Saved view readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Evidence drawer saved views/filter presets ready"),
        },
        {
            "id": "saved_views",
            "title": "Saved views",
            "value": summary.get("saved_view_count", 0),
            "label": "Preset views previewed",
        },
        {
            "id": "non_empty_views",
            "title": "Non-empty views",
            "value": summary.get("non_empty_view_count", 0),
            "label": "Views with matching records",
        },
        {
            "id": "owner_review_views",
            "title": "Owner-review views",
            "value": review_counts.get("owner_review_required", 0),
            "label": "Views requiring owner attention",
        },
        {
            "id": "standard_views",
            "title": "No-review views",
            "value": review_counts.get("owner_review_not_required", 0),
            "label": "Monitor/safe preview views",
        },
        {
            "id": "real_saved_view_write",
            "title": "Real saved view write",
            "value": "No" if checks.get("no_real_saved_view_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_saved_views_filter_presets",
        "title": "Evidence Drawer Saved Views",
        "subtitle": "Preview saved views for critical, quarantine, fresh recheck, renewal, monitor, redacted, and safe-only filters.",
        "status": payload.get("status", "ready"),
        "href": SAVED_VIEWS_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "saved_view_preview_only": True,
        "filter_preset_preview_only": True,
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


def build_policy_change_approval_receipt_saved_views_filter_presets_html_section() -> str:
    section = build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-saved-view-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-saved-view-section" id="policy-change-approval-receipt-saved-views-filter-presets">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 168</p>
            <h2>{section.get('title', 'Evidence Drawer Saved Views')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{SAVED_VIEWS_ENDPOINT}">Open evidence drawer saved views JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "SAVED_VIEWS_ENDPOINT",
    "FILTER_LANES_ENDPOINT",
    "SAVED_VIEW_BLUEPRINTS",
    "EXPECTED_SAVED_VIEWS",
    "build_policy_change_approval_receipt_saved_views_filter_presets_payload",
    "get_policy_change_approval_receipt_saved_views_filter_presets_payload",
    "build_policy_change_approval_receipt_saved_views_filter_presets_status_bridge",
    "get_policy_change_approval_receipt_saved_views_filter_presets_status_bridge",
    "build_policy_change_approval_receipt_saved_views_filter_presets_quick_action",
    "build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section",
    "build_policy_change_approval_receipt_saved_views_filter_presets_html_section",
]
