"""Tower-guarded Public owner connection. No browser token, order, disk or secret DB.

The owner enters their existing key only into an HTTPS + Tower-step-up protected
POST. Exchange immediately for a 15-minute JWT and drop the long-lived key.
Only a 10-minute JWT and exact single brokerage account ID remain in process RAM,
bound to the random Tower login session ID. This is explicitly NOT persistent:
worker restart or session change needs reconnection. No Automatic Live/data gateway.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hmac
import os
import re
import secrets
from threading import RLock
from urllib.request import Request
from urllib.parse import urlsplit

from flask import Blueprint, Flask, abort, make_response, redirect, render_template, request, session, url_for

from scripts.ob_public_local_probe import _ACCOUNTS, _http, _request_json, get_short_token, ProbeHold
from engine.market_intake.public_quote_readonly import (
    PublicReadPolicy, PublicReadOnlyQuoteClient, PublicQuoteHold, QuoteRequest,
)

PATH = "/ob/data-desk/public"
_AUTH_TTL_SECONDS = 600
_MAX_CONNECTIONS = 32
_MAX_POST_BYTES = 8192
_ACCOUNT_ID = re.compile(r"^[A-Za-z0-9_-]{5,128}$")
_HOLD_MESSAGES = {
    "ACCOUNT_DISCOVERY_HOLD": "No unique eligible brokerage account was returned. No account selected.",
    "PROBE_NETWORK_OR_AUTH_HOLD": "Public rejected the authentication or network request. Check the key and Public account access.",
    "ACCESS_TOKEN_NOT_RETURNED": "Public did not return the expected access token.",
    "PROBE_INVALID_RESPONSE": "Public returned an unexpected response.",
    "PROBE_RESPONSE_TOO_LARGE": "The Public response exceeded the safety limit.",
    "SECRET_NOT_CONFIGURED": "Enter the Public key into the protected form.",
    "PUBLIC_QUOTE_UNAVAILABLE": "Public did not return a usable quote for that instrument.",
    "PUBLIC_TRANSPORT_HOLD": "Public rejected the quote request or was unavailable.",
    "PUBLIC_SCOPE_RIGHTS_HOLD": "This instrument's reviewed source rights have not been enabled.",
    "PUBLIC_REQUEST_INVALID": "The requested instrument was invalid.",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _flag(name: str) -> bool:
    return os.environ.get(name) == "1"


def _quote_policy() -> PublicReadPolicy:
    return PublicReadPolicy(
        account_scope_reviewed=_flag("OB_PUBLIC_ACCOUNT_SCOPE_REVIEWED"),
        non_display_use_reviewed=_flag("OB_PUBLIC_NONDISPLAY_REVIEWED"),
        owner_display_reviewed=_flag("OB_PUBLIC_OWNER_DISPLAY_REVIEWED"),
        marketdata_scope_verified=_flag("OB_PUBLIC_MARKETDATA_SCOPE_VERIFIED"),
        equity_entitled=_flag("OB_PUBLIC_EQUITY_ENTITLED"),
        option_entitled=_flag("OB_PUBLIC_OPTION_ENTITLED"),
    )


@dataclass
class _Connection:
    access_token: str
    account_id: str
    expires_at: datetime
    account_kind: str = "BROKERAGE"
    last_quote: dict | None = None


class OwnerConnectionStore:
    """Short-lived, per-worker, session-bound bearer only; NEVER secret key."""
    def __init__(self):
        self._lock = RLock()
        self._items: dict[str, _Connection] = {}

    def _prune(self):
        now = _now()
        for key, item in tuple(self._items.items()):
            if item.expires_at <= now:
                self._items.pop(key, None)

    def get(self, session_id: str) -> _Connection | None:
        if not isinstance(session_id, str) or not session_id.startswith("tower_session_"):
            return None
        with self._lock:
            self._prune()
            return self._items.get(session_id)

    def put(self, session_id: str, item: _Connection) -> None:
        if not isinstance(session_id, str) or not session_id.startswith("tower_session_"):
            raise ProbeHold("OWNER_SESSION_BINDING_HOLD")
        with self._lock:
            self._prune()
            if session_id not in self._items and len(self._items) >= _MAX_CONNECTIONS:
                raise ProbeHold("OWNER_CONNECTION_CAPACITY_HOLD")
            self._items[session_id] = item

    def drop(self, session_id: str) -> None:
        with self._lock:
            self._items.pop(session_id, None)


def _owner_sid() -> str:
    val = session.get("tower_session_id")
    return val if isinstance(val, str) and val.startswith("tower_session_") and len(val) < 150 else ""


def _csrf() -> str:
    val = session.get("ob_public_owner_csrf")
    if not isinstance(val, str) or len(val) < 30:
        val = secrets.token_urlsafe(32)
        session["ob_public_owner_csrf"] = val
    return val


# Only fixed, non-sensitive reason codes may be returned to the browser.
_FORM_HOLDS = {
    "OWNER_GATE_HOLD": "Tower could not verify the current owner access. Return to Tower, sign in and relaunch OB.",
    "SESSION_GATE_HOLD": "Your Tower login session has changed. Sign in again and open the connection from OB.",
    "BODY_SIZE_HOLD": "The submitted form was missing or exceeded the permitted size. Reopen the connection form.",
    "FORM_TYPE_HOLD": "This action needs the protected browser form. Reopen the connection page.",
    "ORIGIN_HOLD": "The browser's HTTPS origin could not be verified. Reopen the form from the Tower HTTPS address.",
    "BROWSER_SITE_HOLD": "This request did not originate from the protected Tower page.",
    "CSRF_HOLD": "Your form security token expired or changed. Reopen the connection page before resubmitting.",
    "CONNECT_DISABLED_HOLD": "The owner connection feature is not enabled for this Tower service.",
}


def _post_hold_reason() -> str | None:
    """Return only a stable rejection reason. NEVER inspect or echo the secret.

    Modern browsers usually send an Origin on a same-origin POST, but privacy
    configurations may omit it. When absent, require affirmative browser
    same-origin navigation metadata AND the session-bound CSRF token. Never
    allow an explicitly mismatched/non-HTTPS Origin or cross-site Fetch metadata.
    """
    if request.content_length is None or request.content_length > _MAX_POST_BYTES:
        return "BODY_SIZE_HOLD"
    if request.mimetype != "application/x-www-form-urlencoded":
        return "FORM_TYPE_HOLD"
    fetch_site = request.headers.get("Sec-Fetch-Site", "").lower()
    if fetch_site not in {"", "same-origin", "none"}:
        return "BROWSER_SITE_HOLD"
    origin = request.headers.get("Origin", "").strip()
    if origin:
        parsed = urlsplit(origin)
        approved_hosts = {request.host.lower()}
        render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").lower().strip()
        if render_hostname:
            approved_hosts.add(render_hostname)
        if (parsed.scheme != "https" or not parsed.netloc
                or parsed.netloc.lower() not in approved_hosts
                or parsed.username is not None or parsed.password is not None
                or parsed.path or parsed.query or parsed.fragment):
            return "ORIGIN_HOLD"
    else:
        # Explicit same-origin browser navigation is required when Origin is
        # missing. Missing Fetch metadata must not become a permissive fallback.
        if (fetch_site != "same-origin"
                or request.headers.get("Sec-Fetch-Mode", "").lower() != "navigate"):
            return "ORIGIN_HOLD"
    submitted = request.form.get("csrf", "")
    if not isinstance(submitted, str) or not hmac.compare_digest(_csrf(), submitted):
        return "CSRF_HOLD"
    return None


def _post_rejected(code: str):
    # Fixed status and message, never submitted values, credentials or tokens.
    response = make_response(render_template(
        "ob_public_owner_hold.html",
        hold_code=code,
        hold_message=_FORM_HOLDS.get(code, "Connection not attempted. Reopen Tower."),
    ), 403)
    return _headers(response)


def _discover_single_brokerage(token: str, opener) -> str:
    req = Request(_ACCOUNTS, method="GET",
                  headers={"Accept": "application/json",
                           "Authorization": "Bearer " + token})
    payload = _request_json(opener, req)
    rows = payload.get("accounts") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or len(rows) > 20:
        raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
    accounts = [
        x.get("accountId") for x in rows if isinstance(x, dict)
        and x.get("accountType") == "BROKERAGE"
        and isinstance(x.get("accountId"), str)
        and _ACCOUNT_ID.fullmatch(x["accountId"])
    ]
    # No arbitrary first-account choice, and no exposure of account identifiers.
    if len(accounts) != 1:
        raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
    return accounts[0]


def _headers(response):
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = ("default-src 'none'; style-src 'self'; "
                                                  "form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
    return response


def create_public_owner_blueprint(*, owner_authorize, opener=None, store=None):
    if not callable(owner_authorize):
        raise ValueError("independent Tower owner/step-up/OB authority required")
    request_opener = opener or _http
    vault = store if store is not None else OwnerConnectionStore()
    bp = Blueprint("ob_public_owner_connection", __name__)

    @bp.route(PATH, methods=["GET", "POST"])
    def owner_public_connection():
        if owner_authorize() is not True:
            if request.method == "POST":
                return _post_rejected("OWNER_GATE_HOLD")
            abort(403)
        sid = _owner_sid()
        if not sid:
            if request.method == "POST":
                return _post_rejected("SESSION_GATE_HOLD")
            abort(403)
        if request.method == "POST":
            hold_reason = _post_hold_reason()
            if hold_reason is not None:
                return _post_rejected(hold_reason)
            if not _flag("OB_PUBLIC_OWNER_CONNECT_ENABLED"):
                return _post_rejected("CONNECT_DISABLED_HOLD")
            operation = request.form.get("operation")
            # No secret included in URL, output, session cookie, flash, DB or logs.
            if operation == "disconnect":
                vault.drop(sid)
                session["ob_public_owner_notice"] = "Disconnected. The short-lived token was discarded."
            elif operation == "connect":
                vault.drop(sid)
                raw = request.form.get("secret", "")
                if not isinstance(raw, str) or len(raw) < 10 or len(raw) > 4096:
                    session["ob_public_owner_notice"] = _HOLD_MESSAGES["SECRET_NOT_CONFIGURED"]
                else:
                    try:
                        token = get_short_token(raw, opener=request_opener)
                        # Do not hold a long-lived secret in the session store.
                        account_id = _discover_single_brokerage(token, request_opener)
                        vault.put(sid, _Connection(token, account_id,
                                                  _now() + timedelta(seconds=_AUTH_TTL_SECONDS)))
                        session["ob_public_owner_notice"] = (
                            "Public authenticated. One brokerage account verified. Temporary connection only."
                        )
                    except (ProbeHold, PublicQuoteHold) as exc:
                        vault.drop(sid)
                        session["ob_public_owner_notice"] = _HOLD_MESSAGES.get(str(exc),
                                                       "Connection held. Nothing was activated.")
            elif operation == "quote":
                item = vault.get(sid)
                kind = request.form.get("kind")
                symbol = request.form.get("symbol", "").strip().upper()[:26]
                policy = _quote_policy()
                if item is None:
                    session["ob_public_owner_notice"] = "Connection expired; connect again."
                elif not policy.permits({kind}):
                    session["ob_public_owner_notice"] = "Quote held: separate business data-use, display and instrument permissions must be reviewed."
                else:
                    try:
                        q = QuoteRequest(symbol=symbol, kind=kind)
                        result = PublicReadOnlyQuoteClient(policy, opener=request_opener).fetch_once(
                            backend_account_id=item.account_id,
                            backend_access_token=item.access_token, requests=[q])[0]
                        age = (_now() - min(result.last_timestamp, result.bid_timestamp,
                                             result.ask_timestamp)).total_seconds()
                        # Source-only: never install in the gateway or imply live entitlement.
                        item.last_quote = {
                            "kind": result.kind, "symbol": symbol,
                            "bid": result.normalized["bid"], "ask": result.normalized["ask"],
                            "last": result.normalized.get("last"),
                            "observed_at": result.normalized["observed_at"],
                            "age_seconds": max(0, round(age, 1)),
                            "fresh_within_5_seconds": 0 <= age <= 5,
                            "source_only": True, "not_a_trading_signal": True,
                        }
                        session["ob_public_owner_notice"] = "One source-bound quote checked; not installed as a live OB feed."
                    except (ValueError, PublicQuoteHold) as exc:
                        item.last_quote = None
                        session["ob_public_owner_notice"] = _HOLD_MESSAGES.get(str(exc),
                                                       "Quote could not be verified. No fallback used.")
            else:
                abort(400)
            return _headers(redirect(PATH, code=303))
        item = vault.get(sid)
        rights = _quote_policy()
        visible_quote = (
            item.last_quote if item and item.last_quote
            and rights.permits({item.last_quote["kind"]}) else None
        )
        response = make_response(render_template(
            "ob_public_owner_connection.html",
            csrf=_csrf(),
            connect_enabled=_flag("OB_PUBLIC_OWNER_CONNECT_ENABLED"),
            is_connected=item is not None,
            expires_at=item.expires_at.isoformat() if item else None,
            equity_ready=rights.permits({"EQUITY"}),
            option_ready=rights.permits({"OPTION"}),
            quote=visible_quote,
            notice=session.pop("ob_public_owner_notice", ""),
        ))
        return _headers(response)

    return bp


def register_public_owner_connection(app: Flask, *, owner_authorize):
    if app.extensions.get("ob_public_owner_connection_v1"):
        return app
    store = OwnerConnectionStore()
    app.register_blueprint(create_public_owner_blueprint(
        owner_authorize=owner_authorize, store=store,
    ))

    @app.before_request
    def _public_owner_drop_token_on_tower_logout():
        # Runs before the canonical Tower logout view clears its session.
        if request.path == "/tower/logout":
            store.drop(_owner_sid())

    app.extensions["ob_public_owner_connection_v1"] = {
        "path": PATH, "api_key_persisted": False, "bearer_in_cookie": False,
        "in_process_token_seconds": _AUTH_TTL_SECONDS, "broker_execution": False,
        "auto_connection": False, "gateway_installation": False,
    }
    return app
