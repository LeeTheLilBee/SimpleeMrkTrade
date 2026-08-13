"""
GP031 — Owner Decision Choice / Intent Recording Boundary.

Records explicit owner intent only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OwnerChoiceState(str, Enum):
    PENDING = "pending"
    RECORDED = "recorded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class OwnerChoiceRecord:
    choice_record_id: str

    review_id: str
    packet_id: str
    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    selected_option_id: str | None
    selected_option_kind: str | None
    selected_option_label: str | None

    owner_intent: str | None

    choice_state: str

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool

    owner_choice_recorded: bool

    approval_performed: bool
    automatic_decision_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_choice_summary: str
    soulaana_what_this_means: str
    soulaana_what_did_not_happen: str
    soulaana_next_step: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "choice_record_id": (
                self.choice_record_id
            ),
            "review_id": self.review_id,
            "packet_id": self.packet_id,
            "agenda_item_id": (
                self.agenda_item_id
            ),
            "source_id": self.source_id,
            "source_label": (
                self.source_label
            ),
            "impacted_source_id": (
                self.impacted_source_id
            ),
            "impacted_source_label": (
                self.impacted_source_label
            ),
            "selected_option_id": (
                self.selected_option_id
            ),
            "selected_option_kind": (
                self.selected_option_kind
            ),
            "selected_option_label": (
                self.selected_option_label
            ),
            "owner_intent": (
                self.owner_intent
            ),
            "choice_state": (
                self.choice_state
            ),
            "owning_application_id": (
                self.owning_application_id
            ),
            "owning_application_label": (
                self.owning_application_label
            ),
            "requires_tower_mediation": (
                self.requires_tower_mediation
            ),
            "owner_choice_recorded": (
                self.owner_choice_recorded
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
            ),
            "capital_movement_performed": (
                self.capital_movement_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "soulaana_choice_summary": (
                self.soulaana_choice_summary
            ),
            "soulaana_what_this_means": (
                self.soulaana_what_this_means
            ),
            "soulaana_what_did_not_happen": (
                self.soulaana_what_did_not_happen
            ),
            "soulaana_next_step": (
                self.soulaana_next_step
            ),
        }


@dataclass(frozen=True)
class OwnerChoiceSurface:
    title: str

    records: tuple[
        OwnerChoiceRecord,
        ...
    ]

    record_count: int
    recorded_count: int
    pending_count: int
    blocked_count: int

    owner_choice_recorded: bool

    approval_performed: bool
    automatic_decision_performed: bool
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
            "record_count": (
                self.record_count
            ),
            "recorded_count": (
                self.recorded_count
            ),
            "pending_count": (
                self.pending_count
            ),
            "blocked_count": (
                self.blocked_count
            ),
            "owner_choice_recorded": (
                self.owner_choice_recorded
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
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
