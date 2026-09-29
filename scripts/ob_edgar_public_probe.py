"""Manual localhost/office EDGAR research probe. Never hosted or a trade route.

Requires an independently obtained approved Nasdaq Trader directory file so an
SEC ticker alone cannot establish a listed security. Prints counts/states only.
No raw SEC filing or financial values are persisted or printed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys

from engine.market_intake.sec_public_client import (
    EDGARPublicClient, SECResearchUnavailable, SEC_API,
)
from engine.market_intake.sec_public_research import EDGARPolicy, EDGARResearchCollector
from engine.market_intake.universe import parse_nasdaq_directory


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only owner EDGAR research probe")
    parser.add_argument("--symbol", required=True, help="Exact symbol in approved Nasdaq directory")
    parser.add_argument("--directory-file", required=True, type=Path,
                        help="Local approved nasdaqlisted.txt or otherlisted.txt")
    parser.add_argument("--confirm-sec-policy-reviewed", action="store_true")
    parser.add_argument("--confirm-directory-use-approved", action="store_true")
    parser.add_argument("--confirm-single-worker", action="store_true",
                        help="Operator has verified only one collector worker/process is active")
    parser.add_argument("--enable-ai-explanation", action="store_true",
                        help="Use only after owner has separately reviewed this permitted use")
    args = parser.parse_args(argv)
    if not (args.confirm_sec_policy_reviewed and args.confirm_directory_use_approved
            and args.confirm_single_worker):
        parser.error("Explicit SEC policy, directory-use and single-worker confirmations required")
    contact = os.getenv("OB_SEC_CONTACT_EMAIL", "")
    if not contact:
        parser.error("Set OB_SEC_CONTACT_EMAIL privately to a real business contact email")
    directory_name = args.directory_file.name
    if directory_name not in {"nasdaqlisted.txt", "otherlisted.txt"}:
        parser.error("Only named approved Nasdaq Trader directory inputs supported")
    try:
        rows = parse_nasdaq_directory(
            args.directory_file.read_text(encoding="utf-8"),
            directory=directory_name, observed_at=datetime.now(timezone.utc))
        matches = [row for row in rows if row.symbol == args.symbol.strip().upper()]
        if len(matches) != 1:
            raise SECResearchUnavailable("SYMBOL_NOT_IN_APPROVED_DIRECTORY")
        policy = EDGARPolicy(
            reviewed_reference=SEC_API, reviewed_at=datetime.now(timezone.utc),
            internal_research_approved=True, owner_display_approved=True,
            ai_explanation_approved=args.enable_ai_explanation, retention_approved=False)
        collector = EDGARResearchCollector(
            EDGARPublicClient(contact), policy, owner_authorized=True,
            single_worker_confirmed=True)
        index = collector.public_ticker_index()
        packet = collector.owner_snapshot(matches[0], index)
    except (SECResearchUnavailable, ValueError, OSError) as exc:
        # No raw provider body, tokens or contact email should reach logs.
        print("EDGAR probe HOLD: " + (str(exc) if isinstance(exc, SECResearchUnavailable)
                                       else "INPUT_OR_SOURCE_VALIDATION_FAILED"), file=sys.stderr)
        return 2
    print("EDGAR public research verified (read only; not hosted/live/trade-enabled)")
    print("Symbol:", packet["symbol"])
    print("Identity:", packet["identity"]["identity_status"])
    print("Research state:", packet["state"])
    print("SEC facts:", len(packet["fundamentals"].get("reported_concepts", [])))
    print("Issuer events:", len(packet.get("issuer_events", [])))
    print("Current quote:", packet["scanner"]["state"])
    print("Candidate admitted:", packet["candidate_admitted"])
    print("Order authorized:", packet["execution_authorized"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
