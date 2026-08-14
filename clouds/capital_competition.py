"""
GP051 — Capital Need / Competition Interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CapitalNeedView:
    entry_id: str

    source_id: str
    source_label: str

    amount_cents: int
    currency: str

    horizon: str
    urgency: str

    priority_rank: int

    owner_attention_required: bool

    certification_fixture_only: bool

    soulaana_reason: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class CapitalCompetitionSurface:
    title: str

    needs: tuple[
        CapitalNeedView,
        ...
    ]

    need_count: int

    total_need_cents: int

    verified_real_spendable_cents: int

    verified_coverage_gap_cents: int

    fully_covered_by_verified_real_capital: bool

    capital_competition_present: bool

    review_order_source_ids: tuple[
        str,
        ...
    ]

    allocation_performed: bool
    capital_movement_performed: bool
    downstream_execution_performed: bool

    soulaana_what_is_competing: str
    soulaana_what_it_means: str
    soulaana_what_needs_attention: str
    soulaana_what_can_wait: str
    soulaana_next_step: str

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,

            "needs": [
                item.to_dict()
                for item in self.needs
            ],

            "need_count": (
                self.need_count
            ),

            "total_need_cents": (
                self.total_need_cents
            ),

            "verified_real_spendable_cents": (
                self
                .verified_real_spendable_cents
            ),

            "verified_coverage_gap_cents": (
                self
                .verified_coverage_gap_cents
            ),

            "fully_covered_by_verified_real_capital": (
                self
                .fully_covered_by_verified_real_capital
            ),

            "capital_competition_present": (
                self.capital_competition_present
            ),

            "review_order_source_ids": list(
                self.review_order_source_ids
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

            "soulaana_what_is_competing": (
                self
                .soulaana_what_is_competing
            ),

            "soulaana_what_it_means": (
                self.soulaana_what_it_means
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

            "boundary_notice": (
                self.boundary_notice
            ),
        }
