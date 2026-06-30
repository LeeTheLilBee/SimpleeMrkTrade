"""
VAULT GIANT PACK 047 — Storage Audit Review Board

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP046 by creating a metadata-only review board for audit trail previews.

Purpose:
- Build audit review board cards.
- Add audit review focus lanes.
- Add unresolved issue labels.
- Add Tower audit authority checks.
- Add reviewer note placeholders.
- Carry forward to GP048.

Important truth:
- GP047 creates a review board only.
- GP047 does not approve audit review.
- GP047 does not write an official audit log.
- GP047 does not write immutable audit entries.
- GP047 does not create official receipts.
- GP047 does not finalize receipts.
- GP047 does not close receipts.
- GP047 does not approve access.
- GP047 does not grant access.
- GP047 does not read provider objects.
- GP047 does not write provider objects.
- GP047 does not show object bodies.
- GP047 does not store raw files.
- GP047 does not unlock direct upload.
- GP047 does not select or configure a provider.
- GP047 does not verify checksums/hashes.
- GP047 does not export or externally deliver anything.
- GP047 does not create public proof.
- GP047 does not open portals.
- GP047 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP047 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization,
  receipt authority, audit authority, review authority, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_audit_trail_preview_service import get_storage_audit_trail_preview_payload


PACK_ID = "VAULT_GP047"
PACK_NAME = "Storage Audit Review Board"
SCHEMA_VERSION = "vault.storage_audit_review_board.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

REVIEW_FOCUS_LANES = [
    "denied_access_review",
    "tower_gate_review",
    "receipt_preview_review",
    "immutable_placeholder_review",
    "provider_lock_review",
]

UNRESOLVED_ISSUE_TYPES = [
    "official_audit_log_not_written",
    "immutable_audit_not_written",
    "tower_attestation_not_written",
    "official_receipt_not_claimed",
    "receipt_not_finalized",
    "access_not_granted",
    "provider_read_locked",
    "object_body_view_locked",
]

REVIEWER_NOTE_FIELDS = [
    "reviewer_observation",
    "risk_note",
    "tower_followup_note",
    "owner_summary_note",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_audit_review_board_payload() -> Dict[str, Any]:
    gp046 = get_storage_audit_trail_preview_payload()

    review_cards = _build_review_cards(gp046)
    focus_lanes = _build_focus_lanes(review_cards)
    unresolved_issue_labels = _build_unresolved_issue_labels(review_cards)
    tower_authority_checks = _build_tower_authority_checks(gp046)
    reviewer_note_placeholders = _build_reviewer_note_placeholders(review_cards)
    next_step = _build_next_step(
        review_cards,
        focus_lanes,
        unresolved_issue_labels,
        tower_authority_checks,
        reviewer_note_placeholders,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_audit_review_board",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "review_truth": {
            "storage_audit_review_board_ready": True,
            "review_cards_visible": True,
            "focus_lanes_visible": True,
            "unresolved_issue_labels_visible": True,
            "tower_audit_authority_checks_visible": True,
            "reviewer_note_placeholders_visible": True,
            "metadata_only": True,
            "private_review_only": True,
            "audit_review_card_count": review_cards["review_card_count"],
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
            "access_denied_by_default_count": review_cards["review_card_count"],
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
            "safe_to_continue_to_gp048": True,
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
            "tower_owns_object_visibility": True,
            "tower_owns_storage_access_authorization": True,
            "tower_owns_access_decision_approval": True,
            "tower_owns_receipt_authority": True,
            "tower_owns_audit_authority": True,
            "tower_owns_audit_review_authority": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
            "vault_can_finalize_storage_access_receipt": False,
            "vault_can_write_official_audit_log": False,
            "vault_can_approve_audit_review": False,
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
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "review_routes": {
            "room_title": "Vault Storage Audit Review Board",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-audit-review-board",
            "json_route": "/vault/storage-audit-review-board.json",
            "review_cards_route": "/vault/storage-audit-review-cards.json",
            "focus_lanes_route": "/vault/storage-audit-review-focus-lanes.json",
            "unresolved_issue_labels_route": "/vault/storage-audit-unresolved-issue-labels.json",
            "tower_authority_checks_route": "/vault/storage-tower-audit-authority-checks.json",
            "reviewer_note_placeholders_route": "/vault/storage-audit-reviewer-note-placeholders.json",
            "next_step_route": "/vault/storage-audit-review-next-step.json",
            "gp047_status_route": "/vault/gp047-status.json",
        },
        "review_counts": {
            "review_card_count": review_cards["review_card_count"],
            "focus_lane_count": focus_lanes["focus_lane_count"],
            "unresolved_issue_label_count": unresolved_issue_labels["unresolved_issue_label_count"],
            "tower_authority_check_count": tower_authority_checks["tower_authority_check_count"],
            "reviewer_note_placeholder_count": reviewer_note_placeholders["reviewer_note_placeholder_count"],
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
        "review_cards": review_cards,
        "focus_lanes": focus_lanes,
        "unresolved_issue_labels": unresolved_issue_labels,
        "tower_authority_checks": tower_authority_checks,
        "reviewer_note_placeholders": reviewer_note_placeholders,
        "next_step": next_step,
        "gp046_connection": {
            "gp046_pack_id": gp046["pack"]["id"],
            "gp046_ready": gp046["gp046_status"]["ready"],
            "gp046_safe_to_continue": gp046["gp046_status"]["safe_to_continue_to_gp047"],
            "gp046_vault_done": gp046["gp046_status"]["vault_done"],
            "gp046_section": gp046["pack"]["section"],
            "gp046_audit_event_card_count": gp046["audit_counts"]["audit_event_card_count"],
            "gp046_denied_access_audit_row_count": gp046["audit_counts"]["denied_access_audit_row_count"],
            "gp046_tower_gate_audit_snapshot_count": gp046["audit_counts"]["tower_gate_audit_snapshot_count"],
            "gp046_receipt_preview_audit_link_count": gp046["audit_counts"]["receipt_preview_audit_link_count"],
            "gp046_immutable_log_placeholder_count": gp046["audit_counts"]["immutable_log_placeholder_count"],
            "gp046_official_audit_log_written_count": gp046["audit_counts"]["official_audit_log_written_count"],
        },
        "gp047_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_audit_review_board_ready": True,
            "safe_to_continue_to_gp048": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_review_board": True,
            "private_review_only": True,
            "review_cards_ready": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp047",
            "next_pack": "VAULT_GP048_STORAGE_AUDIT_ACTION_PREVIEW",
        },
    }

    return payload


def _build_review_cards(gp046: Dict[str, Any]) -> Dict[str, Any]:
    audit_items = gp046["audit_event_cards"]["audit_event_card_items"]

    cards = []
    for index, item in enumerate(audit_items, start=1):
        cards.append(
            {
                "review_card_id": f"VSARB-{index:03d}",
                "audit_event_card_id": item["audit_event_card_id"],
                "receipt_card_id": item["receipt_card_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "review_status": "REVIEW_BOARD_PREVIEW_ONLY_UNAPPROVED_UNCLOSED",
                "review_owner_label": "Audit review preview — unresolved and unapproved",
                "metadata_only": True,
                "private_review_only": True,
                "review_card_created": True,
                "review_approved": False,
                "review_completed": False,
                "review_closed": False,
                "reviewer_note_required": True,
                "reviewer_note_present": False,
                "unresolved_issues_active": True,
                "tower_audit_authority_required": True,
                "tower_audit_authority_granted": False,
                "official_audit_log_created": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "immutable_hash_chain_written": False,
                "tower_attestation_written": False,
                "receipt_preview_linked": True,
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
                "safe_to_continue_to_gp048": True,
            }
        )

    return {
        "review_card_items": cards,
        "review_card_count": len(cards),
        "review_card_created_count": len(cards),
        "review_approved_count": 0,
        "review_completed_count": 0,
        "review_closed_count": 0,
        "reviewer_note_required_count": len(cards),
        "reviewer_note_present_count": 0,
        "unresolved_issues_active_count": len(cards),
        "tower_audit_authority_required_count": len(cards),
        "tower_audit_authority_granted_count": 0,
        "official_audit_log_created_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "immutable_hash_chain_written_count": 0,
        "tower_attestation_written_count": 0,
        "receipt_preview_linked_count": len(cards),
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
        "safe_to_continue_review_cards": True,
    }


def _build_focus_lanes(review_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in review_cards["review_card_items"]:
        for lane in REVIEW_FOCUS_LANES:
            items.append(
                {
                    "focus_lane_id": f"VSARFL-{card['review_card_id'].split('-')[-1]}-{lane}",
                    "review_card_id": card["review_card_id"],
                    "audit_event_card_id": card["audit_event_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "focus_lane": lane,
                    "focus_status": "OPEN_REVIEW_FOCUS_METADATA_ONLY",
                    "metadata_only": True,
                    "focus_lane_open": True,
                    "focus_lane_completed": False,
                    "review_approved": False,
                    "official_audit_log_written": False,
                    "immutable_audit_written": False,
                    "tower_attestation_written": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "external_delivery_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp048": True,
                }
            )

    return {
        "focus_lane_items": items,
        "focus_lane_count": len(items),
        "focus_lane_type_count": len(REVIEW_FOCUS_LANES),
        "review_card_count": review_cards["review_card_count"],
        "focus_lane_open_count": len(items),
        "focus_lane_completed_count": 0,
        "review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_focus_lanes": True,
    }


def _build_unresolved_issue_labels(review_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in review_cards["review_card_items"]:
        for issue in UNRESOLVED_ISSUE_TYPES:
            items.append(
                {
                    "unresolved_issue_label_id": f"VSAUIL-{card['review_card_id'].split('-')[-1]}-{issue}",
                    "review_card_id": card["review_card_id"],
                    "audit_event_card_id": card["audit_event_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "issue_type": issue,
                    "issue_status": "ACTIVE_UNRESOLVED_REVIEW_ISSUE",
                    "metadata_only": True,
                    "unresolved": True,
                    "blocks_review_approval": True,
                    "blocks_review_close": True,
                    "blocks_official_audit_log": True,
                    "blocks_immutable_audit_write": True,
                    "blocks_tower_attestation": True,
                    "blocks_access_grant": True,
                    "blocks_provider_read": True,
                    "blocks_object_body_view": True,
                    "blocks_export": True,
                    "blocks_external_delivery": True,
                    "blocks_execution": True,
                    "owner_resolvable_now": False,
                    "tower_authority_required": True,
                    "safe_to_continue_to_gp048": True,
                }
            )

    return {
        "unresolved_issue_label_items": items,
        "unresolved_issue_label_count": len(items),
        "unresolved_issue_type_count": len(UNRESOLVED_ISSUE_TYPES),
        "review_card_count": review_cards["review_card_count"],
        "unresolved_count": len(items),
        "blocks_review_approval_count": len(items),
        "blocks_review_close_count": len(items),
        "blocks_official_audit_log_count": len(items),
        "blocks_immutable_audit_write_count": len(items),
        "blocks_tower_attestation_count": len(items),
        "blocks_access_grant_count": len(items),
        "blocks_provider_read_count": len(items),
        "blocks_object_body_view_count": len(items),
        "blocks_export_count": len(items),
        "blocks_external_delivery_count": len(items),
        "blocks_execution_count": len(items),
        "owner_resolvable_now_count": 0,
        "tower_authority_required_count": len(items),
        "safe_to_continue_unresolved_issue_labels": True,
    }


def _build_tower_authority_checks(gp046: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp046["tower_gate_audit_snapshots"]["tower_gate_audit_snapshot_items"]

    checks = []
    for item in source_items:
        checks.append(
            {
                "tower_authority_check_id": f"VSATAC-{item['tower_gate_audit_snapshot_id'].split('-', 1)[-1]}",
                "tower_gate_audit_snapshot_id": item["tower_gate_audit_snapshot_id"],
                "tower_requirement_receipt_id": item["tower_requirement_receipt_id"],
                "tower_requirement_id": item["tower_requirement_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "requirement_name": item["requirement_name"],
                "authority_check_status": "TOWER_AUDIT_AUTHORITY_REQUIRED_NOT_GRANTED",
                "metadata_only": True,
                "tower_audit_authority_required": True,
                "tower_audit_authority_granted": False,
                "vault_can_override": False,
                "review_approved": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "decision_approved": False,
                "decision_granted": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "safe_to_continue_to_gp048": True,
            }
        )

    return {
        "tower_authority_check_items": checks,
        "tower_authority_check_count": len(checks),
        "tower_audit_authority_required_count": len(checks),
        "tower_audit_authority_granted_count": 0,
        "vault_override_allowed_count": 0,
        "review_approved_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "safe_to_continue_tower_authority_checks": True,
    }


def _build_reviewer_note_placeholders(review_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in review_cards["review_card_items"]:
        for field in REVIEWER_NOTE_FIELDS:
            items.append(
                {
                    "reviewer_note_placeholder_id": f"VSARNP-{card['review_card_id'].split('-')[-1]}-{field}",
                    "review_card_id": card["review_card_id"],
                    "audit_event_card_id": card["audit_event_card_id"],
                    "receipt_card_id": card["receipt_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "note_field": field,
                    "placeholder_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                    "metadata_only": True,
                    "note_required": True,
                    "note_present": False,
                    "reviewer_bound": False,
                    "reviewer_confirmed": False,
                    "review_approved": False,
                    "review_completed": False,
                    "review_closed": False,
                    "official_audit_log_written": False,
                    "immutable_audit_written": False,
                    "tower_attestation_written": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "external_delivery_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp048": True,
                }
            )

    return {
        "reviewer_note_placeholder_items": items,
        "reviewer_note_placeholder_count": len(items),
        "reviewer_note_field_type_count": len(REVIEWER_NOTE_FIELDS),
        "review_card_count": review_cards["review_card_count"],
        "note_required_count": len(items),
        "note_present_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "review_approved_count": 0,
        "review_completed_count": 0,
        "review_closed_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_reviewer_note_placeholders": True,
    }


def _build_next_step(
    review_cards: Dict[str, Any],
    focus_lanes: Dict[str, Any],
    unresolved_issue_labels: Dict[str, Any],
    tower_authority_checks: Dict[str, Any],
    reviewer_note_placeholders: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSARBNX-001",
            "title": "Prepare storage audit action preview",
            "target_pack": "VAULT_GP048",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARBNX-002",
            "title": "Keep audit review board metadata-only",
            "target_pack": "VAULT_GP048",
            "status": "METADATA_ONLY_REVIEW_BOARD_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARBNX-003",
            "title": "Keep unresolved review issues active",
            "target_pack": "VAULT_GP048",
            "status": "UNRESOLVED_ISSUES_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp048_count": len(items),
        "review_card_count": review_cards["review_card_count"],
        "focus_lane_count": focus_lanes["focus_lane_count"],
        "unresolved_issue_label_count": unresolved_issue_labels["unresolved_issue_label_count"],
        "tower_authority_check_count": tower_authority_checks["tower_authority_check_count"],
        "reviewer_note_placeholder_count": reviewer_note_placeholders["reviewer_note_placeholder_count"],
        "safe_to_continue_to_gp048": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP048",
        "recommended_next_pack_title": "Storage Audit Action Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep audit review board metadata-only.",
            "Keep audit review unapproved, incomplete, and unclosed.",
            "Keep unresolved review issues active.",
            "Keep Tower audit authority checks required and ungranted.",
            "Keep reviewer note placeholders empty and unconfirmed.",
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
    return deepcopy(get_storage_audit_review_board_payload())


def get_storage_audit_review_board_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_truth": payload["review_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "review_routes": payload["review_routes"],
        "review_counts": payload["review_counts"],
        "gp046_connection": payload["gp046_connection"],
    }


def get_storage_audit_review_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_cards": payload["review_cards"],
    }


def get_storage_audit_review_focus_lanes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "focus_lanes": payload["focus_lanes"],
    }


def get_storage_audit_unresolved_issue_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "unresolved_issue_labels": payload["unresolved_issue_labels"],
    }


def get_storage_tower_audit_authority_checks() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_authority_checks": payload["tower_authority_checks"],
    }


def get_storage_audit_reviewer_note_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "reviewer_note_placeholders": payload["reviewer_note_placeholders"],
    }


def get_storage_audit_review_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp047_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp047_status": payload["gp047_status"],
        "review_truth": payload["review_truth"],
        "review_routes": payload["review_routes"],
        "review_counts": payload["review_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp046_connection": payload["gp046_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_audit_review_board_page() -> str:
    payload = clone_payload()
    routes = payload["review_routes"]
    counts = payload["review_counts"]
    truth = payload["review_truth"]
    cards = payload["review_cards"]
    issues = payload["unresolved_issue_labels"]
    notes = payload["reviewer_note_placeholders"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_review_card(item) for item in cards["review_card_items"])
    issue_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['issue_type'])} · {escape(item['issue_status'])}</span>
          </div>
          <div class="pill danger">Unresolved</div>
        </div>
        """
        for item in issues["unresolved_issue_label_items"][:12]
    )

    note_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['note_field'])} · {escape(item['placeholder_status'])}</span>
          </div>
          <div class="pill warn">Empty</div>
        </div>
        """
        for item in notes["reviewer_note_placeholder_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Audit Review Board · GP047</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 047</div>
        <h1>Storage Audit Review Board</h1>
        <p class="hero-copy">
          GP047 reviews the storage audit trail previews without approving, closing, or writing official logs.
          It organizes review cards, focus lanes, unresolved issues, Tower audit authority checks, and reviewer notes.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['review_card_count']}</strong>
            <span>review cards</span>
          </div>
          <div class="metric">
            <strong>{counts['unresolved_issue_label_count']}</strong>
            <span>unresolved issues</span>
          </div>
          <div class="metric">
            <strong>{counts['audit_review_approved_count']}</strong>
            <span>review approvals</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Review board ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No review approval</span>
          <span class="pill danger">No official audit log</span>
          <span class="pill danger">No immutable write</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Audit Review Cards</h2>
      <p>Review cards are metadata-only. Nothing is approved, closed, official, immutable, exported, delivered, or executed.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Unresolved Issue Labels</h2>
        <p>Unresolved labels block review approval, official audit logs, immutable writes, grants, object access, export, and execution.</p>
        <div>{issue_rows}</div>
      </div>
      <div>
        <h2>Reviewer Note Placeholders</h2>
        <p>Reviewer notes are placeholders only and remain empty/unconfirmed.</p>
        <div>{note_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP048</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP047 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['review_cards_route'])}</code>
        <code>{escape(routes['focus_lanes_route'])}</code>
        <code>{escape(routes['unresolved_issue_labels_route'])}</code>
        <code>{escape(routes['tower_authority_checks_route'])}</code>
        <code>{escape(routes['reviewer_note_placeholders_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp047_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_review_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['review_card_id'])}</code><br>
              Status: <code>{escape(item['review_status'])}</code><br>
              Approved: <code>{str(item['review_approved']).lower()}</code><br>
              Closed: <code>{str(item['review_closed']).lower()}</code><br>
              Official log: <code>{str(item['official_audit_log_written']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Unresolved</span>
        </div>
      </article>
    """
