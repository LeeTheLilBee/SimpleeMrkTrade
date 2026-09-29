"""One-shot hosted proof of actual keyless provider reads and Soulaana examination.

Runs ONLY with OB_KEYLESS_ONE_SHOT_SOURCE_PROBE=1. The normal owner route
remains protected. This diagnostic sends no requests to a broker or paid API;
never logs raw source values, identifiers, credentials, HTTP bodies or errors.
It proves the same source service can retrieve and examine actual observations
from the running Render environment, not an authenticated browser session.
"""
from __future__ import annotations

import json

SOURCES = ("bls", "treasury", "openfigi")
ORDER = ("sec",) + SOURCES


def summarize_snapshot(packet: dict) -> dict:
    """Return only constrained state/count proof; reject fabricated authority."""
    if (not isinstance(packet, dict)
            or packet.get("schema") != "OB_KEYLESS_PUBLIC_CONTEXT_V1"
            or packet.get("source_only") is not True
            or packet.get("context_only") is not True
            or packet.get("prices_attached") is not False
            or packet.get("options_chain_attached") is not False
            or packet.get("live_quote_verified") is not False
            or packet.get("candidate_admitted") is not False
            or packet.get("broker_execution_authorized") is not False
            or packet.get("ai_input_approved") is not False):
        raise ValueError("SOURCE_CONTRACT_HOLD")
    rows = packet.get("sources")
    if not isinstance(rows, list) or [r.get("source") for r in rows if isinstance(r, dict)] != list(ORDER):
        raise ValueError("SOURCE_CONTRACT_HOLD")
    states = {r["source"]: r.get("state") for r in rows}
    evidence = packet.get("soulaana_evidence_brief")
    if (not isinstance(evidence, dict)
            or evidence.get("schema") != "OB_SOULAANA_KEYLESS_EVIDENCE_V1"
            or evidence.get("channel") != "SOULAANA_REVIEWED_PUBLIC_RESEARCH"
            or evidence.get("external_model_called") is not False
            or evidence.get("live_quote_verified") is not False
            or evidence.get("candidate_admitted") is not False
            or evidence.get("broker_execution_authorized") is not False
            or evidence.get("capital_authorized") is not False
            or not isinstance(evidence.get("observations"), list)
            or not isinstance(evidence.get("comparisons"), list)):
        raise ValueError("SOULAANA_CONTRACT_HOLD")
    observed = {r.get("source") for r in evidence["observations"] if isinstance(r, dict)}
    compared = {r.get("source") for r in evidence["comparisons"] if isinstance(r, dict)}
    source_ok = all(states[k] == "SOURCE_BOUND" for k in SOURCES)
    ai_ok = source_ok and observed == set(SOURCES) and len(evidence["observations"]) == 3
    comparison_ok = compared == {"bls", "treasury"} and len(evidence["comparisons"]) == 2
    return {
        "schema": "OB_KEYLESS_HOSTED_ONE_SHOT_PROOF_V1",
        "source_states": {k: states[k] for k in ORDER},
        "source_read_verified": source_ok,
        "soulaana_evidence_verified": ai_ok,
        "two_period_comparisons_verified": comparison_ok,
        "all_verified": source_ok and ai_ok and comparison_ok,
        "sec_filing_fetched_by_probe": False,
        "owner_browser_session_verified": False,
        "real_time_prices_verified": False,
        "raw_values_logged": False,
    }


def main() -> int:
    try:
        from engine.market_intake.keyless_public_context import from_environment
        # One fixed, public, illustrative ticker; no user account, no broker,
        # no persistence or scheduled repeat. From_environment uses the
        # existing independent use/display/AI flags.
        report = summarize_snapshot(from_environment().snapshot(symbol="MSFT"))
    except Exception:
        # Exception messages may contain provider-supplied text. Never log them.
        report = {
            "schema": "OB_KEYLESS_HOSTED_ONE_SHOT_PROOF_V1",
            "all_verified": False, "status": "SOURCE_OR_CONTRACT_HOLD",
            "owner_browser_session_verified": False,
            "raw_values_logged": False,
        }
    print("OB_KEYLESS_ONE_SHOT_PROOF " + json.dumps(report, sort_keys=True), flush=True)
    return 0 if report["all_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
