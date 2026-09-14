from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from web.ob_observation_freshness import (
    DEFAULT_FRESHNESS_POLICIES,
    FreshnessPolicy,
    FreshnessStatus,
    FreshnessUse,
    ObservationClass,
    classify_age,
    evaluate_freshness,
    freshness_snapshot,
    must_not_be_treated_as_current,
    propagate_derived_freshness,
    requires_freshness_review,
    suitable_for_current_analysis,
    worst_freshness_status,
)


ROOT = Path(__file__).resolve().parents[1]


def provenance_at(
    observed_at: datetime,
    retrieved_at: datetime | None = None,
):
    return SimpleNamespace(
        observed_at=observed_at,
        retrieved_at=(
            retrieved_at
            if retrieved_at is not None
            else observed_at
        ),
    )


def test_obdata016_exact_freshness_identity():
    assert [item.value for item in FreshnessStatus] == [
        "FRESH",
        "AGING",
        "STALE",
        "EXPIRED",
        "UNKNOWN",
    ]


def test_obdata017_default_policies_are_context_specific():
    quote = DEFAULT_FRESHNESS_POLICIES[
        ObservationClass.REALTIME_QUOTE
    ]

    reference = DEFAULT_FRESHNESS_POLICIES[
        ObservationClass.REFERENCE_DATA
    ]

    assert quote.fresh_for < reference.fresh_for
    assert quote.aging_for < reference.aging_for
    assert quote.expires_after < reference.expires_after


def test_obdata017_policy_thresholds_are_ordered():
    with pytest.raises(ValueError):
        FreshnessPolicy(
            fresh_for=timedelta(minutes=10),
            aging_for=timedelta(minutes=5),
            expires_after=timedelta(minutes=20),
        )

    with pytest.raises(ValueError):
        FreshnessPolicy(
            fresh_for=timedelta(minutes=1),
            aging_for=timedelta(minutes=5),
            expires_after=timedelta(minutes=2),
        )


def test_obdata017_boundary_classification():
    policy = FreshnessPolicy(
        fresh_for=timedelta(seconds=10),
        aging_for=timedelta(seconds=20),
        expires_after=timedelta(seconds=30),
    )

    assert classify_age(
        timedelta(seconds=5),
        policy,
    ) is FreshnessStatus.FRESH

    assert classify_age(
        timedelta(seconds=15),
        policy,
    ) is FreshnessStatus.AGING

    assert classify_age(
        timedelta(seconds=25),
        policy,
    ) is FreshnessStatus.STALE

    assert classify_age(
        timedelta(seconds=35),
        policy,
    ) is FreshnessStatus.EXPIRED


def test_authoritative_provenance_can_still_be_stale():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    observation = provenance_at(
        now - timedelta(minutes=3)
    )

    assessment = evaluate_freshness(
        observation,
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    assert assessment.status is FreshnessStatus.STALE
    assert assessment.use is FreshnessUse.DO_NOT_TREAT_AS_CURRENT
    assert not suitable_for_current_analysis(
        assessment
    )


def test_same_age_can_have_different_contextual_freshness():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    observation = provenance_at(
        now - timedelta(minutes=10)
    )

    quote = evaluate_freshness(
        observation,
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    reference = evaluate_freshness(
        observation,
        ObservationClass.REFERENCE_DATA,
        now=now,
    )

    assert quote.status is FreshnessStatus.EXPIRED
    assert reference.status is FreshnessStatus.FRESH


def test_future_observation_becomes_unknown():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    observation = provenance_at(
        now + timedelta(seconds=5)
    )

    assessment = evaluate_freshness(
        observation,
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    assert assessment.status is FreshnessStatus.UNKNOWN
    assert assessment.age_seconds is None


def test_naive_timestamp_is_rejected():
    naive = datetime(
        2026,
        9,
        14,
        15,
        0,
    )

    with pytest.raises(ValueError):
        evaluate_freshness(
            provenance_at(naive),
            ObservationClass.REALTIME_QUOTE,
            now=datetime(
                2026,
                9,
                14,
                15,
                1,
                tzinfo=timezone.utc,
            ),
        )


def test_obdata018_derived_result_cannot_be_fresher_than_stalest_input():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    own = evaluate_freshness(
        provenance_at(
            now - timedelta(seconds=2)
        ),
        ObservationClass.DERIVED,
        now=now,
    )

    fresh_input = evaluate_freshness(
        provenance_at(
            now - timedelta(seconds=3)
        ),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    stale_input = evaluate_freshness(
        provenance_at(
            now - timedelta(minutes=3)
        ),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    propagated = propagate_derived_freshness(
        own,
        [
            fresh_input,
            stale_input,
        ],
    )

    assert own.status is FreshnessStatus.FRESH
    assert stale_input.status is FreshnessStatus.STALE
    assert propagated.status is FreshnessStatus.STALE
    assert propagated.use is FreshnessUse.DO_NOT_TREAT_AS_CURRENT


def test_derived_result_without_input_evidence_is_unknown():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    own = evaluate_freshness(
        provenance_at(now),
        ObservationClass.DERIVED,
        now=now,
    )

    result = propagate_derived_freshness(
        own,
        [],
    )

    assert result.status is FreshnessStatus.UNKNOWN


def test_worst_status_is_monotonic():
    assert worst_freshness_status(
        [
            FreshnessStatus.FRESH,
            FreshnessStatus.AGING,
            FreshnessStatus.STALE,
        ]
    ) is FreshnessStatus.STALE

    assert worst_freshness_status(
        []
    ) is FreshnessStatus.UNKNOWN


def test_obdata019_decision_use_boundary():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    fresh = evaluate_freshness(
        provenance_at(
            now - timedelta(seconds=2)
        ),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    aging = evaluate_freshness(
        provenance_at(
            now - timedelta(seconds=30)
        ),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    stale = evaluate_freshness(
        provenance_at(
            now - timedelta(minutes=2)
        ),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    assert suitable_for_current_analysis(fresh)

    assert not suitable_for_current_analysis(aging)
    assert requires_freshness_review(aging)

    assert must_not_be_treated_as_current(stale)


def test_freshness_snapshot_is_descriptive_only():
    now = datetime(
        2026,
        9,
        14,
        15,
        0,
        tzinfo=timezone.utc,
    )

    assessment = evaluate_freshness(
        provenance_at(now),
        ObservationClass.REALTIME_QUOTE,
        now=now,
    )

    snapshot = freshness_snapshot(
        assessment
    )

    assert snapshot["status"] == "FRESH"
    assert snapshot["use"] == "CURRENT_ANALYSIS_OK"
    assert "observation_class" in snapshot
    assert "observed_at" in snapshot
    assert "retrieved_at" in snapshot


def test_obdata019_module_contains_no_execution_surface():
    source = (
        ROOT
        / "web/ob_observation_freshness.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "autoSelectContract(",
        "moveCapital(",
        "unlockHybrid(",
        "unlockAutomated(",
        "unlockManualLive(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata020_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata016_020_observation_freshness_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata016_020_observation_freshness_authority_handoff.md"
    ).is_file()


def test_obdata020_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata016_020_observation_freshness_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"hybrid_execution": false' in evidence
    assert '"automated_execution": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"source_authority_override": false' in evidence
