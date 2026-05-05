from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


TRADE_LOG_FILE = "data/trade_log.json"
CLOSED_FILE = "data/closed_positions.json"
OPEN_FILE = "data/open_positions.json"
EXPORT_FILE = "data/trade_journal_export.csv"


EXPORT_FIELDS = [
    "record_source",
    "timestamp",
    "trade_id",
    "symbol",
    "strategy",
    "status",
    "vehicle",
    "vehicle_selected",
    "contracts",
    "shares",
    "entry",
    "entry_price",
    "entry_premium",
    "current_price",
    "current_premium",
    "exit_price",
    "exit_premium",
    "underlying_price",
    "current_underlying_price",
    "stop",
    "target",
    "take_profit",
    "option_stop",
    "option_target",
    "premium_stop",
    "premium_target",
    "target_premium",
    "take_profit_premium",
    "pnl",
    "realized_pnl",
    "unrealized_pnl",
    "pnl_pct",
    "pnl_basis",
    "price_review_basis",
    "monitoring_price_type",
    "underlying_price_used_for_close_decision",
    "underlying_price_used_for_pnl",
    "option_underlying_leak_blocked",
    "contract_symbol",
    "option_symbol",
    "expiry",
    "expiration",
    "strike",
    "right",
    "bid",
    "ask",
    "last",
    "mark",
    "volume",
    "open_interest",
    "dte",
    "option_contract_score",
    "contract_score",
    "score",
    "fused_score",
    "confidence",
    "final_reason",
    "final_reason_code",
    "reason",
    "close_reason",
    "opened_at",
    "closed_at",
    "trading_mode",
    "mode",
    "regime",
    "breadth",
    "volatility_state",
    "capital_required",
    "minimum_trade_cost",
    "capital_available",
    "execution_position_shape",
    "exit_price_source",
    "selected_for_execution",
    "research_approved",
    "execution_ready",
    "duplicate_source_note",
]


def _load(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
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
        if value is None:
            return int(default)
        if isinstance(value, bool):
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


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _contract_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    contract = _safe_dict(row.get("contract"))
    option = _safe_dict(row.get("option"))
    best_option = _safe_dict(row.get("best_option"))
    selected_contract = _safe_dict(row.get("selected_contract"))

    out.update(best_option)
    out.update(selected_contract)
    out.update(contract)
    out.update(option)

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
            row.get("selected_vehicle", row.get("vehicle", row.get("asset_type", row.get("instrument_type", "")))),
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

    return raw or "UNKNOWN"


def _strategy(row: Dict[str, Any]) -> str:
    strategy = _upper(row.get("strategy", row.get("direction", "")), "")
    if strategy in {"LONG", "BUY"}:
        return "CALL"
    if strategy in {"SHORT", "SELL"}:
        return "PUT"
    return strategy or "UNKNOWN"


def _status(row: Dict[str, Any], fallback_status: str = "") -> str:
    status = _upper(row.get("status", ""), "")
    if status:
        return status

    if _safe_str(row.get("closed_at"), "") or _safe_str(row.get("close_reason"), ""):
        return "CLOSED"

    if _safe_str(row.get("opened_at"), ""):
        return "OPEN"

    return _upper(fallback_status, "LOG")


def _timestamp(row: Dict[str, Any]) -> str:
    return _safe_str(row.get("timestamp", row.get("closed_at", row.get("opened_at", ""))), "")


def _trade_id(row: Dict[str, Any]) -> str:
    return _safe_str(row.get("trade_id"), "")


def _symbol(row: Dict[str, Any]) -> str:
    return _upper(row.get("symbol"), "UNKNOWN")


def _record_priority(record_source: str, status: str) -> int:
    source = _safe_str(record_source, "").lower()
    status = _upper(status, "")

    if source == "closed_positions" or status == "CLOSED":
        return 3

    if source == "open_positions" or status == "OPEN":
        return 2

    if source == "trade_log":
        return 1

    return 0


def _canonical_key(row: Dict[str, Any]) -> str:
    trade_id = _trade_id(row)
    if trade_id:
        return f"trade_id:{trade_id}"

    symbol = _symbol(row)
    strategy = _strategy(row)
    status = _status(row)
    opened_at = _safe_str(row.get("opened_at"), "")
    closed_at = _safe_str(row.get("closed_at"), "")
    timestamp = _timestamp(row)

    return f"fallback:{symbol}:{strategy}:{status}:{opened_at}:{closed_at}:{timestamp}"


def _first_positive_float(row: Dict[str, Any], contract: Dict[str, Any], keys: List[str]) -> float:
    for key in keys:
        value = row.get(key)
        if value in (None, ""):
            value = contract.get(key)
        number = _safe_optional_float(value)
        if number is not None and number > 0:
            return round(number, 4)
    return 0.0


def _normalize_option_aliases(normalized: Dict[str, Any]) -> None:
    option_stop = _first_positive_from_normalized(
        normalized,
        [
            "option_stop",
            "premium_stop",
            "stop_premium",
            "stop_loss_premium",
            "stop",
        ],
    )

    option_target = _first_positive_from_normalized(
        normalized,
        [
            "option_target",
            "premium_target",
            "target_premium",
            "take_profit_premium",
            "take_profit",
            "target",
        ],
    )

    if option_stop > 0:
        normalized["stop"] = option_stop
        normalized["option_stop"] = option_stop
        normalized["premium_stop"] = option_stop

    if option_target > 0:
        normalized["target"] = option_target
        normalized["take_profit"] = option_target
        normalized["option_target"] = option_target
        normalized["premium_target"] = option_target
        normalized["target_premium"] = option_target
        normalized["take_profit_premium"] = option_target


def _first_positive_from_normalized(row: Dict[str, Any], keys: List[str]) -> float:
    for key in keys:
        number = _safe_optional_float(row.get(key))
        if number is not None and number > 0:
            return round(number, 4)
    return 0.0


def _normalize_row(row: Dict[str, Any], *, record_source: str, fallback_status: str = "") -> Dict[str, Any]:
    row = dict(_safe_dict(row))
    contract = _contract_payload(row)
    vehicle = _vehicle(row)
    status = _status(row, fallback_status=fallback_status)

    contract_symbol = _safe_str(
        _pick(row, contract, "contract_symbol", "contractSymbol", "option_symbol", "option_contract_symbol"),
        "",
    )

    entry_premium = _first_positive_float(
        row,
        contract,
        [
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
        ],
    )

    if entry_premium <= 0 and vehicle == "OPTION":
        entry_candidate = _safe_optional_float(row.get("entry", row.get("entry_price")))
        if entry_candidate is not None and entry_candidate > 0:
            entry_premium = round(entry_candidate, 4)

    current_premium = _first_positive_float(
        row,
        contract,
        [
            "current_premium",
            "premium_current",
            "current_option_mark",
            "option_current_mark",
            "option_current_price",
            "current_option_price",
            "option_mark",
            "contract_mark",
            "mark",
            "last",
            "selected_price_reference",
            "price_reference",
        ],
    )

    exit_price = round(_safe_float(row.get("exit_price", row.get("close_price", 0.0)), 0.0), 4)
    exit_premium = round(_safe_float(row.get("exit_premium", exit_price if vehicle == "OPTION" else 0.0), 0.0), 4)

    normalized = {
        "record_source": record_source,
        "timestamp": _timestamp(row),
        "trade_id": _trade_id(row),
        "symbol": _symbol(row),
        "strategy": _strategy(row),
        "status": status,
        "vehicle": vehicle,
        "vehicle_selected": vehicle,

        "contracts": _safe_int(row.get("contracts", row.get("contract_count", row.get("quantity", 0))), 0),
        "shares": _safe_int(row.get("shares", row.get("quantity", 0)), 0),

        "entry": round(_safe_float(row.get("entry", row.get("entry_price", entry_premium if vehicle == "OPTION" else 0.0)), 0.0), 4),
        "entry_price": round(_safe_float(row.get("entry_price", row.get("entry", entry_premium if vehicle == "OPTION" else 0.0)), 0.0), 4),
        "entry_premium": entry_premium,

        "current_price": round(_safe_float(row.get("current_price", current_premium if vehicle == "OPTION" else 0.0), 0.0), 4),
        "current_premium": current_premium,

        "exit_price": exit_price,
        "exit_premium": exit_premium,

        "underlying_price": round(
            _safe_float(
                row.get(
                    "underlying_price",
                    row.get(
                        "current_underlying_price",
                        row.get("stock_price", row.get("market_price", 0.0)),
                    ),
                ),
                0.0,
            ),
            4,
        ),
        "current_underlying_price": round(
            _safe_float(
                row.get(
                    "current_underlying_price",
                    row.get("underlying_price", row.get("stock_price", 0.0)),
                ),
                0.0,
            ),
            4,
        ),

        "stop": round(_safe_float(row.get("stop", row.get("stop_loss", 0.0)), 0.0), 4),
        "target": round(_safe_float(row.get("target", row.get("take_profit", 0.0)), 0.0), 4),
        "take_profit": round(_safe_float(row.get("take_profit", row.get("target", 0.0)), 0.0), 4),

        "option_stop": round(_safe_float(row.get("option_stop", row.get("premium_stop", row.get("stop_premium", 0.0))), 0.0), 4),
        "option_target": round(_safe_float(row.get("option_target", row.get("premium_target", row.get("target_premium", 0.0))), 0.0), 4),
        "premium_stop": round(_safe_float(row.get("premium_stop", row.get("option_stop", row.get("stop_premium", 0.0))), 0.0), 4),
        "premium_target": round(_safe_float(row.get("premium_target", row.get("option_target", row.get("target_premium", 0.0))), 0.0), 4),
        "target_premium": round(_safe_float(row.get("target_premium", row.get("premium_target", row.get("option_target", 0.0))), 0.0), 4),
        "take_profit_premium": round(_safe_float(row.get("take_profit_premium", row.get("target_premium", row.get("premium_target", 0.0))), 0.0), 4),

        "pnl": round(_safe_float(row.get("pnl", 0.0), 0.0), 4),
        "realized_pnl": round(_safe_float(row.get("realized_pnl", row.get("pnl", 0.0)), 0.0), 4),
        "unrealized_pnl": round(_safe_float(row.get("unrealized_pnl", 0.0), 0.0), 4),
        "pnl_pct": round(_safe_float(row.get("pnl_pct", 0.0), 0.0), 4),
        "pnl_basis": _safe_str(row.get("pnl_basis"), ""),

        "price_review_basis": _safe_str(row.get("price_review_basis"), ""),
        "monitoring_price_type": _safe_str(row.get("monitoring_price_type"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            row.get("underlying_price_used_for_close_decision"),
            vehicle != "OPTION",
        ),
        "underlying_price_used_for_pnl": _safe_bool(
            row.get("underlying_price_used_for_pnl"),
            vehicle != "OPTION",
        ),
        "option_underlying_leak_blocked": _safe_bool(row.get("option_underlying_leak_blocked"), False),

        "contract_symbol": contract_symbol,
        "option_symbol": _safe_str(
            _pick(row, contract, "option_symbol", "contract_symbol", "contractSymbol", "option_contract_symbol"),
            "",
        ),
        "expiry": _safe_str(_pick(row, contract, "expiry", "expiration", "expiration_date"), ""),
        "expiration": _safe_str(_pick(row, contract, "expiration", "expiry", "expiration_date"), ""),
        "strike": round(_safe_float(_pick(row, contract, "strike", "strike_price", default=0.0), 0.0), 4),
        "right": _upper(_pick(row, contract, "right", "option_type", "call_put"), ""),

        "bid": round(_safe_float(_pick(row, contract, "bid", "option_bid", default=0.0), 0.0), 4),
        "ask": round(_safe_float(_pick(row, contract, "ask", "option_ask", default=0.0), 0.0), 4),
        "last": round(_safe_float(_pick(row, contract, "last", "last_price", "option_last", default=0.0), 0.0), 4),
        "mark": round(_safe_float(_pick(row, contract, "mark", "option_mark", "current_option_mark", "price_reference", default=0.0), 0.0), 4),
        "volume": _safe_int(_pick(row, contract, "volume", "option_volume", default=0), 0),
        "open_interest": _safe_int(_pick(row, contract, "open_interest", "oi", "option_open_interest", default=0), 0),
        "dte": _safe_int(_pick(row, contract, "dte", "daysToExpiration", default=0), 0),

        "option_contract_score": round(
            _safe_float(row.get("option_contract_score", row.get("contract_score", contract.get("contract_score", 0.0))), 0.0),
            4,
        ),
        "contract_score": round(
            _safe_float(row.get("contract_score", row.get("option_contract_score", contract.get("contract_score", 0.0))), 0.0),
            4,
        ),

        "score": round(_safe_float(row.get("score", 0.0), 0.0), 4),
        "fused_score": round(_safe_float(row.get("fused_score", row.get("score", 0.0)), 0.0), 4),
        "confidence": _upper(row.get("confidence"), ""),

        "final_reason": _safe_str(row.get("final_reason"), ""),
        "final_reason_code": _safe_str(row.get("final_reason_code"), ""),
        "reason": _safe_str(row.get("reason"), ""),
        "close_reason": _safe_str(row.get("close_reason"), ""),

        "opened_at": _safe_str(row.get("opened_at"), ""),
        "closed_at": _safe_str(row.get("closed_at"), ""),
        "trading_mode": _safe_str(row.get("trading_mode"), ""),
        "mode": _safe_str(row.get("mode"), ""),
        "regime": _safe_str(row.get("regime"), ""),
        "breadth": _safe_str(row.get("breadth"), ""),
        "volatility_state": _safe_str(row.get("volatility_state"), ""),

        "capital_required": round(_safe_float(row.get("capital_required", 0.0), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(row.get("minimum_trade_cost", 0.0), 0.0), 4),
        "capital_available": round(_safe_float(row.get("capital_available", 0.0), 0.0), 4),

        "execution_position_shape": _safe_str(row.get("execution_position_shape"), ""),
        "exit_price_source": _safe_str(row.get("exit_price_source"), ""),
        "selected_for_execution": _safe_bool(row.get("selected_for_execution"), False),
        "research_approved": _safe_bool(row.get("research_approved"), False),
        "execution_ready": _safe_bool(row.get("execution_ready"), False),
        "duplicate_source_note": "",
    }

    if normalized["vehicle"] == "OPTION":
        if normalized["contracts"] <= 0:
            normalized["contracts"] = 1
        normalized["shares"] = 0

        if normalized["entry_premium"] <= 0 and normalized["entry"] > 0:
            normalized["entry_premium"] = normalized["entry"]

        if normalized["current_premium"] <= 0 and normalized["current_price"] > 0:
            normalized["current_premium"] = normalized["current_price"]

        if normalized["entry"] <= 0 and normalized["entry_premium"] > 0:
            normalized["entry"] = normalized["entry_premium"]

        if normalized["entry_price"] <= 0 and normalized["entry_premium"] > 0:
            normalized["entry_price"] = normalized["entry_premium"]

        if normalized["current_price"] <= 0 and normalized["current_premium"] > 0:
            normalized["current_price"] = normalized["current_premium"]

        if not normalized["price_review_basis"]:
            normalized["price_review_basis"] = "OPTION_PREMIUM_ONLY"

        if not normalized["monitoring_price_type"]:
            normalized["monitoring_price_type"] = "OPTION_PREMIUM"

        if not normalized["pnl_basis"]:
            normalized["pnl_basis"] = "option_premium_x_100"

        normalized["underlying_price_used_for_close_decision"] = False
        normalized["underlying_price_used_for_pnl"] = False

        _normalize_option_aliases(normalized)

    elif normalized["vehicle"] == "STOCK":
        if normalized["shares"] <= 0:
            normalized["shares"] = 1
        normalized["contracts"] = 0

        if not normalized["price_review_basis"]:
            normalized["price_review_basis"] = "STOCK_PRICE"

        if not normalized["monitoring_price_type"]:
            normalized["monitoring_price_type"] = "UNDERLYING"

        if not normalized["pnl_basis"]:
            normalized["pnl_basis"] = "stock_price_x_shares"

        normalized["underlying_price_used_for_close_decision"] = True
        normalized["underlying_price_used_for_pnl"] = True

    return normalized


def _load_normalized_rows(
    *,
    include_open: bool = True,
    include_closed: bool = True,
    include_trade_log: bool = True,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if include_trade_log:
        trade_log = _safe_list(_load(TRADE_LOG_FILE, []))
        for row in trade_log:
            if isinstance(row, dict):
                rows.append(_normalize_row(row, record_source="trade_log", fallback_status="LOG"))

    if include_open:
        open_positions = _safe_list(_load(OPEN_FILE, []))
        for row in open_positions:
            if isinstance(row, dict):
                rows.append(_normalize_row(row, record_source="open_positions", fallback_status="OPEN"))

    if include_closed:
        closed_positions = _safe_list(_load(CLOSED_FILE, []))
        for row in closed_positions:
            if isinstance(row, dict):
                rows.append(_normalize_row(row, record_source="closed_positions", fallback_status="CLOSED"))

    return rows


def _dedupe_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prefer real position records over old log rows.

    Priority:
    1. closed_positions
    2. open_positions
    3. trade_log
    """
    best_by_key: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        key = _canonical_key(row)
        existing = best_by_key.get(key)

        if existing is None:
            best_by_key[key] = row
            continue

        existing_priority = _record_priority(existing.get("record_source", ""), existing.get("status", ""))
        new_priority = _record_priority(row.get("record_source", ""), row.get("status", ""))

        if new_priority > existing_priority:
            row["duplicate_source_note"] = f"replaced_lower_priority_{existing.get('record_source', '')}"
            best_by_key[key] = row
        else:
            existing["duplicate_source_note"] = existing.get("duplicate_source_note") or f"kept_over_{row.get('record_source', '')}"

    output = list(best_by_key.values())

    def _sort_key(row: Dict[str, Any]) -> Tuple[str, str, str]:
        return (
            _safe_str(row.get("closed_at") or row.get("opened_at") or row.get("timestamp"), ""),
            _safe_str(row.get("symbol"), ""),
            _safe_str(row.get("trade_id"), ""),
        )

    return sorted(output, key=_sort_key)


def build_trade_journal_rows(
    *,
    include_open: bool = True,
    include_closed: bool = True,
    include_trade_log: bool = True,
) -> List[Dict[str, Any]]:
    rows = _load_normalized_rows(
        include_open=include_open,
        include_closed=include_closed,
        include_trade_log=include_trade_log,
    )
    return _dedupe_rows(rows)


def export_trade_journal(path: str = EXPORT_FILE) -> str:
    rows = build_trade_journal_rows()

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in EXPORT_FIELDS})

    print(f"Journal exported: {path}")
    print(f"Journal rows: {len(rows)}")
    return path


def export_journal(path: str = EXPORT_FILE) -> str:
    return export_trade_journal(path)


def build_export_preview(limit: int = 10) -> List[Dict[str, Any]]:
    rows = build_trade_journal_rows()
    return rows[: max(0, int(limit))]


def print_trade_journal_preview(limit: int = 10) -> None:
    rows = build_export_preview(limit)

    print("TRADE JOURNAL PREVIEW")
    if not rows:
        print("No journal rows available.")
        return

    for row in rows:
        print(
            row.get("status"),
            row.get("symbol"),
            row.get("strategy"),
            "| vehicle:",
            row.get("vehicle"),
            "| pnl:",
            row.get("pnl"),
            "| entry premium:",
            row.get("entry_premium"),
            "| current premium:",
            row.get("current_premium"),
            "| exit premium:",
            row.get("exit_premium"),
            "| basis:",
            row.get("price_review_basis"),
            "| source:",
            row.get("record_source"),
        )


def main() -> None:
    export_trade_journal(EXPORT_FILE)


if __name__ == "__main__":
    main()


__all__ = [
    "build_trade_journal_rows",
    "export_trade_journal",
    "export_journal",
    "build_export_preview",
    "print_trade_journal_preview",
]
