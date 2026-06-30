"""The Clouds Giant Pack 004 App/Lane Status Board.

This pack builds the operating status layer for The Clouds:
- App status board
- Lane status board
- Vault live source health card
- Tower / OB / Teller placeholder health cards
- Blocked/source-not-connected visibility
- Open-app status handoff targets

Boundary:
Clouds shows status and routes the owner. Clouds does not become the owning app,
does not grant access, does not approve exports, does not upload documents,
does not execute trades, and does not run payroll.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_app_registry_service import (
    get_clouds_app_registry_dashboard_payload,
    get_clouds_app_registry_payload,
    get_clouds_authority_map_payload,
    get_clouds_gp002_status_payload,
    get_clouds_placeholder_sources_payload,
)
from .clouds_contracts import CLOUDS_VERSION, utc_now_iso
from .clouds_owner_focus_service import (
    get_clouds_blocked_watch_payload,
    get_clouds_focus_lanes_payload,
    get_clouds_gp003_status_payload,
    get_clouds_owner_focus_dashboard_payload,
    get_clouds_owner_focus_queue_payload,
)
from .clouds_service import (
    get_clouds_command_dashboard_payload,
    get_clouds_gp001_status_payload,
    get_clouds_source_map_payload,
    get_clouds_vault_summary_payload,
)

from vault.vault_final_readiness_service import get_vault_final_readiness_payload
from vault.vault_command_center_service import get_unified_vault_command_center_payload
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


def _health_label(source_status: str, registry_status: str, tone: str) -> str:
    if source_status == "connected_summary_only":
        return "live_summary_ready"
    if source_status == "vault_summary_only":
        return "vault_summary_ready"
    if source_status == "not_connected_yet":
        return "placeholder_not_connected"
    if tone == "locked":
        return "locked_placeholder"
    if "ready" in registry_status:
        return "ready"
    return "watch"


def _status_rank(status: str) -> int:
    order = {
        "live_summary_ready": 0,
        "vault_summary_ready": 1,
        "ready": 2,
        "placeholder_not_connected": 3,
        "locked_placeholder": 4,
        "watch": 5,
    }
    return order.get(status, 9)


def get_clouds_app_status_board_payload() -> Dict[str, Any]:
    registry = get_clouds_app_registry_payload()
    focus = get_clouds_owner_focus_queue_payload()
    placeholders = get_clouds_placeholder_sources_payload()

    focus_by_app: Dict[str, List[Dict[str, Any]]] = {}
    for item in focus["focus_items"]:
        focus_by_app.setdefault(item["source_app"], []).append(item)

    placeholder_ids = set(placeholders["placeholder_apps"])

    app_status_cards = []
    for app in registry["apps"]:
        app_id = app["registered_app_id"]
        app_focus = focus_by_app.get(app_id, [])
        health = _health_label(app["source_status"], app["registry_status"], app["tone"])
        blocked_focus_count = sum(1 for item in app_focus if item["blocked_by"])
        ready_focus_count = sum(1 for item in app_focus if not item["blocked_by"])

        app_status_cards.append(
            {
                "app_id": app_id,
                "label": app["label"],
                "short_label": app["short_label"],
                "health": health,
                "registry_status": app["registry_status"],
                "source_status": app["source_status"],
                "tone": app["tone"],
                "authority_owner": app["authority_owner"],
                "clouds_role": app["clouds_role"],
                "primary_route": app["primary_route"],
                "source_route": app["source_route"],
                "business_lanes": app["business_lanes"],
                "focus_count": len(app_focus),
                "blocked_focus_count": blocked_focus_count,
                "ready_focus_count": ready_focus_count,
                "is_placeholder": app_id in placeholder_ids,
                "clouds_can_route": True,
                "clouds_can_complete": False,
                "owning_app_keeps_authority": True,
                "owner_next_action": (
                    "Open the owning app route if action is needed."
                    if app_id not in placeholder_ids
                    else "Keep as placeholder until the owning app exposes a safe summary source contract."
                ),
            }
        )

    app_status_cards.sort(key=lambda item: (_status_rank(item["health"]), item["label"]))

    payload = {
        **_base_payload("/clouds/app-status-board.json", "clouds_app_status_board"),
        "status": "ready",
        "app_count": len(app_status_cards),
        "live_source_count": sum(1 for item in app_status_cards if item["health"] == "live_summary_ready"),
        "vault_summary_source_count": sum(1 for item in app_status_cards if item["health"] == "vault_summary_ready"),
        "placeholder_count": sum(1 for item in app_status_cards if item["is_placeholder"]),
        "locked_placeholder_count": sum(1 for item in app_status_cards if item["tone"] == "locked"),
        "app_status_cards": app_status_cards,
        "boundary": {
            "clouds_is_status_board": True,
            "clouds_is_not_authority": True,
            "owning_app_keeps_authority": True,
            "placeholders_are_not_connected": True,
            "summary_only_redacted": True,
        },
    }
    return payload


def get_clouds_lane_status_board_payload() -> Dict[str, Any]:
    focus_lanes = get_clouds_focus_lanes_payload()
    vault_summary = get_clouds_vault_summary_payload()
    command = get_unified_vault_command_center_payload()

    vault_lane_lookup = {
        lane["lane_id"]: lane
        for lane in command["lane_cards"]
    }

    lane_status_cards = []
    for lane in focus_lanes["lanes"]:
        lane_id = lane["lane_id"]
        vault_lane = vault_lane_lookup.get(lane_id)
        source_type = "vault_live_lane" if vault_lane else "clouds_focus_lane"
        setup_score = vault_lane["setup_score"] if vault_lane else None
        source_route = vault_lane["source_route"] if vault_lane else "not_connected_or_focus_only"

        lane_status_cards.append(
            {
                "lane_id": lane_id,
                "label": lane_id.replace("_", " ").title(),
                "source_type": source_type,
                "source_route": source_route,
                "setup_score": setup_score,
                "focus_count": lane["focus_count"],
                "critical_count": lane["critical_count"],
                "high_count": lane["high_count"],
                "blocked_count": lane["blocked_count"],
                "ready_count": lane["ready_count"],
                "source_apps": lane["source_apps"],
                "open_targets": lane["open_targets"],
                "clouds_role": lane["clouds_role"],
                "status": "ready" if lane["blocked_count"] == 0 else "watch",
                "clouds_can_complete": False,
                "owning_app_keeps_authority": True,
            }
        )

    # Add Vault lanes that may not currently have focus items.
    existing_lane_ids = {lane["lane_id"] for lane in lane_status_cards}
    for vault_lane_id, vault_lane in vault_lane_lookup.items():
        if vault_lane_id not in existing_lane_ids:
            lane_status_cards.append(
                {
                    "lane_id": vault_lane_id,
                    "label": vault_lane["label"],
                    "source_type": "vault_live_lane",
                    "source_route": vault_lane["source_route"],
                    "setup_score": vault_lane["setup_score"],
                    "focus_count": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "blocked_count": 0,
                    "ready_count": 0,
                    "source_apps": [vault_lane["source_app"]],
                    "open_targets": [vault_lane["source_route"]],
                    "clouds_role": "show_lane_status_and_open_vault",
                    "status": vault_lane["status"],
                    "clouds_can_complete": False,
                    "owning_app_keeps_authority": True,
                }
            )

    lane_status_cards.sort(key=lambda item: (item["status"] != "watch", item["lane_id"]))

    payload = {
        **_base_payload("/clouds/lane-status-board.json", "clouds_lane_status_board"),
        "status": "ready",
        "lane_count": len(lane_status_cards),
        "watch_lane_count": sum(1 for item in lane_status_cards if item["status"] == "watch"),
        "vault_live_lane_count": sum(1 for item in lane_status_cards if item["source_type"] == "vault_live_lane"),
        "focus_only_lane_count": sum(1 for item in lane_status_cards if item["source_type"] == "clouds_focus_lane"),
        "vault_final_score": vault_summary["vault"]["final_score"],
        "lane_status_cards": lane_status_cards,
        "boundary": {
            "lanes_are_visibility_groupings": True,
            "clouds_routes_to_owning_app": True,
            "clouds_does_not_execute_lane_actions": True,
            "summary_only_redacted": True,
        },
    }
    return payload


def get_clouds_placeholder_health_payload() -> Dict[str, Any]:
    placeholders = get_clouds_placeholder_sources_payload()
    registry = get_clouds_app_registry_payload()

    app_lookup = {app["registered_app_id"]: app for app in registry["apps"]}
    health_cards = []

    for app_id in placeholders["placeholder_apps"]:
        app = app_lookup[app_id]
        health_cards.append(
            {
                "app_id": app_id,
                "label": app["label"],
                "health": "placeholder_not_connected",
                "source_status": app["source_status"],
                "primary_route": app["primary_route"],
                "source_route": app["source_route"],
                "authority_owner": app["authority_owner"],
                "reason": placeholders["why_placeholder"],
                "owner_next_action": "Build a safe summary source contract in the owning app before connecting this card.",
                "clouds_can_route": True,
                "clouds_can_claim_live_source": False,
                "clouds_can_grant_authority": False,
                "blocked_by": ["source_contract_not_connected"],
            }
        )

    payload = {
        **_base_payload("/clouds/placeholder-health.json", "clouds_placeholder_health"),
        "status": "ready",
        "placeholder_health_count": len(health_cards),
        "health_cards": health_cards,
        "placeholder_apps": placeholders["placeholder_apps"],
        "boundary": {
            "placeholder_is_visible": True,
            "placeholder_is_not_connected": True,
            "clouds_cannot_claim_live_source": True,
            "clouds_cannot_grant_authority": True,
        },
    }
    return payload


def get_clouds_vault_live_status_payload() -> Dict[str, Any]:
    vault_summary = get_clouds_vault_summary_payload()
    vault_final = get_vault_final_readiness_payload()
    tracker = get_vault_search_tracker_payload()
    receipt = get_receipt_control_center_payload()
    export = get_export_preview_center_payload()

    status_cards = [
        {
            "card_id": "vault_live_readiness",
            "label": "Vault Readiness",
            "value": vault_summary["vault"]["final_score"],
            "unit": "%",
            "status": vault_summary["vault"]["status"],
            "source_route": "/vault/final-readiness.json",
            "open_app_target": "/vault/final-readiness",
        },
        {
            "card_id": "vault_live_requirements",
            "label": "Vault Requirements",
            "value": vault_summary["vault"]["requirement_count"],
            "unit": "requirements",
            "status": "watch" if vault_summary["vault"]["blocked_requirement_count"] else "ready",
            "source_route": "/vault/search-tracker.json",
            "open_app_target": "/vault/search-tracker",
        },
        {
            "card_id": "vault_live_receipts",
            "label": "Vault Receipts",
            "value": vault_summary["vault"]["receipt_count"],
            "unit": "receipts",
            "status": receipt["status"],
            "source_route": "/vault/receipt-control-center.json",
            "open_app_target": "/vault/receipt-control",
        },
        {
            "card_id": "vault_live_exports",
            "label": "Vault Locked Exports",
            "value": vault_summary["vault"]["locked_export_count"],
            "unit": "locked",
            "status": "locked",
            "source_route": "/vault/export-preview-center.json",
            "open_app_target": "/vault/export-preview",
        },
        {
            "card_id": "vault_live_freshness",
            "label": "Vault Freshness Lanes",
            "value": tracker["data_freshness_wall"]["lane_count"],
            "unit": "lanes",
            "status": tracker["status"],
            "source_route": "/vault/search-tracker.json",
            "open_app_target": "/vault/search-tracker",
        },
        {
            "card_id": "vault_live_previews",
            "label": "Vault Redacted Previews",
            "value": export["redacted_packet_preview"]["preview_count"],
            "unit": "previews",
            "status": "redacted",
            "source_route": "/vault/export-preview-center.json",
            "open_app_target": "/vault/export-preview",
        },
    ]

    payload = {
        **_base_payload("/clouds/vault-live-status.json", "clouds_vault_live_status"),
        "status": "ready",
        "source_app": "archive_vault",
        "live_status_card_count": len(status_cards),
        "status_cards": status_cards,
        "vault_ready": vault_final["safe_to_start_clouds"],
        "vault_final_score": vault_summary["vault"]["final_score"],
        "clouds_view": vault_summary["vault"]["clouds_view"],
        "intentional_locks": vault_final["intentional_locks"],
        "boundary": {
            "vault_is_live_summary_source": True,
            "clouds_reads_summary_only": True,
            "clouds_does_not_unlock_vault": True,
            "clouds_opens_vault_for_action": True,
        },
    }
    return payload


def get_clouds_app_lane_status_dashboard_payload() -> Dict[str, Any]:
    app_board = get_clouds_app_status_board_payload()
    lane_board = get_clouds_lane_status_board_payload()
    placeholder_health = get_clouds_placeholder_health_payload()
    vault_live = get_clouds_vault_live_status_payload()
    focus_dashboard = get_clouds_owner_focus_dashboard_payload()
    authority = get_clouds_authority_map_payload()
    gp001 = get_clouds_gp001_status_payload()
    gp002 = get_clouds_gp002_status_payload()
    gp003 = get_clouds_gp003_status_payload()

    payload = {
        **_base_payload("/clouds/app-lane-status-dashboard.json", "clouds_app_lane_status_dashboard"),
        "status": "ready",
        "dashboard_label": "Clouds App + Lane Status Board",
        "app_board": {
            "app_count": app_board["app_count"],
            "live_source_count": app_board["live_source_count"],
            "vault_summary_source_count": app_board["vault_summary_source_count"],
            "placeholder_count": app_board["placeholder_count"],
            "locked_placeholder_count": app_board["locked_placeholder_count"],
        },
        "lane_board": {
            "lane_count": lane_board["lane_count"],
            "watch_lane_count": lane_board["watch_lane_count"],
            "vault_live_lane_count": lane_board["vault_live_lane_count"],
            "focus_only_lane_count": lane_board["focus_only_lane_count"],
        },
        "placeholder_health": {
            "placeholder_health_count": placeholder_health["placeholder_health_count"],
            "placeholder_apps": placeholder_health["placeholder_apps"],
        },
        "vault_live_status": {
            "live_status_card_count": vault_live["live_status_card_count"],
            "vault_ready": vault_live["vault_ready"],
            "vault_final_score": vault_live["vault_final_score"],
            "clouds_view": vault_live["clouds_view"],
        },
        "focus_summary": focus_dashboard["focus_summary"],
        "authority_row_count": authority["authority_row_count"],
        "prior_pack_status": {
            "gp001": gp001["status"],
            "gp002": gp002["status"],
            "gp003": gp003["status"],
        },
        "app_status_cards": app_board["app_status_cards"],
        "lane_status_cards": lane_board["lane_status_cards"],
        "placeholder_health_cards": placeholder_health["health_cards"],
        "vault_live_cards": vault_live["status_cards"],
        "open_app_targets": sorted(
            set(
                [card["primary_route"] for card in app_board["app_status_cards"] if card["primary_route"] != "not_connected"]
                + [card["open_app_target"] for card in vault_live["status_cards"]]
            )
        ),
        "boundary": {
            "clouds_is_status_layer": True,
            "clouds_is_not_system_of_record": True,
            "summary_only_redacted": True,
            "owning_apps_keep_authority": True,
            "placeholder_sources_are_not_connected": True,
        },
        "next_pack_recommendation": "Clouds GP005 should build Owner Snapshot Header + Today View using the app/lane status board and owner focus queue.",
    }
    return payload


def get_clouds_gp004_status_payload() -> Dict[str, Any]:
    dashboard = get_clouds_app_lane_status_dashboard_payload()

    payload = {
        **_base_payload("/clouds/gp004-status.json", "clouds_gp004_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 004",
        "built": [
            "app_status_board",
            "lane_status_board",
            "vault_live_status_cards",
            "tower_ob_teller_placeholder_health_cards",
            "blocked_source_status_wall",
            "open_app_status_handoffs",
            "app_lane_status_dashboard_ui",
            "gp004_status_endpoint",
        ],
        "app_count": dashboard["app_board"]["app_count"],
        "lane_count": dashboard["lane_board"]["lane_count"],
        "placeholder_count": dashboard["placeholder_health"]["placeholder_health_count"],
        "vault_live_status_card_count": dashboard["vault_live_status"]["live_status_card_count"],
        "vault_final_score": dashboard["vault_live_status"]["vault_final_score"],
        "watch_lane_count": dashboard["lane_board"]["watch_lane_count"],
        "prior_gp001_status": dashboard["prior_pack_status"]["gp001"],
        "prior_gp002_status": dashboard["prior_pack_status"]["gp002"],
        "prior_gp003_status": dashboard["prior_pack_status"]["gp003"],
        "clouds_is_status_layer": True,
        "clouds_is_not_system_of_record": True,
        "summary_only_redacted": True,
        "safe_to_continue_to_clouds_gp005": True,
    }
    return payload
