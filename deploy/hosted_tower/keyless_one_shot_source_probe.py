"""One-shot hosted proof of actual keyless provider reads and Soulaana examination.

Runs ONLY with OB_KEYLESS_ONE_SHOT_SOURCE_PROBE=1. The normal owner route
remains protected. This diagnostic sends no requests to a broker or paid API;
never logs raw source values, identifiers, credentials, HTTP bodies or errors.
It proves the same source service can retrieve and examine actual observations
from the running Render environment, not an authenticated browser session.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError

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


# These identifiers are defined by our own source adapter. Never log vendor
# response text, HTTP body, request URL, exception object or host details.
_SAFE_BLS_HOLDS = frozenset({
    "OWNER_SOURCE_REVIEW_REQUIRED", "SOURCE_ENDPOINT_NOT_ALLOWED",
    "SOURCE_RESPONSE_TOO_LARGE", "SOURCE_TRANSPORT_HOLD",
    "SOURCE_JSON_INVALID", "SOURCE_VALUE_INVALID",
    "BLS_SERIES_INVALID", "BLS_SOURCE_SHAPE_HOLD",
})


def capture_bls_diagnostic(service, state: dict) -> None:
    """Attach ephemeral trace at the existing source call, not a second API hit."""
    from engine.market_intake.public_research_sources import PublicResearchUnavailable

    original_open = service.reference._opener
    original_reader = service.reference.bls_v1

    def traced_open(request, timeout):
        if not request.full_url.startswith(
            "https://api.bls.gov/publicAPI/v1/timeseries/data/"
        ):
            return original_open(request, timeout)
        try:
            response = original_open(request, timeout)
            state["bls_http"] = "HTTP_" + str(getattr(response, "status", 200))
            return response
        except HTTPError as exc:
            code = int(exc.code)
            state["bls_http"] = ("HTTP_" + str(code)
                                  if 300 <= code <= 599 else "HTTP_HOLD")
            raise
        except URLError:
            state["bls_http"] = "NETWORK_HOLD"
            raise
        except (TimeoutError, OSError):
            state["bls_http"] = "TRANSPORT_HOLD"
            raise

    def traced_reader(series_id):
        try:
            return original_reader(series_id)
        except PublicResearchUnavailable as exc:
            identifier = str(exc)
            state["bls_failure_kind"] = (
                identifier if identifier in _SAFE_BLS_HOLDS else "OTHER_HOLD"
            )
            raise

    service.reference._opener = traced_open
    service.reference.bls_v1 = traced_reader


def main() -> int:
    safe_diagnostic = {}
    try:
        from engine.market_intake.keyless_public_context import from_environment
        # One fixed, public, illustrative ticker; no user account, no broker,
        # no persistence or scheduled repeat. From_environment uses the
        # existing independent use/display/AI flags.
        service = from_environment()
        capture_bls_diagnostic(service, safe_diagnostic)
        report = summarize_snapshot(service.snapshot(symbol="MSFT"))
        report.update(safe_diagnostic)
    except Exception:
        # Exception messages may contain provider-supplied text. Never log them.
        report = {
            "schema": "OB_KEYLESS_HOSTED_ONE_SHOT_PROOF_V1",
            "all_verified": False, "status": "SOURCE_OR_CONTRACT_HOLD",
            "owner_browser_session_verified": False,
            "raw_values_logged": False,
            **safe_diagnostic,
        }
    print("OB_KEYLESS_ONE_SHOT_PROOF " + json.dumps(report, sort_keys=True), flush=True)
    return 0 if report["all_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
