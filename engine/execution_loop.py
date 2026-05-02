from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from engine.execution_handoff import (
    execute_via_adapter,
    summarize_execution_packet,
)

try:
    from engine.paper_portfolio import open_count
except Exception:
    def open_count():
        positions = _load_json("data/user_positions.json", [])
        if isinstance(positions, list):
            return len([p for p in positions if isinstance(p, dict)])
        return 0


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


def _build_position_record(packet: Dict[str, Any]) -> Dict[str, Any]:
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    raw = _safe_dict(lifecycle_after.get("raw"))
    option = _safe_dict(lifecycle_after.get("option")) or _safe_dict(raw.get("option"))
    contract = _safe_dict(lifecycle_after.get("contract")) or _safe_dict(raw.get("contract"))
    mode_context = _safe_dict(packet.get("mode_context")) or _safe_dict(lifecycle_after.get("mode_context"))

    symbol = _norm_symbol(lifecycle_after.get("symbol") or raw.get("symbol"))
    strategy = _safe_str(lifecycle_after.get("strategy") or raw.get("strategy"), "CALL").upper()
    vehicle_selected = _safe_str(
        lifecycle_after.get("vehicle_selected")
        or lifecycle_after.get("selected_vehicle")
        or raw.get("vehicle_selected")
        or raw.get("selected_vehicle")
        or raw.get("vehicle"),
        "RESEARCH_ONLY",
    ).upper()

    fill_price = round(
        _safe_float(
            execution_result.get("fill_price", execution_record.get("fill_price", 0.0)),
            0.0,
        ),
        4,
    )

    contracts = _safe_int(
        execution_record.get("contracts", lifecycle_after.get("contracts", raw.get("contracts", 0))),
        0,
    )
    shares = _safe_int(
        execution_record.get("shares", lifecycle_after.get("shares", raw.get("shares", raw.get("size", 0)))),
        0,
    )

    if vehicle_selected == "OPTION":
        quantity = contracts if contracts > 0 else max(1, _safe_int(execution_record.get("filled_quantity", 1), 1))
    else:
        quantity = shares if shares > 0 else max(1, _safe_int(execution_record.get("filled_quantity", 1), 1))

    capital_committed = round(
        _safe_float(execution_result.get("actual_cost", lifecycle_after.get("capital_required", 0.0)), 0.0),
        4,
    )

    position = {
        "trade_id": _extract_trade_id(packet),
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": vehicle_selected,
        "vehicle_selected": vehicle_selected,
        "selected_vehicle": vehicle_selected,
        "status": "OPEN",
        "opened_at": _safe_str(execution_record.get("opened_at"), _now_iso()),
        "entry": fill_price,
        "fill_price": fill_price,
        "price": fill_price,
        "current": fill_price,
        "current_price": fill_price,
        "requested_price": round(
            _safe_float(execution_record.get("requested_price", fill_price), fill_price),
            4,
        ),
        "commission": round(_safe_float(execution_record.get("commission", 0.0), 0.0), 4),
        "capital_committed": capital_committed,
        "capital_required": round(_safe_float(lifecycle_after.get("capital_required", 0.0), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(lifecycle_after.get("minimum_trade_cost", 0.0), 0.0), 4),
        "capital_available_at_entry": round(_safe_float(lifecycle_after.get("capital_available", 0.0), 0.0), 4),
        "contracts": contracts if vehicle_selected == "OPTION" else 0,
        "shares": shares if vehicle_selected == "STOCK" else 0,
        "quantity": quantity,
        "score": _safe_float(lifecycle_after.get("score", raw.get("score", 0.0)), 0.0),
        "fused_score": _safe_float(lifecycle_after.get("fused_score", raw.get("fused_score", 0.0)), 0.0),
        "confidence": _safe_str(lifecycle_after.get("confidence", raw.get("confidence", "LOW")), "LOW").upper(),
        "mode": _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper"),
        "trading_mode": _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper"),
        "mode_context": mode_context,
        "final_reason": _safe_str(lifecycle_after.get("final_reason", "entered"), "entered"),
        "final_reason_code": _safe_str(lifecycle_after.get("final_reason_code", "entered"), "entered"),
        "execution_reason": _safe_str(lifecycle_after.get("execution_reason", "entered"), "entered"),
        "execution_reason_code": _safe_str(lifecycle_after.get("execution_reason_code", "entered"), "entered"),
        "broker_order_id": _safe_str(execution_result.get("broker_order_id"), ""),
        "actual_cost": capital_committed,
        "pnl": 0.0,
        "unrealized_pnl": 0.0,
        "realized_pnl": 0.0,
        "stop": _safe_float(
            lifecycle_after.get("stop", raw.get("stop", 0.0)),
            0.0,
        ),
        "target": _safe_float(
            lifecycle_after.get("target", raw.get("target", 0.0)),
            0.0,
        ),
    }

    if option or contract:
        option_payload = option or contract
        position.update({
            "option": option_payload,
            "contract": contract or option_payload,
            "contract_symbol": _safe_str(
                option_payload.get("contract_symbol")
                or option_payload.get("contractSymbol"),
                "",
            ),
            "expiry": _safe_str(
                option_payload.get("expiry")
                or option_payload.get("expiration"),
                "",
            ),
            "strike": _safe_float(option_payload.get("strike"), 0.0),
            "right": _safe_str(option_payload.get("right"), strategy),
            "bid": _safe_float(option_payload.get("bid"), 0.0),
            "ask": _safe_float(option_payload.get("ask"), 0.0),
            "mark": _safe_float(
                option_payload.get("mark", option_payload.get("last", option_payload.get("price", fill_price))),
                fill_price,
            ),
            "last": _safe_float(option_payload.get("last", fill_price), fill_price),
            "open_interest": _safe_int(
                option_payload.get("open_interest", option_payload.get("openInterest", 0)),
                0,
            ),
            "volume": _safe_int(option_payload.get("volume", 0), 0),
            "dte": _safe_int(
                option_payload.get("dte", option_payload.get("daysToExpiration", 0)),
                0,
            ),
            "contract_score": round(
                _safe_float(
                    lifecycle_after.get(
                        "option_contract_score",
                        option_payload.get("contract_score", 0.0),
                    ),
                    0.0,
                ),
                4,
            ),
        })

    return position


def _append_open_position(position: Dict[str, Any]) -> None:
    positions = _load_json("data/user_positions.json", [])
    if not isinstance(positions, list):
        positions = []

    trade_id = _safe_str(position.get("trade_id"), "")
    symbol = _norm_symbol(position.get("symbol"))

    deduped: List[Dict[str, Any]] = []
    for row in positions:
        row = _safe_dict(row)
        existing_trade_id = _safe_str(row.get("trade_id"), "")
        existing_symbol = _norm_symbol(row.get("symbol"))
        if trade_id and existing_trade_id == trade_id:
            continue
        if not trade_id and symbol and existing_symbol == symbol and _safe_str(row.get("status", "OPEN"), "OPEN").upper() == "OPEN":
            continue
        deduped.append(row)

    deduped.append(position)
    _write_json("data/user_positions.json", deduped)


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
        "quantity": _safe_int(position.get("quantity", 0), 0),
        "shares": _safe_int(position.get("shares", 0), 0),
        "contracts": _safe_int(position.get("contracts", 0), 0),
        "commission": round(_safe_float(position.get("commission", 0.0), 0.0), 4),
        "actual_cost": round(_safe_float(execution_result.get("actual_cost", 0.0), 0.0), 4),
        "broker_order_id": _safe_str(execution_result.get("broker_order_id"), ""),
        "trading_mode": _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper"),
        "reason": _safe_str(lifecycle_after.get("final_reason", execution_result.get("reason", "entered")), "entered"),
        "reason_code": _safe_str(lifecycle_after.get("final_reason_code", execution_result.get("reason_code", "entered")), "entered"),
        "execution_record": execution_record,
    })

    _write_json("data/trade_log.json", trade_log)


def _persist_via_module(position: Dict[str, Any]) -> bool:
    try:
        import engine.paper_portfolio as pp  # type: ignore
    except Exception:
        return False

    candidate_funcs = [
        "open_position",
        "open_trade",
        "add_position",
        "save_position",
        "append_position",
    ]

    for name in candidate_funcs:
        fn = getattr(pp, name, None)
        if callable(fn):
            try:
                fn(position)
                return True
            except TypeError:
                try:
                    fn(**position)
                    return True
                except Exception:
                    continue
            except Exception:
                continue
    return False


def _persist_executed_trade(packet: Dict[str, Any]) -> Dict[str, Any]:
    position = _build_position_record(packet)

    persisted_via_module = _persist_via_module(position)
    if not persisted_via_module:
        _append_open_position(position)

    _append_trade_log(packet, position)

    return {
        "persisted": True,
        "position": position,
        "persisted_via_module": persisted_via_module,
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

    for queued_trade in queue:
        if executed >= max(0, limit):
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
