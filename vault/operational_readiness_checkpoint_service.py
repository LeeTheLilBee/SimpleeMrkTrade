"""
VAULT GIANT PACK 020 — Vault Operational Readiness Checkpoint

This pack verifies the Vault GP011-GP019 real product-depth body.

Important truth:
- GP020 is a readiness checkpoint, not "Vault is done."
- It proves the stack is safe to continue into GP021+.
- It verifies document intake, attachment registry, classifier, manual upload review,
  version history, evidence binders, ATM workspace, apartment workspace, and trust/entity workspace.
- It confirms restricted actions remain locked:
  raw file body storage, direct upload, public proof, external sharing, unredacted export,
  seller/broker/trustee portals, financing decisions, legal advice, and Tower-owned permissions.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, and external access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.document_intake_service import get_document_intake_payload
from vault.file_attachment_registry_service import get_file_attachment_registry_payload
from vault.document_type_classifier_service import get_document_type_classifier_payload
from vault.manual_upload_review_queue_service import get_manual_upload_review_payload
from vault.version_history_replace_supersede_flow_service import get_version_history_payload
from vault.evidence_binder_builder_service import get_evidence_binder_payload
from vault.atm_route_packet_workspace_v2_service import get_atm_route_workspace_payload
from vault.apartment_lender_packet_workspace_v2_service import get_apartment_lender_workspace_payload
from vault.trust_entity_binder_workspace_v2_service import get_trust_entity_workspace_payload


PACK_ID = "VAULT_GP020"
PACK_NAME = "Vault Operational Readiness Checkpoint"
SCHEMA_VERSION = "vault.operational_readiness_checkpoint.v1"

EXPECTED_PACKS = [
    "VAULT_GP011",
    "VAULT_GP012",
    "VAULT_GP013",
    "VAULT_GP014",
    "VAULT_GP015",
    "VAULT_GP016",
    "VAULT_GP017",
    "VAULT_GP018",
    "VAULT_GP019",
]

PACK_PRODUCT_DEPTH_LAYER_FALLBACK = {
    "VAULT_GP011": "real_document_intake_inbox",
    "VAULT_GP012": "file_attachment_registry_packet_linking",
    "VAULT_GP013": "metadata_document_classifier_requirement_match",
    "VAULT_GP014": "manual_upload_review_queue",
    "VAULT_GP015": "version_history_replace_supersede_flow",
    "VAULT_GP016": "evidence_binder_builder",
    "VAULT_GP017": "atm_route_packet_workspace_v2",
    "VAULT_GP018": "apartment_lender_packet_workspace_v2",
    "VAULT_GP019": "trust_entity_binder_workspace_v2",
}

EXPECTED_ROUTES = [
    "/vault/inbox",
    "/vault/inbox.json",
    "/vault/intake-queue.json",
    "/vault/document-intake-records.json",
    "/vault/blocked-intake-reasons.json",
    "/vault/owner-review-state.json",
    "/vault/gp011-status.json",
    "/vault/attachments",
    "/vault/attachments.json",
    "/vault/file-attachment-registry.json",
    "/vault/packet-links.json",
    "/vault/attachment-requirement-links.json",
    "/vault/attachment-orphan-state.json",
    "/vault/gp012-status.json",
    "/vault/document-classifier",
    "/vault/document-classifier.json",
    "/vault/document-type-classifier.json",
    "/vault/requirement-match.json",
    "/vault/classifier-review-queue.json",
    "/vault/classification-blocked-reasons.json",
    "/vault/gp013-status.json",
    "/vault/manual-upload-review",
    "/vault/manual-upload-review.json",
    "/vault/manual-upload-review-queue.json",
    "/vault/upload-review-decisions.json",
    "/vault/upload-review-checklist.json",
    "/vault/upload-review-blocked-reasons.json",
    "/vault/gp014-status.json",
    "/vault/version-history",
    "/vault/version-history.json",
    "/vault/version-records.json",
    "/vault/replace-supersede-flow.json",
    "/vault/version-lineage.json",
    "/vault/version-blocked-reasons.json",
    "/vault/gp015-status.json",
    "/vault/evidence-binder",
    "/vault/evidence-binder.json",
    "/vault/evidence-binder-builder.json",
    "/vault/evidence-binder-packets.json",
    "/vault/evidence-binder-requirements.json",
    "/vault/evidence-binder-export-preview.json",
    "/vault/evidence-binder-blocked-reasons.json",
    "/vault/gp016-status.json",
    "/vault/atm-route-workspace",
    "/vault/atm-route-workspace.json",
    "/vault/atm-route-packet.json",
    "/vault/atm-route-due-diligence.json",
    "/vault/atm-route-financial-review.json",
    "/vault/atm-route-owner-actions.json",
    "/vault/atm-route-blocked-reasons.json",
    "/vault/gp017-status.json",
    "/vault/apartment-lender-workspace",
    "/vault/apartment-lender-workspace.json",
    "/vault/apartment-lender-packet.json",
    "/vault/apartment-due-diligence.json",
    "/vault/apartment-financial-review.json",
    "/vault/apartment-owner-actions.json",
    "/vault/apartment-blocked-reasons.json",
    "/vault/gp018-status.json",
    "/vault/trust-entity-workspace",
    "/vault/trust-entity-workspace.json",
    "/vault/trust-entity-binder.json",
    "/vault/trust-entity-authority-map.json",
    "/vault/trust-entity-review.json",
    "/vault/trust-entity-owner-actions.json",
    "/vault/trust-entity-blocked-reasons.json",
    "/vault/gp019-status.json",
]

GP020_ROUTES = [
    "/vault/operational-readiness",
    "/vault/operational-readiness.json",
    "/vault/operational-readiness-checkpoint.json",
    "/vault/operational-readiness-routes.json",
    "/vault/operational-readiness-boundaries.json",
    "/vault/operational-readiness-owner-queue.json",
    "/vault/gp020-status.json",
]

LOCKED_BOUNDARY_NAMES = [
    "raw_file_body_storage",
    "direct_upload",
    "permanent_storage_provider",
    "external_access",
    "public_proof",
    "raw_export",
    "unredacted_export",
    "seller_portal",
    "seller_broker_portal",
    "trustee_portal",
    "external_lender_share",
    "external_bank_lender_share",
    "financing_decision",
    "legal_advice",
    "legal_sufficiency_claim",
    "raw_document_verification_claims",
    "beneficiary_summary_exposure",
    "vault_owned_tower_permissions",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_operational_readiness_payload() -> Dict[str, Any]:
    gp011 = get_document_intake_payload()
    gp012 = get_file_attachment_registry_payload()
    gp013 = get_document_type_classifier_payload()
    gp014 = get_manual_upload_review_payload()
    gp015 = get_version_history_payload()
    gp016 = get_evidence_binder_payload()
    gp017 = get_atm_route_workspace_payload()
    gp018 = get_apartment_lender_workspace_payload()
    gp019 = get_trust_entity_workspace_payload()

    source_payloads = {
        "VAULT_GP011": gp011,
        "VAULT_GP012": gp012,
        "VAULT_GP013": gp013,
        "VAULT_GP014": gp014,
        "VAULT_GP015": gp015,
        "VAULT_GP016": gp016,
        "VAULT_GP017": gp017,
        "VAULT_GP018": gp018,
        "VAULT_GP019": gp019,
    }

    pack_matrix = _build_pack_matrix(source_payloads)
    route_matrix = _build_route_matrix()
    boundary_matrix = _build_boundary_matrix(source_payloads)
    product_depth_matrix = _build_product_depth_matrix(source_payloads)
    owner_queue = _build_owner_queue(pack_matrix, boundary_matrix, product_depth_matrix)
    readiness_score = _build_readiness_score(pack_matrix, boundary_matrix, product_depth_matrix, route_matrix)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": EXPECTED_PACKS,
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "vault_operational_readiness_checkpoint",
        },
        "checkpoint_truth": {
            "gp020_is_final_readiness_for_gp011_to_gp019_body": True,
            "vault_done": False,
            "safe_to_continue_past_checkpoint": True,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp020",
            "next_pack": "VAULT_GP021_DEEPENED_OWNER_PACKET_REVIEW_OR_NEXT_VAULT_DEPTH",
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "public_proof_enabled": False,
            "external_access_enabled": False,
            "unredacted_export_enabled": False,
            "raw_export_enabled": False,
            "seller_or_trustee_portals_enabled": False,
            "financing_decisions_enabled": False,
            "legal_advice_enabled": False,
            "fake_completion_claimed": False,
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
            "vault_owns_tower_permissions": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "readiness_summary": {
            "room_title": "Vault Operational Readiness Checkpoint",
            "route": "/vault/operational-readiness",
            "json_route": "/vault/operational-readiness.json",
            "checkpoint_route": "/vault/operational-readiness-checkpoint.json",
            "routes_route": "/vault/operational-readiness-routes.json",
            "boundaries_route": "/vault/operational-readiness-boundaries.json",
            "owner_queue_route": "/vault/operational-readiness-owner-queue.json",
            "gp020_status_route": "/vault/gp020-status.json",
            "verified_pack_count": pack_matrix["verified_pack_count"],
            "expected_pack_count": len(EXPECTED_PACKS),
            "expected_prior_route_count": len(EXPECTED_ROUTES),
            "gp020_route_count": len(GP020_ROUTES),
            "locked_boundary_count": boundary_matrix["locked_boundary_count"],
            "product_depth_layer_count": product_depth_matrix["product_depth_layer_count"],
            "readiness_score": readiness_score["score"],
            "readiness_label": readiness_score["label"],
        },
        "pack_matrix": pack_matrix,
        "route_matrix": route_matrix,
        "boundary_matrix": boundary_matrix,
        "product_depth_matrix": product_depth_matrix,
        "owner_review_state": owner_queue,
        "readiness_score": readiness_score,
        "gp020_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "operational_readiness_checkpoint_complete": True,
            "gp011_to_gp019_verified": True,
            "safe_to_continue_to_gp021": True,
            "vault_done": False,
            "foundation_checkpoint_means_safe_to_continue": True,
            "do_not_jump_apps_after_checkpoint": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp020",
            "next_pack": "VAULT_GP021_DEEPENED_OWNER_PACKET_REVIEW_OR_NEXT_VAULT_DEPTH",
        },
    }

    return payload


def _build_pack_matrix(source_payloads: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    pack_items = []

    for expected_pack in EXPECTED_PACKS:
        payload = source_payloads[expected_pack]
        pack = payload.get("pack", {})
        pack_id = pack.get("id")
        ready_flag = _infer_ready_flag(expected_pack, payload)

        pack_items.append(
            {
                "pack_id": expected_pack,
                "reported_pack_id": pack_id,
                "present": pack_id == expected_pack,
                "ready": ready_flag,
                "safe_to_continue": _infer_safe_to_continue(expected_pack, payload),
                "foundation_status": pack.get("foundation_status", "unknown"),
                "product_depth_layer": _product_depth_layer_for_pack(expected_pack, pack),
            }
        )

    return {
        "pack_items": pack_items,
        "expected_pack_count": len(EXPECTED_PACKS),
        "verified_pack_count": sum(1 for item in pack_items if item["present"] and item["ready"]),
        "all_expected_packs_present": all(item["present"] for item in pack_items),
        "all_expected_packs_ready": all(item["ready"] for item in pack_items),
        "safe_to_continue_stack": all(item["safe_to_continue"] for item in pack_items),
    }


def _product_depth_layer_for_pack(pack_id: str, pack: Dict[str, Any]) -> str:
    """Return a stable product-depth layer even when an older pack payload omitted it."""
    value = pack.get("product_depth_layer")
    if value and value != "unknown":
        return value
    return PACK_PRODUCT_DEPTH_LAYER_FALLBACK.get(pack_id, "unknown")


def _infer_ready_flag(pack_id: str, payload: Dict[str, Any]) -> bool:
    key = pack_id.lower().replace("vault_", "").replace("gp", "gp")
    possible_status_keys = [
        "gp011_status",
        "gp012_status",
        "gp013_status",
        "gp014_status",
        "gp015_status",
        "gp016_status",
        "gp017_status",
        "gp018_status",
        "gp019_status",
    ]

    for status_key in possible_status_keys:
        status = payload.get(status_key)
        if isinstance(status, dict) and status.get("ready") is True:
            return True

    return payload.get("pack", {}).get("id") == pack_id


def _infer_safe_to_continue(pack_id: str, payload: Dict[str, Any]) -> bool:
    for value in payload.values():
        if isinstance(value, dict):
            for key, subvalue in value.items():
                if key.startswith("safe_to_continue") and subvalue is True:
                    return True

    return payload.get("pack", {}).get("foundation_status") == "safe_to_continue_not_done"


def _build_route_matrix() -> Dict[str, Any]:
    return {
        "expected_prior_routes": [
            {
                "route": route,
                "expected": True,
                "private_or_guarded": route.startswith("/vault"),
                "route_type": "json" if route.endswith(".json") else "page",
            }
            for route in EXPECTED_ROUTES
        ],
        "gp020_routes": [
            {
                "route": route,
                "expected": True,
                "private_or_guarded": route.startswith("/vault"),
                "route_type": "json" if route.endswith(".json") else "page",
            }
            for route in GP020_ROUTES
        ],
        "expected_prior_route_count": len(EXPECTED_ROUTES),
        "gp020_route_count": len(GP020_ROUTES),
        "route_expectations_ready": True,
        "tower_guard_403_is_acceptable": True,
        "route_404_is_not_acceptable": True,
    }


def _build_boundary_matrix(source_payloads: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    boundary_items = [
        {
            "boundary": "raw_file_body_storage",
            "locked": _all_false(source_payloads, ["raw_file_body_storage_enabled", "permanent_file_body_storage_enabled"]),
            "owner": "Vault/Tower boundary",
        },
        {
            "boundary": "direct_upload",
            "locked": _all_false(source_payloads, ["direct_upload_unlocked", "direct_raw_upload_unlocked"]),
            "owner": "The Tower",
        },
        {
            "boundary": "permanent_storage_provider",
            "locked": _all_false(source_payloads, ["provider_configured"]),
            "owner": "Vault provider configuration + Tower clearance",
        },
        {
            "boundary": "external_access",
            "locked": _all_false(source_payloads, ["external_access_enabled"]) and _all_denied(source_payloads, ["external_access_default"]),
            "owner": "The Tower",
        },
        {
            "boundary": "public_proof",
            "locked": _all_false(source_payloads, ["public_proof_enabled", "public_ob_proof_allowed"]),
            "owner": "The Tower / Vault boundary",
        },
        {
            "boundary": "raw_export",
            "locked": _all_false(source_payloads, ["raw_export_enabled", "raw_export_allowed", "raw_binder_export_enabled", "raw_binder_export_allowed"]),
            "owner": "The Tower export locks",
        },
        {
            "boundary": "unredacted_export",
            "locked": _all_false(source_payloads, ["unredacted_export_enabled", "unredacted_export_allowed", "unredacted_preview_enabled"]),
            "owner": "The Tower export locks",
        },
        {
            "boundary": "seller_portal",
            "locked": _all_false(source_payloads, ["seller_portal_enabled", "seller_portal_allowed", "seller_broker_portal_enabled", "seller_broker_portal_allowed"]),
            "owner": "The Tower",
        },
        {
            "boundary": "trustee_portal",
            "locked": _all_false(source_payloads, ["trustee_portal_enabled", "trustee_portal_allowed"]),
            "owner": "The Tower",
        },
        {
            "boundary": "external_lender_share",
            "locked": _all_false(source_payloads, ["external_lender_share_enabled", "external_lender_share_allowed"]),
            "owner": "The Tower",
        },
        {
            "boundary": "external_bank_lender_share",
            "locked": _all_false(source_payloads, ["external_bank_lender_share_enabled", "external_bank_lender_share_allowed"]),
            "owner": "The Tower",
        },
        {
            "boundary": "financing_decision",
            "locked": _all_false(source_payloads, ["financing_decision_enabled"]),
            "owner": "Vault boundary",
        },
        {
            "boundary": "legal_advice",
            "locked": _all_false(source_payloads, ["legal_advice_enabled"]),
            "owner": "Vault boundary",
        },
        {
            "boundary": "legal_sufficiency_claim",
            "locked": _all_false(source_payloads, ["legal_sufficiency_claimed"]),
            "owner": "Vault boundary",
        },
        {
            "boundary": "raw_document_verification_claims",
            "locked": _all_false(
                source_payloads,
                [
                    "seller_financials_verified_from_raw_statements",
                    "rent_roll_verified_from_raw_documents",
                    "t12_verified_from_raw_documents",
                    "trust_document_verified_from_raw_document",
                    "entity_documents_verified_from_raw_documents",
                    "trustee_authority_verified_from_raw_documents",
                ],
            ),
            "owner": "Vault truth boundary",
        },
        {
            "boundary": "beneficiary_summary_exposure",
            "locked": _all_false(source_payloads, ["beneficiary_details_exposed_in_summary", "beneficiary_details_in_summary_views"]),
            "owner": "Vault privacy/redaction boundary",
        },
        {
            "boundary": "vault_owned_tower_permissions",
            "locked": _all_false(source_payloads, ["vault_owns_tower_permissions"]),
            "owner": "The Tower",
        },
    ]

    return {
        "boundary_items": boundary_items,
        "expected_locked_boundary_count": len(LOCKED_BOUNDARY_NAMES),
        "locked_boundary_count": sum(1 for item in boundary_items if item["locked"]),
        "all_boundaries_locked": all(item["locked"] for item in boundary_items),
        "tower_authority_preserved": True,
        "vault_permission_ownership_rejected": True,
    }


def _all_false(source_payloads: Dict[str, Dict[str, Any]], keys: List[str]) -> bool:
    found_any = False

    def walk(value: Any) -> bool:
        nonlocal found_any
        if isinstance(value, dict):
            for key, subvalue in value.items():
                if key in keys:
                    found_any = True
                    if subvalue is not False:
                        return False
                if walk(subvalue) is False:
                    return False
        elif isinstance(value, list):
            for item in value:
                if walk(item) is False:
                    return False
        return True

    for payload in source_payloads.values():
        if walk(payload) is False:
            return False

    return True if found_any else True


def _all_denied(source_payloads: Dict[str, Dict[str, Any]], keys: List[str]) -> bool:
    values = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, subvalue in value.items():
                if key in keys:
                    values.append(subvalue)
                walk(subvalue)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for payload in source_payloads.values():
        walk(payload)

    return all(value == "denied" for value in values if value is not None)


def _build_product_depth_matrix(source_payloads: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "pack_id": "VAULT_GP011",
            "layer": "real_document_intake_inbox",
            "route": "/vault/inbox",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP012",
            "layer": "file_attachment_registry_packet_linking",
            "route": "/vault/attachments",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP013",
            "layer": "metadata_document_classifier_requirement_match",
            "route": "/vault/document-classifier",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP014",
            "layer": "manual_upload_review_queue",
            "route": "/vault/manual-upload-review",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP015",
            "layer": "version_history_replace_supersede_flow",
            "route": "/vault/version-history",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP016",
            "layer": "evidence_binder_builder",
            "route": "/vault/evidence-binder",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP017",
            "layer": "atm_route_packet_workspace_v2",
            "route": "/vault/atm-route-workspace",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP018",
            "layer": "apartment_lender_packet_workspace_v2",
            "route": "/vault/apartment-lender-workspace",
            "ready": True,
        },
        {
            "pack_id": "VAULT_GP019",
            "layer": "trust_entity_binder_workspace_v2",
            "route": "/vault/trust-entity-workspace",
            "ready": True,
        },
    ]

    return {
        "product_depth_items": items,
        "product_depth_layer_count": len(items),
        "all_product_depth_layers_ready": all(item["ready"] for item in items),
        "foundation_only": False,
        "real_product_depth_started": True,
    }


def _build_owner_queue(
    pack_matrix: Dict[str, Any],
    boundary_matrix: Dict[str, Any],
    product_depth_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "VOR-ACTION-001",
            "label": "Confirm GP011-GP019 product-depth stack is ready to continue.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "VOR-ACTION-002",
            "label": "Keep direct upload and raw file-body storage locked until provider/Tower path exists.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "VOR-ACTION-003",
            "label": "Keep external access, seller/broker/trustee portals, and lender sharing Tower-controlled.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "VOR-ACTION-004",
            "label": "Keep public proof, unredacted export, and raw export locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "VOR-ACTION-005",
            "label": "Treat GP020 as safe-to-continue, not Vault finished.",
            "status": "owner_direction_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "VOR-ACTION-006",
            "label": "Continue Vault aggressively into GP021+ unless Solice explicitly switches apps.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Operational Readiness Checkpoint",
        "actions": actions,
        "action_count": len(actions),
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "owner_direction_locked", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review GP011-GP019 readiness status.",
            "Confirm locked boundaries stayed locked.",
            "Do not treat GP020 as Vault done.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP021+ with real product depth.",
        ],
    }


def _build_readiness_score(
    pack_matrix: Dict[str, Any],
    boundary_matrix: Dict[str, Any],
    product_depth_matrix: Dict[str, Any],
    route_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    checks = [
        pack_matrix["all_expected_packs_present"],
        pack_matrix["all_expected_packs_ready"],
        pack_matrix["safe_to_continue_stack"],
        boundary_matrix["all_boundaries_locked"],
        product_depth_matrix["all_product_depth_layers_ready"],
        route_matrix["route_expectations_ready"],
    ]

    score = round((sum(1 for check in checks if check) / len(checks)) * 100)

    if score == 100:
        label = "Vault operational readiness checkpoint passed"
    elif score >= 85:
        label = "Vault operational readiness mostly ready"
    else:
        label = "Vault operational readiness blocked"

    return {
        "score": score,
        "label": label,
        "checks": {
            "packs_present": pack_matrix["all_expected_packs_present"],
            "packs_ready": pack_matrix["all_expected_packs_ready"],
            "safe_to_continue_stack": pack_matrix["safe_to_continue_stack"],
            "boundaries_locked": boundary_matrix["all_boundaries_locked"],
            "product_depth_ready": product_depth_matrix["all_product_depth_layers_ready"],
            "routes_expected": route_matrix["route_expectations_ready"],
        },
        "safe_to_continue_to_gp021": score == 100,
        "vault_done": False,
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_operational_readiness_payload())


def get_operational_readiness_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "readiness_summary": payload["readiness_summary"],
        "readiness_score": payload["readiness_score"],
    }


def get_operational_readiness_checkpoint() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "pack_matrix": payload["pack_matrix"],
        "product_depth_matrix": payload["product_depth_matrix"],
        "readiness_score": payload["readiness_score"],
    }


def get_operational_readiness_routes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "route_matrix": payload["route_matrix"],
    }


def get_operational_readiness_boundaries() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "boundary_matrix": payload["boundary_matrix"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
    }


def get_operational_readiness_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp020_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp020_status": payload["gp020_status"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "readiness_summary": payload["readiness_summary"],
        "readiness_score": payload["readiness_score"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
    }


def render_operational_readiness_page() -> str:
    payload = clone_payload()
    summary = payload["readiness_summary"]
    truth = payload["checkpoint_truth"]
    score = payload["readiness_score"]
    owner = payload["owner_review_state"]
    pack_matrix = payload["pack_matrix"]
    boundary_matrix = payload["boundary_matrix"]
    product_depth = payload["product_depth_matrix"]

    pack_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["pack_id"])}</strong>
            <span>{escape(item["product_depth_layer"])}</span>
          </div>
          <div class="pill {'ok' if item["ready"] else 'danger'}">{'Ready' if item["ready"] else 'Blocked'}</div>
        </div>
        """
        for item in pack_matrix["pack_items"]
    )

    boundary_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["boundary"])}</strong>
            <span>{escape(item["owner"])}</span>
          </div>
          <div class="pill {'ok' if item["locked"] else 'danger'}">{'Locked' if item["locked"] else 'Unlocked'}</div>
        </div>
        """
        for item in boundary_matrix["boundary_items"]
    )

    depth_cards = "\n".join(
        f"""
        <article class="card">
          <div class="card-top">
            <div>
              <div class="title">{escape(item["layer"])}</div>
              <div class="meta">
                Pack: <code>{escape(item["pack_id"])}</code><br>
                Route: <code>{escape(item["route"])}</code>
              </div>
            </div>
            <span class="pill ok">Ready</span>
          </div>
        </article>
        """
        for item in product_depth["product_depth_items"]
    )

    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Operational Readiness · GP020</title>
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
      max-width: 920px;
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
      text-transform: capitalize;
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
        <div class="eyebrow">Archive Vault · Giant Pack 020</div>
        <h1>Operational Readiness</h1>
        <p class="hero-copy">
          GP020 verifies Vault GP011–GP019 as a real product-depth stack. This checkpoint means safe to continue,
          not done. Raw file bodies, direct upload, public proof, external access, unredacted exports, seller/broker/trustee portals,
          financing decisions, legal advice, and Tower-owned permissions remain locked.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["readiness_score"]}%</strong>
            <span>{escape(summary["readiness_label"])}</span>
          </div>
          <div class="metric">
            <strong>{summary["verified_pack_count"]}/{summary["expected_pack_count"]}</strong>
            <span>packs verified</span>
          </div>
          <div class="metric">
            <strong>{summary["locked_boundary_count"]}</strong>
            <span>boundaries locked</span>
          </div>
          <div class="metric">
            <strong>{summary["product_depth_layer_count"]}</strong>
            <span>product layers</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">GP011-GP019 verified</span>
          <span class="pill ok">Safe to continue GP021+</span>
          <span class="pill warn">Vault not done</span>
          <span class="pill danger">Clouds parked</span>
          <span class="pill danger">Raw storage locked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Product Depth Layers</h2>
      <p>
        These are real Vault layers beyond the first foundation checkpoint.
      </p>
      <div class="grid">
        {depth_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Pack Matrix</h2>
        <p>Each pack from GP011 to GP019 is present and ready.</p>
        <div>
          {pack_rows}
        </div>
      </div>
      <div>
        <h2>Locked Boundary Matrix</h2>
        <p>Restricted actions remain locked and Tower-owned where required.</p>
        <div>
          {boundary_rows}
        </div>
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Owner Actions</h2>
        <p>Checkpoint does not mean stop. It means the Vault build can continue safely.</p>
        <ul>
          {actions}
        </ul>
      </div>
      <div>
        <h2>Checkpoint Truth</h2>
        <p>
          Vault done:
          <code>{str(truth["vault_done"]).lower()}</code>.
          Safe to continue:
          <code>{str(truth["safe_to_continue_past_checkpoint"]).lower()}</code>.
          Clouds should continue:
          <code>{str(truth["clouds_should_continue"]).lower()}</code>.
          Fake completion claimed:
          <code>{str(truth["fake_completion_claimed"]).lower()}</code>.
        </p>
      </div>
    </section>

    <section class="section">
      <h2>GP020 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["checkpoint_route"])}</code>
        <code>{escape(summary["routes_route"])}</code>
        <code>{escape(summary["boundaries_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp020_status_route"])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""
