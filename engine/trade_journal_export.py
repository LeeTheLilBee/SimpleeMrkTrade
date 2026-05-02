from __future__ import annotations

"""
Observatory Trade Journal Export

Purpose:
    Export the trade journal to CSV in a way that is audit-friendly for both
    STOCK and OPTION positions.

Critical option-safety rule:
    OPTION prices must be separated into premium fields and underlying context.

For options:
    entry_premium
    current_premium
    exit_premium
    option_stop
    option_target
    underlying_price
    current_underlying_price
    pnl_basis = option_premium_x_100

For stocks:
    entry_price
    current_price
    exit_price
    stop
    target
    shares
    pnl_basis = stock_price_x_shares

Why this rewrite exists:
    The old export had generic fields like entry/current_price/exit_price,
    which made it hard to tell whether an option row was showing premium or
    the underlying stock price.

Compatibility:
    - Keeps export_trade_journal(path=..., refresh_snapshot=...)
    - Uses read_trade_journal() and write_trade_journal_snapshot()
    - Accepts old and new schemas
    - Produces one flat CSV
"""

import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.trade_journal import read_trade_journal, write_trade_journal_snapshot


EXPORT_FILE = "data/trade_journal_export.csv"
OPTION_CONTRACT_MULTIPLIER = 100


# =============================================================================
# Safe helpers
# =============================================================================

def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return None
            value = cleaned
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
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _round4(value: Any) -> float:
    return round(_safe_float(value, 0.0), 4)


def _json_blob(value: Any) -> str:
    if value in (None, "", [], {}):
        return ""
    try:
        return json.dumps(value, default=str, ensure_ascii=False)
    except Exception:
        return str(value)


def _first_float(row: Dict[str, Any], keys: List[str]) -> Optional[float]:
    for key in keys:
        value = _safe_optional_float(row.get(key))
        if value is not None:
            return value
    return None


def _first_str(row: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _upper(value: Any, default: str = "") -> str:
    text = _safe_str(value, default).upper()
    return text or default


# =============================================================================
# Shape helpers
# =============================================================================

def _detect_vehicle(row: Dict[str, Any]) -> str:
    raw = _upper(
        row.get(
            "vehicle_selected",
            row.get("selected_vehicle", row.get("vehicle", row.get("asset_type", ""))),
        ),
        "",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return "OPTION"

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return "STOCK"

    option = _safe_dict(row.get("option"))
    contract = _safe_dict(row.get("contract"))
    contract_symbol = _first_str(
        row,
        [
            "contract_symbol",
            "option_symbol",
            "option_contract_symbol",
            "selected_contract_symbol",
            "occ_symbol",
        ],
        "",
    )

    if option or contract or contract_symbol:
        return "OPTION"

    return "STOCK"


def _nested(row: Dict[str, Any], *keys: str) -> Any:
    current: Any = row
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _extract_contract(row: Dict[str, Any]) -> Dict[str, Any]:
    option = _safe_dict(row.get("option"))
    contract = _safe_dict(row.get("contract"))

    merged: Dict[str, Any] = {}
    merged.update(contract)
    merged.update(option)

    contract_symbol = (
        _first_str(
            row,
            [
                "contract_symbol",
                "option_symbol",
                "option_contract_symbol",
                "selected_contract_symbol",
                "occ_symbol",
            ],
            "",
        )
        or _first_str(
            merged,
            [
                "contractSymbol",
                "contract_symbol",
                "option_symbol",
                "symbol",
                "occ_symbol",
                "selected_contract_symbol",
            ],
            "",
        )
    )

    expiry = (
        _first_str(row, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
        or _first_str(merged, ["expiration", "expiry", "expiration_date", "contract_expiry"], "")
    )

    right = _upper(
        _first_str(row, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(merged, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if right in {"C", "CALLS"}:
        right = "CALL"
    elif right in {"P", "PUTS"}:
        right = "PUT"

    strike = _first_float(row, ["strike", "strike_price", "contract_strike"])
    if strike is None:
        strike = _first_float(merged, ["strike", "strike_price", "contract_strike"])

    bid = _first_float(row, ["option_bid", "bid"])
    if bid is None:
        bid = _first_float(merged, ["bid"])

    ask = _first_float(row, ["option_ask", "ask"])
    if ask is None:
        ask = _first_float(merged, ["ask"])

    last = _first_float(row, ["option_last", "last"])
    if last is None:
        last = _first_float(merged, ["last", "last_price"])

    mark = _first_float(
        row,
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "mark",
            "current_premium",
            "premium_current",
        ],
    )
    if mark is None:
        mark = _first_float(
            merged,
            [
                "current_option_mark",
                "option_current_mark",
                "option_mark",
                "current_mark",
                "mark",
                "mid",
                "selected_price_reference",
                "price_reference",
            ],
        )

    return {
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "right": right,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "volume": _safe_int(row.get("volume", merged.get("volume")), 0),
        "open_interest": _safe_int(row.get("open_interest", merged.get("open_interest", merged.get("oi"))), 0),
        "implied_volatility": _safe_float(row.get("implied_volatility", merged.get("implied_volatility")), 0.0),
        "contract_score": _safe_float(row.get("contract_score", merged.get("contract_score")), 0.0),
    }


def _option_entry_premium(row: Dict[str, Any]) -> float:
    option = _safe_dict(row.get("option"))
    contract = _safe_dict(row.get("contract"))
    pnl_meta = _safe_dict(row.get("pnl_meta"))
    close_audit = _safe_dict(row.get("close_audit"))

    value = _first_float(
        row,
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
            "debit",
            "price_paid",
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(pnl_meta, ["entry_premium"])
    if value is not None:
        return round(value, 4)

    value = _safe_optional_float(_nested(close_audit, "pnl_meta", "entry_premium"))
    if value is not None:
        return round(value, 4)

    value = _first_float(
        option,
        [
            "entry_premium",
            "premium_entry",
            "option_entry",
            "entry_price",
            "premium",
            "mark_at_entry",
            "fill_price",
            "executed_price",
            "selected_price_reference",
            "price_reference",
            "mark",
            "ask",
            "last",
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(
        contract,
        [
            "entry_premium",
            "premium_entry",
            "option_entry",
            "entry_price",
            "selected_price_reference",
            "price_reference",
            "mark",
            "ask",
            "last",
        ],
    )
    if value is not None:
        return round(value, 4)

    # Legacy compatibility: for OPTION rows only, entry/entry_price may be premium.
    return round(
        _safe_float(row.get("entry", row.get("entry_price", row.get("price", 0.0))), 0.0),
        4,
    )


def _option_current_premium(row: Dict[str, Any]) -> float:
    option = _safe_dict(row.get("option"))
    contract = _safe_dict(row.get("contract"))
    monitor_debug = _safe_dict(row.get("monitor_debug"))

    value = _first_float(
        row,
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
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(monitor_debug, ["current_premium", "current_option_mark"])
    if value is not None:
        return round(value, 4)

    value = _first_float(
        option,
        [
            "current_premium",
            "premium_current",
            "current_option_mark",
            "option_current_mark",
            "current_mark",
            "mark",
            "selected_price_reference",
            "price_reference",
            "last",
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(
        contract,
        [
            "current_premium",
            "premium_current",
            "current_option_mark",
            "option_current_mark",
            "current_mark",
            "mark",
            "selected_price_reference",
            "price_reference",
            "last",
        ],
    )
    if value is not None:
        return round(value, 4)

    # Legacy compatibility: for OPTION rows after our fixes, current_price is premium-safe.
    return round(_safe_float(row.get("current_price", 0.0), 0.0), 4)


def _option_exit_premium(row: Dict[str, Any]) -> float:
    pnl_meta = _safe_dict(row.get("pnl_meta"))
    close_audit = _safe_dict(row.get("close_audit"))

    value = _first_float(
        row,
        [
            "exit_premium",
            "premium_exit",
            "option_exit_price",
            "exit_option_mark",
            "close_premium",
            "exit_price",
            "close_price",
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(pnl_meta, ["exit_premium"])
    if value is not None:
        return round(value, 4)

    value = _safe_optional_float(_nested(close_audit, "pnl_meta", "exit_premium"))
    if value is not None:
        return round(value, 4)

    return 0.0


def _underlying_price(row: Dict[str, Any]) -> float:
    monitor_debug = _safe_dict(row.get("monitor_debug"))

    value = _first_float(
        row,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "last_underlying_price",
        ],
    )
    if value is not None:
        return round(value, 4)

    value = _first_float(monitor_debug, ["underlying_price", "current_underlying_price"])
    if value is not None:
        return round(value, 4)

    return 0.0


def _stock_entry_price(row: Dict[str, Any]) -> float:
    return round(
        _safe_float(
            row.get(
                "entry",
                row.get("entry_price", row.get("avg_entry", row.get("average_entry", row.get("price", 0.0)))),
            ),
            0.0,
        ),
        4,
    )


def _stock_current_price(row: Dict[str, Any]) -> float:
    return round(
        _safe_float(
            row.get(
                "current_price",
                row.get("current_underlying_price", row.get("underlying_price", row.get("market_price", 0.0))),
            ),
            0.0,
        ),
        4,
    )


def _stock_exit_price(row: Dict[str, Any]) -> float:
    return round(_safe_float(row.get("exit_price", row.get("close_price", 0.0)), 0.0), 4)


def _contracts(row: Dict[str, Any]) -> int:
    pnl_meta = _safe_dict(row.get("pnl_meta"))
    value = row.get("contracts", row.get("contract_count", row.get("quantity", row.get("qty", None))))
    if value is None:
        value = pnl_meta.get("contracts")
    return _safe_int(value, 0)


def _shares(row: Dict[str, Any]) -> int:
    value = row.get("shares", row.get("quantity", row.get("qty", None)))
    return _safe_int(value, 0)


def _pnl_basis(row: Dict[str, Any], vehicle: str) -> str:
    pnl_meta = _safe_dict(row.get("pnl_meta"))

    value = _safe_str(row.get("pnl_basis"), "")
    if value:
        return value

    value = _safe_str(pnl_meta.get("pnl_basis"), "")
    if value:
        return value

    if vehicle == "OPTION":
        return "option_premium_x_100"

    return "stock_price_x_shares"


def _pnl_pct(row: Dict[str, Any]) -> float:
    pnl_meta = _safe_dict(row.get("pnl_meta"))
    close_audit = _safe_dict(row.get("close_audit"))

    value = _safe_optional_float(row.get("pnl_pct"))
    if value is not None:
        return round(value, 4)

    value = _safe_optional_float(pnl_meta.get("pnl_pct"))
    if value is not None:
        return round(value, 4)

    value = _safe_optional_float(_nested(close_audit, "pnl_meta", "pnl_pct"))
    if value is not None:
        return round(value, 4)

    return 0.0


# =============================================================================
# Flatten row
# =============================================================================

def _flatten_journal_row(row: Dict[str, Any]) -> Dict[str, Any]:
    row = _safe_dict(row)

    summary = _safe_dict(row.get("summary"))
    monitor_debug = _safe_dict(row.get("monitor_debug"))
    close_audit = _safe_dict(row.get("close_audit"))
    pnl_meta = _safe_dict(row.get("pnl_meta"))
    capital_release_meta = _safe_dict(row.get("capital_release_meta"))

    vehicle = _detect_vehicle(row)
    contract = _extract_contract(row)

    if vehicle == "OPTION":
        entry_price = 0.0
        current_price = 0.0
        exit_price = 0.0

        entry_premium = _option_entry_premium(row)
        current_premium = _option_current_premium(row)
        exit_premium = _option_exit_premium(row)

        option_stop = round(_safe_float(row.get("option_stop", row.get("premium_stop", row.get("stop", 0.0))), 0.0), 4)
        option_target = round(_safe_float(row.get("option_target", row.get("premium_target", row.get("target", 0.0))), 0.0), 4)

        stock_stop = 0.0
        stock_target = 0.0

        underlying_price = _underlying_price(row)

        price_review_basis = _safe_str(row.get("price_review_basis"), "OPTION_PREMIUM_ONLY")
        monitoring_price_type = _safe_str(row.get("monitoring_price_type"), "OPTION_PREMIUM")
        underlying_used_for_close = False

    else:
        entry_price = _stock_entry_price(row)
        current_price = _stock_current_price(row)
        exit_price = _stock_exit_price(row)

        entry_premium = 0.0
        current_premium = 0.0
        exit_premium = 0.0
        option_stop = 0.0
        option_target = 0.0

        stock_stop = round(_safe_float(row.get("stop", row.get("stock_stop", 0.0)), 0.0), 4)
        stock_target = round(_safe_float(row.get("target", row.get("stock_target", 0.0)), 0.0), 4)

        underlying_price = current_price or _underlying_price(row)

        price_review_basis = _safe_str(row.get("price_review_basis"), "STOCK_PRICE")
        monitoring_price_type = _safe_str(row.get("monitoring_price_type"), "UNDERLYING")
        underlying_used_for_close = True

    return {
        # Identity
        "timestamp": _safe_str(row.get("timestamp"), ""),
        "opened_at": _safe_str(row.get("opened_at", row.get("created_at")), ""),
        "closed_at": _safe_str(row.get("closed_at", row.get("exit_time")), ""),
        "journal_type": _safe_str(row.get("journal_type"), ""),
        "status": _safe_str(row.get("status"), ""),
        "trade_id": _safe_str(row.get("trade_id"), ""),
        "symbol": _safe_str(row.get("symbol"), ""),
        "strategy": _safe_str(row.get("strategy"), ""),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,

        # Contract identity
        "contract_symbol": _safe_str(contract.get("contract_symbol"), ""),
        "expiry": _safe_str(contract.get("expiry"), ""),
        "right": _safe_str(contract.get("right"), ""),
        "strike": _round4(contract.get("strike")),
        "contracts": _contracts(row),
        "shares": _shares(row),

        # Option market quality
        "option_bid": _round4(contract.get("bid")),
        "option_ask": _round4(contract.get("ask")),
        "option_last": _round4(contract.get("last")),
        "option_mark": _round4(contract.get("mark")),
        "option_volume": _safe_int(contract.get("volume"), 0),
        "option_open_interest": _safe_int(contract.get("open_interest"), 0),
        "option_implied_volatility": _round4(contract.get("implied_volatility")),
        "option_contract_score": _round4(contract.get("contract_score")),

        # Separated stock versus option prices
        "entry_price": entry_price,
        "current_price": current_price,
        "exit_price": exit_price,
        "entry_premium": entry_premium,
        "current_premium": current_premium,
        "exit_premium": exit_premium,
        "underlying_price": underlying_price,
        "current_underlying_price": underlying_price,

        # Separated risk levels
        "stock_stop": stock_stop,
        "stock_target": stock_target,
        "option_stop": option_stop,
        "option_target": option_target,

        # Legacy compatibility columns
        "legacy_entry": _round4(row.get("entry")),
        "legacy_current_price": _round4(row.get("current_price")),
        "legacy_option_current_price": _round4(row.get("option_current_price")),
        "legacy_stop": _round4(row.get("stop")),
        "legacy_target": _round4(row.get("target")),

        # PnL
        "pnl": round(_safe_float(row.get("pnl", row.get("realized_pnl", 0.0)), 0.0), 4),
        "realized_pnl": round(_safe_float(row.get("realized_pnl", row.get("pnl", 0.0)), 0.0), 4),
        "unrealized_pnl": round(_safe_float(row.get("unrealized_pnl", 0.0), 0.0), 4),
        "pnl_pct": _pnl_pct(row),
        "pnl_basis": _pnl_basis(row, vehicle),

        # Price basis audit
        "monitoring_price_type": monitoring_price_type,
        "price_review_basis": price_review_basis,
        "underlying_price_used_for_close_decision": underlying_used_for_close,
        "exit_price_source": _safe_str(row.get("exit_price_source"), ""),
        "option_price_source": _safe_str(row.get("option_price_source"), ""),
        "option_underlying_leak_blocked": _safe_str(
            row.get(
                "option_underlying_leak_blocked",
                row.get("option_underlying_leak_blocked_on_close", ""),
            ),
            "",
        ),

        # Decision / close reason
        "close_reason": _safe_str(row.get("close_reason", row.get("reason")), ""),
        "final_reason": _safe_str(row.get("final_reason"), ""),
        "summary_status": _safe_str(summary.get("status"), ""),
        "summary_final_reason_code": _safe_str(summary.get("final_reason_code"), ""),
        "monitor_action": _safe_str(row.get("monitor_action", monitor_debug.get("final_action")), ""),
        "monitor_days_open": round(_safe_float(monitor_debug.get("days_open", 0.0), 0.0), 4),
        "monitor_pct_change": round(_safe_float(monitor_debug.get("pct_change", 0.0), 0.0), 4),
        "monitor_progress_to_target": round(_safe_float(monitor_debug.get("progress_to_target", 0.0), 0.0), 4),

        # Scores / explainability
        "readiness_score": round(_safe_float(row.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(row.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(row.get("rebuild_pressure", 0.0), 0.0), 4),
        "v2_score": round(_safe_float(row.get("v2_score", 0.0), 0.0), 4),
        "v2_reason": _safe_str(row.get("v2_reason"), ""),

        # Capital / audit blobs
        "capital_release_basis": _safe_str(capital_release_meta.get("capital_release_basis"), ""),
        "capital_release_meta": _json_blob(capital_release_meta),
        "pnl_meta": _json_blob(pnl_meta),
        "close_audit": _json_blob(close_audit),
        "exit_explanation": _json_blob(row.get("exit_explanation")),
    }


FIELDNAMES = [
    # Identity
    "timestamp",
    "opened_at",
    "closed_at",
    "journal_type",
    "status",
    "trade_id",
    "symbol",
    "strategy",
    "vehicle",
    "vehicle_selected",

    # Contract identity
    "contract_symbol",
    "expiry",
    "right",
    "strike",
    "contracts",
    "shares",

    # Option market quality
    "option_bid",
    "option_ask",
    "option_last",
    "option_mark",
    "option_volume",
    "option_open_interest",
    "option_implied_volatility",
    "option_contract_score",

    # Separated prices
    "entry_price",
    "current_price",
    "exit_price",
    "entry_premium",
    "current_premium",
    "exit_premium",
    "underlying_price",
    "current_underlying_price",

    # Separated risk
    "stock_stop",
    "stock_target",
    "option_stop",
    "option_target",

    # Legacy compatibility
    "legacy_entry",
    "legacy_current_price",
    "legacy_option_current_price",
    "legacy_stop",
    "legacy_target",

    # PnL
    "pnl",
    "realized_pnl",
    "unrealized_pnl",
    "pnl_pct",
    "pnl_basis",

    # Price basis audit
    "monitoring_price_type",
    "price_review_basis",
    "underlying_price_used_for_close_decision",
    "exit_price_source",
    "option_price_source",
    "option_underlying_leak_blocked",

    # Decision / close reason
    "close_reason",
    "final_reason",
    "summary_status",
    "summary_final_reason_code",
    "monitor_action",
    "monitor_days_open",
    "monitor_pct_change",
    "monitor_progress_to_target",

    # Scores
    "readiness_score",
    "promotion_score",
    "rebuild_pressure",
    "v2_score",
    "v2_reason",

    # Audit blobs
    "capital_release_basis",
    "capital_release_meta",
    "pnl_meta",
    "close_audit",
    "exit_explanation",
]


def export_trade_journal(path: str = EXPORT_FILE, refresh_snapshot: bool = True) -> str:
    if refresh_snapshot:
        rows = write_trade_journal_snapshot()
    else:
        rows = read_trade_journal()

    rows = _safe_list(rows)
    flattened = [_flatten_journal_row(row) for row in rows if isinstance(row, dict)]

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in flattened:
            writer.writerow(row)

    print(f"Journal exported: {p}")
    return str(p)


# Compatibility alias
export_journal = export_trade_journal


if __name__ == "__main__":
    export_trade_journal()
