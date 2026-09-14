from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class VersionStatus(str, Enum):
    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"
    HISTORICAL = "HISTORICAL"
    UNKNOWN = "UNKNOWN"


class SupersessionReason(str, Enum):
    FRESHER_EVIDENCE = "FRESHER_EVIDENCE"
    CORROBORATION_CHANGED = "CORROBORATION_CHANGED"
    QUALITY_CHANGED = "QUALITY_CHANGED"
    CONFLICT_CHANGED = "CONFLICT_CHANGED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObservationVersion:
    observation_id: str
    version: int
    effective_state: str
    confidence: str
    lineage_hash: str
    supersedes_version: int | None = None
    supersession_reason: SupersessionReason | None = None

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError(
                "observation_id cannot be blank"
            )

        if self.version < 1:
            raise ValueError(
                "version must be >= 1"
            )

        if not self.effective_state.strip():
            raise ValueError(
                "effective_state cannot be blank"
            )

        if not self.confidence.strip():
            raise ValueError(
                "confidence cannot be blank"
            )

        if not self.lineage_hash.strip():
            raise ValueError(
                "lineage_hash cannot be blank"
            )

        if self.supersedes_version is not None:
            if self.supersedes_version < 1:
                raise ValueError(
                    "supersedes_version must be >= 1"
                )

            if self.supersedes_version >= self.version:
                raise ValueError(
                    "supersedes_version must be less than version"
                )

            if self.supersession_reason is None:
                raise ValueError(
                    "supersession_reason required when superseding a prior version"
                )

        elif self.supersession_reason is not None:
            raise ValueError(
                "supersession_reason requires supersedes_version"
            )


@dataclass(frozen=True)
class VersionedObservationHistory:
    observation_id: str
    versions: tuple[ObservationVersion, ...]
    current_version: int | None


def create_initial_version(
    *,
    observation_id: str,
    effective_state: Any,
    confidence: Any,
    lineage_hash: str,
) -> ObservationVersion:
    return ObservationVersion(
        observation_id=observation_id,
        version=1,
        effective_state=str(
            getattr(
                effective_state,
                "value",
                effective_state,
            )
        ).strip(),
        confidence=str(
            getattr(
                confidence,
                "value",
                confidence,
            )
        ).strip(),
        lineage_hash=lineage_hash.strip(),
    )


def supersede_observation(
    *,
    prior: ObservationVersion,
    effective_state: Any,
    confidence: Any,
    lineage_hash: str,
    reason: SupersessionReason,
) -> ObservationVersion:
    """
    Create a new immutable version that explicitly supersedes the prior version.

    The prior object is never mutated.
    """

    return ObservationVersion(
        observation_id=prior.observation_id,
        version=prior.version + 1,
        effective_state=str(
            getattr(
                effective_state,
                "value",
                effective_state,
            )
        ).strip(),
        confidence=str(
            getattr(
                confidence,
                "value",
                confidence,
            )
        ).strip(),
        lineage_hash=lineage_hash.strip(),
        supersedes_version=prior.version,
        supersession_reason=reason,
    )


def build_version_history(
    versions: Iterable[ObservationVersion],
) -> VersionedObservationHistory:
    supplied = tuple(
        versions
    )

    if not supplied:
        return VersionedObservationHistory(
            observation_id="",
            versions=(),
            current_version=None,
        )

    observation_ids = {
        item.observation_id
        for item in supplied
    }

    if len(observation_ids) != 1:
        raise ValueError(
            "version history cannot mix observation identities"
        )

    by_number = {}

    for item in supplied:

        if item.version in by_number:
            raise ValueError(
                f"duplicate version: {item.version}"
            )

        by_number[item.version] = item

    ordered = tuple(
        sorted(
            supplied,
            key=lambda item: item.version,
        )
    )

    expected_numbers = tuple(
        range(
            1,
            len(ordered) + 1,
        )
    )

    actual_numbers = tuple(
        item.version
        for item in ordered
    )

    if actual_numbers != expected_numbers:
        raise ValueError(
            "version history must be contiguous starting at version 1"
        )

    for item in ordered:

        if item.version == 1:
            if item.supersedes_version is not None:
                raise ValueError(
                    "version 1 cannot supersede another version"
                )

            continue

        expected_prior = item.version - 1

        if item.supersedes_version != expected_prior:
            raise ValueError(
                (
                    f"version {item.version} must explicitly supersede "
                    f"version {expected_prior}"
                )
            )

    return VersionedObservationHistory(
        observation_id=ordered[0].observation_id,
        versions=ordered,
        current_version=ordered[-1].version,
    )


def version_status(
    history: VersionedObservationHistory,
    version: int,
) -> VersionStatus:
    if not history.versions:
        return VersionStatus.UNKNOWN

    known = {
        item.version
        for item in history.versions
    }

    if version not in known:
        return VersionStatus.UNKNOWN

    if version == history.current_version:
        return VersionStatus.CURRENT

    if version < history.current_version:
        return VersionStatus.SUPERSEDED

    return VersionStatus.HISTORICAL


def current_observation(
    history: VersionedObservationHistory,
) -> ObservationVersion | None:
    if history.current_version is None:
        return None

    matches = [
        item
        for item in history.versions
        if item.version == history.current_version
    ]

    if len(matches) != 1:
        raise ValueError(
            "history does not resolve to exactly one current version"
        )

    return matches[0]


def supersession_chain(
    history: VersionedObservationHistory,
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (
            item.supersedes_version,
            item.version,
        )
        for item in history.versions
        if item.supersedes_version is not None
    )


def version_history_snapshot(
    history: VersionedObservationHistory,
) -> dict[str, object]:
    current = current_observation(
        history
    )

    return {
        "observation_id": history.observation_id,
        "current_version": history.current_version,
        "current_effective_state": (
            current.effective_state
            if current is not None
            else None
        ),
        "current_confidence": (
            current.confidence
            if current is not None
            else None
        ),
        "supersession_chain": [
            {
                "from_version": prior,
                "to_version": later,
            }
            for prior, later
            in supersession_chain(history)
        ],
        "versions": [
            {
                "version": item.version,
                "status": version_status(
                    history,
                    item.version,
                ).value,
                "effective_state": item.effective_state,
                "confidence": item.confidence,
                "lineage_hash": item.lineage_hash,
                "supersedes_version": item.supersedes_version,
                "supersession_reason": (
                    item.supersession_reason.value
                    if item.supersession_reason is not None
                    else None
                ),
            }
            for item in history.versions
        ],
    }
