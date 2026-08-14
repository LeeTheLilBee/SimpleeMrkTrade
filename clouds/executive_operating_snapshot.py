"""
GP020 — Executive Operating Snapshot /
Soulaana Interpretation Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutiveOperatingSourceCard:
    source_id: str
    source_label: str

    health: str
    readiness: str
    attention: str

    what_it_means: str
    why_it_matters: str
    what_needs_attention: str
    what_can_wait: str
    owner_next_step: str

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class SoulaanaExecutiveBrief:
    headline: str
    explanation: str

    needs_you_now: tuple[str, ...]
    keep_watching: tuple[str, ...]
    can_wait: tuple[str, ...]

    no_action_needed: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "headline": self.headline,
            "explanation": self.explanation,
            "needs_you_now": list(
                self.needs_you_now
            ),
            "keep_watching": list(
                self.keep_watching
            ),
            "can_wait": list(
                self.can_wait
            ),
            "no_action_needed": list(
                self.no_action_needed
            ),
        }


@dataclass(frozen=True)
class ExecutiveOperatingSnapshot:
    title: str

    brief: SoulaanaExecutiveBrief

    source_cards: tuple[
        ExecutiveOperatingSourceCard,
        ...
    ]

    source_count: int
    action_required_count: int
    watch_count: int
    no_action_count: int

    raw_source_access_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "brief": self.brief.to_dict(),
            "source_cards": [
                item.to_dict()
                for item in self.source_cards
            ],
            "source_count": self.source_count,
            "action_required_count": (
                self.action_required_count
            ),
            "watch_count": self.watch_count,
            "no_action_count": (
                self.no_action_count
            ),
            "raw_source_access_performed": (
                self.raw_source_access_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "boundary_notice": self.boundary_notice,
        }
