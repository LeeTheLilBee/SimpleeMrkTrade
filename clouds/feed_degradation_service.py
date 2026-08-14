"""
GP058 — Safe Degradation /
No False Urgency + Fallback Interpretation.
"""

from __future__ import annotations

try:

    from .feed_degradation import (
        SafeDegradationSurface,
        SourceDegradationDecision,
    )

    from .feed_resilience import (
        FeedResilienceState,
    )

    from .feed_resilience_service import (
        get_gp057_certification_scenarios,
    )

except ImportError:

    from feed_degradation import (
        SafeDegradationSurface,
        SourceDegradationDecision,
    )

    from feed_resilience import (
        FeedResilienceState,
    )

    from feed_resilience_service import (
        get_gp057_certification_scenarios,
    )


DEGRADED_STATES = {
    FeedResilienceState
    .MISSING.value,

    FeedResilienceState
    .STALE.value,

    FeedResilienceState
    .CONFLICT.value,

    FeedResilienceState
    .INVALID.value,
}


def build_safe_degradation_surface(
    resilience_surface,
):

    decisions = []


    for item in (
        resilience_surface
        .assessments
    ):

        state = (
            item.resilience_state
        )


        if (
            state
            == FeedResilienceState
            .HEALTHY_LIVE.value
        ):

            degraded = False

            display_allowed = True

            trusted = True

            fallback = (
                "current_live_interpretation"
            )

            reference_label = False

            system_review = False

            status = (
                "Current"
            )

            meaning = (
                "The source has a valid live envelope "
                "inside the freshness boundary."
            )

            can_wait = (
                "No feed-recovery action is required."
            )

            next_step = (
                "Continue normal interpretation."
            )


        elif (
            state
            == FeedResilienceState
            .PROJECTION_ONLY.value
        ):

            degraded = False

            display_allowed = True

            trusted = False

            fallback = (
                "projection_reference_only"
            )

            reference_label = True

            system_review = False

            status = (
                "Projection only"
            )

            meaning = (
                "I can show this as planning/reference context, "
                "but I am not calling it current live truth."
            )

            can_wait = (
                "No emergency action is implied."
            )

            next_step = (
                "Keep the projection label visible until "
                "a verified live source is connected."
            )


        else:

            degraded = True

            display_allowed = False

            trusted = False

            fallback = (
                "withhold_current_claim_show_labeled_reference_only"
            )

            reference_label = True

            system_review = True

            status = (
                "Data unavailable for current-state claim"
            )

            meaning = (
                item.soulaana_what_it_means
            )

            can_wait = (
                "The business itself does not receive a "
                "new danger label just because its data feed degraded."
            )

            next_step = (
                item.soulaana_next_step
            )


        decisions.append(
            SourceDegradationDecision(

                source_id=(
                    item.source_id
                ),

                source_label=(
                    item.source_label
                ),

                resilience_state=(
                    state
                ),

                safely_degraded=(
                    degraded
                ),

                current_state_display_allowed=(
                    display_allowed
                ),

                current_state_trusted=(
                    trusted
                ),

                fallback_mode=(
                    fallback
                ),

                last_known_may_be_shown_as_current=False,

                reference_data_must_be_labeled=(
                    reference_label
                ),

                business_health_overridden=False,

                business_attention_escalated=False,

                owner_system_review_required=(
                    system_review
                ),

                soulaana_status=(
                    status
                ),

                soulaana_what_it_means=(
                    meaning
                ),

                soulaana_what_can_wait=(
                    can_wait
                ),

                soulaana_next_step=(
                    next_step
                ),

                automatic_business_decision_performed=False,

                downstream_execution_performed=False,
            )
        )


    decisions = tuple(
        decisions
    )


    degraded_count = sum(
        item.resilience_state
        in DEGRADED_STATES

        for item
        in decisions
    )


    withheld_count = sum(
        (
            item.resilience_state
            in DEGRADED_STATES
        )

        and (
            item
            .current_state_display_allowed
            is False
        )

        for item
        in decisions
    )


    false_urgency_count = sum(
        item.business_attention_escalated
        is True

        for item
        in decisions
    )


    all_fail_safe = all(

        item.safely_degraded
        is True

        and item
        .current_state_display_allowed
        is False

        and item
        .current_state_trusted
        is False

        and item
        .last_known_may_be_shown_as_current
        is False

        and item
        .reference_data_must_be_labeled
        is True

        and item
        .business_health_overridden
        is False

        and item
        .business_attention_escalated
        is False

        for item
        in decisions

        if (
            item.resilience_state
            in DEGRADED_STATES
        )
    )


    return SafeDegradationSurface(

        title=(
            "Safe Feed Degradation"
        ),

        decisions=(
            decisions
        ),

        source_count=(
            len(
                decisions
            )
        ),

        degraded_source_count=(
            degraded_count
        ),

        withheld_current_state_count=(
            withheld_count
        ),

        projection_reference_count=sum(
            item.fallback_mode
            == "projection_reference_only"

            for item
            in decisions
        ),

        healthy_live_count=sum(
            item.resilience_state
            == FeedResilienceState
            .HEALTHY_LIVE.value

            for item
            in decisions
        ),

        system_review_count=sum(
            item
            .owner_system_review_required

            for item
            in decisions
        ),

        business_health_override_count=sum(
            item.business_health_overridden

            for item
            in decisions
        ),

        business_attention_escalation_count=sum(
            item.business_attention_escalated

            for item
            in decisions
        ),

        false_urgency_count=(
            false_urgency_count
        ),

        last_known_falsely_current_count=sum(
            item
            .last_known_may_be_shown_as_current

            for item
            in decisions
        ),

        all_degraded_sources_fail_safe=(
            all_fail_safe
        ),

        automatic_business_decision_performed=False,

        downstream_execution_performed=False,

        soulaana_summary=(
            "If source data is stale, missing, conflicting, "
            "or invalid, I will tell you the data is degraded, "
            "withhold an unsupported current-state claim, "
            "and avoid turning a feed problem into fake business urgency."
        ),

        boundary_notice=(
            "System-review attention for a degraded feed is "
            "not the same thing as escalating business health "
            "or owner business urgency."
        ),
    )


def get_gp058_certification_surfaces():

    scenarios = (
        get_gp057_certification_scenarios()
    )

    return {

        name:
        build_safe_degradation_surface(
            surface
        )

        for (
            name,
            surface,
        )
        in scenarios.items()
    }


def get_clouds_gp058_status_payload():

    surfaces = (
        get_gp058_certification_surfaces()
    )


    projection = (
        surfaces[
            "projection"
        ]
    )

    missing = (
        surfaces[
            "missing"
        ]
    )

    stale = (
        surfaces[
            "stale"
        ]
    )

    conflict = (
        surfaces[
            "conflict"
        ]
    )


    safe = (
        projection
        .projection_reference_count
        == 6

        and projection
        .last_known_falsely_current_count
        == 0

        and missing
        .degraded_source_count
        == 1

        and stale
        .degraded_source_count
        == 1

        and conflict
        .degraded_source_count
        == 1

        and missing
        .withheld_current_state_count
        == 1

        and stale
        .withheld_current_state_count
        == 1

        and conflict
        .withheld_current_state_count
        == 1

        and missing
        .all_degraded_sources_fail_safe
        is True

        and stale
        .all_degraded_sources_fail_safe
        is True

        and conflict
        .all_degraded_sources_fail_safe
        is True

        and missing
        .business_health_override_count
        == 0

        and stale
        .business_health_override_count
        == 0

        and conflict
        .business_health_override_count
        == 0

        and missing
        .business_attention_escalation_count
        == 0

        and stale
        .business_attention_escalation_count
        == 0

        and conflict
        .business_attention_escalation_count
        == 0

        and missing.false_urgency_count
        == 0

        and stale.false_urgency_count
        == 0

        and conflict.false_urgency_count
        == 0

        and missing
        .last_known_falsely_current_count
        == 0

        and stale
        .last_known_falsely_current_count
        == 0

        and conflict
        .last_known_falsely_current_count
        == 0

        and missing
        .automatic_business_decision_performed
        is False

        and missing
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP058",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "SAFE DEGRADATION / NO FALSE URGENCY + "
            "FALLBACK INTERPRETATION"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "projection_reference_fallback_ready":
        True,

        "missing_fail_safe_ready":
        True,

        "stale_fail_safe_ready":
        True,

        "conflict_fail_safe_ready":
        True,

        "invalid_fail_safe_ready":
        True,

        "current_claim_withheld_when_degraded":
        True,

        "reference_data_label_required":
        True,

        "last_known_falsely_current_count":
        0,

        "business_health_override_count":
        0,

        "business_attention_escalation_count":
        0,

        "false_urgency_count":
        0,

        "system_review_is_business_danger":
        False,

        "automatic_business_decision_performed":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP059 — PHASE II OWNER WALKTHROUGH / "
            "TOWER-CLOUDS READINESS REHEARSAL"
        ),
    }
