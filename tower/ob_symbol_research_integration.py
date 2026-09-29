"""OBINTEL/Tower — optional source-bound context in existing private OB rooms.

The shipped hosted application installs NO research resolver. Therefore this
adds no live data, mock research or extra route. A future separate backend
handoff can inject exact reviewed SymbolResearchInputs, never a URL parameter,
browser JSON, symbol guess, session flag or synthetic quote.

This boundary is intentionally independent from the existing Desk/engine-feed
corridors; no trade, candidate or capital permission derives from it.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from math import isfinite
import re

from flask import Flask, abort, request

from engine.market_intake.contracts import clean_symbol
from engine.market_intake.symbol_research import (
    SymbolResearchInputs, symbol_research_snapshot,
)
from engine.market_intake.research_bridge import project_research
from tower.tower_human_login_ob_launch import (
    operational_ob_access_active, owner_session_active, step_up_active,
)

_EXACT_ROOMS = {
    "/ob/market-map": "market_map",
    "/ob/trade-center": "trade_center",
    "/ob/review-center": "review_center",
}
_SYMBOL = re.compile(r"^/ob/symbol/([A-Za-z][A-Za-z0-9.-]{0,15})$")
_EXTENSION = "tower_ob_symbol_research_context_v1"


def _trusted_owner() -> bool:
    return (owner_session_active() is True and step_up_active() is True
            and operational_ob_access_active() is True)



def _reviewed_sec_examination(snapshot: dict) -> dict:
    """Turn only the independently AI-reviewed SEC facts into an owner explanation.

    Reuse the authoritative Soulaana rights projection; do not infer permission
    from the owner's display view. This is deterministic research, not an LLM
    call, an unreviewed filing-body handoff or market/trading authority.
    """
    view = project_research(snapshot, "soulaana")
    facts = view["fundamentals"]
    state = facts.get("state")
    findings = []
    comparisons = []
    if state == "SOURCE_BOUND":
        for fact in facts.get("reported_concepts", [])[:6]:
            if not isinstance(fact, dict):
                continue
            value = fact.get("value")
            reference = fact.get("reference")
            if (type(value) not in (int, float) or not isfinite(value)
                    or not isinstance(reference, str)
                    or not reference.startswith("https://www.sec.gov/Archives/edgar/data/")
                    or len(reference) > 500):
                continue
            findings.append({
                "concept": str(fact.get("concept", ""))[:90],
                "value": value,
                "unit": str(fact.get("units", ""))[:25],
                "fiscal_end": str(fact.get("fiscal_end", ""))[:32],
                "accepted_at": str(fact.get("accepted_at", ""))[:40],
                "filing_form": str(fact.get("form", ""))[:20],
                "source_reference": reference,
                "meaning": "A historical issuer-reported SEC financial concept, not a current market price.",
            })
        for item in facts.get("year_end_balance_sheet_comparisons", [])[:3]:
            if not isinstance(item, dict):
                continue
            earlier, later = item.get("earlier_source"), item.get("later_source")
            if (not all(isinstance(x, str) and
                    x.startswith("https://www.sec.gov/Archives/edgar/data/")
                    and len(x) <= 500 for x in (earlier, later))):
                continue
            comparisons.append({
                "concept": str(item.get("concept", ""))[:90],
                "earlier_period": str(item.get("earlier_fiscal_end", ""))[:32],
                "later_period": str(item.get("later_fiscal_end", ""))[:32],
                "reported_change_pct": item.get("reported_change_pct"),
                "unit": str(item.get("unit", ""))[:25],
                "earlier_source": earlier,
                "later_source": later,
                "meaning": "Retrospective issuer-filing comparison only; it cannot establish a live quote or causality.",
            })
    return {
        "schema": "OB_SOULAANA_REVIEWED_SEC_EXAMINATION_V1",
        "state": "SOURCE_BOUND" if findings else (
            "AI_RIGHTS_HOLD" if state == "EXPLANATION_RIGHTS_HOLD" else "NO_VERIFIED_REVIEWED_FACTS"
        ),
        "symbol": view["symbol"],
        "as_of": view["as_of"],
        "findings": findings,
        "comparisons": comparisons,
        "issuer_events_in_ai_content": False,
        "external_model_called": False,
        "source_only": True,
        "live_quote_verified": False,
        "candidate_admitted": False,
        "broker_execution_authorized": False,
    }


def register_protected_symbol_research_context(
    app: Flask,
    *,
    research_resolver: Callable[[str, str], SymbolResearchInputs | None] | None = None,
    trusted_selected_symbol: Callable[[str], str | None] | None = None,
) -> Flask:
    """Install read-only Jinja context projection, never an API/fetch endpoint.

    research_resolver(room, exact_symbol) MUST be a backend-owned service
    returning input assembled from source-reviewed historical/SEC records.
    The selected_symbol callback is required for rooms whose path does not
    carry a symbol; it MUST read existing server-side canonical selection.
    """
    if _EXTENSION in app.extensions:
        raise RuntimeError("symbol research integration must be registered once")
    if research_resolver is not None and not callable(research_resolver):
        raise ValueError("trusted research resolver must be callable")
    if trusted_selected_symbol is not None and not callable(trusted_selected_symbol):
        raise ValueError("trusted symbol selection must be callable")

    app.extensions[_EXTENSION] = {
        "source_only": True, "provider_attached": research_resolver is not None,
        "runtime_market_feed_attached": False, "trading_authorized": False,
        "browser_mutations": False,
    }

    @app.context_processor
    def _optional_source_bound_research() -> dict:
        if research_resolver is None:
            return {}
        path = request.path
        room = _EXACT_ROOMS.get(path)
        symbol = None
        match = _SYMBOL.fullmatch(path)
        if match:
            room = "symbol_page"
            symbol = match.group(1)
        elif room is not None and trusted_selected_symbol is not None:
            # Existing owner-selected symbol from canonical server state only,
            # never a request argument, Referer or stale browser storage.
            if not _trusted_owner():
                return {}
            try:
                symbol = trusted_selected_symbol(room)
            except Exception:
                abort(503)
        if room is None or not symbol or not _trusted_owner():
            return {}
        try:
            symbol = clean_symbol(symbol)
            inputs = research_resolver(room, symbol)
            if inputs is None:
                return {}  # Unavailable evidence is not a demo fallback.
            if (not isinstance(inputs, SymbolResearchInputs) or
                    inputs.identity.symbol != symbol):
                abort(503)
            if inputs.captured_at > datetime.now(timezone.utc):
                abort(503)
            # No live gateway/ScanContext passed: historical/issuer evidence
            # is not promoted to a current quote through UI projection.
            snapshot = symbol_research_snapshot(inputs, as_of=inputs.captured_at)
            context = project_research(snapshot, room)
            context["soulaana_sec_examination"] = _reviewed_sec_examination(snapshot)
            if (context.get("symbol") != symbol or context.get("room") != room
                    or context.get("may_authorize_order") is not False
                    or context.get("may_authorize_candidate") is not False):
                abort(503)
            return {"ob_research_context": context}
        except Exception:
            # No provider error detail, key, raw licensed payload or selected
            # source data may leak into the owner's HTML on a failed read.
            abort(503)

    return app
