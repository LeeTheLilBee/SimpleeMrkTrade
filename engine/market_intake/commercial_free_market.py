"""Commercially usable zero-cost market-context adapters for Observatory.

These records are deliberately NOT execution-grade quotes. The currently reviewed
free sources can provide real-time/near-real-time price, bar, volume and reference
context, but this lane does not invent NBBO bid/ask or OPRA/SIP authority.

Twelve Data Business Basic:
- $0 business tier, internal non-display use.
- real-time US equities/ETFs, 8 API credits/minute, 800/day, 8 trial WS credits.
- owner/browser display remains disabled here.

Finazon US Equities Basic:
- dataset is advertised for commercial use with no market-data agreement required.
- free-forever trial is restricted to AAPL, TSLA and GOOG; one WS symbol.
- runtime still requires a commercial/business account review flag.

No object in this module grants AI use, redistribution, broker execution, candidate
admission, Manual Live or Live Auto.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import isfinite
from typing import Iterable, Mapping

from .contracts import clean_symbol

TWELVE_DATA_ID = "twelve_data"
FINAZON_ID = "finazon"
PROVIDER_IDS = (TWELVE_DATA_ID, FINAZON_ID)
FINAZON_FREE_TRIAL_SYMBOLS = frozenset({"AAPL", "TSLA", "GOOG"})
TWELVE_WS_BUDGET = 8
FINAZON_FREE_WS_BUDGET = 1


def _num(value, name, *, zero=False):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(number) or number < 0 or (not zero and number == 0):
        raise ValueError(f"{name} outside valid range")
    return number


def _count(value, name):
    if value is None:
        return None
    number = _num(value, name, zero=True)
    if number is None or not number.is_integer():
        raise ValueError(f"{name} must be an integer")
    return int(number)


def _unix(value, *, millis=False):
    if isinstance(value, bool):
        raise ValueError("provider timestamp must be numeric")
    try:
        raw = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("provider timestamp must be numeric") from exc
    if not isfinite(raw) or raw <= 0:
        raise ValueError("provider timestamp outside valid range")
    if millis:
        raw /= 1000.0
    return datetime.fromtimestamp(raw, tz=timezone.utc)


@dataclass(frozen=True)
class MarketContextRecord:
    source_id: str
    symbol: str
    observed_at: datetime
    received_at: datetime
    last: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    previous_close: float | None = None
    volume: int | None = None
    average_volume: float | None = None
    daily_change_percent: float | None = None
    weekly_change_percent: float | None = None
    monthly_change_percent: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    market_open: bool | None = None

    def __post_init__(self):
        if self.source_id not in PROVIDER_IDS:
            raise ValueError("unreviewed commercial-free source")
        object.__setattr__(self, "symbol", clean_symbol(self.symbol))
        if any(
            not isinstance(t, datetime) or t.tzinfo is None or t.utcoffset() is None
            for t in (self.observed_at, self.received_at)
        ):
            raise ValueError("timezone-aware observation and receipt required")
        if self.observed_at > self.received_at:
            raise ValueError("provider observation cannot post-date receipt")
        if self.last is None:
            raise ValueError("last is required")
        _num(self.last, "last")
        for name in ("open", "high", "low", "previous_close",
                     "average_volume", "fifty_two_week_high", "fifty_two_week_low"):
            value = getattr(self, name)
            if value is not None:
                _num(value, name)
        if self.volume is not None and (type(self.volume) is not int or self.volume < 0):
            raise ValueError("volume must be nonnegative integer")
        for name in ("daily_change_percent", "weekly_change_percent", "monthly_change_percent"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)
                                      or not isfinite(value)):
                raise ValueError(f"{name} must be finite numeric")
        if self.market_open is not None and type(self.market_open) is not bool:
            raise ValueError("market_open must be boolean when supplied")

    def internal_projection(self) -> dict:
        """Server-side context only; caller must enforce source/use rights."""
        return {
            "source_id": self.source_id,
            "symbol": self.symbol,
            "observed_at": self.observed_at.isoformat(),
            "received_at": self.received_at.isoformat(),
            "last": self.last,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "previous_close": self.previous_close,
            "volume": self.volume,
            "average_volume": self.average_volume,
            "daily_change_percent": self.daily_change_percent,
            "weekly_change_percent": self.weekly_change_percent,
            "monthly_change_percent": self.monthly_change_percent,
            "fifty_two_week_high": self.fifty_two_week_high,
            "fifty_two_week_low": self.fifty_two_week_low,
            "market_open": self.market_open,
            "bid_ask_attached": False,
            "execution_grade_quote": False,
            "candidate_admitted": False,
            "broker_execution_authorized": False,
        }


def normalize_twelve_data_quote(document: Mapping, *, symbol: str,
                                received_at: datetime) -> MarketContextRecord:
    if not isinstance(document, Mapping):
        raise ValueError("Twelve Data response must be an object")
    symbol = clean_symbol(symbol)
    if str(document.get("symbol") or "").upper() != symbol:
        raise ValueError("Twelve Data symbol mismatch")
    status = document.get("status")
    if status is not None and str(status).lower() not in {"ok", "success"}:
        raise ValueError("Twelve Data provider status hold")
    observed_raw = document.get("last_quote_at") or document.get("timestamp")
    observed = _unix(observed_raw)
    fifty = document.get("fifty_two_week") if isinstance(document.get("fifty_two_week"), Mapping) else {}
    last = document.get("close")
    if last is None:
        last = document.get("price")
    return MarketContextRecord(
        source_id=TWELVE_DATA_ID,
        symbol=symbol,
        observed_at=observed,
        received_at=received_at,
        last=_num(last, "last"),
        open=_num(document.get("open"), "open") if document.get("open") is not None else None,
        high=_num(document.get("high"), "high") if document.get("high") is not None else None,
        low=_num(document.get("low"), "low") if document.get("low") is not None else None,
        previous_close=_num(document.get("previous_close"), "previous_close")
            if document.get("previous_close") is not None else None,
        volume=_count(document.get("volume"), "volume") if document.get("volume") is not None else None,
        average_volume=_num(document.get("average_volume"), "average_volume")
            if document.get("average_volume") is not None else None,
        daily_change_percent=float(document["percent_change"])
            if document.get("percent_change") not in (None, "") else None,
        fifty_two_week_high=_num(fifty.get("high"), "fifty_two_week_high")
            if fifty.get("high") is not None else None,
        fifty_two_week_low=_num(fifty.get("low"), "fifty_two_week_low")
            if fifty.get("low") is not None else None,
        market_open=document.get("is_market_open") if type(document.get("is_market_open")) is bool else None,
    )


def normalize_finazon_snapshot(document: Mapping, *, symbol: str,
                               received_at: datetime) -> MarketContextRecord:
    if not isinstance(document, Mapping):
        raise ValueError("Finazon response must be an object")
    symbol = clean_symbol(symbol)
    last_trade = document.get("lt")
    day = document.get("1d")
    previous = document.get("p1d")
    fifty = document.get("52w")
    change = document.get("ch")
    if not all(isinstance(x, Mapping) for x in (last_trade, day, previous, fifty, change)):
        raise ValueError("Finazon snapshot schema hold")
    observed = _unix(last_trade.get("tm"), millis=True)
    return MarketContextRecord(
        source_id=FINAZON_ID,
        symbol=symbol,
        observed_at=observed,
        received_at=received_at,
        last=_num(last_trade.get("p"), "last"),
        open=_num(day.get("o"), "open") if day.get("o") is not None else None,
        high=_num(day.get("h"), "high") if day.get("h") is not None else None,
        low=_num(day.get("l"), "low") if day.get("l") is not None else None,
        previous_close=_num(previous.get("c"), "previous_close")
            if previous.get("c") is not None else None,
        volume=_count(day.get("v"), "volume") if day.get("v") is not None else None,
        average_volume=_num(fifty.get("av"), "average_volume")
            if fifty.get("av") is not None else None,
        daily_change_percent=float(change["dap"]) if change.get("dap") is not None else None,
        weekly_change_percent=float(change["wep"]) if change.get("wep") is not None else None,
        monthly_change_percent=float(change["mop"]) if change.get("mop") is not None else None,
        fifty_two_week_high=_num(fifty.get("h"), "fifty_two_week_high")
            if fifty.get("h") is not None else None,
        fifty_two_week_low=_num(fifty.get("l"), "fifty_two_week_low")
            if fifty.get("l") is not None else None,
    )


def parse_twelve_data_ws_price(document: Mapping, *, received_at: datetime) -> MarketContextRecord:
    """Normalize Twelve Data's price-event subset without inventing OHLC or bid/ask."""
    if not isinstance(document, Mapping) or document.get("event") != "price":
        raise ValueError("Twelve Data websocket price event required")
    symbol = clean_symbol(str(document.get("symbol") or ""))
    return MarketContextRecord(
        source_id=TWELVE_DATA_ID,
        symbol=symbol,
        observed_at=_unix(document.get("timestamp")),
        received_at=received_at,
        last=_num(document.get("price"), "price"),
        volume=_count(document.get("day_volume"), "day_volume")
            if document.get("day_volume") is not None else None,
    )


def parse_finazon_ws_bar(document: Mapping, *, symbol: str,
                         received_at: datetime) -> MarketContextRecord:
    """Normalize a Finazon us_stocks_essential bars event."""
    if not isinstance(document, Mapping):
        raise ValueError("Finazon websocket bar must be an object")
    symbol = clean_symbol(symbol)
    if document.get("d") not in (None, "us_stocks_essential"):
        raise ValueError("Finazon websocket dataset mismatch")
    if document.get("ch") not in (None, "bars"):
        raise ValueError("Finazon websocket channel mismatch")
    if document.get("s") not in (None, symbol):
        raise ValueError("Finazon websocket symbol mismatch")
    return MarketContextRecord(
        source_id=FINAZON_ID,
        symbol=symbol,
        observed_at=_unix(document.get("t")),
        received_at=received_at,
        last=_num(document.get("c"), "close"),
        open=_num(document.get("o"), "open"),
        high=_num(document.get("h"), "high"),
        low=_num(document.get("l"), "low"),
        volume=_count(document.get("v"), "volume") if document.get("v") is not None else None,
    )


def stream_plan(
    symbols: Iterable[str], *, twelve_trial_symbols: Iterable[str] = ()
) -> dict[str, tuple[str, ...]]:
    """Allocate only provider-confirmed free WebSocket symbols.

    Twelve Data Business Basic carries 8 *trial* WS credits, not a blanket grant
    to stream any eight US symbols. Callers must supply the provider-confirmed
    current trial-symbol set; default is therefore no Twelve WS subscriptions.
    Finazon's free-trial symbols are explicitly AAPL/TSLA/GOOG.
    """
    ordered = []
    seen = set()
    for value in symbols:
        symbol = clean_symbol(value)
        if symbol not in seen:
            seen.add(symbol)
            ordered.append(symbol)
    twelve_allowed = {clean_symbol(x) for x in twelve_trial_symbols}
    twelve = tuple(x for x in ordered if x in twelve_allowed)[:TWELVE_WS_BUDGET]
    finazon = tuple(
        x for x in ordered if x in FINAZON_FREE_TRIAL_SYMBOLS
    )[:FINAZON_FREE_WS_BUDGET]
    return {TWELVE_DATA_ID: twelve, FINAZON_ID: finazon}


def record_digest(records: Iterable[MarketContextRecord]) -> str:
    stable = [r.internal_projection() for r in sorted(records, key=lambda x: (x.source_id, x.symbol))]
    for item in stable:
        item.pop("received_at", None)
    return sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
