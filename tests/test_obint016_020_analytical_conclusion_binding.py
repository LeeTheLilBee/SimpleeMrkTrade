from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_analytical_conclusion_binding import (
    analytical_conclusion_eligible,
    build_analytical_conclusion_receipt,
    build_governed_claim_basis,
    derive_bound_analytical_claim,
    verify_analytical_conclusion_receipt,
)
from web.ob_analytical_conclusion_integrity import (
    ClaimKind,
    ConclusionState,
    SupportState,
    UncertaintyState,
)
from web.ob_candidate_admission_receipt_binding import (
    admit_receipt_bound_evidence,
    bind_candidate_identity,
    empty_receipt_bound_candidate_set,
    evidence_item_from_context_receipt,
)
from web.ob_candidate_evidence_sufficiency import build_evidence_requirement
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
)
from web.ob_reasoning_context_composition import GateVerdict, REQUIRED_GATES


def chain():
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

    candidate_set = empty_receipt_bound_candidate_set(identity)

    evidence = evidence_item_from_context_receipt(
        identity=identity,
        context_receipt=context_receipt,
    )

    candidate_set = admit_receipt_bound_evidence(
        bound_set=candidate_set,
        bound_item=evidence,
    )

    origin = BoundEvidenceOrigin(
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

    independence = build_candidate_independence_receipt(
        candidate_set=candidate_set,
        origins=(origin,),
    )

    requirements = build_policy_requirement_set(
        candidate_set=candidate_set,
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=1,
                minimum_independent_confirmations=1,
                required=True,
            ),
        ),
    )

    sufficiency = build_candidate_sufficiency_receipt(
        candidate_set=candidate_set,
        origins=(origin,),
        independence_receipt=independence,
        requirement_set=requirements,
    )

    return candidate_set, sufficiency


def test_support_and_uncertainty_are_derived_not_supplied():
    candidate_set, sufficiency = chain()

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Observed market evidence supports this analytical statement.",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:1:LINEAGE-001",),
    )

    bound = derive_bound_analytical_claim(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        basis=basis,
    )

    assert bound.claim.support_state is SupportState.SUPPORTED
    assert bound.claim.uncertainty_state is UncertaintyState.RESOLVED


def test_non_admitted_evidence_reference_is_blocked():
    candidate_set, sufficiency = chain()

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Claim",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("FORGED:1:LINEAGE",),
    )

    with pytest.raises(ValueError):
        derive_bound_analytical_claim(
            candidate_set=candidate_set,
            sufficiency_receipt=sufficiency,
            basis=basis,
        )


def test_conclusion_consumes_actual_sufficiency_receipt():
    candidate_set, sufficiency = chain()

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Observed evidence supports this analytical statement.",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:1:LINEAGE-001",),
    )

    claim = derive_bound_analytical_claim(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        basis=basis,
    )

    receipt = build_analytical_conclusion_receipt(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        claims=(claim,),
    )

    assert receipt.assessment.state is ConclusionState.ELIGIBLE
    assert verify_analytical_conclusion_receipt(receipt)
    assert analytical_conclusion_eligible(receipt)


def test_sufficiency_receipt_substitution_is_blocked():
    candidate_set, sufficiency = chain()

    forged = replace(
        sufficiency,
        candidate_set_receipt_id="OBSET-FORGED",
    )

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Claim",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:1:LINEAGE-001",),
    )

    with pytest.raises(ValueError):
        derive_bound_analytical_claim(
            candidate_set=candidate_set,
            sufficiency_receipt=forged,
            basis=basis,
        )


def test_conflict_derives_review_required():
    candidate_set, sufficiency = chain()

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Conflicted analytical statement.",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:1:LINEAGE-001",),
        conflict_refs=("CONFLICT-001",),
    )

    claim = derive_bound_analytical_claim(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        basis=basis,
    )

    receipt = build_analytical_conclusion_receipt(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        claims=(claim,),
    )

    assert claim.claim.support_state is SupportState.SUPPORTED
    assert claim.claim.uncertainty_state is UncertaintyState.MATERIAL
    assert claim.claim.unresolved_conflicts == ("CONFLICT-001",)
    assert receipt.assessment.state is ConclusionState.REVIEW_REQUIRED
    assert not analytical_conclusion_eligible(receipt)


def test_conclusion_receipt_is_tamper_evident():
    candidate_set, sufficiency = chain()

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Claim",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:1:LINEAGE-001",),
    )

    claim = derive_bound_analytical_claim(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        basis=basis,
    )

    receipt = build_analytical_conclusion_receipt(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        claims=(claim,),
    )

    forged = replace(receipt, integrity_hash="0" * 64)

    assert not verify_analytical_conclusion_receipt(forged)
    assert not analytical_conclusion_eligible(forged)


def test_runtime_has_no_execution_authority():
    from pathlib import Path
    import web.ob_analytical_conclusion_binding as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    for token in (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ):
        assert token not in source
