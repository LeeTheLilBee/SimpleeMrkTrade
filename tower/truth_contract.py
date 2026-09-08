
"""Canonical Tower truth contract.

TWR121-TWR125 establishes the difference between:
- authoritative product truth,
- derived truth,
- cached truth,
- historical truth,
- evidence/test-only material,
- explicit unavailability.

The module deliberately refuses to manufacture plausible product state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


# --------------------------------------------------------------------------------------------------
# TWR121 — SOURCE CLASSES
# --------------------------------------------------------------------------------------------------

AUTHORITATIVE = "AUTHORITATIVE"
DERIVED = "DERIVED"
CACHED = "CACHED"
HISTORICAL = "HISTORICAL"
EVIDENCE_ONLY = "EVIDENCE_ONLY"
TEST_ONLY = "TEST_ONLY"
UNAVAILABLE_SOURCE = "UNAVAILABLE"

SOURCE_CLASSES = frozenset({
    AUTHORITATIVE,
    DERIVED,
    CACHED,
    HISTORICAL,
    EVIDENCE_ONLY,
    TEST_ONLY,
    UNAVAILABLE_SOURCE,
})


# --------------------------------------------------------------------------------------------------
# TWR122 — VERIFICATION STATES
# --------------------------------------------------------------------------------------------------

VERIFIED = "VERIFIED"
UNVERIFIED = "UNVERIFIED"
UNKNOWN = "UNKNOWN"
UNAVAILABLE = "UNAVAILABLE"
NOT_CONFIGURED = "NOT_CONFIGURED"
STALE = "STALE"

VERIFICATION_STATES = frozenset({
    VERIFIED,
    UNVERIFIED,
    UNKNOWN,
    UNAVAILABLE,
    NOT_CONFIGURED,
    STALE,
})


PRODUCT_FORBIDDEN_SOURCE_CLASSES = frozenset({
    EVIDENCE_ONLY,
    TEST_ONLY,
})


# --------------------------------------------------------------------------------------------------
# TWR124 — CAPABILITY VOCABULARY
# --------------------------------------------------------------------------------------------------

REGISTERED = "REGISTERED"
CONFIGURED = "CONFIGURED"
PUBLISHED = "PUBLISHED"
ENTITLED = "ENTITLED"
AUTHORIZED = "AUTHORIZED"
AVAILABLE = "AVAILABLE"
ENABLED = "ENABLED"
LOCKED = "LOCKED"

CAPABILITY_STATES = (
    REGISTERED,
    CONFIGURED,
    PUBLISHED,
    ENTITLED,
    AUTHORIZED,
    AVAILABLE,
    ENABLED,
    LOCKED,
)


class TowerTruthContractError(ValueError):
    """Raised when code attempts to manufacture or misuse Tower product truth."""


@dataclass(frozen=True)
class TowerTruthEnvelope:
    value: Any
    source_id: str
    source_class: str
    verification_state: str
    observed_at_utc: str | None
    fresh_until_utc: str | None
    reason: str | None
    product_visible: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_timestamp(value: str | None) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    candidate = text

    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise TowerTruthContractError(
            f"Invalid ISO timestamp: {text}"
        ) from exc

    if parsed.tzinfo is None:
        raise TowerTruthContractError(
            "Tower truth timestamps must be timezone-aware."
        )

    return parsed.astimezone(timezone.utc).isoformat()


def validate_truth_envelope(
    envelope: TowerTruthEnvelope,
) -> TowerTruthEnvelope:

    if not isinstance(envelope, TowerTruthEnvelope):
        raise TowerTruthContractError(
            "Tower truth envelope type required."
        )

    if envelope.source_class not in SOURCE_CLASSES:
        raise TowerTruthContractError(
            f"Unknown Tower source class: {envelope.source_class}"
        )

    if envelope.verification_state not in VERIFICATION_STATES:
        raise TowerTruthContractError(
            "Unknown Tower verification state: "
            f"{envelope.verification_state}"
        )

    if not str(envelope.source_id or "").strip():
        raise TowerTruthContractError(
            "Tower truth requires a non-empty source_id."
        )

    if (
        envelope.product_visible
        and envelope.source_class
        in PRODUCT_FORBIDDEN_SOURCE_CLASSES
    ):
        raise TowerTruthContractError(
            "TEST_ONLY and EVIDENCE_ONLY state cannot "
            "be presented as primary Tower product truth."
        )

    if (
        envelope.verification_state == VERIFIED
        and envelope.value is None
    ):
        raise TowerTruthContractError(
            "VERIFIED Tower truth cannot contain a missing value."
        )

    if (
        envelope.verification_state
        in {UNKNOWN, UNAVAILABLE, NOT_CONFIGURED}
        and envelope.value is not None
    ):
        raise TowerTruthContractError(
            f"{envelope.verification_state} Tower truth "
            "must not carry a plausible value."
        )

    _normalize_timestamp(
        envelope.observed_at_utc
    )

    _normalize_timestamp(
        envelope.fresh_until_utc
    )

    return envelope


def truth_envelope(
    *,
    value: Any,
    source_id: str,
    source_class: str,
    verification_state: str,
    observed_at_utc: str | None = None,
    fresh_until_utc: str | None = None,
    reason: str | None = None,
    product_visible: bool = True,
) -> TowerTruthEnvelope:

    envelope = TowerTruthEnvelope(
        value=value,
        source_id=str(source_id or "").strip(),
        source_class=str(source_class or "").strip(),
        verification_state=str(
            verification_state or ""
        ).strip(),
        observed_at_utc=_normalize_timestamp(
            observed_at_utc
        ),
        fresh_until_utc=_normalize_timestamp(
            fresh_until_utc
        ),
        reason=(
            str(reason).strip()
            if reason is not None
            else None
        ),
        product_visible=bool(product_visible),
    )

    return validate_truth_envelope(
        envelope
    )


def verified_truth(
    *,
    value: Any,
    source_id: str,
    source_class: str = AUTHORITATIVE,
    observed_at_utc: str | None = None,
    fresh_until_utc: str | None = None,
    reason: str | None = None,
    product_visible: bool = True,
) -> TowerTruthEnvelope:

    return truth_envelope(
        value=value,
        source_id=source_id,
        source_class=source_class,
        verification_state=VERIFIED,
        observed_at_utc=observed_at_utc,
        fresh_until_utc=fresh_until_utc,
        reason=reason,
        product_visible=product_visible,
    )


def unknown_truth(
    *,
    source_id: str,
    source_class: str = UNAVAILABLE_SOURCE,
    reason: str = "authoritative_state_not_available",
    product_visible: bool = True,
) -> TowerTruthEnvelope:

    return truth_envelope(
        value=None,
        source_id=source_id,
        source_class=source_class,
        verification_state=UNKNOWN,
        reason=reason,
        product_visible=product_visible,
    )


def unavailable_truth(
    *,
    source_id: str,
    reason: str = "authoritative_provider_unavailable",
    product_visible: bool = True,
) -> TowerTruthEnvelope:

    return truth_envelope(
        value=None,
        source_id=source_id,
        source_class=UNAVAILABLE_SOURCE,
        verification_state=UNAVAILABLE,
        reason=reason,
        product_visible=product_visible,
    )


def not_configured_truth(
    *,
    source_id: str,
    reason: str = "authoritative_provider_not_configured",
    product_visible: bool = True,
) -> TowerTruthEnvelope:

    return truth_envelope(
        value=None,
        source_id=source_id,
        source_class=UNAVAILABLE_SOURCE,
        verification_state=NOT_CONFIGURED,
        reason=reason,
        product_visible=product_visible,
    )


def is_truth_fresh(
    envelope: TowerTruthEnvelope,
    *,
    now_utc: str | None = None,
) -> bool:

    validate_truth_envelope(
        envelope
    )

    if envelope.verification_state != VERIFIED:
        return False

    if envelope.fresh_until_utc is None:
        return True

    now = (
        _normalize_timestamp(now_utc)
        if now_utc is not None
        else datetime.now(timezone.utc).isoformat()
    )

    now_dt = datetime.fromisoformat(now)
    fresh_dt = datetime.fromisoformat(
        envelope.fresh_until_utc
    )

    return now_dt <= fresh_dt


def product_display_projection(
    envelope: TowerTruthEnvelope,
    *,
    now_utc: str | None = None,
) -> dict[str, Any]:

    validate_truth_envelope(
        envelope
    )

    verified_and_fresh = (
        envelope.verification_state == VERIFIED
        and is_truth_fresh(
            envelope,
            now_utc=now_utc,
        )
    )

    state = envelope.verification_state

    if (
        envelope.verification_state == VERIFIED
        and not verified_and_fresh
    ):
        state = STALE

    return {
        "display_value": (
            envelope.value
            if verified_and_fresh
            else None
        ),
        "display_state": state,
        "source_id": envelope.source_id,
        "source_class": envelope.source_class,
        "reason": envelope.reason,
    }


def require_verified_value(
    envelope: TowerTruthEnvelope,
    *,
    now_utc: str | None = None,
) -> Any:

    projection = product_display_projection(
        envelope,
        now_utc=now_utc,
    )

    if projection["display_state"] != VERIFIED:
        raise TowerTruthContractError(
            "Tower product code requested a value "
            "that is not verified and fresh."
        )

    return envelope.value


# --------------------------------------------------------------------------------------------------
# TWR123 — NO PLAUSIBLE DEFAULTS
# --------------------------------------------------------------------------------------------------

def read_mapping_truth(
    mapping: Mapping[str, Any] | None,
    key: str,
    *,
    source_id: str,
    source_class: str = AUTHORITATIVE,
    observed_at_utc: str | None = None,
    fresh_until_utc: str | None = None,
) -> TowerTruthEnvelope:
    """
    Read a value without manufacturing a default.

    Missing mapping, missing key, or None value becomes explicit UNKNOWN.
    It NEVER becomes 0, False, Healthy, Ready, Clean, Available, or an
    arbitrary empty collection.
    """

    if mapping is None:
        return unknown_truth(
            source_id=source_id,
            reason="source_mapping_missing",
        )

    if key not in mapping:
        return unknown_truth(
            source_id=source_id,
            reason=f"source_key_missing:{key}",
        )

    value = mapping[key]

    if value is None:
        return unknown_truth(
            source_id=source_id,
            reason=f"source_value_missing:{key}",
        )

    return verified_truth(
        value=value,
        source_id=source_id,
        source_class=source_class,
        observed_at_utc=observed_at_utc,
        fresh_until_utc=fresh_until_utc,
        reason=f"source_key_verified:{key}",
    )


def count_truth(
    items: Any,
    *,
    source_id: str,
    source_class: str = AUTHORITATIVE,
    observed_at_utc: str | None = None,
    fresh_until_utc: str | None = None,
) -> TowerTruthEnvelope:
    """
    Count only when the collection itself is actually present.

    None does not mean zero.
    """

    if items is None:
        return unknown_truth(
            source_id=source_id,
            reason="collection_missing_count_unknown",
        )

    try:
        count = len(items)
    except TypeError as exc:
        raise TowerTruthContractError(
            "count_truth requires a sized collection."
        ) from exc

    return verified_truth(
        value=count,
        source_id=source_id,
        source_class=source_class,
        observed_at_utc=observed_at_utc,
        fresh_until_utc=fresh_until_utc,
        reason="collection_present_count_verified",
    )


def capability_truth_contract() -> dict[str, tuple[str, ...]]:
    """
    Explicitly document that Tower capability words are separate dimensions.

    REGISTERED does not imply CONFIGURED.
    CONFIGURED does not imply PUBLISHED.
    PUBLISHED does not imply ENTITLED.
    ENTITLED does not imply AUTHORIZED.
    AUTHORIZED does not imply AVAILABLE.
    AVAILABLE does not imply ENABLED.
    ENABLED does not imply not LOCKED.
    """

    return {
        "ordered_dimensions": CAPABILITY_STATES,

        "non_implications": (
            "REGISTERED_DOES_NOT_IMPLY_CONFIGURED",
            "CONFIGURED_DOES_NOT_IMPLY_PUBLISHED",
            "PUBLISHED_DOES_NOT_IMPLY_ENTITLED",
            "ENTITLED_DOES_NOT_IMPLY_AUTHORIZED",
            "AUTHORIZED_DOES_NOT_IMPLY_AVAILABLE",
            "AVAILABLE_DOES_NOT_IMPLY_ENABLED",
            "ENABLED_DOES_NOT_IMPLY_UNLOCKED",
        ),
    }
