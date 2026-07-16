"""
Service layer for the Clouds owner app registry surface.

Uses only GP001 local registry and local starter status data.
"""

from __future__ import annotations

try:
    from .app_registry_surface import (
        AppRegistryCard,
        AppRegistryDetail,
        AppRegistryGroup,
        AppRegistrySummary,
        AppRegistrySurface,
        app_attention_sort_key,
        app_registry_sort_key,
        build_app_registry_card,
        filter_registry_cards,
    )
    from .contracts import (
        AppConnectionState,
        HealthState,
    )
    from .owner_command_service import (
        STARTER_APP_STATUS,
    )
    from .registry import (
        get_app,
        list_apps,
    )
except ImportError:
    from app_registry_surface import (
        AppRegistryCard,
        AppRegistryDetail,
        AppRegistryGroup,
        AppRegistrySummary,
        AppRegistrySurface,
        app_attention_sort_key,
        app_registry_sort_key,
        build_app_registry_card,
        filter_registry_cards,
    )
    from contracts import (
        AppConnectionState,
        HealthState,
    )
    from owner_command_service import (
        STARTER_APP_STATUS,
    )
    from registry import (
        get_app,
        list_apps,
    )


APP_CAPABILITIES = {
    "tower": (
        "Owner identity and secure session entry",
        "Application permission checks",
        "Step-up and approval boundaries",
        "Protected application routing",
    ),
    "observatory": (
        "Investment intelligence",
        "Portfolio and risk stewardship",
        "Owner-controlled trading workflows",
        "Trade review and evidence",
    ),
    "archive_vault": (
        "Sealed evidence preservation",
        "Permanent receipt memory",
        "Protected document stewardship",
        "Tower-mediated proof and record access",
    ),
    "teller": (
        "Payroll and payment workflows",
        "Employee and vendor workflows",
        "Agreement and onboarding workflows",
        "Workflow-safe proof requests through Tower",
    ),
    "grounds": (
        "Property acquisition operations",
        "Leasing and occupancy operations",
        "Maintenance and vendor coordination",
        "Portfolio stewardship and compliance",
    ),
    "clouds": (
        "Cross-business owner summaries",
        "Owner attention and priorities",
        "Application and mission-lane visibility",
        "Safe owner navigation handoffs",
    ),
}


CLOUDS_PERMISSIONS = (
    "Display compact owner-facing app summaries",
    "Display app health and readiness",
    "Display owner attention counts",
    "Provide descriptive navigation handoffs",
    "Show application authority boundaries",
)


CLOUDS_PROHIBITIONS = (
    "Clouds cannot authenticate the owner",
    "Clouds cannot grant application permissions",
    "Clouds cannot perform step-up",
    "Clouds cannot execute another application's workflow",
    "Clouds cannot bypass Tower navigation controls",
    "Clouds cannot infer that navigation completed execution",
)


def _build_cards() -> tuple[AppRegistryCard, ...]:
    cards = []

    for app in list_apps():
        try:
            status = STARTER_APP_STATUS[app.app_id]
        except KeyError as exc:
            raise RuntimeError(
                f"Missing local status for app: "
                f"{app.app_id}"
            ) from exc

        cards.append(
            build_app_registry_card(
                app,
                status,
            )
        )

    return tuple(
        sorted(
            cards,
            key=app_registry_sort_key,
        )
    )


def get_app_registry_surface() -> AppRegistrySurface:
    cards = _build_cards()

    active_apps = tuple(
        card
        for card in cards
        if card.group
        == AppRegistryGroup.ACTIVE.value
    )

    reserved_apps = tuple(
        card
        for card in cards
        if card.group
        == AppRegistryGroup.RESERVED.value
    )

    summary = AppRegistrySummary(
        total_app_count=len(cards),
        active_app_count=len(active_apps),
        reserved_app_count=len(reserved_apps),
        connected_app_count=sum(
            card.connection_state
            == AppConnectionState.CONNECTED.value
            for card in cards
        ),
        summary_ready_app_count=sum(
            card.connection_state
            == AppConnectionState.SUMMARY_READY.value
            for card in cards
        ),
        healthy_app_count=sum(
            card.health == HealthState.HEALTHY.value
            for card in cards
        ),
        watch_app_count=sum(
            card.health == HealthState.WATCH.value
            for card in cards
        ),
        attention_app_count=sum(
            card.health
            == HealthState.ATTENTION.value
            for card in cards
        ),
        blocked_app_count=sum(
            card.health == HealthState.BLOCKED.value
            for card in cards
        ),
        unknown_app_count=sum(
            card.health == HealthState.UNKNOWN.value
            for card in cards
        ),
        total_attention_count=sum(
            card.attention_count
            for card in cards
        ),
        owner_execution_performed=False,
    )

    return AppRegistrySurface(
        title="Owner Application Registry",
        subtitle=(
            "See every Simplee application, its current "
            "readiness, authority boundary, and safe owner "
            "entry path."
        ),
        summary=summary,
        active_apps=active_apps,
        reserved_apps=reserved_apps,
        all_apps=cards,
        boundary_notice=(
            "Opening an application is a navigation handoff. "
            "Tower remains responsible for identity, permission, "
            "step-up, and protected access."
        ),
    )


def get_app_registry_surface_payload() -> dict:
    return get_app_registry_surface().to_dict()


def get_app_registry_cards(
    *,
    group: str | None = None,
    health: str | None = None,
    readiness: str | None = None,
    attention_only: bool = False,
) -> tuple[AppRegistryCard, ...]:
    return filter_registry_cards(
        _build_cards(),
        group=group,
        health=health,
        readiness=readiness,
        attention_only=attention_only,
    )


def get_app_registry_attention_queue() -> tuple[
    AppRegistryCard,
    ...
]:
    cards = tuple(
        card
        for card in _build_cards()
        if (
            card.attention_count > 0
            or card.health
            in {
                HealthState.WATCH.value,
                HealthState.ATTENTION.value,
                HealthState.BLOCKED.value,
            }
        )
    )

    return tuple(
        sorted(
            cards,
            key=app_attention_sort_key,
        )
    )


def get_app_registry_detail(
    app_id: str,
) -> AppRegistryDetail:
    app = get_app(app_id)

    if app is None:
        raise KeyError(
            f"Clouds app registry entry not found: "
            f"{app_id}"
        )

    status = STARTER_APP_STATUS.get(app_id)

    if status is None:
        raise RuntimeError(
            f"Clouds app status not found: {app_id}"
        )

    capabilities = APP_CAPABILITIES.get(
        app_id,
        (),
    )

    card = build_app_registry_card(
        app,
        status,
    )

    return AppRegistryDetail(
        card=card,
        capabilities=tuple(capabilities),
        clouds_permissions=CLOUDS_PERMISSIONS,
        clouds_prohibitions=CLOUDS_PROHIBITIONS,
        navigation_requires_tower=(
            app_id != "clouds"
        ),
        downstream_execution_performed=False,
    )


def get_app_registry_detail_payload(
    app_id: str,
) -> dict:
    return get_app_registry_detail(
        app_id
    ).to_dict()


def get_clouds_gp002_status_payload() -> dict:
    surface = get_app_registry_surface()
    attention_queue = (
        get_app_registry_attention_queue()
    )

    return {
        "pack": "GP002",
        "section": (
            "OWNER COMMAND APP REGISTRY SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "total_app_count": (
            surface.summary.total_app_count
        ),
        "active_app_count": (
            surface.summary.active_app_count
        ),
        "reserved_app_count": (
            surface.summary.reserved_app_count
        ),
        "attention_app_count": len(
            attention_queue
        ),
        "tower_boundary_preserved": True,
        "direct_app_execution": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP003 — OWNER COMMAND MISSION LANE SURFACE"
        ),
    }
