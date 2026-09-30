"""Mountable, exact protected OB Market Data Desk route — NOT registered by default.

Only the authorized Tower/OB web integration may register this blueprint after
mapping /ob/data-desk to a normal owner-only read route. No wildcard corridor.
The injection callbacks must be trusted backend functions; no client-supplied
approval flags, cookies decoded by this module, or market-data network calls.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from flask import Blueprint, abort, make_response, render_template

_EXPECTED = {"schema", "as_of", "read_only", "source_only", "runtime_health_attached",
             "prices_attached", "connection_truth", "providers", "cases", "summary",
             "traffic", "soulaana", "safety"}
_PROVIDER = {"product_key", "company", "instrument", "quote_kind",
             "current_quote_eligible_if_entitled", "state"}
_CASE = {"case_id", "product_key", "state", "reason", "audit_count", "last_receipt",
         "live_data_connected", "trading_authorized"}


def _valid(snapshot: object) -> bool:
    """Never place an arbitrary provider payload or secret in embedded page JSON."""
    if not isinstance(snapshot, dict) or set(snapshot) != _EXPECTED:
        return False
    if (snapshot.get("schema") != "OB_MARKET_DATA_DESK_V1" or
        snapshot.get("read_only") is not True or snapshot.get("source_only") is not True or
        snapshot.get("prices_attached") is not False or
        snapshot.get("runtime_health_attached") is not False or
        snapshot.get("connection_truth") != "UNVERIFIED"):
        return False
    providers, cases = snapshot.get("providers"), snapshot.get("cases")
    if not isinstance(providers, list) or not isinstance(cases, list) or len(providers)>200 or len(cases)>200:
        return False
    if not all(isinstance(x, dict) and set(x) == _PROVIDER for x in providers):
        return False
    if not all(isinstance(x, dict) and set(x) == _CASE for x in cases):
        return False
    safe = snapshot.get("safety")
    if not isinstance(safe, dict) or safe != {
        "can_approve_in_browser": False, "can_execute": False,
        "manual_live_unlocked": False, "invitee_prices_visible": False,
    }:
        return False
    summary, traffic, soulaana = (snapshot.get("summary"), snapshot.get("traffic"),
                                  snapshot.get("soulaana"))
    if not all(isinstance(x, dict) for x in (summary, traffic, soulaana)):
        return False
    if set(summary) != {"catalog_products", "onboarding_cases", "actions_needing_review",
                        "live_feeds_verified", "api_requests_remaining", "live_option_feeds_verified"}:
        return False
    if any(summary[key] is not None for key in ("live_feeds_verified", "api_requests_remaining",
                                               "live_option_feeds_verified")):
        return False
    if set(traffic) != {"state", "verified_usage", "provider_quotas", "streams"} or (
            traffic["state"] != "NOT_CONNECTED" or any(traffic[key] is not None for key in (
                "verified_usage", "provider_quotas", "streams"))):
        return False
    if set(soulaana) != {"headline", "meaning", "needs_owner", "next_step"} or any(
            not isinstance(value, str) or len(value) > 500 for value in soulaana.values()):
        return False
    if any(type(summary[key]) is not int or summary[key] < 0 for key in (
            "catalog_products", "onboarding_cases", "actions_needing_review")):
        return False
    if any(not isinstance(p["product_key"], str) or len(p["product_key"]) > 100 or
           not isinstance(p["company"], str) or len(p["company"]) > 100 for p in providers):
        return False
    if any(not isinstance(c["reason"], str) or len(c["reason"]) > 200 or
           c["trading_authorized"] is not False or c["live_data_connected"] is not False
           for c in cases):
        return False
    return True


def create_market_data_desk_blueprint(
    *, tower_owner_authorize: Callable[[], bool],
    protected_snapshot: Callable[[], dict],
    connection_ui_state: Callable[[], dict] | None = None,
) -> Blueprint:
    """Default deny; caller must supply exact Tower owner/session/step-up decision.

    This factory intentionally does not register itself. Tower must separately
    approve the exact route, handler binding and owner access in its allowlist.
    """
    if not callable(tower_owner_authorize) or not callable(protected_snapshot):
        raise ValueError("explicit trusted Tower authorizer and snapshot required")

    bp = Blueprint("ob_market_data_desk", __name__)

    @bp.route("/ob/data-desk", methods=["GET"])
    def owner_market_data_desk():
        # Identity, session, fresh step-up, Tower OB admission and revocation
        # are the responsibility of the injected authoritative guard. Its
        # decision must be literal True, not a truthy user-supplied object.
        if tower_owner_authorize() is not True:
            abort(403)
        try:
            snapshot = protected_snapshot()
        except Exception:
            # Provider failures must never leak credentials or convert the
            # protected Desk into an unverified browser/catalog fallback.
            abort(503)
        if not _valid(snapshot):
            abort(503)
        connection_state = connection_ui_state() if connection_ui_state else {}
        if not isinstance(connection_state, dict):
            abort(503)
        response = make_response(render_template(
            "market_data_desk.html",
            data_desk_snapshot=snapshot,
            data_desk_route_enabled=True,
            connection_state=connection_state,
        ))
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    return bp
