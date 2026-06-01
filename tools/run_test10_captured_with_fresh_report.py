#!/usr/bin/env python3
# ============================================================
# OBSERVATORY_TEST_10_CAPTURED_REAL_BOT_AFTER_HANDOFF_FIX_20260519
# OBSERVATORY_PACK_TEST10_FRESH_REPORT_REBUILD_001
#
# Purpose:
# - Run the real bot with output captured to a log file.
# - Avoid browser crash from massive print output.
# - Compare active book before/after.
# - Fresh-rebuild polished readiness_report.json after bot run.
# - Prevent cached/old report writer from leaving unknown top_blockers.
#
# Usage from repo root:
#   python tools/run_test10_captured_with_fresh_report.py
# ============================================================

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import json
import os
import py_compile
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Set


LABEL = "OBSERVATORY_TEST_10_CAPTURED_REAL_BOT_AFTER_HANDOFF_FIX_20260519"
PATCH_LABEL = "OBSERVATORY_PACK_TEST10_FRESH_REPORT_REBUILD_001"


def find_project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent] + list(here.parents):
        if (parent / "engine").exists() and (parent / "data").exists():
            return parent
    return Path("/content/SimpleeMrkTrade")


PROJECT_ROOT = find_project_root()
LOG_DIR = PROJECT_ROOT / "data" / "test_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def get_active_book_detector():
    import engine.observatory_recovery_diagnostics as ordx

    importlib.reload(ordx)

    if hasattr(ordx, "root_only_active_position_detector"):
        return ordx.root_only_active_position_detector

    if hasattr(ordx, "strict_path_filter_open_positions"):
        return ordx.strict_path_filter_open_positions

    raise RuntimeError("No strict active book detector found.")


def compact_positions(result: Any) -> List[Dict[str, Any]]:
    rows = result.get("positions", []) if isinstance(result, dict) else []
    compact: List[Dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        compact.append({
            "symbol": row.get("symbol"),
            "trade_id": row.get("trade_id"),
            "vehicle": row.get("vehicle"),
            "entry": row.get("entry"),
            "current": row.get("current"),
            "monitoring": row.get("monitoring"),
            "basis": row.get("basis"),
            "status": row.get("status"),
            "position_status": row.get("position_status"),
        })

    return compact


def trade_ids(rows: List[Dict[str, Any]]) -> Set[str]:
    return {
        str(row.get("trade_id"))
        for row in rows
        if isinstance(row, dict) and row.get("trade_id")
    }


def fresh_rebuild_polished_readiness_report() -> Dict[str, Any]:
    """
    Fresh-imports engine/process_signals.py under a unique module name and rebuilds
    data/readiness_report.json with the latest report elegance + reason cleanup helpers.

    This does not run the bot and does not mutate active books.
    """
    process_signals_path = PROJECT_ROOT / "engine" / "process_signals.py"
    report_path = PROJECT_ROOT / "data" / "readiness_report.json"

    py_compile.compile(str(process_signals_path), doraise=True)

    fresh_name = (
        "engine.process_signals_test10_fresh_report_"
        + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )
    spec = importlib.util.spec_from_file_location(fresh_name, process_signals_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not build import spec for process_signals.py")

    psig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(psig)

    required_helpers = [
        "_observatory_rr_build_report_20260522",
        "_observatory_rr_write_json_20260522",
        "_observatory_rr_infer_clean_reason_20260527",
        "_observatory_rr_top_blockers_20260522",
    ]

    missing = [name for name in required_helpers if not hasattr(psig, name)]
    if missing:
        raise RuntimeError(f"Missing polished readiness report helpers: {missing}")

    report = psig._observatory_rr_build_report_20260522(process_result=None)
    psig._observatory_rr_write_json_20260522(report_path, report)

    saved = read_json(report_path, {})
    top_blockers = saved.get("top_blockers", [])

    unknown_count = 0
    for item in top_blockers:
        if isinstance(item, dict) and str(item.get("reason") or "").strip().lower() == "unknown":
            unknown_count += int(item.get("count") or 0)

    return {
        "rebuilt": True,
        "report_path": str(report_path),
        "generated_at": saved.get("report_meta", {}).get("generated_at"),
        "source": saved.get("report_meta", {}).get("source"),
        "summary": saved.get("summary", {}),
        "execution_pause": saved.get("execution_pause", {}),
        "top_blockers": top_blockers[:10],
        "unknown_top_blocker_count": unknown_count,
        "ui_card_count": len(saved.get("ui_cards", [])),
    }


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"{LABEL}_{stamp}.log"
    summary_path = LOG_DIR / f"{LABEL}_{stamp}_summary.json"

    print("=" * 80)
    print(LABEL)
    print("=" * 80)
    print("Patch label:", PATCH_LABEL)
    print("Project root:", PROJECT_ROOT)
    print("Log path:", log_path)
    print("Summary path:", summary_path)

    os.chdir(PROJECT_ROOT)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    get_active_book = get_active_book_detector()

    before = get_active_book()
    before_positions = compact_positions(before)
    before_ids = trade_ids(before_positions)

    print("\n===== BEFORE ACTIVE BOOK =====")
    print({
        "open_count": before.get("open_count") if isinstance(before, dict) else None,
        "symbols": [x.get("symbol") for x in before_positions],
        "trade_ids": list(before_ids),
    })

    print("\n===== RUNNING BOT WITH CAPTURED OUTPUT =====")
    print("Full bot output is being written to the log file, not the browser.")

    bot_error_type = None
    bot_error = None
    report_rebuild = None
    report_rebuild_error_type = None
    report_rebuild_error = None

    started_at = datetime.now().isoformat()

    try:
        import engine.bot as bot

        importlib.reload(bot)

        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("=" * 80 + "\n")
            log_file.write(LABEL + "\n")
            log_file.write(PATCH_LABEL + "\n")
            log_file.write("=" * 80 + "\n\n")
            log_file.flush()

            with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
                result = bot.run()
                print("\n===== BOT RETURN VALUE =====")
                print(repr(result))

    except Exception as exc:
        bot_error_type = type(exc).__name__
        bot_error = str(exc)

        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n\n===== BOT ERROR =====\n")
            log_file.write(f"{bot_error_type}: {bot_error}\n")
            log_file.write(traceback.format_exc())

    print("\n===== FRESH POLISHED READINESS REPORT REBUILD =====")
    try:
        report_rebuild = fresh_rebuild_polished_readiness_report()
        print(json.dumps({
            "rebuilt": report_rebuild.get("rebuilt"),
            "generated_at": report_rebuild.get("generated_at"),
            "source": report_rebuild.get("source"),
            "unknown_top_blocker_count": report_rebuild.get("unknown_top_blocker_count"),
            "top_blockers": report_rebuild.get("top_blockers"),
            "execution_pause": report_rebuild.get("execution_pause"),
        }, indent=2, default=str))

        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n\n===== FRESH POLISHED READINESS REPORT REBUILD =====\n")
            log_file.write(json.dumps(report_rebuild, indent=2, default=str))
            log_file.write("\n")

    except Exception as exc:
        report_rebuild_error_type = type(exc).__name__
        report_rebuild_error = str(exc)

        print("❌ Fresh report rebuild failed:", report_rebuild_error_type, report_rebuild_error)

        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n\n===== FRESH POLISHED READINESS REPORT REBUILD ERROR =====\n")
            log_file.write(f"{report_rebuild_error_type}: {report_rebuild_error}\n")
            log_file.write(traceback.format_exc())

    finished_at = datetime.now().isoformat()

    after = get_active_book()
    after_positions = compact_positions(after)
    after_ids = trade_ids(after_positions)

    new_ids = sorted(after_ids - before_ids)
    removed_ids = sorted(before_ids - after_ids)

    summary = {
        "label": LABEL,
        "patch_label": PATCH_LABEL,
        "started_at": started_at,
        "finished_at": finished_at,
        "log_path": str(log_path),
        "summary_path": str(summary_path),
        "open_count_before": before.get("open_count") if isinstance(before, dict) else None,
        "open_count_after": after.get("open_count") if isinstance(after, dict) else None,
        "before_symbols": [x.get("symbol") for x in before_positions],
        "after_symbols": [x.get("symbol") for x in after_positions],
        "new_positions_count": len(new_ids),
        "new_trade_ids": new_ids,
        "removed_positions_count": len(removed_ids),
        "removed_trade_ids": removed_ids,
        "bot_error_type": bot_error_type,
        "bot_error": bot_error,
        "fresh_readiness_report_rebuild": report_rebuild,
        "fresh_readiness_report_rebuild_error_type": report_rebuild_error_type,
        "fresh_readiness_report_rebuild_error": report_rebuild_error,
    }

    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    print("\n===== BOT RUN SUMMARY =====")
    print(json.dumps(summary, indent=2, default=str))

    if bot_error_type:
        print("\n❌ Bot crashed. Inspect the log tail.")
        return 1

    if report_rebuild_error_type:
        print("\n⚠️ Bot completed, but fresh readiness report rebuild failed.")
        return 2

    if report_rebuild and report_rebuild.get("unknown_top_blocker_count", 0) > 0:
        print("\n⚠️ Bot completed, but unknown still appears in top_blockers after fresh rebuild.")
        return 3

    print("\n✅ Bot completed without crashing.")
    print("✅ Fresh polished readiness_report.json rebuilt after Test 10.")
    print("✅ Unknown is gone from top_blockers after Test 10.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
