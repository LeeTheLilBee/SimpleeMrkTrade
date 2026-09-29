"""Explicit owner-operated EDGAR read-only source check; no credentials or trade mode."""
from __future__ import annotations

import argparse
import json

from engine.market_intake.sec_public_research import sec_owner_resolver_from_environment
from engine.market_intake.symbol_research import symbol_research_snapshot
from engine.market_intake.research_memory import soulaana_research_brief


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check official SEC issuer research for OB")
    parser.add_argument("--symbol", required=True, help="Exact official SEC-listed ticker")
    args = parser.parse_args(argv)
    resolver = sec_owner_resolver_from_environment()
    if resolver is None:
        parser.error("EDGAR owner research is disabled; review SEC configuration first")
    inputs = resolver("symbol_page", args.symbol.upper())
    if inputs is None:
        print(json.dumps({"state": "SEC_TICKER_NOT_FOUND", "source": "SEC_OFFICIAL_DIRECTORY",
                          "live_quote": False, "trading_authorized": False}))
        return 2
    packet = symbol_research_snapshot(inputs, as_of=inputs.captured_at)
    print(json.dumps({
        "schema": "OB_SEC_OWNER_SOURCE_CHECK_V1",
        "symbol": packet["symbol"],
        "identity": packet["identity"],
        "state": packet["state"],
        "fundamentals": packet["fundamentals"],
        "issuer_events": packet["issuer_events"],
        "soulaana": soulaana_research_brief(packet),
        "live_market_data_connected": False,
        "can_authorize_trading": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
