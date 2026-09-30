"""Tower-guarded temporary research API-key entry (Finnhub / Alpha Vantage).

This is NOT a durable secret vault, API rights approval, market-data gateway, or
broker login. Values live only in one server worker's RAM for <= 30 minutes and
are cleared on Tower logout/forget/restart. No logs, cookies, rendered values,
client-side storage, untrusted URLs, network calls on GET, or trading actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hmac
import json
import os
import re
import secrets
from threading import RLock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from flask import Blueprint, Flask, abort, make_response, redirect, render_template, request, session

from tower.ob_public_owner_connection import _approved_browser_origin, _owner_sid
from tower.ob_provider_diagnostics import (
    classify_http_status, classify_provider_message, normalize_probe_code, probe_message,
)

PATH = "/ob/data-desk/api-keys"
TTL = timedelta(minutes=30)
MAX_BODY = 8192
MAX_KEYS_PER_SESSION = 5
PROVIDERS = {
    "finnhub": {"name": "Finnhub", "purpose": "Company and market research; exact endpoint and rights review still required.",
                "docs": "https://finnhub.io/docs/api"},
    "alpha_vantage": {"name": "Alpha Vantage", "purpose": "Completed historical stock bars and company research; default free quotes are not live.",
                      "docs": "https://www.alphavantage.co/documentation/"},
    "finazon": {"name": "Finazon", "purpose": "US Equities Basic derived market data; free-forever trial is limited to AAPL, TSLA and GOOG.",
                "docs": "https://finazon.io/dataset/us_stocks_essential/docs/api/latest"},
    "eia": {"name": "U.S. EIA", "purpose": "Free official U.S. energy data; used as economic/catalyst context, never a stock or option quote.",
            "docs": "https://www.eia.gov/opendata/documentation.php"},
    "bea": {"name": "U.S. BEA", "purpose": "Free official U.S. economic statistics; macro context only, never a security quote.",
            "docs": "https://apps.bea.gov/api/signup/"},
}
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,14}$")


def _now():
    return datetime.now(timezone.utc)


def _csrf():
    value = session.get("ob_provider_key_csrf")
    if not isinstance(value, str) or len(value) < 30:
        value = secrets.token_urlsafe(32)
        session["ob_provider_key_csrf"] = value
    return value


def _enabled():
    return os.environ.get("OB_PROVIDER_KEY_DESK_ENABLED") == "1"


def _form_hold():
    """Exact HTTPS origin, affirmative same-origin metadata and session CSRF."""
    if request.content_length is None or request.content_length > MAX_BODY:
        return "FORM_SIZE_HOLD"
    if request.mimetype != "application/x-www-form-urlencoded":
        return "FORM_TYPE_HOLD"
    # Duplicate/conflicting form fields must not allow different parser/proxy
    # interpretations of the same credential operation.
    required = {"csrf", "provider", "operation"}
    allowed = required | {"secret"}
    if not required <= set(request.form) or set(request.form) - allowed:
        return "FORM_FIELDS_HOLD"
    if any(len(request.form.getlist(key)) != 1 for key in request.form):
        return "FORM_FIELDS_HOLD"
    if request.form.get("operation") == "save" and "secret" not in request.form:
        return "FORM_FIELDS_HOLD"
    if request.form.get("operation") != "save" and "secret" in request.form:
        return "FORM_FIELDS_HOLD"
    expected = _approved_browser_origin()
    if not expected:
        return "ORIGIN_CONFIG_HOLD"
    site = request.headers.get("Sec-Fetch-Site", "").strip().lower()
    if site not in {"", "same-origin", "none"}:
        return "CROSS_SITE_HOLD"
    origin = request.headers.get("Origin", "").strip().lower()
    if origin:
        # Exact origin only. No null/opaque, paths, ports, internal host aliases.
        if origin != expected:
            return "ORIGIN_HOLD"
    elif site != "same-origin":
        return "ORIGIN_META_HOLD"
    supplied = request.form.get("csrf", "")
    if not isinstance(supplied, str) or not hmac.compare_digest(_csrf(), supplied):
        return "CSRF_HOLD"
    return None


def _headers(response):
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'self'; form-action 'self'; "
        "base-uri 'none'; frame-ancestors 'none'")
    return response


@dataclass
class TemporaryKey:
    value: str
    expires_at: datetime
    probe: str = "NOT_TESTED"
    last_checked_at: datetime | None = None


class TemporaryProviderKeyStore:
    """Only the trusted backend may read secret material; never a UI projection."""

    def __init__(self):
        self._lock = RLock()
        self._data: dict[str, dict[str, TemporaryKey]] = {}

    def _prune(self):
        current = _now()
        for sid in tuple(self._data):
            for provider in tuple(self._data[sid]):
                if self._data[sid][provider].expires_at <= current:
                    self._data[sid].pop(provider, None)
            if not self._data[sid]:
                self._data.pop(sid, None)

    def put(self, sid: str, provider: str, secret: str):
        if not sid.startswith("tower_session_") or provider not in PROVIDERS:
            raise ValueError("invalid owner/provider selection")
        if (not isinstance(secret, str) or not 8 <= len(secret) <= 4096
                or secret.strip() != secret or any(ord(ch) < 33 or ord(ch) > 126 for ch in secret)):
            raise ValueError("invalid key format")
        with self._lock:
            self._prune()
            bucket = self._data.setdefault(sid, {})
            if provider not in bucket and len(bucket) >= MAX_KEYS_PER_SESSION:
                raise ValueError("provider key capacity")
            bucket[provider] = TemporaryKey(secret, _now() + TTL)

    def get(self, sid: str, provider: str) -> TemporaryKey | None:
        if not isinstance(sid, str) or provider not in PROVIDERS:
            return None
        with self._lock:
            self._prune()
            return self._data.get(sid, {}).get(provider)

    def forget(self, sid: str, provider: str | None = None):
        with self._lock:
            if provider is None:
                self._data.pop(sid, None)
            elif provider in PROVIDERS:
                self._data.get(sid, {}).pop(provider, None)
                if not self._data.get(sid):
                    self._data.pop(sid, None)

    def status(self, sid: str):
        with self._lock:
            self._prune()
            bucket = self._data.get(sid, {})
            return tuple({
                "id": provider, "name": descriptor["name"],
                "purpose": descriptor["purpose"], "docs": descriptor["docs"],
                "present": provider in bucket,
                "probe": bucket[provider].probe if provider in bucket else "NOT_CONFIGURED",
                "probe_message": probe_message(
                    bucket[provider].probe if provider in bucket else "NOT_CONFIGURED"
                ),
                "expires_at": bucket[provider].expires_at.isoformat() if provider in bucket else None,
            } for provider, descriptor in PROVIDERS.items())


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def probe_one(provider: str, secret: str, *, opener=None) -> str:
    """One bounded official read-only request with secret-safe diagnostics.

    Alpha Vantage requires its key as an HTTPS query parameter. Never log the
    URL, request, HTTP exception, response, provider message or key. Finnhub uses
    its key header. Classification is deliberately coarse enough to avoid leaking
    upstream content while still distinguishing actionable failure families.
    """
    opener = opener or build_opener(_NoRedirect())
    if provider == "finnhub":
        url = "https://finnhub.io/api/v1/stock/profile2?symbol=AAPL"
        headers = {"X-Finnhub-Token": secret, "Accept": "application/json"}
    elif provider == "alpha_vantage":
        url = "https://www.alphavantage.co/query?" + urlencode({
            "function": "TIME_SERIES_DAILY", "symbol": "IBM",
            "outputsize": "compact", "apikey": secret})
        headers = {"Accept": "application/json"}
    elif provider == "finazon":
        url = "https://api.finazon.io/v2.0/finazon/us_stocks_essential/api_usage?" + urlencode({
            "apikey": secret})
        headers = {"Accept": "application/json"}
    elif provider == "eia":
        url = "https://api.eia.gov/v2/electricity?" + urlencode({"api_key": secret})
        headers = {"Accept": "application/json"}
    elif provider == "bea":
        url = "https://apps.bea.gov/api/data?" + urlencode({
            "UserID": secret, "method": "GETDATASETLIST", "ResultFormat": "JSON"})
        headers = {"Accept": "application/json"}
    else:
        raise ValueError("unrecognized provider")
    try:
        with opener.open(Request(url, headers=headers, method="GET"), timeout=8) as response:
            if response.geturl() != url:
                return "REDIRECT_HOLD"
            if response.status != 200:
                return classify_http_status(response.status)
            raw = response.read(800_001)
    except HTTPError as exc:
        return classify_http_status(exc.code)
    except (URLError, OSError, TimeoutError):
        return "NETWORK_HOLD"
    if len(raw) > 800_000:
        return "RESPONSE_TOO_LARGE"
    try:
        document = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        return "RESPONSE_PARSE_HOLD"
    if not isinstance(document, dict):
        return "RESPONSE_SHAPE_HOLD"

    if provider == "finnhub":
        provider_error = document.get("error")
        if provider_error is not None:
            return classify_provider_message(provider_error)
        if document.get("ticker") != "AAPL" or not isinstance(document.get("name"), str):
            return "RESPONSE_SHAPE_HOLD"
    elif provider == "alpha_vantage":
        # Alpha Vantage commonly returns a normal HTTP 200 with a bounded
        # Information/Note/Error Message object instead of the requested series.
        # We classify the family, then discard the upstream message itself.
        for key in ("Information", "Note"):
            if key in document:
                return classify_provider_message(document.get(key))
        if "Error Message" in document:
            return "REQUEST_REJECTED"
        if not isinstance(document.get("Time Series (Daily)"), dict) or not isinstance(document.get("Meta Data"), dict):
            return "RESPONSE_SHAPE_HOLD"
    elif provider == "finazon":
        calls = document.get("api_calls")
        if not isinstance(calls, dict) or not isinstance(calls.get("limit"), int) or not isinstance(calls.get("usage"), int):
            return "RESPONSE_SHAPE_HOLD"
    elif provider == "eia":
        response = document.get("response")
        if not isinstance(response, dict) or not isinstance(response.get("routes"), list):
            return "RESPONSE_SHAPE_HOLD"
    elif provider == "bea":
        bea = document.get("BEAAPI")
        results = bea.get("Results") if isinstance(bea, dict) else None
        datasets = results.get("Dataset") if isinstance(results, dict) else None
        error = results.get("Error") if isinstance(results, dict) else None
        if error is not None:
            return classify_provider_message(str(error)[:400])
        if not isinstance(datasets, list) or not datasets:
            return "RESPONSE_SHAPE_HOLD"
    return "READ_ONLY_CHECK_PASSED"


def create_provider_key_blueprint(*, owner_authorize, store=None, probe=None):
    if not callable(owner_authorize):
        raise ValueError("Tower owner authorization required")
    memory = store if store is not None else TemporaryProviderKeyStore()
    checker = probe if probe is not None else probe_one
    bp = Blueprint("ob_owner_provider_api_keys", __name__)

    @bp.route(PATH, methods=["GET", "POST"])
    def provider_api_keys():
        if owner_authorize() is not True:
            abort(403)
        sid = _owner_sid()
        if not sid:
            abort(403)
        if request.method == "POST":
            hold = _form_hold()
            if hold is not None:
                return _headers(make_response(render_template(
                    "ob_provider_key_hold.html", code=hold), 403))
            if not _enabled():
                abort(403)
            provider = request.form.get("provider", "")
            operation = request.form.get("operation", "")
            if provider not in PROVIDERS or operation not in {"save", "forget", "verify"}:
                abort(400)
            if operation == "save":
                raw = request.form.get("secret", "")
                try:
                    memory.put(sid, provider, raw)
                    session["ob_provider_key_notice"] = "Key received into temporary server memory. No feed was activated."
                except ValueError:
                    session["ob_provider_key_notice"] = "Key format not accepted. Nothing was saved."
            elif operation == "forget":
                memory.forget(sid, provider)
                session["ob_provider_key_notice"] = "Temporary key discarded."
            else:
                item = memory.get(sid, provider)
                if item is None:
                    session["ob_provider_key_notice"] = "Enter a key first."
                elif item.last_checked_at and _now() - item.last_checked_at < timedelta(seconds=60):
                    session["ob_provider_key_notice"] = "Verification cooldown is active. No new request sent."
                else:
                    item.last_checked_at = _now()
                    # A provider network or parser failure is a generic hold, never
                    # an exception response containing the credential-bearing URL.
                    try:
                        item.probe = normalize_probe_code(checker(provider, item.value))
                    except Exception:
                        item.probe = "PROVIDER_MESSAGE"
                    session["ob_provider_key_notice"] = probe_message(item.probe)
            return _headers(redirect(PATH, code=303))
        return _headers(make_response(render_template(
            "ob_provider_key_desk.html", csrf=_csrf(), enabled=_enabled(),
            providers=memory.status(sid),
            notice=session.pop("ob_provider_key_notice", ""))))

    return bp


def register_provider_key_desk(app: Flask, *, owner_authorize):
    if app.extensions.get("ob_provider_key_desk_v1"):
        return app
    store = TemporaryProviderKeyStore()
    app.register_blueprint(create_provider_key_blueprint(
        owner_authorize=owner_authorize, store=store))
    @app.before_request
    def _discard_on_tower_logout():
        if request.path == "/tower/logout":
            store.forget(_owner_sid())
    # The application marker reports capabilities only; it contains NO secret
    # and cannot authorize use of a key by trading or data gateway components.
    # Server-only projection closure exposes safe status, NEVER the stored key.
    app.extensions["ob_provider_key_status_reader_v1"] = store.status
    # Trusted server-only consumer for normalized research. This closure is not
    # rendered, serialized, logged or exposed by a route; callers still need
    # current Tower owner/session authorization and independent source rights.
    app.extensions["ob_provider_key_secret_reader_v1"] = store.get
    app.extensions["ob_provider_key_desk_v1"] = {
        "path": PATH, "volatile_only": True, "secrets_in_browser": False,
        "api_authority": False, "live_feed_installed": False,
        "broker_execution": False, "providers": tuple(PROVIDERS),
    }
    return app
