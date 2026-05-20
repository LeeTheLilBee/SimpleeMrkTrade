# =============================================================================
# THE TOWER — SECURITY EVENTS
# FILE: tower/security_events.py
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
SECURITY_EVENTS_PATH = TOWER_DATA_DIR / "security_events.jsonl"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def create_security_event(
    user_id: str,
    event_type: str,
    severity: str,
    description: str,
    source_app: Optional[str] = None,
    status: str = "open",
    recommended_action: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Creates one security alert.

    Baby version:
    Audit log = receipt book.
    Security event = sticky note that says, "Hey, look at this."
    """

    metadata = metadata or {}

    record = {
        "timestamp": _now(),
        "user_id": user_id,
        "event_type": event_type,
        "severity": severity,
        "status": status,
        "source_app": source_app,
        "description": description,
        "recommended_action": recommended_action,
        "metadata": metadata,
    }

    with SECURITY_EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, default=str) + "\n")

    return record


def read_security_events(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Reads recent security alerts.
    """

    if not SECURITY_EVENTS_PATH.exists():
        return []

    try:
        lines = SECURITY_EVENTS_PATH.read_text(encoding="utf-8").splitlines()
        rows = []
        for line in lines[-limit:]:
            if line.strip():
                rows.append(json.loads(line))
        return rows
    except Exception:
        return []


def get_security_summary() -> Dict[str, Any]:
    """
    Dashboard-friendly security numbers.
    """

    events = read_security_events(limit=1000)

    summary = {
        "total_security_events": len(events),
        "open": 0,
        "resolved": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "by_type": {},
        "by_source_app": {},
    }

    for event in events:
        status = event.get("status") or "open"
        severity = event.get("severity") or "low"
        event_type = event.get("event_type") or "unknown"
        source_app = event.get("source_app") or "unknown"

        if status == "resolved":
            summary["resolved"] += 1
        else:
            summary["open"] += 1

        if severity in summary:
            summary[severity] += 1

        summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
        summary["by_source_app"][source_app] = summary["by_source_app"].get(source_app, 0) + 1

    return summary


def security_event_from_clearance_decision(decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Converts scary clearance decisions into security alerts.

    Baby version:
    Not every no is scary.
    But some nos need a big red sticky note.
    """

    risk_score = int(decision.get("risk_score") or 0)
    risk_state = decision.get("risk_state") or "clear"
    reason_code = decision.get("reason_code") or "unknown"
    metadata = decision.get("metadata") or {}

    user_id = metadata.get("user_id", "unknown")
    app_name = metadata.get("app_name") or metadata.get("source_app") or "unknown"

    if risk_score < 70 and risk_state not in {"locked", "quarantined", "step_up_required"}:
        return None

    severity = "medium"

    if risk_score >= 95:
        severity = "critical"
    elif risk_score >= 80:
        severity = "high"
    elif risk_score >= 70:
        severity = "medium"

    return create_security_event(
        user_id=user_id,
        event_type=reason_code,
        severity=severity,
        source_app=app_name,
        description=decision.get("human_reason", "Security-relevant Tower decision."),
        recommended_action=", ".join(decision.get("required_actions", [])) or None,
        metadata={
            "decision": decision,
        },
    )
