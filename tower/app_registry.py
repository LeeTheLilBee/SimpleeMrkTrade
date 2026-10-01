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
        app_status="protected_hosted",
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
        app_status="protected_hosted",
        tower_launch_route="/tower/launch/teller",
        primary_room_route="/teller",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The Teller has an active protected Tower owner launch corridor. "
            "The application remains multi-role, but employee and manager hosted "
            "access are not activated by the owner launch."
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

    # TWR201 — BuyBox is a known ecosystem application, not a live doorway.
    # The BuyBox workspace currently uses development-only local login.
    # Do not represent that as Tower identity or hosted availability.
    TowerAppRegistration(
        app_id="buybox",
        app_name="BuyBox",
        app_label="BuyBox",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/buybox",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "BuyBox is a Tower-governed universal acquisition workspace under "
            "separate development. No hosted owner launch, production BuyBox "
            "session, external acquisition readiness, Vault archival, "
            "closing, funding, or handoff authority is activated here. "
            "Teller owns financial and capacity readiness; Grounds owns "
            "owned-property operations; Vault proof is mediated by Tower."
        ),
    ),,
    TowerAppRegistration(
        app_id="simplee_on_the_go",
        app_name="SimpleeOnTheGo",
        app_label="ATMs",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/simplee-on-the-go",
        owner_only=True,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "SimpleeOnTheGo is registered as the ATM operations and acquisition "
            "system. No hosted Tower launch is published from this registry yet."
        ),
    ),
    TowerAppRegistration(
        app_id="crown_calendar",
        app_name="Crown Calendar",
        app_label="Crown",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/crown-calendar",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "Crown Calendar is registered in the Simplee consumer-app portfolio. "
            "Its hosted runtime and Tower launch corridor are not published yet."
        ),
    ),
    TowerAppRegistration(
        app_id="beauty",
        app_name="Simplee Beauty",
        app_label="Beauty",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/beauty",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation=(
            "The merged beauty application is registered for future Tower entry. "
            "Booking and Teller-led payment handoffs remain unpublished."
        ),
    ),
    TowerAppRegistration(
        app_id="sunday_table",
        app_name="Sunday Table",
        app_label="Table",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/sunday-table",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Sunday Table is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="our_oral_traditions",
        app_name="Our Oral Traditions",
        app_label="Traditions",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/our-oral-traditions",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Our Oral Traditions is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="cookout_ready",
        app_name="Cookout Ready",
        app_label="Cookout",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/cookout-ready",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Cookout Ready is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="sunday_best",
        app_name="Sunday Best",
        app_label="Sunday Best",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/sunday-best",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Sunday Best is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="the_village",
        app_name="The Village",
        app_label="Village",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/the-village",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="The Village is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="simplee_fitness",
        app_name="Simplee Fitness",
        app_label="Fitness",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/simplee-fitness",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Simplee Fitness is registered for future protected Tower entry.",
    ),
    TowerAppRegistration(
        app_id="simplee_skincare",
        app_name="Simplee Skincare",
        app_label="Skincare",
        app_status="registered_future_room",
        tower_launch_route="/tower/app-registry",
        primary_room_route="/apps/simplee-skincare",
        owner_only=False,
        requires_tower_handoff=True,
        dangerous_actions_locked=True,
        live_auto_locked=True,
        broker_execution_enabled=False,
        capital_action_enabled=False,
        explanation="Simplee Skincare is registered for future protected Tower entry.",
    )
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
    TowerRouteRegistration(
        route_id="teller_owner_launch",
        route="/tower/launch/teller",
        label="Open The Teller",
        app_id="teller",
        room_id="owner_launch",
        route_type="exact",
        owner_only=True,
        requires_owner_session=True,
        requires_step_up=True,
        default_denied_when_unknown=True,
        temporary_placeholder=False,
        risk_level="high",
        lock_state="protected_owner_handoff",
        explanation=(
            "Active owner-only Tower launch corridor for The Teller. "
            "A current owner session, step-up, effective entitlement, "
            "verified publication truth, and one-time Tower handoff are required."
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
