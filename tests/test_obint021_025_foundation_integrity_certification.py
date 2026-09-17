from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_analytical_conclusion_binding import (
    build_analytical_conclusion_receipt,
    build_governed_claim_basis,
    derive_bound_analytical_claim,
)
from web.ob_analytical_conclusion_integrity import ClaimKind
from web.ob_candidate_admission_receipt_binding import (
    admit_receipt_bound_evidence,
    bind_candidate_identity,
    empty_receipt_bound_candidate_set,
    evidence_item_from_context_receipt,
)
from web.ob_candidate_evidence_sufficiency import build_evidence_requirement
from web.ob_canonical_reasoning_context_spine import (
    build_certified_canonical_reasoning_context_receipt,
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
)
from web.ob_foundation_integrity_certification import (
    certify_foundation_integrity,
    foundation_integrity_snapshot,
    verify_foundation_integrity_certificate,
)
from web.ob_independence_sufficiency_binding import (
    BoundEvidenceOrigin,
    build_candidate_independence_receipt,
    build_candidate_sufficiency_receipt,
    build_policy_requirement_set,
)
from web.ob_reasoning_context_composition import GateVerdict, REQUIRED_GATES


def full_chain():
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
        observation_version=9,
        lineage_hash="LINEAGE-009",
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
            observation_version=9,
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

    context_receipt = build_certified_canonical_reasoning_context_receipt(
        context=context,
        authorities=authorities,
        certified_authority_hash="CERTIFIED-NATIVE-AUTHORITY-TEST-HASH",
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
        observation_version=9,
        lineage_hash="LINEAGE-009",
        source_id="SOURCE-001",
        source_family_id="SOURCE-FAMILY-001",
        origin_family_id="ORIGIN-FAMILY-001",
        independence_family_id="INDEPENDENCE-001",
        dependency_ids=(),
        dependency_known=True,
        category="MARKET",
    )

    independence = build_candidate_independence_receipt(
        candidate_set=candidate_set,
        origins=(origin,),
    )

    requirement_set = build_policy_requirement_set(
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
        requirement_set=requirement_set,
    )

    basis = build_governed_claim_basis(
        claim_id="CLAIM-001",
        statement="Observed admitted evidence supports this analytical statement.",
        claim_kind=ClaimKind.DIRECT,
        evidence_refs=("OBS-001:9:LINEAGE-009",),
    )

    claim = derive_bound_analytical_claim(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        basis=basis,
    )

    conclusion = build_analytical_conclusion_receipt(
        candidate_set=candidate_set,
        sufficiency_receipt=sufficiency,
        claims=(claim,),
    )

    return (
        context_receipt,
        candidate_set,
        independence,
        requirement_set,
        sufficiency,
        conclusion,
    )


def certify(parts):
    return certify_foundation_integrity(
        context_receipt=parts[0],
        candidate_set=parts[1],
        independence_receipt=parts[2],
        requirement_set=parts[3],
        sufficiency_receipt=parts[4],
        conclusion_receipt=parts[5],
    )


def test_full_receipt_chain_certifies():
    certificate = certify(full_chain())

    assert certificate.chain_valid is True
    assert verify_foundation_integrity_certificate(certificate)


def test_observation_version_and_lineage_survive_end_to_end():
    certificate = certify(full_chain())

    assert certificate.observation_id == "OBS-001"
    assert certificate.observation_version == 9
    assert certificate.lineage_hash == "LINEAGE-009"


def test_exact_option_contract_survives_end_to_end():
    certificate = certify(full_chain())

    assert certificate.symbol == "AAPL"
    assert certificate.instrument_kind == "OPTION"
    assert certificate.contract_id == "AAPL-20261218-C-250"


def test_policy_identity_survives_end_to_end():
    certificate = certify(full_chain())

    assert certificate.operating_mode == "PAPER"
    assert certificate.effective_policy_id == "POLICY-001"
    assert certificate.effective_policy_hash == "POLICY-HASH-001"


def test_independence_substitution_fails_closed():
    parts = list(full_chain())

    parts[2] = replace(
        parts[2],
        candidate_set_receipt_id="OBSET-FORGED",
    )

    with pytest.raises(ValueError):
        certify(tuple(parts))


def test_sufficiency_substitution_fails_closed():
    parts = list(full_chain())

    parts[4] = replace(
        parts[4],
        independence_receipt_id="OBIND-FORGED",
    )

    with pytest.raises(ValueError):
        certify(tuple(parts))


def test_conclusion_policy_substitution_fails_closed():
    parts = list(full_chain())

    parts[5] = replace(
        parts[5],
        effective_policy_hash="FORGED",
    )

    with pytest.raises(ValueError):
        certify(tuple(parts))


def test_certificate_is_tamper_evident():
    certificate = certify(full_chain())

    forged = replace(
        certificate,
        integrity_hash="0" * 64,
    )

    assert not verify_foundation_integrity_certificate(forged)


def test_final_boundary_does_not_grant_execution_authority():
    certificate = certify(full_chain())

    boundary = foundation_integrity_snapshot(
        certificate
    )["authority_boundary"]

    assert boundary["foundation_integrity_certification_only"] is True
    assert boundary["natural_language_truth_proof"] is False
    assert boundary["logical_inference_proof"] is False
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_runtime_has_no_execution_calls():
    from pathlib import Path
    import web.ob_foundation_integrity_certification as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    for token in (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ):
        assert token not in source
