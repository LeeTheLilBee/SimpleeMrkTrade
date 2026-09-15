from __future__ import annotations

import json
from pathlib import Path

import pytest

from web.ob_analytical_conclusion_integrity import (
    ClaimKind,
    ConclusionReason,
    ConclusionState,
    SupportState,
    UncertaintyState,
    analytical_conclusion_snapshot,
    assess_analytical_conclusion,
    assess_claim_integrity,
    build_analytical_claim,
    eligible_analytical_conclusion,
)


ROOT = Path(__file__).resolve().parents[1]

MODULE = ROOT / "web" / "ob_analytical_conclusion_integrity.py"

EVIDENCE = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata096_100_analytical_conclusion_integrity_authority.json"
)

HANDOFF = (
    ROOT
    / "ob_evidence"
    / "authority_foundation"
    / "obdata096_100_analytical_conclusion_integrity_authority_handoff.md"
)


def direct_claim(
    claim_id="claim-direct",
    *,
    support=SupportState.SUPPORTED,
    uncertainty=UncertaintyState.RESOLVED,
    conflicts=(),
):
    return build_analytical_claim(
        claim_id=claim_id,
        statement="The observed price is above the referenced threshold.",
        claim_kind=ClaimKind.DIRECT,
        support_state=support,
        uncertainty_state=uncertainty,
        evidence_refs=("obs-price-1",),
        unresolved_conflicts=conflicts,
    )


def inference_claim(
    claim_id="claim-inference",
    *,
    support=SupportState.SUPPORTED,
    uncertainty=UncertaintyState.RESOLVED,
    conflicts=(),
):
    return build_analytical_claim(
        claim_id=claim_id,
        statement="The combined observations suggest strengthening momentum.",
        claim_kind=ClaimKind.INFERENCE,
        support_state=support,
        uncertainty_state=uncertainty,
        evidence_refs=("obs-price-1", "obs-volume-1"),
        inference_basis=("price-structure", "volume-confirmation"),
        unresolved_conflicts=conflicts,
    )


def test_obdata096_direct_claim_preserves_direct_identity():
    claim = direct_claim()

    assert claim.claim_kind is ClaimKind.DIRECT
    assert claim.evidence_refs == ("obs-price-1",)
    assert claim.inference_basis == ()


def test_obdata096_inference_claim_preserves_inference_identity():
    claim = inference_claim()

    assert claim.claim_kind is ClaimKind.INFERENCE
    assert claim.inference_basis == (
        "price-structure",
        "volume-confirmation",
    )


def test_obdata096_unknown_claim_kind_fails_closed():
    claim = build_analytical_claim(
        claim_id="unknown",
        statement="Unknown analytical statement.",
        claim_kind="nonsense",
        support_state="SUPPORTED",
        uncertainty_state="RESOLVED",
        evidence_refs=("obs-1",),
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.UNKNOWN


def test_obdata096_duplicate_evidence_refs_rejected():
    with pytest.raises(ValueError):
        build_analytical_claim(
            claim_id="duplicate",
            statement="Duplicate evidence reference test.",
            claim_kind="DIRECT",
            support_state="SUPPORTED",
            uncertainty_state="RESOLVED",
            evidence_refs=("obs-1", "obs-1"),
        )


def test_obdata097_direct_claim_requires_evidence():
    claim = build_analytical_claim(
        claim_id="direct-no-evidence",
        statement="Direct statement.",
        claim_kind="DIRECT",
        support_state="SUPPORTED",
        uncertainty_state="RESOLVED",
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.BLOCKED


def test_obdata097_direct_claim_cannot_hide_inference_basis():
    claim = build_analytical_claim(
        claim_id="fake-direct",
        statement="A supposed direct statement.",
        claim_kind="DIRECT",
        support_state="SUPPORTED",
        uncertainty_state="RESOLVED",
        evidence_refs=("obs-1",),
        inference_basis=("interpretation-layer",),
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.BLOCKED


def test_obdata097_inference_requires_explicit_basis():
    claim = build_analytical_claim(
        claim_id="inference-no-basis",
        statement="An inferred statement.",
        claim_kind="INFERENCE",
        support_state="SUPPORTED",
        uncertainty_state="RESOLVED",
        evidence_refs=("obs-1",),
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.BLOCKED


def test_obdata097_inference_requires_supporting_evidence():
    claim = build_analytical_claim(
        claim_id="inference-no-evidence",
        statement="An inferred statement.",
        claim_kind="INFERENCE",
        support_state="SUPPORTED",
        uncertainty_state="RESOLVED",
        inference_basis=("pattern-a",),
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.BLOCKED


def test_obdata098_unresolved_conflict_requires_review():
    claim = inference_claim(
        conflicts=("price-vs-volume-conflict",)
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.REVIEW_REQUIRED


def test_obdata098_conflicted_support_requires_review():
    claim = inference_claim(
        support=SupportState.CONFLICTED
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.REVIEW_REQUIRED


def test_obdata098_material_uncertainty_requires_review():
    claim = inference_claim(
        uncertainty=UncertaintyState.MATERIAL
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.REVIEW_REQUIRED


def test_obdata098_unknown_uncertainty_fails_closed():
    claim = inference_claim(
        uncertainty=UncertaintyState.UNKNOWN
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.UNKNOWN


def test_obdata098_partial_support_cannot_become_clean_eligible():
    claim = inference_claim(
        support=SupportState.PARTIAL
    )

    assessment = assess_claim_integrity(claim)

    assert assessment.state is ConclusionState.REVIEW_REQUIRED


def test_obdata099_sufficient_evidence_does_not_override_unsupported_claim():
    claim = inference_claim(
        support=SupportState.UNSUPPORTED
    )

    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(claim,),
    )

    assert assessment.state is ConclusionState.BLOCKED
    assert assessment.reason is ConclusionReason.UNSUPPORTED_CLAIM
    assert assessment.unsupported_claim_ids == (
        "claim-inference",
    )


@pytest.mark.parametrize(
    "sufficiency",
    (
        "INSUFFICIENT",
        "BLOCKED",
        "REVIEW_REQUIRED",
    ),
)
def test_obdata099_non_sufficient_candidate_cannot_form_eligible_conclusion(
    sufficiency,
):
    assessment = assess_analytical_conclusion(
        sufficiency_state=sufficiency,
        claims=(direct_claim(),),
    )

    assert assessment.state is ConclusionState.BLOCKED
    assert assessment.reason is ConclusionReason.EVIDENCE_NOT_SUFFICIENT
    assert eligible_analytical_conclusion(assessment) is False


def test_obdata099_unknown_sufficiency_fails_unknown():
    assessment = assess_analytical_conclusion(
        sufficiency_state="UNKNOWN",
        claims=(direct_claim(),),
    )

    assert assessment.state is ConclusionState.UNKNOWN
    assert eligible_analytical_conclusion(assessment) is False


def test_obdata099_empty_claims_blocked():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(),
    )

    assert assessment.state is ConclusionState.BLOCKED
    assert assessment.reason is ConclusionReason.EMPTY_CLAIMS


def test_obdata099_duplicate_claim_ids_blocked():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(
            direct_claim("same-id"),
            inference_claim("same-id"),
        ),
    )

    assert assessment.state is ConclusionState.BLOCKED


def test_obdata099_clean_direct_and_inference_claims_are_eligible():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(
            direct_claim(),
            inference_claim(),
        ),
    )

    assert assessment.state is ConclusionState.ELIGIBLE
    assert assessment.reason is ConclusionReason.INTEGRITY_SATISFIED
    assert eligible_analytical_conclusion(assessment) is True


def test_obdata099_conflict_preserved_at_conclusion_level():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(
            direct_claim(),
            inference_claim(
                conflicts=("unresolved-cross-source-conflict",)
            ),
        ),
    )

    assert assessment.state is ConclusionState.REVIEW_REQUIRED
    assert assessment.reason is ConclusionReason.UNRESOLVED_CONFLICT
    assert assessment.conflicted_claim_ids == (
        "claim-inference",
    )


def test_obdata099_material_uncertainty_preserved_at_conclusion_level():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(
            inference_claim(
                uncertainty=UncertaintyState.MATERIAL
            ),
        ),
    )

    assert assessment.state is ConclusionState.REVIEW_REQUIRED
    assert assessment.reason is ConclusionReason.MATERIAL_UNCERTAINTY
    assert assessment.uncertain_claim_ids == (
        "claim-inference",
    )


def test_obdata100_snapshot_preserves_authority_boundary():
    assessment = assess_analytical_conclusion(
        sufficiency_state="SUFFICIENT",
        claims=(direct_claim(),),
    )

    snapshot = analytical_conclusion_snapshot(assessment)

    assert snapshot["state"] == "ELIGIBLE"

    boundary = snapshot["authority_boundary"]

    assert boundary["analytical_conclusion_integrity_only"] is True
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata100_evidence_and_handoff_exist():
    assert MODULE.is_file()
    assert EVIDENCE.is_file()
    assert HANDOFF.is_file()


def test_obdata100_evidence_declares_boundary():
    payload = json.loads(
        EVIDENCE.read_text(encoding="utf-8")
    )

    assert payload["pack"] == "OBDATA096-100"
    assert payload["status"] in {"PENDING", "SEALED"}

    boundary = payload["authority_boundary"]

    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_obdata100_module_contains_no_execution_surface():
    source = MODULE.read_text(encoding="utf-8").lower()

    forbidden = (
        "placeorder(",
        "submitorder(",
        "executetrade(",
        "autoselectcontract(",
        "broker.submit(",
    )

    for token in forbidden:
        assert token not in source
