"""Vault Giant Pack 006 Unified Vault Command Center.

This pack links all six Vault lanes into one command room:
- ATM route acquisition
- Apartment lender due diligence
- Trust/entity records
- OB Manual Live private proof
- Soulaana Artist/IP package
- Private beta onboarding

The command center gives the owner one readiness wall, one route index, one
blocked-boundary view, one owner focus queue, and one Clouds-safe source map.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_acquisition_service import (
    get_acquisition_builders_payload,
    get_acquisition_owner_queue_payload,
    get_apartment_lender_builder_payload,
    get_atm_route_builder_payload,
)
from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_readiness import get_readiness_score
from .vault_room_service import (
    get_document_drawer_payload,
    get_owner_action_queue_payload,
    get_packet_board_payload,
    get_vault_room_payload,
)
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard
from .vault_service import (
    get_clouds_source_payload,
    get_no_direct_upload_payload,
    get_redacted_view_policy_payload,
    get_vault_status,
)
from .vault_soulaana_beta_service import (
    get_private_beta_onboarding_vault_payload,
    get_soulaana_artist_ip_vault_payload,
    get_soulaana_beta_owner_queue_payload,
    get_soulaana_beta_vault_payload,
)
from .vault_trust_ob_service import (
    get_ob_manual_live_proof_vault_payload,
    get_trust_entity_vault_payload,
    get_trust_ob_owner_queue_payload,
    get_trust_ob_vault_payload,
)


def _lane_card(
    lane_id: str,
    label: str,
    source_app: str,
    source_route: str,
    setup_score: int,
    record_count: int,
    status: str,
    owner_focus: str,
    blocked_reasons: List[str],
    sensitivity: str,
) -> Dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "source_app": source_app,
        "source_route": source_route,
        "setup_score": setup_score,
        "record_count": record_count,
        "status": status,
        "owner_focus": owner_focus,
        "blocked_reasons": blocked_reasons,
        "sensitivity": sensitivity,
        "tower_guard_required": True,
        "direct_upload_allowed": False,
        "redacted_view_default": True,
        "clouds_view": "summary_only_redacted",
    }


def _collect_owner_actions() -> List[Dict[str, Any]]:
    action_sources = [
        ("vault_room", get_owner_action_queue_payload()["actions"]),
        ("acquisition", get_acquisition_owner_queue_payload()["actions"]),
        ("trust_ob", get_trust_ob_owner_queue_payload()["actions"]),
        ("soulaana_beta", get_soulaana_beta_owner_queue_payload()["actions"]),
    ]

    actions: List[Dict[str, Any]] = []
    for source, source_actions in action_sources:
        for index, action in enumerate(source_actions, start=1):
            actions.append(
                {
                    "source": source,
                    "position": len(actions) + 1,
                    "source_position": index,
                    **action,
                }
            )

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    actions.sort(key=lambda item: (priority_order.get(item.get("priority", "low"), 9), item["position"]))
    return actions


def _route_index() -> List[Dict[str, Any]]:
    return [
        {"label": "Vault Room", "route": "/vault", "type": "ui", "lane": "all"},
        {"label": "Unified Command Center", "route": "/vault/command-center", "type": "ui", "lane": "all"},
        {"label": "Acquisition Builders", "route": "/vault/acquisition-builders", "type": "ui", "lane": "atm_property"},
        {"label": "Trust + OB Vault", "route": "/vault/trust-ob", "type": "ui", "lane": "trust_ob"},
        {"label": "Soulaana + Beta Vault", "route": "/vault/soulaana-beta", "type": "ui", "lane": "soulaana_beta"},
        {"label": "Command Center JSON", "route": "/vault/command-center.json", "type": "json", "lane": "all"},
        {"label": "Room JSON", "route": "/vault/room.json", "type": "json", "lane": "all"},
        {"label": "Packet Board JSON", "route": "/vault/packet-board.json", "type": "json", "lane": "all"},
        {"label": "Document Drawer JSON", "route": "/vault/document-drawer.json", "type": "json", "lane": "all"},
        {"label": "ATM Route Builder JSON", "route": "/vault/atm-route-builder.json", "type": "json", "lane": "atm"},
        {"label": "Apartment Lender Builder JSON", "route": "/vault/apartment-lender-builder.json", "type": "json", "lane": "property"},
        {"label": "Trust Entity Vault JSON", "route": "/vault/trust-entity-vault.json", "type": "json", "lane": "trust"},
        {"label": "OB Manual Live Proof Vault JSON", "route": "/vault/ob-manual-live-proof-vault.json", "type": "json", "lane": "observatory"},
        {"label": "Soulaana Artist/IP Vault JSON", "route": "/vault/soulaana-artist-ip-vault.json", "type": "json", "lane": "soulaana"},
        {"label": "Private Beta Onboarding Vault JSON", "route": "/vault/private-beta-onboarding-vault.json", "type": "json", "lane": "beta"},
        {"label": "Clouds Source JSON", "route": "/vault/clouds-source.json", "type": "json", "lane": "clouds"},
        {"label": "GP006 Status JSON", "route": "/vault/gp006-status.json", "type": "json", "lane": "all"},
    ]


def get_unified_vault_command_center_payload() -> Dict[str, Any]:
    vault_status = get_vault_status()
    readiness = get_readiness_score()
    room = get_vault_room_payload()
    packet_board = get_packet_board_payload()
    document_drawer = get_document_drawer_payload()
    acquisition = get_acquisition_builders_payload()
    atm = get_atm_route_builder_payload()["builder"]
    apartment = get_apartment_lender_builder_payload()["builder"]
    trust_ob = get_trust_ob_vault_payload()
    trust = get_trust_entity_vault_payload()
    ob = get_ob_manual_live_proof_vault_payload()
    soulaana_beta = get_soulaana_beta_vault_payload()
    soulaana = get_soulaana_artist_ip_vault_payload()
    beta = get_private_beta_onboarding_vault_payload()
    clouds_source = get_clouds_source_payload()

    lane_cards = [
        _lane_card(
            lane_id="atm",
            label="ATM Route Acquisition",
            source_app="vault_acquisition_service",
            source_route="/vault/atm-route-builder.json",
            setup_score=atm["readiness"]["builder_setup_score"],
            record_count=atm["readiness"]["required_document_count"],
            status=atm["status"],
            owner_focus=atm["owner_next_action"],
            blocked_reasons=["direct_upload_locked", "funding_source_pending", "target_not_selected"],
            sensitivity="high",
        ),
        _lane_card(
            lane_id="property",
            label="Apartment Lender Due Diligence",
            source_app="vault_acquisition_service",
            source_route="/vault/apartment-lender-builder.json",
            setup_score=apartment["readiness"]["builder_setup_score"],
            record_count=apartment["readiness"]["required_document_count"],
            status=apartment["status"],
            owner_focus=apartment["owner_next_action"],
            blocked_reasons=["direct_upload_locked", "target_not_selected", "lender_not_selected"],
            sensitivity="high",
        ),
        _lane_card(
            lane_id="trust",
            label="Trust / Entity Packet",
            source_app="vault_trust_ob_service",
            source_route="/vault/trust-entity-vault.json",
            setup_score=trust["readiness"]["setup_score"],
            record_count=len(trust["documents"]),
            status=trust["status"],
            owner_focus=trust["owner_next_action"],
            blocked_reasons=["direct_upload_locked", "sensitive_fields_redacted", "financial_review_pending"],
            sensitivity="restricted",
        ),
        _lane_card(
            lane_id="observatory",
            label="OB Manual Live Proof",
            source_app="vault_trust_ob_service",
            source_route="/vault/ob-manual-live-proof-vault.json",
            setup_score=ob["readiness"]["setup_score"],
            record_count=len(ob["proof_documents"]),
            status=ob["status"],
            owner_focus=ob["owner_next_action"],
            blocked_reasons=["no_auto_execution", "no_broker_order_submit", "public_proof_blocked"],
            sensitivity="restricted",
        ),
        _lane_card(
            lane_id="soulaana",
            label="Soulaana Artist/IP Package",
            source_app="vault_soulaana_beta_service",
            source_route="/vault/soulaana-artist-ip-vault.json",
            setup_score=soulaana["readiness"]["setup_score"],
            record_count=len(soulaana["package_records"]),
            status=soulaana["status"],
            owner_focus=soulaana["owner_next_action"],
            blocked_reasons=["direct_upload_locked", "ai_generated_character_art_blocked", "legal_review_pending"],
            sensitivity="restricted",
        ),
        _lane_card(
            lane_id="beta",
            label="Private Beta Onboarding",
            source_app="vault_soulaana_beta_service",
            source_route="/vault/private-beta-onboarding-vault.json",
            setup_score=beta["readiness"]["setup_score"],
            record_count=len(beta["onboarding_records"]),
            status=beta["status"],
            owner_focus=beta["owner_next_action"],
            blocked_reasons=["tower_clearance_pending", "nda_missing_blocks_access", "public_beta_routes_blocked"],
            sensitivity="restricted",
        ),
    ]

    owner_actions = _collect_owner_actions()
    critical_actions = [action for action in owner_actions if action.get("priority") == "critical"]
    high_actions = [action for action in owner_actions if action.get("priority") == "high"]

    command_cards = [
        {
            "card_id": "vault_six_lane_foundation",
            "label": "Six-lane Vault foundation",
            "value": len(lane_cards),
            "status": "ready",
            "summary": "ATM, property, trust, OB proof, Soulaana, and beta lanes are linked.",
        },
        {
            "card_id": "vault_route_index",
            "label": "Route index",
            "value": len(_route_index()),
            "status": "ready",
            "summary": "UI and JSON routes are discoverable from one command source.",
        },
        {
            "card_id": "vault_owner_actions",
            "label": "Owner actions",
            "value": len(owner_actions),
            "status": "active",
            "summary": "All Vault owner actions are consolidated and priority sorted.",
        },
        {
            "card_id": "vault_direct_upload",
            "label": "Direct upload",
            "value": "locked",
            "status": "locked",
            "summary": "Direct uploads stay blocked until Tower storage clearance.",
        },
        {
            "card_id": "vault_clouds_source",
            "label": "Clouds source",
            "value": "ready",
            "status": "ready",
            "summary": "Clouds can read summary-only redacted Vault state.",
        },
        {
            "card_id": "vault_tower_guard",
            "label": "Tower guard",
            "value": "required",
            "status": "locked",
            "summary": "Vault never owns identity, clearance, or beta access permission authority.",
        },
    ]

    all_blocked_reasons = sorted(
        set(NO_DIRECT_UPLOAD_POLICY["blocked_now"])
        | set(acquisition["clouds_safe_source"]["blocked_reasons"])
        | set(trust_ob["clouds_safe_source"]["blocked_reasons"])
        | set(soulaana_beta["clouds_safe_source"]["blocked_reasons"])
        | {
            "direct_upload_locked",
            "tower_clearance_pending",
            "sensitive_fields_redacted",
            "public_proof_blocked",
            "ai_generated_character_art_blocked",
            "public_beta_routes_blocked",
        }
    )

    payload = {
        "app_id": "archive_vault",
        "app_name": "Archive Vault",
        "version": VAULT_VERSION,
        "payload_type": "unified_vault_command_center",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "private_invite_only": True,
        "command_center_status": "ready",
        "command_level": "six_lane_foundation_ready",
        "readiness_score": readiness["score"],
        "readiness_label": readiness["label"],
        "vault_status": {
            "status": vault_status["status"],
            "readiness_score": vault_status["readiness_score"],
            "packet_template_count": vault_status["packet_template_count"],
            "document_type_count": vault_status["document_type_count"],
            "direct_upload_allowed": vault_status["direct_upload_allowed"],
            "clouds_source_ready": vault_status["clouds_source_ready"],
        },
        "command_cards": command_cards,
        "lane_cards": lane_cards,
        "lane_count": len(lane_cards),
        "route_index": _route_index(),
        "route_count": len(_route_index()),
        "owner_focus_queue": owner_actions,
        "owner_action_count": len(owner_actions),
        "critical_owner_action_count": len(critical_actions),
        "high_owner_action_count": len(high_actions),
        "packet_board_summary": {
            "card_count": packet_board["card_count"],
            "filters": packet_board["board_filters"],
        },
        "document_drawer_summary": {
            "record_count": document_drawer["record_count"],
            "redaction_default": document_drawer["redaction_default"],
            "direct_upload_allowed": document_drawer["direct_upload_allowed"],
        },
        "boundary_wall": {
            "tower_permission_required": True,
            "vault_owns_permissions": False,
            "direct_upload_allowed": False,
            "redacted_view_default": True,
            "clouds_view": "summary_only_redacted",
            "broker_secrets_allowed": False,
            "auto_execution_allowed": False,
            "public_proof_allowed": False,
            "public_beta_routes_allowed": False,
            "ai_generated_character_art_allowed": False,
            "bank_account_details_hidden": True,
            "beneficiary_details_hidden": True,
            "blocked_reasons": all_blocked_reasons,
        },
        "clouds_safe_source_map": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "source_routes": [
                "/vault/command-center.json",
                "/vault/clouds-source.json",
                "/vault/acquisition-builders.json",
                "/vault/trust-ob-vault.json",
                "/vault/soulaana-beta-vault.json",
            ],
            "lane_summaries": [
                {
                    "lane_id": card["lane_id"],
                    "label": card["label"],
                    "setup_score": card["setup_score"],
                    "status": card["status"],
                    "record_count": card["record_count"],
                    "owner_focus": card["owner_focus"],
                }
                for card in lane_cards
            ],
            "hidden_sensitive_fields": sorted(set(REDACTION_POLICY["sensitive_fields"] + [
                "broker_credentials",
                "broker_api_key",
                "order_submit_token",
                "beneficiary_details",
                "bank_account_numbers",
                "artist_payment_details",
                "nda_body",
                "beta_tester_private_contact",
                "full_legal_document_body",
            ])),
        },
        "room_links": {
            "vault_room": "/vault",
            "command_center": "/vault/command-center",
            "acquisition_builders": "/vault/acquisition-builders",
            "trust_ob": "/vault/trust-ob",
            "soulaana_beta": "/vault/soulaana-beta",
            "clouds_source": clouds_source.get("route", "/vault/clouds-source.json"),
            "no_direct_upload": get_no_direct_upload_payload().get("route", "/vault/no-direct-upload.json"),
            "redacted_view_policy": get_redacted_view_policy_payload().get("route", "/vault/redacted-view-policy.json"),
        },
        "next_pack_recommendation": "Vault Giant Pack 007 should build Vault Search + Requirement Tracker + Expiration/Renewal wall.",
    }
    return attach_tower_guard(payload, "/vault/command-center.json")


def get_vault_gp006_status_payload() -> Dict[str, Any]:
    command = get_unified_vault_command_center_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp006_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 006",
        "built": [
            "unified_vault_command_center",
            "six_lane_readiness_wall",
            "vault_route_index",
            "consolidated_owner_focus_queue",
            "boundary_wall",
            "clouds_safe_source_map",
            "command_center_ui",
            "gp006_status_endpoint",
        ],
        "lane_count": command["lane_count"],
        "route_count": command["route_count"],
        "owner_action_count": command["owner_action_count"],
        "critical_owner_action_count": command["critical_owner_action_count"],
        "high_owner_action_count": command["high_owner_action_count"],
        "readiness_score": command["readiness_score"],
        "command_level": command["command_level"],
        "direct_upload_allowed": command["boundary_wall"]["direct_upload_allowed"],
        "vault_owns_permissions": command["boundary_wall"]["vault_owns_permissions"],
        "clouds_safe": command["clouds_safe_source_map"]["safe_for_clouds"],
        "safe_to_continue_to_gp007": True,
    }
    return attach_tower_guard(payload, "/vault/gp006-status.json")
