from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


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
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
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


def load_json(path: str, default: Any) -> Any:
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


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
# PRICE EXTRACTION
# ============================================================

def _extract_last_price_from_dataframe(df: Any) -> Tuple[float, str]:
    """
    Handles normal yfinance frames, MultiIndex columns, lowercase columns,
    Adj Close, Close, and final numeric fallback.
    """
    try:
        if df is None:
            return 0.0, "df_none"

        if getattr(df, "empty", True):
            return 0.0, "df_empty"

        columns = list(getattr(df, "columns", []))

        # Direct simple columns.
        for col in ["Close", "Adj Close", "close", "adj close"]:
            try:
                if col in columns:
                    series = df[col].dropna()
                    if len(series) > 0:
                        price = _safe_float(series.iloc[-1], 0.0)
                        if price > 0:
                            return price, f"dataframe_column:{col}"
            except Exception:
                pass

        # MultiIndex columns, common with yfinance group_by behavior.
        try:
            if hasattr(df.columns, "levels"):
                for col in columns:
                    col_text = "|".join([str(x) for x in col]) if isinstance(col, tuple) else str(col)
                    col_text_l = col_text.lower()

                    if "close" in col_text_l and "adj" not in col_text_l:
                        series = df[col].dropna()
                        if len(series) > 0:
                            price = _safe_float(series.iloc[-1], 0.0)
                            if price > 0:
                                return price, f"dataframe_multi_close:{col_text}"

                for col in columns:
                    col_text = "|".join([str(x) for x in col]) if isinstance(col, tuple) else str(col)
                    col_text_l = col_text.lower()

                    if "adj close" in col_text_l or ("adj" in col_text_l and "close" in col_text_l):
                        series = df[col].dropna()
                        if len(series) > 0:
                            price = _safe_float(series.iloc[-1], 0.0)
                            if price > 0:
                                return price, f"dataframe_multi_adj_close:{col_text}"
        except Exception:
            pass

        # Last-resort: scan last row for usable positive numeric value.
        try:
            last_row = df.dropna(how="all").iloc[-1]
            numeric_values = []
            for value in list(last_row.values):
                price = _safe_float(value, 0.0)
                if price > 0:
                    numeric_values.append(price)

            if numeric_values:
                # Usually Close/Open/High/Low are clustered. Pick the last positive.
                return float(numeric_values[-1]), "dataframe_numeric_last_row_fallback"
        except Exception:
            pass

    except Exception:
        return 0.0, "dataframe_extract_exception"

    return 0.0, "dataframe_no_price"


def _fresh_price_via_safe_download(symbol: str) -> Tuple[float, str]:
    try:
        from engine.data_utils import safe_download

        df = safe_download(
            symbol,
            period="5d",
            interval="1d",
            auto_adjust=True,
            progress=False,
        )

        price, source = _extract_last_price_from_dataframe(df)
        if price > 0:
            return round(price, 4), f"safe_download:{source}"

        # Try shorter plain call too, because some wrappers dislike interval.
        df = safe_download(
            symbol,
            period="1mo",
            auto_adjust=True,
            progress=False,
        )

        price, source = _extract_last_price_from_dataframe(df)
        if price > 0:
            return round(price, 4), f"safe_download_retry:{source}"

        return 0.0, f"safe_download_no_price:{source}"

    except Exception as exc:
        return 0.0, f"safe_download_exception:{exc}"


def _fresh_price_via_yfinance(symbol: str) -> Tuple[float, str]:
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)

        # Fast info first.
        try:
            info = getattr(ticker, "fast_info", None)
            if info:
                for key in ["last_price", "lastPrice", "regular_market_price", "regularMarketPrice"]:
                    try:
                        price = _safe_float(info.get(key), 0.0)
                        if price > 0:
                            return round(price, 4), f"yfinance_fast_info:{key}"
                    except Exception:
                        pass
        except Exception:
            pass

        # History fallback.
        try:
            df = ticker.history(period="5d", interval="1d", auto_adjust=True)
            price, source = _extract_last_price_from_dataframe(df)
            if price > 0:
                return round(price, 4), f"yfinance_history:{source}"
        except Exception:
            pass

        try:
            df = yf.download(
                symbol,
                period="5d",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            price, source = _extract_last_price_from_dataframe(df)
            if price > 0:
                return round(price, 4), f"yfinance_download:{source}"
        except Exception:
            pass

    except Exception as exc:
        return 0.0, f"yfinance_exception:{exc}"

    return 0.0, "yfinance_no_price"


def _fresh_underlying_price(symbol: str) -> Tuple[float, str]:
    clean_symbol = _norm_symbol(symbol)
    if not clean_symbol:
        return 0.0, "missing_symbol"

    price, source = _fresh_price_via_safe_download(clean_symbol)
    if price > 0:
        return price, source

    yf_price, yf_source = _fresh_price_via_yfinance(clean_symbol)
    if yf_price > 0:
        return yf_price, yf_source

    return 0.0, f"{source}|{yf_source}"


def _stored_price_from_candidate(row: Dict[str, Any]) -> Tuple[float, str]:
    row = _safe_dict(row)

    candidates = [
        ("current_price", row.get("current_price")),
        ("price", row.get("price")),
        ("entry", row.get("entry")),
        ("last_price", row.get("last_price")),
        ("close", row.get("close")),
        ("underlying_price", row.get("underlying_price")),
        ("market_price", row.get("market_price")),
        ("latest_price", row.get("latest_price")),
        ("fill_price", row.get("fill_price")),
        ("requested_price", row.get("requested_price")),
    ]

    for source, value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4), source

    option = _safe_dict(row.get("option"))
    for source, value in [
        ("option.mark", option.get("mark")),
        ("option.last", option.get("last")),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4), source

    return 0.0, "no_stored_price"


def _resolve_candidate_price(symbol: str, row: Dict[str, Any]) -> Dict[str, Any]:
    stored_price, stored_source = _stored_price_from_candidate(row)
    fresh_price, fresh_source = _fresh_underlying_price(symbol)

    payload = {
        "price": stored_price,
        "current_price": stored_price,
        "underlying_price": stored_price,
        "stored_price": stored_price,
        "stored_price_source": stored_source,
        "fresh_price": fresh_price,
        "fresh_price_source": fresh_source,
        "price_status": "stored_price_used_no_fresh_price",
        "price_warning": "",
        "price_delta_pct": 0.0,
        "price_is_fresh": False,
    }

    if fresh_price > 0:
        payload["price"] = round(fresh_price, 4)
        payload["current_price"] = round(fresh_price, 4)
        payload["underlying_price"] = round(fresh_price, 4)
        payload["price_status"] = "fresh_price_used"
        payload["price_is_fresh"] = True

        if stored_price > 0:
            delta_pct = abs(fresh_price - stored_price) / stored_price
            payload["price_delta_pct"] = round(delta_pct, 4)

            if delta_pct >= 0.20:
                payload["price_status"] = "fresh_price_used_large_stored_delta"
                payload["price_warning"] = (
                    f"Fresh price differs from stored {stored_source} by "
                    f"{round(delta_pct * 100, 2)}%."
                )

        return payload

    if stored_price > 0:
        payload["price_warning"] = "Fresh price unavailable; using stored current_price."
        return payload

    payload["price"] = 0.0
    payload["current_price"] = 0.0
    payload["underlying_price"] = 0.0
    payload["price_status"] = "no_usable_price"
    payload["price_warning"] = "No fresh or stored price available."
    return payload


# ============================================================
# SCORING / SORTING
# ============================================================

def _confidence_rank(value: Any) -> int:
    confidence = _safe_str(value, "LOW").upper()
    mapping = {
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
    )


def _normalize_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(candidate or {})
    symbol = _norm_symbol(row.get("symbol", ""))

    if not symbol:
        return {}

    price_payload = _resolve_candidate_price(symbol, row)
    price = _safe_float(price_payload.get("price"), 0.0)

    if price <= 0:
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

    strategy = _safe_str(row.get("strategy", "CALL"), "CALL").upper()
    if not strategy:
        strategy = "CALL"

    company_name = _safe_str(
        row.get("company_name", row.get("company", symbol)),
        symbol,
    )

    current_price = round(price, 4)
    entry = round(_safe_float(row.get("entry", current_price), current_price), 4)

    # If entry came from stale stored price and fresh is available, use fresh for candidate entry preview.
    if bool(price_payload.get("price_is_fresh")):
        entry = current_price

    stop_existing = _safe_float(row.get("stop"), 0.0)
    target_existing = _safe_float(row.get("target"), 0.0)

    if strategy == "PUT":
        stop = round(stop_existing if stop_existing > 0 and not price_payload.get("price_is_fresh") else current_price * 1.03, 4)
        target = round(target_existing if target_existing > 0 and not price_payload.get("price_is_fresh") else current_price * 0.90, 4)
    else:
        stop = round(stop_existing if stop_existing > 0 and not price_payload.get("price_is_fresh") else current_price * 0.97, 4)
        target = round(target_existing if target_existing > 0 and not price_payload.get("price_is_fresh") else current_price * 1.10, 4)

    normalized = dict(row)
    normalized["symbol"] = symbol
    normalized["company_name"] = company_name
    normalized["strategy"] = strategy

    normalized["price"] = current_price
    normalized["current_price"] = current_price
    normalized["underlying_price"] = current_price
    normalized["entry"] = entry
    normalized["stop"] = stop
    normalized["target"] = target

    normalized["stored_price"] = price_payload.get("stored_price", 0.0)
    normalized["stored_price_source"] = price_payload.get("stored_price_source", "")
    normalized["fresh_price"] = price_payload.get("fresh_price", 0.0)
    normalized["fresh_price_source"] = price_payload.get("fresh_price_source", "")
    normalized["price_status"] = price_payload.get("price_status", "")
    normalized["price_warning"] = price_payload.get("price_warning", "")
    normalized["price_delta_pct"] = price_payload.get("price_delta_pct", 0.0)
    normalized["price_is_fresh"] = bool(price_payload.get("price_is_fresh", False))

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

    normalized["option_chain"] = _safe_list(row.get("option_chain"))
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

    v2 = _safe_dict(normalized.get("v2"))

    normalized["v2_regime_alignment"] = _safe_str(
        row.get("v2_regime_alignment", v2.get("regime_alignment", "")),
        "",
    )
    normalized["v2_signal_strength"] = round(
        _safe_float(row.get("v2_signal_strength", v2.get("signal_strength", 0.0)), 0.0),
        4,
    )
    normalized["v2_conviction_adjustment"] = round(
        _safe_float(row.get("v2_conviction_adjustment", v2.get("conviction_adjustment", 0.0)), 0.0),
        4,
    )
    normalized["v2_vehicle_bias"] = _safe_str(
        row.get("v2_vehicle_bias", v2.get("vehicle_bias", "")),
        "",
    ).upper()
    normalized["v2_thesis"] = _safe_str(
        row.get("v2_thesis", v2.get("thesis", "")),
        "",
    )
    normalized["v2_notes"] = _safe_list(
        row.get("v2_notes", v2.get("notes", []))
    )
    normalized["v2_risk_flags"] = _safe_list(
        row.get("v2_risk_flags", v2.get("risk_flags", []))
    )

    return normalized


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
            print("[EXECUTION_UNIVERSE_REBUILD_FAILED]", exc)

        if not rebuilt:
            print("[EXECUTION_UNIVERSE_REBUILD_SKIPPED] no compatible builder found")

    universe = load_json("data/execution_universe.json", {})
    universe = _safe_dict(universe)

    selected = _safe_list(universe.get("selected", []))
    watchlist_set = _watchlist_to_symbol_set(watchlist)

    normalized: List[Dict[str, Any]] = []

    for item in selected:
        if not isinstance(item, dict):
            continue

        candidate = _normalize_candidate(item)
        if not candidate:
            continue

        symbol = candidate["symbol"]
        if watchlist_set is not None and symbol not in watchlist_set:
            continue

        if candidate.get("price_warning"):
            print("EXECUTION SOURCE PRICE WARNING:", {
                "symbol": symbol,
                "warning": candidate.get("price_warning"),
                "used_price": candidate.get("price"),
                "stored_price": candidate.get("stored_price"),
                "stored_source": candidate.get("stored_price_source"),
                "fresh_price": candidate.get("fresh_price"),
                "fresh_source": candidate.get("fresh_price_source"),
                "delta_pct": candidate.get("price_delta_pct"),
                "price_status": candidate.get("price_status"),
            })

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
                    "fresh_source": row.get("fresh_price_source"),
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
            row.get("price_status", "UNKNOWN"),
            "| vehicle:",
            row.get("vehicle_selected", "RESEARCH_ONLY"),
        )

        if row.get("price_warning"):
            print("  PRICE WARNING:", row.get("price_warning"))

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
