"""
VAULT GIANT PACK 049 — Storage Audit Action Receipt Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP048 by creating metadata-only action receipt previews
for blocked audit action suggestions.

Purpose:
- Build audit action receipt preview cards.
- Add blocked action receipt labels.
- Add Tower action gate receipt snapshots.
- Add reviewer follow-up receipt placeholders.
- Add no-execution receipt enforcement records.
- Carry forward to GP050.

Important truth:
- GP049 previews action receipts only.
- GP049 does not create official action receipts.
- GP049 does not finalize action receipts.
- GP049 does not close action receipts.
- GP049 does not approve actions.
- GP049 does not execute actions.
- GP049 does not approve audit review.
- GP049 does not write an official audit log.
- GP049 does not write immutable audit entries.
- GP049 does not create official storage receipts.
- GP049 does not finalize storage receipts.
- GP049 does not close storage receipts.
- GP049 does not approve access.
- GP049 does not grant access.
- GP049 does not read provider objects.
- GP049 does not write provider objects.
- GP049 does not show object bodies.
- GP049 does not store raw files.
- GP049 does not unlock direct upload.
- GP049 does not select or configure a provider.
- GP049 does not verify checksums/hashes.
- GP049 does not export or externally deliver anything.
- GP049 does not create public proof.
- GP049 does not open portals.
- GP049 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP049 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization,
  receipt authority, audit authority, review authority, action authority,
  action receipt authority, and execution gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict

from vault.storage_audit_action_preview_service import get_storage_audit_action_preview_payload


PACK_ID = "VAULT_GP049"
PACK_NAME = "Storage Audit Action Receipt Preview"
SCHEMA_VERSION = "vault.storage_audit_action_receipt_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

ACTION_RECEIPT_PREVIEW_TYPES = [
    "blocked_action_receipt_preview",
    "tower_gate_receipt_snapshot",
    "reviewer_followup_receipt_placeholder",
    "no_execution_receipt_enforcement",
    "gp050_readiness_carry_forward",
]

ACTION_RECEIPT_LOCK_REASONS = [
    "not_official_action_receipt",
    "not_finalized_action_receipt",
    "not_closed_action_receipt",
    "action_not_approved",
    "action_not_executed",
    "tower_action_authority_missing",
    "provider_access_locked",
    "object_body_view_locked",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_audit_action_receipt_preview_payload() -> Dict[str, Any]:
    gp048 = get_storage_audit_action_preview_payload()

    receipt_cards = _build_action_receipt_cards(gp048)
    blocked_receipt_labels = _build_blocked_action_receipt_labels(receipt_cards)
    tower_gate_receipts = _build_tower_action_gate_receipts(gp048)
    followup_receipt_placeholders = _build_followup_receipt_placeholders(gp048)
    no_execution_receipts = _build_no_execution_receipts(gp048)
    next_step = _build_next_step(
        receipt_cards,
        blocked_receipt_labels,
        tower_gate_receipts,
        followup_receipt_placeholders,
        no_execution_receipts,
    )

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
                "VAULT_GP041",
                "VAULT_GP042",
                "VAULT_GP043",
                "VAULT_GP044",
                "VAULT_GP045",
                "VAULT_GP046",
                "VAULT_GP047",
                "VAULT_GP048",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_audit_action_receipt_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "action_receipt_truth": {
            "storage_audit_action_receipt_preview_ready": True,
            "action_receipt_preview_cards_visible": True,
            "blocked_action_receipt_labels_visible": True,
            "tower_action_gate_receipt_snapshots_visible": True,
            "reviewer_followup_receipt_placeholders_visible": True,
            "no_execution_receipt_enforcement_visible": True,
            "metadata_only": True,
            "private_action_receipt_preview_only": True,
            "action_receipt_preview_count": receipt_cards["action_receipt_card_count"],
            "official_action_receipt_created_count": 0,
            "official_action_receipt_claimed_count": 0,
            "finalized_action_receipt_count": 0,
            "closed_action_receipt_count": 0,
            "action_receipt_finalized": False,
            "action_receipt_closed": False,
            "action_approved_count": 0,
            "action_executed_count": 0,
            "action_completed_count": 0,
            "action_closed_count": 0,
            "audit_review_approved_count": 0,
            "audit_review_completed_count": 0,
            "audit_review_closed_count": 0,
            "official_audit_log_created_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "immutable_hash_chain_written_count": 0,
            "tower_attestation_written_count": 0,
            "official_storage_receipt_created_count": 0,
            "official_storage_receipt_claimed_count": 0,
            "finalized_storage_receipt_count": 0,
            "closed_storage_receipt_count": 0,
            "storage_receipt_finalized": False,
            "storage_receipt_closed": False,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "access_denied_by_default_count": gp048["action_counts"]["source_review_card_count"],
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "provider_object_read_claimed": False,
            "raw_file_body_storage_enabled": False,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "object_body_view_enabled": False,
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
            "vault_done": False,
            "clouds_should_continue": False,
            "safe_to_continue_to_gp050": True,
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
            "tower_owns_execution_gates": True,
            "tower_owns_storage_provider_authorization": True,
            "tower_owns_object_visibility": True,
            "tower_owns_storage_access_authorization": True,
            "tower_owns_access_decision_approval": True,
            "tower_owns_storage_receipt_authority": True,
            "tower_owns_audit_authority": True,
            "tower_owns_audit_review_authority": True,
            "tower_owns_audit_action_authority": True,
            "tower_owns_action_receipt_authority": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
            "vault_can_finalize_storage_receipt": False,
            "vault_can_write_official_audit_log": False,
            "vault_can_approve_audit_review": False,
            "vault_can_approve_audit_action": False,
            "vault_can_execute_audit_action": False,
            "vault_can_finalize_action_receipt": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "storage_access_default": "denied_by_default",
            "decision_default": "blocked_denied_by_default",
            "storage_receipt_default": "preview_only_not_official_not_final",
            "audit_default": "preview_only_not_official_not_immutable",
            "review_default": "metadata_only_unapproved_unclosed",
            "action_default": "suggestion_only_blocked_no_execution",
            "action_receipt_default": "preview_only_not_official_not_final_not_closed",
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
        "action_receipt_routes": {
            "room_title": "Vault Storage Audit Action Receipt Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-audit-action-receipt-preview",
            "json_route": "/vault/storage-audit-action-receipt-preview.json",
            "action_receipt_cards_route": "/vault/storage-audit-action-receipt-cards.json",
            "blocked_action_receipt_labels_route": "/vault/storage-audit-blocked-action-receipt-labels.json",
            "tower_action_gate_receipts_route": "/vault/storage-tower-action-gate-receipts.json",
            "followup_receipt_placeholders_route": "/vault/storage-audit-followup-receipt-placeholders.json",
            "no_execution_receipts_route": "/vault/storage-audit-no-execution-receipts.json",
            "next_step_route": "/vault/storage-audit-action-receipt-next-step.json",
            "gp049_status_route": "/vault/gp049-status.json",
        },
        "action_receipt_counts": {
            "source_action_suggestion_count": receipt_cards["source_action_suggestion_count"],
            "action_receipt_card_count": receipt_cards["action_receipt_card_count"],
            "action_receipt_preview_type_count": receipt_cards["action_receipt_preview_type_count"],
            "blocked_action_receipt_label_count": blocked_receipt_labels["blocked_action_receipt_label_count"],
            "tower_action_gate_receipt_count": tower_gate_receipts["tower_action_gate_receipt_count"],
            "followup_receipt_placeholder_count": followup_receipt_placeholders["followup_receipt_placeholder_count"],
            "no_execution_receipt_count": no_execution_receipts["no_execution_receipt_count"],
            "official_action_receipt_created_count": 0,
            "official_action_receipt_claimed_count": 0,
            "finalized_action_receipt_count": 0,
            "closed_action_receipt_count": 0,
            "action_approved_count": 0,
            "action_executed_count": 0,
            "action_completed_count": 0,
            "action_closed_count": 0,
            "audit_review_approved_count": 0,
            "audit_review_completed_count": 0,
            "audit_review_closed_count": 0,
            "official_audit_log_created_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "immutable_hash_chain_written_count": 0,
            "tower_attestation_written_count": 0,
            "official_storage_receipt_created_count": 0,
            "official_storage_receipt_claimed_count": 0,
            "finalized_storage_receipt_count": 0,
            "closed_storage_receipt_count": 0,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "provider_read_enabled_count": 0,
            "provider_write_enabled_count": 0,
            "object_body_view_enabled_count": 0,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "checksum_verified_count": 0,
            "hash_verified_count": 0,
            "raw_file_body_storage_enabled_count": 0,
            "direct_upload_unlocked_count": 0,
            "external_delivery_allowed_count": 0,
            "packet_export_allowed_count": 0,
            "execution_allowed_count": 0,
            "metadata_only": True,
        },
        "action_receipt_cards": receipt_cards,
        "blocked_action_receipt_labels": blocked_receipt_labels,
        "tower_action_gate_receipts": tower_gate_receipts,
        "followup_receipt_placeholders": followup_receipt_placeholders,
        "no_execution_receipts": no_execution_receipts,
        "next_step": next_step,
        "gp048_connection": {
            "gp048_pack_id": gp048["pack"]["id"],
            "gp048_ready": gp048["gp048_status"]["ready"],
            "gp048_safe_to_continue": gp048["gp048_status"]["safe_to_continue_to_gp049"],
            "gp048_vault_done": gp048["gp048_status"]["vault_done"],
            "gp048_section": gp048["pack"]["section"],
            "gp048_action_suggestion_count": gp048["action_counts"]["action_suggestion_count"],
            "gp048_blocked_action_label_count": gp048["action_counts"]["blocked_action_label_count"],
            "gp048_tower_action_authority_gate_count": gp048["action_counts"]["tower_action_authority_gate_count"],
            "gp048_reviewer_followup_placeholder_count": gp048["action_counts"]["reviewer_followup_placeholder_count"],
            "gp048_no_execution_enforcement_count": gp048["action_counts"]["no_execution_enforcement_count"],
            "gp048_action_executed_count": gp048["action_counts"]["action_executed_count"],
        },
        "gp049_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_audit_action_receipt_preview_ready": True,
            "safe_to_continue_to_gp050": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_action_receipt_preview": True,
            "private_action_receipt_preview_only": True,
            "action_receipt_cards_ready": True,
            "official_action_receipt_created_count": 0,
            "official_action_receipt_claimed_count": 0,
            "finalized_action_receipt_count": 0,
            "closed_action_receipt_count": 0,
            "action_receipt_finalized": False,
            "action_receipt_closed": False,
            "action_approved_count": 0,
            "action_executed_count": 0,
            "action_completed_count": 0,
            "action_closed_count": 0,
            "audit_review_approved_count": 0,
            "audit_review_completed_count": 0,
            "audit_review_closed_count": 0,
            "official_audit_log_created_count": 0,
            "official_audit_log_written_count": 0,
            "immutable_audit_write_count": 0,
            "immutable_hash_chain_written_count": 0,
            "tower_attestation_written_count": 0,
            "official_storage_receipt_created_count": 0,
            "official_storage_receipt_claimed_count": 0,
            "finalized_storage_receipt_count": 0,
            "closed_storage_receipt_count": 0,
            "storage_receipt_finalized": False,
            "storage_receipt_closed": False,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "access_denied_by_default": True,
            "blocked_action_receipts_active": True,
            "no_execution_receipts_active": True,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "provider_object_read_claimed": False,
            "object_body_view_enabled": False,
            "raw_file_body_storage_still_locked": True,
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp049",
            "next_pack": "VAULT_GP050_NEXT_PRODUCT_DEPTH_READINESS_CHECKPOINT",
        },
    }

    return payload


def _build_action_receipt_cards(gp048: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp048["action_suggestions"]["action_suggestion_items"]

    cards = []
    for index, item in enumerate(source_items, start=1):
        cards.append(
            {
                "action_receipt_card_id": f"VSAAR-{index:03d}",
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "receipt_card_id": item["receipt_card_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "action_receipt_status": "PREVIEW_ONLY_NOT_OFFICIAL_NOT_FINAL_NOT_CLOSED",
                "action_receipt_owner_label": "Action receipt preview only — no approval or execution",
                "metadata_only": True,
                "private_action_receipt_preview_only": True,
                "action_receipt_preview_created": True,
                "official_action_receipt_created": False,
                "official_action_receipt_claimed": False,
                "action_receipt_finalized": False,
                "action_receipt_closed": False,
                "action_approved": False,
                "action_executed": False,
                "action_completed": False,
                "action_closed": False,
                "blocked_action_receipt": True,
                "no_execution_receipt": True,
                "tower_action_authority_required": True,
                "tower_action_authority_granted": False,
                "reviewer_followup_required": True,
                "reviewer_followup_present": False,
                "audit_review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "official_storage_receipt_claimed": False,
                "storage_receipt_finalized": False,
                "storage_receipt_closed": False,
                "access_request_submitted": False,
                "access_request_approved": False,
                "access_granted": False,
                "decision_approved": False,
                "decision_granted": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "provider_object_read_claimed": False,
                "object_body_view_enabled": False,
                "object_body_available": False,
                "file_body_persisted": False,
                "raw_file_body_storage_enabled": False,
                "direct_upload_enabled": False,
                "checksum_verified": False,
                "hash_verified": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "portal_access_allowed": False,
                "approval_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp050": True,
            }
        )

    return {
        "action_receipt_card_items": cards,
        "source_action_suggestion_count": len(source_items),
        "action_receipt_card_count": len(cards),
        "action_receipt_preview_type_count": len(ACTION_RECEIPT_PREVIEW_TYPES),
        "action_receipt_preview_created_count": len(cards),
        "official_action_receipt_created_count": 0,
        "official_action_receipt_claimed_count": 0,
        "action_receipt_finalized_count": 0,
        "action_receipt_closed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "action_completed_count": 0,
        "action_closed_count": 0,
        "blocked_action_receipt_count": len(cards),
        "no_execution_receipt_count": len(cards),
        "tower_action_authority_required_count": len(cards),
        "tower_action_authority_granted_count": 0,
        "reviewer_followup_required_count": len(cards),
        "reviewer_followup_present_count": 0,
        "audit_review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "official_storage_receipt_claimed_count": 0,
        "storage_receipt_finalized_count": 0,
        "storage_receipt_closed_count": 0,
        "access_request_submitted_count": 0,
        "access_request_approved_count": 0,
        "access_granted_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "object_body_available_count": 0,
        "file_body_persisted_count": 0,
        "raw_file_body_storage_enabled_count": 0,
        "direct_upload_enabled_count": 0,
        "checksum_verified_count": 0,
        "hash_verified_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "approval_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_action_receipt_cards": True,
    }


def _build_blocked_action_receipt_labels(receipt_cards: Dict[str, Any]) -> Dict[str, Any]:
    labels = []

    for item in receipt_cards["action_receipt_card_items"]:
        labels.append(
            {
                "blocked_action_receipt_label_id": f"VSABARL-{item['action_receipt_card_id'].split('-')[-1]}",
                "action_receipt_card_id": item["action_receipt_card_id"],
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "blocked_receipt_label": "BLOCKED_ACTION_RECEIPT_PREVIEW_ONLY",
                "owner_label": "Blocked action receipt — preview only, no approval or execution",
                "metadata_only": True,
                "blocked_action_receipt": True,
                "blocks_official_action_receipt": True,
                "blocks_action_receipt_finalize": True,
                "blocks_action_receipt_close": True,
                "blocks_action_approval": True,
                "blocks_action_execution": True,
                "blocks_execution": True,
                "blocks_provider_read": True,
                "blocks_object_body_view": True,
                "blocks_export": True,
                "blocks_external_delivery": True,
                "blocks_portal_access": True,
                "blocks_public_proof": True,
                "blocks_financing_decision": True,
                "blocks_legal_advice": True,
                "tower_authority_required": True,
                "official_action_receipt_claimed": False,
                "action_receipt_finalized": False,
                "action_receipt_closed": False,
                "action_approved": False,
                "action_executed": False,
                "safe_to_continue_to_gp050": True,
            }
        )

    return {
        "blocked_action_receipt_label_items": labels,
        "blocked_action_receipt_label_count": len(labels),
        "blocked_action_receipt_count": len(labels),
        "blocks_official_action_receipt_count": len(labels),
        "blocks_action_receipt_finalize_count": len(labels),
        "blocks_action_receipt_close_count": len(labels),
        "blocks_action_approval_count": len(labels),
        "blocks_action_execution_count": len(labels),
        "blocks_execution_count": len(labels),
        "blocks_provider_read_count": len(labels),
        "blocks_object_body_view_count": len(labels),
        "blocks_export_count": len(labels),
        "blocks_external_delivery_count": len(labels),
        "blocks_portal_access_count": len(labels),
        "blocks_public_proof_count": len(labels),
        "blocks_financing_decision_count": len(labels),
        "blocks_legal_advice_count": len(labels),
        "tower_authority_required_count": len(labels),
        "official_action_receipt_claimed_count": 0,
        "action_receipt_finalized_count": 0,
        "action_receipt_closed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "safe_to_continue_blocked_action_receipt_labels": True,
    }


def _build_tower_action_gate_receipts(gp048: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp048["tower_action_authority_gates"]["tower_action_authority_gate_items"]

    receipts = []
    for item in source_items:
        receipts.append(
            {
                "tower_action_gate_receipt_id": f"VSATAGR-{item['tower_action_gate_id'].split('-', 1)[-1]}",
                "tower_action_gate_id": item["tower_action_gate_id"],
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "gate_name": item["gate_name"],
                "gate_receipt_status": "REQUIRED_NOT_GRANTED_RECEIPT_PREVIEW",
                "metadata_only": True,
                "required": True,
                "granted": False,
                "vault_can_override": False,
                "receipt_snapshot_created": True,
                "official_action_receipt_claimed": False,
                "action_receipt_finalized": False,
                "action_receipt_closed": False,
                "action_approved": False,
                "action_executed": False,
                "audit_review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp050": True,
            }
        )

    return {
        "tower_action_gate_receipt_items": receipts,
        "tower_action_gate_receipt_count": len(receipts),
        "receipt_snapshot_created_count": len(receipts),
        "required_count": len(receipts),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
        "official_action_receipt_claimed_count": 0,
        "action_receipt_finalized_count": 0,
        "action_receipt_closed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "audit_review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_tower_action_gate_receipts": True,
    }


def _build_followup_receipt_placeholders(gp048: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp048["reviewer_followup_placeholders"]["reviewer_followup_placeholder_items"]

    placeholders = []
    for item in source_items:
        placeholders.append(
            {
                "followup_receipt_placeholder_id": f"VSARFR-{item['reviewer_followup_placeholder_id'].split('-', 1)[-1]}",
                "reviewer_followup_placeholder_id": item["reviewer_followup_placeholder_id"],
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "followup_field": item["followup_field"],
                "receipt_placeholder_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                "metadata_only": True,
                "followup_required": True,
                "followup_present": False,
                "reviewer_bound": False,
                "reviewer_confirmed": False,
                "receipt_snapshot_created": True,
                "official_action_receipt_claimed": False,
                "action_receipt_finalized": False,
                "action_receipt_closed": False,
                "action_approved": False,
                "action_executed": False,
                "audit_review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp050": True,
            }
        )

    return {
        "followup_receipt_placeholder_items": placeholders,
        "followup_receipt_placeholder_count": len(placeholders),
        "receipt_snapshot_created_count": len(placeholders),
        "followup_required_count": len(placeholders),
        "followup_present_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "official_action_receipt_claimed_count": 0,
        "action_receipt_finalized_count": 0,
        "action_receipt_closed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "audit_review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_followup_receipt_placeholders": True,
    }


def _build_no_execution_receipts(gp048: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp048["no_execution_enforcement"]["no_execution_enforcement_items"]

    receipts = []
    for item in source_items:
        receipts.append(
            {
                "no_execution_receipt_id": f"VSANER-{item['no_execution_enforcement_id'].split('-', 1)[-1]}",
                "no_execution_enforcement_id": item["no_execution_enforcement_id"],
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "no_execution_receipt_status": "NO_EXECUTION_RECEIPT_PREVIEW_ACTIVE",
                "metadata_only": True,
                "no_execution_receipt": True,
                "no_execution_enforced": True,
                "official_action_receipt_claimed": False,
                "action_receipt_finalized": False,
                "action_receipt_closed": False,
                "action_approved": False,
                "action_executed": False,
                "action_completed": False,
                "action_closed": False,
                "audit_review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "official_storage_receipt_claimed": False,
                "storage_receipt_finalized": False,
                "storage_receipt_closed": False,
                "access_granted": False,
                "decision_granted": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "object_body_view_enabled": False,
                "object_body_available": False,
                "file_body_persisted": False,
                "direct_upload_enabled": False,
                "external_delivery_allowed": False,
                "export_allowed": False,
                "portal_access_allowed": False,
                "public_proof_allowed": False,
                "financing_decision_allowed": False,
                "legal_advice_allowed": False,
                "execution_allowed": False,
                "vault_can_override": False,
                "tower_authority_required": True,
                "safe_to_continue_to_gp050": True,
            }
        )

    return {
        "no_execution_receipt_items": receipts,
        "no_execution_receipt_count": len(receipts),
        "no_execution_enforced_count": len(receipts),
        "official_action_receipt_claimed_count": 0,
        "action_receipt_finalized_count": 0,
        "action_receipt_closed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "action_completed_count": 0,
        "action_closed_count": 0,
        "audit_review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "official_storage_receipt_claimed_count": 0,
        "storage_receipt_finalized_count": 0,
        "storage_receipt_closed_count": 0,
        "access_granted_count": 0,
        "decision_granted_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "object_body_available_count": 0,
        "file_body_persisted_count": 0,
        "direct_upload_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "financing_decision_allowed_count": 0,
        "legal_advice_allowed_count": 0,
        "execution_allowed_count": 0,
        "vault_override_allowed_count": 0,
        "tower_authority_required_count": len(receipts),
        "safe_to_continue_no_execution_receipts": True,
    }


def _build_next_step(
    receipt_cards: Dict[str, Any],
    blocked_receipt_labels: Dict[str, Any],
    tower_gate_receipts: Dict[str, Any],
    followup_receipt_placeholders: Dict[str, Any],
    no_execution_receipts: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSAARNX-001",
            "title": "Prepare next product depth readiness checkpoint",
            "target_pack": "VAULT_GP050",
            "status": "READY_FOR_SECTION_CHECKPOINT",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSAARNX-002",
            "title": "Keep action receipts preview-only",
            "target_pack": "VAULT_GP050",
            "status": "ACTION_RECEIPT_PREVIEWS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSAARNX-003",
            "title": "Keep no-execution receipt enforcement active",
            "target_pack": "VAULT_GP050",
            "status": "NO_EXECUTION_RECEIPTS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp050_count": len(items),
        "action_receipt_card_count": receipt_cards["action_receipt_card_count"],
        "blocked_action_receipt_label_count": blocked_receipt_labels["blocked_action_receipt_label_count"],
        "tower_action_gate_receipt_count": tower_gate_receipts["tower_action_gate_receipt_count"],
        "followup_receipt_placeholder_count": followup_receipt_placeholders["followup_receipt_placeholder_count"],
        "no_execution_receipt_count": no_execution_receipts["no_execution_receipt_count"],
        "safe_to_continue_to_gp050": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP050",
        "recommended_next_pack_title": "Next Product Depth Readiness Checkpoint",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. GP050 should close GP041-GP050. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep action receipt previews metadata-only.",
            "Keep action receipts preview-only, not official.",
            "Keep no official action receipt claim.",
            "Keep no finalized action receipt claim.",
            "Keep no closed action receipt claim.",
            "Keep action suggestions blocked.",
            "Keep no action approval claim.",
            "Keep no action execution claim.",
            "Keep no-execution receipt enforcement active.",
            "Keep Tower action gate receipt snapshots required and ungranted.",
            "Keep reviewer follow-up receipt placeholders empty and unconfirmed.",
            "Keep no official audit log claim.",
            "Keep no immutable audit write claim.",
            "Keep no Tower attestation write claim.",
            "Keep no finalized or closed storage receipt claim.",
            "Keep access requests unsubmitted, unapproved, and ungranted.",
            "Keep object body view locked.",
            "Keep provider read/write locked.",
            "Keep raw file body storage locked.",
            "Keep direct upload locked.",
            "Keep checksum/hash verification unclaimed.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_audit_action_receipt_preview_payload())


def get_storage_audit_action_receipt_preview_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_receipt_truth": payload["action_receipt_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "action_receipt_routes": payload["action_receipt_routes"],
        "action_receipt_counts": payload["action_receipt_counts"],
        "gp048_connection": payload["gp048_connection"],
    }


def get_storage_audit_action_receipt_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_receipt_cards": payload["action_receipt_cards"],
    }


def get_storage_audit_blocked_action_receipt_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_action_receipt_labels": payload["blocked_action_receipt_labels"],
    }


def get_storage_tower_action_gate_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_action_gate_receipts": payload["tower_action_gate_receipts"],
    }


def get_storage_audit_followup_receipt_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "followup_receipt_placeholders": payload["followup_receipt_placeholders"],
    }


def get_storage_audit_no_execution_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution_receipts": payload["no_execution_receipts"],
    }


def get_storage_audit_action_receipt_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp049_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp049_status": payload["gp049_status"],
        "action_receipt_truth": payload["action_receipt_truth"],
        "action_receipt_routes": payload["action_receipt_routes"],
        "action_receipt_counts": payload["action_receipt_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp048_connection": payload["gp048_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_audit_action_receipt_preview_page() -> str:
    payload = clone_payload()
    routes = payload["action_receipt_routes"]
    counts = payload["action_receipt_counts"]
    truth = payload["action_receipt_truth"]
    cards = payload["action_receipt_cards"]
    blocked = payload["blocked_action_receipt_labels"]
    no_exec = payload["no_execution_receipts"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_action_receipt_card(item) for item in cards["action_receipt_card_items"][:12])
    blocked_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['action_type'])} · {escape(item['blocked_receipt_label'])}</span>
          </div>
          <div class="pill danger">Blocked receipt</div>
        </div>
        """
        for item in blocked["blocked_action_receipt_label_items"][:12]
    )

    no_exec_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['action_type'])} · {escape(item['no_execution_receipt_status'])}</span>
          </div>
          <div class="pill danger">No execution</div>
        </div>
        """
        for item in no_exec["no_execution_receipt_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Audit Action Receipt Preview · GP049</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 049</div>
        <h1>Storage Audit Action Receipt Preview</h1>
        <p class="hero-copy">
          GP049 previews receipts for blocked audit action suggestions. These are metadata-only previews:
          not official, not finalized, not closed, not approved, and not executed.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['action_receipt_card_count']}</strong>
            <span>action receipt cards</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_action_gate_receipt_count']}</strong>
            <span>Tower gate receipts</span>
          </div>
          <div class="metric">
            <strong>{counts['action_executed_count']}</strong>
            <span>actions executed</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Action receipt preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No official receipt</span>
          <span class="pill danger">No receipt close</span>
          <span class="pill danger">No execution</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Action Receipt Preview Cards</h2>
      <p>Action receipt cards are preview-only. Nothing is official, finalized, closed, approved, executed, exported, or delivered.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Blocked Action Receipt Labels</h2>
        <p>Blocked receipt labels prevent official receipt claims, approval, execution, provider access, object body view, export, delivery, and portals.</p>
        <div>{blocked_rows}</div>
      </div>
      <div>
        <h2>No-Execution Receipt Enforcement</h2>
        <p>No-execution receipts keep every action suggestion locked.</p>
        <div>{no_exec_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP050</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP049 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['action_receipt_cards_route'])}</code>
        <code>{escape(routes['blocked_action_receipt_labels_route'])}</code>
        <code>{escape(routes['tower_action_gate_receipts_route'])}</code>
        <code>{escape(routes['followup_receipt_placeholders_route'])}</code>
        <code>{escape(routes['no_execution_receipts_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp049_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_action_receipt_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['action_receipt_card_id'])}</code><br>
              Action: <code>{escape(item['action_type'])}</code><br>
              Status: <code>{escape(item['action_receipt_status'])}</code><br>
              Official: <code>{str(item['official_action_receipt_claimed']).lower()}</code><br>
              Executed: <code>{str(item['action_executed']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Preview only</span>
        </div>
      </article>
    """
