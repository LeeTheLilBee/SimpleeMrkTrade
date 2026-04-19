from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

OPEN_FILE = "data/open_positions.json"
POSITIONS_FILE = "data/positions.json"
CANONICAL_LEDGER_FILE = "data/canonical_ledger.json"


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


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _ensure_parent(path_str: str) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(default)


def _write_json(path_str: str, payload: Any) -> None:
    _ensure_parent(path_str)
    with open(path_str, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _load_open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_canonical_ledger() -> List[Dict[str, Any]]:
    rows = _read_json(CANONICAL_LEDGER_FILE, [])
    return rows if isinstance(rows, list) else []


def _best_price(trade: Dict[str, Any]) -> float:
    candidates = [
        trade.get("current_price"),
        trade.get("price"),
        trade.get("entry"),
        trade.get("fill_price"),
        trade.get("requested_price"),
        trade.get("underlying_price"),
        trade.get("market_price"),
        trade.get("latest_price"),
    ]
    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return price
    return 0.0


def _vehicle_shape(vehicle: str) -> Dict[str, int]:
    vehicle = _safe_str(vehicle, "RESEARCH_ONLY").upper()
    if vehicle == "OPTION":
        return {"shares": 0, "contracts": 1}
    if vehicle == "STOCK":
        return {"shares": 1, "contracts": 0}
    return {"shares": 0, "contracts": 0}


def _normalize_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    trade = _safe_dict(deepcopy(trade))

    symbol = _norm_symbol(trade.get("symbol"))
    strategy = _safe_str(trade.get("strategy"), "CALL").upper()

    timestamp = _safe_str(trade.get("timestamp"), _now_iso())
    opened_at = _safe_str(trade.get("opened_at"), timestamp)

    price = round(_best_price(trade), 4)
    entry = round(_safe_float(trade.get("entry", price), price), 4)
    current_price = round(_safe_float(trade.get("current_price", price), price), 4)

    stop_default = round(entry * (1.03 if strategy == "PUT" else 0.97), 4) if entry > 0 else 0.0
    target_default = round(entry * (0.90 if strategy == "PUT" else 1.10), 4) if entry > 0 else 0.0
    stop = round(_safe_float(trade.get("stop", stop_default), stop_default), 4)
    target = round(_safe_float(trade.get("target", target_default), target_default), 4)

    vehicle_selected = _safe_str(
        trade.get("vehicle_selected", trade.get("vehicle", "STOCK")),
        "STOCK",
    ).upper()

    if vehicle_selected not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        vehicle_selected = "STOCK"

    shape = _vehicle_shape(vehicle_selected)

    shares = _safe_int(
        trade.get("shares", trade.get("size", shape["shares"])),
        shape["shares"],
    )
    contracts = _safe_int(trade.get("contracts", shape["contracts"]), shape["contracts"])

    if vehicle_selected == "OPTION":
        shares = 0
        contracts = max(1, contracts or 1)
    elif vehicle_selected == "STOCK":
        shares = max(1, shares or 1)
        contracts = 0
    else:
        shares = 0
        contracts = 0

    status = _safe_str(trade.get("status"), "OPEN").upper()

    trade_id = _safe_str(trade.get("trade_id"), "")
    if not trade_id:
        trade_id = f"{symbol}-{strategy}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}"

    option_obj = _safe_dict(trade.get("option"))
    option_path = _safe_dict(trade.get("option_path"))
    stock_path = _safe_dict(trade.get("stock_path"))
    governor = _safe_dict(trade.get("governor"))
    canonical_decision = _safe_dict(trade.get("canonical_decision"))
    final_decision = _safe_dict(trade.get("final_decision"))
    execution_result = _safe_dict(trade.get("execution_result"))
    mode_context = _safe_dict(trade.get("mode_context"))
    v2_payload = _safe_dict(trade.get("v2_payload"))

    normalized = dict(trade)

    normalized["symbol"] = symbol
    normalized["strategy"] = strategy
    normalized["trade_id"] = trade_id
    normalized["timestamp"] = timestamp
    normalized["opened_at"] = opened_at
    normalized["status"] = status

    normalized["price"] = price
    normalized["entry"] = entry
    normalized["current_price"] = current_price
    normalized["stop"] = stop
    normalized["target"] = target

    normalized["vehicle_selected"] = vehicle_selected
    normalized["vehicle"] = vehicle_selected
    normalized["shares"] = shares
    normalized["contracts"] = contracts
    normalized["size"] = shares if vehicle_selected == "STOCK" else contracts

    normalized["company_name"] = _safe_str(
        trade.get("company_name", trade.get("company", symbol)),
        symbol,
    )
    normalized["sector"] = _safe_str(trade.get("sector"), "UNKNOWN")

    normalized["score"] = round(_safe_float(trade.get("score"), 0.0), 4)
    normalized["base_score"] = round(_safe_float(trade.get("base_score"), normalized["score"]), 4)
    normalized["v2_score"] = round(_safe_float(trade.get("v2_score"), 0.0), 4)
    normalized["fused_score"] = round(
        _safe_float(trade.get("fused_score", normalized["score"]), normalized["score"]),
        4,
    )

    normalized["confidence"] = _safe_str(trade.get("confidence"), "LOW").upper()
    normalized["base_confidence"] = _safe_str(
        trade.get("base_confidence", normalized["confidence"]),
        normalized["confidence"],
    ).upper()
    normalized["v2_confidence"] = _safe_str(
        trade.get("v2_confidence", normalized["confidence"]),
        normalized["confidence"],
    ).upper()

    normalized["v2_reason"] = _safe_str(trade.get("v2_reason"), "")
    normalized["v2_vehicle_bias"] = _safe_str(trade.get("v2_vehicle_bias"), "").upper()
    normalized["v2_quality"] = round(_safe_float(trade.get("v2_quality"), 0.0), 4)
    normalized["v2_payload"] = v2_payload

    normalized["decision_reason"] = _safe_str(trade.get("decision_reason"), "")
    normalized["final_reason"] = _safe_str(trade.get("final_reason"), "")
    normalized["vehicle_reason"] = _safe_str(trade.get("vehicle_reason"), "")
    normalized["blocked_at"] = _safe_str(trade.get("blocked_at"), "")

    normalized["research_approved"] = _safe_bool(trade.get("research_approved"), False)
    normalized["execution_ready"] = _safe_bool(trade.get("execution_ready"), False)
    normalized["selected_for_execution"] = _safe_bool(trade.get("selected_for_execution"), False)

    normalized["capital_required"] = round(_safe_float(trade.get("capital_required"), 0.0), 4)
    normalized["minimum_trade_cost"] = round(_safe_float(trade.get("minimum_trade_cost"), 0.0), 4)
    normalized["capital_available"] = round(_safe_float(trade.get("capital_available"), 0.0), 4)

    normalized["atr"] = round(_safe_float(trade.get("atr"), 0.0), 4)
    normalized["rsi"] = round(_safe_float(trade.get("rsi"), 0.0), 4)

    normalized["setup_type"] = _safe_str(trade.get("setup_type"), "")
    normalized["setup_family"] = _safe_str(trade.get("setup_family"), "")
    normalized["entry_quality"] = _safe_str(trade.get("entry_quality"), "")
    normalized["trend"] = _safe_str(trade.get("trend"), "")
    normalized["mode"] = _safe_str(trade.get("mode"), "")
    normalized["regime"] = _safe_str(trade.get("regime"), "")
    normalized["breadth"] = _safe_str(trade.get("breadth"), "")
    normalized["volatility_state"] = _safe_str(trade.get("volatility_state"), "")

    normalized["readiness_score"] = round(_safe_float(trade.get("readiness_score"), 0.0), 4)
    normalized["promotion_score"] = round(_safe_float(trade.get("promotion_score"), 0.0), 4)
    normalized["rebuild_pressure"] = round(_safe_float(trade.get("rebuild_pressure"), 0.0), 4)
    normalized["execution_quality"] = round(_safe_float(trade.get("execution_quality"), 0.0), 4)

    normalized["readiness_notes"] = _safe_list(trade.get("readiness_notes"))
    normalized["promotion_notes"] = _safe_list(trade.get("promotion_notes"))
    normalized["rebuild_notes"] = _safe_list(trade.get("rebuild_notes"))
    normalized["learning_notes"] = _safe_list(trade.get("learning_notes"))
    normalized["learning_exit_notes"] = _safe_list(trade.get("learning_exit_notes"))

    normalized["option"] = option_obj
    normalized["option_contract_score"] = round(_safe_float(trade.get("option_contract_score"), 0.0), 4)
    normalized["option_explanation"] = _safe_list(trade.get("option_explanation"))
    normalized["option_path"] = option_path
    normalized["stock_path"] = stock_path

    normalized["governor"] = governor
    normalized["governor_blocked"] = _safe_bool(trade.get("governor_blocked"), False)
    normalized["governor_status"] = _safe_str(trade.get("governor_status"), "")
    normalized["governor_reasons"] = _safe_list(trade.get("governor_reasons"))
    normalized["governor_warnings"] = _safe_list(trade.get("governor_warnings"))
    normalized["mode_context"] = mode_context

    normalized["canonical_decision"] = canonical_decision
    normalized["final_decision"] = final_decision
    normalized["execution_result"] = execution_result

    normalized["why"] = _safe_list(trade.get("why"))
    normalized["supports"] = _safe_list(trade.get("supports"))
    normalized["blockers"] = _safe_list(trade.get("blockers"))
    normalized["rejection_analysis"] = _safe_list(trade.get("rejection_analysis"))
    normalized["stronger_competing_setups"] = _safe_list(trade.get("stronger_competing_setups"))

    normalized["position_explanation"] = _safe_dict(trade.get("position_explanation"))
    normalized["soulaana"] = _safe_dict(trade.get("soulaana"))
    normalized["monitor_debug"] = _safe_dict(trade.get("monitor_debug"))
    normalized["capital_protection_mode"] = _safe_bool(trade.get("capital_protection_mode"), False)
    normalized["capital_protection_snapshot"] = _safe_dict(trade.get("capital_protection_snapshot"))

    return normalized


def _append_ledger_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    ledger = _load_canonical_ledger()
    event = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "symbol": _norm_symbol(payload.get("symbol")),
        "trade_id": _safe_str(payload.get("trade_id"), ""),
        "payload": deepcopy(_safe_dict(payload)),
    }
    ledger.append(event)
    _write_json(CANONICAL_LEDGER_FILE, ledger)
    return event


def _sync_positions_mirror(open_positions: Optional[List[Dict[str, Any]]] = None) -> None:
    if open_positions is None:
        open_positions = _load_open_positions()
    _write_json(POSITIONS_FILE, open_positions)


def _find_open_index(
    open_positions: List[Dict[str, Any]],
    *,
    symbol: str,
    trade_id: str = "",
    opened_at: str = "",
) -> int:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    opened_at = _safe_str(opened_at, "")

    for idx, pos in enumerate(open_positions):
        pos_symbol = _norm_symbol(pos.get("symbol"))
        pos_trade_id = _safe_str(pos.get("trade_id"), "")
        pos_opened_at = _safe_str(pos.get("opened_at"), "")

        if trade_id and pos_trade_id == trade_id:
            return idx
        if symbol and opened_at and pos_symbol == symbol and pos_opened_at == opened_at:
            return idx
        if symbol and not trade_id and not opened_at and pos_symbol == symbol:
            return idx

    return -1


def clear_open_positions() -> None:
    _write_json(OPEN_FILE, [])
    _sync_positions_mirror([])
    _append_ledger_event(
        "OPEN_CLEAR",
        {"symbol": "", "trade_id": "", "note": "All open positions cleared."},
    )


def open_count() -> int:
    return len(_load_open_positions())


def show_positions() -> List[Dict[str, Any]]:
    return _load_open_positions()


def get_position(symbol: str, trade_id: str = "") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    for pos in _load_open_positions():
        if trade_id and _safe_str(pos.get("trade_id"), "") == trade_id:
            return pos
        if symbol and _norm_symbol(pos.get("symbol")) == symbol:
            return pos
    return None


def add_position(trade: Dict[str, Any], allow_replace: bool = False) -> Dict[str, Any]:
    normalized = _normalize_trade(trade)
    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=normalized.get("symbol", ""),
        trade_id=normalized.get("trade_id", ""),
        opened_at=normalized.get("opened_at", ""),
    )

    if idx >= 0:
        if not allow_replace:
            raise ValueError(
                f"Open position already exists for {normalized.get('symbol')} "
                f"({normalized.get('trade_id')})."
            )
        open_positions[idx] = normalized
        event_type = "POSITION_REPLACED_ON_ADD"
    else:
        open_positions.append(normalized)
        event_type = "POSITION_OPENED"

    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)
    _append_ledger_event(event_type, normalized)
    return normalized


def replace_position(symbol: str, updated_position: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    updated = _normalize_trade(updated_position)
    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=symbol or updated.get("symbol", ""),
        trade_id=updated.get("trade_id", ""),
        opened_at=updated.get("opened_at", ""),
    )

    if idx < 0:
        return None

    prior = _safe_dict(open_positions[idx])
    merged = dict(prior)
    merged.update(updated)
    merged = _normalize_trade(merged)
    merged["symbol"] = _norm_symbol(merged.get("symbol", symbol))
    merged["status"] = "OPEN"

    open_positions[idx] = merged
    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)
    _append_ledger_event("POSITION_UPDATED", merged)
    return merged


def remove_position(symbol: str, trade_id: str = "", reason: str = "removed") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    removed = open_positions.pop(idx)
    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)

    payload = dict(removed)
    payload["remove_reason"] = _safe_str(reason, "removed")
    _append_ledger_event("POSITION_REMOVED", payload)
    return removed


def print_positions() -> None:
    positions = _load_open_positions()
    print("OPEN POSITIONS:")
    if not positions:
        print("No open positions.")
        return

    for pos in positions:
        print(
            pos.get("symbol"),
            pos.get("strategy"),
            pos.get("fused_score", pos.get("score")),
            "| vehicle:",
            pos.get("vehicle_selected"),
            "| entry:",
            pos.get("entry", pos.get("price")),
            "| stop:",
            pos.get("stop"),
            "| target:",
            pos.get("target"),
            "| trade_id:",
            pos.get("trade_id"),
            "| opened_at:",
            pos.get("opened_at"),
        )
