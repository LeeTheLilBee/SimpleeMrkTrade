from pathlib import Path

import math
import pytest

from web.ob_observation_quality import (
    AnomalyStatus,
    ObservationDisposition,
    ObservationQuality,
    ObservationQualityPolicy,
    evaluate_against_peer_group,
    evaluate_observation_quality,
    must_quarantine,
    must_reject,
    quality_snapshot,
    requires_quality_review,
    robust_reference_value,
    usable_without_review,
)


ROOT = Path(__file__).resolve().parents[1]


def test_obdata026_quality_identity():
    assert [item.value for item in ObservationQuality] == [
        "VALID",
        "DEGRADED",
        "INVALID",
        "UNKNOWN",
    ]

    assert [item.value for item in AnomalyStatus] == [
        "NORMAL",
        "SUSPECT",
        "OUTLIER",
        "IMPOSSIBLE",
        "UNKNOWN",
    ]

    assert [item.value for item in ObservationDisposition] == [
        "ACCEPT",
        "REVIEW",
        "QUARANTINE",
        "REJECT",
        "UNKNOWN",
    ]


def test_obdata027_normal_value_is_accepted():
    result = evaluate_observation_quality(
        100.0,
        reference_value=100.0,
    )

    assert result.quality is ObservationQuality.VALID
    assert result.anomaly is AnomalyStatus.NORMAL
    assert result.disposition is ObservationDisposition.ACCEPT
    assert usable_without_review(result)


def test_obdata027_non_numeric_is_rejected():
    result = evaluate_observation_quality(
        "not-a-number"
    )

    assert result.quality is ObservationQuality.INVALID
    assert result.anomaly is AnomalyStatus.IMPOSSIBLE
    assert must_reject(result)


def test_obdata027_nan_is_rejected():
    result = evaluate_observation_quality(
        float("nan")
    )

    assert result.quality is ObservationQuality.INVALID
    assert result.anomaly is AnomalyStatus.IMPOSSIBLE
    assert must_reject(result)


def test_obdata027_infinity_is_rejected():
    result = evaluate_observation_quality(
        float("inf")
    )

    assert result.quality is ObservationQuality.INVALID
    assert result.anomaly is AnomalyStatus.IMPOSSIBLE
    assert must_reject(result)


def test_obdata027_impossible_negative_market_value_is_rejected():
    result = evaluate_observation_quality(
        -100.0
    )

    assert result.quality is ObservationQuality.INVALID
    assert result.anomaly is AnomalyStatus.IMPOSSIBLE
    assert result.disposition is ObservationDisposition.REJECT


def test_obdata027_zero_can_be_policy_specific():
    strict = evaluate_observation_quality(
        0.0
    )

    assert strict.disposition is ObservationDisposition.REJECT

    permissive = evaluate_observation_quality(
        0.0,
        policy=ObservationQualityPolicy(
            allow_zero=True,
            allow_negative=False,
        ),
    )

    assert permissive.disposition is ObservationDisposition.ACCEPT


def test_obdata028_suspect_deviation_requires_review():
    policy = ObservationQualityPolicy(
        allow_zero=False,
        allow_negative=False,
        suspect_relative_deviation=0.05,
        outlier_relative_deviation=0.20,
    )

    result = evaluate_observation_quality(
        108.0,
        reference_value=100.0,
        policy=policy,
    )

    assert result.anomaly is AnomalyStatus.SUSPECT
    assert result.disposition is ObservationDisposition.REVIEW
    assert requires_quality_review(result)


def test_obdata028_outlier_is_quarantined():
    policy = ObservationQualityPolicy(
        allow_zero=False,
        allow_negative=False,
        suspect_relative_deviation=0.05,
        outlier_relative_deviation=0.20,
    )

    result = evaluate_observation_quality(
        130.0,
        reference_value=100.0,
        policy=policy,
    )

    assert result.anomaly is AnomalyStatus.OUTLIER
    assert result.disposition is ObservationDisposition.QUARANTINE
    assert must_quarantine(result)


def test_obdata028_outlier_is_not_silently_replaced():
    result = evaluate_observation_quality(
        150.0,
        reference_value=100.0,
    )

    assert result.value == 150.0
    assert result.reference_value == 100.0
    assert result.value != result.reference_value


def test_robust_reference_value_is_median_anchor_only():
    result = robust_reference_value(
        [
            100.0,
            101.0,
            500.0,
        ]
    )

    assert result == 101.0


def test_peer_group_anomaly_uses_median_anchor():
    result = evaluate_against_peer_group(
        500.0,
        [
            100.0,
            101.0,
            102.0,
        ],
    )

    assert result.reference_value == 101.0
    assert result.anomaly is AnomalyStatus.OUTLIER
    assert result.disposition is ObservationDisposition.QUARANTINE


def test_valid_disagreement_is_not_automatically_invalid_data():
    policy = ObservationQualityPolicy(
        allow_zero=False,
        allow_negative=False,
        suspect_relative_deviation=0.20,
        outlier_relative_deviation=0.50,
    )

    result = evaluate_observation_quality(
        110.0,
        reference_value=100.0,
        policy=policy,
    )

    assert result.quality is ObservationQuality.VALID
    assert result.anomaly is AnomalyStatus.NORMAL
    assert result.disposition is ObservationDisposition.ACCEPT


def test_policy_bounds_are_enforced():
    policy = ObservationQualityPolicy(
        allow_zero=True,
        allow_negative=True,
        minimum_value=-10,
        maximum_value=10,
    )

    low = evaluate_observation_quality(
        -20,
        policy=policy,
    )

    high = evaluate_observation_quality(
        20,
        policy=policy,
    )

    assert must_reject(low)
    assert must_reject(high)


def test_invalid_policy_threshold_order_rejected():
    with pytest.raises(ValueError):
        ObservationQualityPolicy(
            suspect_relative_deviation=0.30,
            outlier_relative_deviation=0.20,
        )


def test_obdata029_snapshot_is_descriptive_only():
    result = evaluate_observation_quality(
        100.0,
        reference_value=100.0,
    )

    snapshot = quality_snapshot(result)

    assert snapshot["quality"] == "VALID"
    assert snapshot["anomaly"] == "NORMAL"
    assert snapshot["disposition"] == "ACCEPT"
    assert snapshot["value"] == 100.0
    assert snapshot["reference_value"] == 100.0


def test_obdata029_module_contains_no_execution_surface():
    source = (
        ROOT
        / "web/ob_observation_quality.py"
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


def test_obdata030_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata026_030_observation_quality_anomaly_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata026_030_observation_quality_anomaly_authority_handoff.md"
    ).is_file()


def test_obdata030_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata026_030_observation_quality_anomaly_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"fabricated_correction": false' in evidence
    assert '"silent_anomaly_suppression": false' in evidence
