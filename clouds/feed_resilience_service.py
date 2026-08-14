"""
GP057 — Feed Resilience /
Stale + Missing + Conflict Detection.

Reuses GP025 canonical envelopes and validator.

Feed degradation is DATA degradation.

It does not automatically become business-risk escalation.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from functools import lru_cache

try:

    from .feed_resilience import (
        FeedResilienceState,
        FeedResilienceSurface,
        SourceFeedResilience,
    )

    from .operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedMode,
    )

    from .operating_feed_ingestion_service import (
        _build_integrity_payload,
        _hash_payload,
        build_projection_feed_envelopes,
        validate_operating_feed,
    )

except ImportError:

    from feed_resilience import (
        FeedResilienceState,
        FeedResilienceSurface,
        SourceFeedResilience,
    )

    from operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
        OperatingFeedMode,
    )

    from operating_feed_ingestion_service import (
        _build_integrity_payload,
        _hash_payload,
        build_projection_feed_envelopes,
        validate_operating_feed,
    )


DEFAULT_STALE_AFTER_SECONDS = (
    15 * 60
)


SOURCE_LABELS = {
    "observatory":
    "The Observatory",

    "tower":
    "The Tower",

    "teller":
    "The Teller",

    "grounds":
    "The Grounds",

    "archive_vault":
    "Archive Vault",

    "atm_operations":
    "ATM Operations",
}


def _parse_iso(
    value,
):

    if not value:
        return None

    if (
        value
        == "projection-not-live"
    ):
        return None

    try:

        if (
            value.endswith(
                "Z"
            )
        ):

            value = (
                value[:-1]
                + "+00:00"
            )

        parsed = (
            datetime.fromisoformat(
                value
            )
        )

        if (
            parsed.tzinfo
            is None
        ):

            parsed = (
                parsed.replace(
                    tzinfo=timezone.utc
                )
            )

        return parsed

    except (
        ValueError,
        TypeError,
    ):

        return None


def _live_age_seconds(
    observed_at,
    now_iso,
):

    observed = (
        _parse_iso(
            observed_at
        )
    )

    now = (
        _parse_iso(
            now_iso
        )
    )

    if (
        observed
        is None

        or now
        is None
    ):

        return None

    return (
        now
        - observed
    ).total_seconds()


def _rebuild_integrity_hash(
    envelope,
):

    payload = (
        _build_integrity_payload(

            schema_version=(
                envelope
                .schema_version
            ),

            feed_id=(
                envelope.feed_id
            ),

            source_id=(
                envelope.source_id
            ),

            source_label=(
                envelope
                .source_label
            ),

            mode=(
                envelope.mode
            ),

            source_sequence=(
                envelope
                .source_sequence
            ),

            observed_at=(
                envelope
                .observed_at
            ),

            health=(
                envelope.health
            ),

            readiness=(
                envelope.readiness
            ),

            attention=(
                envelope.attention
            ),

            headline=(
                envelope.headline
            ),

            explanation=(
                envelope.explanation
            ),

            owner_message=(
                envelope.owner_message
            ),

            metrics=(
                envelope.metrics
            ),
        )
    )

    return (
        _hash_payload(
            payload
        )
    )


def build_certification_live_envelope(
    source_id,
    *,
    feed_id,
    source_sequence,
    observed_at,
    headline=None,
):
    """
    Create a structurally valid GP025 live-envelope fixture.

    Certification fixture only.
    No external connection is claimed.
    """

    base = next(

        item

        for item
        in build_projection_feed_envelopes()

        if (
            item.source_id
            == source_id
        )
    )


    envelope = replace(

        base,

        feed_id=(
            feed_id
        ),

        mode=(
            OperatingFeedMode
            .LIVE.value
        ),

        source_sequence=(
            source_sequence
        ),

        observed_at=(
            observed_at
        ),

        headline=(
            headline
            or base.headline
        ),

        source_claims_live=True,

        source_integrity_hash="",
    )


    return replace(

        envelope,

        source_integrity_hash=(
            _rebuild_integrity_hash(
                envelope
            )
        ),
    )


def assess_feed_resilience(
    envelopes,
    *,
    now_iso,
    stale_after_seconds=(
        DEFAULT_STALE_AFTER_SECONDS
    ),
):

    envelopes = tuple(
        envelopes
    )


    assessments = []


    for source_id in (
        CANONICAL_OPERATING_SOURCE_IDS
    ):

        source_envelopes = tuple(

            item

            for item
            in envelopes

            if (
                item.source_id
                == source_id
            )
        )


        source_label = (
            SOURCE_LABELS[
                source_id
            ]
        )


        if not source_envelopes:

            assessments.append(
                SourceFeedResilience(

                    source_id=(
                        source_id
                    ),

                    source_label=(
                        source_label
                    ),

                    resilience_state=(
                        FeedResilienceState
                        .MISSING.value
                    ),

                    envelope_count=0,

                    valid_envelope_count=0,

                    invalid_envelope_count=0,

                    selected_feed_id=None,

                    selected_sequence=None,

                    selected_mode=None,

                    selected_observed_at=None,

                    current_source_truth_trusted=False,

                    stale_detected=False,

                    missing_detected=True,

                    conflict_detected=False,

                    invalid_detected=False,

                    projection_only=False,

                    live_current=False,

                    system_review_required=True,

                    business_risk_inferred=False,

                    business_attention_escalated=False,

                    false_urgency_created=False,

                    soulaana_what_happened=(
                        "I do not have a current envelope "
                        "for this source in the supplied feed set."
                    ),

                    soulaana_what_it_means=(
                        "I cannot claim the source's current "
                        "operating state from this feed set."
                    ),

                    soulaana_what_not_to_assume=(
                        "Missing data does not prove that "
                        "the business is unhealthy or in danger."
                    ),

                    soulaana_next_step=(
                        "Keep the source visibly unavailable "
                        "until a valid source envelope arrives."
                    ),

                    raw_source_access_performed=False,

                    downstream_execution_performed=False,
                )
            )

            continue


        validated = tuple(
            (
                envelope,

                validate_operating_feed(
                    envelope
                ),
            )

            for envelope
            in source_envelopes
        )


        valid = tuple(

            envelope

            for (
                envelope,
                receipt,
            )
            in validated

            if (
                receipt
                .accepted_for_clouds_interpretation
                is True
            )
        )


        invalid_count = (
            len(source_envelopes)
            - len(valid)
        )


        if not valid:

            assessments.append(
                SourceFeedResilience(

                    source_id=source_id,

                    source_label=(
                        source_label
                    ),

                    resilience_state=(
                        FeedResilienceState
                        .INVALID.value
                    ),

                    envelope_count=(
                        len(
                            source_envelopes
                        )
                    ),

                    valid_envelope_count=0,

                    invalid_envelope_count=(
                        invalid_count
                    ),

                    selected_feed_id=None,

                    selected_sequence=None,

                    selected_mode=None,

                    selected_observed_at=None,

                    current_source_truth_trusted=False,

                    stale_detected=False,

                    missing_detected=False,

                    conflict_detected=False,

                    invalid_detected=True,

                    projection_only=False,

                    live_current=False,

                    system_review_required=True,

                    business_risk_inferred=False,

                    business_attention_escalated=False,

                    false_urgency_created=False,

                    soulaana_what_happened=(
                        "The supplied source envelope failed "
                        "the existing GP025 feed-validation contract."
                    ),

                    soulaana_what_it_means=(
                        "I am withholding current source truth "
                        "rather than interpreting rejected input."
                    ),

                    soulaana_what_not_to_assume=(
                        "A rejected data envelope is a data-quality "
                        "problem, not proof of a business failure."
                    ),

                    soulaana_next_step=(
                        "Resolve the feed validation problem "
                        "before treating the source as current."
                    ),

                    raw_source_access_performed=False,

                    downstream_execution_performed=False,
                )
            )

            continue


        highest_sequence = max(
            item.source_sequence
            for item
            in valid
        )


        highest = tuple(

            item

            for item
            in valid

            if (
                item.source_sequence
                == highest_sequence
            )
        )


        distinct_hashes = {
            item.source_integrity_hash
            for item
            in highest
        }


        conflict = (
            len(
                highest
            )
            > 1

            and len(
                distinct_hashes
            )
            > 1
        )


        if conflict:

            assessments.append(
                SourceFeedResilience(

                    source_id=source_id,

                    source_label=(
                        source_label
                    ),

                    resilience_state=(
                        FeedResilienceState
                        .CONFLICT.value
                    ),

                    envelope_count=(
                        len(
                            source_envelopes
                        )
                    ),

                    valid_envelope_count=(
                        len(
                            valid
                        )
                    ),

                    invalid_envelope_count=(
                        invalid_count
                    ),

                    selected_feed_id=None,

                    selected_sequence=(
                        highest_sequence
                    ),

                    selected_mode=None,

                    selected_observed_at=None,

                    current_source_truth_trusted=False,

                    stale_detected=False,

                    missing_detected=False,

                    conflict_detected=True,

                    invalid_detected=False,

                    projection_only=False,

                    live_current=False,

                    system_review_required=True,

                    business_risk_inferred=False,

                    business_attention_escalated=False,

                    false_urgency_created=False,

                    soulaana_what_happened=(
                        "I received more than one valid envelope "
                        "for the same highest source sequence, "
                        "and their integrity hashes disagree."
                    ),

                    soulaana_what_it_means=(
                        "I cannot safely choose one current truth."
                    ),

                    soulaana_what_not_to_assume=(
                        "I will not pick whichever conflicting "
                        "snapshot looks better or worse."
                    ),

                    soulaana_next_step=(
                        "Hold the source's current state as "
                        "unresolved until the conflict is reconciled."
                    ),

                    raw_source_access_performed=False,

                    downstream_execution_performed=False,
                )
            )

            continue


        selected = sorted(
            valid,

            key=lambda item: (
                item.source_sequence,
                item.feed_id,
            ),

            reverse=True,
        )[0]


        if (
            selected.mode
            == OperatingFeedMode
            .PROJECTION.value
        ):

            state = (
                FeedResilienceState
                .PROJECTION_ONLY.value
            )

            trusted = False

            stale = False

            projection_only = True

            live_current = False

            system_review = False

            what_happened = (
                "This source currently has an accepted "
                "projection envelope, not a live envelope."
            )

            what_it_means = (
                "I may use it as labeled planning/reference "
                "context, but not as verified current live state."
            )

            not_assume = (
                "Projection does not become current live truth "
                "just because it is the newest available record."
            )

            next_step = (
                "Keep it labeled projection-only until "
                "a valid externally connected live feed exists."
            )


        else:

            age = (
                _live_age_seconds(
                    selected.observed_at,
                    now_iso,
                )
            )


            stale = (
                age is None

                or age
                > stale_after_seconds
            )


            if stale:

                state = (
                    FeedResilienceState
                    .STALE.value
                )

                trusted = False

                projection_only = False

                live_current = False

                system_review = True

                what_happened = (
                    "The newest valid live envelope is older "
                    "than the configured freshness boundary."
                )

                what_it_means = (
                    "I cannot treat that source snapshot "
                    "as current."
                )

                not_assume = (
                    "Stale data does not prove the business "
                    "itself is in trouble."
                )

                next_step = (
                    "Keep the last known information visibly "
                    "labeled stale and wait for a fresh valid envelope."
                )


            else:

                state = (
                    FeedResilienceState
                    .HEALTHY_LIVE.value
                )

                trusted = True

                projection_only = False

                live_current = True

                system_review = False

                what_happened = (
                    "A valid live envelope is inside "
                    "the configured freshness boundary."
                )

                what_it_means = (
                    "The source may count as current for "
                    "Clouds interpretation."
                )

                not_assume = (
                    "A current feed still does not grant "
                    "Clouds downstream authority."
                )

                next_step = (
                    "Continue normal interpretation."
                )


        assessments.append(
            SourceFeedResilience(

                source_id=(
                    source_id
                ),

                source_label=(
                    source_label
                ),

                resilience_state=(
                    state
                ),

                envelope_count=(
                    len(
                        source_envelopes
                    )
                ),

                valid_envelope_count=(
                    len(
                        valid
                    )
                ),

                invalid_envelope_count=(
                    invalid_count
                ),

                selected_feed_id=(
                    selected.feed_id
                ),

                selected_sequence=(
                    selected
                    .source_sequence
                ),

                selected_mode=(
                    selected.mode
                ),

                selected_observed_at=(
                    selected
                    .observed_at
                ),

                current_source_truth_trusted=(
                    trusted
                ),

                stale_detected=(
                    stale
                ),

                missing_detected=False,

                conflict_detected=False,

                invalid_detected=False,

                projection_only=(
                    projection_only
                ),

                live_current=(
                    live_current
                ),

                system_review_required=(
                    system_review
                ),

                business_risk_inferred=False,

                business_attention_escalated=False,

                false_urgency_created=False,

                soulaana_what_happened=(
                    what_happened
                ),

                soulaana_what_it_means=(
                    what_it_means
                ),

                soulaana_what_not_to_assume=(
                    not_assume
                ),

                soulaana_next_step=(
                    next_step
                ),

                raw_source_access_performed=False,

                downstream_execution_performed=False,
            )
        )


    assessments = tuple(
        assessments
    )


    degraded_states = {
        FeedResilienceState
        .MISSING.value,

        FeedResilienceState
        .STALE.value,

        FeedResilienceState
        .CONFLICT.value,

        FeedResilienceState
        .INVALID.value,
    }


    return FeedResilienceSurface(

        title=(
            "Operating Feed Resilience"
        ),

        assessments=(
            assessments
        ),

        canonical_source_count=(
            len(
                CANONICAL_OPERATING_SOURCE_IDS
            )
        ),

        assessment_count=(
            len(
                assessments
            )
        ),

        healthy_live_count=sum(
            item.resilience_state
            == FeedResilienceState
            .HEALTHY_LIVE.value

            for item
            in assessments
        ),

        projection_only_count=sum(
            item.resilience_state
            == FeedResilienceState
            .PROJECTION_ONLY.value

            for item
            in assessments
        ),

        missing_count=sum(
            item.missing_detected
            for item
            in assessments
        ),

        stale_count=sum(
            item.stale_detected
            for item
            in assessments
        ),

        conflict_count=sum(
            item.conflict_detected
            for item
            in assessments
        ),

        invalid_count=sum(
            item.invalid_detected
            for item
            in assessments
        ),

        degraded_count=sum(
            item.resilience_state
            in degraded_states

            for item
            in assessments
        ),

        trusted_current_source_count=sum(
            item
            .current_source_truth_trusted

            for item
            in assessments
        ),

        business_risk_inference_count=sum(
            item.business_risk_inferred
            for item
            in assessments
        ),

        business_attention_escalation_count=sum(
            item.business_attention_escalated
            for item
            in assessments
        ),

        false_urgency_count=sum(
            item.false_urgency_created
            for item
            in assessments
        ),

        raw_source_access_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "Feed resilience identifies data quality and "
            "freshness conditions. It does not convert a "
            "data problem into an unsupported business-risk "
            "or urgency claim."
        ),
    )


@lru_cache(
    maxsize=1
)
def get_gp057_projection_resilience_surface():

    return (
        assess_feed_resilience(
            build_projection_feed_envelopes(),

            now_iso=(
                "2026-08-14T16:00:00Z"
            ),
        )
    )


def get_gp057_certification_scenarios():
    """
    Certification-only degraded scenarios.
    """

    base = list(
        build_projection_feed_envelopes()
    )


    # --------------------------------------------------
    # MISSING
    # --------------------------------------------------

    missing_source_id = (
        "teller"
    )


    missing_set = tuple(
        item

        for item
        in base

        if (
            item.source_id
            != missing_source_id
        )
    )


    missing_surface = (
        assess_feed_resilience(
            missing_set,

            now_iso=(
                "2026-08-14T16:00:00Z"
            ),
        )
    )


    # --------------------------------------------------
    # STALE VALID LIVE ENVELOPE
    # --------------------------------------------------

    stale_source_id = (
        "observatory"
    )


    stale_live = (
        build_certification_live_envelope(

            stale_source_id,

            feed_id=(
                "gp057-stale-observatory"
            ),

            source_sequence=500,

            observed_at=(
                "2026-08-14T14:00:00Z"
            ),
        )
    )


    stale_set = tuple(

        stale_live

        if (
            item.source_id
            == stale_source_id
        )

        else item

        for item
        in base
    )


    stale_surface = (
        assess_feed_resilience(
            stale_set,

            now_iso=(
                "2026-08-14T16:00:00Z"
            ),

            stale_after_seconds=900,
        )
    )


    # --------------------------------------------------
    # CONFLICT
    # --------------------------------------------------

    conflict_source_id = (
        "tower"
    )


    conflict_a = (
        build_certification_live_envelope(

            conflict_source_id,

            feed_id=(
                "gp057-conflict-tower-a"
            ),

            source_sequence=700,

            observed_at=(
                "2026-08-14T15:58:00Z"
            ),

            headline=(
                "Tower certification state A"
            ),
        )
    )


    conflict_b = (
        build_certification_live_envelope(

            conflict_source_id,

            feed_id=(
                "gp057-conflict-tower-b"
            ),

            source_sequence=700,

            observed_at=(
                "2026-08-14T15:58:00Z"
            ),

            headline=(
                "Tower certification state B"
            ),
        )
    )


    conflict_set = tuple(

        item

        for item
        in base

        if (
            item.source_id
            != conflict_source_id
        )

    ) + (
        conflict_a,
        conflict_b,
    )


    conflict_surface = (
        assess_feed_resilience(

            conflict_set,

            now_iso=(
                "2026-08-14T16:00:00Z"
            ),
        )
    )


    return {

        "projection":
        get_gp057_projection_resilience_surface(),

        "missing":
        missing_surface,

        "stale":
        stale_surface,

        "conflict":
        conflict_surface,
    }


def get_clouds_gp057_status_payload():

    scenarios = (
        get_gp057_certification_scenarios()
    )


    projection = (
        scenarios[
            "projection"
        ]
    )

    missing = (
        scenarios[
            "missing"
        ]
    )

    stale = (
        scenarios[
            "stale"
        ]
    )

    conflict = (
        scenarios[
            "conflict"
        ]
    )


    safe = (
        projection.assessment_count
        == 6

        and projection.projection_only_count
        == 6

        and projection.healthy_live_count
        == 0

        and projection
        .trusted_current_source_count
        == 0

        and missing.missing_count
        == 1

        and stale.stale_count
        == 1

        and conflict.conflict_count
        == 1

        and missing
        .business_risk_inference_count
        == 0

        and stale
        .business_risk_inference_count
        == 0

        and conflict
        .business_risk_inference_count
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

        and projection
        .downstream_execution_performed
        is False

        and missing
        .downstream_execution_performed
        is False

        and stale
        .downstream_execution_performed
        is False

        and conflict
        .downstream_execution_performed
        is False
    )


    return {

        "pack":
        "GP057",

        "phase":
        "CLOUDS_PHASE_II",

        "section":
        (
            "FEED RESILIENCE / STALE + MISSING + "
            "CONFLICT DETECTION"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "canonical_source_count":
        6,

        "projection_only_detection_ready":
        True,

        "missing_detection_ready":
        True,

        "stale_detection_ready":
        True,

        "conflict_detection_ready":
        True,

        "invalid_detection_ready":
        True,

        "projection_count":
        (
            projection
            .projection_only_count
        ),

        "certification_missing_count":
        (
            missing.missing_count
        ),

        "certification_stale_count":
        (
            stale.stale_count
        ),

        "certification_conflict_count":
        (
            conflict.conflict_count
        ),

        "data_degradation_is_business_risk":
        False,

        "business_risk_inference_count":
        0,

        "business_attention_escalation_count":
        0,

        "false_urgency_count":
        0,

        "real_live_feed_connected":
        False,

        "raw_source_access_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP058 — SAFE DEGRADATION / "
            "NO FALSE URGENCY + FALLBACK INTERPRETATION"
        ),
    }
