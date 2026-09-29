"""Owner-invoked backend-only smoke check for free public reference APIs.

Never auto-called by Tower, CI, the browser, scanner, or Soulaana. No data
persistence. No credentials in output, URL logs or command arguments.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os

from engine.market_intake.public_research_sources import (
    OwnerResearchPolicy, PublicReferenceClient, PublicResearchUnavailable,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Opt-in public-reference research check")
    parser.add_argument("--source", required=True, choices=("bls", "bea", "openfigi"))
    parser.add_argument("--series", default="LNS14000000",
                        help="Official BLS series ID, BLS only")
    parser.add_argument("--ticker", default="MSFT",
                        help="Ticker for optional OpenFIGI identifier mapping")
    args = parser.parse_args()
    if any(os.environ.get(name) != "1" for name in (
        "OB_PUBLIC_RESEARCH_ENABLED",
        "OB_PUBLIC_RESEARCH_USE_REVIEWED",
        "OB_PUBLIC_RESEARCH_OWNER_DISPLAY_REVIEWED",
    )):
        print("HOLD: backend source use/owner display not enabled and reviewed.")
        return 2
    # Each provider must be reviewed separately, even when global opt-in is on.
    # No default approval or inference from another provider's consent.
    provider_prefix = "OB_PUBLIC_RESEARCH_" + args.source.upper()
    if os.environ.get(provider_prefix + "_USE_REVIEWED") != "1" or os.environ.get(
        provider_prefix + "_OWNER_DISPLAY_REVIEWED"
    ) != "1":
        print("HOLD: selected provider use/display rights are not independently reviewed.")
        return 2
    ai_reviewed = (
        os.environ.get("OB_PUBLIC_RESEARCH_AI_USE_REVIEWED") == "1"
        and os.environ.get(provider_prefix + "_AI_USE_REVIEWED") == "1"
    )
    policy = OwnerResearchPolicy(
        source_use_reviewed=True, owner_display_reviewed=True,
        ai_use_reviewed=ai_reviewed,
        reviewed_sources=frozenset({args.source}),
        ai_reviewed_sources=frozenset({args.source}) if ai_reviewed else frozenset(),
    )
    client = PublicReferenceClient(policy)
    try:
        if args.source == "bls":
            result = client.bls_v1(args.series)
        elif args.source == "bea":
            result = client.bea_nipa(os.environ.get("OB_BEA_API_KEY", ""))
        else:
            result = client.openfigi_ticker(args.ticker,
                                            api_key=os.environ.get("OB_OPENFIGI_API_KEY") or None)
    except PublicResearchUnavailable as exc:
        print("HOLD: " + str(exc))
        return 2
    print(json.dumps(asdict(result), default=str, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
