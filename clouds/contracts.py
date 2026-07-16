"""
The Clouds — clean owner command contracts.

These contracts are local, deterministic, and JSON-ready.

They do not import or call operational applications.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AppConnectionState(str, Enum):
    RESERVED = "reserved"
    SUMMARY_READY = "summary_ready"
    CONNECTED = "connected"


class HealthState(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class ReadinessState(str, Enum):
    NOT_STARTED = "not_started"
    FOUNDATION = "foundation"
    BUILDING = "building"
    READY_FOR_REVIEW = "ready_for_review"
    READY = "ready"
    HELD = "held"


class AttentionPriority(str, Enum):
    ROUTINE = "routine"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class AttentionKind(str, Enum):
    REVIEW = "review"
    DECISION = "decision"
    RISK = "risk"
    BLOCKER = "blocker"
    OPPORTUNITY = "opportunity"
    INFORMATION = "information"


@dataclass(frozen=True)
class AppDefinition:
    app_id: str
    app_name: str
    purpose: str
    owner_surface_route: str
    authority_boundary: str
    connection_state: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "purpose": self.purpose,
            "owner_surface_route": (
                self.owner_surface_route
            ),
            "authority_boundary": (
                self.authority_boundary
            ),
            "connection_state": (
                self.connection_state
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class MissionLaneDefinition:
    lane_id: str
    lane_name: str
    business_name: str
    owning_app_id: str
    purpose: str
    active: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id,
            "lane_name": self.lane_name,
            "business_name": self.business_name,
            "owning_app_id": self.owning_app_id,
            "purpose": self.purpose,
            "active": self.active,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class AppStatus:
    app_id: str
    health: str
    readiness: str
    summary: str
    attention_count: int
    open_route: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "health": self.health,
            "readiness": self.readiness,
            "summary": self.summary,
            "attention_count": self.attention_count,
            "open_route": self.open_route,
        }


@dataclass(frozen=True)
class MissionLaneStatus:
    lane_id: str
    health: str
    readiness: str
    summary: str
    attention_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id,
            "health": self.health,
            "readiness": self.readiness,
            "summary": self.summary,
            "attention_count": self.attention_count,
        }


@dataclass(frozen=True)
class OwnerAttentionItem:
    attention_id: str
    title: str
    summary: str
    kind: str
    priority: str
    source_app_id: str | None
    source_lane_id: str | None
    open_route: str | None
    action_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "attention_id": self.attention_id,
            "title": self.title,
            "summary": self.summary,
            "kind": self.kind,
            "priority": self.priority,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "open_route": self.open_route,
            "action_required": self.action_required,
        }


@dataclass(frozen=True)
class OwnerCommandSummary:
    title: str
    subtitle: str
    active_app_count: int
    reserved_app_count: int
    active_lane_count: int
    owner_attention_count: int
    critical_attention_count: int
    high_attention_count: int
    overall_health: str
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "active_app_count": self.active_app_count,
            "reserved_app_count": self.reserved_app_count,
            "active_lane_count": self.active_lane_count,
            "owner_attention_count": (
                self.owner_attention_count
            ),
            "critical_attention_count": (
                self.critical_attention_count
            ),
            "high_attention_count": (
                self.high_attention_count
            ),
            "overall_health": self.overall_health,
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class OwnerCommandDashboard:
    summary: OwnerCommandSummary
    apps: tuple[AppDefinition, ...]
    app_statuses: tuple[AppStatus, ...]
    mission_lanes: tuple[MissionLaneDefinition, ...]
    mission_lane_statuses: tuple[MissionLaneStatus, ...]
    owner_attention: tuple[OwnerAttentionItem, ...]
    boundaries: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "apps": [
                item.to_dict()
                for item in self.apps
            ],
            "app_statuses": [
                item.to_dict()
                for item in self.app_statuses
            ],
            "mission_lanes": [
                item.to_dict()
                for item in self.mission_lanes
            ],
            "mission_lane_statuses": [
                item.to_dict()
                for item in self.mission_lane_statuses
            ],
            "owner_attention": [
                item.to_dict()
                for item in self.owner_attention
            ],
            "boundaries": list(self.boundaries),
        }
