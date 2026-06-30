"""
VAULT GIANT PACK 046 — Storage Audit Trail Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP045 by creating metadata-only audit trail previews for the
storage/access/receipt layer.

Purpose:
- Build audit event cards.
- Add denied-access audit rows.
- Add Tower gate audit snapshots.
- Add receipt-preview audit links.
- Add immutable-log placeholders.
- Carry forward to GP047.

Important truth:
- GP046 previews audit trail records only.
- GP046 does not write an official audit log.
- GP046 does not write immutable audit entries.
- GP046 does not create official receipts.
- GP046 does not finalize receipts.
- GP046 does not close receipts.
- GP046 does not approve access.
- GP046 does not grant access.
- GP046 does not read provider objects.
- GP046 does not write provider objects.
- GP046 does not show object bodies.
- GP046 does not store raw files.
- GP046 does not unlock direct upload.
- GP046 does not select or configure a provider.
- GP046 does not verify checksums/hashes.
- GP046 does not export or externally deliver anything.
- GP046 does not create public proof.
- GP046 does not open portals.
- GP046 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP046 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization,
  receipt authority, audit authority, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_access_receipt_preview_service import get_storage_access_receipt_preview_payload


PACK_ID = "VAULT_GP046"
PACK_NAME = "Storage Audit Trail Preview"
SCHEMA_VERSION = "vault.storage_audit_trail_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

AUDIT_EVENT_TYPES = [
    "receipt_preview_created",
    "no_grant_receipt_seen",
    "tower_requirement_missing",
    "owner_review_missing",
    "denial_summary_active",
]

IMMUTABLE_PLACEHOLDER_TYPES = [
    "audit_chain_placeholder",
    "hash_chain_placeholder",
    "timestamp_anchor_placeholder",
    "tower_attestation_placeholder",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_audit_trail_preview_payload() -> Dict[str, Any]:
    gp045 = get_storage_access_receipt_preview_payload()

    audit_event_cards = _build_audit_event_cards(gp045)
    denied_access_audit_rows = _build_denied_access_audit_rows(gp045)
    tower_gate_audit_snapshots = _build_tower_gate_audit_snapshots(gp045)
    receipt_preview_audit_links = _build_receipt_preview_audit_links(gp045)
    immutable_log_placeholders = _build_immutable_log_placeholders(audit_event_cards)
    next_step = _build_next_step(
        audit_event_cards,
        denied_access_audit_rows,
        tower_gate_audit_snapshots,
        receipt_preview_audit_links,
        immutable_log_placeholders,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_audit_trail_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "audit_truth": {
            "storage_audit_trail_preview_ready": True,
            "audit_event_cards_visible": True,
            "denied_access_audit_rows_visible": True,
            "tower_gate_audit_snapshots_visible": True,
            "receipt_preview_audit_links_visible": True,
            "immutable_log_placeholders_visible": True,
            "metadata_only": True,
            "private_preview_only": True,
            "audit_event_preview_created_count": audit_event_cards["audit_event_card_count"],
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
            "access_denied_by_default_count": gp045["receipt_counts"]["receipt_card_count"],
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
            "safe_to_continue_to_gp047": True,
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
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
            "vault_can_finalize_storage_access_receipt": False,
            "vault_can_write_official_audit_log": False,
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
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "audit_routes": {
            "room_title": "Vault Storage Audit Trail Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-audit-trail-preview",
            "json_route": "/vault/storage-audit-trail-preview.json",
            "audit_event_cards_route": "/vault/storage-audit-event-cards.json",
            "denied_access_audit_rows_route": "/vault/storage-denied-access-audit-rows.json",
            "tower_gate_audit_snapshots_route": "/vault/storage-tower-gate-audit-snapshots.json",
            "receipt_preview_audit_links_route": "/vault/storage-receipt-preview-audit-links.json",
            "immutable_log_placeholders_route": "/vault/storage-immutable-log-placeholders.json",
            "next_step_route": "/vault/storage-audit-trail-next-step.json",
            "gp046_status_route": "/vault/gp046-status.json",
        },
        "audit_counts": {
            "audit_event_card_count": audit_event_cards["audit_event_card_count"],
            "audit_event_type_count": audit_event_cards["audit_event_type_count"],
            "denied_access_audit_row_count": denied_access_audit_rows["denied_access_audit_row_count"],
            "tower_gate_audit_snapshot_count": tower_gate_audit_snapshots["tower_gate_audit_snapshot_count"],
            "receipt_preview_audit_link_count": receipt_preview_audit_links["receipt_preview_audit_link_count"],
            "immutable_log_placeholder_count": immutable_log_placeholders["immutable_log_placeholder_count"],
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
        "audit_event_cards": audit_event_cards,
        "denied_access_audit_rows": denied_access_audit_rows,
        "tower_gate_audit_snapshots": tower_gate_audit_snapshots,
        "receipt_preview_audit_links": receipt_preview_audit_links,
        "immutable_log_placeholders": immutable_log_placeholders,
        "next_step": next_step,
        "gp045_connection": {
            "gp045_pack_id": gp045["pack"]["id"],
            "gp045_ready": gp045["gp045_status"]["ready"],
            "gp045_safe_to_continue": gp045["gp045_status"]["safe_to_continue_to_gp046"],
            "gp045_vault_done": gp045["gp045_status"]["vault_done"],
            "gp045_section": gp045["pack"]["section"],
            "gp045_receipt_card_count": gp045["receipt_counts"]["receipt_card_count"],
            "gp045_tower_requirement_receipt_count": gp045["receipt_counts"]["tower_requirement_receipt_count"],
            "gp045_owner_review_receipt_placeholder_count": gp045["receipt_counts"]["owner_review_receipt_placeholder_count"],
            "gp045_denial_receipt_summary_count": gp045["receipt_counts"]["denial_receipt_summary_count"],
            "gp045_official_receipt_claimed_count": gp045["receipt_counts"]["official_receipt_claimed_count"],
        },
        "gp046_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_audit_trail_preview_ready": True,
            "safe_to_continue_to_gp047": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_audit_preview": True,
            "private_preview_only": True,
            "audit_event_cards_ready": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp046",
            "next_pack": "VAULT_GP047_STORAGE_AUDIT_REVIEW_BOARD",
        },
    }

    return payload


def _build_audit_event_cards(gp045: Dict[str, Any]) -> Dict[str, Any]:
    receipt_items = gp045["receipt_cards"]["receipt_card_items"]

    cards = []
    for index, item in enumerate(receipt_items, start=1):
        cards.append(
            {
                "audit_event_card_id": f"VSAE-{index:03d}",
                "receipt_card_id": item["receipt_card_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "audit_event_status": "PREVIEW_ONLY_NOT_OFFICIAL_NOT_IMMUTABLE",
                "audit_owner_label": "Audit preview only — no official immutable log written",
                "metadata_only": True,
                "private_preview_only": True,
                "audit_preview_created": True,
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
                "safe_to_continue_to_gp047": True,
            }
        )

    return {
        "audit_event_card_items": cards,
        "audit_event_card_count": len(cards),
        "audit_event_type_count": len(AUDIT_EVENT_TYPES),
        "audit_preview_created_count": len(cards),
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
        "safe_to_continue_audit_event_cards": True,
    }


def _build_denied_access_audit_rows(gp045: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp045["denial_receipt_summaries"]["denial_receipt_summary_items"]

    rows = []
    for item in source_items:
        rows.append(
            {
                "denied_access_audit_row_id": f"VSADAR-{item['denial_receipt_summary_id'].split('-', 1)[-1]}",
                "denial_receipt_summary_id": item["denial_receipt_summary_id"],
                "denial_reason_label_id": item["denial_reason_label_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "denial_reason": item["denial_reason"],
                "audit_row_status": "DENIED_ACCESS_AUDIT_PREVIEW_ONLY",
                "metadata_only": True,
                "denied_by_default": True,
                "access_granted": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "portal_access_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp047": True,
            }
        )

    return {
        "denied_access_audit_row_items": rows,
        "denied_access_audit_row_count": len(rows),
        "denied_by_default_count": len(rows),
        "access_granted_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_denied_access_audit_rows": True,
    }


def _build_tower_gate_audit_snapshots(gp045: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp045["tower_requirement_receipts"]["tower_requirement_receipt_items"]

    snapshots = []
    for item in source_items:
        snapshots.append(
            {
                "tower_gate_audit_snapshot_id": f"VSATGAS-{item['tower_requirement_receipt_id'].split('-', 1)[-1]}",
                "tower_requirement_receipt_id": item["tower_requirement_receipt_id"],
                "tower_requirement_id": item["tower_requirement_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "requirement_name": item["requirement_name"],
                "audit_snapshot_status": "TOWER_REQUIREMENT_REQUIRED_NOT_GRANTED_AUDIT_PREVIEW",
                "metadata_only": True,
                "required": True,
                "granted": False,
                "audit_snapshot_created": True,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "tower_attestation_written": False,
                "vault_can_override": False,
                "decision_approved": False,
                "decision_granted": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "safe_to_continue_to_gp047": True,
            }
        )

    return {
        "tower_gate_audit_snapshot_items": snapshots,
        "tower_gate_audit_snapshot_count": len(snapshots),
        "audit_snapshot_created_count": len(snapshots),
        "required_count": len(snapshots),
        "granted_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "tower_attestation_written_count": 0,
        "vault_override_allowed_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "safe_to_continue_tower_gate_audit_snapshots": True,
    }


def _build_receipt_preview_audit_links(gp045: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp045["receipt_cards"]["receipt_card_items"]

    links = []
    for item in source_items:
        links.append(
            {
                "receipt_preview_audit_link_id": f"VSARPAL-{item['receipt_card_id'].split('-')[-1]}",
                "receipt_card_id": item["receipt_card_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "audit_link_status": "LINKED_TO_PREVIEW_ONLY_RECEIPT",
                "metadata_only": True,
                "receipt_preview_linked": True,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "official_audit_log_written": False,
                "immutable_audit_written": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "safe_to_continue_to_gp047": True,
            }
        )

    return {
        "receipt_preview_audit_link_items": links,
        "receipt_preview_audit_link_count": len(links),
        "receipt_preview_linked_count": len(links),
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "safe_to_continue_receipt_preview_audit_links": True,
    }


def _build_immutable_log_placeholders(audit_event_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in audit_event_cards["audit_event_card_items"]:
        for placeholder_type in IMMUTABLE_PLACEHOLDER_TYPES:
            items.append(
                {
                    "immutable_log_placeholder_id": f"VSAILP-{card['audit_event_card_id'].split('-')[-1]}-{placeholder_type}",
                    "audit_event_card_id": card["audit_event_card_id"],
                    "receipt_card_id": card["receipt_card_id"],
                    "decision_card_id": card["decision_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "placeholder_type": placeholder_type,
                    "placeholder_status": "PLACEHOLDER_ONLY_NOT_WRITTEN",
                    "metadata_only": True,
                    "immutable_log_placeholder_created": True,
                    "official_audit_log_written": False,
                    "immutable_audit_written": False,
                    "immutable_hash_chain_written": False,
                    "timestamp_anchor_written": False,
                    "tower_attestation_written": False,
                    "official_receipt_claimed": False,
                    "receipt_finalized": False,
                    "receipt_closed": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "external_delivery_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp047": True,
                }
            )

    return {
        "immutable_log_placeholder_items": items,
        "immutable_log_placeholder_count": len(items),
        "placeholder_type_count": len(IMMUTABLE_PLACEHOLDER_TYPES),
        "audit_event_card_count": audit_event_cards["audit_event_card_count"],
        "immutable_log_placeholder_created_count": len(items),
        "official_audit_log_written_count": 0,
        "immutable_audit_written_count": 0,
        "immutable_hash_chain_written_count": 0,
        "timestamp_anchor_written_count": 0,
        "tower_attestation_written_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_immutable_log_placeholders": True,
    }


def _build_next_step(
    audit_event_cards: Dict[str, Any],
    denied_access_audit_rows: Dict[str, Any],
    tower_gate_audit_snapshots: Dict[str, Any],
    receipt_preview_audit_links: Dict[str, Any],
    immutable_log_placeholders: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSATPNX-001",
            "title": "Prepare storage audit review board",
            "target_pack": "VAULT_GP047",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSATPNX-002",
            "title": "Keep audit trail preview-only",
            "target_pack": "VAULT_GP047",
            "status": "PREVIEW_ONLY_AUDIT_TRAIL_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSATPNX-003",
            "title": "Keep no official immutable audit write",
            "target_pack": "VAULT_GP047",
            "status": "NO_OFFICIAL_IMMUTABLE_AUDIT_WRITE",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp047_count": len(items),
        "audit_event_card_count": audit_event_cards["audit_event_card_count"],
        "denied_access_audit_row_count": denied_access_audit_rows["denied_access_audit_row_count"],
        "tower_gate_audit_snapshot_count": tower_gate_audit_snapshots["tower_gate_audit_snapshot_count"],
        "receipt_preview_audit_link_count": receipt_preview_audit_links["receipt_preview_audit_link_count"],
        "immutable_log_placeholder_count": immutable_log_placeholders["immutable_log_placeholder_count"],
        "safe_to_continue_to_gp047": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP047",
        "recommended_next_pack_title": "Storage Audit Review Board",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep audit trail previews metadata-only.",
            "Keep audit records preview-only, not official.",
            "Keep no immutable audit write claim.",
            "Keep no official audit log claim.",
            "Keep no finalized or closed receipt claim.",
            "Keep receipt previews metadata-only and not official.",
            "Keep denied-access audit rows active.",
            "Keep Tower gate audit snapshots required and ungranted.",
            "Keep immutable-log placeholders unwritten.",
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
    return deepcopy(get_storage_audit_trail_preview_payload())


def get_storage_audit_trail_preview_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "audit_truth": payload["audit_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "audit_routes": payload["audit_routes"],
        "audit_counts": payload["audit_counts"],
        "gp045_connection": payload["gp045_connection"],
    }


def get_storage_audit_event_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "audit_event_cards": payload["audit_event_cards"],
    }


def get_storage_denied_access_audit_rows() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "denied_access_audit_rows": payload["denied_access_audit_rows"],
    }


def get_storage_tower_gate_audit_snapshots() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gate_audit_snapshots": payload["tower_gate_audit_snapshots"],
    }


def get_storage_receipt_preview_audit_links() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_preview_audit_links": payload["receipt_preview_audit_links"],
    }


def get_storage_immutable_log_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "immutable_log_placeholders": payload["immutable_log_placeholders"],
    }


def get_storage_audit_trail_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp046_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp046_status": payload["gp046_status"],
        "audit_truth": payload["audit_truth"],
        "audit_routes": payload["audit_routes"],
        "audit_counts": payload["audit_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp045_connection": payload["gp045_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_audit_trail_preview_page() -> str:
    payload = clone_payload()
    routes = payload["audit_routes"]
    counts = payload["audit_counts"]
    truth = payload["audit_truth"]
    cards = payload["audit_event_cards"]
    denied = payload["denied_access_audit_rows"]
    immutable = payload["immutable_log_placeholders"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_audit_card(item) for item in cards["audit_event_card_items"])
    denied_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['denial_reason'])} · {escape(item['audit_row_status'])}</span>
          </div>
          <div class="pill danger">Denied</div>
        </div>
        """
        for item in denied["denied_access_audit_row_items"][:12]
    )

    immutable_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['placeholder_type'])} · {escape(item['placeholder_status'])}</span>
          </div>
          <div class="pill warn">Placeholder</div>
        </div>
        """
        for item in immutable["immutable_log_placeholder_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Audit Trail Preview · GP046</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 046</div>
        <h1>Storage Audit Trail Preview</h1>
        <p class="hero-copy">
          GP046 previews audit trail records without writing an official or immutable audit log. It connects
          denied-access audit rows, Tower gate audit snapshots, receipt-preview links, and immutable-log placeholders.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['audit_event_card_count']}</strong>
            <span>audit event cards</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_gate_audit_snapshot_count']}</strong>
            <span>Tower audit snapshots</span>
          </div>
          <div class="metric">
            <strong>{counts['official_audit_log_written_count']}</strong>
            <span>official audit writes</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Audit preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No official audit log</span>
          <span class="pill danger">No immutable audit write</span>
          <span class="pill danger">No object access</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Audit Event Cards</h2>
      <p>Audit cards are preview-only. Nothing is official, immutable, exported, delivered, approved, or executed.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Denied Access Audit Rows</h2>
        <p>Denied-access rows preserve why access remains blocked.</p>
        <div>{denied_rows}</div>
      </div>
      <div>
        <h2>Immutable Log Placeholders</h2>
        <p>Immutable-log placeholders are not written and do not claim hash-chain proof.</p>
        <div>{immutable_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP047</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP046 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['audit_event_cards_route'])}</code>
        <code>{escape(routes['denied_access_audit_rows_route'])}</code>
        <code>{escape(routes['tower_gate_audit_snapshots_route'])}</code>
        <code>{escape(routes['receipt_preview_audit_links_route'])}</code>
        <code>{escape(routes['immutable_log_placeholders_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp046_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_audit_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['audit_event_card_id'])}</code><br>
              Status: <code>{escape(item['audit_event_status'])}</code><br>
              Official log: <code>{str(item['official_audit_log_written']).lower()}</code><br>
              Immutable write: <code>{str(item['immutable_audit_written']).lower()}</code><br>
              Tower attestation: <code>{str(item['tower_attestation_written']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Preview only</span>
        </div>
      </article>
    """
