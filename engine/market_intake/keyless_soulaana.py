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
    "treasury": ("US Treasury", "Record-dated fiscal context is available; the same reviewed Treasury lane may also carry official daily par-yield context. Neither is an executable quote."),
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
_TREASURY_RATE_REFERENCE = "https://home.treasury.gov/treasury-daily-interest-rate-xml-feed"
_BLS_SERIES = {
    "CUUR0000SA0": ("CPI-U all items", "index"),
    "LNS14000000": ("Unemployment rate", "percent"),
    "CES0000000001": ("Total nonfarm payroll employment", "thousands"),
    "WPUFD4": ("PPI final demand", "index"),
}
_ALLOWED_REFERENCES = {
    "bls": frozenset({_REFERENCES["bls"], _BLS_BULK_REFERENCE, _BLS_V2_REFERENCE}),
    "treasury": frozenset({_REFERENCES["treasury"], _TREASURY_RATE_REFERENCE}),
    "openfigi": frozenset({_REFERENCES["openfigi"]}),
}
_NUMBER = re.compile(r"^\d{1,43}(?:\.\d{1,9})?$")
_SIGNED_NUMBER = re.compile(r"^-?\d{1,5}(?:\.\d{1,4})?$")
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
    rates_read = None
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
            rates = row.get("rates")
            if not isinstance(rates, dict):
                raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
            if (rates.get("source") != "US Treasury"
                    or rates.get("product") != "DAILY_PAR_YIELD_CURVES"
                    or rates.get("source_reference") != _TREASURY_RATE_REFERENCE
                    or rates.get("intraday") is not False
                    or rates.get("executable_quote") is not False
                    or rates.get("broker_execution_authorized") is not False):
                raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
            if rates.get("state") in {"SOURCE_HOLD", "NOT_ENABLED"}:
                if any(rates.get(name) is not None for name in ("nominal", "real", "derived")):
                    raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                rates_read = {"state": rates["state"]}
            elif rates.get("state") == "SOURCE_BOUND":
                nominal, real, derived = rates.get("nominal"), rates.get("real"), rates.get("derived")
                if not all(isinstance(item, dict) for item in (nominal, real, derived)):
                    raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                date_rule = re.compile(r"^20\d{2}-\d{2}-\d{2}$")
                if (not date_rule.fullmatch(str(nominal.get("date", "")))
                        or not date_rule.fullmatch(str(nominal.get("previous_date", "")))
                        or nominal["previous_date"] >= nominal["date"]
                        or not date_rule.fullmatch(str(real.get("date", "")))
                        or not date_rule.fullmatch(str(real.get("previous_date", "")))
                        or real["previous_date"] >= real["date"]):
                    raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                expected = (
                    (nominal.get("yields_percent"), ("2Y", "5Y", "10Y", "30Y")),
                    (nominal.get("previous_yields_percent"), ("2Y", "5Y", "10Y", "30Y")),
                    (real.get("yields_percent"), ("5Y", "10Y", "30Y")),
                    (real.get("previous_yields_percent"), ("5Y", "10Y", "30Y")),
                )
                for values, keys in expected:
                    if not isinstance(values, dict) or tuple(values) != keys:
                        raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                    for raw_rate in values.values():
                        if (not isinstance(raw_rate, str) or not _SIGNED_NUMBER.fullmatch(raw_rate)
                                or not Decimal("-20") < Decimal(raw_rate) < Decimal("30")):
                            raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                if (derived.get("curve_shape") not in {"INVERTED", "POSITIVE", "NEAR_FLAT"}
                        or derived.get("curve_change") not in {"STEEPENED", "FLATTENED", "LITTLE_CHANGED"}
                        or derived.get("breakeven_is_simple_approximation") is not True):
                    raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                for name in (
                    "two_year_change_bp", "ten_year_change_bp", "thirty_year_change_bp",
                    "real_ten_year_change_bp", "two_ten_spread_bp",
                    "previous_two_ten_spread_bp",
                ):
                    if not isinstance(derived.get(name), str) or not _SIGNED_NUMBER.fullmatch(derived[name]):
                        raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                for name in (
                    "ten_year_breakeven_percent", "previous_ten_year_breakeven_percent",
                    "breakeven_change_bp",
                ):
                    raw_metric = derived.get(name)
                    if raw_metric is not None and (
                            not isinstance(raw_metric, str) or not _SIGNED_NUMBER.fullmatch(raw_metric)):
                        raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                if (derived.get("ten_year_breakeven_percent") is None) != (
                        derived.get("breakeven_date") is None):
                    raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
                rates_read = {
                    "state": "SOURCE_BOUND",
                    "source_reference": _TREASURY_RATE_REFERENCE,
                    "nominal_date": nominal["date"],
                    "two_year_percent": nominal["yields_percent"]["2Y"],
                    "ten_year_percent": nominal["yields_percent"]["10Y"],
                    "thirty_year_percent": nominal["yields_percent"]["30Y"],
                    "real_ten_year_percent": real["yields_percent"]["10Y"],
                    "two_year_change_bp": derived["two_year_change_bp"],
                    "ten_year_change_bp": derived["ten_year_change_bp"],
                    "real_ten_year_change_bp": derived["real_ten_year_change_bp"],
                    "two_ten_spread_bp": derived["two_ten_spread_bp"],
                    "curve_shape": derived["curve_shape"],
                    "curve_change": derived["curve_change"],
                    "ten_year_breakeven_percent": derived.get("ten_year_breakeven_percent"),
                    "breakeven_change_bp": derived.get("breakeven_change_bp"),
                    "breakeven_is_simple_approximation": True,
                }
            else:
                raise ValueError("SOULAANA_TREASURY_RATE_HOLD")
            meaning = (
                "Treasury Debt to the Penny: total public debt outstanding was "
                + value + " USD on " + period
                + ". The nested rate context is a separate official daily close; neither is an intraday executable price."
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

    if rates_read and rates_read.get("state") == "SOURCE_BOUND":
        two_change = Decimal(rates_read["two_year_change_bp"])
        ten_change = Decimal(rates_read["ten_year_change_bp"])
        real_change = Decimal(rates_read["real_ten_year_change_bp"])
        rate_word = lambda number: "rose" if number > 0 else "fell" if number < 0 else "was unchanged"
        rates_story = (
            f"At Treasury's {rates_read['nominal_date']} official daily close, the 2-year yield was "
            f"{rates_read['two_year_percent']}% and the 10-year was {rates_read['ten_year_percent']}%. "
            f"The 2-year {rate_word(two_change)} {abs(two_change)} bp and the 10-year "
            f"{rate_word(ten_change)} {abs(ten_change)} bp from the prior publication. "
            f"The 2s10s spread is {rates_read['two_ten_spread_bp']} bp; the curve is "
            f"{rates_read['curve_shape'].lower().replace('_', ' ')} and "
            f"{rates_read['curve_change'].lower().replace('_', ' ')} versus the prior close."
        )
        real_yield_story = (
            f"The 10-year real/TIPS yield is {rates_read['real_ten_year_percent']}%; it "
            f"{rate_word(real_change)} {abs(real_change)} bp from its prior Treasury publication. "
            "Real yields are discount-rate context, not an equity or option quote."
        )
        if rates_read.get("ten_year_breakeven_percent") is not None:
            be_change = rates_read.get("breakeven_change_bp")
            inflation_comp_story = (
                f"The simple 10-year nominal-minus-real breakeven approximation is "
                f"{rates_read['ten_year_breakeven_percent']}%."
            )
            if be_change is not None:
                be_delta = Decimal(be_change)
                inflation_comp_story += (
                    f" It {rate_word(be_delta)} {abs(be_delta)} bp from the prior matched Treasury close."
                )
            inflation_comp_story += (
                " This is market inflation-compensation context, not CPI and not a literal inflation forecast."
            )
        else:
            inflation_comp_story = (
                "Nominal and real Treasury observations do not share the same latest date, "
                "so I am withholding the breakeven approximation."
            )
        rates_explanation = {
            **rates_read,
            "rates_story": rates_story,
            "real_yield_story": real_yield_story,
            "inflation_compensation_story": inflation_comp_story,
            "causality_claimed": False,
            "trade_signal_created": False,
        }
    else:
        rates_explanation = {
            "state": (
                "SOURCE_HOLD"
                if rates_read and rates_read.get("state") == "SOURCE_HOLD"
                else "NOT_AVAILABLE"
            ),
            "rates_story": "Official Treasury daily yield-curve context is not available in this read.",
            "real_yield_story": "Real-yield context is not available in this read.",
            "inflation_compensation_story": "No breakeven approximation is available without matched official nominal and real Treasury observations.",
            "causality_claimed": False,
            "trade_signal_created": False,
        }

    if rates_explanation.get("state") == "SOURCE_BOUND":
        be_change_raw = rates_explanation.get("breakeven_change_bp")
        if cpi_dir == ppi_dir == "UP" and be_change_raw is not None and Decimal(be_change_raw) < 0:
            tensions.append(
                "BLS consumer and producer price indexes rose over their source periods while the Treasury breakeven approximation fell at the latest matched daily close; the horizons differ, so I would treat that as a tension to investigate rather than a contradiction."
            )
        elif cpi_dir == ppi_dir == "DOWN" and be_change_raw is not None and Decimal(be_change_raw) > 0:
            tensions.append(
                "BLS consumer and producer price indexes fell over their source periods while the Treasury breakeven approximation rose at the latest matched daily close; the horizons differ, so I would investigate rather than force one inflation label."
            )

    macro_explanation = {
        "state": "SOURCE_BOUND_DIRECTIONAL_CONTEXT_ONLY" if directions else "INSUFFICIENT_COMPARISONS",
        "inflation": inflation_story,
        "labor": labor_story,
        "rates": rates_explanation,
        "why_it_matters": (
            "Inflation and labor conditions can change rate expectations; nominal yields, real yields and curve shape show how Treasury markets are pricing parts of that environment at the official daily close. "
            "I can explain those relationships, but correlation across different source periods does not prove causality or authorize a trade."
        ),
        "tensions": tensions,
        "what_would_change_my_read": [
            "A newer BLS release that reverses one or more series directions.",
            "BEA real-growth and price-index context that confirms or conflicts with the BLS picture.",
            "A newer Treasury close reversing the yield, real-yield, curve or breakeven move.",
            "Current entitled equity/options prices and liquidity showing how the security itself is actually repricing.",
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
