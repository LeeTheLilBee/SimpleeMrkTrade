"""Tower server-only runtime for zero-cost commercial market context.

The browser-visible route from this module is STATUS ONLY. Raw/normalized Twelve Data
Business Basic market values are kept server-side because that $0 business tier is
internal non-display. Finazon values are also kept server-side by default until an
independent owner-display grant is reviewed for the actual account/workspace.

This service never creates an execution-grade quote, order, candidate admission or
trading-mode change. It consumes temporary Key Desk credentials for the current
Tower owner session only.
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

from flask import Blueprint, abort, jsonify, make_response

from engine.market_intake.commercial_free_market import (
    FINAZON_FREE_TRIAL_SYMBOLS,
    FINAZON_ID,
    TWELVE_DATA_ID,
    normalize_finazon_snapshot,
    normalize_twelve_data_quote,
    record_digest,
    stream_plan,
)
from tower.ob_provider_diagnostics import classify_http_status
from tower.ob_public_owner_connection import _owner_sid

PATH = "/ob/data-desk/commercial-free.json"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
MAX_RESPONSE = 900_000
TWELVE_CACHE = timedelta(seconds=12)
FINAZON_CACHE = timedelta(seconds=35)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _now():
    return datetime.now(timezone.utc)


def _global_enabled():
    return os.environ.get("OB_COMMERCIAL_FREE_MARKET_FETCH_ENABLED") == "1"


def _rights(provider):
    if provider == TWELVE_DATA_ID:
        reviewed = os.environ.get("OB_PROVIDER_TWELVE_DATA_BUSINESS_BASIC_REVIEWED") == "1"
        return {
            "terms_reviewed": reviewed,
            "commercial_internal_use": reviewed,
            "owner_display": False,
            "invitee_display": False,
            "redistribution": False,
            "ai_use": os.environ.get("OB_PROVIDER_TWELVE_DATA_AI_USE_REVIEWED") == "1" and reviewed,
            "product": "Twelve Data Business Basic",
            "permission_reference": "https://twelvedata.com/pricing-business",
            "coverage": "US equities/ETFs; plan-defined real-time context; no bid/ask asserted",
            "free_limit": "8 API credits/minute, 800/day, 8 trial WebSocket credits",
        }
    if provider == FINAZON_ID:
        reviewed = os.environ.get(
            "OB_PROVIDER_FINAZON_US_EQUITIES_BASIC_COMMERCIAL_REVIEWED"
        ) == "1"
        return {
            "terms_reviewed": reviewed,
            "commercial_internal_use": reviewed,
            "owner_display": (
                os.environ.get("OB_PROVIDER_FINAZON_OWNER_DISPLAY_REVIEWED") == "1" and reviewed
            ),
            "invitee_display": False,
            "redistribution": False,
            "ai_use": os.environ.get("OB_PROVIDER_FINAZON_AI_USE_REVIEWED") == "1" and reviewed,
            "product": "Finazon US Equities Basic free trial",
            "permission_reference": "https://finazon.io/dataset/us_stocks_essential",
            "coverage": "derived US equity context; free trial AAPL/TSLA/GOOG only",
            "free_limit": "AAPL/TSLA/GOOG via API/WS; 1 WebSocket symbol; 2 snapshot RPM",
        }
    raise ValueError("unknown commercial-free provider")


def _read_json(request, *, opener=None):
    opener = opener or build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=8) as response:
            if response.geturl() != request.full_url:
                raise ValueError("REDIRECT_HOLD")
            if response.status != 200:
                raise ValueError(classify_http_status(response.status))
            raw = response.read(MAX_RESPONSE + 1)
    except HTTPError as exc:
        raise ValueError(classify_http_status(exc.code)) from None
    except (URLError, OSError, TimeoutError):
        raise ValueError("NETWORK_HOLD") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("RESPONSE_TOO_LARGE")
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ValueError("RESPONSE_PARSE_HOLD") from None
    if not isinstance(document, dict):
        raise ValueError("RESPONSE_SHAPE_HOLD")
    return document


class CommercialFreeMarketService:
    def __init__(self, *, secret_reader, status_reader, opener=None, clock=None):
        if not callable(secret_reader) or not callable(status_reader):
            raise ValueError("server-only Key Desk secret/status readers required")
        self.secret_reader = secret_reader
        self.status_reader = status_reader
        self.opener = opener
        self.clock = clock or _now
        self._lock = RLock()
        self._cache = {}
        self._last_success = {}

    def _cached(self, sid, provider, symbol, ttl):
        with self._lock:
            item = self._cache.get((sid, provider, symbol))
            if not item:
                return None
            expires, record = item
            if expires <= self.clock():
                self._cache.pop((sid, provider, symbol), None)
                return None
            return record

    def _store(self, sid, provider, symbol, ttl, record):
        with self._lock:
            self._cache[(sid, provider, symbol)] = (self.clock() + ttl, record)
            self._last_success[(sid, provider)] = self.clock()

    def _twelve(self, sid, symbol):
        cached = self._cached(sid, TWELVE_DATA_ID, symbol, TWELVE_CACHE)
        if cached is not None:
            return cached
        key = self.secret_reader(sid, TWELVE_DATA_ID)
        if key is None:
            raise ValueError("NOT_CONFIGURED")
        rights = _rights(TWELVE_DATA_ID)
        if not _global_enabled() or not rights["commercial_internal_use"]:
            raise ValueError("RIGHTS_OR_FETCH_HOLD")
        url = "https://api.twelvedata.com/quote?" + urlencode({"symbol": symbol})
        document = _read_json(Request(
            url,
            headers={"Authorization": "apikey " + key.value, "Accept": "application/json"},
            method="GET",
        ), opener=self.opener)
        if document.get("status") == "error" or document.get("code") in {401, 403, 429}:
            code = document.get("code")
            raise ValueError(classify_http_status(code) if code else "PROVIDER_MESSAGE")
        record = normalize_twelve_data_quote(document, symbol=symbol, received_at=self.clock())
        self._store(sid, TWELVE_DATA_ID, symbol, TWELVE_CACHE, record)
        return record

    def _finazon(self, sid, symbol):
        if symbol not in FINAZON_FREE_TRIAL_SYMBOLS:
            raise ValueError("TRIAL_SYMBOL_HOLD")
        cached = self._cached(sid, FINAZON_ID, symbol, FINAZON_CACHE)
        if cached is not None:
            return cached
        key = self.secret_reader(sid, FINAZON_ID)
        if key is None:
            raise ValueError("NOT_CONFIGURED")
        rights = _rights(FINAZON_ID)
        if not _global_enabled() or not rights["commercial_internal_use"]:
            raise ValueError("RIGHTS_OR_FETCH_HOLD")
        url = "https://api.finazon.io/latest/finazon/us_stocks_essential/ticker_snapshot?" + urlencode(
            {"ticker": symbol}
        )
        document = _read_json(Request(
            url,
            headers={"Authorization": "apikey " + key.value, "Accept": "application/json"},
            method="GET",
        ), opener=self.opener)
        record = normalize_finazon_snapshot(document, symbol=symbol, received_at=self.clock())
        self._store(sid, FINAZON_ID, symbol, FINAZON_CACHE, record)
        return record

    def read_symbol_internal(self, sid, symbol):
        if not isinstance(sid, str) or not sid.startswith("tower_session_"):
            raise ValueError("current Tower owner session required")
        symbol = str(symbol or "").strip().upper()
        if not SYMBOL.fullmatch(symbol) or ".." in symbol:
            raise ValueError("valid ticker required")
        rows = []
        records = []
        for provider, reader in ((TWELVE_DATA_ID, self._twelve), (FINAZON_ID, self._finazon)):
            try:
                record = reader(sid, symbol)
                records.append(record)
                rows.append({
                    "provider": provider,
                    "state": "SOURCE_BOUND",
                    "record": record.internal_projection(),
                    "rights": _rights(provider),
                })
            except ValueError as exc:
                code = str(exc)
                if code not in {
                    "NOT_CONFIGURED", "RIGHTS_OR_FETCH_HOLD", "TRIAL_SYMBOL_HOLD",
                    "RATE_LIMITED", "ACCESS_REJECTED", "REQUEST_REJECTED",
                    "PROVIDER_UNAVAILABLE", "NETWORK_HOLD", "REDIRECT_HOLD",
                    "RESPONSE_TOO_LARGE", "RESPONSE_PARSE_HOLD",
                    "RESPONSE_SHAPE_HOLD", "PROVIDER_MESSAGE",
                }:
                    code = "SOURCE_HOLD"
                rows.append({
                    "provider": provider,
                    "state": code,
                    "record": None,
                    "rights": _rights(provider),
                })
            except Exception:
                rows.append({
                    "provider": provider,
                    "state": "SOURCE_HOLD",
                    "record": None,
                    "rights": _rights(provider),
                })
        return {
            "schema": "OB_COMMERCIAL_FREE_MARKET_INTERNAL_V1",
            "symbol": symbol,
            "as_of": self.clock().isoformat(),
            "internal_non_display": True,
            "provider_context": rows,
            "digest": record_digest(records) if records else None,
            "bid_ask_attached": False,
            "execution_grade_quote_attached": False,
            "candidate_admitted": False,
            "broker_execution_authorized": False,
            "capital_authorized": False,
            "may_change_trading_mode": False,
        }

    def status(self, sid):
        if not isinstance(sid, str) or not sid.startswith("tower_session_"):
            raise ValueError("current Tower owner session required")
        rows = []
        key_status = {row["id"]: row for row in self.status_reader(sid)}
        for provider in (TWELVE_DATA_ID, FINAZON_ID):
            rights = _rights(provider)
            row = key_status.get(provider, {})
            with self._lock:
                success = self._last_success.get((sid, provider))
            rows.append({
                "provider": provider,
                "product": rights["product"],
                "credential_present": row.get("present") is True,
                "credential_probe": row.get("probe", "NOT_CONFIGURED"),
                "terms_reviewed": rights["terms_reviewed"],
                "commercial_internal_use": rights["commercial_internal_use"],
                "owner_display": rights["owner_display"],
                "ai_use": rights["ai_use"],
                "coverage": rights["coverage"],
                "free_limit": rights["free_limit"],
                "websocket_supported": True,
                "stream_slots": 8 if provider == TWELVE_DATA_ID else 1,
                "last_internal_success_at": success.isoformat() if success else None,
                "raw_values_exposed_to_browser": False,
                "execution_grade_quote": False,
            })
        return {
            "schema": "OB_COMMERCIAL_FREE_MARKET_STATUS_V1",
            "as_of": self.clock().isoformat(),
            "owner_session_checked": True,
            "fetch_enabled": _global_enabled(),
            "providers": rows,
            "raw_market_values_attached": False,
            "browser_display_authority": False,
            "broker_execution_authorized": False,
            "candidate_admitted": False,
            "may_change_trading_mode": False,
        }


    def free_stream_plan(self, symbols):
        return stream_plan(symbols)


def create_commercial_free_market_status_blueprint(*, owner_authorize, service):
    if not callable(owner_authorize) or not isinstance(service, CommercialFreeMarketService):
        raise ValueError("Tower owner auth and commercial-free market service required")
    bp = Blueprint("ob_commercial_free_market_status", __name__)

    @bp.route(PATH, methods=["GET"])
    def status():
        if owner_authorize() is not True:
            abort(403)
        sid = _owner_sid()
        if not sid:
            abort(403)
        try:
            payload = service.status(sid)
        except Exception:
            abort(503)
        response = make_response(jsonify(payload))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return bp
