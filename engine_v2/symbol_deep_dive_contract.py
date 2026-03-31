from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.symbol_hero_contract import build_symbol_hero_contract

DEEP_DIVE_FILE = "/content/SimpleeMrkTrade/data_v2/symbol_deep_dive_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_panels(symbol_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    lanes = _safe_dict(symbol_payload.get("lanes"))
    equity = _safe_dict(lanes.get("equity"))
    options = _safe_dict(lanes.get("options"))

    panels = [
        {
            "key": "equity_intelligence",
            "title": "Equity Intelligence",
            "summary": "How the stock setup looks on its own.",
            "available": bool(equity.get("available")),
            "content": {
                "scanner": _safe_dict(equity.get("scanner")),
                "state": _safe_dict(equity.get("state")),
                "reasoning": _safe_dict(equity.get("reasoning")),
            },
        },
        {
            "key": "options_intelligence",
            "title": "Options Intelligence",
            "summary": "How the options layer wants to structure the trade.",
            "available": bool(options.get("available")),
            "content": {
                "scanner": _safe_dict(options.get("scanner")),
                "state": _safe_dict(options.get("state")),
                "reasoning": _safe_dict(options.get("reasoning")),
                "options_plan": _safe_dict(options.get("options_plan")),
            },
        },
    ]

    return panels


def _build_timeline(symbol: str) -> List[Dict[str, Any]]:
    symbol = str(symbol or "").upper()
    return [
        {
            "key": "setup_seen",
            "label": f"{symbol} setup recognized",
            "summary": "The system recognized this symbol as one of the current active setups.",
        },
        {
            "key": "lane_selected",
            "label": f"{symbol} lane assignment",
            "summary": "The symbol was routed into equity and/or options intelligence.",
        },
        {
            "key": "ready_state",
            "label": f"{symbol} readiness state",
            "summary": "The system attached status, pressure, and confidence framing.",
        },
    ]


def build_symbol_deep_dive_contract(symbol: str) -> Dict[str, Any]:
    symbol = str(symbol or "").upper()
    hero_payload = build_symbol_hero_contract(symbol)

    payload = {
        "symbol": symbol,
        "hero": _safe_dict(hero_payload.get("hero")),
        "panels": _build_panels(hero_payload),
        "timeline": _build_timeline(symbol),
        "meta": {
            "rebuilt_at": now_iso(),
            "panel_count": 2,
            "timeline_count": 3,
        },
    }

    _save_json(DEEP_DIVE_FILE, payload)
    return payload


def load_symbol_deep_dive_contract() -> Dict[str, Any]:
    payload = _load_json(DEEP_DIVE_FILE, {})
    return payload if isinstance(payload, dict) else {}
