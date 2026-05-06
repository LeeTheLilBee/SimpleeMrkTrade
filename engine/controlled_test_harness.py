from __future__ import annotations

"""
🔭 Observatory Controlled Test Harness

Purpose:
    Run dangerous paper-account tests without permanently polluting real data.

This module backs up the live Observatory data files, runs a controlled test,
then restores the original files automatically unless explicitly told not to.

Protected files:
    - data/account_state.json
    - data/open_positions.json
    - data/closed_positions.json
    - data/trade_log.json
    - data/trade_journal_export.csv

Main helpers:
    - backup_observatory_state()
    - restore_observatory_state()
    - controlled_observatory_state()
    - run_controlled_option_close_test()

Safety:
    By default, tests restore files even if the test errors.
"""

import csv
import json
import shutil
import traceback
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path("/content/SimpleeMrkTrade")

DATA_FILES = [
    "data/account_state.json",
    "data/open_positions.json",
    "data/closed_positions.json",
    "data/trade_log.json",
    "data/trade_journal_export.csv",
]

BACKUP_ROOT = PROJECT_ROOT / "data" / "_controlled_test_backups"


# =============================================================================
# Basic helpers
# =============================================================================

def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _now_iso() -> str:
    return datetime.now().isoformat()


def _path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path


def _safe_read_json(relative_path: str, default: Any) -> Any:
    path = _path(relative_path)
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_write_json(relative_path: str, payload: Any) -> None:
    path = _path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    tmp.replace(path)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


# =============================================================================
# Backup / restore
# =============================================================================

def backup_observatory_state(label: str = "controlled_test") -> Dict[str, Any]:
    """
    Copies protected data files into a timestamped backup folder.
    """
    stamp = _now_stamp()
    clean_label = str(label or "controlled_test").strip().replace(" ", "_")
    backup_dir = BACKUP_ROOT / f"{stamp}_{clean_label}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    copied: List[Dict[str, Any]] = []
    missing: List[str] = []

    for relative_path in DATA_FILES:
        source = _path(relative_path)
        destination = backup_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        if source.exists():
            shutil.copy2(source, destination)
            copied.append({
                "relative_path": relative_path,
                "source": str(source),
                "backup": str(destination),
                "size_bytes": source.stat().st_size,
            })
        else:
            missing.append(relative_path)

    manifest = {
        "created_at": _now_iso(),
        "label": clean_label,
        "project_root": str(PROJECT_ROOT),
        "backup_dir": str(backup_dir),
        "copied": copied,
        "missing": missing,
        "data_files": DATA_FILES,
    }

    with open(backup_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)

    return manifest


def restore_observatory_state(backup_dir: str) -> Dict[str, Any]:
    """
    Restores protected data files from a backup folder.
    """
    backup_path = Path(backup_dir)

    if not backup_path.exists():
        return {
            "restored": False,
            "reason": "backup_dir_not_found",
            "backup_dir": str(backup_path),
        }

    restored: List[Dict[str, Any]] = []
    missing: List[str] = []

    for relative_path in DATA_FILES:
        source = backup_path / relative_path
        destination = _path(relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        if source.exists():
            shutil.copy2(source, destination)
            restored.append({
                "relative_path": relative_path,
                "source": str(source),
                "restored_to": str(destination),
                "size_bytes": destination.stat().st_size,
            })
        else:
            missing.append(relative_path)

    return {
        "restored": True,
        "restored_at": _now_iso(),
        "backup_dir": str(backup_path),
        "restored_files": restored,
        "missing_backup_files": missing,
    }


@contextmanager
def controlled_observatory_state(
    label: str = "controlled_test",
    restore_after: bool = True,
):
    """
    Context manager for tests.

    Example:
        with controlled_observatory_state("my_test"):
            ... mutate account/open/closed/trade log ...
        # files are restored automatically
    """
    backup = backup_observatory_state(label=label)
    restore_result: Optional[Dict[str, Any]] = None

    try:
        yield backup
    finally:
        if restore_after:
            restore_result = restore_observatory_state(backup["backup_dir"])
            print("[CONTROLLED_TEST_RESTORE]", restore_result)


# =============================================================================
# Snapshots
# =============================================================================

def get_account_view() -> Dict[str, Any]:
    """
    Pulls the current account + portfolio view using live modules.
    """
    try:
        from engine.account_snapshot import account_snapshot
        from engine.portfolio_summary import portfolio_summary

        snap = account_snapshot()
        portfolio = portfolio_summary()

        return {
            "ok": True,
            "account_snapshot": snap,
            "portfolio_summary": portfolio,
            "cash": snap.get("cash"),
            "buying_power": snap.get("buying_power"),
            "equity": snap.get("equity"),
            "estimated_account_value": snap.get("estimated_account_value"),
            "open_positions": snap.get("open_positions"),
            "unrealized_pnl": snap.get("unrealized_pnl"),
            "official_realized_pnl": snap.get("official_realized_pnl"),
            "all_closed_records_pnl": snap.get("realized_pnl_all_closed_records"),
            "excluded_realized_pnl": snap.get("excluded_realized_pnl"),
            "account_math": snap.get("account_math"),
        }

    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }


def print_account_view(title: str = "ACCOUNT VIEW") -> Dict[str, Any]:
    view = get_account_view()

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    if not view.get("ok"):
        print("ERROR:", view.get("error"))
        return view

    print(f"Cash: {view.get('cash')}")
    print(f"Buying Power: {view.get('buying_power')}")
    print(f"Equity: {view.get('equity')}")
    print(f"Estimated Account Value: {view.get('estimated_account_value')}")
    print(f"Open Positions: {view.get('open_positions')}")
    print(f"Unrealized PnL: {view.get('unrealized_pnl')}")
    print(f"Official Realized PnL: {view.get('official_realized_pnl')}")
    print(f"All Closed Records PnL: {view.get('all_closed_records_pnl')}")
    print(f"Excluded Realized PnL: {view.get('excluded_realized_pnl')}")
    print(f"Account Math: {view.get('account_math')}")

    return view


# =============================================================================
# Controlled test data
# =============================================================================

def build_test_option_position(
    *,
    symbol: str = "TESTCLOSE",
    trade_id: str = "",
    entry_premium: float = 2.00,
    current_premium: float = 2.50,
    exit_premium: float = 2.75,
    contracts: int = 1,
    underlying_price: float = 100.0,
) -> Dict[str, Any]:
    symbol = str(symbol or "TESTCLOSE").upper()
    contracts = max(1, _safe_int(contracts, 1))

    if not trade_id:
        trade_id = f"{symbol}-CALL-CONTROLLED-{_now_stamp()}"

    contract_symbol = f"{symbol}260508C00100000"

    stop = round(entry_premium * 0.65, 4)
    target = round(entry_premium * 1.60, 4)

    return {
        "trade_id": trade_id,
        "symbol": symbol,
        "company_name": symbol,
        "status": "OPEN",
        "position_status": "OPEN",
        "execution_status": "OPEN",
        "timestamp": _now_iso(),
        "opened_at": _now_iso(),

        "strategy": "CALL",
        "direction": "LONG",
        "side": "CALL",

        "vehicle": "OPTION",
        "vehicle_selected": "OPTION",
        "selected_vehicle": "OPTION",
        "asset_type": "OPTION",
        "instrument_type": "OPTION",

        "shares": 0,
        "contracts": contracts,
        "contract_count": contracts,
        "quantity": contracts,
        "qty": contracts,
        "size": contracts,

        "entry": entry_premium,
        "entry_price": entry_premium,
        "entry_premium": entry_premium,
        "premium_entry": entry_premium,
        "option_entry": entry_premium,
        "option_entry_price": entry_premium,
        "entry_option_mark": entry_premium,
        "contract_entry_price": entry_premium,

        "current_price": current_premium,
        "current": current_premium,
        "current_premium": current_premium,
        "premium_current": current_premium,
        "current_option_mark": current_premium,
        "option_current_mark": current_premium,
        "option_current_price": current_premium,
        "current_option_price": current_premium,

        "underlying_price": underlying_price,
        "current_underlying_price": underlying_price,
        "stock_price": underlying_price,

        "stop": stop,
        "stop_loss": stop,
        "option_stop": stop,
        "premium_stop": stop,
        "stop_premium": stop,
        "stop_loss_premium": stop,

        "target": target,
        "take_profit": target,
        "option_target": target,
        "premium_target": target,
        "target_premium": target,
        "take_profit_premium": target,

        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "option_contract_symbol": contract_symbol,
        "contractSymbol": contract_symbol,
        "expiry": "2026-05-08",
        "expiration": "2026-05-08",
        "expiration_date": "2026-05-08",
        "strike": underlying_price,
        "strike_price": underlying_price,
        "right": "CALL",
        "option_type": "CALL",
        "call_put": "CALL",

        "bid": round(current_premium - 0.05, 4),
        "ask": round(current_premium + 0.05, 4),
        "last": current_premium,
        "mark": current_premium,
        "open_interest": 500,
        "volume": 50,

        "price_review_basis": "OPTION_PREMIUM_ONLY",
        "monitoring_price_type": "OPTION_PREMIUM",
        "monitoring_mode": "OPTION_PREMIUM",
        "pnl_basis": "option_premium_x_100",
        "underlying_price_used_for_close_decision": False,
        "underlying_price_used_for_pnl": False,
        "execution_position_shape": "OPTION_PREMIUM_POSITION",

        "controlled_test": True,
        "controlled_test_expected_exit_premium": exit_premium,
    }


def inject_test_position(position: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a test position to open_positions.json only.

    This is intentionally used inside the controlled harness, where the files
    are restored afterward.
    """
    rows = _safe_read_json("data/open_positions.json", [])
    rows = rows if isinstance(rows, list) else []

    trade_id = str(position.get("trade_id", "")).strip()

    rows = [
        row for row in rows
        if not (isinstance(row, dict) and str(row.get("trade_id", "")).strip() == trade_id)
    ]

    rows.append(position)
    _safe_write_json("data/open_positions.json", rows)

    return {
        "injected": True,
        "trade_id": trade_id,
        "symbol": position.get("symbol"),
        "open_positions_after_inject": len(rows),
    }


# =============================================================================
# Controlled close test
# =============================================================================

def run_controlled_option_close_test(
    *,
    symbol: str = "TESTCLOSE",
    entry_premium: float = 2.00,
    current_premium: float = 2.50,
    exit_premium: float = 2.75,
    contracts: int = 1,
    restore_after: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Runs a full option close test while protecting live data.

    Expected math:
        PnL = (exit_premium - entry_premium) * 100 * contracts

    If restore_after=True:
        The account, open positions, closed positions, and trade log are restored
        after the test.
    """
    label = f"option_close_{symbol}"

    result: Dict[str, Any] = {
        "ok": False,
        "label": label,
        "restore_after": restore_after,
        "expected": {},
        "before": {},
        "after_inject": {},
        "close_result": {},
        "after_close": {},
        "after_restore": {},
        "backup": {},
        "errors": [],
    }

    expected_pnl = round((exit_premium - entry_premium) * 100 * max(1, contracts), 2)
    expected_market_value_before_close = round(current_premium * 100 * max(1, contracts), 2)
    expected_capital_credit = round((entry_premium * 100 * max(1, contracts)) + expected_pnl, 2)

    result["expected"] = {
        "entry_premium": entry_premium,
        "current_premium": current_premium,
        "exit_premium": exit_premium,
        "contracts": contracts,
        "expected_pnl": expected_pnl,
        "expected_market_value_before_close": expected_market_value_before_close,
        "expected_capital_credit": expected_capital_credit,
        "expected_pnl_rule": "(exit_premium - entry_premium) * 100 * contracts",
    }

    try:
        with controlled_observatory_state(label=label, restore_after=restore_after) as backup:
            result["backup"] = backup

            if verbose:
                before = print_account_view("CONTROLLED TEST — BEFORE")
            else:
                before = get_account_view()

            result["before"] = before

            trade_id = f"{symbol.upper()}-CALL-CONTROLLED-{_now_stamp()}"

            test_position = build_test_option_position(
                symbol=symbol,
                trade_id=trade_id,
                entry_premium=entry_premium,
                current_premium=current_premium,
                exit_premium=exit_premium,
                contracts=contracts,
            )

            injection = inject_test_position(test_position)
            result["injection"] = injection

            if verbose:
                after_inject = print_account_view("CONTROLLED TEST — AFTER INJECT")
            else:
                after_inject = get_account_view()

            result["after_inject"] = after_inject

            from engine.close_trade import close_position

            close_result = close_position(
                symbol=symbol,
                trade_id=trade_id,
                exit_price=exit_premium,
                reason="manual_option_premium_test",
            )

            result["close_result"] = close_result

            if verbose:
                print()
                print("=" * 80)
                print("CONTROLLED TEST — CLOSE RESULT")
                print("=" * 80)
                print(json.dumps({
                    "closed": close_result.get("closed"),
                    "blocked": close_result.get("blocked"),
                    "symbol": close_result.get("symbol"),
                    "trade_id": close_result.get("trade_id"),
                    "vehicle": close_result.get("vehicle"),
                    "exit_price": close_result.get("exit_price"),
                    "exit_premium": close_result.get("exit_premium"),
                    "pnl": close_result.get("pnl"),
                    "pnl_meta": close_result.get("pnl_meta"),
                    "capital_release": close_result.get("capital_release"),
                    "performance_classification": close_result.get("performance_classification"),
                    "performance_include": close_result.get("performance_include"),
                    "option_underlying_leak_blocked": close_result.get("option_underlying_leak_blocked"),
                }, indent=2, default=str))

            if verbose:
                after_close = print_account_view("CONTROLLED TEST — AFTER CLOSE BEFORE RESTORE")
            else:
                after_close = get_account_view()

            result["after_close"] = after_close

            close_pnl = round(_safe_float(close_result.get("pnl"), 0.0), 2)
            capital_release = _safe_dict(close_result.get("capital_release"))
            release_meta = _safe_dict(capital_release.get("metadata"))
            closing_match = _safe_dict(release_meta.get("closing_open_market_value_match"))

            checks = {
                "close_returned_true": close_result.get("closed") is True,
                "not_blocked": close_result.get("blocked") is False,
                "vehicle_option": close_result.get("vehicle") == "OPTION",
                "pnl_matches_expected": close_pnl == expected_pnl,
                "premium_basis": close_result.get("pnl_basis") == "option_premium_x_100",
                "no_underlying_close_decision": close_result.get("underlying_price_used_for_close_decision") is False,
                "no_underlying_pnl": close_result.get("underlying_price_used_for_pnl") is False,
                "leak_not_blocked_for_valid_premium": close_result.get("option_underlying_leak_blocked") is False,
                "closing_match_found": closing_match.get("matched") is True,
                "closing_match_trade_id": closing_match.get("match_reason") == "trade_id",
                "manual_test_excluded": close_result.get("performance_classification") == "MANUAL_TEST"
                and close_result.get("performance_include") is False,
            }

            result["checks"] = checks
            result["ok"] = all(bool(v) for v in checks.values())

    except Exception as exc:
        result["ok"] = False
        result["errors"].append({
            "error": str(exc),
            "traceback": traceback.format_exc(),
        })

    if restore_after:
        result["after_restore"] = get_account_view()

    if verbose:
        print()
        print("=" * 80)
        print("CONTROLLED TEST — FINAL CHECKS")
        print("=" * 80)

        for key, value in result.get("checks", {}).items():
            print(f"{key}: {value}")

        print()
        print("TEST OK:", result.get("ok"))

        if restore_after:
            print()
            print("=" * 80)
            print("CONTROLLED TEST — RESTORED REAL ACCOUNT VIEW")
            print("=" * 80)
            restored = result.get("after_restore", {})
            print(f"Cash: {restored.get('cash')}")
            print(f"Equity: {restored.get('equity')}")
            print(f"Estimated Account Value: {restored.get('estimated_account_value')}")
            print(f"Open Positions: {restored.get('open_positions')}")
            print("Restored:", restore_after)

    return result


__all__ = [
    "backup_observatory_state",
    "restore_observatory_state",
    "controlled_observatory_state",
    "get_account_view",
    "print_account_view",
    "build_test_option_position",
    "inject_test_position",
    "run_controlled_option_close_test",
]
