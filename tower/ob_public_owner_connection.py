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
    "ACCOUNT_DISCOVERY_HOLD": "Public's account list had an unexpected structure. No account selected.",
    "ACCOUNT_LIST_EMPTY_HOLD": "Authentication succeeded, but Public returned an empty account list for this access token. Confirm the account is open and approved and that the API key belongs to the correct Public profile. If it is, ask Public Support to check API account linkage. No account was selected.",
    "ACCOUNT_TYPE_HOLD": "Public accepted authentication and returned accounts, but none has a recognized brokerage, entity or joint account type. No account selected.",
    "ACCOUNT_SELECTION_HOLD": "Select one account from the protected list; no account was selected.",
    "ACCOUNT_SELECTION_EXPIRED_HOLD": "Account selection expired. Connect again using the protected Tower form.",
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
    account_kind: str = "UNSELECTED"
    candidates: tuple[tuple[str, str], ...] = ()
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
    "ORIGIN_HOLD": "The request did not match the Tower HTTPS connection address. Your key was not submitted to Public.",
    "ORIGIN_CONFIG_HOLD": "The Tower service is missing its approved public HTTPS address. Connection is disabled until corrected.",
    "ORIGIN_OPAQUE_HOLD": "The browser sent an opaque Origin. Open the actual Tower HTTPS page directly, not an embedded preview.",
    "ORIGIN_SCHEME_HOLD": "The browser did not send a clean HTTPS Origin. Connection is held.",
    "ORIGIN_EXPECTED_HOST_HOLD": "The browser and Tower service disagreed on the approved site address. Connection is held.",
    "ORIGIN_META_HOLD": "The browser did not supply enough same-origin navigation evidence. Connection is held.",
    "BROWSER_SITE_HOLD": "This request did not originate from the protected Tower page.",
    "CSRF_HOLD": "Your form security token expired or changed. Reopen the connection page before resubmitting.",
    "CONNECT_DISABLED_HOLD": "The owner connection feature is not enabled for this Tower service.",
}


def _approved_browser_origin() -> str:
    """A concrete external HTTPS origin. Never rely on Render's internal Host.

    Each existing Tower service configures its own exact public origin in the
    OB_PUBLIC_OWNER_CANONICAL_ORIGIN environment variable. In local/isolated
    synthetic tests only, request.host is used when no Render identity exists.
    """
    configured = os.environ.get("OB_PUBLIC_OWNER_CANONICAL_ORIGIN", "").strip().lower()
    if configured:
        try:
            parsed = urlsplit(configured)
            if (parsed.scheme == "https" and parsed.hostname
                    and parsed.port is None
                    and parsed.username is None and parsed.password is None
                    and not parsed.path and not parsed.query and not parsed.fragment
                    and parsed.netloc == parsed.hostname):
                return configured
        except ValueError:
            pass
        return ""
    # Hosted services must never guess whether a reverse-proxy internal Host
    # is the public URL.
    if os.environ.get("RENDER_SERVICE_ID") or os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
        return ""
    return "https://" + request.host.lower()


def _post_hold_reason() -> str | None:
    """Form gate: exact service-owned HTTPS origin, Fetch metadata, and CSRF.

    Do not echo or log Origin strings, user tokens, session cookies or the API
    secret. Render reverse proxies may have an internal request.host: compare
    the browser against the explicitly configured external HTTPS URL instead.
    """
    if request.content_length is None or request.content_length > _MAX_POST_BYTES:
        return "BODY_SIZE_HOLD"
    if request.mimetype != "application/x-www-form-urlencoded":
        return "FORM_TYPE_HOLD"

    expected = _approved_browser_origin()
    if not expected:
        return "ORIGIN_CONFIG_HOLD"
    fetch_site = request.headers.get("Sec-Fetch-Site", "").strip().lower()
    if fetch_site not in {"", "same-origin", "none"}:
        return "BROWSER_SITE_HOLD"

    origin = request.headers.get("Origin", "").strip().lower()
    if origin:
        if origin == "null":
            return "ORIGIN_OPAQUE_HOLD"
        try:
            parsed = urlsplit(origin)
            if (parsed.scheme != "https" or parsed.username is not None
                    or parsed.password is not None or parsed.path or parsed.query
                    or parsed.fragment or parsed.port not in {None, 443}):
                return "ORIGIN_SCHEME_HOLD"
        except ValueError:
            return "ORIGIN_SCHEME_HOLD"
        if parsed.netloc.lower().removesuffix(":443") != urlsplit(expected).netloc:
            return "ORIGIN_EXPECTED_HOST_HOLD"
    else:
        # A privacy-filtered browser can omit Origin or Sec-Fetch-Mode.
        # Require affirmative SAME-ORIGIN browser site metadata and the
        # independent signed Tower-session CSRF token. Missing or same-site
        # metadata is NOT enough. POST remains an exact protected route.
        if fetch_site != "same-origin":
            return "ORIGIN_META_HOLD"

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


_SELECTABLE_ACCOUNT_TYPES = frozenset({"BROKERAGE", "ENTITY", "JOINT"})


def _discover_accounts(token: str, opener) -> tuple[tuple[str, str], ...]:
    """Read Public's documented account-list response, never account balances.

    Business entities may be returned as ENTITY, not necessarily BROKERAGE.
    If multiple eligible accounts exist, return all for an *owner-selected*
    server-memory ordinal; never pick the first silently. No identifiers or
    raw provider bodies reach logs, HTML, browser cookies or generic errors.
    """
    req = Request(_ACCOUNTS, method="GET",
                  headers={"Accept": "application/json",
                           "Content-Type": "application/json",
                           "Authorization": "Bearer " + token})
    payload = _request_json(opener, req)
    rows = payload.get("accounts") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or len(rows) > 20:
        raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
    if not rows:
        raise ProbeHold("ACCOUNT_LIST_EMPTY_HOLD")
    seen = set()
    candidates = []
    for row in rows:
        if not isinstance(row, dict):
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        identifier, kind = row.get("accountId"), row.get("accountType")
        if not isinstance(identifier, str) or not _ACCOUNT_ID.fullmatch(identifier):
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        if identifier in seen:
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        seen.add(identifier)
        if not isinstance(kind, str) or len(kind) > 40:
            raise ProbeHold("ACCOUNT_DISCOVERY_HOLD")
        if kind in _SELECTABLE_ACCOUNT_TYPES:
            candidates.append((identifier, kind))
    if not candidates:
        raise ProbeHold("ACCOUNT_TYPE_HOLD")
    return tuple(candidates)


def _public_selection_view(record: _Connection | None) -> tuple[dict, ...]:
    if not record or record.account_id or not record.candidates:
        return ()
    return tuple({
        "index": index,
        "kind": kind,
        # A short suffix makes same-type accounts distinguishable without
        # exposing full accountId or account numbers.
        "hint": "\u2022\u2022\u2022\u2022" + identifier[-4:],
    } for index, (identifier, kind) in enumerate(record.candidates, 1))


def _headers(response):
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    # Important: no-referrer causes browsers to serialize Origin: null on
    # same-origin HTML form POSTs. Our exact HTTPS Origin gate must see the
    # real source, not a privacy-policy-induced opaque value. same-origin
    # sends referrer only within this Tower origin and never cross-site.
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = ("default-src 'none'; style-src 'self'; "
                                                  "form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
    return response


def create_public_owner_blueprint(*, owner_authorize, opener=None, store=None, desk_return_path=None):
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
                        accounts = _discover_accounts(token, request_opener)
                        connection = _Connection(
                            token, "", _now() + timedelta(seconds=_AUTH_TTL_SECONDS),
                            candidates=accounts,
                        )
                        if len(accounts) == 1:
                            connection.account_id, connection.account_kind = accounts[0]
                            connection.candidates = ()
                            session["ob_public_owner_notice"] = (
                                "Public authenticated. One " + connection.account_kind
                                + " account selected for temporary source-only API checks."
                            )
                        else:
                            session["ob_public_owner_notice"] = (
                                "Public authenticated. Choose one of " + str(len(accounts))
                                + " accounts below; nothing has been selected yet."
                            )
                        vault.put(sid, connection)
                    except (ProbeHold, PublicQuoteHold) as exc:
                        vault.drop(sid)
                        session["ob_public_owner_notice"] = _HOLD_MESSAGES.get(str(exc),
                                                       "Connection held. Nothing was activated.")
            elif operation == "select":
                item = vault.get(sid)
                selected = request.form.get("account_index", "")
                if (item is None or item.account_id or not item.candidates
                        or not isinstance(selected, str)
                        or not re.fullmatch(r"[1-9][0-9]?", selected)
                        or int(selected) > len(item.candidates)):
                    session["ob_public_owner_notice"] = _HOLD_MESSAGES["ACCOUNT_SELECTION_EXPIRED_HOLD"]
                else:
                    item.account_id, item.account_kind = item.candidates[int(selected) - 1]
                    item.candidates = ()
                    item.last_quote = None
                    session["ob_public_owner_notice"] = (
                        "Selected " + item.account_kind
                        + " account. Temporary authentication established; market-data permissions remain separate."
                    )
            elif operation == "quote":
                item = vault.get(sid)
                kind = request.form.get("kind")
                symbol = request.form.get("symbol", "").strip().upper()[:26]
                policy = _quote_policy()
                if item is None:
                    session["ob_public_owner_notice"] = "Connection expired; connect again."
                elif not item.account_id or item.account_kind not in _SELECTABLE_ACCOUNT_TYPES:
                    session["ob_public_owner_notice"] = "Choose an account before checking quotes."
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
            return _headers(redirect(desk_return_path or PATH, code=303))
        if desk_return_path:
            return _headers(redirect(desk_return_path, code=303))
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
            is_connected=bool(item and item.account_id),
            selection_options=_public_selection_view(item),
            selected_account_kind=item.account_kind if item and item.account_id else None,
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
        desk_return_path="/ob/data-desk#provider-connections",
    ))

    @app.before_request
    def _public_owner_drop_token_on_tower_logout():
        # Runs before the canonical Tower logout view clears its session.
        if request.path == "/tower/logout":
            store.drop(_owner_sid())

    # No credential or account ID is included in this read-only owner status.
    # Empty account discovery cannot be mistaken for a connected account.
    def _safe_owner_connection_status(sid):
        item = store.get(sid)
        return {
            "authentication_temporarily_present": item is not None,
            "account_linked": bool(item is not None and item.account_id),
            "owner_selection_required": bool(item is not None and item.candidates and not item.account_id),
        }

    app.extensions["ob_public_owner_status_reader_v1"] = _safe_owner_connection_status

    def _safe_owner_connection_ui():
        sid = _owner_sid()
        item = store.get(sid) if sid else None
        rights = _quote_policy()
        visible_quote = (
            item.last_quote if item and item.last_quote
            and rights.permits({item.last_quote["kind"]}) else None
        )
        return {
            "csrf": _csrf() if sid else "",
            "connect_enabled": _flag("OB_PUBLIC_OWNER_CONNECT_ENABLED"),
            "is_connected": bool(item and item.account_id),
            "selection_options": _public_selection_view(item),
            "selected_account_kind": item.account_kind if item and item.account_id else None,
            "expires_at": item.expires_at.isoformat() if item else None,
            "equity_ready": rights.permits({"EQUITY"}),
            "option_ready": rights.permits({"OPTION"}),
            "quote": visible_quote,
            "notice": session.pop("ob_public_owner_notice", ""),
        }
    app.extensions["ob_public_owner_ui_reader_v1"] = _safe_owner_connection_ui
    app.extensions["ob_public_owner_connection_v1"] = {
        "path": PATH, "api_key_persisted": False, "bearer_in_cookie": False,
        "in_process_token_seconds": _AUTH_TTL_SECONDS, "broker_execution": False,
        "auto_connection": False, "gateway_installation": False,
    }
    return app
