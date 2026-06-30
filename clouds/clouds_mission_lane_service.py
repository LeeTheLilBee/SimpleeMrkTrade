"""The Clouds Giant Pack 006 Mission Lane Board.

This pack creates the mission/business lane layer:
- Trust lane
- ATM lane
- Property lane
- OB lane
- Soulaana lane
- Private Beta lane
- Tower/Teller placeholder lanes
- Future apps lane

Boundary:
Clouds displays mission status and routes the owner to the owning app.
Clouds does not own the lane, move money, approve deals, unlock access, execute
trades, run payroll, upload documents, or replace any specialized app.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_app_lane_status_service import (
    get_clouds_app_lane_status_dashboard_payload,
    get_clouds_gp004_status_payload,
)
from .clouds_app_registry_service import (
    get_clouds_app_registry_payload,
    get_clouds_gp002_status_payload,
)
from .clouds_contracts import CLOUDS_VERSION, utc_now_iso
from .clouds_owner_focus_service import (
    get_clouds_gp003_status_payload,
    get_clouds_owner_focus_queue_payload,
)
from .clouds_service import (
    get_clouds_gp001_status_payload,
    get_clouds_vault_summary_payload,
)
from .clouds_today_service import (
    get_clouds_gp005_status_payload,
    get_clouds_today_dashboard_payload,
)

from vault.vault_command_center_service import get_unified_vault_command_center_payload
from vault.vault_final_readiness_service import get_vault_final_readiness_payload
from vault.vault_tracking_service import get_vault_search_tracker_payload
from vault.vault_receipt_control_service import get_receipt_control_center_payload
from vault.vault_export_service import get_export_preview_center_payload


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


MISSION_LANE_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "mission_lane_id": "trust",
        "label": "Trust / Entity",
        "short_label": "Trust",
        "mission_type": "ownership_governance",
        "owning_apps": ["archive_vault", "tower"],
        "primary_open_target": "/vault/trust-ob",
        "source_route": "/vault/trust-entity-vault.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Keep ownership, entity, trust, authority, and sensitive proof records organized and redacted.",
        "clouds_can_show": ["readiness", "document count", "blocked status", "open Vault trust room"],
        "clouds_must_not_do": ["show beneficiary details", "show bank details", "approve legal documents", "change authority"],
    },
    {
        "mission_lane_id": "atm",
        "label": "SimpleeOnTheGo / ATM",
        "short_label": "ATM",
        "mission_type": "acquisition_growth",
        "owning_apps": ["archive_vault", "simplee_on_the_go", "tower"],
        "primary_open_target": "/vault/acquisition-builders",
        "source_route": "/vault/atm-route-builder.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Prepare ATM route acquisition packets and use them when route targets appear.",
        "clouds_can_show": ["packet readiness", "target-needed status", "blocked reasons", "open acquisition builder"],
        "clouds_must_not_do": ["approve purchase", "move vault cash", "approve loan", "grant seller access"],
    },
    {
        "mission_lane_id": "property",
        "label": "SimpleeProperty / Apartments",
        "short_label": "Property",
        "mission_type": "acquisition_growth",
        "owning_apps": ["archive_vault", "simplee_property", "tower"],
        "primary_open_target": "/vault/acquisition-builders",
        "source_route": "/vault/apartment-lender-builder.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Prepare apartment lender/due diligence packet while property targets are searched.",
        "clouds_can_show": ["packet readiness", "lender packet status", "blocked reasons", "open acquisition builder"],
        "clouds_must_not_do": ["approve property deal", "approve loan", "replace diligence", "grant lender access"],
    },
    {
        "mission_lane_id": "observatory",
        "label": "The Observatory / OB",
        "short_label": "OB",
        "mission_type": "engine_proof_private",
        "owning_apps": ["observatory", "archive_vault", "tower"],
        "primary_open_target": "/vault/trust-ob",
        "source_route": "/vault/ob-manual-live-proof-vault.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Preserve private Manual Live proof and keep no-auto-execution boundaries locked.",
        "clouds_can_show": ["private proof readiness", "manual-live boundary", "open OB proof vault"],
        "clouds_must_not_do": ["execute trades", "review trades", "connect broker", "publish proof"],
    },
    {
        "mission_lane_id": "soulaana",
        "label": "Soulaana",
        "short_label": "Soulaana",
        "mission_type": "creative_ip",
        "owning_apps": ["archive_vault", "soulaana", "tower"],
        "primary_open_target": "/vault/soulaana-beta",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Preserve Soulaana IP, reserved art slots, canon references, and no-AI-character-art boundary.",
        "clouds_can_show": ["reserved art slot status", "IP packet readiness", "open Soulaana vault"],
        "clouds_must_not_do": ["generate character art", "approve IP terms", "show private artist details", "override creative boundary"],
    },
    {
        "mission_lane_id": "beta",
        "label": "Private Beta",
        "short_label": "Beta",
        "mission_type": "private_access",
        "owning_apps": ["archive_vault", "tower"],
        "primary_open_target": "/vault/soulaana-beta",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "status_mode": "vault_summary_ready",
        "owner_intent": "Track invite, NDA, Tower clearance, scope, feedback consent, and revocation paths.",
        "clouds_can_show": ["onboarding status", "Tower clearance reminder", "open beta vault"],
        "clouds_must_not_do": ["invite testers", "grant access", "show NDA body", "override Tower clearance"],
    },
    {
        "mission_lane_id": "tower",
        "label": "The Tower",
        "short_label": "Tower",
        "mission_type": "security_authority",
        "owning_apps": ["tower"],
        "primary_open_target": "/clouds/app-registry#clouds_app_tower",
        "source_route": "not_connected",
        "status_mode": "placeholder_not_connected",
        "owner_intent": "Future Tower summary should show identity, permissions, clearance, audit, and locks without letting Clouds control them.",
        "clouds_can_show": ["placeholder", "future source slot", "authority reminder"],
        "clouds_must_not_do": ["grant permissions", "change roles", "revoke access", "own audit"],
    },
    {
        "mission_lane_id": "teller",
        "label": "The Teller",
        "short_label": "Teller",
        "mission_type": "people_payments",
        "owning_apps": ["teller", "tower"],
        "primary_open_target": "/clouds/app-registry#clouds_app_teller",
        "source_route": "not_connected",
        "status_mode": "placeholder_not_connected",
        "owner_intent": "Future Teller summary should show people, payroll, payment, onboarding, and vendor packet health.",
        "clouds_can_show": ["placeholder", "future source slot", "authority reminder"],
        "clouds_must_not_do": ["run payroll", "change direct deposit", "approve payments", "show employee-sensitive records"],
    },
    {
        "mission_lane_id": "future_apps",
        "label": "Future Businesses",
        "short_label": "Future",
        "mission_type": "future_growth",
        "owning_apps": ["clouds", "tower", "future_app"],
        "primary_open_target": "/clouds/app-registry",
        "source_route": "not_connected",
        "status_mode": "future_slot",
        "owner_intent": "Reserve space for laundromat, farming, grocery, land, skincare, and later operating apps without building them too early.",
        "clouds_can_show": ["future slots", "planning status", "open registry"],
        "clouds_must_not_do": ["invent live data", "claim source connected", "replace future app"],
    },
]


def _priority_rank(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 9)


def _mission_status(status_mode: str, setup_score: int | None, blocked_count: int, focus_count: int) -> str:
    if status_mode == "placeholder_not_connected":
        return "placeholder"
    if status_mode == "future_slot":
        return "future"
    if blocked_count:
        return "watch"
    if setup_score == 100:
        return "ready"
    if focus_count:
        return "active"
    return "ready"


def get_clouds_mission_lane_registry_payload() -> Dict[str, Any]:
    registry = get_clouds_app_registry_payload()
    app_ids = {app["registered_app_id"] for app in registry["apps"]}

    lane_registry = []
    for lane in MISSION_LANE_DEFINITIONS:
        lane_registry.append(
            {
                **lane,
                "registered_owning_apps": [app for app in lane["owning_apps"] if app in app_ids],
                "missing_owning_apps": [app for app in lane["owning_apps"] if app not in app_ids],
                "clouds_role": "show_mission_summary_and_route_owner",
                "clouds_can_complete": False,
                "owning_apps_keep_authority": True,
            }
        )

    payload = {
        **_base_payload("/clouds/mission-lane-registry.json", "clouds_mission_lane_registry"),
        "status": "ready",
        "mission_lane_count": len(lane_registry),
        "vault_backed_lane_count": sum(1 for lane in lane_registry if lane["status_mode"] == "vault_summary_ready"),
        "placeholder_lane_count": sum(1 for lane in lane_registry if lane["status_mode"] == "placeholder_not_connected"),
        "future_lane_count": sum(1 for lane in lane_registry if lane["status_mode"] == "future_slot"),
        "mission_lanes": lane_registry,
        "boundary": {
            "clouds_is_mission_dashboard": True,
            "clouds_is_not_mission_owner": True,
            "owning_apps_keep_authority": True,
            "summary_only_redacted": True,
            "future_slots_are_not_live_sources": True,
        },
    }
    return payload


def get_clouds_mission_lane_status_payload() -> Dict[str, Any]:
    mission_registry = get_clouds_mission_lane_registry_payload()
    command = get_unified_vault_command_center_payload()
    focus = get_clouds_owner_focus_queue_payload()
    tracker = get_vault_search_tracker_payload()
    receipt = get_receipt_control_center_payload()
    export = get_export_preview_center_payload()
    today = get_clouds_today_dashboard_payload()
    app_lane_status = get_clouds_app_lane_status_dashboard_payload()

    vault_lane_lookup = {
        lane["lane_id"]: lane
        for lane in command["lane_cards"]
    }

    focus_by_lane: Dict[str, List[Dict[str, Any]]] = {}
    for item in focus["focus_items"]:
        focus_by_lane.setdefault(item["business_lane"], []).append(item)

    requirement_summary = tracker["requirement_tracker"]["lane_summary"]

    mission_cards = []
    for lane in mission_registry["mission_lanes"]:
        lane_id = lane["mission_lane_id"]
        vault_lane = vault_lane_lookup.get(lane_id)
        lane_focus = focus_by_lane.get(lane_id, [])
        req = requirement_summary.get(lane_id, {})
        setup_score = vault_lane["setup_score"] if vault_lane else None
        blocked_focus_count = sum(1 for item in lane_focus if item["blocked_by"])
        ready_focus_count = sum(1 for item in lane_focus if not item["blocked_by"])
        critical_count = sum(1 for item in lane_focus if item["priority"] == "critical")
        high_count = sum(1 for item in lane_focus if item["priority"] == "high")
        status = _mission_status(lane["status_mode"], setup_score, blocked_focus_count, len(lane_focus))

        mission_cards.append(
            {
                "mission_lane_id": lane_id,
                "label": lane["label"],
                "short_label": lane["short_label"],
                "mission_type": lane["mission_type"],
                "status": status,
                "status_mode": lane["status_mode"],
                "source_route": lane["source_route"],
                "primary_open_target": lane["primary_open_target"],
                "owning_apps": lane["owning_apps"],
                "setup_score": setup_score,
                "record_count": vault_lane["record_count"] if vault_lane else 0,
                "required_count": req.get("required", 0),
                "attached_count": req.get("attached", 0),
                "blocked_requirement_count": req.get("blocked", 0),
                "focus_count": len(lane_focus),
                "critical_count": critical_count,
                "high_count": high_count,
                "blocked_focus_count": blocked_focus_count,
                "ready_focus_count": ready_focus_count,
                "owner_intent": lane["owner_intent"],
                "clouds_can_show": lane["clouds_can_show"],
                "clouds_must_not_do": lane["clouds_must_not_do"],
                "top_focus_items": sorted(
                    lane_focus,
                    key=lambda item: (_priority_rank(item["priority"]), bool(item["blocked_by"]), item["focus_id"]),
                )[:4],
                "clouds_can_complete": False,
                "clouds_can_route": True,
                "owning_apps_keep_authority": True,
            }
        )

    mission_cards.sort(
        key=lambda card: (
            {"watch": 0, "ready": 1, "active": 2, "placeholder": 3, "future": 4}.get(card["status"], 9),
            card["mission_lane_id"],
        )
    )

    payload = {
        **_base_payload("/clouds/mission-lane-status.json", "clouds_mission_lane_status"),
        "status": "ready",
        "mission_card_count": len(mission_cards),
        "ready_count": sum(1 for card in mission_cards if card["status"] == "ready"),
        "watch_count": sum(1 for card in mission_cards if card["status"] == "watch"),
        "placeholder_count": sum(1 for card in mission_cards if card["status"] == "placeholder"),
        "future_count": sum(1 for card in mission_cards if card["status"] == "future"),
        "vault_backed_count": sum(1 for card in mission_cards if card["status_mode"] == "vault_summary_ready"),
        "mission_cards": mission_cards,
        "supporting_summary": {
            "receipt_count": receipt["receipt_chain_console"]["receipt_count"],
            "locked_export_count": export["export_lock_console"]["locked_export_count"],
            "today_focus_count": today["today_focus"]["focus_count"],
            "app_status_card_count": len(app_lane_status["app_status_cards"]),
        },
        "boundary": {
            "mission_status_is_summary_only": True,
            "clouds_routes_to_owning_app": True,
            "clouds_does_not_complete_lane_actions": True,
            "owning_apps_keep_authority": True,
        },
    }
    return payload


def get_clouds_mission_lane_focus_payload() -> Dict[str, Any]:
    status = get_clouds_mission_lane_status_payload()

    lane_focus = []
    for card in status["mission_cards"]:
        lane_focus.append(
            {
                "mission_lane_id": card["mission_lane_id"],
                "label": card["label"],
                "status": card["status"],
                "focus_count": card["focus_count"],
                "critical_count": card["critical_count"],
                "high_count": card["high_count"],
                "blocked_focus_count": card["blocked_focus_count"],
                "blocked_requirement_count": card["blocked_requirement_count"],
                "owner_intent": card["owner_intent"],
                "primary_open_target": card["primary_open_target"],
                "top_focus_items": card["top_focus_items"],
                "owner_next_action": (
                    "Open owning app for lane action."
                    if card["status"] in {"ready", "watch", "active"}
                    else "Keep visible as a future/placeholder lane until source contract exists."
                ),
            }
        )

    payload = {
        **_base_payload("/clouds/mission-lane-focus.json", "clouds_mission_lane_focus"),
        "status": "ready",
        "lane_focus_count": len(lane_focus),
        "watch_lane_count": sum(1 for lane in lane_focus if lane["status"] == "watch"),
        "placeholder_or_future_count": sum(1 for lane in lane_focus if lane["status"] in {"placeholder", "future"}),
        "lane_focus": lane_focus,
        "boundary": {
            "focus_is_visibility_only": True,
            "clouds_routes_only": True,
            "owning_apps_act": True,
        },
    }
    return payload


def get_clouds_future_lane_slots_payload() -> Dict[str, Any]:
    future_slots = [
        {
            "future_slot_id": "luxe_laundromat",
            "label": "Luxe Laundromat",
            "status": "future_slot",
            "owning_app_future": "laundromat_app_later",
            "clouds_role": "reserve dashboard slot only",
            "not_live_reason": "No operating source contract yet.",
        },
        {
            "future_slot_id": "simplee_farming",
            "label": "SimpleeFarming",
            "status": "future_slot",
            "owning_app_future": "farming_app_later",
            "clouds_role": "reserve dashboard slot only",
            "not_live_reason": "No operating source contract yet.",
        },
        {
            "future_slot_id": "simplee_grocery",
            "label": "SimpleeGrocery",
            "status": "future_slot",
            "owning_app_future": "grocery_app_later",
            "clouds_role": "reserve dashboard slot only",
            "not_live_reason": "No operating source contract yet.",
        },
        {
            "future_slot_id": "simplee_land",
            "label": "SimpleeLand",
            "status": "future_slot",
            "owning_app_future": "land_app_later",
            "clouds_role": "reserve dashboard slot only",
            "not_live_reason": "No operating source contract yet.",
        },
        {
            "future_slot_id": "simplee_skincare",
            "label": "SimpleeSkincare",
            "status": "future_slot",
            "owning_app_future": "skincare_app_later",
            "clouds_role": "reserve dashboard slot only",
            "not_live_reason": "No operating source contract yet.",
        },
    ]

    payload = {
        **_base_payload("/clouds/future-lane-slots.json", "clouds_future_lane_slots"),
        "status": "ready",
        "future_slot_count": len(future_slots),
        "future_slots": future_slots,
        "boundary": {
            "future_slots_are_not_live_apps": True,
            "clouds_does_not_invent_operating_data": True,
            "source_contract_required_before_live_status": True,
        },
    }
    return payload


def get_clouds_mission_lane_dashboard_payload() -> Dict[str, Any]:
    registry = get_clouds_mission_lane_registry_payload()
    status = get_clouds_mission_lane_status_payload()
    focus = get_clouds_mission_lane_focus_payload()
    future = get_clouds_future_lane_slots_payload()
    today = get_clouds_today_dashboard_payload()
    vault_final = get_vault_final_readiness_payload()
    gp001 = get_clouds_gp001_status_payload()
    gp002 = get_clouds_gp002_status_payload()
    gp003 = get_clouds_gp003_status_payload()
    gp004 = get_clouds_gp004_status_payload()
    gp005 = get_clouds_gp005_status_payload()

    payload = {
        **_base_payload("/clouds/mission-lane-dashboard.json", "clouds_mission_lane_dashboard"),
        "status": "ready",
        "dashboard_label": "Clouds Mission Lane Board",
        "mission_registry": {
            "mission_lane_count": registry["mission_lane_count"],
            "vault_backed_lane_count": registry["vault_backed_lane_count"],
            "placeholder_lane_count": registry["placeholder_lane_count"],
            "future_lane_count": registry["future_lane_count"],
        },
        "mission_status": {
            "mission_card_count": status["mission_card_count"],
            "ready_count": status["ready_count"],
            "watch_count": status["watch_count"],
            "placeholder_count": status["placeholder_count"],
            "future_count": status["future_count"],
            "vault_backed_count": status["vault_backed_count"],
        },
        "mission_focus": {
            "lane_focus_count": focus["lane_focus_count"],
            "watch_lane_count": focus["watch_lane_count"],
            "placeholder_or_future_count": focus["placeholder_or_future_count"],
        },
        "future_slots": {
            "future_slot_count": future["future_slot_count"],
            "slots": future["future_slots"],
        },
        "today_summary": {
            "focus_count": today["today_focus"]["focus_count"],
            "critical_count": today["today_focus"]["critical_count"],
            "blocked_count": today["today_focus"]["blocked_count"],
        },
        "vault_summary": {
            "final_score": vault_final["final_score"],
            "safe_to_start_clouds": vault_final["safe_to_start_clouds"],
            "readiness_label": vault_final["readiness_label"],
        },
        "prior_pack_status": {
            "gp001": gp001["status"],
            "gp002": gp002["status"],
            "gp003": gp003["status"],
            "gp004": gp004["status"],
            "gp005": gp005["status"],
        },
        "mission_cards": status["mission_cards"],
        "lane_focus": focus["lane_focus"],
        "open_app_targets": sorted({card["primary_open_target"] for card in status["mission_cards"]}),
        "boundary": {
            "clouds_is_mission_visibility_layer": True,
            "clouds_is_not_operating_app": True,
            "summary_only_redacted": True,
            "owning_apps_keep_authority": True,
            "future_slots_not_live": True,
        },
        "next_pack_recommendation": "Clouds GP007 should build Owner Decision Desk summary layer across mission lanes.",
    }
    return payload


def get_clouds_gp006_status_payload() -> Dict[str, Any]:
    dashboard = get_clouds_mission_lane_dashboard_payload()

    payload = {
        **_base_payload("/clouds/gp006-status.json", "clouds_gp006_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 006",
        "built": [
            "mission_lane_registry",
            "mission_lane_status_board",
            "mission_lane_focus_rollup",
            "trust_atm_property_ob_soulaana_beta_cards",
            "tower_teller_placeholder_mission_lanes",
            "future_lane_slots",
            "mission_lane_dashboard_ui",
            "gp006_status_endpoint",
        ],
        "mission_lane_count": dashboard["mission_registry"]["mission_lane_count"],
        "vault_backed_lane_count": dashboard["mission_registry"]["vault_backed_lane_count"],
        "placeholder_lane_count": dashboard["mission_registry"]["placeholder_lane_count"],
        "future_lane_count": dashboard["mission_registry"]["future_lane_count"],
        "mission_card_count": dashboard["mission_status"]["mission_card_count"],
        "watch_count": dashboard["mission_status"]["watch_count"],
        "future_slot_count": dashboard["future_slots"]["future_slot_count"],
        "vault_final_score": dashboard["vault_summary"]["final_score"],
        "prior_gp001_status": dashboard["prior_pack_status"]["gp001"],
        "prior_gp002_status": dashboard["prior_pack_status"]["gp002"],
        "prior_gp003_status": dashboard["prior_pack_status"]["gp003"],
        "prior_gp004_status": dashboard["prior_pack_status"]["gp004"],
        "prior_gp005_status": dashboard["prior_pack_status"]["gp005"],
        "clouds_is_mission_visibility_layer": True,
        "clouds_is_not_operating_app": True,
        "summary_only_redacted": True,
        "safe_to_continue_to_clouds_gp007": True,
    }
    return payload
