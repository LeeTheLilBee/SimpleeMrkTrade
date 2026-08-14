"""
GP024 — Clouds core-v1 beta-readiness closeout.

This certifies Clouds-side readiness only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OwnerWalkthroughStep:
    step_id: str
    label: str
    expected_state: str
    passed: bool
    execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class CloudsBetaReadinessRecord:
    checkpoint_id: str

    core_pack_start: str
    core_pack_end: str

    owner_command_ready: bool
    soulaana_explanation_ready: bool
    progressive_disclosure_ready: bool
    owner_preferences_ready: bool
    operating_summary_boundary_ready: bool
    tower_boundary_preserved: bool

    live_downstream_feeds_connected: bool
    hosted_tower_integration_verified: bool
    hosted_staging_verified: bool
    external_beta_acceptance_recorded: bool

    clouds_side_ready: bool
    externally_beta_ready: bool

    conclusion: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class CloudsBetaReadinessSurface:
    title: str

    walkthrough: tuple[
        OwnerWalkthroughStep,
        ...
    ]

    readiness: CloudsBetaReadinessRecord

    walkthrough_step_count: int
    walkthrough_pass_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "walkthrough": [
                item.to_dict()
                for item in self.walkthrough
            ],
            "readiness": (
                self.readiness.to_dict()
            ),
            "walkthrough_step_count": (
                self.walkthrough_step_count
            ),
            "walkthrough_pass_count": (
                self.walkthrough_pass_count
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
