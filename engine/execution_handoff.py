from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict

from engine.canonical_trade_state import build_open_trade_state
from engine.canonical_execution_guard import validate_selected_trade_for_execution
from engine.observatory_mode import build_mode_context, normalize_mode


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


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


def _now_iso() -> str:
    return datetime.now().isoformat()


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _derive_trade_id(symbol: str, strategy: str, timestamp: str) -> str:
    stamp = _safe_str(timestamp, _now_iso()).replace(":", "").replace("-", "").replace(".", "")
    return f"{symbol}-{strategy}-{stamp}"


def _resolve_mode_context(
    trading_mode: str,
    incoming_mode_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    resolved = build_mode_context(normalize_mode(trading_mode))
    incoming = _safe_dict(incoming_mode_context)
    merged = dict(resolved)

    for key, value in incoming.items():
        if value is not None:
            merged[key] = value

    merged["mode"] = normalize_mode(merged.get("mode", trading_mode))
    return merged


def _normalize_selected_vehicle(
    lifecycle_obj: Dict[str, Any],
    raw: Dict[str, Any],
) -> str:
    vehicle = _safe_str(
        lifecycle_obj.get("selected_vehicle")
        or lifecycle_obj.get("vehicle_selected")
        or raw.get("vehicle_selected")
        or raw.get("selected_vehicle")
        or raw.get("vehicle"),
        "RESEARCH_ONLY",
    ).upper()

    if vehicle not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        return "RESEARCH_ONLY"
    return vehicle


def _normalize_contract_payload(
    lifecycle_obj: Dict[str, Any],
    raw: Dict[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    contract = _safe_dict(lifecycle_obj.get("contract"))
    option = _safe_dict(lifecycle_obj.get("option"))

    if not contract:
        contract = _safe_dict(raw.get("contract"))
    if not option:
        option = _safe_dict(raw.get("option"))

    if option and not contract:
        contract = dict(option)
    if contract and not option:
        option = dict(contract)

    return contract, option


def build_queued_trade_payload(
    lifecycle_obj: Dict[str, Any],
    *,
    mode: str = "paper",
) -> Dict[str, Any]:
    lifecycle_obj = deepcopy(_safe_dict(lifecycle_obj))
    raw = deepcopy(_safe_dict(lifecycle_obj.get("raw")))

    trading_mode = normalize_mode(
        mode
        or lifecycle_obj.get("trading_mode")
        or lifecycle_obj.get("execution_mode")
        or lifecycle_obj.get("mode")
        or raw.get("trading_mode")
        or raw.get("execution_mode")
        or raw.get("mode")
        or "paper"
    )

    mode_context = _resolve_mode_context(
        trading_mode,
        lifecycle_obj.get("mode_context") or raw.get("mode_context"),
    )

    symbol = _norm_symbol(lifecycle_obj.get("symbol") or raw.get("symbol"))
    strategy = _safe_str(
        lifecycle_obj.get("strategy") or raw.get("strategy"),
        "CALL",
    ).upper()

    timestamp = _safe_str(
        lifecycle_obj.get("updated_at")
        or lifecycle_obj.get("timestamp")
        or raw.get("timestamp"),
        _now_iso(),
    )

    trade_id = _safe_str(
        lifecycle_obj.get("trade_id") or raw.get("trade_id"),
        _derive_trade_id(symbol, strategy, timestamp),
    )

    vehicle_selected = _normalize_selected_vehicle(lifecycle_obj, raw)
    contract, option = _normalize_contract_payload(lifecycle_obj, raw)

    payload: Dict[str, Any] = {}
    payload.update(raw)
    payload.update(lifecycle_obj)

    payload["symbol"] = symbol
    payload["strategy"] = strategy
    payload["trade_id"] = trade_id
    payload["timestamp"] = timestamp

    payload["trading_mode"] = trading_mode
    payload["execution_mode"] = trading_mode
    payload["mode"] = trading_mode
    payload["mode_context"] = mode_context

    payload["vehicle_selected"] = vehicle_selected
    payload["selected_vehicle"] = vehicle_selected
    payload["vehicle"] = vehicle_selected

    payload["research_approved"] = _safe_bool(
        lifecycle_obj.get("research_approved", raw.get("research_approved", True)),
        True,
    )
    payload["execution_ready"] = _safe_bool(
        lifecycle_obj.get("execution_ready", raw.get("execution_ready", True)),
        True,
    )
    payload["selected_for_execution"] = _safe_bool(
        lifecycle_obj.get("selected_for_execution", raw.get("selected_for_execution", False)),
        False,
    )

    payload["lifecycle_stage"] = _safe_str(
        lifecycle_obj.get("lifecycle_stage", raw.get("lifecycle_stage", "SELECTED")),
        "SELECTED",
    )

    payload["final_reason"] = _safe_str(
        lifecycle_obj.get("final_reason", raw.get("final_reason", "selected_for_execution")),
        "selected_for_execution",
    )
    payload["final_reason_code"] = _safe_str(
        lifecycle_obj.get("final_reason_code", raw.get("final_reason_code", "selected_for_execution")),
        "selected_for_execution",
    )
    payload["decision_reason"] = _safe_str(
        lifecycle_obj.get("decision_reason", raw.get("decision_reason", payload["final_reason"])),
        payload["final_reason"],
    )
    payload["decision_reason_code"] = _safe_str(
        lifecycle_obj.get("decision_reason_code", raw.get("decision_reason_code", payload["final_reason_code"])),
        payload["final_reason_code"],
    )

    payload["capital_required"] = round(
        _safe_float(lifecycle_obj.get("capital_required", raw.get("capital_required", 0.0)), 0.0),
        4,
    )
    payload["minimum_trade_cost"] = round(
        _safe_float(lifecycle_obj.get("minimum_trade_cost", raw.get("minimum_trade_cost", 0.0)), 0.0),
        4,
    )
    payload["capital_available"] = round(
        _safe_float(lifecycle_obj.get("capital_available", raw.get("capital_available", 0.0)), 0.0),
        4,
    )

    payload["contracts"] = _safe_int(lifecycle_obj.get("contracts", raw.get("contracts", 0)), 0)
    payload["shares"] = _safe_int(lifecycle_obj.get("shares", raw.get("shares", 0)), 0)

    payload["contract"] = contract
    payload["option"] = option
    payload["option_contract_score"] = round(
        _safe_float(
            lifecycle_obj.get(
                "option_contract_score",
                raw.get("option_contract_score", option.get("contract_score", 0.0)),
            ),
            0.0,
        ),
        4,
    )

    if option:
        payload["contract_symbol"] = _safe_str(
            option.get("contract_symbol") or option.get("contractSymbol"),
            "",
        )
        payload["expiry"] = _safe_str(
            option.get("expiry") or option.get("expiration"),
            "",
        )
        payload["strike"] = _safe_float(option.get("strike"), 0.0)
        payload["right"] = _safe_str(option.get("right"), strategy)
        payload["mark"] = _safe_float(
            option.get("mark", option.get("last", option.get("price", 0.0))),
            0.0,
        )
        payload["bid"] = _safe_float(option.get("bid"), 0.0)
        payload["ask"] = _safe_float(option.get("ask"), 0.0)
        payload["open_interest"] = _safe_int(
            option.get("open_interest", option.get("openInterest", 0)),
            0,
        )
        payload["volume"] = _safe_int(option.get("volume", 0), 0)
        payload["dte"] = _safe_int(option.get("dte", option.get("daysToExpiration", 0)), 0)

    payload["lifecycle"] = deepcopy(lifecycle_obj)

    payload["open_trade_state_preview"] = build_open_trade_state(
        payload,
        lifecycle=lifecycle_obj,
        execution_result={},
        mode=trading_mode,
        mode_context=mode_context,
    )

    return payload


def _simulate_fill(
    queued_trade: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(queued_trade)

    vehicle_selected = _safe_str(
        queued_trade.get("vehicle_selected", queued_trade.get("selected_vehicle", "STOCK")),
        "STOCK",
    ).upper()

    option = _safe_dict(queued_trade.get("option"))
    symbol = _norm_symbol(queued_trade.get("symbol"))
    strategy = _safe_str(queued_trade.get("strategy"), "CALL").upper()

    if vehicle_selected == "OPTION":
        fill_price = _safe_float(
            queued_trade.get(
                "fill_price",
                option.get("mark", option.get("last", option.get("price", queued_trade.get("price", 0.0)))),
            ),
            0.0,
        )
        quantity = max(1, _safe_int(queued_trade.get("contracts", 1), 1))
        actual_cost = round(fill_price * 100 * quantity, 4)
    else:
        fill_price = _safe_float(
            queued_trade.get("fill_price", queued_trade.get("price", queued_trade.get("entry", 0.0))),
            0.0,
        )
        quantity = max(1, _safe_int(queued_trade.get("shares", queued_trade.get("size", 1)), 1))
        actual_cost = round(fill_price * quantity, 4)

    commission = 1.0
    actual_cost = round(actual_cost + commission, 4)
    opened_at = _now_iso()

    execution_record = {
        "trade_id": _safe_str(queued_trade.get("trade_id"), ""),
        "symbol": symbol,
        "strategy": strategy,
        "vehicle_selected": vehicle_selected,
        "requested_price": round(
            _safe_float(
                queued_trade.get("requested_price", queued_trade.get("price", fill_price)),
                fill_price,
            ),
            4,
        ),
        "fill_price": round(fill_price, 4),
        "filled_price": round(fill_price, 4),
        "filled_quantity": quantity,
        "quantity": quantity,
        "commission": commission,
        "shares": quantity if vehicle_selected == "STOCK" else 0,
        "contracts": quantity if vehicle_selected == "OPTION" else 0,
        "status": "FILLED",
        "opened_at": opened_at,
    }

    return {
        "status": "FILLED",
        "fill_price": round(fill_price, 4),
        "filled_quantity": quantity,
        "actual_cost": actual_cost,
        "broker_order_id": f"SIM-{symbol}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}",
        "reason": "executed",
        "reason_code": "executed",
        "execution_record": execution_record,
    }


def execute_via_adapter(
    *,
    queued_trade: Dict[str, Any],
    portfolio_context: Dict[str, Any] | None = None,
    max_open_positions: int = 5,
    current_open_positions: int = 0,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
    broker_adapter: Any = None,
) -> Dict[str, Any]:
    queued_trade = deepcopy(_safe_dict(queued_trade))
    portfolio_context = _safe_dict(portfolio_context)

    trading_mode = normalize_mode(
        queued_trade.get("trading_mode")
        or queued_trade.get("execution_mode")
        or queued_trade.get("mode")
        or "paper"
    )
    mode_context = _resolve_mode_context(trading_mode, queued_trade.get("mode_context"))

    capital_available = _safe_float(
        queued_trade.get(
            "capital_available",
            portfolio_context.get("cash_available", portfolio_context.get("cash", 0.0)),
        ),
        0.0,
    )

    guard = validate_selected_trade_for_execution(
        queued_trade,
        capital_available=capital_available,
        trading_mode=trading_mode,
        current_open_positions=current_open_positions,
        max_open_positions=max_open_positions,
        kill_switch_enabled=kill_switch_enabled,
        session_healthy=session_healthy,
        broker_healthy=True,
    )

    lifecycle_after = deepcopy(_safe_dict(queued_trade.get("lifecycle")))
    lifecycle_after.update({
        "trade_id": _safe_str(queued_trade.get("trade_id"), ""),
        "symbol": _norm_symbol(queued_trade.get("symbol")),
        "strategy": _safe_str(queued_trade.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "selected_vehicle": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "vehicle": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "trading_mode": trading_mode,
        "execution_mode": trading_mode,
        "mode": trading_mode,
        "mode_context": mode_context,
        "capital_available": round(capital_available, 4),
    })

    if _safe_bool(guard.get("blocked"), False):
        reason = _safe_str(guard.get("reason"), "Execution blocked.")
        reason_code = _safe_str(guard.get("reason_code"), "execution_blocked")

        lifecycle_after["execution_ready"] = False
        lifecycle_after["selected_for_execution"] = False
        lifecycle_after["lifecycle_stage"] = "EXECUTION_BLOCKED"
        lifecycle_after["final_decision"] = "REJECT"
        lifecycle_after["final_reason"] = reason
        lifecycle_after["final_reason_code"] = reason_code
        lifecycle_after["execution_reason"] = reason
        lifecycle_after["execution_reason_code"] = reason_code
        lifecycle_after["blocked_at"] = "execution_handoff"

        return {
            "success": False,
            "status": "REJECTED",
            "symbol": _norm_symbol(queued_trade.get("symbol")),
            "selected_vehicle": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
            "guard": {
                "decision": "REJECT",
                "guard_reason": reason,
                "guard_reason_code": reason_code,
                "warnings": _safe_list(guard.get("warnings")),
                "guard_details": _safe_dict(guard.get("details")),
            },
            "execution_result": {},
            "lifecycle_after": lifecycle_after,
            "trading_mode": trading_mode,
            "mode_context": mode_context,
        }

    if callable(getattr(broker_adapter, "execute_trade", None)):
        adapter_response = broker_adapter.execute_trade(queued_trade)
        execution_result = _safe_dict(adapter_response)
    else:
        execution_result = _simulate_fill(queued_trade)

    fill_price = _safe_float(execution_result.get("fill_price"), 0.0)
    if fill_price <= 0:
        reason = "Execution returned invalid fill price."
        reason_code = "invalid_fill_price"

        lifecycle_after["execution_ready"] = False
        lifecycle_after["selected_for_execution"] = False
        lifecycle_after["lifecycle_stage"] = "EXECUTION_BLOCKED"
        lifecycle_after["final_decision"] = "REJECT"
        lifecycle_after["final_reason"] = reason
        lifecycle_after["final_reason_code"] = reason_code
        lifecycle_after["execution_reason"] = reason
        lifecycle_after["execution_reason_code"] = reason_code
        lifecycle_after["blocked_at"] = "execution_handoff"

        return {
            "success": False,
            "status": "REJECTED",
            "symbol": _norm_symbol(queued_trade.get("symbol")),
            "selected_vehicle": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
            "guard": {
                "decision": "REJECT",
                "guard_reason": reason,
                "guard_reason_code": reason_code,
                "warnings": _safe_list(guard.get("warnings")),
                "guard_details": _safe_dict(guard.get("details")),
            },
            "execution_result": execution_result,
            "lifecycle_after": lifecycle_after,
            "trading_mode": trading_mode,
            "mode_context": mode_context,
        }

    execution_record = _safe_dict(execution_result.get("execution_record"))

    lifecycle_after["execution_ready"] = True
    lifecycle_after["selected_for_execution"] = True
    lifecycle_after["lifecycle_stage"] = "ENTERED"
    lifecycle_after["final_decision"] = "APPROVE"
    lifecycle_after["final_reason"] = "Position entered."
    lifecycle_after["final_reason_code"] = "entered"
    lifecycle_after["execution_reason"] = "Position entered."
    lifecycle_after["execution_reason_code"] = "entered"
    lifecycle_after["fill_price"] = round(fill_price, 4)
    lifecycle_after["entered_at"] = _safe_str(
        execution_record.get("opened_at"),
        _now_iso(),
    )
    lifecycle_after["blocked_at"] = ""
    lifecycle_after["execution_result"] = execution_result

    return {
        "success": True,
        "status": "EXECUTED",
        "symbol": _norm_symbol(queued_trade.get("symbol")),
        "selected_vehicle": _safe_str(queued_trade.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "guard": {
            "decision": "APPROVE",
            "guard_reason": "Execution completed successfully.",
            "guard_reason_code": "executed",
            "warnings": _safe_list(guard.get("warnings")),
            "guard_details": _safe_dict(guard.get("details")),
        },
        "execution_result": execution_result,
        "lifecycle_after": lifecycle_after,
        "trading_mode": trading_mode,
        "mode_context": mode_context,
    }


def summarize_execution_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(packet)
    guard = _safe_dict(packet.get("guard"))
    execution_result = _safe_dict(packet.get("execution_result"))
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))

    return {
        "success": _safe_bool(packet.get("success"), False),
        "status": _safe_str(packet.get("status"), ""),
        "symbol": _norm_symbol(packet.get("symbol")),
        "selected_vehicle": _safe_str(packet.get("selected_vehicle"), "RESEARCH_ONLY").upper(),
        "guard_reason": _safe_str(guard.get("guard_reason"), ""),
        "guard_reason_code": _safe_str(guard.get("guard_reason_code"), ""),
        "guard_warnings": _safe_list(guard.get("warnings")),
        "fill_price": round(_safe_float(execution_result.get("fill_price"), 0.0), 4),
        "filled_quantity": _safe_int(execution_result.get("filled_quantity"), 0),
        "actual_cost": round(_safe_float(execution_result.get("actual_cost"), 0.0), 4),
        "trade_id": _safe_str(lifecycle_after.get("trade_id"), ""),
        "lifecycle_stage_after": _safe_str(lifecycle_after.get("lifecycle_stage"), ""),
        "trading_mode": _safe_str(packet.get("trading_mode"), ""),
    }


__all__ = [
    "build_queued_trade_payload",
    "execute_via_adapter",
    "summarize_execution_packet",
]
