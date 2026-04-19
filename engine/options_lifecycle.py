from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.vehicle_selector import choose_vehicle

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
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

DIRECTION_CALL = "CALL"
DIRECTION_PUT = "PUT"
DIRECTION_UNKNOWN = "UNKNOWN"

DECISION_APPROVE = "APPROVE"
DECISION_REJECT = "REJECT"
DECISION_WATCH = "WATCH"
DECISION_WARN = "WARN"


def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_text(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _normalize_upper(value: Any, default: str = "") -> str:
    return _normalize_text(value, default).upper()


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        item = _normalize_text(item)
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _default_direction_from_strategy(strategy: str) -> str:
    strategy = _normalize_upper(strategy, DIRECTION_UNKNOWN)
    if strategy in {"CALL", "LONG_CALL"}:
        return DIRECTION_CALL
    if strategy in {"PUT", "LONG_PUT"}:
        return DIRECTION_PUT
    return DIRECTION_UNKNOWN


def _candidate_best_price(candidate: Dict[str, Any]) -> float:
    candidate = _safe_dict(candidate)
    candidates = [
        candidate.get("current_price"),
        candidate.get("price"),
        candidate.get("entry"),
        candidate.get("fill_price"),
        candidate.get("requested_price"),
        candidate.get("underlying_price"),
        candidate.get("market_price"),
        candidate.get("latest_price"),
    ]
    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return price
    return 0.0


@dataclass
class LifecycleState:
    symbol: str = ""
    strategy: str = ""
    direction: str = DIRECTION_UNKNOWN

    lifecycle_stage: str = LIFECYCLE_NEW
    selected_vehicle: str = VEHICLE_NONE
    fallback_vehicle: str = VEHICLE_NONE

    research_approved: bool = False
    execution_ready: bool = False
    selected_for_execution: bool = False

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
    base_confidence: str = "UNKNOWN"
    v2_confidence: str = "UNKNOWN"

    score: float = 0.0
    base_score: float = 0.0
    fused_score: float = 0.0
    v2_score: float = 0.0
    v2_quality: float = 0.0

    v2_reason: str = ""
    v2_vehicle_bias: str = ""
    v2_payload: Dict[str, Any] = field(default_factory=dict)

    readiness_score: float = 0.0
    promotion_score: float = 0.0
    rebuild_pressure: float = 0.0
    execution_quality: float = 0.0

    setup_type: str = ""
    setup_family: str = ""
    entry_quality: str = ""
    trend: str = ""
    regime: str = ""
    breadth: str = ""
    volatility_state: str = ""
    mode: str = ""

    decision_reason: str = ""
    vehicle_reason: str = ""
    blocked_at: str = ""

    why: List[Any] = field(default_factory=list)
    supports: List[Any] = field(default_factory=list)
    blockers: List[Any] = field(default_factory=list)
    rejection_analysis: List[Any] = field(default_factory=list)
    option_explanation: List[Any] = field(default_factory=list)
    learning_notes: List[Any] = field(default_factory=list)
    stronger_competing_setups: List[Any] = field(default_factory=list)

    candidate_size_dollars: float = 0.0
    capital_required: float = 0.0
    minimum_trade_cost: float = 0.0
    capital_available: float = 0.0
    estimated_cost: float = 0.0

    contracts: int = 0
    shares: int = 0

    contract: Optional[Dict[str, Any]] = None
    option: Dict[str, Any] = field(default_factory=dict)
    stock_path: Dict[str, Any] = field(default_factory=dict)
    option_path: Dict[str, Any] = field(default_factory=dict)

    reserve_check: Dict[str, Any] = field(default_factory=dict)
    governor: Dict[str, Any] = field(default_factory=dict)
    mode_context: Dict[str, Any] = field(default_factory=dict)

    top_ranked_contracts: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)

    entered_at: Optional[str] = None
    exited_at: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    raw: Dict[str, Any] = field(default_factory=dict)


def build_options_lifecycle(
    candidate: Dict[str, Any],
    option_chain: List[Dict[str, Any]],
    account_context: Dict[str, Any],
    mode: str = "paper",
    allow_stock_fallback: bool = True,
) -> Dict[str, Any]:
    from engine.observatory_mode import normalize_mode, build_mode_context

    candidate = _safe_dict(candidate)
    account_context = _safe_dict(account_context)
    option_chain = _safe_list(option_chain)

    requested_mode = normalize_mode(mode or candidate.get("trading_mode") or candidate.get("mode") or "paper")
    incoming_mode_context = _safe_dict(candidate.get("mode_context"))
    resolved_mode_context = build_mode_context(requested_mode)
    mode_context = dict(resolved_mode_context)
    if incoming_mode_context:
        mode_context.update({k: v for k, v in incoming_mode_context.items() if v is not None})

    symbol = _normalize_upper(candidate.get("symbol"))
    strategy = _normalize_upper(candidate.get("strategy"), "UNKNOWN")
    direction = _normalize_upper(
        candidate.get("direction"),
        _default_direction_from_strategy(strategy),
    )

    confidence = _normalize_upper(candidate.get("confidence"), "UNKNOWN")
    base_confidence = _normalize_upper(candidate.get("base_confidence"), confidence)
    v2_confidence = _normalize_upper(candidate.get("v2_confidence"), confidence)

    score = _safe_float(candidate.get("score"))
    base_score = _safe_float(candidate.get("base_score", score))
    fused_score = _safe_float(candidate.get("fused_score", score))
    v2_score = _safe_float(candidate.get("v2_score"))
    v2_quality = _safe_float(candidate.get("v2_quality"))

    underlying_price = _safe_float(
        candidate.get("underlying_price", _candidate_best_price(candidate))
    )

    capital_required_existing = _safe_float(candidate.get("capital_required"))
    minimum_trade_cost_existing = _safe_float(candidate.get("minimum_trade_cost"))

    allocation_dollars = _safe_float(
        candidate.get(
            "capital_allocation_dollars",
            candidate.get(
                "allocation_dollars",
                capital_required_existing if capital_required_existing > 0 else minimum_trade_cost_existing,
            ),
        )
    )
    if allocation_dollars <= 0:
        allocation_dollars = underlying_price if underlying_price > 0 else 0.0

    cash_available = _safe_float(
        account_context.get("cash_available", account_context.get("cash"))
    )

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct"), 0.0)
    reserve_warning_only = _safe_bool(mode_context.get("reserve_warning_only"), False)
    execution_warning_only = _safe_bool(mode_context.get("execution_warning_only"), False)
    strict_execution_gate = _safe_bool(mode_context.get("strict_execution_gate"), True)
    options_first = _safe_bool(mode_context.get("options_first"), True)
    allow_stock_fallback_by_mode = _safe_bool(mode_context.get("allow_stock_fallback"), True)
    minimum_option_dte = _safe_int(mode_context.get("minimum_option_dte"), 0)
    allow_same_day_high_risk_contracts = _safe_bool(
        mode_context.get("allow_same_day_high_risk_contracts"),
        False,
    )

    reserve_floor_dollars = round(cash_available * reserve_floor_pct, 2) if reserve_floor_pct > 0 else 0.0

    life = LifecycleState(
        symbol=symbol,
        strategy=strategy,
        direction=direction,
        confidence=confidence,
        base_confidence=base_confidence,
        v2_confidence=v2_confidence,
        score=score,
        base_score=base_score,
        fused_score=fused_score,
        v2_score=v2_score,
        v2_quality=v2_quality,
        v2_reason=_normalize_text(candidate.get("v2_reason")),
        v2_vehicle_bias=_normalize_upper(candidate.get("v2_vehicle_bias")),
        v2_payload=_safe_dict(candidate.get("v2_payload")),
        readiness_score=_safe_float(candidate.get("readiness_score")),
        promotion_score=_safe_float(candidate.get("promotion_score")),
        rebuild_pressure=_safe_float(candidate.get("rebuild_pressure")),
        execution_quality=_safe_float(candidate.get("execution_quality")),
        setup_type=_normalize_text(candidate.get("setup_type")),
        setup_family=_normalize_text(candidate.get("setup_family")),
        entry_quality=_normalize_text(candidate.get("entry_quality")),
        trend=_normalize_text(candidate.get("trend")),
        regime=_normalize_text(candidate.get("regime")),
        breadth=_normalize_text(candidate.get("breadth")),
        volatility_state=_normalize_text(candidate.get("volatility_state")),
        mode=requested_mode,
        decision_reason=_normalize_text(candidate.get("decision_reason")),
        vehicle_reason=_normalize_text(candidate.get("vehicle_reason")),
        blocked_at=_normalize_text(candidate.get("blocked_at")),
        why=_safe_list(candidate.get("why")),
        supports=_safe_list(candidate.get("supports")),
        blockers=_safe_list(candidate.get("blockers")),
        rejection_analysis=_safe_list(candidate.get("rejection_analysis")),
        option_explanation=_safe_list(candidate.get("option_explanation")),
        learning_notes=_safe_list(candidate.get("learning_notes")),
        stronger_competing_setups=_safe_list(candidate.get("stronger_competing_setups")),
        candidate_size_dollars=round(allocation_dollars, 2),
        capital_required=round(capital_required_existing, 2),
        minimum_trade_cost=round(minimum_trade_cost_existing, 2),
        capital_available=round(cash_available, 2),
        contract=_safe_dict(candidate.get("contract")) or None,
        option=_safe_dict(candidate.get("option")),
        stock_path=_safe_dict(candidate.get("stock_path")),
        option_path=_safe_dict(candidate.get("option_path")),
        governor=_safe_dict(candidate.get("governor")),
        mode_context=mode_context,
        warnings=[_normalize_text(x) for x in _safe_list(candidate.get("warnings")) if _normalize_text(x)],
        rejection_reasons=[_normalize_text(x) for x in _safe_list(candidate.get("rejection_reasons")) if _normalize_text(x)],
        research_approved=_safe_bool(candidate.get("research_approved"), False),
        execution_ready=_safe_bool(candidate.get("execution_ready"), False),
        selected_for_execution=_safe_bool(candidate.get("selected_for_execution"), False),
        raw=dict(candidate),
    )

    life.raw["trading_mode"] = requested_mode
    life.raw["mode_context"] = mode_context
    life.raw["reserve_floor_dollars"] = reserve_floor_dollars

    research_reason = _normalize_text(candidate.get("research_reason"))
    research_reason_code = _normalize_text(candidate.get("research_reason_code"))

    if not life.research_approved:
        life.lifecycle_stage = LIFECYCLE_RESEARCH_REJECTED
        life.research_decision = DECISION_REJECT
        life.research_reason = research_reason or "Research gate did not approve this setup."
        life.research_reason_code = research_reason_code or "research_rejected"
        life.final_decision = DECISION_REJECT
        life.final_reason = life.research_reason
        life.final_reason_code = life.research_reason_code
        life.execution_ready = False
        life.selected_for_execution = False
        life.blocked_at = "research_gate"
        life.updated_at = _now_iso()
        return asdict(life)

    life.lifecycle_stage = LIFECYCLE_RESEARCH_APPROVED
    life.research_decision = DECISION_APPROVE
    life.research_reason = research_reason or "Research gate approved the setup."
    life.research_reason_code = research_reason_code or "research_approved"

    trade_intent = _normalize_text(candidate.get("trade_intent"), "GRIND")

    vehicle = choose_vehicle(
        symbol=symbol,
        strategy=strategy,
        trade_intent=trade_intent,
        option_chain=option_chain,
        stock_price=underlying_price,
        available_capital=cash_available,
        stock_allowed=bool(allow_stock_fallback and allow_stock_fallback_by_mode),
        trading_mode=requested_mode,
    )
    vehicle = _safe_dict(vehicle)

    option_result = _safe_dict(vehicle.get("option_result"))
    best_option_preview = _safe_dict(option_result.get("best_option_preview"))
    option_reason = _normalize_text(option_result.get("option_reason"))
    option_notes = _safe_list(option_result.get("option_notes"))
    option_score = _safe_float(option_result.get("option_score"))
    option_dte = _safe_int(best_option_preview.get("dte"))

    life.selected_vehicle = _normalize_upper(
        vehicle.get("vehicle_selected"),
        VEHICLE_NONE,
    )
    if life.selected_vehicle not in {VEHICLE_OPTION, VEHICLE_STOCK, VEHICLE_NONE, VEHICLE_RESEARCH_ONLY}:
        life.selected_vehicle = VEHICLE_NONE

    life.fallback_vehicle = VEHICLE_NONE
    life.contract = best_option_preview or life.contract
    if best_option_preview and not life.option:
        life.option = dict(best_option_preview)

    life.top_ranked_contracts = [best_option_preview] if best_option_preview else []
    life.capital_required = round(_safe_float(vehicle.get("capital_required")), 2)
    life.minimum_trade_cost = round(_safe_float(vehicle.get("minimum_trade_cost")), 2)
    life.estimated_cost = round(_safe_float(vehicle.get("minimum_trade_cost")), 2)
    life.contracts = _safe_int(vehicle.get("contracts"))
    life.shares = _safe_int(vehicle.get("shares"))
    life.vehicle_reason = _normalize_text(vehicle.get("vehicle_reason"))
    life.option_explanation = _dedupe_keep_order(_safe_list(life.option_explanation) + option_notes)

    if option_reason:
        life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + [option_reason])

    if best_option_preview and not life.option_path:
        option_mark = _safe_float(best_option_preview.get("mark"))
        option_capital_required = round(option_mark * 100, 2) if option_mark > 0 else 0.0
        option_minimum_trade_cost = round(option_capital_required + 1.0, 2) if option_capital_required > 0 else 0.0
        option_affordable = cash_available >= option_minimum_trade_cost if option_minimum_trade_cost > 0 else False
        option_after_trade_cash = round(cash_available - option_minimum_trade_cost, 2) if option_minimum_trade_cost > 0 else cash_available

        life.option_path = {
            "vehicle": "OPTION",
            "capital_required": option_capital_required,
            "minimum_trade_cost": option_minimum_trade_cost,
            "contracts": 1,
            "shares": 0,
            "affordable": option_affordable,
            "score": option_score,
            "dte": option_dte,
            "spread_pct": _safe_float(best_option_preview.get("spread_pct"), 999.0),
            "cash_after_trade": option_after_trade_cash,
            "reserve_floor_dollars": reserve_floor_dollars,
            "reserve_ok_after_trade": option_after_trade_cash >= reserve_floor_dollars,
        }

    if not life.stock_path and underlying_price > 0:
        stock_capital_required = round(underlying_price, 2)
        stock_minimum_trade_cost = round(underlying_price + 1.0, 2)
        stock_after_trade_cash = round(cash_available - stock_minimum_trade_cost, 2)
        life.stock_path = {
            "vehicle": "STOCK",
            "capital_required": stock_capital_required,
            "minimum_trade_cost": stock_minimum_trade_cost,
            "contracts": 0,
            "shares": 1,
            "affordable": cash_available >= stock_minimum_trade_cost,
            "cash_after_trade": stock_after_trade_cash,
            "reserve_floor_dollars": reserve_floor_dollars,
            "reserve_ok_after_trade": stock_after_trade_cash >= reserve_floor_dollars,
        }

    stock_path = _safe_dict(life.stock_path)
    option_path = _safe_dict(life.option_path)

    option_affordable = _safe_bool(option_path.get("affordable"), False)
    stock_affordable = _safe_bool(stock_path.get("affordable"), False)
    option_reserve_ok = _safe_bool(option_path.get("reserve_ok_after_trade"), False)
    stock_reserve_ok = _safe_bool(stock_path.get("reserve_ok_after_trade"), False)

    if life.selected_vehicle == VEHICLE_OPTION and option_path:
        if minimum_option_dte > 0 and option_dte > 0 and option_dte < minimum_option_dte:
            option_warning_or_block = "option_dte_below_mode_minimum"
            if allow_same_day_high_risk_contracts:
                life.warnings = _dedupe_keep_order(life.warnings + [option_warning_or_block])
            else:
                life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + [option_warning_or_block])
                if allow_stock_fallback and allow_stock_fallback_by_mode and stock_path:
                    life.fallback_vehicle = VEHICLE_STOCK
                    life.selected_vehicle = VEHICLE_STOCK
                    life.vehicle_reason = "stock_fallback_after_option_dte_block"
                    life.warnings = _dedupe_keep_order(life.warnings + [option_warning_or_block])
                else:
                    life.selected_vehicle = VEHICLE_RESEARCH_ONLY

    if life.selected_vehicle == VEHICLE_OPTION and option_path:
        if not option_affordable:
            if allow_stock_fallback and allow_stock_fallback_by_mode and stock_affordable:
                life.fallback_vehicle = VEHICLE_STOCK
                life.selected_vehicle = VEHICLE_STOCK
                life.vehicle_reason = "stock_fallback_after_option_capital_failure"
                life.warnings = _dedupe_keep_order(life.warnings + ["option_not_affordable"])
            else:
                life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + ["option_not_affordable"])
                life.selected_vehicle = VEHICLE_RESEARCH_ONLY

    if life.selected_vehicle == VEHICLE_OPTION and option_path:
        if reserve_floor_dollars > 0 and not option_reserve_ok:
            reserve_reason = "insufficient_cash_after_reserve"
            if reserve_warning_only or execution_warning_only or not strict_execution_gate:
                life.warnings = _dedupe_keep_order(life.warnings + [reserve_reason])
            else:
                if allow_stock_fallback and allow_stock_fallback_by_mode and stock_affordable and stock_reserve_ok:
                    life.fallback_vehicle = VEHICLE_STOCK
                    life.selected_vehicle = VEHICLE_STOCK
                    life.vehicle_reason = "stock_fallback_after_option_reserve_failure"
                    life.warnings = _dedupe_keep_order(life.warnings + [reserve_reason])
                else:
                    life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + [reserve_reason])
                    life.selected_vehicle = VEHICLE_RESEARCH_ONLY

    if life.selected_vehicle == VEHICLE_STOCK and stock_path:
        if not stock_affordable:
            life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + ["stock_not_affordable"])
            life.selected_vehicle = VEHICLE_RESEARCH_ONLY

    if life.selected_vehicle == VEHICLE_STOCK and stock_path:
        if reserve_floor_dollars > 0 and not stock_reserve_ok:
            reserve_reason = "insufficient_cash_after_reserve"
            if reserve_warning_only or execution_warning_only or not strict_execution_gate:
                life.warnings = _dedupe_keep_order(life.warnings + [reserve_reason])
            else:
                life.rejection_reasons = _dedupe_keep_order(life.rejection_reasons + [reserve_reason])
                life.selected_vehicle = VEHICLE_RESEARCH_ONLY

    if options_first and allow_stock_fallback and allow_stock_fallback_by_mode:
        if life.selected_vehicle == VEHICLE_STOCK and best_option_preview:
            if option_affordable and (option_reserve_ok or reserve_warning_only or execution_warning_only or not strict_execution_gate):
                if option_score >= 90:
                    life.selected_vehicle = VEHICLE_OPTION
                    life.vehicle_reason = "options_first_preferred_executable_contract"
                    life.fallback_vehicle = VEHICLE_STOCK

    blocked_vehicle = life.selected_vehicle in {VEHICLE_NONE, VEHICLE_RESEARCH_ONLY, ""}

    if blocked_vehicle:
        life.lifecycle_stage = LIFECYCLE_EXECUTION_BLOCKED
        life.execution_ready = False
        life.selected_for_execution = False
        life.execution_decision = DECISION_REJECT
        life.execution_reason = "No executable vehicle passed the lifecycle rules."
        life.execution_reason_code = (
            life.rejection_reasons[-1]
            if life.rejection_reasons
            else option_reason or "no_vehicle_selected"
        )
        life.final_decision = DECISION_REJECT
        life.final_reason = life.execution_reason
        life.final_reason_code = life.execution_reason_code
        life.blocked_at = "options_lifecycle"
        life.updated_at = _now_iso()
        return asdict(life)

    if life.selected_vehicle == VEHICLE_OPTION:
        selected_path = option_path
    elif life.selected_vehicle == VEHICLE_STOCK:
        selected_path = stock_path
    else:
        selected_path = {}

    selected_capital_required = round(_safe_float(selected_path.get("capital_required")), 2)
    selected_minimum_trade_cost = round(_safe_float(selected_path.get("minimum_trade_cost")), 2)

    if selected_capital_required > 0:
        life.capital_required = selected_capital_required
    if selected_minimum_trade_cost > 0:
        life.minimum_trade_cost = selected_minimum_trade_cost
        life.estimated_cost = selected_minimum_trade_cost

    if life.selected_vehicle == VEHICLE_OPTION:
        life.contracts = max(1, _safe_int(selected_path.get("contracts"), 1))
        life.shares = 0
    elif life.selected_vehicle == VEHICLE_STOCK:
        life.shares = max(1, _safe_int(selected_path.get("shares"), 1))
        life.contracts = 0

    lifecycle_warning_only = bool(life.warnings) and not strict_execution_gate

    life.execution_ready = True
    life.selected_for_execution = False

    if lifecycle_warning_only:
        life.execution_decision = DECISION_WARN
        life.execution_reason = "Vehicle selected with lifecycle warnings."
        life.execution_reason_code = "execution_warning_only"
        life.final_decision = DECISION_WARN
        life.final_reason = life.execution_reason
        life.final_reason_code = life.execution_reason_code
        life.lifecycle_stage = LIFECYCLE_EXECUTION_READY
        life.blocked_at = ""
    else:
        life.execution_decision = DECISION_APPROVE
        life.execution_reason = "Vehicle selected for execution."
        life.execution_reason_code = life.vehicle_reason or "vehicle_selected"
        life.final_decision = DECISION_APPROVE
        life.final_reason = life.execution_reason
        life.final_reason_code = life.execution_reason_code
        life.lifecycle_stage = LIFECYCLE_EXECUTION_READY
        life.blocked_at = ""

    life.raw["selected_vehicle"] = life.selected_vehicle
    life.raw["fallback_vehicle"] = life.fallback_vehicle
    life.raw["trading_mode"] = requested_mode
    life.raw["mode_context"] = mode_context
    life.raw["reserve_floor_dollars"] = reserve_floor_dollars
    life.raw["execution_warning_only"] = execution_warning_only
    life.raw["strict_execution_gate"] = strict_execution_gate
    life.raw["reserve_warning_only"] = reserve_warning_only

    life.updated_at = _now_iso()
    return asdict(life)


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
    obj = advance_lifecycle(
        lifecycle_obj,
        LIFECYCLE_SELECTED,
        reason=reason,
        reason_code=reason_code,
    )
    obj["selected_for_execution"] = True
    return obj


def mark_entered(
    lifecycle_obj: Dict[str, Any],
    fill_price: float,
    quantity: int,
    extra_updates: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    updates = {
        "fill_price": round(_safe_float(fill_price), 4),
        "filled_quantity": _safe_int(quantity),
        "status": "OPEN",
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
        "status": "CLOSED",
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


def summarize_lifecycle(lifecycle_obj: Dict[str, Any]) -> Dict[str, Any]:
    obj = lifecycle_obj or {}
    reserve = obj.get("reserve_check") or {}
    return {
        "symbol": obj.get("symbol"),
        "strategy": obj.get("strategy"),
        "direction": obj.get("direction"),
        "lifecycle_stage": obj.get("lifecycle_stage"),
        "selected_vehicle": obj.get("selected_vehicle"),
        "research_approved": obj.get("research_approved"),
        "execution_ready": obj.get("execution_ready"),
        "research_decision": obj.get("research_decision"),
        "execution_decision": obj.get("execution_decision"),
        "final_decision": obj.get("final_decision"),
        "final_reason": obj.get("final_reason"),
        "final_reason_code": obj.get("final_reason_code"),
        "score": obj.get("score"),
        "base_score": obj.get("base_score"),
        "fused_score": obj.get("fused_score"),
        "v2_score": obj.get("v2_score"),
        "v2_reason": obj.get("v2_reason"),
        "v2_vehicle_bias": obj.get("v2_vehicle_bias"),
        "readiness_score": obj.get("readiness_score"),
        "promotion_score": obj.get("promotion_score"),
        "rebuild_pressure": obj.get("rebuild_pressure"),
        "estimated_cost": obj.get("estimated_cost", 0.0),
        "capital_required": obj.get("capital_required", 0.0),
        "minimum_trade_cost": obj.get("minimum_trade_cost", 0.0),
        "contracts": obj.get("contracts", 0),
        "shares": obj.get("shares", 0),
        "reserve_pressure": reserve.get("is_pressure", False),
        "reserve_hard_block": reserve.get("hard_block", False),
        "reserve_warning_only": reserve.get("warning_only", False),
        "warnings": obj.get("warnings", []),
        "rejection_reasons": obj.get("rejection_reasons", []),
        "top_ranked_contracts": obj.get("top_ranked_contracts", []),
    }
