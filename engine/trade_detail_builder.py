import json
from pathlib import Path
from datetime import datetime
import uuid

DETAIL_FILE = "data/trade_details.json"

def _load():
    if not Path(DETAIL_FILE).exists():
        return []
    with open(DETAIL_FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(DETAIL_FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def _risk_story(strategy, atr):
    if atr is None:
        return "Risk model unavailable."
    if strategy == "PUT":
        return f"Bearish setup using ATR-aware downside framing. Current ATR is {round(atr, 2)}."
    return f"Bullish setup using ATR-aware upside framing. Current ATR is {round(atr, 2)}."

def _management_story(confidence, score):
    if (score or 0) >= 200:
        return "This setup belongs to the highest-conviction bucket and deserves closer monitoring for follow-through."
    if (score or 0) >= 120:
        return "This setup is premium-worthy and should be monitored for confirmation, persistence, and risk stability."
    if confidence == "MEDIUM":
        return "This setup has enough structure to matter, but should be treated with discipline and context."
    return "This setup is exploratory and should be interpreted carefully."

def build_trade_detail(trade, market_context=None):
    trade_id = str(uuid.uuid4())

    symbol = trade.get("symbol")
    strategy = trade.get("strategy")
    score = trade.get("score")
    confidence = trade.get("confidence")
    entry = trade.get("price")
    atr = trade.get("atr")

    thesis = [
        f"{symbol} surfaced with a structured {strategy} setup.",
        f"Score {score} confirmed enough strength to pass the current ranking logic.",
        f"Confidence registered as {confidence}, which shapes how aggressively it should be interpreted.",
    ]

    detail = {
        "id": trade_id,
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "entry": entry,
        "atr": atr,
        "thesis": thesis,
        "context": market_context or [],
        "risk": {
            "stop_logic": "ATR-based dynamic stop",
            "note": "Position risk aligned with volatility",
            "story": _risk_story(strategy, atr),
        },
        "narrative": {
            "entry_story": f"{symbol} became interesting because its structure, score, and context aligned strongly enough to create a tradable thesis.",
            "management_story": _management_story(confidence, score),
            "exit_story": "Exit logic should respond to stop pressure, target progress, weakening structure, or automated close conditions.",
        },
        "timeline": [
            {
                "timestamp": datetime.now().isoformat(),
                "event": "DETAIL_CREATED",
                "note": f"{symbol} detail record created.",
            }
        ],
    }

    return trade_id, detail

def save_trade_detail(detail):
    data = _load()
    data.append(detail)
    _save(data)
    return detail

def get_trade_details():
    return _load()

def get_trade_detail_by_id(trade_id):
    for d in _load():
        if d["id"] == trade_id:
            return d
    return None

def append_trade_detail_timeline(trade_id, event, note, extra=None):
    if not trade_id:
        return None

    data = _load()
    updated = None

    for d in data:
        if d.get("id") == trade_id:
            d.setdefault("timeline", [])
            payload = {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "note": note,
            }
            if extra:
                payload["extra"] = extra
            d["timeline"].append(payload)
            updated = d
            break

    if updated is not None:
        _save(data)

    return updated
