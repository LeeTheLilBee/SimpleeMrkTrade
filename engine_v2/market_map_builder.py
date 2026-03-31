from typing import Any, Dict, List

from engine_v2.engine_helpers import _load_json, _save_json, now_iso

EQUITY_FILE = "/content/SimpleeMrkTrade/data_v2/equity_universe.json"
OPTIONS_FILE = "/content/SimpleeMrkTrade/data_v2/options_universe.json"
MAP_FILE = "/content/SimpleeMrkTrade/data_v2/market_map.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _bucket_from_symbol(symbol: str) -> str:
    symbol = str(symbol or "").upper()

    tech = {"NVDA", "AMD", "MRVL", "AVGO", "QCOM", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "PLTR", "PANW", "CRWD", "NOW", "ORCL", "ADBE"}
    energy = {"XOM", "CVX", "COP", "EOG", "OXY", "DVN", "HAL", "SLB", "USO", "XLE"}
    finance = {"JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA", "COIN", "HOOD"}
    healthcare = {"LLY", "UNH", "JNJ", "MRK", "ABBV", "PFE", "TMO", "DHR", "ISRG", "VRTX", "XLV"}
    industrials = {"CAT", "GE", "RTX", "LMT", "BA", "UPS", "FDX", "XLI"}
    consumer = {"WMT", "COST", "PG", "HD", "LOW", "TGT", "MCD", "SBUX", "NKE", "DIS", "NFLX", "XLY", "XLP"}
    real_assets = {"GLD", "SLV", "TLT", "LQD", "HYG", "XLB", "XLRE", "AMT", "PLD", "EQIX"}

    if symbol in tech:
        return "technology"
    if symbol in energy:
        return "energy"
    if symbol in finance:
        return "finance"
    if symbol in healthcare:
        return "healthcare"
    if symbol in industrials:
        return "industrials"
    if symbol in consumer:
        return "consumer"
    if symbol in real_assets:
        return "real_assets"
    return "general"


def _glow_intensity(pressure_level: str, confidence_tier: int) -> int:
    pressure_level = str(pressure_level or "medium").lower()
    confidence_tier = int(confidence_tier or 3)

    pressure_base = {
        "low": 35,
        "medium": 60,
        "high": 85,
    }.get(pressure_level, 50)

    tier_bonus = {
        1: 10,
        2: 5,
        3: 0,
    }.get(confidence_tier, 0)

    return min(100, pressure_base + tier_bonus)


def _size_score(score: float) -> int:
    try:
        score = float(score)
    except Exception:
        score = 0.0

    if score >= 300:
        return 3
    if score >= 180:
        return 2
    return 1


def _tile_from_item(item: Dict[str, Any], lane: str) -> Dict[str, Any]:
    scanner = _safe_dict(item.get("scanner"))
    state = _safe_dict(item.get("state"))
    options_plan = _safe_dict(item.get("options_plan"))

    symbol = str(item.get("symbol", "") or "").upper()
    score = scanner.get("score", 0)
    pressure_level = state.get("pressure_level", "medium")
    confidence_tier = state.get("confidence_tier", 3)

    tile = {
        "symbol": symbol,
        "company_name": item.get("company_name", symbol),
        "lane": lane,
        "bucket": _bucket_from_symbol(symbol),
        "direction": scanner.get("direction", "CALL"),
        "trend": scanner.get("trend", "SIDEWAYS"),
        "setup_type": scanner.get("setup_type", "developing"),
        "status_label": state.get("status_label", "Active"),
        "pressure_level": pressure_level,
        "confidence_tier": confidence_tier,
        "glow_intensity": _glow_intensity(pressure_level, confidence_tier),
        "size_score": _size_score(score),
        "score": score,
        "price": scanner.get("price"),
        "destination": f"/signals/{symbol}",
        "timestamp": item.get("timestamp", now_iso()),
    }

    if lane == "options":
        tile["structure"] = options_plan.get("strategy_type", "")
        tile["target_dte"] = options_plan.get("target_dte", "")
        tile["option_ready"] = options_plan.get("is_option_ready", False)

    return tile


def _dedupe_tiles(tiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    seen = set()

    for tile in tiles:
        symbol = str(tile.get("symbol", "")).upper()
        lane = str(tile.get("lane", "")).lower()
        key = (symbol, lane)
        if key in seen:
            continue
        seen.add(key)
        out.append(tile)

    return out


def _group_tiles_by_bucket(tiles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for tile in tiles:
        bucket = str(tile.get("bucket", "general"))
        grouped.setdefault(bucket, []).append(tile)

    for bucket in grouped:
        grouped[bucket] = sorted(
            grouped[bucket],
            key=lambda x: (
                x.get("size_score", 1),
                x.get("glow_intensity", 0),
                x.get("score", 0),
            ),
            reverse=True,
        )

    return grouped


def build_market_map() -> Dict[str, Any]:
    equity_payload = _safe_dict(_load_json(EQUITY_FILE, {}))
    options_payload = _safe_dict(_load_json(OPTIONS_FILE, {}))

    equity_selected = _safe_list(equity_payload.get("selected", []))
    options_selected = _safe_list(options_payload.get("selected", []))

    equity_tiles = [_tile_from_item(item, "equity") for item in equity_selected if isinstance(item, dict)]
    options_tiles = [_tile_from_item(item, "options") for item in options_selected if isinstance(item, dict)]

    all_tiles = _dedupe_tiles(options_tiles + equity_tiles)
    grouped = _group_tiles_by_bucket(all_tiles)

    payload = {
        "tiles": all_tiles,
        "grouped_tiles": grouped,
        "legend": {
            "pressure_levels": ["low", "medium", "high"],
            "lanes": ["equity", "options"],
            "size_scores": [1, 2, 3],
        },
        "meta": {
            "rebuilt_at": now_iso(),
            "tile_count": len(all_tiles),
            "bucket_count": len(grouped),
            "options_tile_count": len(options_tiles),
            "equity_tile_count": len(equity_tiles),
        },
    }

    _save_json(MAP_FILE, payload)
    return payload


def load_market_map() -> Dict[str, Any]:
    payload = _load_json(MAP_FILE, {})
    return payload if isinstance(payload, dict) else {}
