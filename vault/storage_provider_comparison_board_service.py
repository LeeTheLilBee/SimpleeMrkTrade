"""
VAULT GIANT PACK 054 — Storage Provider Comparison Board

CURRENT SECTION:
Archive Vault — Storage Provider Prep Layer
GP051-GP060

This pack deepens GP053 by turning risk and criteria prep into a comparison board.

Purpose:
- Build metadata-only provider comparison rows.
- Build criteria comparison rollups.
- Build risk comparison rollups.
- Build ranking placeholders.
- Build Tower comparison review gates.
- Build provider recommendation blockers.
- Carry forward to GP055.

Important truth:
- GP054 does not select a provider.
- GP054 does not configure a provider.
- GP054 does not enable provider read or write.
- GP054 does not finalize provider scores.
- GP054 does not finalize rankings.
- GP054 does not recommend a provider.
- GP054 does not accept or waive risk.
- GP054 does not approve mitigations.
- GP054 does not view object bodies.
- GP054 does not store raw file bodies.
- GP054 does not unlock direct upload.
- GP054 does not verify checksums/hashes.
- GP054 does not create official receipts.
- GP054 does not finalize receipts.
- GP054 does not close receipts.
- GP054 does not write official audit logs.
- GP054 does not write immutable audit entries.
- GP054 does not grant storage access.
- GP054 does not approve or execute actions.
- GP054 does not export or externally deliver anything.
- GP054 does not open portals.
- GP054 does not create public proof.
- GP054 does not mark Vault done.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.storage_provider_risk_matrix_service import get_storage_provider_risk_matrix_payload


PACK_ID = "VAULT_GP054"
PACK_NAME = "Storage Provider Comparison Board"
SCHEMA_VERSION = "vault.storage_provider_comparison_board.v1"

SECTION_ID = "ARCHIVE_VAULT_STORAGE_PROVIDER_PREP_LAYER"
SECTION_TITLE = "Archive Vault — Storage Provider Prep Layer"
SECTION_RANGE = "GP051-GP060"

NEXT_PACK = "VAULT_GP055_STORAGE_PROVIDER_DECISION_DRAFT"
NEXT_PACK_TITLE = "Storage Provider Decision Draft"

COMPARISON_FACTORS = [
    "criteria_fit_placeholder",
    "risk_posture_placeholder",
    "tower_authority_readiness_placeholder",
    "audit_trace_readiness_placeholder",
    "integration_readiness_placeholder",
    "continuity_readiness_placeholder",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_storage_provider_comparison_board_payload() -> Dict[str, Any]:
    gp053 = get_storage_provider_risk_matrix_payload()

    comparison_rows = _build_comparison_rows(gp053)
    criteria_rollups = _build_criteria_comparison_rollups(gp053)
    risk_rollups = _build_risk_comparison_rollups(gp053)
    ranking_placeholders = _build_ranking_placeholders(comparison_rows)
    tower_review_gates = _build_tower_comparison_review_gates(gp053)
    recommendation_blockers = _build_recommendation_blockers(gp053)
    next_step = _build_next_step(
        comparison_rows,
        criteria_rollups,
        risk_rollups,
        ranking_placeholders,
        tower_review_gates,
        recommendation_blockers,
    )

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP053"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "storage_provider_comparison_board",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "comparison_truth": {
            "storage_provider_comparison_board_ready": True,
            "comparison_rows_visible": True,
            "criteria_comparison_rollups_visible": True,
            "risk_comparison_rollups_visible": True,
            "ranking_placeholders_visible": True,
            "tower_comparison_review_gates_visible": True,
            "recommendation_blockers_visible": True,
            "metadata_only": True,
            "private_comparison_board_only": True,
            "provider_candidate_count": comparison_rows["provider_candidate_count"],
            "comparison_row_count": comparison_rows["comparison_row_count"],
            "comparison_factor_count": comparison_rows["comparison_factor_count"],
            "criteria_comparison_rollup_count": criteria_rollups["criteria_comparison_rollup_count"],
            "risk_comparison_rollup_count": risk_rollups["risk_comparison_rollup_count"],
            "ranking_placeholder_count": ranking_placeholders["ranking_placeholder_count"],
            "tower_comparison_review_gate_count": tower_review_gates["tower_comparison_review_gate_count"],
            "recommendation_blocker_count": recommendation_blockers["recommendation_blocker_count"],
            "comparison_score_present_count": 0,
            "comparison_score_finalized_count": 0,
            "rank_present_count": 0,
            "rank_finalized_count": 0,
            "provider_recommended_count": 0,
            "provider_selected_count": 0,
            "provider_configured_count": 0,
            "provider_write_enabled_count": 0,
            "provider_read_enabled_count": 0,
            "provider_object_read_claimed_count": 0,
            "provider_connection_tested_count": 0,
            "risk_accepted_count": 0,
            "risk_waived_count": 0,
            "mitigation_approved_count": 0,
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
            "safe_to_continue_to_gp055": True,
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
            "tower_owns_provider_comparison_review": True,
            "tower_owns_provider_recommendation_authority": True,
            "vault_owns_tower_permissions": False,
            "vault_can_override_tower_storage_authority": False,
            "vault_can_select_provider_without_tower": False,
            "vault_can_configure_provider_without_tower": False,
            "vault_can_finalize_provider_score": False,
            "vault_can_finalize_provider_ranking": False,
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
            "provider_selection_default": "comparison_board_only_no_provider_selected",
            "provider_configuration_default": "locked_not_configured",
            "provider_read_default": "locked_not_enabled",
            "provider_write_default": "locked_not_enabled",
            "provider_score_default": "placeholder_only_not_finalized",
            "provider_ranking_default": "placeholder_only_not_finalized",
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
        "comparison_routes": {
            "room_title": "Vault Storage Provider Comparison Board",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/storage-provider-comparison-board",
            "json_route": "/vault/storage-provider-comparison-board.json",
            "comparison_rows_route": "/vault/storage-provider-comparison-rows.json",
            "criteria_comparison_rollups_route": "/vault/storage-provider-criteria-comparison-rollups.json",
            "risk_comparison_rollups_route": "/vault/storage-provider-risk-comparison-rollups.json",
            "ranking_placeholders_route": "/vault/storage-provider-ranking-placeholders.json",
            "tower_review_gates_route": "/vault/storage-provider-comparison-tower-review-gates.json",
            "recommendation_blockers_route": "/vault/storage-provider-recommendation-blockers.json",
            "next_step_route": "/vault/storage-provider-comparison-next-step.json",
            "gp054_status_route": "/vault/gp054-status.json",
        },
        "comparison_counts": {
            "provider_candidate_count": comparison_rows["provider_candidate_count"],
            "comparison_row_count": comparison_rows["comparison_row_count"],
            "comparison_factor_count": comparison_rows["comparison_factor_count"],
            "criteria_comparison_rollup_count": criteria_rollups["criteria_comparison_rollup_count"],
            "risk_comparison_rollup_count": risk_rollups["risk_comparison_rollup_count"],
            "ranking_placeholder_count": ranking_placeholders["ranking_placeholder_count"],
            "tower_comparison_review_gate_count": tower_review_gates["tower_comparison_review_gate_count"],
            "recommendation_blocker_count": recommendation_blockers["recommendation_blocker_count"],
            "comparison_score_present_count": 0,
            "comparison_score_finalized_count": 0,
            "rank_present_count": 0,
            "rank_finalized_count": 0,
            "provider_recommended_count": 0,
            "provider_selected_count": 0,
            "provider_configured_count": 0,
            "provider_read_enabled_count": 0,
            "provider_write_enabled_count": 0,
            "provider_object_read_claimed_count": 0,
            "provider_connection_tested_count": 0,
            "risk_accepted_count": 0,
            "risk_waived_count": 0,
            "mitigation_approved_count": 0,
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
        "comparison_rows": comparison_rows,
        "criteria_rollups": criteria_rollups,
        "risk_rollups": risk_rollups,
        "ranking_placeholders": ranking_placeholders,
        "tower_review_gates": tower_review_gates,
        "recommendation_blockers": recommendation_blockers,
        "next_step": next_step,
        "gp053_connection": {
            "gp053_pack_id": gp053["pack"]["id"],
            "gp053_ready": gp053["gp053_status"]["ready"],
            "gp053_section": gp053["pack"]["section"],
            "gp053_section_title": gp053["pack"]["section_title"],
            "gp053_section_range": gp053["pack"]["section_range"],
            "gp053_safe_to_continue": gp053["gp053_status"]["safe_to_continue_to_gp054"],
            "gp053_vault_done": gp053["gp053_status"]["vault_done"],
            "gp053_provider_candidate_count": gp053["risk_counts"]["provider_candidate_count"],
            "gp053_risk_card_count": gp053["risk_counts"]["risk_card_count"],
            "gp053_risk_rollup_count": gp053["risk_counts"]["risk_rollup_count"],
            "gp053_severity_placeholder_count": gp053["risk_counts"]["severity_placeholder_count"],
            "gp053_mitigation_placeholder_count": gp053["risk_counts"]["mitigation_placeholder_count"],
            "gp053_risk_selection_blocker_count": gp053["risk_counts"]["risk_selection_blocker_count"],
            "gp053_provider_selected_count": gp053["risk_counts"]["provider_selected_count"],
            "gp053_provider_recommended_count": gp053["risk_counts"]["provider_recommended_count"],
        },
        "gp054_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "storage_provider_comparison_board_ready": True,
            "safe_to_continue_to_gp055": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "metadata_only_comparison_board": True,
            "private_comparison_board_only": True,
            "comparison_rows_ready": True,
            "criteria_comparison_rollups_ready": True,
            "risk_comparison_rollups_ready": True,
            "ranking_placeholders_ready": True,
            "provider_ranking_finalized": False,
            "provider_score_finalized": False,
            "provider_recommended": False,
            "provider_selected": False,
            "provider_configured": False,
            "provider_write_enabled": False,
            "provider_read_enabled": False,
            "provider_object_read_claimed": False,
            "provider_connection_tested": False,
            "risk_accepted": False,
            "risk_waived": False,
            "mitigation_approved": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp054",
            "next_pack": NEXT_PACK,
            "next_pack_title": NEXT_PACK_TITLE,
        },
    }

    return payload


def _candidate_summary_from_gp053(gp053: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_candidate: Dict[str, Dict[str, Any]] = {}

    for item in gp053["risk_cards"]["risk_card_items"]:
        candidate_id = item["provider_candidate_id"]
        if candidate_id not in by_candidate:
            by_candidate[candidate_id] = {
                "provider_candidate_id": candidate_id,
                "candidate_type": item["candidate_type"],
                "risk_card_count": 0,
            }
        by_candidate[candidate_id]["risk_card_count"] += 1

    return list(by_candidate.values())


def _build_comparison_rows(gp053: Dict[str, Any]) -> Dict[str, Any]:
    candidates = _candidate_summary_from_gp053(gp053)
    rows = []

    for candidate in candidates:
        rows.append(
            {
                "comparison_row_id": f"VSPCMP-{len(rows) + 1:03d}",
                "provider_candidate_id": candidate["provider_candidate_id"],
                "candidate_type": candidate["candidate_type"],
                "comparison_status": "COMPARISON_PLACEHOLDER_ONLY_NOT_RANKED_NOT_RECOMMENDED",
                "metadata_only": True,
                "private_comparison_board_only": True,
                "comparison_visible": True,
                "criteria_card_count": 8,
                "risk_card_count": candidate["risk_card_count"],
                "comparison_factor_count": len(COMPARISON_FACTORS),
                "comparison_score_present": False,
                "comparison_score_value": None,
                "comparison_score_finalized": False,
                "rank_present": False,
                "rank_value": None,
                "rank_finalized": False,
                "provider_recommended": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "provider_object_read_claimed": False,
                "provider_connection_tested": False,
                "risk_accepted": False,
                "risk_waived": False,
                "mitigation_approved": False,
                "tower_comparison_review_required": True,
                "tower_comparison_review_granted": False,
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
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "comparison_row_items": rows,
        "comparison_row_count": len(rows),
        "provider_candidate_count": len(candidates),
        "comparison_factor_count": len(COMPARISON_FACTORS),
        "comparison_visible_count": len(rows),
        "criteria_card_count": 40,
        "risk_card_count": 40,
        "comparison_score_present_count": 0,
        "comparison_score_finalized_count": 0,
        "rank_present_count": 0,
        "rank_finalized_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "provider_object_read_claimed_count": 0,
        "provider_connection_tested_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_approved_count": 0,
        "tower_comparison_review_required_count": len(rows),
        "tower_comparison_review_granted_count": 0,
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
        "safe_to_continue_comparison_rows": True,
    }


def _build_criteria_comparison_rollups(gp053: Dict[str, Any]) -> Dict[str, Any]:
    gp052_connection = gp053["gp052_connection"]
    rows = []

    criteria_names = [
        "audit_trace_support_required",
        "encryption_support_required",
        "export_lock_compatibility_required",
        "metadata_first_support_required",
        "no_public_access_default_required",
        "object_body_locked_until_authorized",
        "private_vault_boundary_required",
        "tower_authority_required",
    ]

    for criterion in criteria_names:
        rows.append(
            {
                "criteria_comparison_rollup_id": f"VSPCCR-{len(rows) + 1:03d}",
                "criterion": criterion,
                "candidate_count": gp052_connection["gp052_provider_candidate_count"],
                "criteria_status": "REQUIRED_NOT_SATISFIED_NOT_VERIFIED_NOT_RANKED",
                "metadata_only": True,
                "criteria_present": True,
                "criteria_satisfied_count": 0,
                "criteria_verified_count": 0,
                "comparison_score_present_count": 0,
                "comparison_score_finalized_count": 0,
                "rank_present_count": 0,
                "rank_finalized_count": 0,
                "provider_recommended_count": 0,
                "provider_selected_count": 0,
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "criteria_comparison_rollup_items": rows,
        "criteria_comparison_rollup_count": len(rows),
        "provider_candidate_count": gp052_connection["gp052_provider_candidate_count"],
        "criteria_present_count": len(rows),
        "criteria_satisfied_count": 0,
        "criteria_verified_count": 0,
        "comparison_score_present_count": 0,
        "comparison_score_finalized_count": 0,
        "rank_present_count": 0,
        "rank_finalized_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "safe_to_continue_criteria_comparison_rollups": True,
    }


def _build_risk_comparison_rollups(gp053: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp053["risk_rollups"]["risk_rollup_items"]
    rows = []

    for item in source_items:
        rows.append(
            {
                "risk_comparison_rollup_id": f"VSPRCR-{len(rows) + 1:03d}",
                "risk_category": item["risk_category"],
                "candidate_count": item["candidate_count"],
                "risk_status": "RISK_PLACEHOLDER_NOT_ACCEPTED_NOT_WAIVED_NOT_RANKED",
                "metadata_only": True,
                "risk_present": True,
                "severity_present_count": 0,
                "severity_finalized_count": 0,
                "risk_score_present_count": 0,
                "risk_score_finalized_count": 0,
                "risk_accepted_count": 0,
                "risk_waived_count": 0,
                "mitigation_approved_count": 0,
                "comparison_score_present_count": 0,
                "comparison_score_finalized_count": 0,
                "rank_present_count": 0,
                "rank_finalized_count": 0,
                "provider_recommended_count": 0,
                "provider_selected_count": 0,
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "risk_comparison_rollup_items": rows,
        "risk_comparison_rollup_count": len(rows),
        "provider_candidate_count": gp053["risk_counts"]["provider_candidate_count"],
        "risk_present_count": len(rows),
        "severity_present_count": 0,
        "severity_finalized_count": 0,
        "risk_score_present_count": 0,
        "risk_score_finalized_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_approved_count": 0,
        "comparison_score_present_count": 0,
        "comparison_score_finalized_count": 0,
        "rank_present_count": 0,
        "rank_finalized_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "safe_to_continue_risk_comparison_rollups": True,
    }


def _build_ranking_placeholders(comparison_rows: Dict[str, Any]) -> Dict[str, Any]:
    placeholders = []

    for item in comparison_rows["comparison_row_items"]:
        placeholders.append(
            {
                "ranking_placeholder_id": f"VSPRANK-{item['comparison_row_id'].split('-')[-1]}",
                "comparison_row_id": item["comparison_row_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "ranking_status": "EMPTY_NOT_RANKED_NOT_FINALIZED",
                "metadata_only": True,
                "rank_required": True,
                "rank_present": False,
                "rank_value": None,
                "rank_finalized": False,
                "comparison_score_present": False,
                "comparison_score_finalized": False,
                "provider_recommended": False,
                "provider_selected": False,
                "provider_configured": False,
                "tower_comparison_review_required": True,
                "tower_comparison_review_granted": False,
                "reviewer_bound": False,
                "reviewer_confirmed": False,
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "ranking_placeholder_items": placeholders,
        "ranking_placeholder_count": len(placeholders),
        "rank_required_count": len(placeholders),
        "rank_present_count": 0,
        "rank_finalized_count": 0,
        "comparison_score_present_count": 0,
        "comparison_score_finalized_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "tower_comparison_review_required_count": len(placeholders),
        "tower_comparison_review_granted_count": 0,
        "reviewer_bound_count": 0,
        "reviewer_confirmed_count": 0,
        "safe_to_continue_ranking_placeholders": True,
    }


def _build_tower_comparison_review_gates(gp053: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp053["tower_review_gates"]["tower_risk_review_gate_items"]
    gates = []

    for item in source_items:
        gates.append(
            {
                "tower_comparison_review_gate_id": f"VSPTCG-{item['tower_risk_review_gate_id'].split('-', 1)[-1]}",
                "tower_risk_review_gate_id": item["tower_risk_review_gate_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "gate_name": item["gate_name"],
                "gate_status": "TOWER_COMPARISON_REVIEW_REQUIRED_NOT_GRANTED",
                "metadata_only": True,
                "required": True,
                "granted": False,
                "vault_can_override": False,
                "rank_finalized": False,
                "comparison_score_finalized": False,
                "provider_recommended": False,
                "provider_selected": False,
                "provider_configured": False,
                "provider_read_enabled": False,
                "provider_write_enabled": False,
                "risk_accepted": False,
                "risk_waived": False,
                "mitigation_approved": False,
                "object_body_view_enabled": False,
                "official_receipt_claimed": False,
                "official_audit_log_written": False,
                "access_granted": False,
                "export_allowed": False,
                "execution_allowed": False,
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "tower_comparison_review_gate_items": gates,
        "tower_comparison_review_gate_count": len(gates),
        "required_count": len(gates),
        "granted_count": 0,
        "vault_override_allowed_count": 0,
        "rank_finalized_count": 0,
        "comparison_score_finalized_count": 0,
        "provider_recommended_count": 0,
        "provider_selected_count": 0,
        "provider_configured_count": 0,
        "provider_read_enabled_count": 0,
        "provider_write_enabled_count": 0,
        "risk_accepted_count": 0,
        "risk_waived_count": 0,
        "mitigation_approved_count": 0,
        "object_body_view_enabled_count": 0,
        "official_receipt_claimed_count": 0,
        "official_audit_log_written_count": 0,
        "access_granted_count": 0,
        "export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_tower_comparison_review_gates": True,
    }


def _build_recommendation_blockers(gp053: Dict[str, Any]) -> Dict[str, Any]:
    source_items = gp053["selection_blockers"]["risk_selection_blocker_items"]
    blockers = []

    for item in source_items:
        blockers.append(
            {
                "recommendation_blocker_id": f"VSPREC-{item['risk_selection_blocker_id'].split('-', 1)[-1]}",
                "risk_selection_blocker_id": item["risk_selection_blocker_id"],
                "provider_candidate_id": item["provider_candidate_id"],
                "candidate_type": item["candidate_type"],
                "lock_name": item["lock_name"],
                "blocker_status": "ACTIVE_COMPARISON_RECOMMENDATION_BLOCKER",
                "metadata_only": True,
                "active": True,
                "blocks_rank_finalize": True,
                "blocks_comparison_score_finalize": True,
                "blocks_provider_recommendation": True,
                "blocks_provider_selection": True,
                "blocks_provider_configuration": True,
                "blocks_provider_read": True,
                "blocks_provider_write": True,
                "blocks_risk_acceptance": True,
                "blocks_risk_waiver": True,
                "blocks_mitigation_approval": True,
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
                "safe_to_continue_to_gp055": True,
            }
        )

    return {
        "recommendation_blocker_items": blockers,
        "recommendation_blocker_count": len(blockers),
        "active_blocker_count": len(blockers),
        "blocks_rank_finalize_count": len(blockers),
        "blocks_comparison_score_finalize_count": len(blockers),
        "blocks_provider_recommendation_count": len(blockers),
        "blocks_provider_selection_count": len(blockers),
        "blocks_provider_configuration_count": len(blockers),
        "blocks_provider_read_count": len(blockers),
        "blocks_provider_write_count": len(blockers),
        "blocks_risk_acceptance_count": len(blockers),
        "blocks_risk_waiver_count": len(blockers),
        "blocks_mitigation_approval_count": len(blockers),
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
        "safe_to_continue_recommendation_blockers": True,
    }


def _build_next_step(
    comparison_rows: Dict[str, Any],
    criteria_rollups: Dict[str, Any],
    risk_rollups: Dict[str, Any],
    ranking_placeholders: Dict[str, Any],
    tower_review_gates: Dict[str, Any],
    recommendation_blockers: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_step_id": "VSPCBNX-001",
            "title": "Build storage provider decision draft",
            "target_pack": NEXT_PACK,
            "status": "READY_FOR_NEXT_PACK",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPCBNX-002",
            "title": "Keep comparison rows unranked and unrecommended",
            "target_pack": NEXT_PACK,
            "status": "COMPARISON_PLACEHOLDERS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
        {
            "next_step_id": "VSPCBNX-003",
            "title": "Keep provider recommendation blocked",
            "target_pack": NEXT_PACK,
            "status": "RECOMMENDATION_BLOCKERS_CARRIED_FORWARD",
            "safe_to_continue": True,
            "vault_done": False,
            "clouds_should_continue": False,
        },
    ]

    return {
        "next_step_items": items,
        "next_step_count": len(items),
        "ready_for_gp055_count": len(items),
        "comparison_row_count": comparison_rows["comparison_row_count"],
        "criteria_comparison_rollup_count": criteria_rollups["criteria_comparison_rollup_count"],
        "risk_comparison_rollup_count": risk_rollups["risk_comparison_rollup_count"],
        "ranking_placeholder_count": ranking_placeholders["ranking_placeholder_count"],
        "tower_comparison_review_gate_count": tower_review_gates["tower_comparison_review_gate_count"],
        "recommendation_blocker_count": recommendation_blockers["recommendation_blocker_count"],
        "safe_to_continue_to_gp055": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "recommended_next_pack": NEXT_PACK,
        "recommended_next_pack_title": NEXT_PACK_TITLE,
        "owner_notebook_note": "Continue under ARCHIVE VAULT — STORAGE PROVIDER PREP LAYER / GP051-GP060. Do not switch to Clouds unless Solice explicitly asks.",
        "carry_forward_rules": [
            "Keep provider comparison board metadata-only.",
            "Keep comparison rows visible but unranked.",
            "Keep ranking placeholders empty and unfinalized.",
            "Do not finalize comparison scores.",
            "Do not finalize provider rankings.",
            "Do not recommend a provider.",
            "Do not select a provider.",
            "Do not configure a provider.",
            "Do not enable provider read.",
            "Do not enable provider write.",
            "Do not accept risk.",
            "Do not waive risk.",
            "Do not approve mitigation.",
            "Do not claim provider object reads.",
            "Do not show object bodies.",
            "Do not persist raw file bodies.",
            "Do not unlock direct upload.",
            "Do not claim checksum/hash verification.",
            "Keep Tower comparison review gates required and ungranted.",
            "Keep recommendation blockers active.",
            "Keep official receipts, finalized receipts, and receipt close locked.",
            "Keep official audit logs and immutable audit writes locked.",
            "Keep access grants, action approval, and action execution locked.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this as safe to continue, not Vault done.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_storage_provider_comparison_board_payload())


def get_storage_provider_comparison_board_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "comparison_truth": payload["comparison_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "comparison_routes": payload["comparison_routes"],
        "comparison_counts": payload["comparison_counts"],
        "gp053_connection": payload["gp053_connection"],
    }


def get_storage_provider_comparison_rows() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "comparison_rows": payload["comparison_rows"],
    }


def get_storage_provider_criteria_comparison_rollups() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "criteria_rollups": payload["criteria_rollups"],
    }


def get_storage_provider_risk_comparison_rollups() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "risk_rollups": payload["risk_rollups"],
    }


def get_storage_provider_ranking_placeholders() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "ranking_placeholders": payload["ranking_placeholders"],
    }


def get_storage_provider_comparison_tower_review_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_review_gates": payload["tower_review_gates"],
    }


def get_storage_provider_recommendation_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "recommendation_blockers": payload["recommendation_blockers"],
    }


def get_storage_provider_comparison_next_step() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_step": payload["next_step"],
    }


def get_gp054_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp054_status": payload["gp054_status"],
        "comparison_truth": payload["comparison_truth"],
        "comparison_routes": payload["comparison_routes"],
        "comparison_counts": payload["comparison_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "comparison_rows": payload["comparison_rows"],
        "criteria_rollups": payload["criteria_rollups"],
        "risk_rollups": payload["risk_rollups"],
        "ranking_placeholders": payload["ranking_placeholders"],
        "tower_review_gates": payload["tower_review_gates"],
        "recommendation_blockers": payload["recommendation_blockers"],
        "next_step": payload["next_step"],
        "gp053_connection": payload["gp053_connection"],
    }


def render_storage_provider_comparison_board_page() -> str:
    payload = clone_payload()
    routes = payload["comparison_routes"]
    counts = payload["comparison_counts"]
    truth = payload["comparison_truth"]
    rows = payload["comparison_rows"]
    criteria_rollups = payload["criteria_rollups"]
    blockers = payload["recommendation_blockers"]
    next_step = payload["next_step"]

    row_html = "\n".join(_render_comparison_row(item) for item in rows["comparison_row_items"])
    criteria_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['criterion'])}</strong>
            <span>{item['candidate_count']} candidates · {escape(item['criteria_status'])}</span>
          </div>
          <div class="pill danger">Unverified</div>
        </div>
        """
        for item in criteria_rollups["criteria_comparison_rollup_items"]
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
        for item in blockers["recommendation_blocker_items"][:12]
    )
    carry_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in next_step["carry_forward_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Storage Provider Comparison Board · GP054</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 054</div>
        <div class="eyebrow">Storage Provider Prep Layer · GP051-GP060</div>
        <h1>Storage Provider Comparison Board</h1>
        <p class="hero-copy">
          GP054 compares provider candidates using metadata-only rows. Comparison rows are visible,
          but rankings are empty, no comparison score is finalized, and no provider is recommended or selected.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['comparison_row_count']}</strong>
            <span>comparison rows</span>
          </div>
          <div class="metric">
            <strong>{counts['ranking_placeholder_count']}</strong>
            <span>ranking placeholders</span>
          </div>
          <div class="metric">
            <strong>{counts['provider_recommended_count']}</strong>
            <span>providers recommended</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Comparison board ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill danger">No ranking finalized</span>
          <span class="pill danger">No provider recommended</span>
          <span class="pill danger">No provider selected</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Comparison Rows</h2>
      <p>Provider candidates are visible for comparison only. No rankings, recommendations, selections, or provider actions are unlocked.</p>
      <div class="grid">
        {row_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Criteria Comparison Rollups</h2>
        <p>Each criterion remains required, unsatisfied, unverified, and unranked.</p>
        <div>{criteria_rows}</div>
      </div>
      <div>
        <h2>Recommendation Blockers</h2>
        <p>Blockers prevent ranking finalization, provider recommendation, provider selection, export, and execution.</p>
        <div>{blocker_rows}</div>
      </div>
    </section>

    <section class="section">
      <h2>Carry Forward to GP055</h2>
      <p>{escape(next_step['owner_notebook_note'])}</p>
      <ul>
        {carry_rules}
      </ul>
    </section>

    <section class="section">
      <h2>GP054 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['comparison_rows_route'])}</code>
        <code>{escape(routes['criteria_comparison_rollups_route'])}</code>
        <code>{escape(routes['risk_comparison_rollups_route'])}</code>
        <code>{escape(routes['ranking_placeholders_route'])}</code>
        <code>{escape(routes['tower_review_gates_route'])}</code>
        <code>{escape(routes['recommendation_blockers_route'])}</code>
        <code>{escape(routes['next_step_route'])}</code>
        <code>{escape(routes['gp054_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_comparison_row(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['candidate_type'])}</div>
            <div class="meta">
              Row: <code>{escape(item['comparison_row_id'])}</code><br>
              Candidate: <code>{escape(item['provider_candidate_id'])}</code><br>
              Status: <code>{escape(item['comparison_status'])}</code><br>
              Ranked: <code>{str(item['rank_present']).lower()}</code><br>
              Recommended: <code>{str(item['provider_recommended']).lower()}</code>
            </div>
          </div>
          <span class="pill danger">Unranked</span>
        </div>
      </article>
    """
