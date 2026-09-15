from dataclasses import replace

import pytest

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
from web.ob_foundation_integration_closure import (
    ClosureEvidenceOrigin,
    admit_closure_evidence,
    build_closure_candidate_identity,
    build_closure_independence_receipt,
    build_closure_sufficiency_receipt,
    build_policy_requirement_authority,
    build_verified_authority_artifact,
    empty_closure_candidate_set,
    evidence_from_compatible_context,
    verify_closure_candidate_set,
    verify_closure_independence_receipt,
    verify_closure_sufficiency_receipt,
    verify_policy_requirement_authority,
    verify_verified_authority_artifact,
)
from web.ob_reasoning_context_composition import (
    GateVerdict,
    REQUIRED_GATES,
)


def context_receipt(
    observation_id,
    version,
    lineage,
    context_id,
):
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
        context_id=context_id,
        observation_id=observation_id,
        observation_version=version,
        lineage_hash=lineage,
        provenance_identity=f"PROV-{observation_id}",
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
            observation_id=observation_id,
            observation_version=version,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=GateVerdict.ALLOW,
            reason=f"{gate} allow",
            authority_identity=f"LEGACY-{gate}",
            authority_hash=f"LEGACY-HASH-{gate}",
        )
        for gate in REQUIRED_GATES
    }

    return build_canonical_reasoning_context_receipt(
        context=context,
        authorities=authorities,
    )


def two_context_candidate():
    r1 = context_receipt(
        "OBS-001",
        1,
        "LINEAGE-001",
        "CTX-001",
    )

    r2 = context_receipt(
        "OBS-002",
        1,
        "LINEAGE-002",
        "CTX-002",
    )

    identity = build_closure_candidate_identity(
        candidate_id="CANDIDATE-001",
        purpose="analytical reasoning",
        context_receipt=r1,
    )

    candidate_set = empty_closure_candidate_set(identity)

    candidate_set = admit_closure_evidence(
        candidate_set=candidate_set,
        evidence=evidence_from_compatible_context(
            identity=identity,
            context_receipt=r1,
        ),
    )

    candidate_set = admit_closure_evidence(
        candidate_set=candidate_set,
        evidence=evidence_from_compatible_context(
            identity=identity,
            context_receipt=r2,
        ),
    )

    return r1, r2, candidate_set


def test_obfixint001_bare_caller_strings_are_not_native_authority_proof():
    with pytest.raises(ValueError, match="native authority object is required"):
        build_verified_authority_artifact(
            gate="freshness",
            observation_id="OBS-001",
            observation_version=1,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict="ALLOW",
            reason="caller says allow",
            native_authority=None,
        )


def test_obfixint001_native_object_is_serialized_and_tamper_evident():
    native = {
        "state": "CURRENT",
        "observation_id": "OBS-001",
        "observation_version": 1,
        "source": "TEST-NATIVE-AUTHORITY",
    }

    artifact = build_verified_authority_artifact(
        gate="freshness",
        observation_id="OBS-001",
        observation_version=1,
        reasoning_target_id="TARGET-001",
        symbol="AAPL",
        instrument_kind="OPTION",
        verdict="ALLOW",
        reason="native authority permits",
        native_authority=native,
    )

    assert verify_verified_authority_artifact(artifact)

    forged = replace(
        artifact,
        verdict="BLOCK",
    )

    assert not verify_verified_authority_artifact(forged)


def test_obfixint002_multiple_compatible_contexts_enter_one_candidate():
    r1, r2, candidate_set = two_context_candidate()

    assert r1.receipt_id != r2.receipt_id
    assert len(candidate_set.evidence_items) == 2

    assert {
        x.context_receipt_id
        for x in candidate_set.evidence_items
    } == {
        r1.receipt_id,
        r2.receipt_id,
    }

    assert verify_closure_candidate_set(candidate_set)


def test_obfixint002_exact_contract_mismatch_fails_closed():
    r1 = context_receipt(
        "OBS-001",
        1,
        "LINEAGE-001",
        "CTX-001",
    )

    identity = build_closure_candidate_identity(
        candidate_id="CANDIDATE-001",
        purpose="analytical reasoning",
        context_receipt=r1,
    )

    instrument = build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-P-250",
        underlying_symbol="AAPL",
        option_right="PUT",
        strike="250",
        expiration="2026-12-18",
    )

    context = build_canonical_context_identity(
        context_id="CTX-OTHER",
        observation_id="OBS-OTHER",
        observation_version=1,
        lineage_hash="LINEAGE-OTHER",
        provenance_identity="PROV-OTHER",
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
            observation_id="OBS-OTHER",
            observation_version=1,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=GateVerdict.ALLOW,
            reason="allow",
            authority_identity=f"LEGACY-{gate}",
            authority_hash=f"HASH-{gate}",
        )
        for gate in REQUIRED_GATES
    }

    other = build_canonical_reasoning_context_receipt(
        context=context,
        authorities=authorities,
    )

    with pytest.raises(ValueError, match="exact instrument identity mismatch"):
        evidence_from_compatible_context(
            identity=identity,
            context_receipt=other,
        )


def test_obfixint003_sufficiency_has_no_second_origins_boundary():
    _, _, candidate_set = two_context_candidate()

    origins = (
        ClosureEvidenceOrigin(
            observation_id="OBS-001",
            observation_version=1,
            lineage_hash="LINEAGE-001",
            source_id="SOURCE-A",
            source_family_id="FAMILY-A",
            origin_family_id="ORIGIN-A",
            independence_family_id="IND-A",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
        ClosureEvidenceOrigin(
            observation_id="OBS-002",
            observation_version=1,
            lineage_hash="LINEAGE-002",
            source_id="SOURCE-B",
            source_family_id="FAMILY-B",
            origin_family_id="ORIGIN-B",
            independence_family_id="IND-B",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
    )

    independence = build_closure_independence_receipt(
        candidate_set=candidate_set,
        origins=origins,
    )

    assert verify_closure_independence_receipt(independence)

    policy = build_policy_requirement_authority(
        authority_id="MODEPOLICY-REQ-001",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=2,
                minimum_independent_confirmations=2,
                required=True,
            ),
        ),
    )

    sufficiency = build_closure_sufficiency_receipt(
        candidate_set=candidate_set,
        independence_receipt=independence,
        policy_requirement_authority=policy,
    )

    assert sufficiency.origin_hash == independence.origin_hash
    assert verify_closure_sufficiency_receipt(sufficiency)


def test_obfixint003_origin_tamper_invalidates_independence():
    _, _, candidate_set = two_context_candidate()

    origins = (
        ClosureEvidenceOrigin(
            observation_id="OBS-001",
            observation_version=1,
            lineage_hash="LINEAGE-001",
            source_id="SOURCE-A",
            source_family_id="FAMILY-A",
            origin_family_id="ORIGIN-A",
            independence_family_id="IND-A",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
        ClosureEvidenceOrigin(
            observation_id="OBS-002",
            observation_version=1,
            lineage_hash="LINEAGE-002",
            source_id="SOURCE-B",
            source_family_id="FAMILY-B",
            origin_family_id="ORIGIN-B",
            independence_family_id="IND-B",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
    )

    receipt = build_closure_independence_receipt(
        candidate_set=candidate_set,
        origins=origins,
    )

    forged_origins = (
        replace(
            receipt.origins[0],
            source_id="FORGED-SOURCE",
        ),
        receipt.origins[1],
    )

    forged = replace(
        receipt,
        origins=forged_origins,
    )

    assert not verify_closure_independence_receipt(forged)


def test_obfixint004_requirement_contents_are_bound_to_authority():
    loose = build_policy_requirement_authority(
        authority_id="MODEPOLICY-REQ-001",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=1,
                minimum_independent_confirmations=1,
                required=True,
            ),
        ),
    )

    strict = build_policy_requirement_authority(
        authority_id="MODEPOLICY-REQ-001",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=50,
                minimum_independent_confirmations=25,
                required=True,
            ),
        ),
    )

    assert verify_policy_requirement_authority(loose)
    assert verify_policy_requirement_authority(strict)

    assert loose.requirements_hash != strict.requirements_hash
    assert loose.integrity_hash != strict.integrity_hash


def test_obfixint004_policy_requirement_tamper_fails():
    authority = build_policy_requirement_authority(
        authority_id="MODEPOLICY-REQ-001",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=1,
                minimum_independent_confirmations=1,
                required=True,
            ),
        ),
    )

    forged = replace(
        authority,
        effective_policy_hash="FORGED",
    )

    assert not verify_policy_requirement_authority(forged)


def test_obfixint005_full_assessments_are_integrity_bound():
    _, _, candidate_set = two_context_candidate()

    origins = (
        ClosureEvidenceOrigin(
            observation_id="OBS-001",
            observation_version=1,
            lineage_hash="LINEAGE-001",
            source_id="SOURCE-A",
            source_family_id="FAMILY-A",
            origin_family_id="ORIGIN-A",
            independence_family_id="IND-A",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
        ClosureEvidenceOrigin(
            observation_id="OBS-002",
            observation_version=1,
            lineage_hash="LINEAGE-002",
            source_id="SOURCE-B",
            source_family_id="FAMILY-B",
            origin_family_id="ORIGIN-B",
            independence_family_id="IND-B",
            dependency_ids=(),
            dependency_known=True,
            category="MARKET",
        ),
    )

    independence = build_closure_independence_receipt(
        candidate_set=candidate_set,
        origins=origins,
    )

    policy = build_policy_requirement_authority(
        authority_id="MODEPOLICY-REQ-001",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        requirements=(
            build_evidence_requirement(
                category="MARKET",
                minimum_observations=2,
                minimum_independent_confirmations=2,
                required=True,
            ),
        ),
    )

    sufficiency = build_closure_sufficiency_receipt(
        candidate_set=candidate_set,
        independence_receipt=independence,
        policy_requirement_authority=policy,
    )

    assert verify_closure_independence_receipt(independence)
    assert verify_policy_requirement_authority(policy)
    assert verify_closure_sufficiency_receipt(sufficiency)

    assert sufficiency.assessment.state in (
        SufficiencyState.SUFFICIENT,
        SufficiencyState.REVIEW_REQUIRED,
        SufficiencyState.BLOCKED,
        SufficiencyState.UNKNOWN,
        SufficiencyState.INSUFFICIENT,
    )


def test_runtime_has_no_execution_authority():
    from pathlib import Path
    import web.ob_foundation_integration_closure as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    for token in (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ):
        assert token not in source
