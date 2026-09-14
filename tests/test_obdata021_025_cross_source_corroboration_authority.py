from pathlib import Path

import pytest

from web.ob_cross_source_corroboration import (
    ConfidenceUse,
    CorroborationPolicy,
    CorroborationStatus,
    SourceObservation,
    assess_corroboration,
    corroborated_for_normal_analysis,
    disagreement_snapshot,
    must_not_be_treated_as_settled,
    requires_disagreement_review,
)


ROOT = Path(__file__).resolve().parents[1]


def obs(
    source_id,
    value,
    *,
    authoritative=False,
    fresh_enough=True,
):
    return SourceObservation(
        source_id=source_id,
        value=value,
        authoritative=authoritative,
        fresh_enough=fresh_enough,
    )


def test_obdata021_corroboration_identity():
    assert [item.value for item in CorroborationStatus] == [
        "SINGLE_SOURCE",
        "CORROBORATED",
        "MINOR_DISAGREEMENT",
        "MATERIAL_DISAGREEMENT",
        "CONFLICTED",
        "UNKNOWN",
    ]


def test_obdata022_identical_independent_sources_corroborate():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
            obs("provider-b", 100.0),
        ]
    )

    assert result.status is CorroborationStatus.CORROBORATED
    assert result.use is ConfidenceUse.NORMAL_ANALYSIS
    assert result.relative_spread == 0.0


def test_obdata022_single_source_is_not_fabricated_consensus():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
        ]
    )

    assert result.status is CorroborationStatus.SINGLE_SOURCE
    assert result.eligible_source_count == 1


def test_duplicate_source_is_not_independent_corroboration():
    with pytest.raises(ValueError):
        assess_corroboration(
            [
                obs("provider-a", 100.0),
                obs("provider-a", 100.0),
            ]
        )


def test_obdata022_minor_disagreement_is_explicit():
    policy = CorroborationPolicy(
        corroborated_relative_spread=0.001,
        minor_disagreement_relative_spread=0.01,
        material_disagreement_relative_spread=0.03,
    )

    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
            obs("provider-b", 100.5),
        ],
        policy=policy,
    )

    assert result.status is CorroborationStatus.MINOR_DISAGREEMENT
    assert requires_disagreement_review(result)
    assert not corroborated_for_normal_analysis(result)


def test_obdata023_material_disagreement_does_not_become_settled():
    policy = CorroborationPolicy(
        corroborated_relative_spread=0.001,
        minor_disagreement_relative_spread=0.005,
        material_disagreement_relative_spread=0.03,
    )

    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
            obs("provider-b", 102.0),
        ],
        policy=policy,
    )

    assert result.status is CorroborationStatus.MATERIAL_DISAGREEMENT
    assert result.use is ConfidenceUse.DO_NOT_TREAT_AS_SETTLED
    assert must_not_be_treated_as_settled(result)


def test_obdata023_large_disagreement_becomes_conflicted():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
            obs("provider-b", 110.0),
        ]
    )

    assert result.status is CorroborationStatus.CONFLICTED
    assert must_not_be_treated_as_settled(result)


def test_stale_source_is_excluded_from_current_corroboration():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0, fresh_enough=True),
            obs("provider-b", 120.0, fresh_enough=False),
        ]
    )

    assert result.status is CorroborationStatus.SINGLE_SOURCE
    assert result.source_ids == ("provider-a",)
    assert result.values == (100.0,)


def test_all_stale_sources_produce_unknown_not_fake_consensus():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0, fresh_enough=False),
            obs("provider-b", 100.0, fresh_enough=False),
        ]
    )

    assert result.status is CorroborationStatus.UNKNOWN
    assert result.eligible_source_count == 0


def test_authoritative_label_does_not_silently_win_disagreement():
    result = assess_corroboration(
        [
            obs(
                "authoritative-a",
                100.0,
                authoritative=True,
            ),
            obs(
                "corroborating-b",
                110.0,
                authoritative=False,
            ),
        ]
    )

    assert result.status is CorroborationStatus.CONFLICTED
    assert result.center_value == 105.0


def test_obdata024_snapshot_preserves_all_source_values():
    result = assess_corroboration(
        [
            obs("provider-a", 100.0),
            obs("provider-b", 100.0),
        ]
    )

    snapshot = disagreement_snapshot(result)

    assert snapshot["source_ids"] == [
        "provider-a",
        "provider-b",
    ]

    assert snapshot["values"] == [
        100.0,
        100.0,
    ]

    assert snapshot["status"] == "CORROBORATED"


def test_policy_thresholds_must_be_monotonic():
    with pytest.raises(ValueError):
        CorroborationPolicy(
            corroborated_relative_spread=0.02,
            minor_disagreement_relative_spread=0.01,
            material_disagreement_relative_spread=0.03,
        )


def test_obdata024_module_has_no_execution_authority():
    source = (
        ROOT
        / "web/ob_cross_source_corroboration.py"
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


def test_obdata025_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata021_025_cross_source_corroboration_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata021_025_cross_source_corroboration_authority_handoff.md"
    ).is_file()


def test_obdata025_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata021_025_cross_source_corroboration_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"fabricated_consensus": false' in evidence
