"""
GP058 — Safe Degradation /
No False Urgency + Fallback Interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceDegradationDecision:

    source_id: str

    source_label: str

    resilience_state: str

    safely_degraded: bool

    current_state_display_allowed: bool

    current_state_trusted: bool

    fallback_mode: str

    last_known_may_be_shown_as_current: bool

    reference_data_must_be_labeled: bool

    business_health_overridden: bool

    business_attention_escalated: bool

    owner_system_review_required: bool

    soulaana_status: str

    soulaana_what_it_means: str

    soulaana_what_can_wait: str

    soulaana_next_step: str

    automatic_business_decision_performed: bool

    downstream_execution_performed: bool


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return (
            self.__dict__.copy()
        )


@dataclass(frozen=True)
class SafeDegradationSurface:

    title: str

    decisions: tuple[
        SourceDegradationDecision,
        ...
    ]

    source_count: int

    degraded_source_count: int

    withheld_current_state_count: int

    projection_reference_count: int

    healthy_live_count: int

    system_review_count: int

    business_health_override_count: int

    business_attention_escalation_count: int

    false_urgency_count: int

    last_known_falsely_current_count: int

    all_degraded_sources_fail_safe: bool

    automatic_business_decision_performed: bool

    downstream_execution_performed: bool

    soulaana_summary: str

    boundary_notice: str


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "title":
            self.title,

            "decisions": [
                item.to_dict()
                for item
                in self.decisions
            ],

            "source_count":
            self.source_count,

            "degraded_source_count":
            self.degraded_source_count,

            "withheld_current_state_count":
            self.withheld_current_state_count,

            "projection_reference_count":
            self.projection_reference_count,

            "healthy_live_count":
            self.healthy_live_count,

            "system_review_count":
            self.system_review_count,

            "business_health_override_count":
            self.business_health_override_count,

            "business_attention_escalation_count":
            (
                self
                .business_attention_escalation_count
            ),

            "false_urgency_count":
            self.false_urgency_count,

            "last_known_falsely_current_count":
            self.last_known_falsely_current_count,

            "all_degraded_sources_fail_safe":
            self.all_degraded_sources_fail_safe,

            "automatic_business_decision_performed":
            (
                self
                .automatic_business_decision_performed
            ),

            "downstream_execution_performed":
            self.downstream_execution_performed,

            "soulaana_summary":
            self.soulaana_summary,

            "boundary_notice":
            self.boundary_notice,
        }
