from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


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


def _normalize_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(candidate or {})
    symbol = _norm_symbol(row.get("symbol", ""))
    if not symbol:
        return {}

    price = _safe_float(
        row.get("price", row.get("current_price", row.get("entry", 100.0))),
        100.0,
    )
    score = _safe_float(row.get("score", row.get("latest_score", 0)), 0.0)
    confidence = _safe_str(
        row.get("confidence", row.get("latest_confidence", "LOW")),
        "LOW",
    ).upper()
    strategy = _safe_str(row.get("strategy", "CALL"), "CALL").upper()

    row["symbol"] = symbol
    row.setdefault("company_name", row.get("company", symbol))
    row.setdefault("trend", "UPTREND")
    row.setdefault("rsi", 55)
    row.setdefault("atr", 2.0)
    row.setdefault("price", price)
    row.setdefault("current_price", price)
    row.setdefault("entry", price)

    if strategy == "PUT":
        row.setdefault("stop", round(price * 1.03, 2))
        row.setdefault("target", round(price * 0.90, 2))
    else:
        row.setdefault("stop", round(price * 0.97, 2))
        row.setdefault("target", round(price * 1.10, 2))

    row.setdefault("strategy", strategy)
    row.setdefault("volatility_state", "NORMAL")
    row.setdefault("mode", "AGGRESSIVE_ROTATION")
    row.setdefault("sector", "General")
    row.setdefault("confidence", confidence)
    row.setdefault("score", score)
    row.setdefault("option_chain", [])
    row.setdefault("source", "execution_universe")

    return row


def _dedupe_by_symbol(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for row in rows:
        symbol = _norm_symbol(row.get("symbol", ""))
        if not symbol or symbol in seen:
            continue
        out.append(row)
        seen.add(symbol)
    return out


# ============================================================
# UNIVERSE REBUILD COMPATIBILITY
# ============================================================

def _get_execution_universe_builder():
    try:
        import engine.execution_universe_builder as builder_module
    except Exception:
        return None

    candidate_names = [
        "build_execution_universe",
        "get_execution_universe",
        "build_universe",
        "build_execution_candidates",
    ]

    for name in candidate_names:
        fn = getattr(builder_module, name, None)
        if callable(fn):
            return fn

    return None


def _try_rebuild_execution_universe(
    limit: int,
    spotlight_limit: int,
    watchlist_limit: int,
    universe_limit: int,
    debug: bool = True,
) -> None:
    builder = _get_execution_universe_builder()
    if not callable(builder):
        if debug:
            print("[EXECUTION_UNIVERSE_REBUILD_SKIPPED] no compatible builder found")
        return

    attempts = [
        {
            "limit": limit,
            "spotlight_limit": spotlight_limit,
            "watchlist_limit": watchlist_limit,
            "universe_limit": universe_limit,
        },
        {
            "limit": limit,
            "spotlight_limit": spotlight_limit,
            "universe_limit": universe_limit,
        },
        {
            "limit": limit,
            "spotlight_limit": spotlight_limit,
        },
        {
            "limit": limit,
        },
        {},
    ]

    for kwargs in attempts:
        try:
            builder(**kwargs)
            return
        except TypeError:
            continue
        except Exception as e:
            if debug:
                print(f"[EXECUTION_UNIVERSE_REBUILD_ERROR] {e}")
            return

    if debug:
        print("[EXECUTION_UNIVERSE_REBUILD_SKIPPED] builder signature mismatch")


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
    """
    Compatibility-safe execution candidate accessor.

    Supports calls like:
        get_execution_candidates()
        get_execution_candidates(force_rebuild=True)
        get_execution_candidates(force_rebuild=True, watchlist=watchlist)
        get_execution_candidates(limit=20, watchlist=watchlist)

    Rebuilds the execution universe first when requested, then normalizes the
    selected candidates from data/execution_universe.json.
    """
    del args, kwargs

    limit = max(1, _safe_int(limit, 50))
    spotlight_limit = max(1, _safe_int(spotlight_limit, 5))
    watchlist_limit = max(limit, _safe_int(watchlist_limit, 50))
    universe_limit = max(watchlist_limit, _safe_int(universe_limit, 220))

    if force_rebuild:
        _try_rebuild_execution_universe(
            limit=limit,
            spotlight_limit=spotlight_limit,
            watchlist_limit=watchlist_limit,
            universe_limit=universe_limit,
            debug=debug,
        )

    universe = load_json("data/execution_universe.json", {})
    universe = _safe_dict(universe)

    selected = _safe_list(universe.get("selected", []))
    spotlight = _safe_list(universe.get("spotlight", []))
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

        normalized.append(candidate)

    normalized = _dedupe_by_symbol(normalized)

    confidence_rank = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    normalized.sort(
        key=lambda x: (
            _safe_float(x.get("score", 0), 0.0),
            confidence_rank.get(_safe_str(x.get("confidence", "LOW"), "LOW").upper(), 0),
        ),
        reverse=True,
    )

    final_rows = normalized[:limit]

    if debug:
        print("Execution candidates:", [row.get("symbol") for row in final_rows[:8]])
        print("Execution candidate count:", len(final_rows))
        print(
            "Execution spotlight:",
            [row.get("symbol") for row in spotlight[:5] if isinstance(row, dict)]
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
            row.get("score", 0),
            "|",
            row.get("confidence", "LOW"),
        )

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
