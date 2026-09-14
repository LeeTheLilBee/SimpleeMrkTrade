from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from statistics import median
from typing import Iterable, Sequence


class ObservationQuality(str, Enum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class AnomalyStatus(str, Enum):
    NORMAL = "NORMAL"
    SUSPECT = "SUSPECT"
    OUTLIER = "OUTLIER"
    IMPOSSIBLE = "IMPOSSIBLE"
    UNKNOWN = "UNKNOWN"


class ObservationDisposition(str, Enum):
    ACCEPT = "ACCEPT"
    REVIEW = "REVIEW"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObservationQualityPolicy:
    allow_zero: bool = True
    allow_negative: bool = False
    minimum_value: float | None = None
    maximum_value: float | None = None
    suspect_relative_deviation: float = 0.05
    outlier_relative_deviation: float = 0.20

    def __post_init__(self) -> None:
        if self.minimum_value is not None:
            if not isfinite(float(self.minimum_value)):
                raise ValueError("minimum_value must be finite")

        if self.maximum_value is not None:
            if not isfinite(float(self.maximum_value)):
                raise ValueError("maximum_value must be finite")

        if (
            self.minimum_value is not None
            and self.maximum_value is not None
            and self.minimum_value > self.maximum_value
        ):
            raise ValueError(
                "minimum_value cannot exceed maximum_value"
            )

        if self.suspect_relative_deviation < 0:
            raise ValueError(
                "suspect_relative_deviation cannot be negative"
            )

        if self.outlier_relative_deviation < 0:
            raise ValueError(
                "outlier_relative_deviation cannot be negative"
            )

        if (
            self.suspect_relative_deviation
            > self.outlier_relative_deviation
        ):
            raise ValueError(
                "suspect threshold must be <= outlier threshold"
            )


@dataclass(frozen=True)
class ObservationQualityAssessment:
    quality: ObservationQuality
    anomaly: AnomalyStatus
    disposition: ObservationDisposition
    value: float | None
    reference_value: float | None
    relative_deviation: float | None
    reasons: tuple[str, ...]


DEFAULT_MARKET_VALUE_POLICY = ObservationQualityPolicy(
    allow_zero=False,
    allow_negative=False,
    minimum_value=0.0,
    maximum_value=None,
    suspect_relative_deviation=0.05,
    outlier_relative_deviation=0.20,
)


def _disposition(
    quality: ObservationQuality,
    anomaly: AnomalyStatus,
) -> ObservationDisposition:
    if quality is ObservationQuality.INVALID:
        return ObservationDisposition.REJECT

    if anomaly is AnomalyStatus.IMPOSSIBLE:
        return ObservationDisposition.REJECT

    if anomaly is AnomalyStatus.OUTLIER:
        return ObservationDisposition.QUARANTINE

    if (
        quality is ObservationQuality.DEGRADED
        or anomaly is AnomalyStatus.SUSPECT
    ):
        return ObservationDisposition.REVIEW

    if (
        quality is ObservationQuality.VALID
        and anomaly is AnomalyStatus.NORMAL
    ):
        return ObservationDisposition.ACCEPT

    return ObservationDisposition.UNKNOWN


def _relative_deviation(
    value: float,
    reference_value: float,
) -> float:
    denominator = abs(reference_value)

    if denominator == 0:
        if value == reference_value:
            return 0.0

        return float("inf")

    return abs(value - reference_value) / denominator


def evaluate_observation_quality(
    value: object,
    *,
    reference_value: float | None = None,
    policy: ObservationQualityPolicy = DEFAULT_MARKET_VALUE_POLICY,
) -> ObservationQualityAssessment:
    """
    Evaluate structural observation quality and anomaly state.

    This does NOT:
    - repair a bad value
    - invent a replacement
    - choose a broker action
    - change operating mode
    - move capital
    """

    reasons: list[str] = []

    try:
        numeric = float(value)

    except (TypeError, ValueError):

        return ObservationQualityAssessment(
            quality=ObservationQuality.INVALID,
            anomaly=AnomalyStatus.IMPOSSIBLE,
            disposition=ObservationDisposition.REJECT,
            value=None,
            reference_value=reference_value,
            relative_deviation=None,
            reasons=(
                "Observation value is not numeric.",
            ),
        )

    if not isfinite(numeric):

        return ObservationQualityAssessment(
            quality=ObservationQuality.INVALID,
            anomaly=AnomalyStatus.IMPOSSIBLE,
            disposition=ObservationDisposition.REJECT,
            value=numeric,
            reference_value=reference_value,
            relative_deviation=None,
            reasons=(
                "Observation value is not finite.",
            ),
        )

    quality = ObservationQuality.VALID
    anomaly = AnomalyStatus.NORMAL

    if numeric == 0 and not policy.allow_zero:
        quality = ObservationQuality.INVALID
        anomaly = AnomalyStatus.IMPOSSIBLE
        reasons.append(
            "Zero is not allowed for this observation policy."
        )

    if numeric < 0 and not policy.allow_negative:
        quality = ObservationQuality.INVALID
        anomaly = AnomalyStatus.IMPOSSIBLE
        reasons.append(
            "Negative values are not allowed for this observation policy."
        )

    if (
        policy.minimum_value is not None
        and numeric < policy.minimum_value
    ):
        quality = ObservationQuality.INVALID
        anomaly = AnomalyStatus.IMPOSSIBLE
        reasons.append(
            "Observation is below the configured minimum."
        )

    if (
        policy.maximum_value is not None
        and numeric > policy.maximum_value
    ):
        quality = ObservationQuality.INVALID
        anomaly = AnomalyStatus.IMPOSSIBLE
        reasons.append(
            "Observation exceeds the configured maximum."
        )

    relative_deviation = None

    if (
        reference_value is not None
        and quality is not ObservationQuality.INVALID
    ):
        ref = float(reference_value)

        if not isfinite(ref):
            quality = ObservationQuality.DEGRADED
            anomaly = AnomalyStatus.UNKNOWN
            reasons.append(
                "Reference value is non-finite."
            )

        else:
            relative_deviation = _relative_deviation(
                numeric,
                ref,
            )

            if (
                relative_deviation
                > policy.outlier_relative_deviation
            ):
                anomaly = AnomalyStatus.OUTLIER

                reasons.append(
                    "Observation exceeds the configured outlier deviation threshold."
                )

            elif (
                relative_deviation
                > policy.suspect_relative_deviation
            ):
                anomaly = AnomalyStatus.SUSPECT

                reasons.append(
                    "Observation exceeds the configured suspect deviation threshold."
                )

    if not reasons:
        reasons.append(
            "Observation passed structural and anomaly checks."
        )

    return ObservationQualityAssessment(
        quality=quality,
        anomaly=anomaly,
        disposition=_disposition(
            quality,
            anomaly,
        ),
        value=numeric,
        reference_value=reference_value,
        relative_deviation=relative_deviation,
        reasons=tuple(reasons),
    )


def robust_reference_value(
    values: Iterable[float],
) -> float | None:
    """
    Median-based reference used only as an analytical comparison anchor.

    It is NOT a corrected market price and must not replace source observations.
    """

    clean = []

    for value in values:

        numeric = float(value)

        if isfinite(numeric):
            clean.append(numeric)

    if not clean:
        return None

    return float(
        median(clean)
    )


def evaluate_against_peer_group(
    value: object,
    peer_values: Sequence[float],
    *,
    policy: ObservationQualityPolicy = DEFAULT_MARKET_VALUE_POLICY,
) -> ObservationQualityAssessment:
    reference = robust_reference_value(
        peer_values
    )

    return evaluate_observation_quality(
        value,
        reference_value=reference,
        policy=policy,
    )


def usable_without_review(
    assessment: ObservationQualityAssessment,
) -> bool:
    return (
        assessment.disposition
        is ObservationDisposition.ACCEPT
    )


def requires_quality_review(
    assessment: ObservationQualityAssessment,
) -> bool:
    return (
        assessment.disposition
        is ObservationDisposition.REVIEW
    )


def must_quarantine(
    assessment: ObservationQualityAssessment,
) -> bool:
    return (
        assessment.disposition
        is ObservationDisposition.QUARANTINE
    )


def must_reject(
    assessment: ObservationQualityAssessment,
) -> bool:
    return (
        assessment.disposition
        is ObservationDisposition.REJECT
    )


def quality_snapshot(
    assessment: ObservationQualityAssessment,
) -> dict[str, object]:
    return {
        "quality": assessment.quality.value,
        "anomaly": assessment.anomaly.value,
        "disposition": assessment.disposition.value,
        "value": assessment.value,
        "reference_value": assessment.reference_value,
        "relative_deviation": assessment.relative_deviation,
        "reasons": list(assessment.reasons),
    }
