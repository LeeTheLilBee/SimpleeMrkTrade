from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from tower.app_registry import (
    registered_apps,
    registered_routes,
    owner_only_routes,
    step_up_routes,
    temporary_placeholder_routes,
)


@dataclass(frozen=True)
class TowerSecurityMapSummary:
    status: str
    generated_at_utc: str
    app_count: int
    route_count: int
    owner_only_count: int
    step_up_count: int
    placeholder_count: int
    unknown_ob_default: str
    live_auto: str
    broker_execution: bool
    capital_action: bool
    tower_meaning: str
    owner_next_action: str


def build_tower_security_map() -> Dict[str, Any]:
    apps = registered_apps()
    routes = registered_routes()

    owner_routes = owner_only_routes()
    step_routes = step_up_routes()
    placeholders = temporary_placeholder_routes()

    summary = TowerSecurityMapSummary(
        status="tower_security_map_ready",
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        app_count=len(apps),
        route_count=len(routes),
        owner_only_count=len(owner_routes),
        step_up_count=len(step_routes),
        placeholder_count=len(placeholders),
        unknown_ob_default="403_default_deny",
        live_auto="LOCKED",
        broker_execution=False,
        capital_action=False,
        tower_meaning=(
            "Tower is the front door, key ring, and lock map. "
            "It can show which app routes are registered, which routes are owner-only, "
            "which routes require step-up, and which dangerous actions remain locked."
        ),
        owner_next_action=(
            "Continue Tower walkthrough through the Security Map, then use it as the "
            "source of truth before adding new OB, Teller, Vault, Clouds, or Grounds routes."
        ),
    )

    risk_counts: Dict[str, int] = {}

    for route in routes:
        risk_level = str(route["risk_level"])
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

    return {
        "summary": asdict(summary),
        "apps": apps,
        "routes": routes,
        "route_groups": {
            "owner_only": owner_routes,
            "step_up_required": step_routes,
            "temporary_placeholders": placeholders,
        },
        "risk_counts": risk_counts,
        "default_deny": {
            "ob_unknown_route_status": 403,
            "meaning": (
                "Unknown /ob/* routes remain denied by default. "
                "A valid session does not automatically make an unmapped route safe."
            ),
        },
        "danger_locks": {
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def security_map_status_cards() -> List[Dict[str, Any]]:
    security_map = build_tower_security_map()
    summary = security_map["summary"]

    return [
        {
            "card_id": "tower-card-app-registry",
            "title": "Registered apps",
            "value": summary["app_count"],
            "status": "mapped",
            "meaning": "Tower has a registry for current and future Simplee rooms.",
        },
        {
            "card_id": "tower-card-protected-routes",
            "title": "Protected routes",
            "value": summary["route_count"],
            "status": "protected",
            "meaning": "Tower can explain the approved route surface.",
        },
        {
            "card_id": "tower-card-owner-only",
            "title": "Owner-only routes",
            "value": summary["owner_only_count"],
            "status": "owner_only",
            "meaning": "These routes require Tower owner session.",
        },
        {
            "card_id": "tower-card-step-up",
            "title": "Step-up routes",
            "value": summary["step_up_count"],
            "status": "step_up",
            "meaning": "These routes require Tower owner session plus step-up.",
        },
        {
            "card_id": "tower-card-default-deny",
            "title": "Unknown OB routes",
            "value": "403",
            "status": "default_deny",
            "meaning": "Unknown OB paths are denied by default.",
        },
        {
            "card_id": "tower-card-danger-locks",
            "title": "Danger locks",
            "value": "LOCKED",
            "status": "locked",
            "meaning": "Live Auto, broker execution, and capital action remain locked.",
        },
    ]
