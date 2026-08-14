"""
GP054 — Consequences / Blockers / Dependency Interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OwnerConsequenceItem:

    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    horizon: str
    urgency: str

    consequence_basis: str

    soulaana_if_we_wait: str

    consequence_inferred_beyond_source_contract: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class OwnerBlockerItem:

    agenda_item_id: str

    source_id: str
    source_label: str

    blocker_kind: str

    blocker_basis: str

    owner_action_should_wait: bool

    soulaana_explanation: str

    fabricated_blocker: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class ConsequenceBlockerSurface:

    title: str

    consequences: tuple[
        OwnerConsequenceItem,
        ...
    ]

    blockers: tuple[
        OwnerBlockerItem,
        ...
    ]

    consequence_count: int

    blocker_count: int

    current_waiting_dependency_count: int

    fabricated_blocker_count: int

    consequence_inference_count: int

    soulaana_consequence_summary: str

    soulaana_blocker_summary: str

    soulaana_what_can_wait: str

    automatic_action_performed: bool

    downstream_execution_performed: bool

    boundary_notice: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "title":
            self.title,

            "consequences": [
                item.to_dict()
                for item
                in self.consequences
            ],

            "blockers": [
                item.to_dict()
                for item
                in self.blockers
            ],

            "consequence_count":
            self.consequence_count,

            "blocker_count":
            self.blocker_count,

            "current_waiting_dependency_count":
            (
                self
                .current_waiting_dependency_count
            ),

            "fabricated_blocker_count":
            self.fabricated_blocker_count,

            "consequence_inference_count":
            self.consequence_inference_count,

            "soulaana_consequence_summary":
            (
                self
                .soulaana_consequence_summary
            ),

            "soulaana_blocker_summary":
            self.soulaana_blocker_summary,

            "soulaana_what_can_wait":
            self.soulaana_what_can_wait,

            "automatic_action_performed":
            self.automatic_action_performed,

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "boundary_notice":
            self.boundary_notice,
        }
