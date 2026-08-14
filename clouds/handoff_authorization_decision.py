"""
GP033 — Handoff Authorization Decision / Owner Confirmation Boundary.

Records explicit owner authorization or decline.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class HandoffAuthorizationDecision(str, Enum):
    AUTHORIZE = "authorize"
    DECLINE = "decline"


class HandoffAuthorizationState(str, Enum):
    AUTHORIZED_FOR_PREPARATION = (
        "authorized_for_preparation"
    )
    DECLINED = "declined"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class HandoffAuthorizationRecord:
    authorization_record_id: str

    intent_review_id: str
    choice_record_id: str
    review_id: str
    packet_id: str
    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    selected_option_id: str
    selected_option_kind: str
    selected_option_label: str

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool

    owner_decision: str
    authorization_state: str

    owner_confirmation_recorded: bool
    handoff_authorized: bool
    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_decision_summary: str
    soulaana_what_this_means: str
    soulaana_what_did_not_happen: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class HandoffAuthorizationSurface:
    title: str

    records: tuple[
        HandoffAuthorizationRecord,
        ...
    ]

    record_count: int
    authorized_count: int
    declined_count: int
    blocked_count: int

    owner_confirmation_recorded: bool

    handoff_authorized: bool
    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "records": [
                item.to_dict()
                for item in self.records
            ],
            "record_count": self.record_count,
            "authorized_count": (
                self.authorized_count
            ),
            "declined_count": (
                self.declined_count
            ),
            "blocked_count": (
                self.blocked_count
            ),
            "owner_confirmation_recorded": (
                self.owner_confirmation_recorded
            ),
            "handoff_authorized": (
                self.handoff_authorized
            ),
            "handoff_delivered": (
                self.handoff_delivered
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "capital_movement_performed": (
                self.capital_movement_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
