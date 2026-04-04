from typing import Dict


def normalize_replay_trade(trade: Dict) -> Dict:
    if not isinstance(trade, dict):
        trade = {}

    symbol = str(trade.get("symbol", "") or "").upper().strip()
    setup_family = str(trade.get("setup_family", "") or trade.get("pattern", "") or "unknown")
    direction = str(trade.get("direction", "") or "unknown")
    outcome = str(trade.get("outcome", "") or "unknown")
    pnl = trade.get("pnl", 0)
    entry_quality = trade.get("entry_quality", "unknown")
    notes = str(trade.get("notes", "") or "")

    return {
        "symbol": symbol,
        "setup_family": setup_family,
        "direction": direction,
        "outcome": outcome,
        "pnl": pnl,
        "entry_quality": entry_quality,
        "notes": notes,
        "raw_trade": trade,
    }
