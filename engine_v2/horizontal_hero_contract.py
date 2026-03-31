from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.spotlight_builder import load_spotlight_feed

HERO_STRIP_FILE = "/content/SimpleeMrkTrade/data_v2/horizontal_hero_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _hero_card(item: Dict[str, Any]) -> Dict[str, Any]:
    item = _safe_dict(item)
    return {
        "symbol": item.get("symbol"),
        "headline": item.get("headline", ""),
        "summary": item.get("summary", ""),
        "lane": item.get("lane", "equity"),
        "pressure_level": item.get("pressure_level", "medium"),
        "confidence_tier": item.get("confidence_tier", 3),
        "destination": item.get("destination", "/signals"),
    }


def build_horizontal_hero_contract() -> Dict[str, Any]:
    spotlight = _safe_dict(load_spotlight_feed())
    featured = _safe_list(spotlight.get("featured", []))

    cards = [_hero_card(item) for item in featured[:8] if isinstance(item, dict)]

    payload = {
        "enabled_on": ["symbol_page"],
        "disabled_on": ["dashboard", "market_map"],
        "behavior": {
            "layout": "horizontal_scroll",
            "snap": True,
            "dim_non_focus": True,
            "focus_expand": True,
        },
        "cards": cards,
        "meta": {
            "rebuilt_at": now_iso(),
            "card_count": len(cards),
        },
    }

    _save_json(HERO_STRIP_FILE, payload)
    return payload


def load_horizontal_hero_contract() -> Dict[str, Any]:
    payload = _load_json(HERO_STRIP_FILE, {})
    return payload if isinstance(payload, dict) else {}
