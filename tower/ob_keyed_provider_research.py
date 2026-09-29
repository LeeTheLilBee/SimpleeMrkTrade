"""Tower owner-only normalized research from temporary Finnhub/Alpha Vantage keys.

This corridor is deliberately NOT a live quote feed, scanner install, broker route
or durable secret store. It is a user-triggered, bounded read-only research
projection for the current Tower owner session.

- Finnhub: company profile reference only (no quote endpoint).
- Alpha Vantage: raw completed daily history only (TIME_SERIES_DAILY compact).
- Every provider requires separate source-use + owner-display review flags.
- Soulaana content requires a separate provider-specific AI-use review flag.
- Temporary keys remain in the existing in-memory key desk and never enter JSON.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
import re
from threading import RLock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from flask import Blueprint, abort, jsonify, make_response, request

from tower.ob_public_owner_connection import _owner_sid

PATH = "/ob/research/providers.json"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
PROVIDERS = ("finnhub", "alpha_vantage")
MAX_RESPONSE = 900_000
CACHE_TTL = timedelta(minutes=5)


def _now():
    return datetime.now(timezone.utc)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _enabled(provider: str) -> bool:
    prefix = "OB_PROVIDER_" + provider.upper()
    return (
        os.environ.get("OB_PROVIDER_RESEARCH_FETCH_ENABLED") == "1"
        and os.environ.get(prefix + "_SOURCE_USE_REVIEWED") == "1"
        and os.environ.get(prefix + "_OWNER_DISPLAY_REVIEWED") == "1"
    )


def _ai_enabled(provider: str) -> bool:
    prefix = "OB_PROVIDER_" + provider.upper()
    return _enabled(provider) and os.environ.get(prefix + "_AI_USE_REVIEWED") == "1"


def _read_json(req: Request, *, opener=None) -> dict:
    opener = opener or build_opener(_NoRedirect())
    try:
        with opener.open(req, timeout=8) as response:
            if response.status != 200 or response.geturl() != req.full_url:
                raise ValueError("provider response hold")
            raw = response.read(MAX_RESPONSE + 1)
    except (HTTPError, URLError, OSError, TimeoutError) as exc:
        raise ValueError("provider response hold") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("provider response hold")
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ValueError("provider response hold") from None
    if not isinstance(document, dict):
        raise ValueError("provider response hold")
    return document


def _finnhub(symbol: str, secret: str, *, opener=None) -> dict:
    url = "https://finnhub.io/api/v1/stock/profile2?" + urlencode({"symbol": symbol})
    doc = _read_json(Request(
        url, headers={"X-Finnhub-Token": secret, "Accept": "application/json"}, method="GET"
    ), opener=opener)
    ticker = str(doc.get("ticker") or "").upper()
    name = doc.get("name")
    exchange = doc.get("exchange")
    industry = doc.get("finnhubIndustry")
    ipo = doc.get("ipo")
    if ticker != symbol or not isinstance(name, str) or not name.strip():
        raise ValueError("provider response hold")
    return {
        "provider": "finnhub",
        "kind": "COMPANY_REFERENCE",
        "symbol": symbol,
        "security_name": name[:180],
        "exchange": exchange[:120] if isinstance(exchange, str) else None,
        "industry": industry[:120] if isinstance(industry, str) else None,
        "ipo_date": ipo[:20] if isinstance(ipo, str) else None,
        "source_reference": "https://finnhub.io/docs/api/company-profile2",
        "historical_only": False,
        "live_quote": False,
    }


def _alpha_vantage(symbol: str, secret: str, *, opener=None) -> dict:
    url = "https://www.alphavantage.co/query?" + urlencode({
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": secret,
    })
    doc = _read_json(Request(url, headers={"Accept": "application/json"}, method="GET"), opener=opener)
    if "Error Message" in doc or "Information" in doc or "Note" in doc:
        raise ValueError("provider response hold")
    meta = doc.get("Meta Data")
    series = doc.get("Time Series (Daily)")
    if not isinstance(meta, dict) or not isinstance(series, dict):
        raise ValueError("provider response hold")
    stated_symbol = str(meta.get("2. Symbol") or "").upper()
    if stated_symbol and stated_symbol != symbol:
        raise ValueError("provider response hold")
    bars = []
    for day in sorted(series.keys(), reverse=True)[:5]:
        row = series.get(day)
        if not isinstance(row, dict) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day)):
            continue
        try:
            open_v = float(row["1. open"])
            high_v = float(row["2. high"])
            low_v = float(row["3. low"])
            close_v = float(row["4. close"])
            volume_v = int(float(row["5. volume"]))
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if min(open_v, high_v, low_v, close_v) <= 0 or volume_v < 0:
            continue
        if low_v > min(open_v, close_v) or high_v < max(open_v, close_v):
            continue
        bars.append({
            "session_date": str(day),
            "open": open_v, "high": high_v, "low": low_v, "close": close_v,
            "volume": volume_v,
        })
    if not bars:
        raise ValueError("provider response hold")
    return {
        "provider": "alpha_vantage",
        "kind": "COMPLETED_DAILY_HISTORY",
        "symbol": symbol,
        "bars": bars,
        "source_reference": "https://www.alphavantage.co/documentation/#daily",
        "historical_only": True,
        "live_quote": False,
    }


def _soulaana(rows: list[dict]) -> dict:
    readable = []
    for row in rows:
        provider = row.get("provider")
        if row.get("state") != "SOURCE_BOUND" or provider not in PROVIDERS or not _ai_enabled(provider):
            continue
        item = {
            "provider": provider,
            "kind": row["kind"],
            "symbol": row["symbol"],
            "source_reference": row["source_reference"],
            "research_only": True,
            "live_quote": False,
        }
        if provider == "finnhub":
            item["summary"] = {
                "security_name": row.get("security_name"),
                "exchange": row.get("exchange"),
                "industry": row.get("industry"),
                "ipo_date": row.get("ipo_date"),
            }
        else:
            item["summary"] = {
                "completed_sessions": len(row.get("bars", [])),
                "latest_session": row.get("bars", [{}])[0].get("session_date") if row.get("bars") else None,
            }
        readable.append(item)
    return {
        "schema": "OB_SOULAANA_KEYED_PROVIDER_RESEARCH_V1",
        "channel": "SOULAANA_REVIEWED_PROVIDER_RESEARCH",
        "observations": readable,
        "source_specific_ai_use_approved": bool(readable),
        "raw_credentials_included": False,
        "account_identifiers_included": False,
        "live_quote_verified": False,
        "candidate_admitted": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
        "may_change_trading_mode": False,
    }


class ProviderResearchCache:
    def __init__(self):
        self._lock = RLock()
        self._rows = {}

    def get(self, key):
        now = _now()
        with self._lock:
            item = self._rows.get(key)
            if not item:
                return None
            expires, value = item
            if expires <= now:
                self._rows.pop(key, None)
                return None
            return value

    def put(self, key, value):
        with self._lock:
            self._rows[key] = (_now() + CACHE_TTL, value)


def provider_research_projection(*, sid: str, symbol: str, secret_reader,
                                 opener=None, cache=None) -> dict:
    if not isinstance(sid, str) or not sid.startswith("tower_session_"):
        raise ValueError("current owner session required")
    symbol = str(symbol or "").strip().upper()
    if not SYMBOL.fullmatch(symbol) or ".." in symbol:
        raise ValueError("valid ticker required")
    cache = cache or ProviderResearchCache()
    rows = []
    for provider in PROVIDERS:
        item = secret_reader(sid, provider)
        if item is None:
            rows.append({"provider": provider, "state": "NOT_CONNECTED"})
            continue
        if not _enabled(provider):
            rows.append({"provider": provider, "state": "RIGHTS_OR_FETCH_HOLD"})
            continue
        key = (sid, provider, symbol)
        cached = cache.get(key)
        if cached is not None:
            rows.append(cached)
            continue
        try:
            payload = (
                _finnhub(symbol, item.value, opener=opener)
                if provider == "finnhub"
                else _alpha_vantage(symbol, item.value, opener=opener)
            )
            row = {"state": "SOURCE_BOUND", **payload}
        except Exception:
            row = {"provider": provider, "state": "SOURCE_HOLD"}
        cache.put(key, row)
        rows.append(row)
    return {
        "schema": "OB_KEYED_PROVIDER_RESEARCH_V1",
        "symbol": symbol,
        "as_of": _now().isoformat(),
        "owner_session_checked": True,
        "source_only": True,
        "provider_research": rows,
        "live_prices_attached": False,
        "positions_attached": False,
        "orders_attached": False,
        "may_authorize_order": False,
        "may_authorize_capital": False,
        "may_change_trading_mode": False,
        "soulaana_research": _soulaana(rows),
    }


def create_keyed_provider_research_blueprint(*, owner_authorize, secret_reader, opener=None):
    if not callable(owner_authorize) or not callable(secret_reader):
        raise ValueError("Tower owner authorization and server key reader required")
    cache = ProviderResearchCache()
    bp = Blueprint("ob_keyed_provider_research", __name__)

    @bp.route(PATH, methods=["GET"])
    def provider_research():
        if owner_authorize() is not True:
            abort(403)
        sid = _owner_sid()
        if not sid:
            abort(403)
        try:
            payload = provider_research_projection(
                sid=sid, symbol=request.args.get("symbol", ""),
                secret_reader=secret_reader, opener=opener, cache=cache,
            )
        except ValueError:
            abort(400)
        response = make_response(jsonify(payload))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Cookie"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    return bp
