from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


TRADE_LOG_FILE = "data/trade_log.json"
CLOSED_FILE = "data/closed_positions.json"
OPEN_FILE = "data/open_positions.json"

OPTION_CONTRACT_MULTIPLIER = 100


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


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _load_json(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _vehicle(row: Dict[str, Any]) -> str:
    row = _safe_dict(row)

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

    option = _safe_dict(row.get("option"))
    contract = _safe_dict(row.get("contract"))

    contract_symbol = _safe_str(
        row.get(
            "contract_symbol",
            row.get(
                "option_symbol",
                row.get(
                    "option_contract_symbol",
                    option.get("contractSymbol", contract.get("contractSymbol", "")),
                ),
            ),
        ),
        "",
    )

    right = _upper(row.get("right", option.get("right", contract.get("right", ""))), "")

    if contract_symbol or right in {"CALL", "PUT", "C", "P"} or option or contract:
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
    return _upper(row.get("status", fallback), fallback)


def _pnl(row: Dict[str, Any]) -> float:
    for key in ["pnl", "realized_pnl", "net_pnl", "profit_loss"]:
        if row.get(key) not in (None, ""):
            return round(_safe_float(row.get(key), 0.0), 2)
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
    return False


def _load_closed_rows() -> List[Dict[str, Any]]:
    closed = _safe_list(_load_json(CLOSED_FILE, []))
    return [row for row in closed if isinstance(row, dict)]


def _load_trade_log_rows() -> List[Dict[str, Any]]:
    trade_log = _safe_list(_load_json(TRADE_LOG_FILE, []))
    return [row for row in trade_log if isinstance(row, dict)]


def _canonical_trade_key(row: Dict[str, Any]) -> str:
    trade_id = _trade_id(row)
    if trade_id:
        return f"trade_id:{trade_id}"

    symbol = _symbol(row)
    strategy = _strategy(row)
    timestamp = _timestamp(row)
    status = _status(row, "")
    return f"fallback:{symbol}:{strategy}:{status}:{timestamp}"


def _load_source_rows() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Closed positions are the performance source of truth.

    trade_log.json is only used as fallback for older runs where closed_positions.json
    is missing or empty. If both exist, this intentionally avoids double counting.
    """
    closed_rows = _load_closed_rows()
    trade_log_rows = _load_trade_log_rows()

    source = "closed_positions"
    rows = closed_rows

    if not rows:
        source = "trade_log_closed_like_fallback"
        rows = [row for row in trade_log_rows if _is_closed_like(row)]

    if not rows:
        source = "trade_log_all_fallback"
        rows = trade_log_rows

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
        "rows_used": len(deduped),
        "deduped_count": max(0, len(rows) - len(deduped)),
    }

    return deduped, meta


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
    }


def _add_trade_to_bucket(bucket: Dict[str, Any], row: Dict[str, Any]) -> None:
    pnl = _pnl(row)
    vehicle = _vehicle(row)
    symbol = _symbol(row)

    if vehicle not in bucket["vehicle_mix"]:
        vehicle = "UNKNOWN"

    bucket["trades"] += 1
    bucket["pnl"] = round(_safe_float(bucket.get("pnl"), 0.0) + pnl, 2)
    bucket["vehicle_mix"][vehicle] += 1

    symbols = bucket.setdefault("symbols", {})
    symbols[symbol] = int(symbols.get(symbol, 0)) + 1

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


def strategy_breakdown() -> Dict[str, Dict[str, Any]]:
    trades, _meta = _load_source_rows()
    stats: Dict[str, Dict[str, Any]] = {}

    for trade in trades:
        strategy = _strategy(trade)

        if strategy not in stats:
            stats[strategy] = _empty_bucket()

        _add_trade_to_bucket(stats[strategy], trade)

    for strategy in list(stats.keys()):
        stats[strategy] = _finalize_bucket(stats[strategy])

    return stats


def get_strategy_breakdown() -> Dict[str, Dict[str, Any]]:
    return strategy_breakdown()


def strategy_performance_summary() -> Dict[str, Any]:
    trades, meta = _load_source_rows()
    breakdown = strategy_breakdown()

    total = _empty_bucket()

    for trade in trades:
        _add_trade_to_bucket(total, trade)

    total = _finalize_bucket(total)

    return {
        "source": meta,
        "summary": total,
        "strategies": breakdown,
    }


def get_strategy_performance_summary() -> Dict[str, Any]:
    return strategy_performance_summary()


def print_strategy_breakdown() -> None:
    payload = strategy_performance_summary()
    source = payload.get("source", {})
    summary = payload.get("summary", {})
    strategies = payload.get("strategies", {})

    print("STRATEGY PERFORMANCE")
    print(f"Source: {source.get('source')}")
    print(f"Rows Used: {source.get('rows_used')}")
    print(f"Trades: {summary.get('trades')}")
    print(f"Wins/Losses/Flats: {summary.get('wins')} / {summary.get('losses')} / {summary.get('flats')}")
    print(f"Winrate: {summary.get('winrate')}")
    print(f"Total PnL: {summary.get('pnl')}")
    print(f"Average PnL: {summary.get('average_pnl')}")
    print(f"Vehicle Mix: {summary.get('vehicle_mix')}")

    if not strategies:
        print("No strategy rows available.")
        return

    print()
    print("BY STRATEGY")
    for strategy, row in sorted(strategies.items(), key=lambda item: _safe_float(item[1].get("pnl"), 0.0), reverse=True):
        print(
            f"{strategy}: trades={row.get('trades')} "
            f"wins={row.get('wins')} losses={row.get('losses')} flats={row.get('flats')} "
            f"winrate={row.get('winrate')} pnl={row.get('pnl')} "
            f"avg={row.get('average_pnl')} vehicles={row.get('vehicle_mix')}"
        )


__all__ = [
    "strategy_breakdown",
    "get_strategy_breakdown",
    "strategy_performance_summary",
    "get_strategy_performance_summary",
    "print_strategy_breakdown",
]
