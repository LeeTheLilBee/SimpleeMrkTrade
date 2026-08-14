"""
Service layer for the Clouds owner mission-lane surface.

Uses only local Clouds registries and local starter statuses.
"""

from __future__ import annotations

try:
    from .contracts import (
        HealthState,
        ReadinessState,
    )
    from .mission_lane_surface import (
        MissionLaneCard,
        MissionLaneDetail,
        MissionLaneGroup,
        MissionLaneSummary,
        MissionLaneSurface,
        build_mission_lane_card,
        filter_mission_lane_cards,
        mission_lane_attention_sort_key,
        mission_lane_sort_key,
    )
    from .owner_command_service import (
        STARTER_LANE_STATUS,
    )
    from .registry import (
        get_app,
        get_mission_lane,
        list_mission_lanes,
    )
except ImportError:
    from contracts import (
        HealthState,
        ReadinessState,
    )
    from mission_lane_surface import (
        MissionLaneCard,
        MissionLaneDetail,
        MissionLaneGroup,
        MissionLaneSummary,
        MissionLaneSurface,
        build_mission_lane_card,
        filter_mission_lane_cards,
        mission_lane_attention_sort_key,
        mission_lane_sort_key,
    )
    from owner_command_service import (
        STARTER_LANE_STATUS,
    )
    from registry import (
        get_app,
        get_mission_lane,
        list_mission_lanes,
    )


LANE_OWNER_QUESTIONS = {
    "owner_command": (
        "What requires owner attention now?",
        "Which application or business needs direction?",
        "Which operating surface should the owner open?",
    ),
    "investment_engine": (
        "What is the current investment-engine readiness?",
        "Is an owner review or decision required?",
        "Should the owner open The Observatory?",
    ),
    "trust_stewardship": (
        "Is trust evidence safely preserved?",
        "Does any trust matter require owner review?",
        "Should the owner open the Tower Vault surface?",
    ),
    "atm_operations": (
        "What ATM preparation remains incomplete?",
        "Does route or funding planning require attention?",
        "Which future Teller workflow will own the action?",
    ),
    "real_estate": (
        "What office or property milestone comes next?",
        "Is acquisition research ready to begin?",
        "Should the owner open The Grounds when available?",
    ),
    "people_and_payments": (
        "Which people or payment workflow is being held?",
        "What Teller alignment is required first?",
        "Does the owner need to review a future workflow?",
    ),
}


CLOUDS_PERMISSIONS = (
    "Display mission-lane purpose and ownership",
    "Display local lane health and readiness",
    "Display owner-attention counts",
    "Group active and reserved lanes",
    "Provide navigation toward the owning application",
    "Show the owning application's authority boundary",
)


CLOUDS_PROHIBITIONS = (
    "Clouds cannot execute mission-lane operations",
    "Clouds cannot authenticate or authorize the owner",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault documents",
    "Clouds cannot operate property workflows",
)


def _build_lane_cards() -> tuple[
    MissionLaneCard,
    ...
]:
    cards = []

    for lane in list_mission_lanes():
        status = STARTER_LANE_STATUS.get(
            lane.lane_id
        )

        if status is None:
            raise RuntimeError(
                f"Missing local status for mission lane: "
                f"{lane.lane_id}"
            )

        app = get_app(
            lane.owning_app_id
        )

        if app is None:
            raise RuntimeError(
                f"Mission lane {lane.lane_id!r} "
                f"references missing app "
                f"{lane.owning_app_id!r}."
            )

        cards.append(
            build_mission_lane_card(
                lane,
                status,
                owning_app_name=app.app_name,
                owning_app_route=(
                    app.owner_surface_route
                ),
            )
        )

    return tuple(
        sorted(
            cards,
            key=mission_lane_sort_key,
        )
    )


def get_mission_lane_surface() -> MissionLaneSurface:
    cards = _build_lane_cards()

    active_lanes = tuple(
        card
        for card in cards
        if card.group
        == MissionLaneGroup.ACTIVE.value
    )

    reserved_lanes = tuple(
        card
        for card in cards
        if card.group
        == MissionLaneGroup.RESERVED.value
    )

    summary = MissionLaneSummary(
        total_lane_count=len(cards),
        active_lane_count=len(active_lanes),
        reserved_lane_count=len(reserved_lanes),
        healthy_lane_count=sum(
            card.health == HealthState.HEALTHY.value
            for card in cards
        ),
        watch_lane_count=sum(
            card.health == HealthState.WATCH.value
            for card in cards
        ),
        attention_lane_count=sum(
            card.health
            == HealthState.ATTENTION.value
            for card in cards
        ),
        blocked_lane_count=sum(
            card.health == HealthState.BLOCKED.value
            for card in cards
        ),
        unknown_lane_count=sum(
            card.health == HealthState.UNKNOWN.value
            for card in cards
        ),
        building_lane_count=sum(
            card.readiness
            == ReadinessState.BUILDING.value
            for card in cards
        ),
        foundation_lane_count=sum(
            card.readiness
            == ReadinessState.FOUNDATION.value
            for card in cards
        ),
        not_started_lane_count=sum(
            card.readiness
            == ReadinessState.NOT_STARTED.value
            for card in cards
        ),
        held_lane_count=sum(
            card.readiness
            == ReadinessState.HELD.value
            for card in cards
        ),
        total_attention_count=sum(
            card.attention_count
            for card in cards
        ),
        clouds_execution_performed=False,
    )

    return MissionLaneSurface(
        title="Owner Mission Lanes",
        subtitle=(
            "See each major business and operating lane, "
            "its owning application, current readiness, "
            "and owner-attention state."
        ),
        summary=summary,
        active_lanes=active_lanes,
        reserved_lanes=reserved_lanes,
        all_lanes=cards,
        boundary_notice=(
            "Mission-lane cards are owner summaries and "
            "navigation handoffs. Operational execution "
            "remains inside the lane's owning application "
            "under Tower controls."
        ),
    )


def get_mission_lane_surface_payload() -> dict:
    return get_mission_lane_surface().to_dict()


def get_mission_lane_cards(
    *,
    group: str | None = None,
    health: str | None = None,
    readiness: str | None = None,
    owning_app_id: str | None = None,
    attention_only: bool = False,
) -> tuple[MissionLaneCard, ...]:
    return filter_mission_lane_cards(
        _build_lane_cards(),
        group=group,
        health=health,
        readiness=readiness,
        owning_app_id=owning_app_id,
        attention_only=attention_only,
    )


def get_mission_lane_attention_queue() -> tuple[
    MissionLaneCard,
    ...
]:
    cards = tuple(
        card
        for card in _build_lane_cards()
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
            key=mission_lane_attention_sort_key,
        )
    )


def get_mission_lane_detail(
    lane_id: str,
) -> MissionLaneDetail:
    lane = get_mission_lane(
        lane_id
    )

    if lane is None:
        raise KeyError(
            f"Clouds mission lane not found: "
            f"{lane_id}"
        )

    status = STARTER_LANE_STATUS.get(
        lane_id
    )

    if status is None:
        raise RuntimeError(
            f"Clouds mission-lane status not found: "
            f"{lane_id}"
        )

    app = get_app(
        lane.owning_app_id
    )

    if app is None:
        raise RuntimeError(
            f"Owning application not found: "
            f"{lane.owning_app_id}"
        )

    card = build_mission_lane_card(
        lane,
        status,
        owning_app_name=app.app_name,
        owning_app_route=(
            app.owner_surface_route
        ),
    )

    return MissionLaneDetail(
        card=card,
        owner_questions=tuple(
            LANE_OWNER_QUESTIONS.get(
                lane_id,
                (),
            )
        ),
        clouds_permissions=CLOUDS_PERMISSIONS,
        clouds_prohibitions=CLOUDS_PROHIBITIONS,
        owning_app_authority_boundary=(
            app.authority_boundary
        ),
        navigation_requires_tower=(
            lane.owning_app_id != "clouds"
        ),
        downstream_execution_performed=False,
    )


def get_mission_lane_detail_payload(
    lane_id: str,
) -> dict:
    return get_mission_lane_detail(
        lane_id
    ).to_dict()


def get_clouds_gp003_status_payload() -> dict:
    surface = get_mission_lane_surface()
    attention_queue = (
        get_mission_lane_attention_queue()
    )

    return {
        "pack": "GP003",
        "section": (
            "OWNER COMMAND MISSION LANE SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "total_lane_count": (
            surface.summary.total_lane_count
        ),
        "active_lane_count": (
            surface.summary.active_lane_count
        ),
        "reserved_lane_count": (
            surface.summary.reserved_lane_count
        ),
        "attention_lane_count": len(
            attention_queue
        ),
        "owning_app_boundaries_visible": True,
        "tower_boundary_preserved": True,
        "direct_lane_execution": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP004 — OWNER ATTENTION COMMAND SURFACE"
        ),
    }
