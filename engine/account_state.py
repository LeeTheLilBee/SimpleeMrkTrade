import json
from pathlib import Path
from datetime import datetime, timedelta

FILE = "data/account_state.json"

DEFAULT_STATE = {
    "equity": 1000,
    "cash": 1000,
    "buying_power": 1000,
    "trade_history": []
}

def load_state():
    if not Path(FILE).exists():
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE
    with open(FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(FILE, "w") as f:
        json.dump(state, f, indent=2)

def record_trade(symbol, price, size):
    state = load_state()

    trade = {
        "symbol": symbol,
        "price": price,
        "size": size,
        "timestamp": datetime.now().isoformat(),
        "settle_date": (datetime.now() + timedelta(days=1)).isoformat()
    }

    cost = price * size
    state["trade_history"].append(trade)
    state["cash"] = round(state["cash"] - cost, 2)
    state["buying_power"] = round(state["cash"], 2)

    save_state(state)

def settle_cash():
    state = load_state()
    now = datetime.now()

    unsettled = []
    settled_value = 0

    for trade in state.get("trade_history", []):
        settle_date = datetime.fromisoformat(trade["settle_date"])
        if settle_date <= now:
            settled_value += trade["price"] * trade["size"]
        else:
            unsettled.append(trade)

    state["trade_history"] = unsettled
    state["cash"] = round(state["cash"] + settled_value, 2)
    state["buying_power"] = round(state["cash"], 2)

    save_state(state)

def buying_power():
    return load_state().get("buying_power", 0)

def apply_realized_pnl(pnl):
    state = load_state()
    state["equity"] = round(state.get("equity", 1000) + pnl, 2)
    state["cash"] = round(state.get("cash", 1000) + pnl, 2)
    state["buying_power"] = round(state["cash"], 2)
    save_state(state)
