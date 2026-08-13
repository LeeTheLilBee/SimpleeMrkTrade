"""
GP030 — Owner Decision Review / Readiness Gate.

Reviews prepared owner decision packets.
No owner decision is recorded here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DecisionReviewState(str, Enum):
    READY_FOR_OWNER_CHOICE = "ready_for_owner_choice"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class DecisionReviewCheck:
    check_id: str
    label: str
    passed: bool
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OwnerDecisionReview:
    review_id: str
    packet_id: str
    agenda_item_id: str

    source_id: str
    source_label: str

    review_state: str

    checks: tuple[
        DecisionReviewCheck,
        ...
    ]

    check_count: int
    passed_check_count: int
    failed_check_count: int

    owner_ready_to_choose: bool

    soulaana_readiness_summary: str
    soulaana_blocker_summary: str
    soulaana_next_step: str

    automatic_decision_performed: bool
    approval_performed: bool
    owner_choice_recorded: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "packet_id": self.packet_id,
            "agenda_item_id": self.agenda_item_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "review_state": self.review_state,
            "checks": [
                item.to_dict()
                for item in self.checks
            ],
            "check_count": self.check_count,
            "passed_check_count": (
                self.passed_check_count
            ),
            "failed_check_count": (
                self.failed_check_count
            ),
            "owner_ready_to_choose": (
                self.owner_ready_to_choose
            ),
            "soulaana_readiness_summary": (
                self.soulaana_readiness_summary
            ),
            "soulaana_blocker_summary": (
                self.soulaana_blocker_summary
            ),
            "soulaana_next_step": (
                self.soulaana_next_step
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "owner_choice_recorded": (
                self.owner_choice_recorded
            ),
            "capital_movement_performed": (
                self.capital_movement_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class OwnerDecisionReviewSurface:
    title: str

    reviews: tuple[
        OwnerDecisionReview,
        ...
    ]

    review_count: int
    ready_review_count: int
    blocked_review_count: int

    automatic_decision_performed: bool
    approval_performed: bool
    owner_choice_recorded: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "reviews": [
                item.to_dict()
                for item in self.reviews
            ],
            "review_count": self.review_count,
            "ready_review_count": (
                self.ready_review_count
            ),
            "blocked_review_count": (
                self.blocked_review_count
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "owner_choice_recorded": (
                self.owner_choice_recorded
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
