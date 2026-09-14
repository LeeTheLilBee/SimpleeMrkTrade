from pathlib import Path

import pytest

from web.ob_observation_conflict import (
    ConflictAssessment,
    ConflictObservation,
    ConflictState,
    EscalationLevel,
    ResolutionState,
    assess_observation_conflict,
    conflict_snapshot,
    may_continue_normal_reasoning,
    must_block_observation_truth,
    preserves_ambiguity,
    requires_owner_review,
)


ROOT = Path(__file__).resolve().parents[1]


def obs(
    source_id,
    value,
    *,
    effective_state="TRUSTED",
    confidence="HIGH",
):
    return ConflictObservation(
        source_id=source_id,
        value=value,
        effective_state=effective_state,
        confidence=confidence,
    )


def test_obdata036_conflict_identity():
    assert [item.value for item in ConflictState] == [
        "NONE",
        "RECONCILABLE",
        "AMBIGUOUS",
        "MATERIAL",
        "UNRESOLVED",
        "UNKNOWN",
    ]

    assert [item.value for item in ResolutionState] == [
        "NO_ACTION",
        "PRESERVE_ALL",
        "ANALYTICALLY_RECONCILED",
        "ESCALATE",
        "BLOCK",
        "UNKNOWN",
    ]

    assert [item.value for item in EscalationLevel] == [
        "NONE",
        "REVIEW",
        "OWNER_REVIEW",
        "HARD_BLOCK",
        "UNKNOWN",
    ]


def test_obdata037_corroborated_sources_need_no_conflict_resolution():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
            obs("b", 100.0),
        ],
        corroboration_state="CORROBORATED",
    )

    assert result.conflict is ConflictState.NONE
    assert result.resolution is ResolutionState.NO_ACTION
    assert result.escalation is EscalationLevel.NONE
    assert result.selected_source_id is None
    assert may_continue_normal_reasoning(result)


def test_obdata037_minor_disagreement_can_be_analytically_reconciled_without_source_winner():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
            obs(
                "b",
                100.4,
                effective_state="USABLE",
                confidence="MODERATE",
            ),
        ],
        corroboration_state="MINOR_DISAGREEMENT",
    )

    assert result.conflict is ConflictState.RECONCILABLE
    assert result.resolution is ResolutionState.ANALYTICALLY_RECONCILED
    assert result.escalation is EscalationLevel.REVIEW
    assert result.selected_source_id is None
    assert result.preserved_source_ids == (
        "a",
        "b",
    )


def test_obdata038_material_disagreement_preserves_all_observations():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
            obs("b", 102.0),
        ],
        corroboration_state="MATERIAL_DISAGREEMENT",
    )

    assert result.conflict is ConflictState.AMBIGUOUS
    assert result.resolution is ResolutionState.PRESERVE_ALL
    assert result.escalation is EscalationLevel.OWNER_REVIEW
    assert preserves_ambiguity(result)
    assert requires_owner_review(result)
    assert result.selected_source_id is None


def test_obdata038_conflicted_sources_escalate_instead_of_picking_winner():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
            obs("b", 115.0),
        ],
        corroboration_state="CONFLICTED",
    )

    assert result.conflict is ConflictState.MATERIAL
    assert result.resolution is ResolutionState.ESCALATE
    assert result.escalation is EscalationLevel.OWNER_REVIEW
    assert result.selected_source_id is None


def test_obdata039_unusable_observation_hard_blocks_conflict_resolution():
    result = assess_observation_conflict(
        [
            obs(
                "a",
                100.0,
                effective_state="TRUSTED",
            ),
            obs(
                "b",
                500.0,
                effective_state="UNUSABLE",
                confidence="NONE",
            ),
        ],
        corroboration_state="CONFLICTED",
    )

    assert result.resolution is ResolutionState.BLOCK
    assert result.escalation is EscalationLevel.HARD_BLOCK
    assert must_block_observation_truth(result)
    assert result.selected_source_id is None


def test_obdata039_quarantined_observation_hard_blocks():
    result = assess_observation_conflict(
        [
            obs(
                "a",
                100.0,
            ),
            obs(
                "b",
                130.0,
                effective_state="QUARANTINED",
                confidence="LOW",
            ),
        ],
        corroboration_state="MATERIAL_DISAGREEMENT",
    )

    assert result.resolution is ResolutionState.BLOCK
    assert result.escalation is EscalationLevel.HARD_BLOCK


def test_obdata039_unknown_authority_escalates():
    result = assess_observation_conflict(
        [
            obs(
                "a",
                100.0,
            ),
            obs(
                "b",
                101.0,
                effective_state="UNKNOWN",
                confidence="UNKNOWN",
            ),
        ],
        corroboration_state="MINOR_DISAGREEMENT",
    )

    assert result.conflict is ConflictState.UNRESOLVED
    assert result.resolution is ResolutionState.ESCALATE
    assert result.escalation is EscalationLevel.OWNER_REVIEW


def test_single_source_has_no_cross_source_conflict():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
        ],
        corroboration_state="SINGLE_SOURCE",
    )

    assert result.conflict is ConflictState.NONE
    assert result.resolution is ResolutionState.NO_ACTION
    assert result.escalation is EscalationLevel.NONE


def test_duplicate_source_is_rejected_as_independent_conflict_evidence():
    with pytest.raises(ValueError):
        assess_observation_conflict(
            [
                obs("a", 100.0),
                obs("a", 101.0),
            ],
            corroboration_state="CONFLICTED",
        )


def test_obdata039_snapshot_never_contains_selected_winner():
    result = assess_observation_conflict(
        [
            obs("a", 100.0),
            obs("b", 102.0),
        ],
        corroboration_state="MATERIAL_DISAGREEMENT",
    )

    snapshot = conflict_snapshot(
        result
    )

    assert snapshot["selected_source_id"] is None
    assert snapshot["preserved_source_ids"] == [
        "a",
        "b",
    ]


def test_obdata039_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_conflict.py"
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


def test_obdata039_no_silent_winner_api():
    source = (
        ROOT
        / "web/ob_observation_conflict.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "chooseWinner(",
        "pickWinner(",
        "preferredSource(",
        "selectBestSource(",
        "winning_source",
    )

    for token in forbidden:
        assert token not in source


def test_obdata040_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata036_040_conflict_resolution_escalation_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata036_040_conflict_resolution_escalation_authority_handoff.md"
    ).is_file()


def test_obdata040_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata036_040_conflict_resolution_escalation_authority.json"
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
    assert '"fabricated_consensus": false' in evidence
    assert '"silent_source_winner": false' in evidence
