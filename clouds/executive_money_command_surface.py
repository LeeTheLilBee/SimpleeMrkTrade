"""
GP052 — Soulaana Executive Money Command Surface / Layer Closeout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutiveMoneyCommandSurface:
    title: str
    subtitle: str

    snapshot: Any
    capital_competition: Any

    verified_real_spendable_cents: int

    planning_available_cents: int
    planning_committed_cents: int

    projected_cents: int
    simulated_cents: int

    target_cents: int
    need_cents: int

    strict_money_separation_verified: bool

    simulated_money_in_spendable_total: bool
    projected_money_in_spendable_total: bool
    target_money_in_spendable_total: bool

    real_money_claimed: bool

    soulaana_owner_brief: str
    soulaana_why_it_matters: str
    soulaana_what_needs_attention: str
    soulaana_what_can_wait: str
    soulaana_next_step: str

    allocation_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,

            "snapshot": (
                self.snapshot.to_dict()
            ),

            "capital_competition": (
                self
                .capital_competition
                .to_dict()
            ),

            "verified_real_spendable_cents": (
                self
                .verified_real_spendable_cents
            ),

            "planning_available_cents": (
                self.planning_available_cents
            ),

            "planning_committed_cents": (
                self.planning_committed_cents
            ),

            "projected_cents": (
                self.projected_cents
            ),

            "simulated_cents": (
                self.simulated_cents
            ),

            "target_cents": (
                self.target_cents
            ),

            "need_cents": (
                self.need_cents
            ),

            "strict_money_separation_verified": (
                self
                .strict_money_separation_verified
            ),

            "simulated_money_in_spendable_total": (
                self
                .simulated_money_in_spendable_total
            ),

            "projected_money_in_spendable_total": (
                self
                .projected_money_in_spendable_total
            ),

            "target_money_in_spendable_total": (
                self
                .target_money_in_spendable_total
            ),

            "real_money_claimed": (
                self.real_money_claimed
            ),

            "soulaana_owner_brief": (
                self.soulaana_owner_brief
            ),

            "soulaana_why_it_matters": (
                self.soulaana_why_it_matters
            ),

            "soulaana_what_needs_attention": (
                self
                .soulaana_what_needs_attention
            ),

            "soulaana_what_can_wait": (
                self.soulaana_what_can_wait
            ),

            "soulaana_next_step": (
                self.soulaana_next_step
            ),

            "allocation_performed": (
                self.allocation_performed
            ),

            "capital_movement_performed": (
                self.capital_movement_performed
            ),

            "downstream_execution_performed": (
                self
                .downstream_execution_performed
            ),

            "boundary_notice": (
                self.boundary_notice
            ),
        }
