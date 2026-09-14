
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class SourceKind(str, Enum):
    MARKET_DATA = "MARKET_DATA"
    BROKER_DATA = "BROKER_DATA"
    USER_INPUT = "USER_INPUT"
    DERIVED = "DERIVED"
    INTERNAL_SYSTEM = "INTERNAL_SYSTEM"
    UNKNOWN = "UNKNOWN"


class SourceAuthority(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    CORROBORATING = "CORROBORATING"
    ADVISORY = "ADVISORY"
    UNVERIFIED = "UNVERIFIED"


class ProvenanceStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class SourceIdentity:
    source_id: str
    display_name: str
    source_kind: SourceKind
    authority: SourceAuthority

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.display_name or not self.display_name.strip():
            raise ValueError("display_name is required")


@dataclass(frozen=True)
class SourceProvenance:
    source: SourceIdentity
    observed_at: datetime
    retrieved_at: datetime
    instrument: str | None = None
    provider_event_id: str | None = None
    sequence: str | None = None
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        observed = _ensure_aware(self.observed_at, "observed_at")
        retrieved = _ensure_aware(self.retrieved_at, "retrieved_at")

        if retrieved < observed:
            raise ValueError("retrieved_at cannot precede observed_at")

        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "retrieved_at", retrieved)

    @property
    def status(self) -> ProvenanceStatus:
        if (
            self.source.source_id
            and self.source.display_name
            and self.observed_at
            and self.retrieved_at
        ):
            return ProvenanceStatus.COMPLETE
        return ProvenanceStatus.INCOMPLETE

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": {
                "source_id": self.source.source_id,
                "display_name": self.source.display_name,
                "source_kind": self.source.source_kind.value,
                "authority": self.source.authority.value,
            },
            "observed_at": self.observed_at.isoformat(),
            "retrieved_at": self.retrieved_at.isoformat(),
            "instrument": self.instrument,
            "provider_event_id": self.provider_event_id,
            "sequence": self.sequence,
            "metadata": dict(self.metadata or {}),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ProvenancedObservation:
    value: Any
    provenance: SourceProvenance

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "provenance": self.provenance.as_dict(),
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_source(
    *,
    source_id: str,
    display_name: str,
    source_kind: SourceKind,
    authority: SourceAuthority,
) -> SourceIdentity:
    return SourceIdentity(
        source_id=source_id.strip(),
        display_name=display_name.strip(),
        source_kind=source_kind,
        authority=authority,
    )


def provenance_for(
    *,
    source: SourceIdentity,
    observed_at: datetime,
    retrieved_at: datetime | None = None,
    instrument: str | None = None,
    provider_event_id: str | None = None,
    sequence: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> SourceProvenance:
    return SourceProvenance(
        source=source,
        observed_at=observed_at,
        retrieved_at=retrieved_at or utc_now(),
        instrument=instrument,
        provider_event_id=provider_event_id,
        sequence=sequence,
        metadata=metadata,
    )


def attach_provenance(
    value: Any,
    provenance: SourceProvenance,
) -> ProvenancedObservation:
    """
    Attach descriptive provenance to an observation.

    IMPORTANT:
    This function does not authorize a trade, determine operating mode,
    submit an order, move capital, select a broker contract, or alter
    execution state.
    """
    return ProvenancedObservation(
        value=value,
        provenance=provenance,
    )


def _ensure_aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)
