"""Archive Vault service payloads for routes, tests, Tower, and Clouds."""

from __future__ import annotations

from typing import Any, Dict

from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_readiness import get_readiness_score
from .vault_registry import get_registry_snapshot
from .vault_security import (
    NO_DIRECT_UPLOAD_POLICY,
    REDACTION_POLICY,
    attach_tower_guard,
)


def _base_payload(route: str, payload_type: str) -> Dict[str, Any]:
    return {
        "app_id": "archive_vault",
        "app_name": "Archive Vault",
        "version": VAULT_VERSION,
        "route": route,
        "payload_type": payload_type,
        "generated_at": utc_now_iso(),
        "public_access": False,
        "private_invite_only": True,
    }


def get_vault_status() -> Dict[str, Any]:
    registry = get_registry_snapshot()
    readiness = get_readiness_score()
    payload = {
        **_base_payload("/vault/status.json", "vault_status"),
        "status": "ready",
        "readiness_score": readiness["score"],
        "readiness_label": readiness["label"],
        "document_type_count": len(registry["document_types"]),
        "packet_template_count": len(registry["packet_templates"]),
        "sample_document_record_count": len(registry["sample_document_records"]),
        "receipt_count": len(registry["sample_receipts"]),
        "direct_upload_allowed": False,
        "redacted_view_default": True,
        "clouds_source_ready": True,
        "owner_focus_queue": [
            "Keep Vault private and Tower-controlled.",
            "Use Vault packets for ATM route acquisition and apartment lender diligence.",
            "Feed Vault summary status into The Clouds after Clouds foundation is built.",
        ],
    }
    return attach_tower_guard(payload, "/vault/status.json")


def get_document_registry_payload() -> Dict[str, Any]:
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/document-registry.json", "document_registry"),
        "document_types": registry["document_types"],
        "document_records": registry["sample_document_records"],
        "global_search_scope": registry["global_search_scope"],
        "universal_id_standard_enabled": True,
        "data_freshness_standard_enabled": True,
    }
    return attach_tower_guard(payload, "/vault/document-registry.json")


def get_packet_templates_payload() -> Dict[str, Any]:
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/packet-templates.json", "packet_templates"),
        "packet_templates": registry["packet_templates"],
        "template_count": len(registry["packet_templates"]),
        "aggressive_build_scope": [
            "ATM route acquisition",
            "Apartment lender due diligence",
            "Trust and entity records",
            "OB Manual Live proof",
            "Soulaana artist package",
            "Private beta onboarding",
        ],
    }
    return attach_tower_guard(payload, "/vault/packet-templates.json")


def get_owner_console_payload() -> Dict[str, Any]:
    status = get_vault_status()
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/owner-console.json", "owner_console"),
        "summary_cards": [
            {"label": "Readiness", "value": status["readiness_score"], "unit": "%"},
            {"label": "Packet templates", "value": len(registry["packet_templates"]), "unit": "templates"},
            {"label": "Document records", "value": len(registry["sample_document_records"]), "unit": "records"},
            {"label": "Direct upload", "value": "locked", "unit": "security"},
        ],
        "focus_lanes": [
            {"lane": "observatory", "label": "OB Manual Live proof", "status": "ready_for_receipts"},
            {"lane": "atm", "label": "ATM acquisition packets", "status": "ready_for_targets"},
            {"lane": "property", "label": "Apartment lender diligence", "status": "ready_for_targets"},
            {"lane": "trust", "label": "Trust/entity preservation", "status": "ready_for_indexing"},
            {"lane": "beta", "label": "Private beta onboarding", "status": "ready_for_invites"},
        ],
        "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        "next_pack_recommendation": "Vault Giant Pack 002 should build the real Vault room UI, packet board, document drawer, and owner action queue.",
    }
    return attach_tower_guard(payload, "/vault/owner-console.json")


def get_readiness_payload() -> Dict[str, Any]:
    payload = {
        **_base_payload("/vault/readiness.json", "readiness"),
        **get_readiness_score(),
    }
    return attach_tower_guard(payload, "/vault/readiness.json")


def get_no_direct_upload_payload() -> Dict[str, Any]:
    payload = {
        **_base_payload("/vault/no-direct-upload.json", "no_direct_upload_policy"),
        **NO_DIRECT_UPLOAD_POLICY,
    }
    return attach_tower_guard(payload, "/vault/no-direct-upload.json")


def get_redacted_view_policy_payload() -> Dict[str, Any]:
    payload = {
        **_base_payload("/vault/redacted-view-policy.json", "redacted_view_policy"),
        **REDACTION_POLICY,
    }
    return attach_tower_guard(payload, "/vault/redacted-view-policy.json")


def get_open_app_handoff_payload() -> Dict[str, Any]:
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/open-app-handoff.json", "open_app_handoff"),
        "handoffs": registry["open_app_handoffs"],
        "handoff_pattern": "Vault never replaces app authority; it opens the owning app or Tower for action.",
    }
    return attach_tower_guard(payload, "/vault/open-app-handoff.json")


def get_receipt_chain_payload() -> Dict[str, Any]:
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/receipt-chain.json", "receipt_chain"),
        "receipts": registry["sample_receipts"],
        "receipt_count": len(registry["sample_receipts"]),
        "revocation_freeze_undo_standard_enabled": True,
        "approval_chain_standard_enabled": True,
    }
    return attach_tower_guard(payload, "/vault/receipt-chain.json")


def get_clouds_source_payload() -> Dict[str, Any]:
    readiness = get_readiness_score()
    registry = get_registry_snapshot()
    payload = {
        **_base_payload("/vault/clouds-source.json", "clouds_source"),
        "source_app": "archive_vault",
        "safe_for_clouds": True,
        "clouds_view": "summary_only_redacted",
        "readiness_score": readiness["score"],
        "readiness_label": readiness["label"],
        "packet_template_count": len(registry["packet_templates"]),
        "active_packet_lanes": sorted({template["business_lane"] for template in registry["packet_templates"]}),
        "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        "owner_focus": [
            "ATM packet ready for first route targets.",
            "Apartment packet ready for 4-5 building lender diligence.",
            "OB Manual Live proof packet ready for private proof receipts.",
            "Trust/entity packet ready for ownership preservation.",
        ],
        "clouds_should_not_display": REDACTION_POLICY["sensitive_fields"],
    }
    return attach_tower_guard(payload, "/vault/clouds-source.json")
