from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from engine.execution_handoff import execute_via_adapter, summarize_execution_packet
from engine.paper_portfolio import add_position, open_count


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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


def _now_iso() -> str:
    return datetime.now().isoformat()


def _load_json(path: str, default: Any) -> Any:
    try:
        p = Path(path)
        if not p.exists():
            return default
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: str, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _extract_trade_id(packet: Dict[str, Any]) -> str:
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))
    return _safe_str(
        lifecycle_after.get("trade_id")
        or execution_record.get("trade_id")
        or packet.get("trade_id"),
        "",
    )


def _append_trade_log(packet: Dict[str, Any], position: Dict[str, Any]) -> None:
    trade_log = _load_json("data/trade_log.json", [])
    if not isinstance(trade_log, list):
        trade_log = []

    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    trade_log.append({
        "timestamp": _safe_str(position.get("opened_at"), _now_iso()),
        "trade_id": _safe_str(position.get("trade_id"), ""),
        "symbol": _norm_symbol(position.get("symbol")),
        "strategy": _safe_str(position.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(position.get("vehicle_selected"), "RESEARCH_ONLY").upper(),
        "action": "OPEN",
        "status": "FILLED",
        "fill_price": round(_safe_float(position.get("fill_price", 0.0), 0.0), 4),
        "entry": round(_safe_float(position.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(position.get("current_price", 0.0), 0.0), 4),
        "underlying_price": round(_safe_float(position.get("underlying_price", 0.0), 0.0), 4),
        "option_current_price": round(_safe_float(position.get("option_current_price", 0.0), 0.0), 4),
        "quantity": _safe_int(position.get("size", 0), 0),
        "shares": _safe_int(position.get("shares", 0), 0),
        "contracts": _safe_int(position.get("contracts", 0), 0),
        "commission": round(_safe_float(position.get("commission", 0.0), 0.0), 4),
        "actual_cost": round(_safe_float(execution_result.get("actual_cost", 0.0), 0.0), 4),
        "broker_order_id": _safe_str(execution_result.get("broker_order_id"), ""),
        "trading_mode": _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper"),
        "reason": _safe_str(lifecycle_after.get("final_reason", execution_result.get("reason", "entered")), "entered"),
        "reason_code": _safe_str(lifecycle_after.get("final_reason_code", execution_result.get("reason_code", "entered")), "entered"),
        "monitoring_price_type": _safe_str(position.get("monitoring_price_type"), ""),
        "execution_record": execution_record,
    })

    _write_json("data/trade_log.json", trade_log)


def _persist_executed_trade(packet: Dict[str, Any]) -> Dict[str, Any]:
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    trading_mode = _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper")
    mode_context = _safe_dict(packet.get("mode_context", lifecycle_after.get("mode_context")))

    position = add_position(
        lifecycle_after,
        allow_replace=False,
        lifecycle=lifecycle_after,
        execution_result=execution_result,
        mode=trading_mode,
        mode_context=mode_context,
    )

    _append_trade_log(packet, position)

    return {
        "persisted": True,
        "position": position,
        "persisted_via_module": True,
    }


def execute_trades(
    queue: List[Dict[str, Any]] | None,
    limit: int = 3,
    portfolio_context: Dict[str, Any] | None = None,
    broker_adapter: Any = None,
    trading_mode: str | None = None,
    max_open_positions: int = 5,
    current_open_positions: int | None = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
) -> Dict[str, Any]:
    queue = queue if isinstance(queue, list) else []
    portfolio_context = _safe_dict(portfolio_context)

    results: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []

    executed = 0
    rejected = 0
    skipped = 0

    open_positions_running = (
        _safe_int(current_open_positions, open_count())
        if current_open_positions is not None
        else _safe_int(open_count(), 0)
    )

    remaining_slots = max(0, _safe_int(max_open_positions, 0) - open_positions_running)
    effective_limit = min(max(0, _safe_int(limit, 0)), remaining_slots)

    for queued_trade in queue:
        if executed >= effective_limit:
            break

        queued_trade = deepcopy(_safe_dict(queued_trade))
        if not queued_trade:
            skipped += 1
            continue

        resolved_mode = _safe_str(
            trading_mode
            or queued_trade.get("trading_mode")
            or queued_trade.get("execution_mode")
            or queued_trade.get("mode"),
            "paper",
        )

        print("PRE-EXECUTION-HANDOFF:", {
            "symbol": queued_trade.get("symbol"),
            "trade_id": queued_trade.get("trade_id"),
            "research_approved": queued_trade.get("research_approved"),
            "execution_ready": queued_trade.get("execution_ready"),
            "selected_for_execution": queued_trade.get("selected_for_execution"),
            "vehicle_selected": queued_trade.get("vehicle_selected"),
            "lifecycle_stage": queued_trade.get("lifecycle_stage"),
            "trading_mode": resolved_mode,
        })

        packet = execute_via_adapter(
            queued_trade=queued_trade,
            portfolio_context=portfolio_context,
            max_open_positions=max_open_positions,
            current_open_positions=open_positions_running,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_adapter=broker_adapter,
        )

        packet = _safe_dict(packet)
        packet["trade_id"] = _extract_trade_id(packet) or _safe_str(queued_trade.get("trade_id"), "")
        packet["trading_mode"] = _safe_str(packet.get("trading_mode", resolved_mode), resolved_mode)

        if _safe_bool(packet.get("success"), False):
            persistence = _persist_executed_trade(packet)
            packet["persistence"] = persistence
            open_positions_running += 1
            executed += 1
        else:
            rejected += 1

        summaries.append(summarize_execution_packet(packet))
        results.append(packet)

    print("EXECUTION LOOP SUMMARY:", {
        "queue_size": len(queue),
        "processed": len(results),
        "executed": executed,
        "rejected": rejected,
        "skipped": skipped,
        "open_positions_after": open_positions_running,
        "remaining_slots_before_execution": remaining_slots,
        "effective_limit": effective_limit,
    })

    return {
        "results": results,
        "summaries": summaries,
        "executed": executed,
        "rejected": rejected,
        "skipped": skipped,
        "processed": len(results),
        "queue_size": len(queue),
        "open_positions_after": open_positions_running,
        "timestamp": _now_iso(),
    }


__all__ = [
    "execute_trades",
]
