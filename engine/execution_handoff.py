from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.options_lifecycle import (
    VEHICLE_OPTION,
    VEHICLE_STOCK,
    VEHICLE_NONE,
    DECISION_APPROVE,
    DECISION_WARN,
    DECISION_REJECT,
    LIFECYCLE_EXECUTION_READY,
    mark_selected,
    mark_entered,
)


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
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# =========================================================
# Canonical Handoff Objects
# =========================================================

@dataclass
class ExecutionGuardResult:
    allowed: bool = False
    decision: str = DECISION_REJECT
    guard_reason: str = ""
    guard_reason_code: str = ""
    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    guard_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionIntent:
    symbol: str = ""
    strategy: str = ""
    direction: str = ""
    selected_vehicle: str = VEHICLE_NONE

    final_decision: str = DECISION_REJECT
    final_reason: str = ""
    final_reason_code: str = ""

    quantity: int = 0
    estimated_cost: float = 0.0
    stock_price: float = 0.0
    contract: Optional[Dict[str, Any]] = None

    execution_mode: str = "paper"
    confidence: str = "UNKNOWN"
    score: float = 0.0

    reserve_check: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    source_lifecycle: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    success: bool = False
    status: str = "REJECTED"

    symbol: str = ""
    selected_vehicle: str = VEHICLE_NONE

    filled_quantity: int = 0
    fill_price: float = 0.0
    estimated_cost: float = 0.0
    actual_cost: float = 0.0

    broker_order_id: str = ""
    execution_mode: str = "paper"

    reason: str = ""
    reason_code: str = ""

    warnings: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)

    lifecycle_after: Dict[str, Any] = field(default_factory=dict)
    execution_record: Dict[str, Any] = field(default_factory=dict)


# =========================================================
# Intent Builder
# =========================================================

def build_execution_intent(
    lifecycle_obj: Dict[str, Any],
    mode: str = "paper",
) -> ExecutionIntent:
    lifecycle_obj = lifecycle_obj if isinstance(lifecycle_obj, dict) else {}

    selected_vehicle = _normalize_upper(lifecycle_obj.get("selected_vehicle"), VEHICLE_NONE)
    contracts = _safe_int(lifecycle_obj.get("contracts"))
    shares = _safe_int(lifecycle_obj.get("shares"))
    quantity = contracts if selected_vehicle == VEHICLE_OPTION else shares

    raw = lifecycle_obj.get("raw") if isinstance(lifecycle_obj.get("raw"), dict) else {}
    contract = lifecycle_obj.get("contract") if isinstance(lifecycle_obj.get("contract"), dict) else None

    return ExecutionIntent(
        symbol=_normalize_upper(lifecycle_obj.get("symbol")),
        strategy=_normalize_upper(lifecycle_obj.get("strategy"), "UNKNOWN"),
        direction=_normalize_upper(lifecycle_obj.get("direction"), "UNKNOWN"),
        selected_vehicle=selected_vehicle,
        final_decision=_normalize_upper(lifecycle_obj.get("final_decision"), DECISION_REJECT),
        final_reason=_normalize_text(lifecycle_obj.get("final_reason")),
        final_reason_code=_normalize_text(lifecycle_obj.get("final_reason_code")),
        quantity=quantity,
        estimated_cost=_safe_float(lifecycle_obj.get("estimated_cost")),
        stock_price=_safe_float(
            raw.get("underlying_price")
            or raw.get("price")
            or lifecycle_obj.get("price")
        ),
        contract=contract,
        execution_mode=_normalize_text(mode or lifecycle_obj.get("mode") or "paper", "paper").lower(),
        confidence=_normalize_upper(lifecycle_obj.get("confidence"), "UNKNOWN"),
        score=_safe_float(lifecycle_obj.get("score")),
        reserve_check=dict(lifecycle_obj.get("reserve_check") or {}),
        warnings=list(lifecycle_obj.get("warnings") or []),
        rejection_reasons=list(lifecycle_obj.get("rejection_reasons") or []),
        source_lifecycle=dict(lifecycle_obj),
    )


def build_queued_trade_payload(
    lifecycle_obj: Dict[str, Any],
    mode: str = "paper",
) -> Dict[str, Any]:
    lifecycle_obj = lifecycle_obj if isinstance(lifecycle_obj, dict) else {}
    intent = build_execution_intent(lifecycle_obj, mode=mode)

    return {
        "symbol": intent.symbol,
        "strategy": intent.strategy,
        "direction": intent.direction,
        "selected_vehicle": intent.selected_vehicle,
        "vehicle_selected": intent.selected_vehicle,
        "vehicle": intent.selected_vehicle,

        "final_decision": intent.final_decision,
        "final_reason": intent.final_reason,
        "final_reason_code": intent.final_reason_code,

        "quantity": intent.quantity,
        "estimated_cost": round(intent.estimated_cost, 2),
        "capital_required": round(_safe_float(lifecycle_obj.get("capital_required", intent.estimated_cost)), 2),
        "minimum_trade_cost": round(_safe_float(lifecycle_obj.get("minimum_trade_cost", intent.estimated_cost)), 2),
        "stock_price": round(intent.stock_price, 4),

        "contract": intent.contract,
        "option": dict(lifecycle_obj.get("option") or intent.contract or {}),
        "stock_path": dict(lifecycle_obj.get("stock_path") or {}),
        "option_path": dict(lifecycle_obj.get("option_path") or {}),

        "execution_mode": intent.execution_mode,
        "mode": lifecycle_obj.get("mode", intent.execution_mode),
        "mode_context": dict(lifecycle_obj.get("mode_context") or {}),

        "confidence": intent.confidence,
        "base_confidence": lifecycle_obj.get("base_confidence"),
        "v2_confidence": lifecycle_obj.get("v2_confidence"),

        "score": round(intent.score, 4),
        "base_score": _safe_float(lifecycle_obj.get("base_score"), 0.0),
        "fused_score": _safe_float(lifecycle_obj.get("fused_score"), 0.0),
        "v2_score": _safe_float(lifecycle_obj.get("v2_score"), 0.0),
        "v2_quality": _safe_float(lifecycle_obj.get("v2_quality"), 0.0),
        "v2_reason": lifecycle_obj.get("v2_reason", ""),
        "v2_vehicle_bias": lifecycle_obj.get("v2_vehicle_bias", ""),
        "v2_payload": dict(lifecycle_obj.get("v2_payload") or {}),

        "readiness_score": _safe_float(lifecycle_obj.get("readiness_score"), 0.0),
        "promotion_score": _safe_float(lifecycle_obj.get("promotion_score"), 0.0),
        "rebuild_pressure": _safe_float(lifecycle_obj.get("rebuild_pressure"), 0.0),
        "execution_quality": _safe_float(lifecycle_obj.get("execution_quality"), 0.0),

        "setup_type": lifecycle_obj.get("setup_type", ""),
        "setup_family": lifecycle_obj.get("setup_family", ""),
        "entry_quality": lifecycle_obj.get("entry_quality", ""),
        "trend": lifecycle_obj.get("trend", ""),
        "regime": lifecycle_obj.get("regime", ""),
        "breadth": lifecycle_obj.get("breadth", ""),
        "volatility_state": lifecycle_obj.get("volatility_state", ""),

        "decision_reason": lifecycle_obj.get("decision_reason", ""),
        "vehicle_reason": lifecycle_obj.get("vehicle_reason", ""),
        "blocked_at": lifecycle_obj.get("blocked_at", ""),

        "research_approved": bool(lifecycle_obj.get("research_approved", False)),
        "execution_ready": bool(lifecycle_obj.get("execution_ready", False)),
        "selected_for_execution": bool(lifecycle_obj.get("selected_for_execution", False)),

        "reserve_check": dict(intent.reserve_check or {}),
        "governor": dict(lifecycle_obj.get("governor") or {}),

        "warnings": list(intent.warnings or []),
        "rejection_reasons": list(intent.rejection_reasons or []),
        "why": list(lifecycle_obj.get("why") or []),
        "supports": list(lifecycle_obj.get("supports") or []),
        "blockers": list(lifecycle_obj.get("blockers") or []),
        "rejection_analysis": list(lifecycle_obj.get("rejection_analysis") or []),
        "option_explanation": list(lifecycle_obj.get("option_explanation") or []),
        "learning_notes": list(lifecycle_obj.get("learning_notes") or []),
        "stronger_competing_setups": list(lifecycle_obj.get("stronger_competing_setups") or []),

        "trade_id": lifecycle_obj.get("raw", {}).get("trade_id", lifecycle_obj.get("trade_id", "")),
        "timestamp": lifecycle_obj.get("raw", {}).get("timestamp", lifecycle_obj.get("created_at")),
        "queued_at": _now_iso(),

        "lifecycle": dict(intent.source_lifecycle or {}),
    }


# =========================================================
# Guard Layer
# =========================================================

def execution_guard(
    intent: ExecutionIntent,
    portfolio_context: Optional[Dict[str, Any]] = None,
    max_open_positions: Optional[int] = None,
    current_open_positions: Optional[int] = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
) -> ExecutionGuardResult:
    portfolio_context = portfolio_context or {}
    warnings: List[str] = list(intent.warnings or [])
    rejections: List[str] = []

    if kill_switch_enabled:
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because the kill switch is enabled.",
            guard_reason_code="kill_switch_enabled",
            warnings=warnings,
            rejection_reasons=["kill_switch_enabled"],
            guard_details={"kill_switch_enabled": True},
        )

    if not session_healthy:
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because the broker or session heartbeat is unhealthy.",
            guard_reason_code="session_unhealthy",
            warnings=warnings,
            rejection_reasons=["session_unhealthy"],
            guard_details={"session_healthy": False},
        )

    if intent.final_decision not in {DECISION_APPROVE, DECISION_WARN}:
        rejections.append("lifecycle_not_execution_ready")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because lifecycle did not approve this trade.",
            guard_reason_code="lifecycle_not_execution_ready",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details={
                "final_decision": intent.final_decision,
                "final_reason_code": intent.final_reason_code,
            },
        )

    if _normalize_upper(intent.source_lifecycle.get("lifecycle_stage")) != LIFECYCLE_EXECUTION_READY:
        rejections.append("lifecycle_stage_not_ready")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because lifecycle stage is not execution ready.",
            guard_reason_code="lifecycle_stage_not_ready",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details={
                "lifecycle_stage": intent.source_lifecycle.get("lifecycle_stage"),
            },
        )

    if intent.selected_vehicle == VEHICLE_NONE:
        rejections.append("no_selected_vehicle")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because no vehicle was selected.",
            guard_reason_code="no_selected_vehicle",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details={},
        )

    if intent.quantity <= 0:
        rejections.append("invalid_quantity")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because quantity is not valid.",
            guard_reason_code="invalid_quantity",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details={"quantity": intent.quantity},
        )

    if intent.selected_vehicle == VEHICLE_OPTION and not intent.contract:
        rejections.append("missing_option_contract")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because the selected option contract is missing.",
            guard_reason_code="missing_option_contract",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details={},
        )

    if max_open_positions is not None and current_open_positions is not None:
        if int(current_open_positions) >= int(max_open_positions):
            rejections.append("max_open_positions_reached")
            return ExecutionGuardResult(
                allowed=False,
                decision=DECISION_REJECT,
                guard_reason="Execution blocked because the max open positions limit has been reached.",
                guard_reason_code="max_open_positions_reached",
                warnings=warnings,
                rejection_reasons=rejections,
                guard_details={
                    "max_open_positions": int(max_open_positions),
                    "current_open_positions": int(current_open_positions),
                },
            )

    reserve_check = intent.reserve_check or {}
    reserve_hard_block = bool(reserve_check.get("hard_block", False))
    reserve_warning_only = bool(reserve_check.get("warning_only", False))
    execution_mode = _normalize_text(intent.execution_mode, "paper").lower()

    if reserve_hard_block:
        rejections.append("reserve_hard_block")
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason="Execution blocked because reserve protection is in hard-block mode.",
            guard_reason_code="reserve_hard_block",
            warnings=warnings,
            rejection_reasons=rejections,
            guard_details=reserve_check,
        )

    if execution_mode != "live" and reserve_warning_only:
        warnings.append("paper_reserve_warning_respected")

    warnings = _dedupe_keep_order(warnings)

    return ExecutionGuardResult(
        allowed=True,
        decision=DECISION_WARN if reserve_warning_only else DECISION_APPROVE,
        guard_reason=(
            "Execution allowed with reserve warning in paper mode."
            if reserve_warning_only and execution_mode != "live"
            else "Execution allowed."
        ),
        guard_reason_code=(
            "paper_reserve_warning_respected"
            if reserve_warning_only and execution_mode != "live"
            else "execution_allowed"
        ),
        warnings=warnings,
        rejection_reasons=[],
        guard_details={
            "execution_mode": execution_mode,
            "reserve_check": reserve_check,
        },
    )


# =========================================================
# Queue State Transition
# =========================================================

def mark_lifecycle_selected_for_queue(
    lifecycle_obj: Dict[str, Any],
    queue_reason: str = "Candidate selected and handed to execution queue.",
    queue_reason_code: str = "queued_for_execution",
) -> Dict[str, Any]:
    return mark_selected(
        lifecycle_obj,
        reason=queue_reason,
        reason_code=queue_reason_code,
    )


# =========================================================
# Execution Adapters
# =========================================================

def simulate_execution(intent: ExecutionIntent) -> ExecutionResult:
    if intent.selected_vehicle == VEHICLE_OPTION:
        fill_price = _safe_float((intent.contract or {}).get("mark"))
        if fill_price <= 0:
            fill_price = _safe_float((intent.contract or {}).get("last"))
        actual_cost = round(fill_price * 100.0 * max(intent.quantity, 0), 2)

    elif intent.selected_vehicle == VEHICLE_STOCK:
        fill_price = _safe_float(intent.stock_price)
        actual_cost = round(fill_price * max(intent.quantity, 0), 2)

    else:
        return ExecutionResult(
            success=False,
            status="REJECTED",
            symbol=intent.symbol,
            selected_vehicle=intent.selected_vehicle,
            execution_mode=intent.execution_mode,
            reason="Simulation rejected because no executable vehicle was present.",
            reason_code="no_executable_vehicle",
            rejection_reasons=["no_executable_vehicle"],
        )

    lifecycle_after = mark_entered(
        intent.source_lifecycle,
        fill_price=fill_price,
        quantity=intent.quantity,
        extra_updates={
            "selected_vehicle": intent.selected_vehicle,
            "estimated_cost": round(intent.estimated_cost, 2),
            "actual_cost": actual_cost,
            "entry_mode": intent.execution_mode,
            "entry_reason": intent.final_reason,
            "entry_reason_code": intent.final_reason_code,
        },
    )

    execution_record = {
        "timestamp": _now_iso(),
        "symbol": intent.symbol,
        "vehicle": intent.selected_vehicle,
        "filled_quantity": int(intent.quantity),
        "fill_price": round(fill_price, 4),
        "estimated_cost": round(intent.estimated_cost, 2),
        "actual_cost": actual_cost,
        "execution_mode": intent.execution_mode,
        "status": "FILLED",
        "reason": intent.final_reason,
        "reason_code": intent.final_reason_code,
    }

    return ExecutionResult(
        success=True,
        status="FILLED",
        symbol=intent.symbol,
        selected_vehicle=intent.selected_vehicle,
        filled_quantity=int(intent.quantity),
        fill_price=round(fill_price, 4),
        estimated_cost=round(intent.estimated_cost, 2),
        actual_cost=actual_cost,
        broker_order_id=f"SIM-{intent.symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        execution_mode=intent.execution_mode,
        reason="Trade simulated successfully.",
        reason_code="simulated_fill",
        warnings=list(intent.warnings or []),
        rejection_reasons=[],
        lifecycle_after=lifecycle_after,
        execution_record=execution_record,
    )


def execute_via_adapter(
    queued_trade: Dict[str, Any],
    portfolio_context: Optional[Dict[str, Any]] = None,
    max_open_positions: Optional[int] = None,
    current_open_positions: Optional[int] = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
    broker_adapter: Optional[Any] = None,
) -> Dict[str, Any]:
    queued_trade = queued_trade if isinstance(queued_trade, dict) else {}
    lifecycle_obj = dict(queued_trade.get("lifecycle") or {})
    mode = _normalize_text(queued_trade.get("execution_mode"), "paper").lower()

    intent = build_execution_intent(lifecycle_obj, mode=mode)

    guard = execution_guard(
        intent=intent,
        portfolio_context=portfolio_context,
        max_open_positions=max_open_positions,
        current_open_positions=current_open_positions,
        kill_switch_enabled=kill_switch_enabled,
        session_healthy=session_healthy,
    )

    if not guard.allowed:
        return {
            "success": False,
            "status": "REJECTED",
            "symbol": intent.symbol,
            "selected_vehicle": intent.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": None,
            "lifecycle_after": lifecycle_obj,
        }

    lifecycle_for_entry = mark_lifecycle_selected_for_queue(
        lifecycle_obj,
        queue_reason=guard.guard_reason,
        queue_reason_code=guard.guard_reason_code,
    )

    intent.source_lifecycle = lifecycle_for_entry
    intent.warnings = _dedupe_keep_order(list(intent.warnings or []) + list(guard.warnings or []))

    if mode == "paper" or broker_adapter is None:
        result = simulate_execution(intent)
        return {
            "success": result.success,
            "status": result.status,
            "symbol": result.symbol,
            "selected_vehicle": result.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": asdict(result),
            "lifecycle_after": result.lifecycle_after,
        }

    adapter_response = broker_adapter.execute(asdict(intent))
    adapter_success = bool(adapter_response.get("success", False))
    adapter_status = _normalize_upper(adapter_response.get("status"), "REJECTED")

    if not adapter_success:
        return {
            "success": False,
            "status": adapter_status,
            "symbol": intent.symbol,
            "selected_vehicle": intent.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": adapter_response,
            "lifecycle_after": lifecycle_for_entry,
        }

    fill_price = _safe_float(adapter_response.get("fill_price"))
    filled_quantity = _safe_int(adapter_response.get("filled_quantity"), intent.quantity)
    actual_cost = _safe_float(adapter_response.get("actual_cost"), intent.estimated_cost)

    lifecycle_after = mark_entered(
        lifecycle_for_entry,
        fill_price=fill_price,
        quantity=filled_quantity,
        extra_updates={
            "selected_vehicle": intent.selected_vehicle,
            "estimated_cost": round(intent.estimated_cost, 2),
            "actual_cost": round(actual_cost, 2),
            "entry_mode": mode,
            "entry_reason": intent.final_reason,
            "entry_reason_code": intent.final_reason_code,
            "broker_order_id": _normalize_text(adapter_response.get("broker_order_id")),
        },
    )

    result = ExecutionResult(
        success=True,
        status=adapter_status,
        symbol=intent.symbol,
        selected_vehicle=intent.selected_vehicle,
        filled_quantity=filled_quantity,
        fill_price=round(fill_price, 4),
        estimated_cost=round(intent.estimated_cost, 2),
        actual_cost=round(actual_cost, 2),
        broker_order_id=_normalize_text(adapter_response.get("broker_order_id")),
        execution_mode=mode,
        reason=_normalize_text(adapter_response.get("reason"), "Trade executed successfully."),
        reason_code=_normalize_text(adapter_response.get("reason_code"), "live_execution_fill"),
        warnings=_dedupe_keep_order(list(intent.warnings or []) + list(guard.warnings or [])),
        rejection_reasons=[],
        lifecycle_after=lifecycle_after,
        execution_record={
            "timestamp": _now_iso(),
            "symbol": intent.symbol,
            "vehicle": intent.selected_vehicle,
            "filled_quantity": filled_quantity,
            "fill_price": round(fill_price, 4),
            "estimated_cost": round(intent.estimated_cost, 2),
            "actual_cost": round(actual_cost, 2),
            "execution_mode": mode,
            "status": adapter_status,
            "broker_order_id": _normalize_text(adapter_response.get("broker_order_id")),
            "reason": _normalize_text(adapter_response.get("reason")),
            "reason_code": _normalize_text(adapter_response.get("reason_code")),
        },
    )

    return {
        "success": result.success,
        "status": result.status,
        "symbol": result.symbol,
        "selected_vehicle": result.selected_vehicle,
        "guard": asdict(guard),
        "execution_result": asdict(result),
        "lifecycle_after": result.lifecycle_after,
    }


# =========================================================
# Public Summary Helpers
# =========================================================

def summarize_execution_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = packet if isinstance(packet, dict) else {}
    guard = packet.get("guard") or {}
    result = packet.get("execution_result") or {}
    lifecycle_after = packet.get("lifecycle_after") or {}

    return {
        "success": bool(packet.get("success", False)),
        "status": packet.get("status"),
        "symbol": packet.get("symbol"),
        "selected_vehicle": packet.get("selected_vehicle"),
        "guard_decision": guard.get("decision"),
        "guard_reason": guard.get("guard_reason"),
        "guard_reason_code": guard.get("guard_reason_code"),
        "fill_price": result.get("fill_price"),
        "filled_quantity": result.get("filled_quantity"),
        "actual_cost": result.get("actual_cost"),
        "broker_order_id": result.get("broker_order_id"),
        "lifecycle_stage_after": lifecycle_after.get("lifecycle_stage"),
        "final_reason_after": lifecycle_after.get("final_reason"),
        "final_reason_code_after": lifecycle_after.get("final_reason_code"),
    }
