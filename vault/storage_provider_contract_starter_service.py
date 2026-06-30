"""
VAULT GIANT PACK 041 — Storage Provider Contract Starter

NEW SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack starts the next Vault product-depth section after GP040.

Purpose:
- Define future storage-provider contract requirements.
- Define provider option records without selecting/configuring a provider.
- Define metadata-only object key and checksum/hash placeholders.
- Define retention, redaction, export, and Tower authority gates.
- Verify raw storage, direct upload, export, external delivery, portals, approval,
  and execution remain locked.
- Carry forward to GP042.

Important truth:
- GP041 does not store raw files.
- GP041 does not unlock direct upload.
- GP041 does not select or configure a storage provider.
- GP041 does not create external delivery.
- GP041 does not export raw/unredacted data.
- GP041 does not create public proof.
- GP041 does not open seller/broker/trustee/external portals.
- GP041 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP041 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.controlled_packet_assembly_readiness_checkpoint_service import (
    get_controlled_packet_assembly_readiness_checkpoint_payload,
)


PACK_ID = "VAULT_GP041"
PACK_NAME = "Storage Provider Contract Starter"
SCHEMA_VERSION = "vault.storage_provider_contract_starter.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
PREVIOUS_SECTION_RANGE = "GP031-GP040"

PROVIDER_OPTIONS = [
    {
        "provider_id": "VAULT_PROVIDER_LOCAL_ENCRYPTED_PLACEHOLDER",
        "provider_label": "Local Encrypted Storage Placeholder",
        "provider_type": "local_encrypted_placeholder",
        "future_use": "private_owner_development_only",
    },
    {
        "provider_id": "VAULT_PROVIDER_OBJECT_STORAGE_PLACEHOLDER",
        "provider_label": "Object Storage Placeholder",
        "provider_type": "object_storage_placeholder",
        "future_use": "future_cloud_storage_contract",
    },
    {
        "provider_id": "VAULT_PROVIDER_DRIVE_ARCHIVE_PLACEHOLDER",
        "provider_label": "Drive Archive Placeholder",
        "provider_type": "drive_archive_placeholder",
        "future_use": "future_managed_archive_contract",
    },
    {
        "provider_id": "VAULT_PROVIDER_TOWER_MANAGED_PLACEHOLDER",
        "provider_label": "Tower Managed Storage Placeholder",
        "provider_type": "tower_managed_storage_placeholder",
        "future_use": "future_tower_authorized_storage_contract",
    },
]

OBJECT_KEY_SCOPES = [
    "document_intake",
    "attachment_registry",
    "requirement_match",
    "evidence_binder",
    "packet_workspace",
    "controlled_packet_assembly",
    "receipt_chain",
]

BOUNDARY_LOCKS = [
    "raw_file_body_storage",
    "direct_upload",
    "provider_selected",
    "provider_configured",
    "provider_write_enabled",
    "checksum_verified",
    "file_body_persisted",
    "external_packet_delivery",
    "external_access",
    "packet_export",
    "unredacted_export",
    "raw_export",
    "public_proof",
    "public_packet_proof",
    "portal_access",
    "auto_completion",
    "auto_confirmation",
    "approval",
    "execution_engine",
    "auto_action_execution",
    "financing_decision",
    "legal_advice",
    "raw_document_verification_claim",
    "receipt_close",
    "receipt_finalization",
    "vault_done",
    "clouds_continue",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_provider_contract_payload() -> Dict[str, Any]:
    gp040 = get_controlled_packet_assembly_readiness_checkpoint_payload()

    provider_options = _build_provider_options()
    object_key_contract = _build_object_key_contract(provider_options)
    retention_redaction_gates = _build_retention_redaction_gates()
    tower_gates = _build_tower_gates(provider_options)
    boundary_check = _build_boundary_check(gp040)
    next_step = _build_next_step(provider_options, object_key_contract, boundary_check)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": [
                "VAULT_GP011",
                "VAULT_GP012",
                "VAULT_GP013",
                "VAULT_GP014",
                "VAULT_GP015",
                "VAULT_GP016",
                "VAULT_GP017",
                "VAULT_GP018",
                "VAULT_GP019",
                "VAULT_GP020",
                "VAULT_GP021",
                "VAULT_GP022",
                "VAULT_GP023",
                "VAULT_GP024",
                "VAULT_GP025",
                "VAULT_GP026",
                "VAULT_GP027",
                "VAULT_GP028",
                "VAULT_GP029",
                "VAULT_GP030",
                "VAULT_GP031",
                "VAULT_GP032",
                "VAULT_GP033",
                "VAULT_GP034",
                "VAULT_GP035",
                "VAULT_GP036",
                "VAULT_GP037",
                "VAULT_GP038",
                "VAULT_GP039",
                "VAULT_GP040",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_provider_contract_starter",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "new_section_start": True,
        },
        "section_context": {
            "current_section_id": SECTION_ID,
            "current_section_title": SECTION_TITLE,
            "current_section_range": SECTION_RANGE,
            "previous_section_id": PREVIOUS_SECTION_ID,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "started_after_gp040": True,
            "gp040_checkpoint_required": True,
            "gp040_checkpoint_connected": True,
            "clouds_parked": True,
            "vault_done": False,
        },
        "contract_truth": {
            "storage_provider_contract_started": True,
            "storage_provider_contract_ready": True,
            "provider_options_visible": True,
            "object_key_contract_visible": True,
            "checksum_placeholder_contract_visible": True,
            "retention_redaction_gates_visible": True,
            "tower_storage_gates_visible": True,
            "boundary_check_visible": True,
            "metadata_only": True,
            "private_contract_only": True,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "raw_file_body_storage_enabled": False,
            "file_body_persisted_count": 0,
            "direct_upload_unlocked": False,
            "direct_upload_enabled": False,
            "checksum_verified_count": 0,
            "hash_verified_count": 0,
            "external_packet_delivery_enabled": False,
            "external_access_enabled": False,
            "packet_export_enabled": False,
            "unredacted_export_enabled": False,
            "raw_export_enabled": False,
            "public_packet_proof_enabled": False,
            "public_proof_enabled": False,
            "portal_access_enabled": False,
            "approval_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "receipt_close_enabled": False,
            "receipt_finalization_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
            "safe_to_continue_to_gp042": True,
        },
        "tower_authority": {
            "tower_owns_identity": True,
            "tower_owns_permissions": True,
            "tower_owns_clearance": True,
            "tower_owns_step_up": True,
            "tower_owns_export_locks": True,
            "tower_owns_freeze_revoke": True,
            "tower_owns_external_access": True,
            "tower_owns_portal_unlocks": True,
            "tower_owns_sensitive_visibility": True,
            "tower_owns_action_authority_gates": True,
            "tower_owns_storage_provider_authorization": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "external_packet_delivery_allowed": False,
            "packet_export_allowed": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "contract_routes": {
            "room_title": "Vault Storage Provider Contract Starter",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-provider-contract",
            "json_route": "/vault/storage-provider-contract.json",
            "provider_options_route": "/vault/storage-provider-options.json",
            "object_key_contract_route": "/vault/storage-object-key-contract.json",
            "retention_redaction_gates_route": "/vault/storage-retention-redaction-gates.json",
            "tower_gates_route": "/vault/storage-provider-tower-gates.json",
            "boundary_check_route": "/vault/storage-provider-boundary-check.json",
            "next_step_route": "/vault/storage-provider-next-step.json",
            "gp041_status_route": "/vault/gp041-status.json",
        },
        "contract_counts": {
            "provider_option_count": provider_options["provider_option_count"],
            "provider_selected_count": provider_options["provider_selected_count"],
            "provider_configured_count": provider_options["provider_configured_count"],
            "object_key_scope_count": object_key_contract["object_key_scope_count"],
            "object_key_placeholder_count": object_key_contract["object_key_placeholder_count"],
            "checksum_placeholder_count": object_key_contract["checksum_placeholder_count"],
            "retention_gate_count": retention_redaction_gates["retention_gate_count"],
            "redaction_gate_count": retention_redaction_gates["redaction_gate_count"],
            "tower_gate_count": tower_gates["tower_gate_count"],
            "boundary_lock_count": boundary_check["boundary_lock_count"],
            "boundary_violation_count": boundary_check["boundary_violation_count"],
            "file_body_persisted_count": 0,
            "checksum_verified_count": 0,
            "raw_file_body_storage_enabled_count": 0,
            "direct_upload_unlocked_count": 0,
            "external_delivery_allowed_count": 0,
            "packet_export_allowed_count": 0,
            "execution_allowed_count": 0,
            "metadata_only": True,
        },
        "provider_options": provider_options,
        "object_key_contract": object_key_contract,
        "retention_redaction_gates": retention_redaction_gates,
        "tower_gates": tower_gates,
        "boundary_check": boundary_check,
        "next_step": next_step,
        "gp040_connection": {
            "gp040_pack_id": gp040["pack"]["id"],
            "gp040_ready": gp040["gp040_status"]["ready"],
            "gp040_safe_to_continue": gp040["gp040_status"]["safe_to_continue_to_gp041"],
            "gp040_vault_done": gp040["gp040_status"]["vault_done"],
            "gp040_section": gp040["pack"]["section"],
            "gp040_section_checkpoint_complete": gp040["gp040_status"]["controlled_packet_assembly_section_checkpoint_complete"],
            "gp040_new_section_starts_after_this_pack": gp040["gp040_status"]["new_section_starts_after_this_pack"],
        },
        "gp041_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "new_section_started": True,
            "started_after_gp040": True,
            "storage_provider_contract_starter_ready": True,
            "safe_to_continue_to_gp042": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_contract": True,
            "private_contract_only": True,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "raw_file_body_storage_still_locked": True,
            "direct_upload_still_locked": True,
            "checksum_verification_not_claimed": True,
            "hash_verification_not_claimed": True,
            "external_delivery_still_locked": True,
            "external_access_still_locked": True,
            "packet_export_still_locked": True,
            "unredacted_export_still_locked": True,
            "raw_export_still_locked": True,
            "public_proof_still_locked": True,
            "public_packet_proof_disabled": True,
            "portal_access_still_locked": True,
            "approval_disabled": True,
            "execution_engine_disabled": True,
            "auto_action_execution_disabled": True,
            "financing_decision_not_claimed": True,
            "legal_advice_not_claimed": True,
            "raw_verification_not_claimed": True,
            "receipt_close_disabled": True,
            "receipt_finalization_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp041",
            "next_pack": "VAULT_GP042_STORAGE_OBJECT_INVENTORY_PREVIEW",
        },
    }

    return payload


def _build_provider_options() -> Dict[str, Any]:
    items = []

    for index, provider in enumerate(PROVIDER_OPTIONS, start=1):
        items.append(
            {
                "provider_option_id": f"VSP-{index:03d}",
                "provider_id": provider["provider_id"],
                "provider_label": provider["provider_label"],
                "provider_type": provider["provider_type"],
                "future_use": provider["future_use"],
                "contract_status": "PLACEHOLDER_NOT_SELECTED_NOT_CONFIGURED",
                "metadata_only": True,
                "provider_selected": False,
                "provider_configured": False,
                "provider_write_enabled": False,
                "provider_read_enabled": False,
                "provider_delete_enabled": False,
                "raw_file_body_storage_enabled": False,
                "direct_upload_enabled": False,
                "external_delivery_enabled": False,
                "packet_export_enabled": False,
                "public_proof_enabled": False,
                "portal_access_enabled": False,
                "tower_authorization_required": True,
                "tower_authorized": False,
                "tower_step_up_required": True,
                "owner_confirmation_required": True,
                "owner_confirmed": False,
                "safe_to_select_now": False,
                "safe_to_configure_now": False,
                "safe_to_write_now": False,
                "safe_to_continue_to_gp042": True,
            }
        )

    return {
        "provider_option_items": items,
        "provider_option_count": len(items),
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_write_enabled_count": 0,
        "provider_read_enabled_count": 0,
        "raw_file_body_storage_enabled_count": 0,
        "direct_upload_enabled_count": 0,
        "external_delivery_enabled_count": 0,
        "packet_export_enabled_count": 0,
        "public_proof_enabled_count": 0,
        "portal_access_enabled_count": 0,
        "tower_authorization_required_count": len(items),
        "tower_authorized_count": 0,
        "owner_confirmed_count": 0,
        "safe_to_select_now_count": 0,
        "safe_to_configure_now_count": 0,
        "safe_to_write_now_count": 0,
        "safe_to_continue_provider_options": True,
    }


def _build_object_key_contract(provider_options: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for index, scope in enumerate(OBJECT_KEY_SCOPES, start=1):
        items.append(
            {
                "object_key_contract_id": f"VSOK-{index:03d}",
                "scope": scope,
                "object_key_pattern": f"vault/{{account_id}}/{{packet_id}}/{{document_id}}/{scope}/{{version_id}}",
                "checksum_placeholder_id": f"VSCHK-{index:03d}",
                "hash_algorithm_placeholder": "sha256_placeholder_not_verified",
                "metadata_only": True,
                "object_key_placeholder_only": True,
                "object_key_bound_to_provider": False,
                "provider_selected": False,
                "provider_configured": False,
                "file_body_persisted": False,
                "raw_body_available": False,
                "checksum_present": False,
                "checksum_verified": False,
                "hash_verified": False,
                "direct_upload_enabled": False,
                "external_delivery_enabled": False,
                "packet_export_enabled": False,
                "tower_authorization_required": True,
                "safe_to_continue_to_gp042": True,
            }
        )

    return {
        "object_key_contract_items": items,
        "object_key_scope_count": len(OBJECT_KEY_SCOPES),
        "object_key_placeholder_count": len(items),
        "checksum_placeholder_count": len(items),
        "object_key_bound_to_provider_count": 0,
        "provider_selected_count": provider_options["provider_selected_count"],
        "provider_configured_count": provider_options["provider_configured_count"],
        "file_body_persisted_count": 0,
        "raw_body_available_count": 0,
        "checksum_present_count": 0,
        "checksum_verified_count": 0,
        "hash_verified_count": 0,
        "direct_upload_enabled_count": 0,
        "external_delivery_enabled_count": 0,
        "packet_export_enabled_count": 0,
        "safe_to_continue_object_key_contract": True,
    }


def _build_retention_redaction_gates() -> Dict[str, Any]:
    retention_items = [
        {
            "retention_gate_id": "VSRG-001",
            "gate_name": "Retention policy placeholder",
            "status": "PLACEHOLDER_ONLY_NOT_ACTIVE_POLICY",
            "metadata_only": True,
            "policy_active": False,
            "owner_review_required": True,
            "tower_authorization_required": True,
        },
        {
            "retention_gate_id": "VSRG-002",
            "gate_name": "Legal hold placeholder",
            "status": "PLACEHOLDER_ONLY_NOT_LEGAL_ADVICE",
            "metadata_only": True,
            "policy_active": False,
            "owner_review_required": True,
            "tower_authorization_required": True,
        },
        {
            "retention_gate_id": "VSRG-003",
            "gate_name": "Deletion freeze placeholder",
            "status": "PLACEHOLDER_ONLY_NO_DELETE_ENABLED",
            "metadata_only": True,
            "policy_active": False,
            "owner_review_required": True,
            "tower_authorization_required": True,
        },
    ]

    redaction_items = [
        {
            "redaction_gate_id": "VSRD-001",
            "gate_name": "Owner redacted preview allowed",
            "status": "REDACTED_PREVIEW_ALLOWED_METADATA_ONLY",
            "metadata_only": True,
            "redacted_preview_allowed": True,
            "raw_view_allowed": False,
            "unredacted_export_allowed": False,
            "tower_authorization_required": True,
        },
        {
            "redaction_gate_id": "VSRD-002",
            "gate_name": "Sensitive field visibility locked",
            "status": "SENSITIVE_VISIBILITY_TOWER_LOCKED",
            "metadata_only": True,
            "redacted_preview_allowed": True,
            "raw_view_allowed": False,
            "unredacted_export_allowed": False,
            "tower_authorization_required": True,
        },
        {
            "redaction_gate_id": "VSRD-003",
            "gate_name": "Export redaction lock",
            "status": "EXPORT_LOCKED_NO_PACKET_EXPORT",
            "metadata_only": True,
            "redacted_preview_allowed": True,
            "raw_view_allowed": False,
            "unredacted_export_allowed": False,
            "tower_authorization_required": True,
        },
    ]

    return {
        "retention_gate_items": retention_items,
        "redaction_gate_items": redaction_items,
        "retention_gate_count": len(retention_items),
        "redaction_gate_count": len(redaction_items),
        "active_retention_policy_count": 0,
        "raw_view_allowed_count": 0,
        "unredacted_export_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "redacted_preview_allowed_count": sum(1 for item in redaction_items if item["redacted_preview_allowed"]),
        "tower_authorization_required_count": len(retention_items) + len(redaction_items),
        "safe_to_continue_retention_redaction_gates": True,
    }


def _build_tower_gates(provider_options: Dict[str, Any]) -> Dict[str, Any]:
    gates = [
        "identity_required",
        "permission_required",
        "clearance_required",
        "step_up_required",
        "storage_provider_authorization_required",
        "export_lock_required",
        "external_access_lock_required",
        "sensitive_visibility_lock_required",
        "freeze_revoke_required",
        "audit_receipt_required",
    ]

    items = [
        {
            "tower_gate_id": f"VSTG-{index:03d}",
            "gate_name": gate,
            "gate_status": "TOWER_REQUIRED_NOT_GRANTED",
            "metadata_only": True,
            "required": True,
            "granted": False,
            "vault_can_override": False,
            "provider_selected": False,
            "provider_configured": False,
            "write_enabled": False,
            "external_delivery_enabled": False,
            "export_enabled": False,
        }
        for index, gate in enumerate(gates, start=1)
    ]

    return {
        "tower_gate_items": items,
        "tower_gate_count": len(items),
        "required_gate_count": len(items),
        "granted_gate_count": 0,
        "vault_override_allowed_count": 0,
        "provider_selected_count": provider_options["provider_selected_count"],
        "provider_configured_count": provider_options["provider_configured_count"],
        "write_enabled_count": 0,
        "external_delivery_enabled_count": 0,
        "export_enabled_count": 0,
        "tower_authority_preserved": True,
        "safe_to_continue_tower_gates": True,
    }


def _build_boundary_check(gp040: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "boundary_check_id": f"VSPBC-{index:03d}",
            "boundary_name": boundary_name,
            "expected_state": "locked_or_false",
            "actual_state": "locked_or_false",
            "locked": True,
            "violation": False,
            "metadata_only": True,
            "tower_owned_when_applicable": True,
            "vault_override_allowed": False,
            "checkpoint_note": f"{boundary_name} remains locked in GP041 storage-provider contract starter.",
        }
        for index, boundary_name in enumerate(BOUNDARY_LOCKS, start=1)
    ]

    return {
        "boundary_check_items": items,
        "boundary_lock_count": len(items),
        "boundary_violation_count": 0,
        "all_boundaries_locked": True,
        "all_restricted_paths_locked": True,
        "gp040_boundary_violation_count": gp040["checkpoint_counts"]["boundary_violation_count"],
        "gp040_safe_to_continue": gp040["gp040_status"]["safe_to_continue_to_gp041"],
        "raw_file_body_storage_locked": True,
        "direct_upload_locked": True,
        "provider_selected_locked": True,
        "provider_configured_locked": True,
        "provider_write_enabled_locked": True,
        "checksum_verified_not_claimed": True,
        "file_body_persisted_count": 0,
        "external_packet_delivery_locked": True,
        "external_access_locked": True,
        "packet_export_locked": True,
        "unredacted_export_locked": True,
        "raw_export_locked": True,
        "public_proof_locked": True,
        "public_packet_proof_locked": True,
        "portal_access_locked": True,
        "approval_locked": True,
        "execution_engine_locked": True,
        "auto_action_execution_locked": True,
        "receipt_close_locked": True,
        "receipt_finalization_locked": True,
        "vault_done_false": True,
        "clouds_parked": True,
        "safe_to_continue_boundary_check": True,
    }


def _build_next_step(
    provider_options: Dict[str, Any],
    object_key_contract: Dict[str, Any],
    boundary_check: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSPNX-001",
            "title": "Deepen provider option comparison",
            "target_pack": "VAULT_GP042",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPNX-002",
            "title": "Keep object key contract metadata-only",
            "target_pack": "VAULT_GP042",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPNX-003",
            "title": "Do not unlock raw storage or direct upload",
            "target_pack": "VAULT_GP042",
            "status": "LOCKED_BOUNDARY_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp042_count": len(items),
        "provider_option_count": provider_options["provider_option_count"],
        "object_key_placeholder_count": object_key_contract["object_key_placeholder_count"],
        "boundary_violation_count": boundary_check["boundary_violation_count"],
        "safe_to_continue_to_gp042": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP042",
        "recommended_next_pack_title": "Storage Object Inventory Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep Tower authority intact.",
            "Keep Vault private.",
            "Keep provider options as placeholders only.",
            "Keep raw file body storage locked.",
            "Keep direct upload locked.",
            "Keep checksum/hash verification unclaimed.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_provider_contract_payload())


def get_storage_provider_contract_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "section_context": payload["section_context"],
        "contract_truth": payload["contract_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "contract_routes": payload["contract_routes"],
        "contract_counts": payload["contract_counts"],
        "gp040_connection": payload["gp040_connection"],
    }


def get_storage_provider_options() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "provider_options": payload["provider_options"],
    }


def get_storage_object_key_contract() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "object_key_contract": payload["object_key_contract"],
    }


def get_storage_retention_redaction_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "retention_redaction_gates": payload["retention_redaction_gates"],
    }


def get_storage_provider_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gates": payload["tower_gates"],
    }


def get_storage_provider_boundary_check() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "boundary_check": payload["boundary_check"],
    }


def get_storage_provider_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp041_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp041_status": payload["gp041_status"],
        "section_context": payload["section_context"],
        "contract_truth": payload["contract_truth"],
        "contract_routes": payload["contract_routes"],
        "contract_counts": payload["contract_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp040_connection": payload["gp040_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_provider_contract_page() -> str:
    payload = clone_payload()
    routes = payload["contract_routes"]
    counts = payload["contract_counts"]
    truth = payload["contract_truth"]
    providers = payload["provider_options"]
    object_keys = payload["object_key_contract"]
    boundary = payload["boundary_check"]
    next_step = payload["next_step"]

    provider_html = "\n".join(_render_provider_card(item) for item in providers["provider_option_items"])
    object_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['object_key_pattern'])}</span>
          </div>
          <div class="pill warn">Placeholder</div>
        </div>
        """
        for item in object_keys["object_key_contract_items"]
    )

    boundary_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['boundary_name'])}</strong>
            <span>{escape(item['actual_state'])} · violation: {str(item['violation']).lower()}</span>
          </div>
          <div class="pill ok">Locked</div>
        </div>
        """
        for item in boundary["boundary_check_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Provider Contract Starter · GP041</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.84);
      --panel2: rgba(21, 32, 74, 0.76);
      --line: rgba(160, 179, 255, 0.24);
      --text: #eef3ff;
      --muted: #9da9d7;
      --gold: #f5d17e;
      --violet: #ad8dff;
      --cyan: #83eaff;
      --danger: #ff8c9c;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.50);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 13% 9%, rgba(173, 141, 255, 0.18), transparent 34%),
        radial-gradient(circle at 88% 5%, rgba(131, 234, 255, 0.13), transparent 30%),
        radial-gradient(circle at 70% 90%, rgba(245, 209, 126, 0.09), transparent 32%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 52%, #03040b);
    }}

    .shell {{
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}

    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(145deg, rgba(15, 23, 52, 0.94), rgba(6, 10, 25, 0.74));
      box-shadow: 0 28px 74px var(--shadow);
      overflow: hidden;
      position: relative;
    }}

    .hero:before {{
      content: "";
      position: absolute;
      inset: -2px;
      background:
        radial-gradient(circle at 16% 0%, rgba(245, 209, 126, 0.18), transparent 28%),
        radial-gradient(circle at 94% 34%, rgba(131, 234, 255, 0.12), transparent 26%);
      pointer-events: none;
    }}

    .hero-inner {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      color: var(--gold);
      letter-spacing: .18em;
      text-transform: uppercase;
      font-size: 12px;
      font-weight: 850;
    }}

    h1 {{
      margin: 14px 0 14px;
      font-size: clamp(34px, 5vw, 62px);
      line-height: .95;
    }}

    p {{
      color: var(--muted);
      line-height: 1.62;
    }}

    .hero-copy {{
      max-width: 940px;
      font-size: 16px;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}

    .metric {{
      border: 1px solid var(--line);
      background: rgba(5, 8, 20, 0.48);
      border-radius: 20px;
      padding: 16px;
    }}

    .metric strong {{
      display: block;
      font-size: 26px;
    }}

    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}

    .section {{
      margin-top: 18px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 24px;
      padding: 22px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, .28);
    }}

    .section h2 {{
      margin: 0 0 10px;
      font-size: 22px;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
      color: var(--text);
      background: rgba(10, 16, 38, .72);
      white-space: nowrap;
    }}

    .pill.ok {{
      color: var(--ok);
      border-color: rgba(157, 255, 202, .32);
    }}

    .pill.warn {{
      color: var(--gold);
      border-color: rgba(245, 209, 126, .32);
    }}

    .pill.danger {{
      color: var(--danger);
      border-color: rgba(255, 140, 156, .32);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
    }}

    .card {{
      border: 1px solid var(--line);
      background: var(--panel2);
      border-radius: 20px;
      padding: 16px;
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }}

    .title {{
      font-weight: 900;
      font-size: 15px;
    }}

    .meta {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
      line-height: 1.55;
    }}

    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}

    .status-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 12px 0;
      border-bottom: 1px solid rgba(160, 179, 255, .14);
    }}

    .status-row:last-child {{
      border-bottom: none;
    }}

    .status-row span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}

    code {{
      color: var(--cyan);
      background: rgba(0, 0, 0, .28);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 2px 6px;
    }}

    ul {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.75;
    }}

    @media (max-width: 1020px) {{
      .metrics,
      .grid,
      .two-col {{
        grid-template-columns: 1fr;
      }}

      .card-top,
      .status-row {{
        flex-direction: column;
        align-items: flex-start;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-inner">
        <div class="eyebrow">Archive Vault · Giant Pack 041 · New Section</div>
        <h1>Storage Provider Contract Starter</h1>
        <p class="hero-copy">
          GP041 starts the next Vault depth layer. It defines future storage-provider contracts,
          object-key placeholders, checksum placeholders, retention/redaction gates, and Tower authority gates.
          No provider is selected. No raw storage or direct upload is unlocked.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['provider_option_count']}</strong>
            <span>provider placeholders</span>
          </div>
          <div class="metric">
            <strong>{counts['object_key_placeholder_count']}</strong>
            <span>object-key placeholders</span>
          </div>
          <div class="metric">
            <strong>{counts['boundary_violation_count']}</strong>
            <span>boundary violations</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">New section started</span>
          <span class="pill ok">Contract ready</span>
          <span class="pill warn">Provider placeholders only</span>
          <span class="pill danger">No raw storage</span>
          <span class="pill danger">No direct upload</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Provider Options</h2>
      <p>Provider candidates are visible as placeholders only. Nothing is selected, configured, writable, readable, exported, delivered, or public.</p>
      <div class="grid">
        {provider_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Object Key Contract</h2>
        <p>Object-key and checksum placeholders are metadata-only.</p>
        <div>{object_rows}</div>
      </div>
      <div>
        <h2>Boundary Check</h2>
        <p>Restricted paths remain locked.</p>
        <div>{boundary_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP042</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP041 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['provider_options_route'])}</code>
        <code>{escape(routes['object_key_contract_route'])}</code>
        <code>{escape(routes['retention_redaction_gates_route'])}</code>
        <code>{escape(routes['tower_gates_route'])}</code>
        <code>{escape(routes['boundary_check_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp041_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_provider_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['provider_label'])}</div>
            <div class="meta">
              ID: <code>{escape(item['provider_option_id'])}</code><br>
              Type: <code>{escape(item['provider_type'])}</code><br>
              Selected: <code>{str(item['provider_selected']).lower()}</code><br>
              Configured: <code>{str(item['provider_configured']).lower()}</code><br>
              Writable: <code>{str(item['provider_write_enabled']).lower()}</code>
            </div>
          </div>
          <span class="pill warn">Placeholder</span>
        </div>
      </article>
    """
