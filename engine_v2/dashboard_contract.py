from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso
from engine_v2.mode_router import resolve_user_modes
from engine_v2.spotlight_builder import build_spotlight_feed_for_user
from engine_v2.market_map_builder import build_market_map
from engine_v2.rejection_builder import build_rejection_feed

DASHBOARD_FILE = "/content/SimpleeMrkTrade/data_v2/dashboard_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_mode_bar(modes: Dict[str, Any]) -> Dict[str, Any]:
    intelligence_mode = str(modes.get("intelligence_mode", "hybrid"))
    control_mode = str(modes.get("control_mode", "manual"))
    auto_scope = str(modes.get("auto_scope", "both"))
    experience_mode = str(modes.get("experience_mode", "balanced"))

    return {
        "intelligence_mode": intelligence_mode,
        "control_mode": control_mode,
        "auto_scope": auto_scope,
        "experience_mode": experience_mode,
        "chips": [
            {"label": f"Mode: {intelligence_mode.title()}", "key": "intelligence_mode"},
            {"label": f"Control: {control_mode.title()}", "key": "control_mode"},
            {"label": f"Scope: {auto_scope.title()}", "key": "auto_scope"},
            {"label": f"Experience: {experience_mode.replace('_', ' ').title()}", "key": "experience_mode"},
        ],
    }


def _build_command_cards(spotlight: Dict[str, Any], market_map: Dict[str, Any], rejections: Dict[str, Any]) -> List[Dict[str, Any]]:
    featured = _safe_list(spotlight.get("featured", []))
    map_meta = _safe_dict(market_map.get("meta", {}))
    rejection_meta = _safe_dict(rejections.get("meta", {}))

    cards = [
        {
            "key": "spotlight",
            "title": "Spotlight",
            "value": len(featured),
            "summary": "Top live ideas leading the platform right now.",
            "destination": "/spotlight",
        },
        {
            "key": "market_map",
            "title": "Market Map",
            "value": map_meta.get("tile_count", 0),
            "summary": "Interactive pressure tiles across the current field.",
            "destination": "/market-map",
        },
        {
            "key": "rejections",
            "title": "Passed Over",
            "value": rejection_meta.get("combined_count", 0),
            "summary": "Names that missed the current cut and why.",
            "destination": "/research/rejections",
        },
    ]
    return cards


def _build_sections(spotlight: Dict[str, Any], market_map: Dict[str, Any], rejections: Dict[str, Any]) -> List[Dict[str, Any]]:
    featured = _safe_list(spotlight.get("featured", []))
    top_stocks = _safe_list(spotlight.get("top_stocks", []))
    top_options = _safe_list(spotlight.get("top_options", []))
    top_mixed = _safe_list(spotlight.get("top_mixed", []))
    map_tiles = _safe_list(market_map.get("tiles", []))
    rejection_cards = _safe_list(rejections.get("combined", []))

    return [
        {
            "key": "featured",
            "title": "Best Plays Right Now",
            "summary": "The strongest live ideas across the current system mode.",
            "destination": "/spotlight",
            "items": featured[:5],
        },
        {
            "key": "top_options",
            "title": "Best Options",
            "summary": "Current option-ready structures with the cleanest setup profile.",
            "destination": "/signals?lane=options",
            "items": top_options[:5],
        },
        {
            "key": "top_stocks",
            "title": "Best Stocks",
            "summary": "Top equity setups without forcing the options layer.",
            "destination": "/signals?lane=equity",
            "items": top_stocks[:5],
        },
        {
            "key": "market_pressure",
            "title": "Market Pressure",
            "summary": "Calm pressure map data the UI can turn into the main visual layer.",
            "destination": "/market-map",
            "items": map_tiles[:8],
        },
        {
            "key": "mixed_view",
            "title": "Cross-Lane View",
            "summary": "Where equity and options intelligence overlap.",
            "destination": "/research/overview",
            "items": top_mixed[:5],
        },
        {
            "key": "passed_over",
            "title": "Passed Over For Now",
            "summary": "Names that were watched but did not beat the current leaders.",
            "destination": "/research/rejections",
            "items": rejection_cards[:6],
        },
    ]


def build_dashboard_contract(username: str) -> Dict[str, Any]:
    modes = resolve_user_modes(username)
    spotlight = build_spotlight_feed_for_user(username)
    market_map = build_market_map()
    rejections = build_rejection_feed()

    payload = {
        "username": username,
        "mode_bar": _build_mode_bar(modes),
        "command_cards": _build_command_cards(spotlight, market_map, rejections),
        "sections": _build_sections(spotlight, market_map, rejections),
        "meta": {
            "rebuilt_at": now_iso(),
            "section_count": 6,
            "command_card_count": 3,
            "page_mode": modes.get("intelligence_mode", "hybrid"),
        },
    }

    _save_json(DASHBOARD_FILE, payload)
    return payload


def load_dashboard_contract() -> Dict[str, Any]:
    payload = _load_json(DASHBOARD_FILE, {})
    return payload if isinstance(payload, dict) else {}
