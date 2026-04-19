from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
from engine.portfolio_summary import portfolio_summary

TRADE_FILE = "data/trade_log.json"


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _read_json(path_str: str, default: Any):
    path = Path(path_str)
    if not path.exists():
        return default
    try:
        with open(path_str, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def analytics():
    trades = _safe_list(_read_json(TRADE_FILE, []))

    wins = 0
    losses = 0
    flats = 0
    total_pnl = 0.0
    strategies: Dict[str, int] = {}
    by_symbol: Dict[str, int] = {}

    last_trade = None

    for row in trades:
        if not isinstance(row, dict):
            continue

        pnl = _safe_float(row.get("pnl", 0.0), 0.0)
        strategy = _safe_str(row.get("strategy"), "UNKNOWN").upper()
        symbol = _safe_str(row.get("symbol"), "UNKNOWN").upper()

        total_pnl += pnl
        strategies[strategy] = strategies.get(strategy, 0) + 1
        by_symbol[symbol] = by_symbol.get(symbol, 0) + 1

        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1
        else:
            flats += 1

        last_trade = {
            "symbol": symbol,
            "trade_id": _safe_str(row.get("trade_id"), ""),
            "strategy": strategy,
            "pnl": round(pnl, 2),
            "timestamp": _safe_str(
                row.get("closed_at", row.get("timestamp", row.get("opened_at", ""))),
                "",
            ),
        }

    total = wins + losses + flats
    winrate = round(wins / total, 4) if total else 0.0
    lossrate = round(losses / total, 4) if total else 0.0

    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "flats": flats,
        "winrate": winrate,
        "lossrate": lossrate,
        "total_pnl": round(total_pnl, 2),
        "average_pnl": round(total_pnl / total, 2) if total else 0.0,
        "strategies": strategies,
        "symbols": by_symbol,
        "last_trade": last_trade,
        "portfolio": portfolio_summary(),
    }
