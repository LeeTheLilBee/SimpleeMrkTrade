"""
The Clouds.

Clean owner command rebuild.
"""

from .contracts import (
    AppConnectionState,
    AppDefinition,
    AppStatus,
    AttentionKind,
    AttentionPriority,
    HealthState,
    MissionLaneDefinition,
    MissionLaneStatus,
    OwnerAttentionItem,
    OwnerCommandDashboard,
    OwnerCommandSummary,
    ReadinessState,
)

from .registry import (
    get_app,
    get_mission_lane,
    list_apps,
    list_mission_lanes,
)

from .owner_command_service import (
    get_clouds_gp001_status_payload,
    get_owner_command_dashboard,
    get_owner_command_payload,
)

__all__ = [
    "AppConnectionState",
    "AppDefinition",
    "AppStatus",
    "AttentionKind",
    "AttentionPriority",
    "HealthState",
    "MissionLaneDefinition",
    "MissionLaneStatus",
    "OwnerAttentionItem",
    "OwnerCommandDashboard",
    "OwnerCommandSummary",
    "ReadinessState",
    "get_app",
    "get_mission_lane",
    "list_apps",
    "list_mission_lanes",
    "get_clouds_gp001_status_payload",
    "get_owner_command_dashboard",
    "get_owner_command_payload",
]


# ============================================================
# CLOUDS CLEAN REBUILD GP002
# OWNER COMMAND APP REGISTRY SURFACE
# ============================================================

from .app_registry_surface import (
    AppOpenMode,
    AppRegistryAttentionState,
    AppRegistryCard,
    AppRegistryDetail,
    AppRegistryGroup,
    AppRegistrySummary,
    AppRegistrySurface,
    build_app_registry_card,
    filter_registry_cards,
)

from .app_registry_surface_service import (
    get_app_registry_attention_queue,
    get_app_registry_cards,
    get_app_registry_detail,
    get_app_registry_detail_payload,
    get_app_registry_surface,
    get_app_registry_surface_payload,
    get_clouds_gp002_status_payload,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP003
# OWNER COMMAND MISSION LANE SURFACE
# ============================================================

from .mission_lane_surface import (
    MissionLaneAttentionState,
    MissionLaneCard,
    MissionLaneDetail,
    MissionLaneGroup,
    MissionLaneOpenMode,
    MissionLaneSummary,
    MissionLaneSurface,
    build_mission_lane_card,
    filter_mission_lane_cards,
)

from .mission_lane_surface_service import (
    get_clouds_gp003_status_payload,
    get_mission_lane_attention_queue,
    get_mission_lane_cards,
    get_mission_lane_detail,
    get_mission_lane_detail_payload,
    get_mission_lane_surface,
    get_mission_lane_surface_payload,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP004
# OWNER ATTENTION COMMAND SURFACE
# ============================================================

from .owner_attention_surface import (
    AttentionCommandGroup,
    AttentionNavigationMode,
    AttentionSourceType,
    OwnerAttentionCommand,
    OwnerAttentionDetail,
    OwnerAttentionSummary,
    OwnerAttentionSurface,
    filter_owner_attention,
    owner_attention_sort_key,
)

from .owner_attention_surface_service import (
    get_clouds_gp004_status_payload,
    get_owner_attention_commands,
    get_owner_attention_detail,
    get_owner_attention_detail_payload,
    get_owner_attention_queue,
    get_owner_attention_surface,
    get_owner_attention_surface_payload,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP005
# OWNER COMMAND TODAY SURFACE
# ============================================================

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

from .today_surface_service import (
    get_clouds_gp005_status_payload,
    get_today_cards,
    get_today_detail,
    get_today_detail_payload,
    get_today_queue,
    get_today_surface,
    get_today_surface_payload,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP006
# OWNER COMMAND PRIORITY BOARD
# ============================================================

from .priority_board import (
    EffortLevel,
    ImpactLevel,
    PriorityBoard,
    PriorityCard,
    PriorityCategory,
    PriorityDetail,
    PriorityNavigationMode,
    PriorityState,
    PrioritySummary,
    StrategicPriority,
    calculate_priority_score,
    filter_priority_cards,
    priority_sort_key,
)

from .priority_board_service import (
    get_clouds_gp006_status_payload,
    get_priority_board,
    get_priority_board_payload,
    get_priority_card,
    get_priority_cards,
    get_priority_detail,
    get_priority_detail_payload,
    get_priority_queue,
    get_priority_summary,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP007
# EXECUTIVE OWNER DASHBOARD SURFACE
# ============================================================

from .executive_dashboard import (
    ExecutiveCardPriority,
    ExecutiveDashboard,
    ExecutiveDashboardCard,
    ExecutiveDashboardDetail,
    ExecutiveDashboardSummary,
    ExecutiveHealth,
    ExecutiveHealthSummary,
    ExecutiveNavigationMode,
    ExecutiveRecommendation,
    ExecutiveRecommendationKind,
    ExecutiveSection,
    calculate_readiness_score,
    determine_executive_health,
    determine_readiness_state,
    executive_card_sort_key,
    filter_executive_cards,
)

from .executive_dashboard_service import (
    get_clouds_gp007_status_payload,
    get_executive_dashboard,
    get_executive_dashboard_card,
    get_executive_dashboard_cards,
    get_executive_dashboard_detail,
    get_executive_dashboard_detail_payload,
    get_executive_dashboard_health,
    get_executive_dashboard_payload,
    get_executive_dashboard_summary,
    get_executive_recommendations,
)
