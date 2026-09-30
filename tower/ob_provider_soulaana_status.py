"""Soulaana source-status only handoff for Tower provider lanes.

The input is Tower's *already sanitized* same-session connection projection,
not a vendor response, provider credential, raw account object, or market data.
This is a deterministic explanatory register, not permission for model access to
source content, quote admission, brokerage or any trading mode.
"""
from __future__ import annotations

from collections.abc import Mapping

ORDER = ("public", "finnhub", "alpha_vantage", "finazon", "eia", "bea", "sec", "bls", "treasury", "openfigi")
KEY_STATES = frozenset({"READ_ONLY_CHECK_PASSED", "TEMPORARY_KEY_RECEIVED", "NOT_CONFIGURED"})
PUBLIC_STATES = frozenset({
    "TEMPORARY_ACCOUNT_LINK_VERIFIED", "OWNER_SELECTION_REQUIRED",
    "TEMPORARY_AUTH_ONLY", "NO_VERIFIED_ACCOUNT_LINK",
})
REFERENCE_STATES = frozenset({"USE_AND_OWNER_DISPLAY_CONFIGURED", "RIGHTS_REVIEW_HOLD"})
SEC_STATES = frozenset({"SEPARATE_ISSUER_RESEARCH_CONFIGURED", "RIGHTS_REVIEW_HOLD"})
NAMES = {
    "public": "Public", "finnhub": "Finnhub", "alpha_vantage": "Alpha Vantage",
    "finazon": "Finazon", "eia": "U.S. EIA", "bea": "U.S. BEA",
    "sec": "SEC EDGAR", "bls": "BLS", "treasury": "U.S. Treasury", "openfigi": "OpenFIGI",
}
EXPLANATIONS = {
    "READ_ONLY_CHECK_PASSED": "The temporary key passed one read-only provider probe. Market-data, display and AI-use rights are still unverified.",
    "TEMPORARY_KEY_RECEIVED": "A key is in temporary server memory. No provider response or permitted feed has been proven.",
    "NOT_CONFIGURED": "No current provider key was received in this Tower session.",
    "TEMPORARY_ACCOUNT_LINK_VERIFIED": "A Public account was linked to temporary authentication. This is not quote-feed or trade permission.",
    "OWNER_SELECTION_REQUIRED": "The owner must choose an eligible Public account in its protected connection flow.",
    "TEMPORARY_AUTH_ONLY": "Public authentication was temporary, but no eligible account was linked. Check Public API account linkage.",
    "NO_VERIFIED_ACCOUNT_LINK": "No verified Public API account is attached to this owner session.",
    "USE_AND_OWNER_DISPLAY_CONFIGURED": "Source use and owner-display review flags are configured. No actual data was requested or verified by this status endpoint.",
    "SEPARATE_ISSUER_RESEARCH_CONFIGURED": "SEC issuer research has a separately reviewed corridor. This status read did not retrieve a filing.",
    "RIGHTS_REVIEW_HOLD": "Source use and owner-display review are not both configured.",
}


def build_soulaana_provider_status(packet: Mapping) -> dict:
    """Allow only the exact non-promoting Tower status document and seven lanes."""
    if (
        not isinstance(packet, dict)
        or packet.get("schema") != "OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1"
        or packet.get("owner_session_checked") is not True
        or packet.get("source_only") is not True
        or packet.get("dissemination_contract") != "OWNER_STATUS_ONLY"
        or packet.get("real_market_feed_attached_by_this_route") is not False
        or packet.get("prices_attached") is not False
        or packet.get("positions_attached") is not False
        or packet.get("live_feed_count_verified") is not None
        or packet.get("no_browser_provider_credentials") is not True
        or packet.get("may_authorize_order") is not False
        or packet.get("may_authorize_capital") is not False
        or packet.get("may_change_trading_mode") is not False
    ):
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    rows = packet.get("provider_status")
    if not isinstance(rows, list) or len(rows) != len(ORDER):
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    register = []
    for key, row in zip(ORDER, rows):
        if not isinstance(row, dict) or row.get("provider") != key:
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
        state = row.get("state")
        allowed = (
            PUBLIC_STATES if key == "public" else
            KEY_STATES if key in {"finnhub", "alpha_vantage", "finazon", "eia", "bea"} else
            SEC_STATES if key == "sec" else REFERENCE_STATES
        )
        if (
            not isinstance(state, str) or state not in allowed
            or row.get("quote_feed_activated") is not False
            or (key in {"public", "finnhub", "alpha_vantage", "finazon", "eia", "bea"} and (
                row.get("source_use_rights_verified") is not False
                or row.get("data_display_rights_verified") is not False
            ))
            or (key in {"sec", "bls", "treasury", "openfigi"} and (
                row.get("reference_only") is not True
                or row.get("provider_request_made") is not False
                or row.get("current_data_accepted") is not False
                or row.get("ai_use_authorized") is not False
            ))
        ):
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
        if key == "public":
            if type(row.get("account_linked")) is not bool:
                raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
            if (state == "TEMPORARY_ACCOUNT_LINK_VERIFIED") != row["account_linked"]:
                raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
        register.append({
            "provider": key,
            "label": NAMES[key],
            "state": state,
            "meaning": EXPLANATIONS[state],
        })
    return {
        "schema": "OB_SOULAANA_PROVIDER_CONNECTION_STATUS_V1",
        "channel": "SOULAANA_CONNECTION_STATUS_ONLY",
        "what_i_see": "I can see ten separately labeled provider connection and rights-review states from Tower.",
        "what_it_means": "Credential receipt, a read-only probe, source configuration and Public account linkage are different steps; none independently supplies a licensed current market feed.",
        "what_is_missing": "Approved instrument/product data rights, provider provenance, permitted owner display/AI use, verified current prices and execution authority remain separate.",
        "next_step": "Use the protected Market Data Desk for credential checks and source review. Resolve Public's account linkage with Public; do not invent an account ID or substitute historical data for a live quote.",
        "provider_register": register,
        "raw_provider_values_included": False,
        "account_identifiers_included": False,
        "credentials_included": False,
        "source_content_ai_authorized": False,
        "quote_verified": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
    }
