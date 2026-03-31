from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso

EQUITY_FILE = "/content/SimpleeMrkTrade/data_v2/equity_universe.json"
OPTIONS_FILE = "/content/SimpleeMrkTrade/data_v2/options_universe.json"
SYMBOL_HERO_FILE = "/content/SimpleeMrkTrade/data_v2/symbol_hero_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _find_symbol(symbol: str) -> Dict[str, Any]:
    symbol = str(symbol or "").strip().upper()

    equity_payload = _safe_dict(_load_json(EQUITY_FILE, {}))
    options_payload = _safe_dict(_load_json(OPTIONS_FILE, {}))

    equity_selected = _safe_list(equity_payload.get("selected", []))
    options_selected = _safe_list(options_payload.get("selected", []))

    equity_match = next((row for row in equity_selected if str(row.get("symbol", "")).upper() == symbol), None)
    options_match = next((row for row in options_selected if str(row.get("symbol", "")).upper() == symbol), None)

    return {
        "equity": equity_match if isinstance(equity_match, dict) else {},
        "options": options_match if isinstance(options_match, dict) else {},
    }


def build_symbol_hero_contract(symbol: str) -> Dict[str, Any]:
    symbol = str(symbol or "").strip().upper()
    found = _find_symbol(symbol)

    equity = _safe_dict(found.get("equity"))
    options = _safe_dict(found.get("options"))

    primary = options if options else equity
    scanner = _safe_dict(primary.get("scanner"))
    state = _safe_dict(primary.get("state"))
    options_plan = _safe_dict(options.get("options_plan"))

    payload = {
        "symbol": symbol,
        "company_name": primary.get("company_name", symbol),
        "hero": {
            "title": f"{symbol} Intelligence",
            "summary": state.get("status_label", "Active setup") if primary else "No active intelligence found.",
            "direction": scanner.get("direction", "CALL"),
            "trend": scanner.get("trend", "SIDEWAYS"),
            "setup_type": scanner.get("setup_type", "developing"),
            "pressure_level": state.get("pressure_level", "medium"),
            "confidence_tier": state.get("confidence_tier", 3),
            "price": scanner.get("price"),
            "destination": f"/signals/{symbol}",
        },
        "lanes": {
            "equity": {
                "available": bool(equity),
                "scanner": _safe_dict(equity.get("scanner")),
                "state": _safe_dict(equity.get("state")),
                "reasoning": _safe_dict(equity.get("reasoning")),
            },
            "options": {
                "available": bool(options),
                "scanner": _safe_dict(options.get("scanner")),
                "state": _safe_dict(options.get("state")),
                "reasoning": _safe_dict(options.get("reasoning")),
                "options_plan": options_plan,
            },
        },
        "meta": {
            "rebuilt_at": now_iso(),
            "has_equity_lane": bool(equity),
            "has_options_lane": bool(options),
        },
    }

    _save_json(SYMBOL_HERO_FILE, payload)
    return payload


def load_symbol_hero_contract() -> Dict[str, Any]:
    payload = _load_json(SYMBOL_HERO_FILE, {})
    return payload if isinstance(payload, dict) else {}
