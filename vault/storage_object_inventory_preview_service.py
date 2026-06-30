"""
VAULT GIANT PACK 042 — Storage Object Inventory Preview

CURRENT SECTION:
Archive Vault — Next Product Depth Layer
GP041-GP050

This pack deepens GP041 by creating a metadata-only inventory preview for future
stored objects.

Purpose:
- Build storage object inventory preview rows.
- Add storage status labels.
- Link inventory rows to provider placeholders.
- Add checksum/hash pending labels.
- Add missing object warnings.
- Add Tower visibility gates.
- Carry forward to GP043.

Important truth:
- GP042 does not store raw files.
- GP042 does not unlock direct upload.
- GP042 does not select or configure a storage provider.
- GP042 does not enable provider write/read.
- GP042 does not verify checksums or hashes.
- GP042 does not persist file bodies.
- GP042 does not create external delivery.
- GP042 does not export raw/unredacted data.
- GP042 does not create public proof.
- GP042 does not open seller/broker/trustee/external portals.
- GP042 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- GP042 does not mark Vault done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_provider_contract_starter_service import get_storage_provider_contract_payload


PACK_ID = "VAULT_GP042"
PACK_NAME = "Storage Object Inventory Preview"
SCHEMA_VERSION = "vault.storage_object_inventory_preview.v1"

SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
SECTION_RANGE = "GP041-GP050"

WARNING_TYPES = [
    "provider_not_selected",
    "provider_not_configured",
    "file_body_not_persisted",
    "checksum_not_verified",
    "direct_upload_locked",
]

VISIBILITY_GATES = [
    "owner_redacted_preview",
    "tower_sensitive_visibility",
    "tower_clearance",
    "tower_step_up",
    "export_lock",
    "external_access_lock",
    "portal_access_lock",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_object_inventory_payload() -> Dict[str, Any]:
    gp041 = get_storage_provider_contract_payload()

    inventory_rows = _build_inventory_rows(gp041)
    status_labels = _build_status_labels(inventory_rows)
    provider_links = _build_provider_links(gp041, inventory_rows)
    checksum_status = _build_checksum_status(inventory_rows)
    missing_warnings = _build_missing_warnings(inventory_rows)
    tower_visibility_gates = _build_tower_visibility_gates(inventory_rows)
    next_step = _build_next_step(
        inventory_rows,
        provider_links,
        checksum_status,
        missing_warnings,
        tower_visibility_gates,
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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_object_inventory_preview",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "inventory_truth": {
            "storage_object_inventory_preview_ready": True,
            "inventory_rows_visible": True,
            "storage_status_labels_visible": True,
            "provider_placeholder_links_visible": True,
            "checksum_pending_labels_visible": True,
            "missing_object_warnings_visible": True,
            "tower_visibility_gates_visible": True,
            "metadata_only": True,
            "private_preview_only": True,
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
            "object_body_available_count": 0,
            "object_body_preview_allowed": False,
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
            "safe_to_continue_to_gp043": True,
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
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_override_tower_visibility": False,
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
            "object_body_preview_allowed": False,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "inventory_routes": {
            "room_title": "Vault Storage Object Inventory Preview",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-object-inventory",
            "json_route": "/vault/storage-object-inventory.json",
            "inventory_rows_route": "/vault/storage-object-inventory-rows.json",
            "status_labels_route": "/vault/storage-object-status-labels.json",
            "provider_links_route": "/vault/storage-object-provider-links.json",
            "checksum_status_route": "/vault/storage-object-checksum-status.json",
            "missing_warnings_route": "/vault/storage-object-missing-warnings.json",
            "tower_visibility_gates_route": "/vault/storage-object-tower-visibility-gates.json",
            "next_step_route": "/vault/storage-object-next-step.json",
            "gp042_status_route": "/vault/gp042-status.json",
        },
        "inventory_counts": {
            "inventory_row_count": inventory_rows["inventory_row_count"],
            "status_label_count": status_labels["status_label_count"],
            "provider_link_count": provider_links["provider_link_count"],
            "checksum_status_count": checksum_status["checksum_status_count"],
            "missing_warning_count": missing_warnings["missing_warning_count"],
            "tower_visibility_gate_count": tower_visibility_gates["tower_visibility_gate_count"],
            "file_body_persisted_count": 0,
            "object_body_available_count": 0,
            "provider_selected_count": 0,
            "provider_configured_count": 0,
            "provider_write_enabled_count": 0,
            "provider_read_enabled_count": 0,
            "checksum_verified_count": 0,
            "hash_verified_count": 0,
            "raw_file_body_storage_enabled_count": 0,
            "direct_upload_unlocked_count": 0,
            "external_delivery_allowed_count": 0,
            "packet_export_allowed_count": 0,
            "execution_allowed_count": 0,
            "metadata_only": True,
        },
        "inventory_rows": inventory_rows,
        "status_labels": status_labels,
        "provider_links": provider_links,
        "checksum_status": checksum_status,
        "missing_warnings": missing_warnings,
        "tower_visibility_gates": tower_visibility_gates,
        "next_step": next_step,
        "gp041_connection": {
            "gp041_pack_id": gp041["pack"]["id"],
            "gp041_ready": gp041["gp041_status"]["ready"],
            "gp041_safe_to_continue": gp041["gp041_status"]["safe_to_continue_to_gp042"],
            "gp041_vault_done": gp041["gp041_status"]["vault_done"],
            "gp041_section": gp041["pack"]["section"],
            "gp041_provider_option_count": gp041["contract_counts"]["provider_option_count"],
            "gp041_object_key_placeholder_count": gp041["contract_counts"]["object_key_placeholder_count"],
            "gp041_checksum_placeholder_count": gp041["contract_counts"]["checksum_placeholder_count"],
            "gp041_boundary_violation_count": gp041["contract_counts"]["boundary_violation_count"],
        },
        "gp042_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_object_inventory_preview_ready": True,
            "safe_to_continue_to_gp043": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_inventory": True,
            "private_preview_only": True,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp042",
            "next_pack": "VAULT_GP043_STORAGE_ACCESS_REQUEST_PREVIEW",
        },
    }

    return payload


def _build_inventory_rows(gp041: Dict[str, Any]) -> Dict[str, Any]:
    object_key_items = gp041["object_key_contract"]["object_key_contract_items"]

    rows = []
    for index, item in enumerate(object_key_items, start=1):
        rows.append(
            {
                "inventory_row_id": f"VSOI-{index:03d}",
                "object_key_contract_id": item["object_key_contract_id"],
                "checksum_placeholder_id": item["checksum_placeholder_id"],
                "scope": item["scope"],
                "object_key_pattern": item["object_key_pattern"],
                "object_inventory_status": "EXPECTED_METADATA_ONLY_OBJECT_NOT_STORED",
                "storage_status_label": "MISSING_OBJECT_BODY_PROVIDER_NOT_CONFIGURED",
                "metadata_only": True,
                "private_preview_only": True,
                "provider_placeholder_linked": True,
                "provider_selected": False,
                "provider_configured": False,
                "provider_write_enabled": False,
                "provider_read_enabled": False,
                "object_key_bound_to_provider": False,
                "file_body_persisted": False,
                "object_body_available": False,
                "object_body_preview_allowed": False,
                "raw_file_body_storage_enabled": False,
                "direct_upload_enabled": False,
                "checksum_present": False,
                "checksum_verified": False,
                "hash_verified": False,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "raw_export_allowed": False,
                "unredacted_export_allowed": False,
                "public_packet_proof_allowed": False,
                "portal_access_allowed": False,
                "tower_visibility_required": True,
                "tower_visibility_granted": False,
                "safe_to_continue_to_gp043": True,
            }
        )

    return {
        "inventory_row_items": rows,
        "inventory_row_count": len(rows),
        "metadata_only_row_count": len(rows),
        "provider_placeholder_linked_count": len(rows),
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_write_enabled_count": 0,
        "provider_read_enabled_count": 0,
        "object_key_bound_to_provider_count": 0,
        "file_body_persisted_count": 0,
        "object_body_available_count": 0,
        "object_body_preview_allowed_count": 0,
        "raw_file_body_storage_enabled_count": 0,
        "direct_upload_enabled_count": 0,
        "checksum_present_count": 0,
        "checksum_verified_count": 0,
        "hash_verified_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "raw_export_allowed_count": 0,
        "unredacted_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "tower_visibility_required_count": len(rows),
        "tower_visibility_granted_count": 0,
        "safe_to_continue_inventory_rows": True,
    }


def _build_status_labels(inventory_rows: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for row in inventory_rows["inventory_row_items"]:
        items.append(
            {
                "status_label_id": f"VSOSL-{row['inventory_row_id'].split('-')[-1]}",
                "inventory_row_id": row["inventory_row_id"],
                "scope": row["scope"],
                "storage_status_label": row["storage_status_label"],
                "owner_label": "Missing object body — provider not configured",
                "metadata_only": True,
                "ready_for_owner_preview": True,
                "ready_for_raw_view": False,
                "ready_for_provider_write": False,
                "ready_for_export": False,
                "ready_for_external_delivery": False,
                "ready_for_public_proof": False,
                "ready_for_execution": False,
                "safe_to_continue_to_gp043": True,
            }
        )

    return {
        "status_label_items": items,
        "status_label_count": len(items),
        "ready_for_owner_preview_count": len(items),
        "ready_for_raw_view_count": 0,
        "ready_for_provider_write_count": 0,
        "ready_for_export_count": 0,
        "ready_for_external_delivery_count": 0,
        "ready_for_public_proof_count": 0,
        "ready_for_execution_count": 0,
        "safe_to_continue_status_labels": True,
    }


def _build_provider_links(gp041: Dict[str, Any], inventory_rows: Dict[str, Any]) -> Dict[str, Any]:
    providers = gp041["provider_options"]["provider_option_items"]
    items = []

    for row in inventory_rows["inventory_row_items"]:
        for provider in providers:
            items.append(
                {
                    "provider_link_id": f"VSPL-{row['inventory_row_id'].split('-')[-1]}-{provider['provider_option_id'].split('-')[-1]}",
                    "inventory_row_id": row["inventory_row_id"],
                    "scope": row["scope"],
                    "provider_option_id": provider["provider_option_id"],
                    "provider_id": provider["provider_id"],
                    "provider_label": provider["provider_label"],
                    "provider_link_status": "PLACEHOLDER_LINK_NOT_SELECTED_NOT_CONFIGURED",
                    "metadata_only": True,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_write_enabled": False,
                    "provider_read_enabled": False,
                    "object_key_bound_to_provider": False,
                    "file_body_persisted": False,
                    "external_delivery_enabled": False,
                    "packet_export_enabled": False,
                    "tower_authorization_required": True,
                    "tower_authorized": False,
                    "safe_to_continue_to_gp043": True,
                }
            )

    return {
        "provider_link_items": items,
        "provider_link_count": len(items),
        "inventory_row_count": inventory_rows["inventory_row_count"],
        "provider_option_count": len(providers),
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_write_enabled_count": 0,
        "provider_read_enabled_count": 0,
        "object_key_bound_to_provider_count": 0,
        "file_body_persisted_count": 0,
        "external_delivery_enabled_count": 0,
        "packet_export_enabled_count": 0,
        "tower_authorization_required_count": len(items),
        "tower_authorized_count": 0,
        "safe_to_continue_provider_links": True,
    }


def _build_checksum_status(inventory_rows: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for row in inventory_rows["inventory_row_items"]:
        items.append(
            {
                "checksum_status_id": f"VSCS-{row['inventory_row_id'].split('-')[-1]}",
                "inventory_row_id": row["inventory_row_id"],
                "checksum_placeholder_id": row["checksum_placeholder_id"],
                "scope": row["scope"],
                "checksum_status_label": "CHECKSUM_PENDING_NOT_PRESENT_NOT_VERIFIED",
                "hash_status_label": "HASH_PENDING_NOT_VERIFIED",
                "hash_algorithm_placeholder": "sha256_placeholder_not_verified",
                "metadata_only": True,
                "checksum_present": False,
                "checksum_verified": False,
                "hash_verified": False,
                "file_body_persisted": False,
                "raw_body_available": False,
                "direct_upload_enabled": False,
                "provider_configured": False,
                "verification_claimed": False,
                "safe_to_continue_to_gp043": True,
            }
        )

    return {
        "checksum_status_items": items,
        "checksum_status_count": len(items),
        "checksum_present_count": 0,
        "checksum_verified_count": 0,
        "hash_verified_count": 0,
        "file_body_persisted_count": 0,
        "raw_body_available_count": 0,
        "direct_upload_enabled_count": 0,
        "provider_configured_count": 0,
        "verification_claimed_count": 0,
        "safe_to_continue_checksum_status": True,
    }


def _build_missing_warnings(inventory_rows: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for row in inventory_rows["inventory_row_items"]:
        for warning_type in WARNING_TYPES:
            items.append(
                {
                    "missing_warning_id": f"VSOW-{row['inventory_row_id'].split('-')[-1]}-{warning_type}",
                    "inventory_row_id": row["inventory_row_id"],
                    "scope": row["scope"],
                    "warning_type": warning_type,
                    "warning_status": "ACTIVE_METADATA_ONLY_WARNING",
                    "metadata_only": True,
                    "blocks_raw_view": True,
                    "blocks_provider_write": True,
                    "blocks_export": True,
                    "blocks_external_delivery": True,
                    "blocks_public_proof": True,
                    "blocks_execution": True,
                    "owner_resolvable_now": False,
                    "tower_authorization_required": True,
                    "safe_to_continue_to_gp043": True,
                }
            )

    return {
        "missing_warning_items": items,
        "missing_warning_count": len(items),
        "warning_type_count": len(WARNING_TYPES),
        "inventory_row_count": inventory_rows["inventory_row_count"],
        "blocks_raw_view_count": len(items),
        "blocks_provider_write_count": len(items),
        "blocks_export_count": len(items),
        "blocks_external_delivery_count": len(items),
        "blocks_public_proof_count": len(items),
        "blocks_execution_count": len(items),
        "owner_resolvable_now_count": 0,
        "tower_authorization_required_count": len(items),
        "safe_to_continue_missing_warnings": True,
    }


def _build_tower_visibility_gates(inventory_rows: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for row in inventory_rows["inventory_row_items"]:
        for gate in VISIBILITY_GATES:
            items.append(
                {
                    "visibility_gate_id": f"VSOVG-{row['inventory_row_id'].split('-')[-1]}-{gate}",
                    "inventory_row_id": row["inventory_row_id"],
                    "scope": row["scope"],
                    "gate_name": gate,
                    "gate_status": "TOWER_VISIBILITY_REQUIRED_NOT_GRANTED",
                    "metadata_only": True,
                    "required": True,
                    "granted": False,
                    "vault_can_override": False,
                    "owner_redacted_preview_allowed": gate == "owner_redacted_preview",
                    "raw_view_allowed": False,
                    "sensitive_visibility_allowed": False,
                    "export_allowed": False,
                    "external_access_allowed": False,
                    "portal_access_allowed": False,
                    "safe_to_continue_to_gp043": True,
                }
            )

    return {
        "tower_visibility_gate_items": items,
        "tower_visibility_gate_count": len(items),
        "visibility_gate_type_count": len(VISIBILITY_GATES),
        "inventory_row_count": inventory_rows["inventory_row_count"],
        "required_gate_count": len(items),
        "granted_gate_count": 0,
        "vault_override_allowed_count": 0,
        "owner_redacted_preview_allowed_count": inventory_rows["inventory_row_count"],
        "raw_view_allowed_count": 0,
        "sensitive_visibility_allowed_count": 0,
        "export_allowed_count": 0,
        "external_access_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "tower_visibility_preserved": True,
        "safe_to_continue_tower_visibility_gates": True,
    }


def _build_next_step(
    inventory_rows: Dict[str, Any],
    provider_links: Dict[str, Any],
    checksum_status: Dict[str, Any],
    missing_warnings: Dict[str, Any],
    tower_visibility_gates: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSONX-001",
            "title": "Prepare storage access request preview",
            "target_pack": "VAULT_GP043",
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSONX-002",
            "title": "Keep inventory metadata-only",
            "target_pack": "VAULT_GP043",
            "status": "METADATA_ONLY_BOUNDARY_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSONX-003",
            "title": "Keep provider write/read locked",
            "target_pack": "VAULT_GP043",
            "status": "PROVIDER_ACCESS_LOCKED",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp043_count": len(items),
        "inventory_row_count": inventory_rows["inventory_row_count"],
        "provider_link_count": provider_links["provider_link_count"],
        "checksum_status_count": checksum_status["checksum_status_count"],
        "missing_warning_count": missing_warnings["missing_warning_count"],
        "tower_visibility_gate_count": tower_visibility_gates["tower_visibility_gate_count"],
        "safe_to_continue_to_gp043": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": "VAULT_GP043",
        "recommended_next_pack_title": "Storage Access Request Preview",
        "owner_notebook_note": "Continue under ARCHIVE VAULT — NEXT PRODUCT DEPTH LAYER. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep inventory rows metadata-only.",
            "Keep provider options as placeholders only.",
            "Keep provider write/read locked.",
            "Keep raw file body storage locked.",
            "Keep direct upload locked.",
            "Keep checksum/hash verification unclaimed.",
            "Keep Tower visibility gates required and ungranted.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_object_inventory_payload())


def get_storage_object_inventory_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "inventory_truth": payload["inventory_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "inventory_routes": payload["inventory_routes"],
        "inventory_counts": payload["inventory_counts"],
        "gp041_connection": payload["gp041_connection"],
    }


def get_storage_object_inventory_rows() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "inventory_rows": payload["inventory_rows"],
    }


def get_storage_object_status_labels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "status_labels": payload["status_labels"],
    }


def get_storage_object_provider_links() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "provider_links": payload["provider_links"],
    }


def get_storage_object_checksum_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "checksum_status": payload["checksum_status"],
    }


def get_storage_object_missing_warnings() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "missing_warnings": payload["missing_warnings"],
    }


def get_storage_object_tower_visibility_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_visibility_gates": payload["tower_visibility_gates"],
    }


def get_storage_object_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp042_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp042_status": payload["gp042_status"],
        "inventory_truth": payload["inventory_truth"],
        "inventory_routes": payload["inventory_routes"],
        "inventory_counts": payload["inventory_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp041_connection": payload["gp041_connection"],
        "next_step": payload["next_step"],
    }


def render_storage_object_inventory_preview_page() -> str:
    payload = clone_payload()
    routes = payload["inventory_routes"]
    counts = payload["inventory_counts"]
    truth = payload["inventory_truth"]
    rows = payload["inventory_rows"]
    checksum = payload["checksum_status"]
    warnings = payload["missing_warnings"]
    next_step = payload["next_step"]

    row_html = "\n".join(_render_inventory_card(item) for item in rows["inventory_row_items"])
    checksum_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['checksum_status_label'])} · {escape(item['hash_status_label'])}</span>
          </div>
          <div class="pill warn">Pending</div>
        </div>
        """
        for item in checksum["checksum_status_items"]
    )

    warning_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['scope'])}</strong>
            <span>{escape(item['warning_type'])}</span>
          </div>
          <div class="pill danger">Active</div>
        </div>
        """
        for item in warnings["missing_warning_items"][:12]
    )

    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Object Inventory Preview · GP042</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 042</div>
        <h1>Storage Object Inventory Preview</h1>
        <p class="hero-copy">
          GP042 previews the future storage object inventory without storing object bodies. It creates inventory rows,
          status labels, provider placeholder links, checksum/hash pending labels, missing object warnings, and Tower visibility gates.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['inventory_row_count']}</strong>
            <span>inventory rows</span>
          </div>
          <div class="metric">
            <strong>{counts['provider_link_count']}</strong>
            <span>provider placeholder links</span>
          </div>
          <div class="metric">
            <strong>{counts['missing_warning_count']}</strong>
            <span>missing warnings</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Inventory preview ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Checksum pending</span>
          <span class="pill danger">No object bodies</span>
          <span class="pill danger">No provider write/read</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Storage Object Inventory Rows</h2>
      <p>Rows are metadata-only. No provider is selected, no object body is persisted, and no checksum/hash is verified.</p>
      <div class="grid">
        {row_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Checksum / Hash Pending</h2>
        <p>Verification labels are visible, but no verification claim is made.</p>
        <div>{checksum_rows}</div>
      </div>
      <div>
        <h2>Missing Object Warnings</h2>
        <p>Warnings block raw view, provider write, export, delivery, proof, and execution.</p>
        <div>{warning_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP043</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP042 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['inventory_rows_route'])}</code>
        <code>{escape(routes['status_labels_route'])}</code>
        <code>{escape(routes['provider_links_route'])}</code>
        <code>{escape(routes['checksum_status_route'])}</code>
        <code>{escape(routes['missing_warnings_route'])}</code>
        <code>{escape(routes['tower_visibility_gates_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp042_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_inventory_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['scope'])}</div>
            <div class="meta">
              Row: <code>{escape(item['inventory_row_id'])}</code><br>
              Status: <code>{escape(item['storage_status_label'])}</code><br>
              Body persisted: <code>{str(item['file_body_persisted']).lower()}</code><br>
              Checksum verified: <code>{str(item['checksum_verified']).lower()}</code><br>
              Provider configured: <code>{str(item['provider_configured']).lower()}</code>
            </div>
          </div>
          <span class="pill warn">Metadata</span>
        </div>
      </article>
    """
