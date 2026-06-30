"""The Clouds Giant Pack 005 Owner Snapshot Header + Today View.

This pack creates the daily command surface:
- Owner Snapshot Header
- Today View
- Critical / High / Watch / Locked rollups
- Open-app quick targets
- What to do next, what to leave locked, what to watch

Boundary:
Clouds can summarize and route. It cannot grant authority, complete the action,
approve exports, unlock Vault, execute OB activity, or run Teller/payroll work.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_app_lane_status_service import (
    get_clouds_app_lane_status_dashboard_payload,
    get_clouds_app_status_board_payload,
    get_clouds_gp004_status_payload,
    get_clouds_lane_status_board_payload,
    get_clouds_placeholder_health_payload,
    get_clouds_vault_live_status_payload,
)
from .clouds_app_registry_service import (
    get_clouds_app_registry_payload,
    get_clouds_gp002_status_payload,
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


def _priority_rank(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 9)


def _snapshot_card(
    card_id: str,
    label: str,
    value: object,
    unit: str,
    status: str,
    summary: str,
    open_app_target: str,
) -> Dict[str, object]:
    return {
        "card_id": card_id,
        "label": label,
        "value": value,
        "unit": unit,
        "status": status,
        "summary": summary,
        "open_app_target": open_app_target,
        "clouds_can_complete": False,
        "clouds_can_route": True,
    }


def get_clouds_owner_snapshot_header_payload() -> Dict[str, object]:
    gp001 = get_clouds_gp001_status_payload()
    gp002 = get_clouds_gp002_status_payload()
    gp003 = get_clouds_gp003_status_payload()
    gp004 = get_clouds_gp004_status_payload()
    vault_summary = get_clouds_vault_summary_payload()
    focus = get_clouds_owner_focus_queue_payload()
    app_board = get_clouds_app_status_board_payload()
    lane_board = get_clouds_lane_status_board_payload()
    placeholder = get_clouds_placeholder_health_payload()
    vault_live = get_clouds_vault_live_status_payload()

    snapshot_cards = [
        _snapshot_card(
            "snapshot_vault_score",
            "Vault score",
            vault_summary["vault"]["final_score"],
            "%",
            "ready",
            "Vault GP001-GP010 is the first live Clouds source.",
            "/vault/final-readiness",
        ),
        _snapshot_card(
            "snapshot_focus_count",
            "Owner focus",
            focus["focus_count"],
            "items",
            "active",
            "Priority-sorted owner focus items across Vault and placeholder app slots.",
            "/clouds/owner-focus",
        ),
        _snapshot_card(
            "snapshot_critical_count",
            "Critical",
            focus["critical_count"],
            "items",
            "watch",
            "Critical items are visible, but Clouds routes only.",
            "/clouds/owner-focus",
        ),
        _snapshot_card(
            "snapshot_apps",
            "Apps",
            app_board["app_count"],
            "registered",
            "ready",
            "Clouds App Registry has live, Vault-backed, and placeholder app cards.",
            "/clouds/app-registry",
        ),
        _snapshot_card(
            "snapshot_lanes",
            "Lanes",
            lane_board["lane_count"],
            "lanes",
            "ready",
            "Business lanes are grouped for owner visibility.",
            "/clouds/app-lane-status",
        ),
        _snapshot_card(
            "snapshot_placeholders",
            "Placeholders",
            placeholder["placeholder_health_count"],
            "not connected",
            "locked",
            "Tower, OB, and Teller are visible but not live-connected yet.",
            "/clouds/app-lane-status",
        ),
        _snapshot_card(
            "snapshot_vault_live_cards",
            "Vault live cards",
            vault_live["live_status_card_count"],
            "cards",
            "ready",
            "Vault readiness, requirements, receipts, exports, freshness, and previews are summarized.",
            "/clouds/app-lane-status",
        ),
        _snapshot_card(
            "snapshot_gp_status",
            "Clouds packs",
            "GP001-GP004",
            "ready",
            "ready",
            "Previous Clouds packs are available as source layers for Today View.",
            "/clouds/status.json",
        ),
    ]

    payload = {
        **_base_payload("/clouds/owner-snapshot.json", "clouds_owner_snapshot_header"),
        "status": "ready",
        "snapshot_label": "Owner Snapshot Header",
        "snapshot_status": "ready",
        "clouds_pack_status": {
            "gp001": gp001["status"],
            "gp002": gp002["status"],
            "gp003": gp003["status"],
            "gp004": gp004["status"],
        },
        "vault_final_score": vault_summary["vault"]["final_score"],
        "vault_safe_to_start_clouds": vault_summary["vault"]["safe_to_start_clouds"],
        "clouds_view": vault_summary["vault"]["clouds_view"],
        "snapshot_card_count": len(snapshot_cards),
        "snapshot_cards": snapshot_cards,
        "boundary": {
            "snapshot_is_visibility_only": True,
            "clouds_can_complete_actions": False,
            "clouds_can_route_to_owning_app": True,
            "summary_only_redacted": True,
            "owning_apps_keep_authority": True,
        },
    }
    return payload


def get_clouds_today_focus_payload() -> Dict[str, object]:
    focus = get_clouds_owner_focus_queue_payload()
    blocked = get_clouds_blocked_watch_payload()

    focus_items = focus["focus_items"]
    critical_items = [item for item in focus_items if item["priority"] == "critical"]
    high_items = [item for item in focus_items if item["priority"] == "high"]
    ready_items = [item for item in focus_items if not item["blocked_by"]]
    blocked_items = [item for item in focus_items if item["blocked_by"]]

    today_sections = [
        {
            "section_id": "today_critical",
            "label": "Critical",
            "status": "watch",
            "item_count": len(critical_items),
            "items": critical_items[:6],
            "owner_instruction": "Review first. Keep dangerous doors locked unless the owning app and Tower clear them.",
        },
        {
            "section_id": "today_high",
            "label": "High",
            "status": "active",
            "item_count": len(high_items),
            "items": high_items[:8],
            "owner_instruction": "Move these forward by opening the owning app route.",
        },
        {
            "section_id": "today_ready",
            "label": "Ready Now",
            "status": "ready",
            "item_count": len(ready_items),
            "items": ready_items[:8],
            "owner_instruction": "These are ready to review without unlocking blocked systems.",
        },
        {
            "section_id": "today_blocked",
            "label": "Blocked / Keep Locked",
            "status": "locked",
            "item_count": len(blocked_items),
            "items": blocked_items[:8],
            "owner_instruction": "Blocked means stay blocked by default. Clouds cannot unlock these.",
        },
    ]

    today_top_items = sorted(
        focus_items,
        key=lambda item: (_priority_rank(item["priority"]), bool(item["blocked_by"]), item["focus_id"]),
    )[:10]

    payload = {
        **_base_payload("/clouds/today-focus.json", "clouds_today_focus"),
        "status": "ready",
        "today_label": "Today View",
        "focus_count": focus["focus_count"],
        "critical_count": len(critical_items),
        "high_count": len(high_items),
        "ready_count": len(ready_items),
        "blocked_count": len(blocked_items),
        "blocked_reason_count": blocked["blocked_reason_count"],
        "today_top_item_count": len(today_top_items),
        "today_top_items": today_top_items,
        "today_sections": today_sections,
        "boundary": {
            "today_view_is_command_visibility": True,
            "clouds_can_route": True,
            "clouds_can_complete": False,
            "blocked_items_default_to_locked": True,
            "summary_only_redacted": True,
        },
    }
    return payload


def get_clouds_today_watch_payload() -> Dict[str, object]:
    blocked = get_clouds_blocked_watch_payload()
    placeholder_health = get_clouds_placeholder_health_payload()
    app_board = get_clouds_app_status_board_payload()
    lane_board = get_clouds_lane_status_board_payload()
    vault_live = get_clouds_vault_live_status_payload()

    locked_apps = [
        app for app in app_board["app_status_cards"]
        if app["tone"] == "locked" or app["is_placeholder"]
    ]

    watch_lanes = [
        lane for lane in lane_board["lane_status_cards"]
        if lane["status"] == "watch"
    ]

    locked_vault_cards = [
        card for card in vault_live["status_cards"]
        if card["status"] in {"locked", "watch", "redacted"}
    ]

    watch_cards = [
        {
            "watch_id": "watch_blocked_reasons",
            "label": "Blocked reasons",
            "value": blocked["blocked_reason_count"],
            "unit": "reasons",
            "status": "locked",
            "summary": "Blocked reasons default to stay blocked.",
            "open_app_target": "/clouds/blocked-watch.json",
        },
        {
            "watch_id": "watch_placeholder_apps",
            "label": "Placeholder apps",
            "value": placeholder_health["placeholder_health_count"],
            "unit": "apps",
            "status": "placeholder",
            "summary": "Tower, OB, and Teller slots are visible but not live-connected.",
            "open_app_target": "/clouds/placeholder-health.json",
        },
        {
            "watch_id": "watch_locked_apps",
            "label": "Locked app cards",
            "value": len(locked_apps),
            "unit": "cards",
            "status": "locked",
            "summary": "Locked app cards need source contracts or owning app clearance.",
            "open_app_target": "/clouds/app-status-board.json",
        },
        {
            "watch_id": "watch_lanes",
            "label": "Watch lanes",
            "value": len(watch_lanes),
            "unit": "lanes",
            "status": "watch",
            "summary": "Watch lanes have blocked or critical focus.",
            "open_app_target": "/clouds/lane-status-board.json",
        },
        {
            "watch_id": "watch_vault_locked",
            "label": "Vault locked/redacted",
            "value": len(locked_vault_cards),
            "unit": "cards",
            "status": "locked",
            "summary": "Vault locked/redacted cards are intentional safety boundaries.",
            "open_app_target": "/clouds/vault-live-status.json",
        },
    ]

    payload = {
        **_base_payload("/clouds/today-watch.json", "clouds_today_watch"),
        "status": "ready",
        "watch_card_count": len(watch_cards),
        "watch_cards": watch_cards,
        "blocked_watch": {
            "blocked_item_count": blocked["blocked_item_count"],
            "blocked_reason_count": blocked["blocked_reason_count"],
            "watch_items": blocked["watch_items"],
        },
        "placeholder_health": {
            "placeholder_count": placeholder_health["placeholder_health_count"],
            "placeholder_apps": placeholder_health["placeholder_apps"],
        },
        "boundary": {
            "watch_items_do_not_unlock": True,
            "clouds_can_route_only": True,
            "owning_app_or_tower_required": True,
        },
    }
    return payload


def get_clouds_open_targets_payload() -> Dict[str, object]:
    today = get_clouds_today_focus_payload()
    snapshot = get_clouds_owner_snapshot_header_payload()
    app_lane = get_clouds_app_lane_status_dashboard_payload()
    focus_dashboard = get_clouds_owner_focus_dashboard_payload()

    targets = []

    for card in snapshot["snapshot_cards"]:
        targets.append(
            {
                "target_id": f"snapshot_{card['card_id']}",
                "label": card["label"],
                "route": card["open_app_target"],
                "source": "owner_snapshot",
                "purpose": "open source for snapshot card",
            }
        )

    for item in today["today_top_items"]:
        targets.append(
            {
                "target_id": f"focus_{item['focus_id']}",
                "label": item["label"],
                "route": item["open_app_target"],
                "source": "today_focus",
                "purpose": "open owning app for focus item",
            }
        )

    for route in app_lane["open_app_targets"] + focus_dashboard["open_app_targets"]:
        targets.append(
            {
                "target_id": f"route_{route.replace('/', '_').replace('#', '_')}",
                "label": route,
                "route": route,
                "source": "status_or_focus_dashboard",
                "purpose": "open app handoff",
            }
        )

    deduped: Dict[str, Dict[str, object]] = {}
    for target in targets:
        deduped[target["route"]] = target

    final_targets = sorted(deduped.values(), key=lambda item: item["route"])

    payload = {
        **_base_payload("/clouds/open-targets.json", "clouds_open_targets"),
        "status": "ready",
        "target_count": len(final_targets),
        "targets": final_targets,
        "boundary": {
            "targets_are_links_not_authority": True,
            "clouds_routes_to_owning_app": True,
            "owning_app_completes_action": True,
        },
    }
    return payload


def get_clouds_today_dashboard_payload() -> Dict[str, object]:
    snapshot = get_clouds_owner_snapshot_header_payload()
    today = get_clouds_today_focus_payload()
    watch = get_clouds_today_watch_payload()
    targets = get_clouds_open_targets_payload()
    gp001 = get_clouds_gp001_status_payload()
    gp002 = get_clouds_gp002_status_payload()
    gp003 = get_clouds_gp003_status_payload()
    gp004 = get_clouds_gp004_status_payload()

    payload = {
        **_base_payload("/clouds/today-dashboard.json", "clouds_today_dashboard"),
        "status": "ready",
        "dashboard_label": "Clouds Today View",
        "snapshot": {
            "snapshot_status": snapshot["snapshot_status"],
            "snapshot_card_count": snapshot["snapshot_card_count"],
            "vault_final_score": snapshot["vault_final_score"],
            "clouds_view": snapshot["clouds_view"],
            "cards": snapshot["snapshot_cards"],
        },
        "today_focus": {
            "focus_count": today["focus_count"],
            "critical_count": today["critical_count"],
            "high_count": today["high_count"],
            "ready_count": today["ready_count"],
            "blocked_count": today["blocked_count"],
            "today_top_item_count": today["today_top_item_count"],
            "today_top_items": today["today_top_items"],
            "today_sections": today["today_sections"],
        },
        "today_watch": {
            "watch_card_count": watch["watch_card_count"],
            "watch_cards": watch["watch_cards"],
            "blocked_reason_count": watch["blocked_watch"]["blocked_reason_count"],
            "placeholder_count": watch["placeholder_health"]["placeholder_count"],
        },
        "open_targets": {
            "target_count": targets["target_count"],
            "targets": targets["targets"],
        },
        "prior_pack_status": {
            "gp001": gp001["status"],
            "gp002": gp002["status"],
            "gp003": gp003["status"],
            "gp004": gp004["status"],
        },
        "boundary": {
            "today_view_is_owner_visibility": True,
            "clouds_can_complete_actions": False,
            "clouds_routes_only": True,
            "summary_only_redacted": True,
            "owning_apps_keep_authority": True,
        },
        "next_pack_recommendation": "Clouds GP006 should build Mission Lane Board v1 for Trust, ATM, Property, OB, Soulaana, Beta, and future apps.",
    }
    return payload


def get_clouds_gp005_status_payload() -> Dict[str, object]:
    dashboard = get_clouds_today_dashboard_payload()

    payload = {
        **_base_payload("/clouds/gp005-status.json", "clouds_gp005_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 005",
        "built": [
            "owner_snapshot_header",
            "today_view",
            "today_focus_sections",
            "today_watch_cards",
            "critical_high_ready_blocked_rollups",
            "open_app_target_map",
            "today_dashboard_ui",
            "gp005_status_endpoint",
        ],
        "snapshot_card_count": dashboard["snapshot"]["snapshot_card_count"],
        "focus_count": dashboard["today_focus"]["focus_count"],
        "critical_count": dashboard["today_focus"]["critical_count"],
        "high_count": dashboard["today_focus"]["high_count"],
        "ready_count": dashboard["today_focus"]["ready_count"],
        "blocked_count": dashboard["today_focus"]["blocked_count"],
        "watch_card_count": dashboard["today_watch"]["watch_card_count"],
        "open_target_count": dashboard["open_targets"]["target_count"],
        "vault_final_score": dashboard["snapshot"]["vault_final_score"],
        "prior_gp001_status": dashboard["prior_pack_status"]["gp001"],
        "prior_gp002_status": dashboard["prior_pack_status"]["gp002"],
        "prior_gp003_status": dashboard["prior_pack_status"]["gp003"],
        "prior_gp004_status": dashboard["prior_pack_status"]["gp004"],
        "clouds_can_complete_actions": False,
        "clouds_routes_only": True,
        "summary_only_redacted": True,
        "safe_to_continue_to_clouds_gp006": True,
    }
    return payload
