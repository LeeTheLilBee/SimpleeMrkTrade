from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from statistics import mean
from typing import Iterable, Sequence


class CorroborationStatus(str, Enum):
    SINGLE_SOURCE = "SINGLE_SOURCE"
    CORROBORATED = "CORROBORATED"
    MINOR_DISAGREEMENT = "MINOR_DISAGREEMENT"
    MATERIAL_DISAGREEMENT = "MATERIAL_DISAGREEMENT"
    CONFLICTED = "CONFLICTED"
    UNKNOWN = "UNKNOWN"


class ConfidenceUse(str, Enum):
    NORMAL_ANALYSIS = "NORMAL_ANALYSIS"
    REVIEW_WITH_CAUTION = "REVIEW_WITH_CAUTION"
    DO_NOT_TREAT_AS_SETTLED = "DO_NOT_TREAT_AS_SETTLED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SourceObservation:
    source_id: str
    value: float
    authoritative: bool = False
    fresh_enough: bool = True

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id cannot be blank")

        if not isfinite(float(self.value)):
            raise ValueError("value must be finite")


@dataclass(frozen=True)
class CorroborationPolicy:
    corroborated_relative_spread: float = 0.001
    minor_disagreement_relative_spread: float = 0.005
    material_disagreement_relative_spread: float = 0.02

    def __post_init__(self) -> None:
        values = (
            self.corroborated_relative_spread,
            self.minor_disagreement_relative_spread,
            self.material_disagreement_relative_spread,
        )

        if any(value < 0 for value in values):
            raise ValueError("corroboration thresholds cannot be negative")

        if not (
            self.corroborated_relative_spread
            <= self.minor_disagreement_relative_spread
            <= self.material_disagreement_relative_spread
        ):
            raise ValueError(
                "corroboration thresholds must be monotonically increasing"
            )


@dataclass(frozen=True)
class CorroborationAssessment:
    status: CorroborationStatus
    use: ConfidenceUse
    source_count: int
    eligible_source_count: int
    values: tuple[float, ...]
    source_ids: tuple[str, ...]
    center_value: float | None
    absolute_spread: float | None
    relative_spread: float | None
    reason: str


DEFAULT_CORROBORATION_POLICY = CorroborationPolicy()


def _use_for_status(
    status: CorroborationStatus,
) -> ConfidenceUse:
    if status in {
        CorroborationStatus.SINGLE_SOURCE,
        CorroborationStatus.CORROBORATED,
    }:
        return ConfidenceUse.NORMAL_ANALYSIS

    if status is CorroborationStatus.MINOR_DISAGREEMENT:
        return ConfidenceUse.REVIEW_WITH_CAUTION

    if status in {
        CorroborationStatus.MATERIAL_DISAGREEMENT,
        CorroborationStatus.CONFLICTED,
    }:
        return ConfidenceUse.DO_NOT_TREAT_AS_SETTLED

    return ConfidenceUse.UNKNOWN


def _relative_spread(
    values: Sequence[float],
) -> tuple[float, float, float]:
    low = min(values)
    high = max(values)

    center = mean(values)
    absolute = high - low

    denominator = abs(center)

    if denominator == 0:
        relative = (
            0.0
            if absolute == 0
            else float("inf")
        )
    else:
        relative = absolute / denominator

    return center, absolute, relative


def assess_corroboration(
    observations: Iterable[SourceObservation],
    *,
    policy: CorroborationPolicy = DEFAULT_CORROBORATION_POLICY,
) -> CorroborationAssessment:
    """
    Compare eligible independent observations.

    This function does not choose a preferred source.
    It does not submit orders, select contracts, move capital,
    or mutate operating mode.

    Observations that are not fresh enough are excluded from corroboration
    rather than silently treated as current.
    """

    supplied = tuple(observations)

    if not supplied:
        return CorroborationAssessment(
            status=CorroborationStatus.UNKNOWN,
            use=ConfidenceUse.UNKNOWN,
            source_count=0,
            eligible_source_count=0,
            values=(),
            source_ids=(),
            center_value=None,
            absolute_spread=None,
            relative_spread=None,
            reason="No source observations were supplied.",
        )

    seen = set()

    for item in supplied:
        if item.source_id in seen:
            raise ValueError(
                f"duplicate source_id is not independent corroboration: {item.source_id}"
            )

        seen.add(item.source_id)

    eligible = tuple(
        item
        for item in supplied
        if item.fresh_enough
    )

    if not eligible:
        return CorroborationAssessment(
            status=CorroborationStatus.UNKNOWN,
            use=ConfidenceUse.UNKNOWN,
            source_count=len(supplied),
            eligible_source_count=0,
            values=(),
            source_ids=(),
            center_value=None,
            absolute_spread=None,
            relative_spread=None,
            reason="No fresh-enough observations remain for corroboration.",
        )

    values = tuple(
        float(item.value)
        for item in eligible
    )

    source_ids = tuple(
        item.source_id
        for item in eligible
    )

    if len(eligible) == 1:
        return CorroborationAssessment(
            status=CorroborationStatus.SINGLE_SOURCE,
            use=ConfidenceUse.NORMAL_ANALYSIS,
            source_count=len(supplied),
            eligible_source_count=1,
            values=values,
            source_ids=source_ids,
            center_value=values[0],
            absolute_spread=0.0,
            relative_spread=0.0,
            reason="Only one fresh-enough independent source is available.",
        )

    center, absolute, relative = _relative_spread(values)

    if relative <= policy.corroborated_relative_spread:
        status = CorroborationStatus.CORROBORATED

    elif relative <= policy.minor_disagreement_relative_spread:
        status = CorroborationStatus.MINOR_DISAGREEMENT

    elif relative <= policy.material_disagreement_relative_spread:
        status = CorroborationStatus.MATERIAL_DISAGREEMENT

    else:
        status = CorroborationStatus.CONFLICTED

    return CorroborationAssessment(
        status=status,
        use=_use_for_status(status),
        source_count=len(supplied),
        eligible_source_count=len(eligible),
        values=values,
        source_ids=source_ids,
        center_value=center,
        absolute_spread=absolute,
        relative_spread=relative,
        reason=(
            f"{len(eligible)} independent fresh-enough sources "
            f"evaluated as {status.value} with relative spread {relative:.8f}."
        ),
    )


def corroborated_for_normal_analysis(
    assessment: CorroborationAssessment,
) -> bool:
    return assessment.status in {
        CorroborationStatus.SINGLE_SOURCE,
        CorroborationStatus.CORROBORATED,
    }


def requires_disagreement_review(
    assessment: CorroborationAssessment,
) -> bool:
    return assessment.status is CorroborationStatus.MINOR_DISAGREEMENT


def must_not_be_treated_as_settled(
    assessment: CorroborationAssessment,
) -> bool:
    return assessment.status in {
        CorroborationStatus.MATERIAL_DISAGREEMENT,
        CorroborationStatus.CONFLICTED,
        CorroborationStatus.UNKNOWN,
    }


def disagreement_snapshot(
    assessment: CorroborationAssessment,
) -> dict[str, object]:
    return {
        "status": assessment.status.value,
        "use": assessment.use.value,
        "source_count": assessment.source_count,
        "eligible_source_count": assessment.eligible_source_count,
        "source_ids": list(assessment.source_ids),
        "values": list(assessment.values),
        "center_value": assessment.center_value,
        "absolute_spread": assessment.absolute_spread,
        "relative_spread": assessment.relative_spread,
        "reason": assessment.reason,
    }
