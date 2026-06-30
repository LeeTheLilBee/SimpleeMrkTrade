"""
VAULT GIANT PACK 048 — Storage Audit Action Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP047 by creating metadata-only audit action previews.

Purpose:
- Build audit action suggestion cards.
- Add blocked action labels.
- Add Tower action authority gates.
- Add reviewer follow-up placeholders.
- Add no-execution enforcement records.
- Carry forward to GP049.

Important truth:
- GP048 previews action suggestions only.
- GP048 does not approve actions.
- GP048 does not execute actions.
- GP048 does not approve audit review.
- GP048 does not write an official audit log.
- GP048 does not write immutable audit entries.
- GP048 does not create official receipts.
- GP048 does not finalize receipts.
- GP048 does not close receipts.
- GP048 does not approve access.
- GP048 does not grant access.
- GP048 does not read provider objects.
- GP048 does not write provider objects.
- GP048 does not show object bodies.
- GP048 does not store raw files.
- GP048 does not unlock direct upload.
- GP048 does not select or configure a provider.
- GP048 does not verify checksums/hashes.
- GP048 does not export or externally deliver anything.
- GP048 does not create public proof.
- GP048 does not open portals.
- GP048 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP048 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization,
  receipt authority, audit authority, review authority, action authority, and execution gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_audit_review_board_service import get_storage_audit_review_board_payload


PACK_ID = "VAULT_GP048"
PACK_NAME = "Storage Audit Action Preview"
SCHEMA_VERSION = "vault.storage_audit_action_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

ACTION_SUGGESTION_TYPES = [
    "create_reviewer_followup",
    "request_tower_authority_review",
    "keep_provider_lock",
    "prepare_owner_summary",
    "carry_forward_to_action_receipt_preview",
]

TOWER_ACTION_GATES = [
    "identity_required",
    "tower_action_authority_required",
    "tower_audit_review_authority_required",
    "owner_review_required",
    "export_lock_required",
    "execution_lock_required",
]

REVIEWER_FOLLOWUP_FIELDS = [
    "followup_note",
    "risk_context",
    "tower_question",
    "owner_summary",
]

BLOCKED_ACTION_REASONS = [
    "no_action_approval",
    "tower_action_authority_missing",
    "audit_review_not_approved",
    "official_audit_log_not_written",
    "immutable_audit_not_written",
    "provider_access_locked",
    "object_body_view_locked",
    "execution_locked",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_audit_action_preview_payload() -> Dict[str, Any]:
    gp047 = get_storage_audit_review_board_payload()

    action_suggestions = _build_action_suggestions(gp047)
    blocked_action_labels = _build_blocked_action_labels(action_suggestions)
    tower_action_authority_gates = _build_tower_action_authority_gates(action_suggestions)
    reviewer_followup_placeholders = _build_reviewer_followup_placeholders(action_suggestions)
    no_execution_enforcement = _build_no_execution_enforcement(action_suggestions)
    next_step = _build_next_step(
        action_suggestions,
        blocked_action_labels,
        tower_action_authority_gates,
        reviewer_followup_placeholders,
        no_execution_enforcement,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_audit_action_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "action_truth": {
            "storage_audit_action_preview_ready": True,
            "action_suggestion_cards_visible": True,
            "blocked_action_labels_visible": True,
            "tower_action_authority_gates_visible": True,
            "reviewer_followup_placeholders_visible": True,
            "no_execution_enforcement_visible": True,
            "metadata_only": True,
            "private_action_preview_only": True,
            "action_suggestion_count": action_suggestions["action_suggestion_count"],
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
            "official_receipt_created_count": 0,
            "official_receipt_claimed_count": 0,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
            "receipt_finalized": False,
            "receipt_closed": False,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "access_denied_by_default_count": action_suggestions["source_review_card_count"],
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
            "safe_to_continue_to_gp049": True,
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
            "tower_owns_receipt_authority": True,
            "tower_owns_audit_authority": True,
            "tower_owns_audit_review_authority": True,
            "tower_owns_audit_action_authority": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
            "vault_can_finalize_storage_access_receipt": False,
            "vault_can_write_official_audit_log": False,
            "vault_can_approve_audit_review": False,
            "vault_can_approve_audit_action": False,
            "vault_can_execute_audit_action": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "storage_access_default": "denied_by_default",
            "decision_default": "blocked_denied_by_default",
            "receipt_default": "preview_only_not_official_not_final",
            "audit_default": "preview_only_not_official_not_immutable",
            "review_default": "metadata_only_unapproved_unclosed",
            "action_default": "suggestion_only_blocked_no_execution",
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
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "action_routes": {
            "room_title": "Vault Storage Audit Action Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-audit-action-preview",
            "json_route": "/vault/storage-audit-action-preview.json",
            "action_suggestions_route": "/vault/storage-audit-action-suggestions.json",
            "blocked_action_labels_route": "/vault/storage-audit-blocked-action-labels.json",
            "tower_action_authority_gates_route": "/vault/storage-tower-action-authority-gates.json",
            "reviewer_followup_placeholders_route": "/vault/storage-audit-reviewer-followup-placeholders.json",
            "no_execution_enforcement_route": "/vault/storage-audit-no-execution-enforcement.json",
            "next_step_route": "/vault/storage-audit-action-next-step.json",
            "gp048_status_route": "/vault/gp048-status.json",
        },
        "action_counts": {
            "source_review_card_count": action_suggestions["source_review_card_count"],
            "action_suggestion_count": action_suggestions["action_suggestion_count"],
            "action_suggestion_type_count": action_suggestions["action_suggestion_type_count"],
            "blocked_action_label_count": blocked_action_labels["blocked_action_label_count"],
            "tower_action_authority_gate_count": tower_action_authority_gates["tower_action_authority_gate_count"],
            "reviewer_followup_placeholder_count": reviewer_followup_placeholders["reviewer_followup_placeholder_count"],
            "no_execution_enforcement_count": no_execution_enforcement["no_execution_enforcement_count"],
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
            "official_receipt_created_count": 0,
            "official_receipt_claimed_count": 0,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
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
        "action_suggestions": action_suggestions,
        "blocked_action_labels": blocked_action_labels,
        "tower_action_authority_gates": tower_action_authority_gates,
        "reviewer_followup_placeholders": reviewer_followup_placeholders,
        "no_execution_enforcement": no_execution_enforcement,
        "next_step": next_step,
        "gp047_connection": {
            "gp047_pack_id": gp047["pack"]["id"],
            "gp047_ready": gp047["gp047_status"]["ready"],
            "gp047_safe_to_continue": gp047["gp047_status"]["safe_to_continue_to_gp048"],
            "gp047_vault_done": gp047["gp047_status"]["vault_done"],
            "gp047_section": gp047["pack"]["section"],
            "gp047_review_card_count": gp047["review_counts"]["review_card_count"],
            "gp047_focus_lane_count": gp047["review_counts"]["focus_lane_count"],
            "gp047_unresolved_issue_label_count": gp047["review_counts"]["unresolved_issue_label_count"],
            "gp047_tower_authority_check_count": gp047["review_counts"]["tower_authority_check_count"],
            "gp047_reviewer_note_placeholder_count": gp047["review_counts"]["reviewer_note_placeholder_count"],
            "gp047_audit_review_approved_count": gp047["review_counts"]["audit_review_approved_count"],
        },
        "gp048_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_audit_action_preview_ready": True,
            "safe_to_continue_to_gp049": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_action_preview": True,
            "private_action_preview_only": True,
            "action_suggestions_ready": True,
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
            "official_receipt_created_count": 0,
            "official_receipt_claimed_count": 0,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
            "receipt_finalized": False,
            "receipt_closed": False,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "access_denied_by_default": True,
            "no_execution_enforced": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp048",
            "next_pack": "VAULT_GP049_STORAGE_AUDIT_ACTION_RECEIPT_PREVIEW",
        },
    }

    return payload


def _build_action_suggestions(gp047: Dict[str, Any]) -> Dict[str, Any]:
    review_items = gp047["review_cards"]["review_card_items"]

    suggestions = []
    for review_index, item in enumerate(review_items, start=1):
        for action_index, action_type in enumerate(ACTION_SUGGESTION_TYPES, start=1):
            suggestions.append(
                {
                    "action_suggestion_id": f"VSASP-{review_index:03d}-{action_index:02d}",
                    "review_card_id": item["review_card_id"],
                    "audit_event_card_id": item["audit_event_card_id"],
                    "receipt_card_id": item["receipt_card_id"],
                    "decision_card_id": item["decision_card_id"],
                    "access_request_card_id": item["access_request_card_id"],
                    "inventory_row_id": item["inventory_row_id"],
                    "object_key_contract_id": item["object_key_contract_id"],
                    "checksum_placeholder_id": item["checksum_placeholder_id"],
                    "scope": item["scope"],
                    "action_type": action_type,
                    "action_status": "SUGGESTION_ONLY_BLOCKED_NO_EXECUTION",
                    "action_owner_label": "Action suggestion only — blocked from approval and execution",
                    "metadata_only": True,
                    "private_action_preview_only": True,
                    "action_suggestion_created": True,
                    "action_approved": False,
                    "action_executed": False,
                    "action_completed": False,
                    "action_closed": False,
                    "blocked_action": True,
                    "tower_action_authority_required": True,
                    "tower_action_authority_granted": False,
                    "reviewer_followup_required": True,
                    "reviewer_followup_present": False,
                    "no_execution_enforced": True,
                    "audit_review_approved": False,
                    "audit_review_completed": False,
                    "audit_review_closed": False,
                    "official_audit_log_created": False,
                    "official_audit_log_written": False,
                    "immutable_audit_written": False,
                    "immutable_hash_chain_written": False,
                    "tower_attestation_written": False,
                    "official_receipt_claimed": False,
                    "receipt_finalized": False,
                    "receipt_closed": False,
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
                    "safe_to_continue_to_gp049": True,
                }
            )

    return {
        "action_suggestion_items": suggestions,
        "source_review_card_count": len(review_items),
        "action_suggestion_count": len(suggestions),
        "action_suggestion_type_count": len(ACTION_SUGGESTION_TYPES),
        "action_suggestion_created_count": len(suggestions),
        "action_approved_count": 0,
        "action_executed_count": 0,
        "action_completed_count": 0,
        "action_closed_count": 0,
        "blocked_action_count": len(suggestions),
        "tower_action_authority_required_count": len(suggestions),
        "tower_action_authority_granted_count": 0,
        "reviewer_followup_required_count": len(suggestions),
        "reviewer_followup_present_count": 0,
        "no_execution_enforced_count": len(suggestions),
        "audit_review_approved_count": 0,
        "audit_review_completed_count": 0,
        "audit_review_closed_count": 0,
        "official_audit_log_created_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "immutable_hash_chain_written_count": 0,
        "tower_attestation_written_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
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
        "safe_to_continue_action_suggestions": True,
    }


def _build_blocked_action_labels(action_suggestions: Dict[str, Any]) -> Dict[str, Any]:
    labels = []

    for item in action_suggestions["action_suggestion_items"]:
        labels.append(
            {
                "blocked_action_label_id": f"VSABAL-{item['action_suggestion_id'].split('-', 1)[-1]}",
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "blocked_action_label": "BLOCKED_ACTION_PREVIEW_ONLY_NO_EXECUTION",
                "owner_label": "Blocked action — preview only, no approval or execution",
                "metadata_only": True,
                "blocked_action": True,
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
                "action_approved": False,
                "action_executed": False,
                "safe_to_continue_to_gp049": True,
            }
        )

    return {
        "blocked_action_label_items": labels,
        "blocked_action_label_count": len(labels),
        "blocked_action_count": len(labels),
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
        "action_approved_count": 0,
        "action_executed_count": 0,
        "safe_to_continue_blocked_action_labels": True,
    }


def _build_tower_action_authority_gates(action_suggestions: Dict[str, Any]) -> Dict[str, Any]:
    gates = []

    for item in action_suggestions["action_suggestion_items"]:
        for gate in TOWER_ACTION_GATES:
            gates.append(
                {
                    "tower_action_gate_id": f"VSATAG-{item['action_suggestion_id'].split('-', 1)[-1]}-{gate}",
                    "action_suggestion_id": item["action_suggestion_id"],
                    "review_card_id": item["review_card_id"],
                    "audit_event_card_id": item["audit_event_card_id"],
                    "inventory_row_id": item["inventory_row_id"],
                    "scope": item["scope"],
                    "action_type": item["action_type"],
                    "gate_name": gate,
                    "gate_status": "TOWER_ACTION_AUTHORITY_REQUIRED_NOT_GRANTED",
                    "metadata_only": True,
                    "required": True,
                    "granted": False,
                    "vault_can_override": False,
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
                    "safe_to_continue_to_gp049": True,
                }
            )

    return {
        "tower_action_authority_gate_items": gates,
        "tower_action_authority_gate_count": len(gates),
        "gate_type_count": len(TOWER_ACTION_GATES),
        "action_suggestion_count": action_suggestions["action_suggestion_count"],
        "required_count": len(gates),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
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
        "safe_to_continue_tower_action_authority_gates": True,
    }


def _build_reviewer_followup_placeholders(action_suggestions: Dict[str, Any]) -> Dict[str, Any]:
    placeholders = []

    for item in action_suggestions["action_suggestion_items"]:
        for field in REVIEWER_FOLLOWUP_FIELDS:
            placeholders.append(
                {
                    "reviewer_followup_placeholder_id": f"VSARFP-{item['action_suggestion_id'].split('-', 1)[-1]}-{field}",
                    "action_suggestion_id": item["action_suggestion_id"],
                    "review_card_id": item["review_card_id"],
                    "audit_event_card_id": item["audit_event_card_id"],
                    "inventory_row_id": item["inventory_row_id"],
                    "scope": item["scope"],
                    "action_type": item["action_type"],
                    "followup_field": field,
                    "placeholder_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                    "metadata_only": True,
                    "followup_required": True,
                    "followup_present": False,
                    "reviewer_bound": False,
                    "reviewer_confirmed": False,
                    "action_approved": False,
                    "action_executed": False,
                    "action_completed": False,
                    "action_closed": False,
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
                    "safe_to_continue_to_gp049": True,
                }
            )

    return {
        "reviewer_followup_placeholder_items": placeholders,
        "reviewer_followup_placeholder_count": len(placeholders),
        "followup_field_type_count": len(REVIEWER_FOLLOWUP_FIELDS),
        "action_suggestion_count": action_suggestions["action_suggestion_count"],
        "followup_required_count": len(placeholders),
        "followup_present_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "action_approved_count": 0,
        "action_executed_count": 0,
        "action_completed_count": 0,
        "action_closed_count": 0,
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
        "safe_to_continue_reviewer_followup_placeholders": True,
    }


def _build_no_execution_enforcement(action_suggestions: Dict[str, Any]) -> Dict[str, Any]:
    records = []

    for item in action_suggestions["action_suggestion_items"]:
        records.append(
            {
                "no_execution_enforcement_id": f"VSANEE-{item['action_suggestion_id'].split('-', 1)[-1]}",
                "action_suggestion_id": item["action_suggestion_id"],
                "review_card_id": item["review_card_id"],
                "audit_event_card_id": item["audit_event_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "action_type": item["action_type"],
                "enforcement_status": "NO_EXECUTION_ENFORCED",
                "metadata_only": True,
                "no_execution_enforced": True,
                "action_approved": False,
                "action_executed": False,
                "action_completed": False,
                "action_closed": False,
                "audit_review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
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
                "safe_to_continue_to_gp049": True,
            }
        )

    return {
        "no_execution_enforcement_items": records,
        "no_execution_enforcement_count": len(records),
        "no_execution_enforced_count": len(records),
        "action_approved_count": 0,
        "action_executed_count": 0,
        "action_completed_count": 0,
        "action_closed_count": 0,
        "audit_review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
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
        "tower_authority_required_count": len(records),
        "safe_to_continue_no_execution_enforcement": True,
    }


def _build_next_step(
    action_suggestions: Dict[str, Any],
    blocked_action_labels: Dict[str, Any],
    tower_action_authority_gates: Dict[str, Any],
    reviewer_followup_placeholders: Dict[str, Any],
    no_execution_enforcement: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSAAPNX-001",
            "title": "Prepare storage audit action receipt preview",
            "target_pack": "VAULT_GP049",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSAAPNX-002",
            "title": "Keep audit actions suggestion-only",
            "target_pack": "VAULT_GP049",
            "status": "ACTION_SUGGESTIONS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSAAPNX-003",
            "title": "Keep no-execution enforcement active",
            "target_pack": "VAULT_GP049",
            "status": "NO_EXECUTION_ENFORCEMENT_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp049_count": len(items),
        "action_suggestion_count": action_suggestions["action_suggestion_count"],
        "blocked_action_label_count": blocked_action_labels["blocked_action_label_count"],
        "tower_action_authority_gate_count": tower_action_authority_gates["tower_action_authority_gate_count"],
        "reviewer_followup_placeholder_count": reviewer_followup_placeholders["reviewer_followup_placeholder_count"],
        "no_execution_enforcement_count": no_execution_enforcement["no_execution_enforcement_count"],
        "safe_to_continue_to_gp049": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP049",
        "recommended_next_pack_title": "Storage Audit Action Receipt Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep audit action previews metadata-only.",
            "Keep action suggestions suggestion-only and blocked.",
            "Keep no action approval claim.",
            "Keep no action execution claim.",
            "Keep no-execution enforcement active.",
            "Keep Tower action authority gates required and ungranted.",
            "Keep reviewer follow-up placeholders empty and unconfirmed.",
            "Keep no official audit log claim.",
            "Keep no immutable audit write claim.",
            "Keep no Tower attestation write claim.",
            "Keep no finalized or closed receipt claim.",
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
    return deepcopy(get_storage_audit_action_preview_payload())


def get_storage_audit_action_preview_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_truth": payload["action_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "action_routes": payload["action_routes"],
        "action_counts": payload["action_counts"],
        "gp047_connection": payload["gp047_connection"],
    }


def get_storage_audit_action_suggestions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_suggestions": payload["action_suggestions"],
    }


def get_storage_audit_blocked_action_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_action_labels": payload["blocked_action_labels"],
    }


def get_storage_tower_action_authority_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_action_authority_gates": payload["tower_action_authority_gates"],
    }


def get_storage_audit_reviewer_followup_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "reviewer_followup_placeholders": payload["reviewer_followup_placeholders"],
    }


def get_storage_audit_no_execution_enforcement() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution_enforcement": payload["no_execution_enforcement"],
    }


def get_storage_audit_action_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp048_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp048_status": payload["gp048_status"],
        "action_truth": payload["action_truth"],
        "action_routes": payload["action_routes"],
        "action_counts": payload["action_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp047_connection": payload["gp047_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_audit_action_preview_page() -> str:
    payload = clone_payload()
    routes = payload["action_routes"]
    counts = payload["action_counts"]
    truth = payload["action_truth"]
    suggestions = payload["action_suggestions"]
    blocked = payload["blocked_action_labels"]
    enforcement = payload["no_execution_enforcement"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_action_card(item) for item in suggestions["action_suggestion_items"][:12])
    blocked_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['action_type'])} · {escape(item['blocked_action_label'])}</span>
          </div>
          <div class="pill danger">Blocked</div>
        </div>
        """
        for item in blocked["blocked_action_label_items"][:12]
    )

    enforcement_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['action_type'])} · {escape(item['enforcement_status'])}</span>
          </div>
          <div class="pill danger">No execution</div>
        </div>
        """
        for item in enforcement["no_execution_enforcement_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Audit Action Preview · GP048</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 048</div>
        <h1>Storage Audit Action Preview</h1>
        <p class="hero-copy">
          GP048 previews audit action suggestions without approving or executing anything. It adds blocked action labels,
          Tower action authority gates, reviewer follow-up placeholders, and no-execution enforcement.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['action_suggestion_count']}</strong>
            <span>action suggestions</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_action_authority_gate_count']}</strong>
            <span>Tower action gates</span>
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
          <span class="pill ok">Action preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No action approval</span>
          <span class="pill danger">No execution</span>
          <span class="pill danger">No provider access</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Action Suggestion Cards</h2>
      <p>Action cards are suggestion-only. Nothing is approved, executed, exported, delivered, or finalized.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Blocked Action Labels</h2>
        <p>Blocked labels prevent action approval, execution, provider access, object body view, export, delivery, and portals.</p>
        <div>{blocked_rows}</div>
      </div>
      <div>
        <h2>No-Execution Enforcement</h2>
        <p>No-execution records keep every suggested action locked.</p>
        <div>{enforcement_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP049</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP048 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['action_suggestions_route'])}</code>
        <code>{escape(routes['blocked_action_labels_route'])}</code>
        <code>{escape(routes['tower_action_authority_gates_route'])}</code>
        <code>{escape(routes['reviewer_followup_placeholders_route'])}</code>
        <code>{escape(routes['no_execution_enforcement_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp048_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_action_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['action_suggestion_id'])}</code><br>
              Action: <code>{escape(item['action_type'])}</code><br>
              Status: <code>{escape(item['action_status'])}</code><br>
              Approved: <code>{str(item['action_approved']).lower()}</code><br>
              Executed: <code>{str(item['action_executed']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Blocked</span>
        </div>
      </article>
    """
