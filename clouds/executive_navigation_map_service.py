"""
Service layer for the Clouds Executive Dashboard Navigation Map.

GP009 is descriptive only.

It provides owner navigation references while preserving
Tower authority for authentication, permission, step-up,
and downstream application entry.
"""

from __future__ import annotations

try:
    from .executive_dashboard_detail_service import (
        get_clouds_gp008_status_payload,
        get_executive_dashboard_sections,
    )
    from .executive_navigation_map import (
        ExecutiveNavigationAuthority,
        ExecutiveNavigationAvailability,
        ExecutiveNavigationDestination,
        ExecutiveNavigationDestinationKind,
        ExecutiveNavigationMap,
        ExecutiveNavigationMapSummary,
        ExecutiveNavigationMode,
        ExecutiveNavigationSectionMap,
        filter_navigation_destinations,
        navigation_destination_sort_key,
        navigation_section_sort_key,
    )
except ImportError:
    from executive_dashboard_detail_service import (
        get_clouds_gp008_status_payload,
        get_executive_dashboard_sections,
    )
    from executive_navigation_map import (
        ExecutiveNavigationAuthority,
        ExecutiveNavigationAvailability,
        ExecutiveNavigationDestination,
        ExecutiveNavigationDestinationKind,
        ExecutiveNavigationMap,
        ExecutiveNavigationMapSummary,
        ExecutiveNavigationMode,
        ExecutiveNavigationSectionMap,
        filter_navigation_destinations,
        navigation_destination_sort_key,
        navigation_section_sort_key,
    )


ALLOWED_CLOUDS_ACTIONS = (
    "Display executive navigation destinations",
    "Map executive sections to navigation destinations",
    "Distinguish Clouds-internal navigation from Tower handoffs",
    "Display source application and mission-lane ownership",
    "Display navigation availability",
    "Filter navigation destinations",
    "Provide safe route references",
    "Fail closed on unknown destinations",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot authenticate the owner",
    "Clouds cannot grant application permission",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot bypass Tower",
    "Clouds cannot launch downstream applications directly",
    "Clouds cannot approve an owner decision",
    "Clouds cannot execute trades",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


SECTION_ORDER = {
    "today": 10,
    "priorities": 20,
    "attention": 30,
    "mission_lanes": 40,
    "applications": 50,
    "readiness": 60,
}


def _destination(
    *,
    destination_id: str,
    label: str,
    description: str,
    kind: str,
    open_route: str | None,
    navigation_mode: str,
    availability: str,
    authority: str,
    source_section_id: str | None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    requires_tower: bool = False,
    requires_owner_permission: bool = False,
    requires_step_up: bool = False,
    display_order: int,
) -> ExecutiveNavigationDestination:
    return ExecutiveNavigationDestination(
        destination_id=destination_id,
        label=label,
        description=description,
        kind=kind,
        open_route=open_route,
        navigation_mode=navigation_mode,
        availability=availability,
        authority=authority,
        source_section_id=source_section_id,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        requires_tower=requires_tower,
        requires_owner_permission=(
            requires_owner_permission
        ),
        requires_step_up=requires_step_up,
        clouds_executes_navigation=False,
        downstream_execution_performed=False,
        display_order=display_order,
    )


def _build_destinations() -> tuple[
    ExecutiveNavigationDestination,
    ...
]:
    destinations = (
        _destination(
            destination_id="clouds-executive-dashboard",
            label="Executive Dashboard",
            description=(
                "Return to the Clouds executive owner "
                "dashboard."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .DASHBOARD.value
            ),
            open_route="/clouds/executive",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id=None,
            display_order=10,
        ),

        _destination(
            destination_id="clouds-today",
            label="Today",
            description=(
                "Open the Clouds Today owner-command "
                "surface."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .TODAY.value
            ),
            open_route="/clouds/today",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="today",
            display_order=20,
        ),

        _destination(
            destination_id="clouds-priority-board",
            label="Priority Board",
            description=(
                "Open the Clouds strategic owner "
                "priority board."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .PRIORITY.value
            ),
            open_route="/clouds/priorities",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="priorities",
            display_order=30,
        ),

        _destination(
            destination_id="clouds-owner-attention",
            label="Owner Attention",
            description=(
                "Open the unified owner-attention "
                "command surface."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .OWNER_ATTENTION.value
            ),
            open_route="/clouds/attention",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="attention",
            display_order=40,
        ),

        _destination(
            destination_id="clouds-mission-lanes",
            label="Mission Lanes",
            description=(
                "Open the Clouds mission-lane "
                "command surface."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .MISSION_LANE.value
            ),
            open_route="/clouds/mission-lanes",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="mission_lanes",
            display_order=50,
        ),

        _destination(
            destination_id="clouds-applications",
            label="Applications",
            description=(
                "Open the Clouds owner application "
                "registry surface."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .APPLICATION.value
            ),
            open_route="/clouds/applications",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="applications",
            display_order=60,
        ),

        _destination(
            destination_id="clouds-readiness",
            label="Overall Readiness",
            description=(
                "Open the executive readiness detail "
                "inside Clouds."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .READINESS.value
            ),
            open_route="/clouds/executive/readiness",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .AVAILABLE.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .CLOUDS.value
            ),
            source_section_id="readiness",
            display_order=70,
        ),

        _destination(
            destination_id="tower-observatory",
            label="The Observatory",
            description=(
                "Request Tower-mediated entry to "
                "The Observatory. Clouds does not "
                "perform the launch."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .APPLICATION.value
            ),
            open_route="/tower/launch/observatory",
            navigation_mode=(
                ExecutiveNavigationMode
                .TOWER_HANDOFF.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .REFERENCED.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .TOWER.value
            ),
            source_section_id="applications",
            source_app_id="observatory",
            source_lane_id="investment_engine",
            requires_tower=True,
            requires_owner_permission=True,
            requires_step_up=True,
            display_order=80,
        ),

        _destination(
            destination_id="tower-teller",
            label="The Teller",
            description=(
                "Request Tower-mediated entry to "
                "The Teller when that application "
                "becomes available."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .APPLICATION.value
            ),
            open_route="/tower/launch/teller",
            navigation_mode=(
                ExecutiveNavigationMode
                .TOWER_HANDOFF.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .RESERVED.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .TOWER.value
            ),
            source_section_id="applications",
            source_app_id="teller",
            source_lane_id="people_and_payments",
            requires_tower=True,
            requires_owner_permission=True,
            requires_step_up=True,
            display_order=90,
        ),

        _destination(
            destination_id="tower-grounds",
            label="The Grounds",
            description=(
                "Request Tower-mediated entry to "
                "The Grounds when that application "
                "becomes available."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .APPLICATION.value
            ),
            open_route="/tower/launch/grounds",
            navigation_mode=(
                ExecutiveNavigationMode
                .TOWER_HANDOFF.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .RESERVED.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .TOWER.value
            ),
            source_section_id="applications",
            source_app_id="grounds",
            source_lane_id="property_operations",
            requires_tower=True,
            requires_owner_permission=True,
            requires_step_up=True,
            display_order=100,
        ),

        _destination(
            destination_id="tower-vault",
            label="Archive Vault",
            description=(
                "Reference Archive Vault through "
                "Tower authority only. Clouds does "
                "not retrieve raw Vault evidence."
            ),
            kind=(
                ExecutiveNavigationDestinationKind
                .APPLICATION.value
            ),
            open_route="/tower/launch/archive-vault",
            navigation_mode=(
                ExecutiveNavigationMode
                .TOWER_HANDOFF.value
            ),
            availability=(
                ExecutiveNavigationAvailability
                .REFERENCED.value
            ),
            authority=(
                ExecutiveNavigationAuthority
                .TOWER.value
            ),
            source_section_id="applications",
            source_app_id="archive_vault",
            requires_tower=True,
            requires_owner_permission=True,
            requires_step_up=True,
            display_order=110,
        ),
    )

    return tuple(
        sorted(
            destinations,
            key=navigation_destination_sort_key,
        )
    )


def get_executive_navigation_destinations() -> tuple[
    ExecutiveNavigationDestination,
    ...
]:
    return _build_destinations()


def get_executive_navigation_destination(
    destination_id: str,
) -> ExecutiveNavigationDestination:
    for destination in (
        get_executive_navigation_destinations()
    ):
        if (
            destination.destination_id
            == destination_id
        ):
            return destination

    raise KeyError(
        "Unknown Clouds executive navigation "
        f"destination: {destination_id}"
    )


def get_executive_navigation_destination_payload(
    destination_id: str,
) -> dict:
    return (
        get_executive_navigation_destination(
            destination_id
        ).to_dict()
    )


def filter_executive_navigation_destinations(
    *,
    kind: str | None = None,
    navigation_mode: str | None = None,
    availability: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    requires_tower: bool | None = None,
) -> tuple[
    ExecutiveNavigationDestination,
    ...
]:
    return filter_navigation_destinations(
        get_executive_navigation_destinations(),
        kind=kind,
        navigation_mode=navigation_mode,
        availability=availability,
        source_section_id=source_section_id,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        requires_tower=requires_tower,
    )


def _build_section_maps() -> tuple[
    ExecutiveNavigationSectionMap,
    ...
]:
    details = get_executive_dashboard_sections()
    destinations = (
        get_executive_navigation_destinations()
    )

    maps = []

    for detail in details:
        section_id = (
            detail.summary.section_id
        )

        section_destinations = tuple(
            destination
            for destination in destinations
            if (
                destination.source_section_id
                == section_id
            )
        )

        internal_count = sum(
            1
            for destination
            in section_destinations
            if destination.navigation_mode
            == ExecutiveNavigationMode
            .CLOUDS_INTERNAL.value
        )

        tower_count = sum(
            1
            for destination
            in section_destinations
            if destination.navigation_mode
            == ExecutiveNavigationMode
            .TOWER_HANDOFF.value
        )

        default_destination_id = (
            section_destinations[0]
            .destination_id
            if section_destinations
            else None
        )

        maps.append(
            ExecutiveNavigationSectionMap(
                section_id=section_id,
                section_label=(
                    detail.summary.title
                ),
                destination_ids=tuple(
                    destination.destination_id
                    for destination
                    in section_destinations
                ),
                default_destination_id=(
                    default_destination_id
                ),
                clouds_internal_count=(
                    internal_count
                ),
                tower_handoff_count=(
                    tower_count
                ),
                source_integrity_verified=(
                    detail.summary
                    .source_integrity_verified
                ),
                execution_performed=False,
                display_order=(
                    SECTION_ORDER[
                        section_id
                    ]
                ),
            )
        )

    return tuple(
        sorted(
            maps,
            key=navigation_section_sort_key,
        )
    )


def get_executive_navigation_sections() -> tuple[
    ExecutiveNavigationSectionMap,
    ...
]:
    return _build_section_maps()


def get_executive_navigation_section(
    section_id: str,
) -> ExecutiveNavigationSectionMap:
    for section in (
        get_executive_navigation_sections()
    ):
        if section.section_id == section_id:
            return section

    raise KeyError(
        "Unknown Clouds executive navigation "
        f"section: {section_id}"
    )


def get_executive_navigation_section_payload(
    section_id: str,
) -> dict:
    return (
        get_executive_navigation_section(
            section_id
        ).to_dict()
    )


def get_executive_navigation_map_summary(
) -> ExecutiveNavigationMapSummary:
    destinations = (
        get_executive_navigation_destinations()
    )

    sections = (
        get_executive_navigation_sections()
    )

    internal_count = sum(
        1
        for destination in destinations
        if destination.navigation_mode
        == ExecutiveNavigationMode
        .CLOUDS_INTERNAL.value
    )

    tower_count = sum(
        1
        for destination in destinations
        if destination.navigation_mode
        == ExecutiveNavigationMode
        .TOWER_HANDOFF.value
    )

    unavailable_count = sum(
        1
        for destination in destinations
        if destination.availability
        in {
            ExecutiveNavigationAvailability
            .RESERVED.value,
            ExecutiveNavigationAvailability
            .HELD.value,
        }
    )

    source_integrity_verified = all(
        section.source_integrity_verified
        for section in sections
    )

    tower_boundary_preserved = all(
        (
            not destination.requires_tower
            or (
                destination.navigation_mode
                == ExecutiveNavigationMode
                .TOWER_HANDOFF.value
                and destination.authority
                == ExecutiveNavigationAuthority
                .TOWER.value
                and destination
                .clouds_executes_navigation
                is False
            )
        )
        for destination in destinations
    )

    return ExecutiveNavigationMapSummary(
        destination_count=len(destinations),
        section_count=len(sections),
        clouds_internal_count=internal_count,
        tower_handoff_count=tower_count,
        unavailable_count=unavailable_count,
        source_integrity_verified=(
            source_integrity_verified
        ),
        tower_boundary_preserved=(
            tower_boundary_preserved
        ),
        downstream_execution_performed=False,
    )


def get_executive_navigation_map(
) -> ExecutiveNavigationMap:
    return ExecutiveNavigationMap(
        title="Executive Navigation Map",
        subtitle=(
            "Owner navigation references across "
            "Clouds and Tower-mediated application "
            "boundaries."
        ),
        summary=(
            get_executive_navigation_map_summary()
        ),
        destinations=(
            get_executive_navigation_destinations()
        ),
        sections=(
            get_executive_navigation_sections()
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        boundary_notice=(
            "Clouds describes navigation. Tower "
            "retains authentication, permission, "
            "step-up, and downstream application "
            "entry authority."
        ),
    )


def get_executive_navigation_map_payload(
) -> dict:
    return (
        get_executive_navigation_map()
        .to_dict()
    )


def get_clouds_gp009_status_payload() -> dict:
    gp008 = get_clouds_gp008_status_payload()
    navigation_map = (
        get_executive_navigation_map()
    )

    summary = navigation_map.summary

    safe_to_continue = (
        gp008["status"] == "ready"
        and gp008["safe_to_continue"] is True
        and summary.section_count == 6
        and summary.destination_count == 11
        and summary.clouds_internal_count == 7
        and summary.tower_handoff_count == 4
        and summary.source_integrity_verified
        is True
        and summary.tower_boundary_preserved
        is True
        and summary
        .downstream_execution_performed
        is False
        and all(
            destination
            .clouds_executes_navigation
            is False
            for destination
            in navigation_map.destinations
        )
        and all(
            destination
            .downstream_execution_performed
            is False
            for destination
            in navigation_map.destinations
        )
    )

    return {
        "pack": "GP009",
        "section": (
            "EXECUTIVE DASHBOARD NAVIGATION MAP"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": safe_to_continue,
        "section_count": summary.section_count,
        "destination_count": (
            summary.destination_count
        ),
        "clouds_internal_count": (
            summary.clouds_internal_count
        ),
        "tower_handoff_count": (
            summary.tower_handoff_count
        ),
        "unavailable_count": (
            summary.unavailable_count
        ),
        "source_integrity_verified": (
            summary.source_integrity_verified
        ),
        "tower_boundary_preserved": (
            summary.tower_boundary_preserved
        ),
        "navigation_execution_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP010 — EXECUTIVE OWNER COMMAND "
            "WORKSPACE SURFACE"
        ),
    }
