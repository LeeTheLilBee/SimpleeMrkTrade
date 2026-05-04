from __future__ import annotations

"""
🔭 Observatory Account State

Canonical paper-account rules:

1. Cash is spendable cash.
2. Buying power follows cash for this paper simulator.
3. Open market value is computed from open positions.
4. Equity / estimated account value is computed as:

       equity = cash + open_market_value

5. OPTION positions use option premium math only:

       option market value = current_premium * 100 * contracts
       option cost basis   = entry_premium * 100 * contracts

6. STOCK positions use stock/share math:

       stock market value = current_price * shares
       stock cost basis   = entry_price * shares

This file is compatibility-preserving:
- keeps load_state()
- keeps save_state()
- keeps buying_power()
- keeps record_trade()
- keeps release_trade_capital()
- keeps release_trade_cap()
- keeps reserve functions
- keeps daily counter functions
- keeps reset_account_state()

It also adds:
- get_account_snapshot()
- sync_account_from_portfolio()
- calculate_open_market_value()
- print_account_snapshot()
"""

import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


FILE = "data/account_state.json"
OPEN_POSITIONS_FILE = "data/open_positions.json"
CLOSED_POSITIONS_FILE = "data/closed_positions.json"

OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"
VEHICLE_UNKNOWN = "UNKNOWN"

DEFAULT_STATE = {
    "equity": 1000.0,
    "cash": 1000.0,
    "buying_power": 1000.0,
    "estimated_account_value": 1000.0,
    "open_market_value": 0.0,
    "open_cost_basis": 0.0,
    "open_unrealized_pnl": 0.0,
    "account_type": "margin",
    "trade_history": [],
    "activity_log": [],
    "reserve_mode": "percent",
    "reserve_value": 20.0,
    "last_account_sync": "",
    "account_math_basis": "cash_plus_open_market_value",
}


# =============================================================================
# Safe helpers
# =============================================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return None
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        if isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _now() -> datetime:
    return datetime.now()


def _now_iso() -> str:
    return _now().isoformat()


def _date_key(dt: Optional[datetime] = None) -> str:
    dt = dt or _now()
    return dt.strftime("%Y-%m-%d")


def _timestamp_to_date_key(value: Any) -> str:
    raw = _safe_str(value, "")
    if not raw:
        return ""
    try:
        return datetime.fromisoformat(raw).strftime("%Y-%m-%d")
    except Exception:
        return ""


def _round_money(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 2)


def _round_price(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 4)


def _ensure_parent_dir(path_str: str = FILE) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path_str: str, payload: Any) -> None:
    _ensure_parent_dir(path_str)
    tmp = Path(path_str).with_suffix(Path(path_str).suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    tmp.replace(path_str)


# =============================================================================
# Position math helpers
# =============================================================================

def _detect_vehicle(pos: Dict[str, Any]) -> str:
    pos = _safe_dict(pos)

    raw = _upper(
        pos.get(
            "vehicle_selected",
            pos.get(
                "selected_vehicle",
                pos.get("vehicle", pos.get("asset_type", pos.get("instrument_type", ""))),
            ),
        ),
        "",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION
    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK
    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    contract_symbol = _safe_str(
        pos.get(
            "contract_symbol",
            pos.get("option_symbol", pos.get("option_contract_symbol", "")),
        ),
        "",
    )

    if option or contract or contract_symbol:
        return VEHICLE_OPTION

    return VEHICLE_STOCK


def _first_positive_float(*values: Any, default: float = 0.0) -> float:
    for value in values:
        number = _safe_float(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _option_contracts(pos: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(
            pos.get(
                "contracts",
                pos.get("contract_count", pos.get("quantity", pos.get("qty", pos.get("size", 1)))),
            ),
            1,
        ),
    )


def _stock_shares(pos: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(
            pos.get("shares", pos.get("quantity", pos.get("qty", pos.get("size", 1)))),
            1,
        ),
    )


def _option_entry_premium(pos: Dict[str, Any]) -> float:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    value = _first_positive_float(
        pos.get("entry_premium"),
        pos.get("premium_entry"),
        pos.get("option_entry"),
        pos.get("option_entry_price"),
        pos.get("entry_option_mark"),
        pos.get("contract_entry_price"),
        pos.get("fill_premium"),
        pos.get("average_premium"),
        pos.get("avg_premium"),
        pos.get("debit"),
        pos.get("price_paid"),
        pos.get("entry"),
        pos.get("entry_price"),
        pos.get("fill_price"),
        pos.get("executed_price"),
        option.get("entry_premium"),
        option.get("premium_entry"),
        option.get("entry_price"),
        option.get("premium"),
        option.get("mark_at_entry"),
        option.get("fill_price"),
        option.get("executed_price"),
        option.get("selected_price_reference"),
        option.get("price_reference"),
        option.get("mark"),
        contract.get("entry_premium"),
        contract.get("premium_entry"),
        contract.get("entry_price"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
        contract.get("mark"),
        default=0.0,
    )
    return _round_price(value)


def _option_current_premium(pos: Dict[str, Any]) -> float:
    pos = _safe_dict(pos)
    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))

    value = _first_positive_float(
        pos.get("current_premium"),
        pos.get("premium_current"),
        pos.get("current_option_mark"),
        pos.get("option_current_mark"),
        pos.get("option_current_price"),
        pos.get("current_option_price"),
        pos.get("option_mark"),
        pos.get("contract_mark"),
        pos.get("mark"),
        option.get("current_premium"),
        option.get("premium_current"),
        option.get("current_option_mark"),
        option.get("option_current_mark"),
        option.get("option_current_price"),
        option.get("current_option_price"),
        option.get("mark"),
        option.get("selected_price_reference"),
        option.get("price_reference"),
        option.get("last"),
        contract.get("current_premium"),
        contract.get("premium_current"),
        contract.get("current_option_mark"),
        contract.get("option_current_mark"),
        contract.get("option_current_price"),
        contract.get("current_option_price"),
        contract.get("mark"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
        contract.get("last"),
        default=0.0,
    )

    if value <= 0:
        value = _option_entry_premium(pos)

    return _round_price(value)


def _stock_entry_price(pos: Dict[str, Any]) -> float:
    value = _first_positive_float(
        pos.get("entry"),
        pos.get("entry_price"),
        pos.get("avg_entry"),
        pos.get("average_entry"),
        pos.get("fill_price"),
        pos.get("price"),
        default=0.0,
    )
    return _round_price(value)


def _stock_current_price(pos: Dict[str, Any]) -> float:
    value = _first_positive_float(
        pos.get("current_price"),
        pos.get("current_underlying_price"),
        pos.get("underlying_price"),
        pos.get("market_price"),
        pos.get("stock_price"),
        pos.get("price"),
        pos.get("entry"),
        pos.get("entry_price"),
        default=0.0,
    )
    return _round_price(value)


def _position_market_values(pos: Dict[str, Any]) -> Dict[str, Any]:
    pos = _safe_dict(pos)
    vehicle = _detect_vehicle(pos)

    symbol = _upper(pos.get("symbol"), "UNKNOWN")
    trade_id = _safe_str(pos.get("trade_id"), "")

    if vehicle == VEHICLE_OPTION:
        contracts = _option_contracts(pos)
        entry_premium = _option_entry_premium(pos)
        current_premium = _option_current_premium(pos)

        cost_basis = round(entry_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
        market_value = round(current_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
        unrealized = round(market_value - cost_basis, 2)

        return {
            "symbol": symbol,
            "trade_id": trade_id,
            "vehicle": VEHICLE_OPTION,
            "contracts": contracts,
            "shares": 0,
            "entry_price": entry_premium,
            "current_price": current_premium,
            "entry_premium": entry_premium,
            "current_premium": current_premium,
            "cost_basis": cost_basis,
            "market_value": market_value,
            "unrealized_pnl": unrealized,
            "pnl_basis": "option_premium_x_100_x_contracts",
            "underlying_used_for_pnl": False,
        }

    if vehicle == VEHICLE_STOCK:
        shares = _stock_shares(pos)
        entry_price = _stock_entry_price(pos)
        current_price = _stock_current_price(pos)

        cost_basis = round(entry_price * shares, 2)
        market_value = round(current_price * shares, 2)
        unrealized = round(market_value - cost_basis, 2)

        return {
            "symbol": symbol,
            "trade_id": trade_id,
            "vehicle": VEHICLE_STOCK,
            "contracts": 0,
            "shares": shares,
            "entry_price": entry_price,
            "current_price": current_price,
            "entry_premium": 0.0,
            "current_premium": 0.0,
            "cost_basis": cost_basis,
            "market_value": market_value,
            "unrealized_pnl": unrealized,
            "pnl_basis": "stock_price_x_shares",
            "underlying_used_for_pnl": True,
        }

    return {
        "symbol": symbol,
        "trade_id": trade_id,
        "vehicle": vehicle,
        "contracts": 0,
        "shares": 0,
        "entry_price": 0.0,
        "current_price": 0.0,
        "entry_premium": 0.0,
        "current_premium": 0.0,
        "cost_basis": 0.0,
        "market_value": 0.0,
        "unrealized_pnl": 0.0,
        "pnl_basis": "research_only_no_market_value",
        "underlying_used_for_pnl": False,
    }


def _load_open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_POSITIONS_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_closed_positions() -> List[Dict[str, Any]]:
    rows = _read_json(CLOSED_POSITIONS_FILE, [])
    return rows if isinstance(rows, list) else []


def calculate_open_market_value() -> Dict[str, Any]:
    open_positions = _load_open_positions()

    total_market_value = 0.0
    total_cost_basis = 0.0
    total_unrealized = 0.0

    vehicle_mix = {
        VEHICLE_OPTION: 0,
        VEHICLE_STOCK: 0,
        VEHICLE_RESEARCH_ONLY: 0,
        VEHICLE_UNKNOWN: 0,
    }

    positions: List[Dict[str, Any]] = []
    option_positions = 0
    underlying_used_for_option_pnl = False

    for raw_pos in open_positions:
        if not isinstance(raw_pos, dict):
            continue

        row = _position_market_values(raw_pos)
        vehicle = row.get("vehicle", VEHICLE_UNKNOWN)
        if vehicle not in vehicle_mix:
            vehicle = VEHICLE_UNKNOWN

        vehicle_mix[vehicle] += 1

        if vehicle == VEHICLE_OPTION:
            option_positions += 1
            if bool(row.get("underlying_used_for_pnl")):
                underlying_used_for_option_pnl = True

        total_market_value += _safe_float(row.get("market_value"), 0.0)
        total_cost_basis += _safe_float(row.get("cost_basis"), 0.0)
        total_unrealized += _safe_float(row.get("unrealized_pnl"), 0.0)
        positions.append(row)

    return {
        "open_positions": len(open_positions),
        "total_market_value": round(total_market_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_unrealized": round(total_unrealized, 2),
        "positions": positions,
        "vehicle_mix": vehicle_mix,
        "option_safety": {
            "option_positions": option_positions,
            "underlying_used_for_option_pnl": bool(underlying_used_for_option_pnl),
            "basis": "OPTION positions use premium math only.",
        },
    }


def _realized_pnl_from_closed_positions() -> float:
    total = 0.0
    for row in _load_closed_positions():
        if not isinstance(row, dict):
            continue
        total += _safe_float(row.get("pnl"), 0.0)
    return round(total, 2)


# =============================================================================
# State normalization and sync
# =============================================================================

def _normalize_state(data: Any) -> Dict[str, Any]:
    state = dict(DEFAULT_STATE)
    if isinstance(data, dict):
        state.update(data)

    state["cash"] = _round_money(state.get("cash", DEFAULT_STATE["cash"]), DEFAULT_STATE["cash"])
    state["buying_power"] = _round_money(state.get("buying_power", state["cash"]), state["cash"])
    state["equity"] = _round_money(state.get("equity", DEFAULT_STATE["equity"]), DEFAULT_STATE["equity"])
    state["estimated_account_value"] = _round_money(
        state.get("estimated_account_value", state["equity"]),
        state["equity"],
    )

    state["open_market_value"] = _round_money(state.get("open_market_value", 0.0), 0.0)
    state["open_cost_basis"] = _round_money(state.get("open_cost_basis", 0.0), 0.0)
    state["open_unrealized_pnl"] = _round_money(state.get("open_unrealized_pnl", 0.0), 0.0)

    account_type = _safe_str(state.get("account_type", "margin"), "margin").lower()
    if account_type not in {"cash", "margin"}:
        account_type = "margin"
    state["account_type"] = account_type

    reserve_mode = _safe_str(state.get("reserve_mode", "percent"), "percent").lower()
    if reserve_mode not in {"percent", "amount"}:
        reserve_mode = "percent"
    state["reserve_mode"] = reserve_mode

    reserve_value = _safe_float(state.get("reserve_value", 20.0), 20.0)
    if reserve_mode == "percent":
        reserve_value = max(0.0, min(reserve_value, 100.0))
    else:
        reserve_value = max(0.0, reserve_value)
    state["reserve_value"] = reserve_value

    state["trade_history"] = _safe_list(state.get("trade_history"))
    state["activity_log"] = _safe_list(state.get("activity_log"))

    state["last_account_sync"] = _safe_str(state.get("last_account_sync"), "")
    state["account_math_basis"] = _safe_str(
        state.get("account_math_basis"),
        "cash_plus_open_market_value",
    )

    return state


def _sync_state_with_open_positions(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _normalize_state(state)
    open_math = calculate_open_market_value()

    cash = _round_money(state.get("cash", 0.0), 0.0)
    open_market_value = _round_money(open_math.get("total_market_value", 0.0), 0.0)
    open_cost_basis = _round_money(open_math.get("total_cost_basis", 0.0), 0.0)
    open_unrealized = _round_money(open_math.get("total_unrealized", 0.0), 0.0)

    estimated_account_value = round(cash + open_market_value, 2)

    state["cash"] = cash
    state["buying_power"] = cash
    state["open_market_value"] = open_market_value
    state["open_cost_basis"] = open_cost_basis
    state["open_unrealized_pnl"] = open_unrealized
    state["equity"] = estimated_account_value
    state["estimated_account_value"] = estimated_account_value
    state["open_positions"] = _safe_int(open_math.get("open_positions"), 0)
    state["vehicle_mix"] = open_math.get("vehicle_mix", {})
    state["option_safety"] = open_math.get("option_safety", {})
    state["last_account_sync"] = _now_iso()
    state["account_math_basis"] = "cash_plus_open_market_value"

    return state


def load_state(sync: bool = True) -> Dict[str, Any]:
    if not Path(FILE).exists():
        save_state(DEFAULT_STATE, sync=False)
        state = dict(DEFAULT_STATE)
    else:
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            raw = dict(DEFAULT_STATE)

        state = _normalize_state(raw)

    if sync:
        synced = _sync_state_with_open_positions(state)
        if synced != state:
            save_state(synced, sync=False)
        return synced

    return state


def save_state(state: Dict[str, Any], sync: bool = True) -> None:
    _ensure_parent_dir(FILE)
    normalized = _normalize_state(state)
    if sync:
        normalized = _sync_state_with_open_positions(normalized)
    _write_json(FILE, normalized)


def sync_account_from_portfolio() -> Dict[str, Any]:
    state = load_state(sync=False)
    synced = _sync_state_with_open_positions(state)
    save_state(synced, sync=False)
    return synced


# =============================================================================
# Reserve policy
# =============================================================================

def resolve_min_cash_reserve(
    state: Optional[Dict[str, Any]] = None,
    fallback_amount: float = 100.0,
) -> float:
    state = load_state() if state is None else _normalize_state(state)

    reserve_mode = _safe_str(state.get("reserve_mode", "percent"), "percent").lower()
    reserve_value = _safe_float(state.get("reserve_value", fallback_amount), fallback_amount)
    equity = _safe_float(state.get("equity", 0.0), 0.0)

    if reserve_mode == "percent":
        reserve_value = max(0.0, min(reserve_value, 100.0))
        return round(equity * (reserve_value / 100.0), 2)

    return round(max(0.0, reserve_value), 2)


def set_reserve_policy(mode: str = "percent", value: float = 20.0) -> Dict[str, Any]:
    state = load_state()

    mode = _safe_str(mode, "percent").lower()
    if mode not in {"percent", "amount"}:
        mode = "percent"

    value = _safe_float(value, 20.0)
    if mode == "percent":
        value = max(0.0, min(value, 100.0))
    else:
        value = max(0.0, value)

    state["reserve_mode"] = mode
    state["reserve_value"] = value
    save_state(state)

    synced = load_state()
    return {
        "reserve_mode": synced["reserve_mode"],
        "reserve_value": synced["reserve_value"],
        "effective_min_cash_reserve": resolve_min_cash_reserve(synced),
    }


def get_reserve_policy() -> Dict[str, Any]:
    state = load_state()
    return {
        "reserve_mode": state.get("reserve_mode", "percent"),
        "reserve_value": state.get("reserve_value", 20.0),
        "effective_min_cash_reserve": resolve_min_cash_reserve(state),
    }


# =============================================================================
# Activity events and trading cash movements
# =============================================================================

def _append_activity_event(
    state: Dict[str, Any],
    *,
    event_type: str,
    symbol: str = "",
    trade_id: str = "",
    price: float = 0.0,
    size: float = 0.0,
    cost: float = 0.0,
    pnl: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    ts = _safe_str(timestamp, _now_iso())
    event = {
        "event_type": _safe_str(event_type, "").upper(),
        "symbol": _safe_str(symbol, "").upper(),
        "trade_id": _safe_str(trade_id, ""),
        "timestamp": ts,
        "date_key": _timestamp_to_date_key(ts) or _date_key(),
        "price": _round_price(price),
        "size": _round_price(size),
        "cost": _round_money(cost),
        "pnl": _round_money(pnl),
        "metadata": metadata if isinstance(metadata, dict) else {},
    }
    state.setdefault("activity_log", [])
    state["activity_log"].append(event)
    return event


def _capital_cost(price: float, size: float, vehicle: str = "") -> float:
    vehicle = _upper(vehicle, "")

    price = _safe_float(price, 0.0)
    size = _safe_float(size, 0.0)

    if vehicle == VEHICLE_OPTION:
        return round(price * OPTION_CONTRACT_MULTIPLIER * size, 2)

    return round(price * size, 2)


def record_trade(
    symbol: str,
    price: float,
    size: float,
    trade_id: str = "",
    action: str = "OPEN",
    timestamp: Optional[str] = None,
    vehicle: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state = load_state(sync=False)

    symbol = _safe_str(symbol, "UNKNOWN").upper()
    price = _safe_float(price, 0.0)
    size = _safe_float(size, 0.0)
    vehicle = _upper(vehicle, "")

    metadata = _safe_dict(metadata)
    if not vehicle:
        vehicle = _upper(metadata.get("vehicle_selected", metadata.get("vehicle", "")), "")

    cost = _capital_cost(price, size, vehicle=vehicle)

    ts = _safe_str(timestamp, _now_iso())
    action = _safe_str(action, "OPEN").upper()
    if action not in {"OPEN", "ENTRY"}:
        action = "OPEN"

    trade = {
        "trade_id": _safe_str(trade_id, ""),
        "symbol": symbol,
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "price": _round_price(price),
        "size": _round_price(size),
        "timestamp": ts,
        "date_key": _timestamp_to_date_key(ts) or _date_key(),
        "settle_date": (_now() + timedelta(days=1)).isoformat(),
        "cost": cost,
        "status": "OPEN",
        "action": action,
        "metadata": metadata,
    }

    state.setdefault("trade_history", [])
    state["trade_history"].append(trade)

    _append_activity_event(
        state,
        event_type="ENTRY",
        symbol=symbol,
        trade_id=trade.get("trade_id", ""),
        price=price,
        size=size,
        cost=cost,
        timestamp=ts,
        metadata={
            "source": "record_trade",
            "vehicle": vehicle,
            "capital_cost_rule": "option_premium_x_100_x_contracts" if vehicle == VEHICLE_OPTION else "price_x_size",
            **metadata,
        },
    )

    state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) - cost, 2)
    state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)

    save_state(state)
    return trade


def settle_cash() -> Dict[str, Any]:
    state = load_state(sync=False)
    now = _now()

    unsettled = []
    settled_value = 0.0

    for trade in _safe_list(state.get("trade_history")):
        trade = _safe_dict(trade)
        settle_date_raw = trade.get("settle_date")
        try:
            settle_date = datetime.fromisoformat(_safe_str(settle_date_raw, ""))
        except Exception:
            unsettled.append(trade)
            continue

        if settle_date <= now and trade.get("status") == "SETTLED_CREDIT":
            settled_value += _safe_float(trade.get("credit_amount", 0.0), 0.0)
        else:
            unsettled.append(trade)

    state["trade_history"] = unsettled
    state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) + settled_value, 2)
    state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)

    save_state(state)
    return load_state()


def buying_power() -> float:
    return _safe_float(load_state().get("buying_power", 0.0), 0.0)


def apply_realized_pnl(pnl: float) -> Dict[str, Any]:
    """
    Compatibility function.

    Use this only when no principal is being returned.
    For normal closes, release_trade_capital() is preferred because it returns
    principal plus pnl.
    """
    state = load_state(sync=False)
    pnl = _safe_float(pnl, 0.0)

    state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) + pnl, 2)
    state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)

    _append_activity_event(
        state,
        event_type="REALIZED_PNL",
        pnl=pnl,
        metadata={"source": "apply_realized_pnl"},
    )

    save_state(state)
    return load_state()


def release_trade_capital(
    entry_price: float,
    size: float,
    pnl: float = 0.0,
    immediate: bool = True,
    symbol: str = "",
    trade_id: str = "",
    timestamp: Optional[str] = None,
    vehicle: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state = load_state(sync=False)

    entry_price = _safe_float(entry_price, 0.0)
    size = _safe_float(size, 0.0)
    pnl = _safe_float(pnl, 0.0)
    vehicle = _upper(vehicle, "")
    metadata = _safe_dict(metadata)

    if not vehicle:
        vehicle = _upper(metadata.get("vehicle_selected", metadata.get("vehicle", "")), "")

    principal = _capital_cost(entry_price, size, vehicle=vehicle)
    total_credit = round(principal + pnl, 2)

    ts = _safe_str(timestamp, _now_iso())
    symbol = _safe_str(symbol, "").upper()
    trade_id = _safe_str(trade_id, "")

    release_meta = {
        "principal": principal,
        "pnl": round(pnl, 2),
        "total_credit": total_credit,
        "immediate": bool(immediate),
        "vehicle": vehicle,
        "capital_release_rule": "option_premium_x_100_x_contracts" if vehicle == VEHICLE_OPTION else "entry_price_x_size",
        **metadata,
    }

    if immediate:
        state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) + total_credit, 2)
        state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)

        _append_activity_event(
            state,
            event_type="CLOSE",
            symbol=symbol,
            trade_id=trade_id,
            price=entry_price,
            size=size,
            cost=principal,
            pnl=pnl,
            timestamp=ts,
            metadata={
                "source": "release_trade_capital",
                **release_meta,
            },
        )
    else:
        state.setdefault("trade_history", [])
        state["trade_history"].append({
            "timestamp": ts,
            "date_key": _timestamp_to_date_key(ts) or _date_key(),
            "settle_date": (_now() + timedelta(days=1)).isoformat(),
            "status": "SETTLED_CREDIT",
            "credit_amount": total_credit,
            "trade_id": trade_id,
            "symbol": symbol,
            "principal": principal,
            "pnl": round(pnl, 2),
            "vehicle": vehicle,
            "metadata": release_meta,
        })

        _append_activity_event(
            state,
            event_type="CLOSE_PENDING_SETTLEMENT",
            symbol=symbol,
            trade_id=trade_id,
            price=entry_price,
            size=size,
            cost=principal,
            pnl=pnl,
            timestamp=ts,
            metadata={
                "source": "release_trade_capital",
                **release_meta,
            },
        )

    save_state(state)
    synced = load_state()

    return {
        "principal": principal,
        "pnl": round(pnl, 2),
        "total_credit": total_credit,
        "cash": synced["cash"],
        "buying_power": synced["buying_power"],
        "equity": synced["equity"],
        "estimated_account_value": synced.get("estimated_account_value", synced["equity"]),
        "open_market_value": synced.get("open_market_value", 0.0),
        "metadata": release_meta,
    }


def release_trade_cap(
    entry_price: float,
    size: float,
    pnl: float = 0.0,
    immediate: bool = True,
) -> Dict[str, Any]:
    return release_trade_capital(
        entry_price=entry_price,
        size=size,
        pnl=pnl,
        immediate=immediate,
    )


# =============================================================================
# Counters
# =============================================================================

def get_daily_trade_counters(date_key: Optional[str] = None) -> Dict[str, Any]:
    state = load_state()
    target_day = _safe_str(date_key, _date_key())

    entries = 0
    closes = 0
    pending_closes = 0
    entry_trade_ids = set()
    close_trade_ids = set()
    symbols_opened = set()
    symbols_closed = set()

    for event in _safe_list(state.get("activity_log")):
        event = _safe_dict(event)
        event_day = _safe_str(event.get("date_key"), "") or _timestamp_to_date_key(event.get("timestamp"))
        if event_day != target_day:
            continue

        event_type = _safe_str(event.get("event_type"), "").upper()
        trade_id = _safe_str(event.get("trade_id"), "")
        symbol = _safe_str(event.get("symbol"), "").upper()

        if event_type == "ENTRY":
            entries += 1
            if trade_id:
                entry_trade_ids.add(trade_id)
            if symbol:
                symbols_opened.add(symbol)

        elif event_type == "CLOSE":
            closes += 1
            if trade_id:
                close_trade_ids.add(trade_id)
            if symbol:
                symbols_closed.add(symbol)

        elif event_type == "CLOSE_PENDING_SETTLEMENT":
            pending_closes += 1
            if trade_id:
                close_trade_ids.add(trade_id)
            if symbol:
                symbols_closed.add(symbol)

    round_trips = 0
    if entry_trade_ids and close_trade_ids:
        round_trips = len(entry_trade_ids.intersection(close_trade_ids))
    elif closes > 0 and entries > 0:
        round_trips = min(entries, closes)

    return {
        "date_key": target_day,
        "entries_today": int(entries),
        "executed_entries_today": int(entries),
        "closes_today": int(closes),
        "pending_closes_today": int(pending_closes),
        "executed_trades_today": int(entries),
        "round_trips_today": int(round_trips),
        "entry_trade_ids": sorted(entry_trade_ids),
        "close_trade_ids": sorted(close_trade_ids),
        "symbols_opened_today": sorted(symbols_opened),
        "symbols_closed_today": sorted(symbols_closed),
        "counter_source": "account_state.activity_log",
    }


# =============================================================================
# Snapshots and display
# =============================================================================

def get_account_snapshot() -> Dict[str, Any]:
    state = sync_account_from_portfolio()
    open_math = calculate_open_market_value()
    realized_pnl = _realized_pnl_from_closed_positions()

    return {
        "cash": _round_money(state.get("cash", 0.0)),
        "buying_power": _round_money(state.get("buying_power", 0.0)),
        "equity": _round_money(state.get("equity", 0.0)),
        "estimated_account_value": _round_money(state.get("estimated_account_value", state.get("equity", 0.0))),
        "open_positions": _safe_int(open_math.get("open_positions"), 0),
        "open_market_value": _round_money(open_math.get("total_market_value", 0.0)),
        "open_cost_basis": _round_money(open_math.get("total_cost_basis", 0.0)),
        "open_unrealized_pnl": _round_money(open_math.get("total_unrealized", 0.0)),
        "realized_pnl": realized_pnl,
        "net_liquidation_value": _round_money(state.get("estimated_account_value", state.get("equity", 0.0))),
        "account_type": _safe_str(state.get("account_type"), "margin"),
        "reserve_mode": _safe_str(state.get("reserve_mode"), "percent"),
        "reserve_value": _safe_float(state.get("reserve_value"), 20.0),
        "effective_min_cash_reserve": resolve_min_cash_reserve(state),
        "vehicle_mix": open_math.get("vehicle_mix", {}),
        "option_safety": open_math.get("option_safety", {}),
        "account_math_basis": "cash + open_market_value",
        "last_account_sync": state.get("last_account_sync", ""),
    }


def print_account_snapshot() -> Dict[str, Any]:
    snapshot = get_account_snapshot()

    print("ACCOUNT SNAPSHOT")
    print(f"Cash: {snapshot['cash']}")
    print(f"Buying Power: {snapshot['buying_power']}")
    print(f"Equity: {snapshot['equity']}")
    print(f"Estimated Account Value: {snapshot['estimated_account_value']}")
    print(f"Open Positions: {snapshot['open_positions']}")
    print(f"Open Market Value: {snapshot['open_market_value']}")
    print(f"Open Cost Basis: {snapshot['open_cost_basis']}")
    print(f"Open Unrealized PnL: {snapshot['open_unrealized_pnl']}")
    print(f"Realized PnL: {snapshot['realized_pnl']}")
    print(f"Vehicle Mix: {snapshot['vehicle_mix']}")
    print(f"Option Safety: {snapshot['option_safety']}")
    print(f"Math Basis: {snapshot['account_math_basis']}")

    return snapshot


# =============================================================================
# Reset
# =============================================================================

def reset_account_state(
    equity: float = 1000.0,
    cash: float = 1000.0,
    buying_power: Optional[float] = None,
    account_type: str = "margin",
    reserve_mode: str = "percent",
    reserve_value: float = 20.0,
    clear_activity: bool = True,
) -> Dict[str, Any]:
    buying_power = cash if buying_power is None else buying_power

    reserve_mode = _safe_str(reserve_mode, "percent").lower()
    if reserve_mode not in {"percent", "amount"}:
        reserve_mode = "percent"

    reserve_value = _safe_float(reserve_value, 20.0)
    if reserve_mode == "percent":
        reserve_value = max(0.0, min(reserve_value, 100.0))
    else:
        reserve_value = max(0.0, reserve_value)

    state = {
        "equity": _round_money(equity, 1000.0),
        "cash": _round_money(cash, 1000.0),
        "buying_power": _round_money(buying_power, cash),
        "estimated_account_value": _round_money(equity, 1000.0),
        "open_market_value": 0.0,
        "open_cost_basis": 0.0,
        "open_unrealized_pnl": 0.0,
        "account_type": _safe_str(account_type, "margin").lower(),
        "trade_history": [] if clear_activity else _safe_list(load_state(sync=False).get("trade_history")),
        "activity_log": [] if clear_activity else _safe_list(load_state(sync=False).get("activity_log")),
        "reserve_mode": reserve_mode,
        "reserve_value": reserve_value,
        "last_account_sync": _now_iso(),
        "account_math_basis": "cash_plus_open_market_value",
    }

    if state["account_type"] not in {"cash", "margin"}:
        state["account_type"] = "margin"

    save_state(state)
    return load_state()


__all__ = [
    "load_state",
    "save_state",
    "sync_account_from_portfolio",
    "calculate_open_market_value",
    "get_account_snapshot",
    "print_account_snapshot",
    "resolve_min_cash_reserve",
    "set_reserve_policy",
    "get_reserve_policy",
    "record_trade",
    "settle_cash",
    "buying_power",
    "apply_realized_pnl",
    "release_trade_capital",
    "release_trade_cap",
    "get_daily_trade_counters",
    "reset_account_state",
]
