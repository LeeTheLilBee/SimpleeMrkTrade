"""
VAULT GIANT PACK 053 — Storage Provider Risk Matrix

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack deepens GP052 by turning provider criteria into a risk matrix.

Purpose:
- Build metadata-only provider risk cards.
- Build provider risk rollups.
- Build severity placeholders.
- Build mitigation placeholders.
- Build Tower risk review gates.
- Build risk selection blockers.
- Carry forward to GP054.

Important truth:
- GP053 does not select a provider.
- GP053 does not configure a provider.
- GP053 does not enable provider read or write.
- GP053 does not finalize provider scores.
- GP053 does not recommend a provider.
- GP053 does not accept or waive risk.
- GP053 does not approve mitigations.
- GP053 does not view object bodies.
- GP053 does not store raw file bodies.
- GP053 does not unlock direct upload.
- GP053 does not verify checksums/hashes.
- GP053 does not create official receipts.
- GP053 does not finalize receipts.
- GP053 does not close receipts.
- GP053 does not write official audit logs.
- GP053 does not write immutable audit entries.
- GP053 does not grant storage access.
- GP053 does not approve or execute actions.
- GP053 does not export or externally deliver anything.
- GP053 does not open portals.
- GP053 does not create public proof.
- GP053 does not mark Vault done.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict

from vault.storage_provider_criteria_board_service import get_storage_provider_criteria_board_payload


PACK_ID = "VAULT_GP053"
PACK_NAME = "Storage Provider Risk Matrix"
SCHEMA_VERSION = "vault.storage_provider_risk_matrix.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP054_STORAGE_PROVIDER_COMPARISON_BOARD"
NEXT_PACK_TITLE = "Storage Provider Comparison Board"

RISK_CATEGORIES = [
    "tower_authority_risk",
    "privacy_boundary_risk",
    "encryption_risk",
    "audit_trace_risk",
    "object_visibility_risk",
    "export_control_risk",
    "integration_risk",
    "continuity_risk",
]

MITIGATION_FIELDS = [
    "owner_mitigation_note",
    "tower_mitigation_question",
    "technical_mitigation_note",
    "operational_mitigation_note",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_provider_risk_matrix_payload() -> Dict[str, Any]:
    gp052 = get_storage_provider_criteria_board_payload()

    risk_cards = _build_risk_cards(gp052)
    risk_rollups = _build_risk_rollups(risk_cards)
    severity_placeholders = _build_severity_placeholders(risk_cards)
    mitigation_placeholders = _build_mitigation_placeholders(risk_cards)
    tower_review_gates = _build_tower_risk_review_gates(gp052)
    selection_blockers = _build_risk_selection_blockers(gp052)
    next_step = _build_next_step(
        risk_cards,
        risk_rollups,
        severity_placeholders,
        mitigation_placeholders,
        tower_review_gates,
        selection_blockers,
    )

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP052"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_provider_risk_matrix",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "risk_truth": {
            "storage_provider_risk_matrix_ready": True,
            "risk_cards_visible": True,
            "risk_rollups_visible": True,
            "severity_placeholders_visible": True,
            "mitigation_placeholders_visible": True,
            "tower_risk_review_gates_visible": True,
            "risk_selection_blockers_visible": True,
            "metadata_only": True,
            "private_risk_matrix_only": True,
            "provider_candidate_count": risk_cards["provider_candidate_count"],
            "risk_category_count": risk_cards["risk_category_count"],
            "risk_card_count": risk_cards["risk_card_count"],
            "risk_rollup_count": risk_rollups["risk_rollup_count"],
            "severity_placeholder_count": severity_placeholders["severity_placeholder_count"],
            "mitigation_placeholder_count": mitigation_placeholders["mitigation_placeholder_count"],
            "tower_risk_review_gate_count": tower_review_gates["tower_risk_review_gate_count"],
            "risk_selection_blocker_count": selection_blockers["risk_selection_blocker_count"],
            "severity_present_count": 0,
            "severity_finalized_count": 0,
            "risk_score_present_count": 0,
            "risk_score_finalized_count": 0,
            "risk_accepted_count": 0,
            "risk_waived_count": 0,
            "mitigation_present_count": 0,
            "mitigation_approved_count": 0,
            "provider_recommended_count": 0,
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
            "safe_to_continue_to_gp054": True,
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
            "tower_owns_provider_criteria_review": True,
            "tower_owns_provider_risk_review": True,
            "tower_owns_risk_acceptance_authority": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_select_provider_without_tower": False,
            "vault_can_configure_provider_without_tower": False,
            "vault_can_finalize_provider_score": False,
            "vault_can_recommend_provider": False,
            "vault_can_accept_or_waive_risk": False,
            "vault_can_approve_mitigation": False,
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
            "provider_selection_default": "risk_matrix_only_no_provider_selected",
            "provider_configuration_default": "locked_not_configured",
            "provider_read_default": "locked_not_enabled",
            "provider_write_default": "locked_not_enabled",
            "provider_score_default": "placeholder_only_not_finalized",
            "provider_recommendation_default": "blocked_no_recommendation",
            "risk_default": "placeholder_only_not_accepted_not_waived",
            "mitigation_default": "placeholder_only_not_approved",
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
        "risk_routes": {
            "room_title": "Vault Storage Provider Risk Matrix",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-provider-risk-matrix",
            "json_route": "/vault/storage-provider-risk-matrix.json",
            "risk_cards_route": "/vault/storage-provider-risk-cards.json",
            "risk_rollups_route": "/vault/storage-provider-risk-rollups.json",
            "severity_placeholders_route": "/vault/storage-provider-risk-severity-placeholders.json",
            "mitigation_placeholders_route": "/vault/storage-provider-risk-mitigation-placeholders.json",
            "tower_review_gates_route": "/vault/storage-provider-risk-tower-review-gates.json",
            "selection_blockers_route": "/vault/storage-provider-risk-selection-blockers.json",
            "next_step_route": "/vault/storage-provider-risk-next-step.json",
            "gp053_status_route": "/vault/gp053-status.json",
        },
        "risk_counts": {
            "provider_candidate_count": risk_cards["provider_candidate_count"],
            "risk_category_count": risk_cards["risk_category_count"],
            "risk_card_count": risk_cards["risk_card_count"],
            "risk_rollup_count": risk_rollups["risk_rollup_count"],
            "severity_placeholder_count": severity_placeholders["severity_placeholder_count"],
            "mitigation_placeholder_count": mitigation_placeholders["mitigation_placeholder_count"],
            "tower_risk_review_gate_count": tower_review_gates["tower_risk_review_gate_count"],
            "risk_selection_blocker_count": selection_blockers["risk_selection_blocker_count"],
            "severity_present_count": 0,
            "severity_finalized_count": 0,
            "risk_score_present_count": 0,
            "risk_score_finalized_count": 0,
            "risk_accepted_count": 0,
            "risk_waived_count": 0,
            "mitigation_present_count": 0,
            "mitigation_approved_count": 0,
            "provider_recommended_count": 0,
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
        "risk_cards": risk_cards,
        "risk_rollups": risk_rollups,
        "severity_placeholders": severity_placeholders,
        "mitigation_placeholders": mitigation_placeholders,
        "tower_review_gates": tower_review_gates,
        "selection_blockers": selection_blockers,
        "next_step": next_step,
        "gp052_connection": {
            "gp052_pack_id": gp052["pack"]["id"],
            "gp052_ready": gp052["gp052_status"]["ready"],
            "gp052_section": gp052["pack"]["section"],
            "gp052_section_title": gp052["pack"]["section_title"],
            "gp052_section_range": gp052["pack"]["section_range"],
            "gp052_safe_to_continue": gp052["gp052_status"]["safe_to_continue_to_gp053"],
            "gp052_vault_done": gp052["gp052_status"]["vault_done"],
            "gp052_provider_candidate_count": gp052["criteria_counts"]["provider_candidate_count"],
            "gp052_criteria_card_count": gp052["criteria_counts"]["criteria_card_count"],
            "gp052_scoring_placeholder_count": gp052["criteria_counts"]["scoring_placeholder_count"],
            "gp052_selection_blocker_count": gp052["criteria_counts"]["selection_blocker_count"],
            "gp052_provider_selected_count": gp052["criteria_counts"]["provider_selected_count"],
            "gp052_provider_recommended_count": gp052["criteria_counts"]["provider_recommended_count"],
        },
        "gp053_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_provider_risk_matrix_ready": True,
            "safe_to_continue_to_gp054": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_risk_matrix": True,
            "private_risk_matrix_only": True,
            "risk_cards_ready": True,
            "risk_rollups_ready": True,
            "severity_placeholders_ready": True,
            "mitigation_placeholders_ready": True,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
            "provider_score_finalized": False,
            "provider_recommended": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp053",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
    }

    return payload


def _candidate_types_from_gp052(gp052: Dict[str, Any]) -> list[str]:
    items = gp052["criteria_board"]["criteria_card_items"]
    candidate_types = []
    seen = set()
    for item in items:
        candidate_type = item["candidate_type"]
        if candidate_type not in seen:
            seen.add(candidate_type)
            candidate_types.append(candidate_type)
    return candidate_types


def _build_risk_cards(gp052: Dict[str, Any]) -> Dict[str, Any]:
    candidate_types = _candidate_types_from_gp052(gp052)
    cards = []

    for candidate_type in candidate_types:
        candidate_id = _candidate_id_for_type(gp052, candidate_type)
        for category in RISK_CATEGORIES:
            cards.append(
                {
                    "risk_card_id": f"VSPRM-{len(cards) + 1:03d}",
                    "provider_candidate_id": candidate_id,
                    "candidate_type": candidate_type,
                    "risk_category": category,
                    "risk_card_status": "RISK_PLACEHOLDER_ONLY_NOT_SCORED_NOT_ACCEPTED_NOT_WAIVED",
                    "metadata_only": True,
                    "private_risk_matrix_only": True,
                    "risk_visible": True,
                    "risk_required": True,
                    "severity_present": False,
                    "severity_level": None,
                    "severity_finalized": False,
                    "risk_score_present": False,
                    "risk_score_value": None,
                    "risk_score_finalized": False,
                    "risk_accepted": False,
                    "risk_waived": False,
                    "mitigation_required": True,
                    "mitigation_present": False,
                    "mitigation_approved": False,
                    "tower_risk_review_required": True,
                    "tower_risk_review_granted": False,
                    "provider_recommended": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "provider_read_enabled": False,
                    "provider_write_enabled": False,
                    "provider_object_read_claimed": False,
                    "provider_connection_tested": False,
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
                    "safe_to_continue_to_gp054": True,
                }
            )

    return {
        "risk_card_items": cards,
        "risk_card_count": len(cards),
        "provider_candidate_count": len(candidate_types),
        "risk_category_count": len(RISK_CATEGORIES),
        "risk_visible_count": len(cards),
        "risk_required_count": len(cards),
        "severity_present_count": 0,
        "severity_finalized_count": 0,
        "risk_score_present_count": 0,
        "risk_score_finalized_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_required_count": len(cards),
        "mitigation_present_count": 0,
        "mitigation_approved_count": 0,
        "tower_risk_review_required_count": len(cards),
        "tower_risk_review_granted_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "provider_object_read_claimed_count": 0,
        "provider_connection_tested_count": 0,
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
        "safe_to_continue_risk_cards": True,
    }


def _candidate_id_for_type(gp052: Dict[str, Any], candidate_type: str) -> str:
    for item in gp052["criteria_board"]["criteria_card_items"]:
        if item["candidate_type"] == candidate_type:
            return item["provider_candidate_id"]
    return "VSPC-UNKNOWN"


def _build_risk_rollups(risk_cards: Dict[str, Any]) -> Dict[str, Any]:
    grouped: Dict[str, list] = {}
    for item in risk_cards["risk_card_items"]:
        grouped.setdefault(item["risk_category"], []).append(item)

    rollups = []
    for index, (category, items) in enumerate(sorted(grouped.items()), start=1):
        rollups.append(
            {
                "risk_rollup_id": f"VSPRR-{index:03d}",
                "risk_category": category,
                "candidate_count": len(items),
                "risk_card_count": len(items),
                "rollup_status": "RISK_PLACEHOLDER_ONLY_NOT_SCORED_NOT_ACCEPTED_NOT_WAIVED",
                "metadata_only": True,
                "risk_required_count": len(items),
                "severity_present_count": 0,
                "severity_finalized_count": 0,
                "risk_score_present_count": 0,
                "risk_score_finalized_count": 0,
                "risk_accepted_count": 0,
                "risk_waived_count": 0,
                "mitigation_present_count": 0,
                "mitigation_approved_count": 0,
                "provider_recommended_count": 0,
                "provider_selected_count": 0,
                "provider_configured_count": 0,
                "provider_read_enabled_count": 0,
                "provider_write_enabled_count": 0,
                "object_body_view_enabled_count": 0,
                "export_allowed_count": 0,
                "execution_allowed_count": 0,
                "safe_to_continue_to_gp054": True,
            }
        )

    return {
        "risk_rollup_items": rollups,
        "risk_rollup_count": len(rollups),
        "risk_card_count": risk_cards["risk_card_count"],
        "provider_candidate_count": risk_cards["provider_candidate_count"],
        "risk_required_count": risk_cards["risk_required_count"],
        "severity_present_count": 0,
        "severity_finalized_count": 0,
        "risk_score_present_count": 0,
        "risk_score_finalized_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_present_count": 0,
        "mitigation_approved_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "object_body_view_enabled_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_risk_rollups": True,
    }


def _build_severity_placeholders(risk_cards: Dict[str, Any]) -> Dict[str, Any]:
    placeholders = []

    for item in risk_cards["risk_card_items"]:
        placeholders.append(
            {
                "severity_placeholder_id": f"VSPSV-{item['risk_card_id'].split('-')[-1]}",
                "risk_card_id": item["risk_card_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "risk_category": item["risk_category"],
                "severity_status": "EMPTY_NOT_ASSIGNED_NOT_FINALIZED",
                "metadata_only": True,
                "severity_required": True,
                "severity_present": False,
                "severity_level": None,
                "severity_finalized": False,
                "risk_score_present": False,
                "risk_score_finalized": False,
                "risk_accepted": False,
                "risk_waived": False,
                "provider_recommended": False,
                "provider_selected": False,
                "tower_risk_review_required": True,
                "tower_risk_review_granted": False,
                "reviewer_bound": False,
                "reviewer_confirmed": False,
                "safe_to_continue_to_gp054": True,
            }
        )

    return {
        "severity_placeholder_items": placeholders,
        "severity_placeholder_count": len(placeholders),
        "severity_required_count": len(placeholders),
        "severity_present_count": 0,
        "severity_finalized_count": 0,
        "risk_score_present_count": 0,
        "risk_score_finalized_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "tower_risk_review_required_count": len(placeholders),
        "tower_risk_review_granted_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "safe_to_continue_severity_placeholders": True,
    }


def _build_mitigation_placeholders(risk_cards: Dict[str, Any]) -> Dict[str, Any]:
    placeholders = []

    for item in risk_cards["risk_card_items"]:
        for field in MITIGATION_FIELDS:
            placeholders.append(
                {
                    "mitigation_placeholder_id": f"VSPMP-{item['risk_card_id'].split('-')[-1]}-{field}",
                    "risk_card_id": item["risk_card_id"],
                    "provider_candidate_id": item["provider_candidate_id"],
                    "candidate_type": item["candidate_type"],
                    "risk_category": item["risk_category"],
                    "mitigation_field": field,
                    "mitigation_status": "EMPTY_NOT_REVIEWED_NOT_APPROVED",
                    "metadata_only": True,
                    "mitigation_required": True,
                    "mitigation_present": False,
                    "mitigation_approved": False,
                    "risk_accepted": False,
                    "risk_waived": False,
                    "provider_recommended": False,
                    "provider_selected": False,
                    "provider_configured": False,
                    "tower_risk_review_required": True,
                    "tower_risk_review_granted": False,
                    "reviewer_bound": False,
                    "reviewer_confirmed": False,
                    "safe_to_continue_to_gp054": True,
                }
            )

    return {
        "mitigation_placeholder_items": placeholders,
        "mitigation_placeholder_count": len(placeholders),
        "mitigation_field_type_count": len(MITIGATION_FIELDS),
        "risk_card_count": risk_cards["risk_card_count"],
        "mitigation_required_count": len(placeholders),
        "mitigation_present_count": 0,
        "mitigation_approved_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "tower_risk_review_required_count": len(placeholders),
        "tower_risk_review_granted_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "safe_to_continue_mitigation_placeholders": True,
    }


def _build_tower_risk_review_gates(gp052: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp052["tower_review_gates"]["tower_review_gate_items"]
    gates = []

    for item in source_items:
        gates.append(
            {
                "tower_risk_review_gate_id": f"VSPTRR-{item['tower_review_gate_id'].split('-', 1)[-1]}",
                "tower_review_gate_id": item["tower_review_gate_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "gate_name": item["gate_name"],
                "gate_status": "TOWER_RISK_REVIEW_REQUIRED_NOT_GRANTED",
                "metadata_only": True,
                "required": True,
                "granted": False,
                "vault_can_override": False,
                "risk_score_finalized": False,
                "risk_accepted": False,
                "risk_waived": False,
                "mitigation_approved": False,
                "provider_score_finalized": False,
                "provider_recommended": False,
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
                "safe_to_continue_to_gp054": True,
            }
        )

    return {
        "tower_risk_review_gate_items": gates,
        "tower_risk_review_gate_count": len(gates),
        "required_count": len(gates),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
        "risk_score_finalized_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_approved_count": 0,
        "provider_score_finalized_count": 0,
        "provider_recommended_count": 0,
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
        "safe_to_continue_tower_risk_review_gates": True,
    }


def _build_risk_selection_blockers(gp052: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp052["selection_blockers"]["selection_blocker_items"]
    blockers = []

    for item in source_items:
        blockers.append(
            {
                "risk_selection_blocker_id": f"VSPRSB-{item['selection_blocker_id'].split('-', 1)[-1]}",
                "selection_blocker_id": item["selection_blocker_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "lock_name": item["lock_name"],
                "blocker_status": "ACTIVE_RISK_MATRIX_BLOCKER",
                "metadata_only": True,
                "active": True,
                "blocks_severity_finalize": True,
                "blocks_risk_score_finalize": True,
                "blocks_risk_acceptance": True,
                "blocks_risk_waiver": True,
                "blocks_mitigation_approval": True,
                "blocks_provider_recommendation": True,
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
                "safe_to_continue_to_gp054": True,
            }
        )

    return {
        "risk_selection_blocker_items": blockers,
        "risk_selection_blocker_count": len(blockers),
        "active_blocker_count": len(blockers),
        "blocks_severity_finalize_count": len(blockers),
        "blocks_risk_score_finalize_count": len(blockers),
        "blocks_risk_acceptance_count": len(blockers),
        "blocks_risk_waiver_count": len(blockers),
        "blocks_mitigation_approval_count": len(blockers),
        "blocks_provider_recommendation_count": len(blockers),
        "blocks_provider_selection_count": len(blockers),
        "blocks_provider_configuration_count": len(blockers),
        "blocks_provider_read_count": len(blockers),
        "blocks_provider_write_count": len(blockers),
        "blocks_object_body_view_count": len(blockers),
        "blocks_raw_file_body_storage_count": len(blockers),
        "blocks_direct_upload_count": len(blockers),
        "blocks_checksum_hash_verification_claim_count": len(blockers),
        "blocks_export_count": len(blockers),
        "blocks_external_delivery_count": len(blockers),
        "blocks_execution_count": len(blockers),
        "blocks_vault_done_count": len(blockers),
        "owner_resolvable_now_count": 0,
        "tower_authority_required_count": len(blockers),
        "safe_to_continue_risk_selection_blockers": True,
    }


def _build_next_step(
    risk_cards: Dict[str, Any],
    risk_rollups: Dict[str, Any],
    severity_placeholders: Dict[str, Any],
    mitigation_placeholders: Dict[str, Any],
    tower_review_gates: Dict[str, Any],
    selection_blockers: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSPRMNX-001",
            "title": "Build storage provider comparison board",
            "target_pack": NEXT_PACK,
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPRMNX-002",
            "title": "Keep risk placeholders unaccepted and unwaived",
            "target_pack": NEXT_PACK,
            "status": "RISK_PLACEHOLDERS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPRMNX-003",
            "title": "Keep provider selection blocked",
            "target_pack": NEXT_PACK,
            "status": "RISK_BLOCKERS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp054_count": len(items),
        "risk_card_count": risk_cards["risk_card_count"],
        "risk_rollup_count": risk_rollups["risk_rollup_count"],
        "severity_placeholder_count": severity_placeholders["severity_placeholder_count"],
        "mitigation_placeholder_count": mitigation_placeholders["mitigation_placeholder_count"],
        "tower_risk_review_gate_count": tower_review_gates["tower_risk_review_gate_count"],
        "risk_selection_blocker_count": selection_blockers["risk_selection_blocker_count"],
        "safe_to_continue_to_gp054": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": NEXT_PACK,
        "recommended_next_pack_title": NEXT_PACK_TITLE,
        "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep provider risk matrix metadata-only.",
            "Keep risk cards required but unscored.",
            "Keep severity placeholders empty and unfinalized.",
            "Keep risk scores empty and unfinalized.",
            "Do not accept risk.",
            "Do not waive risk.",
            "Do not approve mitigation.",
            "Do not finalize provider scores.",
            "Do not recommend a provider.",
            "Do not select a provider.",
            "Do not configure a provider.",
            "Do not enable provider read.",
            "Do not enable provider write.",
            "Do not claim provider object reads.",
            "Do not show object bodies.",
            "Do not persist raw file bodies.",
            "Do not unlock direct upload.",
            "Do not claim checksum/hash verification.",
            "Keep Tower risk review gates required and ungranted.",
            "Keep risk selection blockers active.",
            "Keep official receipts, finalized receipts, and receipt close locked.",
            "Keep official audit logs and immutable audit writes locked.",
            "Keep access grants, action approval, and action execution locked.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_provider_risk_matrix_payload())


def get_storage_provider_risk_matrix_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "risk_truth": payload["risk_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "risk_routes": payload["risk_routes"],
        "risk_counts": payload["risk_counts"],
        "gp052_connection": payload["gp052_connection"],
    }


def get_storage_provider_risk_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "risk_cards": payload["risk_cards"],
    }


def get_storage_provider_risk_rollups() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "risk_rollups": payload["risk_rollups"],
    }


def get_storage_provider_risk_severity_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "severity_placeholders": payload["severity_placeholders"],
    }


def get_storage_provider_risk_mitigation_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "mitigation_placeholders": payload["mitigation_placeholders"],
    }


def get_storage_provider_risk_tower_review_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_review_gates": payload["tower_review_gates"],
    }


def get_storage_provider_risk_selection_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "selection_blockers": payload["selection_blockers"],
    }


def get_storage_provider_risk_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp053_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp053_status": payload["gp053_status"],
        "risk_truth": payload["risk_truth"],
        "risk_routes": payload["risk_routes"],
        "risk_counts": payload["risk_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "risk_cards": payload["risk_cards"],
        "risk_rollups": payload["risk_rollups"],
        "severity_placeholders": payload["severity_placeholders"],
        "mitigation_placeholders": payload["mitigation_placeholders"],
        "tower_review_gates": payload["tower_review_gates"],
        "selection_blockers": payload["selection_blockers"],
        "next_step": payload["next_step"],
        "gp052_connection": payload["gp052_connection"],
    }


def render_storage_provider_risk_matrix_page() -> str:
    payload = clone_payload()
    routes = payload["risk_routes"]
    counts = payload["risk_counts"]
    truth = payload["risk_truth"]
    cards = payload["risk_cards"]
    rollups = payload["risk_rollups"]
    blockers = payload["selection_blockers"]
    next_step = payload["next_step"]

    card_html = "\n".join(_render_risk_card(item) for item in cards["risk_card_items"][:12])
    rollup_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['risk_category'])}</strong>
            <span>{item['risk_card_count']} candidates · {escape(item['rollup_status'])}</span>
          </div>
          <div class="pill danger">Unaccepted</div>
        </div>
        """
        for item in rollups["risk_rollup_items"]
    )
    blocker_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['candidate_type'])}</strong>
            <span>{escape(item['lock_name'])} · {escape(item['blocker_status'])}</span>
          </div>
          <div class="pill danger">Blocked</div>
        </div>
        """
        for item in blockers["risk_selection_blocker_items"][:12]
    )
    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Provider Risk Matrix · GP053</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 053</div>
        <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
        <h1>Storage Provider Risk Matrix</h1>
        <p class="hero-copy">
          GP053 organizes storage provider risk into a metadata-only matrix. Risks are visible,
          but no severity is finalized, no risk is accepted or waived, no mitigation is approved,
          and no provider is recommended or selected.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['risk_card_count']}</strong>
            <span>risk cards</span>
          </div>
          <div class="metric">
            <strong>{counts['mitigation_placeholder_count']}</strong>
            <span>mitigation placeholders</span>
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
          <span class="pill ok">Risk matrix ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No risk accepted</span>
          <span class="pill danger">No mitigation approved</span>
          <span class="pill danger">No provider selected</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Risk Cards</h2>
      <p>Risks are required placeholders. They are not scored, accepted, waived, or mitigated.</p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Risk Rollups</h2>
        <p>Each risk category remains visible but unresolved.</p>
        <div>{rollup_rows}</div>
      </div>
      <div>
        <h2>Risk Selection Blockers</h2>
        <p>Blockers prevent risk acceptance, mitigation approval, provider recommendation, provider selection, export, and execution.</p>
        <div>{blocker_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP054</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP053 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['risk_cards_route'])}</code>
        <code>{escape(routes['risk_rollups_route'])}</code>
        <code>{escape(routes['severity_placeholders_route'])}</code>
        <code>{escape(routes['mitigation_placeholders_route'])}</code>
        <code>{escape(routes['tower_review_gates_route'])}</code>
        <code>{escape(routes['selection_blockers_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp053_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_risk_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['risk_category'])}</div>
            <div class="meta">
              Card: <code>{escape(item['risk_card_id'])}</code><br>
              Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
              Status: <code>{escape(item['risk_card_status'])}</code><br>
              Accepted: <code>{str(item['risk_accepted']).lower()}</code><br>
              Waived: <code>{str(item['risk_waived']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Unaccepted</span>
        </div>
      </article>
    """
