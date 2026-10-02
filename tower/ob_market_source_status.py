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

from tower.ob_public_owner_connection import _owner_sid
from tower.ob_soulaana_autonomous_market_research import (
    autonomous_dashboard_projection, resolve_credential,
)
from tower.ob_alpaca_iex_stream import stream_manager

FEED_PATH = "/ob/engine-feed-snapshot.json"
FEED_ENDPOINT = "ob_engine_feed_snapshot_v25"
VERSION = "OBDATA009_HOSTED_PROVIDER_NOT_CONFIGURED"
NO_PROVIDER_REASON = (
    "A current, authorized market-data source has not been connected to the "
    "hosted Observatory. Its old market-universe file is discovery/test "
    "membership, not a quote provider. Survey/Paper market values will remain "
    "unavailable until a source with valid as-of and usage permissions is attached."
)


def _midpoint(bid, ask, last=None):
    if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) and bid > 0 and ask > 0:
        return (float(bid) + float(ask)) / 2.0
    if isinstance(last, (int, float)) and last > 0:
        return float(last)
    return None


def _canonical_public_option_contracts(options, symbol):
    """Convert reviewed Public option rows into the existing web research contract shape."""
    if not isinstance(options, dict):
        return []
    expiration = options.get("expiration")
    source_reference = options.get("source_reference")
    rows = options.get("contracts")
    if not isinstance(rows, list):
        return []

    normalized = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        provider_symbol = raw.get("provider_symbol")
        greeks = raw.get("greeks") if isinstance(raw.get("greeks"), dict) else {}
        contract = dict(raw)
        contract["symbol"] = symbol
        contract["underlying_symbol"] = symbol
        if provider_symbol:
            contract.setdefault("contract_symbol", provider_symbol)
            contract.setdefault("contractSymbol", provider_symbol)
        if expiration:
            contract.setdefault("expiration", expiration)
            contract.setdefault("expiry", expiration)
        if contract.get("mark") is None and isinstance(contract.get("mid"), (int, float)):
            contract["mark"] = contract["mid"]
        if contract.get("implied_volatility") is None and isinstance(
            greeks.get("implied_volatility"), (int, float)
        ):
            contract["implied_volatility"] = greeks["implied_volatility"]
        if contract.get("delta") is None and isinstance(greeks.get("delta"), (int, float)):
            contract["delta"] = greeks["delta"]
        contract["source"] = "public_options"
        contract["data_source"] = "public_options"
        contract["source_reference"] = source_reference
        contract["source_backed"] = True
        contract["research_only"] = True
        contract["personal_owner_only"] = True
        contract["commercial_use_allowed"] = False
        contract["broker_execution"] = False
        contract["automatic_execution"] = False
        contract["automatic_contract_selection"] = False
        normalized.append(contract)
    return normalized


def _compact_cached_provider_row(row):
    if not isinstance(row, dict):
        return None
    if row.get("state") != "SOURCE_BOUND" or row.get("owner_display_reviewed") is not True:
        return None
    provider = row.get("provider")
    if provider not in {"finnhub", "alpha_vantage", "finazon", "bea"}:
        return None

    compact = {
        "provider": provider,
        "state": "SOURCE_BOUND",
        "kind": row.get("kind"),
        "source_reference": row.get("source_reference"),
        "historical_only": row.get("historical_only") is True,
        "live_quote": row.get("live_quote") is True,
        "real_time_market_context": row.get("real_time_market_context") is True,
        "consolidated_quote": row.get("consolidated_quote") is True,
        "soulaana_ai_use_reviewed": row.get("soulaana_ai_use_reviewed") is True,
        "research_only": True,
    }
    if provider == "finnhub":
        compact["summary"] = {
            "security_name": row.get("security_name"),
            "exchange": row.get("exchange"),
            "industry": row.get("industry"),
            "ipo_date": row.get("ipo_date"),
            "country": row.get("country"),
            "currency": row.get("currency"),
            "market_cap_millions": row.get("market_cap_millions"),
            "shares_outstanding_millions": row.get("shares_outstanding_millions"),
        }
    elif provider == "alpha_vantage":
        profile = row.get("company_profile") if isinstance(row.get("company_profile"), dict) else {}
        bars = row.get("bars") if isinstance(row.get("bars"), list) else []
        compact["summary"] = {
            "company_name": profile.get("name"),
            "sector": profile.get("sector"),
            "industry": profile.get("industry"),
            "country": profile.get("country"),
            "exchange": profile.get("exchange"),
            "market_cap": profile.get("market_cap"),
            "shares_outstanding": profile.get("shares_outstanding"),
            "latest_sessions": [dict(item) for item in bars[:2] if isinstance(item, dict)],
        }
    elif provider == "finazon":
        compact["summary"] = {
            "last_trade": dict(row.get("last_trade")) if isinstance(row.get("last_trade"), dict) else None,
            "session": dict(row.get("session")) if isinstance(row.get("session"), dict) else None,
            "prior_close": row.get("prior_close"),
            "high_52w": row.get("high_52w"),
            "low_52w": row.get("low_52w"),
            "daily_change_percent": row.get("daily_change_percent"),
            "coverage": row.get("coverage"),
        }
    else:
        macro = row.get("macro_series") if isinstance(row.get("macro_series"), list) else []
        compact["summary"] = {
            "macro_series": [dict(item) for item in macro[:4] if isinstance(item, dict)],
        }
    return compact


def _merge_cached_provider_context(app, document, sid):
    """Amalgamate already-fetched provider research without triggering new API calls."""
    cache = app.extensions.get("ob_provider_research_cache_v1")
    snapshot = getattr(cache, "snapshot_for_symbol", None)
    if not callable(snapshot) or not isinstance(sid, str) or not sid:
        document.setdefault("market_health", {})["cached_provider_amalgamation"] = {
            "available": False,
            "network_fetches_triggered": False,
        }
        return document

    symbol_rows = [
        row for row in document.get("symbols", [])
        if isinstance(row, dict) and isinstance(row.get("symbol"), str)
    ][:6]
    shared_context = {}
    per_symbol = {}
    ai_consumed = set()

    for row in symbol_rows:
        symbol = row["symbol"]
        coverage = [
            item for item in row.get("source_coverage", [])
            if isinstance(item, str)
        ]
        observations = (
            dict(row.get("source_observations"))
            if isinstance(row.get("source_observations"), dict)
            else {}
        )
        attached = []
        for cached in snapshot(sid, symbol):
            compact = _compact_cached_provider_row(cached)
            if compact is None:
                continue
            provider = compact["provider"]
            if provider == "bea":
                shared_context.setdefault("bea", compact)
                if compact.get("soulaana_ai_use_reviewed") is True:
                    ai_consumed.add("bea")
                continue
            observations[provider] = compact
            if provider not in coverage:
                coverage.append(provider)
            attached.append(provider)
            if compact.get("soulaana_ai_use_reviewed") is True:
                ai_consumed.add(provider)

        row["source_coverage"] = coverage
        row["source_observations"] = observations
        row["amalgamated_cached_providers"] = sorted(set(attached))
        per_symbol[symbol] = sorted(set(attached))

    if symbol_rows:
        document["sectors"] = [{
            "name": "Source-backed attention",
            "region_type": "RESEARCH_ATTENTION",
            "symbols": [dict(row) for row in symbol_rows],
        }]

    providers_present = {
        provider
        for row in symbol_rows
        for provider in row.get("source_coverage", [])
        if isinstance(provider, str)
    }
    providers_present.update(shared_context.keys())
    providers_present = sorted(providers_present)

    fusion = document.setdefault("source_fusion", {})
    fusion["providers_present"] = providers_present
    fusion["cached_provider_amalgamation"] = {
        "per_symbol": per_symbol,
        "shared_context_providers": sorted(shared_context.keys()),
        "network_fetches_triggered": False,
    }
    fusion["single_provider_selected_as_truth"] = False
    fusion["provider_values_overwritten"] = False
    fusion["all_source_observations_preserved_separately"] = True

    document["shared_research_context"] = shared_context
    document.setdefault("market_health", {})["cached_provider_amalgamation"] = {
        "available": True,
        "providers_present": providers_present,
        "symbols_with_cached_research": sum(1 for providers in per_symbol.values() if providers),
        "network_fetches_triggered": False,
    }
    soulaana = document.setdefault("soulaana", {}).setdefault("source_fusion", {})
    soulaana["cached_ai_reviewed_providers"] = sorted(ai_consumed)
    soulaana["single_provider_selected"] = False
    soulaana["meaning"] = (
        "I read the same canonical symbol records as every Observatory room. "
        "Already-fetched provider evidence stays separate by provenance but is "
        "amalgamated into one room projection."
    )
    if len(providers_present) > 1:
        document["source"] = "observatory-multi-provider-owner-research"
    return document


def _merge_public_owner_context(app, document, sid):
    """Add Public beside existing sources; never replace or promote it."""
    quote_reader = app.extensions.get("ob_public_owner_quote_reader_v1")
    option_reader = app.extensions.get("ob_public_owner_option_chain_reader_v1")
    if not callable(quote_reader):
        document.setdefault("source_fusion", {})["public_lane"] = "UNAVAILABLE"
        return document

    try:
        from tower.ob_settings_control_room import get_owner_settings
        use_public_options = get_owner_settings().get("use_public_options_data") is True
    except Exception:
        use_public_options = False

    symbol_rows = [
        row for row in document.get("symbols", [])
        if isinstance(row, dict) and isinstance(row.get("symbol"), str)
    ][:6]
    per_symbol = {}
    public_quotes = 0
    public_options = 0
    soulaana_public_quotes = 0
    soulaana_public_options = 0
    canonical_public_option_contracts = []

    for row in symbol_rows:
        symbol = row["symbol"]
        coverage = [
            x for x in row.get("source_coverage", [])
            if isinstance(x, str)
        ]
        observations = (
            dict(row.get("source_observations"))
            if isinstance(row.get("source_observations"), dict)
            else {}
        )

        try:
            public = quote_reader(sid, symbol, "EQUITY")
        except Exception:
            public = {"provider": "public", "state": "SOURCE_HOLD"}
        quote_state = public.get("state") if isinstance(public, dict) else "SOURCE_HOLD"
        public_ai = isinstance(public, dict) and public.get("soulaana_ai_use_reviewed") is True
        if (
            isinstance(public, dict)
            and quote_state == "SOURCE_BOUND"
            and public.get("owner_display_reviewed") is True
        ):
            observations["public"] = {
                "bid": public.get("bid"),
                "ask": public.get("ask"),
                "last": public.get("last"),
                "midpoint": _midpoint(public.get("bid"), public.get("ask"), public.get("last")),
                "observed_at": public.get("observed_at"),
                "personal_owner_only": True,
                "consolidated_quote": public.get("consolidated_quote") is True,
                "execution_grade_quote": False,
            }
            if "public" not in coverage:
                coverage.append("public")
            public_quotes += 1
            if public_ai:
                soulaana_public_quotes += 1

        option_state = "DISABLED_BY_OWNER"
        option_ai = False
        if use_public_options and callable(option_reader):
            try:
                options = option_reader(sid, symbol)
            except Exception:
                options = {"provider": "public_options", "state": "SOURCE_HOLD"}
            option_state = options.get("state") if isinstance(options, dict) else "SOURCE_HOLD"
            option_ai = isinstance(options, dict) and options.get("soulaana_ai_use_reviewed") is True
            if (
                isinstance(options, dict)
                and option_state == "SOURCE_BOUND"
                and options.get("owner_display_reviewed") is True
            ):
                canonical_contracts = _canonical_public_option_contracts(
                    options, symbol
                )
                canonical_public_option_contracts.extend(canonical_contracts)
                observations["public_options"] = {
                    "expiration": options.get("expiration"),
                    "underlying_midpoint": options.get("underlying_midpoint"),
                    "contract_count": len(canonical_contracts),
                    "personal_owner_only": True,
                    "execution_authorized": False,
                }
                if "public_options" not in coverage:
                    coverage.append("public_options")
                public_options += 1
                if option_ai:
                    soulaana_public_options += 1

        alpaca = observations.get("alpaca") if isinstance(observations.get("alpaca"), dict) else {}
        pub = observations.get("public") if isinstance(observations.get("public"), dict) else {}
        alpaca_value = alpaca.get("midpoint")
        public_value = pub.get("midpoint")
        comparison = {
            "sources_compared": [],
            "dispersion_percent": None,
            "winner_selected": False,
            "direct_interchangeability_assumed": False,
        }
        if isinstance(alpaca_value, (int, float)) and alpaca_value > 0:
            comparison["sources_compared"].append("alpaca")
        if isinstance(public_value, (int, float)) and public_value > 0:
            comparison["sources_compared"].append("public")
        if (
            isinstance(alpaca_value, (int, float)) and alpaca_value > 0
            and isinstance(public_value, (int, float)) and public_value > 0
        ):
            mean = (float(alpaca_value) + float(public_value)) / 2.0
            comparison["dispersion_percent"] = round(
                abs(float(alpaca_value) - float(public_value)) / mean * 100.0, 6
            )

        row["source_coverage"] = coverage
        row["source_observations"] = observations
        row["source_comparison"] = comparison
        per_symbol[symbol] = {
            "source_coverage": list(coverage),
            "public_quote_state": quote_state,
            "public_options_state": option_state,
            "public_quote_ai_consumable": public_ai and quote_state == "SOURCE_BOUND",
            "public_options_ai_consumable": option_ai and option_state == "SOURCE_BOUND",
            "comparison": comparison,
        }

    if symbol_rows:
        document["sectors"] = [{
            "name": "Source-backed attention",
            "region_type": "RESEARCH_ATTENTION",
            "symbols": [dict(row) for row in symbol_rows],
        }]

    providers_present = sorted({
        provider
        for row in symbol_rows
        for provider in row.get("source_coverage", [])
        if isinstance(provider, str)
    })
    if len(providers_present) > 1:
        document["source"] = "observatory-multi-provider-owner-research"
        document["reason"] = (
            "The Observatory retained multiple permitted source families for the same "
            "research symbols. No provider overwrote another; provenance and differences "
            "remain explicit."
        )

    if canonical_public_option_contracts:
        existing_options = [
            dict(row)
            for row in document.get("options", [])
            if isinstance(row, dict)
        ]
        seen = {
            (
                row.get("contract_symbol")
                or row.get("contractSymbol")
                or row.get("provider_symbol"),
                row.get("symbol") or row.get("underlying_symbol"),
            )
            for row in existing_options
        }
        for contract in canonical_public_option_contracts:
            key = (
                contract.get("contract_symbol")
                or contract.get("contractSymbol")
                or contract.get("provider_symbol"),
                contract.get("symbol") or contract.get("underlying_symbol"),
            )
            if key not in seen:
                existing_options.append(contract)
                seen.add(key)
        document["options"] = existing_options
        document["public_option_contract_count"] = len(canonical_public_option_contracts)

    fusion = {
        "schema": "OB_CANONICAL_MULTI_SOURCE_FUSION_V1",
        "providers_present": providers_present,
        "per_symbol": per_symbol,
        "public_quote_symbols": public_quotes,
        "public_option_symbols": public_options,
        "soulaana_public_quote_symbols": soulaana_public_quotes,
        "soulaana_public_option_symbols": soulaana_public_options,
        "single_provider_selected_as_truth": False,
        "provider_values_overwritten": False,
        "all_source_observations_preserved_separately": True,
    }
    document["source_fusion"] = fusion
    document.setdefault("market_health", {})["source_fusion"] = {
        "providers_present": providers_present,
        "symbol_count": len(symbol_rows),
        "multi_source_symbols": sum(
            1 for row in symbol_rows if len(row.get("source_coverage", [])) > 1
        ),
    }
    document.setdefault("soulaana", {})["source_fusion"] = {
        "providers_present": providers_present,
        "public_quote_symbols_consumed": soulaana_public_quotes,
        "public_option_symbols_consumed": soulaana_public_options,
        "single_provider_selected": False,
        "meaning": (
            "I am keeping every permitted source observation in its own lane and comparing "
            "overlap instead of choosing one provider to replace the rest."
        ),
    }
    return document


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
    old_handler = app.view_functions.get(FEED_ENDPOINT)
    # Never override a future real provider bridge or a different Flask app.
    if (
        not callable(old_handler)
        or old_handler.__module__ != "web.app"
        or old_handler.__name__ != FEED_ENDPOINT
    ):
        raise RuntimeError("Expected historical seed-only OB handler changed; review provider before overriding")
    app.extensions["ob_old_seed_only_feed_handler_preserved_for_audit"] = old_handler

    def hosted_source_status():
        document = pending_provider_document()
        state = "provider-not-configured"
        try:
            sid = _owner_sid()
            reader = app.extensions.get("ob_provider_key_secret_reader_v1")
            document = autonomous_dashboard_projection(
                sid=sid,
                temp_reader=reader,
            )
            item, _credential_source = resolve_credential(
                sid=sid,
                temp_reader=reader,
            )
            if item is not None and isinstance(sid, str) and sid:
                manager = stream_manager()
                stream_status = manager.ensure(
                    sid=sid,
                    credential=item,
                    symbols=document.get("watchlist") or [
                        row.get("symbol") for row in document.get("symbols", [])
                    ],
                    hub=app.extensions.get("ob_observatory_event_hub"),
                )
                stream_rows = manager.snapshot(document.get("watchlist") or None)
                document.setdefault("market_health", {})["alpaca_websocket"] = stream_status
                document["stream_market_context"] = stream_rows
                document.setdefault("provider_boundary", {})["persistent_websocket_requested"] = True
                document["provider_boundary"]["websocket_endpoint"] = (
                    "wss://stream.data.alpaca.markets/v2/iex"
                )
                document["provider_boundary"]["stream_read_only"] = True
                document.setdefault("soulaana", {})["stream_state"] = stream_status["state"]
                document["soulaana"]["stream_symbols"] = stream_status["symbols_active"]
                if stream_rows:
                    document["soulaana"]["stream_note"] = (
                        "I am receiving normalized Alpaca IEX trade, quote and minute-bar updates "
                        "for the current research watchlist. This is venue-limited research context, "
                        "not SIP/NBBO and not an execution quote."
                    )

            document = _merge_public_owner_context(app, document, sid)
            document = _merge_cached_provider_context(app, document, sid)
            providers = document.get("source_fusion", {}).get("providers_present", [])
            state = (
                "multi-provider-observatory-research"
                if len(providers) > 1
                else "alpaca-autonomous-research-websocket"
            )
        except Exception as exc:
            # Fail closed without leaking provider response or secret material.
            document["reason"] = (
                "Soulaana's autonomous market-research request is held. "
                "A verified temporary Alpaca credential or durable hosted Alpaca secret pair "
                "is required; no synthetic market values are substituted."
            )
            document["provider_boundary"]["autonomous_research_hold"] = type(exc).__name__
        response = jsonify(document)
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Cookie"
        response.headers["X-OB-Market-Source-State"] = state
        return response

    app.view_functions[FEED_ENDPOINT] = hosted_source_status
    app.extensions[marker] = True
    return app
