"""
Service layer for the Clouds Owner Command Today Surface.

It composes only the compact local summaries created by
GP001–GP004.
"""

from __future__ import annotations

try:
    from .app_registry_surface_service import (
        get_app_registry_cards,
    )
    from .mission_lane_surface_service import (
        get_mission_lane_cards,
    )
    from .owner_attention_surface_service import (
        get_owner_attention_commands,
    )
    from .registry import (
        get_app,
        get_mission_lane,
    )
    from .today_surface import (
        TodayCard,
        TodayCardKind,
        TodayDetail,
        TodayHeader,
        TodayNavigationMode,
        TodayPriority,
        TodaySurface,
        filter_today_cards,
        today_sort_key,
    )
except ImportError:
    from app_registry_surface_service import (
        get_app_registry_cards,
    )
    from mission_lane_surface_service import (
        get_mission_lane_cards,
    )
    from owner_attention_surface_service import (
        get_owner_attention_commands,
    )
    from registry import (
        get_app,
        get_mission_lane,
    )
    from today_surface import (
        TodayCard,
        TodayCardKind,
        TodayDetail,
        TodayHeader,
        TodayNavigationMode,
        TodayPriority,
        TodaySurface,
        filter_today_cards,
        today_sort_key,
    )


OWNER_QUESTIONS = {
    TodayCardKind.FOCUS.value: (
        "What requires owner attention today?",
        "What decision or review comes next?",
        "Which operating app owns the next action?",
    ),
    TodayCardKind.WATCH.value: (
        "What should the owner continue watching?",
        "What condition would increase urgency?",
        "Which app owns the underlying status?",
    ),
    TodayCardKind.TARGET.value: (
        "What target is currently open?",
        "What milestone would close the target?",
        "Where should the owner navigate next?",
    ),
}


ALLOWED_CLOUDS_ACTIONS = (
    "Display today's owner priorities",
    "Group focus, watch, and target cards",
    "Show source apps and mission lanes",
    "Provide safe navigation handoffs",
    "Filter and order Today cards",
    "Display owner review questions",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot approve an action",
    "Clouds cannot execute an action",
    "Clouds cannot authenticate or authorize",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _navigation_mode(
    *,
    open_route: str | None,
    source_app_id: str | None,
) -> str:
    if not open_route:
        return TodayNavigationMode.NONE.value

    if source_app_id == "clouds":
        return (
            TodayNavigationMode
            .CLOUDS_INTERNAL
            .value
        )

    return (
        TodayNavigationMode
        .TOWER_HANDOFF
        .value
    )


def _attention_focus_cards() -> tuple[
    TodayCard,
    ...
]:
    cards = []

    for item in get_owner_attention_commands():
        if not item.action_required:
            continue

        cards.append(
            TodayCard(
                card_id=(
                    "today-focus-"
                    f"{item.attention_id}"
                ),
                title=item.title,
                summary=item.summary,
                kind=TodayCardKind.FOCUS.value,
                priority=item.priority,
                source_app_id=item.source_app_id,
                source_app_name=item.source_app_name,
                source_lane_id=item.source_lane_id,
                source_lane_name=item.source_lane_name,
                action_required=True,
                owner_action_label="Review today",
                open_route=item.open_route,
                navigation_mode=(
                    _navigation_mode(
                        open_route=item.open_route,
                        source_app_id=(
                            item.source_app_id
                        ),
                    )
                ),
                source_integrity_verified=(
                    item.source_integrity_verified
                ),
                execution_performed=False,
            )
        )

    return tuple(cards)


def _attention_watch_cards() -> tuple[
    TodayCard,
    ...
]:
    cards = []

    for item in get_owner_attention_commands():
        if item.action_required:
            continue

        cards.append(
            TodayCard(
                card_id=(
                    "today-watch-"
                    f"{item.attention_id}"
                ),
                title=item.title,
                summary=item.summary,
                kind=TodayCardKind.WATCH.value,
                priority=item.priority,
                source_app_id=item.source_app_id,
                source_app_name=item.source_app_name,
                source_lane_id=item.source_lane_id,
                source_lane_name=item.source_lane_name,
                action_required=False,
                owner_action_label="Keep watch",
                open_route=item.open_route,
                navigation_mode=(
                    _navigation_mode(
                        open_route=item.open_route,
                        source_app_id=(
                            item.source_app_id
                        ),
                    )
                ),
                source_integrity_verified=(
                    item.source_integrity_verified
                ),
                execution_performed=False,
            )
        )

    return tuple(cards)


def _open_target_cards() -> tuple[
    TodayCard,
    ...
]:
    cards = []

    # Reserved applications become visible targets without
    # pretending they are already operational.
    for app_card in get_app_registry_cards(
        group="reserved"
    ):
        cards.append(
            TodayCard(
                card_id=(
                    "today-target-app-"
                    f"{app_card.app_id}"
                ),
                title=(
                    f"Prepare {app_card.app_name}"
                ),
                summary=app_card.status_summary,
                kind=TodayCardKind.TARGET.value,
                priority=TodayPriority.ROUTINE.value,
                source_app_id=app_card.app_id,
                source_app_name=app_card.app_name,
                source_lane_id=None,
                source_lane_name=None,
                action_required=False,
                owner_action_label=(
                    "View reserved app"
                ),
                open_route=app_card.open_route,
                navigation_mode=(
                    _navigation_mode(
                        open_route=app_card.open_route,
                        source_app_id=app_card.app_id,
                    )
                ),
                source_integrity_verified=True,
                execution_performed=False,
            )
        )

    # Reserved mission lanes also remain visible targets.
    for lane_card in get_mission_lane_cards(
        group="reserved"
    ):
        app = get_app(
            lane_card.owning_app_id
        )

        lane = get_mission_lane(
            lane_card.lane_id
        )

        verified = (
            app is not None
            and lane is not None
            and lane.owning_app_id
            == lane_card.owning_app_id
        )

        cards.append(
            TodayCard(
                card_id=(
                    "today-target-lane-"
                    f"{lane_card.lane_id}"
                ),
                title=(
                    f"Prepare {lane_card.lane_name}"
                ),
                summary=lane_card.status_summary,
                kind=TodayCardKind.TARGET.value,
                priority=TodayPriority.ROUTINE.value,
                source_app_id=(
                    lane_card.owning_app_id
                ),
                source_app_name=(
                    lane_card.owning_app_name
                ),
                source_lane_id=lane_card.lane_id,
                source_lane_name=lane_card.lane_name,
                action_required=False,
                owner_action_label=(
                    "View reserved lane"
                ),
                open_route=lane_card.open_route,
                navigation_mode=(
                    _navigation_mode(
                        open_route=lane_card.open_route,
                        source_app_id=(
                            lane_card.owning_app_id
                        ),
                    )
                ),
                source_integrity_verified=verified,
                execution_performed=False,
            )
        )

    return tuple(cards)


def get_today_cards() -> tuple[
    TodayCard,
    ...
]:
    cards = (
        *_attention_focus_cards(),
        *_attention_watch_cards(),
        *_open_target_cards(),
    )

    identifiers = [
        card.card_id
        for card in cards
    ]

    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError(
            "Duplicate Today card IDs detected."
        )

    return tuple(
        sorted(
            cards,
            key=today_sort_key,
        )
    )


def get_today_surface() -> TodaySurface:
    cards = get_today_cards()

    focus = tuple(
        card
        for card in cards
        if card.kind == TodayCardKind.FOCUS.value
    )

    watch = tuple(
        card
        for card in cards
        if card.kind == TodayCardKind.WATCH.value
    )

    targets = tuple(
        card
        for card in cards
        if card.kind == TodayCardKind.TARGET.value
    )

    action_required_count = sum(
        card.action_required
        for card in cards
    )

    if any(
        card.priority == TodayPriority.CRITICAL.value
        for card in cards
    ):
        overall_state = "critical"
    elif action_required_count:
        overall_state = "focus"
    elif watch:
        overall_state = "watch"
    else:
        overall_state = "clear"

    header = TodayHeader(
        title="Today",
        subtitle=(
            "The owner's focused view of what matters "
            "right now across the Simplee ecosystem."
        ),
        focus_count=len(focus),
        watch_count=len(watch),
        target_count=len(targets),
        action_required_count=(
            action_required_count
        ),
        overall_state=overall_state,
        execution_performed=False,
    )

    return TodaySurface(
        header=header,
        focus=focus,
        watch=watch,
        targets=targets,
        all_cards=cards,
        boundary_notice=(
            "Today cards summarize owner priorities and "
            "navigation. Clouds does not execute the "
            "underlying operational action."
        ),
    )


def get_today_surface_payload() -> dict:
    return get_today_surface().to_dict()


def get_today_queue(
    *,
    kind: str | None = None,
    priority: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    action_required: bool | None = None,
) -> tuple[TodayCard, ...]:
    return filter_today_cards(
        get_today_cards(),
        kind=kind,
        priority=priority,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        action_required=action_required,
    )


def get_today_detail(
    card_id: str,
) -> TodayDetail:
    card = next(
        (
            item
            for item in get_today_cards()
            if item.card_id == card_id
        ),
        None,
    )

    if card is None:
        raise KeyError(
            f"Today card not found: {card_id}"
        )

    return TodayDetail(
        card=card,
        owner_questions=tuple(
            OWNER_QUESTIONS.get(
                card.kind,
                (),
            )
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
    )


def get_today_detail_payload(
    card_id: str,
) -> dict:
    return get_today_detail(
        card_id
    ).to_dict()


def get_clouds_gp005_status_payload() -> dict:
    surface = get_today_surface()

    return {
        "pack": "GP005",
        "section": (
            "OWNER COMMAND TODAY SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "focus_count": (
            surface.header.focus_count
        ),
        "watch_count": (
            surface.header.watch_count
        ),
        "target_count": (
            surface.header.target_count
        ),
        "action_required_count": (
            surface.header
            .action_required_count
        ),
        "source_integrity_verified": all(
            card.source_integrity_verified
            for card in surface.all_cards
        ),
        "tower_boundary_preserved": True,
        "today_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP006 — OWNER COMMAND PRIORITY BOARD"
        ),
    }
