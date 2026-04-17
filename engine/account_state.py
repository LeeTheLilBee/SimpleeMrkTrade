import json
from pathlib import Path
from datetime import datetime, timedelta

FILE = "data/account_state.json"

DEFAULT_STATE = {
    "equity": 1000.0,
    "cash": 1000.0,
    "buying_power": 1000.0,
    "account_type": "margin",
    "trade_history": [],
    "reserve_mode": "percent",   # "percent" or "amount"
    "reserve_value": 20.0,       # 20% by default
}


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value, default=""):
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def load_state():
    if not Path(FILE).exists():
        save_state(DEFAULT_STATE)
        return dict(DEFAULT_STATE)

    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        data = dict(DEFAULT_STATE)

    for key, value in DEFAULT_STATE.items():
        data.setdefault(key, value)

    return data


def save_state(state):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def resolve_min_cash_reserve(state=None, fallback_amount=100.0):
    state = load_state() if state is None else state

    reserve_mode = _safe_str(state.get("reserve_mode", "amount"), "amount").lower()
    reserve_value = _safe_float(state.get("reserve_value", fallback_amount), fallback_amount)
    equity = _safe_float(state.get("equity", 0.0), 0.0)

    if reserve_mode == "percent":
        reserve_value = max(0.0, min(reserve_value, 100.0))
        return round(equity * (reserve_value / 100.0), 2)

    return round(max(0.0, reserve_value), 2)


def set_reserve_policy(mode="percent", value=20.0):
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

    return {
        "reserve_mode": state["reserve_mode"],
        "reserve_value": state["reserve_value"],
        "effective_min_cash_reserve": resolve_min_cash_reserve(state),
    }


def get_reserve_policy():
    state = load_state()
    return {
        "reserve_mode": state.get("reserve_mode", "percent"),
        "reserve_value": state.get("reserve_value", 20.0),
        "effective_min_cash_reserve": resolve_min_cash_reserve(state),
    }


def record_trade(symbol, price, size):
    state = load_state()

    price = _safe_float(price, 0.0)
    size = _safe_float(size, 0.0)
    cost = round(price * size, 2)

    trade = {
        "symbol": symbol,
        "price": price,
        "size": size,
        "timestamp": datetime.now().isoformat(),
        "settle_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "cost": cost,
        "status": "OPEN",
    }

    state["trade_history"].append(trade)
    state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) - cost, 2)
    state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)
    save_state(state)
    return trade


def settle_cash():
    state = load_state()
    now = datetime.now()

    unsettled = []
    settled_value = 0.0

    for trade in state.get("trade_history", []):
        settle_date_raw = trade.get("settle_date")
        try:
            settle_date = datetime.fromisoformat(settle_date_raw)
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
    return state


def buying_power():
    return _safe_float(load_state().get("buying_power", 0.0), 0.0)


def apply_realized_pnl(pnl):
    state = load_state()
    pnl = _safe_float(pnl, 0.0)

    state["equity"] = round(_safe_float(state.get("equity", 1000.0), 1000.0) + pnl, 2)
    state["cash"] = round(_safe_float(state.get("cash", 1000.0), 1000.0) + pnl, 2)
    state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)

    save_state(state)
    return state


def release_trade_capital(entry_price, size, pnl=0.0, immediate=True):
    state = load_state()

    entry_price = _safe_float(entry_price, 0.0)
    size = _safe_float(size, 0.0)
    pnl = _safe_float(pnl, 0.0)

    principal = round(entry_price * size, 2)
    total_credit = round(principal + pnl, 2)

    if immediate:
        state["cash"] = round(_safe_float(state.get("cash", 0.0), 0.0) + total_credit, 2)
        state["buying_power"] = round(_safe_float(state.get("cash", 0.0), 0.0), 2)
        state["equity"] = round(_safe_float(state.get("equity", 1000.0), 1000.0) + pnl, 2)
    else:
        state["trade_history"].append({
            "timestamp": datetime.now().isoformat(),
            "settle_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "SETTLED_CREDIT",
            "credit_amount": total_credit,
        })
        state["equity"] = round(_safe_float(state.get("equity", 1000.0), 1000.0) + pnl, 2)

    save_state(state)

    return {
        "principal": principal,
        "pnl": pnl,
        "total_credit": total_credit,
        "cash": state["cash"],
        "buying_power": state["buying_power"],
        "equity": state["equity"],
    }


def release_trade_cap(entry_price, size, pnl=0.0, immediate=True):
    return release_trade_capital(
        entry_price=entry_price,
        size=size,
        pnl=pnl,
        immediate=immediate,
    )


def reset_account_state(
    equity=1000.0,
    cash=1000.0,
    buying_power=None,
    account_type="margin",
    reserve_mode="percent",
    reserve_value=20.0,
):
    buying_power = cash if buying_power is None else buying_power

    if _safe_str(reserve_mode, "percent").lower() not in {"percent", "amount"}:
        reserve_mode = "percent"

    reserve_value = _safe_float(reserve_value, 20.0)
    if reserve_mode == "percent":
        reserve_value = max(0.0, min(reserve_value, 100.0))
    else:
        reserve_value = max(0.0, reserve_value)

    state = {
        "equity": _safe_float(equity, 1000.0),
        "cash": _safe_float(cash, 1000.0),
        "buying_power": _safe_float(buying_power, cash),
        "account_type": account_type,
        "trade_history": [],
        "reserve_mode": reserve_mode,
        "reserve_value": reserve_value,
    }

    save_state(state)
    return state
