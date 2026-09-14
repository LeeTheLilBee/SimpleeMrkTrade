from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class ObservationClass(str, Enum):
    REALTIME_QUOTE = "REALTIME_QUOTE"
    MARKET_SNAPSHOT = "MARKET_SNAPSHOT"
    SESSION_DATA = "SESSION_DATA"
    REFERENCE_DATA = "REFERENCE_DATA"
    USER_INPUT = "USER_INPUT"
    DERIVED = "DERIVED"


class FreshnessUse(str, Enum):
    CURRENT_ANALYSIS_OK = "CURRENT_ANALYSIS_OK"
    REVIEW_WITH_CAUTION = "REVIEW_WITH_CAUTION"
    DO_NOT_TREAT_AS_CURRENT = "DO_NOT_TREAT_AS_CURRENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FreshnessPolicy:
    fresh_for: timedelta
    aging_for: timedelta
    expires_after: timedelta

    def __post_init__(self) -> None:
        if self.fresh_for < timedelta(0):
            raise ValueError("fresh_for cannot be negative")

        if self.aging_for < self.fresh_for:
            raise ValueError("aging_for must be >= fresh_for")

        if self.expires_after < self.aging_for:
            raise ValueError("expires_after must be >= aging_for")


@dataclass(frozen=True)
class FreshnessAssessment:
    observation_class: ObservationClass
    status: FreshnessStatus
    age_seconds: float | None
    observed_at: datetime | None
    retrieved_at: datetime | None
    policy: FreshnessPolicy | None
    use: FreshnessUse
    reason: str


_DEFAULT_POLICIES = {
    ObservationClass.REALTIME_QUOTE: FreshnessPolicy(
        fresh_for=timedelta(seconds=15),
        aging_for=timedelta(seconds=60),
        expires_after=timedelta(minutes=5),
    ),
    ObservationClass.MARKET_SNAPSHOT: FreshnessPolicy(
        fresh_for=timedelta(minutes=1),
        aging_for=timedelta(minutes=5),
        expires_after=timedelta(minutes=15),
    ),
    ObservationClass.SESSION_DATA: FreshnessPolicy(
        fresh_for=timedelta(minutes=15),
        aging_for=timedelta(hours=1),
        expires_after=timedelta(days=1),
    ),
    ObservationClass.REFERENCE_DATA: FreshnessPolicy(
        fresh_for=timedelta(days=7),
        aging_for=timedelta(days=30),
        expires_after=timedelta(days=180),
    ),
    ObservationClass.USER_INPUT: FreshnessPolicy(
        fresh_for=timedelta(hours=1),
        aging_for=timedelta(days=1),
        expires_after=timedelta(days=30),
    ),
    ObservationClass.DERIVED: FreshnessPolicy(
        fresh_for=timedelta(minutes=1),
        aging_for=timedelta(minutes=5),
        expires_after=timedelta(minutes=15),
    ),
}


DEFAULT_FRESHNESS_POLICIES: Mapping[
    ObservationClass,
    FreshnessPolicy,
] = MappingProxyType(_DEFAULT_POLICIES)


_STATUS_RANK = {
    FreshnessStatus.FRESH: 0,
    FreshnessStatus.AGING: 1,
    FreshnessStatus.STALE: 2,
    FreshnessStatus.EXPIRED: 3,
    FreshnessStatus.UNKNOWN: 4,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _aware_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("freshness timestamps must be timezone-aware")

    return value.astimezone(timezone.utc)


def use_for_status(status: FreshnessStatus) -> FreshnessUse:
    if status is FreshnessStatus.FRESH:
        return FreshnessUse.CURRENT_ANALYSIS_OK

    if status is FreshnessStatus.AGING:
        return FreshnessUse.REVIEW_WITH_CAUTION

    if status in {
        FreshnessStatus.STALE,
        FreshnessStatus.EXPIRED,
    }:
        return FreshnessUse.DO_NOT_TREAT_AS_CURRENT

    return FreshnessUse.UNKNOWN


def classify_age(
    age: timedelta,
    policy: FreshnessPolicy,
) -> FreshnessStatus:
    if age < timedelta(0):
        return FreshnessStatus.UNKNOWN

    if age <= policy.fresh_for:
        return FreshnessStatus.FRESH

    if age <= policy.aging_for:
        return FreshnessStatus.AGING

    if age <= policy.expires_after:
        return FreshnessStatus.STALE

    return FreshnessStatus.EXPIRED


def evaluate_freshness(
    provenance: Any,
    observation_class: ObservationClass,
    *,
    now: datetime | None = None,
    policy: FreshnessPolicy | None = None,
) -> FreshnessAssessment:
    """
    Evaluate whether a provenanced observation is current enough for a particular data context.

    This function is descriptive authority only.
    It does not submit orders, move capital, choose contracts, or change operating mode.
    """

    selected_policy = (
        policy
        if policy is not None
        else DEFAULT_FRESHNESS_POLICIES.get(observation_class)
    )

    if selected_policy is None:
        return FreshnessAssessment(
            observation_class=observation_class,
            status=FreshnessStatus.UNKNOWN,
            age_seconds=None,
            observed_at=None,
            retrieved_at=None,
            policy=None,
            use=FreshnessUse.UNKNOWN,
            reason="No freshness policy exists for this observation class.",
        )

    observed_at = _aware_utc(
        getattr(
            provenance,
            "observed_at",
            None,
        )
    )

    retrieved_at = _aware_utc(
        getattr(
            provenance,
            "retrieved_at",
            None,
        )
    )

    if observed_at is None or retrieved_at is None:
        return FreshnessAssessment(
            observation_class=observation_class,
            status=FreshnessStatus.UNKNOWN,
            age_seconds=None,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            policy=selected_policy,
            use=FreshnessUse.UNKNOWN,
            reason="Observation or retrieval timestamp is missing.",
        )

    if retrieved_at < observed_at:
        return FreshnessAssessment(
            observation_class=observation_class,
            status=FreshnessStatus.UNKNOWN,
            age_seconds=None,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            policy=selected_policy,
            use=FreshnessUse.UNKNOWN,
            reason="Retrieval timestamp precedes observation timestamp.",
        )

    effective_now = _aware_utc(
        now
        if now is not None
        else utc_now()
    )

    assert effective_now is not None

    age = effective_now - observed_at

    status = classify_age(
        age,
        selected_policy,
    )

    if status is FreshnessStatus.UNKNOWN:
        reason = (
            "Observation timestamp is in the future relative to the evaluation clock."
        )

        age_seconds = None

    else:
        age_seconds = age.total_seconds()

        reason = (
            f"{observation_class.value} observation evaluated as "
            f"{status.value} at {age_seconds:.3f} seconds old."
        )

    return FreshnessAssessment(
        observation_class=observation_class,
        status=status,
        age_seconds=age_seconds,
        observed_at=observed_at,
        retrieved_at=retrieved_at,
        policy=selected_policy,
        use=use_for_status(status),
        reason=reason,
    )


def worst_freshness_status(
    statuses: Iterable[FreshnessStatus],
) -> FreshnessStatus:
    values = tuple(statuses)

    if not values:
        return FreshnessStatus.UNKNOWN

    return max(
        values,
        key=lambda item: _STATUS_RANK[item],
    )


def propagate_derived_freshness(
    own_assessment: FreshnessAssessment,
    input_assessments: Iterable[FreshnessAssessment],
) -> FreshnessAssessment:
    """
    Derived information cannot become fresher than the least-current input.

    The derived result may retain its own worse state, but it may never outrank
    a stale, expired, or unknown input.
    """

    inputs = tuple(input_assessments)

    if not inputs:
        return replace(
            own_assessment,
            status=FreshnessStatus.UNKNOWN,
            use=FreshnessUse.UNKNOWN,
            reason=(
                "Derived observation has no input freshness evidence."
            ),
        )

    effective_status = worst_freshness_status(
        (
            own_assessment.status,
            *(
                assessment.status
                for assessment in inputs
            ),
        )
    )

    if effective_status is own_assessment.status:
        reason = (
            own_assessment.reason
            + " Derived result does not outrank any input freshness state."
        )
    else:
        reason = (
            "Derived freshness was reduced to "
            f"{effective_status.value} because at least one input "
            "is less current than the derived observation itself."
        )

    return replace(
        own_assessment,
        status=effective_status,
        use=use_for_status(effective_status),
        reason=reason,
    )


def suitable_for_current_analysis(
    assessment: FreshnessAssessment,
) -> bool:
    """
    Freshness suitability is intentionally conservative.

    FRESH may be treated as current.
    AGING requires review.
    STALE / EXPIRED / UNKNOWN are not current-market truth.

    This is not execution permission.
    """

    return (
        assessment.status
        is FreshnessStatus.FRESH
    )


def requires_freshness_review(
    assessment: FreshnessAssessment,
) -> bool:
    return (
        assessment.status
        is FreshnessStatus.AGING
    )


def must_not_be_treated_as_current(
    assessment: FreshnessAssessment,
) -> bool:
    return assessment.status in {
        FreshnessStatus.STALE,
        FreshnessStatus.EXPIRED,
        FreshnessStatus.UNKNOWN,
    }


def freshness_snapshot(
    assessment: FreshnessAssessment,
) -> dict[str, object]:
    return {
        "observation_class": assessment.observation_class.value,
        "status": assessment.status.value,
        "age_seconds": assessment.age_seconds,
        "observed_at": (
            assessment.observed_at.isoformat()
            if assessment.observed_at is not None
            else None
        ),
        "retrieved_at": (
            assessment.retrieved_at.isoformat()
            if assessment.retrieved_at is not None
            else None
        ),
        "use": assessment.use.value,
        "reason": assessment.reason,
    }
