from __future__ import annotations

"""
🔭 Observatory Journal History Cleaner

Purpose:
- Keep active trading data clean.
- Preserve old bad/manual/test rows for audit.
- Mark historical bad option closes clearly so they do not scare the active safety report.
- Do not delete user history.
- Do not touch open positions.
- Do not include quarantined/manual/test rows in official performance.

This module is intentionally separate from trade_journal_export.py.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple


CLOSED_FILE = "data/closed_positions.json"
TRADE_LOG_FILE = "data/trade_log.json"
EXPORT_FILE = "data/trade_journal_export.csv"
AUDIT_FILE = "data/quarantined_trade_audit.json"
BACKUP_ROOT = "data/_journal_history_cleaner_backups"

BAD_CLOSE_CLASSIFICATION = "QUARANTINED_BAD_CLOSE"
MANUAL_TEST_CLASSIFICATION = "MANUAL_TEST"
CONTROLLED_RELEASE_CLASSIFICATION = "CONTROLLED_RELEASE"
REAL_TRADE_CLASSIFICATION = "REAL_TRADE"

HISTORICAL_WARNING_BUCKET = "HISTORICAL_WARNING"
CLEAN_HISTORY_BUCKET = "CLEAN_HISTORY"
ACTIVE_OK_BUCKET = "ACTIVE_OK"
MANUAL_TEST_BUCKET = "MANUAL_TEST"
CONTROLLED_RELEASE_BUCKET = "CONTROLLED_RELEASE"
REAL_TRADE_BUCKET = "REAL_TRADE"


def _now_iso() -> str:
    return datetime.now().isoformat()


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


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


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if not value:
                return float(default)
        return float(value)
    except Exception:
        return float(default)


def _load_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path_str: str, payload: Any) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    tmp.replace(path)


def _backup_files() -> Dict[str, Any]:
    backup_dir = Path(BACKUP_ROOT) / _stamp()
    backup_dir.mkdir(parents=True, exist_ok=True)

    backed_up: List[Dict[str, Any]] = []
    missing: List[str] = []

    for path_str in [CLOSED_FILE, TRADE_LOG_FILE, EXPORT_FILE, AUDIT_FILE]:
        src = Path(path_str)
        if not src.exists():
            missing.append(path_str)
            continue

        dst = backup_dir / path_str
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        backed_up.append({
            "source": path_str,
            "backup": str(dst),
            "size_bytes": dst.stat().st_size,
        })

    return {
        "backup_dir": str(backup_dir),
        "backed_up": backed_up,
        "missing": missing,
    }


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
                    row.get("contractSymbol", option.get("contractSymbol", contract.get("contractSymbol", ""))),
                ),
            ),
        ),
        "",
    )

    right = _upper(
        row.get(
            "right",
            row.get("option_type", row.get("call_put", option.get("right", contract.get("right", "")))),
        ),
        "",
    )

    if contract_symbol or option or contract or right in {"CALL", "PUT", "C", "P"}:
        return "OPTION"

    return raw or "UNKNOWN"


def _status(row: Dict[str, Any]) -> str:
    status = _upper(row.get("status", row.get("position_status", row.get("execution_status", ""))), "")
    if status:
        return status

    if row.get("closed_at") or row.get("close_reason"):
        return "CLOSED"

    if row.get("opened_at"):
        return "OPEN"

    return "UNKNOWN"


def _reason_text(row: Dict[str, Any]) -> str:
    pieces = [
        row.get("reason"),
        row.get("close_reason"),
        row.get("classification_reason"),
        row.get("final_reason"),
        row.get("final_reason_code"),
        row.get("exit_price_source"),
        row.get("journal_warning"),
    ]
    return " ".join(_safe_str(x, "") for x in pieces).lower()


def _has_underlying_leak_warning(row: Dict[str, Any]) -> bool:
    if _safe_bool(row.get("option_underlying_leak_blocked"), False):
        return True
    if _safe_bool(row.get("option_underlying_leak_blocked_on_close"), False):
        return True
    if "underlying_leak" in _reason_text(row):
        return True
    if _vehicle(row) == "OPTION" and _safe_bool(row.get("underlying_price_used_for_pnl"), False):
        return True
    if _vehicle(row) == "OPTION" and _safe_bool(row.get("underlying_price_used_for_close_decision"), False):
        return True
    return False


def _is_manual_or_test(row: Dict[str, Any]) -> bool:
    text = _reason_text(row)
    classification = _upper(row.get("performance_classification"), "")
    if classification == MANUAL_TEST_CLASSIFICATION:
        return True
    return (
        "manual_option_premium_test" in text
        or "manual_test" in text
        or text.endswith("_test")
        or "testclose" in _safe_str(row.get("symbol"), "").lower()
    )


def _is_controlled_release(row: Dict[str, Any]) -> bool:
    text = _reason_text(row)
    classification = _upper(row.get("performance_classification"), "")
    if classification == CONTROLLED_RELEASE_CLASSIFICATION:
        return True
    return "controlled_release" in text or "slot_release" in text


def _is_open_row(row: Dict[str, Any]) -> bool:
    return _status(row) == "OPEN"


def _is_closed_row(row: Dict[str, Any]) -> bool:
    return _status(row) == "CLOSED"


def _trade_identity(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "trade_id": _safe_str(row.get("trade_id"), ""),
        "symbol": _upper(row.get("symbol"), "UNKNOWN"),
        "vehicle": _vehicle(row),
        "status": _status(row),
        "pnl": round(_safe_float(row.get("pnl", row.get("realized_pnl", 0.0)), 0.0), 2),
        "opened_at": _safe_str(row.get("opened_at"), ""),
        "closed_at": _safe_str(row.get("closed_at"), ""),
        "reason": _safe_str(row.get("reason", row.get("close_reason", "")), ""),
    }


def _classification_for_row(row: Dict[str, Any]) -> Tuple[str, str, bool, bool]:
    """
    Returns:
        classification, audit_bucket, performance_include, needs_review
    """
    if _is_open_row(row):
        return "", ACTIVE_OK_BUCKET, False, False

    if _is_manual_or_test(row):
        return MANUAL_TEST_CLASSIFICATION, MANUAL_TEST_BUCKET, False, False

    if _is_controlled_release(row):
        return CONTROLLED_RELEASE_CLASSIFICATION, CONTROLLED_RELEASE_BUCKET, False, False

    if _has_underlying_leak_warning(row):
        return BAD_CLOSE_CLASSIFICATION, HISTORICAL_WARNING_BUCKET, False, False

    existing = _upper(row.get("performance_classification"), "")

    if existing == BAD_CLOSE_CLASSIFICATION:
        return BAD_CLOSE_CLASSIFICATION, HISTORICAL_WARNING_BUCKET, False, False

    if existing == REAL_TRADE_CLASSIFICATION:
        return REAL_TRADE_CLASSIFICATION, REAL_TRADE_BUCKET, True, False

    if _is_closed_row(row):
        # Do not blindly promote old rows unless they were already counted by strategy_performance.
        include = _safe_bool(
            row.get("performance_include", row.get("include_in_performance", row.get("counts_in_performance", False))),
            False,
        )
        if include:
            return REAL_TRADE_CLASSIFICATION, REAL_TRADE_BUCKET, True, False
        return existing or "", CLEAN_HISTORY_BUCKET, False, False

    return existing or "", CLEAN_HISTORY_BUCKET, False, False


def _apply_classification(row: Dict[str, Any], *, source_file: str) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
    original = dict(row)
    updated = dict(row)

    classification, bucket, include, needs_review = _classification_for_row(updated)

    changed = False

    def set_if_different(key: str, value: Any) -> None:
        nonlocal changed
        if updated.get(key) != value:
            updated[key] = value
            changed = True

    if classification:
        set_if_different("performance_classification", classification)
        set_if_different("performance_include", include)
        set_if_different("include_in_performance", include)
        set_if_different("counts_in_performance", include)
        set_if_different("needs_review", needs_review)

    set_if_different("journal_audit_bucket", bucket)

    if bucket == HISTORICAL_WARNING_BUCKET:
        set_if_different("historical_warning", True)
        set_if_different("active_safety_issue", False)
        set_if_different("classification_reason", updated.get("classification_reason") or "historical_bad_option_close_quarantined")
        set_if_different("official_performance_note", "Excluded from official performance; retained for audit history.")
    elif bucket in {MANUAL_TEST_BUCKET, CONTROLLED_RELEASE_BUCKET}:
        set_if_different("historical_warning", False)
        set_if_different("active_safety_issue", False)
        set_if_different("official_performance_note", "Excluded from official performance by design.")
        if not updated.get("classification_reason"):
            set_if_different("classification_reason", "manual_or_controlled_non_performance_row")
    elif bucket == REAL_TRADE_BUCKET:
        set_if_different("historical_warning", False)
        set_if_different("active_safety_issue", False)
        set_if_different("official_performance_note", "Included in official filtered performance.")
        if not updated.get("classification_reason"):
            set_if_different("classification_reason", "verified_real_trade")
    else:
        set_if_different("historical_warning", False)
        set_if_different("active_safety_issue", False)

    if changed:
        set_if_different("journal_history_cleaned_by", "engine.journal_history_cleaner")
        set_if_different("journal_history_cleaned_at", _now_iso())

    audit_row = {
        "source_file": source_file,
        "changed": changed,
        "before": _trade_identity(original),
        "after": _trade_identity(updated),
        "classification": updated.get("performance_classification", ""),
        "journal_audit_bucket": updated.get("journal_audit_bucket", ""),
        "performance_include": updated.get("performance_include", False),
        "classification_reason": updated.get("classification_reason", ""),
    }

    return updated, changed, audit_row


def _clean_rows(rows: List[Any], *, source_file: str) -> Tuple[List[Any], int, List[Dict[str, Any]]]:
    cleaned: List[Any] = []
    changed_count = 0
    audit_rows: List[Dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            cleaned.append(row)
            continue

        updated, changed, audit = _apply_classification(row, source_file=source_file)
        cleaned.append(updated)

        if changed:
            changed_count += 1
            audit_rows.append(audit)

    return cleaned, changed_count, audit_rows


def clean_journal_history(*, write: bool = True, make_backup: bool = True) -> Dict[str, Any]:
    backup = _backup_files() if make_backup else {
        "backup_dir": "",
        "backed_up": [],
        "missing": [],
    }

    closed_rows = _safe_list(_load_json(CLOSED_FILE, []))
    trade_log_rows = _safe_list(_load_json(TRADE_LOG_FILE, []))

    cleaned_closed, changed_closed, closed_audit = _clean_rows(
        closed_rows,
        source_file=CLOSED_FILE,
    )
    cleaned_trade_log, changed_trade_log, trade_log_audit = _clean_rows(
        trade_log_rows,
        source_file=TRADE_LOG_FILE,
    )

    audit_payload = {
        "cleaned_at": _now_iso(),
        "backup": backup,
        "write": bool(write),
        "changed_closed_positions": changed_closed,
        "changed_trade_log_rows": changed_trade_log,
        "total_changed": changed_closed + changed_trade_log,
        "audit_rows": closed_audit + trade_log_audit,
        "note": "Rows were labeled for audit/performance filtering. No rows were deleted.",
    }

    if write:
        _write_json(CLOSED_FILE, cleaned_closed)
        _write_json(TRADE_LOG_FILE, cleaned_trade_log)
        _write_json(AUDIT_FILE, audit_payload)

    return audit_payload


def preview_journal_history_cleaning() -> Dict[str, Any]:
    return clean_journal_history(write=False, make_backup=False)


def print_journal_history_cleaning_result(result: Dict[str, Any]) -> None:
    result = _safe_dict(result)

    print("")
    print("=" * 80)
    print("JOURNAL HISTORY CLEANER RESULT")
    print("=" * 80)
    print("Write:", result.get("write"))
    print("Changed closed positions:", result.get("changed_closed_positions"))
    print("Changed trade_log rows:", result.get("changed_trade_log_rows"))
    print("Total changed:", result.get("total_changed"))

    backup = _safe_dict(result.get("backup"))
    if backup:
        print("Backup dir:", backup.get("backup_dir"))

    print("Audit file:", AUDIT_FILE)
    print("Note:", result.get("note"))
    print("=" * 80)


def run_journal_history_cleaner() -> Dict[str, Any]:
    result = clean_journal_history(write=True, make_backup=True)
    print_journal_history_cleaning_result(result)
    return result


def main() -> None:
    run_journal_history_cleaner()


if __name__ == "__main__":
    main()


__all__ = [
    "clean_journal_history",
    "preview_journal_history_cleaning",
    "print_journal_history_cleaning_result",
    "run_journal_history_cleaner",
    "main",
]
