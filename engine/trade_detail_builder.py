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

def build_trade_detail(trade, market_context=None):
    trade_id = str(uuid.uuid4())

    detail = {
        "id": trade_id,
        "timestamp": datetime.now().isoformat(),
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "entry": trade.get("price"),
        "atr": trade.get("atr"),

        "thesis": [
            f"{trade['symbol']} showing structured setup",
            f"Score {trade.get('score')} confirms strength",
            f"Confidence: {trade.get('confidence')}",
        ],

        "context": market_context or [],

        "risk": {
            "stop_logic": "ATR-based dynamic stop",
            "note": "Position risk aligned with volatility"
        },

        "timeline": []
    }

    return trade_id, detail

def save_trade_detail(detail):
    data = _load()
    data.append(detail)
    _save(data)

def get_trade_details():
    return _load()

def get_trade_detail_by_id(trade_id):
    for d in _load():
        if d["id"] == trade_id:
            return d
    return None
