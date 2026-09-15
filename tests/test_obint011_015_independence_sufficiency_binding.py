from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_candidate_admission_receipt_binding import (
    admit_receipt_bound_evidence,
    bind_candidate_identity,
    empty_receipt_bound_candidate_set,
    evidence_item_from_context_receipt,
)
from web.ob_candidate_evidence_sufficiency import (
    SufficiencyState,
    build_evidence_requirement,
)
from web.ob_canonical_reasoning_context_spine import (
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
)
from web.ob_independence_sufficiency_binding import (
    BoundEvidenceOrigin,
    build_candidate_independence_receipt,
    build_candidate_sufficiency_receipt,
    build_policy_requirement_set,
    candidate_sufficiency_eligible,
    independence_sufficiency_snapshot,
    verify_candidate_independence_receipt,
    verify_candidate_sufficiency_receipt,
)
from web.ob_reasoning_context_composition import (
    GateVerdict,
    REQUIRED_GATES,
)


def admitted_set():
    instrument = build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
        underlying_symbol="AAPL",
        option_right="CALL",
        strike="250",
        expiration="2026-12-18",
    )

    context = build_canonical_context_identity(
        context_id="CTX-001",
        observation_id="OBS-001",
        observation_version=1,
        lineage_hash="LINEAGE-001",
        provenance_identity="PROV-001",
        reasoning_target_id="TARGET-001",
        instrument=instrument,
        operating_mode="PAPER",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        purpose="analytical reasoning",
    )

    authorities = {
        gate: authority_result(
            gate=gate,
            observation_id="OBS-001",
            observation_version=1,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=GateVerdict.ALLOW,
            reason=f"{gate} allow",
            authority_identity=f"AUTH-{gate}",
            authority_hash=f"HASH-{gate}",
        )
        for gate in REQUIRED_GATES
    }

    context_receipt = build_canonical_reasoning_context_receipt(
        context=context,
        authorities=authorities,
    )

    identity = bind_candidate_identity(
        candidate_id="CANDIDATE-001",
        purpose="candidate evidence",
        context_receipt=context_receipt,
    )

    bound_set = empty_receipt_bound_candidate_set(identity)

    item = evidence_item_from_context_receipt(
        identity=identity,
        context_receipt=context_receipt,
    )

    return admit_receipt_bound_evidence(
        bound_set=bound_set,
        bound_item=item,
    )


def origin():
    return BoundEvidenceOrigin(
        observation_id="OBS-001",
        observation_version=1,
        lineage_hash="LINEAGE-001",
        source_id="SOURCE-001",
        source_family_id="FAMILY-001",
        origin_family_id="ORIGIN-001",
        independence_family_id="INDEPENDENCE-001",
        dependency_ids=(),
        dependency_known=True,
        category="MARKET",
    )


def requirement(bound_set):
    return build_policy_requirement_set(
        candidate_set=bound_set,
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=1,
                minimum_independent_confirmations=1,
                required=True,
            ),
        ),
    )


def test_independence_receipt_is_bound_to_candidate_set():
    bound_set = admitted_set()

    receipt = build_candidate_independence_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
    )

    assert receipt.candidate_set_receipt_id == bound_set.set_receipt_id
    assert verify_candidate_independence_receipt(receipt)


def test_origin_must_exactly_cover_admitted_evidence():
    bound_set = admitted_set()

    bad = replace(
        origin(),
        observation_id="OTHER",
    )

    with pytest.raises(ValueError):
        build_candidate_independence_receipt(
            candidate_set=bound_set,
            origins=(bad,),
        )


def test_sufficiency_consumes_actual_independence_receipt():
    bound_set = admitted_set()

    independence = build_candidate_independence_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
    )

    requirements = requirement(bound_set)

    sufficiency = build_candidate_sufficiency_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
        independence_receipt=independence,
        requirement_set=requirements,
    )

    assert sufficiency.assessment.state is SufficiencyState.SUFFICIENT
    assert verify_candidate_sufficiency_receipt(sufficiency)
    assert candidate_sufficiency_eligible(sufficiency)


def test_policy_identity_substitution_is_blocked():
    bound_set = admitted_set()

    independence = build_candidate_independence_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
    )

    requirements = requirement(bound_set)

    forged = replace(
        requirements,
        effective_policy_hash="FORGED",
    )

    with pytest.raises(ValueError):
        build_candidate_sufficiency_receipt(
            candidate_set=bound_set,
            origins=(origin(),),
            independence_receipt=independence,
            requirement_set=forged,
        )


def test_independence_receipt_tampering_is_blocked():
    bound_set = admitted_set()

    independence = build_candidate_independence_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
    )

    forged = replace(
        independence,
        integrity_hash="0" * 64,
    )

    with pytest.raises(ValueError):
        build_candidate_sufficiency_receipt(
            candidate_set=bound_set,
            origins=(origin(),),
            independence_receipt=forged,
            requirement_set=requirement(bound_set),
        )


def test_snapshot_preserves_authority_boundary():
    bound_set = admitted_set()

    independence = build_candidate_independence_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
    )

    sufficiency = build_candidate_sufficiency_receipt(
        candidate_set=bound_set,
        origins=(origin(),),
        independence_receipt=independence,
        requirement_set=requirement(bound_set),
    )

    boundary = independence_sufficiency_snapshot(
        independence_receipt=independence,
        sufficiency_receipt=sufficiency,
    )["authority_boundary"]

    assert boundary["evidence_independence_and_sufficiency_only"] is True
    assert boundary["analytical_conclusion"] is False
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_runtime_contains_no_execution_calls():
    from pathlib import Path
    import web.ob_independence_sufficiency_binding as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    for token in (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ):
        assert token not in source
