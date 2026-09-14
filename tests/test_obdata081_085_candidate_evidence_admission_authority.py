from pathlib import Path

import pytest

from web.ob_candidate_evidence_admission import (
    AdmissionReason,
    AdmissionState,
    CandidateEvidenceSet,
    admit_candidate_evidence,
    assess_candidate_evidence_admission,
    build_candidate_evidence_item,
    build_candidate_identity,
    candidate_evidence_set_integrity,
    candidate_evidence_snapshot,
    empty_candidate_evidence_set,
)


ROOT = Path(__file__).resolve().parents[1]


def candidate():
    return build_candidate_identity(
        candidate_id="candidate-001",
        reasoning_target_id="target-001",
        target_symbol="SPY",
        target_instrument_kind="ETF",
        purpose="current-market-analysis",
    )


def item(
    *,
    observation_id="obs-001",
    observation_version=1,
    lineage_hash="lineage-001",
    reasoning_target_id="target-001",
    target_symbol="SPY",
    target_instrument_kind="ETF",
    upstream_composition_state="ELIGIBLE",
):
    return build_candidate_evidence_item(
        observation_id=observation_id,
        observation_version=observation_version,
        lineage_hash=lineage_hash,
        reasoning_target_id=reasoning_target_id,
        target_symbol=target_symbol,
        target_instrument_kind=target_instrument_kind,
        upstream_composition_state=upstream_composition_state,
    )


def clean_set():
    return empty_candidate_evidence_set(
        candidate()
    )


def test_obdata081_candidate_identity_explicit():
    result = candidate()

    assert result.candidate_id == "candidate-001"
    assert result.reasoning_target_id == "target-001"
    assert result.target_symbol == "SPY"
    assert result.target_instrument_kind == "ETF"
    assert result.purpose == "current-market-analysis"


def test_obdata081_candidate_identity_rejects_blank():
    with pytest.raises(ValueError):
        build_candidate_identity(
            candidate_id="",
            reasoning_target_id="target",
            target_symbol="SPY",
            target_instrument_kind="ETF",
            purpose="analysis",
        )


def test_obdata081_evidence_identity_requires_version_and_lineage():
    with pytest.raises(ValueError):
        item(
            observation_version=0
        )

    with pytest.raises(ValueError):
        item(
            lineage_hash=""
        )


def test_obdata082_clean_eligible_evidence_admitted():
    evidence_set = clean_set()

    assessment = assess_candidate_evidence_admission(
        evidence_set=evidence_set,
        item=item(),
    )

    assert assessment.state is AdmissionState.ADMITTED
    assert assessment.reason is AdmissionReason.CLEAN_ADMISSION

    admitted = admit_candidate_evidence(
        evidence_set=evidence_set,
        item=item(),
    )

    assert len(admitted.items) == 1
    assert candidate_evidence_set_integrity(admitted)


def test_obdata082_upstream_not_eligible_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            upstream_composition_state="BLOCKED"
        ),
    )

    assert assessment.state is AdmissionState.BLOCKED
    assert assessment.reason is AdmissionReason.UPSTREAM_NOT_ELIGIBLE


def test_obdata082_unknown_upstream_state_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            upstream_composition_state="UNKNOWN"
        ),
    )

    assert assessment.state is AdmissionState.BLOCKED
    assert assessment.reason is AdmissionReason.UPSTREAM_NOT_ELIGIBLE


def test_obdata082_review_upstream_state_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            upstream_composition_state="REVIEW_REQUIRED"
        ),
    )

    assert assessment.state is AdmissionState.BLOCKED
    assert assessment.reason is AdmissionReason.UPSTREAM_NOT_ELIGIBLE


def test_obdata082_mixed_reasoning_target_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            reasoning_target_id="target-999"
        ),
    )

    assert assessment.reason is AdmissionReason.TARGET_ID_MISMATCH


def test_obdata082_mixed_symbol_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            target_symbol="QQQ"
        ),
    )

    assert assessment.reason is AdmissionReason.SYMBOL_MISMATCH


def test_obdata082_mixed_instrument_kind_blocked():
    assessment = assess_candidate_evidence_admission(
        evidence_set=clean_set(),
        item=item(
            target_instrument_kind="OPTION"
        ),
    )

    assert assessment.reason is AdmissionReason.INSTRUMENT_KIND_MISMATCH


def test_obdata083_exact_duplicate_blocked():
    evidence_set = admit_candidate_evidence(
        evidence_set=clean_set(),
        item=item(),
    )

    assessment = assess_candidate_evidence_admission(
        evidence_set=evidence_set,
        item=item(),
    )

    assert assessment.reason is AdmissionReason.EXACT_DUPLICATE


def test_obdata083_two_active_versions_same_observation_blocked():
    evidence_set = admit_candidate_evidence(
        evidence_set=clean_set(),
        item=item(
            observation_version=1,
            lineage_hash="lineage-v1",
        ),
    )

    assessment = assess_candidate_evidence_admission(
        evidence_set=evidence_set,
        item=item(
            observation_version=2,
            lineage_hash="lineage-v2",
        ),
    )

    assert assessment.reason is AdmissionReason.OBSERVATION_VERSION_CONFLICT


def test_obdata083_duplicate_lineage_cannot_masquerade_as_independent_evidence():
    evidence_set = admit_candidate_evidence(
        evidence_set=clean_set(),
        item=item(
            observation_id="obs-a",
            lineage_hash="shared-lineage",
        ),
    )

    assessment = assess_candidate_evidence_admission(
        evidence_set=evidence_set,
        item=item(
            observation_id="obs-b",
            lineage_hash="shared-lineage",
        ),
    )

    assert assessment.reason is AdmissionReason.LINEAGE_DUPLICATE


def test_obdata083_distinct_observations_distinct_lineage_allowed():
    evidence_set = admit_candidate_evidence(
        evidence_set=clean_set(),
        item=item(
            observation_id="obs-a",
            lineage_hash="lineage-a",
        ),
    )

    evidence_set = admit_candidate_evidence(
        evidence_set=evidence_set,
        item=item(
            observation_id="obs-b",
            lineage_hash="lineage-b",
        ),
    )

    assert len(evidence_set.items) == 2
    assert candidate_evidence_set_integrity(evidence_set)


def test_obdata084_integrity_detects_manual_mixed_target_contamination():
    bad = CandidateEvidenceSet(
        candidate=candidate(),
        items=(
            item(),
            item(
                observation_id="obs-002",
                lineage_hash="lineage-002",
                reasoning_target_id="wrong-target",
            ),
        ),
    )

    assert not candidate_evidence_set_integrity(
        bad
    )


def test_obdata084_integrity_detects_manual_version_contamination():
    bad = CandidateEvidenceSet(
        candidate=candidate(),
        items=(
            item(
                observation_version=1,
                lineage_hash="lineage-v1",
            ),
            item(
                observation_version=2,
                lineage_hash="lineage-v2",
            ),
        ),
    )

    assert not candidate_evidence_set_integrity(
        bad
    )


def test_obdata084_integrity_detects_manual_lineage_duplication():
    bad = CandidateEvidenceSet(
        candidate=candidate(),
        items=(
            item(
                observation_id="obs-a",
                lineage_hash="same-lineage",
            ),
            item(
                observation_id="obs-b",
                lineage_hash="same-lineage",
            ),
        ),
    )

    assert not candidate_evidence_set_integrity(
        bad
    )


def test_obdata084_snapshot_preserves_candidate_and_evidence_identity():
    evidence_set = admit_candidate_evidence(
        evidence_set=clean_set(),
        item=item(),
    )

    snapshot = candidate_evidence_snapshot(
        evidence_set
    )

    assert snapshot["integrity"] is True
    assert snapshot["candidate"]["candidate_id"] == "candidate-001"
    assert snapshot["candidate"]["reasoning_target_id"] == "target-001"
    assert snapshot["items"][0]["observation_id"] == "obs-001"
    assert snapshot["items"][0]["observation_version"] == 1
    assert snapshot["items"][0]["lineage_hash"] == "lineage-001"


def test_obdata084_blocked_admission_cannot_mutate_set():
    evidence_set = clean_set()

    with pytest.raises(ValueError):
        admit_candidate_evidence(
            evidence_set=evidence_set,
            item=item(
                target_symbol="QQQ"
            ),
        )

    assert evidence_set.items == ()


def test_obdata084_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_candidate_evidence_admission.py"
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
        "rankTrade(",
        "recommendTrade(",
        "unlockManualLive(",
        "unlockHybrid(",
        "unlockAutomated(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata084_no_integrity_bypass_api():
    source = (
        ROOT
        / "web/ob_candidate_evidence_admission.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "forceAdmission(",
        "ignoreDuplicate(",
        "ignoreVersionConflict(",
        "ignoreLineageDuplicate(",
        "ignoreTargetMismatch(",
        "overrideComposition(",
        "promoteBlockedEvidence(",
        "treatDuplicateAsCorroboration(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata085_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata081_085_candidate_evidence_admission_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata081_085_candidate_evidence_admission_authority_handoff.md"
    ).is_file()


def test_obdata085_evidence_preserves_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata081_085_candidate_evidence_admission_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"contract_auto_selection": false' in evidence
    assert '"trade_ranking_authority": false' in evidence
    assert '"trade_recommendation_authority": false' in evidence
    assert '"manual_live_unlock": false' in evidence
    assert '"hybrid_execution": false' in evidence
    assert '"automated_execution": false' in evidence

    assert '"composition_override": false' in evidence
    assert '"source_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"revocation_override": false' in evidence
    assert '"temporal_override": false' in evidence
    assert '"instrument_override": false' in evidence

    assert '"duplicate_as_independent_evidence": false' in evidence
    assert '"mixed_target_evidence": false' in evidence
    assert '"multiple_active_versions_same_observation": false' in evidence
    assert '"lineage_duplication_as_corroboration": false' in evidence
