from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.account_state import record_trade
from engine.bot_logger import log_bot as default_log_bot
from engine.canonical_execution_guard import validate_selected_trade_for_execution
from engine.canonical_trade_state import build_open_trade_state
from engine.execution_handoff import execute_via_adapter, summarize_execution_packet
from engine.observatory_mode import build_mode_context, normalize_mode
from engine.paper_portfolio import add_position, get_position
from engine.trade_logger import log_trade_open_from_position
from engine.trade_summary import trade_summary
from engine.trade_timeline import add_timeline_event

try:
    from engine.premium_feed import write_premium_feed_item
except Exception:
    def write_premium_feed_item(_payload):
        return None


def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _write_skip_feed(trade: Dict[str, Any], summary: str) -> None:
    if not isinstance(trade, dict):
        return
    symbol = _norm_symbol(trade.get("symbol"))
    mode = _safe_str(trade.get("mode"), "UNKNOWN")
    write_premium_feed_item(
        {
            "title": f"{symbol} Skipped",
            "summary": summary,
            "pro_lines": [],
            "elite_lines": [],
            "timestamp": trade.get("timestamp"),
            "mode": mode,
            "symbol": symbol,
            "status": "SKIPPED",
            "final_reason": summary,
        }
    )


def _resolve_trade_mode(trade: Dict[str, Any]) -> str:
    trade = _safe_dict(trade)
    return normalize_mode(
        trade.get("trading_mode")
        or trade.get("execution_mode")
        or trade.get("mode")
        or _safe_dict(trade.get("mode_context")).get("mode")
        or "paper"
    )


def _build_trade_mode_context(trade_mode: str, trade: Dict[str, Any]) -> Dict[str, Any]:
    resolved = build_mode_context(trade_mode)
    incoming = _safe_dict(_safe_dict(trade).get("mode_context"))
    merged = dict(resolved)
    for key, value in incoming.items():
        if value is not None:
            merged[key] = value
    merged["mode"] = normalize_mode(merged.get("mode", trade_mode))
    return merged


def _position_already_present(
    open_positions: List[Dict[str, Any]],
    trade_id: str,
    symbol: str,
) -> bool:
    trade_id = _safe_str(trade_id, "")
    symbol = _norm_symbol(symbol)

    for pos in _safe_list(open_positions):
        pos = _safe_dict(pos)
        if trade_id and _safe_str(pos.get("trade_id"), "") == trade_id:
            return True
        if not trade_id and symbol and _norm_symbol(pos.get("symbol")) == symbol:
            if _safe_str(pos.get("status"), "").upper() == "OPEN":
                return True
    return False


def _append_result(
    results: List[Dict[str, Any]],
    *,
    success: bool,
    status: str,
    symbol: str,
    selected_vehicle: str,
    guard: Optional[Dict[str, Any]],
    execution_result: Optional[Dict[str, Any]],
    lifecycle_after: Optional[Dict[str, Any]],
    trade_mode: str,
    mode_context: Dict[str, Any],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "success": bool(success),
        "status": _safe_str(status, "UNKNOWN").upper(),
        "symbol": _norm_symbol(symbol),
        "selected_vehicle": _safe_str(selected_vehicle, "UNKNOWN").upper(),
        "guard": _safe_dict(guard),
        "execution_result": _safe_dict(execution_result),
        "lifecycle_after": _safe_dict(lifecycle_after),
        "trading_mode": normalize_mode(trade_mode),
        "mode_context": _safe_dict(mode_context),
        "timestamp": _now_iso(),
    }
    if isinstance(extra, dict):
        payload.update(extra)
    results.append(payload)
    return payload


def _build_stored_position(
    trade: Dict[str, Any],
    lifecycle_after: Dict[str, Any],
    execution_result: Dict[str, Any],
    trade_mode: str,
    mode_context: Dict[str, Any],
) -> Dict[str, Any]:
    position = build_open_trade_state(
        trade,
        lifecycle=lifecycle_after,
        execution_result=execution_result,
        mode=trade_mode,
        mode_context=mode_context,
    )

    position["trading_mode"] = trade_mode
    position["execution_mode"] = trade_mode
    position["mode"] = trade_mode
    position["mode_context"] = mode_context
    position["status"] = "OPEN"
    position["research_approved"] = True
    position["execution_ready"] = True
    position["selected_for_execution"] = True
    position["execution_result"] = _safe_dict(execution_result)
    position["execution_status"] = _safe_str(
        _safe_dict(execution_result).get("status"),
        "FILLED",
    ).upper()

    return position


def execute_trades(
    queue,
    limit=3,
    portfolio_context=None,
    max_open_positions=5,
    open_positions=None,
    kill_switch_enabled=False,
    session_healthy=True,
    broker_adapter=None,
    log_bot=None,
):
    queue = queue if isinstance(queue, list) else []
    portfolio_context = portfolio_context if isinstance(portfolio_context, dict) else {}
    open_positions = open_positions if isinstance(open_positions, list) else []

    executed = 0
    results: List[Dict[str, Any]] = []
    remaining_queue: List[Dict[str, Any]] = []

    def _log(message: str, level: str = "INFO") -> None:
        logger = log_bot if callable(log_bot) else default_log_bot
        try:
            logger(message, level)
        except Exception:
            pass

    for trade in queue:
        if executed >= limit:
            if isinstance(trade, dict):
                remaining_queue.append(trade)
            continue

        if not isinstance(trade, dict):
            _log("Skipped malformed queued trade payload.", "WARN")
            continue

        trade = deepcopy(_safe_dict(trade))
        trade_mode = _resolve_trade_mode(trade)
        mode_context = _build_trade_mode_context(trade_mode, trade)

        symbol = _norm_symbol(trade.get("symbol"))
        strategy = _safe_str(trade.get("strategy"), "CALL").upper()
        selected_vehicle = _safe_str(
            trade.get("vehicle_selected", trade.get("selected_vehicle", "STOCK")),
            "STOCK",
        ).upper()

        queue_limit = _safe_int(mode_context.get("queue_limit", limit), limit)
        if queue_limit > 0 and executed >= queue_limit:
            remaining_queue.append(trade)
            continue

        print("PRE-EXECUTION-HANDOFF:", {
            "symbol": symbol,
            "trade_id": _safe_str(trade.get("trade_id"), ""),
            "research_approved": _safe_bool(trade.get("research_approved"), False),
            "execution_ready": _safe_bool(trade.get("execution_ready"), False),
            "selected_for_execution": _safe_bool(trade.get("selected_for_execution"), False),
            "vehicle_selected": selected_vehicle,
            "lifecycle_stage": trade.get("lifecycle_stage"),
            "trading_mode": trade_mode,
        })

        existing_position = get_position(symbol, trade_id=_safe_str(trade.get("trade_id"), ""))
        if existing_position:
            reason_text = "Existing open position."
            reason_code = "existing_open_position"
            _log(f"{symbol} rejected | {reason_code}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped because there is already an open position.")
            add_timeline_event(symbol, "SKIPPED", {"reason": reason_code, "trading_mode": trade_mode})
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard={
                    "decision": "REJECT",
                    "guard_reason": reason_text,
                    "guard_reason_code": reason_code,
                    "warnings": [],
                    "guard_details": {},
                },
                execution_result=None,
                lifecycle_after=trade,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        local_guard = validate_selected_trade_for_execution(
            trade,
            capital_available=_safe_float(
                trade.get(
                    "capital_available",
                    portfolio_context.get("cash_available", portfolio_context.get("cash", 0.0)),
                ),
                0.0,
            ),
            trading_mode=trade_mode,
            current_open_positions=len(open_positions),
            max_open_positions=max_open_positions,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_healthy=True,
        )

        if _safe_bool(local_guard.get("blocked"), False):
            reason_text = _safe_str(local_guard.get("reason"), "Execution blocked.")
            reason_code = _safe_str(local_guard.get("reason_code"), "execution_blocked")
            _log(f"{symbol} rejected | {reason_code}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped: {reason_text}")
            add_timeline_event(symbol, "SKIPPED", {"reason": reason_code, "trading_mode": trade_mode})
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard={
                    "decision": "REJECT",
                    "guard_reason": reason_text,
                    "guard_reason_code": reason_code,
                    "warnings": _safe_list(local_guard.get("warnings")),
                    "guard_details": _safe_dict(local_guard.get("details")),
                },
                execution_result=None,
                lifecycle_after=trade,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        packet_raw = execute_via_adapter(
            queued_trade=trade,
            portfolio_context=portfolio_context,
            max_open_positions=max_open_positions,
            current_open_positions=len(open_positions),
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_adapter=broker_adapter,
        )

        summary = _safe_dict(summarize_execution_packet(_safe_dict(packet_raw)))
        lifecycle_after = _safe_dict(packet_raw.get("lifecycle_after"))
        execution_result = _safe_dict(packet_raw.get("execution_result"))
        guard = _safe_dict(packet_raw.get("guard"))

        print("QUEUE EXECUTION PACKET:", {
            "symbol": packet_raw.get("symbol") or symbol,
            "success": packet_raw.get("success"),
            "status": packet_raw.get("status"),
            "selected_vehicle": packet_raw.get("selected_vehicle") or selected_vehicle,
            "guard_decision": guard.get("decision"),
            "guard_reason": guard.get("guard_reason"),
            "lifecycle_stage_after": lifecycle_after.get("lifecycle_stage"),
            "trade_id_after": lifecycle_after.get("trade_id"),
            "fill_price": execution_result.get("fill_price"),
            "filled_quantity": execution_result.get("filled_quantity"),
        })

        if not _safe_bool(packet_raw.get("success"), False):
            reason_text = _safe_str(
                guard.get("guard_reason"),
                summary.get("guard_reason", "Execution rejected."),
            )
            reason_code = _safe_str(
                guard.get("guard_reason_code"),
                summary.get("guard_reason_code", "execution_rejected"),
            )
            _log(f"{symbol} rejected | {reason_code}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped: {reason_text}")
            add_timeline_event(symbol, "SKIPPED", {"reason": reason_code, "trading_mode": trade_mode})
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard=guard,
                execution_result=execution_result,
                lifecycle_after=lifecycle_after,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        try:
            position_payload = _build_stored_position(
                trade=trade,
                lifecycle_after=lifecycle_after,
                execution_result=execution_result,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            stored_position = add_position(position_payload)
            stored_position = _safe_dict(stored_position) or position_payload
        except Exception as e:
            _log(f"{symbol} execution succeeded but add_position failed: {e}", "ERROR")
            _append_result(
                results,
                success=False,
                status="STORAGE_FAILED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard={
                    "decision": "REJECT",
                    "guard_reason": str(e),
                    "guard_reason_code": "storage_failed",
                    "warnings": [],
                    "guard_details": {},
                },
                execution_result=execution_result,
                lifecycle_after=lifecycle_after,
                trade_mode=trade_mode,
                mode_context=mode_context,
                extra={"storage_error": str(e)},
            )
            continue

        if not _position_already_present(
            open_positions,
            _safe_str(stored_position.get("trade_id"), ""),
            symbol,
        ):
            open_positions.append(stored_position)

        try:
            log_trade_open_from_position(stored_position)
        except Exception:
            pass

        fill_price = _safe_float(execution_result.get("fill_price"), 0.0)

        if selected_vehicle == "OPTION":
            quantity_for_account = _safe_int(stored_position.get("contracts", 1), 1)
        else:
            quantity_for_account = _safe_int(
                stored_position.get("shares", stored_position.get("size", 1)),
                1,
            )

        try:
            record_trade(symbol, fill_price, quantity_for_account)
        except Exception:
            pass

        add_timeline_event(
            symbol,
            "OPENED",
            {
                "trade_id": stored_position.get("trade_id"),
                "strategy": strategy,
                "vehicle_selected": stored_position.get("vehicle_selected"),
                "requested_price": round(_safe_float(stored_position.get("requested_price", 0.0), 0.0), 4),
                "fill_price": round(fill_price, 4),
                "shares": stored_position.get("shares", 0),
                "contracts": stored_position.get("contracts", 0),
                "size": stored_position.get("size", 0),
                "stop": round(_safe_float(stored_position.get("stop", 0.0), 0.0), 4),
                "target": round(_safe_float(stored_position.get("target", 0.0), 0.0), 4),
                "mode": stored_position.get("mode"),
                "trading_mode": trade_mode,
                "fused_score": stored_position.get("fused_score", stored_position.get("score")),
                "v2_score": stored_position.get("v2_score"),
                "final_reason": stored_position.get("final_reason"),
                "final_reason_code": stored_position.get("final_reason_code"),
            },
        )

        try:
            trade_summary(stored_position)
        except Exception:
            pass

        executed += 1

        _log(
            f"{symbol} executed successfully | mode={trade_mode} "
            f"vehicle={stored_position.get('vehicle_selected')} "
            f"shares={stored_position.get('shares', 0)} "
            f"contracts={stored_position.get('contracts', 0)} "
            f"fill={round(fill_price, 4)} "
            f"trade_id={stored_position.get('trade_id')}",
            "SUCCESS",
        )

        _append_result(
            results,
            success=True,
            status="EXECUTED",
            symbol=symbol,
            selected_vehicle=selected_vehicle,
            guard=guard,
            execution_result=execution_result,
            lifecycle_after=lifecycle_after,
            trade_mode=trade_mode,
            mode_context=mode_context,
            extra={
                "stored_position": stored_position,
                "fill_price": fill_price,
                "trade_id": stored_position.get("trade_id"),
            },
        )

    return {
        "executed_count": executed,
        "results": results,
        "remaining_queue": remaining_queue,
        "open_positions": open_positions,
    }
