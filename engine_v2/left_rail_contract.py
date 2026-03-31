from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso
from engine_v2.mode_router import resolve_user_modes

LEFT_RAIL_FILE = "/content/SimpleeMrkTrade/data_v2/left_rail_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _section(key: str, label: str, icon: str, destination: str, children: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "icon": icon,
        "destination": destination,
        "children": children or [],
    }


def build_left_rail_contract(username: str) -> Dict[str, Any]:
    modes = resolve_user_modes(username)

    sections = [
        _section("dashboard", "Dashboard", "layout-dashboard", "/dashboard"),
        _section("spotlight", "Spotlight", "star", "/spotlight"),
        _section("signals", "Signals", "radar", "/signals", children=[
            {"key": "signals_options", "label": "Options Lane", "destination": "/signals?lane=options"},
            {"key": "signals_equity", "label": "Stocks Lane", "destination": "/signals?lane=equity"},
        ]),
        _section("market_map", "Market Map", "map", "/market-map"),
        _section("research", "Research", "book-open", "/research/overview", children=[
            {"key": "research_rejections", "label": "Passed Over", "destination": "/research/rejections"},
            {"key": "research_overview", "label": "Overview", "destination": "/research/overview"},
        ]),
        _section("positions", "Positions", "briefcase", "/positions"),
        _section("settings", "Settings", "sliders-horizontal", "/settings"),
    ]

    payload = {
        "username": username,
        "collapsed_default": True,
        "active_mode": {
            "intelligence_mode": modes.get("intelligence_mode", "hybrid"),
            "control_mode": modes.get("control_mode", "manual"),
            "auto_scope": modes.get("auto_scope", "both"),
            "experience_mode": modes.get("experience_mode", "balanced"),
        },
        "sections": sections,
        "meta": {
            "rebuilt_at": now_iso(),
            "section_count": len(sections),
        },
    }

    _save_json(LEFT_RAIL_FILE, payload)
    return payload


def load_left_rail_contract() -> Dict[str, Any]:
    payload = _load_json(LEFT_RAIL_FILE, {})
    return payload if isinstance(payload, dict) else {}
