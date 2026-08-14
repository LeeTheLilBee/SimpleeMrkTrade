"""
Service layer for the Clouds Owner Attention Command Surface.

It combines only local Clouds summary contracts.
"""

from __future__ import annotations

try:
    from .app_registry_surface_service import (
        get_app_registry_attention_queue,
    )
    from .contracts import (
        AttentionKind,
        AttentionPriority,
    )
    from .mission_lane_surface_service import (
        get_mission_lane_attention_queue,
    )
    from .owner_attention_surface import (
        AttentionCommandGroup,
        AttentionNavigationMode,
        AttentionSourceType,
        OwnerAttentionCommand,
        OwnerAttentionDetail,
        OwnerAttentionSummary,
        OwnerAttentionSurface,
        determine_command_group,
        determine_navigation_mode,
        filter_owner_attention,
        owner_attention_sort_key,
    )
    from .owner_command_service import (
        STARTER_ATTENTION,
    )
    from .registry import (
        get_app,
        get_mission_lane,
    )
except ImportError:
    from app_registry_surface_service import (
        get_app_registry_attention_queue,
    )
    from contracts import (
        AttentionKind,
        AttentionPriority,
    )
    from mission_lane_surface_service import (
        get_mission_lane_attention_queue,
    )
    from owner_attention_surface import (
        AttentionCommandGroup,
        AttentionNavigationMode,
        AttentionSourceType,
        OwnerAttentionCommand,
        OwnerAttentionDetail,
        OwnerAttentionSummary,
        OwnerAttentionSurface,
        determine_command_group,
        determine_navigation_mode,
        filter_owner_attention,
        owner_attention_sort_key,
    )
    from owner_command_service import (
        STARTER_ATTENTION,
    )
    from registry import (
        get_app,
        get_mission_lane,
    )


OWNER_QUESTIONS = {
    AttentionKind.REVIEW.value: (
        "What exactly should the owner review?",
        "Which source application or lane owns the detail?",
        "Is a direction required after review?",
    ),
    AttentionKind.DECISION.value: (
        "What decision is being requested?",
        "What information supports the decision?",
        "Which application will execute the approved direction?",
    ),
    AttentionKind.RISK.value: (
        "What risk requires owner awareness?",
        "What happens if the risk remains unresolved?",
        "Which application owns mitigation?",
    ),
    AttentionKind.BLOCKER.value: (
        "What is currently blocked?",
        "What owner action could remove the blocker?",
        "Which operating application owns the resolution?",
    ),
    AttentionKind.OPPORTUNITY.value: (
        "What opportunity is available?",
        "What timing or readiness matters?",
        "Which application owns the next step?",
    ),
    AttentionKind.INFORMATION.value: (
        "What should the owner know?",
        "Does this information require action now?",
        "Where can the owner review more detail?",
    ),
}


ALLOWED_CLOUDS_ACTIONS = (
    "Display the attention summary",
    "Show the source application and mission lane",
    "Prioritize the attention item",
    "Filter attention items",
    "Provide a safe navigation handoff",
    "Display owner review questions",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot approve the requested direction",
    "Clouds cannot execute the requested action",
    "Clouds cannot authenticate or authorize the owner",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _validate_source_links(
    *,
    source_app_id: str | None,
    source_lane_id: str | None,
) -> tuple[
    str | None,
    str | None,
    bool,
]:
    app_name = None
    lane_name = None
    verified = True

    if source_app_id is not None:
        app = get_app(
            source_app_id
        )

        if app is None:
            verified = False
        else:
            app_name = app.app_name

    if source_lane_id is not None:
        lane = get_mission_lane(
            source_lane_id
        )

        if lane is None:
            verified = False
        else:
            lane_name = lane.lane_name

            if (
                source_app_id is not None
                and lane.owning_app_id
                != source_app_id
            ):
                verified = False

    return (
        app_name,
        lane_name,
        verified,
    )


def _owner_record_commands() -> tuple[
    OwnerAttentionCommand,
    ...
]:
    commands = []

    for item in STARTER_ATTENTION:
        (
            app_name,
            lane_name,
            verified,
        ) = _validate_source_links(
            source_app_id=item.source_app_id,
            source_lane_id=item.source_lane_id,
        )

        group = determine_command_group(
            action_required=item.action_required
        )

        navigation_mode = (
            determine_navigation_mode(
                open_route=item.open_route,
                source_app_id=item.source_app_id,
            )
        )

        action_label = (
            "Review now"
            if item.action_required
            else "View information"
        )

        commands.append(
            OwnerAttentionCommand(
                attention_id=item.attention_id,
                title=item.title,
                summary=item.summary,
                source_type=(
                    AttentionSourceType
                    .OWNER_RECORD
                    .value
                ),
                source_app_id=item.source_app_id,
                source_app_name=app_name,
                source_lane_id=item.source_lane_id,
                source_lane_name=lane_name,
                kind=item.kind,
                priority=item.priority,
                command_group=group.value,
                action_required=(
                    item.action_required
                ),
                owner_action_label=action_label,
                open_route=item.open_route,
                navigation_mode=(
                    navigation_mode.value
                ),
                source_integrity_verified=verified,
                execution_performed=False,
            )
        )

    return tuple(commands)


def _application_commands() -> tuple[
    OwnerAttentionCommand,
    ...
]:
    commands = []

    explicit_app_ids = {
        item.source_app_id
        for item in STARTER_ATTENTION
        if item.source_app_id is not None
    }

    for card in get_app_registry_attention_queue():
        # Avoid duplicating an application already represented
        # by a richer explicit owner-attention record.
        if card.app_id in explicit_app_ids:
            continue

        action_required = (
            card.attention_count > 0
        )

        app = get_app(card.app_id)
        verified = app is not None

        commands.append(
            OwnerAttentionCommand(
                attention_id=(
                    "clouds-app-attention-"
                    f"{card.app_id}"
                ),
                title=(
                    f"{card.app_name} requires awareness"
                ),
                summary=card.status_summary,
                source_type=(
                    AttentionSourceType
                    .APPLICATION
                    .value
                ),
                source_app_id=card.app_id,
                source_app_name=card.app_name,
                source_lane_id=None,
                source_lane_name=None,
                kind=(
                    AttentionKind.REVIEW.value
                    if action_required
                    else AttentionKind
                    .INFORMATION
                    .value
                ),
                priority=(
                    AttentionPriority.HIGH.value
                    if action_required
                    else AttentionPriority
                    .ROUTINE
                    .value
                ),
                command_group=(
                    determine_command_group(
                        action_required=(
                            action_required
                        )
                    ).value
                ),
                action_required=action_required,
                owner_action_label=(
                    "Review application"
                    if action_required
                    else "View application"
                ),
                open_route=card.open_route,
                navigation_mode=(
                    determine_navigation_mode(
                        open_route=card.open_route,
                        source_app_id=card.app_id,
                    ).value
                ),
                source_integrity_verified=verified,
                execution_performed=False,
            )
        )

    return tuple(commands)


def _mission_lane_commands() -> tuple[
    OwnerAttentionCommand,
    ...
]:
    commands = []

    explicit_lane_ids = {
        item.source_lane_id
        for item in STARTER_ATTENTION
        if item.source_lane_id is not None
    }

    for card in get_mission_lane_attention_queue():
        # Avoid duplicating a lane already represented by
        # a richer explicit owner-attention record.
        if card.lane_id in explicit_lane_ids:
            continue

        (
            app_name,
            lane_name,
            verified,
        ) = _validate_source_links(
            source_app_id=card.owning_app_id,
            source_lane_id=card.lane_id,
        )

        action_required = (
            card.attention_count > 0
        )

        commands.append(
            OwnerAttentionCommand(
                attention_id=(
                    "clouds-lane-attention-"
                    f"{card.lane_id}"
                ),
                title=(
                    f"{card.lane_name} needs awareness"
                ),
                summary=card.status_summary,
                source_type=(
                    AttentionSourceType
                    .MISSION_LANE
                    .value
                ),
                source_app_id=card.owning_app_id,
                source_app_name=app_name,
                source_lane_id=card.lane_id,
                source_lane_name=lane_name,
                kind=(
                    AttentionKind.REVIEW.value
                    if action_required
                    else AttentionKind
                    .INFORMATION
                    .value
                ),
                priority=(
                    AttentionPriority.HIGH.value
                    if action_required
                    else AttentionPriority
                    .ROUTINE
                    .value
                ),
                command_group=(
                    determine_command_group(
                        action_required=(
                            action_required
                        )
                    ).value
                ),
                action_required=action_required,
                owner_action_label=(
                    "Review mission lane"
                    if action_required
                    else "View mission lane"
                ),
                open_route=card.open_route,
                navigation_mode=(
                    determine_navigation_mode(
                        open_route=card.open_route,
                        source_app_id=(
                            card.owning_app_id
                        ),
                    ).value
                ),
                source_integrity_verified=verified,
                execution_performed=False,
            )
        )

    return tuple(commands)


def get_owner_attention_commands() -> tuple[
    OwnerAttentionCommand,
    ...
]:
    commands = (
        *_owner_record_commands(),
        *_application_commands(),
        *_mission_lane_commands(),
    )

    identifiers = [
        item.attention_id
        for item in commands
    ]

    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError(
            "Duplicate owner attention IDs detected."
        )

    return tuple(
        sorted(
            commands,
            key=owner_attention_sort_key,
        )
    )


def get_owner_attention_surface() -> OwnerAttentionSurface:
    commands = get_owner_attention_commands()

    action_required = tuple(
        item
        for item in commands
        if item.action_required
    )

    informational = tuple(
        item
        for item in commands
        if not item.action_required
    )

    summary = OwnerAttentionSummary(
        total_attention_count=len(commands),
        action_required_count=len(
            action_required
        ),
        informational_count=len(
            informational
        ),
        critical_count=sum(
            item.priority
            == AttentionPriority.CRITICAL.value
            for item in commands
        ),
        high_count=sum(
            item.priority
            == AttentionPriority.HIGH.value
            for item in commands
        ),
        elevated_count=sum(
            item.priority
            == AttentionPriority.ELEVATED.value
            for item in commands
        ),
        routine_count=sum(
            item.priority
            == AttentionPriority.ROUTINE.value
            for item in commands
        ),
        application_source_count=sum(
            item.source_type
            == AttentionSourceType.APPLICATION.value
            for item in commands
        ),
        mission_lane_source_count=sum(
            item.source_type
            == AttentionSourceType.MISSION_LANE.value
            for item in commands
        ),
        owner_record_source_count=sum(
            item.source_type
            == AttentionSourceType.OWNER_RECORD.value
            for item in commands
        ),
        source_integrity_verified=all(
            item.source_integrity_verified
            for item in commands
        ),
        execution_performed=False,
    )

    return OwnerAttentionSurface(
        title="Owner Attention",
        subtitle=(
            "One prioritized view of what requires owner "
            "review, awareness, or navigation across the "
            "Simplee ecosystem."
        ),
        summary=summary,
        action_required=action_required,
        informational=informational,
        all_attention=commands,
        boundary_notice=(
            "Attention items identify what needs owner "
            "awareness. Clouds does not approve or execute "
            "the underlying operational action."
        ),
    )


def get_owner_attention_surface_payload() -> dict:
    return get_owner_attention_surface().to_dict()


def get_owner_attention_queue(
    *,
    priority: str | None = None,
    kind: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    action_required: bool | None = None,
    source_type: str | None = None,
) -> tuple[OwnerAttentionCommand, ...]:
    return filter_owner_attention(
        get_owner_attention_commands(),
        priority=priority,
        kind=kind,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        action_required=action_required,
        source_type=source_type,
    )


def get_owner_attention_detail(
    attention_id: str,
) -> OwnerAttentionDetail:
    command = next(
        (
            item
            for item
            in get_owner_attention_commands()
            if item.attention_id == attention_id
        ),
        None,
    )

    if command is None:
        raise KeyError(
            f"Owner attention item not found: "
            f"{attention_id}"
        )

    authority_boundary = None

    if command.source_app_id is not None:
        app = get_app(
            command.source_app_id
        )

        if app is None:
            raise RuntimeError(
                "Attention source app disappeared "
                "after integrity verification."
            )

        authority_boundary = (
            app.authority_boundary
        )

    return OwnerAttentionDetail(
        command=command,
        owner_questions=tuple(
            OWNER_QUESTIONS.get(
                command.kind,
                (),
            )
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        owning_app_authority_boundary=(
            authority_boundary
        ),
        downstream_execution_performed=False,
    )


def get_owner_attention_detail_payload(
    attention_id: str,
) -> dict:
    return get_owner_attention_detail(
        attention_id
    ).to_dict()


def get_clouds_gp004_status_payload() -> dict:
    surface = get_owner_attention_surface()

    return {
        "pack": "GP004",
        "section": (
            "OWNER ATTENTION COMMAND SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "total_attention_count": (
            surface.summary.total_attention_count
        ),
        "action_required_count": (
            surface.summary.action_required_count
        ),
        "informational_count": (
            surface.summary.informational_count
        ),
        "source_integrity_verified": (
            surface.summary
            .source_integrity_verified
        ),
        "tower_boundary_preserved": True,
        "attention_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP005 — OWNER COMMAND TODAY SURFACE"
        ),
    }
