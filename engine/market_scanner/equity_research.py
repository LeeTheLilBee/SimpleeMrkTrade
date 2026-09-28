"""OBDATA012–015: provider-neutral read-only equity/ETF research scanner.

The caller must first establish and validate a provider entitlement on the
server. This module never fetches data, creates a trading signal, trades,
supplies an options chain, or assumes that a one-venue quote is consolidated.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping
import re

VERSION = "OBDATA012_015_SOURCE_BOUND_PRICE_SCANNER_V1"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,9}$")
APPROVED_SCOPES = {"owner_private_research", "invitee_display_approved"}
MAX_SYMBOLS = 30
MAX_BARS = 60


def _time(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing provider-supplied timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Malformed provider timestamp") from exc
    if dt.utcoffset() is None:
        raise ValueError("Market observation must include timezone")
    return dt.astimezone(timezone.utc)


def _decimal(value: object, *, positive: bool = True) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("Missing numeric market observation")
    try:
        val = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Malformed numeric observation") from exc
    if not val.is_finite() or (positive and val <= 0) or (not positive and val < 0):
        raise ValueError("Invalid market observation value")
    return val


def _number(value: Decimal) -> float:
    return float(round(value, 6))


@dataclass(frozen=True)
class Entitlement:
    """Construct ONLY from server-side verified provider agreement/config."""
    provider: str
    product: str
    venue: str
    license_verified: bool
    scope: str
    permits_derived_research: bool
    permits_client_display: bool
    is_consolidated: bool = False

    def approved(self) -> bool:
        return bool(self.provider and self.product and self.venue
                    and self.license_verified and self.permits_derived_research
                    and self.scope in APPROVED_SCOPES)


def _empty(reason: str, status: str = "HOLD", *, source: str = "") -> dict:
    return {
        "schema": VERSION, "status": status, "reason": reason, "source": source,
        "market_quotes": [], "research_observations": [], "options_chains": [],
        "broker_positions": [], "manual_live_queue": [], "scan_completed": False,
        "market_data_current": False, "broker_api": False,
        "trading_authorized": False, "options_execution_authorized": False,
        "data_is_consolidated": False,
    }


def scan_equities(*, observations: Iterable[Mapping], daily_bars: Mapping,
                  entitlement: Entitlement | None, now: datetime,
                  user_scope: str = "owner_private_research",
                  max_quote_age_seconds: int = 180) -> dict:
    """Analyze supplied vendor observations; never fetch or upgrade data rights.

    Each incoming observation:
      symbol, trade_price, trade_size(optional), trade_as_of,
      venue, provider, product; and optional vendor-supplied previous_close.
    daily_bars[symbol]: up to 60 provider daily bars {day, close, volume}.
    This is only an observational screen, NOT an investment recommendation.
    """
    if not isinstance(now, datetime) or now.utcoffset() is None:
        raise ValueError("Explicit timezone-aware evaluation clock required")
    if (not isinstance(entitlement, Entitlement) or not entitlement.approved()
            or user_scope not in APPROVED_SCOPES
            or (user_scope != "owner_private_research"
                and (entitlement.scope != "invitee_display_approved"
                     or not entitlement.permits_client_display))):
        return _empty("Verified provider entitlement/scope absent", "LICENSE_HOLD")
    if not isinstance(max_quote_age_seconds, int) or not 15 <= max_quote_age_seconds <= 900:
        raise ValueError("Quote staleness policy outside approved range")
    rows = list(observations)
    if not rows or len(rows) > MAX_SYMBOLS:
        return _empty("No observations or per-scan free-tier symbol budget exceeded",
                      "SOURCE_UNAVAILABLE", source=entitlement.provider)
    if not isinstance(daily_bars, Mapping):
        return _empty("Historical bars missing", "SOURCE_UNAVAILABLE", source=entitlement.provider)
    seen: set[str] = set()
    output: list[dict] = []
    rejected: list[dict] = []
    clock = now.astimezone(timezone.utc)
    for raw in rows:
        sym = str(raw.get("symbol", "")).strip().upper() if isinstance(raw, Mapping) else ""
        if not SYMBOL.fullmatch(sym) or sym in seen:
            rejected.append({"symbol": sym[:12], "reason": "invalid_or_duplicate_symbol"})
            continue
        seen.add(sym)
        if (str(raw.get("provider", "")) != entitlement.provider
            or str(raw.get("product", "")) != entitlement.product
            or str(raw.get("venue", "")) != entitlement.venue):
            rejected.append({"symbol": sym, "reason": "source_entitlement_mismatch"})
            continue
        try:
            price = _decimal(raw.get("trade_price"))
            traded = _time(raw.get("trade_as_of"))
            age_seconds = (clock - traded).total_seconds()
            if age_seconds < -30:
                raise ValueError("future_vendor_timestamp")
            if age_seconds > max_quote_age_seconds:
                rejected.append({"symbol": sym, "reason": "stale_quote",
                                 "as_of": traded.isoformat(), "age_seconds": round(age_seconds)})
                continue
            bars = daily_bars.get(sym)
            if not isinstance(bars, list) or len(bars) < 20 or len(bars) > MAX_BARS:
                raise ValueError("insufficient_authorized_daily_history")
            prepared: list[tuple[str, Decimal, Decimal]] = []
            for bar in bars:
                if not isinstance(bar, Mapping):
                    raise ValueError("malformed_daily_bar")
                day = str(bar.get("day", ""))
                date.fromisoformat(day)
                prepared.append((day, _decimal(bar.get("close")), _decimal(bar.get("volume"), positive=False)))
            if len({b[0] for b in prepared}) != len(prepared):
                raise ValueError("duplicate_history_date")
            prepared.sort(key=lambda x: x[0])
            if prepared[-1][0] > clock.date().isoformat():
                raise ValueError("future_history_date")
            # Historical close averages are not official market breadth or execution signals.
            mean5 = sum((b[1] for b in prepared[-5:]), Decimal(0)) / Decimal(5)
            mean20 = sum((b[1] for b in prepared[-20:]), Decimal(0)) / Decimal(20)
            previous = prepared[-1][1]
            change = (price - previous) / previous * 100
            last_volume = prepared[-1][2]
            mean_volume = sum((b[2] for b in prepared[-20:]), Decimal(0)) / Decimal(20)
            state = "above_both_averages" if price > mean5 and price > mean20 else (
                "below_both_averages" if price < mean5 and price < mean20 else "mixed")
            output.append({
                "symbol": sym, "source": entitlement.provider,
                "source_product": entitlement.product, "venue": entitlement.venue,
                "coverage": "consolidated" if entitlement.is_consolidated else "single_venue_or_limited",
                "quote_as_of": traded.isoformat(), "quote_age_seconds": max(0, round(age_seconds)),
                "trade_price": _number(price),
                "historical_last_day": prepared[-1][0],
                "historical_days": len(prepared),
                "last_historical_close": _number(previous),
                "change_from_historical_close_pct": _number(change),
                "avg_last_5_closes": _number(mean5),
                "avg_last_20_closes": _number(mean20),
                "last_historical_volume": _number(last_volume),
                "avg_last_20_historical_volumes": _number(mean_volume),
                "observation": state,
                "research_only": True, "current_price_research_eligible": True,
                "actual_broker_fill": False, "trading_signal": False,
                "options_quote": False,
            })
        except (ValueError, TypeError, OverflowError, InvalidOperation) as exc:
            rejected.append({"symbol": sym, "reason": str(exc)[:100]})
    return {
        "schema": VERSION, "status": "SOURCE_OBSERVED" if output else "SOURCE_UNAVAILABLE",
        "reason": "Observational source scan, not a recommendation" if output else "No valid, current source observations",
        "source": entitlement.provider,
        "source_product": entitlement.product,
        "coverage": "consolidated" if entitlement.is_consolidated else "single_venue_or_limited",
        "scope": user_scope,
        "market_quotes": output if entitlement.permits_client_display else [],
        "research_observations": output,
        "rejections": rejected, "options_chains": [], "broker_positions": [],
        "manual_live_queue": [], "scan_completed": True,
        "market_data_current": bool(output),
        "broker_api": False, "trading_authorized": False,
        "options_execution_authorized": False,
        "data_is_consolidated": entitlement.is_consolidated,
        "last_known_cannot_become_current": True,
    }
