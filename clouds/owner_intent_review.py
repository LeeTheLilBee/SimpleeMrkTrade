"""
GP032 — Owner Intent Review / Handoff Authorization Preparation.

Reviews recorded owner intent before any authorization boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OwnerIntentReviewState(str, Enum):
    READY_FOR_HANDOFF_AUTHORIZATION_PREP = (
        "ready_for_handoff_authorization_prep"
    )
    BLOCKED = "blocked"


@dataclass(frozen=True)
class OwnerIntentReviewCheck:
    check_id: str
    label: str
    passed: bool
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OwnerIntentReview:
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

    checks: tuple[
        OwnerIntentReviewCheck,
        ...
    ]

    check_count: int
    passed_check_count: int
    failed_check_count: int

    review_state: str

    ready_for_handoff_authorization_prep: bool

    soulaana_review_summary: str
    soulaana_why_it_matters: str
    soulaana_blocker_summary: str
    soulaana_next_step: str

    handoff_authorized: bool
    handoff_delivered: bool

    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_review_id": self.intent_review_id,
            "choice_record_id": self.choice_record_id,
            "review_id": self.review_id,
            "packet_id": self.packet_id,
            "agenda_item_id": self.agenda_item_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
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
            "owning_application_id": (
                self.owning_application_id
            ),
            "owning_application_label": (
                self.owning_application_label
            ),
            "requires_tower_mediation": (
                self.requires_tower_mediation
            ),
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
            "review_state": self.review_state,
            "ready_for_handoff_authorization_prep": (
                self
                .ready_for_handoff_authorization_prep
            ),
            "soulaana_review_summary": (
                self.soulaana_review_summary
            ),
            "soulaana_why_it_matters": (
                self.soulaana_why_it_matters
            ),
            "soulaana_blocker_summary": (
                self.soulaana_blocker_summary
            ),
            "soulaana_next_step": (
                self.soulaana_next_step
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
        }


@dataclass(frozen=True)
class OwnerIntentReviewSurface:
    title: str

    reviews: tuple[
        OwnerIntentReview,
        ...
    ]

    review_count: int
    ready_count: int
    blocked_count: int

    handoff_authorized: bool
    handoff_delivered: bool

    approval_performed: bool
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
            "ready_count": self.ready_count,
            "blocked_count": self.blocked_count,
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
