# engine/options_lifecycle.py

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import math


# =========================================================
# Constants
# =========================================================

LIFECYCLE_NEW = "NEW"
LIFECYCLE_RESEARCH_APPROVED = "RESEARCH_APPROVED"
LIFECYCLE_RESEARCH_REJECTED = "RESEARCH_REJECTED"
LIFECYCLE_EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
LIFECYCLE_EXECUTION_READY = "EXECUTION_READY"
LIFECYCLE_SELECTED = "SELECTED"
LIFECYCLE_ENTERED = "ENTERED"
LIFECYCLE_MANAGING = "MANAGING"
LIFECYCLE_EXIT_READY = "EXIT_READY"
LIFECYCLE_CLOSED = "CLOSED"

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_NONE = "NONE"

DIRECTION_CALL = "CALL"
DIRECTION_PUT = "PUT"
DIRECTION_UNKNOWN = "UNKNOWN"

DECISION_APPROVE = "APPROVE"
DECISION_REJECT = "REJECT"
DECISION_WATCH = "WATCH"
DECISION_WARN = "WARN"

DEFAULT_MAX_SPREAD_PCT = 0.18
DEFAULT_MIN_OI = 100
DEFAULT_MIN_VOLUME = 10
DEFAULT_MIN_DTE = 7
DEFAULT_MAX_DTE = 45
DEFAULT_MIN_DELTA = 0.20
DEFAULT_MAX_DELTA = 0.65
DEFAULT_PAPER_RESERVE_FLOOR = 0.10
DEFAULT_LIVE_RESERVE_FLOOR = 0.20
DEFAULT_MIN_TOTAL_SCORE = 0.40
DEFAULT_TOP_CONTRACTS_TO_KEEP = 5


# =========================================================
# Helpers
# =========================================================

def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize_text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def _normalize_upper(value: Any, default: str = "") -> str:
    return _normalize_text(value, default).upper()


def _days_to_expiry(expiration: str) -> Optional[int]:
    try:
        exp_dt = datetime.fromisoformat(expiration[:10])
        return (exp_dt.date() - datetime.now().date()).days
    except Exception:
        return None


def _mid_price(bid: float, ask: float, last: float) -> float:
    if bid > 0 and ask > 0 and ask >= bid:
        return (bid + ask) / 2.0
    if last > 0:
        return last
    if ask > 0:
        return ask
    return bid


def _spread_pct(bid: float, ask: float, ref_price: float) -> float:
    if ref_price <= 0:
        return 1.0
    if bid <= 0 and ask <= 0:
        return 1.0
    if ask < bid:
        return 1.0
    return (ask - bid) / ref_price


def _score_range(value: float, low: float, high: float, ideal: Optional[float] = None) -> float:
    if value < low or value > high:
        return 0.0
    if ideal is None:
        return 1.0
    width = max((high - low) / 2.0, 1e-9)
    return max(0.0, 1.0 - abs(value - ideal) / width)


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# =========================================================
# Canonical Data Objects
# =========================================================

@dataclass
class OptionContract:
    symbol: str = ""
    underlying: str = ""
    option_symbol: str = ""
    option_type: str = DIRECTION_UNKNOWN
    strike: float = 0.0
    expiration: str = ""
    dte: int = 0

    bid: float = 0.0
    ask: float = 0.0
    last: float = 0.0
    mark: float = 0.0

    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    iv: float = 0.0

    volume: int = 0
    open_interest: int = 0

    spread_pct: float = 1.0
    liquidity_score: float = 0.0
    greek_score: float = 0.0
    structure_score: float = 0.0
    affordability_score: float = 0.0
    total_score: float = 0.0

    rejection_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VehicleDecision:
    symbol: str = ""
    selected_vehicle: str = VEHICLE_NONE
    fallback_vehicle: str = VEHICLE_NONE

    approved: bool = False
    action: str = DECISION_REJECT
    reason: str = ""
    reason_code: str = ""

    contract: Optional[Dict[str, Any]] = None
    contract_score: float = 0.0

    estimated_cost: float = 0.0
    contracts: int = 0
    shares: int = 0

    reserve_check: Dict[str, Any] = field(default_factory=dict)
    top_ranked_contracts: List[Dict[str, Any]] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)


@dataclass
class LifecycleState:
    symbol: str = ""
    strategy: str = ""
    direction: str = DIRECTION_UNKNOWN

    lifecycle_stage: str = LIFECYCLE_NEW
    selected_vehicle: str = VEHICLE_NONE
    fallback_vehicle: str = VEHICLE_NONE

    research_decision: str = DECISION_REJECT
    research_reason: str = ""
    research_reason_code: str = ""

    execution_decision: str = DECISION_REJECT
    execution_reason: str = ""
    execution_reason_code: str = ""

    final_decision: str = DECISION_REJECT
    final_reason: str = ""
    final_reason_code: str = ""

    confidence: str = "UNKNOWN"
    score: float = 0.0

    candidate_size_dollars: float = 0.0
    estimated_cost: float = 0.0
    contracts: int = 0
    shares: int = 0

    contract: Optional[Dict[str, Any]] = None
    reserve_check: Dict[str, Any] = field(default_factory=dict)
    top_ranked_contracts: List[Dict[str, Any]] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)

    entered_at: Optional[str] = None
    exited_at: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    raw: Dict[str, Any] = field(default_factory=dict)


# =========================================================
# Contract Normalization
# =========================================================

def normalize_option_contract(
    contract: Dict[str, Any],
    underlying_symbol: str,
) -> OptionContract:
    bid = _safe_float(contract.get("bid"))
    ask = _safe_float(contract.get("ask"))
    last = _safe_float(contract.get("last"))
    mark = _safe_float(contract.get("mark")) or _mid_price(bid, ask, last)

    expiration = _normalize_text(contract.get("expiration"))
    dte = _safe_int(contract.get("dte"))
    if dte <= 0 and expiration:
        parsed_dte = _days_to_expiry(expiration)
        if parsed_dte is not None:
            dte = parsed_dte

    oc = OptionContract(
        symbol=_normalize_upper(underlying_symbol),
        underlying=_normalize_upper(underlying_symbol),
        option_symbol=_normalize_text(contract.get("option_symbol") or contract.get("contractSymbol")),
        option_type=_normalize_upper(contract.get("option_type") or contract.get("type"), DIRECTION_UNKNOWN),
        strike=_safe_float(contract.get("strike")),
        expiration=expiration,
        dte=dte,
        bid=bid,
        ask=ask,
        last=last,
        mark=mark,
        delta=_safe_float(contract.get("delta")),
        gamma=_safe_float(contract.get("gamma")),
        theta=_safe_float(contract.get("theta")),
        vega=_safe_float(contract.get("vega")),
        iv=_safe_float(contract.get("iv")),
        volume=_safe_int(contract.get("volume")),
        open_interest=_safe_int(contract.get("open_interest") or contract.get("openInterest")),
        raw=dict(contract),
    )

    oc.spread_pct = _spread_pct(oc.bid, oc.ask, oc.mark)
    return oc


# =========================================================
# Contract Scoring
# =========================================================

def score_option_contract(
    contract: OptionContract,
    target_direction: str,
    underlying_price: float,
    max_spread_pct: float = DEFAULT_MAX_SPREAD_PCT,
    min_oi: int = DEFAULT_MIN_OI,
    min_volume: int = DEFAULT_MIN_VOLUME,
    min_dte: int = DEFAULT_MIN_DTE,
    max_dte: int = DEFAULT_MAX_DTE,
    min_delta: float = DEFAULT_MIN_DELTA,
    max_delta: float = DEFAULT_MAX_DELTA,
) -> OptionContract:
    reasons: List[str] = []
    warnings: List[str] = []

    if contract.option_type not in {DIRECTION_CALL, DIRECTION_PUT}:
        reasons.append("invalid_option_type")

    if target_direction in {DIRECTION_CALL, DIRECTION_PUT} and contract.option_type != target_direction:
        reasons.append("direction_mismatch")

    if contract.mark <= 0:
        reasons.append("invalid_price")

    if contract.spread_pct > max_spread_pct:
        reasons.append("spread_too_wide")

    if contract.open_interest < min_oi:
        warnings.append("low_open_interest")

    if contract.volume < min_volume:
        warnings.append("low_volume")

    if contract.dte < min_dte:
        reasons.append("dte_too_short")

    if contract.dte > max_dte:
        warnings.append("dte_longer_than_preferred")

    abs_delta = abs(contract.delta)
    if abs_delta <= 0:
        warnings.append("missing_delta")
    elif abs_delta < min_delta:
        reasons.append("delta_too_low")
    elif abs_delta > max_delta:
        warnings.append("delta_aggressive")

    spread_score = 1.0 - _clamp(contract.spread_pct / max_spread_pct, 0.0, 1.0)
    oi_score = _clamp(contract.open_interest / max(min_oi * 4, 1), 0.0, 1.0)
    volume_score = _clamp(contract.volume / max(min_volume * 5, 1), 0.0, 1.0)
    liquidity_score = (spread_score * 0.5) + (oi_score * 0.3) + (volume_score * 0.2)

    delta_score = _score_range(abs_delta, min_delta, max(0.80, max_delta), ideal=0.35)
    dte_score = _score_range(float(contract.dte), float(min_dte), float(max_dte), ideal=21.0)

    moneyness = 0.0
    if underlying_price > 0 and contract.strike > 0:
        moneyness = abs(contract.strike - underlying_price) / underlying_price

    structure_score = max(0.0, 1.0 - min(moneyness / 0.10, 1.0))
    greek_score = (delta_score * 0.65) + (dte_score * 0.35)

    premium_cost = contract.mark * 100.0
    if premium_cost <= 0:
        affordability_score = 0.0
    else:
        affordability_score = 1.0 / (1.0 + math.log1p(max(premium_cost - 1.0, 0.0)))

    total_score = (
        liquidity_score * 0.40
        + greek_score * 0.30
        + structure_score * 0.20
        + affordability_score * 0.10
    )

    contract.liquidity_score = round(liquidity_score, 4)
    contract.greek_score = round(greek_score, 4)
    contract.structure_score = round(structure_score, 4)
    contract.affordability_score = round(affordability_score, 4)
    contract.total_score = round(total_score, 4)
    contract.rejection_reasons = _dedupe_keep_order(reasons)
    contract.warnings = _dedupe_keep_order(warnings)
    return contract


def rank_option_contracts(
    option_chain: List[Dict[str, Any]],
    underlying_symbol: str,
    target_direction: str,
    underlying_price: float,
    **score_kwargs: Any,
) -> List[OptionContract]:
    ranked: List[OptionContract] = []

    for raw_contract in option_chain or []:
        normalized = normalize_option_contract(raw_contract, underlying_symbol)
        scored = score_option_contract(
            normalized,
            target_direction=target_direction,
            underlying_price=underlying_price,
            **score_kwargs,
        )
        ranked.append(scored)

    ranked.sort(
        key=lambda c: (
            len(c.rejection_reasons) == 0,
            c.total_score,
            c.open_interest,
            c.volume,
        ),
        reverse=True,
    )
    return ranked


def choose_best_option_contract(
    option_chain: List[Dict[str, Any]],
    underlying_symbol: str,
    target_direction: str,
    underlying_price: float,
    min_total_score: float = DEFAULT_MIN_TOTAL_SCORE,
    **score_kwargs: Any,
) -> Tuple[Optional[OptionContract], List[OptionContract]]:
    ranked = rank_option_contracts(
        option_chain=option_chain,
        underlying_symbol=underlying_symbol,
        target_direction=target_direction,
        underlying_price=underlying_price,
        **score_kwargs,
    )

    for contract in ranked:
        if contract.rejection_reasons:
            continue
        if contract.total_score < min_total_score:
            continue
        return contract, ranked

    return None, ranked


# =========================================================
# Position Sizing / Reserve Logic
# =========================================================

def estimate_option_trade_cost(mark_price: float, contracts: int = 1) -> float:
    return round(max(mark_price, 0.0) * 100.0 * max(contracts, 0), 2)


def estimate_stock_trade_cost(stock_price: float, shares: int) -> float:
    return round(max(stock_price, 0.0) * max(shares, 0), 2)


def determine_option_contract_count(
    option_mark: float,
    allocation_dollars: float,
    minimum_contracts: int = 1,
    allow_slight_underfill: bool = True,
) -> int:
    per_contract_cost = max(option_mark, 0.0) * 100.0
    if per_contract_cost <= 0 or allocation_dollars <= 0:
        return 0

    contracts = int(allocation_dollars // per_contract_cost)

    if contracts <= 0 and allow_slight_underfill and allocation_dollars >= per_contract_cost * 0.85:
        contracts = minimum_contracts

    return max(contracts, 0)


def determine_stock_share_count(
    stock_price: float,
    allocation_dollars: float,
) -> int:
    if stock_price <= 0 or allocation_dollars <= 0:
        return 0
    return max(int(allocation_dollars // stock_price), 0)


def evaluate_reserve_pressure(
    cash_available: float,
    estimated_trade_cost: float,
    mode: str = "paper",
    paper_reserve_floor: float = DEFAULT_PAPER_RESERVE_FLOOR,
    live_reserve_floor: float = DEFAULT_LIVE_RESERVE_FLOOR,
) -> Dict[str, Any]:
    cash_available = max(cash_available, 0.0)
    estimated_trade_cost = max(estimated_trade_cost, 0.0)

    remaining_cash = cash_available - estimated_trade_cost
    reserve_floor_pct = live_reserve_floor if str(mode).lower() == "live" else paper_reserve_floor
    reserve_floor_dollars = cash_available * reserve_floor_pct

    is_pressure = remaining_cash < reserve_floor_dollars
    hard_block = str(mode).lower() == "live" and is_pressure
    warning_only = str(mode).lower() != "live" and is_pressure

    return {
        "mode": str(mode).lower(),
        "cash_available": round(cash_available, 2),
        "estimated_trade_cost": round(estimated_trade_cost, 2),
        "remaining_cash": round(remaining_cash, 2),
        "reserve_floor_pct": round(reserve_floor_pct, 4),
        "reserve_floor_dollars": round(reserve_floor_dollars, 2),
        "is_pressure": bool(is_pressure),
        "hard_block": bool(hard_block),
        "warning_only": bool(warning_only),
    }


# =========================================================
# Vehicle Selection
# =========================================================

def _serialize_top_contracts(
    ranked: List[OptionContract],
    keep: int = DEFAULT_TOP_CONTRACTS_TO_KEEP,
) -> List[Dict[str, Any]]:
    return [asdict(contract) for contract in (ranked or [])[:keep]]


def choose_vehicle(
    symbol: str,
    direction: str,
    underlying_price: float,
    option_chain: List[Dict[str, Any]],
    allocation_dollars: float,
    cash_available: float,
    mode: str = "paper",
    allow_stock_fallback: bool = True,
) -> VehicleDecision:
    decision = VehicleDecision(symbol=_normalize_upper(symbol))

    best_contract, ranked = choose_best_option_contract(
        option_chain=option_chain,
        underlying_symbol=symbol,
        target_direction=direction,
        underlying_price=underlying_price,
    )

    decision.top_ranked_contracts = _serialize_top_contracts(ranked)

    if best_contract:
        contracts = determine_option_contract_count(best_contract.mark, allocation_dollars)
        est_cost = estimate_option_trade_cost(best_contract.mark, contracts)

        decision.selected_vehicle = VEHICLE_OPTION
        decision.fallback_vehicle = VEHICLE_STOCK if allow_stock_fallback else VEHICLE_NONE
        decision.contract = asdict(best_contract)
        decision.contract_score = best_contract.total_score
        decision.contracts = contracts
        decision.estimated_cost = est_cost

        if contracts <= 0:
            decision.warnings.append("allocation_too_small_for_option_contract")
            decision.rejection_reasons.append("option_affordability_failed")
        else:
            reserve_check = evaluate_reserve_pressure(
                cash_available=cash_available,
                estimated_trade_cost=est_cost,
                mode=mode,
            )
            decision.reserve_check = reserve_check

            if reserve_check["hard_block"]:
                decision.approved = False
                decision.action = DECISION_REJECT
                decision.reason = "Option contract passed research but failed live reserve protection."
                decision.reason_code = "live_reserve_block"
                decision.rejection_reasons.append("live_reserve_block")
                return decision

            decision.approved = True
            decision.action = DECISION_WARN if reserve_check["warning_only"] else DECISION_APPROVE
            decision.reason = (
                "Option selected with reserve-pressure warning in paper mode."
                if reserve_check["warning_only"]
                else "Option selected as primary vehicle."
            )
            decision.reason_code = (
                "paper_reserve_warning"
                if reserve_check["warning_only"]
                else "option_selected"
            )
            if reserve_check["warning_only"]:
                decision.warnings.append("paper_reserve_warning")
            return decision

    if ranked:
        top_fail = ranked[0]
        decision.rejection_reasons.extend(top_fail.rejection_reasons or [])
        decision.warnings.extend(top_fail.warnings or [])

    decision.rejection_reasons = _dedupe_keep_order(decision.rejection_reasons)
    decision.warnings = _dedupe_keep_order(decision.warnings)

    if allow_stock_fallback and underlying_price > 0:
        shares = determine_stock_share_count(underlying_price, allocation_dollars)
        if shares > 0:
            est_cost = estimate_stock_trade_cost(underlying_price, shares)
            reserve_check = evaluate_reserve_pressure(
                cash_available=cash_available,
                estimated_trade_cost=est_cost,
                mode=mode,
            )

            decision.selected_vehicle = VEHICLE_STOCK
            decision.fallback_vehicle = VEHICLE_NONE
            decision.shares = shares
            decision.estimated_cost = est_cost
            decision.reserve_check = reserve_check

            if reserve_check["hard_block"]:
                decision.approved = False
                decision.action = DECISION_REJECT
                decision.reason = "Options were unsuitable and stock fallback failed live reserve protection."
                decision.reason_code = "stock_fallback_live_reserve_block"
                decision.rejection_reasons.append("stock_fallback_live_reserve_block")
                decision.rejection_reasons = _dedupe_keep_order(decision.rejection_reasons)
                return decision

            decision.approved = True
            decision.action = DECISION_WARN if reserve_check["warning_only"] else DECISION_APPROVE
            decision.reason = (
                "Options were unsuitable; stock fallback selected with reserve warning in paper mode."
                if reserve_check["warning_only"]
                else "Options were unsuitable; stock fallback selected."
            )
            decision.reason_code = (
                "stock_fallback_paper_warning"
                if reserve_check["warning_only"]
                else "stock_fallback_selected"
            )
            if reserve_check["warning_only"]:
                decision.warnings.append("paper_reserve_warning")
            decision.warnings = _dedupe_keep_order(decision.warnings)
            return decision

        decision.rejection_reasons.append("stock_fallback_affordability_failed")

    decision.selected_vehicle = VEHICLE_NONE
    decision.fallback_vehicle = VEHICLE_NONE
    decision.approved = False
    decision.action = DECISION_REJECT
    decision.reason = "No executable vehicle passed the lifecycle rules."
    decision.reason_code = "no_vehicle_selected"
    decision.rejection_reasons = _dedupe_keep_order(
        decision.rejection_reasons or ["no_option_and_no_stock_fallback"]
    )
    decision.warnings = _dedupe_keep_order(decision.warnings)
    return decision


# =========================================================
# Lifecycle Builder
# =========================================================

def build_options_lifecycle(
    candidate: Dict[str, Any],
    option_chain: List[Dict[str, Any]],
    account_context: Dict[str, Any],
    mode: str = "paper",
    allow_stock_fallback: bool = True,
) -> Dict[str, Any]:
    symbol = _normalize_upper(candidate.get("symbol"))
    strategy = _normalize_upper(candidate.get("strategy"), "UNKNOWN")
    direction = _normalize_upper(candidate.get("direction"), DIRECTION_UNKNOWN)
    confidence = _normalize_upper(candidate.get("confidence"), "UNKNOWN")
    score = _safe_float(candidate.get("score"))

    underlying_price = _safe_float(candidate.get("underlying_price", candidate.get("price")))
    allocation_dollars = _safe_float(
        candidate.get("capital_allocation_dollars", candidate.get("allocation_dollars"))
    )
    cash_available = _safe_float(
        account_context.get("cash_available", account_context.get("cash"))
    )

    life = LifecycleState(
        symbol=symbol,
        strategy=strategy,
        direction=direction,
        confidence=confidence,
        score=score,
        candidate_size_dollars=round(allocation_dollars, 2),
        raw=dict(candidate),
    )

    research_approved = bool(candidate.get("research_approved", False))
    research_reason = _normalize_text(candidate.get("research_reason"))
    research_reason_code = _normalize_text(candidate.get("research_reason_code"))

    if not research_approved:
        life.lifecycle_stage = LIFECYCLE_RESEARCH_REJECTED
        life.research_decision = DECISION_REJECT
        life.research_reason = research_reason or "Research gate did not approve this setup."
        life.research_reason_code = research_reason_code or "research_rejected"
        life.final_decision = DECISION_REJECT
        life.final_reason = life.research_reason
        life.final_reason_code = life.research_reason_code
        life.updated_at = _now_iso()
        return asdict(life)

    life.lifecycle_stage = LIFECYCLE_RESEARCH_APPROVED
    life.research_decision = DECISION_APPROVE
    life.research_reason = research_reason or "Research gate approved the setup."
    life.research_reason_code = research_reason_code or "research_approved"

    vehicle = choose_vehicle(
        symbol=symbol,
        direction=direction,
        underlying_price=underlying_price,
        option_chain=option_chain,
        allocation_dollars=allocation_dollars,
        cash_available=cash_available,
        mode=mode,
        allow_stock_fallback=allow_stock_fallback,
    )

    life.selected_vehicle = vehicle.selected_vehicle
    life.fallback_vehicle = vehicle.fallback_vehicle
    life.contract = vehicle.contract
    life.reserve_check = dict(vehicle.reserve_check or {})
    life.top_ranked_contracts = list(vehicle.top_ranked_contracts or [])
    life.warnings.extend(vehicle.warnings)
    life.rejection_reasons.extend(vehicle.rejection_reasons)
    life.warnings = _dedupe_keep_order(life.warnings)
    life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons)

    if not vehicle.approved:
        life.lifecycle_stage = LIFECYCLE_EXECUTION_BLOCKED
        life.execution_decision = DECISION_REJECT
        life.execution_reason = vehicle.reason
        life.execution_reason_code = vehicle.reason_code
        life.final_decision = DECISION_REJECT
        life.final_reason = vehicle.reason
        life.final_reason_code = vehicle.reason_code
        life.estimated_cost = round(vehicle.estimated_cost, 2)
        life.contracts = vehicle.contracts
        life.shares = vehicle.shares
        life.updated_at = _now_iso()
        return asdict(life)

    life.execution_decision = vehicle.action
    life.execution_reason = vehicle.reason
    life.execution_reason_code = vehicle.reason_code
    life.final_decision = vehicle.action
    life.final_reason = vehicle.reason
    life.final_reason_code = vehicle.reason_code
    life.estimated_cost = round(vehicle.estimated_cost, 2)
    life.contracts = vehicle.contracts
    life.shares = vehicle.shares

    if vehicle.action in {DECISION_APPROVE, DECISION_WARN}:
        life.lifecycle_stage = LIFECYCLE_EXECUTION_READY
    else:
        life.lifecycle_stage = LIFECYCLE_EXECUTION_BLOCKED

    life.updated_at = _now_iso()
    return asdict(life)


# =========================================================
# Lifecycle Transitions
# =========================================================

def advance_lifecycle(
    lifecycle_obj: Dict[str, Any],
    new_stage: str,
    reason: str = "",
    reason_code: str = "",
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    obj = dict(lifecycle_obj or {})
    obj["lifecycle_stage"] = new_stage
    obj["updated_at"] = _now_iso()

    if reason:
        obj["final_reason"] = reason
    if reason_code:
        obj["final_reason_code"] = reason_code

    if new_stage == LIFECYCLE_ENTERED and not obj.get("entered_at"):
        obj["entered_at"] = _now_iso()

    if new_stage == LIFECYCLE_CLOSED and not obj.get("exited_at"):
        obj["exited_at"] = _now_iso()

    if extra_updates:
        obj.update(extra_updates)

    return obj


def mark_selected(
    lifecycle_obj: Dict[str, Any],
    reason: str = "Candidate selected for execution queue.",
    reason_code: str = "selected_for_execution",
) -> Dict[str, Any]:
    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_SELECTED,
        reason=reason,
        reason_code=reason_code,
    )


def mark_entered(
    lifecycle_obj: Dict[str, Any],
    fill_price: float,
    quantity: int,
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = {
        "fill_price": round(_safe_float(fill_price), 4),
        "filled_quantity": _safe_int(quantity),
    }
    if extra_updates:
        updates.update(extra_updates)

    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_ENTERED,
        reason="Position entered.",
        reason_code="entered",
        extra_updates=updates,
    )


def mark_managing(
    lifecycle_obj: Dict[str, Any],
    management_reason: str = "Position is active and under management.",
) -> Dict[str, Any]:
    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_MANAGING,
        reason=management_reason,
        reason_code="managing",
    )


def mark_exit_ready(
    lifecycle_obj: Dict[str, Any],
    exit_reason: str,
    exit_reason_code: str = "exit_ready",
) -> Dict[str, Any]:
    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_EXIT_READY,
        reason=exit_reason,
        reason_code=exit_reason_code,
    )


def mark_closed(
    lifecycle_obj: Dict[str, Any],
    exit_price: float,
    pnl: float,
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = {
        "exit_price": round(_safe_float(exit_price), 4),
        "pnl": round(_safe_float(pnl), 2),
    }
    if extra_updates:
        updates.update(extra_updates)

    return advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_CLOSED,
        reason="Position closed.",
        reason_code="closed",
        extra_updates=updates,
    )


# =========================================================
# Explainability / Summary
# =========================================================

def summarize_lifecycle(lifecycle_obj: Dict[str, Any]) -> Dict[str, Any]:
    obj = lifecycle_obj or {}
    reserve = obj.get("reserve_check") or {}

    return {
        "symbol": obj.get("symbol"),
        "strategy": obj.get("strategy"),
        "direction": obj.get("direction"),
        "lifecycle_stage": obj.get("lifecycle_stage"),
        "selected_vehicle": obj.get("selected_vehicle"),
        "research_decision": obj.get("research_decision"),
        "execution_decision": obj.get("execution_decision"),
        "final_decision": obj.get("final_decision"),
        "final_reason": obj.get("final_reason"),
        "final_reason_code": obj.get("final_reason_code"),
        "estimated_cost": obj.get("estimated_cost", 0.0),
        "contracts": obj.get("contracts", 0),
        "shares": obj.get("shares", 0),
        "reserve_pressure": reserve.get("is_pressure", False),
        "reserve_hard_block": reserve.get("hard_block", False),
        "reserve_warning_only": reserve.get("warning_only", False),
        "warnings": obj.get("warnings", []),
        "rejection_reasons": obj.get("rejection_reasons", []),
        "top_ranked_contracts": obj.get("top_ranked_contracts", []),
    }
