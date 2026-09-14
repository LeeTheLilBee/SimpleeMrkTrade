from pathlib import Path

import pytest

from web.ob_observation_rehabilitation import (
    RehabilitationReason,
    RehabilitationState,
    approve_rehabilitation,
    create_rehabilitated_version,
    rehabilitation_approved,
    rehabilitation_snapshot,
    rehabilitated_version_snapshot,
    reject_rehabilitation,
    request_rehabilitation_review,
    revoked_predecessor_remains_revoked,
)


ROOT = Path(__file__).resolve().parents[1]


def base_review():
    return request_rehabilitation_review(
        observation_id="obs-001",
        revoked_version=2,
        revoked_lineage_hash="revoked-lineage-v2",
        review_note="New evidence may support rehabilitation.",
    )


def approved_review():
    return approve_rehabilitation(
        base_review(),
        reason=RehabilitationReason.NEW_INDEPENDENT_EVIDENCE,
        new_lineage_hash="new-lineage-v3",
        approval_note="Independent evidence supports a new analytical version.",
    )


def test_obdata061_rehabilitation_identity():
    assert [item.value for item in RehabilitationState] == [
        "NOT_APPLICABLE",
        "REVIEW_REQUIRED",
        "APPROVED_FOR_NEW_VERSION",
        "REJECTED",
        "UNKNOWN",
    ]

    assert [item.value for item in RehabilitationReason] == [
        "SOURCE_RESTORED",
        "CORRECTED_DATA",
        "PROVENANCE_REESTABLISHED",
        "ERROR_CORRECTED",
        "NEW_INDEPENDENT_EVIDENCE",
        "OWNER_REVIEW",
        "OTHER",
        "UNKNOWN",
    ]


def test_obdata062_rehabilitation_starts_as_review_required():
    review = base_review()

    assert review.state is RehabilitationState.REVIEW_REQUIRED
    assert review.reason is None
    assert review.new_lineage_hash is None
    assert not rehabilitation_approved(review)


def test_obdata062_approval_requires_new_lineage():
    review = base_review()

    with pytest.raises(ValueError):
        approve_rehabilitation(
            review,
            reason=RehabilitationReason.CORRECTED_DATA,
            new_lineage_hash="revoked-lineage-v2",
            approval_note="Would incorrectly reuse revoked lineage.",
        )


def test_obdata062_approval_requires_known_reason():
    review = base_review()

    with pytest.raises(ValueError):
        approve_rehabilitation(
            review,
            reason=RehabilitationReason.UNKNOWN,
            new_lineage_hash="new-lineage",
            approval_note="Unknown reason is not sufficient.",
        )


def test_obdata062_approval_requires_note():
    review = base_review()

    with pytest.raises(ValueError):
        approve_rehabilitation(
            review,
            reason=RehabilitationReason.CORRECTED_DATA,
            new_lineage_hash="new-lineage",
            approval_note="   ",
        )


def test_obdata062_rejected_review_cannot_create_version():
    review = reject_rehabilitation(
        base_review(),
        reason=RehabilitationReason.OWNER_REVIEW,
        rejection_note="Evidence remains insufficient.",
    )

    assert review.state is RehabilitationState.REJECTED

    with pytest.raises(ValueError):
        create_rehabilitated_version(
            review,
            new_version=3,
            effective_state="TRUSTED",
            confidence="HIGH",
        )


def test_obdata063_approved_review_creates_new_version():
    review = approved_review()

    version = create_rehabilitated_version(
        review,
        new_version=3,
        effective_state="TRUSTED",
        confidence="HIGH",
    )

    assert version.version == 3
    assert version.rehabilitates_revoked_version == 2
    assert version.revoked_lineage_hash == "revoked-lineage-v2"
    assert version.new_lineage_hash == "new-lineage-v3"
    assert version.effective_state == "TRUSTED"
    assert version.confidence == "HIGH"


def test_obdata063_cannot_reuse_revoked_version_number():
    review = approved_review()

    with pytest.raises(ValueError):
        create_rehabilitated_version(
            review,
            new_version=2,
            effective_state="TRUSTED",
            confidence="HIGH",
        )


def test_obdata063_unknown_effective_state_rejected():
    review = approved_review()

    with pytest.raises(ValueError):
        create_rehabilitated_version(
            review,
            new_version=3,
            effective_state="UNKNOWN",
            confidence="HIGH",
        )


def test_obdata063_unknown_confidence_rejected():
    review = approved_review()

    with pytest.raises(ValueError):
        create_rehabilitated_version(
            review,
            new_version=3,
            effective_state="TRUSTED",
            confidence="UNKNOWN",
        )


def test_obdata064_revoked_predecessor_remains_distinct():
    review = approved_review()

    version = create_rehabilitated_version(
        review,
        new_version=3,
        effective_state="TRUSTED",
        confidence="HIGH",
    )

    assert revoked_predecessor_remains_revoked(version)

    assert (
        version.revoked_lineage_hash
        != version.new_lineage_hash
    )


def test_obdata064_snapshot_preserves_revoked_and_new_lineage():
    review = approved_review()

    version = create_rehabilitated_version(
        review,
        new_version=3,
        effective_state="USABLE",
        confidence="MODERATE",
    )

    review_snapshot = rehabilitation_snapshot(
        review
    )

    version_snapshot = rehabilitated_version_snapshot(
        version
    )

    assert review_snapshot["revoked_version"] == 2
    assert review_snapshot["revoked_lineage_hash"] == "revoked-lineage-v2"
    assert review_snapshot["new_lineage_hash"] == "new-lineage-v3"

    assert version_snapshot["version"] == 3
    assert version_snapshot["rehabilitates_revoked_version"] == 2
    assert version_snapshot["revoked_lineage_hash"] == "revoked-lineage-v2"
    assert version_snapshot["new_lineage_hash"] == "new-lineage-v3"


def test_obdata064_review_identity_validation():
    with pytest.raises(ValueError):
        request_rehabilitation_review(
            observation_id="   ",
            revoked_version=1,
            revoked_lineage_hash="hash",
            review_note="note",
        )

    with pytest.raises(ValueError):
        request_rehabilitation_review(
            observation_id="obs",
            revoked_version=0,
            revoked_lineage_hash="hash",
            review_note="note",
        )

    with pytest.raises(ValueError):
        request_rehabilitation_review(
            observation_id="obs",
            revoked_version=1,
            revoked_lineage_hash="   ",
            review_note="note",
        )

    with pytest.raises(ValueError):
        request_rehabilitation_review(
            observation_id="obs",
            revoked_version=1,
            revoked_lineage_hash="hash",
            review_note="   ",
        )


def test_obdata064_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_rehabilitation.py"
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


def test_obdata064_no_in_place_reinstatement_or_revocation_delete_api():
    source = (
        ROOT
        / "web/ob_observation_rehabilitation.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "clearRevocation(",
        "deleteRevocation(",
        "reinstateInPlace(",
        "restoreRevoked(",
        "unrevoke(",
        "mutateRevokedVersion(",
        "replaceRevokedLineage(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata065_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata061_065_reinstatement_rehabilitation_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata061_065_reinstatement_rehabilitation_authority_handoff.md"
    ).is_file()


def test_obdata065_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata061_065_reinstatement_rehabilitation_authority.json"
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
    assert '"synthesis_override": false' in evidence
    assert '"conflict_resolution_override": false' in evidence
    assert '"lineage_override": false' in evidence
    assert '"lifecycle_override": false' in evidence
    assert '"revocation_delete": false' in evidence
    assert '"in_place_reinstatement": false' in evidence
    assert '"silent_rehabilitation": false' in evidence
    assert '"rehabilitation_without_new_lineage": false' in evidence
    assert '"rehabilitation_without_revoked_predecessor": false' in evidence
    assert '"rehabilitation_without_approval": false' in evidence
