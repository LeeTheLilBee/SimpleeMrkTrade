"""
===========================================================
SYMBOL INTELLIGENCE ENGINE
-----------------------------------------------------------
Builds per-symbol intelligence by merging:
- signal data
- trade intelligence
- execution universe status

Output shape per symbol:
{
  "symbol": ...,
  "score": ...,
  "previous_score": ...,
  "confidence": ...,
  "opinion": ...,
  "timestamp": ...,
  "execution": {
      "status": "selected" | "eligible_not_selected" | "rejected" | "unknown",
      "selected": bool,
      "eligible": bool,
      "execution_quality": int,
      "cap_context": ...,
      "reason": ...
  },
  "intelligence": {...}
}
===========================================================
"""

from typing import Any, Dict, List
from engine.trade_intelligence import build_trade_intelligence


def _execution_lookup(execution_universe: Dict):
    selected = execution_universe.get("selected", [])
    if not isinstance(selected, list):
        selected = []

    selected_symbols = set()
    selected_by_symbol = {}
    for item in selected:
        if not isinstance(item, dict):
            continue
        symbol = item.get("symbol")
        if not symbol:
            continue
        selected_symbols.add(symbol)
        selected_by_symbol[symbol] = item

    return selected_symbols, selected_by_symbol


def _infer_execution_status(signal: Dict, selected_symbols: set, selected_by_symbol: Dict, execution_universe: Dict):
    symbol = signal.get("symbol")
    eligible = bool(signal.get("eligible", False))
    execution_quality = int(signal.get("execution_quality", 0) or 0)

    if symbol in selected_symbols:
        return {
            "status": "selected",
            "selected": True,
            "eligible": True,
            "execution_quality": selected_by_symbol.get(symbol, {}).get("execution_quality", execution_quality),
            "cap_context": execution_universe.get("cap", 0),
            "reason": "Selected for active execution because it ranked inside the current execution cap."
        }

    if eligible:
        return {
            "status": "eligible_not_selected",
            "selected": False,
            "eligible": True,
            "execution_quality": execution_quality,
            "cap_context": execution_universe.get("cap", 0),
            "reason": "Passed the trade gate, but was ranked below the current execution cap."
        }

    return {
        "status": "rejected",
        "selected": False,
        "eligible": False,
        "execution_quality": execution_quality,
        "cap_context": execution_universe.get("cap", 0),
        "reason": "Rejected by the current execution filters for market conditions, score, or confidence."
    }


def build_symbol_intelligence(signals: List[Dict], execution_universe: Dict) -> Dict:
    symbols = {}

    selected_symbols, selected_by_symbol = _execution_lookup(execution_universe)

    for s in signals:
        if not isinstance(s, dict):
            continue

        symbol = s.get("symbol")
        if not symbol:
            continue

        intel = build_trade_intelligence(s)
        execution = _infer_execution_status(
            signal=s,
            selected_symbols=selected_symbols,
            selected_by_symbol=selected_by_symbol,
            execution_universe=execution_universe,
        )

        symbols[symbol] = {
            "symbol": symbol,
            "score": s.get("score", s.get("latest_score", 0)),
            "previous_score": s.get("previous_score", s.get("score", 0)),
            "confidence": s.get("confidence", s.get("latest_confidence", "LOW")),
            "opinion": s.get("opinion", "Active setup."),
            "timestamp": s.get("timestamp", s.get("latest_timestamp", "")),
            "execution": execution,
            "intelligence": intel,
        }

    return symbols
