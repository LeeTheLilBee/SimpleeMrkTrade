"""Hosted Observatory's explicit provider-not-configured source response.

The historical OB V25 Flask handler synthesizes market attention, fake position
previews and a Manual Live queue from static market_universe.json. It has no
source/as-of quote provenance. Do not let newly opened Tower data corridor
silently publish those examples as authoritative market data.

This narrow replacement is deliberately separate from the 2.8MB historical
web.app module; it replaces only the existing exact read-only endpoint on the
hosted Tower instance. An approved quote-provider integration will replace this
status contract in a separately reviewed source authority PR.
"""
from __future__ import annotations

from flask import jsonify

FEED_PATH = "/ob/engine-feed-snapshot.json"
FEED_ENDPOINT = "ob_engine_feed_snapshot_v25"
VERSION = "OBDATA009_HOSTED_PROVIDER_NOT_CONFIGURED"
NO_PROVIDER_REASON = (
    "A current, authorized market-data source has not been connected to the "
    "hosted Observatory. Its old market-universe file is discovery/test "
    "membership, not a quote provider. Survey/Paper market values will remain "
    "unavailable until a source with valid as-of and usage permissions is attached."
)


def pending_provider_document() -> dict:
    """No fabricated positions, opportunities, option contracts, or market score."""
    return {
        "version": VERSION,
        "market_data_state": "provider_not_configured",
        "source": None,
        "as_of": None,
        "source_identified": False,
        "timestamp_identified": False,
        "current_eligible": False,
        "display_eligible": False,
        "reason": NO_PROVIDER_REASON,
        "market_health": {},
        "sectors": [],
        "symbols": [],
        "signals": [],
        "options": [],
        "options_projection": {},
        "research_contracts": [],
        "ranked_contracts": [],
        "positions": [],
        "positions_preview": [],
        "candidates": [],
        "candidates_preview": [],
        "manual_live_queue": [],
        "review_summary": {},
        "provider_boundary": {
            "authorized_feed_connected": False,
            "historical_seed_universe_quarantined": True,
            "explicit_source_and_as_of_required": True,
            "public_market_data_license_verified": False,
            "actual_broker_positions_available": False,
            "status_only": True,
        },
        "tower_boundaries": {
            "private_beta_only": True,
            "no_broker_api": True,
            "no_order_submission": True,
            "no_capital_movement": True,
            "no_auto_execution": True,
            "live_auto_locked": True,
        },
    }


def register_hosted_ob_market_source_status(app):
    """Override only an existing canonical endpoint; never create a public alias."""
    marker = "_tower_ob_provider_pending_status_registered"
    if app.extensions.get(marker):
        return app
    rules = [r for r in app.url_map.iter_rules() if r.rule == FEED_PATH]
    if len(rules) != 1 or rules[0].endpoint != FEED_ENDPOINT or "GET" not in rules[0].methods:
        raise RuntimeError("Expected exact existing protected OB feed endpoint unavailable")
    if not callable(app.view_functions.get(FEED_ENDPOINT)):
        raise RuntimeError("Existing OB feed handler unavailable")
    app.extensions["ob_old_seed_only_feed_handler_preserved_for_audit"] = app.view_functions[FEED_ENDPOINT]

    def hosted_source_status():
        response = jsonify(pending_provider_document())
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Cookie"
        response.headers["X-OB-Market-Source-State"] = "provider-not-configured"
        return response

    app.view_functions[FEED_ENDPOINT] = hosted_source_status
    app.extensions[marker] = True
    return app
