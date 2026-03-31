from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso

MARKET_MAP_FILE = "/content/SimpleeMrkTrade/data_v2/market_map.json"
INTERACTION_FILE = "/content/SimpleeMrkTrade/data_v2/market_map_interaction_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_hover_card(tile: Dict[str, Any]) -> Dict[str, Any]:
    tile = _safe_dict(tile)
    return {
        "symbol": tile.get("symbol"),
        "headline": f"{tile.get('symbol')} {tile.get('direction', 'CALL')}",
        "summary": f"{tile.get('status_label', 'Active')} | {tile.get('setup_type', 'developing').replace('_', ' ').title()}",
        "pressure_level": tile.get("pressure_level", "medium"),
        "glow_intensity": tile.get("glow_intensity", 50),
        "destination": tile.get("destination", "/signals"),
    }


def _build_tile_action(tile: Dict[str, Any]) -> Dict[str, Any]:
    tile = _safe_dict(tile)
    symbol = str(tile.get("symbol", "") or "").upper()

    return {
        "symbol": symbol,
        "primary_action": {
            "label": "Open Symbol",
            "destination": tile.get("destination", f"/signals/{symbol}"),
        },
        "secondary_actions": [
            {
                "label": "Open Spotlight",
                "destination": "/spotlight",
            },
            {
                "label": "Open Signals Lane",
                "destination": f"/signals/{symbol}",
            },
        ],
    }


def build_market_map_interaction_contract() -> Dict[str, Any]:
    market_map = _safe_dict(_load_json(MARKET_MAP_FILE, {}))
    tiles = _safe_list(market_map.get("tiles", []))

    preview_tiles = tiles[:12]

    payload = {
        "hover_cards": [_build_hover_card(tile) for tile in preview_tiles if isinstance(tile, dict)],
        "tile_actions": [_build_tile_action(tile) for tile in preview_tiles if isinstance(tile, dict)],
        "interaction_rules": {
            "default_behavior": "hover_reveal",
            "click_behavior": "open_symbol_page",
            "secondary_behavior": "route_to_related_area",
            "calm_mode_behavior": "reduce_hover_motion",
        },
        "meta": {
            "rebuilt_at": now_iso(),
            "preview_tile_count": len(preview_tiles),
        },
    }

    _save_json(INTERACTION_FILE, payload)
    return payload


def load_market_map_interaction_contract() -> Dict[str, Any]:
    payload = _load_json(INTERACTION_FILE, {})
    return payload if isinstance(payload, dict) else {}
