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


# ============================================================
# CLOUDS CLEAN REBUILD GP008
# EXECUTIVE DASHBOARD SECTION DETAIL SURFACE
# ============================================================

from .executive_dashboard_detail import (
    ExecutiveDashboardSectionDetail,
    ExecutiveDashboardSectionSummary,
    ExecutiveDashboardSectionSurface,
    ExecutiveSectionHealth,
    ExecutiveSectionId,
    ExecutiveSectionMetric,
    ExecutiveSectionMetricKind,
    ExecutiveSectionNavigationMode,
    ExecutiveSectionNavigationTarget,
    ExecutiveSectionReadiness,
    ExecutiveSectionRecommendation,
    ExecutiveSectionRecommendationKind,
    filter_section_details,
    metric_sort_key,
    navigation_target_sort_key,
    recommendation_sort_key,
    section_sort_key,
)

from .executive_dashboard_detail_service import (
    filter_executive_dashboard_sections,
    get_clouds_gp008_status_payload,
    get_executive_dashboard_section,
    get_executive_dashboard_section_detail,
    get_executive_dashboard_section_detail_payload,
    get_executive_dashboard_section_surface,
    get_executive_dashboard_section_surface_payload,
    get_executive_dashboard_sections,
    get_executive_section_metrics,
    get_executive_section_navigation_targets,
    get_executive_section_recommendations,
    get_executive_section_summary,
)


# ============================================================
# CLOUDS CLEAN REBUILD GP009
# EXECUTIVE DASHBOARD NAVIGATION MAP
# ============================================================

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

from .executive_navigation_map_service import (
    filter_executive_navigation_destinations,
    get_clouds_gp009_status_payload,
    get_executive_navigation_destination,
    get_executive_navigation_destination_payload,
    get_executive_navigation_destinations,
    get_executive_navigation_map,
    get_executive_navigation_map_payload,
    get_executive_navigation_map_summary,
    get_executive_navigation_section,
    get_executive_navigation_section_payload,
    get_executive_navigation_sections,
)

# ============================================================
# CLOUDS CLEAN REBUILD GP010
# EXECUTIVE OWNER COMMAND WORKSPACE SURFACE
# ============================================================

from .executive_owner_workspace import (
    ExecutiveOwnerWorkspace,
    WorkspaceHeadline,
    WorkspaceHealth,
    WorkspaceItem,
    WorkspaceItemKind,
    WorkspaceNavigationAction,
    WorkspaceNavigationMode,
    WorkspacePanel,
    WorkspacePanelKind,
    WorkspacePriority,
    WorkspaceSummary,
    filter_workspace_items,
    workspace_item_sort_key,
    workspace_panel_sort_key,
)

from .executive_owner_workspace_service import (
    filter_executive_owner_workspace_items,
    get_clouds_gp010_status_payload,
    get_executive_owner_workspace,
    get_executive_owner_workspace_item,
    get_executive_owner_workspace_item_payload,
    get_executive_owner_workspace_items,
    get_executive_owner_workspace_panel,
    get_executive_owner_workspace_panel_payload,
    get_executive_owner_workspace_panels,
    get_executive_owner_workspace_payload,
    get_executive_owner_workspace_summary,
)

# ============================================================
# CLOUDS CLEAN REBUILD GP011
# EXECUTIVE OWNER WORKSPACE DETAIL / ACTION INTENT SURFACE
# ============================================================

from .executive_owner_workspace_detail import (
    ExecutiveOwnerWorkspaceDetail,
    ExecutiveOwnerWorkspaceDetailSurface,
    OwnerActionBlocker,
    OwnerActionIntent,
    OwnerActionIntentAuthority,
    OwnerActionIntentKind,
    OwnerActionIntentRisk,
    OwnerActionIntentState,
    OwnerActionPrerequisite,
    blocker_sort_key,
    filter_workspace_details,
    prerequisite_sort_key,
)

from .executive_owner_workspace_detail_service import (
    filter_executive_owner_workspace_details,
    get_clouds_gp011_status_payload,
    get_executive_owner_workspace_detail,
    get_executive_owner_workspace_detail_payload,
    get_executive_owner_workspace_detail_surface,
    get_executive_owner_workspace_detail_surface_payload,
    get_executive_owner_workspace_details,
)

# ============================================================
# CLOUDS CLEAN REBUILD GP012
# EXECUTIVE OWNER ACTION INTENT REVIEW / HANDOFF PREPARATION SURFACE
# ============================================================

from .executive_owner_action_intent_review import (
    HandoffPreparation,
    HandoffPreparationState,
    IntentReviewAuthority,
    IntentReviewDecision,
    IntentReviewState,
    OwnerIntentReviewPacket,
    OwnerIntentReviewSurface,
    ReviewBlocker,
    ReviewRequirement,
    filter_review_packets,
    requirement_sort_key,
    review_blocker_sort_key,
    review_packet_sort_key,
)

from .executive_owner_action_intent_review_service import (
    filter_owner_intent_review_packets,
    get_clouds_gp012_status_payload,
    get_owner_intent_review_packet,
    get_owner_intent_review_packet_payload,
    get_owner_intent_review_packets,
    get_owner_intent_review_surface,
    get_owner_intent_review_surface_payload,
)

# ============================================================
# CLOUDS CLEAN REBUILD GP013
# EXECUTIVE OWNER HANDOFF REQUEST DRAFT / TOWER DELIVERY ENVELOPE SURFACE
# ============================================================

from .executive_owner_handoff_request_draft import (
    DeliveryEnvelopeState,
    HandoffDraftDecision,
    HandoffDraftState,
    HandoffDraftSurface,
    HandoffRequestDraft,
    TowerDeliveryEnvelope,
)

from .executive_owner_handoff_request_draft_service import (
    get_clouds_gp013_status_payload,
    get_handoff_draft_surface,
    get_handoff_draft_surface_payload,
    get_handoff_request_draft,
    get_handoff_request_draft_by_item,
    get_handoff_request_draft_payload,
    get_handoff_request_drafts,
    get_tower_delivery_envelope,
    get_tower_delivery_envelope_by_draft,
    get_tower_delivery_envelope_payload,
    get_tower_delivery_envelopes,
)

# ============================================================
# CLOUDS CLEAN REBUILD GP014
# EXECUTIVE OWNER HANDOFF REQUEST OWNER DECISION / SUBMISSION AUTHORIZATION SURFACE
# ============================================================

from .executive_owner_handoff_submission_authorization import (
    OwnerHandoffAuthorizationSurface,
    OwnerHandoffDecision,
    OwnerHandoffDecisionRecord,
    OwnerReviewConfirmationState,
    SubmissionAuthorizationRecord,
    SubmissionAuthorizationState,
    filter_authorizations,
)

from .executive_owner_handoff_submission_authorization_service import (
    filter_submission_authorizations,
    get_clouds_gp014_status_payload,
    get_owner_handoff_authorization_surface,
    get_owner_handoff_authorization_surface_payload,
    get_owner_handoff_decision,
    get_owner_handoff_decision_by_draft,
    get_owner_handoff_decisions,
    get_submission_authorization,
    get_submission_authorization_by_draft,
    get_submission_authorizations,
)
