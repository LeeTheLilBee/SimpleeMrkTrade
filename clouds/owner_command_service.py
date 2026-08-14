"""
The Clouds — owner command foundation service.

GP001 uses local deterministic starter summaries.

Future app integrations must provide compact summary contracts.
Clouds must not crawl another application's full service graph.
"""

from __future__ import annotations

try:
    from .contracts import (
        AppConnectionState,
        AppStatus,
        AttentionKind,
        AttentionPriority,
        HealthState,
        MissionLaneStatus,
        OwnerAttentionItem,
        OwnerCommandDashboard,
        OwnerCommandSummary,
        ReadinessState,
    )
    from .registry import (
        list_apps,
        list_mission_lanes,
    )
except ImportError:
    from contracts import (
        AppConnectionState,
        AppStatus,
        AttentionKind,
        AttentionPriority,
        HealthState,
        MissionLaneStatus,
        OwnerAttentionItem,
        OwnerCommandDashboard,
        OwnerCommandSummary,
        ReadinessState,
    )
    from registry import (
        list_apps,
        list_mission_lanes,
    )


CLOUDS_BOUNDARIES = (
    "Clouds does not authenticate users.",
    "Clouds does not grant permissions.",
    "Clouds does not perform step-up.",
    "Clouds does not execute trades.",
    "Clouds does not move money.",
    "Clouds does not retrieve raw Vault documents.",
    "Clouds does not operate properties.",
    "Clouds navigates the owner to the correct operating app.",
)


STARTER_APP_STATUS = {
    "tower": AppStatus(
        app_id="tower",
        health=HealthState.HEALTHY.value,
        readiness=ReadinessState.BUILDING.value,
        summary=(
            "Tower front-door and Observatory launch "
            "corridors are established."
        ),
        attention_count=0,
        open_route="/tower",
    ),
    "observatory": AppStatus(
        app_id="observatory",
        health=HealthState.WATCH.value,
        readiness=ReadinessState.BUILDING.value,
        summary=(
            "Observatory remains in controlled owner build "
            "and beta-readiness work."
        ),
        attention_count=1,
        open_route="/tower/observatory",
    ),
    "archive_vault": AppStatus(
        app_id="archive_vault",
        health=HealthState.HEALTHY.value,
        readiness=ReadinessState.BUILDING.value,
        summary=(
            "Archive Vault remains sealed and under active "
            "readiness construction."
        ),
        attention_count=0,
        open_route="/tower/vault",
    ),
    "teller": AppStatus(
        app_id="teller",
        health=HealthState.UNKNOWN.value,
        readiness=ReadinessState.HELD.value,
        summary=(
            "Teller requires a future alignment pass."
        ),
        attention_count=0,
        open_route="/tower/teller",
    ),
    "grounds": AppStatus(
        app_id="grounds",
        health=HealthState.UNKNOWN.value,
        readiness=ReadinessState.NOT_STARTED.value,
        summary=(
            "Grounds is reserved for a future focused build."
        ),
        attention_count=0,
        open_route="/tower/grounds",
    ),
    "clouds": AppStatus(
        app_id="clouds",
        health=HealthState.HEALTHY.value,
        readiness=ReadinessState.FOUNDATION.value,
        summary=(
            "Clean owner command rebuild foundation is active."
        ),
        attention_count=0,
        open_route="/clouds",
    ),
}


STARTER_LANE_STATUS = {
    "owner_command": MissionLaneStatus(
        lane_id="owner_command",
        health=HealthState.HEALTHY.value,
        readiness=ReadinessState.FOUNDATION.value,
        summary=(
            "Owner command foundation is active."
        ),
        attention_count=0,
    ),
    "investment_engine": MissionLaneStatus(
        lane_id="investment_engine",
        health=HealthState.WATCH.value,
        readiness=ReadinessState.BUILDING.value,
        summary=(
            "Investment engine remains in controlled "
            "build and readiness work."
        ),
        attention_count=1,
    ),
    "trust_stewardship": MissionLaneStatus(
        lane_id="trust_stewardship",
        health=HealthState.HEALTHY.value,
        readiness=ReadinessState.BUILDING.value,
        summary=(
            "Trust records remain under sealed Vault "
            "stewardship."
        ),
        attention_count=0,
    ),
    "atm_operations": MissionLaneStatus(
        lane_id="atm_operations",
        health=HealthState.WATCH.value,
        readiness=ReadinessState.FOUNDATION.value,
        summary=(
            "ATM operations remain planned and not yet "
            "operationally connected."
        ),
        attention_count=1,
    ),
    "real_estate": MissionLaneStatus(
        lane_id="real_estate",
        health=HealthState.UNKNOWN.value,
        readiness=ReadinessState.NOT_STARTED.value,
        summary=(
            "Office and property acquisition lane is reserved."
        ),
        attention_count=0,
    ),
    "people_and_payments": MissionLaneStatus(
        lane_id="people_and_payments",
        health=HealthState.UNKNOWN.value,
        readiness=ReadinessState.HELD.value,
        summary=(
            "People and payment workflows await Teller "
            "alignment."
        ),
        attention_count=0,
    ),
}


STARTER_ATTENTION = (
    OwnerAttentionItem(
        attention_id="clouds-attention-ob-readiness",
        title="Observatory readiness remains active",
        summary=(
            "Continue controlled Tower and Observatory "
            "readiness work before broader activation."
        ),
        kind=AttentionKind.REVIEW.value,
        priority=AttentionPriority.HIGH.value,
        source_app_id="observatory",
        source_lane_id="investment_engine",
        open_route="/tower/observatory",
        action_required=True,
    ),
    OwnerAttentionItem(
        attention_id="clouds-attention-atm-planning",
        title="ATM operating lane needs future preparation",
        summary=(
            "ATM route acquisition and operating readiness "
            "remain planned but not connected."
        ),
        kind=AttentionKind.INFORMATION.value,
        priority=AttentionPriority.ELEVATED.value,
        source_app_id="teller",
        source_lane_id="atm_operations",
        open_route="/tower/teller",
        action_required=False,
    ),
)


def get_owner_command_dashboard() -> OwnerCommandDashboard:
    apps = list_apps()
    lanes = list_mission_lanes()

    app_statuses = tuple(
        STARTER_APP_STATUS[app.app_id]
        for app in apps
    )

    lane_statuses = tuple(
        STARTER_LANE_STATUS[lane.lane_id]
        for lane in lanes
    )

    owner_attention = tuple(
        sorted(
            STARTER_ATTENTION,
            key=lambda item: (
                {
                    "critical": 1,
                    "high": 2,
                    "elevated": 3,
                    "routine": 4,
                }[item.priority],
                item.attention_id,
            ),
        )
    )

    active_app_count = sum(
        app.connection_state
        != AppConnectionState.RESERVED.value
        for app in apps
    )

    reserved_app_count = sum(
        app.connection_state
        == AppConnectionState.RESERVED.value
        for app in apps
    )

    active_lane_count = sum(
        lane.active
        for lane in lanes
    )

    critical_count = sum(
        item.priority
        == AttentionPriority.CRITICAL.value
        for item in owner_attention
    )

    high_count = sum(
        item.priority
        == AttentionPriority.HIGH.value
        for item in owner_attention
    )

    if critical_count:
        overall_health = HealthState.ATTENTION.value
    elif high_count:
        overall_health = HealthState.WATCH.value
    else:
        overall_health = HealthState.HEALTHY.value

    summary = OwnerCommandSummary(
        title="The Clouds",
        subtitle=(
            "Universal owner command across the Simplee "
            "ecosystem."
        ),
        active_app_count=active_app_count,
        reserved_app_count=reserved_app_count,
        active_lane_count=active_lane_count,
        owner_attention_count=len(owner_attention),
        critical_attention_count=critical_count,
        high_attention_count=high_count,
        overall_health=overall_health,
        execution_performed=False,
    )

    return OwnerCommandDashboard(
        summary=summary,
        apps=apps,
        app_statuses=app_statuses,
        mission_lanes=lanes,
        mission_lane_statuses=lane_statuses,
        owner_attention=owner_attention,
        boundaries=CLOUDS_BOUNDARIES,
    )


def get_owner_command_payload() -> dict:
    return get_owner_command_dashboard().to_dict()


def get_clouds_gp001_status_payload() -> dict:
    payload = get_owner_command_payload()

    return {
        "pack": "GP001",
        "section": "CLEAN OWNER COMMAND FOUNDATION",
        "status": "ready",
        "safe_to_continue": True,
        "owner_command_summary": payload["summary"],
        "app_count": len(payload["apps"]),
        "mission_lane_count": len(
            payload["mission_lanes"]
        ),
        "attention_count": len(
            payload["owner_attention"]
        ),
        "direct_operational_execution": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP002 — OWNER COMMAND APP REGISTRY SURFACE"
        ),
    }
