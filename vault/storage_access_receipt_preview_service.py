"""
VAULT GIANT PACK 045 — Storage Access Receipt Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP044 by creating metadata-only receipt previews for storage access decisions.

Purpose:
- Build access receipt preview cards.
- Add no-grant receipt labels.
- Add Tower requirement receipt snapshots.
- Add owner review receipt placeholders.
- Add denial receipt summaries.
- Carry forward to GP046.

Important truth:
- GP045 previews receipts only.
- GP045 does not create official receipts.
- GP045 does not finalize receipts.
- GP045 does not close receipts.
- GP045 does not approve access.
- GP045 does not grant access.
- GP045 does not submit access requests.
- GP045 does not read provider objects.
- GP045 does not write provider objects.
- GP045 does not show object bodies.
- GP045 does not store raw files.
- GP045 does not unlock direct upload.
- GP045 does not select or configure a provider.
- GP045 does not verify checksums/hashes.
- GP045 does not export or externally deliver anything.
- GP045 does not create public proof.
- GP045 does not open portals.
- GP045 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP045 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization,
  receipt authority, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_access_decision_queue_service import get_storage_access_decision_queue_payload


PACK_ID = "VAULT_GP045"
PACK_NAME = "Storage Access Receipt Preview"
SCHEMA_VERSION = "vault.storage_access_receipt_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

RECEIPT_PREVIEW_TYPES = [
    "access_denied_by_default_preview",
    "tower_requirements_missing_preview",
    "owner_review_missing_preview",
    "no_grant_enforcement_preview",
]

RECEIPT_LOCK_REASONS = [
    "not_official_receipt",
    "not_finalized",
    "not_closed",
    "no_access_grant",
    "no_tower_approval",
    "no_owner_confirmation",
    "no_provider_read",
    "no_object_body_view",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_access_receipt_preview_payload() -> Dict[str, Any]:
    gp044 = get_storage_access_decision_queue_payload()

    receipt_cards = _build_receipt_cards(gp044)
    no_grant_receipt_labels = _build_no_grant_receipt_labels(receipt_cards)
    tower_requirement_receipts = _build_tower_requirement_receipts(gp044)
    owner_review_receipts = _build_owner_review_receipts(gp044)
    denial_receipt_summaries = _build_denial_receipt_summaries(gp044)
    next_step = _build_next_step(
        receipt_cards,
        no_grant_receipt_labels,
        tower_requirement_receipts,
        owner_review_receipts,
        denial_receipt_summaries,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_access_receipt_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "receipt_truth": {
            "storage_access_receipt_preview_ready": True,
            "receipt_preview_cards_visible": True,
            "no_grant_receipt_labels_visible": True,
            "tower_requirement_receipt_snapshots_visible": True,
            "owner_review_receipt_placeholders_visible": True,
            "denial_receipt_summaries_visible": True,
            "metadata_only": True,
            "private_preview_only": True,
            "receipt_preview_created_count": receipt_cards["receipt_card_count"],
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
            "access_denied_by_default_count": receipt_cards["receipt_card_count"],
            "no_grant_receipt_count": no_grant_receipt_labels["no_grant_receipt_label_count"],
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
            "safe_to_continue_to_gp046": True,
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
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
            "vault_can_finalize_storage_access_receipt": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "storage_access_default": "denied_by_default",
            "decision_default": "blocked_denied_by_default",
            "receipt_default": "preview_only_not_official_not_final",
            "external_packet_delivery_allowed": False,
            "packet_export_allowed": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "object_body_preview_allowed": False,
            "object_body_view_allowed": False,
            "provider_read_allowed": False,
            "provider_write_allowed": False,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "receipt_routes": {
            "room_title": "Vault Storage Access Receipt Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-access-receipt-preview",
            "json_route": "/vault/storage-access-receipt-preview.json",
            "receipt_cards_route": "/vault/storage-access-receipt-cards.json",
            "no_grant_receipt_labels_route": "/vault/storage-access-no-grant-receipt-labels.json",
            "tower_requirement_receipts_route": "/vault/storage-access-tower-requirement-receipts.json",
            "owner_review_receipts_route": "/vault/storage-access-owner-review-receipts.json",
            "denial_receipt_summaries_route": "/vault/storage-access-denial-receipt-summaries.json",
            "next_step_route": "/vault/storage-access-receipt-next-step.json",
            "gp045_status_route": "/vault/gp045-status.json",
        },
        "receipt_counts": {
            "receipt_card_count": receipt_cards["receipt_card_count"],
            "receipt_preview_type_count": receipt_cards["receipt_preview_type_count"],
            "no_grant_receipt_label_count": no_grant_receipt_labels["no_grant_receipt_label_count"],
            "tower_requirement_receipt_count": tower_requirement_receipts["tower_requirement_receipt_count"],
            "owner_review_receipt_placeholder_count": owner_review_receipts["owner_review_receipt_placeholder_count"],
            "denial_receipt_summary_count": denial_receipt_summaries["denial_receipt_summary_count"],
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
        "receipt_cards": receipt_cards,
        "no_grant_receipt_labels": no_grant_receipt_labels,
        "tower_requirement_receipts": tower_requirement_receipts,
        "owner_review_receipts": owner_review_receipts,
        "denial_receipt_summaries": denial_receipt_summaries,
        "next_step": next_step,
        "gp044_connection": {
            "gp044_pack_id": gp044["pack"]["id"],
            "gp044_ready": gp044["gp044_status"]["ready"],
            "gp044_safe_to_continue": gp044["gp044_status"]["safe_to_continue_to_gp045"],
            "gp044_vault_done": gp044["gp044_status"]["vault_done"],
            "gp044_section": gp044["pack"]["section"],
            "gp044_decision_card_count": gp044["decision_counts"]["decision_card_count"],
            "gp044_tower_requirement_count": gp044["decision_counts"]["tower_requirement_count"],
            "gp044_owner_review_placeholder_count": gp044["decision_counts"]["owner_review_placeholder_count"],
            "gp044_denial_reason_label_count": gp044["decision_counts"]["denial_reason_label_count"],
            "gp044_no_grant_enforcement_count": gp044["decision_counts"]["no_grant_enforcement_count"],
        },
        "gp045_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_access_receipt_preview_ready": True,
            "safe_to_continue_to_gp046": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_receipt_preview": True,
            "private_preview_only": True,
            "receipt_cards_ready": True,
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
            "no_grant_receipt_enforced": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp045",
            "next_pack": "VAULT_GP046_STORAGE_AUDIT_TRAIL_PREVIEW",
        },
    }

    return payload


def _build_receipt_cards(gp044: Dict[str, Any]) -> Dict[str, Any]:
    decision_items = gp044["decision_cards"]["decision_card_items"]

    cards = []
    for index, item in enumerate(decision_items, start=1):
        cards.append(
            {
                "receipt_card_id": f"VSARP-{index:03d}",
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "receipt_preview_status": "PREVIEW_ONLY_NOT_OFFICIAL_NOT_FINAL",
                "receipt_owner_label": "Receipt preview only — no access granted",
                "metadata_only": True,
                "private_preview_only": True,
                "receipt_preview_created": True,
                "official_receipt_created": False,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "receipt_export_allowed": False,
                "receipt_external_delivery_allowed": False,
                "receipt_public_proof_allowed": False,
                "access_request_submitted": False,
                "access_request_approved": False,
                "access_granted": False,
                "decision_approved": False,
                "decision_granted": False,
                "no_grant_receipt": True,
                "tower_requirements_missing": True,
                "owner_review_missing": True,
                "denial_summary_required": True,
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
                "safe_to_continue_to_gp046": True,
            }
        )

    return {
        "receipt_card_items": cards,
        "receipt_card_count": len(cards),
        "receipt_preview_type_count": len(RECEIPT_PREVIEW_TYPES),
        "receipt_preview_created_count": len(cards),
        "official_receipt_created_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "receipt_export_allowed_count": 0,
        "receipt_external_delivery_allowed_count": 0,
        "receipt_public_proof_allowed_count": 0,
        "access_request_submitted_count": 0,
        "access_request_approved_count": 0,
        "access_granted_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "no_grant_receipt_count": len(cards),
        "tower_requirements_missing_count": len(cards),
        "owner_review_missing_count": len(cards),
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
        "safe_to_continue_receipt_cards": True,
    }


def _build_no_grant_receipt_labels(receipt_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in receipt_cards["receipt_card_items"]:
        items.append(
            {
                "no_grant_receipt_label_id": f"VSANGRL-{card['receipt_card_id'].split('-')[-1]}",
                "receipt_card_id": card["receipt_card_id"],
                "decision_card_id": card["decision_card_id"],
                "access_request_card_id": card["access_request_card_id"],
                "inventory_row_id": card["inventory_row_id"],
                "scope": card["scope"],
                "no_grant_label": "NO_GRANT_RECEIPT_PREVIEW_ONLY",
                "owner_label": "No access granted — receipt preview only",
                "metadata_only": True,
                "no_grant_receipt": True,
                "access_granted": False,
                "decision_granted": False,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "external_delivery_allowed": False,
                "export_allowed": False,
                "portal_access_allowed": False,
                "public_proof_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp046": True,
            }
        )

    return {
        "no_grant_receipt_label_items": items,
        "no_grant_receipt_label_count": len(items),
        "no_grant_receipt_count": len(items),
        "access_granted_count": 0,
        "decision_granted_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_no_grant_receipt_labels": True,
    }


def _build_tower_requirement_receipts(gp044: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp044["tower_requirements"]["tower_requirement_items"]

    items = []
    for item in source_items:
        items.append(
            {
                "tower_requirement_receipt_id": f"VSATRS-{item['tower_requirement_id'].split('-', 1)[-1]}",
                "tower_requirement_id": item["tower_requirement_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "requirement_name": item["requirement_name"],
                "receipt_snapshot_status": "REQUIRED_NOT_GRANTED_SNAPSHOT",
                "metadata_only": True,
                "required": True,
                "granted": False,
                "receipt_snapshot_created": True,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "vault_can_override": False,
                "decision_approved": False,
                "decision_granted": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "export_allowed": False,
                "external_delivery_allowed": False,
                "safe_to_continue_to_gp046": True,
            }
        )

    return {
        "tower_requirement_receipt_items": items,
        "tower_requirement_receipt_count": len(items),
        "receipt_snapshot_created_count": len(items),
        "required_count": len(items),
        "granted_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "vault_override_allowed_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "safe_to_continue_tower_requirement_receipts": True,
    }


def _build_owner_review_receipts(gp044: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp044["owner_review_placeholders"]["owner_review_placeholder_items"]

    items = []
    for item in source_items:
        items.append(
            {
                "owner_review_receipt_placeholder_id": f"VSAORR-{item['owner_review_placeholder_id'].split('-', 1)[-1]}",
                "owner_review_placeholder_id": item["owner_review_placeholder_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "owner_review_field": item["owner_review_field"],
                "receipt_placeholder_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                "metadata_only": True,
                "owner_review_required": True,
                "owner_reviewed": False,
                "owner_confirmed": False,
                "field_value_present": False,
                "receipt_snapshot_created": True,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "decision_approved": False,
                "decision_granted": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "external_delivery_allowed": False,
                "export_allowed": False,
                "safe_to_continue_to_gp046": True,
            }
        )

    return {
        "owner_review_receipt_placeholder_items": items,
        "owner_review_receipt_placeholder_count": len(items),
        "receipt_snapshot_created_count": len(items),
        "owner_review_required_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "field_value_present_count": 0,
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "export_allowed_count": 0,
        "safe_to_continue_owner_review_receipts": True,
    }


def _build_denial_receipt_summaries(gp044: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp044["denial_reason_labels"]["denial_reason_label_items"]

    items = []
    for item in source_items:
        items.append(
            {
                "denial_receipt_summary_id": f"VSADRS-{item['denial_reason_label_id'].split('-', 1)[-1]}",
                "denial_reason_label_id": item["denial_reason_label_id"],
                "decision_card_id": item["decision_card_id"],
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "scope": item["scope"],
                "denial_reason": item["denial_reason"],
                "denial_receipt_status": "ACTIVE_DENIAL_RECEIPT_SUMMARY",
                "metadata_only": True,
                "denied_by_default": True,
                "blocks_official_receipt": True,
                "blocks_final_receipt": True,
                "blocks_receipt_close": True,
                "blocks_access_grant": True,
                "blocks_provider_read": True,
                "blocks_object_body_view": True,
                "blocks_export": True,
                "blocks_external_delivery": True,
                "blocks_portal_access": True,
                "blocks_execution": True,
                "official_receipt_claimed": False,
                "receipt_finalized": False,
                "receipt_closed": False,
                "safe_to_continue_to_gp046": True,
            }
        )

    return {
        "denial_receipt_summary_items": items,
        "denial_receipt_summary_count": len(items),
        "denied_by_default_count": len(items),
        "blocks_official_receipt_count": len(items),
        "blocks_final_receipt_count": len(items),
        "blocks_receipt_close_count": len(items),
        "blocks_access_grant_count": len(items),
        "blocks_provider_read_count": len(items),
        "blocks_object_body_view_count": len(items),
        "blocks_export_count": len(items),
        "blocks_external_delivery_count": len(items),
        "blocks_portal_access_count": len(items),
        "blocks_execution_count": len(items),
        "official_receipt_claimed_count": 0,
        "receipt_finalized_count": 0,
        "receipt_closed_count": 0,
        "safe_to_continue_denial_receipt_summaries": True,
    }


def _build_next_step(
    receipt_cards: Dict[str, Any],
    no_grant_receipt_labels: Dict[str, Any],
    tower_requirement_receipts: Dict[str, Any],
    owner_review_receipts: Dict[str, Any],
    denial_receipt_summaries: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSARPNX-001",
            "title": "Prepare storage audit trail preview",
            "target_pack": "VAULT_GP046",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARPNX-002",
            "title": "Keep receipts preview-only",
            "target_pack": "VAULT_GP046",
            "status": "PREVIEW_ONLY_RECEIPTS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARPNX-003",
            "title": "Keep no official/final/closed receipt claim",
            "target_pack": "VAULT_GP046",
            "status": "NO_OFFICIAL_RECEIPT_CLAIM",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp046_count": len(items),
        "receipt_card_count": receipt_cards["receipt_card_count"],
        "no_grant_receipt_label_count": no_grant_receipt_labels["no_grant_receipt_label_count"],
        "tower_requirement_receipt_count": tower_requirement_receipts["tower_requirement_receipt_count"],
        "owner_review_receipt_placeholder_count": owner_review_receipts["owner_review_receipt_placeholder_count"],
        "denial_receipt_summary_count": denial_receipt_summaries["denial_receipt_summary_count"],
        "safe_to_continue_to_gp046": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP046",
        "recommended_next_pack_title": "Storage Audit Trail Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep receipt previews metadata-only.",
            "Keep receipts preview-only, not official.",
            "Keep no finalized receipt claim.",
            "Keep no receipt close claim.",
            "Keep no-grant receipt labels active.",
            "Keep Tower requirement snapshots required and ungranted.",
            "Keep owner review receipt placeholders empty and unconfirmed.",
            "Keep denial receipt summaries active.",
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
    return deepcopy(get_storage_access_receipt_preview_payload())


def get_storage_access_receipt_preview_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_truth": payload["receipt_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "receipt_routes": payload["receipt_routes"],
        "receipt_counts": payload["receipt_counts"],
        "gp044_connection": payload["gp044_connection"],
    }


def get_storage_access_receipt_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_cards": payload["receipt_cards"],
    }


def get_storage_access_no_grant_receipt_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_grant_receipt_labels": payload["no_grant_receipt_labels"],
    }


def get_storage_access_tower_requirement_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_requirement_receipts": payload["tower_requirement_receipts"],
    }


def get_storage_access_owner_review_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_receipts": payload["owner_review_receipts"],
    }


def get_storage_access_denial_receipt_summaries() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "denial_receipt_summaries": payload["denial_receipt_summaries"],
    }


def get_storage_access_receipt_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp045_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp045_status": payload["gp045_status"],
        "receipt_truth": payload["receipt_truth"],
        "receipt_routes": payload["receipt_routes"],
        "receipt_counts": payload["receipt_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp044_connection": payload["gp044_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_access_receipt_preview_page() -> str:
    payload = clone_payload()
    routes = payload["receipt_routes"]
    counts = payload["receipt_counts"]
    truth = payload["receipt_truth"]
    cards = payload["receipt_cards"]
    tower = payload["tower_requirement_receipts"]
    denial = payload["denial_receipt_summaries"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_receipt_card(item) for item in cards["receipt_card_items"])
    tower_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['requirement_name'])} · {escape(item['receipt_snapshot_status'])}</span>
          </div>
          <div class="pill danger">Ungranted</div>
        </div>
        """
        for item in tower["tower_requirement_receipt_items"][:12]
    )

    denial_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['denial_reason'])}</span>
          </div>
          <div class="pill danger">Blocks final</div>
        </div>
        """
        for item in denial["denial_receipt_summary_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Access Receipt Preview · GP045</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 045</div>
        <h1>Storage Access Receipt Preview</h1>
        <p class="hero-copy">
          GP045 previews storage access receipts without making them official, final, or closed. It records
          no-grant labels, Tower requirement snapshots, owner review placeholders, and denial receipt summaries.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['receipt_card_count']}</strong>
            <span>receipt cards</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_requirement_receipt_count']}</strong>
            <span>Tower snapshots</span>
          </div>
          <div class="metric">
            <strong>{counts['official_receipt_claimed_count']}</strong>
            <span>official claims</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Receipt preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No official receipt</span>
          <span class="pill danger">No final receipt</span>
          <span class="pill danger">No access grant</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Receipt Preview Cards</h2>
      <p>Receipt cards are preview-only. Nothing is official, finalized, closed, exported, delivered, or executed.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Tower Requirement Receipt Snapshots</h2>
        <p>Tower requirements remain required and ungranted.</p>
        <div>{tower_rows}</div>
      </div>
      <div>
        <h2>Denial Receipt Summaries</h2>
        <p>Denial summaries block official/final/closed receipt claims and access grants.</p>
        <div>{denial_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP046</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP045 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['receipt_cards_route'])}</code>
        <code>{escape(routes['no_grant_receipt_labels_route'])}</code>
        <code>{escape(routes['tower_requirement_receipts_route'])}</code>
        <code>{escape(routes['owner_review_receipts_route'])}</code>
        <code>{escape(routes['denial_receipt_summaries_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp045_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_receipt_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['receipt_card_id'])}</code><br>
              Status: <code>{escape(item['receipt_preview_status'])}</code><br>
              Official: <code>{str(item['official_receipt_claimed']).lower()}</code><br>
              Finalized: <code>{str(item['receipt_finalized']).lower()}</code><br>
              Closed: <code>{str(item['receipt_closed']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Preview only</span>
        </div>
      </article>
    """
