from pathlib import Path

import pytest

from web.ob_reasoning_context_composition import (
    CompositionState,
    GateVerdict,
    REQUIRED_GATES,
    blocked_from_current_analytical_reasoning,
    build_reasoning_target,
    compose_reasoning_context,
    composition_snapshot,
    eligible_for_current_analytical_reasoning,
    gate_assessment,
)


ROOT = Path(__file__).resolve().parents[1]


def target():
    return build_reasoning_target(
        target_id="reasoning-target-001",
        observation_id="obs-001",
        observation_version=7,
        target_symbol="SPY",
        target_instrument_kind="ETF",
        purpose="current-market-observation",
    )


def allow_all():
    return {
        name: gate_assessment(
            gate=name,
            verdict=GateVerdict.ALLOW,
            reason=f"{name} explicitly allows current analytical use.",
        )
        for name in REQUIRED_GATES
    }


def test_obdata076_required_gate_identity_exact():
    assert REQUIRED_GATES == (
        "source_provenance",
        "freshness",
        "corroboration",
        "quality",
        "effective_observation",
        "conflict",
        "lineage",
        "current_version",
        "lifecycle",
        "revocation",
        "rehabilitation",
        "temporal_validity",
        "instrument_binding",
    )


def test_obdata076_target_identity_is_explicit():
    result = target()

    assert result.target_id == "reasoning-target-001"
    assert result.observation_id == "obs-001"
    assert result.observation_version == 7
    assert result.target_symbol == "SPY"
    assert result.target_instrument_kind == "ETF"
    assert result.purpose == "current-market-observation"


def test_obdata076_target_requires_valid_identity():
    with pytest.raises(ValueError):
        build_reasoning_target(
            target_id="",
            observation_id="obs",
            observation_version=1,
            target_symbol="SPY",
            target_instrument_kind="ETF",
            purpose="reason",
        )

    with pytest.raises(ValueError):
        build_reasoning_target(
            target_id="target",
            observation_id="obs",
            observation_version=0,
            target_symbol="SPY",
            target_instrument_kind="ETF",
            purpose="reason",
        )


def test_obdata077_all_explicit_allow_is_eligible():
    result = compose_reasoning_context(
        target=target(),
        gates=allow_all(),
    )

    assert result.state is CompositionState.ELIGIBLE
    assert eligible_for_current_analytical_reasoning(result)
    assert not blocked_from_current_analytical_reasoning(result)


def test_obdata077_one_block_blocks_entire_context():
    gates = allow_all()

    gates["revocation"] = gate_assessment(
        gate="revocation",
        verdict=GateVerdict.BLOCK,
        reason="Observation is revoked.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.BLOCKED
    assert result.blocking_gates == (
        "revocation",
    )
    assert not eligible_for_current_analytical_reasoning(result)
    assert blocked_from_current_analytical_reasoning(result)


def test_obdata077_multiple_blocks_are_preserved():
    gates = allow_all()

    gates["temporal_validity"] = gate_assessment(
        gate="temporal_validity",
        verdict=GateVerdict.BLOCK,
        reason="Observation is outside temporal window.",
    )

    gates["instrument_binding"] = gate_assessment(
        gate="instrument_binding",
        verdict=GateVerdict.BLOCK,
        reason="Observation belongs to a different instrument.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.BLOCKED
    assert result.blocking_gates == (
        "temporal_validity",
        "instrument_binding",
    )


def test_obdata078_unknown_fails_closed():
    gates = allow_all()

    gates["freshness"] = gate_assessment(
        gate="freshness",
        verdict=GateVerdict.UNKNOWN,
        reason="Freshness could not be established.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.UNKNOWN
    assert result.unknown_gates == (
        "freshness",
    )
    assert blocked_from_current_analytical_reasoning(result)
    assert not eligible_for_current_analytical_reasoning(result)


def test_obdata078_review_never_becomes_eligible():
    gates = allow_all()

    gates["quality"] = gate_assessment(
        gate="quality",
        verdict=GateVerdict.REVIEW,
        reason="Quality requires explicit review.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.REVIEW_REQUIRED
    assert result.review_gates == (
        "quality",
    )
    assert blocked_from_current_analytical_reasoning(result)
    assert not eligible_for_current_analytical_reasoning(result)


def test_obdata078_block_takes_precedence_over_unknown_and_review():
    gates = allow_all()

    gates["quality"] = gate_assessment(
        gate="quality",
        verdict=GateVerdict.REVIEW,
        reason="Quality requires review.",
    )

    gates["freshness"] = gate_assessment(
        gate="freshness",
        verdict=GateVerdict.UNKNOWN,
        reason="Freshness unknown.",
    )

    gates["revocation"] = gate_assessment(
        gate="revocation",
        verdict=GateVerdict.BLOCK,
        reason="Observation revoked.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.BLOCKED
    assert result.blocking_gates == (
        "revocation",
    )
    assert result.review_gates == (
        "quality",
    )
    assert result.unknown_gates == (
        "freshness",
    )


def test_obdata078_missing_gate_fails_closed():
    gates = allow_all()

    del gates[
        "instrument_binding"
    ]

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    assert result.state is CompositionState.UNKNOWN
    assert "instrument_binding" in result.unknown_gates
    assert not eligible_for_current_analytical_reasoning(result)


def test_obdata078_extra_gate_is_rejected():
    gates = allow_all()

    gates["made_up_gate"] = gate_assessment(
        gate="source_provenance",
        verdict=GateVerdict.ALLOW,
        reason="This mapping key is invalid.",
    )

    with pytest.raises(ValueError):
        compose_reasoning_context(
            target=target(),
            gates=gates,
        )


def test_obdata078_mapping_identity_mismatch_rejected():
    gates = allow_all()

    gates["freshness"] = gate_assessment(
        gate="quality",
        verdict=GateVerdict.ALLOW,
        reason="Wrong identity under freshness key.",
    )

    with pytest.raises(ValueError):
        compose_reasoning_context(
            target=target(),
            gates=gates,
        )


def test_obdata078_gate_verdict_requires_enum():
    with pytest.raises(ValueError):
        gate_assessment(
            gate="freshness",
            verdict="ALLOW",
            reason="Raw string must not bypass enum authority.",
        )


def test_obdata079_snapshot_preserves_target_and_blockers():
    gates = allow_all()

    gates["temporal_validity"] = gate_assessment(
        gate="temporal_validity",
        verdict=GateVerdict.BLOCK,
        reason="Wrong temporal context.",
    )

    result = compose_reasoning_context(
        target=target(),
        gates=gates,
    )

    snapshot = composition_snapshot(
        result
    )

    assert snapshot["target"]["target_id"] == "reasoning-target-001"
    assert snapshot["target"]["observation_id"] == "obs-001"
    assert snapshot["target"]["observation_version"] == 7
    assert snapshot["target"]["target_symbol"] == "SPY"

    assert snapshot["state"] == "BLOCKED"
    assert snapshot["blocking_gates"] == [
        "temporal_validity",
    ]


def test_obdata079_every_gate_reason_survives_snapshot():
    result = compose_reasoning_context(
        target=target(),
        gates=allow_all(),
    )

    snapshot = composition_snapshot(
        result
    )

    assert len(
        snapshot["gates"]
    ) == len(
        REQUIRED_GATES
    )

    assert all(
        item["reason"]
        for item in snapshot["gates"]
    )


def test_obdata079_composition_module_has_no_execution_authority():
    source = (
        ROOT
        / "web/ob_reasoning_context_composition.py"
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
        "unlockManualLive(",
        "unlockHybrid(",
        "unlockAutomated(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata079_no_upstream_override_api():
    source = (
        ROOT
        / "web/ob_reasoning_context_composition.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "overrideSource(",
        "overrideFreshness(",
        "overrideCorroboration(",
        "overrideQuality(",
        "overrideConflict(",
        "overrideLineage(",
        "overrideVersion(",
        "overrideLifecycle(",
        "overrideRevocation(",
        "overrideRehabilitation(",
        "overrideTemporal(",
        "overrideInstrument(",
        "forceEligible(",
        "promoteUnknown(",
        "promoteReview(",
        "ignoreMissingGate(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata080_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata076_080_reasoning_context_composition_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata076_080_reasoning_context_composition_authority_handoff.md"
    ).is_file()


def test_obdata080_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata076_080_reasoning_context_composition_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"contract_auto_selection": false' in evidence
    assert '"manual_live_unlock": false' in evidence
    assert '"hybrid_execution": false' in evidence
    assert '"automated_execution": false' in evidence

    assert '"mode_policy_override": false' in evidence
    assert '"source_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"anomaly_override": false' in evidence
    assert '"synthesis_override": false' in evidence
    assert '"conflict_override": false' in evidence
    assert '"lineage_override": false' in evidence
    assert '"version_override": false' in evidence
    assert '"lifecycle_override": false' in evidence
    assert '"revocation_override": false' in evidence
    assert '"rehabilitation_override": false' in evidence
    assert '"temporal_override": false' in evidence
    assert '"instrument_override": false' in evidence

    assert '"unknown_as_eligible": false' in evidence
    assert '"review_as_eligible": false' in evidence
    assert '"missing_gate_as_eligible": false' in evidence
    assert '"composition_grants_denied_authority": false' in evidence
