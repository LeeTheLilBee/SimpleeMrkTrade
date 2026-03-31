from typing import Dict, Any

from engine_v2.equity_engine import build_equity_universe
from engine_v2.options_engine import build_options_universe
from engine_v2.engine_helpers import _save_json, now_iso

HYBRID_OUTPUT = "/content/SimpleeMrkTrade/data_v2/hybrid_universe.json"


def build_hybrid_universe(
    watchlist_limit: int = 50,
    universe_limit: int = 220,
    selected_limit: int = 20,
    spotlight_limit: int = 5,
) -> Dict[str, Any]:
    equity = build_equity_universe(
        watchlist_limit=watchlist_limit,
        universe_limit=universe_limit,
        selected_limit=selected_limit,
        spotlight_limit=spotlight_limit,
    )

    options = build_options_universe(
        watchlist_limit=watchlist_limit,
        universe_limit=universe_limit,
        selected_limit=selected_limit,
        spotlight_limit=spotlight_limit,
    )

    equity_spotlight = equity.get("spotlight", [])[:spotlight_limit]
    options_spotlight = options.get("spotlight", [])[:spotlight_limit]

    mixed_spotlight = []
    seen = set()

    for item in options_spotlight + equity_spotlight:
        symbol = item.get("symbol")
        if symbol in seen:
            continue
        seen.add(symbol)
        mixed_spotlight.append(item)

    payload = {
        "equity_spotlight": equity_spotlight,
        "options_spotlight": options_spotlight,
        "mixed_spotlight": mixed_spotlight[:spotlight_limit],
        "meta": {
            "rebuilt_at": now_iso(),
            "engine_type": "hybrid",
            "watchlist_limit": watchlist_limit,
            "universe_limit": universe_limit,
            "selected_limit": selected_limit,
            "spotlight_limit": spotlight_limit,
            "equity_spotlight_count": len(equity_spotlight),
            "options_spotlight_count": len(options_spotlight),
            "mixed_spotlight_count": len(mixed_spotlight[:spotlight_limit]),
        },
    }

    _save_json(HYBRID_OUTPUT, payload)
    return payload
