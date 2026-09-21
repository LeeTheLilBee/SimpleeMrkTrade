from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

from web.ob_canonical_reasoning_context_spine import (
    GateVerdict,
    SpineReason,
    SpineState,
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
)
from web.ob_evidence_lineage import (
    EvidenceLineage,
    TraceStatus,
)
from web.ob_foundation_integration_closure import (
    build_verified_authority_artifact,
)
from web.ob_observation_instrument_binding import (
    ScopeBindingState,
    ScopeReasoningEligibility,
    build_instrument_identity,
    assess_instrument_binding,
)
from web.ob_observation_lifecycle import (
    CurrentReasoningEligibility,
    ObservationLifecycleAssessment,
    ObservationLifecycleState,
    RetentionState,
)
from web.ob_observation_rehabilitation import (
    RehabilitationReview,
    RehabilitationState,
)
from web.ob_observation_revocation import (
    InvalidationState,
    ObservationRevocationAssessment,
    RevokedReasoningUse,
)
from web.ob_observation_temporal_validity import (
    MarketSession,
    TemporalReasoningEligibility,
    TemporalValidityAssessment,
    TemporalValidityState,
)
from web.ob_observation_versioning import (
    build_version_history,
    create_initial_version,
)


BASE = dict(
    observation_id="OBS-011-015",
    observation_version=1,
    reasoning_target_id="TARGET-011-015",
    symbol="AAPL",
    instrument_kind="EQUITY",
)


def verdict(gate, native):
    artifact = build_verified_authority_artifact(
        gate=gate,
        native_authority=native,
        **BASE,
    )
    return artifact.verdict


def test_lineage_uses_trace_status_not_generic_fallback():
    base = EvidenceLineage(
        observation_id="OBS-011-015",
        steps=(),
        trace_status=TraceStatus.COMPLETE,
        trace_hash="trace",
    )

    assert verdict("lineage", base) == GateVerdict.ALLOW.value
    assert verdict(
        "lineage",
        replace(base, trace_status=TraceStatus.PARTIAL),
    ) == GateVerdict.REVIEW.value
    assert verdict(
        "lineage",
        replace(base, trace_status=TraceStatus.BROKEN),
    ) == GateVerdict.BLOCK.value
    assert verdict(
        "lineage",
        replace(base, trace_status=TraceStatus.UNKNOWN),
    ) == GateVerdict.UNKNOWN.value


def test_current_version_requires_relational_history():
    version = create_initial_version(
        observation_id="OBS-011-015",
        effective_state="TRUSTED",
        confidence="HIGH",
        lineage_hash="trace",
    )

    # Bare version cannot prove that it is the current version.
    assert verdict(
        "current_version",
        version,
    ) == GateVerdict.UNKNOWN.value

    history = build_version_history((version,))

    assert verdict(
        "current_version",
        history,
    ) == GateVerdict.ALLOW.value


def test_lifecycle_uses_reasoning_eligibility():
    base = ObservationLifecycleAssessment(
        version_status="CURRENT",
        effective_state="TRUSTED",
        lifecycle=ObservationLifecycleState.ACTIVE,
        reasoning_eligibility=CurrentReasoningEligibility.ELIGIBLE,
        retention=RetentionState.HOT,
        reasons=("eligible",),
    )

    assert verdict("lifecycle", base) == GateVerdict.ALLOW.value
    assert verdict(
        "lifecycle",
        replace(
            base,
            reasoning_eligibility=CurrentReasoningEligibility.REVIEW_ONLY,
        ),
    ) == GateVerdict.REVIEW.value
    assert verdict(
        "lifecycle",
        replace(
            base,
            reasoning_eligibility=CurrentReasoningEligibility.INELIGIBLE,
        ),
    ) == GateVerdict.BLOCK.value


def test_revocation_uses_invalidation_and_reasoning_use():
    base = ObservationRevocationAssessment(
        observation_id="OBS-011-015",
        version=1,
        invalidation=InvalidationState.VALID,
        reason=None,
        reasoning_use=RevokedReasoningUse.CURRENT_TRUTH_ALLOWED,
        original_effective_state="TRUSTED",
        lineage_hash="trace",
        notes=("valid",),
    )

    assert verdict("revocation", base) == GateVerdict.ALLOW.value

    review = replace(
        base,
        invalidation=InvalidationState.REVIEW_REQUIRED,
        reasoning_use=RevokedReasoningUse.UNKNOWN,
    )
    assert verdict("revocation", review) == GateVerdict.REVIEW.value

    revoked = replace(
        base,
        invalidation=InvalidationState.REVOKED,
        reasoning_use=RevokedReasoningUse.HISTORICAL_WITH_WARNING_ONLY,
    )
    assert verdict("revocation", revoked) == GateVerdict.BLOCK.value


def test_rehabilitation_uses_native_rehabilitation_state():
    base = RehabilitationReview(
        observation_id="OBS-011-015",
        revoked_version=1,
        revoked_lineage_hash="old-trace",
        state=RehabilitationState.REVIEW_REQUIRED,
        reason=None,
        review_note="review",
        new_lineage_hash=None,
    )

    assert verdict(
        "rehabilitation",
        base,
    ) == GateVerdict.REVIEW.value

    approved = replace(
        base,
        state=RehabilitationState.APPROVED_FOR_NEW_VERSION,
        new_lineage_hash="new-trace",
    )

    assert verdict(
        "rehabilitation",
        approved,
    ) == GateVerdict.ALLOW.value

    rejected = replace(
        base,
        state=RehabilitationState.REJECTED,
    )

    assert verdict(
        "rehabilitation",
        rejected,
    ) == GateVerdict.BLOCK.value


def test_temporal_validity_uses_state_and_reasoning_eligibility():
    now = datetime(2026, 9, 21, 14, 0, tzinfo=timezone.utc)

    base = TemporalValidityAssessment(
        state=TemporalValidityState.VALID_NOW,
        reasoning_eligibility=TemporalReasoningEligibility.ELIGIBLE,
        evaluated_at=now,
        observation_trading_date=date(2026, 9, 21),
        current_trading_date=date(2026, 9, 21),
        observation_session=MarketSession.REGULAR,
        current_session=MarketSession.REGULAR,
        valid_from=now - timedelta(minutes=5),
        valid_until=now + timedelta(minutes=5),
        reasons=("valid",),
    )

    assert verdict(
        "temporal_validity",
        base,
    ) == GateVerdict.ALLOW.value

    blocked = replace(
        base,
        state=TemporalValidityState.OUT_OF_WINDOW,
        reasoning_eligibility=TemporalReasoningEligibility.INELIGIBLE,
    )

    assert verdict(
        "temporal_validity",
        blocked,
    ) == GateVerdict.BLOCK.value


def test_instrument_binding_uses_exact_scope_state():
    identity = build_instrument_identity(
        symbol="AAPL",
        instrument_kind="EQUITY",
    )

    matched = assess_instrument_binding(
        observation=identity,
        target=identity,
    )

    assert matched.state is ScopeBindingState.MATCH
    assert (
        matched.reasoning_eligibility
        is ScopeReasoningEligibility.ELIGIBLE
    )
    assert verdict(
        "instrument_binding",
        matched,
    ) == GateVerdict.ALLOW.value

    other = build_instrument_identity(
        symbol="MSFT",
        instrument_kind="EQUITY",
    )

    mismatch = assess_instrument_binding(
        observation=identity,
        target=other,
    )

    assert verdict(
        "instrument_binding",
        mismatch,
    ) == GateVerdict.BLOCK.value


def _context():
    instrument = build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="EQUITY",
    )

    return build_canonical_context_identity(
        context_id="CTX-011-015",
        observation_id="OBS-011-015",
        observation_version=1,
        lineage_hash="trace",
        provenance_identity="prov",
        reasoning_target_id="TARGET-011-015",
        instrument=instrument,
        operating_mode="PAPER",
        effective_policy_id="POLICY-PAPER",
        effective_policy_hash="POLICY-PAPER-HASH",
        purpose="analytical reasoning",
    )


def _authorities(*, mismatch_gate=None):
    context = _context()

    gates = (
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

    result = {}

    for gate in gates:
        policy_id = context.effective_policy_id
        policy_hash = context.effective_policy_hash

        if gate == mismatch_gate:
            policy_hash = "FORGED-POLICY-HASH"

        result[gate] = authority_result(
            gate=gate,
            observation_id=context.observation_id,
            observation_version=context.observation_version,
            reasoning_target_id=context.reasoning_target_id,
            symbol=context.instrument.symbol,
            instrument_kind=context.instrument.instrument_kind,
            verdict=GateVerdict.ALLOW,
            reason=f"{gate} allow",
            authority_identity=f"AUTH-{gate}",
            authority_hash=f"HASH-{gate}",
            effective_policy_id=policy_id,
            effective_policy_hash=policy_hash,
        )

    return result


def test_policy_mismatch_is_reachable_and_fails_closed():
    context = _context()

    receipt = build_canonical_reasoning_context_receipt(
        context=context,
        authorities=_authorities(
            mismatch_gate="freshness",
        ),
    )

    assert receipt.state is SpineState.UNKNOWN
    assert receipt.reason is SpineReason.POLICY_MISMATCH
    assert receipt.certified_native_authority is False
    assert receipt.certified_authority_hash is None


def test_matching_policy_identity_preserves_eligible_context():
    context = _context()

    receipt = build_canonical_reasoning_context_receipt(
        context=context,
        authorities=_authorities(),
    )

    assert receipt.state is SpineState.ELIGIBLE
    assert receipt.reason is SpineReason.CONTEXT_INTEGRITY_SATISFIED
