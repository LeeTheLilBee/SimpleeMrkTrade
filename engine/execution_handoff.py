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
from engine.observatory_mode import (
    normalize_mode,
    build_mode_context,
    classify_reason_for_mode,
)


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
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _normalize_text(value: Any, default: str = "") -> str:
    return _safe_str(value, default)


def _normalize_upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _resolve_mode_from_lifecycle(lifecycle_obj: Dict[str, Any], mode: str = "paper") -> str:
    lifecycle_obj = _safe_dict(lifecycle_obj)
    return normalize_mode(
        mode
        or lifecycle_obj.get("trading_mode")
        or lifecycle_obj.get("execution_mode")
        or lifecycle_obj.get("mode")
        or _safe_dict(lifecycle_obj.get("mode_context")).get("mode")
        or "paper"
    )


def _merge_mode_context(lifecycle_obj: Dict[str, Any], mode: str = "paper") -> Dict[str, Any]:
    lifecycle_obj = _safe_dict(lifecycle_obj)
    resolved_mode = _resolve_mode_from_lifecycle(lifecycle_obj, mode=mode)
    base = build_mode_context(resolved_mode)
    incoming = _safe_dict(lifecycle_obj.get("mode_context"))
    merged = dict(base)
    for key, value in incoming.items():
        if value is not None:
            merged[key] = value
    merged["mode"] = normalize_mode(merged.get("mode", resolved_mode))
    return merged


def _reason_is_hard(reason_code: str, mode_context: Dict[str, Any]) -> bool:
    reason_code = _safe_str(reason_code, "")
    if not reason_code:
        return False
    if reason_code in set(_safe_list(mode_context.get("hard_block_reasons"))):
        return True
    return classify_reason_for_mode(reason_code, mode_context.get("mode")) == "hard"


def _reason_is_soft(reason_code: str, mode_context: Dict[str, Any]) -> bool:
    reason_code = _safe_str(reason_code, "")
    if not reason_code:
        return False
    if reason_code in set(_safe_list(mode_context.get("soft_block_reasons"))):
        return True
    return classify_reason_for_mode(reason_code, mode_context.get("mode")) == "soft"


def _mode_allows_warning_pass(mode_context: Dict[str, Any]) -> bool:
    mode_name = normalize_mode(mode_context.get("mode"))
    if mode_name != "survey":
        return False
    if _safe_bool(mode_context.get("strict_execution_gate"), True):
        return False
    return _safe_bool(mode_context.get("execution_warning_only"), False)


def _decision_for_reason(reason_code: str, mode_context: Dict[str, Any]) -> str:
    if _reason_is_hard(reason_code, mode_context):
        return DECISION_REJECT
    if _reason_is_soft(reason_code, mode_context):
        return DECISION_WARN if _mode_allows_warning_pass(mode_context) else DECISION_REJECT
    return DECISION_REJECT if _safe_bool(mode_context.get("strict_execution_gate"), True) else DECISION_WARN


def _derive_reason_text(code: str, fallback: str) -> str:
    return _safe_str(fallback, code or "execution_guard_blocked")


def _preferred_final_reason_code(source: Dict[str, Any]) -> str:
    return _safe_str(
        source.get("final_reason_code")
        or source.get("decision_reason_code")
        or source.get("final_reason")
        or source.get("decision_reason")
        or "",
        "",
    )


def _preferred_final_reason(source: Dict[str, Any]) -> str:
    return _safe_str(
        source.get("final_reason")
        or source.get("decision_reason")
        or source.get("decision_label")
        or "",
        "",
    )


def _preserve_preferred(primary: Dict[str, Any], fallback: Dict[str, Any], key: str, default: Any = None) -> Any:
    if key in primary and primary.get(key) is not None:
        return primary.get(key)
    if key in fallback and fallback.get(key) is not None:
        return fallback.get(key)
    return default


def _merge_lifecycle_with_trade_fields(lifecycle_obj: Dict[str, Any], trade_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    lifecycle_obj = _safe_dict(lifecycle_obj)
    trade_obj = _safe_dict(trade_obj)

    merged = dict(lifecycle_obj)

    preserve_keys = [
        "trade_id",
        "timestamp",
        "queued_at",
        "research_approved",
        "execution_ready",
        "selected_for_execution",
        "selected_vehicle",
        "vehicle_selected",
        "vehicle",
        "final_decision",
        "final_reason",
        "final_reason_code",
        "decision_reason",
        "decision_reason_code",
        "score",
        "fused_score",
        "base_score",
        "v2_score",
        "v2_quality",
        "v2_reason",
        "v2_vehicle_bias",
        "readiness_score",
        "promotion_score",
        "rebuild_pressure",
        "execution_quality",
        "minimum_trade_cost",
        "capital_required",
        "capital_available",
        "capital_buffer_after",
        "confidence",
        "strategy",
        "direction",
        "symbol",
        "contracts",
        "shares",
        "estimated_cost",
        "stock_price",
        "reserve_check",
        "warnings",
        "rejection_reasons",
        "governor",
        "option",
        "stock_path",
        "option_path",
        "top_ranked_contracts",
        "why",
        "supports",
        "blockers",
        "rejection_analysis",
        "option_explanation",
        "learning_notes",
        "setup_type",
        "setup_family",
        "entry_quality",
        "trend",
        "regime",
        "breadth",
        "volatility_state",
        "trading_mode",
        "execution_mode",
        "mode",
        "mode_context",
        "contract",
    ]

    for key in preserve_keys:
        preferred = _preserve_preferred(trade_obj, lifecycle_obj, key, None)
        if preferred is not None:
            merged[key] = preferred

    if "raw" not in merged:
        merged["raw"] = _safe_dict(lifecycle_obj.get("raw"))
    if not merged.get("raw") and isinstance(trade_obj.get("raw"), dict):
        merged["raw"] = _safe_dict(trade_obj.get("raw"))

    return merged


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
    mode_context: Dict[str, Any] = field(default_factory=dict)


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


def build_execution_intent(
    lifecycle_obj: Dict[str, Any],
    mode: str = "paper",
) -> ExecutionIntent:
    lifecycle_obj = _safe_dict(lifecycle_obj)
    resolved_mode = _resolve_mode_from_lifecycle(lifecycle_obj, mode=mode)
    mode_context = _merge_mode_context(lifecycle_obj, mode=resolved_mode)

    selected_vehicle = _normalize_upper(
        lifecycle_obj.get("selected_vehicle")
        or lifecycle_obj.get("vehicle_selected")
        or lifecycle_obj.get("vehicle"),
        VEHICLE_NONE,
    )

    contracts = _safe_int(lifecycle_obj.get("contracts"))
    shares = _safe_int(lifecycle_obj.get("shares"))
    quantity = contracts if selected_vehicle == VEHICLE_OPTION else shares

    raw = _safe_dict(lifecycle_obj.get("raw"))
    contract = lifecycle_obj.get("contract") if isinstance(lifecycle_obj.get("contract"), dict) else None
    if not contract:
        option_obj = lifecycle_obj.get("option")
        if isinstance(option_obj, dict):
            contract = dict(option_obj)

    return ExecutionIntent(
        symbol=_normalize_upper(lifecycle_obj.get("symbol")),
        strategy=_normalize_upper(lifecycle_obj.get("strategy"), "UNKNOWN"),
        direction=_normalize_upper(lifecycle_obj.get("direction"), "UNKNOWN"),
        selected_vehicle=selected_vehicle,
        final_decision=_normalize_upper(lifecycle_obj.get("final_decision"), DECISION_REJECT),
        final_reason=_normalize_text(
            lifecycle_obj.get("final_reason"),
            _preferred_final_reason(lifecycle_obj),
        ),
        final_reason_code=_normalize_text(
            lifecycle_obj.get("final_reason_code"),
            _preferred_final_reason_code(lifecycle_obj),
        ),
        quantity=max(0, quantity),
        estimated_cost=_safe_float(lifecycle_obj.get("estimated_cost")),
        stock_price=_safe_float(
            raw.get("underlying_price")
            or raw.get("price")
            or lifecycle_obj.get("stock_price")
            or lifecycle_obj.get("price")
        ),
        contract=contract,
        execution_mode=resolved_mode,
        confidence=_normalize_upper(lifecycle_obj.get("confidence"), "UNKNOWN"),
        score=_safe_float(lifecycle_obj.get("score", lifecycle_obj.get("fused_score", 0.0))),
        reserve_check=_safe_dict(lifecycle_obj.get("reserve_check")),
        warnings=_dedupe_keep_order(lifecycle_obj.get("warnings") or []),
        rejection_reasons=_dedupe_keep_order(lifecycle_obj.get("rejection_reasons") or []),
        source_lifecycle=dict(lifecycle_obj),
        mode_context=mode_context,
    )


def build_queued_trade_payload(
    lifecycle_obj: Dict[str, Any],
    mode: str = "paper",
) -> Dict[str, Any]:
    lifecycle_obj = _safe_dict(lifecycle_obj)

    requested_mode = _resolve_mode_from_lifecycle(lifecycle_obj, mode=mode)
    merged_source = _merge_lifecycle_with_trade_fields(lifecycle_obj, lifecycle_obj)
    merged_source["trading_mode"] = requested_mode
    merged_source["execution_mode"] = requested_mode
    merged_source["mode"] = requested_mode
    merged_source["mode_context"] = _merge_mode_context(merged_source, mode=requested_mode)

    intent = build_execution_intent(merged_source, mode=requested_mode)
    source = dict(intent.source_lifecycle or {})
    mode_context = _safe_dict(intent.mode_context)

    reserve_check = _safe_dict(intent.reserve_check)
    selected_vehicle = _safe_str(
        intent.selected_vehicle,
        source.get("selected_vehicle", source.get("vehicle_selected", "RESEARCH_ONLY")),
    ).upper()
    final_decision = _safe_str(
        intent.final_decision,
        source.get("final_decision", "REJECT"),
    ).upper()
    final_reason = _safe_str(intent.final_reason, _preferred_final_reason(source))
    final_reason_code = _safe_str(intent.final_reason_code, _preferred_final_reason_code(source))
    estimated_cost = round(_safe_float(intent.estimated_cost, source.get("estimated_cost", 0.0)), 2)
    stock_price = round(_safe_float(intent.stock_price, source.get("stock_price", 0.0)), 4)

    research_approved = _safe_bool(
        _preserve_preferred(lifecycle_obj, source, "research_approved", False),
        False,
    )
    execution_ready = _safe_bool(
        _preserve_preferred(lifecycle_obj, source, "execution_ready", False),
        False,
    )
    selected_for_execution = _safe_bool(
        _preserve_preferred(lifecycle_obj, source, "selected_for_execution", False),
        False,
    )
    preserved_trade_id = _safe_str(
        _preserve_preferred(lifecycle_obj, source, "trade_id", ""),
        "",
    )
    preserved_timestamp = _safe_str(
        _preserve_preferred(lifecycle_obj, source, "timestamp", ""),
        "",
    )

    source["mode"] = requested_mode
    source["trading_mode"] = requested_mode
    source["execution_mode"] = requested_mode
    source["mode_context"] = mode_context
    source["selected_vehicle"] = selected_vehicle
    source["vehicle_selected"] = selected_vehicle
    source["vehicle"] = selected_vehicle
    source["final_decision"] = final_decision
    source["final_reason"] = final_reason
    source["final_reason_code"] = final_reason_code
    source["decision_reason"] = _safe_str(source.get("decision_reason"), final_reason)
    source["decision_reason_code"] = _safe_str(source.get("decision_reason_code"), final_reason_code)
    source["estimated_cost"] = estimated_cost
    source["stock_price"] = stock_price
    source["reserve_check"] = reserve_check
    source["research_approved"] = research_approved
    source["execution_ready"] = execution_ready
    source["selected_for_execution"] = selected_for_execution
    source["trade_id"] = preserved_trade_id
    source["timestamp"] = preserved_timestamp or source.get("timestamp") or _now_iso()

    queued_payload = {
        "symbol": intent.symbol,
        "strategy": intent.strategy,
        "direction": intent.direction,
        "selected_vehicle": selected_vehicle,
        "vehicle_selected": selected_vehicle,
        "vehicle": selected_vehicle,
        "final_decision": final_decision,
        "final_reason": final_reason,
        "final_reason_code": final_reason_code,
        "decision_reason": _safe_str(source.get("decision_reason"), final_reason),
        "decision_reason_code": _safe_str(source.get("decision_reason_code"), final_reason_code),
        "quantity": intent.quantity,
        "estimated_cost": estimated_cost,
        "stock_price": stock_price,
        "contract": intent.contract,
        "execution_mode": requested_mode,
        "trading_mode": requested_mode,
        "mode": requested_mode,
        "mode_context": mode_context,
        "confidence": intent.confidence,
        "score": round(_safe_float(intent.score), 4),
        "reserve_check": reserve_check,
        "warnings": _dedupe_keep_order(intent.warnings or source.get("warnings")),
        "rejection_reasons": _dedupe_keep_order(intent.rejection_reasons or source.get("rejection_reasons")),
        "lifecycle": source,
        "queued_at": _now_iso(),
        "research_approved": research_approved,
        "execution_ready": execution_ready,
        "selected_for_execution": selected_for_execution,
        "base_score": source.get("base_score"),
        "fused_score": source.get("fused_score"),
        "v2_score": source.get("v2_score"),
        "v2_quality": source.get("v2_quality"),
        "v2_reason": source.get("v2_reason"),
        "v2_vehicle_bias": source.get("v2_vehicle_bias"),
        "v2_payload": _safe_dict(source.get("v2_payload", {})),
        "readiness_score": source.get("readiness_score"),
        "promotion_score": source.get("promotion_score"),
        "rebuild_pressure": source.get("rebuild_pressure"),
        "execution_quality": source.get("execution_quality"),
        "minimum_trade_cost": source.get("minimum_trade_cost"),
        "capital_required": source.get("capital_required"),
        "capital_available": source.get("capital_available"),
        "capital_buffer_after": source.get("capital_buffer_after"),
        "vehicle_reason": source.get("vehicle_reason"),
        "blocked_at": source.get("blocked_at"),
        "why": _safe_list(source.get("why", [])),
        "supports": _safe_list(source.get("supports", [])),
        "blockers": _safe_list(source.get("blockers", [])),
        "rejection_analysis": _safe_list(source.get("rejection_analysis", [])),
        "option_explanation": _safe_list(source.get("option_explanation", [])),
        "learning_notes": _safe_list(source.get("learning_notes", [])),
        "setup_type": source.get("setup_type"),
        "setup_family": source.get("setup_family"),
        "entry_quality": source.get("entry_quality"),
        "trend": source.get("trend"),
        "regime": source.get("regime"),
        "breadth": source.get("breadth"),
        "volatility_state": source.get("volatility_state"),
        "option": _safe_dict(source.get("option", {})),
        "stock_path": _safe_dict(source.get("stock_path", {})),
        "option_path": _safe_dict(source.get("option_path", {})),
        "governor": _safe_dict(source.get("governor", {})),
        "top_ranked_contracts": _safe_list(source.get("top_ranked_contracts", [])),
        "trade_id": preserved_trade_id,
        "timestamp": source.get("timestamp"),
        "canonical_source": "options_lifecycle",
    }

    if selected_vehicle == VEHICLE_OPTION:
        queued_payload["contracts"] = max(1, _safe_int(source.get("contracts", intent.quantity or 1), 1))
        queued_payload["shares"] = 0
    elif selected_vehicle == VEHICLE_STOCK:
        queued_payload["shares"] = max(1, _safe_int(source.get("shares", intent.quantity or 1), 1))
        queued_payload["contracts"] = 0
    else:
        queued_payload["shares"] = _safe_int(source.get("shares", 0), 0)
        queued_payload["contracts"] = _safe_int(source.get("contracts", 0), 0)

    queued_payload["queue_diagnostics"] = {
        "mode_label": mode_context.get("mode_label"),
        "mode_shell": mode_context.get("mode_shell"),
        "theme_family": mode_context.get("theme_family"),
        "strict_execution_gate": _safe_bool(mode_context.get("strict_execution_gate"), True),
        "execution_warning_only": _safe_bool(mode_context.get("execution_warning_only"), False),
        "reserve_warning_only": _safe_bool(mode_context.get("reserve_warning_only"), False),
        "options_first": _safe_bool(mode_context.get("options_first"), True),
        "allow_stock_fallback": _safe_bool(mode_context.get("allow_stock_fallback"), True),
        "reserve_check": reserve_check,
        "preserved_trade_id": preserved_trade_id,
        "preserved_selected_for_execution": selected_for_execution,
        "preserved_execution_ready": execution_ready,
    }

    return queued_payload


def execution_guard(
    intent: ExecutionIntent,
    portfolio_context: Optional[Dict[str, Any]] = None,
    max_open_positions: Optional[int] = None,
    current_open_positions: Optional[int] = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
) -> ExecutionGuardResult:
    portfolio_context = _safe_dict(portfolio_context)
    mode_context = _safe_dict(intent.mode_context) or build_mode_context(intent.execution_mode)
    warnings: List[str] = _dedupe_keep_order(intent.warnings or [])
    rejections: List[str] = []

    def _reject(reason: str, code: str, details: Optional[Dict[str, Any]] = None) -> ExecutionGuardResult:
        return ExecutionGuardResult(
            allowed=False,
            decision=DECISION_REJECT,
            guard_reason=reason,
            guard_reason_code=code,
            warnings=warnings,
            rejection_reasons=_dedupe_keep_order(rejections + [code]),
            guard_details=_safe_dict(details),
        )

    def _warn_or_reject(reason: str, code: str, details: Optional[Dict[str, Any]] = None) -> ExecutionGuardResult:
        decision = _decision_for_reason(code, mode_context)
        if decision == DECISION_WARN:
            merged_warnings = _dedupe_keep_order(warnings + [code])
            return ExecutionGuardResult(
                allowed=True,
                decision=DECISION_WARN,
                guard_reason=reason,
                guard_reason_code=code,
                warnings=merged_warnings,
                rejection_reasons=[],
                guard_details=_safe_dict(details),
            )
        return _reject(reason, code, details)

    if kill_switch_enabled:
        return _reject(
            "Execution blocked because the kill switch is enabled.",
            "kill_switch_enabled",
            {"kill_switch_enabled": True},
        )

    if not session_healthy:
        return _reject(
            "Execution blocked because the broker or session heartbeat is unhealthy.",
            "session_unhealthy",
            {"session_healthy": False},
        )

    if intent.final_decision not in {DECISION_APPROVE, DECISION_WARN}:
        reason_code = intent.final_reason_code or "lifecycle_not_execution_ready"
        reason_text = _derive_reason_text(
            reason_code,
            intent.final_reason or "Execution blocked because lifecycle did not approve this trade.",
        )
        return _warn_or_reject(
            reason_text,
            reason_code,
            {
                "final_decision": intent.final_decision,
                "final_reason": intent.final_reason,
                "final_reason_code": intent.final_reason_code,
            },
        )

    if _normalize_upper(intent.source_lifecycle.get("lifecycle_stage")) != LIFECYCLE_EXECUTION_READY:
        return _warn_or_reject(
            "Execution blocked because lifecycle stage is not execution ready.",
            "lifecycle_stage_not_ready",
            {
                "lifecycle_stage": intent.source_lifecycle.get("lifecycle_stage"),
            },
        )

    if intent.selected_vehicle == VEHICLE_NONE:
        return _reject(
            "Execution blocked because no vehicle was selected.",
            "no_selected_vehicle",
            {},
        )

    if intent.quantity <= 0:
        return _reject(
            "Execution blocked because quantity is not valid.",
            "invalid_quantity",
            {"quantity": intent.quantity},
        )

    if intent.selected_vehicle == VEHICLE_OPTION and not intent.contract:
        return _reject(
            "Execution blocked because the selected option contract is missing.",
            "missing_option_contract",
            {},
        )

    if max_open_positions is not None and current_open_positions is not None:
        if int(current_open_positions) >= int(max_open_positions):
            return _warn_or_reject(
                "Execution blocked because the max open positions limit has been reached.",
                "max_open_positions_reached",
                {
                    "max_open_positions": int(max_open_positions),
                    "current_open_positions": int(current_open_positions),
                },
            )

    reserve_check = _safe_dict(intent.reserve_check)
    reserve_hard_block = _safe_bool(reserve_check.get("hard_block"), False)
    reserve_warning_only = _safe_bool(reserve_check.get("warning_only"), False)

    if reserve_hard_block:
        reserve_code = _safe_str(reserve_check.get("reason_code"), "reserve_hard_block")
        reserve_text = _derive_reason_text(
            reserve_code,
            _safe_str(reserve_check.get("reason"), "Execution blocked because reserve protection is in hard-block mode."),
        )
        return _reject(reserve_text, reserve_code, reserve_check)

    if reserve_warning_only:
        reserve_code = _safe_str(reserve_check.get("reason_code"), "reserve_warning_only")
        reserve_text = _derive_reason_text(
            reserve_code,
            _safe_str(reserve_check.get("reason"), "Execution allowed with reserve warning."),
        )
        decision = _decision_for_reason(reserve_code, mode_context)
        if decision == DECISION_WARN:
            warnings = _dedupe_keep_order(warnings + [reserve_code])
            return ExecutionGuardResult(
                allowed=True,
                decision=DECISION_WARN,
                guard_reason=reserve_text,
                guard_reason_code=reserve_code,
                warnings=warnings,
                rejection_reasons=[],
                guard_details={"reserve_check": reserve_check},
            )
        return _reject(reserve_text, reserve_code, {"reserve_check": reserve_check})

    return ExecutionGuardResult(
        allowed=True,
        decision=DECISION_APPROVE,
        guard_reason="Execution allowed.",
        guard_reason_code="execution_allowed",
        warnings=_dedupe_keep_order(warnings),
        rejection_reasons=[],
        guard_details={
            "execution_mode": intent.execution_mode,
            "reserve_check": reserve_check,
            "mode_context": mode_context,
        },
    )


def mark_lifecycle_selected_for_queue(
    lifecycle_obj: Dict[str, Any],
    queue_reason: str = "Candidate selected and handed to execution queue.",
    queue_reason_code: str = "queued_for_execution",
) -> Dict[str, Any]:
    updated = mark_selected(
        lifecycle_obj,
        reason=queue_reason,
        reason_code=queue_reason_code,
    )
    updated = _safe_dict(updated)
    updated["selected_for_execution"] = True
    updated["execution_ready"] = True
    if not updated.get("trade_id"):
        updated["trade_id"] = _safe_str(_safe_dict(lifecycle_obj).get("trade_id"), "")
    return updated


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
            "vehicle_selected": intent.selected_vehicle,
            "estimated_cost": round(intent.estimated_cost, 2),
            "actual_cost": actual_cost,
            "entry_mode": intent.execution_mode,
            "entry_reason": intent.final_reason,
            "entry_reason_code": intent.final_reason_code,
            "final_reason": "entered_execution",
            "final_reason_code": "entered_execution",
            "decision_reason": intent.final_reason,
            "decision_reason_code": intent.final_reason_code,
            "blocked_at": "",
            "trading_mode": intent.execution_mode,
            "execution_mode": intent.execution_mode,
            "mode": intent.execution_mode,
            "mode_context": intent.mode_context,
            "selected_for_execution": True,
            "execution_ready": True,
            "trade_id": _safe_str(intent.source_lifecycle.get("trade_id"), ""),
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
        "mode_context": intent.mode_context,
        "trade_id": _safe_str(lifecycle_after.get("trade_id"), ""),
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
        warnings=_dedupe_keep_order(intent.warnings or []),
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
    queued_trade = _safe_dict(queued_trade)

    raw_lifecycle = _safe_dict(queued_trade.get("lifecycle"))
    merged_lifecycle = _merge_lifecycle_with_trade_fields(raw_lifecycle, queued_trade)

    requested_mode = _resolve_mode_from_lifecycle(
        merged_lifecycle,
        mode=_safe_str(
            queued_trade.get("execution_mode")
            or queued_trade.get("trading_mode")
            or queued_trade.get("mode"),
            "paper",
        ),
    )
    mode_context = _merge_mode_context(merged_lifecycle, mode=requested_mode)

    merged_lifecycle["trading_mode"] = requested_mode
    merged_lifecycle["execution_mode"] = requested_mode
    merged_lifecycle["mode"] = requested_mode
    merged_lifecycle["mode_context"] = mode_context
    merged_lifecycle["trade_id"] = _safe_str(
        _preserve_preferred(queued_trade, merged_lifecycle, "trade_id", ""),
        "",
    )
    merged_lifecycle["research_approved"] = _safe_bool(
        _preserve_preferred(queued_trade, merged_lifecycle, "research_approved", False),
        False,
    )
    merged_lifecycle["execution_ready"] = _safe_bool(
        _preserve_preferred(queued_trade, merged_lifecycle, "execution_ready", False),
        False,
    )
    merged_lifecycle["selected_for_execution"] = _safe_bool(
        _preserve_preferred(queued_trade, merged_lifecycle, "selected_for_execution", False),
        False,
    )

    intent = build_execution_intent(merged_lifecycle, mode=requested_mode)

    guard = execution_guard(
        intent=intent,
        portfolio_context=portfolio_context,
        max_open_positions=max_open_positions,
        current_open_positions=current_open_positions,
        kill_switch_enabled=kill_switch_enabled,
        session_healthy=session_healthy,
    )

    if not guard.allowed:
        merged_lifecycle["final_reason"] = guard.guard_reason or intent.final_reason
        merged_lifecycle["final_reason_code"] = guard.guard_reason_code or intent.final_reason_code
        merged_lifecycle["decision_reason"] = guard.guard_reason or intent.final_reason
        merged_lifecycle["decision_reason_code"] = guard.guard_reason_code or intent.final_reason_code
        merged_lifecycle["blocked_at"] = "execution_guard"
        merged_lifecycle["selected_for_execution"] = _safe_bool(
            merged_lifecycle.get("selected_for_execution"),
            False,
        )
        return {
            "success": False,
            "status": "REJECTED",
            "symbol": intent.symbol,
            "selected_vehicle": intent.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": None,
            "lifecycle_after": merged_lifecycle,
            "trading_mode": requested_mode,
            "mode_context": mode_context,
        }

    lifecycle_for_entry = mark_lifecycle_selected_for_queue(
        merged_lifecycle,
        queue_reason=guard.guard_reason,
        queue_reason_code=guard.guard_reason_code,
    )
    lifecycle_for_entry["trading_mode"] = requested_mode
    lifecycle_for_entry["execution_mode"] = requested_mode
    lifecycle_for_entry["mode"] = requested_mode
    lifecycle_for_entry["mode_context"] = mode_context
    lifecycle_for_entry["trade_id"] = _safe_str(
        _preserve_preferred(queued_trade, lifecycle_for_entry, "trade_id", ""),
        "",
    )

    intent.source_lifecycle = lifecycle_for_entry
    intent.warnings = _dedupe_keep_order(list(intent.warnings or []) + list(guard.warnings or []))
    intent.mode_context = mode_context

    if requested_mode == "paper" or broker_adapter is None:
        result = simulate_execution(intent)
        return {
            "success": result.success,
            "status": result.status,
            "symbol": result.symbol,
            "selected_vehicle": result.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": asdict(result),
            "lifecycle_after": result.lifecycle_after,
            "trading_mode": requested_mode,
            "mode_context": mode_context,
        }

    adapter_response = _safe_dict(broker_adapter.execute(asdict(intent)))
    adapter_success = _safe_bool(adapter_response.get("success"), False)
    adapter_status = _normalize_upper(adapter_response.get("status"), "REJECTED")

    if not adapter_success:
        reason_code = _normalize_text(adapter_response.get("reason_code"), "live_execution_rejected")
        reason_text = _normalize_text(adapter_response.get("reason"), "Broker adapter rejected the trade.")
        lifecycle_for_entry["final_reason"] = reason_text
        lifecycle_for_entry["final_reason_code"] = reason_code
        lifecycle_for_entry["decision_reason"] = reason_text
        lifecycle_for_entry["decision_reason_code"] = reason_code
        lifecycle_for_entry["blocked_at"] = "broker_adapter"
        return {
            "success": False,
            "status": adapter_status,
            "symbol": intent.symbol,
            "selected_vehicle": intent.selected_vehicle,
            "guard": asdict(guard),
            "execution_result": adapter_response,
            "lifecycle_after": lifecycle_for_entry,
            "trading_mode": requested_mode,
            "mode_context": mode_context,
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
            "vehicle_selected": intent.selected_vehicle,
            "estimated_cost": round(intent.estimated_cost, 2),
            "actual_cost": round(actual_cost, 2),
            "entry_mode": requested_mode,
            "entry_reason": intent.final_reason,
            "entry_reason_code": intent.final_reason_code,
            "final_reason": "entered_execution",
            "final_reason_code": "entered_execution",
            "decision_reason": intent.final_reason,
            "decision_reason_code": intent.final_reason_code,
            "broker_order_id": _normalize_text(adapter_response.get("broker_order_id")),
            "blocked_at": "",
            "trading_mode": requested_mode,
            "execution_mode": requested_mode,
            "mode": requested_mode,
            "mode_context": mode_context,
            "selected_for_execution": True,
            "execution_ready": True,
            "trade_id": _safe_str(lifecycle_for_entry.get("trade_id"), ""),
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
        execution_mode=requested_mode,
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
            "execution_mode": requested_mode,
            "status": adapter_status,
            "broker_order_id": _normalize_text(adapter_response.get("broker_order_id")),
            "reason": _normalize_text(adapter_response.get("reason")),
            "reason_code": _normalize_text(adapter_response.get("reason_code")),
            "mode_context": mode_context,
            "trade_id": _safe_str(lifecycle_after.get("trade_id"), ""),
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
        "trading_mode": requested_mode,
        "mode_context": mode_context,
    }


def summarize_execution_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(packet)
    guard = _safe_dict(packet.get("guard"))
    result = _safe_dict(packet.get("execution_result"))
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    return {
        "success": _safe_bool(packet.get("success"), False),
        "status": packet.get("status"),
        "symbol": packet.get("symbol"),
        "selected_vehicle": packet.get("selected_vehicle"),
        "guard": guard,
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
        "decision_reason_after": lifecycle_after.get("decision_reason"),
        "decision_reason_code_after": lifecycle_after.get("decision_reason_code"),
        "trade_id_after": lifecycle_after.get("trade_id"),
        "selected_for_execution_after": lifecycle_after.get("selected_for_execution"),
        "execution_ready_after": lifecycle_after.get("execution_ready"),
        "trading_mode": packet.get("trading_mode"),
        "mode_context": packet.get("mode_context"),
    }
