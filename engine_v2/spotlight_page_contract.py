from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso
from engine_v2.mode_router import resolve_user_modes
from engine_v2.spotlight_builder import build_spotlight_feed_for_user
from engine_v2.rejection_builder import build_rejection_feed

SPOTLIGHT_PAGE_FILE = "/content/SimpleeMrkTrade/data_v2/spotlight_page_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_hero(spotlight: Dict[str, Any], modes: Dict[str, Any]) -> Dict[str, Any]:
    featured = _safe_list(spotlight.get("featured", []))
    lead = featured[0] if featured else {}

    return {
        "title": "Signals Spotlight",
        "summary": "The strongest live ideas the system wants to put in front of you first.",
        "mode": modes.get("intelligence_mode", "hybrid"),
        "lead_symbol": lead.get("symbol"),
        "lead_headline": lead.get("headline"),
        "lead_summary": lead.get("summary"),
        "destination": lead.get("destination", "/signals"),
    }


def _build_lane_sections(spotlight: Dict[str, Any]) -> List[Dict[str, Any]]:
    top_stocks = _safe_list(spotlight.get("top_stocks", []))
    top_options = _safe_list(spotlight.get("top_options", []))
    top_mixed = _safe_list(spotlight.get("top_mixed", []))

    return [
        {
            "key": "featured_now",
            "title": "Featured Now",
            "summary": "The system’s current first-call ideas.",
            "destination": "/spotlight",
            "items": _safe_list(spotlight.get("featured", []))[:10],
        },
        {
            "key": "options_lane",
            "title": "Options Lane",
            "summary": "The cleanest option-ready structures right now.",
            "destination": "/signals?lane=options",
            "items": top_options[:8],
        },
        {
            "key": "stocks_lane",
            "title": "Stocks Lane",
            "summary": "The strongest pure equity setups right now.",
            "destination": "/signals?lane=equity",
            "items": top_stocks[:8],
        },
        {
            "key": "cross_lane",
            "title": "Cross-Lane View",
            "summary": "Where the platform’s strongest ideas overlap across system modes.",
            "destination": "/research/overview",
            "items": top_mixed[:8],
        },
    ]


def _build_side_panels(rejections: Dict[str, Any]) -> List[Dict[str, Any]]:
    combined = _safe_list(rejections.get("combined", []))

    return [
        {
            "key": "why_not_now",
            "title": "Why Not These?",
            "summary": "Names that were watched but did not beat the current leaders.",
            "destination": "/research/rejections",
            "items": combined[:6],
        }
    ]


def build_spotlight_page_contract(username: str) -> Dict[str, Any]:
    modes = resolve_user_modes(username)
    spotlight = build_spotlight_feed_for_user(username)
    rejections = build_rejection_feed()

    payload = {
        "username": username,
        "hero": _build_hero(spotlight, modes),
        "lane_sections": _build_lane_sections(spotlight),
        "side_panels": _build_side_panels(rejections),
        "meta": {
            "rebuilt_at": now_iso(),
            "page_mode": modes.get("intelligence_mode", "hybrid"),
            "lane_section_count": 4,
            "side_panel_count": 1,
        },
    }

    _save_json(SPOTLIGHT_PAGE_FILE, payload)
    return payload


def load_spotlight_page_contract() -> Dict[str, Any]:
    payload = _load_json(SPOTLIGHT_PAGE_FILE, {})
    return payload if isinstance(payload, dict) else {}
