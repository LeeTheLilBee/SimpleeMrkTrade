"""
GP050 — Executive Money Snapshot / Strict Money-Separation Surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutiveMoneySnapshot:
    title: str

    entries: tuple[
        Any,
        ...
    ]

    currency: str

    verified_real_available_cents: int
    verified_real_committed_cents: int
    verified_real_spendable_cents: int

    planning_available_cents: int
    planning_committed_cents: int

    projected_cents: int
    simulated_cents: int

    target_cents: int
    need_cents: int

    real_money_claimed: bool

    simulation_excluded_from_spendable: bool
    projection_excluded_from_spendable: bool
    targets_excluded_from_spendable: bool

    soulaana_what_you_have: str
    soulaana_what_is_spoken_for: str
    soulaana_what_is_only_projected: str
    soulaana_what_is_simulated: str
    soulaana_what_is_targeted: str
    soulaana_what_is_needed: str

    capital_movement_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,

            "entries": [
                item.to_dict()
                for item in self.entries
            ],

            "currency": self.currency,

            "verified_real_available_cents": (
                self
                .verified_real_available_cents
            ),

            "verified_real_committed_cents": (
                self
                .verified_real_committed_cents
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

            "real_money_claimed": (
                self.real_money_claimed
            ),

            "simulation_excluded_from_spendable": (
                self
                .simulation_excluded_from_spendable
            ),

            "projection_excluded_from_spendable": (
                self
                .projection_excluded_from_spendable
            ),

            "targets_excluded_from_spendable": (
                self
                .targets_excluded_from_spendable
            ),

            "soulaana_what_you_have": (
                self.soulaana_what_you_have
            ),

            "soulaana_what_is_spoken_for": (
                self
                .soulaana_what_is_spoken_for
            ),

            "soulaana_what_is_only_projected": (
                self
                .soulaana_what_is_only_projected
            ),

            "soulaana_what_is_simulated": (
                self.soulaana_what_is_simulated
            ),

            "soulaana_what_is_targeted": (
                self.soulaana_what_is_targeted
            ),

            "soulaana_what_is_needed": (
                self.soulaana_what_is_needed
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
