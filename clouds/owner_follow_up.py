"""
GP055 — Owner Follow-Up /
Unresolved + Deferred Attention Recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OwnerFollowUpItem:

    agenda_item_id: str

    source_id: str
    source_label: str

    title: str

    horizon: str
    urgency: str

    follow_up_reason: str

    requires_owner_action: bool

    deferred: bool

    reopened_due_to_material_change: bool

    not_yet_handled: bool

    snooze_expired: bool

    waiting_dependency: bool

    soulaana_explanation: str

    forgotten_claimed: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class OwnerFollowUpSurface:

    title: str

    items: tuple[
        OwnerFollowUpItem,
        ...
    ]

    follow_up_count: int

    unresolved_count: int

    deferred_count: int

    reopened_material_change_count: int

    not_yet_handled_count: int

    snooze_expired_count: int

    waiting_dependency_count: int

    forgotten_claim_count: int

    soulaana_follow_up_summary: str

    soulaana_deferred_summary: str

    soulaana_memory_protection: str

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

            "follow_up_count":
            self.follow_up_count,

            "unresolved_count":
            self.unresolved_count,

            "deferred_count":
            self.deferred_count,

            "reopened_material_change_count":
            (
                self
                .reopened_material_change_count
            ),

            "not_yet_handled_count":
            self.not_yet_handled_count,

            "snooze_expired_count":
            self.snooze_expired_count,

            "waiting_dependency_count":
            self.waiting_dependency_count,

            "forgotten_claim_count":
            self.forgotten_claim_count,

            "soulaana_follow_up_summary":
            self.soulaana_follow_up_summary,

            "soulaana_deferred_summary":
            self.soulaana_deferred_summary,

            "soulaana_memory_protection":
            self.soulaana_memory_protection,

            "automatic_action_performed":
            self.automatic_action_performed,

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "boundary_notice":
            self.boundary_notice,
        }
