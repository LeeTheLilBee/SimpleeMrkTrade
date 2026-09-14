from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class GateVerdict(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


class CompositionState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


REQUIRED_GATES = (
    "source_provenance",
    "freshness",
    "corroboration",
    "quality",
    "effective_observation",
    "conflict",
    "lineage",
    "current_version",
    "lifecycle",
    "revocation",
    "rehabilitation",
    "temporal_validity",
    "instrument_binding",
)


@dataclass(frozen=True)
class ReasoningTarget:
    target_id: str
    observation_id: str
    observation_version: int
    target_symbol: str
    target_instrument_kind: str
    purpose: str


@dataclass(frozen=True)
class GateAssessment:
    gate: str
    verdict: GateVerdict
    reason: str


@dataclass(frozen=True)
class ReasoningContextAssessment:
    target: ReasoningTarget
    state: CompositionState
    gate_assessments: tuple[GateAssessment, ...]
    blocking_gates: tuple[str, ...]
    review_gates: tuple[str, ...]
    unknown_gates: tuple[str, ...]
    reasons: tuple[str, ...]


def _require_nonblank(value: str, *, name: str) -> str:
    normalized = str(value).strip()

    if not normalized:
        raise ValueError(
            f"{name} cannot be blank"
        )

    return normalized


def build_reasoning_target(
    *,
    target_id: str,
    observation_id: str,
    observation_version: int,
    target_symbol: str,
    target_instrument_kind: str,
    purpose: str,
) -> ReasoningTarget:
    if observation_version < 1:
        raise ValueError(
            "observation_version must be >= 1"
        )

    return ReasoningTarget(
        target_id=_require_nonblank(
            target_id,
            name="target_id",
        ),
        observation_id=_require_nonblank(
            observation_id,
            name="observation_id",
        ),
        observation_version=observation_version,
        target_symbol=_require_nonblank(
            target_symbol,
            name="target_symbol",
        ).upper(),
        target_instrument_kind=_require_nonblank(
            target_instrument_kind,
            name="target_instrument_kind",
        ).upper(),
        purpose=_require_nonblank(
            purpose,
            name="purpose",
        ),
    )


def gate_assessment(
    *,
    gate: str,
    verdict: GateVerdict,
    reason: str,
) -> GateAssessment:
    gate = _require_nonblank(
        gate,
        name="gate",
    )

    reason = _require_nonblank(
        reason,
        name="reason",
    )

    if gate not in REQUIRED_GATES:
        raise ValueError(
            f"unknown composition gate: {gate}"
        )

    if not isinstance(
        verdict,
        GateVerdict,
    ):
        raise ValueError(
            "verdict must be GateVerdict"
        )

    return GateAssessment(
        gate=gate,
        verdict=verdict,
        reason=reason,
    )


def compose_reasoning_context(
    *,
    target: ReasoningTarget,
    gates: Mapping[str, GateAssessment],
) -> ReasoningContextAssessment:
    supplied = set(
        gates.keys()
    )

    required = set(
        REQUIRED_GATES
    )

    missing = sorted(
        required - supplied
    )

    extra = sorted(
        supplied - required
    )

    if extra:
        raise ValueError(
            "unexpected composition gates: "
            + ", ".join(extra)
        )

    if missing:
        assessments = tuple(
            gates[name]
            for name in REQUIRED_GATES
            if name in gates
        )

        reasons = tuple(
            f"Missing required authority gate: {name}."
            for name in missing
        )

        return ReasoningContextAssessment(
            target=target,
            state=CompositionState.UNKNOWN,
            gate_assessments=assessments,
            blocking_gates=(),
            review_gates=(),
            unknown_gates=tuple(
                missing
            ),
            reasons=reasons,
        )

    ordered = []

    for name in REQUIRED_GATES:
        assessment = gates[name]

        if assessment.gate != name:
            raise ValueError(
                f"gate mapping mismatch for {name}"
            )

        ordered.append(
            assessment
        )

    blocking = tuple(
        item.gate
        for item in ordered
        if item.verdict is GateVerdict.BLOCK
    )

    reviewing = tuple(
        item.gate
        for item in ordered
        if item.verdict is GateVerdict.REVIEW
    )

    unknown = tuple(
        item.gate
        for item in ordered
        if item.verdict is GateVerdict.UNKNOWN
    )

    if blocking:
        state = CompositionState.BLOCKED

        reasons = tuple(
            item.reason
            for item in ordered
            if item.verdict is GateVerdict.BLOCK
        )

    elif unknown:
        state = CompositionState.UNKNOWN

        reasons = tuple(
            item.reason
            for item in ordered
            if item.verdict is GateVerdict.UNKNOWN
        )

    elif reviewing:
        state = CompositionState.REVIEW_REQUIRED

        reasons = tuple(
            item.reason
            for item in ordered
            if item.verdict is GateVerdict.REVIEW
        )

    else:
        all_allow = all(
            item.verdict is GateVerdict.ALLOW
            for item in ordered
        )

        if not all_allow:
            state = CompositionState.UNKNOWN
            reasons = (
                "Composition reached an unrecognized gate state.",
            )
        else:
            state = CompositionState.ELIGIBLE
            reasons = (
                "All required upstream authority gates explicitly allow current analytical reasoning.",
            )

    return ReasoningContextAssessment(
        target=target,
        state=state,
        gate_assessments=tuple(
            ordered
        ),
        blocking_gates=blocking,
        review_gates=reviewing,
        unknown_gates=unknown,
        reasons=reasons,
    )


def eligible_for_current_analytical_reasoning(
    assessment: ReasoningContextAssessment,
) -> bool:
    if assessment.state is not CompositionState.ELIGIBLE:
        return False

    if len(assessment.gate_assessments) != len(REQUIRED_GATES):
        return False

    return all(
        item.verdict is GateVerdict.ALLOW
        for item in assessment.gate_assessments
    )


def blocked_from_current_analytical_reasoning(
    assessment: ReasoningContextAssessment,
) -> bool:
    return assessment.state in {
        CompositionState.BLOCKED,
        CompositionState.REVIEW_REQUIRED,
        CompositionState.UNKNOWN,
    }


def composition_snapshot(
    assessment: ReasoningContextAssessment,
) -> dict[str, object]:
    return {
        "target": {
            "target_id": assessment.target.target_id,
            "observation_id": assessment.target.observation_id,
            "observation_version": assessment.target.observation_version,
            "target_symbol": assessment.target.target_symbol,
            "target_instrument_kind": assessment.target.target_instrument_kind,
            "purpose": assessment.target.purpose,
        },
        "state": assessment.state.value,
        "gates": [
            {
                "gate": item.gate,
                "verdict": item.verdict.value,
                "reason": item.reason,
            }
            for item in assessment.gate_assessments
        ],
        "blocking_gates": list(
            assessment.blocking_gates
        ),
        "review_gates": list(
            assessment.review_gates
        ),
        "unknown_gates": list(
            assessment.unknown_gates
        ),
        "reasons": list(
            assessment.reasons
        ),
    }
