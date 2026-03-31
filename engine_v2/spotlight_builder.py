from typing import Any, Dict, List

from engine_v2.mode_router import resolve_user_modes
from engine_v2.engine_helpers import _load_json, _save_json, now_iso
from engine_v2.equity_engine import build_equity_universe
from engine_v2.options_engine import build_options_universe
from engine_v2.hybrid_engine import build_hybrid_universe

EQUITY_FILE = "/content/SimpleeMrkTrade/data_v2/equity_universe.json"
OPTIONS_FILE = "/content/SimpleeMrkTrade/data_v2/options_universe.json"
HYBRID_FILE = "/content/SimpleeMrkTrade/data_v2/hybrid_universe.json"
SPOTLIGHT_FILE = "/content/SimpleeMrkTrade/data_v2/spotlight_feed.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _payload_has_cards(payload: Dict[str, Any], mode: str) -> bool:
    payload = _safe_dict(payload)
    if mode in {"equity", "options"}:
        return len(_safe_list(payload.get("spotlight", []))) > 0
    return len(_safe_list(payload.get("mixed_spotlight", []))) > 0


def _ensure_engine_inputs_ready() -> Dict[str, Dict[str, Any]]:
    equity_payload = _safe_dict(_load_json(EQUITY_FILE, {}))
    options_payload = _safe_dict(_load_json(OPTIONS_FILE, {}))
    hybrid_payload = _safe_dict(_load_json(HYBRID_FILE, {}))

    if not _payload_has_cards(equity_payload, "equity"):
        equity_payload = build_equity_universe(
            watchlist_limit=50,
            universe_limit=220,
            selected_limit=20,
            spotlight_limit=5,
        )

    if not _payload_has_cards(options_payload, "options"):
        options_payload = build_options_universe(
            watchlist_limit=50,
            universe_limit=220,
            selected_limit=20,
            spotlight_limit=5,
        )

    if not _payload_has_cards(hybrid_payload, "hybrid"):
        hybrid_payload = build_hybrid_universe(
            watchlist_limit=50,
            universe_limit=220,
            selected_limit=20,
            spotlight_limit=5,
        )

    return {
        "equity": _safe_dict(equity_payload),
        "options": _safe_dict(options_payload),
        "hybrid": _safe_dict(hybrid_payload),
    }


def _headline_for_item(item: Dict[str, Any]) -> str:
    symbol = str(item.get("symbol", "") or "").strip().upper()
    scanner = _safe_dict(item.get("scanner"))
    direction = str(scanner.get("direction", "CALL") or "CALL").strip().upper()
    setup_type = str(scanner.get("setup_type", "setup") or "setup").replace("_", " ").title()
    return f"{symbol} {direction} — {setup_type}" if symbol else "Spotlight Setup"


def _summary_for_equity_item(item: Dict[str, Any]) -> str:
    scanner = _safe_dict(item.get("scanner"))
    state = _safe_dict(item.get("state"))
    momentum = scanner.get("momentum", "N/A")
    trend = scanner.get("trend", "UNKNOWN")
    label = state.get("status_label", "Active")
    return f"{label}. Trend is {trend}. Momentum is {momentum}."


def _summary_for_options_item(item: Dict[str, Any]) -> str:
    scanner = _safe_dict(item.get("scanner"))
    options_plan = _safe_dict(item.get("options_plan"))
    strategy = options_plan.get("strategy_type", "options_structure")
    dte = options_plan.get("target_dte", "N/A")
    direction = scanner.get("direction", "CALL")
    return f"Options-ready {direction} idea using {strategy} with target DTE around {dte}."


def _why_lines(item: Dict[str, Any]) -> List[str]:
    reasoning = _safe_dict(item.get("reasoning"))
    lines = []

    for key in ["why_this_structure", "why_symbol", "why_not_single_leg"]:
        value = reasoning.get(key, [])
        if isinstance(value, list):
            lines.extend([str(x) for x in value if str(x).strip()])

    return lines[:4]


def _spotlight_card(item: Dict[str, Any], lane: str) -> Dict[str, Any]:
    card = {
        "symbol": item.get("symbol"),
        "company_name": item.get("company_name", item.get("symbol")),
        "lane": lane,
        "headline": _headline_for_item(item),
        "summary": "",
        "why_lines": _why_lines(item),
        "status_label": _safe_dict(item.get("state")).get("status_label", "Active"),
        "pressure_level": _safe_dict(item.get("state")).get("pressure_level", "medium"),
        "confidence_tier": _safe_dict(item.get("state")).get("confidence_tier", 3),
        "score": _safe_dict(item.get("scanner")).get("score", 0),
        "direction": _safe_dict(item.get("scanner")).get("direction", "CALL"),
        "destination": f"/signals/{item.get('symbol')}",
        "timestamp": item.get("timestamp", now_iso()),
    }

    if lane == "options":
        card["summary"] = _summary_for_options_item(item)
        card["structure"] = _safe_dict(item.get("options_plan")).get("strategy_type", "")
        card["target_dte"] = _safe_dict(item.get("options_plan")).get("target_dte", "")
    else:
        card["summary"] = _summary_for_equity_item(item)

    return card


def _dedupe_cards_by_lane(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    seen = set()

    for card in cards:
        symbol = str(card.get("symbol", "")).strip().upper()
        lane = str(card.get("lane", "")).strip().lower()
        key = (symbol, lane)
        if key in seen:
            continue
        seen.add(key)
        out.append(card)

    return out


def _dedupe_cards_by_symbol(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    seen = set()

    for card in cards:
        symbol = str(card.get("symbol", "")).strip().upper()
        if symbol in seen:
            continue
        seen.add(symbol)
        out.append(card)

    return out


def build_spotlight_feed_for_mode(intelligence_mode: str) -> Dict[str, Any]:
    intelligence_mode = str(intelligence_mode or "hybrid").strip().lower()

    sources = _ensure_engine_inputs_ready()
    equity_payload = sources["equity"]
    options_payload = sources["options"]
    hybrid_payload = sources["hybrid"]

    equity_spotlight = _safe_list(equity_payload.get("spotlight", []))
    options_spotlight = _safe_list(options_payload.get("spotlight", []))
    mixed_spotlight = _safe_list(hybrid_payload.get("mixed_spotlight", []))

    equity_cards = [_spotlight_card(item, "equity") for item in equity_spotlight if isinstance(item, dict)]
    options_cards = [_spotlight_card(item, "options") for item in options_spotlight if isinstance(item, dict)]

    if intelligence_mode == "equity":
        featured = equity_cards[:5]
    elif intelligence_mode == "options":
        featured = options_cards[:5]
    else:
        featured = _dedupe_cards_by_symbol(options_cards + equity_cards)[:10]

    mixed_cards = []
    for item in mixed_spotlight:
        if not isinstance(item, dict):
            continue
        lane = "options" if "options_plan" in item else "equity"
        mixed_cards.append(_spotlight_card(item, lane))

    payload = {
        "featured": featured,
        "top_stocks": _dedupe_cards_by_lane(equity_cards)[:5],
        "top_options": _dedupe_cards_by_lane(options_cards)[:5],
        "top_mixed": _dedupe_cards_by_symbol(mixed_cards)[:5],
        "what_changed": [],
        "meta": {
            "rebuilt_at": now_iso(),
            "page_mode": intelligence_mode,
            "featured_count": len(featured),
            "stocks_count": len(_dedupe_cards_by_lane(equity_cards)[:5]),
            "options_count": len(_dedupe_cards_by_lane(options_cards)[:5]),
            "mixed_count": len(_dedupe_cards_by_symbol(mixed_cards)[:5]),
        },
    }

    _save_json(SPOTLIGHT_FILE, payload)
    return payload


def build_spotlight_feed_for_user(username: str) -> Dict[str, Any]:
    modes = resolve_user_modes(username)
    intelligence_mode = modes.get("intelligence_mode", "hybrid")
    return build_spotlight_feed_for_mode(intelligence_mode)


def load_spotlight_feed() -> Dict[str, Any]:
    payload = _load_json(SPOTLIGHT_FILE, {})
    return payload if isinstance(payload, dict) else {}
