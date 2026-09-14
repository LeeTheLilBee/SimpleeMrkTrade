from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from web.ob_evidence_lineage import (
    EvidenceTraceStep,
    LineageStage,
    TraceStatus,
    build_evidence_lineage,
    decision_path,
    lineage_snapshot,
    trace_is_complete,
    trace_requires_review,
    trace_step,
)


ROOT = Path(__file__).resolve().parents[1]


def full_steps():
    return [
        trace_step(
            sequence=0,
            stage=LineageStage.SOURCE,
            input_state="RAW",
            output_state="OBSERVED",
            reason="Source observation received.",
            source_ids=("source-a",),
        ),
        trace_step(
            sequence=1,
            stage=LineageStage.PROVENANCE,
            input_state="OBSERVED",
            output_state="PROVENANCE_COMPLETE",
            reason="Source provenance attached.",
            source_ids=("source-a",),
        ),
        trace_step(
            sequence=2,
            stage=LineageStage.SOURCE_AUTHORITY,
            input_state="PROVENANCE_COMPLETE",
            output_state="AUTHORITATIVE",
            reason="Source authority classified.",
            source_ids=("source-a",),
        ),
        trace_step(
            sequence=3,
            stage=LineageStage.FRESHNESS,
            input_state="AUTHORITATIVE",
            output_state="FRESH",
            reason="Observation evaluated as fresh.",
            source_ids=("source-a",),
        ),
        trace_step(
            sequence=4,
            stage=LineageStage.CORROBORATION,
            input_state="FRESH",
            output_state="CORROBORATED",
            reason="Independent observations corroborated.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=5,
            stage=LineageStage.QUALITY,
            input_state="CORROBORATED",
            output_state="VALID",
            reason="Observation passed structural quality checks.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=6,
            stage=LineageStage.ANOMALY,
            input_state="VALID",
            output_state="NORMAL",
            reason="No anomaly detected.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=7,
            stage=LineageStage.SYNTHESIS,
            input_state="NORMAL",
            output_state="TRUSTED",
            reason="Effective observation synthesized.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=8,
            stage=LineageStage.CONFLICT,
            input_state="TRUSTED",
            output_state="NONE",
            reason="No unresolved observation conflict.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=9,
            stage=LineageStage.ESCALATION,
            input_state="NONE",
            output_state="NONE",
            reason="No escalation required.",
            source_ids=("source-a", "source-b"),
        ),
        trace_step(
            sequence=10,
            stage=LineageStage.FINAL,
            input_state="NONE",
            output_state="TRUSTED",
            reason="Final observation state retained.",
            source_ids=("source-a", "source-b"),
        ),
    ]


def test_obdata041_lineage_stage_identity():
    assert [item.value for item in LineageStage] == [
        "SOURCE",
        "PROVENANCE",
        "SOURCE_AUTHORITY",
        "FRESHNESS",
        "CORROBORATION",
        "QUALITY",
        "ANOMALY",
        "SYNTHESIS",
        "CONFLICT",
        "ESCALATION",
        "FINAL",
    ]

    assert [item.value for item in TraceStatus] == [
        "COMPLETE",
        "PARTIAL",
        "BROKEN",
        "UNKNOWN",
    ]


def test_obdata041_complete_lineage():
    lineage = build_evidence_lineage(
        observation_id="obs-001",
        steps=full_steps(),
    )

    assert lineage.trace_status is TraceStatus.COMPLETE
    assert trace_is_complete(lineage)
    assert not trace_requires_review(lineage)


def test_obdata042_trace_is_immutable():
    step = full_steps()[0]

    with pytest.raises(FrozenInstanceError):
        step.reason = "rewritten"


def test_obdata042_lineage_is_immutable():
    lineage = build_evidence_lineage(
        observation_id="obs-001",
        steps=full_steps(),
    )

    with pytest.raises(FrozenInstanceError):
        lineage.trace_status = TraceStatus.BROKEN


def test_obdata042_missing_stage_is_partial_not_fabricated():
    steps = full_steps()

    steps = [
        item
        for item in steps
        if item.stage is not LineageStage.ANOMALY
    ]

    # Renumber so continuity itself is intact.
    rebuilt = [
        trace_step(
            sequence=index,
            stage=item.stage,
            input_state=item.input_state,
            output_state=item.output_state,
            reason=item.reason,
            source_ids=item.source_ids,
        )
        for index, item in enumerate(steps)
    ]

    lineage = build_evidence_lineage(
        observation_id="obs-002",
        steps=rebuilt,
    )

    assert lineage.trace_status is TraceStatus.PARTIAL
    assert trace_requires_review(lineage)


def test_obdata042_sequence_gap_is_broken():
    steps = full_steps()

    broken = [
        item
        for item in steps
        if item.sequence != 4
    ]

    lineage = build_evidence_lineage(
        observation_id="obs-003",
        steps=broken,
    )

    assert lineage.trace_status is TraceStatus.BROKEN
    assert trace_requires_review(lineage)


def test_obdata042_duplicate_sequence_rejected():
    steps = full_steps()

    duplicate = list(steps)

    duplicate.append(
        trace_step(
            sequence=10,
            stage=LineageStage.FINAL,
            input_state="x",
            output_state="y",
            reason="duplicate",
        )
    )

    with pytest.raises(ValueError):
        build_evidence_lineage(
            observation_id="obs-004",
            steps=duplicate,
        )


def test_obdata043_decision_path_preserves_each_authority_stage():
    lineage = build_evidence_lineage(
        observation_id="obs-005",
        steps=full_steps(),
    )

    path = decision_path(
        lineage
    )

    assert path == (
        "SOURCE:OBSERVED",
        "PROVENANCE:PROVENANCE_COMPLETE",
        "SOURCE_AUTHORITY:AUTHORITATIVE",
        "FRESHNESS:FRESH",
        "CORROBORATION:CORROBORATED",
        "QUALITY:VALID",
        "ANOMALY:NORMAL",
        "SYNTHESIS:TRUSTED",
        "CONFLICT:NONE",
        "ESCALATION:NONE",
        "FINAL:TRUSTED",
    )


def test_obdata043_hash_is_deterministic():
    a = build_evidence_lineage(
        observation_id="obs-006",
        steps=full_steps(),
    )

    b = build_evidence_lineage(
        observation_id="obs-006",
        steps=full_steps(),
    )

    assert a.trace_hash == b.trace_hash


def test_obdata043_hash_changes_when_trace_changes():
    original = build_evidence_lineage(
        observation_id="obs-007",
        steps=full_steps(),
    )

    changed_steps = full_steps()

    changed_steps[-1] = trace_step(
        sequence=10,
        stage=LineageStage.FINAL,
        input_state="NONE",
        output_state="CAUTION",
        reason="Final observation state changed.",
        source_ids=("source-a", "source-b"),
    )

    changed = build_evidence_lineage(
        observation_id="obs-007",
        steps=changed_steps,
    )

    assert original.trace_hash != changed.trace_hash


def test_obdata043_hash_changes_when_observation_identity_changes():
    a = build_evidence_lineage(
        observation_id="obs-008-a",
        steps=full_steps(),
    )

    b = build_evidence_lineage(
        observation_id="obs-008-b",
        steps=full_steps(),
    )

    assert a.trace_hash != b.trace_hash


def test_obdata044_snapshot_exposes_trace_not_magic_summary():
    lineage = build_evidence_lineage(
        observation_id="obs-009",
        steps=full_steps(),
    )

    snapshot = lineage_snapshot(
        lineage
    )

    assert snapshot["observation_id"] == "obs-009"
    assert snapshot["trace_status"] == "COMPLETE"
    assert len(snapshot["steps"]) == 11
    assert snapshot["trace_hash"] == lineage.trace_hash
    assert snapshot["steps"][0]["stage"] == "SOURCE"
    assert snapshot["steps"][-1]["stage"] == "FINAL"


def test_obdata044_source_ids_remain_visible():
    lineage = build_evidence_lineage(
        observation_id="obs-010",
        steps=full_steps(),
    )

    snapshot = lineage_snapshot(
        lineage
    )

    corroboration = next(
        item
        for item in snapshot["steps"]
        if item["stage"] == "CORROBORATION"
    )

    assert corroboration["source_ids"] == [
        "source-a",
        "source-b",
    ]


def test_obdata044_empty_lineage_is_unknown_not_complete():
    lineage = build_evidence_lineage(
        observation_id="obs-011",
        steps=[],
    )

    assert lineage.trace_status is TraceStatus.UNKNOWN
    assert trace_requires_review(lineage)


def test_obdata044_blank_observation_identity_rejected():
    with pytest.raises(ValueError):
        build_evidence_lineage(
            observation_id="   ",
            steps=full_steps(),
        )


def test_obdata044_blank_reason_rejected():
    with pytest.raises(ValueError):
        EvidenceTraceStep(
            sequence=0,
            stage=LineageStage.SOURCE,
            input_state="RAW",
            output_state="OBSERVED",
            reason="",
        )


def test_obdata044_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_evidence_lineage.py"
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


def test_obdata044_no_history_mutation_api():
    source = (
        ROOT
        / "web/ob_evidence_lineage.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "rewriteHistory(",
        "deleteTraceStep(",
        "removeEvidence(",
        "hideEvidence(",
        "replacePastState(",
        "mutateLineage(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata045_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata041_045_evidence_lineage_decision_trace_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata041_045_evidence_lineage_decision_trace_authority_handoff.md"
    ).is_file()


def test_obdata045_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata041_045_evidence_lineage_decision_trace_authority.json"
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
    assert '"retroactive_lineage_mutation": false' in evidence
    assert '"fabricated_trace_steps": false' in evidence
    assert '"hidden_evidence_removal": false' in evidence
