from typing import Dict, Any, List

from engine_v2.engine_helpers import build_watchlist, _save_json, now_iso

EQUITY_OUTPUT = "/content/SimpleeMrkTrade/data_v2/equity_universe.json"


def _build_reasoning(item: Dict[str, Any]) -> Dict[str, Any]:
    why_symbol = [
        f"Momentum is {item.get('momentum')}.",
        f"Trend is {item.get('trend', 'UNKNOWN')}.",
        f"Volume ratio is {item.get('volume_ratio', 1.0)}.",
    ]

    why_not = []
    if item.get("entry_quality") in {"EARLY", "USABLE"}:
        why_not.append("Entry quality is not yet elite.")
    if item.get("regime_fit") == "MIXED":
        why_not.append("Market fit is still mixed.")

    return {
        "why_symbol": why_symbol,
        "why_not": why_not,
    }


def _equity_candidate(item: Dict[str, Any], rank: int, spotlight: bool) -> Dict[str, Any]:
    return {
        "symbol": item["symbol"],
        "company_name": item["company_name"],
        "scanner": {
            "direction": item["direction"],
            "score": item["score"],
            "confidence": item["confidence"],
            "grade": item["grade"],
            "trend": item["trend"],
            "setup_type": item["setup_type"],
            "momentum": item["momentum"],
            "volume_quality": "STRONG" if item["volume_ratio"] >= 1.15 else "NORMAL",
            "regime_fit": item["regime_fit"],
            "entry_quality": item["entry_quality"],
            "time_sensitivity": item["time_sensitivity"],
            "setup_maturity": item["setup_maturity"],
            "price": item["price"],
        },
        "execution": {
            "eligible": True,
            "selected": True,
            "selection_rank": rank,
            "spotlight": spotlight,
        },
        "reasoning": _build_reasoning(item),
        "state": {
            "status_label": item["status_label"],
            "pressure_level": item["pressure_level"],
            "confidence_tier": item["confidence_tier"],
        },
        "timestamp": now_iso(),
    }


def build_equity_universe(
    watchlist_limit: int = 50,
    universe_limit: int = 220,
    selected_limit: int = 20,
    spotlight_limit: int = 5,
) -> Dict[str, Any]:
    watchlist = build_watchlist(limit=watchlist_limit, universe_limit=universe_limit)
    selected_rows = watchlist[:selected_limit]

    selected = []
    for idx, item in enumerate(selected_rows, start=1):
        selected.append(_equity_candidate(item, idx, idx <= spotlight_limit))

    spotlight = selected[:spotlight_limit]
    rejected: List[Dict[str, Any]] = []

    payload = {
        "selected": selected,
        "spotlight": spotlight,
        "rejected": rejected,
        "meta": {
            "rebuilt_at": now_iso(),
            "selected_count": len(selected),
            "spotlight_count": len(spotlight),
            "watchlist_limit": watchlist_limit,
            "universe_limit": universe_limit,
            "engine_type": "equity",
        },
    }

    _save_json(EQUITY_OUTPUT, payload)
    return payload
