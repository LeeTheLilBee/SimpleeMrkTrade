from typing import Dict, Any, List

from engine_v2.engine_helpers import build_watchlist, _save_json, now_iso

OPTIONS_OUTPUT = "/content/SimpleeMrkTrade/data_v2/options_universe.json"


def _strategy_type(item: Dict[str, Any]) -> str:
    direction = item.get("direction", "CALL")
    volume_ratio = float(item.get("volume_ratio", 1.0) or 1.0)
    momentum = float(item.get("momentum", 0.0) or 0.0)

    if direction == "CALL":
        if volume_ratio >= 1.15 or momentum >= 0.06:
            return "call_debit_spread"
        return "single_call"

    if volume_ratio >= 1.15 or momentum <= -0.06:
        return "put_debit_spread"
    return "single_put"


def _target_dte(item: Dict[str, Any]) -> int:
    momentum = abs(float(item.get("momentum", 0.0) or 0.0))
    if momentum >= 0.08:
        return 14
    if momentum >= 0.04:
        return 21
    return 30


def _strike_style(item: Dict[str, Any]) -> str:
    strategy = _strategy_type(item)
    if "spread" in strategy:
        return "slightly_otm_spread"
    return "slightly_otm_single"


def _contract_quality_score(item: Dict[str, Any]) -> int:
    score = float(item.get("score", 0) or 0)
    volume_ratio = float(item.get("volume_ratio", 1.0) or 1.0)
    quality = 40 + int(min(35, abs(score) / 5)) + int(min(20, volume_ratio * 10))
    return max(0, min(100, quality))


def _liquidity_score(item: Dict[str, Any]) -> int:
    avg_volume = float(item.get("avg_volume", 0) or 0)
    if avg_volume >= 20_000_000:
        return 90
    if avg_volume >= 10_000_000:
        return 80
    if avg_volume >= 5_000_000:
        return 70
    if avg_volume >= 2_000_000:
        return 60
    return 45


def _spread_score(item: Dict[str, Any]) -> int:
    volume_ratio = float(item.get("volume_ratio", 1.0) or 1.0)
    if volume_ratio >= 1.10:
        return 74
    if volume_ratio >= 0.95:
        return 66
    return 55


def _premium_efficiency_score(item: Dict[str, Any]) -> int:
    strategy = _strategy_type(item)
    momentum = abs(float(item.get("momentum", 0.0) or 0.0))
    base = 72 if "spread" in strategy else 64
    if momentum >= 0.07:
        base += 8
    elif momentum >= 0.04:
        base += 4
    return max(0, min(100, base))


def _time_decay_risk(item: Dict[str, Any]) -> str:
    dte = _target_dte(item)
    if dte <= 14:
        return "HIGH"
    if dte <= 21:
        return "MODERATE"
    return "LOW"


def _expected_move_fit(item: Dict[str, Any]) -> str:
    momentum = abs(float(item.get("momentum", 0.0) or 0.0))
    if momentum >= 0.06:
        return "GOOD"
    if momentum >= 0.03:
        return "USABLE"
    return "MIXED"


def _option_ready(item: Dict[str, Any]) -> bool:
    return (
        item.get("confidence", "LOW") in {"HIGH", "MEDIUM"}
        and item.get("entry_quality", "EARLY") in {"GREAT", "GOOD", "USABLE"}
    )


def _reasoning(item: Dict[str, Any]) -> Dict[str, Any]:
    strategy = _strategy_type(item)
    why_this_structure = [
        f"Underlying direction is {item.get('direction', 'CALL')}.",
        f"Strategy selected: {strategy}.",
        f"Time sensitivity is {item.get('time_sensitivity', 'WATCH')}.",
    ]

    why_not_single_leg = []
    if "spread" in strategy:
        why_not_single_leg.append("Spread structure improves premium efficiency.")

    why_not = []
    if not _option_ready(item):
        why_not.append("Underlying setup is not option-ready enough yet.")

    return {
        "why_this_structure": why_this_structure,
        "why_not_single_leg": why_not_single_leg,
        "why_not": why_not,
    }


def _options_candidate(item: Dict[str, Any], rank: int, spotlight: bool) -> Dict[str, Any]:
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
            "price": item["price"],
        },
        "options_plan": {
            "is_option_ready": _option_ready(item),
            "strategy_type": _strategy_type(item),
            "target_dte": _target_dte(item),
            "expiry_class": "near_monthly",
            "strike_style": _strike_style(item),
            "contract_quality_score": _contract_quality_score(item),
            "liquidity_score": _liquidity_score(item),
            "spread_score": _spread_score(item),
            "premium_efficiency_score": _premium_efficiency_score(item),
            "time_decay_risk": _time_decay_risk(item),
            "expected_move_fit": _expected_move_fit(item),
            "iv_context": "ELEVATED" if item.get("volume_ratio", 1.0) >= 1.15 else "NORMAL",
        },
        "execution": {
            "eligible": True,
            "selected": True,
            "selection_rank": rank,
            "spotlight": spotlight,
        },
        "reasoning": _reasoning(item),
        "state": {
            "status_label": "Option-Ready" if _option_ready(item) else "Needs Better Structure",
            "pressure_level": item["pressure_level"],
            "confidence_tier": item["confidence_tier"],
        },
        "timestamp": now_iso(),
    }


def build_options_universe(
    watchlist_limit: int = 50,
    universe_limit: int = 220,
    selected_limit: int = 20,
    spotlight_limit: int = 5,
) -> Dict[str, Any]:
    watchlist = build_watchlist(limit=watchlist_limit, universe_limit=universe_limit)
    option_ready_rows = [row for row in watchlist if _option_ready(row)]
    selected_rows = option_ready_rows[:selected_limit]

    selected = []
    for idx, item in enumerate(selected_rows, start=1):
        selected.append(_options_candidate(item, idx, idx <= spotlight_limit))

    spotlight = selected[:spotlight_limit]

    rejected: List[Dict[str, Any]] = []
    selected_symbols = {item["symbol"] for item in selected_rows}

    for row in watchlist:
        if row["symbol"] in selected_symbols:
            continue
        rejected.append({
            "symbol": row["symbol"],
            "company_name": row["company_name"],
            "reason": "Not option-ready enough for current selection pass.",
            "timestamp": now_iso(),
        })

    payload = {
        "selected": selected,
        "spotlight": spotlight,
        "rejected": rejected[:20],
        "meta": {
            "rebuilt_at": now_iso(),
            "selected_count": len(selected),
            "spotlight_count": len(spotlight),
            "watchlist_limit": watchlist_limit,
            "universe_limit": universe_limit,
            "engine_type": "options",
        },
    }

    _save_json(OPTIONS_OUTPUT, payload)
    return payload
