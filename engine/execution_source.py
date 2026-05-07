from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# ============================================================
# PURPOSE
# ============================================================
# This file is the safety bridge between data/execution_universe.json
# and process_signals().
#
# Critical rule:
#   Candidate rows may carry stale, synthetic, or corrupted prices.
#   Before a candidate is allowed into process_signals(), this layer
#   attempts to refresh and validate the underlying stock price.
#
# This prevents bad upstream prices from poisoning:
#   - option moneyness
#   - option strike distance scoring
#   - stop/target defaults
#   - stock fallback sizing
#   - candidate display
#   - reentry comparisons


EXECUTION_UNIVERSE_FILE = "data/execution_universe.json"


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)

        if hasattr(value, "iloc"):
            try:
                value = value.iloc[-1]
            except Exception:
                value = value.iloc[0]

        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass

        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)

        if hasattr(value, "iloc"):
            try:
                value = value.iloc[-1]
            except Exception:
                value = value.iloc[0]

        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass

        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def load_json(path: str, default: Any) -> Any:
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ============================================================
# WATCHLIST FILTER
# ============================================================

def _watchlist_to_symbol_set(watchlist: Any) -> Optional[Set[str]]:
    if not isinstance(watchlist, list) or not watchlist:
        return None

    out: Set[str] = set()

    for item in watchlist:
        if isinstance(item, dict):
            symbol = _norm_symbol(item.get("symbol", ""))
        else:
            symbol = _norm_symbol(item)

        if symbol:
            out.add(symbol)

    return out if out else None


# ============================================================
# PRICE EXTRACTION / VALIDATION
# ============================================================

def _stored_price_candidates(row: Dict[str, Any]) -> List[Tuple[str, float]]:
    row = _safe_dict(row)

    ordered_fields = [
        "underlying_price",
        "stock_price",
        "market_price",
        "latest_price",
        "last_price",
        "regular_market_price",
        "current_price",
        "price",
        "entry",
        "close",
        "fill_price",
        "requested_price",
    ]

    out: List[Tuple[str, float]] = []

    for field in ordered_fields:
        value = _safe_float(row.get(field), 0.0)
        if value > 0:
            out.append((field, value))

    return out


def _first_stored_price(row: Dict[str, Any]) -> Tuple[float, str]:
    for field, price in _stored_price_candidates(row):
        if price > 0:
            return round(price, 4), field

    return 0.0, ""


def _extract_last_close_from_df(df: Any) -> float:
    try:
        if df is None or getattr(df, "empty", True):
            return 0.0

        columns = getattr(df, "columns", [])

        for field in ["Close", "Adj Close", "close", "adj_close"]:
            try:
                if field in columns:
                    series = df[field].dropna()
                    if len(series) > 0:
                        value = _safe_float(series.iloc[-1], 0.0)
                        if value > 0:
                            return round(value, 4)
            except Exception:
                continue

        try:
            last_row = df.dropna().iloc[-1]
            for field in ["Close", "Adj Close", "close", "adj_close"]:
                value = _safe_float(last_row.get(field), 0.0)
                if value > 0:
                    return round(value, 4)
        except Exception:
            pass

    except Exception:
        pass

    return 0.0


def _fresh_underlying_price(symbol: str) -> Tuple[float, str]:
    clean_symbol = _norm_symbol(symbol)
    if not clean_symbol:
        return 0.0, "missing_symbol"

    try:
        from engine.data_utils import safe_download

        df = safe_download(
            clean_symbol,
            period="5d",
            auto_adjust=True,
            progress=False,
        )

        price = _extract_last_close_from_df(df)

        if price > 0:
            return price, "safe_download_close"

        return 0.0, "safe_download_no_price"

    except Exception as exc:
        return 0.0, f"safe_download_failed:{exc}"


def _price_delta_pct(a: float, b: float) -> float:
    a = _safe_float(a, 0.0)
    b = _safe_float(b, 0.0)

    if a <= 0 or b <= 0:
        return 0.0

    base = min(a, b)
    if base <= 0:
        return 0.0

    return abs(a - b) / base


def _resolve_underlying_price(row: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    row = _safe_dict(row)
    symbol = _norm_symbol(symbol)

    stored_price, stored_source = _first_stored_price(row)
    fresh_price, fresh_source = _fresh_underlying_price(symbol)

    delta_pct = _price_delta_pct(stored_price, fresh_price)

    # Fresh market data wins when available.
    if fresh_price > 0:
        if stored_price > 0 and delta_pct >= 0.25:
            return {
                "price": round(fresh_price, 4),
                "price_source": fresh_source,
                "stored_price": round(stored_price, 4),
                "stored_price_source": stored_source,
                "fresh_price": round(fresh_price, 4),
                "fresh_price_source": fresh_source,
                "price_delta_pct": round(delta_pct, 4),
                "price_status": "fresh_price_used_stored_price_suspicious",
                "price_warning": (
                    f"Stored price {stored_price} from {stored_source} differed from "
                    f"fresh price {fresh_price} by {round(delta_pct * 100, 2)}%."
                ),
            }

        return {
            "price": round(fresh_price, 4),
            "price_source": fresh_source,
            "stored_price": round(stored_price, 4),
            "stored_price_source": stored_source,
            "fresh_price": round(fresh_price, 4),
            "fresh_price_source": fresh_source,
            "price_delta_pct": round(delta_pct, 4),
            "price_status": "fresh_price_used",
            "price_warning": "",
        }

    # If no fresh price is available, fall back to stored price but mark it.
    if stored_price > 0:
        return {
            "price": round(stored_price, 4),
            "price_source": stored_source,
            "stored_price": round(stored_price, 4),
            "stored_price_source": stored_source,
            "fresh_price": 0.0,
            "fresh_price_source": fresh_source,
            "price_delta_pct": 0.0,
            "price_status": "stored_price_used_no_fresh_price",
            "price_warning": f"Fresh price unavailable; using stored {stored_source}.",
        }

    return {
        "price": 0.0,
        "price_source": "",
        "stored_price": 0.0,
        "stored_price_source": "",
        "fresh_price": 0.0,
        "fresh_price_source": fresh_source,
        "price_delta_pct": 0.0,
        "price_status": "no_price_available",
        "price_warning": "No usable underlying price available.",
    }


# ============================================================
# CANDIDATE QUALITY / SORTING
# ============================================================

def _confidence_rank(value: Any) -> int:
    confidence = _safe_str(value, "LOW").upper()
    mapping = {
        "STRONG": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "UNKNOWN": 0,
    }
    return mapping.get(confidence, 0)


def _candidate_sort_key(row: Dict[str, Any]) -> tuple:
    row = _safe_dict(row)

    return (
        _safe_float(row.get("fused_score", row.get("score", 0.0)), 0.0),
        _confidence_rank(row.get("confidence", "LOW")),
        _safe_float(row.get("score", 0.0), 0.0),
        _safe_float(row.get("base_score", 0.0), 0.0),
        _safe_float(row.get("readiness_score", 0.0), 0.0),
        _safe_float(row.get("promotion_score", 0.0), 0.0),
    )


def _normalize_strategy(value: Any) -> str:
    strategy = _safe_str(value, "CALL").upper()

    if strategy in {"CALL", "PUT", "NO_TRADE"}:
        return strategy

    if strategy in {"LONG", "BUY", "BULLISH"}:
        return "CALL"

    if strategy in {"SHORT", "SELL", "BEARISH"}:
        return "PUT"

    return "CALL"


def _default_stop(price: float, strategy: str) -> float:
    price = _safe_float(price, 0.0)
    strategy = _normalize_strategy(strategy)

    if price <= 0:
        return 0.0

    if strategy == "PUT":
        return round(price * 1.03, 4)

    return round(price * 0.97, 4)


def _default_target(price: float, strategy: str) -> float:
    price = _safe_float(price, 0.0)
    strategy = _normalize_strategy(strategy)

    if price <= 0:
        return 0.0

    if strategy == "PUT":
        return round(price * 0.90, 4)

    return round(price * 1.10, 4)


# ============================================================
# OPTION CHAIN PRICE CONTEXT
# ============================================================

def _normalize_option_chain(option_chain: Any, underlying_price: float) -> List[Dict[str, Any]]:
    rows = _safe_list(option_chain)
    normalized: List[Dict[str, Any]] = []

    for raw in rows:
        if not isinstance(raw, dict):
            continue

        option = dict(raw)
        option.setdefault("underlying_price", round(_safe_float(underlying_price, 0.0), 4))
        option.setdefault("stock_price", round(_safe_float(underlying_price, 0.0), 4))
        option.setdefault("monitoring_mode", "OPTION_PREMIUM")

        normalized.append(option)

    return normalized


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_candidate(candidate: Dict[str, Any], *, debug: bool = False) -> Dict[str, Any]:
    row = dict(candidate or {})
    symbol = _norm_symbol(row.get("symbol", ""))

    if not symbol:
        return {}

    price_resolution = _resolve_underlying_price(row, symbol)
    current_price = _safe_float(price_resolution.get("price"), 0.0)

    if current_price <= 0:
        if debug:
            print("EXECUTION SOURCE PRICE DROP:", {
                "symbol": symbol,
                "reason": price_resolution.get("price_status"),
                "fresh_source": price_resolution.get("fresh_price_source"),
                "stored_source": price_resolution.get("stored_price_source"),
            })
        return {}

    score = _safe_float(
        row.get("score", row.get("latest_score", row.get("fused_score", 0.0))),
        0.0,
    )
    fused_score = _safe_float(row.get("fused_score", score), score)
    base_score = _safe_float(row.get("base_score", score), score)

    confidence = _safe_str(
        row.get("confidence", row.get("latest_confidence", "LOW")),
        "LOW",
    ).upper()

    strategy = _normalize_strategy(row.get("strategy", "CALL"))

    company_name = _safe_str(
        row.get("company_name", row.get("company", symbol)),
        symbol,
    )

    entry = round(_safe_float(row.get("entry", current_price), current_price), 4)

    # If entry is suspiciously far from refreshed underlying price, reset entry too.
    entry_delta = _price_delta_pct(entry, current_price)
    if entry <= 0 or entry_delta >= 0.25:
        entry = round(current_price, 4)

    stop_existing = _safe_float(row.get("stop"), 0.0)
    target_existing = _safe_float(row.get("target"), 0.0)

    stop = round(
        stop_existing
        if stop_existing > 0 and _price_delta_pct(stop_existing, current_price) < 0.50
        else _default_stop(current_price, strategy),
        4,
    )

    target = round(
        target_existing
        if target_existing > 0 and _price_delta_pct(target_existing, current_price) < 0.75
        else _default_target(current_price, strategy),
        4,
    )

    normalized = dict(row)

    normalized["symbol"] = symbol
    normalized["company_name"] = company_name
    normalized["strategy"] = strategy

    # Canonical underlying fields for candidates entering process_signals.
    normalized["price"] = round(current_price, 4)
    normalized["current_price"] = round(current_price, 4)
    normalized["underlying_price"] = round(current_price, 4)
    normalized["stock_price"] = round(current_price, 4)
    normalized["market_price"] = round(current_price, 4)
    normalized["entry"] = entry
    normalized["requested_price"] = round(current_price, 4)

    normalized["stop"] = stop
    normalized["target"] = target

    normalized["price_audit"] = price_resolution
    normalized["price_source"] = price_resolution.get("price_source", "")
    normalized["price_status"] = price_resolution.get("price_status", "")
    normalized["price_warning"] = price_resolution.get("price_warning", "")
    normalized["stored_price"] = price_resolution.get("stored_price", 0.0)
    normalized["stored_price_source"] = price_resolution.get("stored_price_source", "")
    normalized["fresh_price"] = price_resolution.get("fresh_price", 0.0)
    normalized["fresh_price_source"] = price_resolution.get("fresh_price_source", "")
    normalized["price_delta_pct"] = price_resolution.get("price_delta_pct", 0.0)

    normalized["trend"] = _safe_str(row.get("trend", "UPTREND"), "UPTREND")
    normalized["rsi"] = _safe_float(row.get("rsi", 55.0), 55.0)
    normalized["atr"] = _safe_float(row.get("atr", 2.0), 2.0)
    normalized["sector"] = _safe_str(row.get("sector", "General"), "General")
    normalized["mode"] = _safe_str(row.get("mode", "AGGRESSIVE_ROTATION"), "AGGRESSIVE_ROTATION")
    normalized["volatility_state"] = _safe_str(row.get("volatility_state", "NORMAL"), "NORMAL")
    normalized["source"] = _safe_str(row.get("source", "execution_universe"), "execution_universe")

    normalized["score"] = round(score, 4)
    normalized["fused_score"] = round(fused_score, 4)
    normalized["base_score"] = round(base_score, 4)
    normalized["confidence"] = confidence

    normalized["option_chain"] = _normalize_option_chain(
        row.get("option_chain"),
        current_price,
    )
    normalized["option"] = _safe_dict(row.get("option"))
    normalized["v2"] = _safe_dict(row.get("v2"))
    normalized["governor"] = _safe_dict(row.get("governor"))
    normalized["mode_context"] = _safe_dict(row.get("mode_context"))

    normalized["research_approved"] = _safe_bool(row.get("research_approved"), False)
    normalized["execution_ready"] = _safe_bool(row.get("execution_ready"), False)
    normalized["selected_for_execution"] = _safe_bool(row.get("selected_for_execution"), False)

    normalized["vehicle_selected"] = _safe_str(
        row.get("vehicle_selected", "RESEARCH_ONLY"),
        "RESEARCH_ONLY",
    ).upper()
    normalized["vehicle_reason"] = _safe_str(row.get("vehicle_reason", ""), "")
    normalized["capital_required"] = round(_safe_float(row.get("capital_required", 0.0), 0.0), 4)
    normalized["minimum_trade_cost"] = round(_safe_float(row.get("minimum_trade_cost", 0.0), 0.0), 4)

    normalized["readiness_score"] = _safe_float(row.get("readiness_score", 0.0), 0.0)
    normalized["promotion_score"] = _safe_float(row.get("promotion_score", 0.0), 0.0)
    normalized["rebuild_pressure"] = _safe_float(row.get("rebuild_pressure", 0.0), 0.0)
    normalized["execution_quality"] = _safe_float(row.get("execution_quality", 0.0), 0.0)

    normalized["setup_type"] = _safe_str(row.get("setup_type", ""), "")
    normalized["setup_family"] = _safe_str(row.get("setup_family", ""), "")
    normalized["entry_quality"] = _safe_str(row.get("entry_quality", ""), "")
    normalized["decision_reason"] = _safe_str(
        row.get("decision_reason", row.get("final_reason", "")),
        "",
    )
    normalized["final_reason"] = _safe_str(row.get("final_reason", ""), "")
    normalized["blocked_at"] = _safe_str(row.get("blocked_at", ""), "")

    normalized["why"] = _safe_list(row.get("why"))
    normalized["supports"] = _safe_list(row.get("supports"))
    normalized["blockers"] = _safe_list(row.get("blockers"))
    normalized["rejection_analysis"] = _safe_list(row.get("rejection_analysis"))
    normalized["option_explanation"] = _safe_list(row.get("option_explanation"))
    normalized["learning_notes"] = _safe_list(row.get("learning_notes"))

    normalized["v2_regime_alignment"] = _safe_str(
        row.get("v2_regime_alignment", normalized["v2"].get("regime_alignment", "")),
        "",
    )
    normalized["v2_signal_strength"] = round(
        _safe_float(row.get("v2_signal_strength", normalized["v2"].get("signal_strength", 0.0)), 0.0),
        4,
    )
    normalized["v2_conviction_adjustment"] = round(
        _safe_float(row.get("v2_conviction_adjustment", normalized["v2"].get("conviction_adjustment", 0.0)), 0.0),
        4,
    )
    normalized["v2_vehicle_bias"] = _safe_str(
        row.get("v2_vehicle_bias", normalized["v2"].get("vehicle_bias", "")),
        "",
    ).upper()
    normalized["v2_thesis"] = _safe_str(
        row.get("v2_thesis", normalized["v2"].get("thesis", "")),
        "",
    )
    normalized["v2_notes"] = _safe_list(
        row.get("v2_notes", normalized["v2"].get("notes", []))
    )
    normalized["v2_risk_flags"] = _safe_list(
        row.get("v2_risk_flags", normalized["v2"].get("risk_flags", []))
    )

    normalized["execution_source_checked_at"] = _now_iso()

    if debug and normalized.get("price_warning"):
        print("EXECUTION SOURCE PRICE WARNING:", {
            "symbol": symbol,
            "warning": normalized.get("price_warning"),
            "used_price": normalized.get("price"),
            "stored_price": normalized.get("stored_price"),
            "stored_source": normalized.get("stored_price_source"),
            "fresh_price": normalized.get("fresh_price"),
            "fresh_source": normalized.get("fresh_price_source"),
            "delta_pct": normalized.get("price_delta_pct"),
        })

    return normalized


# ============================================================
# DEDUPE
# ============================================================

def _dedupe_by_symbol(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best_by_symbol: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        symbol = _norm_symbol(row.get("symbol", ""))
        if not symbol:
            continue

        current_best = best_by_symbol.get(symbol)

        if current_best is None:
            best_by_symbol[symbol] = row
            continue

        if _candidate_sort_key(row) > _candidate_sort_key(current_best):
            best_by_symbol[symbol] = row

    deduped = list(best_by_symbol.values())
    deduped.sort(key=_candidate_sort_key, reverse=True)
    return deduped


# ============================================================
# EXECUTION CANDIDATE ACCESSOR
# ============================================================

def get_execution_candidates(
    force_rebuild: bool = True,
    watchlist: Optional[List[Any]] = None,
    limit: int = 50,
    spotlight_limit: int = 5,
    watchlist_limit: int = 50,
    universe_limit: int = 220,
    debug: bool = True,
    *args,
    **kwargs,
) -> List[Dict[str, Any]]:
    del args, kwargs

    limit = max(1, _safe_int(limit, 50))
    spotlight_limit = max(1, _safe_int(spotlight_limit, 5))
    watchlist_limit = max(limit, _safe_int(watchlist_limit, 50))
    universe_limit = max(watchlist_limit, _safe_int(universe_limit, 220))

    if force_rebuild:
        rebuilt = False

        try:
            from engine.execution_universe_builder import build_execution_universe

            build_execution_universe(
                limit=limit,
                spotlight_limit=spotlight_limit,
                watchlist_limit=watchlist_limit,
                universe_limit=universe_limit,
            )
            rebuilt = True

        except Exception as exc:
            if debug:
                print("[EXECUTION_UNIVERSE_REBUILD_SKIPPED]", {
                    "reason": "builder_failed_or_unavailable",
                    "error": str(exc),
                })

        if not rebuilt and debug:
            print("[EXECUTION_UNIVERSE_REBUILD_SKIPPED] no compatible builder found")

    universe = load_json(EXECUTION_UNIVERSE_FILE, {})
    universe = _safe_dict(universe)

    selected = _safe_list(universe.get("selected", []))
    watchlist_set = _watchlist_to_symbol_set(watchlist)

    normalized: List[Dict[str, Any]] = []

    for item in selected:
        if not isinstance(item, dict):
            continue

        candidate = _normalize_candidate(item, debug=debug)
        if not candidate:
            continue

        symbol = candidate["symbol"]

        if watchlist_set is not None and symbol not in watchlist_set:
            continue

        normalized.append(candidate)

    normalized = _dedupe_by_symbol(normalized)
    final_rows = normalized[:limit]

    if debug:
        spotlight = _safe_list(universe.get("spotlight", []))

        print("Execution candidates:", [row.get("symbol") for row in final_rows[:8]])
        print("Execution candidate count:", len(final_rows))
        print(
            "Execution candidate prices:",
            [
                {
                    "symbol": row.get("symbol"),
                    "price": row.get("price"),
                    "price_status": row.get("price_status"),
                    "stored_price": row.get("stored_price"),
                    "fresh_price": row.get("fresh_price"),
                }
                for row in final_rows[:8]
            ],
        )
        print(
            "Execution spotlight:",
            [row.get("symbol") for row in spotlight[:5] if isinstance(row, dict)],
        )

    return final_rows


def print_execution_candidates(
    force_rebuild: bool = False,
    watchlist: Optional[List[Any]] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    rows = get_execution_candidates(
        force_rebuild=force_rebuild,
        watchlist=watchlist,
        limit=limit,
        debug=False,
    )

    print("EXECUTION CANDIDATES")

    if not rows:
        print("None")
        return []

    for row in rows:
        warning = row.get("price_warning", "")
        print(
            row.get("symbol", "UNKNOWN"),
            "|",
            row.get("strategy", "CALL"),
            "|",
            row.get("fused_score", row.get("score", 0)),
            "|",
            row.get("confidence", "LOW"),
            "| price:",
            row.get("price", 0),
            "| price_status:",
            row.get("price_status", ""),
            "| vehicle:",
            row.get("vehicle_selected", "RESEARCH_ONLY"),
        )

        if warning:
            print("  PRICE WARNING:", warning)

    return rows


def get_execution_candidate_symbols(
    force_rebuild: bool = False,
    watchlist: Optional[List[Any]] = None,
    limit: int = 50,
) -> List[str]:
    rows = get_execution_candidates(
        force_rebuild=force_rebuild,
        watchlist=watchlist,
        limit=limit,
        debug=False,
    )

    return [
        _norm_symbol(row.get("symbol", ""))
        for row in rows
        if _norm_symbol(row.get("symbol", ""))
    ]


__all__ = [
    "get_execution_candidates",
    "print_execution_candidates",
    "get_execution_candidate_symbols",
]
