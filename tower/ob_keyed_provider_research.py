"""Tower owner-only normalized research from temporary provider keys.

This corridor is a bounded, user-triggered read-only projection for the current
Tower owner session. It never grants trading, capital, broker or mode authority.

- Finnhub: company profile reference only.
- Alpha Vantage: completed daily history only.
- Finazon: commercial-license-free US Equities Basic market context; the
  free-forever trial is restricted to AAPL, TSLA and GOOG.
- BEA: official public-domain U.S. macroeconomic statistics.
- EIA uses the separate Official Catalyst Radar so its energy series are not
  duplicated in this corridor.
- Every provider requires separate source-use + owner-display review flags.
- Soulaana content requires a separate provider-specific AI-use review flag.
- Temporary keys remain in the in-memory Key Desk and never enter JSON.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from math import isfinite
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
PROVIDERS = ("finnhub", "alpha_vantage", "finazon", "bea")
FINAZON_FREE_SYMBOLS = frozenset({"AAPL", "TSLA", "GOOG"})
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
        if not all(isfinite(n) for n in (open_v, high_v, low_v, close_v)):
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



def _finazon(symbol: str, secret: str, *, opener=None) -> dict:
    """One commercial-license-free, venue-limited real-time snapshot.

    Free-trial access is explicitly restricted by Finazon to AAPL/TSLA/GOOG.
    This is derived/venue-limited context, never SIP/NBBO or execution authority.
    """
    if symbol not in FINAZON_FREE_SYMBOLS:
        return {
            "provider": "finazon", "kind": "DERIVED_REALTIME_EQUITY_CONTEXT",
            "symbol": symbol, "trial_symbol_limited": True,
            "eligible_trial_symbols": sorted(FINAZON_FREE_SYMBOLS),
            "source_reference": "https://finazon.io/dataset/us_stocks_essential",
            "historical_only": False, "live_quote": False,
            "real_time_market_context": False, "consolidated_quote": False,
            "trial_access_state": "SYMBOL_NOT_IN_FREE_TRIAL",
        }
    url = "https://api.finazon.io/v2.0/finazon/us_stocks_essential/ticker_snapshot?" + urlencode({
        "ticker": symbol, "apikey": secret})
    doc = _read_json(Request(url, headers={"Accept": "application/json"}, method="GET"),
                     opener=opener)
    last_trade = doc.get("lt")
    day = doc.get("1d")
    prior = doc.get("p1d")
    year = doc.get("52w")
    change = doc.get("ch")
    if not all(isinstance(x, dict) for x in (last_trade, day, prior, year, change)):
        raise ValueError("provider response hold")
    try:
        trade_price = float(last_trade["p"])
        trade_size = int(last_trade["s"])
        trade_time_ms = int(last_trade["tm"])
        day_values = {k: float(day[k]) for k in ("o", "h", "l", "c")}
        day_volume = int(float(day["v"]))
        prior_close = float(prior["c"])
        high_52w = float(year["h"])
        low_52w = float(year["l"])
        daily_change_pct = float(change["dap"])
    except (KeyError, TypeError, ValueError, OverflowError):
        raise ValueError("provider response hold") from None
    numbers = [trade_price, *day_values.values(), prior_close, high_52w,
               low_52w, daily_change_pct]
    if not all(isfinite(x) for x in numbers) or min(trade_price, *day_values.values(),
                                                    prior_close, high_52w, low_52w) <= 0:
        raise ValueError("provider response hold")
    if trade_size < 0 or trade_time_ms <= 0 or day_volume < 0:
        raise ValueError("provider response hold")
    if day_values["l"] > min(day_values["o"], day_values["c"]) or             day_values["h"] < max(day_values["o"], day_values["c"]):
        raise ValueError("provider response hold")
    return {
        "provider": "finazon",
        "kind": "DERIVED_REALTIME_EQUITY_CONTEXT",
        "symbol": symbol,
        "last_trade": {"timestamp_ms": trade_time_ms, "price": trade_price, "size": trade_size},
        "session": {**day_values, "volume": day_volume},
        "prior_close": prior_close,
        "high_52w": high_52w, "low_52w": low_52w,
        "daily_change_percent": daily_change_pct,
        "source_reference": "https://finazon.io/dataset/us_stocks_essential",
        "historical_only": False,
        "live_quote": False,
        "real_time_market_context": True,
        "consolidated_quote": False,
        "coverage": "DERIVED_IEX_AND_LIMITED_US_VENUES",
        "trial_symbol_limited": True,
    }


def _bea(symbol: str, secret: str, *, opener=None) -> dict:
    """Official quarterly nominal GDP context from BEA NIPA table 1.1.1/1.1.5 family.

    The macro observation applies to the whole U.S. economy; symbol is retained
    only to keep this route's per-symbol research packet self-contained.
    """
    year = _now().year
    url = "https://apps.bea.gov/api/data?" + urlencode({
        "UserID": secret,
        "method": "GetData",
        "DataSetName": "NIPA",
        "TableName": "T10101",
        "Frequency": "Q",
        "Year": f"{year-1},{year}",
        "ResultFormat": "JSON",
    })
    doc = _read_json(Request(url, headers={"Accept": "application/json"}, method="GET"),
                     opener=opener)
    bea = doc.get("BEAAPI")
    results = bea.get("Results") if isinstance(bea, dict) else None
    rows = results.get("Data") if isinstance(results, dict) else None
    if not isinstance(rows, list):
        raise ValueError("provider response hold")
    observations = []
    for row in rows:
        if not isinstance(row, dict) or str(row.get("LineNumber")) != "1":
            continue
        period = row.get("TimePeriod")
        raw = row.get("DataValue")
        if not isinstance(period, str) or not re.fullmatch(r"20\d{2}Q[1-4]", period):
            continue
        try:
            value = Decimal(str(raw).replace(",", ""))
        except Exception:
            continue
        if not value.is_finite() or value <= 0:
            continue
        observations.append({"period": period, "value": str(value)})
    observations.sort(key=lambda x: x["period"], reverse=True)
    observations = observations[:4]
    if not observations:
        raise ValueError("provider response hold")
    return {
        "provider": "bea",
        "kind": "OFFICIAL_US_QUARTERLY_GDP_CONTEXT",
        "symbol": symbol,
        "observations": observations,
        "unit": "BEA_SOURCE_UNIT",
        "source_reference": "https://apps.bea.gov/api/",
        "historical_only": True,
        "live_quote": False,
        "public_domain_source": True,
    }

def _soulaana(rows: list[dict]) -> dict:
    """Examine only independently AI-reviewed bounded provider evidence.

    This is source-backed, deterministic interpretation of research facts,
    not an LLM call, streaming price, scanner signal or trade instruction.
    Revoking a provider's AI-use review removes its findings even on a cache hit.
    """
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
            name = row.get("security_name")
            exchange = row.get("exchange")
            industry = row.get("industry")
            item["summary"] = {
                "security_name": name, "exchange": exchange,
                "industry": industry, "ipo_date": row.get("ipo_date"),
            }
            item["finding"] = (
                f"Finnhub's company profile identifies {row['symbol']} as {name or 'unnamed'}"
                + (f"; reported industry: {industry}" if industry else "")
                + (f"; reported exchange: {exchange}" if exchange else "")
                + ". This is provider reference metadata, not independent issuer corroboration."
            )
            item["what_is_missing"] = (
                "Confirm issuer identity and material events in the separate SEC research corridor. "
                "This profile establishes neither a current stock/option quote nor an investment signal."
            )
        elif provider == "alpha_vantage":
            bars = row.get("bars", [])
            latest = bars[0]
            item["summary"] = {
                "completed_sessions": len(bars),
                "latest_session": latest["session_date"],
            }
            item["finding"] = (
                f"Alpha Vantage reports a completed historical daily close for {row['symbol']} "
                f"on {latest['session_date']}: {latest['close']:.2f}. "
            )
            if len(bars) >= 2:
                prior = bars[1]
                current_close = Decimal(str(latest["close"]))
                prior_close = Decimal(str(prior["close"]))
                difference = current_close - prior_close
                percent = (difference / prior_close) * Decimal("100")
                item["finding"] += (
                    f"Compared with {prior['session_date']} ({prior_close:.2f}), "
                    f"the close changed {difference:+.2f} ({percent:+.3f}%). "
                )
                item["summary"]["prior_session"] = prior["session_date"]
                item["summary"]["close_change"] = str(difference)
                item["summary"]["close_change_percent"] = f"{percent:+.3f}"
            else:
                item["finding"] += "No second validated daily session is available for comparison. "
            item["finding"] += (
                "This is a comparison of source-reported completed daily records, not a live quote or forecast."
            )
            item["what_is_missing"] = (
                "The latest intraday market, options chain, data entitlement and issuer-event "
                "cross-check remain separate; do not extrapolate a current price or trade signal."
            )
        elif provider == "finazon":
            trade = row["last_trade"]
            session = row["session"]
            item["summary"] = {
                "last_trade_price": trade["price"],
                "last_trade_timestamp_ms": trade["timestamp_ms"],
                "session_open": session["o"], "session_high": session["h"],
                "session_low": session["l"], "session_close": session["c"],
                "daily_change_percent": row["daily_change_percent"],
                "high_52w": row["high_52w"], "low_52w": row["low_52w"],
            }
            item["finding"] = (
                f"Finazon US Equities Basic reports venue-limited derived real-time context for "
                f"{row['symbol']}; latest source trade {trade['price']:.4f}, "
                f"session range {session['l']:.4f}-{session['h']:.4f}. "
                "This is not SIP/NBBO or a consolidated execution quote."
            )
            item["what_is_missing"] = (
                "A consolidated market quote, options chain, broker-side entitlement and execution "
                "context remain separate. Treat this as one corroborating market-data source."
            )
        else:
            observations = row["observations"]
            latest = observations[0]
            item["summary"] = {
                "latest_period": latest["period"], "latest_value": latest["value"],
                "observation_count": len(observations),
            }
            item["finding"] = (
                f"BEA's official NIPA data reports the latest available quarterly GDP observation "
                f"as {latest['value']} for {latest['period']}. This is U.S. macroeconomic context, "
                "not security-specific price evidence."
            )
            item["what_is_missing"] = (
                "Market reaction, current security pricing and causality must be established separately; "
                "a GDP observation alone does not create a trade candidate."
            )
        readable.append(item)
    return {
        "schema": "OB_SOULAANA_KEYED_PROVIDER_RESEARCH_V1",
        "channel": "SOULAANA_REVIEWED_PROVIDER_RESEARCH",
        "observations": readable,
        "source_specific_ai_use_approved": bool(readable),
        "external_model_called": False,
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
            if provider == "finnhub":
                payload = _finnhub(symbol, item.value, opener=opener)
            elif provider == "alpha_vantage":
                payload = _alpha_vantage(symbol, item.value, opener=opener)
            elif provider == "finazon":
                payload = _finazon(symbol, item.value, opener=opener)
                if payload.get("trial_access_state") == "SYMBOL_NOT_IN_FREE_TRIAL":
                    row = {"state": "FREE_TRIAL_SYMBOL_HOLD", **payload}
                    cache.put(key, row)
                    rows.append(row)
                    continue
            else:
                payload = _bea(symbol, item.value, opener=opener)
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
        "live_prices_attached": any(
            row.get("provider") == "finazon" and row.get("state") == "SOURCE_BOUND"
            and row.get("real_time_market_context") is True
            for row in rows
        ),
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
