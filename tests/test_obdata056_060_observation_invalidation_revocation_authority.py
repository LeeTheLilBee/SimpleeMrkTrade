from pathlib import Path

import pytest

from web.ob_observation_revocation import (
    InvalidationState,
    RevocationReason,
    RevokedReasoningUse,
    blocked_from_current_reasoning,
    may_be_used_as_current_truth,
    request_revocation_review,
    revocation_snapshot,
    revoke_observation,
    valid_observation,
    must_show_revocation_warning,
)


ROOT = Path(__file__).resolve().parents[1]


def test_obdata056_invalidation_identity():
    assert [item.value for item in InvalidationState] == [
        "VALID",
        "REVOKED",
        "REVIEW_REQUIRED",
        "UNKNOWN",
    ]

    assert [item.value for item in RevocationReason] == [
        "SOURCE_COMPROMISED",
        "DATA_CORRUPTION",
        "PROVENANCE_FAILURE",
        "MATERIAL_ERROR",
        "IMPOSSIBLE_OBSERVATION",
        "OWNER_REVIEW",
        "OTHER",
        "UNKNOWN",
    ]

    assert [item.value for item in RevokedReasoningUse] == [
        "CURRENT_TRUTH_ALLOWED",
        "HISTORICAL_WITH_WARNING_ONLY",
        "BLOCKED",
        "UNKNOWN",
    ]


def test_obdata056_valid_observation_may_remain_current_truth():
    result = valid_observation(
        observation_id="obs-001",
        version=1,
        effective_state="TRUSTED",
        lineage_hash="lineage-v1",
    )

    assert result.invalidation is InvalidationState.VALID
    assert (
        result.reasoning_use
        is RevokedReasoningUse.CURRENT_TRUTH_ALLOWED
    )
    assert may_be_used_as_current_truth(result)
    assert not blocked_from_current_reasoning(result)


def test_obdata056_unknown_effective_state_fails_closed():
    result = valid_observation(
        observation_id="obs-001",
        version=1,
        effective_state="UNKNOWN",
        lineage_hash="lineage-v1",
    )

    assert result.invalidation is InvalidationState.UNKNOWN
    assert not may_be_used_as_current_truth(result)
    assert blocked_from_current_reasoning(result)


def test_obdata057_explicit_revocation_blocks_current_truth():
    result = revoke_observation(
        observation_id="obs-001",
        version=1,
        effective_state="TRUSTED",
        lineage_hash="lineage-v1",
        reason=RevocationReason.DATA_CORRUPTION,
        note="Corrupt upstream payload discovered.",
    )

    assert result.invalidation is InvalidationState.REVOKED
    assert (
        result.reasoning_use
        is RevokedReasoningUse.HISTORICAL_WITH_WARNING_ONLY
    )
    assert not may_be_used_as_current_truth(result)
    assert blocked_from_current_reasoning(result)
    assert must_show_revocation_warning(result)


def test_obdata057_revocation_preserves_original_effective_state():
    result = revoke_observation(
        observation_id="obs-002",
        version=3,
        effective_state="TRUSTED",
        lineage_hash="lineage-v3",
        reason=RevocationReason.PROVENANCE_FAILURE,
        note="Source identity later failed verification.",
    )

    assert result.original_effective_state == "TRUSTED"
    assert result.lineage_hash == "lineage-v3"


def test_obdata057_unknown_revocation_reason_rejected():
    with pytest.raises(ValueError):
        revoke_observation(
            observation_id="obs-003",
            version=1,
            effective_state="TRUSTED",
            lineage_hash="lineage",
            reason=RevocationReason.UNKNOWN,
            note="Cannot explicitly revoke with an unknown reason.",
        )


def test_obdata057_revocation_requires_note():
    with pytest.raises(ValueError):
        revoke_observation(
            observation_id="obs-004",
            version=1,
            effective_state="TRUSTED",
            lineage_hash="lineage",
            reason=RevocationReason.MATERIAL_ERROR,
            note="   ",
        )


def test_obdata058_review_required_blocks_use_without_premature_revocation():
    result = request_revocation_review(
        observation_id="obs-005",
        version=2,
        effective_state="CAUTION",
        lineage_hash="lineage-v2",
        note="Potential source compromise requires owner review.",
    )

    assert result.invalidation is InvalidationState.REVIEW_REQUIRED
    assert result.reason is None
    assert result.reasoning_use is RevokedReasoningUse.BLOCKED
    assert blocked_from_current_reasoning(result)
    assert not must_show_revocation_warning(result)


def test_obdata058_revoked_history_remains_visible():
    result = revoke_observation(
        observation_id="obs-006",
        version=4,
        effective_state="USABLE",
        lineage_hash="lineage-v4",
        reason=RevocationReason.MATERIAL_ERROR,
        note="Incorrect contract mapping discovered.",
    )

    snapshot = revocation_snapshot(
        result
    )

    assert snapshot["observation_id"] == "obs-006"
    assert snapshot["version"] == 4
    assert snapshot["invalidation"] == "REVOKED"
    assert snapshot["reason"] == "MATERIAL_ERROR"
    assert snapshot["original_effective_state"] == "USABLE"
    assert snapshot["lineage_hash"] == "lineage-v4"


def test_obdata059_revoked_does_not_mean_deleted():
    result = revoke_observation(
        observation_id="obs-007",
        version=2,
        effective_state="TRUSTED",
        lineage_hash="lineage-v2",
        reason=RevocationReason.SOURCE_COMPROMISED,
        note="Source credential compromise discovered.",
    )

    snapshot = revocation_snapshot(
        result
    )

    assert snapshot["observation_id"] == "obs-007"
    assert snapshot["lineage_hash"] == "lineage-v2"
    assert len(snapshot["notes"]) >= 2


def test_obdata059_identity_validation():
    with pytest.raises(ValueError):
        valid_observation(
            observation_id="   ",
            version=1,
            effective_state="TRUSTED",
            lineage_hash="lineage",
        )

    with pytest.raises(ValueError):
        valid_observation(
            observation_id="obs",
            version=0,
            effective_state="TRUSTED",
            lineage_hash="lineage",
        )

    with pytest.raises(ValueError):
        valid_observation(
            observation_id="obs",
            version=1,
            effective_state="TRUSTED",
            lineage_hash="   ",
        )


def test_obdata059_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_revocation.py"
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


def test_obdata059_no_revocation_history_delete_or_reinstate_api():
    source = (
        ROOT
        / "web/ob_observation_revocation.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "deleteRevocation(",
        "eraseRevocation(",
        "removeRevocationHistory(",
        "reinstateRevoked(",
        "autoReinstate(",
        "clearRevocation(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata060_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata056_060_observation_invalidation_revocation_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata056_060_observation_invalidation_revocation_authority_handoff.md"
    ).is_file()


def test_obdata060_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata056_060_observation_invalidation_revocation_authority.json"
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
    assert '"lifecycle_override": false' in evidence
    assert '"delete_revoked_history": false' in evidence
    assert '"silent_revocation": false' in evidence
    assert '"revoked_as_current_truth": false' in evidence
    assert '"automatic_reinstatement": false' in evidence
