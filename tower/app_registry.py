from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class TowerRouteRegistration:
    route_id: str
    route: str
    label: str
    app_id: str
    room_id: str
    route_type: str
    owner_only: bool
    requires_owner_session: bool
    requires_step_up: bool
    default_denied_when_unknown: bool
    temporary_placeholder: bool
    risk_level: str
    lock_state: str
    explanation: str


@dataclass(frozen=True)
class TowerAppRegistration:
    app_id: str
    app_name: str
    app_label: str
    app_status: str
    tower_launch_route: str
    primary_room_route: str
    owner_only: bool
    requires_tower_handoff: bool
    dangerous_actions_locked: bool
    live_auto_locked: bool
    broker_execution_enabled: bool
    capital_action_enabled: bool
    explanation: str


TOWER_APP_REGISTRY: Tuple[TowerAppRegistration, ...] = (
    TowerAppRegistration(
        app_id="observatory",
        app_name="The Observatory",
        app_label="OB",
        app_status="protected_staging",
        tower_launch_route="/tower/launch/observatory",
        primary_room_route="/ob/dashboard",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The Observatory is currently available only through Tower-controlled "
            "owner launch and protected route checks."
        ),
    ),
    TowerAppRegistration(
        app_id="teller",
        app_name="The Teller",
        app_label="Teller",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/teller",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The Teller is registered as a future Tower-controlled money/workflow app. "
            "This layer does not grant Teller access yet."
        ),
    ),
    TowerAppRegistration(
        app_id="vault",
        app_name="Archive Vault",
        app_label="Vault",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/vault",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "Archive Vault is registered as a future protected evidence/proof room. "
            "This layer does not open Vault storage access."
        ),
    ),
    TowerAppRegistration(
        app_id="clouds",
        app_name="The Clouds",
        app_label="Clouds",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/clouds",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The Clouds is registered as a future owner-wide status room. "
            "This layer does not expose business operations."
        ),
    ),
    TowerAppRegistration(
        app_id="grounds",
        app_name="The Grounds",
        app_label="Grounds",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/grounds",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The Grounds is registered as a future property/operations room. "
            "This layer does not open property workflows."
        ),
    ),
)


TOWER_ROUTE_REGISTRY: Tuple[TowerRouteRegistration, ...] = (
    TowerRouteRegistration(
        route_id="ob_dashboard",
        route="/ob/dashboard",
        label="Dashboard",
        app_id="observatory",
        room_id="dashboard",
        route_type="exact",
        owner_only=False,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="medium",
        lock_state="protected",
        explanation="Normal OB Dashboard requires Tower owner session plus step-up.",
    ),
    TowerRouteRegistration(
        route_id="ob_market_map",
        route="/ob/market-map",
        label="Market Map",
        app_id="observatory",
        room_id="market_map",
        route_type="exact",
        owner_only=False,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="medium",
        lock_state="protected",
        explanation="Market Map requires Tower owner session plus step-up.",
    ),
    TowerRouteRegistration(
        route_id="ob_symbol_page",
        route="/ob/symbol/<symbol>",
        label="Symbol Page",
        app_id="observatory",
        room_id="symbol_page",
        route_type="dynamic",
        owner_only=False,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="medium",
        lock_state="protected_dynamic",
        explanation="Symbol pages are protected dynamic OB routes.",
    ),
    TowerRouteRegistration(
        route_id="ob_trade_center",
        route="/ob/trade-center",
        label="Trade Center",
        app_id="observatory",
        room_id="trade_center",
        route_type="exact",
        owner_only=False,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="high",
        lock_state="protected_no_execution",
        explanation=(
            "Trade Center is protected. Live Auto, broker execution, and capital "
            "action remain locked."
        ),
    ),
    TowerRouteRegistration(
        route_id="ob_review_center",
        route="/ob/review-center",
        label="Review Center",
        app_id="observatory",
        room_id="review_center",
        route_type="exact",
        owner_only=False,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="medium",
        lock_state="protected",
        explanation="Review Center requires Tower owner session plus step-up.",
    ),
    TowerRouteRegistration(
        route_id="ob_owner_console",
        route="/ob/owner-console",
        label="Owner Console",
        app_id="observatory",
        room_id="owner_console",
        route_type="exact",
        owner_only=True,
        requires_owner_session=True,
        requires_step_up=False,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="high",
        lock_state="owner_only_protected",
        explanation="Owner Console is owner-session-only and remains protected.",
    ),
    TowerRouteRegistration(
        route_id="ob_owner_dashboard",
        route="/ob/owner-dashboard",
        label="Owner Dashboard",
        app_id="observatory",
        room_id="owner_dashboard",
        route_type="exact",
        owner_only=True,
        requires_owner_session=True,
        requires_step_up=False,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="high",
        lock_state="owner_only_protected",
        explanation=(
            "Owner Dashboard is the dedicated Observatory owner intelligence surface "
            "behind Tower owner-session protection. Owner Console remains separate."
        ),
    ),
)


def registered_apps() -> List[Dict[str, Any]]:
    return [
        asdict(app)
        for app in TOWER_APP_REGISTRY
    ]


def registered_routes() -> List[Dict[str, Any]]:
    return [
        asdict(route)
        for route in TOWER_ROUTE_REGISTRY
    ]


def app_ids() -> List[str]:
    return [
        app.app_id
        for app in TOWER_APP_REGISTRY
    ]


def protected_ob_routes() -> List[str]:
    return [
        route.route
        for route in TOWER_ROUTE_REGISTRY
        if route.app_id == "observatory"
    ]


def owner_only_routes() -> List[str]:
    return [
        route.route
        for route in TOWER_ROUTE_REGISTRY
        if route.owner_only
    ]


def step_up_routes() -> List[str]:
    return [
        route.route
        for route in TOWER_ROUTE_REGISTRY
        if route.requires_step_up
    ]


def temporary_placeholder_routes() -> List[str]:
    return [
        route.route
        for route in TOWER_ROUTE_REGISTRY
        if route.temporary_placeholder
    ]


def route_by_path(route_path: str) -> Dict[str, Any] | None:
    normalized = str(route_path or "").strip()

    for route in TOWER_ROUTE_REGISTRY:
        if route.route == normalized:
            return asdict(route)

    return None
