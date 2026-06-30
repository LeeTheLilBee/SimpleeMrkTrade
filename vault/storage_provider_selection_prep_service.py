"""
VAULT GIANT PACK 051 — Storage Provider Selection Prep

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack starts the Storage Provider Prep Layer after GP050 closed GP041-GP050.

Purpose:
- Build metadata-only storage provider candidate previews.
- Build provider selection criteria.
- Build provider selection locks.
- Build Tower provider authority gates.
- Build provider prep note placeholders.
- Carry forward to GP052.

Important truth:
- GP051 starts a new section.
- GP051 prepares provider selection; it does not select a provider.
- GP051 does not configure a provider.
- GP051 does not enable provider read or write.
- GP051 does not view object bodies.
- GP051 does not store raw file bodies.
- GP051 does not unlock direct upload.
- GP051 does not verify checksums/hashes.
- GP051 does not create official receipts.
- GP051 does not finalize receipts.
- GP051 does not close receipts.
- GP051 does not write official audit logs.
- GP051 does not write immutable audit entries.
- GP051 does not grant storage access.
- GP051 does not approve or execute actions.
- GP051 does not export or externally deliver anything.
- GP051 does not open portals.
- GP051 does not create public proof.
- GP051 does not mark Vault done.
- Tower remains the authority for identity, permissions, clearance, provider authorization,
  storage access, object visibility, receipts, audit, action, export, and execution gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict

from vault.next_product_depth_readiness_checkpoint_service import get_next_product_depth_readiness_checkpoint_payload


PACK_ID = "VAULT_GP051"
PACK_NAME = "Storage Provider Selection Prep"
SCHEMA_VERSION = "vault.storage_provider_selection_prep.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

PREVIOUS_SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
PREVIOUS_SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
PREVIOUS_SECTION_RANGE = "GP041-GP050"

NEXT_PACK = "VAULT_GP052_STORAGE_PROVIDER_CRITERIA_BOARD"
NEXT_PACK_TITLE = "Storage Provider Criteria Board"

PROVIDER_CANDIDATE_TYPES = [
    "encrypted_object_storage_candidate",
    "private_archive_bucket_candidate",
    "evidence_packet_store_candidate",
    "receipt_metadata_store_candidate",
    "immutable_audit_log_store_candidate",
]

SELECTION_CRITERIA = [
    "tower_authority_required",
    "private_vault_boundary_required",
    "metadata_first_support_required",
    "encryption_support_required",
    "audit_trace_support_required",
    "no_public_access_default_required",
    "object_body_locked_until_authorized",
    "export_lock_compatibility_required",
]

SELECTION_LOCK_TYPES = [
    "provider_selection_blocked",
    "provider_configuration_blocked",
    "provider_read_blocked",
    "provider_write_blocked",
    "object_body_view_blocked",
    "raw_file_body_storage_blocked",
    "direct_upload_blocked",
    "checksum_hash_verification_unclaimed",
    "external_export_blocked",
]

TOWER_PROVIDER_GATES = [
    "tower_identity_gate",
    "tower_clearance_gate",
    "tower_storage_provider_authority_gate",
    "tower_storage_access_authority_gate",
    "tower_object_visibility_gate",
    "tower_export_lock_gate",
    "tower_execution_lock_gate",
]

PREP_NOTE_FIELDS = [
    "owner_selection_note",
    "tower_question",
    "risk_note",
    "integration_note",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_provider_selection_prep_payload() -> Dict[str, Any]:
    gp050 = get_next_product_depth_readiness_checkpoint_payload()

    provider_candidates = _build_provider_candidates()
    selection_criteria = _build_selection_criteria(provider_candidates)
    selection_locks = _build_selection_locks(provider_candidates)
    tower_authority_gates = _build_tower_authority_gates(provider_candidates)
    prep_notes = _build_prep_notes(provider_candidates)
    next_step = _build_next_step(
        provider_candidates,
        selection_criteria,
        selection_locks,
        tower_authority_gates,
        prep_notes,
    )

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP050"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_provider_selection_prep",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "previous_section": PREVIOUS_SECTION_ID,
            "previous_section_title": PREVIOUS_SECTION_TITLE,
            "previous_section_range": PREVIOUS_SECTION_RANGE,
            "starts_new_section": True,
        },
        "selection_truth": {
            "storage_provider_selection_prep_ready": True,
            "new_section_started": True,
            "provider_candidate_previews_visible": True,
            "selection_criteria_visible": True,
            "selection_locks_visible": True,
            "tower_provider_authority_gates_visible": True,
            "provider_prep_notes_visible": True,
            "metadata_only": True,
            "private_prep_only": True,
            "provider_candidate_count": provider_candidates["provider_candidate_count"],
            "selection_criteria_count": selection_criteria["selection_criteria_count"],
            "selection_lock_count": selection_locks["selection_lock_count"],
            "tower_provider_gate_count": tower_authority_gates["tower_provider_gate_count"],
            "prep_note_placeholder_count": prep_notes["prep_note_placeholder_count"],
            "provider_selected_count": 0,
            "provider_configured_count": 0,
            "provider_write_enabled_count": 0,
            "provider_read_enabled_count": 0,
            "provider_object_read_claimed_count": 0,
            "provider_connection_tested_count": 0,
            "raw_file_body_storage_enabled": False,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "object_body_view_enabled": False,
            "direct_upload_unlocked": False,
            "direct_upload_enabled": False,
            "checksum_verified_count": 0,
            "hash_verified_count": 0,
            "official_storage_receipt_created_count": 0,
            "official_storage_receipt_claimed_count": 0,
            "finalized_storage_receipt_count": 0,
            "closed_storage_receipt_count": 0,
            "official_action_receipt_created_count": 0,
            "official_action_receipt_claimed_count": 0,
            "finalized_action_receipt_count": 0,
            "closed_action_receipt_count": 0,
            "official_audit_log_created_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "immutable_hash_chain_written_count": 0,
            "tower_attestation_written_count": 0,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "action_approved_count": 0,
            "action_executed_count": 0,
            "action_completed_count": 0,
            "action_closed_count": 0,
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
            "vault_done": False,
            "clouds_should_continue": False,
            "safe_to_continue_to_gp052": True,
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
            "tower_owns_storage_provider_authorization": True,
            "tower_owns_storage_access_authorization": True,
            "tower_owns_object_visibility": True,
            "tower_owns_storage_receipt_authority": True,
            "tower_owns_audit_authority": True,
            "tower_owns_audit_review_authority": True,
            "tower_owns_audit_action_authority": True,
            "tower_owns_action_receipt_authority": True,
            "tower_owns_action_authority_gates": True,
            "tower_owns_execution_gates": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_select_provider_without_tower": False,
            "vault_can_configure_provider_without_tower": False,
            "vault_can_enable_provider_read": False,
            "vault_can_enable_provider_write": False,
            "vault_can_view_object_body": False,
            "vault_can_store_raw_file_body": False,
            "vault_can_unlock_direct_upload": False,
            "vault_can_verify_checksum_or_hash": False,
            "vault_can_mark_vault_done": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "provider_selection_default": "candidate_preview_only_no_provider_selected",
            "provider_configuration_default": "locked_not_configured",
            "provider_read_default": "locked_not_enabled",
            "provider_write_default": "locked_not_enabled",
            "object_body_default": "locked_not_visible",
            "raw_file_body_storage_default": "locked_not_persisted",
            "direct_upload_default": "locked",
            "checksum_hash_default": "placeholder_only_not_verified",
            "external_access_default": "denied",
            "storage_access_default": "denied_by_default",
            "external_packet_delivery_allowed": False,
            "packet_export_allowed": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "object_body_preview_allowed": False,
            "object_body_view_allowed": False,
            "provider_read_allowed": False,
            "provider_write_allowed": False,
            "official_audit_log_write_allowed": False,
            "immutable_log_write_allowed": False,
            "audit_review_approval_allowed": False,
            "audit_action_approval_allowed": False,
            "audit_action_execution_allowed": False,
            "action_receipt_finalize_allowed": False,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "selection_routes": {
            "room_title": "Vault Storage Provider Selection Prep",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-provider-selection-prep",
            "json_route": "/vault/storage-provider-selection-prep.json",
            "provider_candidates_route": "/vault/storage-provider-candidates.json",
            "selection_criteria_route": "/vault/storage-provider-selection-criteria.json",
            "selection_locks_route": "/vault/storage-provider-selection-locks.json",
            "tower_authority_gates_route": "/vault/storage-provider-tower-authority-gates.json",
            "prep_notes_route": "/vault/storage-provider-prep-notes.json",
            "next_step_route": "/vault/storage-provider-selection-next-step.json",
            "gp051_status_route": "/vault/gp051-status.json",
        },
        "selection_counts": {
            "provider_candidate_count": provider_candidates["provider_candidate_count"],
            "selection_criteria_count": selection_criteria["selection_criteria_count"],
            "selection_lock_count": selection_locks["selection_lock_count"],
            "tower_provider_gate_count": tower_authority_gates["tower_provider_gate_count"],
            "prep_note_placeholder_count": prep_notes["prep_note_placeholder_count"],
            "provider_selected_count": 0,
            "provider_configured_count": 0,
            "provider_read_enabled_count": 0,
            "provider_write_enabled_count": 0,
            "provider_object_read_claimed_count": 0,
            "provider_connection_tested_count": 0,
            "object_body_view_enabled_count": 0,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "checksum_verified_count": 0,
            "hash_verified_count": 0,
            "official_receipt_count": 0,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "access_granted_count": 0,
            "action_approved_count": 0,
            "action_executed_count": 0,
            "external_delivery_allowed_count": 0,
            "packet_export_allowed_count": 0,
            "execution_allowed_count": 0,
            "vault_done_count": 0,
        },
        "provider_candidates": provider_candidates,
        "selection_criteria": selection_criteria,
        "selection_locks": selection_locks,
        "tower_authority_gates": tower_authority_gates,
        "prep_notes": prep_notes,
        "next_step": next_step,
        "gp050_connection": {
            "gp050_pack_id": gp050["pack"]["id"],
            "gp050_ready": gp050["gp050_status"]["ready"],
            "gp050_section_closed": gp050["gp050_status"]["section_closed_by_gp050"],
            "gp050_safe_to_continue": gp050["gp050_status"]["safe_to_continue_to_gp051"],
            "gp050_vault_done": gp050["gp050_status"]["vault_done"],
            "gp050_next_section_id": gp050["gp050_status"]["next_section_id"],
            "gp050_next_section_title": gp050["gp050_status"]["next_section_title"],
            "gp050_next_section_range": gp050["gp050_status"]["next_section_range"],
            "gp050_next_pack": gp050["gp050_status"]["next_pack"],
        },
        "gp051_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_provider_selection_prep_ready": True,
            "new_section_started": True,
            "safe_to_continue_to_gp052": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_provider_prep": True,
            "private_provider_prep_only": True,
            "provider_candidates_ready": True,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "provider_object_read_claimed": False,
            "provider_connection_tested": False,
            "object_body_view_enabled": False,
            "raw_file_body_storage_still_locked": True,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "direct_upload_still_locked": True,
            "checksum_verification_not_claimed": True,
            "hash_verification_not_claimed": True,
            "official_receipt_count": 0,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
            "official_audit_log_created_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "access_request_granted_count": 0,
            "decision_granted_count": 0,
            "action_approved_count": 0,
            "action_executed_count": 0,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp051",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
    }

    return payload


def _build_provider_candidates() -> Dict[str, Any]:
    items = []

    for index, candidate_type in enumerate(PROVIDER_CANDIDATE_TYPES, start=1):
        items.append(
            {
                "provider_candidate_id": f"VSPC-{index:03d}",
                "candidate_type": candidate_type,
                "candidate_label": candidate_type.replace("_", " ").title(),
                "candidate_status": "CANDIDATE_PREVIEW_ONLY_NOT_SELECTED",
                "metadata_only": True,
                "private_prep_only": True,
                "candidate_visible": True,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "provider_object_read_claimed": False,
                "provider_connection_tested": False,
                "tower_provider_authority_required": True,
                "tower_provider_authority_granted": False,
                "object_body_view_enabled": False,
                "raw_file_body_storage_enabled": False,
                "file_body_persisted": False,
                "object_body_available": False,
                "direct_upload_enabled": False,
                "checksum_verified": False,
                "hash_verified": False,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "access_granted": False,
                "action_approved": False,
                "action_executed": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "portal_access_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp052": True,
            }
        )

    return {
        "provider_candidate_items": items,
        "provider_candidate_count": len(items),
        "candidate_visible_count": len(items),
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "provider_object_read_claimed_count": 0,
        "provider_connection_tested_count": 0,
        "tower_provider_authority_required_count": len(items),
        "tower_provider_authority_granted_count": 0,
        "object_body_view_enabled_count": 0,
        "raw_file_body_storage_enabled_count": 0,
        "file_body_persisted_count": 0,
        "object_body_available_count": 0,
        "direct_upload_enabled_count": 0,
        "checksum_verified_count": 0,
        "hash_verified_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "access_granted_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_provider_candidates": True,
    }


def _build_selection_criteria(provider_candidates: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for candidate in provider_candidates["provider_candidate_items"]:
        for criterion in SELECTION_CRITERIA:
            items.append(
                {
                    "selection_criteria_id": f"VSPCR-{candidate['provider_candidate_id'].split('-')[-1]}-{criterion}",
                    "provider_candidate_id": candidate["provider_candidate_id"],
                    "candidate_type": candidate["candidate_type"],
                    "criterion": criterion,
                    "criterion_status": "REQUIRED_NOT_SATISFIED_NOT_VERIFIED",
                    "metadata_only": True,
                    "required": True,
                    "satisfied": False,
                    "verified": False,
                    "tower_authority_required": True,
                    "tower_authority_granted": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp052": True,
                }
            )

    return {
        "selection_criteria_items": items,
        "selection_criteria_count": len(items),
        "criteria_type_count": len(SELECTION_CRITERIA),
        "provider_candidate_count": provider_candidates["provider_candidate_count"],
        "required_count": len(items),
        "satisfied_count": 0,
        "verified_count": 0,
        "tower_authority_required_count": len(items),
        "tower_authority_granted_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_selection_criteria": True,
    }


def _build_selection_locks(provider_candidates: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for candidate in provider_candidates["provider_candidate_items"]:
        for lock_name in SELECTION_LOCK_TYPES:
            items.append(
                {
                    "selection_lock_id": f"VSPL-{candidate['provider_candidate_id'].split('-')[-1]}-{lock_name}",
                    "provider_candidate_id": candidate["provider_candidate_id"],
                    "candidate_type": candidate["candidate_type"],
                    "lock_name": lock_name,
                    "lock_status": "ACTIVE_SELECTION_PREP_LOCK",
                    "metadata_only": True,
                    "active": True,
                    "blocks_provider_selection": True,
                    "blocks_provider_configuration": True,
                    "blocks_provider_read": True,
                    "blocks_provider_write": True,
                    "blocks_object_body_view": True,
                    "blocks_raw_file_body_storage": True,
                    "blocks_direct_upload": True,
                    "blocks_checksum_hash_verification_claim": True,
                    "blocks_export": True,
                    "blocks_external_delivery": True,
                    "blocks_execution": True,
                    "blocks_vault_done": True,
                    "owner_resolvable_now": False,
                    "tower_authority_required": True,
                    "safe_to_continue_to_gp052": True,
                }
            )

    return {
        "selection_lock_items": items,
        "selection_lock_count": len(items),
        "lock_type_count": len(SELECTION_LOCK_TYPES),
        "provider_candidate_count": provider_candidates["provider_candidate_count"],
        "active_lock_count": len(items),
        "blocks_provider_selection_count": len(items),
        "blocks_provider_configuration_count": len(items),
        "blocks_provider_read_count": len(items),
        "blocks_provider_write_count": len(items),
        "blocks_object_body_view_count": len(items),
        "blocks_raw_file_body_storage_count": len(items),
        "blocks_direct_upload_count": len(items),
        "blocks_checksum_hash_verification_claim_count": len(items),
        "blocks_export_count": len(items),
        "blocks_external_delivery_count": len(items),
        "blocks_execution_count": len(items),
        "blocks_vault_done_count": len(items),
        "owner_resolvable_now_count": 0,
        "tower_authority_required_count": len(items),
        "safe_to_continue_selection_locks": True,
    }


def _build_tower_authority_gates(provider_candidates: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for candidate in provider_candidates["provider_candidate_items"]:
        for gate_name in TOWER_PROVIDER_GATES:
            items.append(
                {
                    "tower_provider_gate_id": f"VSPTG-{candidate['provider_candidate_id'].split('-')[-1]}-{gate_name}",
                    "provider_candidate_id": candidate["provider_candidate_id"],
                    "candidate_type": candidate["candidate_type"],
                    "gate_name": gate_name,
                    "gate_status": "TOWER_PROVIDER_AUTHORITY_REQUIRED_NOT_GRANTED",
                    "metadata_only": True,
                    "required": True,
                    "granted": False,
                    "vault_can_override": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                    "object_body_view_enabled": False,
                    "official_receipt_claimed": False,
                    "official_audit_log_written": False,
                    "access_granted": False,
                    "export_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp052": True,
                }
            )

    return {
        "tower_provider_gate_items": items,
        "tower_provider_gate_count": len(items),
        "gate_type_count": len(TOWER_PROVIDER_GATES),
        "provider_candidate_count": provider_candidates["provider_candidate_count"],
        "required_count": len(items),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "official_receipt_claimed_count": 0,
        "official_audit_log_written_count": 0,
        "access_granted_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_tower_authority_gates": True,
    }


def _build_prep_notes(provider_candidates: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for candidate in provider_candidates["provider_candidate_items"]:
        for field in PREP_NOTE_FIELDS:
            items.append(
                {
                    "prep_note_placeholder_id": f"VSPNP-{candidate['provider_candidate_id'].split('-')[-1]}-{field}",
                    "provider_candidate_id": candidate["provider_candidate_id"],
                    "candidate_type": candidate["candidate_type"],
                    "note_field": field,
                    "note_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                    "metadata_only": True,
                    "note_required": True,
                    "note_present": False,
                    "reviewer_bound": False,
                    "reviewer_confirmed": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp052": True,
                }
            )

    return {
        "prep_note_placeholder_items": items,
        "prep_note_placeholder_count": len(items),
        "prep_note_field_type_count": len(PREP_NOTE_FIELDS),
        "provider_candidate_count": provider_candidates["provider_candidate_count"],
        "note_required_count": len(items),
        "note_present_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_prep_notes": True,
    }


def _build_next_step(
    provider_candidates: Dict[str, Any],
    selection_criteria: Dict[str, Any],
    selection_locks: Dict[str, Any],
    tower_authority_gates: Dict[str, Any],
    prep_notes: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSPSPNX-001",
            "title": "Build storage provider criteria board",
            "target_pack": NEXT_PACK,
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPSPNX-002",
            "title": "Keep provider candidates preview-only",
            "target_pack": NEXT_PACK,
            "status": "PROVIDER_CANDIDATES_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPSPNX-003",
            "title": "Keep provider access locked",
            "target_pack": NEXT_PACK,
            "status": "PROVIDER_ACCESS_LOCKS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp052_count": len(items),
        "provider_candidate_count": provider_candidates["provider_candidate_count"],
        "selection_criteria_count": selection_criteria["selection_criteria_count"],
        "selection_lock_count": selection_locks["selection_lock_count"],
        "tower_provider_gate_count": tower_authority_gates["tower_provider_gate_count"],
        "prep_note_placeholder_count": prep_notes["prep_note_placeholder_count"],
        "safe_to_continue_to_gp052": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": NEXT_PACK,
        "recommended_next_pack_title": NEXT_PACK_TITLE,
        "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep provider candidates preview-only.",
            "Do not select a provider.",
            "Do not configure a provider.",
            "Do not enable provider read.",
            "Do not enable provider write.",
            "Do not claim provider object reads.",
            "Do not show object bodies.",
            "Do not persist raw file bodies.",
            "Do not unlock direct upload.",
            "Do not claim checksum/hash verification.",
            "Keep Tower provider authority gates required and ungranted.",
            "Keep selection criteria unsatisfied and unverified.",
            "Keep prep notes empty and unconfirmed.",
            "Keep official receipts, finalized receipts, and receipt close locked.",
            "Keep official audit logs and immutable audit writes locked.",
            "Keep access grants, action approval, and action execution locked.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_provider_selection_prep_payload())


def get_storage_provider_selection_prep_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "selection_truth": payload["selection_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "selection_routes": payload["selection_routes"],
        "selection_counts": payload["selection_counts"],
        "gp050_connection": payload["gp050_connection"],
    }


def get_storage_provider_candidates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "provider_candidates": payload["provider_candidates"],
    }


def get_storage_provider_selection_criteria() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "selection_criteria": payload["selection_criteria"],
    }


def get_storage_provider_selection_locks() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "selection_locks": payload["selection_locks"],
    }


def get_storage_provider_tower_authority_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_authority_gates": payload["tower_authority_gates"],
    }


def get_storage_provider_prep_notes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "prep_notes": payload["prep_notes"],
    }


def get_storage_provider_selection_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp051_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp051_status": payload["gp051_status"],
        "selection_truth": payload["selection_truth"],
        "selection_routes": payload["selection_routes"],
        "selection_counts": payload["selection_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "provider_candidates": payload["provider_candidates"],
        "next_step": payload["next_step"],
        "gp050_connection": payload["gp050_connection"],
    }


def render_storage_provider_selection_prep_page() -> str:
    payload = clone_payload()
    routes = payload["selection_routes"]
    counts = payload["selection_counts"]
    truth = payload["selection_truth"]
    candidates = payload["provider_candidates"]
    locks = payload["selection_locks"]
    gates = payload["tower_authority_gates"]
    next_step = payload["next_step"]

    candidate_html = "\n".join(_render_candidate_card(item) for item in candidates["provider_candidate_items"])
    lock_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['candidate_type'])}</strong>
            <span>{escape(item['lock_name'])} · {escape(item['lock_status'])}</span>
          </div>
          <div class="pill danger">Locked</div>
        </div>
        """
        for item in locks["selection_lock_items"][:12]
    )
    gate_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['candidate_type'])}</strong>
            <span>{escape(item['gate_name'])} · {escape(item['gate_status'])}</span>
          </div>
          <div class="pill warn">Tower required</div>
        </div>
        """
        for item in gates["tower_provider_gate_items"][:12]
    )
    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Provider Selection Prep · GP051</title>
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
      grid-template-columns: repeat(3, minmax(0, 1fr));
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
        <div class="eyebrow">Archive Vault · Giant Pack 051 · New Section</div>
        <h1>Storage Provider Selection Prep</h1>
        <p class="hero-copy">
          GP051 starts the Storage Provider Prep Layer. It shows provider candidates and selection requirements
          without selecting, configuring, reading, writing, exporting, approving, or executing anything.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['provider_candidate_count']}</strong>
            <span>provider candidates</span>
          </div>
          <div class="metric">
            <strong>{counts['selection_criteria_count']}</strong>
            <span>selection criteria</span>
          </div>
          <div class="metric">
            <strong>{counts['provider_selected_count']}</strong>
            <span>providers selected</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">New section started</span>
          <span class="pill ok">Selection prep ready</span>
          <span class="pill danger">No provider selected</span>
          <span class="pill danger">No provider access</span>
          <span class="pill danger">No object body view</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Provider Candidate Previews</h2>
      <p>These are candidates only. No provider is selected, configured, connected, read, or written.</p>
      <div class="grid">
        {candidate_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Selection Locks</h2>
        <p>Locks keep provider selection, configuration, object bodies, raw storage, direct upload, export, and execution blocked.</p>
        <div>{lock_rows}</div>
      </div>
      <div>
        <h2>Tower Provider Authority Gates</h2>
        <p>Tower authority is required and not granted to Vault.</p>
        <div>{gate_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP052</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP051 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['provider_candidates_route'])}</code>
        <code>{escape(routes['selection_criteria_route'])}</code>
        <code>{escape(routes['selection_locks_route'])}</code>
        <code>{escape(routes['tower_authority_gates_route'])}</code>
        <code>{escape(routes['prep_notes_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp051_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_candidate_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['candidate_label'])}</div>
            <div class="meta">
              Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
              Status: <code>{escape(item['candidate_status'])}</code><br>
              Selected: <code>{str(item['provider_selected']).lower()}</code><br>
              Configured: <code>{str(item['provider_configured']).lower()}</code><br>
              Read/write: <code>{str(item['provider_read_enabled']).lower()} / {str(item['provider_write_enabled']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Preview only</span>
        </div>
      </article>
    """
