"""Alpaca personal/owner-development market-data adapter for The Observatory.

Purpose:
- read-only stock market-data normalization for the current Tower owner session
- personal/non-production development entitlement only
- no broker orders, no capital authority, no candidate admission
- no commercial/display/redistribution rights inferred

Credentials are supplied by the existing temporary Tower Key Desk as:
- item.key_id -> APCA-API-KEY-ID
- item.value  -> APCA-API-SECRET-KEY
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
BASE = "https://data.alpaca.markets"
MAX_RESPONSE = 600_000


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _now():
    return datetime.now(timezone.utc)


def _headers(item):
    key_id = getattr(item, "key_id", None)
    secret = getattr(item, "value", None)
    if not isinstance(key_id, str) or not key_id:
        raise ValueError("ALPACA_KEY_ID_MISSING")
    if not isinstance(secret, str) or not secret:
        raise ValueError("ALPACA_SECRET_MISSING")
    return {
        "APCA-API-KEY-ID": key_id,
        "APCA-API-SECRET-KEY": secret,
        "Accept": "application/json",
    }


def _read_json(path, *, item, params=None, opener=None):
    opener = opener or build_opener(_NoRedirect())
    query = ("?" + urlencode(params)) if params else ""
    url = BASE + path + query
    req = Request(url, headers=_headers(item), method="GET")
    try:
        with opener.open(req, timeout=8) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("ALPACA_RESPONSE_HOLD")
            raw = response.read(MAX_RESPONSE + 1)
    except HTTPError as exc:
        if exc.code == 401:
            raise ValueError("ALPACA_AUTH_REJECTED") from None
        if exc.code == 403:
            raise ValueError("ALPACA_ENTITLEMENT_HOLD") from None
        if exc.code == 429:
            raise ValueError("ALPACA_RATE_LIMITED") from None
        raise ValueError("ALPACA_PROVIDER_HOLD") from None
    except (URLError, OSError, TimeoutError):
        raise ValueError("ALPACA_NETWORK_HOLD") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("ALPACA_RESPONSE_TOO_LARGE")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ValueError("ALPACA_RESPONSE_PARSE_HOLD") from None
    if not isinstance(doc, dict):
        raise ValueError("ALPACA_RESPONSE_SHAPE_HOLD")
    return doc


def latest_stock_context(symbol: str, *, item, opener=None) -> dict:
    symbol = str(symbol or "").strip().upper()
    if not SYMBOL.fullmatch(symbol) or ".." in symbol:
        raise ValueError("ALPACA_SYMBOL_HOLD")

    quote_doc = _read_json(
        f"/v2/stocks/{symbol}/quotes/latest",
        item=item,
        params={"feed": "iex"},
        opener=opener,
    )
    bar_doc = _read_json(
        f"/v2/stocks/{symbol}/bars/latest",
        item=item,
        params={"feed": "iex"},
        opener=opener,
    )

    quote = quote_doc.get("quote")
    bar = bar_doc.get("bar")
    if not isinstance(quote, dict) or not isinstance(bar, dict):
        raise ValueError("ALPACA_RESPONSE_SHAPE_HOLD")

    bid = quote.get("bp")
    ask = quote.get("ap")
    close = bar.get("c")
    ts = quote.get("t") or bar.get("t")
    if close is None or ts is None:
        raise ValueError("ALPACA_RESPONSE_SHAPE_HOLD")

    midpoint = None
    if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
        midpoint = (float(bid) + float(ask)) / 2.0

    return {
        "schema": "OB_ALPACA_PERSONAL_MARKET_CONTEXT_V1",
        "provider": "alpaca",
        "symbol": symbol,
        "feed": "iex",
        "observed_at": ts,
        "received_at": _now().isoformat(),
        "latest_minute_bar": {
            "open": bar.get("o"),
            "high": bar.get("h"),
            "low": bar.get("l"),
            "close": close,
            "volume": bar.get("v"),
            "timestamp": bar.get("t"),
        },
        "latest_quote": {
            "bid": bid,
            "bid_size": quote.get("bs"),
            "ask": ask,
            "ask_size": quote.get("as"),
            "midpoint": midpoint,
            "timestamp": quote.get("t"),
        },
        "rights": {
            "account_scope": "PERSONAL_OWNER_DEVELOPMENT",
            "production_commercial_rights_inferred": False,
            "redistribution_rights_inferred": False,
            "display_rights_inferred": False,
            "source_reference": "https://docs.alpaca.markets/us/docs/about-market-data-api",
        },
        "execution_grade_quote": False,
        "candidate_admitted": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
        "may_change_trading_mode": False,
    }


def websocket_plan() -> dict:
    """Declarative stream plan; connection lifecycle is owned by OB stream hub."""
    return {
        "schema": "OB_ALPACA_PERSONAL_STREAM_PLAN_V1",
        "provider": "alpaca",
        "endpoint": "wss://stream.data.alpaca.markets/v2/iex",
        "auth": {
            "type": "key_secret_message",
            "key_source": "tower_temporary_key_desk",
            "secret_persisted": False,
        },
        "channels": ["trades", "quotes", "bars"],
        "scope": "PERSONAL_OWNER_DEVELOPMENT",
        "commercial_rights_inferred": False,
        "execution_authority": False,
    }
