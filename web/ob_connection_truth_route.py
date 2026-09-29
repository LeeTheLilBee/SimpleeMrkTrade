"""Exact Tower owner-only *status*, not a provider-data or credential export.

This projection never calls a vendor, reads raw keys/tokens, fetches positions,
infers rights from authentication, or promotes source research to market prices.
The same-session provider readers return narrow, pre-sanitized boolean/status
records only. An unavailable worker/status reader fails closed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from flask import Blueprint, abort, jsonify, make_response

from engine.market_intake.keyless_public_context import (
    edgar_delegated_from_environment, enabled_sources_from_environment,
)
from tower.ob_public_owner_connection import _owner_sid
from tower.ob_provider_soulaana_status import build_soulaana_provider_status

PATH = "/ob/data-desk/connections.json"
KEY_PROVIDER_IDS = ("finnhub", "alpha_vantage")
KEYLESS_PROVIDER_IDS = ("bls", "treasury", "openfigi")
SAFE_PROBE = frozenset(("NOT_TESTED", "NOT_CONFIGURED",
                        "READ_ONLY_CHECK_PASSED", "VERIFY_HOLD"))


def connection_status_projection(*, sid: str, key_reader: Callable,
                                 public_reader: Callable) -> dict:
    """One read-only owner-session projection; no raw third-party response."""
    if not isinstance(sid, str) or not sid.startswith("tower_session_") or len(sid) >= 150:
        raise ValueError("valid current Tower owner session required")
    keys = key_reader(sid)
    public = public_reader(sid)
    if not isinstance(keys, (list, tuple)) or not isinstance(public, dict):
        raise ValueError("current provider status unavailable")

    entries = {}
    for row in keys:
        if not isinstance(row, dict) or row.get("id") not in KEY_PROVIDER_IDS:
            raise ValueError("unrecognized provider status record")
        provider = row["id"]
        if provider in entries or type(row.get("present")) is not bool:
            raise ValueError("duplicate or malformed provider status")
        probe = row.get("probe")
        if probe not in SAFE_PROBE:
            raise ValueError("unrecognized verification status")
        present = row["present"]
        if not present and probe != "NOT_CONFIGURED":
            raise ValueError("unlinked provider probe status")
        entries[provider] = {
            "provider": provider,
            "state": (
                "READ_ONLY_CHECK_PASSED" if present and probe == "READ_ONLY_CHECK_PASSED"
                else "TEMPORARY_KEY_RECEIVED" if present
                else "NOT_CONFIGURED"
            ),
            "read_only_probe": probe,
            "account_linked": None,
            "source_use_rights_verified": False,
            "data_display_rights_verified": False,
            "quote_feed_activated": False,
        }
    if set(entries) != set(KEY_PROVIDER_IDS):
        raise ValueError("provider status set incomplete")
    if any(type(public.get(k)) is not bool for k in (
        "authentication_temporarily_present", "account_linked",
        "owner_selection_required"
    )):
        raise ValueError("Public session status unavailable")
    if public["account_linked"] and not public["authentication_temporarily_present"]:
        raise ValueError("Public linkage cannot outlive its temporary auth")
    if public["account_linked"] and public["owner_selection_required"]:
        raise ValueError("Public owner selection/linkage contradiction")
    entries["public"] = {
        "provider": "public",
        "state": (
            "TEMPORARY_ACCOUNT_LINK_VERIFIED" if public["account_linked"]
            else "OWNER_SELECTION_REQUIRED" if public["owner_selection_required"]
            else "TEMPORARY_AUTH_ONLY" if public["authentication_temporarily_present"]
            else "NO_VERIFIED_ACCOUNT_LINK"
        ),
        "account_linked": public["account_linked"],
        "read_only_probe": "NOT_APPLICABLE",
        "source_use_rights_verified": False,
        "data_display_rights_verified": False,
        "quote_feed_activated": False,
    }
    enabled = enabled_sources_from_environment()
    for source in KEYLESS_PROVIDER_IDS:
        entries[source] = {
            "provider": source,
            "state": "USE_AND_OWNER_DISPLAY_CONFIGURED" if source in enabled else "RIGHTS_REVIEW_HOLD",
            "reference_only": True,
            "provider_request_made": False,
            "current_data_accepted": False,
            "quote_feed_activated": False,
            "ai_use_authorized": False,
        }
    entries["sec"] = {
        "provider": "sec",
        "state": "SEPARATE_ISSUER_RESEARCH_CONFIGURED" if edgar_delegated_from_environment()
                 else "RIGHTS_REVIEW_HOLD",
        "reference_only": True, "provider_request_made": False,
        "current_data_accepted": False, "quote_feed_activated": False,
        "ai_use_authorized": False,
    }
    result = {
        "schema": "OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1",
        "as_of": datetime.now(timezone.utc).isoformat(),
        "owner_session_checked": True,
        "source_only": True,
        "provider_status": [entries[k] for k in (
            "public", "finnhub", "alpha_vantage", "sec", "bls", "treasury", "openfigi"
        )],
        "real_market_feed_attached_by_this_route": False,
        "prices_attached": False,
        "positions_attached": False,
        "live_feed_count_verified": None,
        "no_browser_provider_credentials": True,
        "may_authorize_order": False,
        "may_authorize_capital": False,
        "may_change_trading_mode": False,
        "dissemination_contract": "OWNER_STATUS_ONLY",
    }
    result["soulaana_provider_status"] = build_soulaana_provider_status(result)
    return result


def create_connection_truth_blueprint(*, owner_authorize, key_reader, public_reader):
    if not all(callable(item) for item in (owner_authorize, key_reader, public_reader)):
        raise ValueError("independent current Tower auth and safe readers required")
    bp = Blueprint("ob_tower_provider_connection_truth", __name__)

    @bp.route(PATH, methods=["GET"])
    def owner_connection_truth():
        if owner_authorize() is not True:
            abort(403)
        sid = _owner_sid()
        if not sid:
            abort(403)
        try:
            payload = connection_status_projection(
                sid=sid, key_reader=key_reader, public_reader=public_reader
            )
        except Exception:
            abort(503)
        response = make_response(jsonify(payload))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Cookie"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    return bp
