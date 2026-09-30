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
TWELVE_WS_ENDPOINT = "wss://ws.twelvedata.com/v1/quotes/price"
FINAZON_WS_ENDPOINT = "wss://ws.finazon.io/v1"


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
    security_name: str | None = None
    exchange: str | None = None
    mic_code: str | None = None
    currency: str | None = None
    last_trade_size: int | None = None
    month_open: float | None = None
    month_high: float | None = None
    month_low: float | None = None
    month_close: float | None = None
    month_volume: int | None = None
    fifty_two_week_change: float | None = None
    fifty_two_week_change_percent: float | None = None
    rolling_1d_change: float | None = None
    rolling_7d_change: float | None = None
    rolling_change: float | None = None

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
        for name in (
            "open", "high", "low", "previous_close", "average_volume",
            "fifty_two_week_high", "fifty_two_week_low",
            "month_open", "month_high", "month_low", "month_close",
        ):
            value = getattr(self, name)
            if value is not None:
                _num(value, name)
        for name in ("volume", "last_trade_size", "month_volume"):
            value = getattr(self, name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"{name} must be nonnegative integer")
        for name in (
            "daily_change_percent", "weekly_change_percent", "monthly_change_percent",
            "fifty_two_week_change", "fifty_two_week_change_percent",
            "rolling_1d_change", "rolling_7d_change", "rolling_change",
        ):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)
                                      or not isfinite(value)):
                raise ValueError(f"{name} must be finite numeric")
        if self.market_open is not None and type(self.market_open) is not bool:
            raise ValueError("market_open must be boolean when supplied")
        for name in ("security_name", "exchange", "mic_code", "currency"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 180):
                raise ValueError(f"{name} must be bounded text when supplied")

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
            "security_name": self.security_name,
            "exchange": self.exchange,
            "mic_code": self.mic_code,
            "currency": self.currency,
            "last_trade_size": self.last_trade_size,
            "month_open": self.month_open,
            "month_high": self.month_high,
            "month_low": self.month_low,
            "month_close": self.month_close,
            "month_volume": self.month_volume,
            "fifty_two_week_change": self.fifty_two_week_change,
            "fifty_two_week_change_percent": self.fifty_two_week_change_percent,
            "rolling_1d_change": self.rolling_1d_change,
            "rolling_7d_change": self.rolling_7d_change,
            "rolling_change": self.rolling_change,
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
        security_name=str(document["name"])[:180] if document.get("name") else None,
        exchange=str(document["exchange"])[:80] if document.get("exchange") else None,
        mic_code=str(document["mic_code"])[:20] if document.get("mic_code") else None,
        currency=str(document["currency"])[:20] if document.get("currency") else None,
        rolling_1d_change=float(document["rolling_1d_change"])
            if document.get("rolling_1d_change") not in (None, "") else None,
        rolling_7d_change=float(document["rolling_7d_change"])
            if document.get("rolling_7d_change") not in (None, "") else None,
        rolling_change=float(document["rolling_change"])
            if document.get("rolling_change") not in (None, "") else None,
    )


def normalize_finazon_snapshot(document: Mapping, *, symbol: str,
                               received_at: datetime) -> MarketContextRecord:
    if not isinstance(document, Mapping):
        raise ValueError("Finazon response must be an object")
    symbol = clean_symbol(symbol)
    last_trade = document.get("lt")
    day = document.get("1d")
    previous = document.get("p1d")
    month = document.get("1m")
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
        last_trade_size=_count(last_trade.get("s"), "last_trade_size")
            if last_trade.get("s") is not None else None,
        month_open=_num(month.get("o"), "month_open")
            if isinstance(month, Mapping) and month.get("o") is not None else None,
        month_high=_num(month.get("h"), "month_high")
            if isinstance(month, Mapping) and month.get("h") is not None else None,
        month_low=_num(month.get("l"), "month_low")
            if isinstance(month, Mapping) and month.get("l") is not None else None,
        month_close=_num(month.get("c"), "month_close")
            if isinstance(month, Mapping) and month.get("c") is not None else None,
        month_volume=_count(month.get("v"), "month_volume")
            if isinstance(month, Mapping) and month.get("v") is not None else None,
        fifty_two_week_change=float(fifty["ch"]) if fifty.get("ch") is not None else None,
        fifty_two_week_change_percent=float(fifty["chp"]) if fifty.get("chp") is not None else None,
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


def twelve_ws_subscribe(symbols: Iterable[str]) -> dict:
    """Build Twelve Data subscribe message; caller must pass entitlement-filtered symbols."""
    clean = tuple(dict.fromkeys(clean_symbol(x) for x in symbols))
    if not clean or len(clean) > TWELVE_WS_BUDGET:
        raise ValueError("Twelve Data trial websocket symbol count outside reviewed limit")
    return {"action": "subscribe", "params": {"symbols": ",".join(clean)}}


def twelve_ws_heartbeat() -> dict:
    return {"action": "heartbeat"}


def finazon_ws_subscribe(symbols: Iterable[str], *, request_id: int | str) -> dict:
    """Build exact free-trial US Equities Basic bars subscription."""
    clean = tuple(dict.fromkeys(clean_symbol(x) for x in symbols))
    if not clean or len(clean) > FINAZON_FREE_WS_BUDGET:
        raise ValueError("Finazon free websocket symbol count outside reviewed limit")
    if any(x not in FINAZON_FREE_TRIAL_SYMBOLS for x in clean):
        raise ValueError("Finazon websocket symbol outside free-trial universe")
    if not isinstance(request_id, (int, str)) or isinstance(request_id, bool) or str(request_id) == "":
        raise ValueError("bounded request id required")
    return {
        "event": "subscribe",
        "dataset": "us_stocks_essential",
        "tickers": list(clean),
        "channel": "bars",
        "frequency": "1s",
        "aggregation": "1m",
        "request_id": request_id,
    }


def finazon_ws_heartbeat(*, request_id: int | str) -> dict:
    if not isinstance(request_id, (int, str)) or isinstance(request_id, bool) or str(request_id) == "":
        raise ValueError("bounded request id required")
    return {"event": "heartbeat", "request_id": request_id}


def record_digest(records: Iterable[MarketContextRecord]) -> str:
    stable = [r.internal_projection() for r in sorted(records, key=lambda x: (x.source_id, x.symbol))]
    for item in stable:
        item.pop("received_at", None)
    return sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
