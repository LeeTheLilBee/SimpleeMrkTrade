"""
VAULT GIANT PACK 043 — Storage Access Request Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP042 by creating metadata-only storage access request previews.

Purpose:
- Build access request cards for storage object inventory rows.
- Add requester/role placeholders.
- Add Tower clearance and step-up gates.
- Add object visibility limits.
- Add denied-by-default labels.
- Add access reason fields.
- Carry forward to GP044.

Important truth:
- GP043 previews access requests only.
- GP043 does not approve access.
- GP043 does not grant access.
- GP043 does not read provider objects.
- GP043 does not write provider objects.
- GP043 does not show object bodies.
- GP043 does not store raw files.
- GP043 does not unlock direct upload.
- GP043 does not select or configure a provider.
- GP043 does not verify checksums/hashes.
- GP043 does not export or externally deliver anything.
- GP043 does not create public proof.
- GP043 does not open portals.
- GP043 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP043 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, storage access authorization, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_object_inventory_preview_service import get_storage_object_inventory_payload


PACK_ID = "VAULT_GP043"
PACK_NAME = "Storage Access Request Preview"
SCHEMA_VERSION = "vault.storage_access_request_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

REQUESTER_PLACEHOLDERS = [
    {
        "requester_role": "owner",
        "requester_label": "Owner Placeholder",
        "scope": "internal_owner_preview",
    },
    {
        "requester_role": "tower_admin",
        "requester_label": "Tower Admin Placeholder",
        "scope": "tower_authority_review",
    },
    {
        "requester_role": "vault_reviewer",
        "requester_label": "Vault Reviewer Placeholder",
        "scope": "metadata_review_only",
    },
    {
        "requester_role": "external_party_placeholder",
        "requester_label": "External Party Placeholder",
        "scope": "denied_by_default_external_access",
    },
]

TOWER_GATES = [
    "identity_required",
    "permission_required",
    "clearance_required",
    "step_up_required",
    "storage_access_authorization_required",
    "sensitive_visibility_lock_required",
    "export_lock_required",
    "external_access_lock_required",
    "audit_receipt_required",
]

VISIBILITY_LIMITS = [
    "metadata_only",
    "redacted_owner_preview_only",
    "no_object_body_view",
    "no_raw_view",
    "no_sensitive_body_display",
    "no_export_view",
    "no_external_access",
]

ACCESS_REASON_FIELDS = [
    "request_reason",
    "business_lane",
    "linked_packet",
    "linked_requirement",
    "requested_visibility",
    "tower_clearance_reason",
    "owner_review_note",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_access_request_payload() -> Dict[str, Any]:
    gp042 = get_storage_object_inventory_payload()

    request_cards = _build_request_cards(gp042)
    requester_placeholders = _build_requester_placeholders(request_cards)
    tower_gates = _build_tower_gates(request_cards)
    visibility_limits = _build_visibility_limits(request_cards)
    denied_labels = _build_denied_labels(request_cards)
    reason_fields = _build_reason_fields(request_cards)
    next_step = _build_next_step(
        request_cards,
        requester_placeholders,
        tower_gates,
        visibility_limits,
        denied_labels,
        reason_fields,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_access_request_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "access_truth": {
            "storage_access_request_preview_ready": True,
            "request_cards_visible": True,
            "requester_placeholders_visible": True,
            "tower_clearance_step_up_gates_visible": True,
            "object_visibility_limits_visible": True,
            "denied_by_default_labels_visible": True,
            "access_reason_fields_visible": True,
            "metadata_only": True,
            "private_preview_only": True,
            "access_request_created_count": request_cards["request_card_count"],
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "access_request_denied_by_default_count": request_cards["request_card_count"],
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
            "safe_to_continue_to_gp044": True,
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
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
            "vault_can_grant_storage_access": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
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
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "access_routes": {
            "room_title": "Vault Storage Access Request Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-access-request",
            "json_route": "/vault/storage-access-request.json",
            "request_cards_route": "/vault/storage-access-request-cards.json",
            "requester_placeholders_route": "/vault/storage-access-requester-placeholders.json",
            "tower_gates_route": "/vault/storage-access-tower-gates.json",
            "visibility_limits_route": "/vault/storage-access-visibility-limits.json",
            "denied_labels_route": "/vault/storage-access-denied-labels.json",
            "reason_fields_route": "/vault/storage-access-reason-fields.json",
            "next_step_route": "/vault/storage-access-next-step.json",
            "gp043_status_route": "/vault/gp043-status.json",
        },
        "access_counts": {
            "request_card_count": request_cards["request_card_count"],
            "requester_placeholder_count": requester_placeholders["requester_placeholder_count"],
            "tower_gate_count": tower_gates["tower_gate_count"],
            "visibility_limit_count": visibility_limits["visibility_limit_count"],
            "denied_label_count": denied_labels["denied_label_count"],
            "reason_field_count": reason_fields["reason_field_count"],
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
            "access_request_denied_by_default_count": request_cards["request_card_count"],
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
        "request_cards": request_cards,
        "requester_placeholders": requester_placeholders,
        "tower_gates": tower_gates,
        "visibility_limits": visibility_limits,
        "denied_labels": denied_labels,
        "reason_fields": reason_fields,
        "next_step": next_step,
        "gp042_connection": {
            "gp042_pack_id": gp042["pack"]["id"],
            "gp042_ready": gp042["gp042_status"]["ready"],
            "gp042_safe_to_continue": gp042["gp042_status"]["safe_to_continue_to_gp043"],
            "gp042_vault_done": gp042["gp042_status"]["vault_done"],
            "gp042_section": gp042["pack"]["section"],
            "gp042_inventory_row_count": gp042["inventory_counts"]["inventory_row_count"],
            "gp042_provider_link_count": gp042["inventory_counts"]["provider_link_count"],
            "gp042_missing_warning_count": gp042["inventory_counts"]["missing_warning_count"],
            "gp042_tower_visibility_gate_count": gp042["inventory_counts"]["tower_visibility_gate_count"],
        },
        "gp043_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_access_request_preview_ready": True,
            "safe_to_continue_to_gp044": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_access_preview": True,
            "private_preview_only": True,
            "access_request_submitted_count": 0,
            "access_request_approved_count": 0,
            "access_request_granted_count": 0,
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
            "receipt_close_disabled": True,
            "receipt_finalization_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp043",
            "next_pack": "VAULT_GP044_STORAGE_ACCESS_DECISION_QUEUE",
        },
    }

    return payload


def _build_request_cards(gp042: Dict[str, Any]) -> Dict[str, Any]:
    inventory_items = gp042["inventory_rows"]["inventory_row_items"]

    cards = []
    for index, item in enumerate(inventory_items, start=1):
        cards.append(
            {
                "access_request_card_id": f"VSAR-{index:03d}",
                "inventory_row_id": item["inventory_row_id"],
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "object_key_pattern": item["object_key_pattern"],
                "request_status": "PREVIEW_ONLY_DENIED_BY_DEFAULT",
                "access_status_label": "ACCESS_NOT_REQUESTED_DENIED_BY_DEFAULT",
                "metadata_only": True,
                "private_preview_only": True,
                "request_created": True,
                "request_submitted": False,
                "request_approved": False,
                "access_granted": False,
                "access_denied_by_default": True,
                "requester_placeholder_required": True,
                "requester_bound": False,
                "tower_clearance_required": True,
                "tower_clearance_granted": False,
                "tower_step_up_required": True,
                "tower_step_up_granted": False,
                "tower_storage_access_authorization_required": True,
                "tower_storage_access_authorized": False,
                "owner_review_required": True,
                "owner_reviewed": False,
                "owner_confirmed": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "provider_object_read_claimed": False,
                "object_body_view_enabled": False,
                "object_body_available": False,
                "object_body_preview_allowed": False,
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
                "safe_to_continue_to_gp044": True,
            }
        )

    return {
        "request_card_items": cards,
        "request_card_count": len(cards),
        "request_created_count": len(cards),
        "request_submitted_count": 0,
        "request_approved_count": 0,
        "access_granted_count": 0,
        "access_denied_by_default_count": len(cards),
        "requester_placeholder_required_count": len(cards),
        "requester_bound_count": 0,
        "tower_clearance_required_count": len(cards),
        "tower_clearance_granted_count": 0,
        "tower_step_up_required_count": len(cards),
        "tower_step_up_granted_count": 0,
        "tower_storage_access_authorization_required_count": len(cards),
        "tower_storage_access_authorized_count": 0,
        "owner_review_required_count": len(cards),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "provider_object_read_claimed_count": 0,
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
        "safe_to_continue_request_cards": True,
    }


def _build_requester_placeholders(request_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in request_cards["request_card_items"]:
        for requester in REQUESTER_PLACEHOLDERS:
            items.append(
                {
                    "requester_placeholder_id": f"VSARP-{card['access_request_card_id'].split('-')[-1]}-{requester['requester_role']}",
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "requester_role": requester["requester_role"],
                    "requester_label": requester["requester_label"],
                    "requester_scope": requester["scope"],
                    "requester_status": "PLACEHOLDER_NOT_BOUND_NOT_AUTHORIZED",
                    "metadata_only": True,
                    "requester_bound": False,
                    "identity_verified": False,
                    "permission_granted": False,
                    "tower_clearance_granted": False,
                    "tower_step_up_granted": False,
                    "access_authorized": False,
                    "external_party": requester["requester_role"] == "external_party_placeholder",
                    "external_access_allowed": False,
                    "portal_access_allowed": False,
                    "object_body_view_enabled": False,
                    "provider_read_enabled": False,
                    "safe_to_continue_to_gp044": True,
                }
            )

    return {
        "requester_placeholder_items": items,
        "requester_placeholder_count": len(items),
        "request_card_count": request_cards["request_card_count"],
        "requester_role_count": len(REQUESTER_PLACEHOLDERS),
        "requester_bound_count": 0,
        "identity_verified_count": 0,
        "permission_granted_count": 0,
        "tower_clearance_granted_count": 0,
        "tower_step_up_granted_count": 0,
        "access_authorized_count": 0,
        "external_party_placeholder_count": request_cards["request_card_count"],
        "external_access_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "object_body_view_enabled_count": 0,
        "provider_read_enabled_count": 0,
        "safe_to_continue_requester_placeholders": True,
    }


def _build_tower_gates(request_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in request_cards["request_card_items"]:
        for gate in TOWER_GATES:
            items.append(
                {
                    "tower_access_gate_id": f"VSATG-{card['access_request_card_id'].split('-')[-1]}-{gate}",
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "gate_name": gate,
                    "gate_status": "TOWER_REQUIRED_NOT_GRANTED",
                    "metadata_only": True,
                    "required": True,
                    "granted": False,
                    "vault_can_override": False,
                    "access_request_submitted": False,
                    "access_request_approved": False,
                    "access_granted": False,
                    "provider_read_enabled": False,
                    "object_body_view_enabled": False,
                    "export_allowed": False,
                    "external_access_allowed": False,
                    "safe_to_continue_to_gp044": True,
                }
            )

    return {
        "tower_gate_items": items,
        "tower_gate_count": len(items),
        "tower_gate_type_count": len(TOWER_GATES),
        "request_card_count": request_cards["request_card_count"],
        "required_gate_count": len(items),
        "granted_gate_count": 0,
        "vault_override_allowed_count": 0,
        "access_request_submitted_count": 0,
        "access_request_approved_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "external_access_allowed_count": 0,
        "tower_authority_preserved": True,
        "safe_to_continue_tower_gates": True,
    }


def _build_visibility_limits(request_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in request_cards["request_card_items"]:
        for limit in VISIBILITY_LIMITS:
            items.append(
                {
                    "visibility_limit_id": f"VSAVL-{card['access_request_card_id'].split('-')[-1]}-{limit}",
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "visibility_limit": limit,
                    "limit_status": "ACTIVE_LIMIT",
                    "metadata_only": True,
                    "limit_active": True,
                    "owner_redacted_preview_allowed": limit == "redacted_owner_preview_only",
                    "object_body_view_allowed": False,
                    "raw_view_allowed": False,
                    "sensitive_body_display_allowed": False,
                    "export_allowed": False,
                    "external_access_allowed": False,
                    "portal_access_allowed": False,
                    "vault_can_override": False,
                    "safe_to_continue_to_gp044": True,
                }
            )

    return {
        "visibility_limit_items": items,
        "visibility_limit_count": len(items),
        "visibility_limit_type_count": len(VISIBILITY_LIMITS),
        "request_card_count": request_cards["request_card_count"],
        "active_limit_count": len(items),
        "owner_redacted_preview_allowed_count": request_cards["request_card_count"],
        "object_body_view_allowed_count": 0,
        "raw_view_allowed_count": 0,
        "sensitive_body_display_allowed_count": 0,
        "export_allowed_count": 0,
        "external_access_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "vault_override_allowed_count": 0,
        "safe_to_continue_visibility_limits": True,
    }


def _build_denied_labels(request_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in request_cards["request_card_items"]:
        items.append(
            {
                "denied_label_id": f"VSADL-{card['access_request_card_id'].split('-')[-1]}",
                "access_request_card_id": card["access_request_card_id"],
                "inventory_row_id": card["inventory_row_id"],
                "scope": card["scope"],
                "denied_label": "DENIED_BY_DEFAULT_TOWER_ACCESS_REQUIRED",
                "owner_label": "Access denied by default — Tower clearance and step-up required",
                "metadata_only": True,
                "denied_by_default": True,
                "access_request_submitted": False,
                "access_request_approved": False,
                "access_granted": False,
                "provider_read_enabled": False,
                "object_body_view_enabled": False,
                "external_access_allowed": False,
                "export_allowed": False,
                "portal_access_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp044": True,
            }
        )

    return {
        "denied_label_items": items,
        "denied_label_count": len(items),
        "denied_by_default_count": len(items),
        "access_request_submitted_count": 0,
        "access_request_approved_count": 0,
        "access_granted_count": 0,
        "provider_read_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "external_access_allowed_count": 0,
        "export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_denied_labels": True,
    }


def _build_reason_fields(request_cards: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for card in request_cards["request_card_items"]:
        for field_name in ACCESS_REASON_FIELDS:
            items.append(
                {
                    "reason_field_id": f"VSARF-{card['access_request_card_id'].split('-')[-1]}-{field_name}",
                    "access_request_card_id": card["access_request_card_id"],
                    "inventory_row_id": card["inventory_row_id"],
                    "scope": card["scope"],
                    "field_name": field_name,
                    "field_status": "PLACEHOLDER_EMPTY_NOT_SUBMITTED",
                    "metadata_only": True,
                    "field_required_before_submission": True,
                    "field_value_present": False,
                    "request_submitted": False,
                    "request_approved": False,
                    "access_granted": False,
                    "tower_review_required": True,
                    "owner_review_required": True,
                    "external_delivery_allowed": False,
                    "export_allowed": False,
                    "execution_allowed": False,
                    "safe_to_continue_to_gp044": True,
                }
            )

    return {
        "reason_field_items": items,
        "reason_field_count": len(items),
        "reason_field_type_count": len(ACCESS_REASON_FIELDS),
        "request_card_count": request_cards["request_card_count"],
        "field_required_before_submission_count": len(items),
        "field_value_present_count": 0,
        "request_submitted_count": 0,
        "request_approved_count": 0,
        "access_granted_count": 0,
        "tower_review_required_count": len(items),
        "owner_review_required_count": len(items),
        "external_delivery_allowed_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_reason_fields": True,
    }


def _build_next_step(
    request_cards: Dict[str, Any],
    requester_placeholders: Dict[str, Any],
    tower_gates: Dict[str, Any],
    visibility_limits: Dict[str, Any],
    denied_labels: Dict[str, Any],
    reason_fields: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSARNX-001",
            "title": "Prepare storage access decision queue",
            "target_pack": "VAULT_GP044",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARNX-002",
            "title": "Keep access denied by default",
            "target_pack": "VAULT_GP044",
            "status": "DENIED_BY_DEFAULT_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSARNX-003",
            "title": "Keep object body and provider read locked",
            "target_pack": "VAULT_GP044",
            "status": "OBJECT_ACCESS_LOCKED",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp044_count": len(items),
        "request_card_count": request_cards["request_card_count"],
        "requester_placeholder_count": requester_placeholders["requester_placeholder_count"],
        "tower_gate_count": tower_gates["tower_gate_count"],
        "visibility_limit_count": visibility_limits["visibility_limit_count"],
        "denied_label_count": denied_labels["denied_label_count"],
        "reason_field_count": reason_fields["reason_field_count"],
        "safe_to_continue_to_gp044": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP044",
        "recommended_next_pack_title": "Storage Access Decision Queue",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep access request cards metadata-only.",
            "Keep access denied by default.",
            "Keep Tower clearance and step-up required and ungranted.",
            "Keep requester placeholders unbound.",
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
    return deepcopy(get_storage_access_request_payload())


def get_storage_access_request_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "access_truth": payload["access_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "access_routes": payload["access_routes"],
        "access_counts": payload["access_counts"],
        "gp042_connection": payload["gp042_connection"],
    }


def get_storage_access_request_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "request_cards": payload["request_cards"],
    }


def get_storage_access_requester_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "requester_placeholders": payload["requester_placeholders"],
    }


def get_storage_access_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gates": payload["tower_gates"],
    }


def get_storage_access_visibility_limits() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "visibility_limits": payload["visibility_limits"],
    }


def get_storage_access_denied_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "denied_labels": payload["denied_labels"],
    }


def get_storage_access_reason_fields() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "reason_fields": payload["reason_fields"],
    }


def get_storage_access_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp043_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp043_status": payload["gp043_status"],
        "access_truth": payload["access_truth"],
        "access_routes": payload["access_routes"],
        "access_counts": payload["access_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp042_connection": payload["gp042_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_access_request_preview_page() -> str:
    payload = clone_payload()
    routes = payload["access_routes"]
    counts = payload["access_counts"]
    truth = payload["access_truth"]
    cards = payload["request_cards"]
    tower = payload["tower_gates"]
    denied = payload["denied_labels"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_access_card(item) for item in cards["request_card_items"])
    tower_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['gate_name'])} · {escape(item['gate_status'])}</span>
          </div>
          <div class="pill danger">Required</div>
        </div>
        """
        for item in tower["tower_gate_items"][:12]
    )

    denied_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['owner_label'])}</span>
          </div>
          <div class="pill danger">Denied</div>
        </div>
        """
        for item in denied["denied_label_items"]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Access Request Preview · GP043</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 043</div>
        <h1>Storage Access Request Preview</h1>
        <p class="hero-copy">
          GP043 previews storage access requests without approving or granting access. It adds request cards,
          requester placeholders, Tower gates, visibility limits, denied-by-default labels, and reason fields.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['request_card_count']}</strong>
            <span>request cards</span>
          </div>
          <div class="metric">
            <strong>{counts['tower_gate_count']}</strong>
            <span>Tower gates</span>
          </div>
          <div class="metric">
            <strong>{counts['access_request_granted_count']}</strong>
            <span>granted access</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Access preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">Denied by default</span>
          <span class="pill danger">No object body view</span>
          <span class="pill danger">No provider read/write</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Access Request Cards</h2>
      <p>Requests are preview-only. Nothing is submitted, approved, granted, read, exported, delivered, or executed.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Tower Access Gates</h2>
        <p>Tower clearance, step-up, authorization, export locks, and external access locks remain required and ungranted.</p>
        <div>{tower_rows}</div>
      </div>
      <div>
        <h2>Denied-by-default Labels</h2>
        <p>Every access request card remains denied by default.</p>
        <div>{denied_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP044</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP043 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['request_cards_route'])}</code>
        <code>{escape(routes['requester_placeholders_route'])}</code>
        <code>{escape(routes['tower_gates_route'])}</code>
        <code>{escape(routes['visibility_limits_route'])}</code>
        <code>{escape(routes['denied_labels_route'])}</code>
        <code>{escape(routes['reason_fields_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp043_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_access_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Card: <code>{escape(item['access_request_card_id'])}</code><br>
              Status: <code>{escape(item['access_status_label'])}</code><br>
              Submitted: <code>{str(item['request_submitted']).lower()}</code><br>
              Approved: <code>{str(item['request_approved']).lower()}</code><br>
              Granted: <code>{str(item['access_granted']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Denied</span>
        </div>
      </article>
    """
