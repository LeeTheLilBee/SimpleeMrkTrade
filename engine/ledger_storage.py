
# ============================================================
# 🔭 OBSERVATORY LEDGER STORAGE GUARD
# Keeps data/canonical_ledger.json small enough for GitHub.
#
# Design:
# - Full historical ledger is archived locally in data/_local_archives/
# - Git-tracked canonical_ledger.json stays as a compact recent snapshot list
# - Shape remains list-compatible for older code that expects JSON list rows
# ============================================================

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ARCHIVE_DIR = DATA_DIR / "_local_archives"
CANONICAL_LEDGER_PATH = DATA_DIR / "canonical_ledger.json"

DEFAULT_SNAPSHOT_ROWS = 750
DEFAULT_ARCHIVE_TRIGGER_MB = 25.0


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_size_mb(path: Path) -> float:
    try:
        if not path.exists():
            return 0.0
        return round(path.stat().st_size / (1024 * 1024), 6)
    except Exception:
        return 0.0


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)


def _safe_read_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = []
    try:
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _extract_ledger_rows(payload: Any) -> List[Dict[str, Any]]:
    """
    Compatibility-first extraction.

    Supports:
    - list ledger: [row, row]
    - dict ledger wrapper: {"ledger": [...]} or {"canonical_ledger": [...]}
    """
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]

    if isinstance(payload, dict):
        for key in ("canonical_ledger", "ledger", "rows", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]

    return []


def _summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    symbols = {}
    vehicles = {}
    statuses = {}
    event_types = {}

    for row in rows:
        symbol = str(row.get("symbol", "") or "").strip().upper()
        vehicle = str(row.get("vehicle", row.get("vehicle_selected", "")) or "").strip().upper()
        status = str(row.get("status", row.get("position_status", "")) or "").strip().upper()
        event_type = str(row.get("event_type", row.get("type", "")) or "").strip().upper()

        if symbol:
            symbols[symbol] = symbols.get(symbol, 0) + 1
        if vehicle:
            vehicles[vehicle] = vehicles.get(vehicle, 0) + 1
        if status:
            statuses[status] = statuses.get(status, 0) + 1
        if event_type:
            event_types[event_type] = event_types.get(event_type, 0) + 1

    return {
        "row_count": len(rows),
        "symbol_count": len(symbols),
        "top_symbols": sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:25],
        "vehicles": vehicles,
        "statuses": statuses,
        "event_types": event_types,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def archive_full_canonical_ledger(reason: str = "manual_archive") -> Dict[str, Any]:
    """
    Archives the current canonical ledger exactly as-is.
    Does not compact by itself.
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    if not CANONICAL_LEDGER_PATH.exists():
        return {
            "archived": False,
            "reason": "canonical_ledger_missing",
            "source": str(CANONICAL_LEDGER_PATH),
        }

    size_mb = _safe_size_mb(CANONICAL_LEDGER_PATH)
    archive_path = ARCHIVE_DIR / f"canonical_ledger_{_utc_stamp()}_{reason}.json"
    shutil.copy2(CANONICAL_LEDGER_PATH, archive_path)

    return {
        "archived": True,
        "reason": reason,
        "source": str(CANONICAL_LEDGER_PATH),
        "archive_path": str(archive_path),
        "archive_size_mb": size_mb,
    }


def compact_canonical_ledger(
    snapshot_rows: int = DEFAULT_SNAPSHOT_ROWS,
    archive_trigger_mb: float = DEFAULT_ARCHIVE_TRIGGER_MB,
    force_archive: bool = False,
) -> Dict[str, Any]:
    """
    Keeps data/canonical_ledger.json small and Git-safe.

    Important compatibility choice:
    The compact file remains a plain JSON list, not a wrapper dict.
    That protects older code that expects canonical_ledger.json to be a list.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    if snapshot_rows <= 0:
        snapshot_rows = DEFAULT_SNAPSHOT_ROWS

    if not CANONICAL_LEDGER_PATH.exists():
        _atomic_write_json(CANONICAL_LEDGER_PATH, [])
        return {
            "status": "created_empty",
            "path": str(CANONICAL_LEDGER_PATH),
            "size_mb": _safe_size_mb(CANONICAL_LEDGER_PATH),
            "snapshot_rows": 0,
        }

    before_size_mb = _safe_size_mb(CANONICAL_LEDGER_PATH)
    payload = _safe_read_json(CANONICAL_LEDGER_PATH, [])
    rows = _extract_ledger_rows(payload)

    should_archive = bool(force_archive or before_size_mb >= archive_trigger_mb or len(rows) > snapshot_rows)

    archive_info = {
        "archived": False,
        "reason": "not_needed",
    }

    if should_archive:
        archive_info = archive_full_canonical_ledger(reason="pre_compact")

        # Also save a tiny summary beside the full archive for quick inspection.
        try:
            summary_path = ARCHIVE_DIR / f"canonical_ledger_summary_{_utc_stamp()}.json"
            _atomic_write_json(summary_path, _summarize_rows(rows))
            archive_info["summary_path"] = str(summary_path)
        except Exception as summary_error:
            archive_info["summary_error"] = str(summary_error)

    compact_rows = rows[-snapshot_rows:] if rows else []
    _atomic_write_json(CANONICAL_LEDGER_PATH, compact_rows)

    after_size_mb = _safe_size_mb(CANONICAL_LEDGER_PATH)

    return {
        "status": "compacted",
        "path": str(CANONICAL_LEDGER_PATH),
        "before_size_mb": before_size_mb,
        "after_size_mb": after_size_mb,
        "rows_before": len(rows),
        "rows_after": len(compact_rows),
        "snapshot_rows": snapshot_rows,
        "archive_trigger_mb": archive_trigger_mb,
        "archive": archive_info,
        "git_safe": after_size_mb < 25.0,
    }


def write_git_safe_canonical_ledger(
    rows: Any,
    snapshot_rows: int = DEFAULT_SNAPSHOT_ROWS,
    archive_trigger_mb: float = DEFAULT_ARCHIVE_TRIGGER_MB,
) -> Dict[str, Any]:
    """
    Safe writer for future modules.

    Accepts either a list of ledger rows or a wrapper dict containing ledger rows.
    Writes a compact list to canonical_ledger.json and archives oversized history.
    """
    extracted_rows = _extract_ledger_rows(rows)
    _atomic_write_json(CANONICAL_LEDGER_PATH, extracted_rows)
    return compact_canonical_ledger(
        snapshot_rows=snapshot_rows,
        archive_trigger_mb=archive_trigger_mb,
        force_archive=len(extracted_rows) > snapshot_rows,
    )


def read_git_safe_canonical_ledger(default: Any = None) -> List[Dict[str, Any]]:
    if default is None:
        default = []
    payload = _safe_read_json(CANONICAL_LEDGER_PATH, default)
    return _extract_ledger_rows(payload)


def ledger_storage_health() -> Dict[str, Any]:
    payload = _safe_read_json(CANONICAL_LEDGER_PATH, [])
    rows = _extract_ledger_rows(payload)
    archives = []
    try:
        archives = sorted(
            [str(p.name) for p in ARCHIVE_DIR.glob("canonical_ledger_*.json")],
            reverse=True,
        )[:10]
    except Exception:
        archives = []

    return {
        "canonical_path": str(CANONICAL_LEDGER_PATH),
        "canonical_size_mb": _safe_size_mb(CANONICAL_LEDGER_PATH),
        "canonical_rows": len(rows),
        "archive_dir": str(ARCHIVE_DIR),
        "recent_archives": archives,
        "git_safe": _safe_size_mb(CANONICAL_LEDGER_PATH) < 25.0,
    }
