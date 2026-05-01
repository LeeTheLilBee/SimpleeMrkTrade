from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from engine.observatory_mode import (
    apply_mode_to_execution_guard,
    build_mode_context,
    classify_reason_for_mode,
    normalize_mode,
)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _guard_payload(
    *,
    blocked: bool,
    reason: str,
    reason_code: str,
    warnings: Optional[List[Any]] = None,
    warning_only: bool = False,
    status_label: str = "",
    details: Optional[Dict[str, Any]] = None,
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "blocked": bool(blocked),
        "reason": _safe_str(reason, ""),
        "reason_code": _safe_str(reason_code, ""),
        "warnings": _dedupe_keep_order(warnings or []),
        "warning_only": bool(warning_only),
        "status_label": _safe_str(status_label, "OK" if not blocked else "BLOCKED"),
        "details": _safe_dict(details),
        "mode_context": _safe_dict(mode_context),
    }


def validate_selected_trade_for_execution(
    trade: Dict[str, Any],
    *,
    capital_available: float,
    trading_mode: str = "paper",
    current_open_positions: int = 0,
    max_open_positions: Optional[int] = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
    broker_healthy: bool = True,
) -> Dict[str, Any]:
    trade = deepcopy(_safe_dict(trade))
    trading_mode = normalize_mode(trading_mode or trade.get("trading_mode") or trade.get("mode"))
    mode_context = build_mode_context(trading_mode)

    symbol = _norm_symbol(trade.get("symbol"))
    selected_vehicle = _safe_str(
        trade.get("vehicle_selected", trade.get("selected_vehicle", "RESEARCH_ONLY")),
        "RESEARCH_ONLY",
    ).upper()

    if kill_switch_enabled:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Kill switch enabled.",
                reason_code="kill_switch_enabled",
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if not session_healthy:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Session unhealthy.",
                reason_code="session_unhealthy",
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if not broker_healthy:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Broker unhealthy.",
                reason_code="broker_unhealthy",
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if not _safe_bool(trade.get("research_approved"), False):
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Research approval missing.",
                reason_code="research_not_approved",
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if not _safe_bool(trade.get("execution_ready"), False):
        reason_code = _safe_str(
            trade.get("final_reason_code", trade.get("decision_reason_code", "execution_not_ready")),
            "execution_not_ready",
        )
        reason = _safe_str(
            trade.get("final_reason", trade.get("decision_reason", "Execution not ready.")),
            "Execution not ready.",
        )
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason=reason,
                reason_code=reason_code,
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if selected_vehicle == "RESEARCH_ONLY":
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Research-only candidate cannot execute.",
                reason_code="research_only_candidate",
                status_label="BLOCKED",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    cap_required = round(
        _safe_float(
            trade.get("minimum_trade_cost", trade.get("capital_required", 0.0)),
            0.0,
        ),
        4,
    )
    capital_available = round(_safe_float(capital_available, 0.0), 4)

    if cap_required <= 0:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Invalid trade cost.",
                reason_code="invalid_trade_cost",
                status_label="BLOCKED",
                details={"symbol": symbol, "capital_required": cap_required},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if capital_available <= 0:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="No buying power available.",
                reason_code="no_buying_power",
                status_label="BLOCKED",
                details={"symbol": symbol, "capital_available": capital_available},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if capital_available < cap_required:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Insufficient capital.",
                reason_code="insufficient_capital",
                status_label="BLOCKED",
                details={
                    "symbol": symbol,
                    "capital_required": cap_required,
                    "capital_available": capital_available,
                },
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if max_open_positions is None:
        max_open_positions = _safe_int(mode_context.get("max_open_positions"), 0)

    if max_open_positions > 0 and current_open_positions >= max_open_positions:
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=True,
                reason="Max open positions reached.",
                reason_code="max_open_positions_reached",
                status_label="BLOCKED",
                details={
                    "symbol": symbol,
                    "current_open_positions": current_open_positions,
                    "max_open_positions": max_open_positions,
                },
                mode_context=mode_context,
            ),
            trading_mode,
        )

    if selected_vehicle == "OPTION":
        option_obj = _safe_dict(trade.get("option", trade.get("contract", {})))
        if not option_obj:
            return apply_mode_to_execution_guard(
                _guard_payload(
                    blocked=True,
                    reason="Missing option contract.",
                    reason_code="missing_option_contract",
                    status_label="BLOCKED",
                    details={"symbol": symbol},
                    mode_context=mode_context,
                ),
                trading_mode,
            )

        option_exec_ok = _safe_bool(option_obj.get("is_executable"), False)
        option_exec_reason = _safe_str(
            option_obj.get("execution_reason", "option_not_executable"),
            "option_not_executable",
        )

        if not option_exec_ok:
            return apply_mode_to_execution_guard(
                _guard_payload(
                    blocked=True,
                    reason=f"Option contract not executable: {option_exec_reason}",
                    reason_code=option_exec_reason,
                    status_label="BLOCKED",
                    details={"symbol": symbol, "selected_vehicle": selected_vehicle},
                    mode_context=mode_context,
                ),
                trading_mode,
            )

        dte = _safe_int(option_obj.get("dte", 999), 999)
        min_dte = _safe_int(mode_context.get("minimum_option_dte", 0), 0)
        if dte < min_dte:
            return apply_mode_to_execution_guard(
                _guard_payload(
                    blocked=True,
                    reason="Option DTE below mode minimum.",
                    reason_code="option_dte_below_mode_minimum",
                    status_label="BLOCKED",
                    details={"symbol": symbol, "dte": dte, "minimum_option_dte": min_dte},
                    mode_context=mode_context,
                ),
                trading_mode,
            )

    elif selected_vehicle == "STOCK":
        shares = _safe_int(trade.get("shares", trade.get("size", 1)), 1)
        price = _safe_float(trade.get("price", trade.get("entry", 0.0)), 0.0)
        if shares <= 0 or price <= 0:
            return apply_mode_to_execution_guard(
                _guard_payload(
                    blocked=True,
                    reason="Invalid stock payload.",
                    reason_code="invalid_stock_payload",
                    status_label="BLOCKED",
                    details={"symbol": symbol, "shares": shares, "price": price},
                    mode_context=mode_context,
                ),
                trading_mode,
            )

    reserve_check = _safe_dict(trade.get("reserve_check"))
    reserve_reason_code = _safe_str(reserve_check.get("reason_code"), "")
    reserve_pressure = _safe_bool(reserve_check.get("is_pressure"), False)
    if reserve_pressure and reserve_reason_code:
        result = _guard_payload(
            blocked=True,
            reason=_safe_str(
                reserve_check.get("reason"),
                "Reserve protection flagged this setup.",
            ),
            reason_code=reserve_reason_code,
            status_label="BLOCKED",
            details={
                "symbol": symbol,
                "reserve_floor_dollars": _safe_float(reserve_check.get("reserve_floor_dollars"), 0.0),
                "cash_available": _safe_float(reserve_check.get("cash_available"), 0.0),
                "selected_vehicle": selected_vehicle,
            },
            mode_context=mode_context,
        )
        return apply_mode_to_execution_guard(result, trading_mode)

    warnings = _safe_list(trade.get("warnings"))
    if warnings and _safe_bool(mode_context.get("execution_warning_only"), False) and not _safe_bool(mode_context.get("strict_execution_gate"), True):
        return apply_mode_to_execution_guard(
            _guard_payload(
                blocked=False,
                reason="warning_only",
                reason_code="warning_only",
                warnings=warnings,
                warning_only=True,
                status_label="WARN",
                details={"symbol": symbol},
                mode_context=mode_context,
            ),
            trading_mode,
        )

    return apply_mode_to_execution_guard(
        _guard_payload(
            blocked=False,
            reason="ok",
            reason_code="ok",
            warnings=warnings,
            warning_only=False,
            status_label="OK",
            details={
                "symbol": symbol,
                "selected_vehicle": selected_vehicle,
                "capital_required": cap_required,
                "capital_available": capital_available,
            },
            mode_context=mode_context,
        ),
        trading_mode,
    )


def summarize_execution_guard(guard: Dict[str, Any]) -> Dict[str, Any]:
    guard = _safe_dict(guard)
    mode_context = _safe_dict(guard.get("mode_context"))

    return {
        "blocked": _safe_bool(guard.get("blocked"), False),
        "reason": _safe_str(guard.get("reason"), ""),
        "reason_code": _safe_str(guard.get("reason_code"), ""),
        "reason_class": classify_reason_for_mode(
            guard.get("reason_code"),
            mode_context.get("mode"),
        ),
        "warnings": _safe_list(guard.get("warnings")),
        "warning_only": _safe_bool(guard.get("warning_only"), False),
        "status_label": _safe_str(guard.get("status_label"), ""),
        "details": _safe_dict(guard.get("details")),
        "trading_mode": _safe_str(mode_context.get("mode"), ""),
        "mode_context": mode_context,
    }


__all__ = [
    "validate_selected_trade_for_execution",
    "summarize_execution_guard",
]
