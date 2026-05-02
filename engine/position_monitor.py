from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from engine.paper_portfolio import show_positions, replace_position
from engine.close_trade import close_position


OPTION_CONTRACT_MULTIPLIER = 100


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


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _vehicle(pos: Dict[str, Any]) -> str:
    value = _safe_str(
        pos.get("vehicle_selected", pos.get("selected_vehicle", pos.get("vehicle", "STOCK"))),
        "STOCK",
    ).upper()
    if value not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        return "STOCK"
    return value


def _direction(strategy: str) -> str:
    return "SHORT" if "PUT" in _safe_str(strategy, "CALL").upper() else "LONG"


def _days_open(opened_at: Any) -> float:
    try:
        dt = datetime.fromisoformat(str(opened_at))
        return max((datetime.now() - dt).total_seconds() / 86400.0, 0.0)
    except Exception:
        return 0.0


def _latest_option_price(pos: Dict[str, Any]) -> float:
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    for value in [
        pos.get("option_current_price"),
        pos.get("current_option_price"),
        option.get("mark"),
        option.get("last"),
        contract.get("mark"),
        contract.get("last"),
        pos.get("mark"),
        pos.get("last"),
        pos.get("current_price"),
        pos.get("entry"),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4)
    return 0.0


def _latest_stock_price(pos: Dict[str, Any]) -> float:
    for value in [
        pos.get("current_price"),
        pos.get("underlying_price"),
        pos.get("price"),
        pos.get("entry"),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4)
    return 0.0


def _ensure_monitor_defaults(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = dict(pos)
    vehicle = _vehicle(pos)
    strategy = _safe_str(pos.get("strategy"), "CALL").upper()
    direction = _direction(strategy)

    if vehicle == "OPTION":
        entry = _safe_float(pos.get("entry", pos.get("option_entry", 0.0)), 0.0)
        current = _latest_option_price(pos)
        if current <= 0:
            current = entry
        stop = _safe_float(pos.get("stop", 0.0), 0.0)
        target = _safe_float(pos.get("target", 0.0), 0.0)
        if stop <= 0:
            stop = round(entry * (1.35 if direction == "SHORT" else 0.70), 4)
        if target <= 0:
            target = round(entry * (0.65 if direction == "SHORT" else 1.35), 4)

        pos["entry"] = round(entry, 4)
        pos["current_price"] = round(current, 4)
        pos["option_current_price"] = round(current, 4)
        pos["stop"] = round(stop, 4)
        pos["target"] = round(target, 4)
        pos["monitoring_price_type"] = "OPTION_PREMIUM"
    else:
        entry = _safe_float(pos.get("entry", pos.get("price", 0.0)), 0.0)
        current = _latest_stock_price(pos)
        if current <= 0:
            current = entry
        stop = _safe_float(pos.get("stop", 0.0), 0.0)
        target = _safe_float(pos.get("target", 0.0), 0.0)
        if stop <= 0:
            stop = round(entry * (1.03 if direction == "SHORT" else 0.97), 4)
        if target <= 0:
            target = round(entry * (0.90 if direction == "SHORT" else 1.10), 4)

        pos["entry"] = round(entry, 4)
        pos["current_price"] = round(current, 4)
        pos["underlying_price"] = round(current, 4)
        pos["stop"] = round(stop, 4)
        pos["target"] = round(target, 4)
        pos["monitoring_price_type"] = "UNDERLYING"

    return pos


def _pct_change(entry: float, current: float, strategy: str, vehicle: str) -> float:
    if entry <= 0 or current <= 0:
        return 0.0
    direction = _direction(strategy)
    if direction == "SHORT":
        base = ((entry - current) / entry) * 100.0
    else:
        base = ((current - entry) / entry) * 100.0
    return round(base, 4)


def _progress(entry: float, current: float, stop: float, target: float, strategy: str) -> float:
    direction = _direction(strategy)
    if entry <= 0:
        return 0.0
    try:
        if direction == "SHORT":
            denom = entry - target
            if denom == 0:
                return 0.0
            return round((entry - current) / denom, 4)
        denom = target - entry
        if denom == 0:
            return 0.0
        return round((current - entry) / denom, 4)
    except Exception:
        return 0.0


def _action_for_position(pos: Dict[str, Any]) -> str:
    vehicle = _vehicle(pos)
    strategy = _safe_str(pos.get("strategy"), "CALL").upper()
    direction = _direction(strategy)

    entry = _safe_float(pos.get("entry", 0.0), 0.0)
    current = _safe_float(pos.get("current_price", 0.0), 0.0)
    stop = _safe_float(pos.get("stop", 0.0), 0.0)
    target = _safe_float(pos.get("target", 0.0), 0.0)
    days_open = _days_open(pos.get("opened_at"))
    pct = _pct_change(entry, current, strategy, vehicle)

    if entry <= 0 or current <= 0:
        return "HOLD"

    if direction == "SHORT":
        stop_hit = current >= stop if stop > 0 else False
        target_hit = current <= target if target > 0 else False
    else:
        stop_hit = current <= stop if stop > 0 else False
        target_hit = current >= target if target > 0 else False

    if stop_hit:
        return "STOP_LOSS"
    if target_hit and days_open >= 0.01:
        return "TAKE_PROFIT"

    if vehicle == "OPTION":
        if pct <= -35:
            return "CUT_WEAKNESS"
        if pct >= 45 and days_open >= 0.01:
            return "PROTECT_PROFIT"
    else:
        if pct <= -1.5:
            return "CUT_WEAKNESS"
        if pct >= 3.0 and days_open >= 0.01:
            return "PROTECT_PROFIT"

    return "HOLD"


def monitor_open_positions() -> List[Dict[str, Any]]:
    try:
        positions = show_positions()
    except Exception:
        positions = []

    actions: List[Dict[str, Any]] = []

    for raw_pos in positions if isinstance(positions, list) else []:
        if not isinstance(raw_pos, dict):
            continue

        pos = _ensure_monitor_defaults(raw_pos)
        symbol = _norm_symbol(pos.get("symbol"))
        trade_id = _safe_str(pos.get("trade_id"), "")
        vehicle = _vehicle(pos)

        entry = _safe_float(pos.get("entry", 0.0), 0.0)
        current = _safe_float(pos.get("current_price", 0.0), 0.0)
        stop = _safe_float(pos.get("stop", 0.0), 0.0)
        target = _safe_float(pos.get("target", 0.0), 0.0)

        action = _action_for_position(pos)

        pos["monitor_debug"] = {
            "vehicle_selected": vehicle,
            "monitoring_price_type": pos.get("monitoring_price_type", ""),
            "entry": round(entry, 4),
            "current": round(current, 4),
            "stop": round(stop, 4),
            "target": round(target, 4),
            "days_open": round(_days_open(pos.get("opened_at")), 4),
            "final_action": action,
        }

        replace_position(symbol, pos)

        print(
            f"{symbol} | Vehicle: {vehicle} | MonitorPrice: {pos.get('monitoring_price_type', '')} | "
            f"Current: {round(current, 4)} | Entry: {round(entry, 4)} | Stop: {round(stop, 4)} | "
            f"Action: {action}"
        )

        if action != "HOLD":
            result = close_position(
                symbol,
                current,
                reason=action.lower(),
                trade_id=trade_id,
            )
            actions.append(
                {
                    "symbol": symbol,
                    "trade_id": trade_id,
                    "reason": action.lower(),
                    "result": result,
                }
            )
            if isinstance(result, dict) and result.get("closed"):
                print(f"CLOSED: {symbol} | Reason: {action} | PnL: {result.get('pnl')}")
            elif isinstance(result, dict) and result.get("blocked"):
                print(f"BLOCKED CLOSE: {symbol} | Reason: {result.get('reason')}")

    return actions
