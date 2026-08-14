"""
GP053 — Soulaana Daily Owner Brief /
What Changed While You Were Gone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SoulaanaBriefItem:

    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    title: str

    horizon: str
    urgency: str

    changed_since_last_snapshot: bool

    material_change: bool

    change_direction: str | None

    memory_present: bool

    memory_disposition: str | None

    continuity_state: str

    needs_owner_now: bool

    quiet_because_already_handled: bool

    waiting_dependency: bool

    soulaana_what_changed: str

    soulaana_what_it_means: str

    soulaana_why_now: str

    soulaana_if_we_wait: str

    soulaana_next_review: str

    automatic_action_performed: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class SoulaanaOwnerBrief:

    title: str

    items: tuple[
        SoulaanaBriefItem,
        ...
    ]

    agenda_item_count: int

    changed_source_count: int

    material_change_count: int

    needs_you_count: int

    quiet_handled_count: int

    waiting_dependency_count: int

    watching_count: int

    can_wait_count: int

    nothing_needs_you: bool

    soulaana_opening: str

    soulaana_changed_since_you_were_gone: str

    soulaana_needs_you: str

    soulaana_already_handled: str

    soulaana_can_wait: str

    soulaana_no_action: str

    automatic_action_performed: bool

    downstream_execution_performed: bool

    boundary_notice: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "title":
            self.title,

            "items": [
                item.to_dict()
                for item
                in self.items
            ],

            "agenda_item_count":
            self.agenda_item_count,

            "changed_source_count":
            self.changed_source_count,

            "material_change_count":
            self.material_change_count,

            "needs_you_count":
            self.needs_you_count,

            "quiet_handled_count":
            self.quiet_handled_count,

            "waiting_dependency_count":
            self.waiting_dependency_count,

            "watching_count":
            self.watching_count,

            "can_wait_count":
            self.can_wait_count,

            "nothing_needs_you":
            self.nothing_needs_you,

            "soulaana_opening":
            self.soulaana_opening,

            "soulaana_changed_since_you_were_gone":
            (
                self
                .soulaana_changed_since_you_were_gone
            ),

            "soulaana_needs_you":
            self.soulaana_needs_you,

            "soulaana_already_handled":
            self.soulaana_already_handled,

            "soulaana_can_wait":
            self.soulaana_can_wait,

            "soulaana_no_action":
            self.soulaana_no_action,

            "automatic_action_performed":
            self.automatic_action_performed,

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "boundary_notice":
            self.boundary_notice,
        }
