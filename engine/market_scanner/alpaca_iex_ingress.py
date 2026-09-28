"""OBDATA017: Alpaca Basic IEX pure ingress mapper; NO network, key, broker or orders.

Only a server-authorized and authenticated source session may invoke it. These
are IEX observations (one venue), not consolidated national best bid/offer.
Neither the free Basic tier nor this mapper authorizes invited-user redisplay.
"""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Mapping
import re

PRODUCT = "alpaca_basic_iex_stocks"
PROVIDER = "Alpaca Markets"
VENUE = "IEX"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,9}$")


def _verified(transport_verified: bool, feed: str) -> None:
    if transport_verified is not True or feed != "iex":
        raise ValueError("Authenticated server-side IEX feed verification required")


def normalize_trade(raw: Mapping, *, transport_verified: bool, feed: str) -> dict:
    """Parse documented Alpaca trade fields (T=t,S,x,p,s,t)."""
    _verified(transport_verified, feed)
    if not isinstance(raw, Mapping) or raw.get("T") != "t":
        raise ValueError("Expected vendor-supplied trade event")
    symbol = str(raw.get("S", "")).upper()
    if not SYMBOL.fullmatch(symbol):
        raise ValueError("Invalid provider symbol")
    try:
        price = Decimal(str(raw.get("p")))
        size = Decimal(str(raw.get("s")))
        if not price.is_finite() or price <= 0 or not size.is_finite() or size <= 0:
            raise ValueError("Invalid trade")
        stamp = str(raw.get("t", ""))
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.utcoffset() is None:
            raise ValueError("Source timestamp missing timezone")
        exchange = str(raw.get("x", ""))
        if not re.fullmatch(r"[A-Za-z0-9]{1,8}", exchange):
            raise ValueError("Missing vendor trade exchange code")
    except (TypeError, InvalidOperation) as exc:
        raise ValueError("Malformed vendor trade") from exc
    return {
        "symbol": symbol,
        "trade_price": str(price),
        "trade_size": str(size),
        "trade_as_of": stamp,
        "trade_exchange_code": exchange,
        "provider": PROVIDER, "product": PRODUCT, "venue": VENUE,
        "source_is_consolidated": False,
        "eligible_as_options_quote": False,
        "eligible_as_broker_execution": False,
    }


def normalize_completed_daily_bars(
    rows: list[Mapping], *, transport_verified: bool, feed: str,
    vendor_dataset_completed: bool,
) -> list[dict]:
    """Caller must first verify these are finalized historical daily bars."""
    _verified(transport_verified, feed)
    if vendor_dataset_completed is not True:
        raise ValueError("Partial intraday daily bars cannot be a completed historical baseline")
    if not isinstance(rows, list) or not 20 <= len(rows) <= 60:
        raise ValueError("Need 20–60 authorized completed daily observations")
    parsed = []
    for entry in rows:
        if not isinstance(entry, Mapping):
            raise ValueError("Malformed completed bar")
        try:
            stamp = datetime.fromisoformat(str(entry.get("t", "")).replace("Z", "+00:00"))
            if stamp.utcoffset() is None:
                raise ValueError("Unattributed bar timestamp")
            close = Decimal(str(entry.get("c")))
            volume = Decimal(str(entry.get("v")))
            if not close.is_finite() or close <= 0 or not volume.is_finite() or volume < 0:
                raise ValueError("Bad historical bar")
        except (TypeError, InvalidOperation) as exc:
            raise ValueError("Malformed vendor daily observation") from exc
        parsed.append({
            "day": stamp.astimezone(timezone.utc).date().isoformat(),
            "close": str(close), "volume": str(volume),
            "provider": PROVIDER, "product": PRODUCT, "venue": VENUE,
            "completed": True,
        })
    return parsed
