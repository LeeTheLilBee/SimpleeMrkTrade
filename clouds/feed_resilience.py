"""
GP057 — Feed Resilience /
Stale + Missing + Conflict Detection.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FeedResilienceState(
    str,
    Enum,
):

    HEALTHY_LIVE = (
        "healthy_live"
    )

    PROJECTION_ONLY = (
        "projection_only"
    )

    MISSING = (
        "missing"
    )

    STALE = (
        "stale"
    )

    CONFLICT = (
        "conflict"
    )

    INVALID = (
        "invalid"
    )


@dataclass(frozen=True)
class SourceFeedResilience:

    source_id: str

    source_label: str

    resilience_state: str

    envelope_count: int

    valid_envelope_count: int

    invalid_envelope_count: int

    selected_feed_id: str | None

    selected_sequence: int | None

    selected_mode: str | None

    selected_observed_at: str | None

    current_source_truth_trusted: bool

    stale_detected: bool

    missing_detected: bool

    conflict_detected: bool

    invalid_detected: bool

    projection_only: bool

    live_current: bool

    system_review_required: bool

    business_risk_inferred: bool

    business_attention_escalated: bool

    false_urgency_created: bool

    soulaana_what_happened: str

    soulaana_what_it_means: str

    soulaana_what_not_to_assume: str

    soulaana_next_step: str

    raw_source_access_performed: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class FeedResilienceSurface:

    title: str

    assessments: tuple[
        SourceFeedResilience,
        ...
    ]

    canonical_source_count: int

    assessment_count: int

    healthy_live_count: int

    projection_only_count: int

    missing_count: int

    stale_count: int

    conflict_count: int

    invalid_count: int

    degraded_count: int

    trusted_current_source_count: int

    business_risk_inference_count: int

    business_attention_escalation_count: int

    false_urgency_count: int

    raw_source_access_performed: bool

    downstream_execution_performed: bool

    boundary_notice: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "title":
            self.title,

            "assessments": [
                item.to_dict()
                for item
                in self.assessments
            ],

            "canonical_source_count":
            self.canonical_source_count,

            "assessment_count":
            self.assessment_count,

            "healthy_live_count":
            self.healthy_live_count,

            "projection_only_count":
            self.projection_only_count,

            "missing_count":
            self.missing_count,

            "stale_count":
            self.stale_count,

            "conflict_count":
            self.conflict_count,

            "invalid_count":
            self.invalid_count,

            "degraded_count":
            self.degraded_count,

            "trusted_current_source_count":
            self.trusted_current_source_count,

            "business_risk_inference_count":
            self.business_risk_inference_count,

            "business_attention_escalation_count":
            (
                self
                .business_attention_escalation_count
            ),

            "false_urgency_count":
            self.false_urgency_count,

            "raw_source_access_performed":
            self.raw_source_access_performed,

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "boundary_notice":
            self.boundary_notice,
        }
