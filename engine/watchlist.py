from __future__ import annotations

from typing import Any, Dict, List
from datetime import datetime

from engine.watchlist_rotation import build_rotating_watchlist


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _dedupe_symbols(rows: List[Any]) -> List[Any]:
    seen = set()
    cleaned = []

    for row in _safe_list(rows):
        if isinstance(row, dict):
            symbol = _norm_symbol(row.get("symbol", ""))
            if not symbol or symbol in seen:
                continue

            clean_row = dict(row)
            clean_row["symbol"] = symbol
            cleaned.append(clean_row)
            seen.add(symbol)

        else:
            symbol = _norm_symbol(row)
            if not symbol or symbol in seen:
                continue

            cleaned.append(symbol)
            seen.add(symbol)

    return cleaned


# ============================================================
# CORE WATCHLIST BUILDERS
# ============================================================

def get_watchlist(
    limit: int = 50,
    universe_limit: int = 220,
    include_meta: bool = False,
    debug: bool = False,
    *args,
    **kwargs,
):
    """
    Primary public watchlist accessor.

    Supports the newer bot-style signature:
        get_watchlist(limit=50, universe_limit=220)

    Also safely tolerates extra args/kwargs so old call sites do not crash.
    """
    limit = max(1, _safe_int(limit, 50))
    universe_limit = max(limit, _safe_int(universe_limit, 220))

    try:
        raw_watchlist = build_rotating_watchlist(
            limit=limit,
            universe_limit=universe_limit,
        )
    except TypeError:
        # compatibility fallback in case build_rotating_watchlist only takes one arg
        try:
            raw_watchlist = build_rotating_watchlist(limit=limit)
        except TypeError:
            raw_watchlist = build_rotating_watchlist()
    except Exception as e:
        print(f"[WATCHLIST_BUILD_ERROR] {e}")
        raw_watchlist = []

    watchlist = _dedupe_symbols(raw_watchlist)[:limit]

    if debug:
        preview = []
        for item in watchlist[:10]:
            if isinstance(item, dict):
                preview.append(item.get("symbol"))
            else:
                preview.append(_norm_symbol(item))
        print(
            "[WATCHLIST]",
            {
                "requested_limit": limit,
                "universe_limit": universe_limit,
                "returned_count": len(watchlist),
                "preview": preview,
            },
        )

    if include_meta:
        return {
            "items": watchlist,
            "count": len(watchlist),
            "limit": limit,
            "universe_limit": universe_limit,
            "generated_at": datetime.now().isoformat(),
        }

    return watchlist


def get_watchlist_symbols(limit: int = 50, universe_limit: int = 220) -> List[str]:
    rows = get_watchlist(limit=limit, universe_limit=universe_limit)
    out: List[str] = []

    for item in _safe_list(rows):
        if isinstance(item, dict):
            symbol = _norm_symbol(item.get("symbol", ""))
        else:
            symbol = _norm_symbol(item)

        if symbol:
            out.append(symbol)

    return out


def get_watchlist_payload(limit: int = 50, universe_limit: int = 220) -> Dict[str, Any]:
    return get_watchlist(
        limit=limit,
        universe_limit=universe_limit,
        include_meta=True,
        debug=False,
    )


def print_watchlist(limit: int = 20, universe_limit: int = 220) -> List[Any]:
    rows = get_watchlist(limit=limit, universe_limit=universe_limit, debug=False)

    print("WATCHLIST")
    if not rows:
        print("No watchlist symbols.")
        return []

    for item in rows:
        if isinstance(item, dict):
            symbol = _norm_symbol(item.get("symbol", "UNKNOWN"))
            company_name = _safe_str(item.get("company_name", ""), "")
            sector = _safe_str(item.get("sector", ""), "")
            line = symbol
            if company_name:
                line += f" | {company_name}"
            if sector:
                line += f" | {sector}"
            print(line)
        else:
            print(_norm_symbol(item))

    return rows
