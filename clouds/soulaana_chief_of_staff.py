"""
GP056 — Soulaana Chief of Staff Command Surface /
Layer Closeout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SoulaanaChiefOfStaffSurface:

    title: str

    subtitle: str

    owner_brief: Any

    consequence_blocker_surface: Any

    follow_up_surface: Any

    money_surface: Any

    changed_since_you_were_gone_count: int

    needs_you_count: int

    unresolved_count: int

    deferred_count: int

    blocker_count: int

    quiet_handled_count: int

    verified_real_spendable_cents: int

    nothing_needs_you: bool

    explicit_no_action_message_ready: bool

    soulaana_opening: str

    soulaana_since_you_were_gone: str

    soulaana_what_matters_first: str

    soulaana_consequences_and_blockers: str

    soulaana_unresolved_follow_up: str

    soulaana_money_context: str

    soulaana_what_can_wait: str

    soulaana_no_action: str

    soulaana_next_step: str

    priority_engine_replaced: bool

    memory_engine_replaced: bool

    money_engine_replaced: bool

    automatic_business_decision_performed: bool

    allocation_performed: bool

    capital_movement_performed: bool

    downstream_execution_performed: bool

    boundary_notice: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "title":
            self.title,

            "subtitle":
            self.subtitle,

            "owner_brief":
            self.owner_brief.to_dict(),

            "consequence_blocker_surface":
            (
                self
                .consequence_blocker_surface
                .to_dict()
            ),

            "follow_up_surface":
            self.follow_up_surface.to_dict(),

            "money_surface":
            self.money_surface.to_dict(),

            "changed_since_you_were_gone_count":
            (
                self
                .changed_since_you_were_gone_count
            ),

            "needs_you_count":
            self.needs_you_count,

            "unresolved_count":
            self.unresolved_count,

            "deferred_count":
            self.deferred_count,

            "blocker_count":
            self.blocker_count,

            "quiet_handled_count":
            self.quiet_handled_count,

            "verified_real_spendable_cents":
            (
                self
                .verified_real_spendable_cents
            ),

            "nothing_needs_you":
            self.nothing_needs_you,

            "explicit_no_action_message_ready":
            (
                self
                .explicit_no_action_message_ready
            ),

            "soulaana_opening":
            self.soulaana_opening,

            "soulaana_since_you_were_gone":
            self.soulaana_since_you_were_gone,

            "soulaana_what_matters_first":
            self.soulaana_what_matters_first,

            "soulaana_consequences_and_blockers":
            (
                self
                .soulaana_consequences_and_blockers
            ),

            "soulaana_unresolved_follow_up":
            self.soulaana_unresolved_follow_up,

            "soulaana_money_context":
            self.soulaana_money_context,

            "soulaana_what_can_wait":
            self.soulaana_what_can_wait,

            "soulaana_no_action":
            self.soulaana_no_action,

            "soulaana_next_step":
            self.soulaana_next_step,

            "priority_engine_replaced":
            self.priority_engine_replaced,

            "memory_engine_replaced":
            self.memory_engine_replaced,

            "money_engine_replaced":
            self.money_engine_replaced,

            "automatic_business_decision_performed":
            (
                self
                .automatic_business_decision_performed
            ),

            "allocation_performed":
            self.allocation_performed,

            "capital_movement_performed":
            self.capital_movement_performed,

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "boundary_notice":
            self.boundary_notice,
        }
