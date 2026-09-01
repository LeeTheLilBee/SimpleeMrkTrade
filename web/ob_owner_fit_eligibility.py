from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Optional
import json
import math
import re


SCHEMA_VERSION = "OB_OWNER_FIT_ELIGIBILITY_V1"
SERVICE_VERSION = "OBRISK006_010_OWNER_FIT_CANDIDATE_ELIGIBILITY"

BUCKETS = ("NOW", "WATCH", "NOT_YET")

BAD_SOURCE_TOKENS = (
    "fallback",
    "preview",
    "demo",
    "sample",
    "mock",
    "fixture",
    "synthetic",
    "seed",
    "bootstrap",
)

NOT_YET_STATE_TOKENS = (
    "reject",
    "rejected",
    "blocked",
    "invalid",
    "guarded",
    "stale",
    "quarantined",
    "not_yet",
    "not yet",
    "not-yet",
)

POSITIVE_STATE_TOKENS = (
    "approved",
    "ready",
    "qualified",
    "actionable",
    "now",
)

GROWTH_EXPLANATIONS = {
    "PRESERVE": (
        "Capital-protection posture is bound. OB stays highly selective "
        "without inventing a return threshold."
    ),
    "STEADY": (
        "Controlled/repeatable growth posture is bound. No promised-return "
        "threshold is created."
    ),
    "GROWTH": (
        "Growth posture is bound. Opportunities may advance only inside the "
        "independently selected risk envelope."
    ),
    "AGGRESSIVE_GROWTH": (
        "Aggressive-growth posture is bound, but it cannot widen or override "
        "the selected risk envelope."
    ),
    "CUSTOM": (
        "Owner-defined growth posture is bound. No return target is inferred "
        "from the label."
    ),
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def stable_hash(value: Any) -> str:
    return sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def _object(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    result = str(value).strip()
    return result if result else fallback


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1].strip()
        try:
            number = float(cleaned)
        except Exception:
            return None
        return number if math.isfinite(number) else None
    return None


def _first(source: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in source and source.get(key) not in (None, ""):
            return source.get(key)
    return None


def _bool_first(source: Dict[str, Any], *keys: str) -> Optional[bool]:
    for key in keys:
        value = source.get(key)
        if isinstance(value, bool):
            return value
    return None


def _percentage_points(
    value: Any,
    *,
    ratio_ceiling: float,
) -> Dict[str, Any]:
    number = _number(value)
    if number is None:
        return {
            "value": None,
            "normalization": "missing",
        }

    if 0 <= abs(number) <= ratio_ceiling:
        return {
            "value": round(number * 100.0, 6),
            "normalization": "ratio_to_percentage_points",
        }

    return {
        "value": round(number, 6),
        "normalization": "percentage_points_passthrough",
    }


def _minutes(value: Any) -> Optional[int]:
    number = _number(value)
    if number is not None:
        return int(round(number))

    text = _text(value).lower()
    if not text:
        return None

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|m|hours?|hrs?|h|days?|d)\b",
        text,
    )
    if not matches:
        return None

    values = []
    for raw_number, unit in matches:
        amount = float(raw_number)
        if unit.startswith(("m", "min")):
            factor = 1
        elif unit.startswith(("h", "hr", "hour")):
            factor = 60
        else:
            factor = 1440
        values.append(amount * factor)

    if not values:
        return None

    # For a range such as "1-2 days", use the upper bound.
    return int(round(max(values)))


def _check_upper(
    *,
    check_id: str,
    actual: Optional[float],
    limit: Any,
    unit: str,
    evidence_source: str,
    deferred_when_missing: bool = True,
) -> Dict[str, Any]:
    numeric_limit = _number(limit)
    if numeric_limit is None:
        raise ValueError(f"Risk envelope missing numeric limit: {check_id}")

    if actual is None:
        return {
            "check_id": check_id,
            "status": "DEFERRED" if deferred_when_missing else "WATCH",
            "actual": None,
            "limit": numeric_limit,
            "unit": unit,
            "evidence_source": evidence_source,
            "reason": "source_evidence_not_available",
        }

    passed = float(actual) <= float(numeric_limit)
    return {
        "check_id": check_id,
        "status": "PASS" if passed else "FAIL",
        "actual": round(float(actual), 6),
        "limit": round(float(numeric_limit), 6),
        "unit": unit,
        "evidence_source": evidence_source,
        "reason": "within_limit" if passed else "upper_limit_exceeded",
    }


def _check_minimum(
    *,
    check_id: str,
    actual: Optional[float],
    limit: Any,
    unit: str,
    evidence_source: str,
    deferred_when_missing: bool = False,
) -> Dict[str, Any]:
    numeric_limit = _number(limit)
    if numeric_limit is None:
        raise ValueError(f"Risk envelope missing numeric limit: {check_id}")

    if actual is None:
        return {
            "check_id": check_id,
            "status": "DEFERRED" if deferred_when_missing else "WATCH",
            "actual": None,
            "limit": numeric_limit,
            "unit": unit,
            "evidence_source": evidence_source,
            "reason": "source_evidence_not_available",
        }

    passed = float(actual) >= float(numeric_limit)
    return {
        "check_id": check_id,
        "status": "PASS" if passed else "FAIL",
        "actual": round(float(actual), 6),
        "limit": round(float(numeric_limit), 6),
        "unit": unit,
        "evidence_source": evidence_source,
        "reason": "meets_minimum" if passed else "minimum_requirement_not_met",
    }


def _market_truth_check(intent: Dict[str, Any]) -> Dict[str, Any]:
    candidate = _object(intent.get("candidate"))
    raw = _object(candidate.get("source_payload"))

    source = _text(
        candidate.get("source")
        or _first(raw, "candidate_source", "source", "data_source"),
        "unlabeled_canonical_candidate",
    )
    source_lower = source.lower()

    hard_reasons: List[str] = []
    watch_reasons: List[str] = []

    for token in BAD_SOURCE_TOKENS:
        if token in source_lower:
            hard_reasons.append(f"QUARANTINED_SOURCE_TOKEN:{token}")

    explicit_flags = {
        "verified": _bool_first(raw, "verified"),
        "current_eligible": _bool_first(raw, "current_eligible"),
        "display_eligible": _bool_first(raw, "display_eligible"),
        "source_backed": _bool_first(raw, "source_backed"),
    }
    for name, value in explicit_flags.items():
        if value is False:
            hard_reasons.append(f"MARKET_TRUTH_FLAG_FALSE:{name}")

    freshness_text = " ".join(
        _text(_first(raw, key))
        for key in ("freshness", "projection_status", "source_status")
        if _first(raw, key) not in (None, "")
    ).lower()

    if any(
        token in freshness_text
        for token in ("stale", "guarded", "quarantined", "invalid")
    ):
        hard_reasons.append("MARKET_TRUTH_NOT_CURRENT")

    state_text = " ".join(
        _text(value)
        for value in (
            candidate.get("actionable_state"),
            _first(
                raw,
                "actionable_state",
                "status",
                "state",
                "priority",
                "decision",
                "recommendation_state",
                "candidate_state",
            ),
        )
        if value not in (None, "")
    ).lower()

    if any(token in state_text for token in NOT_YET_STATE_TOKENS):
        hard_reasons.append("SOURCE_STATE_NOT_YET")

    explicit_actionable = _bool_first(raw, "actionable")
    positive_state = (
        explicit_actionable is True
        or any(token in state_text for token in POSITIVE_STATE_TOKENS)
    )

    return {
        "source": source,
        "source_fingerprint": stable_hash(raw),
        "explicit_flags": explicit_flags,
        "state_text": state_text,
        "source_positive_actionability": positive_state,
        "hard_reasons": sorted(set(hard_reasons)),
        "watch_reasons": sorted(set(watch_reasons)),
        "market_truth_mutated": False,
        "market_score_recalculated": False,
    }


def _instrument_kind(intent: Dict[str, Any]) -> str:
    candidate = _object(intent.get("candidate"))
    raw = _object(candidate.get("source_payload"))

    text = " ".join(
        _text(value)
        for value in (
            _first(
                raw,
                "instrument_type",
                "instrument",
                "asset_class",
                "vehicle_type",
                "vehicle",
                "product_type",
            ),
            candidate.get("strategy"),
            candidate.get("direction"),
        )
        if value not in (None, "")
    ).lower()

    if any(token in text for token in ("stock", "equity", "shares", "share")):
        return "STOCK"

    if any(token in text for token in ("option", "call", "put")):
        return "OPTION"

    return "UNKNOWN"


def _collect_option_contracts(intent: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidate = _object(intent.get("candidate"))
    symbol = _text(candidate.get("symbol")).upper()
    research = _object(intent.get("options_research"))

    rows: List[Dict[str, Any]] = []

    for key in ("ranked_contracts", "research_contracts"):
        for row in _list(research.get(key)):
            if isinstance(row, dict):
                rows.append(deepcopy(row))

    by_symbol = _object(research.get("options_by_symbol"))
    for key in (symbol, symbol.lower()):
        for row in _list(by_symbol.get(key)):
            if isinstance(row, dict):
                rows.append(deepcopy(row))

    payload = _object(research.get("research_payload"))
    for key in ("ranked_contracts", "top_ranked_contracts", "research_contracts"):
        for row in _list(payload.get(key)):
            if isinstance(row, dict):
                rows.append(deepcopy(row))

    unique = []
    seen = set()

    for index, row in enumerate(rows):
        underlying = _text(
            _first(row, "symbol", "underlying_symbol", "underlying", "ticker")
        ).upper()

        if underlying and symbol and underlying != symbol:
            continue

        identity = {
            "contract_symbol": _first(
                row,
                "contract_symbol",
                "contractSymbol",
                "option_symbol",
                "occ_symbol",
            ),
            "symbol": underlying or symbol,
            "right": _first(row, "right", "option_type", "type"),
            "strike": _first(row, "strike", "strike_price"),
            "expiration": _first(
                row,
                "expiration",
                "expiry",
                "expiration_date",
            ),
            "source_order": index + 1,
        }
        key = stable_hash(row)
        if key in seen:
            continue
        seen.add(key)
        row["_obrisk_source_order"] = index + 1
        unique.append(row)

    return unique


def _contract_identifier(
    row: Dict[str, Any],
    *,
    symbol: str,
) -> str:
    explicit = _text(
        _first(
            row,
            "contract_symbol",
            "contractSymbol",
            "option_symbol",
            "occ_symbol",
        )
    )
    if explicit:
        return explicit

    return "research_contract_" + stable_hash(
        {
            "symbol": symbol,
            "right": _first(row, "right", "option_type", "type"),
            "strike": _first(row, "strike", "strike_price"),
            "expiration": _first(
                row,
                "expiration",
                "expiry",
                "expiration_date",
            ),
            "source_order": row.get("_obrisk_source_order"),
        }
    )[:16]


def _contract_evaluation(
    row: Dict[str, Any],
    *,
    symbol: str,
    limits: Dict[str, Any],
) -> Dict[str, Any]:
    bid = _number(_first(row, "bid"))
    ask = _number(_first(row, "ask"))

    raw_spread_pct = _first(
        row,
        "spread_pct",
        "spreadPercent",
        "spread_percent",
    )

    if raw_spread_pct not in (None, ""):
        normalized_spread = _percentage_points(
            raw_spread_pct,
            ratio_ceiling=1.0,
        )
        spread_source = "explicit_spread_pct"
    elif (
        bid is not None
        and ask is not None
        and ask > 0
        and ask >= bid
    ):
        normalized_spread = {
            "value": round(((ask - bid) / ask) * 100.0, 6),
            "normalization": "derived_bid_ask_percentage_points",
        }
        spread_source = "derived_bid_ask"
    else:
        normalized_spread = {
            "value": None,
            "normalization": "missing",
        }
        spread_source = "missing"

    raw_iv = _first(
        row,
        "implied_volatility",
        "impliedVolatility",
        "iv",
    )
    normalized_iv = _percentage_points(
        raw_iv,
        ratio_ceiling=3.0,
    )

    volume = _number(_first(row, "volume"))
    open_interest = _number(
        _first(row, "open_interest", "openInterest", "oi")
    )

    checks = [
        _check_upper(
            check_id="max_spread_pct",
            actual=normalized_spread["value"],
            limit=limits["max_spread_pct"],
            unit="percentage_points",
            evidence_source=spread_source,
            deferred_when_missing=False,
        ),
        _check_minimum(
            check_id="min_option_volume",
            actual=volume,
            limit=limits["min_option_volume"],
            unit="contracts",
            evidence_source="option_research",
            deferred_when_missing=False,
        ),
        _check_minimum(
            check_id="min_open_interest",
            actual=open_interest,
            limit=limits["min_open_interest"],
            unit="contracts",
            evidence_source="option_research",
            deferred_when_missing=False,
        ),
        _check_upper(
            check_id="max_implied_volatility_pct",
            actual=normalized_iv["value"],
            limit=limits["max_implied_volatility_pct"],
            unit="percentage_points",
            evidence_source="option_research",
            deferred_when_missing=False,
        ),
    ]

    source_backed = row.get("source_backed")
    current_market_truth = row.get("current_market_truth")
    source_executable = row.get("is_executable")

    diagnostics = []

    if source_backed is False:
        diagnostics.append(
            {
                "check_id": "source_backed_option_research",
                "status": "FAIL",
                "reason": "option_research_explicitly_not_source_backed",
            }
        )

    if current_market_truth is False:
        diagnostics.append(
            {
                "check_id": "current_option_market_truth",
                "status": "WATCH",
                "reason": "current_market_truth_not_available",
            }
        )

    if source_executable is False:
        diagnostics.append(
            {
                "check_id": "source_execution_diagnostic",
                "status": "FAIL",
                "reason": "source_marked_contract_non_executable",
            }
        )

    checks.extend(diagnostics)

    statuses = {item.get("status") for item in checks}

    if "FAIL" in statuses:
        bucket = "NOT_YET"
    elif "WATCH" in statuses:
        bucket = "WATCH"
    else:
        bucket = "NOW"

    return {
        "contract_id": _contract_identifier(row, symbol=symbol),
        "source_order": row.get("_obrisk_source_order"),
        "bucket": bucket,
        "selected": False,
        "selection_authority": "OWNER",
        "automatic_contract_selection": False,
        "brokerage_execution": False,
        "automatic_execution": False,
        "evidence": {
            "spread_pct": normalized_spread,
            "volume": volume,
            "open_interest": open_interest,
            "implied_volatility_pct": normalized_iv,
            "source_backed": source_backed,
            "current_market_truth": current_market_truth,
            "source_executable_diagnostic": source_executable,
        },
        "checks": checks,
    }


def _option_gate(
    intent: Dict[str, Any],
    *,
    limits: Dict[str, Any],
) -> Dict[str, Any]:
    candidate = _object(intent.get("candidate"))
    symbol = _text(candidate.get("symbol")).upper()
    kind = _instrument_kind(intent)
    contracts = _collect_option_contracts(intent)

    if kind == "STOCK" and not contracts:
        return {
            "status": "NOT_APPLICABLE_STOCK_FALLBACK",
            "bucket": "NOW",
            "instrument_kind": kind,
            "research_contract_count": 0,
            "passing_contract_count": 0,
            "watch_contract_count": 0,
            "failing_contract_count": 0,
            "contracts": [],
            "contract_selected": False,
            "reason_codes": [],
        }

    if not contracts:
        return {
            "status": "OPTION_RESEARCH_INCOMPLETE",
            "bucket": "WATCH",
            "instrument_kind": kind,
            "research_contract_count": 0,
            "passing_contract_count": 0,
            "watch_contract_count": 0,
            "failing_contract_count": 0,
            "contracts": [],
            "contract_selected": False,
            "reason_codes": ["OPTION_RESEARCH_CONTRACTS_UNAVAILABLE"],
        }

    evaluations = [
        _contract_evaluation(
            row,
            symbol=symbol,
            limits=limits,
        )
        for row in contracts
    ]

    passing = sum(
        1 for item in evaluations if item["bucket"] == "NOW"
    )
    watching = sum(
        1 for item in evaluations if item["bucket"] == "WATCH"
    )
    failing = sum(
        1 for item in evaluations if item["bucket"] == "NOT_YET"
    )

    if passing > 0:
        bucket = "NOW"
        status = "AT_LEAST_ONE_RESEARCH_CONTRACT_FITS"
        reasons: List[str] = []
    elif watching > 0:
        bucket = "WATCH"
        status = "RESEARCH_CONTRACT_EVIDENCE_INCOMPLETE"
        reasons = ["OPTION_RESEARCH_NEEDS_MORE_EVIDENCE"]
    else:
        bucket = "NOT_YET"
        status = "NO_RESEARCH_CONTRACT_FITS_ENVELOPE"
        reasons = ["NO_OPTION_RESEARCH_CONTRACT_FITS_RISK_ENVELOPE"]

    return {
        "status": status,
        "bucket": bucket,
        "instrument_kind": kind,
        "research_contract_count": len(evaluations),
        "passing_contract_count": passing,
        "watch_contract_count": watching,
        "failing_contract_count": failing,
        "contracts": evaluations,
        "contract_selected": False,
        "selection_authority": "OWNER",
        "automatic_contract_selection": False,
        "reason_codes": reasons,
    }


def _candidate_context_checks(
    intent: Dict[str, Any],
    *,
    limits: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    candidate = _object(intent.get("candidate"))
    raw = _object(candidate.get("source_payload"))

    context = _object(context)

    estimated_loss = _number(
        _first(
            context,
            "estimated_loss_pct",
            "max_loss_pct",
            "loss_pct",
        )
    )
    if estimated_loss is None:
        estimated_loss = _number(
            _first(
                raw,
                "estimated_loss_pct",
                "max_loss_pct",
                "loss_pct",
            )
        )

    allocation = _number(
        _first(
            context,
            "position_allocation_pct",
            "allocation_pct",
            "position_size_pct",
        )
    )
    if allocation is None:
        allocation = _number(
            _first(
                raw,
                "position_allocation_pct",
                "allocation_pct",
                "position_size_pct",
            )
        )

    daily_loss = _number(
        _first(
            context,
            "daily_loss_pct",
            "current_daily_loss_pct",
        )
    )

    open_positions = _number(
        _first(
            context,
            "open_positions_count",
            "open_positions",
        )
    )

    correlated = _number(
        _first(
            context,
            "correlated_exposure_pct",
            "post_trade_correlated_exposure_pct",
        )
    )

    hold_value = _first(
        context,
        "hold_minutes",
        "expected_hold_minutes",
    )
    if hold_value in (None, ""):
        hold_value = _first(
            raw,
            "expected_hold_minutes",
            "hold_minutes",
            "max_hold_minutes",
        )
    if hold_value in (None, ""):
        hold_value = candidate.get("expected_hold")
    hold_minutes = _minutes(hold_value)

    overnight_required = _bool_first(
        context,
        "overnight_required",
        "overnight",
    )
    if overnight_required is None:
        overnight_required = _bool_first(
            raw,
            "overnight_required",
            "overnight",
            "hold_overnight",
        )
    if overnight_required is None and hold_minutes is not None:
        overnight_required = hold_minutes > 390

    checks = [
        _check_upper(
            check_id="max_loss_per_trade_pct",
            actual=estimated_loss,
            limit=limits["max_loss_per_trade_pct"],
            unit="percentage_points",
            evidence_source="candidate_or_evaluation_context",
            deferred_when_missing=True,
        ),
        _check_upper(
            check_id="max_position_allocation_pct",
            actual=allocation,
            limit=limits["max_position_allocation_pct"],
            unit="percentage_points",
            evidence_source="candidate_or_evaluation_context",
            deferred_when_missing=True,
        ),
        _check_upper(
            check_id="daily_loss_cap_pct",
            actual=daily_loss,
            limit=limits["daily_loss_cap_pct"],
            unit="percentage_points",
            evidence_source="evaluation_context",
            deferred_when_missing=True,
        ),
        _check_upper(
            check_id="max_concurrent_positions",
            actual=open_positions,
            limit=limits["max_concurrent_positions"],
            unit="count",
            evidence_source="evaluation_context",
            deferred_when_missing=True,
        ),
        _check_upper(
            check_id="max_correlated_exposure_pct",
            actual=correlated,
            limit=limits["max_correlated_exposure_pct"],
            unit="percentage_points",
            evidence_source="evaluation_context",
            deferred_when_missing=True,
        ),
        _check_upper(
            check_id="max_hold_minutes",
            actual=hold_minutes,
            limit=limits["max_hold_minutes"],
            unit="minutes",
            evidence_source="candidate_or_evaluation_context",
            deferred_when_missing=True,
        ),
    ]

    if overnight_required is None:
        checks.append(
            {
                "check_id": "overnight_allowed",
                "status": "DEFERRED",
                "actual": None,
                "limit": bool(limits["overnight_allowed"]),
                "unit": "boolean",
                "evidence_source": "candidate_or_evaluation_context",
                "reason": "overnight_requirement_not_known",
            }
        )
    elif overnight_required is True and limits["overnight_allowed"] is not True:
        checks.append(
            {
                "check_id": "overnight_allowed",
                "status": "FAIL",
                "actual": True,
                "limit": False,
                "unit": "boolean",
                "evidence_source": "candidate_or_evaluation_context",
                "reason": "overnight_holding_not_allowed",
            }
        )
    else:
        checks.append(
            {
                "check_id": "overnight_allowed",
                "status": "PASS",
                "actual": bool(overnight_required),
                "limit": bool(limits["overnight_allowed"]),
                "unit": "boolean",
                "evidence_source": "candidate_or_evaluation_context",
                "reason": "overnight_policy_satisfied",
            }
        )

    checks.append(
        {
            "check_id": "live_automation_allowed",
            "status": "LOCKED",
            "actual": False,
            "limit": False,
            "unit": "boolean",
            "evidence_source": "owner_risk_envelope",
            "reason": "live_automation_remains_locked",
        }
    )

    failures = [
        item["check_id"]
        for item in checks
        if item.get("status") == "FAIL"
    ]

    deferred = [
        item["check_id"]
        for item in checks
        if item.get("status") == "DEFERRED"
    ]

    return {
        "checks": checks,
        "hard_failures": failures,
        "deferred_execution_context_checks": deferred,
        "execution_context_complete": len(deferred) == 0,
        "candidate_review_may_precede_execution_context": True,
        "execution_authorized": False,
    }


def _growth_context(intent: Dict[str, Any]) -> Dict[str, Any]:
    owner_fit = _object(intent.get("owner_fit"))
    growth_ref = _object(owner_fit.get("growth_objective_ref"))
    candidate = _object(intent.get("candidate"))
    raw = _object(candidate.get("source_payload"))

    key = _text(growth_ref.get("growth_key")).upper()
    label = _text(growth_ref.get("growth_label"), key.title())

    if key not in GROWTH_EXPLANATIONS:
        raise ValueError(
            "Owner growth objective must be bound before eligibility evaluation."
        )

    source_growth = _first(
        raw,
        "growth_objective",
        "growth_posture",
        "growth_fit",
        "opportunity_posture",
    )

    source_alignment = "NOT_EXPLICITLY_SCORED"
    if source_growth not in (None, ""):
        normalized = _text(source_growth).upper().replace(" ", "_")
        source_alignment = (
            "SOURCE_MATCH"
            if key in normalized or label.upper().replace(" ", "_") in normalized
            else "SOURCE_DIFFERENT_POSTURE"
        )

    return {
        "growth_key": key,
        "growth_label": label,
        "description": GROWTH_EXPLANATIONS[key],
        "source_growth_evidence": source_growth,
        "source_alignment": source_alignment,
        "expected_return_target": None,
        "cagr_target": None,
        "profit_target": None,
        "market_score_threshold_created": False,
        "market_score_recalculated": False,
        "canonical_candidate_score": candidate.get("score"),
        "canonical_candidate_rank": candidate.get("rank"),
        "risk_envelope_overridden": False,
    }


def evaluate_owner_fit(
    intent: Dict[str, Any],
    *,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(intent, dict):
        raise ValueError("OBTradeIntent must be an object.")

    account_context = _object(intent.get("account_context"))
    pending = _object(intent.get("owner_fit"))

    if account_context.get("status") != "BOUND":
        raise ValueError(
            "Explicit account context must be BOUND before owner-fit evaluation."
        )

    if account_context.get("explicit_owner_choice") is not True:
        raise ValueError(
            "Owner-fit evaluation requires explicit owner account choice."
        )

    risk_ref = _object(pending.get("risk_envelope_ref"))
    growth_ref = _object(pending.get("growth_objective_ref"))
    account_ref = _object(pending.get("account_policy_ref"))

    if not risk_ref or not growth_ref or not account_ref:
        raise ValueError(
            "Owner operating profile references are incomplete."
        )

    limits = _object(risk_ref.get("effective_limits"))
    required = (
        "max_loss_per_trade_pct",
        "max_position_allocation_pct",
        "daily_loss_cap_pct",
        "max_concurrent_positions",
        "max_spread_pct",
        "min_option_volume",
        "min_open_interest",
        "max_correlated_exposure_pct",
        "max_hold_minutes",
        "overnight_allowed",
        "max_implied_volatility_pct",
        "live_automation_allowed",
    )
    missing = [key for key in required if key not in limits]
    if missing:
        raise ValueError(
            "Risk envelope is missing limits: " + ", ".join(missing)
        )

    if limits.get("live_automation_allowed") is not False:
        raise ValueError(
            "OBRISK006–010 cannot evaluate a profile that enables live automation."
        )

    candidate_before = deepcopy(_object(intent.get("candidate")))
    options_before = deepcopy(_object(intent.get("options_research")))

    market = _market_truth_check(intent)
    option_gate = _option_gate(intent, limits=limits)
    candidate_checks = _candidate_context_checks(
        intent,
        limits=limits,
        context=_object(context),
    )
    growth = _growth_context(intent)

    hard_reasons = list(market["hard_reasons"])
    hard_reasons.extend(candidate_checks["hard_failures"])

    watch_reasons = list(market["watch_reasons"])
    watch_reasons.extend(option_gate.get("reason_codes", []))

    # Growth objective affects fit only when the canonical/source candidate
    # explicitly supplies a growth-posture tag. We never invent a return model
    # or convert the market score into an expected-return promise.
    if growth.get("source_alignment") == "SOURCE_DIFFERENT_POSTURE":
        watch_reasons.append(
            "SOURCE_GROWTH_POSTURE_DIFFERS_FROM_OWNER_OBJECTIVE"
        )

    if option_gate["bucket"] == "NOT_YET":
        hard_reasons.extend(option_gate.get("reason_codes", []))
    elif option_gate["bucket"] == "WATCH":
        watch_reasons.extend(option_gate.get("reason_codes", []))

    hard_reasons = sorted(set(hard_reasons))
    watch_reasons = sorted(set(watch_reasons))

    if hard_reasons:
        bucket = "NOT_YET"
        eligible: Optional[bool] = False
    elif watch_reasons:
        bucket = "WATCH"
        eligible = None
    else:
        bucket = "NOW"
        eligible = True

    if _object(intent.get("candidate")) != candidate_before:
        raise RuntimeError("Owner-fit evaluation mutated canonical candidate truth.")

    if _object(intent.get("options_research")) != options_before:
        raise RuntimeError("Owner-fit evaluation mutated options research truth.")

    material = {
        "schema_version": SCHEMA_VERSION,
        "intent_id": intent.get("intent_id"),
        "candidate_fingerprint": candidate_before.get("candidate_fingerprint"),
        "profile_id": risk_ref.get("profile_id"),
        "profile_revision": risk_ref.get("profile_revision"),
        "profile_hash": risk_ref.get("profile_hash"),
        "account_key": account_context.get("account_key"),
        "growth_key": growth.get("growth_key"),
        "risk_key": risk_ref.get("risk_key"),
        "market": market,
        "option_gate": option_gate,
        "candidate_checks": candidate_checks,
        "context": _object(context),
        "bucket": bucket,
    }
    evaluation_fingerprint = stable_hash(material)

    if bucket == "NOW":
        summary = (
            "This candidate fits the currently evaluable owner-risk envelope "
            "and may advance to owner review. This is not execution authority."
        )
    elif bucket == "WATCH":
        summary = (
            "This candidate is not cleared for owner review yet because "
            "source-backed eligibility evidence is incomplete."
        )
    else:
        summary = (
            "The market setup may still be real, but it does not currently fit "
            "the selected owner envelope or source-currentness requirements."
        )

    owner_fit = {
        "status": bucket,
        "bucket": bucket,
        "evaluated": True,
        "eligible": eligible,
        "authority": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "growth_objective_ref": deepcopy(growth_ref),
        "risk_envelope_ref": deepcopy(risk_ref),
        "account_policy_ref": deepcopy(account_ref),
        "growth_context": growth,
        "market_truth_check": market,
        "risk_checks": candidate_checks,
        "option_research_gate": option_gate,
        "hard_failure_reasons": hard_reasons,
        "watch_reasons": watch_reasons,
        "summary": summary,
        "evaluation_fingerprint": evaluation_fingerprint,
        "market_truth_mutated": False,
        "market_score_recalculated": False,
        "candidate_rank_recalculated": False,
        "contract_selected": False,
        "selection_authority": "OWNER",
        "execution_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "hybrid_execution_authorized": False,
        "automatic_execution_authorized": False,
        "live_auto_locked": True,
    }

    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "bucket": bucket,
        "eligible": eligible,
        "owner_fit": owner_fit,
        "evaluation_fingerprint": evaluation_fingerprint,
        "market_truth_unchanged": True,
        "options_research_unchanged": True,
        "execution_authorized": False,
    }


def owner_fit_eligibility_contract() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_version": SERVICE_VERSION,
        "authority": "OWNER_FIT_CANDIDATE_ELIGIBILITY",
        "input_candidate_authority": "EXISTING_CANONICAL_ENGINE",
        "input_options_authority": "OB_OPTIONS_RESEARCH_V1",
        "input_profile_authority": "OB_OWNER_OPERATING_PROFILE_V1",
        "buckets": list(BUCKETS),
        "market_truth_mutation": False,
        "market_score_recalculation": False,
        "candidate_rank_recalculation": False,
        "expected_return_target": False,
        "profit_guarantee": False,
        "contract_selection": False,
        "selection_authority": "OWNER",
        "execution_authority": False,
        "broker_submission": False,
        "capital_movement": False,
        "hybrid_execution": False,
        "automatic_execution": False,
        "live_auto_locked": True,
        "watch_is_execution_permission": False,
        "now_is_execution_permission": False,
        "not_yet_hides_market_truth": False,
    }
