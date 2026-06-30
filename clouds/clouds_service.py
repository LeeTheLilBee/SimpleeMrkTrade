"""The Clouds Giant Pack 001 service layer.

This builds the first owner command dashboard foundation using Vault GP010
as the first trusted source.

The Clouds reads:
- /vault/final-readiness.json
- /vault/clouds-handoff-contract.json
- /vault/command-center.json
- /vault/search-tracker.json
- /vault/receipt-control-center.json
- /vault/export-preview-center.json

Boundary:
Clouds is command/visibility/handoff. It does not own permissions, documents,
uploads, receipts, exports, execution, beta access, payroll, payments, or proofs.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_contracts import CLOUDS_VERSION, CloudsBoundary, CloudsCommandCard, CloudsSourceContract, utc_now_iso

from vault.vault_command_center_service import get_unified_vault_command_center_payload
from vault.vault_export_service import get_export_preview_center_payload
from vault.vault_final_readiness_service import (
    get_clouds_handoff_contract_payload,
    get_vault_final_readiness_payload,
    get_vault_gp010_status_payload,
)
from vault.vault_receipt_control_service import get_receipt_control_center_payload
from vault.vault_tracking_service import get_vault_search_tracker_payload


def _base_payload(route: str, payload_type: str) -> Dict[str, Any]:
    return {
        "app_id": "clouds",
        "app_name": "The Clouds",
        "version": CLOUDS_VERSION,
        "route": route,
        "payload_type": payload_type,
        "generated_at": utc_now_iso(),
        "public_access": False,
        "private_invite_only": True,
    }


def _source_contracts() -> List[CloudsSourceContract]:
    return [
        CloudsSourceContract(
            source_id="vault_final_readiness",
            source_app="archive_vault",
            source_route="/vault/final-readiness.json",
            source_label="Vault Final Readiness",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["show_readiness", "show_safe_to_start", "open_vault"],
            clouds_blocked_actions=["unlock_upload", "approve_export", "display_sensitive_body"],
        ),
        CloudsSourceContract(
            source_id="vault_handoff_contract",
            source_app="archive_vault",
            source_route="/vault/clouds-handoff-contract.json",
            source_label="Vault Clouds Handoff Contract",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["read_allowed_fields", "show_handoff_cards", "open_vault"],
            clouds_blocked_actions=["read_hidden_fields", "override_handoff", "become_permission_authority"],
        ),
        CloudsSourceContract(
            source_id="vault_command_center",
            source_app="archive_vault",
            source_route="/vault/command-center.json",
            source_label="Vault Command Center",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["show_lane_status", "show_owner_focus", "open_vault_command_center"],
            clouds_blocked_actions=["edit_vault_records", "grant_access", "unlock_exports"],
        ),
        CloudsSourceContract(
            source_id="vault_search_tracker",
            source_app="archive_vault",
            source_route="/vault/search-tracker.json",
            source_label="Vault Search + Requirement Tracker",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["show_record_counts", "show_requirement_counts", "show_staleness_summary"],
            clouds_blocked_actions=["search_sensitive_bodies", "upload_files", "edit_requirements"],
        ),
        CloudsSourceContract(
            source_id="vault_receipt_control",
            source_app="archive_vault",
            source_route="/vault/receipt-control-center.json",
            source_label="Vault Receipt Control",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["show_receipt_counts", "show_control_counts", "open_receipt_control"],
            clouds_blocked_actions=["create_receipts", "revoke_access", "override_freeze"],
        ),
        CloudsSourceContract(
            source_id="vault_export_preview",
            source_app="archive_vault",
            source_route="/vault/export-preview-center.json",
            source_label="Vault Export Preview",
            summary_only=True,
            redacted=True,
            tower_guard_required=True,
            owning_app_keeps_authority=True,
            clouds_allowed_actions=["show_export_lock_status", "show_preview_counts", "open_export_preview"],
            clouds_blocked_actions=["approve_exports", "download_packets", "show_unredacted_preview"],
        ),
    ]


def get_clouds_source_map_payload() -> Dict[str, Any]:
    sources = [source.to_dict() for source in _source_contracts()]
    handoff = get_clouds_handoff_contract_payload()

    payload = {
        **_base_payload("/clouds/source-map.json", "clouds_source_map"),
        "status": "ready",
        "source_count": len(sources),
        "sources": sources,
        "first_source_app": "archive_vault",
        "vault_handoff_status": handoff["status"],
        "vault_handoff_view": handoff["clouds_view"],
        "allowed_fields": handoff["allowed_fields"],
        "hidden_fields": handoff["hidden_fields"],
        "clouds_must_not_do": handoff["clouds_must_not_do"],
        "clouds_may_do": handoff["clouds_may_do"],
        "boundary": {
            "summary_only": True,
            "redacted": True,
            "tower_guard_required": True,
            "clouds_owns_permissions": False,
            "clouds_owns_documents": False,
            "clouds_owns_exports": False,
            "clouds_owns_execution": False,
        },
    }
    return payload


def _make_command_cards() -> List[CloudsCommandCard]:
    final = get_vault_final_readiness_payload()
    command = get_unified_vault_command_center_payload()
    tracker = get_vault_search_tracker_payload()
    receipt = get_receipt_control_center_payload()
    export = get_export_preview_center_payload()

    return [
        CloudsCommandCard(
            card_id="clouds_vault_final_score",
            label="Vault readiness",
            value=final["final_score"],
            unit="%",
            source_app="archive_vault",
            source_route="/vault/final-readiness.json",
            status=final["status"],
            summary="Vault GP001-GP010 foundation readiness.",
            owner_next_action="Start Clouds using Vault summary-only handoff.",
            open_app_target="/vault/final-readiness",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_lanes",
            label="Vault lanes",
            value=command["lane_count"],
            unit="lanes",
            source_app="archive_vault",
            source_route="/vault/command-center.json",
            status=command["command_center_status"],
            summary="Six Vault lanes connected to the command center.",
            owner_next_action="Open Vault command center for detailed lane status.",
            open_app_target="/vault/command-center",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_routes",
            label="Vault routes",
            value=command["route_count"],
            unit="routes",
            source_app="archive_vault",
            source_route="/vault/command-center.json",
            status="ready",
            summary="Vault UI and JSON sources available for owner handoff.",
            owner_next_action="Use route index to open the owning Vault room.",
            open_app_target="/vault/command-center",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_records",
            label="Vault records",
            value=tracker["search_index"]["record_count"],
            unit="records",
            source_app="archive_vault",
            source_route="/vault/search-tracker.json",
            status=tracker["status"],
            summary="Searchable redacted Vault records across six lanes.",
            owner_next_action="Open Vault search tracker for requirement/freshness state.",
            open_app_target="/vault/search-tracker",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_requirements",
            label="Vault requirements",
            value=tracker["requirement_tracker"]["requirement_count"],
            unit="requirements",
            source_app="archive_vault",
            source_route="/vault/search-tracker.json",
            status="ready",
            summary="Tracked requirements across ATM, property, trust, OB, Soulaana, and beta.",
            owner_next_action="Open Vault tracker when evidence is ready to attach later.",
            open_app_target="/vault/search-tracker",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_receipts",
            label="Vault receipts",
            value=receipt["receipt_chain_console"]["receipt_count"],
            unit="receipts",
            source_app="archive_vault",
            source_route="/vault/receipt-control-center.json",
            status=receipt["status"],
            summary="Private receipt chain and proof/control receipts.",
            owner_next_action="Open receipt control to review proof and freeze/revoke/undo status.",
            open_app_target="/vault/receipt-control",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_controls",
            label="Vault control rules",
            value=receipt["freeze_revoke_undo_wall"]["rule_count"],
            unit="rules",
            source_app="archive_vault",
            source_route="/vault/receipt-control-center.json",
            status="ready",
            summary="Freeze, revoke, and undo controls for dangerous doors and safe drafts.",
            owner_next_action="Keep dangerous unlocks blocked unless Tower/owner review says otherwise.",
            open_app_target="/vault/receipt-control",
        ),
        CloudsCommandCard(
            card_id="clouds_vault_locked_exports",
            label="Locked exports",
            value=export["export_lock_console"]["locked_export_count"],
            unit="locked",
            source_app="archive_vault",
            source_route="/vault/export-preview-center.json",
            status="locked",
            summary="Vault exports are locked by default with redacted previews only.",
            owner_next_action="Open Vault export preview if a packet export needs review later.",
            open_app_target="/vault/export-preview",
        ),
    ]


def get_clouds_vault_summary_payload() -> Dict[str, Any]:
    final = get_vault_final_readiness_payload()
    handoff = get_clouds_handoff_contract_payload()
    command = get_unified_vault_command_center_payload()
    tracker = get_vault_search_tracker_payload()
    receipt = get_receipt_control_center_payload()
    export = get_export_preview_center_payload()
    gp010 = get_vault_gp010_status_payload()

    payload = {
        **_base_payload("/clouds/vault-summary.json", "clouds_vault_summary"),
        "status": "ready",
        "source_app": "archive_vault",
        "summary_only": True,
        "redacted": True,
        "vault": {
            "final_score": final["final_score"],
            "readiness_label": final["readiness_label"],
            "safe_to_start_clouds": final["safe_to_start_clouds"],
            "status": final["status"],
            "gp010_status": gp010["status"],
            "clouds_view": handoff["clouds_view"],
            "lane_count": command["lane_count"],
            "route_count": command["route_count"],
            "owner_action_count": command["owner_action_count"],
            "search_record_count": tracker["search_index"]["record_count"],
            "requirement_count": tracker["requirement_tracker"]["requirement_count"],
            "blocked_requirement_count": tracker["requirement_tracker"]["blocked_count"],
            "renewal_item_count": tracker["expiration_renewal_wall"]["renewal_item_count"],
            "receipt_count": receipt["receipt_chain_console"]["receipt_count"],
            "approval_chain_count": receipt["approval_chain_console"]["chain_count"],
            "control_rule_count": receipt["freeze_revoke_undo_wall"]["rule_count"],
            "export_record_count": export["export_lock_console"]["export_record_count"],
            "locked_export_count": export["export_lock_console"]["locked_export_count"],
            "redacted_preview_count": export["redacted_packet_preview"]["preview_count"],
        },
        "owner_focus": final["owner_final_queue"]["actions"],
        "intentional_locks": final["intentional_locks"],
        "clouds_start_sources": final["clouds_start_sources"],
        "open_app_targets": [
            {"label": "Open Vault Final Readiness", "route": "/vault/final-readiness"},
            {"label": "Open Vault Command Center", "route": "/vault/command-center"},
            {"label": "Open Vault Search Tracker", "route": "/vault/search-tracker"},
            {"label": "Open Vault Receipt Control", "route": "/vault/receipt-control"},
            {"label": "Open Vault Export Preview", "route": "/vault/export-preview"},
        ],
    }
    return payload


def _boundaries() -> List[CloudsBoundary]:
    return [
        CloudsBoundary(
            boundary_id="clouds_not_tower",
            label="Clouds is not Tower",
            enforced=True,
            summary="Clouds does not own identity, permissions, clearance, step-up, export locks, freeze, or revoke.",
        ),
        CloudsBoundary(
            boundary_id="clouds_not_vault",
            label="Clouds is not Vault",
            enforced=True,
            summary="Clouds does not own documents, packet bodies, receipts, upload, storage, or redaction policy.",
        ),
        CloudsBoundary(
            boundary_id="clouds_not_ob",
            label="Clouds is not OB",
            enforced=True,
            summary="Clouds does not detect trades, review trades, execute, track broker activity, or publish proof.",
        ),
        CloudsBoundary(
            boundary_id="clouds_not_teller",
            label="Clouds is not The Teller",
            enforced=True,
            summary="Clouds does not own payroll, payments, people workflows, employee onboarding, or direct deposit records.",
        ),
        CloudsBoundary(
            boundary_id="summary_only_redacted",
            label="Summary-only redacted",
            enforced=True,
            summary="Clouds displays high-level status, counts, readiness, blocked reasons, owner focus, and open-app handoffs only.",
        ),
        CloudsBoundary(
            boundary_id="open_app_handoff_only",
            label="Open-app handoff only",
            enforced=True,
            summary="Clouds routes the owner to the owning app for real action.",
        ),
    ]


def get_clouds_command_dashboard_payload() -> Dict[str, Any]:
    source_map = get_clouds_source_map_payload()
    vault_summary = get_clouds_vault_summary_payload()
    cards = [card.to_dict() for card in _make_command_cards()]
    boundaries = [boundary.to_dict() for boundary in _boundaries()]

    payload = {
        **_base_payload("/clouds/dashboard.json", "clouds_command_dashboard"),
        "status": "ready",
        "dashboard_label": "The Clouds Owner Command Dashboard",
        "mode": "owner_command_foundation",
        "source_count": source_map["source_count"],
        "card_count": len(cards),
        "boundary_count": len(boundaries),
        "cards": cards,
        "boundaries": boundaries,
        "vault_summary": vault_summary["vault"],
        "owner_focus": vault_summary["owner_focus"],
        "open_app_targets": vault_summary["open_app_targets"],
        "foundation_lanes": [
            "vault",
            "tower",
            "observatory",
            "teller",
            "atm",
            "property",
            "soulaana",
            "beta",
        ],
        "not_built_yet": [
            "Tower live source summary card",
            "OB live source summary card",
            "Teller source summary card",
            "ATM operating source summary card",
            "Property operating source summary card",
        ],
        "next_pack_recommendation": "Clouds GP002 should add Tower/OB placeholder source cards and app registry shell without overstepping authority.",
    }
    return payload


def get_clouds_status_payload() -> Dict[str, Any]:
    dashboard = get_clouds_command_dashboard_payload()
    vault_summary = get_clouds_vault_summary_payload()

    payload = {
        **_base_payload("/clouds/status.json", "clouds_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 001",
        "built": [
            "clouds_contracts",
            "source_map",
            "vault_summary",
            "owner_command_dashboard_payload",
            "clouds_boundaries",
            "open_app_handoff_targets",
            "clouds_home_ui",
            "clouds_status_endpoint",
        ],
        "dashboard_status": dashboard["status"],
        "source_count": dashboard["source_count"],
        "card_count": dashboard["card_count"],
        "boundary_count": dashboard["boundary_count"],
        "vault_final_score": vault_summary["vault"]["final_score"],
        "vault_safe_to_start_clouds": vault_summary["vault"]["safe_to_start_clouds"],
        "clouds_view": vault_summary["vault"]["clouds_view"],
        "clouds_owns_permissions": False,
        "clouds_owns_documents": False,
        "clouds_owns_execution": False,
        "clouds_owns_exports": False,
        "safe_to_continue_to_clouds_gp002": True,
    }
    return payload


def get_clouds_gp001_status_payload() -> Dict[str, Any]:
    return get_clouds_status_payload()
