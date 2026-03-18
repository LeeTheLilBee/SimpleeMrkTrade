import json
from datetime import datetime
from engine.account_state import load_state
from engine.paper_portfolio import open_count
from engine.trade_history import executed_trade_count
from engine.performance_tracker import performance_summary

FILE = "data/system_status.json"

def write_system_status(regime="UNKNOWN", volatility="UNKNOWN", mode="UNKNOWN"):
    state = load_state()
    perf = performance_summary()

    payload = {
        "timestamp": datetime.now().isoformat(),
        "cash": round(float(state.get("cash", 0)), 2),
        "buying_power": round(float(state.get("buying_power", 0)), 2),
        "equity": round(float(state.get("equity", 0)), 2),
        "open_positions": open_count(),
        "executed_trades": executed_trade_count(),
        "regime": regime,
        "volatility": volatility,
        "mode": mode,
        "total_trades": perf.get("trades", 0),
        "winrate": perf.get("winrate", 0),
        "max_drawdown": perf.get("max_drawdown", 0),
    }

    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)

    return payload
