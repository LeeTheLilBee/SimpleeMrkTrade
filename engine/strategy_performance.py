from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


TRADE_LOG_FILE = "data/trade_log.json"
CLOSED_FILE = "data/closed_positions.json"
OPEN_FILE = "data/open_positions.json"

OPTION_CONTRACT_MULTIPLIER = 100

CLASS_REAL_TRADE = "REAL_TRADE"
CLASS_QUARANTINED_BAD_CLOSE = "QUARANTINED_BAD_CLOSE"
CLASS_MANUAL_TEST = "MANUAL_TEST"
CLASS_CONTROLLED_RELEASE = "CONTROLLED_RELEASE"
CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE = "NEEDS_REVIEW_HIGH_OPTION_MOVE"
CLASS_STALE_OR_UNKNOWN = "STALE_OR_UNKNOWN"
CLASS_EXCLUDED = "EXCLUDED"

EXCLUDED_CLASSIFICATIONS = {
    CLASS_QUARANTINED_BAD_CLOSE,
    CLASS_MANUAL_TEST,
    CLASS_CONTROLLED_RELEASE,
    CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE,
    CLASS_STALE_OR_UNKNOWN,
    CLASS_EXCLUDED,
}

HIGH_OPTION_MOVE_REVIEW_MULTIPLE = 3.0


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return float(default)
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Any:
    try:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return None
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            value = value.replace(",", "").strip()
            if value == "":
                return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1", "y"}:
                return True
            if lowered in {"false", "no", "0", "n"}:
                return False
        return bool(value)
    except Exception:
        return bool(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _lower(value: Any, default: str = "") -> str:
    return _safe_str(value, default).lower()


def _load_json(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _contract_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    row = _safe_dict(row)
    out: Dict[str, Any] = {}

    for key in ["best_option", "selected_contract", "contract", "option"]:
        value = row.get(key)
        if isinstance(value, dict):
            out.update(value)

    return out


def _pick(row: Dict[str, Any], contract: Dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if row.get(key) not in (None, ""):
            return row.get(key)
        if contract.get(key) not in (None, ""):
            return contract.get(key)
    return default


def _vehicle(row: Dict[str, Any]) -> str:
    row = _safe_dict(row)
    contract = _contract_payload(row)

    raw = _upper(
        row.get(
            "vehicle_selected",
            row.get(
                "selected_vehicle",
                row.get("vehicle", row.get("asset_type", row.get("instrument_type", ""))),
            ),
        ),
        "",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return "OPTION"

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return "STOCK"

    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return "RESEARCH_ONLY"

    contract_symbol = _safe_str(
        _pick(row, contract, "contract_symbol", "contractSymbol", "option_symbol", "option_contract_symbol"),
        "",
    )

    right = _upper(_pick(row, contract, "right", "option_type", "call_put"), "")

    if contract_symbol or right in {"CALL", "PUT", "C", "P"} or contract:
        return "OPTION"

    return "UNKNOWN"


def _strategy(row: Dict[str, Any]) -> str:
    strategy = _upper(row.get("strategy", row.get("direction", "")), "")

    if strategy in {"LONG", "BUY"}:
        return "CALL"

    if strategy in {"SHORT", "SELL"}:
        return "PUT"

    return strategy or "UNKNOWN"


def _symbol(row: Dict[str, Any]) -> str:
    return _upper(row.get("symbol"), "UNKNOWN")


def _trade_id(row: Dict[str, Any]) -> str:
    return _safe_str(row.get("trade_id"), "")


def _timestamp(row: Dict[str, Any]) -> str:
    return _safe_str(row.get("closed_at", row.get("opened_at", row.get("timestamp", ""))), "")


def _status(row: Dict[str, Any], fallback: str = "") -> str:
    status = _upper(row.get("status", ""), "")
    if status:
        return status

    if _safe_str(row.get("closed_at"), "") or _safe_str(row.get("close_reason"), ""):
        return "CLOSED"

    if _safe_str(row.get("opened_at"), ""):
        return "OPEN"

    return _upper(fallback, "")


def _reason(row: Dict[str, Any]) -> str:
    return _safe_str(
        row.get(
            "close_reason",
            row.get(
                "reason",
                row.get("final_reason", row.get("final_reason_code", "")),
            ),
        ),
        "",
    )


def _pnl(row: Dict[str, Any]) -> float:
    for key in ["pnl", "realized_pnl", "net_pnl", "profit_loss"]:
        if row.get(key) not in (None, ""):
            return round(_safe_float(row.get(key), 0.0), 2)
    return 0.0


def _entry(row: Dict[str, Any]) -> float:
    for key in ["entry", "entry_price", "entry_premium", "premium_entry", "option_entry"]:
        if row.get(key) not in (None, ""):
            return round(_safe_float(row.get(key), 0.0), 4)
    return 0.0


def _entry_premium(row: Dict[str, Any]) -> float:
    contract = _contract_payload(row)

    for key in [
        "entry_premium",
        "premium_entry",
        "option_entry",
        "option_entry_price",
        "entry_option_mark",
        "contract_entry_price",
        "fill_premium",
        "average_premium",
        "avg_premium",
        "executed_price",
        "fill_price",
        "selected_price_reference",
        "price_reference",
        "mark",
    ]:
        value = row.get(key)
        if value in (None, ""):
            value = contract.get(key)

        number = _safe_optional_float(value)
        if number is not None and number > 0:
            return round(number, 4)

    if _vehicle(row) == "OPTION":
        return _entry(row)

    return 0.0


def _exit_price(row: Dict[str, Any]) -> float:
    for key in ["exit_price", "close_price", "exit", "closed_price"]:
        if row.get(key) not in (None, ""):
            return round(_safe_float(row.get(key), 0.0), 4)
    return 0.0


def _exit_premium(row: Dict[str, Any]) -> float:
    contract = _contract_payload(row)

    for key in [
        "exit_premium",
        "close_premium",
        "premium_exit",
        "option_exit",
        "option_exit_price",
        "exit_option_mark",
        "close_option_mark",
        "final_option_mark",
    ]:
        value = row.get(key)
        if value in (None, ""):
            value = contract.get(key)

        number = _safe_optional_float(value)
        if number is not None and number > 0:
            return round(number, 4)

    return 0.0


def _is_closed_like(row: Dict[str, Any]) -> bool:
    status = _status(row, "")
    if status == "CLOSED":
        return True
    if _safe_str(row.get("closed_at"), ""):
        return True
    if _safe_str(row.get("close_reason"), ""):
        return True
    if row.get("exit_price") not in (None, "", 0, 0.0):
        return True
    if row.get("exit_premium") not in (None, "", 0, 0.0):
        return True
    return False


def _load_closed_rows() -> List[Dict[str, Any]]:
    closed = _safe_list(_load_json(CLOSED_FILE, []))
    return [row for row in closed if isinstance(row, dict)]


def _load_trade_log_rows() -> List[Dict[str, Any]]:
    trade_log = _safe_list(_load_json(TRADE_LOG_FILE, []))
    return [row for row in trade_log if isinstance(row, dict)]


def _load_open_rows() -> List[Dict[str, Any]]:
    open_rows = _safe_list(_load_json(OPEN_FILE, []))
    return [row for row in open_rows if isinstance(row, dict)]


def _canonical_trade_key(row: Dict[str, Any]) -> str:
    trade_id = _trade_id(row)
    if trade_id:
        return f"trade_id:{trade_id}"

    symbol = _symbol(row)
    strategy = _strategy(row)
    timestamp = _timestamp(row)
    status = _status(row, "")
    return f"fallback:{symbol}:{strategy}:{status}:{timestamp}"


def _explicit_classification(row: Dict[str, Any]) -> str:
    return _upper(
        row.get(
            "performance_classification",
            row.get("classification", row.get("review_classification", "")),
        ),
        "",
    )


def _explicit_performance_include(row: Dict[str, Any]) -> Any:
    if "performance_include" in row:
        return _safe_bool(row.get("performance_include"), True)

    if "include_in_performance" in row:
        return _safe_bool(row.get("include_in_performance"), True)

    if "counts_in_performance" in row:
        return _safe_bool(row.get("counts_in_performance"), True)

    return None


def _looks_like_high_option_move(row: Dict[str, Any]) -> bool:
    if _vehicle(row) != "OPTION":
        return False

    entry_premium = _entry_premium(row)
    exit_premium = _exit_premium(row)

    if entry_premium <= 0 or exit_premium <= 0:
        return False

    return exit_premium >= entry_premium * HIGH_OPTION_MOVE_REVIEW_MULTIPLE


def _classify_row(row: Dict[str, Any]) -> Tuple[str, str]:
    row = _safe_dict(row)

    status = _status(row, "")
    vehicle = _vehicle(row)
    reason_raw = _reason(row)
    reason = reason_raw.lower()
    pnl = _pnl(row)

    explicit_classification = _explicit_classification(row)
    explicit_include = _explicit_performance_include(row)

    if explicit_classification:
        if explicit_classification in {
            CLASS_QUARANTINED_BAD_CLOSE,
            CLASS_MANUAL_TEST,
            CLASS_CONTROLLED_RELEASE,
            CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE,
            CLASS_STALE_OR_UNKNOWN,
            CLASS_EXCLUDED,
            CLASS_REAL_TRADE,
        }:
            return explicit_classification, "explicit_classification"

    if explicit_include is False:
        if _safe_bool(row.get("needs_review"), False):
            return CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE, "performance_include_false_needs_review"
        return CLASS_EXCLUDED, "performance_include_false"

    if _safe_bool(row.get("needs_review"), False):
        return CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE, "needs_review_true"

    if "needs_review_high_option_move" in reason:
        return CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE, "reason_needs_review_high_option_move"

    if "quarantined" in reason or "bad close" in reason or "bad_option" in reason:
        return CLASS_QUARANTINED_BAD_CLOSE, "quarantined_close_reason"

    if _safe_bool(row.get("quarantined"), False):
        return CLASS_QUARANTINED_BAD_CLOSE, "quarantined_flag"

    if _lower(row.get("data_quality"), "") in {"quarantined", "bad_option_close"}:
        return CLASS_QUARANTINED_BAD_CLOSE, "data_quality_flag"

    if _safe_bool(row.get("option_underlying_leak_blocked"), False):
        return CLASS_QUARANTINED_BAD_CLOSE, "underlying_leak_flag"

    if "manual_option_premium_test" in reason or "manual_test" in reason or "test" in reason:
        return CLASS_MANUAL_TEST, "manual_or_test_reason"

    if "controlled_slot_release" in reason or "slot_release" in reason:
        return CLASS_CONTROLLED_RELEASE, "controlled_release_reason"

    if vehicle == "UNKNOWN":
        return CLASS_STALE_OR_UNKNOWN, "unknown_vehicle"

    if status not in {"CLOSED", "FILLED", "OPEN"} and not _is_closed_like(row):
        return CLASS_STALE_OR_UNKNOWN, "not_closed_like"

    if vehicle == "OPTION":
        entry_premium = _entry_premium(row)
        exit_price = _exit_price(row)
        exit_premium = _exit_premium(row)

        if entry_premium > 0 and exit_price >= 25 and exit_price >= entry_premium * 8 and exit_premium <= 0:
            return CLASS_QUARANTINED_BAD_CLOSE, "option_exit_looks_like_underlying"

        if pnl == 0 and "take_profit" in reason and entry_premium > 0 and exit_premium in {0.0, entry_premium}:
            return CLASS_QUARANTINED_BAD_CLOSE, "zero_pnl_take_profit_option_needs_review"

        if _looks_like_high_option_move(row):
            return CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE, "high_option_move_needs_review"

    return CLASS_REAL_TRADE, "counts_in_performance"


def _flatten_row(row: Dict[str, Any], *, record_source: str) -> Dict[str, Any]:
    row = dict(_safe_dict(row))

    classification, classification_reason = _classify_row(row)
    vehicle = _vehicle(row)
    strategy = _strategy(row)
    symbol = _symbol(row)
    pnl = _pnl(row)

    counts = classification not in EXCLUDED_CLASSIFICATIONS

    explicit_include = _explicit_performance_include(row)
    if explicit_include is False:
        counts = False

    flattened = {
        "record_source": record_source,
        "trade_id": _trade_id(row),
        "symbol": symbol,
        "strategy": strategy,
        "status": _status(row, "CLOSED" if record_source == "closed_positions" else ""),
        "vehicle": vehicle,
        "timestamp": _timestamp(row),
        "opened_at": _safe_str(row.get("opened_at"), ""),
        "closed_at": _safe_str(row.get("closed_at"), ""),
        "entry": _entry(row),
        "entry_premium": _entry_premium(row) if vehicle == "OPTION" else 0.0,
        "exit_price": _exit_price(row),
        "exit_premium": _exit_premium(row) if vehicle == "OPTION" else 0.0,
        "pnl": pnl,
        "close_reason": _reason(row),
        "classification": classification,
        "classification_reason": classification_reason,
        "counts_in_performance": counts,
        "performance_include": counts,
        "include_in_performance": counts,
        "needs_review": _safe_bool(row.get("needs_review"), False) or classification == CLASS_NEEDS_REVIEW_HIGH_OPTION_MOVE,
        "raw": row,
    }

    return flattened


def _load_source_rows() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Closed positions are the performance source of truth.

    trade_log.json is only a fallback for older runs where closed_positions.json
    is missing or empty. This prevents double-counting.
    """
    closed_rows = _load_closed_rows()
    trade_log_rows = _load_trade_log_rows()

    source = "closed_positions"
    rows = closed_rows
    record_source = "closed_positions"

    if not rows:
        source = "trade_log_closed_like_fallback"
        rows = [row for row in trade_log_rows if _is_closed_like(row)]
        record_source = "trade_log"

    if not rows:
        source = "trade_log_all_fallback"
        rows = trade_log_rows
        record_source = "trade_log"

    deduped: List[Dict[str, Any]] = []
    seen = set()

    for row in rows:
        key = _canonical_trade_key(row)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    meta = {
        "source": source,
        "closed_position_rows": len(closed_rows),
        "trade_log_rows": len(trade_log_rows),
        "rows_used_before_filter": len(deduped),
        "deduped_count": max(0, len(rows) - len(deduped)),
        "record_source": record_source,
    }

    return deduped, meta


def flattened_closed_rows(include_excluded: bool = True) -> List[Dict[str, Any]]:
    rows, meta = _load_source_rows()
    record_source = _safe_str(meta.get("record_source"), "closed_positions")

    flattened = [_flatten_row(row, record_source=record_source) for row in rows]

    if include_excluded:
        return flattened

    return [row for row in flattened if bool(row.get("counts_in_performance"))]


def get_flattened_closed_rows(include_excluded: bool = True) -> List[Dict[str, Any]]:
    return flattened_closed_rows(include_excluded=include_excluded)


def _empty_bucket() -> Dict[str, Any]:
    return {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "flats": 0,
        "pnl": 0.0,
        "average_pnl": 0.0,
        "best_trade": 0.0,
        "worst_trade": 0.0,
        "winrate": 0.0,
        "lossrate": 0.0,
        "flatrate": 0.0,
        "vehicle_mix": {
            "OPTION": 0,
            "STOCK": 0,
            "RESEARCH_ONLY": 0,
            "UNKNOWN": 0,
        },
        "symbols": {},
        "classifications": {},
    }


def _add_trade_to_bucket(bucket: Dict[str, Any], row: Dict[str, Any]) -> None:
    pnl = _safe_float(row.get("pnl"), 0.0)
    vehicle = _safe_str(row.get("vehicle"), "UNKNOWN").upper()
    symbol = _safe_str(row.get("symbol"), "UNKNOWN").upper()
    classification = _safe_str(row.get("classification"), CLASS_REAL_TRADE).upper()

    if vehicle not in bucket["vehicle_mix"]:
        vehicle = "UNKNOWN"

    bucket["trades"] += 1
    bucket["pnl"] = round(_safe_float(bucket.get("pnl"), 0.0) + pnl, 2)
    bucket["vehicle_mix"][vehicle] += 1

    symbols = bucket.setdefault("symbols", {})
    symbols[symbol] = int(symbols.get(symbol, 0)) + 1

    classifications = bucket.setdefault("classifications", {})
    classifications[classification] = int(classifications.get(classification, 0)) + 1

    if pnl > 0:
        bucket["wins"] += 1
    elif pnl < 0:
        bucket["losses"] += 1
    else:
        bucket["flats"] += 1

    if bucket["trades"] == 1:
        bucket["best_trade"] = pnl
        bucket["worst_trade"] = pnl
    else:
        bucket["best_trade"] = max(_safe_float(bucket.get("best_trade"), 0.0), pnl)
        bucket["worst_trade"] = min(_safe_float(bucket.get("worst_trade"), 0.0), pnl)


def _finalize_bucket(bucket: Dict[str, Any]) -> Dict[str, Any]:
    trades = int(bucket.get("trades", 0))
    wins = int(bucket.get("wins", 0))
    losses = int(bucket.get("losses", 0))
    flats = int(bucket.get("flats", 0))
    pnl = round(_safe_float(bucket.get("pnl"), 0.0), 2)

    bucket["pnl"] = pnl
    bucket["average_pnl"] = round(pnl / trades, 2) if trades else 0.0
    bucket["best_trade"] = round(_safe_float(bucket.get("best_trade"), 0.0), 2)
    bucket["worst_trade"] = round(_safe_float(bucket.get("worst_trade"), 0.0), 2)
    bucket["winrate"] = round(wins / trades, 4) if trades else 0.0
    bucket["lossrate"] = round(losses / trades, 4) if trades else 0.0
    bucket["flatrate"] = round(flats / trades, 4) if trades else 0.0

    return bucket


def _classification_summary(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    buckets: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        classification = _safe_str(row.get("classification"), "UNKNOWN").upper()

        if classification not in buckets:
            buckets[classification] = _empty_bucket()

        _add_trade_to_bucket(buckets[classification], row)

    for key in list(buckets.keys()):
        buckets[key] = _finalize_bucket(buckets[key])

    return buckets


def strategy_breakdown(include_excluded: bool = False) -> Dict[str, Dict[str, Any]]:
    rows = flattened_closed_rows(include_excluded=include_excluded)

    stats: Dict[str, Dict[str, Any]] = {}

    for trade in rows:
        if not include_excluded and not bool(trade.get("counts_in_performance")):
            continue

        strategy = _safe_str(trade.get("strategy"), "UNKNOWN").upper()

        if strategy not in stats:
            stats[strategy] = _empty_bucket()

        _add_trade_to_bucket(stats[strategy], trade)

    for strategy in list(stats.keys()):
        stats[strategy] = _finalize_bucket(stats[strategy])

    return stats


def get_strategy_breakdown(include_excluded: bool = False) -> Dict[str, Dict[str, Any]]:
    return strategy_breakdown(include_excluded=include_excluded)


def strategy_performance_summary(include_excluded: bool = False) -> Dict[str, Any]:
    raw_rows, meta = _load_source_rows()
    flattened_all = flattened_closed_rows(include_excluded=True)

    performance_rows = (
        flattened_all
        if include_excluded
        else [row for row in flattened_all if bool(row.get("counts_in_performance"))]
    )

    breakdown = strategy_breakdown(include_excluded=include_excluded)

    total = _empty_bucket()
    for trade in performance_rows:
        _add_trade_to_bucket(total, trade)

    total = _finalize_bucket(total)

    excluded_rows = [row for row in flattened_all if not bool(row.get("counts_in_performance"))]

    source = dict(meta)
    source["raw_rows_loaded"] = len(raw_rows)
    source["flattened_rows"] = len(flattened_all)
    source["rows_used"] = len(performance_rows)
    source["rows_excluded_from_performance"] = len(excluded_rows)
    source["include_excluded"] = bool(include_excluded)

    return {
        "source": source,
        "summary": total,
        "strategies": breakdown,
        "classifications": _classification_summary(flattened_all),
        "excluded_rows": excluded_rows,
        "flattened_rows": flattened_all,
    }


def get_strategy_performance_summary(include_excluded: bool = False) -> Dict[str, Any]:
    return strategy_performance_summary(include_excluded=include_excluded)


def print_strategy_breakdown(include_excluded: bool = False) -> None:
    payload = strategy_performance_summary(include_excluded=include_excluded)
    source = payload.get("source", {})
    summary = payload.get("summary", {})
    strategies = payload.get("strategies", {})
    classifications = payload.get("classifications", {})

    print("STRATEGY PERFORMANCE")
    print(f"Source: {source.get('source')}")
    print(f"Rows Loaded: {source.get('raw_rows_loaded')}")
    print(f"Flattened Rows: {source.get('flattened_rows')}")
    print(f"Rows Used: {source.get('rows_used')}")
    print(f"Rows Excluded: {source.get('rows_excluded_from_performance')}")
    print(f"Include Excluded: {source.get('include_excluded')}")
    print()
    print("PERFORMANCE SUMMARY")
    print(f"Trades: {summary.get('trades')}")
    print(f"Wins/Losses/Flats: {summary.get('wins')} / {summary.get('losses')} / {summary.get('flats')}")
    print(f"Winrate: {summary.get('winrate')}")
    print(f"Total PnL: {summary.get('pnl')}")
    print(f"Average PnL: {summary.get('average_pnl')}")
    print(f"Best/Worst: {summary.get('best_trade')} / {summary.get('worst_trade')}")
    print(f"Vehicle Mix: {summary.get('vehicle_mix')}")

    print()
    print("CLASSIFICATIONS")
    if classifications:
        for label, row in sorted(classifications.items()):
            print(
                f"{label}: rows={row.get('trades')} "
                f"pnl={row.get('pnl')} "
                f"wins/losses/flats={row.get('wins')}/{row.get('losses')}/{row.get('flats')}"
            )
    else:
        print("No classifications available.")

    if not strategies:
        print()
        print("No strategy rows available.")
        return

    print()
    print("BY STRATEGY")
    for strategy, row in sorted(
        strategies.items(),
        key=lambda item: _safe_float(item[1].get("pnl"), 0.0),
        reverse=True,
    ):
        print(
            f"{strategy}: trades={row.get('trades')} "
            f"wins={row.get('wins')} losses={row.get('losses')} flats={row.get('flats')} "
            f"winrate={row.get('winrate')} pnl={row.get('pnl')} "
            f"avg={row.get('average_pnl')} vehicles={row.get('vehicle_mix')}"
        )


def print_flattened_rows(limit: int = 30, include_excluded: bool = True) -> None:
    rows = flattened_closed_rows(include_excluded=include_excluded)

    print("FLATTENED CLOSED ROWS")
    print(f"Rows: {len(rows)}")
    print(f"Include Excluded: {include_excluded}")
    print("-" * 80)

    for index, row in enumerate(rows[: max(0, int(limit))]):
        vehicle = row.get("vehicle")

        if vehicle == "OPTION":
            entry_display = f"entry premium: {row.get('entry_premium')}"
            exit_display = f"exit premium: {row.get('exit_premium')}"
        else:
            entry_display = f"entry: {row.get('entry')}"
            exit_display = f"exit: {row.get('exit_price')}"

        print(
            index,
            row.get("classification"),
            "|",
            row.get("symbol"),
            row.get("strategy"),
            "| vehicle:",
            row.get("vehicle"),
            "| pnl:",
            row.get("pnl"),
            "|",
            entry_display,
            "|",
            exit_display,
            "| include:",
            row.get("counts_in_performance"),
            "| reason:",
            row.get("close_reason"),
            "| why:",
            row.get("classification_reason"),
        )


__all__ = [
    "strategy_breakdown",
    "get_strategy_breakdown",
    "strategy_performance_summary",
    "get_strategy_performance_summary",
    "flattened_closed_rows",
    "get_flattened_closed_rows",
    "print_strategy_breakdown",
    "print_flattened_rows",
]
