"""Soulaana's bounded explanation/status handoff for keyless public research.

This is a deterministic, non-LLM source-register projection. It deliberately
does NOT transmit BLS/Treasury values, FIGIs, issuer filings, source-period
payloads, source body text or retrieved documents into Soulaana's AI/decision
engines. Source-specific AI-use rights must be reviewed before a separate
content-bearing integration may be installed. The owner can separately see
source observations on protected cards, without promoting them to trading truth.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re

_ORDER = ("sec", "bls", "treasury", "openfigi")
_STATE = frozenset({
    "SOURCE_BOUND", "DELEGATED_ISSUER_RESEARCH", "REVIEW_HOLD",
    "SYMBOL_REQUIRED", "SOURCE_HOLD", "LOCAL_QUOTA_HOLD",
    "NOT_FOUND", "AMBIGUOUS_HOLD",
})
_READY = {
    "sec": ("SEC EDGAR", "Its separate issuer-research corridor is configured. No filing was fetched by this keyless status read."),
    "bls": ("BLS", "A dated CPI index reference was retrieved. It is neither an inflation percentage nor a current securities quote."),
    "treasury": ("US Treasury", "A record-dated public debt reference was retrieved. It is not a Treasury yield or a market price."),
    "openfigi": ("OpenFIGI", "A ticker-to-identifier reference match was found. It does not independently establish issuer identity or tradability."),
}
_GAP = {
    "REVIEW_HOLD": "Owner use/display source review is not enabled. No observation is available to this corridor.",
    "SYMBOL_REQUIRED": "An exact ticker is needed before an identifier lookup can be performed.",
    "SOURCE_HOLD": "The source result was unavailable or failed validation; do not use an old or invented substitute.",
    "LOCAL_QUOTA_HOLD": "The local source request budget is holding additional lookups.",
    "NOT_FOUND": "The source did not return a matching identifier.",
    "AMBIGUOUS_HOLD": "Conflicting or multiple identifier results prevent a unique match.",
}


def build_soulaana_source_register(packet: Mapping) -> dict:
    """Only receive already-vetted metadata from OB_KEYLESS_PUBLIC_CONTEXT_V1."""
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
        raise ValueError("SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD")
    rows = packet.get("sources")
    if not isinstance(rows, list) or len(rows) != len(_ORDER):
        raise ValueError("SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD")
    status = []
    for key, row in zip(_ORDER, rows):
        if (not isinstance(row, dict) or row.get("source") != key
                or row.get("state") not in _STATE
                or row.get("quote_eligible") is not False
                or row.get("trading_authorized") is not False
                or type(row.get("ai_use_approved")) is not bool
                or (row.get("ai_use_approved") is True and row.get("state") != "SOURCE_BOUND")):
            raise ValueError("SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD")
        state = row["state"]
        label, ready = _READY[key]
        if state == "DELEGATED_ISSUER_RESEARCH" and key != "sec":
            raise ValueError("SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD")
        if key == "sec" and state not in {"DELEGATED_ISSUER_RESEARCH", "REVIEW_HOLD"}:
            raise ValueError("SOULAANA_KEYLESS_SOURCE_CONTRACT_HOLD")
        if state in {"SOURCE_BOUND", "DELEGATED_ISSUER_RESEARCH"}:
            note = ready
        else:
            note = _GAP.get(state, "This source cannot be treated as a verified observation.")
        status.append({
            "source": key,
            "label": label,
            "state": state,
            "meaning": note,
        })
    bound = sum(s["state"] == "SOURCE_BOUND" for s in status)
    delegated = any(s["state"] == "DELEGATED_ISSUER_RESEARCH" for s in status)
    if bound == 0:
        what_i_see = "I can see the public-source map, but no keyless observations are verified in this read."
    else:
        what_i_see = (
            f"I can see {bound} independently labeled public reference "
            + ("source" if bound == 1 else "sources")
            + "."
        )
    what_it_means = (
        "These are dated economic/fiscal and identifier references. "
        "They can explain the research landscape, not what a stock or option costs right now."
    )
    if delegated:
        what_it_means += " SEC filings remain in the separately reviewed issuer corridor."
    return {
        "schema": "OB_SOULAANA_KEYLESS_STATUS_V1",
        "channel": "SOULAANA_SOURCE_STATUS_ONLY",
        "what_i_see": what_i_see,
        "what_it_means": what_it_means,
        "what_is_missing": (
            "Public's authenticated account and licensed price feed are independent. "
            "Source-content AI rights and an actual current equity/options quote are not established here."
        ),
        "next_step": (
            "Use the source cards to inspect original period and reference. "
            "Keep unresolved or ambiguous items on HOLD."
        ),
        "source_register": status,
        "source_observations_verified": bound,
        "sec_issuer_corridor_delegated": delegated,
        "raw_source_values_included": False,
        "source_content_ai_authorized": False,
        "candidate_admitted": False,
        "quote_verified": False,
        "broker_execution_authorized": False,
    }



# A separate, source-specific content handoff. The status register above still
# contains no provider values and cannot become an implicit AI-use grant.
_EVIDENCE_SOURCES = frozenset({"bls", "treasury", "openfigi"})
_REFERENCES = {
    "bls": "https://www.bls.gov/developers/api_signature.htm",
    "treasury": "https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/",
    "openfigi": "https://www.openfigi.com/api/documentation",
}
# Only the fixed official BLS API signature and its same-agency bulk file
# may accompany CPI evidence; a third-party link cannot impersonate BLS.
_BLS_BULK_REFERENCE = "https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems"
_BLS_V2_REFERENCE = "https://www.bls.gov/developers/api_signature_v2.htm"
_BLS_SERIES = {
    "CUUR0000SA0": ("CPI-U all items", "index"),
    "LNS14000000": ("Unemployment rate", "percent"),
    "CES0000000001": ("Total nonfarm payroll employment", "thousands"),
    "WPUFD4": ("PPI final demand", "index"),
}
_ALLOWED_REFERENCES = {
    "bls": frozenset({_REFERENCES["bls"], _BLS_BULK_REFERENCE, _BLS_V2_REFERENCE}),
    "treasury": frozenset({_REFERENCES["treasury"]}),
    "openfigi": frozenset({_REFERENCES["openfigi"]}),
}
_NUMBER = re.compile(r"^\d{1,43}(?:\.\d{1,9})?$")
_BLS_PERIOD = re.compile(r"^20\d{2}-M(?:0[1-9]|1[0-2])$")
_FIGI = re.compile(r"^BBG[A-Z0-9]{9}$")
_TICKER = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")


def build_soulaana_evidence_brief(packet: Mapping, *,
                                  approved_sources: frozenset[str]) -> dict:
    """Read bounded official facts only after independently approved AI use.

    The narrow artifact is safe for a separate *future* model connector to
    consume. It is already rendered as a deterministic Soulaana explanation in
    owner-only rooms. No external AI/model request is performed by this code.
    """
    if (type(approved_sources) is not frozenset
            or not approved_sources <= _EVIDENCE_SOURCES):
        raise ValueError("SOULAANA_EVIDENCE_RIGHTS_HOLD")
    # Independent validation of the status/read-only envelope, with exact rows.
    build_soulaana_source_register(packet)
    now = datetime.fromisoformat(str(packet["as_of"]).replace("Z", "+00:00"))
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("SOULAANA_EVIDENCE_TIMESTAMP_HOLD")
    rows = packet["sources"]
    observations = []
    statuses = []
    comparisons = []
    for row in rows:
        key, state = row["source"], row["state"]
        permitted = (key in approved_sources and state == "SOURCE_BOUND")
        if row["ai_use_approved"] is not permitted:
            raise ValueError("SOULAANA_EVIDENCE_RIGHTS_HOLD")
        statuses.append({"source": key, "state": state,
                         "content_readable": permitted})
        if not permitted:
            continue
        if row.get("source_reference") not in _ALLOWED_REFERENCES[key]:
            raise ValueError("SOULAANA_EVIDENCE_REFERENCE_HOLD")
        value = row.get("value")
        fetched_raw = row.get("retrieved_at")
        if not isinstance(value, str) or not isinstance(fetched_raw, str):
            raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
        try:
            fetched = datetime.fromisoformat(fetched_raw.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("SOULAANA_EVIDENCE_TIMESTAMP_HOLD") from None
        if (fetched.tzinfo is None or fetched.utcoffset() is None
                or fetched > now + timedelta(minutes=2)):
            raise ValueError("SOULAANA_EVIDENCE_TIMESTAMP_HOLD")
        period = row.get("period")
        if key == "bls" and isinstance(row.get("series"), list):
            panel = row["series"]
            if ([item.get("series_id") for item in panel] != list(_BLS_SERIES)
                    or len(panel) != len(_BLS_SERIES)):
                raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
            for series_row in panel:
                series_id = series_row["series_id"]
                metric, expected_unit = _BLS_SERIES[series_id]
                state = series_row.get("state")
                if state == "SOURCE_HOLD":
                    if any(series_row.get(k) is not None for k in (
                        "value", "period", "previous_period", "previous_value")):
                        raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
                    continue
                if state != "SOURCE_BOUND":
                    raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
                series_value = series_row.get("value")
                series_period = series_row.get("period")
                reference = series_row.get("source_reference")
                if (not isinstance(series_value, str) or not _NUMBER.fullmatch(series_value)
                        or not isinstance(series_period, str) or not _BLS_PERIOD.fullmatch(series_period)
                        or series_row.get("unit") != expected_unit
                        or reference not in _ALLOWED_REFERENCES["bls"]):
                    raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
                if series_id == "CUUR0000SA0":
                    meaning = (
                        f"BLS CPI-U all-items index: {series_value} for {series_period}. "
                        "This tracks the consumer price level; the index itself is not an inflation rate."
                    )
                elif series_id == "LNS14000000":
                    meaning = (
                        f"BLS unemployment rate: {series_value}% for {series_period}. "
                        "A higher rate can be consistent with labor-market cooling, but one monthly move is not a recession call."
                    )
                elif series_id == "CES0000000001":
                    meaning = (
                        f"BLS total nonfarm payroll employment level: {series_value} thousand for {series_period}. "
                        "The direction of change helps describe labor demand; it is not a securities signal."
                    )
                else:
                    meaning = (
                        f"BLS PPI final-demand index: {series_value} for {series_period}. "
                        "This tracks producer selling-price pressure and can differ from consumer inflation."
                    )
                observations.append({
                    "source": "bls", "series_id": series_id, "metric": metric,
                    "unit": expected_unit, "source_reference": reference,
                    "source_period": series_period, "retrieved_at": fetched.isoformat(),
                    "value": series_value, "interpretation": meaning,
                    "research_only": True, "quote_verified": False,
                    "execution_authorized": False,
                })
                prior_period = series_row.get("previous_period")
                prior_value = series_row.get("previous_value")
                if (prior_period is None) != (prior_value is None):
                    raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
                if prior_period is None:
                    continue
                if (not isinstance(prior_period, str) or not _BLS_PERIOD.fullmatch(prior_period)
                        or prior_period >= series_period or not isinstance(prior_value, str)
                        or not _NUMBER.fullmatch(prior_value)):
                    raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
                current_amount, earlier_amount = Decimal(series_value), Decimal(prior_value)
                if current_amount <= 0 or earlier_amount <= 0:
                    raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
                delta = current_amount - earlier_amount
                pct = delta / earlier_amount * Decimal("100")
                movement = "increased" if delta > 0 else "decreased" if delta < 0 else "was unchanged"
                insight = (
                    f"{metric} {movement} between {prior_period} ({prior_value}) and "
                    f"{series_period} ({series_value}); difference {delta:+,.3f} {expected_unit}; "
                    f"relative change {pct:+.3f}%. This is a same-series comparison, not a causal or trading claim."
                )
                comparisons.append({
                    "source": "bls", "series_id": series_id, "metric": metric,
                    "unit": expected_unit, "source_reference": reference,
                    "earlier_period": prior_period, "later_period": series_period,
                    "earlier_value": prior_value, "later_value": series_value,
                    "difference": str(delta), "relative_change_percent": f"{pct:+.3f}",
                    "direction": "UP" if delta > 0 else "DOWN" if delta < 0 else "UNCHANGED",
                    "insight": insight, "research_only": True,
                    "causality_claimed": False, "quote_verified": False,
                })
            continue
        if key == "bls":
            if (not _NUMBER.fullmatch(value)
                    or not isinstance(period, str)
                    or not _BLS_PERIOD.fullmatch(period)
                    or row.get("unit") != "index"):
                raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
            meaning = (
                "BLS CPI-U all-items NSA index: " + value + " for " + period
                + ". This is an index observation, not an inflation percentage or a securities price."
            )
        elif key == "treasury":
            if (not _NUMBER.fullmatch(value)
                    or not isinstance(period, str)
                    or not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", period)
                    or row.get("unit") != "USD"):
                raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
            meaning = (
                "Treasury Debt to the Penny: total public debt outstanding was "
                + value + " USD on " + period
                + ". This is neither a Treasury yield nor an intraday market price."
            )
        else:
            symbol = row.get("symbol")
            if (not _FIGI.fullmatch(value) or not isinstance(symbol, str)
                    or not _TICKER.fullmatch(symbol) or period is not None
                    or row.get("unit") != "FIGI"):
                raise ValueError("SOULAANA_EVIDENCE_SHAPE_HOLD")
            meaning = (
                "OpenFIGI maps the requested ticker " + symbol + " to FIGI " + value
                + " in this unique filtered result. It does not independently prove issuer identity or tradability."
            )
        # Soulaana compares two actual observations from the SAME approved
        # source response. A period comparison is research, never a quote or
        # a claim that the change caused any move in a stock or option.
        prior_period = row.get("previous_period")
        prior_value = row.get("previous_value")
        if key in {"bls", "treasury"}:
            if (prior_period is None) != (prior_value is None):
                raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
            if prior_period is not None:
                period_rule = _BLS_PERIOD if key == "bls" else re.compile(r"^20\d{2}-\d{2}-\d{2}$")
                if (not isinstance(prior_period, str) or not period_rule.fullmatch(prior_period)
                        or prior_period >= period or not isinstance(prior_value, str)
                        or not _NUMBER.fullmatch(prior_value)):
                    raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
                current_amount, earlier_amount = Decimal(value), Decimal(prior_value)
                if current_amount <= 0 or earlier_amount <= 0:
                    raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
                delta = current_amount - earlier_amount
                pct = delta / earlier_amount * Decimal("100")
                movement = "increased" if delta > 0 else "decreased" if delta < 0 else "was unchanged"
                label = "CPI-U index" if key == "bls" else "Total public debt"
                unit_label = "index points" if key == "bls" else "USD"
                insight = (
                    f"{label} {movement} between {prior_period} ({prior_value}) and "
                    f"{period} ({value}): difference {delta:+,.2f} {unit_label}; "
                    f"relative change {pct:+.3f}%. This compares two source-reported "
                    "observations; it does not establish a release time, an "
                    "investment signal, or a causal relationship."
                )
                comparisons.append({
                    "source": key,
                    "source_reference": row["source_reference"],
                    "earlier_period": prior_period,
                    "later_period": period,
                    "earlier_value": prior_value,
                    "later_value": value,
                    "difference": str(delta),
                    "relative_change_percent": f"{pct:+.3f}",
                    "direction": "UP" if delta > 0 else "DOWN" if delta < 0 else "UNCHANGED",
                    "insight": insight,
                    "research_only": True,
                    "causality_claimed": False,
                    "quote_verified": False,
                })
        elif prior_period is not None or prior_value is not None:
            raise ValueError("SOULAANA_COMPARISON_SHAPE_HOLD")
        observations.append({
            "source": key,
            "source_reference": row["source_reference"],
            "source_period": period,
            "retrieved_at": fetched.isoformat(),
            "value": value,
            "interpretation": meaning,
            "research_only": True,
            "quote_verified": False,
            "execution_authorized": False,
        })
    directions = {
        item.get("series_id"): item.get("direction")
        for item in comparisons if item.get("source") == "bls" and item.get("series_id")
    }
    cpi_dir, ppi_dir = directions.get("CUUR0000SA0"), directions.get("WPUFD4")
    unemployment_dir = directions.get("LNS14000000")
    payroll_dir = directions.get("CES0000000001")
    if cpi_dir and ppi_dir:
        if cpi_dir == ppi_dir == "UP":
            inflation_story = (
                "Consumer and producer price indexes both rose versus their prior source periods. "
                "That is broad price-pressure context, not proof that inflation will accelerate."
            )
        elif cpi_dir == ppi_dir == "DOWN":
            inflation_story = (
                "Consumer and producer price indexes both fell versus their prior source periods. "
                "That is broad cooling context, not proof of sustained disinflation."
            )
        else:
            inflation_story = (
                "Consumer and producer price directions disagree. Upstream and consumer price pressure "
                "are not moving together in this snapshot, so I would not compress them into one inflation story."
            )
    else:
        inflation_story = "I do not yet have two-period CPI and PPI comparisons together, so the inflation picture is incomplete."

    if unemployment_dir and payroll_dir:
        if unemployment_dir == "UP" and payroll_dir == "DOWN":
            labor_story = (
                "Unemployment rose while payroll employment fell. Both comparisons point toward softer labor conditions, "
                "but they remain one-period official observations rather than a forecast."
            )
        elif unemployment_dir == "DOWN" and payroll_dir == "UP":
            labor_story = (
                "Unemployment fell while payroll employment rose. Both comparisons point toward firmer labor conditions, "
                "but they do not establish how markets should react."
            )
        else:
            labor_story = (
                "Unemployment and payrolls are giving a mixed labor signal. I would keep both visible instead of forcing a single label."
            )
    else:
        labor_story = "I do not yet have both unemployment and payroll comparisons, so the labor picture is incomplete."

    tensions = []
    if cpi_dir == "UP" and ppi_dir == "DOWN":
        tensions.append("Consumer prices rose while producer final-demand prices fell.")
    elif cpi_dir == "DOWN" and ppi_dir == "UP":
        tensions.append("Consumer prices fell while producer final-demand prices rose.")
    if unemployment_dir == "UP" and payroll_dir == "UP":
        tensions.append("Unemployment and payroll employment both rose; those measures can move together for different labor-force reasons.")
    elif unemployment_dir == "DOWN" and payroll_dir == "DOWN":
        tensions.append("Unemployment and payroll employment both fell; that combination needs labor-force participation/context before interpretation.")

    macro_explanation = {
        "state": "SOURCE_BOUND_DIRECTIONAL_CONTEXT_ONLY" if directions else "INSUFFICIENT_COMPARISONS",
        "inflation": inflation_story,
        "labor": labor_story,
        "why_it_matters": (
            "Inflation and labor conditions can change rate expectations, discount rates and earnings assumptions. "
            "I can explain that transmission path, but these observations alone do not prove a market move or authorize a trade."
        ),
        "tensions": tensions,
        "what_would_change_my_read": [
            "A newer BLS release that reverses one or more series directions.",
            "BEA real-growth and price-index context that confirms or conflicts with the BLS picture.",
            "Current entitled market prices and options liquidity showing how the market is actually repricing.",
            "Issuer-specific SEC evidence that connects macro context to the company being reviewed.",
        ],
        "causality_claimed": False,
        "trade_signal_created": False,
    }

    return {
        "schema": "OB_SOULAANA_KEYLESS_EVIDENCE_V1",
        "channel": "SOULAANA_REVIEWED_PUBLIC_RESEARCH",
        "as_of": now.isoformat(),
        "symbol": packet.get("symbol"),
        "source_register": statuses,
        "observations": observations,
        "observation_count": len(observations),
        # This is a calculated, source-bound examination of period changes,
        # not merely a static source-register sentence or an LLM-generated fact.
        "comparisons": comparisons,
        "comparison_count": len(comparisons),
        "macro_explanation": macro_explanation,
        "what_changed": (
            f"I compared {len(comparisons)} approved source series against their "
            "earlier published observations. Read each source period and difference below."
            if comparisons else
            "No validated two-period comparison is available under current source AI-use reviews."
        ),
        "what_needs_investigation": (
            "Inflation, labor and federal debt are different measures at different "
            "source periods; agreement can strengthen context but cannot establish causality. "
            "For a specific ticker, inspect the separate SEC issuer evidence and "
            "wait for independently licensed stock/options quote truth."
        ),
        "cross_source_causality_claimed": False,
        "interpretation": (
            "Source-cited, period-bound official reference observations are available."
            if observations else
            "No keyless source currently has both validated evidence and explicit AI-use review."
        ),
        "bls_attribution": (
            "BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov."
            if any(x["source"] == "bls" for x in observations) else None
        ),
        "source_specific_ai_use_approved": bool(observations),
        "blanket_ai_authority": False,
        "external_model_called": False,
        "live_quote_verified": False,
        "candidate_admitted": False,
        "broker_execution_authorized": False,
        "capital_authorized": False,
        "public_brokerage_auth_inferred": False,
    }
