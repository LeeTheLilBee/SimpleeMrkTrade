"""Vault Giant Pack 010 Final Readiness + Clouds Handoff.

This pack closes the first aggressive Vault foundation block:
- verifies GP001-GP009 are integrated
- creates final Vault readiness checkpoint
- creates Clouds handoff contract
- creates Vault source map for Clouds
- creates owner final action queue
- marks Vault foundation safe for Clouds GP001

Boundary:
Safe for Clouds means summary-only redacted Vault state. It does not mean direct
uploads, exports, external access, public proof, beta access, or unredacted packet
bodies are unlocked.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_acquisition_service import get_vault_gp003_status_payload
from .vault_command_center_service import (
    get_unified_vault_command_center_payload,
    get_vault_gp006_status_payload,
)
from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_export_service import (
    get_export_preview_center_payload,
    get_vault_gp009_status_payload,
)
from .vault_receipt_control_service import (
    get_receipt_control_center_payload,
    get_vault_gp008_status_payload,
)
from .vault_room_service import get_vault_gp002_status_payload, get_vault_room_payload
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard
from .vault_service import get_clouds_source_payload, get_vault_status
from .vault_soulaana_beta_service import get_vault_gp005_status_payload
from .vault_tracking_service import (
    get_vault_gp007_status_payload,
    get_vault_search_tracker_payload,
)
from .vault_trust_ob_service import get_vault_gp004_status_payload


def _pack_gate(
    pack_id: str,
    label: str,
    commit_scope: str,
    status_payload: Dict[str, Any],
    required_keys: List[str],
    safe_key: str | None = None,
) -> Dict[str, Any]:
    missing_keys = [key for key in required_keys if key not in status_payload]
    safe_to_continue = True if safe_key is None else bool(status_payload.get(safe_key))
    ready = status_payload.get("status") == "ready" and not missing_keys and safe_to_continue

    return {
        "pack_id": pack_id,
        "label": label,
        "commit_scope": commit_scope,
        "status": status_payload.get("status", "unknown"),
        "ready": ready,
        "safe_to_continue": safe_to_continue,
        "missing_keys": missing_keys,
        "source_payload_type": status_payload.get("payload_type", "unknown"),
        "source_pack": status_payload.get("pack", pack_id),
    }


def get_vault_pack_gate_payload() -> Dict[str, Any]:
    gp001 = get_vault_status()
    gp002 = get_vault_gp002_status_payload()
    gp003 = get_vault_gp003_status_payload()
    gp004 = get_vault_gp004_status_payload()
    gp005 = get_vault_gp005_status_payload()
    gp006 = get_vault_gp006_status_payload()
    gp007 = get_vault_gp007_status_payload()
    gp008 = get_vault_gp008_status_payload()
    gp009 = get_vault_gp009_status_payload()

    gates = [
        _pack_gate(
            "gp001",
            "Archive core foundation",
            "contracts, packets, status, no-direct-upload, redaction",
            gp001,
            ["status", "readiness_score", "packet_template_count", "clouds_source_ready"],
        ),
        _pack_gate(
            "gp002",
            "Real Vault room interface",
            "packet board, document drawer, owner action queue",
            gp002,
            ["status", "room_section_count", "packet_card_count", "document_record_count", "owner_action_count"],
            "safe_to_continue_to_gp003",
        ),
        _pack_gate(
            "gp003",
            "Acquisition builders",
            "ATM route builder and apartment lender builder",
            gp003,
            ["status", "builder_count", "atm_required_document_count", "apartment_required_document_count"],
            "safe_to_continue_to_gp004",
        ),
        _pack_gate(
            "gp004",
            "Trust and OB proof vault",
            "trust/entity packet vault and OB Manual Live private proof vault",
            gp004,
            ["status", "trust_document_count", "ob_proof_document_count", "ob_boundary_count"],
            "safe_to_continue_to_gp005",
        ),
        _pack_gate(
            "gp005",
            "Soulaana and beta vault",
            "Soulaana Artist/IP package and private beta onboarding",
            gp005,
            ["status", "soulaana_package_record_count", "beta_onboarding_record_count"],
            "safe_to_continue_to_gp006",
        ),
        _pack_gate(
            "gp006",
            "Unified command center",
            "six-lane readiness wall, route index, Clouds source map",
            gp006,
            ["status", "lane_count", "route_count", "owner_action_count", "command_level"],
            "safe_to_continue_to_gp007",
        ),
        _pack_gate(
            "gp007",
            "Search and requirement tracker",
            "search index, requirement tracker, expiration wall, freshness wall",
            gp007,
            ["status", "search_record_count", "requirement_count", "renewal_item_count", "freshness_lane_count"],
            "safe_to_continue_to_gp008",
        ),
        _pack_gate(
            "gp008",
            "Receipt control center",
            "receipt chain, approval chain, freeze/revoke/undo, blocked decisions",
            gp008,
            ["status", "receipt_count", "approval_chain_count", "control_rule_count", "blocked_decision_count"],
            "safe_to_continue_to_gp009",
        ),
        _pack_gate(
            "gp009",
            "Export lock and redacted preview",
            "export lock console, redacted packet previews, external access review",
            gp009,
            ["status", "export_record_count", "locked_export_count", "redacted_preview_count", "external_review_item_count"],
            "safe_to_continue_to_gp010",
        ),
    ]

    ready_count = sum(1 for gate in gates if gate["ready"])

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_pack_gate",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready" if ready_count == len(gates) else "needs_attention",
        "gate_count": len(gates),
        "ready_gate_count": ready_count,
        "blocked_gate_count": len(gates) - ready_count,
        "all_previous_gates_ready": ready_count == len(gates),
        "gates": gates,
    }
    return attach_tower_guard(payload, "/vault/pack-gate.json")


def get_clouds_handoff_contract_payload() -> Dict[str, Any]:
    command = get_unified_vault_command_center_payload()
    tracker = get_vault_search_tracker_payload()
    receipt_control = get_receipt_control_center_payload()
    export_preview = get_export_preview_center_payload()

    source_routes = [
        {
            "route": "/vault/final-readiness.json",
            "purpose": "final Vault readiness and safe-to-start-Clouds signal",
            "clouds_use": "owner command readiness card",
        },
        {
            "route": "/vault/command-center.json",
            "purpose": "six-lane command wall and route/source index",
            "clouds_use": "Vault command summary card",
        },
        {
            "route": "/vault/search-tracker.json",
            "purpose": "record count, requirement count, blocked count, renewal/freshness counts",
            "clouds_use": "documents and requirements status card",
        },
        {
            "route": "/vault/receipt-control-center.json",
            "purpose": "receipt counts, approval chains, freeze/revoke/undo controls, blocked decisions",
            "clouds_use": "proof and control status card",
        },
        {
            "route": "/vault/export-preview-center.json",
            "purpose": "export locks, redacted previews, external access review status",
            "clouds_use": "export safety status card",
        },
        {
            "route": "/vault/clouds-source.json",
            "purpose": "legacy GP001 Clouds-safe Vault summary",
            "clouds_use": "compatibility source",
        },
    ]

    allowed_fields = [
        "app_id",
        "app_name",
        "status",
        "readiness_score",
        "readiness_label",
        "lane_count",
        "route_count",
        "owner_action_count",
        "record_count",
        "requirement_count",
        "blocked_count",
        "renewal_item_count",
        "receipt_count",
        "approval_chain_count",
        "control_rule_count",
        "export_record_count",
        "locked_export_count",
        "preview_count",
        "safe_to_start_clouds",
        "owner_focus",
        "blocked_reasons_summary",
        "next_action",
    ]

    hidden_fields = sorted(
        set(REDACTION_POLICY["sensitive_fields"])
        | {
            "broker_credentials",
            "broker_api_key",
            "order_submit_token",
            "broker_account_number",
            "bank_account_numbers",
            "beneficiary_details",
            "full_legal_document_body",
            "tax_identity_details",
            "artist_payment_details",
            "artist_private_contact",
            "full_ip_agreement_body",
            "nda_body",
            "beta_tester_private_contact",
            "tower_clearance_private_details",
            "seller_private_contact",
            "full_cashflow_statement",
            "full_rent_roll",
            "full_t12",
            "tenant_details",
        }
    )

    handoff_cards = [
        {
            "card_id": "clouds_vault_readiness",
            "label": "Vault readiness",
            "value": 100,
            "unit": "%",
            "source_route": "/vault/final-readiness.json",
        },
        {
            "card_id": "clouds_vault_lanes",
            "label": "Vault lanes",
            "value": command["lane_count"],
            "unit": "lanes",
            "source_route": "/vault/command-center.json",
        },
        {
            "card_id": "clouds_vault_records",
            "label": "Search records",
            "value": tracker["search_index"]["record_count"],
            "unit": "records",
            "source_route": "/vault/search-tracker.json",
        },
        {
            "card_id": "clouds_vault_requirements",
            "label": "Requirements",
            "value": tracker["requirement_tracker"]["requirement_count"],
            "unit": "requirements",
            "source_route": "/vault/search-tracker.json",
        },
        {
            "card_id": "clouds_vault_receipts",
            "label": "Receipts",
            "value": receipt_control["receipt_chain_console"]["receipt_count"],
            "unit": "receipts",
            "source_route": "/vault/receipt-control-center.json",
        },
        {
            "card_id": "clouds_vault_exports",
            "label": "Locked exports",
            "value": export_preview["export_lock_console"]["locked_export_count"],
            "unit": "locked",
            "source_route": "/vault/export-preview-center.json",
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "clouds_handoff_contract",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "handoff_name": "Vault to Clouds Summary-Only Handoff",
        "safe_for_clouds": True,
        "clouds_view": "summary_only_redacted",
        "source_routes": source_routes,
        "handoff_cards": handoff_cards,
        "allowed_fields": allowed_fields,
        "hidden_fields": hidden_fields,
        "blocked_reasons": sorted(
            set(NO_DIRECT_UPLOAD_POLICY["blocked_now"])
            | set(command["boundary_wall"]["blocked_reasons"])
            | set(export_preview["clouds_safe_source"]["blocked_reasons"])
        ),
        "clouds_must_not_do": [
            "display_unredacted_document_body",
            "display_bank_account_numbers",
            "display_broker_credentials",
            "display_beneficiary_details",
            "display_beta_tester_private_contact",
            "unlock_vault_upload",
            "approve_exports",
            "grant_beta_access",
            "publish_ob_proof",
            "treat_vault_as_permission_authority",
        ],
        "clouds_may_do": [
            "show_vault_readiness",
            "show_lane_status",
            "show_requirement_counts",
            "show_blocked_reason_counts",
            "show_owner_focus",
            "open_vault_route_for_action",
            "show_safe_redacted_summary",
        ],
        "refresh_standard": {
            "default": "on_page_load_or_owner_refresh",
            "stale_threshold_minutes": 60,
            "clouds_should_show_stale_chip": True,
        },
    }
    return attach_tower_guard(payload, "/vault/clouds-handoff-contract.json")


def get_vault_owner_final_queue_payload() -> Dict[str, Any]:
    actions = [
        {
            "action_id": "vault_final_keep_upload_locked",
            "label": "Keep direct upload locked",
            "priority": "critical",
            "business_lane": "vault",
            "status": "boundary_active",
            "next_step": "Build Tower-approved storage clearance later before any raw uploads.",
            "blocked_by": ["direct_upload_locked", "upload_provider_not_approved"],
        },
        {
            "action_id": "vault_final_start_clouds_gp001",
            "label": "Start Clouds GP001 from Vault handoff",
            "priority": "high",
            "business_lane": "clouds",
            "status": "ready",
            "next_step": "Clouds can read /vault/final-readiness.json and /vault/clouds-handoff-contract.json as summary-only sources.",
            "blocked_by": [],
        },
        {
            "action_id": "vault_final_keep_exports_locked",
            "label": "Keep exports locked by default",
            "priority": "critical",
            "business_lane": "vault",
            "status": "boundary_active",
            "next_step": "Exports require target, scope, owner approval, Tower clearance, and approval chain.",
            "blocked_by": ["export_locked", "tower_step_up_needed"],
        },
        {
            "action_id": "vault_final_use_atm_and_property_packets",
            "label": "Use ATM and property packet builders when targets appear",
            "priority": "high",
            "business_lane": "atm_property",
            "status": "ready_for_targets",
            "next_step": "Use Vault packets when ATM route targets or apartment properties are being reviewed.",
            "blocked_by": [],
        },
        {
            "action_id": "vault_final_use_ob_proof_chain_when_manual_live_begins",
            "label": "Use OB proof chain when Manual Live records begin",
            "priority": "high",
            "business_lane": "observatory",
            "status": "ready_for_private_receipts",
            "next_step": "Link Manual Live alert, checklist, owner review, risk boundary, and tracking receipts.",
            "blocked_by": [],
        },
        {
            "action_id": "vault_final_preserve_redaction_boundaries",
            "label": "Preserve redaction boundaries",
            "priority": "critical",
            "business_lane": "vault",
            "status": "boundary_active",
            "next_step": "Clouds and normal previews stay summary-only and redacted.",
            "blocked_by": ["sensitive_fields_redacted", "unredacted_export_blocked"],
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_owner_final_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "action_count": len(actions),
        "critical_count": sum(1 for action in actions if action["priority"] == "critical"),
        "high_count": sum(1 for action in actions if action["priority"] == "high"),
        "ready_action_count": sum(1 for action in actions if not action["blocked_by"]),
        "actions": actions,
    }
    return attach_tower_guard(payload, "/vault/owner-final-queue.json")


def get_vault_final_readiness_payload() -> Dict[str, Any]:
    gates = get_vault_pack_gate_payload()
    command = get_unified_vault_command_center_payload()
    tracker = get_vault_search_tracker_payload()
    receipt_control = get_receipt_control_center_payload()
    export_preview = get_export_preview_center_payload()
    handoff = get_clouds_handoff_contract_payload()
    owner_queue = get_vault_owner_final_queue_payload()
    gp001_clouds = get_clouds_source_payload()
    room = get_vault_room_payload()

    intentional_locks = [
        "direct_upload_locked",
        "exports_locked_by_default",
        "external_access_default_deny",
        "unredacted_export_blocked",
        "public_proof_blocked",
        "broker_secret_storage_blocked",
        "auto_execution_blocked",
        "ai_generated_character_art_blocked",
        "vault_permission_authority_blocked",
    ]

    final_score = 100 if gates["all_previous_gates_ready"] and handoff["safe_for_clouds"] else 0

    payload = {
        "app_id": "archive_vault",
        "app_name": "Archive Vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_final_readiness",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "private_invite_only": True,
        "status": "ready" if final_score == 100 else "needs_attention",
        "pack": "Vault Giant Pack 010",
        "final_score": final_score,
        "readiness_label": "vault_foundation_complete" if final_score == 100 else "vault_foundation_needs_attention",
        "safe_to_start_clouds": final_score == 100,
        "safe_to_continue_to_vault_gp011": True,
        "final_gate_summary": {
            "gate_count": gates["gate_count"],
            "ready_gate_count": gates["ready_gate_count"],
            "blocked_gate_count": gates["blocked_gate_count"],
            "all_previous_gates_ready": gates["all_previous_gates_ready"],
        },
        "foundation_summary": {
            "lane_count": command["lane_count"],
            "route_count": command["route_count"],
            "owner_action_count": command["owner_action_count"],
            "search_record_count": tracker["search_index"]["record_count"],
            "requirement_count": tracker["requirement_tracker"]["requirement_count"],
            "renewal_item_count": tracker["expiration_renewal_wall"]["renewal_item_count"],
            "freshness_lane_count": tracker["data_freshness_wall"]["lane_count"],
            "receipt_count": receipt_control["receipt_chain_console"]["receipt_count"],
            "approval_chain_count": receipt_control["approval_chain_console"]["chain_count"],
            "control_rule_count": receipt_control["freeze_revoke_undo_wall"]["rule_count"],
            "export_record_count": export_preview["export_lock_console"]["export_record_count"],
            "locked_export_count": export_preview["export_lock_console"]["locked_export_count"],
            "redacted_preview_count": export_preview["redacted_packet_preview"]["preview_count"],
        },
        "clouds_handoff_summary": {
            "safe_for_clouds": handoff["safe_for_clouds"],
            "clouds_view": handoff["clouds_view"],
            "source_route_count": len(handoff["source_routes"]),
            "handoff_card_count": len(handoff["handoff_cards"]),
            "allowed_field_count": len(handoff["allowed_fields"]),
            "hidden_field_count": len(handoff["hidden_fields"]),
            "legacy_clouds_source_ready": gp001_clouds["safe_for_clouds"],
        },
        "room_summary": {
            "room_status": room["room_status"],
            "room_section_count": len(room["room_sections"]),
            "command_chip_count": len(room["command_chips"]),
        },
        "owner_final_queue": owner_queue,
        "intentional_locks": intentional_locks,
        "boundary_final": {
            "tower_guard_required": True,
            "vault_owns_permissions": False,
            "direct_upload_allowed": False,
            "exports_locked_by_default": True,
            "external_access_default_deny": True,
            "unredacted_export_allowed": False,
            "clouds_view": "summary_only_redacted",
            "redacted_view_default": True,
            "broker_secrets_allowed": False,
            "auto_execution_allowed": False,
            "public_proof_allowed": False,
            "public_beta_routes_allowed": False,
            "ai_generated_character_art_allowed": False,
        },
        "clouds_start_sources": [
            "/vault/final-readiness.json",
            "/vault/clouds-handoff-contract.json",
            "/vault/command-center.json",
            "/vault/search-tracker.json",
            "/vault/receipt-control-center.json",
            "/vault/export-preview-center.json",
        ],
        "next_pack_recommendation": "Start The Clouds GP001: owner command dashboard foundation reading Vault summary-only handoff.",
    }
    return attach_tower_guard(payload, "/vault/final-readiness.json")


def get_vault_gp010_status_payload() -> Dict[str, Any]:
    final = get_vault_final_readiness_payload()
    handoff = get_clouds_handoff_contract_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp010_status",
        "generated_at": utc_now_iso(),
        "status": final["status"],
        "pack": "Vault Giant Pack 010",
        "built": [
            "vault_pack_gate",
            "final_vault_readiness_checkpoint",
            "clouds_handoff_contract",
            "clouds_source_route_map",
            "owner_final_queue",
            "safe_to_start_clouds_signal",
            "final_readiness_ui",
            "gp010_status_endpoint",
        ],
        "final_score": final["final_score"],
        "gate_count": final["final_gate_summary"]["gate_count"],
        "ready_gate_count": final["final_gate_summary"]["ready_gate_count"],
        "safe_to_start_clouds": final["safe_to_start_clouds"],
        "clouds_source_route_count": len(handoff["source_routes"]),
        "clouds_handoff_card_count": len(handoff["handoff_cards"]),
        "direct_upload_allowed": final["boundary_final"]["direct_upload_allowed"],
        "vault_owns_permissions": final["boundary_final"]["vault_owns_permissions"],
        "exports_locked_by_default": final["boundary_final"]["exports_locked_by_default"],
        "clouds_view": final["boundary_final"]["clouds_view"],
        "safe_to_continue_to_vault_gp011": final["safe_to_continue_to_vault_gp011"],
    }
    return attach_tower_guard(payload, "/vault/gp010-status.json")
