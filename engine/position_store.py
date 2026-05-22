# ==============================================================================
# OBSERVATORY POSITION STORE
# ==============================================================================
# Canonical active-book helper for The Observatory.
#
# Purpose:
# - Keep active position books aligned.
# - Prevent close/entry code from writing only one active book.
# - Preserve option premium fields.
# - Remove closed trades from all active books.
# - Keep controlled/test rows out of active books after test cleanup.
#
# Active books:
# - data/open_positions.json
# - data/positions.json
# - data/user_positions.json
#
# Closed book:
# - data/closed_positions.json
# ==============================================================================

from __future__ import annotations

import json
import os
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

OPEN_POSITIONS_FILE = DATA_DIR / "open_positions.json"
POSITIONS_FILE = DATA_DIR / "positions.json"
USER_POSITIONS_FILE = DATA_DIR / "user_positions.json"
CLOSED_POSITIONS_FILE = DATA_DIR / "closed_positions.json"

ACTIVE_BOOK_FILES = [
    OPEN_POSITIONS_FILE,
    POSITIONS_FILE,
    USER_POSITIONS_FILE,
]

OPTION_VEHICLES = {"OPTION", "OPTIONS", "CALL_OPTION", "PUT_OPTION"}

CONTROLLED_MARKERS = (
    "CONTROLLED",
    "TEST",
    "TESTOPT",
    "TESTREAL",
    "TESTCLOSE",
    "TESTCLOSEFN",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_upper(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return text.upper()


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return int(float(value))
    except Exception:
        return default


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return deepcopy(default)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return deepcopy(default)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def backup_position_books(label: str = "position_store_backup") -> Dict[str, str]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups: Dict[str, str] = {}

    for path in ACTIVE_BOOK_FILES + [CLOSED_POSITIONS_FILE]:
        if not path.exists():
            continue
        backup = path.with_suffix(path.suffix + f".backup_{label}_{stamp}")
        shutil.copy2(path, backup)
        backups[str(path)] = str(backup)

    return backups


def load_rows(path: Path, default: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    default_rows: List[Dict[str, Any]] = default if default is not None else []
    data = _read_json(path, default_rows)

    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]

    if isinstance(data, dict):
        for key in ("positions", "open_positions", "rows", "data", "closed_positions"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]

    return deepcopy(default_rows)


def save_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    clean = [row for row in rows if isinstance(row, dict)]
    _write_json(path, clean)


def load_active_positions(prefer: Optional[Path] = None) -> List[Dict[str, Any]]:
    candidates = [prefer] if prefer else []
    candidates += ACTIVE_BOOK_FILES

    seen_files = set()
    best_rows: List[Dict[str, Any]] = []

    for path in candidates:
        if not path:
            continue
        path = Path(path)
        if path in seen_files:
            continue
        seen_files.add(path)

        rows = load_rows(path, [])
        if len(rows) > len(best_rows):
            best_rows = rows

    return normalize_active_positions(best_rows)


def load_closed_positions() -> List[Dict[str, Any]]:
    return load_rows(CLOSED_POSITIONS_FILE, [])


def _trade_id(row: Dict[str, Any]) -> str:
    return str(row.get("trade_id") or row.get("id") or row.get("order_id") or "").strip()


def _symbol(row: Dict[str, Any]) -> str:
    return _safe_upper(row.get("symbol") or row.get("ticker") or "")


def _is_option(row: Dict[str, Any]) -> bool:
    # OBSERVATORY_POSITION_STORE_EXPLICIT_STOCK_CLASSIFIER_REPAIR_20260522
    # Explicit STOCK rows must remain STOCK even if they carry rejected option
    # research fields such as option, contract_symbol, option_symbol, or contract.
    vehicle = _safe_upper(
        row.get("vehicle")
        or row.get("vehicle_selected")
        or row.get("selected_vehicle")
        or row.get("asset_type")
        or row.get("instrument_type")
        or ""
    )

    if vehicle in {"STOCK", "EQUITY", "SHARES"}:
        return False

    if vehicle in OPTION_VEHICLES:
        return True

    # If a stock fallback marker is present, this is a stock row carrying
    # rejected option context, not an option position.
    if (
        bool(row.get("stock_fallback_from_option_research"))
        or bool(row.get("option_fallback_used"))
        or str(row.get("final_reason") or "").strip() == "stock_fallback_position_entered"
        or str(row.get("execution_birth_reason") or "").strip() == "stock_fallback_position_entered"
    ):
        return False

    if row.get("contract_symbol") or row.get("option_symbol") or row.get("contractSymbol"):
        return True

    if row.get("entry_premium") is not None or row.get("current_premium") is not None:
        return True

    return False


def _is_controlled_or_test(row: Dict[str, Any]) -> bool:
    text = " ".join(
        str(row.get(key, ""))
        for key in (
            "trade_id",
            "symbol",
            "classification",
            "journal_audit_bucket",
            "controlled_test_label",
            "reason",
            "close_reason",
        )
    ).upper()

    if bool(row.get("controlled_test")) or bool(row.get("test_record")):
        return True

    return any(marker in text for marker in CONTROLLED_MARKERS)


def _status(row: Dict[str, Any]) -> str:
    return _safe_upper(
        row.get("status")
        or row.get("position_status")
        or row.get("execution_status")
        or row.get("lifecycle_state")
        or row.get("lifecycle_stage")
        or "OPEN"
    )


def normalize_option_position(row: Dict[str, Any]) -> Dict[str, Any]:
    pos = deepcopy(row)

    vehicle = "OPTION"
    pos["vehicle"] = vehicle
    pos["vehicle_selected"] = vehicle
    pos["selected_vehicle"] = vehicle
    pos["asset_type"] = vehicle
    pos["instrument_type"] = vehicle

    contracts = _safe_int(
        pos.get("contracts")
        or pos.get("contract_count")
        or pos.get("quantity")
        or pos.get("qty")
        or pos.get("size"),
        1,
    )
    if contracts <= 0:
        contracts = 1

    pos["contracts"] = contracts
    pos["contract_count"] = contracts
    pos["quantity"] = contracts
    pos["shares"] = 0

    entry_premium = _safe_float(
        pos.get("entry_premium")
        or pos.get("premium_entry")
        or pos.get("option_entry")
        or pos.get("contract_entry_price")
        or pos.get("entry")
        or pos.get("entry_price")
        or pos.get("fill_price")
        or pos.get("filled_price"),
        None,
    )

    current_premium = _safe_float(
        pos.get("current_premium")
        or pos.get("premium_current")
        or pos.get("current_option_mark")
        or pos.get("option_current_price")
        or pos.get("option_mark")
        or pos.get("mark")
        or pos.get("current")
        or pos.get("current_price")
        or entry_premium,
        entry_premium,
    )

    if entry_premium is not None:
        pos["entry"] = entry_premium
        pos["entry_price"] = entry_premium
        pos["fill_price"] = entry_premium
        pos["filled_price"] = entry_premium
        pos["entry_premium"] = entry_premium
        pos["premium_entry"] = entry_premium
        pos["option_entry"] = entry_premium
        pos["contract_entry_price"] = entry_premium

    if current_premium is not None:
        pos["current"] = current_premium
        pos["current_price"] = current_premium
        pos["current_premium"] = current_premium
        pos["premium_current"] = current_premium
        pos["current_option_mark"] = current_premium
        pos["option_current_price"] = current_premium

    stop = _safe_float(
        pos.get("premium_stop")
        or pos.get("option_stop")
        or pos.get("stop_premium")
        or pos.get("stop_loss_premium")
        or pos.get("stop")
        or pos.get("stop_loss"),
        None,
    )

    target = _safe_float(
        pos.get("premium_target")
        or pos.get("option_target")
        or pos.get("target_premium")
        or pos.get("take_profit_premium")
        or pos.get("target")
        or pos.get("take_profit"),
        None,
    )

    if stop is not None:
        pos["stop"] = stop
        pos["stop_loss"] = stop
        pos["option_stop"] = stop
        pos["premium_stop"] = stop
        pos["stop_premium"] = stop
        pos["stop_loss_premium"] = stop

    if target is not None:
        pos["target"] = target
        pos["take_profit"] = target
        pos["option_target"] = target
        pos["premium_target"] = target
        pos["target_premium"] = target
        pos["take_profit_premium"] = target

    contract_symbol = (
        pos.get("contract_symbol")
        or pos.get("option_symbol")
        or pos.get("contractSymbol")
        or pos.get("selected_contract_symbol")
    )
    if contract_symbol:
        pos["contract_symbol"] = contract_symbol
        pos["option_symbol"] = contract_symbol
        pos["contractSymbol"] = contract_symbol

    expiry = pos.get("expiry") or pos.get("expiration") or pos.get("contract_expiry") or pos.get("expiration_date")
    if expiry:
        pos["expiry"] = expiry
        pos["expiration"] = expiry
        pos["contract_expiry"] = expiry
        pos["expiration_date"] = expiry

    right = _safe_upper(pos.get("right") or pos.get("call_put") or pos.get("option_type") or pos.get("strategy") or "CALL", "CALL")
    if right not in {"CALL", "PUT"}:
        right = "CALL"

    pos["right"] = right
    pos["call_put"] = right
    pos["option_type"] = right

    strike = _safe_float(pos.get("strike") or pos.get("strike_price"), None)
    if strike is not None:
        pos["strike"] = strike
        pos["strike_price"] = strike

    pos["monitoring_price_type"] = "OPTION_PREMIUM"
    pos["monitoring_mode"] = "OPTION_PREMIUM"
    pos["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    pos["price_basis"] = "OPTION_PREMIUM"
    pos["pnl_basis"] = pos.get("pnl_basis") or "option_premium_x_100"
    pos["underlying_price_used_for_pnl"] = False
    pos["underlying_price_used_for_close_decision"] = False
    pos["execution_position_shape"] = "OPTION_PREMIUM_POSITION"

    if entry_premium is not None:
        pos["cost_basis"] = round(entry_premium * 100 * contracts, 4)
        pos["actual_cost"] = pos.get("actual_cost") or pos["cost_basis"]
        pos["capital_required"] = pos.get("capital_required") or pos["cost_basis"]
        pos["minimum_trade_cost"] = pos.get("minimum_trade_cost") or pos["actual_cost"]

    return pos


def normalize_stock_position(row: Dict[str, Any]) -> Dict[str, Any]:
    pos = deepcopy(row)

    vehicle = "STOCK"
    pos["vehicle"] = vehicle
    pos["vehicle_selected"] = vehicle
    pos["selected_vehicle"] = vehicle
    pos["asset_type"] = vehicle

    shares = _safe_int(
        pos.get("shares")
        or pos.get("quantity")
        or pos.get("qty")
        or pos.get("size"),
        1,
    )
    if shares <= 0:
        shares = 1

    pos["shares"] = shares
    pos["quantity"] = shares
    pos["contracts"] = 0
    pos["contract_count"] = 0

    entry = _safe_float(
        pos.get("entry")
        or pos.get("entry_price")
        or pos.get("fill_price")
        or pos.get("filled_price"),
        None,
    )

    current = _safe_float(
        pos.get("current")
        or pos.get("current_price")
        or pos.get("underlying_price")
        or entry,
        entry,
    )

    if entry is not None:
        pos["entry"] = entry
        pos["entry_price"] = entry
        pos["fill_price"] = entry
        pos["filled_price"] = entry

    if current is not None:
        pos["current"] = current
        pos["current_price"] = current
        pos["underlying_price"] = current

    pos["entry_premium"] = None
    pos["current_premium"] = None
    pos["premium_entry"] = None
    pos["premium_current"] = None
    pos["monitoring_price_type"] = "UNDERLYING"
    pos["price_review_basis"] = "STOCK_PRICE"
    pos["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    if entry is not None:
        pos["cost_basis"] = round(entry * shares, 4)

    return pos


def normalize_position(row: Dict[str, Any]) -> Dict[str, Any]:
    pos = deepcopy(row)

    if not _trade_id(pos):
        symbol = _symbol(pos) or "UNKNOWN"
        stamp = str(pos.get("timestamp") or pos.get("opened_at") or _now_iso()).replace(":", "").replace("-", "")
        pos["trade_id"] = f"{symbol}-POSITION-{stamp}"

    if not _symbol(pos):
        pos["symbol"] = "UNKNOWN"
    else:
        pos["symbol"] = _symbol(pos)

    status = _status(pos)
    if status in {"", "SELECTED"}:
        status = "OPEN"

    pos["status"] = status
    pos["position_status"] = status

    if _is_option(pos):
        pos = normalize_option_position(pos)
    else:
        pos = normalize_stock_position(pos)

    pos["position_store_normalized_at"] = _now_iso()
    return pos


def normalize_active_positions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    seen: set = set()

    for row in rows or []:
        if not isinstance(row, dict):
            continue

        status = _status(row)
        if status in {"CLOSED", "EXITED", "REMOVED"}:
            continue

        pos = normalize_position(row)
        tid = _trade_id(pos)
        key = tid or f"{_symbol(pos)}::{len(normalized)}"

        if key in seen:
            continue

        seen.add(key)
        normalized.append(pos)

    return normalized


def save_active_positions(rows: Iterable[Dict[str, Any]], sync_all: bool = True) -> Dict[str, Any]:
    normalized = normalize_active_positions(rows)

    targets = ACTIVE_BOOK_FILES if sync_all else [OPEN_POSITIONS_FILE]
    written: Dict[str, int] = {}

    for path in targets:
        save_rows(path, normalized)
        written[str(path)] = len(normalized)

    return {
        "status": "saved",
        "active_count": len(normalized),
        "written": written,
        "synced_all_active_books": sync_all,
    }


def sync_active_books(prefer: Optional[Path] = None) -> Dict[str, Any]:
    rows = load_active_positions(prefer=prefer)
    result = save_active_positions(rows, sync_all=True)
    result["source_preference"] = str(prefer) if prefer else "largest_active_book"
    return result


def remove_trade_from_active_books(
    trade_id: str = "",
    symbol: str = "",
    reason: str = "removed",
    sync_all: bool = True,
) -> Dict[str, Any]:
    trade_id = str(trade_id or "").strip()
    symbol = _safe_upper(symbol)

    if not trade_id and not symbol:
        return {
            "status": "skipped",
            "removed": 0,
            "reason": "missing_trade_id_and_symbol",
        }

    before = load_active_positions()
    after: List[Dict[str, Any]] = []
    removed_rows: List[Dict[str, Any]] = []

    for row in before:
        row_tid = _trade_id(row)
        row_symbol = _symbol(row)

        match = False
        if trade_id and row_tid == trade_id:
            match = True
        elif symbol and row_symbol == symbol:
            match = True

        if match:
            closed_copy = deepcopy(row)
            closed_copy["status"] = "REMOVED_FROM_ACTIVE_BOOK"
            closed_copy["position_status"] = "REMOVED_FROM_ACTIVE_BOOK"
            closed_copy["active_book_removed_at"] = _now_iso()
            closed_copy["active_book_remove_reason"] = reason
            removed_rows.append(closed_copy)
        else:
            after.append(row)

    result = save_active_positions(after, sync_all=sync_all)

    return {
        "status": "removed" if removed_rows else "not_found",
        "removed": len(removed_rows),
        "trade_id": trade_id,
        "symbol": symbol,
        "active_count_before": len(before),
        "active_count_after": len(after),
        "save_result": result,
        "removed_rows": removed_rows,
    }


def purge_controlled_test_rows_from_active_books(sync_all: bool = True) -> Dict[str, Any]:
    before = load_active_positions()
    keep: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []

    for row in before:
        if _is_controlled_or_test(row):
            removed.append(row)
        else:
            keep.append(row)

    result = save_active_positions(keep, sync_all=sync_all)

    return {
        "status": "purged" if removed else "clean",
        "removed_count": len(removed),
        "active_count_before": len(before),
        "active_count_after": len(keep),
        "removed_trade_ids": [_trade_id(r) for r in removed],
        "save_result": result,
    }


def append_closed_position(row: Dict[str, Any], dedupe: bool = True) -> Dict[str, Any]:
    if not isinstance(row, dict):
        return {
            "status": "skipped",
            "reason": "closed_row_not_dict",
        }

    closed = deepcopy(row)
    closed["status"] = "CLOSED"
    closed["position_status"] = "CLOSED"
    closed["lifecycle_state"] = "CLOSED"
    closed["position_store_closed_at"] = closed.get("closed_at") or _now_iso()

    if _is_option(closed):
        closed = normalize_option_position(closed)

    rows = load_closed_positions()
    tid = _trade_id(closed)

    if dedupe and tid:
        rows = [r for r in rows if _trade_id(r) != tid]

    rows.append(closed)
    save_rows(CLOSED_POSITIONS_FILE, rows)

    return {
        "status": "closed_appended",
        "trade_id": tid,
        "closed_count": len(rows),
        "dedupe": dedupe,
    }


def active_book_alignment_report() -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "books": {},
        "aligned": True,
        "canonical_trade_ids": [],
        "mismatches": [],
    }

    canonical_ids: Optional[List[str]] = None

    for path in ACTIVE_BOOK_FILES:
        rows = load_rows(path, [])
        normalized = normalize_active_positions(rows)
        ids = sorted([_trade_id(row) for row in normalized if _trade_id(row)])

        report["books"][str(path)] = {
            "count": len(normalized),
            "trade_ids": ids,
            "symbols": sorted([_symbol(row) for row in normalized if _symbol(row)]),
        }

        if canonical_ids is None:
            canonical_ids = ids
            report["canonical_trade_ids"] = ids
        elif ids != canonical_ids:
            report["aligned"] = False
            report["mismatches"].append({
                "file": str(path),
                "trade_ids": ids,
                "expected": canonical_ids,
            })

    return report


def option_premium_safety_report() -> Dict[str, Any]:
    rows = load_active_positions()
    option_rows = [row for row in rows if _is_option(row)]

    audits: List[Dict[str, Any]] = []
    all_safe = True

    required = [
        "entry_premium",
        "current_premium",
        "premium_entry",
        "premium_current",
        "monitoring_price_type",
        "price_review_basis",
    ]

    for row in option_rows:
        missing = [key for key in required if row.get(key) in (None, "")]
        basis_ok = (
            row.get("monitoring_price_type") == "OPTION_PREMIUM"
            and row.get("price_review_basis") == "OPTION_PREMIUM_ONLY"
            and row.get("underlying_price_used_for_pnl") is False
        )

        if missing or not basis_ok:
            all_safe = False

        audits.append({
            "trade_id": _trade_id(row),
            "symbol": _symbol(row),
            "missing": missing,
            "basis_ok": basis_ok,
            "entry_premium": row.get("entry_premium"),
            "current_premium": row.get("current_premium"),
            "underlying_price_used_for_pnl": row.get("underlying_price_used_for_pnl"),
            "price_review_basis": row.get("price_review_basis"),
            "monitoring_price_type": row.get("monitoring_price_type"),
        })

    return {
        "option_count": len(option_rows),
        "all_option_rows_premium_safe": all_safe,
        "audits": audits,
    }


def health_report() -> Dict[str, Any]:
    alignment = active_book_alignment_report()
    option_safety = option_premium_safety_report()
    controlled = [row for row in load_active_positions() if _is_controlled_or_test(row)]

    return {
        "status": "PASS" if alignment["aligned"] and option_safety["all_option_rows_premium_safe"] and not controlled else "REVIEW",
        "books_aligned": alignment["aligned"],
        "alignment": alignment,
        "option_rows_premium_safe": option_safety["all_option_rows_premium_safe"],
        "option_safety": option_safety,
        "controlled_or_test_rows_open": len(controlled),
        "controlled_trade_ids": [_trade_id(row) for row in controlled],
    }


__all__ = [
    "ACTIVE_BOOK_FILES",
    "OPEN_POSITIONS_FILE",
    "POSITIONS_FILE",
    "USER_POSITIONS_FILE",
    "CLOSED_POSITIONS_FILE",
    "backup_position_books",
    "load_active_positions",
    "load_closed_positions",
    "save_active_positions",
    "sync_active_books",
    "remove_trade_from_active_books",
    "purge_controlled_test_rows_from_active_books",
    "append_closed_position",
    "normalize_position",
    "normalize_active_positions",
    "normalize_option_position",
    "active_book_alignment_report",
    "option_premium_safety_report",
    "health_report",
]
