
"""
PACK 161 - Policy Change Approval Receipt Vault Preview / Index.

This module sits on top of Pack 160.

Pack 160 builds simulated approval receipt previews.
Pack 161 creates a simulated vault/index layer for those approval receipts
before anything is written for real.

Important:
- simulated-only
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


PACK_ID = "PACK_161"
APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT = "/tower/policy-change-approval-receipt-vault-index.json"
APPROVAL_RECEIPT_ENDPOINT = "/tower/policy-change-approval-receipt-preview.json"


VAULT_BUCKETS = {
    "critical_denials": {
        "label": "Critical Denials",
        "description": "Automatic-change denial receipts and critical safety stops.",
        "retention_class": "critical_security_evidence",
        "owner_review_required": True,
    },
    "quarantine_reviews": {
        "label": "Quarantine Reviews",
        "description": "Receipts requiring containment or quarantine review.",
        "retention_class": "containment_security_evidence",
        "owner_review_required": True,
    },
    "privacy_reviews": {
        "label": "Privacy Reviews",
        "description": "Receipts involving redaction, privacy review, or sensitive reveal control.",
        "retention_class": "privacy_security_evidence",
        "owner_review_required": True,
    },
    "owner_step_up": {
        "label": "Owner Step-Up",
        "description": "Receipts requiring owner approval and step-up confirmation.",
        "retention_class": "owner_challenge_evidence",
        "owner_review_required": True,
    },
    "owner_reviews": {
        "label": "Owner Reviews",
        "description": "Receipts requiring standard owner review before future change.",
        "retention_class": "owner_review_evidence",
        "owner_review_required": True,
    },
    "monitor_acknowledgements": {
        "label": "Monitor Acknowledgements",
        "description": "Monitor-only acknowledgement receipts with no real access grants.",
        "retention_class": "monitor_only_evidence",
        "owner_review_required": False,
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


def _load_pack_160_payload(force_refresh: bool = False) -> Dict[str, Any]:
    try:
        mod = importlib.import_module("tower.policy_change_approval_receipt_preview")
        fn = getattr(mod, "build_policy_change_approval_receipt_preview_payload", None)
        if callable(fn):
            payload = fn(force_refresh=force_refresh)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        return {
            "pack_id": "PACK_160",
            "status": "review",
            "endpoint": APPROVAL_RECEIPT_ENDPOINT,
            "simulated_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "load_error": str(exc),
            "summary": {
                "receipt_preview_count": 0,
                "readiness_score": 0,
                "readiness_label": "Pack 160 approval receipt preview payload unavailable",
            },
            "receipt_previews": [],
        }

    return {
        "pack_id": "PACK_160",
        "status": "review",
        "endpoint": APPROVAL_RECEIPT_ENDPOINT,
        "simulated_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "summary": {
            "receipt_preview_count": 0,
            "readiness_score": 0,
            "readiness_label": "Pack 160 approval receipt preview payload unavailable",
        },
        "receipt_previews": [],
    }



def _select_vault_bucket(receipt_preview: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the simulated vault bucket for one Pack 160 receipt preview.

    This does not write to a real vault.
    This only previews how the receipt would be indexed later.
    """

    receipt_type = str(receipt_preview.get("receipt_type") or "").lower()

    if receipt_type == "auto_change_denied":
        bucket = "critical_denials"
        index_status = "critical_denial_indexed"
        reason = "Automatic-change denial receipts belong in the critical denial evidence bucket."

    elif receipt_type == "quarantine_review_required":
        bucket = "quarantine_reviews"
        index_status = "quarantine_review_indexed"
        reason = "Quarantine review receipts belong in the containment evidence bucket."

    elif receipt_type == "privacy_review_required":
        bucket = "privacy_reviews"
        index_status = "privacy_review_indexed"
        reason = "Privacy review receipts belong in the privacy evidence bucket."

    elif receipt_type == "owner_step_up_required":
        bucket = "owner_step_up"
        index_status = "owner_step_up_indexed"
        reason = "Owner step-up receipts belong in the owner challenge evidence bucket."

    elif receipt_type == "owner_review_required":
        bucket = "owner_reviews"
        index_status = "owner_review_indexed"
        reason = "Owner review receipts belong in the owner review evidence bucket."

    elif receipt_type == "monitor_only_ack":
        bucket = "monitor_acknowledgements"
        index_status = "monitor_ack_indexed"
        reason = "Monitor-only acknowledgements belong in the monitor-only evidence bucket."

    else:
        bucket = "owner_reviews"
        index_status = "owner_review_indexed"
        reason = "Unknown receipt type defaults to owner review evidence bucket."

    meta = dict(VAULT_BUCKETS.get(bucket) or VAULT_BUCKETS["owner_reviews"])

    return {
        "vault_bucket": bucket,
        "vault_bucket_label": meta["label"],
        "vault_bucket_description": meta["description"],
        "retention_class": meta["retention_class"],
        "bucket_owner_review_required": bool(meta["owner_review_required"]),
        "index_status": index_status,
        "index_reason": reason,
    }


def _build_search_tokens(receipt_preview: Dict[str, Any], bucket: Dict[str, Any]) -> List[str]:
    tokens = [
        receipt_preview.get("receipt_type"),
        receipt_preview.get("receipt_severity"),
        receipt_preview.get("approval_path"),
        receipt_preview.get("risk_band"),
        receipt_preview.get("decision"),
        receipt_preview.get("scenario_id"),
        receipt_preview.get("matched_policy_id"),
        bucket.get("vault_bucket"),
        bucket.get("retention_class"),
    ]

    safe_tokens = []
    for token in tokens:
        token = _safe_text(token).strip()
        if token and token not in safe_tokens:
            safe_tokens.append(token)

    return safe_tokens


def _build_vault_evidence_summary(receipt_preview: Dict[str, Any], bucket: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "approval_receipt_preview_id": _safe_text(receipt_preview.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(receipt_preview.get("approval_gate_id")),
        "risk_score_id": _safe_text(receipt_preview.get("risk_score_id")),
        "recommendation_id": _safe_text(receipt_preview.get("recommendation_id")),
        "scenario_id": _safe_text(receipt_preview.get("scenario_id")),
        "matched_policy_id": _safe_text(receipt_preview.get("matched_policy_id")),
        "receipt_type": _safe_text(receipt_preview.get("receipt_type")),
        "receipt_severity": _safe_text(receipt_preview.get("receipt_severity")),
        "approval_path": _safe_text(receipt_preview.get("approval_path")),
        "risk_score": int(receipt_preview.get("risk_score") or 0),
        "risk_band": _safe_text(receipt_preview.get("risk_band")),
        "vault_bucket": bucket.get("vault_bucket"),
        "retention_class": bucket.get("retention_class"),
    }


def _vault_soulaana_translation(receipt_preview: Dict[str, Any], bucket: Dict[str, Any]) -> str:
    scenario_id = _safe_text(receipt_preview.get("scenario_id"))
    bucket_label = _safe_text(bucket.get("vault_bucket_label"))
    return f"{scenario_id}: This approval receipt is only indexed as a preview in {bucket_label}. Nothing is written to the real vault yet."


def build_policy_change_approval_receipt_vault_index_item(receipt_preview: Dict[str, Any], sequence: int = 1) -> Dict[str, Any]:
    """
    Convert one Pack 160 approval receipt preview into one simulated vault/index item.
    """

    receipt_preview = dict(receipt_preview or {})
    bucket = _select_vault_bucket(receipt_preview)

    identity = {
        "pack": PACK_ID,
        "sequence": sequence,
        "approval_receipt_preview_id": receipt_preview.get("approval_receipt_preview_id"),
        "scenario_id": receipt_preview.get("scenario_id"),
        "receipt_type": receipt_preview.get("receipt_type"),
        "vault_bucket": bucket.get("vault_bucket"),
    }

    vault_preview_id = f"approval_receipt_vault_preview_{_stable_hash(identity, 18)}"
    ledger_index_id = f"approval_receipt_ledger_index_{_stable_hash({'ledger': identity}, 18)}"

    return {
        "vault_preview_id": vault_preview_id,
        "ledger_index_id": ledger_index_id,
        "sequence": sequence,
        "approval_receipt_preview_id": _safe_text(receipt_preview.get("approval_receipt_preview_id")),
        "approval_gate_id": _safe_text(receipt_preview.get("approval_gate_id")),
        "risk_score_id": _safe_text(receipt_preview.get("risk_score_id")),
        "recommendation_id": _safe_text(receipt_preview.get("recommendation_id")),
        "recheck_item_id": _safe_text(receipt_preview.get("recheck_item_id")),
        "expiration_check_id": _safe_text(receipt_preview.get("expiration_check_id")),
        "source_vault_entry_id": _safe_text(receipt_preview.get("vault_entry_id")),
        "source_ledger_entry_id": _safe_text(receipt_preview.get("ledger_entry_id")),
        "source_receipt_preview_id": _safe_text(receipt_preview.get("source_receipt_preview_id")),
        "scenario_id": _safe_text(receipt_preview.get("scenario_id")),
        "matched_policy_id": _safe_text(receipt_preview.get("matched_policy_id")),
        "decision": _safe_text(receipt_preview.get("decision")),
        "risk_score": int(receipt_preview.get("risk_score") or 0),
        "risk_band": _safe_text(receipt_preview.get("risk_band")),
        "approval_path": _safe_text(receipt_preview.get("approval_path")),
        "receipt_type": _safe_text(receipt_preview.get("receipt_type")),
        "receipt_label": _safe_text(receipt_preview.get("receipt_label")),
        "receipt_severity": _safe_text(receipt_preview.get("receipt_severity")),
        "vault_bucket": bucket["vault_bucket"],
        "vault_bucket_label": bucket["vault_bucket_label"],
        "vault_bucket_description": bucket["vault_bucket_description"],
        "retention_class": bucket["retention_class"],
        "index_status": bucket["index_status"],
        "index_reason": bucket["index_reason"],
        "bucket_owner_review_required": bucket["bucket_owner_review_required"],
        "search_tokens": _build_search_tokens(receipt_preview, bucket),
        "evidence_summary": _build_vault_evidence_summary(receipt_preview, bucket),
        "soulaana_vault_translation": _vault_soulaana_translation(receipt_preview, bucket),
        "source_endpoint": APPROVAL_RECEIPT_ENDPOINT,
        "simulated_only": True,
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


def _sort_vault_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bucket_rank = {
        "critical_denials": 1,
        "quarantine_reviews": 2,
        "privacy_reviews": 3,
        "owner_step_up": 4,
        "owner_reviews": 5,
        "monitor_acknowledgements": 6,
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
            bucket_rank.get(str(item.get("vault_bucket")), 99),
            severity_rank.get(str(item.get("receipt_severity")), 99),
            -int(item.get("risk_score") or 0),
            int(item.get("sequence") or 999),
        ),
    )


@lru_cache(maxsize=1)
def build_policy_change_approval_receipt_vault_index_payload_cached() -> Dict[str, Any]:
    pack_160_payload = _load_pack_160_payload(force_refresh=False)
    receipt_previews = pack_160_payload.get("receipt_previews", [])

    if not isinstance(receipt_previews, list):
        receipt_previews = []

    vault_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(receipt_previews, start=1):
        if isinstance(item, dict):
            vault_items.append(build_policy_change_approval_receipt_vault_index_item(item, sequence=idx))

    vault_items = _sort_vault_items(vault_items)

    bucket_counts = _count_by(vault_items, "vault_bucket")
    receipt_type_counts = _count_by(vault_items, "receipt_type")
    receipt_severity_counts = _count_by(vault_items, "receipt_severity")
    approval_path_counts = _count_by(vault_items, "approval_path")
    index_status_counts = _count_by(vault_items, "index_status")
    retention_class_counts = _count_by(vault_items, "retention_class")
    decision_counts = _count_by(vault_items, "decision")

    by_bucket = _group_by(vault_items, "vault_bucket")
    by_receipt_type = _group_by(vault_items, "receipt_type")
    by_receipt_severity = _group_by(vault_items, "receipt_severity")
    by_approval_path = _group_by(vault_items, "approval_path")
    by_index_status = _group_by(vault_items, "index_status")
    by_retention_class = _group_by(vault_items, "retention_class")
    by_decision = _group_by(vault_items, "decision")

    critical_denials = [
        item for item in vault_items
        if item.get("vault_bucket") == "critical_denials"
    ]
    quarantine_reviews = [
        item for item in vault_items
        if item.get("vault_bucket") == "quarantine_reviews"
    ]
    privacy_reviews = [
        item for item in vault_items
        if item.get("vault_bucket") == "privacy_reviews"
    ]
    owner_step_up = [
        item for item in vault_items
        if item.get("vault_bucket") == "owner_step_up"
    ]
    owner_reviews = [
        item for item in vault_items
        if item.get("vault_bucket") == "owner_reviews"
    ]
    monitor_acknowledgements = [
        item for item in vault_items
        if item.get("vault_bucket") == "monitor_acknowledgements"
    ]

    required_buckets = set(VAULT_BUCKETS.keys())
    observed_buckets = set(bucket_counts.keys())

    readiness_checks = {
        "pack_160_ready": pack_160_payload.get("status") == "ready",
        "has_vault_items": len(vault_items) >= 1,
        "vault_count_matches_receipt_previews": len(vault_items) == len(receipt_previews),
        "all_simulated_only": all(item.get("simulated_only") is True for item in vault_items),
        "all_vault_preview_only": all(item.get("vault_preview_only") is True for item in vault_items),
        "all_index_preview_only": all(item.get("index_preview_only") is True for item in vault_items),
        "all_receipt_preview_only": all(item.get("receipt_preview_only") is True for item in vault_items),
        "all_approval_preview_only": all(item.get("approval_preview_only") is True for item in vault_items),
        "all_evidence_preview_only": all(item.get("evidence_preview_only") is True for item in vault_items),
        "no_real_approval_executed": all(item.get("real_approval_executed") is False for item in vault_items),
        "no_real_policy_change": all(item.get("real_policy_change_executed") is False for item in vault_items),
        "no_real_permission_change": all(item.get("real_permission_change_executed") is False for item in vault_items),
        "no_real_access_granted": all(item.get("real_access_granted") is False for item in vault_items),
        "no_real_enforcement": all(item.get("real_enforcement_executed") is False for item in vault_items),
        "no_real_audit_written": all(item.get("real_audit_written") is False for item in vault_items),
        "no_real_receipt_written": all(item.get("real_receipt_written") is False for item in vault_items),
        "no_real_archive_written": all(item.get("real_archive_written") is False for item in vault_items),
        "no_real_vault_written": all(item.get("real_vault_written") is False for item in vault_items),
        "all_vault_ids_present": all(bool(item.get("vault_preview_id")) for item in vault_items),
        "all_ledger_index_ids_present": all(bool(item.get("ledger_index_id")) for item in vault_items),
        "all_buckets_present": all(bool(item.get("vault_bucket")) for item in vault_items),
        "all_index_status_present": all(bool(item.get("index_status")) for item in vault_items),
        "all_search_tokens_present": all(isinstance(item.get("search_tokens"), list) and item.get("search_tokens") for item in vault_items),
        "all_evidence_summaries_present": all(isinstance(item.get("evidence_summary"), dict) for item in vault_items),
        "critical_denials_present": len(critical_denials) >= 1,
        "quarantine_reviews_present": len(quarantine_reviews) >= 1,
        "privacy_reviews_present": len(privacy_reviews) >= 1,
        "owner_step_up_present": len(owner_step_up) >= 1,
        "owner_reviews_present": len(owner_reviews) >= 1,
        "monitor_acknowledgements_present": len(monitor_acknowledgements) >= 1,
        "required_bucket_coverage": required_buckets.issubset(observed_buckets),
        "endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
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
        "pack_number": 161,
        "status": "ready" if readiness_score == 100 else "review",
        "title": "Policy Change Approval Receipt Vault Preview / Index",
        "endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "source_endpoint": APPROVAL_RECEIPT_ENDPOINT,
        "generated_at": _utc_now(),
        "simulated_only": True,
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
        "cached_non_recursive": True,
        "source_pack_160": {
            "status": pack_160_payload.get("status"),
            "readiness_score": pack_160_payload.get("summary", {}).get("readiness_score"),
            "receipt_preview_count": pack_160_payload.get("summary", {}).get("receipt_preview_count"),
            "receipt_type_counts": pack_160_payload.get("summary", {}).get("receipt_type_counts", {}),
        },
        "summary": {
            "vault_item_count": len(vault_items),
            "ledger_index_count": len(vault_items),
            "critical_denial_count": len(critical_denials),
            "quarantine_review_count": len(quarantine_reviews),
            "privacy_review_count": len(privacy_reviews),
            "owner_step_up_count": len(owner_step_up),
            "owner_review_count": len(owner_reviews),
            "monitor_acknowledgement_count": len(monitor_acknowledgements),
            "bucket_counts": bucket_counts,
            "receipt_type_counts": receipt_type_counts,
            "receipt_severity_counts": receipt_severity_counts,
            "approval_path_counts": approval_path_counts,
            "index_status_counts": index_status_counts,
            "retention_class_counts": retention_class_counts,
            "decision_counts": decision_counts,
            "observed_buckets": sorted(observed_buckets),
            "required_buckets": sorted(required_buckets),
            "readiness_score": readiness_score,
            "readiness_label": "Policy change approval receipt vault/index preview ready" if readiness_score == 100 else "Policy change approval receipt vault/index preview needs review",
        },
        "readiness_checks": readiness_checks,
        "vault_items": vault_items,
        "ledger_index": vault_items,
        "indexes": {
            "by_bucket": by_bucket,
            "by_receipt_type": by_receipt_type,
            "by_receipt_severity": by_receipt_severity,
            "by_approval_path": by_approval_path,
            "by_index_status": by_index_status,
            "by_retention_class": by_retention_class,
            "by_decision": by_decision,
        },
        "critical_denials": critical_denials,
        "quarantine_reviews": quarantine_reviews,
        "privacy_reviews": privacy_reviews,
        "owner_step_up": owner_step_up,
        "owner_reviews": owner_reviews,
        "monitor_acknowledgements": monitor_acknowledgements,
        "quick_action": {
            "id": "policy_change_approval_receipt_vault_index",
            "label": "Approval Receipt Vault Index",
            "href": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
            "description": "Preview vault/index placement for policy approval receipt previews.",
            "status": "ready" if readiness_score == 100 else "review",
        },
        "unified_owner_section": {
            "section_id": "policy_change_approval_receipt_vault_index",
            "title": "Approval Receipt Vault Index",
            "subtitle": "Previews where approval receipt evidence would be indexed before any real vault write.",
            "status": "ready" if readiness_score == 100 else "review",
            "card_count": 6,
            "href": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        },
    }


def build_policy_change_approval_receipt_vault_index_payload(force_refresh: bool = False) -> Dict[str, Any]:
    if force_refresh:
        build_policy_change_approval_receipt_vault_index_payload_cached.cache_clear()
    return copy.deepcopy(build_policy_change_approval_receipt_vault_index_payload_cached())


def get_policy_change_approval_receipt_vault_index_payload(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_vault_index_payload(force_refresh=force_refresh)


def build_policy_change_approval_receipt_vault_index_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_vault_index_payload(force_refresh=force_refresh)
    summary = payload.get("summary", {})

    return {
        "pack_id": PACK_ID,
        "pack_number": 161,
        "status": payload.get("status", "ready"),
        "endpoint": payload.get("endpoint", APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT),
        "source_endpoint": payload.get("source_endpoint", APPROVAL_RECEIPT_ENDPOINT),
        "readiness_score": summary.get("readiness_score", 100),
        "readiness_label": summary.get("readiness_label", "Policy change approval receipt vault/index preview ready"),
        "vault_item_count": summary.get("vault_item_count", 0),
        "ledger_index_count": summary.get("ledger_index_count", 0),
        "critical_denial_count": summary.get("critical_denial_count", 0),
        "quarantine_review_count": summary.get("quarantine_review_count", 0),
        "privacy_review_count": summary.get("privacy_review_count", 0),
        "owner_step_up_count": summary.get("owner_step_up_count", 0),
        "owner_review_count": summary.get("owner_review_count", 0),
        "monitor_acknowledgement_count": summary.get("monitor_acknowledgement_count", 0),
        "bucket_counts": summary.get("bucket_counts", {}),
        "receipt_type_counts": summary.get("receipt_type_counts", {}),
        "index_status_counts": summary.get("index_status_counts", {}),
        "simulated_only": True,
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
        "cached_non_recursive": True,
    }


def get_policy_change_approval_receipt_vault_index_status_bridge(force_refresh: bool = False) -> Dict[str, Any]:
    return build_policy_change_approval_receipt_vault_index_status_bridge(force_refresh=force_refresh)



def build_policy_change_approval_receipt_vault_index_quick_action() -> Dict[str, Any]:
    bridge = build_policy_change_approval_receipt_vault_index_status_bridge()
    return {
        "id": "policy_change_approval_receipt_vault_index",
        "label": "Approval Receipt Vault Index",
        "title": "Approval Receipt Vault Index",
        "href": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "endpoint": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "description": "Preview vault/index placement for policy approval receipt evidence.",
        "status": bridge.get("status", "ready"),
        "pack": "Pack 161",
        "category": "policy",
        "simulated_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
    }


def build_policy_change_approval_receipt_vault_index_unified_owner_section() -> Dict[str, Any]:
    payload = build_policy_change_approval_receipt_vault_index_payload()
    summary = payload.get("summary", {})
    checks = payload.get("readiness_checks", {})

    cards = [
        {
            "id": "vault_index_readiness",
            "title": "Vault index readiness",
            "value": summary.get("readiness_score", 100),
            "label": summary.get("readiness_label", "Policy change approval receipt vault/index preview ready"),
        },
        {
            "id": "vault_items",
            "title": "Vault items",
            "value": summary.get("vault_item_count", 0),
            "label": "Receipt previews mapped to vault buckets",
        },
        {
            "id": "ledger_index",
            "title": "Ledger index",
            "value": summary.get("ledger_index_count", 0),
            "label": "Simulated ledger index rows",
        },
        {
            "id": "critical_privacy",
            "title": "Critical / privacy",
            "value": f"{summary.get('critical_denial_count', 0)} / {summary.get('privacy_review_count', 0)}",
            "label": "High-sensitivity buckets",
        },
        {
            "id": "owner_review_buckets",
            "title": "Owner review buckets",
            "value": summary.get("owner_review_count", 0),
            "label": "Owner-review evidence previews",
        },
        {
            "id": "no_real_vault_writes",
            "title": "Real vault writes",
            "value": "No" if checks.get("no_real_vault_written") else "Review",
            "label": "Preview only",
        },
    ]

    return {
        "section_id": "policy_change_approval_receipt_vault_index",
        "title": "Approval Receipt Vault Index",
        "subtitle": "Previews where approval receipt evidence would be indexed before any real vault, archive, audit, or receipt write.",
        "status": payload.get("status", "ready"),
        "href": APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT,
        "cards": cards,
        "simulated_only": True,
        "vault_preview_only": True,
        "index_preview_only": True,
        "receipt_preview_only": True,
        "approval_preview_only": True,
        "evidence_preview_only": True,
        "cached_non_recursive": True,
    }


def build_policy_change_approval_receipt_vault_index_html_section() -> str:
    section = build_policy_change_approval_receipt_vault_index_unified_owner_section()
    cards = section.get("cards", [])

    card_html = []
    for card in cards:
        card_html.append(
            f"""
            <article class="tower-card policy-change-approval-receipt-vault-card">
                <div class="tower-card-kicker">{card.get('title', '')}</div>
                <div class="tower-card-value">{card.get('value', '')}</div>
                <p>{card.get('label', '')}</p>
            </article>
            """
        )

    return f"""
    <section class="tower-section policy-change-approval-receipt-vault-section" id="policy-change-approval-receipt-vault-index">
        <div class="tower-section-heading">
            <p class="tower-kicker">Pack 161</p>
            <h2>{section.get('title', 'Approval Receipt Vault Index')}</h2>
            <p>{section.get('subtitle', '')}</p>
            <a class="tower-link-pill" href="{APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT}">Open approval receipt vault index JSON</a>
        </div>
        <div class="tower-card-grid">
            {''.join(card_html)}
        </div>
    </section>
    """


__all__ = [
    "PACK_ID",
    "APPROVAL_RECEIPT_VAULT_INDEX_ENDPOINT",
    "APPROVAL_RECEIPT_ENDPOINT",
    "VAULT_BUCKETS",
    "build_policy_change_approval_receipt_vault_index_item",
    "build_policy_change_approval_receipt_vault_index_payload",
    "get_policy_change_approval_receipt_vault_index_payload",
    "build_policy_change_approval_receipt_vault_index_status_bridge",
    "get_policy_change_approval_receipt_vault_index_status_bridge",
    "build_policy_change_approval_receipt_vault_index_quick_action",
    "build_policy_change_approval_receipt_vault_index_unified_owner_section",
    "build_policy_change_approval_receipt_vault_index_html_section",
]
