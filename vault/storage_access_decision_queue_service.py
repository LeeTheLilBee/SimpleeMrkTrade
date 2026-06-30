"""
VAULT GIANT PACK 044 — Storage Access Decision Queue

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP043 by creating a metadata-only storage access decision queue.

Purpose:
- Build pending / blocked / denied decision cards.
- Add Tower approval requirement records.
- Add owner review placeholders.
- Add denial reason labels.
- Add no-grant enforcement records.
- Carry forward to GP045.

Important truth:
- GP044 queues decisions only.
- GP044 does not approve access.
- GP044 does not grant access.
- GP044 does not submit access requests.
- GP044 does not read provider objects.
- GP044 does not write provider objects.
- GP044 does not show object bodies.
- GP044 does not store raw files.
- GP044 does not unlock direct upload.
- GP044 does not select or configure a provider.
- GP044 does not verify checksums/hashes.
- GP044 does not export or externally deliver anything.
- GP044 does not create public proof.
- GP044 does not open portals.
- GP044 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP044 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_access_request_preview_service import get_storage_access_request_payload


PACK_ID = "VAULT_GP044"
PACK_NAME = "Storage Access Decision Queue"
SCHEMA_VERSION = "vault.storage_access_decision_queue.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

TOWER_APPROVAL_REQUIREMENTS = [
    "identity_verified",
    "permission_granted",
    "clearance_granted",
    "step_up_completed",
    "storage_access_authorized",
    "sensitive_visibility_authorized",
    "export_lock_reviewed",
    "audit_receipt_ready",
]

OWNER_REVIEW_FIELDS = [
    "owner_review_note",
    "owner_business_reason",
    "owner_visibility_scope",
    "owner_risk_acknowledgment",
]

DENIAL_REASONS = [
    "request_not_submitted",
    "tower_clearance_missing",
    "tower_step_up_missing",
    "storage_access_authorization_missing",
    "provider_read_locked",
    "object_body_view_locked",
    "export_locked",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_access_decision_queue_payload() -> Dict[str, Any]:
    gp043 = get_storage_access_request_payload()

    decision_cards = _build_decision_cards(gp043)
    tower_requirements = _build_tower_approval_requirements(decision_cards)
    owner_review_placeholders = _build_owner_review_placeholders(decision_cards)
    denial_reason_labels = _build_denial_reason_labels(decision_cards)
    no_grant_enforcement = _build_no_grant_enforcement(decision_cards)
    next_step = _build_next_step(
        decision_cards,
        tower_requirements,
        owner_review_placeholders,
        denial_reason_labels,
        no_grant_enforcement,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_access_decision_queue",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "decision_truth": {
            "storage_access_decision_queue_ready": True,
            "decision_cards_visible": True,
            "tower_approval_requirements_visible": True,
            "owner_review_placeholders_visible": True,
            "denial_reason_labels_visible": True,
            "no_grant_enforcement_visible": True,
            "metadata_only": True,
            "private_queue_only": True,
            "decision_card_created_count": decision_cards["decision_card_count"],
            "decision_status_pending_count": decision_cards["pending_decision_count"],
            "decision_status_blocked_count": decision_cards["blocked_decision_count"],
            "decision_status_denied_count": decision_cards["denied_decision_count"],
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "decision_released_count": 0,
            "access_denied_by_default_count": decision_cards["decision_card_count"],
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
            "receipt_close_enabled": False,
            "receipt_finalization_enabled": False,
            "vault_done": False,
            "clouds_should_continue": False,
            "safe_to_continue_to_gp045": True,
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
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
            "vault_can_approve_storage_access_decision": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "storage_access_default": "denied_by_default",
            "decision_default": "blocked_denied_by_default",
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
        "decision_routes": {
            "room_title": "Vault Storage Access Decision Queue",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-access-decision-queue",
            "json_route": "/vault/storage-access-decision-queue.json",
            "decision_cards_route": "/vault/storage-access-decision-cards.json",
            "tower_requirements_route": "/vault/storage-access-tower-approval-requirements.json",
            "owner_review_placeholders_route": "/vault/storage-access-owner-review-placeholders.json",
            "denial_reason_labels_route": "/vault/storage-access-denial-reason-labels.json",
            "no_grant_enforcement_route": "/vault/storage-access-no-grant-enforcement.json",
            "next_step_route": "/vault/storage-access-decision-next-step.json",
            "gp044_status_route": "/vault/gp044-status.json",
        },
        "decision_counts": {
            "decision_card_count": decision_cards["decision_card_count"],
            "pending_decision_count": decision_cards["pending_decision_count"],
            "blocked_decision_count": decision_cards["blocked_decision_count"],
            "denied_decision_count": decision_cards["denied_decision_count"],
            "tower_requirement_count": tower_requirements["tower_requirement_count"],
            "owner_review_placeholder_count": owner_review_placeholders["owner_review_placeholder_count"],
            "denial_reason_label_count": denial_reason_labels["denial_reason_label_count"],
            "no_grant_enforcement_count": no_grant_enforcement["no_grant_enforcement_count"],
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
        "decision_cards": decision_cards,
        "tower_requirements": tower_requirements,
        "owner_review_placeholders": owner_review_placeholders,
        "denial_reason_labels": denial_reason_labels,
        "no_grant_enforcement": no_grant_enforcement,
        "next_step": next_step,
        "gp043_connection": {
            "gp043_pack_id": gp043["pack"]["id"],
            "gp043_ready": gp043["gp043_status"]["ready"],
            "gp043_safe_to_continue": gp043["gp043_status"]["safe_to_continue_to_gp044"],
            "gp043_vault_done": gp043["gp043_status"]["vault_done"],
            "gp043_section": gp043["pack"]["section"],
            "gp043_request_card_count": gp043["access_counts"]["request_card_count"],
            "gp043_tower_gate_count": gp043["access_counts"]["tower_gate_count"],
            "gp043_denied_label_count": gp043["access_counts"]["denied_label_count"],
            "gp043_reason_field_count": gp043["access_counts"]["reason_field_count"],
        },
        "gp044_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_access_decision_queue_ready": True,
            "safe_to_continue_to_gp045": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_decision_queue": True,
            "private_queue_only": True,
            "decision_cards_ready": True,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "decision_approved_count": 0,
            "decision_granted_count": 0,
            "access_denied_by_default": True,
            "no_grant_enforced": True,
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
            "receipt_close_disabled": True,
            "receipt_finalization_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp044",
            "next_pack": "VAULT_GP045_STORAGE_ACCESS_RECEIPT_PREVIEW",
        },
    }

    return payload


def _build_decision_cards(gp043: Dict[str, Any]) -> Dict[str, Any]:
    request_items = gp043["request_cards"]["request_card_items"]

    cards = []
    for index, item in enumerate(request_items, start=1):
        cards.append(
            {
                "decision_card_id": f"VSADQ-{index:03d}",
                "access_request_card_id": item["access_request_card_id"],
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "decision_status": "BLOCKED_DENIED_BY_DEFAULT_TOWER_REVIEW_REQUIRED",
                "queue_label": "Pending decision — blocked and denied by default",
                "metadata_only": True,
                "private_queue_only": True,
                "pending_decision": True,
                "blocked_decision": True,
                "denied_decision": True,
                "decision_submitted": False,
                "decision_approved": False,
                "decision_granted": False,
                "access_request_submitted": False,
                "access_request_approved": False,
                "access_granted": False,
                "no_grant_enforced": True,
                "tower_approval_required": True,
                "tower_approval_granted": False,
                "owner_review_required": True,
                "owner_reviewed": False,
                "owner_confirmed": False,
                "denial_reason_required": True,
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
                "safe_to_continue_to_gp045": True,
            }
        )

    return {
        "decision_card_items": cards,
        "decision_card_count": len(cards),
        "pending_decision_count": len(cards),
        "blocked_decision_count": len(cards),
        "denied_decision_count": len(cards),
        "decision_submitted_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_request_submitted_count": 0,
        "access_request_approved_count": 0,
        "access_granted_count": 0,
        "no_grant_enforced_count": len(cards),
        "tower_approval_required_count": len(cards),
        "tower_approval_granted_count": 0,
        "owner_review_required_count": len(cards),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
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
        "safe_to_continue_decision_cards": True,
    }


def _build_tower_approval_requirements(decision_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in decision_cards["decision_card_items"]:
        for requirement in TOWER_APPROVAL_REQUIREMENTS:
            items.append(
                {
                    "tower_requirement_id": f"VSATR-{card['decision_card_id'].split('-')[-1]}-{requirement}",
                    "decision_card_id": card["decision_card_id"],
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "requirement_name": requirement,
                    "requirement_status": "REQUIRED_NOT_GRANTED",
                    "metadata_only": True,
                    "required": True,
                    "granted": False,
                    "vault_can_override": False,
                    "decision_approved": False,
                    "decision_granted": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "external_delivery_allowed": False,
                    "safe_to_continue_to_gp045": True,
                }
            )

    return {
        "tower_requirement_items": items,
        "tower_requirement_count": len(items),
        "tower_requirement_type_count": len(TOWER_APPROVAL_REQUIREMENTS),
        "decision_card_count": decision_cards["decision_card_count"],
        "required_count": len(items),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "tower_authority_preserved": True,
        "safe_to_continue_tower_requirements": True,
    }


def _build_owner_review_placeholders(decision_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in decision_cards["decision_card_items"]:
        for field in OWNER_REVIEW_FIELDS:
            items.append(
                {
                    "owner_review_placeholder_id": f"VSAOR-{card['decision_card_id'].split('-')[-1]}-{field}",
                    "decision_card_id": card["decision_card_id"],
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "owner_review_field": field,
                    "placeholder_status": "EMPTY_NOT_REVIEWED_NOT_CONFIRMED",
                    "metadata_only": True,
                    "owner_review_required": True,
                    "owner_reviewed": False,
                    "owner_confirmed": False,
                    "field_value_present": False,
                    "decision_approved": False,
                    "decision_granted": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "external_delivery_allowed": False,
                    "export_allowed": False,
                    "safe_to_continue_to_gp045": True,
                }
            )

    return {
        "owner_review_placeholder_items": items,
        "owner_review_placeholder_count": len(items),
        "owner_review_field_type_count": len(OWNER_REVIEW_FIELDS),
        "decision_card_count": decision_cards["decision_card_count"],
        "owner_review_required_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "field_value_present_count": 0,
        "decision_approved_count": 0,
        "decision_granted_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "export_allowed_count": 0,
        "safe_to_continue_owner_review_placeholders": True,
    }


def _build_denial_reason_labels(decision_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in decision_cards["decision_card_items"]:
        for reason in DENIAL_REASONS:
            items.append(
                {
                    "denial_reason_label_id": f"VSADRL-{card['decision_card_id'].split('-')[-1]}-{reason}",
                    "decision_card_id": card["decision_card_id"],
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "denial_reason": reason,
                    "denial_status": "ACTIVE_DENIAL_REASON",
                    "metadata_only": True,
                    "denied_by_default": True,
                    "blocks_approval": True,
                    "blocks_access_grant": True,
                    "blocks_provider_read": True,
                    "blocks_object_body_view": True,
                    "blocks_export": True,
                    "blocks_external_delivery": True,
                    "blocks_portal_access": True,
                    "blocks_execution": True,
                    "owner_resolvable_now": False,
                    "tower_authorization_required": True,
                    "safe_to_continue_to_gp045": True,
                }
            )

    return {
        "denial_reason_label_items": items,
        "denial_reason_label_count": len(items),
        "denial_reason_type_count": len(DENIAL_REASONS),
        "decision_card_count": decision_cards["decision_card_count"],
        "denied_by_default_count": len(items),
        "blocks_approval_count": len(items),
        "blocks_access_grant_count": len(items),
        "blocks_provider_read_count": len(items),
        "blocks_object_body_view_count": len(items),
        "blocks_export_count": len(items),
        "blocks_external_delivery_count": len(items),
        "blocks_portal_access_count": len(items),
        "blocks_execution_count": len(items),
        "owner_resolvable_now_count": 0,
        "tower_authorization_required_count": len(items),
        "safe_to_continue_denial_reason_labels": True,
    }


def _build_no_grant_enforcement(decision_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in decision_cards["decision_card_items"]:
        items.append(
            {
                "no_grant_enforcement_id": f"VSANGE-{card['decision_card_id'].split('-')[-1]}",
                "decision_card_id": card["decision_card_id"],
                "access_request_card_id": card["access_request_card_id"],
                "inventory_row_id": card["inventory_row_id"],
                "scope": card["scope"],
                "enforcement_status": "NO_GRANT_ENFORCED",
                "metadata_only": True,
                "no_grant_enforced": True,
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
                "execution_allowed": False,
                "vault_can_override": False,
                "tower_authorization_required": True,
                "safe_to_continue_to_gp045": True,
            }
        )

    return {
        "no_grant_enforcement_items": items,
        "no_grant_enforcement_count": len(items),
        "no_grant_enforced_count": len(items),
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
        "execution_allowed_count": 0,
        "vault_override_allowed_count": 0,
        "tower_authorization_required_count": len(items),
        "safe_to_continue_no_grant_enforcement": True,
    }


def _build_next_step(
    decision_cards: Dict[str, Any],
    tower_requirements: Dict[str, Any],
    owner_review_placeholders: Dict[str, Any],
    denial_reason_labels: Dict[str, Any],
    no_grant_enforcement: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSADQNX-001",
            "title": "Prepare storage access receipt preview",
            "target_pack": "VAULT_GP045",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSADQNX-002",
            "title": "Keep no-grant enforcement active",
            "target_pack": "VAULT_GP045",
            "status": "NO_GRANT_ENFORCEMENT_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSADQNX-003",
            "title": "Keep Tower approval requirements ungranted",
            "target_pack": "VAULT_GP045",
            "status": "TOWER_REQUIREMENTS_UNGRANTED",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp045_count": len(items),
        "decision_card_count": decision_cards["decision_card_count"],
        "tower_requirement_count": tower_requirements["tower_requirement_count"],
        "owner_review_placeholder_count": owner_review_placeholders["owner_review_placeholder_count"],
        "denial_reason_label_count": denial_reason_labels["denial_reason_label_count"],
        "no_grant_enforcement_count": no_grant_enforcement["no_grant_enforcement_count"],
        "safe_to_continue_to_gp045": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP045",
        "recommended_next_pack_title": "Storage Access Receipt Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep decision queue metadata-only.",
            "Keep access denied by default.",
            "Keep no-grant enforcement active.",
            "Keep Tower approval requirements required and ungranted.",
            "Keep owner review placeholders empty and unconfirmed.",
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
    return deepcopy(get_storage_access_decision_queue_payload())


def get_storage_access_decision_queue_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_truth": payload["decision_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "decision_routes": payload["decision_routes"],
        "decision_counts": payload["decision_counts"],
        "gp043_connection": payload["gp043_connection"],
    }


def get_storage_access_decision_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_cards": payload["decision_cards"],
    }


def get_storage_access_tower_approval_requirements() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_requirements": payload["tower_requirements"],
    }


def get_storage_access_owner_review_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_placeholders": payload["owner_review_placeholders"],
    }


def get_storage_access_denial_reason_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "denial_reason_labels": payload["denial_reason_labels"],
    }


def get_storage_access_no_grant_enforcement() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_grant_enforcement": payload["no_grant_enforcement"],
    }


def get_storage_access_decision_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp044_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp044_status": payload["gp044_status"],
        "decision_truth": payload["decision_truth"],
        "decision_routes": payload["decision_routes"],
        "decision_counts": payload["decision_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp043_connection": payload["gp043_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_access_decision_queue_page() -> str:
    payload = clone_payload()
    routes = payload["decision_routes"]
    counts = payload["decision_counts"]
    truth = payload["decision_truth"]
    cards = payload["decision_cards"]
    requirements = payload["tower_requirements"]
    denied = payload["denial_reason_labels"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_decision_card(item) for item in cards["decision_card_items"])
    tower_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['requirement_name'])} · {escape(item['requirement_status'])}</span>
          </div>
          <div class="pill danger">Required</div>
        </div>
        """
        for item in requirements["tower_requirement_items"][:12]
    )

    denial_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['denial_reason'])}</span>
          </div>
          <div class="pill danger">Blocks grant</div>
        </div>
        """
        for item in denied["denial_reason_label_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Access Decision Queue · GP044</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 044</div>
        <h1>Storage Access Decision Queue</h1>
        <p class="hero-copy">
          GP044 queues storage access decisions without approving or granting anything. It adds decision cards,
          Tower approval requirements, owner review placeholders, denial reason labels, and no-grant enforcement.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['decision_card_count']}</strong>
            <span>decision cards</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_requirement_count']}</strong>
            <span>Tower requirements</span>
          </div>
          <div class="metric">
            <strong>{counts['access_request_granted_count']}</strong>
            <span>access grants</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Decision queue ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No grant enforced</span>
          <span class="pill danger">No access approval</span>
          <span class="pill danger">No provider read/write</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Decision Cards</h2>
      <p>Decision cards are pending, blocked, and denied by default. No decision is approved or granted.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Tower Approval Requirements</h2>
        <p>Tower approval requirements remain required and ungranted.</p>
        <div>{tower_rows}</div>
      </div>
      <div>
        <h2>Denial Reason Labels</h2>
        <p>Denial reasons block approval, access grant, provider read, object body view, export, delivery, portals, and execution.</p>
        <div>{denial_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP045</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP044 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['decision_cards_route'])}</code>
        <code>{escape(routes['tower_requirements_route'])}</code>
        <code>{escape(routes['owner_review_placeholders_route'])}</code>
        <code>{escape(routes['denial_reason_labels_route'])}</code>
        <code>{escape(routes['no_grant_enforcement_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp044_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_decision_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['decision_card_id'])}</code><br>
              Status: <code>{escape(item['decision_status'])}</code><br>
              Approved: <code>{str(item['decision_approved']).lower()}</code><br>
              Granted: <code>{str(item['decision_granted']).lower()}</code><br>
              No-grant enforced: <code>{str(item['no_grant_enforced']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Blocked</span>
        </div>
      </article>
    """
