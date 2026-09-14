from pathlib import Path

from web.ob_effective_observation import (
    ConfidenceLevel,
    EffectiveObservationState,
    effective_observation_snapshot,
    may_be_used_for_normal_reasoning,
    must_not_be_used_as_observation_truth,
    must_remain_quarantined,
    requires_visible_caution,
    synthesize_effective_observation,
)


ROOT = Path(__file__).resolve().parents[1]


def synth(
    *,
    source_authority="AUTHORITATIVE",
    freshness="FRESH",
    corroboration="CORROBORATED",
    quality="VALID",
    anomaly="NORMAL",
    disposition="ACCEPT",
):
    return synthesize_effective_observation(
        source_authority=source_authority,
        freshness=freshness,
        corroboration=corroboration,
        quality=quality,
        anomaly=anomaly,
        disposition=disposition,
    )


def test_obdata031_effective_state_identity():
    assert [item.value for item in EffectiveObservationState] == [
        "TRUSTED",
        "USABLE",
        "CAUTION",
        "QUARANTINED",
        "UNUSABLE",
        "UNKNOWN",
    ]

    assert [item.value for item in ConfidenceLevel] == [
        "HIGH",
        "MODERATE",
        "LOW",
        "NONE",
        "UNKNOWN",
    ]


def test_obdata032_all_green_layers_produce_trusted_high_confidence():
    result = synth()

    assert result.state is EffectiveObservationState.TRUSTED
    assert result.confidence is ConfidenceLevel.HIGH
    assert may_be_used_for_normal_reasoning(result)


def test_obdata032_single_source_can_be_usable_without_fake_corroboration():
    result = synth(
        corroboration="SINGLE_SOURCE",
    )

    assert result.state is EffectiveObservationState.USABLE
    assert result.confidence is ConfidenceLevel.MODERATE
    assert may_be_used_for_normal_reasoning(result)


def test_obdata032_aging_data_produces_visible_caution():
    result = synth(
        freshness="AGING",
    )

    assert result.state is EffectiveObservationState.CAUTION
    assert result.confidence is ConfidenceLevel.MODERATE
    assert requires_visible_caution(result)


def test_obdata032_minor_disagreement_produces_visible_caution():
    result = synth(
        corroboration="MINOR_DISAGREEMENT",
    )

    assert result.state is EffectiveObservationState.CAUTION
    assert result.confidence is ConfidenceLevel.MODERATE


def test_obdata032_stale_data_cannot_become_trusted():
    result = synth(
        freshness="STALE",
    )

    assert result.state is EffectiveObservationState.CAUTION
    assert result.confidence is ConfidenceLevel.LOW
    assert not may_be_used_for_normal_reasoning(result)


def test_obdata032_conflicted_data_cannot_become_trusted():
    result = synth(
        corroboration="CONFLICTED",
    )

    assert result.state is EffectiveObservationState.CAUTION
    assert result.confidence is ConfidenceLevel.LOW


def test_obdata032_outlier_remains_quarantined():
    result = synth(
        anomaly="OUTLIER",
        disposition="QUARANTINE",
    )

    assert result.state is EffectiveObservationState.QUARANTINED
    assert result.confidence is ConfidenceLevel.LOW
    assert must_remain_quarantined(result)


def test_obdata032_invalid_data_is_unusable():
    result = synth(
        quality="INVALID",
        anomaly="IMPOSSIBLE",
        disposition="REJECT",
    )

    assert result.state is EffectiveObservationState.UNUSABLE
    assert result.confidence is ConfidenceLevel.NONE
    assert must_not_be_used_as_observation_truth(result)


def test_obdata032_rejected_data_is_unusable_even_if_other_layers_look_good():
    result = synth(
        disposition="REJECT",
    )

    assert result.state is EffectiveObservationState.UNUSABLE
    assert result.confidence is ConfidenceLevel.NONE


def test_obdata033_unknown_layer_prevents_fake_confidence():
    result = synth(
        source_authority="UNKNOWN",
    )

    assert result.state is EffectiveObservationState.UNKNOWN
    assert result.confidence is ConfidenceLevel.UNKNOWN
    assert must_not_be_used_as_observation_truth(result)


def test_obdata033_advisory_source_can_be_usable_but_not_trusted_high():
    result = synth(
        source_authority="ADVISORY",
    )

    assert result.state is EffectiveObservationState.USABLE
    assert result.confidence is ConfidenceLevel.MODERATE


def test_obdata033_confidence_does_not_override_layers():
    result = synth(
        source_authority="AUTHORITATIVE",
        freshness="EXPIRED",
        corroboration="CORROBORATED",
        quality="VALID",
        anomaly="NORMAL",
        disposition="ACCEPT",
    )

    assert result.layers.freshness == "EXPIRED"
    assert result.state is EffectiveObservationState.CAUTION
    assert result.confidence is ConfidenceLevel.LOW


def test_obdata034_snapshot_explains_every_layer():
    result = synth()

    snapshot = effective_observation_snapshot(
        result
    )

    assert snapshot["state"] == "TRUSTED"
    assert snapshot["confidence"] == "HIGH"

    assert snapshot["layers"] == {
        "source_authority": "AUTHORITATIVE",
        "freshness": "FRESH",
        "corroboration": "CORROBORATED",
        "quality": "VALID",
        "anomaly": "NORMAL",
        "disposition": "ACCEPT",
    }

    assert isinstance(
        snapshot["reasons"],
        list,
    )

    assert isinstance(
        snapshot["limitations"],
        list,
    )


def test_obdata034_module_has_no_execution_authority():
    source = (
        ROOT
        / "web/ob_effective_observation.py"
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


def test_obdata034_no_opaque_numeric_confidence_score():
    source = (
        ROOT
        / "web/ob_effective_observation.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "confidence_score",
        "confidenceScore",
        "certainty_score",
        "trust_score",
    )

    for token in forbidden:
        assert token not in source


def test_obdata035_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata031_035_effective_observation_synthesis_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata031_035_effective_observation_synthesis_authority_handoff.md"
    ).is_file()


def test_obdata035_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata031_035_effective_observation_synthesis_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"source_authority_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"anomaly_override": false' in evidence
    assert '"opaque_confidence_score": false' in evidence
    assert '"fake_certainty": false' in evidence
