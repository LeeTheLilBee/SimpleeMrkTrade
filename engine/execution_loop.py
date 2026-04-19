from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.account_state import buying_power, record_trade
from engine.bot_logger import log_bot as default_log_bot
from engine.paper_portfolio import add_position, get_position
from engine.trade_logger import log_trade_open
from engine.trade_summary import trade_summary
from engine.trade_timeline import add_timeline_event

try:
    from engine.premium_feed import write_premium_feed_item
except Exception:
    def write_premium_feed_item(_payload):
        return None


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _safe_mode(trade: Dict[str, Any]) -> str:
    return _safe_str((trade or {}).get("mode"), "UNKNOWN")


def _write_skip_feed(trade: Dict[str, Any], summary: str) -> None:
    if not isinstance(trade, dict):
        return
    symbol = _norm_symbol(trade.get("symbol"))
    mode = _safe_mode(trade)
    write_premium_feed_item(
        {
            "title": f"{symbol} Skipped",
            "summary": summary,
            "pro_lines": [],
            "elite_lines": [],
            "timestamp": trade.get("timestamp"),
            "mode": mode,
        }
    )


def _merge_execution_into_position(
    queued_trade: Dict[str, Any],
    lifecycle_after: Dict[str, Any],
    execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(deepcopy(queued_trade))
    lifecycle_after = _safe_dict(deepcopy(lifecycle_after))
    execution_result = _safe_dict(deepcopy(execution_result))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    merged: Dict[str, Any] = {}
    merged.update(queued_trade)
    merged.update(lifecycle_after)

    symbol = _norm_symbol(
        merged.get("symbol")
        or execution_record.get("symbol")
        or queued_trade.get("symbol")
    )
    strategy = _safe_str(
        merged.get("strategy")
        or execution_record.get("strategy")
        or queued_trade.get("strategy"),
        "CALL",
    ).upper()

    trade_id = _safe_str(
        merged.get("trade_id")
        or execution_record.get("trade_id")
        or queued_trade.get("trade_id"),
        "",
    )

    selected_vehicle = _safe_str(
        merged.get("vehicle_selected", merged.get("vehicle", "STOCK")),
        "STOCK",
    ).upper()
    if selected_vehicle not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        selected_vehicle = "STOCK"

    fill_price = _safe_float(
        execution_record.get("fill_price", execution_record.get("filled_price", merged.get("fill_price", merged.get("entry", merged.get("price", 0.0))))),
        _safe_float(merged.get("entry", merged.get("price", 0.0)), 0.0),
    )

    requested_price = _safe_float(
        execution_record.get("requested_price", merged.get("requested_price", merged.get("price", 0.0))),
        _safe_float(merged.get("price", 0.0), 0.0),
    )

    opened_at = _safe_str(
        merged.get("opened_at", execution_record.get("opened_at", datetime.now().isoformat())),
        datetime.now().isoformat(),
    )

    shares = _safe_int(
        execution_record.get("shares", merged.get("shares", merged.get("size", 0))),
        _safe_int(merged.get("shares", 0), 0),
    )
    contracts = _safe_int(
        execution_record.get("contracts", merged.get("contracts", 0)),
        _safe_int(merged.get("contracts", 0), 0),
    )

    filled_quantity = _safe_int(
        execution_record.get("filled_quantity", execution_record.get("quantity", 0)),
        0,
    )

    if selected_vehicle == "OPTION":
        contracts = max(1, contracts or filled_quantity or 1)
        shares = 0
        size = contracts
    elif selected_vehicle == "STOCK":
        shares = max(1, shares or filled_quantity or 1)
        contracts = 0
        size = shares
    else:
        shares = 0
        contracts = 0
        size = 0

    merged["symbol"] = symbol
    merged["strategy"] = strategy
    merged["trade_id"] = trade_id or f"{symbol}-{strategy}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}"

    merged["vehicle_selected"] = selected_vehicle
    merged["vehicle"] = selected_vehicle
    merged["shares"] = shares
    merged["contracts"] = contracts
    merged["size"] = size

    merged["requested_price"] = round(requested_price, 4)
    merged["fill_price"] = round(fill_price, 4)
    merged["price"] = round(_safe_float(merged.get("price", fill_price), fill_price), 4)
    merged["entry"] = round(_safe_float(merged.get("entry", fill_price), fill_price), 4)
    merged["current_price"] = round(_safe_float(merged.get("current_price", fill_price), fill_price), 4)

    merged["stop"] = round(_safe_float(merged.get("stop"), 0.0), 4)
    merged["target"] = round(_safe_float(merged.get("target"), 0.0), 4)

    merged["commission"] = round(
        _safe_float(execution_record.get("commission", merged.get("commission", 0.0)), 0.0),
        4,
    )
    merged["opened_at"] = opened_at
    merged["timestamp"] = _safe_str(merged.get("timestamp"), opened_at)
    merged["status"] = "OPEN"

    merged["execution_result"] = execution_result
    merged["execution_status"] = _safe_str(
        execution_result.get("status", execution_record.get("status", "FILLED")),
        "FILLED",
    ).upper()

    merged["research_approved"] = bool(merged.get("research_approved", True))
    merged["execution_ready"] = bool(merged.get("execution_ready", True))
    merged["selected_for_execution"] = True
    merged["final_reason"] = _safe_str(merged.get("final_reason"), "executed")

    return merged


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
    from engine.execution_handoff import execute_via_adapter, summarize_execution_packet

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

        lifecycle = _safe_dict(trade.get("lifecycle"))
        symbol = _norm_symbol(trade.get("symbol") or lifecycle.get("symbol"))
        strategy = _safe_str(trade.get("strategy") or lifecycle.get("strategy"), "CALL").upper()
        selected_vehicle = _safe_str(
            trade.get("vehicle_selected", trade.get("vehicle", lifecycle.get("vehicle_selected", "STOCK"))),
            "STOCK",
        ).upper()

        if not lifecycle:
            _log(f"{symbol or 'UNKNOWN'} skipped: missing canonical lifecycle object.", "WARN")
            _write_skip_feed(trade, "Skipped because the queued trade was missing its lifecycle object.")
            results.append(
                {
                    "success": False,
                    "status": "REJECTED",
                    "symbol": symbol,
                    "selected_vehicle": selected_vehicle,
                    "guard": {
                        "decision": "REJECT",
                        "guard_reason": "Missing lifecycle object in queued trade.",
                        "guard_reason_code": "missing_lifecycle",
                    },
                    "execution_result": None,
                    "lifecycle_after": lifecycle,
                }
            )
            continue

        existing = get_position(symbol, trade_id=_safe_str(trade.get("trade_id"), ""))
        if existing:
            reason = "existing_open_position"
            _log(f"{symbol} rejected | {reason}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped because there is already an open position.")
            results.append(
                {
                    "success": False,
                    "status": "REJECTED",
                    "symbol": symbol,
                    "selected_vehicle": selected_vehicle,
                    "guard": {
                        "decision": "REJECT",
                        "guard_reason": "Existing open position.",
                        "guard_reason_code": reason,
                    },
                    "execution_result": None,
                    "lifecycle_after": lifecycle,
                }
            )
            add_timeline_event(symbol, "SKIPPED", {"reason": reason})
            continue

        current_open_positions = len(open_positions)

        packet = execute_via_adapter(
            queued_trade=trade,
            portfolio_context=portfolio_context,
            max_open_positions=max_open_positions,
            current_open_positions=current_open_positions,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_adapter=broker_adapter,
        )

        summary = summarize_execution_packet(packet)
        results.append(packet)

        if not packet.get("success"):
            reason = (
                _safe_str(summary.get("guard_reason"), "")
                or _safe_str(_safe_dict(packet.get("execution_result")).get("reason"), "")
                or "Execution rejected."
            )
            _log(f"{symbol or 'UNKNOWN'} rejected | {reason}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped: {reason}")
            add_timeline_event(symbol, "SKIPPED", {"reason": reason})
            continue

        lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
        execution_result = _safe_dict(packet.get("execution_result"))
        execution_record = _safe_dict(execution_result.get("execution_record"))

        position_payload = _merge_execution_into_position(
            queued_trade=trade,
            lifecycle_after=lifecycle_after,
            execution_result=execution_result,
        )

        try:
            stored_position = add_position(position_payload)
        except Exception as e:
            _log(f"{symbol} execution succeeded but add_position failed: {e}", "ERROR")
            results[-1]["success"] = False
            results[-1]["status"] = "STORAGE_FAILED"
            results[-1]["storage_error"] = str(e)
            continue

        fill_price = _safe_float(
            execution_record.get("fill_price", execution_record.get("filled_price", stored_position.get("entry", 0.0))),
            _safe_float(stored_position.get("entry", 0.0), 0.0),
        )
        commission = _safe_float(
            execution_record.get("commission", stored_position.get("commission", 0.0)),
            0.0,
        )

        if stored_position.get("vehicle_selected") == "OPTION":
            quantity_for_account = _safe_int(stored_position.get("contracts", 1), 1)
        else:
            quantity_for_account = _safe_int(stored_position.get("shares", stored_position.get("size", 1)), 1)

        try:
            record_trade(symbol, fill_price, quantity_for_account)
        except Exception:
            pass

        try:
            log_trade_open(
                symbol,
                strategy,
                fill_price,
                quantity_for_account,
                _safe_float(stored_position.get("fused_score", stored_position.get("score", 0.0)), 0.0),
                _safe_str(stored_position.get("confidence", "LOW"), "LOW"),
            )
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
                "commission": round(commission, 4),
                "shares": stored_position.get("shares", 0),
                "contracts": stored_position.get("contracts", 0),
                "size": stored_position.get("size", 0),
                "stop": round(_safe_float(stored_position.get("stop", 0.0), 0.0), 4),
                "target": round(_safe_float(stored_position.get("target", 0.0), 0.0), 4),
                "mode": stored_position.get("mode"),
                "fused_score": stored_position.get("fused_score", stored_position.get("score")),
                "v2_score": stored_position.get("v2_score"),
            },
        )

        try:
            trade_summary(stored_position)
        except Exception:
            pass

        open_positions.append(stored_position)
        executed += 1

        _log(
            f"{symbol} executed successfully | vehicle={stored_position.get('vehicle_selected')} "
            f"shares={stored_position.get('shares', 0)} contracts={stored_position.get('contracts', 0)} "
            f"fill={round(fill_price, 4)}",
            "SUCCESS",
        )

    return {
        "executed_count": executed,
        "results": results,
        "remaining_queue": remaining_queue,
        "open_positions": open_positions,
    }
