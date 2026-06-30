"""The Clouds Giant Pack 002 App Registry Shell.

This pack widens The Clouds without overstepping:
- App Registry shell
- Tower placeholder source card
- OB placeholder source card
- Teller placeholder source card
- ATM / Property / Soulaana / Beta registry cards
- authority boundary map
- open-app handoff registry
- Clouds source readiness wall

Boundary:
Clouds sees summary status and routes the owner to the owning app. Clouds does
not own Tower permissions, Vault documents, OB trading/proof, Teller people/payroll,
ATM operations, Property diligence, Soulaana IP, or Beta access.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_contracts import CLOUDS_VERSION, utc_now_iso
from .clouds_service import (
    get_clouds_command_dashboard_payload,
    get_clouds_source_map_payload,
    get_clouds_status_payload,
    get_clouds_vault_summary_payload,
)


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


APP_REGISTRY: List[Dict[str, Any]] = [
    {
        "registered_app_id": "archive_vault",
        "label": "Archive Vault",
        "short_label": "Vault",
        "registry_status": "live_source_ready",
        "source_status": "connected_summary_only",
        "authority_owner": "Archive Vault + Tower",
        "clouds_role": "read_summary_and_open_vault",
        "primary_route": "/vault",
        "summary_route": "/clouds/vault-summary.json",
        "source_route": "/vault/final-readiness.json",
        "business_lanes": ["vault", "atm", "property", "trust", "observatory", "soulaana", "beta"],
        "what_clouds_can_show": [
            "readiness",
            "lane counts",
            "record counts",
            "requirement counts",
            "receipt counts",
            "locked export counts",
            "owner focus",
            "blocked reason summaries",
        ],
        "what_clouds_must_not_do": [
            "unlock uploads",
            "approve exports",
            "show unredacted packet bodies",
            "own documents",
            "own receipts",
        ],
        "tone": "ready",
    },
    {
        "registered_app_id": "tower",
        "label": "The Tower",
        "short_label": "Tower",
        "registry_status": "placeholder_source_card_ready",
        "source_status": "not_connected_yet",
        "authority_owner": "The Tower",
        "clouds_role": "show placeholder and open Tower when source exists",
        "primary_route": "/tower",
        "summary_route": "/clouds/app-registry.json#tower",
        "source_route": "not_connected",
        "business_lanes": ["identity", "permissions", "security", "clearance", "audit", "freeze_revoke"],
        "what_clouds_can_show": [
            "placeholder status",
            "authority reminder",
            "future Tower health summary",
            "future clearance summary",
        ],
        "what_clouds_must_not_do": [
            "grant permissions",
            "change roles",
            "clear users",
            "step-up approve",
            "revoke access",
            "own audit",
        ],
        "tone": "locked",
    },
    {
        "registered_app_id": "observatory",
        "label": "The Observatory",
        "short_label": "OB",
        "registry_status": "placeholder_source_card_ready",
        "source_status": "not_connected_yet",
        "authority_owner": "The Observatory + Tower",
        "clouds_role": "show placeholder and open OB when source exists",
        "primary_route": "/ob",
        "summary_route": "/clouds/app-registry.json#observatory",
        "source_route": "not_connected",
        "business_lanes": ["observatory", "manual_live", "signals", "review", "proof_private"],
        "what_clouds_can_show": [
            "placeholder status",
            "mode reminder",
            "future readiness summary",
            "future owner focus",
        ],
        "what_clouds_must_not_do": [
            "detect trades",
            "review trades",
            "execute trades",
            "connect broker",
            "publish proof",
            "override Manual Live boundary",
        ],
        "tone": "locked",
    },
    {
        "registered_app_id": "teller",
        "label": "The Teller",
        "short_label": "Teller",
        "registry_status": "placeholder_source_card_ready",
        "source_status": "not_connected_yet",
        "authority_owner": "The Teller + Tower",
        "clouds_role": "show placeholder and open Teller when source exists",
        "primary_route": "/teller",
        "summary_route": "/clouds/app-registry.json#teller",
        "source_route": "not_connected",
        "business_lanes": ["people", "payroll", "payments", "onboarding", "vendor_packets"],
        "what_clouds_can_show": [
            "placeholder status",
            "future payroll packet summary",
            "future onboarding summary",
            "future people workflow health",
        ],
        "what_clouds_must_not_do": [
            "run payroll",
            "change direct deposit",
            "own employee sensitive records",
            "approve vendor payments",
            "grant Teller permissions",
        ],
        "tone": "locked",
    },
    {
        "registered_app_id": "simplee_on_the_go",
        "label": "SimpleeOnTheGo",
        "short_label": "ATM",
        "registry_status": "vault_packet_source_ready",
        "source_status": "vault_summary_only",
        "authority_owner": "ATM operating app later + Vault packet records + Tower",
        "clouds_role": "show Vault ATM packet readiness and future ATM ops summary",
        "primary_route": "/vault/acquisition-builders",
        "summary_route": "/clouds/vault-summary.json",
        "source_route": "/vault/atm-route-builder.json",
        "business_lanes": ["atm", "route_acquisition", "vault_cash", "lender_packet"],
        "what_clouds_can_show": [
            "ATM packet readiness",
            "target-needed status",
            "vault cash reminder",
            "open Vault acquisition builder",
        ],
        "what_clouds_must_not_do": [
            "approve route purchase",
            "approve loan",
            "move vault cash",
            "upload seller documents",
            "grant external access",
        ],
        "tone": "ready",
    },
    {
        "registered_app_id": "simplee_property",
        "label": "SimpleeProperty",
        "short_label": "Property",
        "registry_status": "vault_packet_source_ready",
        "source_status": "vault_summary_only",
        "authority_owner": "Property operating app later + Vault packet records + Tower",
        "clouds_role": "show Vault property packet readiness and future property ops summary",
        "primary_route": "/vault/acquisition-builders",
        "summary_route": "/clouds/vault-summary.json",
        "source_route": "/vault/apartment-lender-builder.json",
        "business_lanes": ["property", "apartment_search", "lender_packet", "due_diligence"],
        "what_clouds_can_show": [
            "property packet readiness",
            "target-needed status",
            "lender packet reminder",
            "open Vault acquisition builder",
        ],
        "what_clouds_must_not_do": [
            "approve property purchase",
            "approve loan",
            "replace due diligence",
            "upload rent rolls",
            "grant lender access",
        ],
        "tone": "ready",
    },
    {
        "registered_app_id": "soulaana",
        "label": "Soulaana",
        "short_label": "Soulaana",
        "registry_status": "vault_packet_source_ready",
        "source_status": "vault_summary_only",
        "authority_owner": "Soulaana IP package + Vault + Tower",
        "clouds_role": "show reserved art/IP packet summary only",
        "primary_route": "/vault/soulaana-beta",
        "summary_route": "/clouds/vault-summary.json",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "business_lanes": ["soulaana", "artist_ip", "reserved_art_slots", "canon"],
        "what_clouds_can_show": [
            "reserved art slot count",
            "IP packet readiness",
            "no-AI-character-art boundary",
            "open Vault Soulaana room",
        ],
        "what_clouds_must_not_do": [
            "generate character art",
            "show unaccepted art files",
            "show artist payment details",
            "approve IP terms",
            "override creative boundary",
        ],
        "tone": "ready",
    },
    {
        "registered_app_id": "private_beta",
        "label": "Private Beta",
        "short_label": "Beta",
        "registry_status": "vault_packet_source_ready",
        "source_status": "vault_summary_only",
        "authority_owner": "Tower access + Vault onboarding records",
        "clouds_role": "show beta onboarding packet summary only",
        "primary_route": "/vault/soulaana-beta",
        "summary_route": "/clouds/vault-summary.json",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "business_lanes": ["beta", "invite", "nda", "tower_clearance", "access_scope"],
        "what_clouds_can_show": [
            "beta packet readiness",
            "NDA/access scope reminder",
            "Tower clearance reminder",
            "open Vault beta room",
        ],
        "what_clouds_must_not_do": [
            "invite beta testers",
            "grant beta access",
            "show NDA body",
            "show tester private contact",
            "override Tower clearance",
        ],
        "tone": "ready",
    },
]


def get_clouds_app_registry_payload() -> Dict[str, Any]:
    source_map = get_clouds_source_map_payload()
    vault_summary = get_clouds_vault_summary_payload()

    ready_apps = [app for app in APP_REGISTRY if app["tone"] == "ready"]
    locked_apps = [app for app in APP_REGISTRY if app["tone"] == "locked"]

    payload = {
        **_base_payload("/clouds/app-registry.json", "clouds_app_registry"),
        "status": "ready",
        "registry_label": "The Clouds App Registry",
        "registered_app_count": len(APP_REGISTRY),
        "ready_app_count": len(ready_apps),
        "locked_placeholder_count": len(locked_apps),
        "apps": APP_REGISTRY,
        "first_connected_source": {
            "app_id": "archive_vault",
            "status": vault_summary["status"],
            "final_score": vault_summary["vault"]["final_score"],
            "clouds_view": vault_summary["vault"]["clouds_view"],
        },
        "source_map_summary": {
            "source_count": source_map["source_count"],
            "vault_handoff_status": source_map["vault_handoff_status"],
            "vault_handoff_view": source_map["vault_handoff_view"],
        },
        "registry_boundary": {
            "clouds_is_registry_not_authority": True,
            "owning_app_keeps_authority": True,
            "tower_keeps_permissions": True,
            "summary_only_redacted": True,
            "open_app_handoff_only": True,
        },
    }
    return payload


def get_clouds_placeholder_sources_payload() -> Dict[str, Any]:
    placeholders = [
        app for app in APP_REGISTRY
        if app["registry_status"] == "placeholder_source_card_ready"
    ]

    payload = {
        **_base_payload("/clouds/placeholder-sources.json", "clouds_placeholder_sources"),
        "status": "ready",
        "placeholder_count": len(placeholders),
        "placeholders": placeholders,
        "placeholder_apps": [app["registered_app_id"] for app in placeholders],
        "why_placeholder": "The app belongs on the owner dashboard, but Clouds has no live safe source contract for it yet.",
        "boundary": {
            "placeholder_does_not_mean_connected": True,
            "placeholder_does_not_grant_authority": True,
            "clouds_must_wait_for_source_contract": True,
            "owner_can_see_future_slot": True,
        },
    }
    return payload


def get_clouds_authority_map_payload() -> Dict[str, Any]:
    authority_rows = [
        {
            "authority_id": "tower_authority",
            "system": "The Tower",
            "owns": [
                "identity",
                "permissions",
                "roles",
                "clearance",
                "step_up",
                "export_locks",
                "freeze",
                "revoke",
                "audit",
            ],
            "clouds_can": ["show summary", "open Tower route later"],
            "clouds_cannot": ["grant permission", "change role", "clear user", "revoke access"],
        },
        {
            "authority_id": "vault_authority",
            "system": "Archive Vault",
            "owns": [
                "document indexes",
                "packet records",
                "receipt records",
                "redaction policy",
                "export previews",
                "Vault source routes",
            ],
            "clouds_can": ["show summary", "open Vault route"],
            "clouds_cannot": ["upload files", "approve export", "show sensitive body"],
        },
        {
            "authority_id": "ob_authority",
            "system": "The Observatory",
            "owns": [
                "market rooms",
                "signals",
                "manual live review",
                "OB private proof source",
                "trade center",
            ],
            "clouds_can": ["show future summary", "open OB route later"],
            "clouds_cannot": ["execute", "review trades", "connect broker", "publish proof"],
        },
        {
            "authority_id": "teller_authority",
            "system": "The Teller",
            "owns": [
                "people workflows",
                "payroll packet",
                "payment status",
                "onboarding",
                "vendor workflows",
            ],
            "clouds_can": ["show future summary", "open Teller route later"],
            "clouds_cannot": ["run payroll", "change direct deposit", "approve payment"],
        },
        {
            "authority_id": "clouds_authority",
            "system": "The Clouds",
            "owns": [
                "owner command visibility",
                "summary cards",
                "source map",
                "open-app handoffs",
                "focus queue display",
            ],
            "clouds_can": ["show command overview", "route owner to owning app"],
            "clouds_cannot": ["become the system of record", "override owning apps"],
        },
    ]

    payload = {
        **_base_payload("/clouds/authority-map.json", "clouds_authority_map"),
        "status": "ready",
        "authority_row_count": len(authority_rows),
        "authority_rows": authority_rows,
        "boundary": {
            "clouds_is_command_layer": True,
            "clouds_is_not_system_of_record": True,
            "clouds_routes_to_owning_app": True,
        },
    }
    return payload


def get_clouds_app_registry_dashboard_payload() -> Dict[str, Any]:
    registry = get_clouds_app_registry_payload()
    placeholders = get_clouds_placeholder_sources_payload()
    authority = get_clouds_authority_map_payload()
    gp001_dashboard = get_clouds_command_dashboard_payload()
    gp001_status = get_clouds_status_payload()

    app_cards = []
    for app in registry["apps"]:
        app_cards.append(
            {
                "card_id": f"clouds_app_{app['registered_app_id']}",
                "label": app["label"],
                "short_label": app["short_label"],
                "status": app["registry_status"],
                "source_status": app["source_status"],
                "tone": app["tone"],
                "authority_owner": app["authority_owner"],
                "clouds_role": app["clouds_role"],
                "primary_route": app["primary_route"],
                "source_route": app["source_route"],
                "business_lanes": app["business_lanes"],
                "owner_next_action": "Open owning app route if a real action is needed; Clouds stays summary-only.",
            }
        )

    payload = {
        **_base_payload("/clouds/app-registry-dashboard.json", "clouds_app_registry_dashboard"),
        "status": "ready",
        "dashboard_label": "Clouds App Registry Dashboard",
        "registered_app_count": registry["registered_app_count"],
        "ready_app_count": registry["ready_app_count"],
        "locked_placeholder_count": registry["locked_placeholder_count"],
        "placeholder_count": placeholders["placeholder_count"],
        "authority_row_count": authority["authority_row_count"],
        "app_card_count": len(app_cards),
        "app_cards": app_cards,
        "placeholder_apps": placeholders["placeholder_apps"],
        "authority_map": authority["authority_rows"],
        "gp001_status": {
            "status": gp001_status["status"],
            "card_count": gp001_status["card_count"],
            "vault_final_score": gp001_status["vault_final_score"],
        },
        "gp001_dashboard_card_count": gp001_dashboard["card_count"],
        "next_pack_recommendation": "Clouds GP003 should build Owner Focus Queue v1 across Vault plus Tower/OB/Teller placeholders.",
    }
    return payload


def get_clouds_gp002_status_payload() -> Dict[str, Any]:
    dashboard = get_clouds_app_registry_dashboard_payload()
    registry = get_clouds_app_registry_payload()
    placeholders = get_clouds_placeholder_sources_payload()
    authority = get_clouds_authority_map_payload()

    payload = {
        **_base_payload("/clouds/gp002-status.json", "clouds_gp002_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 002",
        "built": [
            "app_registry_shell",
            "tower_placeholder_source_card",
            "ob_placeholder_source_card",
            "teller_placeholder_source_card",
            "atm_property_soulaana_beta_registry_cards",
            "authority_boundary_map",
            "open_app_handoff_registry",
            "app_registry_dashboard_ui",
            "gp002_status_endpoint",
        ],
        "registered_app_count": registry["registered_app_count"],
        "ready_app_count": registry["ready_app_count"],
        "locked_placeholder_count": registry["locked_placeholder_count"],
        "placeholder_count": placeholders["placeholder_count"],
        "authority_row_count": authority["authority_row_count"],
        "app_card_count": len(dashboard["app_cards"]),
        "clouds_owns_permissions": False,
        "clouds_is_system_of_record": False,
        "summary_only_redacted": True,
        "safe_to_continue_to_clouds_gp003": True,
    }
    return payload
