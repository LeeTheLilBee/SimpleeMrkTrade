"""
GP029 — Owner Decision Prep / Decision Packet Surface.

Decision preparation only.
No owner decision or downstream execution occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DecisionPacketState(str, Enum):
    READY_FOR_OWNER_REVIEW = "ready_for_owner_review"
    BLOCKED = "blocked"


class DecisionOptionKind(str, Enum):
    REVIEW_NOW = "review_now"
    DEFER = "defer"
    HOLD = "hold"
    ESCALATE_TO_SOURCE = "escalate_to_source"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class DecisionOption:
    option_id: str
    label: str
    kind: str

    explanation: str
    expected_benefit: str
    expected_cost_or_risk: str
    what_happens_next: str

    requires_owner_choice: bool
    executes_automatically: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class DecisionEvidenceItem:
    evidence_id: str
    label: str
    explanation: str

    source_id: str
    required_before_decision: bool

    raw_evidence_loaded: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OwnerDecisionPacket:
    packet_id: str
    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    horizon: str
    urgency: str

    decision_question: str

    soulaana_summary: str
    why_this_decision_exists: str
    what_changed: str
    impact_summary: str
    do_nothing_consequence: str

    options: tuple[
        DecisionOption,
        ...
    ]

    evidence_items: tuple[
        DecisionEvidenceItem,
        ...
    ]

    owner_review_prompts: tuple[
        str,
        ...
    ]

    owning_application_id: str
    owning_application_label: str

    requires_tower_mediation: bool
    requires_owner_choice: bool

    packet_state: str

    automatic_decision_performed: bool
    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
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
            "horizon": self.horizon,
            "urgency": self.urgency,
            "decision_question": (
                self.decision_question
            ),
            "soulaana_summary": (
                self.soulaana_summary
            ),
            "why_this_decision_exists": (
                self.why_this_decision_exists
            ),
            "what_changed": self.what_changed,
            "impact_summary": (
                self.impact_summary
            ),
            "do_nothing_consequence": (
                self.do_nothing_consequence
            ),
            "options": [
                option.to_dict()
                for option in self.options
            ],
            "evidence_items": [
                item.to_dict()
                for item in self.evidence_items
            ],
            "owner_review_prompts": list(
                self.owner_review_prompts
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
            "requires_owner_choice": (
                self.requires_owner_choice
            ),
            "packet_state": (
                self.packet_state
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
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
class OwnerDecisionPacketSurface:
    title: str

    packets: tuple[
        OwnerDecisionPacket,
        ...
    ]

    packet_count: int
    ready_packet_count: int
    blocked_packet_count: int

    owner_choice_required_count: int

    automatic_decision_performed: bool
    approval_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "packets": [
                packet.to_dict()
                for packet in self.packets
            ],
            "packet_count": self.packet_count,
            "ready_packet_count": (
                self.ready_packet_count
            ),
            "blocked_packet_count": (
                self.blocked_packet_count
            ),
            "owner_choice_required_count": (
                self.owner_choice_required_count
            ),
            "automatic_decision_performed": (
                self.automatic_decision_performed
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
