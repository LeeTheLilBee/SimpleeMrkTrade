# =============================================================================
# THE TOWER — SECURITY INBOX
# FILE: tower/security_inbox.py
# =============================================================================

import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event
from tower.admin_action_gate import list_admin_actions
from tower.evidence_capsules import list_evidence_capsules
from tower.export_vault import list_exports
from tower.security_events import read_security_events
from tower.step_up import list_step_up_challenges


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
SECURITY_INBOX_PATH = TOWER_DATA_DIR / "security_inbox.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


INBOX_STATUS_OPEN = "open"
INBOX_STATUS_REVIEWING = "reviewing"
INBOX_STATUS_RESOLVED = "resolved"
INBOX_STATUS_DISMISSED = "dismissed"


SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _hash_payload(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_safe_json(payload).encode("utf-8")).hexdigest()


def _load_raw() -> Dict[str, Any]:
    if not SECURITY_INBOX_PATH.exists():
        return {"items": []}

    try:
        with SECURITY_INBOX_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"items": []}

        if not isinstance(data.get("items"), list):
            data["items"] = []

        return data
    except Exception:
        return {"items": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = SECURITY_INBOX_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(SECURITY_INBOX_PATH)


def _dedupe_key(source_type: str, source_id: str, reason_code: Optional[str] = None) -> str:
    return f"{source_type}:{source_id}:{reason_code or ''}"


def _severity_rank(severity: str) -> int:
    return SEVERITY_ORDER.get(str(severity or "info").lower(), 0)


def _make_item(
    source_type: str,
    source_id: str,
    title: str,
    summary: str,
    severity: str = "medium",
    status: str = INBOX_STATUS_OPEN,
    user_id: Optional[str] = None,
    app_name: Optional[str] = None,
    reason_code: Optional[str] = None,
    recommended_action: Optional[str] = None,
    source_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    item_id = secrets.token_urlsafe(18)

    item = {
        "inbox_item_id": item_id,
        "created_at": _now(),
        "updated_at": _now(),
        "status": status,
        "severity": severity,
        "severity_rank": _severity_rank(severity),
        "source_type": source_type,
        "source_id": source_id,
        "dedupe_key": _dedupe_key(source_type, source_id, reason_code),
        "title": title,
        "summary": summary,
        "user_id": user_id,
        "app_name": app_name,
        "reason_code": reason_code,
        "recommended_action": recommended_action or "review_item",
        "source_payload": source_payload or {},
    }

    item["inbox_hash"] = _hash_payload(item)
    return item


def sync_security_inbox(limit_per_source: int = 50) -> Dict[str, Any]:
    """
    Syncs important Tower records into one inbox.

    Baby version:
    This goes around The Tower and says:
    "Anything scary or unfinished? Put it on the review desk."
    """

    data = _load_raw()
    existing_by_dedupe = {
        item.get("dedupe_key"): item
        for item in data.get("items", [])
        if item.get("dedupe_key")
    }

    new_items: List[Dict[str, Any]] = []
    skipped_existing = 0

    def add_item(item: Dict[str, Any]) -> None:
        nonlocal skipped_existing

        key = item.get("dedupe_key")
        if key in existing_by_dedupe:
            skipped_existing += 1
            return

        existing_by_dedupe[key] = item
        new_items.append(item)

    # -------------------------------------------------------------------------
    # Security events
    # -------------------------------------------------------------------------
    for event in read_security_events(limit=limit_per_source):
        if event.get("status", "open") != "open":
            continue

        event_type = event.get("event_type") or "security_event"
        severity = event.get("severity") or "medium"

        add_item(
            _make_item(
                source_type="security_event",
                source_id=f"{event.get('timestamp')}:{event_type}:{event.get('user_id')}",
                title=f"Security event: {event_type}",
                summary=event.get("description") or "Open security event requires review.",
                severity=severity,
                user_id=event.get("user_id"),
                app_name=event.get("source_app"),
                reason_code=event_type,
                recommended_action=event.get("recommended_action") or "review_security_event",
                source_payload=event,
            )
        )

    # -------------------------------------------------------------------------
    # Evidence capsules
    # -------------------------------------------------------------------------
    for capsule in list_evidence_capsules(limit=limit_per_source):
        if capsule.get("status", "open") != "open":
            continue

        decision = capsule.get("decision", {}) or {}
        decision_kind = decision.get("decision") or "unknown"
        risk_state = decision.get("risk_state") or "unknown"
        risk_score = int(decision.get("risk_score") or 0)

        severity = "medium"
        if decision_kind in {"quarantine", "lockdown"} or risk_score >= 90:
            severity = "critical"
        elif decision_kind in {"deny", "step_up"} or risk_score >= 70:
            severity = "high"

        add_item(
            _make_item(
                source_type="evidence_capsule",
                source_id=capsule.get("capsule_id"),
                title=f"Open evidence capsule: {decision_kind}",
                summary=decision.get("human_reason") or "Open evidence capsule requires review.",
                severity=severity,
                user_id=(capsule.get("user") or {}).get("user_id"),
                app_name=(capsule.get("request") or {}).get("app_name"),
                reason_code=decision.get("reason_code"),
                recommended_action="review_evidence_capsule",
                source_payload={
                    "capsule_id": capsule.get("capsule_id"),
                    "capsule_hash": capsule.get("capsule_hash"),
                    "trigger": capsule.get("trigger"),
                    "decision": decision,
                    "risk_state": risk_state,
                },
            )
        )

    # -------------------------------------------------------------------------
    # Exports
    # -------------------------------------------------------------------------
    for export in list_exports(limit=limit_per_source):
        status = export.get("status") or "unknown"

        if status not in {"denied", "step_up_required", "quarantined", "locked", "revoked"}:
            continue

        severity = "medium"
        if status in {"quarantined", "locked"}:
            severity = "critical"
        elif status in {"denied", "revoked"}:
            severity = "high"

        decision = export.get("decision", {}) or {}

        add_item(
            _make_item(
                source_type="export",
                source_id=export.get("export_id"),
                title=f"Export needs review: {status}",
                summary=decision.get("human_reason") or f"Export request ended with status {status}.",
                severity=severity,
                user_id=export.get("user_id"),
                app_name=export.get("app_name"),
                reason_code=decision.get("reason_code") or f"export_{status}",
                recommended_action="review_export_request",
                source_payload={
                    "export_id": export.get("export_id"),
                    "export_hash": export.get("export_hash"),
                    "status": status,
                    "object_type": export.get("object_type"),
                    "object_id": export.get("object_id"),
                    "decision": decision,
                },
            )
        )

    # -------------------------------------------------------------------------
    # Admin actions
    # -------------------------------------------------------------------------
    for action in list_admin_actions(limit=limit_per_source):
        status = action.get("status") or "unknown"

        if status not in {"denied", "step_up_required", "revoked"}:
            continue

        decision = action.get("decision", {}) or {}
        admin_action = action.get("admin_action") or "admin_action"

        severity = "medium"
        risk_score = int(decision.get("risk_score") or 0)

        if risk_score >= 90:
            severity = "critical"
        elif risk_score >= 70:
            severity = "high"

        add_item(
            _make_item(
                source_type="admin_action",
                source_id=action.get("admin_action_id"),
                title=f"Admin action needs review: {admin_action}",
                summary=decision.get("human_reason") or f"Admin action ended with status {status}.",
                severity=severity,
                user_id=action.get("actor_user_id"),
                app_name="tower_admin",
                reason_code=decision.get("reason_code") or f"admin_action_{status}",
                recommended_action="review_admin_action",
                source_payload={
                    "admin_action_id": action.get("admin_action_id"),
                    "admin_action_hash": action.get("admin_action_hash"),
                    "status": status,
                    "admin_action": admin_action,
                    "target_user_id": action.get("target_user_id"),
                    "requested_changes": action.get("requested_changes"),
                    "decision": decision,
                },
            )
        )

    # -------------------------------------------------------------------------
    # Pending step-ups
    # -------------------------------------------------------------------------
    for step in list_step_up_challenges(limit=limit_per_source):
        status = step.get("status") or "unknown"

        if status != "pending":
            continue

        add_item(
            _make_item(
                source_type="step_up_challenge",
                source_id=step.get("challenge_id"),
                title=f"Pending step-up: {step.get('action')}",
                summary="A step-up challenge is waiting for approval or denial.",
                severity="medium",
                user_id=step.get("user_id"),
                app_name=step.get("app_name"),
                reason_code=step.get("reason_code"),
                recommended_action="approve_or_deny_step_up",
                source_payload=step,
            )
        )

    if new_items:
        data["items"].extend(new_items)
        _save_raw(data)

    write_audit_event(
        actor_user_id="tower_security_inbox",
        target_user_id=None,
        action="sync_security_inbox",
        app_name="tower_admin",
        object_type="security_inbox",
        object_id="security_inbox",
        result="allow",
        reason_code="security_inbox_synced",
        human_reason="Tower security inbox was synced.",
        risk_score=20,
        risk_state="clear",
        metadata={
            "new_items": len(new_items),
            "skipped_existing": skipped_existing,
            "total_items": len(data.get("items", [])),
        },
    )

    return {
        "status": "synced",
        "new_items": len(new_items),
        "skipped_existing": skipped_existing,
        "total_items": len(data.get("items", [])),
    }


def list_inbox_items(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    data = _load_raw()
    rows = data.get("items", [])

    if status:
        rows = [item for item in rows if item.get("status") == status]

    if severity:
        rows = [item for item in rows if item.get("severity") == severity]

    rows = sorted(
        rows,
        key=lambda item: (
            item.get("status") != INBOX_STATUS_OPEN,
            -int(item.get("severity_rank") or 0),
            item.get("created_at") or "",
        ),
    )

    return rows[:limit]


def get_inbox_item(inbox_item_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()

    for item in data.get("items", []):
        if item.get("inbox_item_id") == inbox_item_id:
            return item

    return None


def update_inbox_item_status(
    inbox_item_id: str,
    status: str,
    actor_user_id: str,
    resolution_note: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    updated = None

    for item in data.get("items", []):
        if item.get("inbox_item_id") == inbox_item_id:
            item["status"] = status
            item["updated_at"] = _now()

            if status in {INBOX_STATUS_RESOLVED, INBOX_STATUS_DISMISSED}:
                item["closed_at"] = _now()
                item["closed_by"] = actor_user_id

            if status == INBOX_STATUS_REVIEWING:
                item["review_started_at"] = _now()
                item["review_started_by"] = actor_user_id

            if resolution_note:
                item["resolution_note"] = resolution_note

            clean = dict(item)
            clean.pop("inbox_hash", None)
            item["inbox_hash"] = _hash_payload(clean)

            updated = item
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=actor_user_id,
            target_user_id=updated.get("user_id"),
            action="update_security_inbox_item",
            app_name="tower_admin",
            object_type="security_inbox_item",
            object_id=inbox_item_id,
            result="allow",
            reason_code=f"security_inbox_item_{status}",
            human_reason=f"Security inbox item marked {status}.",
            risk_score=35,
            risk_state="clear",
            metadata={
                "inbox_item_id": inbox_item_id,
                "status": status,
                "source_type": updated.get("source_type"),
                "source_id": updated.get("source_id"),
                "resolution_note": resolution_note,
            },
        )

    return updated


def verify_inbox_item(inbox_item_id: str) -> Dict[str, Any]:
    item = get_inbox_item(inbox_item_id)

    if not item:
        return {
            "ok": False,
            "reason_code": "security_inbox_item_not_found",
            "human_reason": "Security inbox item was not found.",
            "inbox_item_id": inbox_item_id,
        }

    stored = item.get("inbox_hash")
    clean = dict(item)
    clean.pop("inbox_hash", None)

    recalculated = _hash_payload(clean)
    ok = stored == recalculated

    return {
        "ok": ok,
        "reason_code": "security_inbox_item_valid" if ok else "security_inbox_item_hash_mismatch",
        "human_reason": "Security inbox item is valid." if ok else "Security inbox item hash does not match.",
        "inbox_item_id": inbox_item_id,
        "stored_hash": stored,
        "recalculated_hash": recalculated,
        "status": item.get("status"),
    }


def get_security_inbox_summary() -> Dict[str, Any]:
    data = _load_raw()
    rows = data.get("items", [])

    summary = {
        "total_inbox_items": len(rows),
        "open": 0,
        "reviewing": 0,
        "resolved": 0,
        "dismissed": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "by_source_type": {},
        "by_app": {},
    }

    for item in rows:
        status = item.get("status") or "open"
        severity = item.get("severity") or "medium"
        source_type = item.get("source_type") or "unknown"
        app_name = item.get("app_name") or "unknown"

        if status in summary:
            summary[status] += 1

        if severity in summary:
            summary[severity] += 1

        summary["by_source_type"][source_type] = summary["by_source_type"].get(source_type, 0) + 1
        summary["by_app"][app_name] = summary["by_app"].get(app_name, 0) + 1

    return summary
