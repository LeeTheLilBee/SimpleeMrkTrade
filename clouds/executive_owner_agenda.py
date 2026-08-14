"""
GP028 — Executive Owner Agenda / Time-Horizon Prioritization.

Advisory owner-attention scheduling for Clouds.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OwnerAgendaHorizon(str, Enum):
    DO_NOW = "do_now"
    TODAY = "today"
    THIS_WEEK = "this_week"
    WATCHING = "watching"
    WAITING = "waiting"
    CAN_WAIT = "can_wait"


class OwnerAgendaSourceKind(str, Enum):
    OPERATING_CHANGE = "operating_change"
    CROSS_BUSINESS_IMPACT = "cross_business_impact"


class OwnerAgendaUrgency(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    ROUTINE = "routine"
    CONTEXT = "context"


@dataclass(frozen=True)
class OwnerAgendaItem:
    agenda_item_id: str

    horizon: str
    urgency: str
    source_kind: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    title: str

    soulaana_what_happened: str
    soulaana_what_it_means: str
    soulaana_why_now: str
    soulaana_if_we_wait: str
    soulaana_next_review: str

    owner_attention_required: bool
    action_available: bool

    automatic_action_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "agenda_item_id": self.agenda_item_id,
            "horizon": self.horizon,
            "urgency": self.urgency,
            "source_kind": self.source_kind,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "impacted_source_id": (
                self.impacted_source_id
            ),
            "impacted_source_label": (
                self.impacted_source_label
            ),
            "title": self.title,
            "soulaana_what_happened": (
                self.soulaana_what_happened
            ),
            "soulaana_what_it_means": (
                self.soulaana_what_it_means
            ),
            "soulaana_why_now": (
                self.soulaana_why_now
            ),
            "soulaana_if_we_wait": (
                self.soulaana_if_we_wait
            ),
            "soulaana_next_review": (
                self.soulaana_next_review
            ),
            "owner_attention_required": (
                self.owner_attention_required
            ),
            "action_available": (
                self.action_available
            ),
            "automatic_action_performed": (
                self.automatic_action_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class OwnerAgendaSection:
    horizon: str
    label: str
    description: str

    items: tuple[
        OwnerAgendaItem,
        ...
    ]

    item_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "label": self.label,
            "description": self.description,
            "items": [
                item.to_dict()
                for item in self.items
            ],
            "item_count": self.item_count,
        }


@dataclass(frozen=True)
class ExecutiveOwnerAgenda:
    title: str

    sections: tuple[
        OwnerAgendaSection,
        ...
    ]

    items: tuple[
        OwnerAgendaItem,
        ...
    ]

    item_count: int
    owner_attention_count: int

    do_now_count: int
    today_count: int
    this_week_count: int
    watching_count: int
    waiting_count: int
    can_wait_count: int

    soulaana_owner_focus: str
    soulaana_attention_protection: str

    automatic_action_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "items": [
                item.to_dict()
                for item in self.items
            ],
            "item_count": self.item_count,
            "owner_attention_count": (
                self.owner_attention_count
            ),
            "do_now_count": self.do_now_count,
            "today_count": self.today_count,
            "this_week_count": (
                self.this_week_count
            ),
            "watching_count": (
                self.watching_count
            ),
            "waiting_count": (
                self.waiting_count
            ),
            "can_wait_count": (
                self.can_wait_count
            ),
            "soulaana_owner_focus": (
                self.soulaana_owner_focus
            ),
            "soulaana_attention_protection": (
                self.soulaana_attention_protection
            ),
            "automatic_action_performed": (
                self.automatic_action_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
