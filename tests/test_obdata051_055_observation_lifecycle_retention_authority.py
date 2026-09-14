from pathlib import Path

from web.ob_observation_lifecycle import (
    CurrentReasoningEligibility,
    ObservationLifecycleState,
    RetentionState,
    assess_observation_lifecycle,
    eligible_for_current_reasoning,
    excluded_from_current_reasoning,
    lifecycle_snapshot,
    requires_current_reasoning_review,
    retained_for_history,
)


ROOT = Path(__file__).resolve().parents[1]


def test_obdata051_lifecycle_identity():
    assert [item.value for item in ObservationLifecycleState] == [
        "ACTIVE",
        "SUPERSEDED",
        "HISTORICAL",
        "ARCHIVED",
        "RETAINED_EVIDENCE",
        "UNKNOWN",
    ]

    assert [item.value for item in CurrentReasoningEligibility] == [
        "ELIGIBLE",
        "REVIEW_ONLY",
        "INELIGIBLE",
        "UNKNOWN",
    ]

    assert [item.value for item in RetentionState] == [
        "HOT",
        "WARM",
        "ARCHIVE",
        "PERMANENT_EVIDENCE",
        "UNKNOWN",
    ]


def test_obdata052_current_trusted_is_active_and_eligible():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="TRUSTED",
    )

    assert result.lifecycle is ObservationLifecycleState.ACTIVE
    assert result.reasoning_eligibility is CurrentReasoningEligibility.ELIGIBLE
    assert result.retention is RetentionState.HOT
    assert eligible_for_current_reasoning(result)


def test_obdata052_current_usable_is_active_and_eligible():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="USABLE",
    )

    assert result.lifecycle is ObservationLifecycleState.ACTIVE
    assert eligible_for_current_reasoning(result)


def test_obdata052_current_caution_is_review_only():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="CAUTION",
    )

    assert result.lifecycle is ObservationLifecycleState.ACTIVE
    assert (
        result.reasoning_eligibility
        is CurrentReasoningEligibility.REVIEW_ONLY
    )
    assert requires_current_reasoning_review(result)


def test_obdata052_current_quarantined_is_not_current_truth():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="QUARANTINED",
    )

    assert (
        result.lifecycle
        is ObservationLifecycleState.RETAINED_EVIDENCE
    )
    assert excluded_from_current_reasoning(result)
    assert result.retention is RetentionState.PERMANENT_EVIDENCE


def test_obdata052_current_unusable_is_not_current_truth():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="UNUSABLE",
    )

    assert (
        result.lifecycle
        is ObservationLifecycleState.RETAINED_EVIDENCE
    )
    assert excluded_from_current_reasoning(result)


def test_obdata053_superseded_is_ineligible_but_retained():
    result = assess_observation_lifecycle(
        version_status="SUPERSEDED",
        effective_state="TRUSTED",
    )

    assert result.lifecycle is ObservationLifecycleState.SUPERSEDED
    assert excluded_from_current_reasoning(result)
    assert retained_for_history(result)
    assert result.retention is RetentionState.PERMANENT_EVIDENCE


def test_obdata053_historical_is_ineligible_but_retained():
    result = assess_observation_lifecycle(
        version_status="HISTORICAL",
        effective_state="TRUSTED",
    )

    assert result.lifecycle is ObservationLifecycleState.HISTORICAL
    assert excluded_from_current_reasoning(result)
    assert retained_for_history(result)


def test_obdata053_archive_is_still_retained():
    result = assess_observation_lifecycle(
        version_status="SUPERSEDED",
        effective_state="TRUSTED",
        archive_requested=True,
    )

    assert result.lifecycle is ObservationLifecycleState.ARCHIVED
    assert result.retention is RetentionState.ARCHIVE
    assert retained_for_history(result)
    assert excluded_from_current_reasoning(result)


def test_obdata053_retention_does_not_restore_reasoning_eligibility():
    result = assess_observation_lifecycle(
        version_status="SUPERSEDED",
        effective_state="TRUSTED",
        retain_as_evidence=True,
    )

    assert retained_for_history(result)
    assert not eligible_for_current_reasoning(result)
    assert excluded_from_current_reasoning(result)


def test_obdata054_unknown_version_fails_closed():
    result = assess_observation_lifecycle(
        version_status="UNKNOWN",
        effective_state="TRUSTED",
    )

    assert result.lifecycle is ObservationLifecycleState.UNKNOWN
    assert (
        result.reasoning_eligibility
        is CurrentReasoningEligibility.UNKNOWN
    )


def test_obdata054_unknown_effective_state_fails_closed():
    result = assess_observation_lifecycle(
        version_status="CURRENT",
        effective_state="UNKNOWN",
    )

    assert result.lifecycle is ObservationLifecycleState.UNKNOWN
    assert (
        result.reasoning_eligibility
        is CurrentReasoningEligibility.UNKNOWN
    )


def test_obdata054_snapshot_preserves_lifecycle_and_retention_distinction():
    result = assess_observation_lifecycle(
        version_status="SUPERSEDED",
        effective_state="TRUSTED",
    )

    snapshot = lifecycle_snapshot(
        result
    )

    assert snapshot["lifecycle"] == "SUPERSEDED"
    assert snapshot["reasoning_eligibility"] == "INELIGIBLE"
    assert snapshot["retention"] == "PERMANENT_EVIDENCE"


def test_obdata054_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_lifecycle.py"
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


def test_obdata054_no_audit_history_deletion_or_reactivation_api():
    source = (
        ROOT
        / "web/ob_observation_lifecycle.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "deleteHistory(",
        "eraseObservation(",
        "deleteArchived(",
        "reactivateSuperseded(",
        "promoteHistoricalToCurrent(",
        "removeAuditEvidence(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata055_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata051_055_observation_lifecycle_retention_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata051_055_observation_lifecycle_retention_authority_handoff.md"
    ).is_file()


def test_obdata055_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata051_055_observation_lifecycle_retention_authority.json"
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
    assert '"version_history_rewrite": false' in evidence
    assert '"delete_audit_history": false' in evidence
    assert '"archived_as_current_truth": false' in evidence
    assert '"implicit_superseded_reactivation": false' in evidence
