import json
from pathlib import Path
from datetime import datetime


FILE = "data/trade_details.json"


def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data[-300:], f, indent=2)


def build_trade_detail(
    trade,
    regime=None,
    mode=None,
    volatility_state=None,
    breadth=None,
    market_context=None,
    why_not_this_trade=None,
    timeline=None,
    crowd_pressure=None,
    signal_decay=None,
    source="execution",
    **kwargs
):
    symbol = trade.get("symbol", "UNKNOWN")
    strategy = trade.get("strategy", "CALL")
    score = trade.get("score", 0)
    confidence = trade.get("confidence", "LOW")
    price = float(trade.get("price", 0) or 0)
    atr = float(trade.get("atr", 0) or 0)

    if strategy == "PUT":
        stop_logic = round(price + (atr * 1.5), 2) if price else None
        target_logic = round(price - (atr * 2.0), 2) if price else None
    else:
        stop_logic = round(price - (atr * 1.5), 2) if price else None
        target_logic = round(price + (atr * 2.0), 2) if price else None

    if score >= 180:
        thesis = [
            "Strong structural alignment is present.",
            "Momentum and participation support continuation.",
            "This setup is acting like a leadership-quality opportunity."
        ]
    elif score >= 130:
        thesis = [
            "Constructive setup with meaningful support.",
            "Conditions are favorable but still developing.",
            "Follow-through matters more than early excitement."
        ]
    else:
        thesis = [
            "Setup quality is mixed or early-stage.",
            "Confirmation is weaker than elite-quality opportunities.",
            "Risk management should stay tight."
        ]

    detail = {
        "trade_id": kwargs.get("trade_id") or f"{symbol}-{strategy}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "entry": round(price, 2) if price else 0,
        "atr": round(atr, 2),
        "regime": regime,
        "mode": mode,
        "volatility_state": volatility_state,
        "breadth": breadth,
        "source": source,
        "risk": {
            "stop_logic": stop_logic,
            "target_logic": target_logic,
            "note": "Stops and targets are volatility-aware.",
            "story": "Risk is framed around ATR and structural confirmation, not random distance."
        },
        "signal_decay": signal_decay or {
            "minutes_old": 0,
            "decay_pct": 0,
            "adjusted_score": score
        },
        "crowd_pressure": crowd_pressure or {
            "score": 0,
            "label": "LOW",
            "note": "Crowd pressure not elevated."
        },
        "thesis": thesis,
        "narrative": {
            "entry_story": "The engine found enough alignment to justify consideration for entry.",
            "management_story": "Trade management should adapt to volatility, confirmation, and structural strength.",
            "exit_story": "The trade should be exited if structure degrades or invalidation is triggered."
        },
        "context": market_context or [],
        "why_not_this_trade": why_not_this_trade or [],
        "timeline": timeline or []
    }

    return detail["trade_id"], detail


def save_trade_detail(detail):
    data = _load()
    data.append(detail)
    _save(data)
    return detail


def build_and_save_trade_detail(*args, **kwargs):
    trade_id, detail = build_trade_detail(*args, **kwargs)
    save_trade_detail(detail)
    return trade_id, detail


def get_trade_detail(trade_id):
    data = _load()
    for detail in reversed(data):
        if detail.get("trade_id") == trade_id:
            return detail
    return None


def update_trade_detail(trade_id, updates):
    data = _load()
    updated = None

    for detail in data:
        if detail.get("trade_id") == trade_id:
            detail.update(updates or {})
            updated = detail
            break

    _save(data)
    return updated


def append_trade_detail_timeline(trade_id, event, note=None, extra=None):
    data = _load()
    updated = None

    for detail in data:
        if detail.get("trade_id") == trade_id:
            timeline = detail.get("timeline", [])
            if not isinstance(timeline, list):
                timeline = []

            timeline.append({
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "note": note or "",
                "extra": extra or {}
            })

            detail["timeline"] = timeline
            updated = detail
            break

    _save(data)
    return updated
