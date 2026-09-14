from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Any, Iterable
import json


class LineageStage(str, Enum):
    SOURCE = "SOURCE"
    PROVENANCE = "PROVENANCE"
    SOURCE_AUTHORITY = "SOURCE_AUTHORITY"
    FRESHNESS = "FRESHNESS"
    CORROBORATION = "CORROBORATION"
    QUALITY = "QUALITY"
    ANOMALY = "ANOMALY"
    SYNTHESIS = "SYNTHESIS"
    CONFLICT = "CONFLICT"
    ESCALATION = "ESCALATION"
    FINAL = "FINAL"


class TraceStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    BROKEN = "BROKEN"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceTraceStep:
    sequence: int
    stage: LineageStage
    input_state: str
    output_state: str
    reason: str
    source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError(
                "sequence cannot be negative"
            )

        if not self.reason.strip():
            raise ValueError(
                "reason cannot be blank"
            )

        if any(
            not source_id.strip()
            for source_id in self.source_ids
        ):
            raise ValueError(
                "source_ids cannot contain blank values"
            )


@dataclass(frozen=True)
class EvidenceLineage:
    observation_id: str
    steps: tuple[EvidenceTraceStep, ...]
    trace_status: TraceStatus
    trace_hash: str


def _normalized(value: Any) -> str:
    if value is None:
        return "UNKNOWN"

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip()

    return text if text else "UNKNOWN"


def _canonical_step_payload(
    step: EvidenceTraceStep,
) -> dict[str, object]:
    return {
        "sequence": step.sequence,
        "stage": step.stage.value,
        "input_state": step.input_state,
        "output_state": step.output_state,
        "reason": step.reason,
        "source_ids": list(
            step.source_ids
        ),
    }


def _lineage_hash(
    observation_id: str,
    steps: tuple[EvidenceTraceStep, ...],
) -> str:
    payload = {
        "observation_id": observation_id,
        "steps": [
            _canonical_step_payload(step)
            for step in steps
        ],
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return sha256(
        encoded
    ).hexdigest()


def build_evidence_lineage(
    *,
    observation_id: str,
    steps: Iterable[EvidenceTraceStep],
) -> EvidenceLineage:
    """
    Build an immutable lineage record.

    This function records prior analytical decisions.
    It does not change those decisions.
    """

    observation_id = observation_id.strip()

    if not observation_id:
        raise ValueError(
            "observation_id cannot be blank"
        )

    supplied = tuple(
        steps
    )

    if not supplied:

        return EvidenceLineage(
            observation_id=observation_id,
            steps=(),
            trace_status=TraceStatus.UNKNOWN,
            trace_hash=_lineage_hash(
                observation_id,
                (),
            ),
        )

    sequences = tuple(
        step.sequence
        for step in supplied
    )

    if len(set(sequences)) != len(sequences):
        raise ValueError(
            "duplicate trace sequence"
        )

    ordered = tuple(
        sorted(
            supplied,
            key=lambda item: item.sequence,
        )
    )

    expected = tuple(
        range(
            ordered[0].sequence,
            ordered[0].sequence
            + len(ordered),
        )
    )

    actual = tuple(
        step.sequence
        for step in ordered
    )

    if actual != expected:

        status = TraceStatus.BROKEN

    else:

        stages = {
            step.stage
            for step in ordered
        }

        required = {
            LineageStage.SOURCE,
            LineageStage.PROVENANCE,
            LineageStage.SOURCE_AUTHORITY,
            LineageStage.FRESHNESS,
            LineageStage.CORROBORATION,
            LineageStage.QUALITY,
            LineageStage.ANOMALY,
            LineageStage.SYNTHESIS,
            LineageStage.CONFLICT,
            LineageStage.ESCALATION,
            LineageStage.FINAL,
        }

        if required.issubset(stages):
            status = TraceStatus.COMPLETE
        else:
            status = TraceStatus.PARTIAL

    return EvidenceLineage(
        observation_id=observation_id,
        steps=ordered,
        trace_status=status,
        trace_hash=_lineage_hash(
            observation_id,
            ordered,
        ),
    )


def trace_step(
    *,
    sequence: int,
    stage: LineageStage,
    input_state: Any,
    output_state: Any,
    reason: str,
    source_ids: Iterable[str] = (),
) -> EvidenceTraceStep:
    """
    Construct one explicit immutable trace step.
    """

    return EvidenceTraceStep(
        sequence=sequence,
        stage=stage,
        input_state=_normalized(
            input_state
        ),
        output_state=_normalized(
            output_state
        ),
        reason=reason.strip(),
        source_ids=tuple(
            source_ids
        ),
    )


def decision_path(
    lineage: EvidenceLineage,
) -> tuple[str, ...]:
    return tuple(
        f"{step.stage.value}:{step.output_state}"
        for step in lineage.steps
    )


def trace_is_complete(
    lineage: EvidenceLineage,
) -> bool:
    return (
        lineage.trace_status
        is TraceStatus.COMPLETE
    )


def trace_requires_review(
    lineage: EvidenceLineage,
) -> bool:
    return lineage.trace_status in {
        TraceStatus.PARTIAL,
        TraceStatus.BROKEN,
        TraceStatus.UNKNOWN,
    }


def lineage_snapshot(
    lineage: EvidenceLineage,
) -> dict[str, object]:
    return {
        "observation_id": lineage.observation_id,
        "trace_status": lineage.trace_status.value,
        "trace_hash": lineage.trace_hash,
        "decision_path": list(
            decision_path(lineage)
        ),
        "steps": [
            _canonical_step_payload(step)
            for step in lineage.steps
        ],
    }
