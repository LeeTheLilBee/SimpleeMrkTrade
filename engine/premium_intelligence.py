import json
from pathlib import Path
from datetime import datetime
from engine.signal_explainer import explain_signal

PREMIUM_FILE = "data/premium_analysis.json"
WHY_FILE = "data/why_this_trade.json"

def _load(path):
    if not Path(path).exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data[-100:], f, indent=2)

def build_premium_entry(trade, market_context=None, mode=None, regime=None, volatility=None):
    price = trade.get("price")
    atr = trade.get("atr", 0) or 0

    if trade.get("strategy") == "PUT":
        stop = round(price + (atr * 1.5), 2) if price is not None else None
        target = round(price - (atr * 2.0), 2) if price is not None else None
    else:
        stop = round(price - (atr * 1.5), 2) if price is not None else None
        target = round(price + (atr * 2.0), 2) if price is not None else None

    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "entry": round(price, 2) if price is not None else None,
        "stop": stop,
        "target": target,
        "mode": mode,
        "regime": regime,
        "volatility": volatility,
        "snippets": market_context or [],
        "reasons": explain_signal(trade),
    }
    return entry

def save_premium_analysis(trade, market_context=None, mode=None, regime=None, volatility=None):
    data = _load(PREMIUM_FILE)
    entry = build_premium_entry(
        trade,
        market_context=market_context,
        mode=mode,
        regime=regime,
        volatility=volatility,
    )
    data.append(entry)
    _save(PREMIUM_FILE, data)
    save_why_this_trade(entry)
    return entry

def save_why_this_trade(entry):
    data = _load(WHY_FILE)
    explanation = {
        "timestamp": entry["timestamp"],
        "symbol": entry["symbol"],
        "strategy": entry["strategy"],
        "score": entry["score"],
        "confidence": entry["confidence"],
        "entry": entry["entry"],
        "stop": entry["stop"],
        "target": entry["target"],
        "market_context": entry.get("snippets", []),
        "why_selected": entry.get("reasons", []),
    }
    data.append(explanation)
    _save(WHY_FILE, data)
    return explanation
