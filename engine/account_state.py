import json
from pathlib import Path
from datetime import datetime, timedelta

FILE = "data/account_state.json"

DEFAULT_STATE = {
    "equity": 1000.0,
    "cash": 1000.0,
    "buying_power": 1000.0,
    "account_type": "margin",
    "trade_history": []
}


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


def record_trade(symbol, price, size):
    state = load_state()

    price = float(price or 0)
    size = float(size or 0)
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
    state["cash"] = round(float(state.get("cash", 0)) - cost, 2)
    state["buying_power"] = round(float(state["cash"]), 2)

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
            settled_value += float(trade.get("credit_amount", 0) or 0)
        else:
            unsettled.append(trade)

    state["trade_history"] = unsettled
    state["cash"] = round(float(state.get("cash", 0)) + settled_value, 2)
    state["buying_power"] = round(float(state["cash"]), 2)

    save_state(state)
    return state


def buying_power():
    return float(load_state().get("buying_power", 0) or 0)


def apply_realized_pnl(pnl):
    state = load_state()
    pnl = float(pnl or 0)

    state["equity"] = round(float(state.get("equity", 1000)) + pnl, 2)
    state["cash"] = round(float(state.get("cash", 1000)) + pnl, 2)
    state["buying_power"] = round(float(state["cash"]), 2)

    save_state(state)
    return state


def release_trade_capital(entry_price, size, pnl=0.0, immediate=True):
    state = load_state()

    entry_price = float(entry_price or 0)
    size = float(size or 0)
    pnl = float(pnl or 0)

    principal = round(entry_price * size, 2)
    total_credit = round(principal + pnl, 2)

    if immediate:
        state["cash"] = round(float(state.get("cash", 0)) + total_credit, 2)
        state["buying_power"] = round(float(state["cash"]), 2)
        state["equity"] = round(float(state.get("equity", 1000)) + pnl, 2)
    else:
        state["trade_history"].append({
            "timestamp": datetime.now().isoformat(),
            "settle_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "SETTLED_CREDIT",
            "credit_amount": total_credit,
        })
        state["equity"] = round(float(state.get("equity", 1000)) + pnl, 2)

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
):
    buying_power = cash if buying_power is None else buying_power

    state = {
        "equity": float(equity),
        "cash": float(cash),
        "buying_power": float(buying_power),
        "account_type": account_type,
        "trade_history": [],
    }
    save_state(state)
    return state
