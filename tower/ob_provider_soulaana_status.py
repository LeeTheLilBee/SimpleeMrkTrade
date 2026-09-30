"""Soulaana source-status handoff for Tower's nine provider lanes.

The input is Tower's already-sanitized same-session connection projection, not a
vendor response, credential, raw account object or market data. This is a
deterministic explanatory register. It never grants source-content AI use,
quote admission, brokerage authority or any trading mode.
"""
from __future__ import annotations

from collections.abc import Mapping

from tower.ob_provider_diagnostics import SAFE_PROBE_CODES

ORDER = (
    "public", "finnhub", "alpha_vantage", "twelve_data", "finazon",
    "sec", "bls", "treasury", "openfigi",
)
KEY_PROVIDERS = frozenset({"finnhub", "alpha_vantage", "twelve_data", "finazon"})
KEY_STATES = frozenset({"READ_ONLY_CHECK_PASSED", "TEMPORARY_KEY_RECEIVED", "NOT_CONFIGURED"})
PUBLIC_STATES = frozenset({
    "TEMPORARY_ACCOUNT_LINK_VERIFIED", "OWNER_SELECTION_REQUIRED",
    "TEMPORARY_AUTH_ONLY", "NO_VERIFIED_ACCOUNT_LINK",
})
REFERENCE_STATES = frozenset({"USE_AND_OWNER_DISPLAY_CONFIGURED", "RIGHTS_REVIEW_HOLD"})
SEC_STATES = frozenset({"SEPARATE_ISSUER_RESEARCH_CONFIGURED", "RIGHTS_REVIEW_HOLD"})
NAMES = {
    "public": "Public",
    "finnhub": "Finnhub",
    "alpha_vantage": "Alpha Vantage",
    "twelve_data": "Twelve Data",
    "finazon": "Finazon",
    "sec": "SEC EDGAR",
    "bls": "BLS",
    "treasury": "U.S. Treasury",
    "openfigi": "OpenFIGI",
}
EXPLANATIONS = {
    "READ_ONLY_CHECK_PASSED": (
        "The temporary key passed one fixed read-only provider probe. "
        "Product rights, display rights, AI use and market authority remain separate."
    ),
    "TEMPORARY_KEY_RECEIVED": (
        "A key is in temporary server memory, but the provider has not passed the "
        "fixed read-only verification for this session."
    ),
    "NOT_CONFIGURED": "No current provider key was received in this Tower session.",
    "TEMPORARY_ACCOUNT_LINK_VERIFIED": (
        "A Public account was linked to temporary authentication. "
        "This is not quote-feed or trade permission."
    ),
    "OWNER_SELECTION_REQUIRED": (
        "The owner must choose an eligible Public account in its protected connection flow."
    ),
    "TEMPORARY_AUTH_ONLY": (
        "Public authentication was temporary, but no eligible account was linked. "
        "Check Public API account linkage."
    ),
    "NO_VERIFIED_ACCOUNT_LINK": "No verified Public API account is attached to this owner session.",
    "USE_AND_OWNER_DISPLAY_CONFIGURED": (
        "Source use and owner-display review flags are configured. "
        "No actual data was requested or verified by this status endpoint."
    ),
    "SEPARATE_ISSUER_RESEARCH_CONFIGURED": (
        "SEC issuer research has a separately reviewed corridor. "
        "This status read did not retrieve a filing."
    ),
    "RIGHTS_REVIEW_HOLD": "Source use and owner-display review are not both configured.",
}


def _key_meaning(key: str, row: Mapping, state: str) -> str:
    meaning = EXPLANATIONS[state]
    probe = row.get("read_only_probe")
    if probe not in SAFE_PROBE_CODES:
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    if state == "READ_ONLY_CHECK_PASSED" and probe != "READ_ONLY_CHECK_PASSED":
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    if state == "NOT_CONFIGURED" and probe != "NOT_CONFIGURED":
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    if state == "TEMPORARY_KEY_RECEIVED" and probe in {
        "NOT_CONFIGURED", "READ_ONLY_CHECK_PASSED"
    }:
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")

    source_reviewed = row.get("source_use_rights_verified")
    display_reviewed = row.get("data_display_rights_verified")
    if type(source_reviewed) is not bool or type(display_reviewed) is not bool:
        raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")

    if key in {"finnhub", "alpha_vantage"}:
        if source_reviewed or display_reviewed:
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
    elif key == "twelve_data":
        if display_reviewed:
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
        if source_reviewed:
            meaning += (
                " The reviewed Business Basic lane is internal non-display only; "
                "market values stay server-side and AI use remains a separate gate."
            )
    elif key == "finazon":
        if display_reviewed and not source_reviewed:
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
        if source_reviewed:
            meaning += (
                " The reviewed US Equities Basic commercial lane is bounded to the "
                "actual workspace entitlement; the free trial remains AAPL/TSLA/GOOG."
            )
            if display_reviewed:
                meaning += " Owner display was separately reviewed for this account."
            else:
                meaning += " Owner display remains held."

    if state == "TEMPORARY_KEY_RECEIVED" and probe != "NOT_TESTED":
        meaning += " Safe probe state: " + probe.replace("_", " ").lower() + "."
    return meaning


def build_soulaana_provider_status(packet: Mapping) -> dict:
    """Allow only the exact non-promoting Tower status document and nine lanes."""
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
            PUBLIC_STATES if key == "public"
            else KEY_STATES if key in KEY_PROVIDERS
            else SEC_STATES if key == "sec"
            else REFERENCE_STATES
        )
        if not isinstance(state, str) or state not in allowed or row.get("quote_feed_activated") is not False:
            raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")

        if key == "public":
            if (
                type(row.get("account_linked")) is not bool
                or row.get("source_use_rights_verified") is not False
                or row.get("data_display_rights_verified") is not False
                or (state == "TEMPORARY_ACCOUNT_LINK_VERIFIED") != row["account_linked"]
            ):
                raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
            meaning = EXPLANATIONS[state]
        elif key in KEY_PROVIDERS:
            meaning = _key_meaning(key, row, state)
        else:
            if (
                row.get("reference_only") is not True
                or row.get("provider_request_made") is not False
                or row.get("current_data_accepted") is not False
                or row.get("ai_use_authorized") is not False
            ):
                raise ValueError("SOULAANA_PROVIDER_CONNECTION_HOLD")
            meaning = EXPLANATIONS[state]

        register.append({
            "provider": key,
            "label": NAMES[key],
            "state": state,
            "meaning": meaning,
        })

    return {
        "schema": "OB_SOULAANA_PROVIDER_CONNECTION_STATUS_V1",
        "channel": "SOULAANA_CONNECTION_STATUS_ONLY",
        "what_i_see": (
            "I can see nine separately labeled provider connection and rights-review "
            "states from Tower, including the commercial-free Twelve Data and Finazon lanes."
        ),
        "what_it_means": (
            "Credential receipt, read-only verification, commercial/internal-use review, "
            "display rights and Public account linkage are separate steps. None alone "
            "creates an execution-grade market feed."
        ),
        "what_is_missing": (
            "Exact runtime transport health, source provenance, permitted AI use, "
            "execution-grade bid/ask where required, options entitlement and execution "
            "authority remain separately gated."
        ),
        "next_step": (
            "Use the protected Market Data Desk for credential and rights checks. "
            "Commercial-free market values stay server-side unless the exact source grants "
            "the requested display use."
        ),
        "provider_register": register,
        "raw_provider_values_included": False,
        "account_identifiers_included": False,
        "credentials_included": False,
        "source_content_ai_authorized": False,
        "quote_verified": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
    }
