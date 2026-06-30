"""Security contract for Archive Vault.

Actual identity, permissions, clearance, and mode-gate authority remain owned by
The Tower. Vault never becomes its own permission authority.
"""

from __future__ import annotations

from typing import Any, Dict


TOWER_GUARD_CONTRACT: Dict[str, Any] = {
    "tower_required": True,
    "vault_owns_permissions": False,
    "identity_source": "tower",
    "clearance_source": "tower",
    "step_up_source": "tower",
    "audit_receipt_source": "tower_or_vault_linked_receipts",
    "direct_upload_allowed": False,
    "public_routes_allowed": False,
    "redaction_default": "redacted_until_owner_or_tower_clearance",
    "blocked_reason_standard": [
        "missing_tower_clearance",
        "missing_owner_approval",
        "expired_clearance",
        "role_mismatch",
        "lane_mismatch",
        "upload_provider_not_approved",
        "direct_upload_locked",
        "redaction_required",
    ],
}


REDACTION_POLICY: Dict[str, Any] = {
    "policy_id": "vault.default_redacted_view",
    "enabled": True,
    "default_view": "redacted",
    "sensitive_fields": [
        "beneficiary_details",
        "bank_account_details",
        "broker_details",
        "loan_terms_private",
        "seller_private_contact",
        "trustee_private_contact",
        "direct_deposit_details",
        "full_legal_document_body",
    ],
    "allowed_clearance_roles": ["owner", "tower", "trustee", "legal", "financial", "compliance"],
    "clouds_default": "summary_only",
}


NO_DIRECT_UPLOAD_POLICY: Dict[str, Any] = {
    "policy_id": "vault.no_direct_upload_until_storage_clearance",
    "enabled": True,
    "direct_upload_allowed": False,
    "reason": "Vault can create indexes, packet records, redaction contracts, and receipt chains before a storage provider is approved. Direct file upload stays locked until Tower approves storage, retention, malware scanning, and permission boundaries.",
    "allowed_now": [
        "create_document_index_record",
        "create_packet_template_record",
        "link_receipt_id",
        "set_redacted_summary",
        "handoff_to_tower_for_clearance",
    ],
    "blocked_now": [
        "raw_direct_file_upload",
        "public_file_share",
        "anonymous_file_access",
        "broker_secret_storage",
        "unredacted_clouds_display",
    ],
}


def attach_tower_guard(payload: Dict[str, Any], route: str) -> Dict[str, Any]:
    guarded = dict(payload)
    guarded["tower_guard"] = {
        "route": route,
        **TOWER_GUARD_CONTRACT,
    }
    return guarded
