from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso

OPTIONS_FILE = "/content/SimpleeMrkTrade/data_v2/options_universe.json"
EQUITY_FILE = "/content/SimpleeMrkTrade/data_v2/equity_universe.json"
REJECTION_FILE = "/content/SimpleeMrkTrade/data_v2/rejection_feed.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _bucket_reason(symbol: str) -> str:
    symbol = str(symbol or "").upper()
    if symbol in {"T", "VZ", "DUK", "SO"}:
        return "Lower velocity profile than the current leaders."
    if symbol in {"GLD", "SLV", "TLT", "LQD", "HYG"}:
        return "Macro asset is interesting, but not currently beating the top pressure names."
    if symbol in {"NKE", "DIS", "SBUX", "TGT"}:
        return "Consumer name is still not showing strong enough setup quality."
    return "Setup did not beat the strongest names in the current ranking pass."


def _rejection_card(item: Dict[str, Any], lane: str) -> Dict[str, Any]:
    symbol = str(item.get("symbol", "") or "").upper()
    company_name = str(item.get("company_name", symbol) or symbol)

    explicit_reason = str(item.get("reason", "") or "").strip()
    reason = explicit_reason or _bucket_reason(symbol)

    if lane == "options":
        next_step = "Watch for stronger option-ready structure, better timing, or cleaner liquidity."
    else:
        next_step = "Watch for stronger momentum, cleaner entry quality, or better relative pressure."

    return {
        "symbol": symbol,
        "company_name": company_name,
        "lane": lane,
        "headline": f"{symbol} was passed over for now",
        "reason": reason,
        "next_step": next_step,
        "destination": f"/signals/{symbol}",
        "timestamp": item.get("timestamp", now_iso()),
    }


def build_rejection_feed() -> Dict[str, Any]:
    equity_payload = _safe_dict(_load_json(EQUITY_FILE, {}))
    options_payload = _safe_dict(_load_json(OPTIONS_FILE, {}))

    equity_rejected = _safe_list(equity_payload.get("rejected", []))
    options_rejected = _safe_list(options_payload.get("rejected", []))

    equity_cards = [_rejection_card(item, "equity") for item in equity_rejected if isinstance(item, dict)]
    options_cards = [_rejection_card(item, "options") for item in options_rejected if isinstance(item, dict)]

    payload = {
        "equity_rejections": equity_cards[:20],
        "options_rejections": options_cards[:20],
        "combined": (options_cards + equity_cards)[:30],
        "meta": {
            "rebuilt_at": now_iso(),
            "equity_rejection_count": len(equity_cards[:20]),
            "options_rejection_count": len(options_cards[:20]),
            "combined_count": len((options_cards + equity_cards)[:30]),
        },
    }

    _save_json(REJECTION_FILE, payload)
    return payload


def load_rejection_feed() -> Dict[str, Any]:
    payload = _load_json(REJECTION_FILE, {})
    return payload if isinstance(payload, dict) else {}
