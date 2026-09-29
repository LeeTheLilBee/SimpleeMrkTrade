"""OBSCAN001-025: normalized observations, explicit data rights and fail-closed gates.

Source facts do not grant trading, display, redistribution or account permissions.
No network calls, API tokens, broker or order transport live in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
import re

VERSION = "OBSCAN001-025"
SYMBOL = re.compile(r"^[A-Z0-9][A-Z0-9./^-]{0,13}$")
OCC = re.compile(r"^[A-Z0-9 .]{1,6}\d{6}[CP]\d{8}$")


def _aware(value: datetime, field: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware datetime")


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonblank")
    return value.strip()


def _positive(value: float, name: str, *, zero: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be finite numeric")
    if value < 0 if zero else value <= 0:
        raise ValueError(f"{name} outside valid range")


def clean_symbol(value: str) -> str:
    symbol = _text(value, "symbol").upper()
    if not SYMBOL.fullmatch(symbol):
        raise ValueError("unrecognized symbol syntax; do not silently remap symbols")
    return symbol


class Gate(str, Enum):
    CURRENT_RESEARCH = "CURRENT_RESEARCH"
    SOURCE_HOLD = "SOURCE_HOLD"
    RIGHTS_HOLD = "RIGHTS_HOLD"
    CONTEXT_HOLD = "CONTEXT_HOLD"
    TEMPORAL_HOLD = "TEMPORAL_HOLD"
    INVALID_HOLD = "INVALID_HOLD"


@dataclass(frozen=True)
class SourceRights:
    """Set only after a documented entitlement/terms review for the actual use.

    A free directory is NOT a free real-time data license. Default denies everything.
    """
    source_id: str
    upstream_family: str
    permission_reference: str = ""
    verified_at: datetime | None = None
    internal_research: bool = False
    automated_non_display: bool = False
    owner_display: bool = False
    invitee_display: bool = False
    redistribution: bool = False
    real_time_entitled: bool = False
    entitled_instruments: frozenset[str] = frozenset()  # independent equity/option/event grants
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        _text(self.source_id, "source_id")
        _text(self.upstream_family, "upstream_family")
        if self.verified_at is not None:
            _aware(self.verified_at, "verified_at")
        if self.expires_at is not None:
            _aware(self.expires_at, "expires_at")
            if self.verified_at is None or self.expires_at <= self.verified_at:
                raise ValueError("entitlement expiry must follow verified time")
        if not self.entitled_instruments.issubset({"equity", "option", "event"}):
            raise ValueError("unrecognized instrument entitlement")

    def reviewed_for_scan(self) -> bool:
        return bool(self.permission_reference.strip() and self.verified_at is not None
                    and self.internal_research and self.automated_non_display)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source_id: str
    upstream_family: str
    symbol: str
    observed_at: datetime
    received_at: datetime
    provenance_reference: str
    feed_label: str  # "realtime", "delayed", "historical", "unknown"
    instrument: str  # "equity", "option", or "event"

    def __post_init__(self) -> None:
        for name in ("observation_id", "source_id", "upstream_family", "provenance_reference"):
            _text(getattr(self, name), name)
        clean_symbol(self.symbol)
        _aware(self.observed_at, "observed_at")
        _aware(self.received_at, "received_at")
        if self.feed_label not in {"realtime", "delayed", "historical", "unknown"}:
            raise ValueError("unrecognized feed label")
        if self.instrument not in {"equity", "option", "event"}:
            raise ValueError("unrecognized instrument type")


@dataclass(frozen=True)
class EquityQuote:
    evidence: Observation
    last: float
    bid: float
    ask: float
    previous_close: float | None = None
    volume: int | None = None
    average_volume: float | None = None

    def __post_init__(self) -> None:
        if self.evidence.instrument != "equity":
            raise ValueError("equity quote requires equity instrument")
        for name in ("last", "bid", "ask"):
            _positive(getattr(self, name), name)
        if self.bid > self.ask:
            raise ValueError("crossed equity quote")
        if self.previous_close is not None:
            _positive(self.previous_close, "previous_close")
        if self.volume is not None:
            _positive(self.volume, "volume", zero=True)
            if not isinstance(self.volume, int):
                raise ValueError("volume must be an integer")
        if self.average_volume is not None:
            _positive(self.average_volume, "average_volume")


@dataclass(frozen=True)
class OptionQuote:
    evidence: Observation
    underlying: str
    occ_symbol: str
    bid: float
    ask: float
    strike: float
    expiry: str
    right: str  # call or put; cannot infer from symbol string alone
    open_interest: int | None = None
    volume: int | None = None

    def __post_init__(self) -> None:
        if self.evidence.instrument != "option" or self.evidence.symbol != clean_symbol(self.underlying):
            raise ValueError("option evidence and underlying must agree")
        if not OCC.fullmatch(self.occ_symbol):
            raise ValueError("OCC option series identity required")
        if self.right not in {"call", "put"}:
            raise ValueError("option right required")
        embedded_right = self.occ_symbol[-9]
        if embedded_right != ("C" if self.right == "call" else "P"):
            raise ValueError("option right conflicts with series identity")
        try:
            parsed = datetime.strptime(self.expiry, "%Y-%m-%d")
            embedded_expiry = datetime.strptime(self.occ_symbol[-15:-9], "%y%m%d")
        except ValueError as exc:
            raise ValueError("valid option expiry required") from exc
        if parsed.date() != embedded_expiry.date():
            raise ValueError("expiry conflicts with OCC identity")
        if abs(int(self.occ_symbol[-8:]) / 1000.0 - self.strike) > 0.000001:
            raise ValueError("strike conflicts with OCC identity")
        _positive(self.bid, "option bid", zero=True)
        _positive(self.ask, "option ask", zero=True)
        _positive(self.strike, "strike")
        if self.bid > self.ask or self.ask == 0:
            raise ValueError("crossed or empty option market")
        for name in ("volume", "open_interest"):
            x = getattr(self, name)
            if x is not None:
                _positive(x, name, zero=True)
                if not isinstance(x, int):
                    raise ValueError(f"{name} must be integer")


@dataclass(frozen=True)
class DiscoveryEvent:
    evidence: Observation
    category: str
    headline: str
    reference_url: str
    issuer_cik: str = ""

    def __post_init__(self) -> None:
        if self.evidence.instrument != "event":
            raise ValueError("event instrument required")
        if self.category not in {"filing", "company_release", "news", "macro", "halt", "watchlist"}:
            raise ValueError("unrecognized discovery category")
        _text(self.headline, "headline")
        _text(self.reference_url, "reference_url")


@dataclass(frozen=True)
class ScanContext:
    now: datetime
    market_session: str = "UNKNOWN"
    verified_market_time: bool = False
    quote_max_age_seconds: int = 5
    event_max_age_seconds: int = 86400
    clock_skew_seconds: int = 2

    def __post_init__(self) -> None:
        _aware(self.now, "now")
        if self.quote_max_age_seconds <= 0 or self.event_max_age_seconds <= 0:
            raise ValueError("freshness windows must be positive")
        if self.clock_skew_seconds < 0:
            raise ValueError("clock skew must be nonnegative")


@dataclass(frozen=True)
class GateResult:
    gate: Gate
    reason: str
    source_id: str
    observation_id: str
    observed_at: str
    age_seconds: float
    display_to_owner: bool = False
    display_to_invitees: bool = False
    execution_authority: bool = False


def assess(evidence: Observation, rights: SourceRights | None, context: ScanContext,
           *, quote: bool = True) -> GateResult:
    age = (context.now.astimezone(timezone.utc)
           - evidence.observed_at.astimezone(timezone.utc)).total_seconds()
    result = lambda gate, why, owner=False, invitees=False: GateResult(
        gate, why, evidence.source_id, evidence.observation_id,
        evidence.observed_at.isoformat(), age, owner, invitees, False)
    if rights is None or rights.source_id != evidence.source_id or rights.upstream_family != evidence.upstream_family:
        return result(Gate.SOURCE_HOLD, "Missing or mismatched source-rights record.")
    if not rights.reviewed_for_scan():
        return result(Gate.RIGHTS_HOLD, "Automated research entitlement was not verified.")
    if rights.verified_at is not None and rights.verified_at > context.now:
        return result(Gate.RIGHTS_HOLD, "Future-dated entitlement evidence cannot authorize a quote.")
    if rights.expires_at is not None and context.now >= rights.expires_at:
        return result(Gate.RIGHTS_HOLD, "Source entitlement expired.")
    if evidence.instrument not in rights.entitled_instruments:
        return result(Gate.RIGHTS_HOLD, "Instrument-specific data entitlement is not granted.")
    if quote and (not rights.real_time_entitled or evidence.feed_label != "realtime"):
        return result(Gate.RIGHTS_HOLD, "A current-quote entitlement and real-time feed label are both required.")
    if (evidence.received_at - evidence.observed_at).total_seconds() < -context.clock_skew_seconds:
        return result(Gate.TEMPORAL_HOLD, "Observation timestamp exceeds receipt timestamp.")
    if age < -context.clock_skew_seconds:
        return result(Gate.TEMPORAL_HOLD, "Observation timestamp is in the future.")
    limit = context.quote_max_age_seconds if quote else context.event_max_age_seconds
    if age > limit or (context.now - evidence.received_at).total_seconds() > limit:
        return result(Gate.TEMPORAL_HOLD, "Observation or receipt has aged beyond the explicit freshness budget.")
    if quote and (not context.verified_market_time or context.market_session != "REGULAR"):
        return result(Gate.CONTEXT_HOLD, "No verified regular-market time context; do not assert a current session.")
    return result(Gate.CURRENT_RESEARCH, "Eligible for source-bound research only.",
                  owner=rights.owner_display, invitees=rights.invitee_display and rights.redistribution)


BOUNDARIES = {
    "provider_fetch_enabled": False,
    "market_data_entitlement_inferred": False,
    "broker_order_submission": False,
    "manual_live_unlock": False,
    "execution_authority": False,
    "capital_movement": False,
    "synthetic_quote_fallback": False,
}
