# =============================================================================
# THE TOWER — AUDIT RECEIPT MACHINE
# FILE: tower/audit.py
# =============================================================================

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
AUDIT_LOG_PATH = TOWER_DATA_DIR / "audit_log.jsonl"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _hash_payload(payload: Dict[str, Any]) -> str:
    raw = _safe_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _base_record_for_hash(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes event_hash before checking the hash.

    Baby version:
    The receipt cannot include its own final sticker while we are checking
    if the sticker is correct.
    """

    clean = dict(record)
    clean.pop("event_hash", None)
    return clean


def _get_previous_hash() -> str:
    """
    Looks at the last audit receipt and gets its hash.

    Baby version:
    This lets every receipt hold hands with the receipt before it.
    If somebody changes an old receipt, the chain looks broken.
    """

    if not AUDIT_LOG_PATH.exists():
        return "GENESIS"

    try:
        last_line = None
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()

        if not last_line:
            return "GENESIS"

        record = json.loads(last_line)
        return record.get("event_hash", "GENESIS")
    except Exception:
        return "GENESIS"


def write_audit_event(
    actor_user_id: str,
    action: str,
    result: str,
    reason_code: str,
    human_reason: str,
    app_name: Optional[str] = None,
    target_user_id: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    risk_score: int = 0,
    risk_state: str = "clear",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Writes one audit receipt.

    Baby version:
    Every time The Tower says yes/no, this writes down:
    who asked, what happened, why, and when.
    """

    metadata = metadata or {}
    previous_hash = _get_previous_hash()

    base_record = {
        "timestamp": _now(),
        "actor_user_id": actor_user_id,
        "target_user_id": target_user_id,
        "action": action,
        "app_name": app_name,
        "object_type": object_type,
        "object_id": object_id,
        "result": result,
        "reason_code": reason_code,
        "human_reason": human_reason,
        "risk_score": risk_score,
        "risk_state": risk_state,
        "metadata": metadata,
        "previous_hash": previous_hash,
    }

    event_hash = _hash_payload(base_record)
    record = dict(base_record)
    record["event_hash"] = event_hash

    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, default=str) + "\n")

    return record


def read_recent_audit_events(limit: int = 25) -> list:
    """
    Reads recent audit receipts.
    """

    if not AUDIT_LOG_PATH.exists():
        return []

    try:
        lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
        rows = []
        for line in lines[-limit:]:
            if line.strip():
                rows.append(json.loads(line))
        return rows
    except Exception:
        return []


def read_all_audit_events() -> List[Dict[str, Any]]:
    """
    Reads all audit receipts.
    """

    if not AUDIT_LOG_PATH.exists():
        return []

    rows = []
    try:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    except Exception:
        return []

    return rows


def verify_audit_chain() -> Dict[str, Any]:
    """
    Checks whether the audit receipt chain still matches.

    Baby version:
    This checks:
    1. Is every receipt's sticker/hash correct?
    2. Is every receipt holding hands with the receipt before it?
    """

    rows = read_all_audit_events()

    if not rows:
        return {
            "ok": True,
            "status": "empty",
            "message": "No audit receipts found yet.",
            "total_events": 0,
            "broken_at": None,
            "problems": [],
        }

    problems = []
    expected_previous_hash = "GENESIS"

    for index, record in enumerate(rows):
        actual_event_hash = record.get("event_hash")
        actual_previous_hash = record.get("previous_hash")

        base_record = _base_record_for_hash(record)
        recalculated_hash = _hash_payload(base_record)

        if actual_previous_hash != expected_previous_hash:
            problems.append({
                "index": index,
                "type": "previous_hash_mismatch",
                "expected_previous_hash": expected_previous_hash,
                "actual_previous_hash": actual_previous_hash,
                "event_hash": actual_event_hash,
            })

        if actual_event_hash != recalculated_hash:
            problems.append({
                "index": index,
                "type": "event_hash_mismatch",
                "expected_event_hash": recalculated_hash,
                "actual_event_hash": actual_event_hash,
            })

        expected_previous_hash = actual_event_hash

    ok = len(problems) == 0

    return {
        "ok": ok,
        "status": "valid" if ok else "broken",
        "message": "Audit chain is valid." if ok else "Audit chain has problems.",
        "total_events": len(rows),
        "broken_at": problems[0]["index"] if problems else None,
        "problems": problems,
    }


def get_audit_summary() -> Dict[str, Any]:
    """
    Gives dashboard-friendly audit numbers.

    Baby version:
    This is for the future Control Deck cards.
    """

    rows = read_all_audit_events()

    summary = {
        "total_events": len(rows),
        "allows": 0,
        "denies": 0,
        "step_ups": 0,
        "quarantines": 0,
        "lockdowns": 0,
        "high_risk_events": 0,
        "apps": {},
        "risk_states": {},
        "chain": verify_audit_chain(),
    }

    for row in rows:
        result = row.get("result")
        app_name = row.get("app_name") or "unknown"
        risk_state = row.get("risk_state") or "unknown"
        risk_score = int(row.get("risk_score") or 0)

        if result == "allow":
            summary["allows"] += 1
        elif result == "deny":
            summary["denies"] += 1
        elif result == "step_up":
            summary["step_ups"] += 1
        elif result == "quarantine":
            summary["quarantines"] += 1
        elif result == "lockdown":
            summary["lockdowns"] += 1

        if risk_score >= 70:
            summary["high_risk_events"] += 1

        summary["apps"][app_name] = summary["apps"].get(app_name, 0) + 1
        summary["risk_states"][risk_state] = summary["risk_states"].get(risk_state, 0) + 1

    return summary
