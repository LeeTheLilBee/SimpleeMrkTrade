"""The Clouds Giant Pack 003 Owner Focus Queue.

This pack makes The Clouds useful as an owner command layer:
- Owner Focus Queue v1
- Focus lane wall
- Blocked/watch wall
- Placeholder source action cards for Tower, OB, Teller
- Vault-ready action rollup
- Open-app handoff targets

Boundary:
Clouds displays what deserves owner attention and opens the owning app.
Clouds does not complete the work, grant permission, upload files, approve
exports, execute trades, run payroll, or replace any owning app.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .clouds_app_registry_service import (
    get_clouds_app_registry_dashboard_payload,
    get_clouds_app_registry_payload,
    get_clouds_authority_map_payload,
    get_clouds_placeholder_sources_payload,
)
from .clouds_contracts import CLOUDS_VERSION, utc_now_iso
from .clouds_service import (
    get_clouds_command_dashboard_payload,
    get_clouds_status_payload,
    get_clouds_vault_summary_payload,
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


def _focus_item(
    focus_id: str,
    label: str,
    source_app: str,
    business_lane: str,
    priority: str,
    status: str,
    owner_action: str,
    open_app_target: str,
    blocked_by: List[str] | None = None,
    source_route: str = "not_connected",
    action_type: str = "open_app_handoff",
) -> Dict[str, Any]:
    blocked_by = blocked_by or []
    return {
        "focus_id": focus_id,
        "label": label,
        "source_app": source_app,
        "business_lane": business_lane,
        "priority": priority,
        "status": status,
        "owner_action": owner_action,
        "open_app_target": open_app_target,
        "source_route": source_route,
        "blocked_by": blocked_by,
        "action_type": action_type,
        "clouds_can_complete": False,
        "clouds_can_route": True,
        "owning_app_keeps_authority": True,
        "summary_only": True,
        "redacted": True,
    }


def _priority_rank(priority: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 9)


def get_clouds_owner_focus_queue_payload() -> Dict[str, Any]:
    vault_final = get_vault_final_readiness_payload()
    registry = get_clouds_app_registry_payload()
    placeholders = get_clouds_placeholder_sources_payload()
    command = get_unified_vault_command_center_payload()
    tracker = get_vault_search_tracker_payload()
    receipt = get_receipt_control_center_payload()
    export = get_export_preview_center_payload()

    focus_items: List[Dict[str, Any]] = []

    # Vault final queue actions become Clouds focus cards.
    for action in vault_final["owner_final_queue"]["actions"]:
        focus_items.append(
            _focus_item(
                focus_id=f"focus_{action['action_id']}",
                label=action["label"],
                source_app="archive_vault",
                business_lane=action["business_lane"],
                priority=action["priority"],
                status=action["status"],
                owner_action=action["next_step"],
                open_app_target="/vault/final-readiness",
                blocked_by=action["blocked_by"],
                source_route="/vault/final-readiness.json",
                action_type="vault_owner_final_action",
            )
        )

    # Vault operational rollups.
    focus_items.extend([
        _focus_item(
            focus_id="focus_vault_command_center_ready",
            label="Review Vault six-lane command center",
            source_app="archive_vault",
            business_lane="vault",
            priority="high",
            status="ready",
            owner_action=f"Vault command center has {command['lane_count']} lanes, {command['route_count']} routes, and {command['owner_action_count']} owner actions.",
            open_app_target="/vault/command-center",
            source_route="/vault/command-center.json",
            action_type="vault_command_review",
        ),
        _focus_item(
            focus_id="focus_vault_requirements_blocked",
            label="Watch blocked Vault requirements",
            source_app="archive_vault",
            business_lane="vault",
            priority="high",
            status="watch",
            owner_action=f"Vault has {tracker['requirement_tracker']['blocked_count']} blocked requirements because evidence/upload/target prerequisites are not complete yet.",
            open_app_target="/vault/search-tracker",
            blocked_by=["direct_upload_locked", "target_not_selected", "evidence_not_attached"],
            source_route="/vault/search-tracker.json",
            action_type="vault_requirement_watch",
        ),
        _focus_item(
            focus_id="focus_vault_receipts_controls_ready",
            label="Keep receipt controls active",
            source_app="archive_vault",
            business_lane="vault",
            priority="medium",
            status="ready",
            owner_action=f"Vault has {receipt['receipt_chain_console']['receipt_count']} receipts and {receipt['freeze_revoke_undo_wall']['rule_count']} control rules preserving proof and locks.",
            open_app_target="/vault/receipt-control",
            source_route="/vault/receipt-control-center.json",
            action_type="vault_receipt_control_review",
        ),
        _focus_item(
            focus_id="focus_vault_exports_locked",
            label="Keep Vault exports locked",
            source_app="archive_vault",
            business_lane="vault",
            priority="critical",
            status="locked",
            owner_action=f"Vault has {export['export_lock_console']['locked_export_count']} locked exports and redacted previews only.",
            open_app_target="/vault/export-preview",
            blocked_by=["export_locked", "unredacted_export_blocked", "external_access_not_approved"],
            source_route="/vault/export-preview-center.json",
            action_type="vault_export_lock_review",
        ),
    ])

    # Placeholder source contracts that need future packs.
    placeholder_map = {app["registered_app_id"]: app for app in placeholders["placeholders"]}
    for app_id, priority, label, open_target in [
        ("tower", "critical", "Create Tower live summary source contract later", "/clouds/app-registry#clouds_app_tower"),
        ("observatory", "high", "Create OB live summary source contract later", "/clouds/app-registry#clouds_app_observatory"),
        ("teller", "high", "Create Teller live summary source contract later", "/clouds/app-registry#clouds_app_teller"),
    ]:
        app = placeholder_map.get(app_id)
        if app:
            focus_items.append(
                _focus_item(
                    focus_id=f"focus_placeholder_{app_id}_source_contract",
                    label=label,
                    source_app=app_id,
                    business_lane=app_id,
                    priority=priority,
                    status="placeholder_not_connected",
                    owner_action=f"{app['label']} has a visible Clouds slot, but no live source contract yet. Keep it placeholder until the owning app exposes a safe summary source.",
                    open_app_target=open_target,
                    blocked_by=["source_contract_not_connected"],
                    source_route="not_connected",
                    action_type="placeholder_source_contract_needed",
                )
            )

    # Growth focus cards from app registry.
    registry_apps = {app["registered_app_id"]: app for app in registry["apps"]}
    for app_id, label, lane, target, priority in [
        ("simplee_on_the_go", "Use ATM packet when route targets appear", "atm", "/vault/acquisition-builders", "high"),
        ("simplee_property", "Use apartment packet while property targets are searched", "property", "/vault/acquisition-builders", "high"),
        ("soulaana", "Keep Soulaana reserved art/IP boundary active", "soulaana", "/vault/soulaana-beta", "medium"),
        ("private_beta", "Keep private beta access Tower-controlled", "beta", "/vault/soulaana-beta", "medium"),
    ]:
        app = registry_apps.get(app_id)
        if app:
            focus_items.append(
                _focus_item(
                    focus_id=f"focus_{app_id}_registry_action",
                    label=label,
                    source_app=app_id,
                    business_lane=lane,
                    priority=priority,
                    status="ready" if app["tone"] == "ready" else "locked",
                    owner_action=app["clouds_role"],
                    open_app_target=target,
                    blocked_by=[] if app["tone"] == "ready" else ["source_contract_not_connected"],
                    source_route=app["source_route"],
                    action_type="registry_growth_focus",
                )
            )

    focus_items.sort(key=lambda item: (_priority_rank(item["priority"]), item["focus_id"]))

    payload = {
        **_base_payload("/clouds/owner-focus-queue.json", "clouds_owner_focus_queue"),
        "status": "ready",
        "queue_label": "Owner Focus Queue v1",
        "focus_count": len(focus_items),
        "critical_count": sum(1 for item in focus_items if item["priority"] == "critical"),
        "high_count": sum(1 for item in focus_items if item["priority"] == "high"),
        "medium_count": sum(1 for item in focus_items if item["priority"] == "medium"),
        "ready_count": sum(1 for item in focus_items if not item["blocked_by"]),
        "blocked_count": sum(1 for item in focus_items if item["blocked_by"]),
        "focus_items": focus_items,
        "boundary": {
            "clouds_can_complete_actions": False,
            "clouds_can_route_to_owning_app": True,
            "owning_app_keeps_authority": True,
            "summary_only_redacted": True,
            "placeholder_sources_are_not_connected": True,
        },
    }
    return payload


def get_clouds_focus_lanes_payload() -> Dict[str, Any]:
    focus = get_clouds_owner_focus_queue_payload()

    lane_map: Dict[str, Dict[str, Any]] = {}
    for item in focus["focus_items"]:
        lane = item["business_lane"]
        lane_map.setdefault(
            lane,
            {
                "lane_id": lane,
                "focus_count": 0,
                "critical_count": 0,
                "high_count": 0,
                "blocked_count": 0,
                "ready_count": 0,
                "source_apps": set(),
                "open_targets": set(),
            },
        )
        lane_map[lane]["focus_count"] += 1
        lane_map[lane]["critical_count"] += 1 if item["priority"] == "critical" else 0
        lane_map[lane]["high_count"] += 1 if item["priority"] == "high" else 0
        lane_map[lane]["blocked_count"] += 1 if item["blocked_by"] else 0
        lane_map[lane]["ready_count"] += 1 if not item["blocked_by"] else 0
        lane_map[lane]["source_apps"].add(item["source_app"])
        lane_map[lane]["open_targets"].add(item["open_app_target"])

    lanes = []
    for lane in lane_map.values():
        lanes.append(
            {
                **lane,
                "source_apps": sorted(lane["source_apps"]),
                "open_targets": sorted(lane["open_targets"]),
                "clouds_role": "show_lane_focus_and_route_owner",
            }
        )

    lanes.sort(key=lambda item: item["lane_id"])

    payload = {
        **_base_payload("/clouds/focus-lanes.json", "clouds_focus_lanes"),
        "status": "ready",
        "lane_count": len(lanes),
        "lanes": lanes,
        "boundary": {
            "lanes_are_dashboard_groupings": True,
            "owning_apps_keep_authority": True,
            "clouds_routes_only": True,
        },
    }
    return payload


def get_clouds_blocked_watch_payload() -> Dict[str, Any]:
    focus = get_clouds_owner_focus_queue_payload()
    blocked_items = [item for item in focus["focus_items"] if item["blocked_by"]]

    blocked_reasons = sorted(
        {
            reason
            for item in blocked_items
            for reason in item["blocked_by"]
        }
    )

    watch_items = [
        {
            "watch_id": f"watch_{reason}",
            "blocked_reason": reason,
            "item_count": sum(1 for item in blocked_items if reason in item["blocked_by"]),
            "default_owner_action": "Keep blocked unless the owning app and Tower clearance say otherwise.",
            "clouds_can_unlock": False,
            "clouds_can_route": True,
        }
        for reason in blocked_reasons
    ]

    payload = {
        **_base_payload("/clouds/blocked-watch.json", "clouds_blocked_watch"),
        "status": "ready",
        "blocked_item_count": len(blocked_items),
        "blocked_reason_count": len(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "watch_items": watch_items,
        "boundary": {
            "default_action": "keep_blocked",
            "clouds_can_unlock": False,
            "tower_or_owning_app_required": True,
            "blocked_watch_is_visibility_only": True,
        },
    }
    return payload


def get_clouds_owner_focus_dashboard_payload() -> Dict[str, Any]:
    focus = get_clouds_owner_focus_queue_payload()
    lanes = get_clouds_focus_lanes_payload()
    blocked = get_clouds_blocked_watch_payload()
    registry_dashboard = get_clouds_app_registry_dashboard_payload()
    gp001_dashboard = get_clouds_command_dashboard_payload()
    clouds_status = get_clouds_status_payload()

    payload = {
        **_base_payload("/clouds/owner-focus-dashboard.json", "clouds_owner_focus_dashboard"),
        "status": "ready",
        "dashboard_label": "Clouds Owner Focus Queue",
        "focus_summary": {
            "focus_count": focus["focus_count"],
            "critical_count": focus["critical_count"],
            "high_count": focus["high_count"],
            "medium_count": focus["medium_count"],
            "ready_count": focus["ready_count"],
            "blocked_count": focus["blocked_count"],
        },
        "focus_items": focus["focus_items"],
        "lane_summary": {
            "lane_count": lanes["lane_count"],
            "lanes": lanes["lanes"],
        },
        "blocked_watch": {
            "blocked_item_count": blocked["blocked_item_count"],
            "blocked_reason_count": blocked["blocked_reason_count"],
            "watch_items": blocked["watch_items"],
        },
        "registry_summary": {
            "registered_app_count": registry_dashboard["registered_app_count"],
            "placeholder_count": registry_dashboard["placeholder_count"],
            "authority_row_count": registry_dashboard["authority_row_count"],
        },
        "gp001_summary": {
            "dashboard_status": gp001_dashboard["status"],
            "card_count": gp001_dashboard["card_count"],
            "vault_final_score": clouds_status["vault_final_score"],
        },
        "open_app_targets": sorted({item["open_app_target"] for item in focus["focus_items"]}),
        "next_pack_recommendation": "Clouds GP004 should build App/Lane Status Board with Vault live source and placeholder app health cards.",
    }
    return payload


def get_clouds_gp003_status_payload() -> Dict[str, Any]:
    dashboard = get_clouds_owner_focus_dashboard_payload()

    payload = {
        **_base_payload("/clouds/gp003-status.json", "clouds_gp003_status"),
        "status": "ready",
        "pack": "The Clouds Giant Pack 003",
        "built": [
            "owner_focus_queue_v1",
            "focus_lane_wall",
            "blocked_watch_wall",
            "tower_placeholder_focus_card",
            "ob_placeholder_focus_card",
            "teller_placeholder_focus_card",
            "vault_ready_action_rollup",
            "owner_focus_dashboard_ui",
            "gp003_status_endpoint",
        ],
        "focus_count": dashboard["focus_summary"]["focus_count"],
        "critical_count": dashboard["focus_summary"]["critical_count"],
        "high_count": dashboard["focus_summary"]["high_count"],
        "ready_count": dashboard["focus_summary"]["ready_count"],
        "blocked_count": dashboard["focus_summary"]["blocked_count"],
        "lane_count": dashboard["lane_summary"]["lane_count"],
        "blocked_reason_count": dashboard["blocked_watch"]["blocked_reason_count"],
        "clouds_can_complete_actions": False,
        "clouds_can_route_to_owning_app": True,
        "summary_only_redacted": True,
        "safe_to_continue_to_clouds_gp004": True,
    }
    return payload
